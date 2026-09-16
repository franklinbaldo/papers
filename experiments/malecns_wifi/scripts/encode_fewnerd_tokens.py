"""Stage B: Few-NERD dedup cache -> per-byte frozen MaleCNS readout embeddings.

Reads stage A's deduplicated window-embedding cache (no per-byte field is ever
stored on disk); for each sentence batch, reassembles the byte-synchronised
fused channel on the fly (deterministic window spans + hash lookup +
interpolation, see ``fewnerd_cache.FewnerdCache.assemble_channel``), then runs
the frozen MaleCNS positional reservoir over it. Sentences are the batch unit
and UTF-8 bytes are the time axis: one recurrent step per byte position, a
readout emitted at every step. Batches are grouped by sentence byte-length so
no padded position is computed needlessly.
"""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np

from malecns_wifi.document_reservoir import equivalence_report, load_reservoir_populations, passes_gate
from malecns_wifi.fewnerd_cache import load_cache
from malecns_wifi.telemetry import Telemetry, progress_fields
from malecns_wifi.token_reservoir import PositionalReservoir, TokenReservoirConfig


def pack_cube(channels: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    """``channels``: list of [byte_length_i, dim] arrays (equal dim, possibly ragged length)."""
    steps = max(c.shape[0] for c in channels)
    dim = channels[0].shape[1]
    cube = np.zeros((len(channels), steps, dim), dtype=np.float32)
    active = np.zeros((len(channels), steps), dtype=np.bool_)
    for row, channel in enumerate(channels):
        n = channel.shape[0]
        cube[row, :n] = channel
        active[row, :n] = True
    return cube, active


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--token-cache", required=True, help="stage-A directory or hf:<repo_id>[@revision]")
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--readout-width", type=int, default=256, help="ignored when --readout-mode=descending_neuron")
    parser.add_argument("--readout-mode", choices=["random_sparse", "descending_neuron"], default="random_sparse")
    parser.add_argument("--seed", type=int, default=20260915)
    parser.add_argument("--gain", type=float, default=4.0)
    parser.add_argument("--leak", type=float, default=0.4)
    parser.add_argument("--target-rms", type=float, default=0.05)
    parser.add_argument("--index-dtype", choices=["int64", "int32"], default="int64")
    parser.add_argument("--reference", type=Path, help="stage-B npz to compare against (equivalence gate)")
    args = parser.parse_args()

    cache = load_cache(args.token_cache)
    model_names = tuple(cache.manifest.get("encoder_order") or list(cache.encoders))
    sentences = cache.sentences
    texts = sentences.column("text").to_pylist()
    fine_lists = sentences.column("fine_label").to_pylist()
    coarse_lists = sentences.column("coarse_label").to_pylist()
    splits = sentences.column("split").to_pylist()
    split_indices = sentences.column("split_index").to_numpy()
    lengths = np.asarray([len(f) for f in fine_lists], dtype=np.int64)
    n_sentences = len(texts)

    matrix, input_indices, readout_indices = load_reservoir_populations(args.graph)
    semantic_dim = sum(cache.encoders[m].base_dim for m in model_names) * len(cache.scales)
    config = TokenReservoirConfig(readout_width=args.readout_width, readout_mode=args.readout_mode, seed=args.seed,
                                   gain=args.gain, leak=args.leak, target_rms=args.target_rms)
    reservoir = PositionalReservoir(matrix, input_indices, semantic_dim=semantic_dim, config=config,
                                     readout_indices=readout_indices,
                                     device=args.device, index_dtype=args.index_dtype)
    telemetry = Telemetry("stage-b-fewnerd-reservoir", config={"batch_size": args.batch_size, "device": args.device,
                          "index_dtype": args.index_dtype})

    total_bytes = int(lengths.sum())
    fine_label = np.zeros(total_bytes, dtype=np.int64)
    coarse_label = np.zeros(total_bytes, dtype=np.int64)
    doc_split = np.empty(total_bytes, dtype="U16")
    doc_split_index = np.zeros(total_bytes, dtype=np.int64)
    offsets = np.concatenate([[0], np.cumsum(lengths)]).astype(np.int64)
    embeddings = np.zeros((total_bytes, config.readout_width), dtype=np.float32)
    for i in range(n_sentences):
        start, stop = int(offsets[i]), int(offsets[i + 1])
        fine_label[start:stop] = fine_lists[i]
        coarse_label[start:stop] = coarse_lists[i]
        doc_split[start:stop] = splits[i]
        doc_split_index[start:stop] = split_indices[i]

    done_sentences = 0
    started = time.perf_counter()
    for length in np.unique(lengths):
        members = np.flatnonzero(lengths == length)
        for start in range(0, len(members), args.batch_size):
            batch_idx = members[start:start + args.batch_size]
            channels = [cache.assemble_channel(model_names, texts[i]) for i in batch_idx]
            cube, active = pack_cube(channels)
            per_position = reservoir.forward(cube, active)
            for row, sentence in enumerate(batch_idx):
                s, e = int(offsets[sentence]), int(offsets[sentence + 1])
                embeddings[s:e] = per_position[row, : e - s]
            done_sentences += len(batch_idx)
            telemetry.log({**progress_fields(done_sentences, n_sentences, started, "sentences"),
                           "spmm_calls": reservoir.stats.spmm_calls}, min_interval=2.0)

    equivalence = None
    if args.reference is not None:
        reference = np.load(args.reference, allow_pickle=False)
        equivalence = equivalence_report(reference["embeddings"], embeddings)
        equivalence["gate_passed"] = passes_gate(equivalence)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        args.output, embeddings=embeddings, fine_label=fine_label, coarse_label=coarse_label,
        doc_split=doc_split, doc_split_index=doc_split_index, offsets=offsets,
    )
    stats = reservoir.stats.as_dict()
    manifest = {
        "schema": "papers/malecns-fewnerd-token-embeddings-v2",
        "index_dtype": args.index_dtype, "device": args.device, "batch_size": args.batch_size,
        "config": config.as_dict(), "token_cache": str(args.token_cache),
        "token_cache_fingerprint": cache.manifest.get("fingerprint"),
        "graph": {"neurons": reservoir.neurons, "edges": reservoir.edges, "sensory_neurons": reservoir.sensory_neurons},
        "stats": stats, "equivalence": equivalence, "python": platform.python_version(),
        "uses_benchmark_labels": False,
        "note": "fine_label/coarse_label are stored for stage C's probe, never seen by the reservoir",
    }
    args.output.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    telemetry.summary({"bytes_per_second": stats.get("chunks_per_second"), "forward_seconds": stats.get("forward_seconds"),
                       **({f"equivalence/{k}": v for k, v in equivalence.items()} if equivalence else {})})
    telemetry.finish()
    print(json.dumps({"event": "fewnerd_tokens_encoded", **manifest}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
