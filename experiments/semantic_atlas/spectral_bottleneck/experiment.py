#!/usr/bin/env python3
"""Synthetic smoke test for spectral bottlenecks in the Semantic Atlas.

This is an implementation/protocol check, not evidence about language-model geometry.
It asks whether a label-blind normalized graph Laplacian can recover a planted
low-conductance bottleneck and distinguish it from a matched continuous control.
"""

from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import numpy as np
import scipy
from scipy.sparse import csr_matrix, diags, eye
from scipy.sparse.linalg import eigsh, spsolve
from scipy.spatial.distance import cdist


def make_bottleneck(seed: int, n_lobe: int = 180, n_bridge: int = 55):
    rng = np.random.default_rng(seed)
    left = rng.normal(loc=(-1.8, 0.0), scale=(0.65, 0.70), size=(n_lobe, 2))
    right = rng.normal(loc=(1.8, 0.0), scale=(0.65, 0.70), size=(n_lobe, 2))
    bridge_x = rng.uniform(-1.2, 1.2, size=n_bridge)
    bridge_y = rng.normal(0.0, 0.22, size=n_bridge)
    bridge = np.column_stack([bridge_x, bridge_y])
    points = np.vstack([left, bridge, right])
    planted_partition = (points[:, 0] >= 0.0).astype(np.int8)
    return points, planted_partition


def make_continuous_control(seed: int, n: int):
    rng = np.random.default_rng(seed)
    points = rng.normal(loc=(0.0, 0.0), scale=(1.35, 0.80), size=(n, 2))
    reference_partition = (points[:, 0] >= 0.0).astype(np.int8)
    return points, reference_partition


def knn_graph(points: np.ndarray, k: int) -> csr_matrix:
    if not 2 <= k < len(points):
        raise ValueError("k must be >= 2 and smaller than the sample size")
    distances = cdist(points, points)
    np.fill_diagonal(distances, np.inf)
    neighbors = np.argpartition(distances, kth=k - 1, axis=1)[:, :k]
    local_distances = np.take_along_axis(distances, neighbors, axis=1)
    sigma = float(np.median(local_distances[np.isfinite(local_distances)]))
    if not sigma > 0:
        raise ValueError("non-positive kernel scale")
    rows = np.repeat(np.arange(len(points)), k)
    cols = neighbors.ravel()
    edge_distances = distances[rows, cols]
    weights = np.exp(-(edge_distances**2) / (2.0 * sigma**2))
    directed = csr_matrix((weights, (rows, cols)), shape=(len(points), len(points)))
    graph = directed.maximum(directed.T)
    graph.setdiag(0.0)
    graph.eliminate_zeros()
    return graph


def conductance(graph: csr_matrix, mask: np.ndarray) -> float:
    degree = np.asarray(graph.sum(axis=1)).ravel()
    volume_left = float(degree[mask].sum())
    volume_right = float(degree[~mask].sum())
    denominator = min(volume_left, volume_right)
    if denominator <= 0:
        return float("inf")
    cut_weight = float(graph[mask][:, ~mask].sum())
    return cut_weight / denominator


def spectral_cut(graph: csr_matrix, min_fraction: float = 0.20):
    n = graph.shape[0]
    degree = np.asarray(graph.sum(axis=1)).ravel()
    if np.any(degree <= 0):
        raise ValueError("graph contains isolated vertices")
    inverse_sqrt_degree = 1.0 / np.sqrt(degree)
    laplacian = (
        eye(n, format="csr")
        - diags(inverse_sqrt_degree) @ graph @ diags(inverse_sqrt_degree)
    )
    values, vectors = eigsh(
        laplacian,
        k=3,
        which="SM",
        tol=1e-9,
        v0=np.ones(n, dtype=float),
    )
    order = np.argsort(values)
    values = values[order]
    fiedler = vectors[:, order[1]]

    sorted_nodes = np.argsort(fiedler)
    lower = max(1, int(np.ceil(min_fraction * n)))
    upper = min(n - 1, int(np.floor((1.0 - min_fraction) * n)))
    best_phi = float("inf")
    best_mask = None
    for cut_size in range(lower, upper + 1):
        mask = np.zeros(n, dtype=bool)
        mask[sorted_nodes[:cut_size]] = True
        phi = conductance(graph, mask)
        if phi < best_phi:
            best_phi = phi
            best_mask = mask
    if best_mask is None:
        raise RuntimeError("no admissible Fiedler sweep cut")
    return float(values[1]), float(best_phi), best_mask


def partition_accuracy(mask: np.ndarray, labels: np.ndarray) -> float:
    predicted = mask.astype(np.int8)
    direct = float(np.mean(predicted == labels))
    flipped = float(np.mean((1 - predicted) == labels))
    return max(direct, flipped)


def left_to_right_hitting_time(graph: csr_matrix, points: np.ndarray) -> float:
    """Expected random-walk steps from the far-left quartile to x >= 0."""
    degree = np.asarray(graph.sum(axis=1)).ravel()
    transition = diags(1.0 / degree) @ graph
    target = points[:, 0] >= 0.0
    source = ~target
    q_matrix = transition[source][:, source]
    system = eye(q_matrix.shape[0], format="csr") - q_matrix
    hitting = spsolve(system, np.ones(q_matrix.shape[0], dtype=float))
    source_x = points[source, 0]
    start_threshold = float(np.quantile(source_x, 0.25))
    starts = source_x <= start_threshold
    return float(np.mean(hitting[starts]))


def evaluate(points: np.ndarray, labels: np.ndarray, k: int):
    graph = knn_graph(points, k)
    lambda2, phi, mask = spectral_cut(graph)
    return {
        "lambda2": lambda2,
        "conductance": phi,
        "partition_accuracy": partition_accuracy(mask, labels),
        "left_to_right_hitting_time": left_to_right_hitting_time(graph, points),
    }


def median(records, key):
    return float(np.median([record[key] for record in records]))


def run(seeds: list[int], ks: list[int]):
    bottleneck_records = []
    control_records = []
    paired = []

    for seed in seeds:
        bottleneck_points, bottleneck_labels = make_bottleneck(seed)
        control_points, control_labels = make_continuous_control(
            seed + 10_000, len(bottleneck_points)
        )
        for k in ks:
            positive = evaluate(bottleneck_points, bottleneck_labels, k)
            negative = evaluate(control_points, control_labels, k)
            positive.update({"scenario": "bottleneck", "seed": seed, "k": k})
            negative.update({"scenario": "continuous_control", "seed": seed, "k": k})
            bottleneck_records.append(positive)
            control_records.append(negative)
            paired.append(
                {
                    "seed": seed,
                    "k": k,
                    "conductance_ratio": positive["conductance"]
                    / negative["conductance"],
                    "lambda2_ratio": positive["lambda2"] / negative["lambda2"],
                    "hitting_time_ratio": positive["left_to_right_hitting_time"]
                    / negative["left_to_right_hitting_time"],
                }
            )

    aggregate = {
        "median_bottleneck_conductance": median(bottleneck_records, "conductance"),
        "median_control_conductance": median(control_records, "conductance"),
        "median_conductance_ratio": median(paired, "conductance_ratio"),
        "median_bottleneck_lambda2": median(bottleneck_records, "lambda2"),
        "median_control_lambda2": median(control_records, "lambda2"),
        "median_lambda2_ratio": median(paired, "lambda2_ratio"),
        "median_bottleneck_partition_accuracy": median(
            bottleneck_records, "partition_accuracy"
        ),
        "median_hitting_time_ratio": median(paired, "hitting_time_ratio"),
        "robust_pair_fraction": float(
            np.mean(
                [
                    pair["conductance_ratio"] < 0.60
                    and pair["lambda2_ratio"] < 0.60
                    and pair["hitting_time_ratio"] > 2.0
                    for pair in paired
                ]
            )
        ),
    }

    gates = {
        "lower_conductance": aggregate["median_conductance_ratio"] < 0.50,
        "smaller_lambda2": aggregate["median_lambda2_ratio"] < 0.50,
        "recovers_planted_partition": aggregate[
            "median_bottleneck_partition_accuracy"
        ]
        >= 0.90,
        "higher_crossing_cost": aggregate["median_hitting_time_ratio"] > 2.0,
        "robust_across_seed_and_k": aggregate["robust_pair_fraction"] >= 0.80,
    }

    return {
        "claim_boundary": (
            "Synthetic implementation/protocol smoke test only. Passing does not "
            "show that language-model semantic states contain spectral bottlenecks."
        ),
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "design": {
            "seeds": seeds,
            "k_values": ks,
            "graph": "symmetric weighted kNN with Gaussian kernel",
            "operator": "normalized graph Laplacian",
            "cut": "label-blind balanced Fiedler sweep",
            "dynamic_check": "random-walk left-to-right expected hitting time",
        },
        "aggregate": aggregate,
        "gates": gates,
        "passed": all(gates.values()),
        "records": bottleneck_records + control_records,
        "paired": paired,
    }


def write_results(result, output: Path):
    output.mkdir(parents=True, exist_ok=True)
    (output / "summary.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    a = result["aggregate"]
    g = result["gates"]
    lines = [
        "# Spectral bottleneck smoke result",
        "",
        f"**Passed:** `{result['passed']}`",
        "",
        result["claim_boundary"],
        "",
        "## Aggregate",
        "",
        f"- median conductance ratio (bottleneck/control): `{a['median_conductance_ratio']:.4f}`",
        f"- median lambda2 ratio (bottleneck/control): `{a['median_lambda2_ratio']:.4f}`",
        f"- median Fiedler partition accuracy on planted bottleneck: `{a['median_bottleneck_partition_accuracy']:.4f}`",
        f"- median crossing hitting-time ratio: `{a['median_hitting_time_ratio']:.4f}`",
        f"- robust paired fraction: `{a['robust_pair_fraction']:.4f}`",
        "",
        "## Gates",
        "",
    ]
    lines.extend(f"- {'PASS' if ok else 'FAIL'} — `{name}`" for name, ok in g.items())
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            (
                "This workflow validates that the registered graph-Laplacian/Fiedler "
                "pipeline can detect a known synthetic bottleneck and reject a "
                "continuous control. It is not empirical evidence for the Semantic Atlas."
            ),
            "",
        ]
    )
    (output / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def parse_int_list(raw: str) -> list[int]:
    values = [int(item.strip()) for item in raw.split(",") if item.strip()]
    if not values:
        raise ValueError("empty integer list")
    return values


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", default="0,1,2,3,4")
    parser.add_argument("--k-values", default="8,12,16")
    parser.add_argument("--output", default="results")
    args = parser.parse_args()

    result = run(parse_int_list(args.seeds), parse_int_list(args.k_values))
    write_results(result, Path(args.output))
    print(
        json.dumps(
            {
                "aggregate": result["aggregate"],
                "gates": result["gates"],
                "passed": result["passed"],
            },
            indent=2,
        )
    )
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
