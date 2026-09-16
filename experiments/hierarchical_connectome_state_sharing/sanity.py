# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "scipy>=1.13"]
# ///

"""Synthetic sanity check for hierarchical connectome state sharing.

This is intentionally NOT a MaleCNS result. It tests whether representative
state sharing behaves numerically as expected in a favorable clustered regime,
and separately measures only the sparse recurrent multiply opportunity.
"""

from __future__ import annotations

import json
import platform
import statistics
import sys
import time

import numpy as np
import scipy
from scipy import sparse


def build_operator(rng, n=2048, avg_degree=10, gain=0.9):
    e = n * avg_degree
    rows = rng.integers(0, n, size=e)
    cols = rng.integers(0, n, size=e)
    vals = rng.normal(size=e).astype(np.float32)
    w = sparse.csr_matrix((vals, (rows, cols)), shape=(n, n), dtype=np.float32)
    row_abs = np.asarray(np.abs(w).sum(axis=1)).ravel()
    w = sparse.diags((gain / np.maximum(row_abs, 1)).astype(np.float32)) @ w
    return w.tocsr()


def step(w, x, u, leak=0.35):
    return (1 - leak) * x + leak * np.tanh(w @ x + u)


def rel_rmse(a, b):
    rmse = np.sqrt(np.mean((a - b) ** 2))
    rms = np.sqrt(np.mean(a * a))
    return float(rmse / (rms + 1e-12))


def mean_cos(a, b):
    dot = np.sum(a * b, axis=0)
    den = np.linalg.norm(a, axis=0) * np.linalg.norm(b, axis=0) + 1e-12
    return float(np.mean(dot / den))


def median_time(fn, reps):
    values = []
    for _ in range(reps):
        t0 = time.perf_counter()
        fn()
        values.append(time.perf_counter() - t0)
    return statistics.median(values)


def main():
    seed = 42
    rng = np.random.default_rng(seed)

    n = 2048
    agents = 512
    clusters = 16
    avg_degree = 10
    leak = 0.35

    w = build_operator(rng, n=n, avg_degree=avg_degree, gain=0.9)
    labels = rng.integers(0, clusters, size=agents)
    centroids0 = rng.normal(0, 0.4, size=(n, clusters)).astype(np.float32)
    drive_centroids = rng.normal(0, 0.08, size=(n, clusters)).astype(np.float32)

    accuracy = {}
    for sigma in (0.005, 0.02, 0.05, 0.1):
        rr = np.random.default_rng(seed + int(sigma * 10000))
        exact = centroids0[:, labels] + rr.normal(0, sigma, size=(n, agents)).astype(np.float32)
        reps = centroids0.copy()
        first = None

        for t in range(30):
            drive = drive_centroids[:, labels] + rr.normal(
                0, sigma * 0.1, size=(n, agents)
            ).astype(np.float32)
            exact = step(w, exact, drive, leak)
            reps = step(w, reps, drive_centroids, leak)
            approx = reps[:, labels]
            if t == 0:
                first = (rel_rmse(exact, approx), mean_cos(exact, approx))

        accuracy[str(sigma)] = {
            "rel_rmse_step1": first[0],
            "cos_step1": first[1],
            "rel_rmse_step30": rel_rmse(exact, approx),
            "cos_step30": mean_cos(exact, approx),
        }

    rr = np.random.default_rng(7)
    n2 = 8192
    agents2 = 1024
    reps2 = 32
    w2 = build_operator(rr, n=n2, avg_degree=10, gain=0.9)
    x2 = rr.normal(0, 0.4, size=(n2, agents2)).astype(np.float32)
    r2 = rr.normal(0, 0.4, size=(n2, reps2)).astype(np.float32)
    _ = w2 @ x2
    _ = w2 @ r2
    full_t = median_time(lambda: w2 @ x2, 7)
    rep_t = median_time(lambda: w2 @ r2, 15)

    result = {
        "kind": "synthetic exploratory sanity check (not MaleCNS)",
        "seed": seed,
        "dynamics": {
            "n": n,
            "agents": agents,
            "latent_clusters": clusters,
            "avg_degree": avg_degree,
            "steps": 30,
            "leak": leak,
            "row_l1_gain": 0.9,
        },
        "approximation": "fixed known latent cluster centroids; individual residuals omitted",
        "accuracy": accuracy,
        "kernel_benchmark": {
            "n": n2,
            "agents": agents2,
            "representatives": reps2,
            "avg_degree": 10,
            "full_spmm_seconds_median": full_t,
            "representative_spmm_seconds_median": rep_t,
            "pure_spmm_speedup": full_t / rep_t,
        },
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "platform": platform.platform(),
        },
        "claim_boundary": (
            "This validates only the algebra/code path in a favorable synthetic clustered regime. "
            "It is not evidence that MaleCNS ensemble states cluster this way and is not an end-to-end "
            "speedup benchmark; clustering, centroid maintenance, reconstruction, and outputs are excluded "
            "from the timing."
        ),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
