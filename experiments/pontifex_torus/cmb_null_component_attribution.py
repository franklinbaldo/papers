# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scipy>=1.14",
# ]
# ///
"""Attribute matched-null calibration error to score components and cells.

Follow-up to ``cmb_null_family_localization.py``.  The previous fixed-theta
experiment found that the residual predictive-Student-t versus exact-rank gap
at alpha=0.01 was not concentrated in one occlusion family.  This experiment
keeps the same balanced geometry x occlusion design and asks a narrower
mechanistic question: does the residual gap come primarily from one component
of the scalar score, or from specific geometry x occlusion interactions?

For every theta we preserve the observed value and all 128 matched-null values
for four quantities:

* score (the scalar used by the harness),
* core_rmse,
* boundary_shift,
* sqrt_global_energy (the transform that actually enters the scalar score).

Predictive Student-t and symmetric leave-one-out exact-rank calibration are
computed per theta/component.  Independently generated skies remain the
replication unit; theta rows within a sky are dependent diagnostics.
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
    run_one,
    sample_theta,
    synthetic_map,
)

COMPONENTS = ("score", "core_rmse", "boundary_shift", "sqrt_global_energy")
ALPHAS = (0.05, 0.01)


def component_value(metrics: dict[str, float], name: str) -> float:
    if name == "sqrt_global_energy":
        return float(np.sqrt(max(float(metrics["global_energy"]), 0.0)))
    return float(metrics[name])


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


def calibrate(observed: float, null: np.ndarray) -> tuple[float, float, float, float, float]:
    m = int(null.size)
    sd = float(np.std(null, ddof=1))
    if not np.isfinite(sd) or sd <= 1e-15:
        raise ValueError("zero-variance null")
    z_like = (observed - float(np.mean(null))) / sd
    t_pred = z_like / np.sqrt(1.0 + 1.0 / m)
    p_t = float(2.0 * t.sf(abs(t_pred), df=m - 1))
    joint = np.concatenate(([observed], null))[None, :]
    loo = leave_one_out_t(joint)[0]
    p_rank = float(np.mean(np.abs(loo) >= abs(loo[0])))
    return p_t, p_rank, float(t_pred), float(skew(null, bias=False)), float(
        kurtosis(null, fisher=True, bias=False)
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skies", type=int, default=12)
    ap.add_argument("--theta-per-cell", type=int, default=4)
    ap.add_argument("--null-maps", type=int, default=128)
    ap.add_argument("--ny", type=int, default=64)
    ap.add_argument("--nx", type=int, default=128)
    ap.add_argument("--seed", type=int, default=20260918)
    ap.add_argument(
        "--scores",
        type=Path,
        default=Path("pontifex-cmb-null-component-scores.jsonl"),
    )
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("pontifex-cmb-null-component-attribution.json"),
    )
    args = ap.parse_args()

    if args.skies < 2:
        raise ValueError("at least two independent skies are required")
    if args.theta_per_cell < 1:
        raise ValueError("theta-per-cell must be positive")
    if args.null_maps < 3:
        raise ValueError("null-maps must be >= 3")

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

    rows: list[dict] = []
    persisted: list[dict] = []
    zero_variance: dict[str, int] = defaultdict(int)

    for sky_id in range(args.skies):
        sky_seed = args.seed + 100_000_007 * sky_id
        field = synthetic_map(args.ny, args.nx, sky_seed)
        null_maps = [
            make_null(field, np.random.default_rng(sky_seed + 1_000_003 * (i + 1)))
            for i in range(args.null_maps)
        ]

        for theta in thetas:
            obs_rng = np.random.default_rng(sky_seed + 97_409 * (theta.sample + 1))
            observed_metrics = run_one(field, theta, obs_rng, "synthetic", None)

            null_metrics = []
            for null_id, null_map in enumerate(null_maps):
                null_rng = np.random.default_rng(
                    sky_seed + 10_000_019 * (theta.sample + 1) + null_id
                )
                null_metrics.append(
                    run_one(null_map, theta, null_rng, "synthetic", None)
                )

            persisted.append(
                {
                    "sky_id": sky_id,
                    "sky_seed": sky_seed,
                    **asdict(theta),
                    "observed": {
                        name: component_value(observed_metrics, name)
                        for name in COMPONENTS
                    },
                    "nulls": {
                        name: [component_value(m, name) for m in null_metrics]
                        for name in COMPONENTS
                    },
                }
            )

            for component in COMPONENTS:
                observed = component_value(observed_metrics, component)
                null = np.asarray(
                    [component_value(m, component) for m in null_metrics], dtype=float
                )
                try:
                    p_t, p_rank, t_pred, null_skew, null_kurtosis = calibrate(
                        observed, null
                    )
                except ValueError:
                    zero_variance[
                        f"{component}:{theta.geometry}:{theta.occlusion}"
                    ] += 1
                    continue

                rows.append(
                    {
                        "sky_id": sky_id,
                        "theta_sample": int(theta.sample),
                        "geometry": theta.geometry,
                        "occlusion": theta.occlusion,
                        "component": component,
                        "predictive_p": p_t,
                        "rank_p": p_rank,
                        "predictive_t": t_pred,
                        "null_skew": null_skew,
                        "null_excess_kurtosis": null_kurtosis,
                    }
                )

    by_component = {}
    by_component_cell = {}
    for component in COMPONENTS:
        crows = [r for r in rows if r["component"] == component]
        by_component[component] = {
            "rows": len(crows),
            "alpha": {
                f"{alpha:g}": {
                    "pooled": calibration_summary(crows, alpha),
                    "sky_blocked": sky_block_summary(crows, alpha),
                }
                for alpha in ALPHAS
            },
            "null_score_shape": {
                "skew": summarize([r["null_skew"] for r in crows]),
                "excess_kurtosis": summarize(
                    [r["null_excess_kurtosis"] for r in crows]
                ),
            },
        }

        cells = {}
        for geometry in GEOMETRIES:
            for occlusion in OCCLUSIONS:
                key = f"{geometry}::{occlusion}"
                cell_rows = [
                    r
                    for r in crows
                    if r["geometry"] == geometry and r["occlusion"] == occlusion
                ]
                cells[key] = {
                    "rows": len(cell_rows),
                    "alpha_0.01": {
                        "pooled": calibration_summary(cell_rows, 0.01),
                        "sky_blocked": sky_block_summary(cell_rows, 0.01),
                    },
                    "null_score_shape": {
                        "skew": summarize([r["null_skew"] for r in cell_rows]),
                        "excess_kurtosis": summarize(
                            [r["null_excess_kurtosis"] for r in cell_rows]
                        ),
                    },
                }
        by_component_cell[component] = cells

    component_tail_diffs = {
        component: float(
            payload["alpha"]["0.01"]["sky_blocked"]["rate_difference_by_sky"][
                "mean"
            ]
        )
        for component, payload in by_component.items()
    }

    score_discordant = {
        (int(r["sky_id"]), int(r["theta_sample"]))
        for r in rows
        if r["component"] == "score"
        and r["predictive_p"] <= 0.01
        and r["rank_p"] > 0.01
    }
    component_extremes_on_score_discordance = {}
    for component in COMPONENTS:
        vals = [
            abs(float(r["predictive_t"]))
            for r in rows
            if r["component"] == component
            and (int(r["sky_id"]), int(r["theta_sample"])) in score_discordant
        ]
        component_extremes_on_score_discordance[component] = summarize(vals)

    result = {
        "experiment": "Pontifex CMB matched-null component attribution",
        "design": {
            "independent_skies": args.skies,
            "theta_per_geometry_occlusion_cell": args.theta_per_cell,
            "theta_per_sky": len(thetas),
            "theta_panel_reused_across_skies": True,
            "balanced_geometries": list(GEOMETRIES),
            "balanced_occlusions": list(OCCLUSIONS),
            "null_maps": args.null_maps,
            "rank_resolution": 1.0 / (args.null_maps + 1),
            "map_shape": [args.ny, args.nx],
            "components": list(COMPONENTS),
        },
        "by_component": by_component,
        "by_component_geometry_occlusion": by_component_cell,
        "tail_attribution": {
            "alpha": 0.01,
            "mean_predictive_minus_rank_rate_by_sky": component_tail_diffs,
            "score_predictive_only_rows": len(score_discordant),
            "absolute_predictive_t_on_score_predictive_only_rows": component_extremes_on_score_discordance,
        },
        "zero_variance_rows": dict(sorted(zero_variance.items())),
        "interpretation_contract": {
            "evidence": (
                "component-level and geometry x occlusion summaries can localize where the "
                "synthetic score law departs from the parametric predictive-t approximation"
            ),
            "hypothesis": (
                "a component with a reproducibly larger predictive-minus-rank tail gap is a "
                "candidate source of the scalar-score mismatch; a cell-specific gap instead "
                "points to an interaction between score component and intervention geometry"
            ),
            "not_evidence": (
                "descriptive attribution on synthetic phase-scrambled skies is not evidence "
                "of a real CMB anomaly, physical topology, or Torus causality"
            ),
            "dependence_boundary": (
                "theta rows within one sky share the field and null-map bank; independently "
                "generated skies are the replication unit"
            ),
            "data_boundary": (
                "no assembly, student, validation, or test data are used; their strict "
                "separation is unchanged"
            ),
        },
    }

    args.scores.parent.mkdir(parents=True, exist_ok=True)
    with args.scores.open("w", encoding="utf-8") as f:
        for row in persisted:
            f.write(json.dumps(row) + "\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
