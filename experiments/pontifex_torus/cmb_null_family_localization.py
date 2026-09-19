# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scipy>=1.14",
# ]
# ///
"""Localize matched-null calibration error by intervention family.

This is the follow-up to ``cmb_empirical_null_ladder.py``.  The earlier run
found that predictive Student-t and exact exchangeable-rank calibration agree
closely around alpha=0.05 at m>=64, while Student-t remains more permissive in
the 1% tail at m=128.  That run changed the theta panel from sky to sky, so it
could not cleanly separate sky-to-sky variation from intervention-family
composition.

Here the theta panel is fixed once and reused on every independently generated
synthetic sky.  It is also balanced over the 5 occlusion families x 3 geometry
families.  This makes sky the natural independent replication unit for asking
whether the residual calibration gap is concentrated in a particular
intervention family.

The experiment is a calibration/falsification control only.  It does not test a
real CMB anomaly, Torus causality, or any assembly/student/val/test hypothesis.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np
from scipy.stats import kurtosis, skew, t

from cmb_matched_null_robustness_ladder import leave_one_out_t
from cmb_occlusion_mc import (
    GEOMETRIES,
    OCCLUSIONS,
    make_null,
    matched_null_stats,
    run_one,
    sample_theta,
    synthetic_map,
)

ALPHAS = (0.05, 0.01)


def summarize(values: list[float]) -> dict[str, float | int]:
    x = np.asarray(values, dtype=float)
    x = x[np.isfinite(x)]
    if not x.size:
        return {
            "n": 0,
            "mean": float("nan"),
            "median": float("nan"),
            "min": float("nan"),
            "max": float("nan"),
        }
    return {
        "n": int(x.size),
        "mean": float(np.mean(x)),
        "median": float(np.median(x)),
        "min": float(np.min(x)),
        "max": float(np.max(x)),
    }


def calibration_summary(rows: list[dict], alpha: float) -> dict:
    if not rows:
        return {"rows": 0}
    pt = np.asarray([r["predictive_p"] for r in rows], dtype=float)
    pr = np.asarray([r["rank_p"] for r in rows], dtype=float)
    pred = pt <= alpha
    rank = pr <= alpha
    return {
        "rows": int(len(rows)),
        "predictive_t_rejection": float(np.mean(pred)),
        "exact_rank_rejection": float(np.mean(rank)),
        "rate_difference_predictive_minus_rank": float(np.mean(pred) - np.mean(rank)),
        "decision_disagreement": float(np.mean(pred != rank)),
        "median_abs_p_gap": float(np.median(np.abs(pt - pr))),
    }


def sky_block_summary(rows: list[dict], alpha: float) -> dict:
    by_sky: dict[int, list[dict]] = defaultdict(list)
    for row in rows:
        by_sky[int(row["sky_id"])].append(row)

    diffs: list[float] = []
    disagreements: list[float] = []
    for sky_rows in by_sky.values():
        pt = np.asarray([r["predictive_p"] for r in sky_rows], dtype=float)
        pr = np.asarray([r["rank_p"] for r in sky_rows], dtype=float)
        pred = pt <= alpha
        rank = pr <= alpha
        diffs.append(float(np.mean(pred) - np.mean(rank)))
        disagreements.append(float(np.mean(pred != rank)))

    return {
        "independent_skies": int(len(by_sky)),
        "rate_difference_by_sky": summarize(diffs),
        "decision_disagreement_by_sky": summarize(disagreements),
        "positive_difference_skies": int(sum(x > 0 for x in diffs)),
        "zero_difference_skies": int(sum(x == 0 for x in diffs)),
        "negative_difference_skies": int(sum(x < 0 for x in diffs)),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skies", type=int, default=12)
    ap.add_argument("--theta-per-cell", type=int, default=4)
    ap.add_argument("--null-counts", nargs="+", type=int, default=[64, 128])
    ap.add_argument("--ny", type=int, default=64)
    ap.add_argument("--nx", type=int, default=128)
    ap.add_argument("--seed", type=int, default=20260918)
    ap.add_argument(
        "--scores",
        type=Path,
        default=Path("pontifex-cmb-null-family-scores.jsonl"),
    )
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("pontifex-cmb-null-family-localization.json"),
    )
    args = ap.parse_args()

    if args.skies < 2:
        raise ValueError("at least two independent skies are required")
    if args.theta_per_cell < 1:
        raise ValueError("theta-per-cell must be positive")
    if min(args.null_counts) < 3:
        raise ValueError("all null counts must be >= 3")

    max_m = max(args.null_counts)
    theta_rng = np.random.default_rng(args.seed + 17)
    thetas = []
    sample_id = 0
    for occlusion in OCCLUSIONS:
        for geometry in GEOMETRIES:
            for _ in range(args.theta_per_cell):
                base = sample_theta(theta_rng, sample_id, 0.008, 0.20)
                thetas.append(
                    replace(base, geometry=str(geometry), occlusion=str(occlusion))
                )
                sample_id += 1

    result_rows: list[dict] = []
    persisted_scores: list[dict] = []
    zero_variance: dict[str, int] = defaultdict(int)

    for sky_id in range(args.skies):
        sky_seed = args.seed + 100_000_007 * sky_id
        field = synthetic_map(args.ny, args.nx, sky_seed)
        null_maps = [
            make_null(field, np.random.default_rng(sky_seed + 1_000_003 * (i + 1)))
            for i in range(max_m)
        ]

        for theta in thetas:
            obs_rng = np.random.default_rng(sky_seed + 97_409 * (theta.sample + 1))
            observed = float(run_one(field, theta, obs_rng, "synthetic", None)["score"])
            _, _, full_null = matched_null_stats(
                null_maps, theta, sky_seed, "synthetic", None
            )
            persisted_scores.append(
                {
                    "sky_id": sky_id,
                    "sky_seed": sky_seed,
                    **asdict(theta),
                    "observed_score": observed,
                    "null_scores": [float(x) for x in full_null],
                }
            )

            for m in args.null_counts:
                null = np.asarray(full_null[:m], dtype=float)
                sd = float(np.std(null, ddof=1))
                if not np.isfinite(sd) or sd <= 1e-15:
                    zero_variance[f"m={m}:{theta.occlusion}"] += 1
                    continue

                z_like = (observed - float(np.mean(null))) / sd
                t_pred = z_like / np.sqrt(1.0 + 1.0 / m)
                p_t = float(2.0 * t.sf(abs(t_pred), df=m - 1))
                joint = np.concatenate(([observed], null))[None, :]
                loo = leave_one_out_t(joint)[0]
                p_rank = float(np.mean(np.abs(loo) >= abs(loo[0])))

                result_rows.append(
                    {
                        "sky_id": sky_id,
                        "theta_sample": int(theta.sample),
                        "geometry": theta.geometry,
                        "occlusion": theta.occlusion,
                        "m": int(m),
                        "predictive_p": p_t,
                        "rank_p": p_rank,
                        "null_skew": float(skew(null, bias=False)),
                        "null_excess_kurtosis": float(
                            kurtosis(null, fisher=True, bias=False)
                        ),
                    }
                )

    global_by_m = {}
    by_occlusion = {}
    for m in args.null_counts:
        m_rows = [r for r in result_rows if r["m"] == m]
        global_by_m[str(m)] = {
            "rows": len(m_rows),
            "rank_resolution": 1.0 / (m + 1),
            "alpha": {
                f"{alpha:g}": {
                    "pooled": calibration_summary(m_rows, alpha),
                    "sky_blocked": sky_block_summary(m_rows, alpha),
                }
                for alpha in ALPHAS
            },
            "null_score_shape": {
                "skew": summarize([r["null_skew"] for r in m_rows]),
                "excess_kurtosis": summarize(
                    [r["null_excess_kurtosis"] for r in m_rows]
                ),
            },
        }

        family_summary = {}
        for occlusion in OCCLUSIONS:
            frows = [r for r in m_rows if r["occlusion"] == occlusion]
            family_summary[occlusion] = {
                "rows": len(frows),
                "alpha": {
                    f"{alpha:g}": {
                        "pooled": calibration_summary(frows, alpha),
                        "sky_blocked": sky_block_summary(frows, alpha),
                    }
                    for alpha in ALPHAS
                },
                "null_score_shape": {
                    "skew": summarize([r["null_skew"] for r in frows]),
                    "excess_kurtosis": summarize(
                        [r["null_excess_kurtosis"] for r in frows]
                    ),
                },
            }
        by_occlusion[str(m)] = family_summary

    m_tail = max_m
    tail_families = by_occlusion[str(m_tail)]
    alpha_key = "0.01"
    family_tail_diffs = {
        family: float(
            payload["alpha"][alpha_key]["sky_blocked"]["rate_difference_by_sky"][
                "mean"
            ]
        )
        for family, payload in tail_families.items()
    }

    result = {
        "experiment": "Pontifex CMB matched-null family localization with fixed theta panel",
        "design": {
            "independent_skies": args.skies,
            "theta_per_geometry_occlusion_cell": args.theta_per_cell,
            "theta_per_sky": len(thetas),
            "theta_panel_reused_across_skies": True,
            "balanced_geometries": list(GEOMETRIES),
            "balanced_occlusions": list(OCCLUSIONS),
            "null_counts": args.null_counts,
            "map_shape": [args.ny, args.nx],
        },
        "global_by_m": global_by_m,
        "by_occlusion": by_occlusion,
        "tail_localization_at_max_m": {
            "m": m_tail,
            "alpha": 0.01,
            "mean_predictive_minus_rank_rate_by_sky": family_tail_diffs,
            "largest_positive_family_descriptive_only": max(
                family_tail_diffs, key=family_tail_diffs.get
            ),
            "smallest_family_descriptive_only": min(
                family_tail_diffs, key=family_tail_diffs.get
            ),
        },
        "zero_variance_rows": dict(sorted(zero_variance.items())),
        "interpretation_contract": {
            "evidence": (
                "the fixed balanced theta panel isolates sky-to-sky replication from "
                "intervention-family composition and localizes predictive-t versus exact-rank "
                "calibration differences within the synthetic Pontifex score functional"
            ),
            "hypothesis": (
                "if the 1% gap concentrates reproducibly in one occlusion family across "
                "independent skies, that family is a candidate mechanism for the score-law "
                "non-Gaussianity; diffuse gaps instead implicate the score functional or null model"
            ),
            "not_evidence": (
                "family localization on synthetic phase-scrambled skies is not evidence of a "
                "real CMB anomaly, physical topology, or Torus causality"
            ),
            "dependence_boundary": (
                "theta rows within one sky share the field and null-map bank; sky-blocked "
                "summaries treat independently generated skies as the replication unit"
            ),
            "data_boundary": (
                "no assembly, student, validation, or test data are used; their strict "
                "separation is unchanged"
            ),
        },
    }

    args.scores.parent.mkdir(parents=True, exist_ok=True)
    with args.scores.open("w", encoding="utf-8") as f:
        for row in persisted_scores:
            f.write(json.dumps(row) + "\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
