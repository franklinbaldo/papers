# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scipy>=1.14",
# ]
# ///
"""Test whether a genuinely nonlocal observable adds a second response axis.

The current Pontifex CMB synthetic score collapses to core amplitude because the
intervention mutates only ``core``: boundary_shift is structurally zero and
sqrt(global_energy) is a positive theta-dependent rescaling of core_rmse.

This discriminant leaves that baseline untouched and adds an *observation*
operator after the intervention: a fixed Gaussian beam is applied to the delta
field.  We then measure response in the unchanged outer boundary ring.  The beam
is deliberately simple and known; it is not claimed to model Planck/ACT.  Its
purpose is to ask one narrow question: can a nonlocal measurement contract
produce calibration information that is not a positive rescaling of core_rmse?

Independent synthetic skies are the replication unit.  Theta rows within a sky
share the field and matched-null bank and are therefore dependent diagnostics.
No assembly/student/validation/test data are used.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.stats import t

from cmb_matched_null_robustness_ladder import leave_one_out_t
from cmb_occlusion_mc import (
    GEOMETRIES,
    OCCLUSIONS,
    apply_occlusion,
    make_null,
    sample_theta,
    synthetic_map,
    synthetic_masks,
)

METRICS = ("core_rmse", "beam_boundary_rmse", "beam_leakage_ratio")


def response(field: np.ndarray, theta, rng: np.random.Generator, sigma: float) -> dict[str, float]:
    core, boundary, rr, local_angle = synthetic_masks(field.shape, theta)
    altered = apply_occlusion(field, core, boundary, rr, local_angle, theta, rng)
    delta = altered - field

    if not np.any(core):
        return {name: 0.0 for name in METRICS}

    core_rmse = float(np.sqrt(np.mean(delta[core] ** 2)))
    # x is periodic in the synthetic map, y is not.  This is an observation
    # operator only; it does not feed back into the intervention dynamics.
    spread = gaussian_filter(delta, sigma=sigma, mode=("nearest", "wrap"))
    beam_boundary_rmse = (
        float(np.sqrt(np.mean(spread[boundary] ** 2))) if np.any(boundary) else 0.0
    )
    beam_leakage_ratio = beam_boundary_rmse / max(core_rmse, 1e-15)
    return {
        "core_rmse": core_rmse,
        "beam_boundary_rmse": beam_boundary_rmse,
        "beam_leakage_ratio": beam_leakage_ratio,
    }


def calibrate(observed: float, null: np.ndarray) -> dict[str, float]:
    m = int(null.size)
    sd = float(np.std(null, ddof=1))
    if not np.isfinite(sd) or sd <= 1e-15:
        raise ValueError("zero-variance null")
    z_like = (observed - float(np.mean(null))) / sd
    t_pred = z_like / np.sqrt(1.0 + 1.0 / m)
    predictive_p = float(2.0 * t.sf(abs(t_pred), df=m - 1))
    joint = np.concatenate(([observed], null))[None, :]
    loo = leave_one_out_t(joint)[0]
    rank_p = float(np.mean(np.abs(loo) >= abs(loo[0])))
    return {"predictive_p": predictive_p, "rank_p": rank_p, "predictive_t": float(t_pred)}


def finite_corr(a: list[float], b: list[float]) -> float:
    x = np.asarray(a, dtype=float)
    y = np.asarray(b, dtype=float)
    good = np.isfinite(x) & np.isfinite(y)
    if np.count_nonzero(good) < 3 or np.std(x[good]) <= 1e-15 or np.std(y[good]) <= 1e-15:
        return float("nan")
    return float(np.corrcoef(x[good], y[good])[0, 1])


def summary(x: list[float]) -> dict[str, float | int]:
    a = np.asarray(x, dtype=float)
    a = a[np.isfinite(a)]
    if not a.size:
        return {"n": 0, "mean": float("nan"), "median": float("nan"), "min": float("nan"), "max": float("nan")}
    return {
        "n": int(a.size),
        "mean": float(np.mean(a)),
        "median": float(np.median(a)),
        "min": float(np.min(a)),
        "max": float(np.max(a)),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skies", type=int, default=8)
    ap.add_argument("--theta-per-cell", type=int, default=4)
    ap.add_argument("--null-maps", type=int, default=64)
    ap.add_argument("--beam-sigma", type=float, default=2.0)
    ap.add_argument("--ny", type=int, default=64)
    ap.add_argument("--nx", type=int, default=128)
    ap.add_argument("--seed", type=int, default=20260919)
    ap.add_argument("--scores", type=Path, default=Path("pontifex-cmb-nonlocal-scores.jsonl"))
    ap.add_argument("--output", type=Path, default=Path("pontifex-cmb-nonlocal-observable.json"))
    args = ap.parse_args()

    if args.skies < 2 or args.theta_per_cell < 1 or args.null_maps < 3 or args.beam_sigma <= 0:
        raise ValueError("invalid experimental budget")

    theta_rng = np.random.default_rng(args.seed + 17)
    thetas = []
    sample_id = 0
    for occlusion in OCCLUSIONS:
        for geometry in GEOMETRIES:
            for _ in range(args.theta_per_cell):
                base = sample_theta(theta_rng, sample_id, 0.008, 0.20)
                thetas.append(replace(base, geometry=str(geometry), occlusion=str(occlusion)))
                sample_id += 1

    rows: list[dict] = []
    persisted: list[dict] = []
    zero_variance: dict[str, int] = defaultdict(int)
    observed_by_sky: dict[int, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))

    for sky_id in range(args.skies):
        sky_seed = args.seed + 100_000_007 * sky_id
        field = synthetic_map(args.ny, args.nx, sky_seed)
        null_maps = [
            make_null(field, np.random.default_rng(sky_seed + 1_000_003 * (i + 1)))
            for i in range(args.null_maps)
        ]

        for theta in thetas:
            obs_rng = np.random.default_rng(sky_seed + 97_409 * (theta.sample + 1))
            observed = response(field, theta, obs_rng, args.beam_sigma)
            null_metrics = []
            for null_id, null_map in enumerate(null_maps):
                null_rng = np.random.default_rng(sky_seed + 10_000_019 * (theta.sample + 1) + null_id)
                null_metrics.append(response(null_map, theta, null_rng, args.beam_sigma))

            persisted.append({
                "sky_id": sky_id,
                "sky_seed": sky_seed,
                **asdict(theta),
                "observed": observed,
                "nulls": {name: [float(m[name]) for m in null_metrics] for name in METRICS},
            })
            for name in METRICS:
                observed_by_sky[sky_id][name].append(float(observed[name]))
                null = np.asarray([m[name] for m in null_metrics], dtype=float)
                try:
                    cal = calibrate(float(observed[name]), null)
                except ValueError:
                    zero_variance[name] += 1
                    continue
                rows.append({
                    "sky_id": sky_id,
                    "theta_sample": int(theta.sample),
                    "geometry": theta.geometry,
                    "occlusion": theta.occlusion,
                    "metric": name,
                    **cal,
                })

    by_key = {(int(r["sky_id"]), int(r["theta_sample"]), str(r["metric"])): r for r in rows}
    paired = []
    for sky_id in range(args.skies):
        for theta in thetas:
            core = by_key.get((sky_id, int(theta.sample), "core_rmse"))
            nonlocal_row = by_key.get((sky_id, int(theta.sample), "beam_boundary_rmse"))
            ratio = by_key.get((sky_id, int(theta.sample), "beam_leakage_ratio"))
            if core is None or nonlocal_row is None or ratio is None:
                continue
            paired.append({"core": core, "nonlocal": nonlocal_row, "ratio": ratio})

    rank_gap = [abs(p["core"]["rank_p"] - p["nonlocal"]["rank_p"]) for p in paired]
    pred_gap = [abs(p["core"]["predictive_p"] - p["nonlocal"]["predictive_p"]) for p in paired]
    ratio_rank_gap = [abs(p["core"]["rank_p"] - p["ratio"]["rank_p"]) for p in paired]
    decision_disagreement = [
        (p["core"]["rank_p"] <= 0.05) != (p["nonlocal"]["rank_p"] <= 0.05)
        for p in paired
    ]

    sky_correlations = []
    sky_ratio_cv = []
    for sky_id in range(args.skies):
        d = observed_by_sky[sky_id]
        sky_correlations.append(finite_corr(d["core_rmse"], d["beam_boundary_rmse"]))
        ratio = np.asarray(d["beam_leakage_ratio"], dtype=float)
        sky_ratio_cv.append(float(np.std(ratio, ddof=1) / max(abs(float(np.mean(ratio))), 1e-15)))

    result = {
        "experiment": "Pontifex CMB nonlocal observable ablation",
        "design": {
            "independent_skies": args.skies,
            "theta_per_sky": len(thetas),
            "balanced_geometries": list(GEOMETRIES),
            "balanced_occlusions": list(OCCLUSIONS),
            "null_maps": args.null_maps,
            "rank_resolution": 1.0 / (args.null_maps + 1),
            "map_shape": [args.ny, args.nx],
            "beam_sigma_pixels": args.beam_sigma,
            "baseline_score_modified": False,
        },
        "dimensionality_discriminant": {
            "observed_core_vs_nonlocal_pearson_by_sky": summary(sky_correlations),
            "observed_leakage_ratio_cv_by_sky": summary(sky_ratio_cv),
            "paired_calibratable_rows": len(paired),
            "rank_p_abs_difference": summary(rank_gap),
            "predictive_p_abs_difference": summary(pred_gap),
            "ratio_vs_core_rank_p_abs_difference": summary(ratio_rank_gap),
            "fraction_nonlocal_rank_p_not_identical_to_core": float(np.mean(np.asarray(rank_gap) > 1e-12)) if paired else float("nan"),
            "rank_decision_disagreement_at_0.05": float(np.mean(decision_disagreement)) if paired else float("nan"),
            "core_rank_p_vs_nonlocal_rank_p_correlation": finite_corr(
                [p["core"]["rank_p"] for p in paired], [p["nonlocal"]["rank_p"] for p in paired]
            ),
        },
        "zero_variance_rows": dict(sorted(zero_variance.items())),
        "interpretation_contract": {
            "evidence": (
                "if the beam-boundary statistic changes matched-null ranks relative to core_rmse, "
                "then it is not merely the same per-theta positive rescaling that caused the old score degeneracy"
            ),
            "hypothesis": (
                "a stable second response axis could later justify a genuinely multichannel score, but this ablation "
                "does not establish that the chosen Gaussian beam is physically appropriate"
            ),
            "not_evidence": (
                "the beam is a synthetic observation operator, not a Planck/ACT instrument model; results are not "
                "evidence of a CMB anomaly, physical topology, or Torus causality"
            ),
            "dependence_boundary": (
                "theta rows within a sky share the field and null-map bank; independently generated skies are the replication unit"
            ),
            "data_boundary": (
                "D_assembly, D_student, D_val, and D_test are untouched; no data from those partitions enter this experiment"
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
