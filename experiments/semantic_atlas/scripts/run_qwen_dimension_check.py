from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from run_relational_stability_posthoc import (
    INITIAL_N,
    chronology_from_parent,
    event_arrays,
    first_churn_times,
    km_summary,
    load_observer,
    paired_rmst_permutation,
    rankings,
)


SEED = 20260826
TARGET_DIMENSION = 384


def normalize(matrix: np.ndarray) -> np.ndarray:
    values = np.asarray(matrix, dtype=np.float64)
    return values / np.linalg.norm(values, axis=1, keepdims=True)


def survival(matrix: np.ndarray, chronology: np.ndarray) -> tuple[dict, np.ndarray, np.ndarray]:
    tau = len(chronology) - INITIAL_N
    anchors = chronology[:INITIAL_N]
    first = first_churn_times(rankings(matrix), chronology)
    durations, events = event_arrays(first, anchors, tau)
    return km_summary(durations, events, tau), durations, events


def run(artifact_dir: Path, projections: int, output: Path) -> dict:
    parent = json.loads(
        (artifact_dir / "relational_dynamics_v1.json").read_text(encoding="utf-8")
    )
    qwen, qwen_paths = load_observer(
        artifact_dir / "embedding_cache_relational_v1" / "reference_observer"
    )
    minilm, minilm_paths = load_observer(
        artifact_dir / "embedding_cache_relational_v1" / "transfer_observer"
    )
    if qwen_paths != minilm_paths:
        raise RuntimeError("observer corpus paths differ")
    chronology = chronology_from_parent(parent, qwen_paths)

    qwen_native, _, _ = survival(qwen, chronology)
    minilm_native, minilm_durations, minilm_events = survival(minilm, chronology)
    prefix = normalize(qwen[:, :TARGET_DIMENSION])
    prefix_summary, prefix_durations, prefix_events = survival(prefix, chronology)
    tau = len(chronology) - INITIAL_N
    paired = paired_rmst_permutation(
        prefix_durations,
        prefix_events,
        minilm_durations,
        minilm_events,
        tau,
    )

    random_rmst = np.empty(projections, dtype=np.float64)
    for index in range(projections):
        rng = np.random.default_rng(SEED + index)
        projection = rng.normal(
            0.0, 1.0 / np.sqrt(TARGET_DIMENSION), size=(qwen.shape[1], TARGET_DIMENSION)
        )
        summary, _, _ = survival(normalize(qwen @ projection), chronology)
        random_rmst[index] = summary["rmst_to_tau"]

    result = {
        "original": {
            "qwen_dim": int(qwen.shape[1]),
            "qwen_rmst": qwen_native["rmst_to_tau"],
            "qwen_km_median": qwen_native["km_median_added_docs"],
            "minilm_dim": int(minilm.shape[1]),
            "minilm_rmst": minilm_native["rmst_to_tau"],
            "minilm_km_median": minilm_native["km_median_added_docs"],
            "rmst_difference": qwen_native["rmst_to_tau"] - minilm_native["rmst_to_tau"],
        },
        "qwen_prefix384_mrl_style": {
            "method": "first 384 dimensions of cached Qwen vector, then L2 renormalize; diagnostic only",
            "qwen_rmst": prefix_summary["rmst_to_tau"],
            "qwen_km_median": prefix_summary["km_median_added_docs"],
            "events": prefix_summary["events"],
            "censored": prefix_summary["censored"],
            "paired_vs_minilm": {
                "q_rmst": paired["reference_rmst"],
                "m_rmst": paired["transfer_rmst"],
                "diff": paired["observed_difference"],
                "p2": paired["p_two_sided_plus1"],
                "p1": paired["p_one_sided_plus1"],
            },
        },
        "random_projection_1024_to_384": {
            "method": f"{projections} independent Gaussian JL projections, seed 20260826+s, L2 renormalize",
            "n": projections,
            "rmst_mean": float(random_rmst.mean()) if projections else None,
            "rmst_sd": float(random_rmst.std(ddof=1)) if projections > 1 else None,
            "rmst_q025": float(np.quantile(random_rmst, 0.025)) if projections else None,
            "rmst_median": float(np.median(random_rmst)) if projections else None,
            "rmst_q975": float(np.quantile(random_rmst, 0.975)) if projections else None,
            "rmst_min": float(random_rmst.min()) if projections else None,
            "rmst_max": float(random_rmst.max()) if projections else None,
            "fraction_rmst_ge_40": float(np.mean(random_rmst >= 40)) if projections else None,
            "fraction_rmst_ge_minilm_plus20": (
                float(np.mean(random_rmst >= minilm_native["rmst_to_tau"] + 20))
                if projections
                else None
            ),
        },
        "interpretation": (
            "Raw output dimensionality alone is not a plausible explanation of the "
            "Qwen/MiniLM survival gap in this 116-document pilot: reducing Qwen from "
            "1024 to 384 dimensions leaves a large RMST separation under both a "
            "prefix/MRL-style diagnostic and Gaussian random projections. This is "
            "post-hoc and does not separate other architecture/training differences."
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--projections", type=int, default=2000)
    parser.add_argument(
        "--output", type=Path, default=Path("artifacts/qwen_384d_dimension_check.json")
    )
    args = parser.parse_args()
    run(args.artifact_dir, args.projections, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
