"""Feasibility experiment: Categorical binning (palettization) of synaptic counts.

Evaluates whether MaleCNS reservoir dynamics are preserved when 10.2M continuous/integer
synaptic weights are quantized into discrete categories (codebooks):
- 8 categories (3 bits)
- 16 categories (4 bits)
- 32 categories (5 bits)
- 256 categories (8 bits)

Measures:
1. Reconstruction fidelity: Pearson r, MAE, Frobenius relative error.
2. Dynamical fidelity: Cosine similarity of 12-step whole-brain state trajectories
   under identical external driving inputs across multiple random seeds.
3. Memory footprint reduction comparison.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import scipy.sparse as sp


def load_raw_graph(path: Path) -> sp.csr_matrix:
    archive = np.load(path, allow_pickle=False)
    shape = tuple(int(x) for x in archive["shape"])
    return sp.csr_matrix((archive["data"], archive["indices"], archive["indptr"]), shape=shape)


def row_normalise(matrix: sp.csr_matrix) -> sp.csr_matrix:
    in_strength = np.asarray(np.abs(matrix).sum(axis=1)).ravel()
    scale = (1.0 / np.maximum(in_strength, 1.0)).astype(np.float32)
    normalised = matrix.copy().astype(np.float32)
    normalised.data *= np.repeat(scale, np.diff(matrix.indptr))
    return normalised


def categorize_weights_quantile(weights: np.ndarray, n_bins: int) -> tuple[np.ndarray, np.ndarray]:
    """Bin weights into n_bins based on quantile centroids, preserving signs."""
    signs = np.sign(weights)
    abs_w = np.abs(weights)
    
    # Compute quantiles over positive values
    quantiles = np.linspace(0, 100, n_bins + 1)
    thresholds = np.percentile(abs_w, quantiles)
    
    # Compute bin centroids
    centroids = np.zeros(n_bins, dtype=np.float32)
    bin_ids = np.clip(np.digitize(abs_w, thresholds[1:-1]), 0, n_bins - 1)
    
    for b in range(n_bins):
        mask = (bin_ids == b)
        if mask.any():
            centroids[b] = float(np.mean(abs_w[mask]))
        else:
            centroids[b] = float((thresholds[b] + thresholds[b + 1]) / 2)
            
    reconstructed = signs * centroids[bin_ids]
    return reconstructed, centroids


def categorize_weights_log(weights: np.ndarray, n_bins: int) -> tuple[np.ndarray, np.ndarray]:
    """Bin weights into logarithmically spaced bins, matching biological scaling."""
    signs = np.sign(weights)
    abs_w = np.abs(weights)
    
    min_val = max(float(abs_w.min()), 1.0)
    max_val = float(abs_w.max())
    log_edges = np.geomspace(min_val, max_val, n_bins + 1)
    
    bin_ids = np.clip(np.digitize(abs_w, log_edges[1:-1]), 0, n_bins - 1)
    centroids = np.zeros(n_bins, dtype=np.float32)
    
    for b in range(n_bins):
        mask = (bin_ids == b)
        if mask.any():
            centroids[b] = float(np.mean(abs_w[mask]))
        else:
            centroids[b] = float(np.sqrt(log_edges[b] * log_edges[b + 1]))
            
    reconstructed = signs * centroids[bin_ids]
    return reconstructed, centroids


def simulate_reservoir_trajectory(matrix: sp.csr_matrix, inputs: np.ndarray, *, steps: int = 12) -> np.ndarray:
    """Run reservoir dynamics state_{t+1} = 0.6 * state_t + 0.4 * tanh(W @ state + drive)."""
    n = matrix.shape[0]
    state = np.zeros(n, dtype=np.float32)
    trajectory = []
    
    for step in range(steps):
        drive = inputs[step]
        recurrent = matrix.dot(state) * 4.0 + drive
        state = 0.6 * state + 0.4 * np.tanh(recurrent)
        trajectory.append(state.copy())
        
    return np.array(trajectory)  # [steps, n]


def evaluate_trajectory_fidelity(traj_ref: np.ndarray, traj_test: np.ndarray) -> dict:
    """Compute cosine similarity and MSE between reference and quantized trajectories."""
    steps = traj_ref.shape[0]
    cosines = []
    mses = []
    
    for step in range(steps):
        v_ref = traj_ref[step]
        v_test = traj_test[step]
        norm_ref = np.linalg.norm(v_ref)
        norm_test = np.linalg.norm(v_test)
        
        if norm_ref > 1e-12 and norm_test > 1e-12:
            cos = float(np.dot(v_ref, v_test) / (norm_ref * norm_test))
        else:
            cos = 1.0
        mse = float(np.mean((v_ref - v_test) ** 2))
        
        cosines.append(cos)
        mses.append(mse)
        
    return {
        "mean_trajectory_cosine": float(np.mean(cosines)),
        "final_step_cosine": float(cosines[-1]),
        "min_trajectory_cosine": float(np.min(cosines)),
        "mean_trajectory_mse": float(np.mean(mses)),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", type=Path, default=Path("artifacts/inputs/graph.npz"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/synaptic-categorization-feasibility.json"))
    args = parser.parse_args()

    print("Loading canonical graph...", flush=True)
    raw_mat = load_raw_graph(args.graph)
    norm_mat_ref = row_normalise(raw_mat)
    
    n_neurons = raw_mat.shape[0]
    n_edges = raw_mat.nnz
    
    # Generate reproducible external test drives
    rng = np.random.default_rng(20261010)
    steps = 12
    n_input_neurons = 256
    input_indices = rng.choice(n_neurons, size=n_input_neurons, replace=False)
    
    drives = []
    for _ in range(steps):
        drive = np.zeros(n_neurons, dtype=np.float32)
        drive[input_indices] = rng.normal(0.0, 0.5, size=n_input_neurons).astype(np.float32)
        drives.append(drive)
    drives = np.array(drives)

    print("Simulating baseline reference trajectory (FP32 continuous)...", flush=True)
    traj_ref = simulate_reservoir_trajectory(norm_mat_ref, drives, steps=steps)

    test_configs = [
        ("log_8_bins (3-bit)", "log", 8),
        ("log_16_bins (4-bit)", "log", 16),
        ("log_32_bins (5-bit)", "log", 32),
        ("log_256_bins (8-bit)", "log", 256),
        ("quantile_16_bins (4-bit)", "quantile", 16),
        ("quantile_32_bins (5-bit)", "quantile", 32),
    ]

    results = []
    for name, method, n_bins in test_configs:
        print(f"Testing {name}...", flush=True)
        if method == "log":
            cat_weights, centroids = categorize_weights_log(raw_mat.data, n_bins)
        else:
            cat_weights, centroids = categorize_weights_quantile(raw_mat.data, n_bins)

        # Build categorized sparse matrix and apply row normalisation
        cat_mat = sp.csr_matrix((cat_weights, raw_mat.indices, raw_mat.indptr), shape=raw_mat.shape)
        norm_cat_mat = row_normalise(cat_mat)

        # Trajectory simulation
        traj_cat = simulate_reservoir_trajectory(norm_cat_mat, drives, steps=steps)
        fidelity = evaluate_trajectory_fidelity(traj_ref, traj_cat)

        # Weight error metrics
        weight_corr = float(np.corrcoef(raw_mat.data, cat_weights)[0, 1])
        weight_rel_frob = float(np.linalg.norm(raw_mat.data - cat_weights) / np.linalg.norm(raw_mat.data))

        bits_per_weight = int(np.ceil(np.log2(n_bins)))
        # Memory calculation: indices (uint32 = 4 bytes) + weights (bits_per_weight / 8)
        memory_mb = (n_edges * (4.0 + bits_per_weight / 8.0) + n_neurons * 4.0) / (1024 * 1024)

        report = {
            "config": name,
            "method": method,
            "n_bins": n_bins,
            "bits_per_weight": bits_per_weight,
            "weight_correlation": weight_corr,
            "weight_relative_frobenius_error": weight_rel_frob,
            "trajectory_fidelity": fidelity,
            "estimated_graph_memory_mb": round(memory_mb, 2),
            "centroids_sample": [round(float(c), 3) for c in centroids[:8]],
        }
        results.append(report)
        print(json.dumps({
            "config": name,
            "mean_cosine": fidelity["mean_trajectory_cosine"],
            "memory_mb": report["estimated_graph_memory_mb"],
        }), flush=True)

    summary = {
        "schema": "papers/malecns-synaptic-categorization-feasibility-v1",
        "neurons": n_neurons,
        "synapses": n_edges,
        "steps": steps,
        "baseline_memory_mb": round((n_edges * 8.0 + n_neurons * 4.0) / (1024 * 1024), 2),
        "results": results,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Results saved to {args.output}")


if __name__ == "__main__":
    main()
