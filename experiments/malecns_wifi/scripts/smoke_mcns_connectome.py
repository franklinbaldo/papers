"""Validation script comparing FlatBuffers .mcns vs raw graph.npz on whole-brain reservoir smoke.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import scipy.sparse as sp

from malecns_wifi import load_graph
from malecns_wifi.cache_spmv import CompactOperator4Bit


def run_smoke_on_operator(op, input_neurons, rng_seeds, steps=12):
    n = op.n_rows if hasattr(op, "n_rows") else op.shape[0]
    state = np.zeros(n, dtype=np.float32)
    next_state = np.zeros(n, dtype=np.float32)
    out_spmv = np.zeros(n, dtype=np.float32)
    trace = []

    t0 = time.perf_counter()
    for step in range(steps):
        external = np.zeros(n, dtype=np.float32)
        if step < 3:
            rng = np.random.default_rng(rng_seeds[step])
            external[input_neurons] = rng.normal(0.0, 0.5, size=input_neurons.size).astype(np.float32)

        if isinstance(op, CompactOperator4Bit):
            # Use fused kernel
            op.fused_step(state, next_state, external, gain=1.0, leak=0.2)
            state, next_state = next_state, state
        else:
            # SciPy CSR
            recurrent = op.dot(state)
            state = (0.8 * state + 0.2 * np.tanh(recurrent + external)).astype(np.float32)

        trace.append({
            "step": step,
            "l2": float(np.linalg.norm(state)),
            "active_gt_1e-6": int(np.count_nonzero(np.abs(state) > 1e-6)),
            "finite": bool(np.isfinite(state).all()),
        })

    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    return state.copy(), trace, elapsed_ms


def main():
    parser = argparse.ArgumentParser(description="Smoke test FlatBuffers .mcns vs graph.npz")
    parser.add_argument("--graph", type=Path, default=Path("artifacts/inputs/graph.npz"))
    parser.add_argument("--mcns", type=Path, default=Path("artifacts/flatbuffers/malecns_l3_compact.mcns"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/reports/smoke_mcns_comparison.json"))
    parser.add_argument("--steps", type=int, default=12)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    print(f"Loading FlatBuffers .mcns from {args.mcns}...")
    t_load_mcns = time.perf_counter()
    mcns_op = CompactOperator4Bit.from_flatbuffer(args.mcns)
    t_load_mcns = (time.perf_counter() - t_load_mcns) * 1e6
    print(f"Loaded .mcns in {t_load_mcns:.1f} us (Zero-Copy mmap)!")

    print(f"Loading raw graph from {args.graph}...")
    t_load_npz = time.perf_counter()
    raw_matrix = load_graph(args.graph)
    t_load_npz = (time.perf_counter() - t_load_npz) * 1000.0
    print(f"Loaded raw graph in {t_load_npz:.1f} ms.")

    n = raw_matrix.shape[0]
    rng = np.random.default_rng(args.seed)
    input_neurons = rng.choice(n, size=min(256, n), replace=False)
    rng_seeds = [int(s) for s in rng.integers(0, 100000, size=args.steps)]

    # Normalize raw matrix by row scale to match operator physics
    in_strength = np.asarray(np.abs(raw_matrix).sum(axis=1)).ravel()
    row_scales = (1.0 / np.maximum(in_strength, 1.0)).astype(np.float32)
    norm_matrix = raw_matrix.copy()
    norm_matrix.data *= np.repeat(row_scales, np.diff(raw_matrix.indptr))

    print(f"\nRunning {args.steps} steps on Raw Graph (SciPy FP32)...")
    state_raw, trace_raw, time_raw_ms = run_smoke_on_operator(norm_matrix, input_neurons, rng_seeds, args.steps)
    print(f"Raw Graph: {time_raw_ms:.2f} ms ({time_raw_ms / args.steps:.2f} ms/step), Final L2: {trace_raw[-1]['l2']:.4f}")

    print(f"\nRunning {args.steps} steps on FlatBuffers .mcns (4-bit LUT)...")
    state_mcns, trace_mcns, time_mcns_ms = run_smoke_on_operator(mcns_op, input_neurons, rng_seeds, args.steps)
    print(f"FlatBuffers: {time_mcns_ms:.2f} ms ({time_mcns_ms / args.steps:.2f} ms/step), Final L2: {trace_mcns[-1]['l2']:.4f}")

    # Compute correlation and similarity
    cos_sim = float(np.dot(state_raw, state_mcns) / (np.linalg.norm(state_raw) * np.linalg.norm(state_mcns) + 1e-9))
    diff_l2 = float(np.linalg.norm(state_raw - state_mcns))
    speedup = time_raw_ms / time_mcns_ms

    results = {
        "mcns_file": str(args.mcns),
        "graph_file": str(args.graph),
        "steps": args.steps,
        "neurons": n,
        "load_time_us_mcns": t_load_mcns,
        "load_time_ms_raw": t_load_npz,
        "time_raw_ms": time_raw_ms,
        "time_mcns_ms": time_mcns_ms,
        "speedup": speedup,
        "cosine_similarity": cos_sim,
        "diff_l2": diff_l2,
        "raw_activity_spread": int(max(t["active_gt_1e-6"] for t in trace_raw)),
        "mcns_activity_spread": int(max(t["active_gt_1e-6"] for t in trace_mcns)),
        "raw_finite": bool(trace_raw[-1]["finite"]),
        "mcns_finite": bool(trace_mcns[-1]["finite"]),
    }

    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY (FLATBUFFERS .MCNS VS RAW FP32)")
    print("=" * 60)
    print(f"Load Time:          .mcns = {t_load_mcns:.1f} us  |  raw = {t_load_npz:.1f} ms  ({t_load_npz * 1000 / t_load_mcns:.0f}x faster load)")
    print(f"Recurrent Step:     .mcns = {time_mcns_ms/args.steps:.2f} ms/step  |  raw = {time_raw_ms/args.steps:.2f} ms/step  ({speedup:.2f}x faster)")
    print(f"Activity Spread:    .mcns = {results['mcns_activity_spread']} neurons  |  raw = {results['raw_activity_spread']} neurons")
    print(f"Cosine Similarity:  {cos_sim:.4f}")
    print(f"State Stability:    Both Finite: {results['raw_finite'] and results['mcns_finite']}")
    print("=" * 60)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Report saved to {args.output}")


if __name__ == "__main__":
    main()
