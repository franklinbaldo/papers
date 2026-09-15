"""Milestone benchmark: canonical vs fast MaleCNS document encoding, plus controls.

Reads a stage-A semantic cache (built with ``build_multieurlex_semantic_cache.py``)
and the compiled graph, then measures on the requested device:

* MaleCNS canonical (batch 16, ragged batches, int64 CSR) as the reference;
* MaleCNS fast over a batch-size sweep (grouped batches, first-step SpMM skipped,
  in-place drive), each checked against the reference with the equivalence gate;
* optional int32 CSR index variant;
* the label-free controls sharing the same semantic inputs.

Emits a JSON file with every engineering metric and prints the milestone table.
"""

from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import numpy as np

from encode_multieurlex_documents import encode_variant
from malecns_wifi.document_reservoir import (
    CONTROL_VARIANTS,
    DocumentReservoirConfig,
    equivalence_report,
    passes_gate,
)
from malecns_wifi.multieurlex_cache import load_cache
from malecns_wifi.telemetry import Telemetry


def _fmt(value, digits=2):
    if value is None:
        return "n/a"
    return f"{value:.{digits}f}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--semantic-cache", required=True, help="stage-A directory or hf:<repo_id>[@revision]")
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--reference-batch-size", type=int, default=16)
    parser.add_argument("--batch-sizes", type=int, nargs="+", default=[16, 32, 64, 128, 256])
    parser.add_argument("--index-dtypes", nargs="+", default=["int64"])
    parser.add_argument("--skip-controls", action="store_true")
    parser.add_argument("--seed", type=int, default=20260915)
    args = parser.parse_args()

    import torch

    cache = load_cache(args.semantic_cache)
    telemetry = Telemetry("stage-b-benchmark", config={
        "device": args.device, "batch_sizes": args.batch_sizes, "index_dtypes": args.index_dtypes,
    })
    config = DocumentReservoirConfig(
        seed=args.seed,
        max_chunks=int(cache.manifest["chunking"]["max_chunks"]),
        chunk_chars=int(cache.manifest["chunking"]["chunk_chars"]),
    )
    counts = np.diff(cache.offsets)
    result = {
        "schema": "papers/malecns-multieurlex-throughput-benchmark-v1",
        "device": args.device,
        "device_name": torch.cuda.get_device_name(0) if args.device.startswith("cuda") and torch.cuda.is_available() else platform.processor(),
        "torch": torch.__version__,
        "torch_threads": torch.get_num_threads(),
        "semantic_cache": {
            "location": str(args.semantic_cache),
            "fingerprint": cache.manifest["fingerprint"],
            "documents": cache.documents,
            "chunks": cache.chunks,
            "chunks_histogram": {int(k): int(v) for k, v in zip(*np.unique(counts, return_counts=True))},
            "bytes": cache.manifest.get("bytes"),
            "partial": cache.manifest["dataset"].get("partial"),
            "encoders": cache.manifest["encoders"],
            "seconds": cache.manifest.get("seconds"),
        },
        "config": config.as_dict(),
        "runs": [],
    }

    def record(name, variant, backend, batch_size, index_dtype, group_by_length=None):
        embeddings, stats, usage, reservoir = encode_variant(
            cache,
            variant=variant,
            backend=backend,
            config=config,
            graph=args.graph,
            device=args.device,
            batch_size=batch_size,
            index_dtype=index_dtype,
            group_by_length=group_by_length,
        )
        entry = {
            "name": name,
            "variant": variant,
            "backend": backend,
            "batch_size": batch_size,
            "index_dtype": index_dtype,
            "group_by_length": group_by_length,
            "stats": stats,
            "resources": usage,
        }
        if reservoir is not None:
            entry["graph"] = {
                "neurons": reservoir.neurons,
                "edges": reservoir.edges,
                "sensory_neurons": reservoir.sensory_neurons,
            }
        result["runs"].append(entry)
        telemetry.log({
            "run": name, "docs_per_second": stats.get("docs_per_second"), "batch_size": batch_size,
            "spmm_mean_ms": stats.get("spmm_mean_ms"), "peak_vram_bytes": usage.get("peak_vram_bytes"),
            "variant": variant, "backend": backend, "index_dtype": index_dtype,
        })
        print(json.dumps({"event": "benchmark_run", **{k: v for k, v in entry.items() if k != "resources"}}), flush=True)
        return embeddings, entry

    reference, ref_entry = record(
        "malecns-canonical", "malecns", "canonical", args.reference_batch_size, "int64", group_by_length=False
    )
    ref_seconds = ref_entry["stats"]["forward_seconds"]

    fast_entries = []
    for index_dtype in args.index_dtypes:
        for batch_size in args.batch_sizes:
            embeddings, entry = record(
                f"malecns-fast-b{batch_size}-{index_dtype}", "malecns", "fast", batch_size, index_dtype, group_by_length=True
            )
            entry["equivalence"] = equivalence_report(reference, embeddings)
            entry["equivalence"]["gate_passed"] = passes_gate(entry["equivalence"])
            entry["speedup"] = ref_seconds / entry["stats"]["forward_seconds"] if entry["stats"]["forward_seconds"] else None
            fast_entries.append(entry)

    control_entries = []
    if not args.skip_controls:
        for variant in CONTROL_VARIANTS:
            embeddings, entry = record(
                f"control-{variant}", variant, "fast", max(args.batch_sizes), "int64", group_by_length=True
            )
            entry["cosine_to_malecns"] = float(np.mean(np.sum(reference * embeddings, axis=1))) if embeddings.shape == reference.shape else None
            control_entries.append(entry)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    sc = result["semantic_cache"]
    enc = {e["name"].split("/")[-1]: e["seconds"] for e in sc["encoders"]}
    lines = [
        "semantic cache:",
        f"  {sc['documents']} docs",
        f"  {sc['chunks']} chunks  {sc['chunks_histogram']}",
        *[f"  {name} time: {_fmt(seconds)} s" for name, seconds in enc.items()],
        f"  size: {_fmt((sc['bytes'] or 0) / 1e6, 1)} MB",
        "",
        f"MaleCNS canonical (batch {args.reference_batch_size}, {result['device']}):",
        f"  docs/s: {_fmt(ref_entry['stats']['docs_per_second'])}",
        f"  chunks/s: {_fmt(ref_entry['stats']['chunks_per_second'])}",
        f"  total seconds: {_fmt(ref_seconds)}",
        f"  spmm calls: {ref_entry['stats']['spmm_calls']}  mean {_fmt(ref_entry['stats']['spmm_mean_ms'])} ms",
        f"  masked column-steps: {ref_entry['stats']['masked_column_steps']}",
        "",
    ]
    for entry in fast_entries:
        eq = entry["equivalence"]
        lines += [
            f"MaleCNS fast (batch {entry['batch_size']}, {entry['index_dtype']}):",
            f"  docs/s: {_fmt(entry['stats']['docs_per_second'])}",
            f"  total seconds: {_fmt(entry['stats']['forward_seconds'])}",
            f"  speedup: {_fmt(entry['speedup'])}x",
            f"  spmm calls: {entry['stats']['spmm_calls']}  mean {_fmt(entry['stats']['spmm_mean_ms'])} ms",
            f"  max_abs_error: {eq['max_abs_error']:.3e}",
            f"  cosine fidelity (min): {eq['min_cosine']:.8f}  bit_exact={eq['bit_exact']}  gate={'PASS' if eq['gate_passed'] else 'FAIL'}",
            "",
        ]
    for entry in control_entries:
        lines += [
            f"{entry['name']} control:",
            f"  docs/s: {_fmt(entry['stats']['docs_per_second'])}",
            f"  mean cosine to MaleCNS canonical: {_fmt(entry['cosine_to_malecns'], 4)}",
            "",
        ]
    telemetry.summary({
        "canonical_docs_per_second": ref_entry["stats"]["docs_per_second"],
        **{f"{e['name']}/docs_per_second": e["stats"]["docs_per_second"] for e in fast_entries},
        **{f"{e['name']}/speedup": e["speedup"] for e in fast_entries},
        **{f"{e['name']}/gate": e["equivalence"]["gate_passed"] for e in fast_entries},
    })
    telemetry.finish()
    report = "\n".join(lines)
    args.output.with_suffix(".txt").write_text(report + "\n", encoding="utf-8")
    print(report, flush=True)


if __name__ == "__main__":
    main()
