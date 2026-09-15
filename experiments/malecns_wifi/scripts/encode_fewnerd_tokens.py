"""Stage B: Few-NERD token cache -> per-token frozen MaleCNS readout embeddings.

Sentences are the batch unit and tokens are the time axis: one recurrent step
per token position, a readout emitted at every step (not just the last, unlike
the MultiEURLEX document encoder). Batches are grouped by sentence length so no
padded position is computed needlessly. Output is one 256-d embedding per
token, in cache order, plus labels for stage C.
"""

from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import numpy as np

from malecns_wifi.document_reservoir import equivalence_report, load_reservoir_inputs, passes_gate
from malecns_wifi.fewnerd_cache import load_cache
from malecns_wifi.telemetry import Telemetry, progress_fields
from malecns_wifi.token_reservoir import PositionalReservoir, TokenReservoirConfig


def pack_cube(fused: np.ndarray, offsets: np.ndarray, sentence_indices: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    counts = offsets[sentence_indices + 1] - offsets[sentence_indices]
    steps = int(counts.max()) if counts.size else 0
    dim = int(fused.shape[1])
    cube = np.zeros((len(sentence_indices), steps, dim), dtype=np.float32)
    active = np.zeros((len(sentence_indices), steps), dtype=np.bool_)
    for row, sentence in enumerate(sentence_indices):
        start, stop = int(offsets[sentence]), int(offsets[sentence + 1])
        cube[row, : stop - start] = fused[start:stop]
        active[row, : stop - start] = True
    return cube, active


def iter_batches(offsets: np.ndarray, *, batch_size: int):
    counts = np.diff(offsets)
    for length in np.unique(counts):
        members = np.flatnonzero(counts == length)
        for start in range(0, len(members), batch_size):
            yield members[start:start + batch_size]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--token-cache", required=True, help="stage-A directory or hf:<repo_id>[@revision]")
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--readout-width", type=int, default=256)
    parser.add_argument("--seed", type=int, default=20260915)
    parser.add_argument("--gain", type=float, default=4.0)
    parser.add_argument("--leak", type=float, default=0.4)
    parser.add_argument("--target-rms", type=float, default=0.05)
    parser.add_argument("--index-dtype", choices=["int64", "int32"], default="int64")
    parser.add_argument("--reference", type=Path, help="stage-B npz to compare against (equivalence gate)")
    args = parser.parse_args()

    cache = load_cache(args.token_cache)
    fused = cache.fused
    matrix, input_indices = load_reservoir_inputs(args.graph)
    config = TokenReservoirConfig(readout_width=args.readout_width, seed=args.seed, gain=args.gain,
                                   leak=args.leak, target_rms=args.target_rms)
    reservoir = PositionalReservoir(matrix, input_indices, semantic_dim=fused.shape[1], config=config,
                                     device=args.device, index_dtype=args.index_dtype)
    telemetry = Telemetry("stage-b-fewnerd-reservoir", config={"batch_size": args.batch_size, "device": args.device,
                          "index_dtype": args.index_dtype})

    n_tokens = int(cache.offsets[-1])
    output = np.zeros((n_tokens, config.readout_width), dtype=np.float32)
    done_sentences = 0
    import time

    started = time.perf_counter()
    for sentences in iter_batches(cache.offsets, batch_size=args.batch_size):
        cube, active = pack_cube(fused, cache.offsets, sentences)
        per_position = reservoir.forward(cube, active)  # [batch, steps, width]
        for row, sentence in enumerate(sentences):
            start, stop = int(cache.offsets[sentence]), int(cache.offsets[sentence + 1])
            output[start:stop] = per_position[row, : stop - start]
        done_sentences += len(sentences)
        telemetry.log({**progress_fields(done_sentences, cache.sentences, started, "sentences"),
                       "spmm_calls": reservoir.stats.spmm_calls}, min_interval=2.0)

    equivalence = None
    if args.reference is not None:
        reference = np.load(args.reference, allow_pickle=False)
        equivalence = equivalence_report(reference["embeddings"], output)
        equivalence["gate_passed"] = passes_gate(equivalence)

    # per-token split/split-index, expanded from the per-sentence cache arrays
    counts = np.diff(cache.offsets)
    token_split = np.repeat(cache.doc_split, counts)
    token_split_index = np.repeat(cache.doc_split_index, counts)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        args.output, embeddings=output, fine_label=cache.fine_label, coarse_label=cache.coarse_label,
        doc_split=token_split, doc_split_index=token_split_index, offsets=cache.offsets,
    )
    stats = reservoir.stats.as_dict()
    manifest = {
        "schema": "papers/malecns-fewnerd-token-embeddings-v1",
        "index_dtype": args.index_dtype, "device": args.device, "batch_size": args.batch_size,
        "config": config.as_dict(), "token_cache": str(args.token_cache),
        "token_cache_fingerprint": cache.manifest.get("fingerprint"),
        "graph": {"neurons": reservoir.neurons, "edges": reservoir.edges, "sensory_neurons": reservoir.sensory_neurons},
        "stats": stats, "equivalence": equivalence, "python": platform.python_version(),
        "uses_benchmark_labels": False,
        "note": "fine_label/coarse_label are stored for stage C's probe, never seen by the reservoir",
    }
    args.output.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    telemetry.summary({"tokens_per_second": stats.get("chunks_per_second"), "forward_seconds": stats.get("forward_seconds"),
                       **({f"equivalence/{k}": v for k, v in equivalence.items()} if equivalence else {})})
    telemetry.finish()
    print(json.dumps({"event": "fewnerd_tokens_encoded", **manifest}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
