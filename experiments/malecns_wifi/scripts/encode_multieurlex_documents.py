"""Stage B: semantic cache -> document embeddings for one encoder variant.

Variants (all label-free, all reading the same stage-A cache):

* ``malecns``: frozen MaleCNS reservoir (``--backend canonical|fast``).
* ``sensory-only``: the MaleCNS pipeline with the recurrent operator removed.
* ``fused-mean-proj``: mean fused MiniLM/E5 vector through a fixed 256-d projection.
* ``fused-mean``: mean fused MiniLM/E5 vector, no projection.

Writes ``<output>.npz`` (``doc_key``, ``embeddings``) plus a manifest with
engineering metrics. ``--reference`` compares the result against another
stage-B file and reports the equivalence gate.
"""

from __future__ import annotations

import argparse
import json
import platform
import resource_usage
from pathlib import Path

import numpy as np

from malecns_wifi.document_reservoir import (
    BACKENDS,
    VARIANTS,
    DocumentReservoir,
    DocumentReservoirConfig,
    control_embeddings,
    equivalence_report,
    load_reservoir_inputs,
    passes_gate,
)
from malecns_wifi.multieurlex_cache import load_cache


def encode_variant(
    cache,
    *,
    variant: str,
    backend: str,
    config: DocumentReservoirConfig,
    graph: Path | None,
    device: str,
    batch_size: int,
    index_dtype: str = "int64",
    group_by_length: bool | None = None,
):
    fused = cache.fused
    reservoir = None
    if variant in ("malecns", "sensory-only"):
        if graph is None:
            raise ValueError(f"variant {variant} needs --graph")
        matrix, input_indices = load_reservoir_inputs(graph)
        reservoir = DocumentReservoir(
            matrix,
            input_indices,
            semantic_dim=fused.shape[1],
            config=config,
            device=device,
            backend=backend,
            index_dtype=index_dtype,
        )
    with resource_usage.track(device) as usage:
        if variant == "malecns":
            embeddings = reservoir.encode_cached(
                fused, cache.offsets, batch_size=batch_size, group_by_length=group_by_length
            )
        else:
            embeddings = control_embeddings(
                variant, fused, cache.offsets, config=config, reservoir=reservoir, batch_size=batch_size
            )
    stats = reservoir.stats.as_dict() if reservoir is not None else {}
    stats.setdefault("documents", cache.documents)
    stats.setdefault("chunks", cache.chunks)
    if not stats.get("forward_seconds"):
        stats["forward_seconds"] = usage.seconds
        stats["docs_per_second"] = cache.documents / usage.seconds if usage.seconds else None
        stats["chunks_per_second"] = cache.chunks / usage.seconds if usage.seconds else None
    return embeddings, stats, usage.as_dict(), reservoir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--semantic-cache", required=True, help="stage-A directory or hf:<repo_id>[@revision]")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--graph", type=Path)
    parser.add_argument("--variant", choices=VARIANTS, default="malecns")
    parser.add_argument("--backend", choices=BACKENDS, default="canonical")
    parser.add_argument("--index-dtype", choices=["int64", "int32"], default="int64")
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--readout-width", type=int, default=256)
    parser.add_argument("--seed", type=int, default=20260915)
    parser.add_argument("--gain", type=float, default=4.0)
    parser.add_argument("--leak", type=float, default=0.4)
    parser.add_argument("--target-rms", type=float, default=0.05)
    parser.add_argument("--reference", type=Path, help="stage-B npz to compare against")
    args = parser.parse_args()

    cache = load_cache(args.semantic_cache)
    config = DocumentReservoirConfig(
        readout_width=args.readout_width,
        seed=args.seed,
        max_chunks=int(cache.manifest["chunking"]["max_chunks"]),
        chunk_chars=int(cache.manifest["chunking"]["chunk_chars"]),
        gain=args.gain,
        leak=args.leak,
        target_rms=args.target_rms,
    )
    embeddings, stats, usage, reservoir = encode_variant(
        cache,
        variant=args.variant,
        backend=args.backend,
        config=config,
        graph=args.graph,
        device=args.device,
        batch_size=args.batch_size,
        index_dtype=args.index_dtype,
    )

    equivalence = None
    if args.reference is not None:
        reference = np.load(args.reference, allow_pickle=False)
        if reference["doc_key"].tolist() != cache.doc_key.tolist():
            raise RuntimeError("reference embeddings cover different documents")
        equivalence = equivalence_report(reference["embeddings"], embeddings)
        equivalence["gate_passed"] = passes_gate(equivalence)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.output, doc_key=cache.doc_key, embeddings=embeddings.astype(np.float32))
    manifest = {
        "schema": "papers/malecns-multieurlex-document-embeddings-v1",
        "variant": args.variant,
        "backend": args.backend if args.variant in ("malecns", "sensory-only") else None,
        "index_dtype": args.index_dtype,
        "device": args.device,
        "batch_size": args.batch_size,
        "config": config.as_dict(),
        "semantic_cache": str(args.semantic_cache),
        "semantic_cache_fingerprint": cache.manifest["fingerprint"],
        "semantic_models_order": list(cache.models),
        "semantic_dim": int(cache.fused.shape[1]),
        "graph": {
            "neurons": reservoir.neurons if reservoir else None,
            "edges": reservoir.edges if reservoir else None,
            "sensory_neurons": reservoir.sensory_neurons if reservoir else None,
        },
        "stats": stats,
        "resources": usage,
        "equivalence": equivalence,
        "python": platform.python_version(),
        "uses_benchmark_labels": False,
    }
    args.output.with_suffix(".manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({"event": "multieurlex_documents_encoded", **manifest}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
