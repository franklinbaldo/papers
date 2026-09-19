# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scipy>=1.14",
# ]
# ///
"""Metric-aware beam-width ladder for the Pontifex CMB synthetic harness.

The previous nonlocal-observable ablation used a fixed isotropic Gaussian sigma
in *pixel coordinates*.  On the CI grid (ny=64, nx=128), however, the synthetic
radial metric uses x with spacing 1/nx and 0.5*y with spacing 1/ny.  A scalar
pixel sigma therefore introduces an avoidable factor-of-two physical anisotropy.

This experiment fixes that confound and tests the stronger discriminant suggested
by the previous result: does the second response coordinate emerge continuously
from the local limit when observation width is increased?

For each theta, sigma is expressed as a fraction of that theta's lesion radius.
The Gaussian receives (sigma_y, sigma_x) = (w*r*ny, w*r*nx), which is isotropic
in the same normalized metric used by ``synthetic_masks``.  Width zero is an
explicit local-limit control and must yield zero boundary response.

The same skies, theta panel, and matched-null maps are reused across every width.
No assembly/student/validation/test data are touched.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np
from scipy.ndimage import gaussian_filter

from cmb_nonlocal_observable_ablation import calibrate, finite_corr, summary
from cmb_occlusion_mc import (
    GEOMETRIES,
    OCCLUSIONS,
    apply_occlusion,
    make_null,
    sample_theta,
    synthetic_map,
    synthetic_masks,
)


def responses(
    field: np.ndarray,
    theta,
    rng: np.random.Generator,
    widths: list[float],
) -> tuple[float, dict[float, float], dict[float, float]]:
    core, boundary, rr, local_angle = synthetic_masks(field.shape, theta)
    altered = apply_occlusion(field, core, boundary, rr, local_angle, theta, rng)
    delta = altered - field

    if not np.any(core):
        return 0.0, {w: 0.0 for w in widths}, {w: 0.0 for w in widths}

    core_rmse = float(np.sqrt(np.mean(delta[core] ** 2)))
    ny, nx = field.shape
    boundary_rmse: dict[float, float] = {}
    leakage_ratio: dict[float, float] = {}

    for width in widths:
        if width == 0.0:
            spread = delta
        else:
            sigma_metric = float(width * theta.radius)
            sigma_y = sigma_metric * ny
            sigma_x = sigma_metric * nx
            spread = gaussian_filter(delta, sigma=(sigma_y, sigma_x), mode=("nearest", "wrap"))
        value = float(np.sqrt(np.mean(spread[boundary] ** 2))) if np.any(boundary) else 0.0
        boundary_rmse[width] = value
        leakage_ratio[width] = value / max(core_rmse, 1e-15)

    return core_rmse, boundary_rmse, leakage_ratio


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skies", type=int, default=6)
    ap.add_argument("--theta-per-cell", type=int, default=3)
    ap.add_argument("--null-maps", type=int, default=32)
    ap.add_argument(
        "--beam-width-ratios",
        nargs="+",
        type=float,
        default=[0.0, 0.125, 0.25, 0.5, 1.0],
        help="Gaussian sigma as a fraction of each theta lesion radius.",
    )
    ap.add_argument("--ny", type=int, default=64)
    ap.add_argument("--nx", type=int, default=128)
    ap.add_argument("--seed", type=int, default=20260919)
    ap.add_argument("--scores", type=Path, default=Path("pontifex-cmb-metric-beam-scores.jsonl"))
    ap.add_argument("--output", type=Path, default=Path("pontifex-cmb-metric-beam-ladder.json"))
    args = ap.parse_args()

    widths = sorted(set(float(x) for x in args.beam_width_ratios))
    if args.skies < 2 or args.theta_per_cell < 1 or args.null_maps < 3:
        raise ValueError("invalid experimental budget")
    if not widths or widths[0] < 0.0:
        raise ValueError("beam widths must be non-negative")
    if 0.0 not in widths:
        raise ValueError("beam ladder must include the width-zero local control")

    theta_rng = np.random.default_rng(args.seed + 17)
    thetas = []
    sample_id = 0
    for occlusion in OCCLUSIONS:
        for geometry in GEOMETRIES:
            for _ in range(args.theta_per_cell):
                base = sample_theta(theta_rng, sample_id, 0.008, 0.20)
                thetas.append(replace(base, geometry=str(geometry), occlusion=str(occlusion)))
                sample_id += 1

    persisted: list[dict] = []
    core_rows: dict[tuple[int, int], dict[str, float]] = {}
    beam_rows: dict[tuple[int, int, float], dict[str, float]] = {}
    zero_variance: dict[float, int] = defaultdict(int)
    observed_core_by_sky: dict[int, list[float]] = defaultdict(list)
    observed_beam_by_sky: dict[tuple[int, float], list[float]] = defaultdict(list)
    observed_ratio_by_width: dict[float, list[float]] = defaultdict(list)

    for sky_id in range(args.skies):
        sky_seed = args.seed + 100_000_007 * sky_id
        field = synthetic_map(args.ny, args.nx, sky_seed)
        null_maps = [
            make_null(field, np.random.default_rng(sky_seed + 1_000_003 * (i + 1)))
            for i in range(args.null_maps)
        ]

        for theta in thetas:
            obs_rng = np.random.default_rng(sky_seed + 97_409 * (theta.sample + 1))
            obs_core, obs_beam, obs_ratio = responses(field, theta, obs_rng, widths)

            null_core: list[float] = []
            null_beam: dict[float, list[float]] = {w: [] for w in widths}
            null_ratio: dict[float, list[float]] = {w: [] for w in widths}
            for null_id, null_map in enumerate(null_maps):
                null_rng = np.random.default_rng(sky_seed + 10_000_019 * (theta.sample + 1) + null_id)
                ncore, nbeam, nratio = responses(null_map, theta, null_rng, widths)
                null_core.append(ncore)
                for w in widths:
                    null_beam[w].append(nbeam[w])
                    null_ratio[w].append(nratio[w])

            persisted.append(
                {
                    "sky_id": sky_id,
                    "sky_seed": sky_seed,
                    **asdict(theta),
                    "beam_width_ratios": widths,
                    "observed_core_rmse": obs_core,
                    "observed_beam_boundary_rmse": {str(w): obs_beam[w] for w in widths},
                    "observed_leakage_ratio": {str(w): obs_ratio[w] for w in widths},
                    "null_core_rmse": [float(x) for x in null_core],
                    "null_beam_boundary_rmse": {str(w): [float(x) for x in null_beam[w]] for w in widths},
                    "null_leakage_ratio": {str(w): [float(x) for x in null_ratio[w]] for w in widths},
                }
            )

            key = (sky_id, int(theta.sample))
            core_rows[key] = calibrate(obs_core, np.asarray(null_core, dtype=float))
            observed_core_by_sky[sky_id].append(obs_core)

            for w in widths:
                observed_beam_by_sky[(sky_id, w)].append(obs_beam[w])
                observed_ratio_by_width[w].append(obs_ratio[w])
                try:
                    beam_rows[(sky_id, int(theta.sample), w)] = calibrate(
                        obs_beam[w], np.asarray(null_beam[w], dtype=float)
                    )
                except ValueError:
                    zero_variance[w] += 1

    ladder = []
    for w in widths:
        paired = []
        for sky_id in range(args.skies):
            for theta in thetas:
                key = (sky_id, int(theta.sample))
                core = core_rows.get(key)
                beam = beam_rows.get((sky_id, int(theta.sample), w))
                if core is not None and beam is not None:
                    paired.append((core, beam))

        rank_gap = [abs(core["rank_p"] - beam["rank_p"]) for core, beam in paired]
        pred_gap = [abs(core["predictive_p"] - beam["predictive_p"]) for core, beam in paired]
        disagree = [
            (core["rank_p"] <= 0.05) != (beam["rank_p"] <= 0.05)
            for core, beam in paired
        ]
        sky_corr = [
            finite_corr(observed_core_by_sky[sky_id], observed_beam_by_sky[(sky_id, w)])
            for sky_id in range(args.skies)
        ]
        ratios = observed_ratio_by_width[w]

        ladder.append(
            {
                "beam_width_ratio": w,
                "sigma_contract": "sigma_y=w*radius*ny; sigma_x=w*radius*nx",
                "paired_calibratable_rows": len(paired),
                "zero_variance_rows": int(zero_variance[w]),
                "observed_leakage_ratio": summary(ratios),
                "observed_core_vs_boundary_pearson_by_sky": summary(sky_corr),
                "rank_p_abs_difference_vs_core": summary(rank_gap),
                "predictive_p_abs_difference_vs_core": summary(pred_gap),
                "fraction_rank_p_not_identical_to_core": (
                    float(np.mean(np.asarray(rank_gap) > 1e-12)) if paired else float("nan")
                ),
                "rank_decision_disagreement_at_0.05": (
                    float(np.mean(disagree)) if paired else float("nan")
                ),
                "core_rank_p_vs_boundary_rank_p_correlation": (
                    finite_corr(
                        [core["rank_p"] for core, _ in paired],
                        [beam["rank_p"] for _, beam in paired],
                    )
                    if paired
                    else float("nan")
                ),
            }
        )

    nonzero_widths = [w for w in widths if w > 0]
    per_row_ratio_cv = []
    per_row_peak_width = []
    for row in persisted:
        vals = np.asarray([row["observed_leakage_ratio"][str(w)] for w in nonzero_widths], dtype=float)
        if vals.size and np.isfinite(vals).all():
            per_row_ratio_cv.append(float(np.std(vals, ddof=1) / max(abs(float(np.mean(vals))), 1e-15)))
            per_row_peak_width.append(float(nonzero_widths[int(np.argmax(vals))]))

    result = {
        "experiment": "Pontifex CMB metric-aware beam-width ladder",
        "design": {
            "independent_skies": args.skies,
            "theta_per_sky": len(thetas),
            "balanced_geometries": list(GEOMETRIES),
            "balanced_occlusions": list(OCCLUSIONS),
            "null_maps": args.null_maps,
            "rank_resolution": 1.0 / (args.null_maps + 1),
            "map_shape": [args.ny, args.nx],
            "beam_width_ratios": widths,
            "metric_correction": (
                "unlike the prior fixed pixel-space sigma, this ladder scales sigma separately by ny and nx "
                "so the Gaussian is isotropic in the normalized metric used by synthetic_masks"
            ),
        },
        "ladder": ladder,
        "cross_width": {
            "observed_leakage_ratio_cv_across_nonzero_widths": summary(per_row_ratio_cv),
            "observed_peak_width_ratio_counts": {
                str(w): int(sum(x == w for x in per_row_peak_width)) for w in nonzero_widths
            },
        },
        "interpretation_contract": {
            "evidence": (
                "a zero response at width=0 followed by reproducible changes in leakage and matched-null ranks as width grows "
                "supports the narrow claim that the second coordinate is induced by a genuinely nonlocal observation scale"
            ),
            "negative_result_rule": (
                "if nonzero widths are effectively identical to one another, or the width-zero control is not degenerate, "
                "the proposed scale interpretation is falsified or the implementation is wrong"
            ),
            "hypothesis": (
                "a stable scale-response curve could motivate a multiscale observation model, but no Gaussian beam width "
                "is asserted to be physically correct for Planck or ACT"
            ),
            "not_evidence": (
                "this is synthetic instrumentation geometry only; it is not evidence of a CMB anomaly, physical nonlocality, "
                "topology, or Torus causality"
            ),
            "dependence_boundary": (
                "theta rows within a sky share the field and null-map bank; independent skies are the replication unit"
            ),
            "data_boundary": (
                "D_assembly, D_student, D_val, and D_test are untouched and none enters this experiment"
            ),
        },
    }

    args.scores.parent.mkdir(parents=True, exist_ok=True)
    with args.scores.open("w", encoding="utf-8") as f:
        for row in persisted:
            f.write(json.dumps(row) + "\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, allow_nan=True))


if __name__ == "__main__":
    main()
