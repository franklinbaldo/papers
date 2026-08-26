from __future__ import annotations

import argparse
import json
from pathlib import Path

import numba as nb
import numpy as np


KS = np.asarray([3, 5, 10], dtype=np.int64)
MKNN_KS = np.asarray([1, 2, 3, 5, 8, 10, 15, 20], dtype=np.int64)


def load_observer(cache_dir: Path) -> tuple[np.ndarray, list[str]]:
    npz_path = next(cache_dir.glob("*.npz"))
    manifest_path = next(cache_dir.glob("*.json"))
    data = np.load(npz_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    splits = ("calibration", "heldout", "trajectory")
    matrix = np.vstack([data[f"normalized_{split}"] for split in splits]).astype(np.float64)
    paths = [item["path"] for split in splits for item in manifest["corpus"][split]]
    return matrix, paths


def rankings(matrix: np.ndarray) -> np.ndarray:
    scores = matrix @ matrix.T
    np.fill_diagonal(scores, -np.inf)
    return np.argsort(-scores, axis=1, kind="stable").astype(np.int64)


@nb.njit
def hazards_for_model(rankings_: np.ndarray, order: np.ndarray, ks: np.ndarray) -> np.ndarray:
    n = len(order)
    positions = np.empty(n, np.int64)
    for pos in range(n):
        positions[order[pos]] = pos
    n_steps = (n - 24 + 3) // 4
    out = np.zeros((len(ks), n_steps), np.float64)
    prev_n = 24
    step = 0
    while prev_n < n:
        cur_n = min(prev_n + 4, n)
        added = cur_n - prev_n
        expected = added / (prev_n - 1 + added)
        for k_idx in range(len(ks)):
            k = ks[k_idx]
            total_new = 0
            for anchor_pos in range(prev_n):
                anchor = order[anchor_pos]
                found = 0
                for rank_pos in range(n):
                    candidate = rankings_[anchor, rank_pos]
                    candidate_pos = positions[candidate]
                    if candidate_pos < cur_n:
                        found += 1
                        if candidate_pos >= prev_n:
                            total_new += 1
                        if found == k:
                            break
            mean_churn = total_new / (prev_n * k)
            out[k_idx, step] = mean_churn / expected
        prev_n = cur_n
        step += 1
    return out


@nb.njit
def divergence_for_order(
    rank_a: np.ndarray,
    rank_b: np.ndarray,
    order: np.ndarray,
    ks: np.ndarray,
) -> np.ndarray:
    a = hazards_for_model(rank_a, order, ks)
    b = hazards_for_model(rank_b, order, ks)
    out = np.empty(len(ks), np.float64)
    for k_idx in range(len(ks)):
        total = 0.0
        for step in range(a.shape[1]):
            total += abs(a[k_idx, step] - b[k_idx, step])
        out[k_idx] = total / a.shape[1]
    return out


@nb.njit
def semantic_drift_for_order(
    matrix_a: np.ndarray,
    matrix_b: np.ndarray,
    order: np.ndarray,
) -> float:
    n = len(order)
    sum_a = np.zeros(matrix_a.shape[1], np.float64)
    sum_b = np.zeros(matrix_b.shape[1], np.float64)
    for pos in range(24):
        idx = order[pos]
        for dim in range(matrix_a.shape[1]):
            sum_a[dim] += matrix_a[idx, dim]
        for dim in range(matrix_b.shape[1]):
            sum_b[dim] += matrix_b[idx, dim]

    total = 0.0
    steps = 0
    prev_n = 24
    while prev_n < n:
        cur_n = min(prev_n + 4, n)
        batch_a = np.zeros(matrix_a.shape[1], np.float64)
        batch_b = np.zeros(matrix_b.shape[1], np.float64)
        for pos in range(prev_n, cur_n):
            idx = order[pos]
            for dim in range(matrix_a.shape[1]):
                batch_a[dim] += matrix_a[idx, dim]
            for dim in range(matrix_b.shape[1]):
                batch_b[dim] += matrix_b[idx, dim]

        dot_a = 0.0
        norm_a = 0.0
        norm_batch_a = 0.0
        for dim in range(matrix_a.shape[1]):
            dot_a += sum_a[dim] * batch_a[dim]
            norm_a += sum_a[dim] * sum_a[dim]
            norm_batch_a += batch_a[dim] * batch_a[dim]

        dot_b = 0.0
        norm_b = 0.0
        norm_batch_b = 0.0
        for dim in range(matrix_b.shape[1]):
            dot_b += sum_b[dim] * batch_b[dim]
            norm_b += sum_b[dim] * sum_b[dim]
            norm_batch_b += batch_b[dim] * batch_b[dim]

        cosine_a = dot_a / (np.sqrt(norm_a * norm_batch_a) + 1e-18)
        cosine_b = dot_b / (np.sqrt(norm_b * norm_batch_b) + 1e-18)
        total += 0.5 * ((1.0 - cosine_a) + (1.0 - cosine_b))

        for dim in range(matrix_a.shape[1]):
            sum_a[dim] += batch_a[dim]
        for dim in range(matrix_b.shape[1]):
            sum_b[dim] += batch_b[dim]

        steps += 1
        prev_n = cur_n
    return total / steps


@nb.njit
def weighted_hazard(
    rankings_: np.ndarray,
    order: np.ndarray,
    weights: np.ndarray,
    k: int = 5,
) -> np.ndarray:
    n = len(order)
    positions = np.empty(n, np.int64)
    for pos in range(n):
        positions[order[pos]] = pos
    out = np.empty((n - 24 + 3) // 4, np.float64)
    prev_n = 24
    step = 0
    while prev_n < n:
        cur_n = min(prev_n + 4, n)
        added = cur_n - prev_n
        weighted_churn = 0.0
        weight_sum = 0.0
        for anchor_pos in range(prev_n):
            anchor = order[anchor_pos]
            weight = weights[anchor]
            if weight <= 0:
                continue
            found = 0
            new_count = 0
            for rank_pos in range(n):
                candidate = rankings_[anchor, rank_pos]
                candidate_pos = positions[candidate]
                if candidate_pos < cur_n:
                    found += 1
                    if candidate_pos >= prev_n:
                        new_count += 1
                    if found == k:
                        break
            weighted_churn += weight * (new_count / k)
            weight_sum += weight
        expected = added / (prev_n - 1 + added)
        out[step] = (weighted_churn / weight_sum) / expected
        prev_n = cur_n
        step += 1
    return out


@nb.njit
def same_observer_d(
    rankings_: np.ndarray,
    order: np.ndarray,
    first_weights: np.ndarray,
    second_weights: np.ndarray,
) -> float:
    first = weighted_hazard(rankings_, order, first_weights)
    second = weighted_hazard(rankings_, order, second_weights)
    total = 0.0
    for idx in range(len(first)):
        total += abs(first[idx] - second[idx])
    return total / len(first)


@nb.njit
def mknn_permuted(
    rank_a: np.ndarray,
    rank_b: np.ndarray,
    permutation: np.ndarray,
    ks: np.ndarray,
) -> np.ndarray:
    n = len(permutation)
    inverse = np.empty(n, np.int64)
    for idx in range(n):
        inverse[permutation[idx]] = idx
    out = np.zeros(len(ks), np.float64)
    for query in range(n):
        for k_idx in range(len(ks)):
            k = ks[k_idx]
            intersection = 0
            for left in range(k):
                a_id = rank_a[query, left]
                for right in range(k):
                    b_id = inverse[rank_b[permutation[query], right]]
                    if a_id == b_id:
                        intersection += 1
                        break
            out[k_idx] += intersection / k
    for k_idx in range(len(ks)):
        out[k_idx] /= n
    return out


def upper_p(observed: float, null: np.ndarray) -> float:
    return float((1 + np.count_nonzero(null >= observed)) / (len(null) + 1))


def summarize(observed: float, null: np.ndarray) -> dict[str, float]:
    return {
        "observed": float(observed),
        "null_mean": float(null.mean()),
        "null_sd": float(null.std(ddof=1)),
        "null_q95": float(np.quantile(null, 0.95)),
        "null_max": float(null.max()),
        "p_upper_plus1": upper_p(observed, null),
    }


def mknn_full(rank_a: np.ndarray, rank_b: np.ndarray, k: int) -> float:
    left = rank_a[:, :k]
    right = rank_b[:, :k]
    overlap = (left[:, :, None] == right[:, None, :]).any(axis=2).sum(axis=1)
    return float(np.mean(overlap / k))


def first_churn_times(rankings_: np.ndarray, order: np.ndarray, k: int = 5) -> dict[int, int | None]:
    n = len(order)
    positions = np.empty(n, dtype=np.int64)
    positions[order] = np.arange(n)
    anchors = order[:24]
    first: dict[int, int | None] = {int(anchor): None for anchor in anchors}
    prev_n = 24
    while prev_n < n:
        cur_n = min(prev_n + 4, n)
        for anchor in anchors:
            anchor_id = int(anchor)
            if first[anchor_id] is not None:
                continue
            found = 0
            new_count = 0
            for candidate in rankings_[anchor]:
                candidate_pos = positions[candidate]
                if candidate_pos < cur_n:
                    found += 1
                    if candidate_pos >= prev_n:
                        new_count += 1
                    if found == k:
                        break
            if new_count:
                first[anchor_id] = cur_n - 24
        prev_n = cur_n
    return first


def kaplan_meier(first: dict[int, int | None]) -> dict:
    event_times = sorted({value for value in first.values() if value is not None})
    survival = 1.0
    curve = [{"added_docs": 0, "survival": 1.0}]
    for time in event_times:
        at_risk = sum(value is None or value >= time for value in first.values())
        events = sum(value == time for value in first.values())
        survival *= 1.0 - events / at_risk
        curve.append({"added_docs": int(time), "survival": float(survival)})
    median = next((row["added_docs"] for row in curve if row["survival"] <= 0.5), None)
    return {
        "anchor_count": len(first),
        "events": sum(value is not None for value in first.values()),
        "censored": sum(value is None for value in first.values()),
        "censored_fraction": float(np.mean([value is None for value in first.values()])),
        "km_median_added_docs": median,
        "curve": curve,
    }


def run(artifact_dir: Path, output: Path, permutations: int) -> dict:
    parent = json.loads((artifact_dir / "relational_dynamics_v1.json").read_text(encoding="utf-8"))
    ref, ref_paths = load_observer(artifact_dir / "embedding_cache_relational_v1" / "reference_observer")
    transfer, transfer_paths = load_observer(
        artifact_dir / "embedding_cache_relational_v1" / "transfer_observer"
    )
    if ref_paths != transfer_paths:
        raise RuntimeError("observer corpus paths differ")
    path_to_idx = {path: idx for idx, path in enumerate(ref_paths)}
    chronology = np.asarray(
        [path_to_idx[row["path"]] for row in sorted(parent["chronology"], key=lambda row: row["rank"])],
        dtype=np.int64,
    )
    rank_ref = rankings(ref)
    rank_transfer = rankings(transfer)

    # Compile before repeated use.
    divergence_for_order(rank_ref, rank_transfer, chronology, KS)
    semantic_drift_for_order(ref, transfer, chronology)
    mknn_permuted(rank_ref, rank_transfer, np.arange(len(chronology)), MKNN_KS)
    ones = np.ones(len(chronology), dtype=np.float64)
    same_observer_d(rank_ref, chronology, ones, ones)

    rng = np.random.default_rng(20260825)
    orders = np.empty((permutations, len(chronology)), dtype=np.int64)
    for idx in range(permutations):
        orders[idx] = rng.permutation(len(chronology))

    observed_d = divergence_for_order(rank_ref, rank_transfer, chronology, KS)
    null_d = np.empty((permutations, len(KS)), dtype=np.float64)
    drift_null = np.empty(permutations, dtype=np.float64)
    for idx in range(permutations):
        null_d[idx] = divergence_for_order(rank_ref, rank_transfer, orders[idx], KS)
        drift_null[idx] = semantic_drift_for_order(ref, transfer, orders[idx])
    observed_drift = semantic_drift_for_order(ref, transfer, chronology)

    k5_null = null_d[:, 1]
    critical = float(np.quantile(k5_null, 0.95))
    q20 = float(np.quantile(k5_null, 0.20))
    mde = critical - q20
    observed_excess = float(observed_d[1] - k5_null.mean())

    rng_boot = np.random.default_rng(20260826)
    ref_same_random = np.empty(permutations, dtype=np.float64)
    transfer_same_random = np.empty(permutations, dtype=np.float64)
    ref_same_chron = np.empty(permutations, dtype=np.float64)
    transfer_same_chron = np.empty(permutations, dtype=np.float64)
    for idx in range(permutations):
        first = rng_boot.poisson(1.0, size=len(chronology)).astype(np.float64)
        second = rng_boot.poisson(1.0, size=len(chronology)).astype(np.float64)
        ref_same_random[idx] = same_observer_d(rank_ref, orders[idx], first, second)
        transfer_same_random[idx] = same_observer_d(rank_transfer, orders[idx], first, second)
    rng_boot = np.random.default_rng(20260826)
    for idx in range(permutations):
        first = rng_boot.poisson(1.0, size=len(chronology)).astype(np.float64)
        second = rng_boot.poisson(1.0, size=len(chronology)).astype(np.float64)
        ref_same_chron[idx] = same_observer_d(rank_ref, chronology, first, second)
        transfer_same_chron[idx] = same_observer_d(rank_transfer, chronology, first, second)

    rng_mknn = np.random.default_rng(20260826)
    observed_mknn = mknn_permuted(
        rank_ref, rank_transfer, np.arange(len(chronology)), MKNN_KS
    )
    null_mknn = np.empty((permutations, len(MKNN_KS)), dtype=np.float64)
    for idx in range(permutations):
        null_mknn[idx] = mknn_permuted(
            rank_ref,
            rank_transfer,
            rng_mknn.permutation(len(chronology)),
            MKNN_KS,
        )
    mknn_stats = {}
    for k_idx, k in enumerate(MKNN_KS):
        null = null_mknn[:, k_idx]
        combined = np.concatenate(([observed_mknn[k_idx]], null))
        tau = float(np.quantile(combined, 0.95))
        mknn_stats[str(int(k))] = {
            "observed": float(observed_mknn[k_idx]),
            "null_mean": float(null.mean()),
            "tau95": tau,
            "p_upper_plus1": upper_p(float(observed_mknn[k_idx]), null),
            "calibrated_score": max(
                (float(observed_mknn[k_idx]) - tau) / (1.0 - tau), 0.0
            ),
        }

    result = {
        "schema_version": 1,
        "kind": "posthoc-robustness-reanalysis",
        "parent_experiment": parent["experiment"],
        "claim_boundary": (
            "Post-hoc robustness and power analysis. It may narrow or qualify the "
            "interpretation of v1 but cannot convert the preregistered chronology-specific "
            "test into a confirmation."
        ),
        "permutation_refinement": {
            "n_permutations": permutations,
            "seed": 20260825,
            "semantic_drift": summarize(observed_drift, drift_null),
            "chronology_specific_dynamic_divergence": {
                str(int(k)): summarize(float(observed_d[k_idx]), null_d[:, k_idx])
                for k_idx, k in enumerate(KS)
            },
        },
        "power": {
            "target": "k=5 additive location-shift alternative on the 10,000-permutation D null",
            "alpha": 0.05,
            "target_power": 0.8,
            "critical_q95": critical,
            "null_q20": q20,
            "mde_absolute_D": mde,
            "mde_relative_to_null_mean": mde / float(k5_null.mean()),
            "observed_excess_absolute_D": observed_excess,
            "observed_excess_relative_to_null_mean": observed_excess / float(k5_null.mean()),
            "estimated_power_at_observed_shift": float(
                np.mean(k5_null + observed_excess > critical)
            ),
        },
        "same_observer_anchor_bootstrap": {
            "method": (
                "Poisson(1) document-anchor bootstrap. Candidate geometry/order remain "
                "unchanged; independent weights perturb only which present anchors estimate "
                "each hazard. This is an estimator-stability reference, not encoder-seed variability."
            ),
            "n_replicates": permutations,
            "chronological_order": {
                "reference": {
                    "mean": float(ref_same_chron.mean()),
                    "q95": float(np.quantile(ref_same_chron, 0.95)),
                    "q99": float(np.quantile(ref_same_chron, 0.99)),
                    "fraction_ge_cross_model_observed": float(
                        np.mean(ref_same_chron >= observed_d[1])
                    ),
                },
                "transfer": {
                    "mean": float(transfer_same_chron.mean()),
                    "q95": float(np.quantile(transfer_same_chron, 0.95)),
                    "q99": float(np.quantile(transfer_same_chron, 0.99)),
                    "fraction_ge_cross_model_observed": float(
                        np.mean(transfer_same_chron >= observed_d[1])
                    ),
                },
            },
            "random_order": {
                "reference_mean": float(ref_same_random.mean()),
                "reference_q95": float(np.quantile(ref_same_random, 0.95)),
                "transfer_mean": float(transfer_same_random.mean()),
                "transfer_q95": float(np.quantile(transfer_same_random, 0.95)),
                "cross_model_random_order_D_mean": float(k5_null.mean()),
            },
        },
        "mknn": {
            "definition": "mean_i |N_k^reference(i) intersect N_k^transfer(i)| / k",
            "permutation_calibration": mknn_stats,
            "full_gallery_curve": {
                str(k): mknn_full(rank_ref, rank_transfer, k)
                for k in (1, 2, 3, 5, 8, 10, 15, 20, 30, 40, 50)
            },
        },
        "resolution_kaplan_meier": {
            "k": 5,
            "reference": kaplan_meier(first_churn_times(rank_ref, chronology)),
            "transfer": kaplan_meier(first_churn_times(rank_transfer, chronology)),
        },
        "literature": {
            "Huh2024": (
                "Minyoung Huh, Brian Cheung, Tongzhou Wang, Phillip Isola. "
                "Position: The Platonic Representation Hypothesis. ICML 2024, PMLR 235."
            ),
            "Groeger2026": (
                "Fabian Gröger, Shuo Wen, Maria Brbić. Revisiting the Platonic "
                "Representation Hypothesis: An Aristotelian View. ICML 2026, arXiv:2602.14486."
            ),
            "Koepke2026": (
                "A. Sophia Koepke, Daniil Zverev, Shiry Ginosar, Alexei A. Efros. "
                "Back into Plato's Cave: Examining Cross-modal Representational Convergence "
                "at Scale. arXiv:2604.18572v2."
            ),
            "Klabunde2023": (
                "Max Klabunde, Tobias Schumacher, Markus Strohmaier, Florian Lemmerich. "
                "Similarity of Neural Network Models: A Survey of Functional and "
                "Representational Measures. arXiv:2305.06329; ACM Computing Surveys 57(9)."
            ),
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/relational_dynamics_v1_reanalysis.json"),
    )
    parser.add_argument("--permutations", type=int, default=10_000)
    args = parser.parse_args()
    result = run(args.artifact_dir, args.output, args.permutations)
    print(
        json.dumps(
            {
                "semantic_drift": result["permutation_refinement"]["semantic_drift"],
                "D_k5": result["permutation_refinement"][
                    "chronology_specific_dynamic_divergence"
                ]["5"],
                "power": result["power"],
                "mknn_k5": result["mknn"]["permutation_calibration"]["5"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
