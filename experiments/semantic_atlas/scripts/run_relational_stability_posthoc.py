from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

INITIAL_N = 24
K = 5
RMST_PERMUTATIONS = 100_000
SEED = 20260826


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
    return np.argsort(-scores, axis=1, kind="stable")


def chronology_from_parent(parent: dict, paths: list[str]) -> np.ndarray:
    path_to_idx = {path: idx for idx, path in enumerate(paths)}
    return np.asarray(
        [
            path_to_idx[row["path"]]
            for row in sorted(parent["chronology"], key=lambda row: row["rank"])
        ],
        dtype=np.int64,
    )


def first_churn_times(
    rankings_: np.ndarray, order: np.ndarray, k: int = K
) -> dict[int, int | None]:
    n = len(order)
    positions = np.empty(n, dtype=np.int64)
    positions[order] = np.arange(n)
    anchors = order[:INITIAL_N]
    first: dict[int, int | None] = {int(anchor): None for anchor in anchors}
    prev_n = INITIAL_N
    while prev_n < n:
        cur_n = min(prev_n + 4, n)
        for anchor in anchors:
            anchor_id = int(anchor)
            if first[anchor_id] is not None:
                continue
            found = 0
            changed = False
            for candidate in rankings_[anchor]:
                candidate_pos = positions[candidate]
                if candidate_pos < cur_n:
                    found += 1
                    if candidate_pos >= prev_n:
                        changed = True
                    if found == k:
                        break
            if changed:
                first[anchor_id] = cur_n - INITIAL_N
        prev_n = cur_n
    return first


def event_arrays(
    first: dict[int, int | None], anchors: np.ndarray, tau: int
) -> tuple[np.ndarray, np.ndarray]:
    durations = np.asarray(
        [first[int(anchor)] if first[int(anchor)] is not None else tau for anchor in anchors],
        dtype=np.float64,
    )
    events = np.asarray([first[int(anchor)] is not None for anchor in anchors], dtype=bool)
    return durations, events


def km_summary(durations: np.ndarray, events: np.ndarray, tau: int) -> dict:
    event_times = sorted(
        set(float(d) for d, e in zip(durations, events) if e and d <= tau)
    )
    survival = 1.0
    curve = [{"added_docs": 0, "survival": 1.0}]
    area = 0.0
    prev_t = 0.0
    median = None
    for time in event_times:
        area += survival * (time - prev_t)
        at_risk = int(np.count_nonzero(durations >= time))
        observed = int(np.count_nonzero((durations == time) & events))
        survival *= 1.0 - observed / at_risk
        curve.append({"added_docs": int(time), "survival": float(survival)})
        if median is None and survival <= 0.5:
            median = int(time)
        prev_t = time
    area += survival * (tau - prev_t)
    return {
        "n": int(len(durations)),
        "events": int(np.count_nonzero(events)),
        "censored": int(len(durations) - np.count_nonzero(events)),
        "censored_fraction": float(1.0 - np.mean(events)),
        "km_median_added_docs": median,
        "rmst_to_tau": float(area),
        "tau_added_docs": int(tau),
        "curve": curve,
    }


def paired_rmst_permutation(
    ref_durations: np.ndarray,
    ref_events: np.ndarray,
    transfer_durations: np.ndarray,
    transfer_events: np.ndarray,
    tau: int,
    permutations: int = RMST_PERMUTATIONS,
    seed: int = SEED,
) -> dict:
    ref_rmst = km_summary(ref_durations, ref_events, tau)["rmst_to_tau"]
    transfer_rmst = km_summary(transfer_durations, transfer_events, tau)["rmst_to_tau"]
    observed = ref_rmst - transfer_rmst
    rng = np.random.default_rng(seed)
    null = np.empty(permutations, dtype=np.float64)
    for idx in range(permutations):
        swap = rng.integers(0, 2, size=len(ref_durations), dtype=np.int8).astype(bool)
        first_d = np.where(swap, transfer_durations, ref_durations)
        first_e = np.where(swap, transfer_events, ref_events)
        second_d = np.where(swap, ref_durations, transfer_durations)
        second_e = np.where(swap, ref_events, transfer_events)
        null[idx] = (
            km_summary(first_d, first_e, tau)["rmst_to_tau"]
            - km_summary(second_d, second_e, tau)["rmst_to_tau"]
        )
    return {
        "method": (
            "Paired within-document permutation of observer labels; statistic is the "
            "difference in Kaplan-Meier restricted mean survival time (RMST) through "
            "the full 92-added-document horizon."
        ),
        "permutations": int(permutations),
        "seed": int(seed),
        "tau_added_docs": int(tau),
        "reference_rmst": float(ref_rmst),
        "transfer_rmst": float(transfer_rmst),
        "observed_difference": float(observed),
        "null_sd": float(null.std(ddof=1)),
        "null_q025": float(np.quantile(null, 0.025)),
        "null_q975": float(np.quantile(null, 0.975)),
        "p_two_sided_plus1": float(
            (1 + np.count_nonzero(np.abs(null) >= abs(observed))) / (permutations + 1)
        ),
        "p_one_sided_plus1": float(
            (1 + np.count_nonzero(null >= observed)) / (permutations + 1)
        ),
    }


def baseline_local_geometry(
    matrix: np.ndarray, anchors: np.ndarray, k: int = K
) -> dict[str, np.ndarray]:
    sub = matrix[anchors] @ matrix[anchors].T
    np.fill_diagonal(sub, -np.inf)
    sorted_scores = np.sort(sub, axis=1)[:, ::-1]
    return {
        "kth_similarity": sorted_scores[:, k - 1],
        "boundary_gap": sorted_scores[:, k - 1] - sorted_scores[:, k],
    }


def density_strata(
    ref_density: np.ndarray,
    transfer_density: np.ndarray,
    ref_durations: np.ndarray,
    ref_events: np.ndarray,
    transfer_durations: np.ndarray,
    transfer_events: np.ndarray,
    tau: int,
) -> dict:
    pooled = np.concatenate([ref_density, transfer_density])
    cuts = np.quantile(pooled, [1 / 3, 2 / 3])
    ref_bins = np.digitize(ref_density, cuts, right=False)
    transfer_bins = np.digitize(transfer_density, cuts, right=False)
    labels = ("low", "middle", "high")
    strata = {}
    for idx, label in enumerate(labels):
        ref_mask = ref_bins == idx
        transfer_mask = transfer_bins == idx
        strata[label] = {
            "reference": km_summary(ref_durations[ref_mask], ref_events[ref_mask], tau),
            "transfer": km_summary(
                transfer_durations[transfer_mask], transfer_events[transfer_mask], tau
            ),
        }
    return {
        "metric": (
            "Baseline local density proxy = cosine similarity to the 5th nearest "
            "neighbor among the 24 initial documents in each L2-normalized geometry."
        ),
        "pooled_tercile_cuts": [float(cut) for cut in cuts],
        "reference": {
            "mean": float(ref_density.mean()),
            "median": float(np.median(ref_density)),
            "q25": float(np.quantile(ref_density, 0.25)),
            "q75": float(np.quantile(ref_density, 0.75)),
        },
        "transfer": {
            "mean": float(transfer_density.mean()),
            "median": float(np.median(transfer_density)),
            "q25": float(np.quantile(transfer_density, 0.25)),
            "q75": float(np.quantile(transfer_density, 0.75)),
        },
        "strata": strata,
        "interpretation_boundary": (
            "Post-hoc confound check only. L2 normalization removes vector-norm scale "
            "from cosine neighborhoods. The survival separation persists in every "
            "pooled density tercile. Embedding dimensionality remains inseparable "
            "from observer identity with only two models."
        ),
    }


def run(artifact_dir: Path, output: Path) -> dict:
    parent = json.loads(
        (artifact_dir / "relational_dynamics_v1.json").read_text(encoding="utf-8")
    )
    robustness = json.loads(
        (artifact_dir / "relational_dynamics_v1_reanalysis.json").read_text(
            encoding="utf-8"
        )
    )
    ref, ref_paths = load_observer(
        artifact_dir / "embedding_cache_relational_v1" / "reference_observer"
    )
    transfer, transfer_paths = load_observer(
        artifact_dir / "embedding_cache_relational_v1" / "transfer_observer"
    )
    if ref_paths != transfer_paths:
        raise RuntimeError("observer corpus paths differ")

    chronology = chronology_from_parent(parent, ref_paths)
    anchors = chronology[:INITIAL_N]
    tau = len(chronology) - INITIAL_N
    rank_ref = rankings(ref)
    rank_transfer = rankings(transfer)

    first_ref = first_churn_times(rank_ref, chronology)
    first_transfer = first_churn_times(rank_transfer, chronology)
    ref_durations, ref_events = event_arrays(first_ref, anchors, tau)
    transfer_durations, transfer_events = event_arrays(first_transfer, anchors, tau)
    ref_local = baseline_local_geometry(ref, anchors)
    transfer_local = baseline_local_geometry(transfer, anchors)

    order_null = robustness["permutation_refinement"][
        "chronology_specific_dynamic_divergence"
    ]["5"]
    same = robustness["same_observer_anchor_bootstrap"]["random_order"]

    result = {
        "schema_version": 1,
        "kind": "posthoc-relational-stability-confound-check",
        "parent_experiment": parent["experiment"],
        "parent_robustness_artifact": "relational_dynamics_v1_reanalysis.json",
        "claim_boundary": (
            "Post-hoc analysis after the v1 outcome and power correction were known. "
            "It can refine interpretation and motivate the large-corpus design; it is "
            "not confirmatory evidence for a new mechanism."
        ),
        "order_invariant_signal": {
            "chronology_cross_model_D": float(order_null["observed"]),
            "arbitrary_order_cross_model_D_mean": float(order_null["null_mean"]),
            "chronology_specific_excess_D": float(
                order_null["observed"] - order_null["null_mean"]
            ),
            "chronology_specific_excess_fraction_of_null": float(
                (order_null["observed"] - order_null["null_mean"])
                / order_null["null_mean"]
            ),
            "same_observer_arbitrary_order_D_mean": {
                "reference": float(same["reference_mean"]),
                "transfer": float(same["transfer_mean"]),
            },
            "interpretation": (
                "Most measured cross-observer churn divergence is already present under "
                "arbitrary shared insertion orders. The next mechanism should therefore "
                "ask which static local properties predict expected churn per unit corpus "
                "mass, averaged over arrival orders: order-invariant susceptibility."
            ),
        },
        "first_churn_survival": {
            "k": K,
            "reference": km_summary(ref_durations, ref_events, tau),
            "transfer": km_summary(transfer_durations, transfer_events, tau),
            "paired_curve_test": paired_rmst_permutation(
                ref_durations,
                ref_events,
                transfer_durations,
                transfer_events,
                tau,
            ),
        },
        "baseline_density_check": density_strata(
            ref_local["kth_similarity"],
            transfer_local["kth_similarity"],
            ref_durations,
            ref_events,
            transfer_durations,
            transfer_events,
            tau,
        ),
        "baseline_gap_descriptive": {
            "metric": (
                "cosine-similarity gap between the 5th and 6th nearest neighbors "
                "among the 24 initial documents"
            ),
            "reference": {
                "mean": float(ref_local["boundary_gap"].mean()),
                "median": float(np.median(ref_local["boundary_gap"])),
            },
            "transfer": {
                "mean": float(transfer_local["boundary_gap"].mean()),
                "median": float(np.median(transfer_local["boundary_gap"])),
            },
            "claim_boundary": (
                "Descriptive only. Gap was already inspected in v1 and had unstable sign "
                "across observers; no post-hoc gap mechanism is inferred here."
            ),
        },
        "large_corpus_measurement_contract": {
            "mknn_panels": [
                "raw mKNN(N,k)",
                "permutation-calibrated mKNN(N,k)",
            ],
            "same_observer_control": (
                "Report a separately specified same-observer bootstrap/stability ceiling "
                "as a function of N. Exact same-model same-gallery mKNN is identically 1 "
                "for deterministic encoders, so the perturbation/bootstrap operator must "
                "be frozen before the large-corpus run and must not be called a seed-null."
            ),
            "decision": (
                "The static paper proceeds only if calibrated cross-model local alignment "
                "is scale-stable enough to interpret and remains materially below the "
                "frozen same-observer stability ceiling across relevant N and k."
            ),
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/relational_stability_density_posthoc.json"),
    )
    args = parser.parse_args()
    result = run(args.artifact_dir, args.output)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
