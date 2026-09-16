"""Fidelity and pruning exploration for MaleCNS cache-resident SpMV.

Evaluates recurrent dynamics fidelity (cosine similarity, Spearman correlation,
stability) across synaptic pruning thresholds and weight quantization schemes
against full-precision 10.23M FP32 baseline over 100 recurrent steps.
"""

from __future__ import annotations

import time
import numpy as np
import scipy.sparse as sp
from scipy.stats import spearmanr
from pathlib import Path

from malecns_wifi import load_graph
from malecns_wifi.tagger import row_normalise, select_populations


def make_pruned_matrix(raw: sp.csr_matrix, threshold: int) -> sp.csr_matrix:
    """Keep only edges where |data| >= threshold."""
    if threshold <= 3:
        return raw.copy()
    abs_d = np.abs(raw.data)
    mask = abs_d >= threshold
    new_data = raw.data[mask]
    new_indices = raw.indices[mask]
    # Rebuild indptr
    row_counts = np.add.reduceat(mask, raw.indptr[:-1])
    # When indptr has empty rows, add.reduceat works if indices are correct,
    # but safer to do it with diff:
    diffs = np.diff(raw.indptr)
    new_diffs = np.zeros_like(diffs)
    for r in range(len(diffs)):
        s = raw.indptr[r]
        e = raw.indptr[r+1]
        new_diffs[r] = np.count_nonzero(mask[s:e])
    new_indptr = np.zeros(len(raw.indptr), dtype=np.int32)
    new_indptr[1:] = np.cumsum(new_diffs)
    return sp.csr_matrix((new_data, new_indices, new_indptr), shape=raw.shape)


def make_ternary_matrix(pruned: sp.csr_matrix) -> sp.csr_matrix:
    """Replace weights with their signs {-1, +1}."""
    tern = pruned.copy()
    tern.data = np.sign(tern.data).astype(np.float32)
    return tern


def run_recurrence(operator: sp.csr_matrix, input_indices: np.ndarray, steps: int = 100, seed: int = 42):
    n = operator.shape[0]
    rng = np.random.default_rng(seed)
    state = np.zeros(n, dtype=np.float32)
    # Sensory drive sequence
    num_inputs = len(input_indices)
    history = []
    
    # Pre-generate inputs for repeatability
    inputs_seq = rng.normal(0.0, 0.05, size=(steps, num_inputs)).astype(np.float32)
    
    drive = np.zeros(n, dtype=np.float32)
    for t in range(steps):
        drive[input_indices] = inputs_seq[t]
        pre = (operator @ state) * np.float32(4.0) + drive
        state = 0.6 * state + 0.4 * np.tanh(pre)
        if t in (9, 24, 49, 99):
            history.append(state.copy())
    return history


def main():
    graph_path = Path("artifacts/inputs/graph.npz")
    print("Loading graph.npz...")
    raw = load_graph(graph_path)
    archive = np.load(graph_path)
    pops = select_populations(archive["superclass"])
    input_indices = pops.input_indices
    readout_indices = pops.readout_indices
    print(f"Graph loaded: N={raw.shape[0]}, NNZ={raw.nnz}, inputs={len(input_indices)}, readouts={len(readout_indices)}")

    print("\n--- Running FP32 Baseline (10.23M edges) ---")
    t0 = time.perf_counter()
    base_op = row_normalise(raw)
    base_hist = run_recurrence(base_op, input_indices, steps=100)
    t_base = time.perf_counter() - t0
    print(f"Base run 100 steps took {t_base:.2f}s. State L2 norm at t=100: {np.linalg.norm(base_hist[-1]):.3f}")

    thresholds = [4, 5, 6, 7, 8, 10, 12, 15]
    print(f"\n{'Thresh':<7} {'Type':<8} {'NNZ':<10} {'Mem(MB)':<9} {'Cos@10':<8} {'Cos@25':<8} {'Cos@50':<8} {'Cos@100':<8} {'Spearman@100':<13} {'ReadoutCos':<11}")
    print("-" * 95)

    for th in thresholds:
        pruned = make_pruned_matrix(raw, th)
        nnz = pruned.nnz
        # Continuous normalized
        op_pruned = row_normalise(pruned)
        mem_mb = (nnz * 8 + (pruned.shape[0] + 1) * 4) / (1024 * 1024)
        hist = run_recurrence(op_pruned, input_indices, steps=100)

        cosines = []
        for h_b, h_p in zip(base_hist, hist):
            cos = float(np.dot(h_b, h_p) / (np.linalg.norm(h_b) * np.linalg.norm(h_p) + 1e-12))
            cosines.append(cos)
        sp_corr, _ = spearmanr(base_hist[-1], hist[-1])
        readout_cos = float(np.dot(base_hist[-1][readout_indices], hist[-1][readout_indices]) / 
                            (np.linalg.norm(base_hist[-1][readout_indices]) * np.linalg.norm(hist[-1][readout_indices]) + 1e-12))

        print(f"{th:<7} {'float':<8} {nnz:<10} {mem_mb:<9.2f} {cosines[0]:<8.4f} {cosines[1]:<8.4f} {cosines[2]:<8.4f} {cosines[3]:<8.4f} {sp_corr:<13.4f} {readout_cos:<11.4f}")

        # Ternary normalized
        tern = make_ternary_matrix(pruned)
        op_tern = row_normalise(tern)
        # Memory if ternary: 1 bit per weight + 16-bit delta
        tern_mem_mb = (nnz * 2.125 + (pruned.shape[0] + 1) * 4) / (1024 * 1024)
        hist_t = run_recurrence(op_tern, input_indices, steps=100)

        cosines_t = []
        for h_b, h_p in zip(base_hist, hist_t):
            cos = float(np.dot(h_b, h_p) / (np.linalg.norm(h_b) * np.linalg.norm(h_p) + 1e-12))
            cosines_t.append(cos)
        sp_corr_t, _ = spearmanr(base_hist[-1], hist_t[-1])
        readout_cos_t = float(np.dot(base_hist[-1][readout_indices], hist_t[-1][readout_indices]) / 
                              (np.linalg.norm(base_hist[-1][readout_indices]) * np.linalg.norm(hist_t[-1][readout_indices]) + 1e-12))

        print(f"{th:<7} {'ternary':<8} {nnz:<10} {tern_mem_mb:<9.2f} {cosines_t[0]:<8.4f} {cosines_t[1]:<8.4f} {cosines_t[2]:<8.4f} {cosines_t[3]:<8.4f} {sp_corr_t:<13.4f} {readout_cos_t:<11.4f}")


if __name__ == "__main__":
    main()
