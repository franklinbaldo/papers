# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scipy>=1.14",
# ]
# ///
"""Metric-spectrum control for the Pontifex CMB nonlocal beam response.

The previous beam experiments corrected the Gaussian observation kernel to the
metric used by ``synthetic_masks``.  The synthetic sky generator itself still
used ``np.fft.fftfreq`` in cycles-per-pixel, however.  On the 64x128 grid that
means the same numerical cutoff corresponds to twice as much physical
wavenumber along x as along y, even though both axes span one unit in the mask
metric.  This is a potential field-anisotropy confound.

This experiment uses one shared white-noise realization per sky and applies:

* the legacy cycles-per-pixel filter, as an audit control;
* metric-isotropic filters at several predeclared physical spectral cutoffs k0.

The beam-width ladder is never re-tuned.  Width 0.5 is the frozen reference from
the prior development/held-out experiment; 0.125, 0.25 and 1.0 are the same
predeclared alternatives.  Independent base sky seeds are the replication unit.
Theta rows within a sky/field are dependent and are used only to form sky-level
summaries.

No assembly/student/validation/test data are touched.  This is synthetic
instrumentation geometry, not a cosmological detection test.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np
from scipy.stats import binomtest, spearmanr

from cmb_beam_scale_holdout import balanced_theta_panel, holm_adjust
from cmb_metric_beam_ladder import responses
from cmb_nonlocal_observable_ablation import summary
from cmb_occlusion_mc import GEOMETRIES, OCCLUSIONS


def filtered_fields(
    ny: int,
    nx: int,
    seed: int,
    metric_k0: list[float],
) -> dict[str, np.ndarray]:
    """Generate legacy and metric-isotropic fields from the same white noise."""
    rng = np.random.default_rng(seed)
    white = rng.normal(size=(ny, nx))
    ft = np.fft.rfft2(white)

    # Exact legacy spectral contract from cmb_occlusion_mc.synthetic_map.
    ky_legacy = np.fft.fftfreq(ny)[:, None]
    kx_legacy = np.fft.rfftfreq(nx)[None, :]
    k2_legacy = kx_legacy * kx_legacy + ky_legacy * ky_legacy
    legacy_filter = np.exp(-k2_legacy / 0.012) / np.sqrt(1.0 + 80.0 * k2_legacy)

    fields: dict[str, np.ndarray] = {
        "legacy_pixel_spectrum": normalize_field(
            np.fft.irfft2(ft * legacy_filter, s=(ny, nx)).real
        )
    }

    # In the mask metric, x spans [0,1) and 0.5*y spans [-0.5,0.5), so both
    # physical axes have length one.  Supplying d=1/n makes FFT frequencies
    # cycles per metric unit instead of cycles per pixel.
    ky_metric = np.fft.fftfreq(ny, d=1.0 / ny)[:, None]
    kx_metric = np.fft.rfftfreq(nx, d=1.0 / nx)[None, :]
    k2_metric = kx_metric * kx_metric + ky_metric * ky_metric
    for k0 in metric_k0:
        q = k2_metric / (k0 * k0)
        # Same dimensionless shape as the legacy filter: because
        # 80 * 0.012 = 0.96, q=k^2/k0^2 gives exp(-q)/sqrt(1+0.96q).
        filt = np.exp(-q) / np.sqrt(1.0 + 0.96 * q)
        fields[f"metric_k0_{k0:g}"] = normalize_field(
            np.fft.irfft2(ft * filt, s=(ny, nx)).real
        )
    return fields


def normalize_field(field: np.ndarray) -> np.ndarray:
    out = np.asarray(field, dtype=float).copy()
    out -= float(np.mean(out))
    out /= max(float(np.std(out)), 1e-12)
    return out


def e_fold_length(field: np.ndarray, axis: int) -> float:
    """Periodic 1/e autocorrelation length in the same unit metric as masks."""
    centered = field - float(np.mean(field))
    var = float(np.mean(centered * centered))
    if var <= 1e-15:
        return float("nan")
    n = field.shape[axis]
    max_lag = max(2, n // 3)
    target = np.exp(-1.0)
    previous = 1.0
    for lag in range(1, max_lag + 1):
        corr = float(np.mean(centered * np.roll(centered, -lag, axis=axis)) / var)
        if corr <= target:
            # Linear interpolation between integer lags keeps the diagnostic
            # continuous without pretending this is a fitted correlation model.
            frac = 0.0
            if abs(corr - previous) > 1e-15:
                frac = float(np.clip((previous - target) / (previous - corr), 0.0, 1.0))
            lag_at_target = (lag - 1) + frac
            spacing = 1.0 / n
            return float(lag_at_target * spacing)
        previous = corr
    return float(max_lag / n)


def condition_sort_key(name: str) -> tuple[int, float]:
    if name == "legacy_pixel_spectrum":
        return (0, 0.0)
    return (1, float(name.rsplit("_", 1)[-1]))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skies", type=int, default=12)
    ap.add_argument("--theta-per-cell", type=int, default=2)
    ap.add_argument(
        "--beam-width-ratios",
        nargs="+",
        type=float,
        default=[0.125, 0.25, 0.5, 1.0],
    )
    ap.add_argument(
        "--metric-k0",
        nargs="+",
        type=float,
        default=[4.0, 8.0, 16.0],
        help="Physical spectral cutoffs in cycles per metric unit.",
    )
    ap.add_argument("--frozen-width", type=float, default=0.5)
    ap.add_argument("--ny", type=int, default=64)
    ap.add_argument("--nx", type=int, default=128)
    ap.add_argument("--seed", type=int, default=20260919)
    ap.add_argument(
        "--rows",
        type=Path,
        default=Path("pontifex-cmb-metric-spectrum-control.jsonl"),
    )
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("pontifex-cmb-metric-spectrum-control.json"),
    )
    args = ap.parse_args()

    widths = sorted(set(float(w) for w in args.beam_width_ratios))
    metric_k0 = sorted(set(float(k) for k in args.metric_k0))
    if args.skies < 2 or args.theta_per_cell < 1:
        raise ValueError("need at least two independent skies and one theta per cell")
    if not widths or args.frozen_width not in widths:
        raise ValueError("frozen width must be one of the predeclared beam widths")
    if min(widths) <= 0.0 or not metric_k0 or min(metric_k0) <= 0.0:
        raise ValueError("widths and metric spectral cutoffs must be positive")

    thetas = balanced_theta_panel(args.seed, args.theta_per_cell)
    conditions = ["legacy_pixel_spectrum"] + [f"metric_k0_{k:g}" for k in metric_k0]

    per_condition_width_sky: dict[tuple[str, float], list[float]] = defaultdict(list)
    peak_widths: dict[str, list[float]] = defaultdict(list)
    corr_x: dict[str, list[float]] = defaultdict(list)
    corr_y: dict[str, list[float]] = defaultdict(list)
    corr_ratio: dict[str, list[float]] = defaultdict(list)
    radius_peak_spearman: dict[str, list[float]] = defaultdict(list)
    persisted: list[dict] = []

    for sky_id in range(args.skies):
        sky_seed = args.seed + 9_000_000_019 + 100_000_007 * sky_id
        fields = filtered_fields(args.ny, args.nx, sky_seed, metric_k0)

        for condition in conditions:
            field = fields[condition]
            lx = e_fold_length(field, axis=1)
            ly = e_fold_length(field, axis=0)
            corr_x[condition].append(lx)
            corr_y[condition].append(ly)
            corr_ratio[condition].append(lx / ly if ly > 0 else float("nan"))
            corr_geom = float(np.sqrt(lx * ly)) if lx > 0 and ly > 0 else float("nan")

            per_width: dict[float, list[float]] = {w: [] for w in widths}
            row_peak_width: list[float] = []
            radius_over_corr: list[float] = []

            for theta in thetas:
                obs_rng = np.random.default_rng(sky_seed + 97_409 * (theta.sample + 1))
                core, beam, ratio = responses(field, theta, obs_rng, widths)
                peak = min(widths, key=lambda w: (-ratio[w], w))
                row_peak_width.append(peak)
                radius_over_corr.append(
                    float(theta.radius / corr_geom) if np.isfinite(corr_geom) and corr_geom > 0 else float("nan")
                )
                for w in widths:
                    per_width[w].append(ratio[w])

                persisted.append(
                    {
                        "sky_id": sky_id,
                        "sky_seed": sky_seed,
                        "field_condition": condition,
                        "field_corr_length_x": lx,
                        "field_corr_length_y": ly,
                        "field_corr_length_geomean": corr_geom,
                        "radius_over_field_corr": radius_over_corr[-1],
                        **asdict(theta),
                        "observed_core_rmse": core,
                        "observed_beam_boundary_rmse": {str(w): beam[w] for w in widths},
                        "observed_leakage_ratio": {str(w): ratio[w] for w in widths},
                        "row_peak_width": peak,
                    }
                )

            medians = {w: float(np.median(per_width[w])) for w in widths}
            for w in widths:
                per_condition_width_sky[(condition, w)].append(medians[w])
            peak_widths[condition].append(min(widths, key=lambda w: (-medians[w], w)))

            x = np.asarray(radius_over_corr, dtype=float)
            y = np.asarray(row_peak_width, dtype=float)
            good = np.isfinite(x) & np.isfinite(y) & (x > 0)
            if np.count_nonzero(good) >= 3 and np.unique(y[good]).size > 1:
                rho = float(spearmanr(np.log(x[good]), y[good]).statistic)
                radius_peak_spearman[condition].append(rho)

    # Planned sky-level contrasts: the previously frozen width against every
    # unchanged alternative, for every field condition. Holm correction is
    # global across this predeclared family of contrasts.
    raw_p: dict[tuple[str, float], float] = {}
    contrasts: dict[str, dict[str, dict]] = defaultdict(dict)
    for condition in conditions:
        selected = np.asarray(
            per_condition_width_sky[(condition, args.frozen_width)], dtype=float
        )
        for w in widths:
            if w == args.frozen_width:
                continue
            alternative = np.asarray(per_condition_width_sky[(condition, w)], dtype=float)
            diffs = selected - alternative
            nonzero = diffs[np.abs(diffs) > 1e-15]
            positives = int(np.count_nonzero(nonzero > 0))
            p = (
                float(binomtest(positives, n=len(nonzero), p=0.5, alternative="two-sided").pvalue)
                if len(nonzero)
                else 1.0
            )
            raw_p[(condition, w)] = p
            contrasts[condition][str(w)] = {
                "alternative_width": w,
                "frozen_minus_alternative_per_sky": [float(v) for v in diffs],
                "frozen_minus_alternative": summary(diffs.tolist()),
                "frozen_greater_count": positives,
                "nonzero_paired_differences": int(len(nonzero)),
                "exact_two_sided_sign_p_raw": p,
            }

    ordered = sorted(raw_p.items(), key=lambda kv: kv[1])
    m = len(ordered)
    running = 0.0
    adjusted: dict[tuple[str, float], float] = {}
    for rank, (key, p) in enumerate(ordered):
        running = max(running, min(1.0, (m - rank) * p))
        adjusted[key] = running
    for (condition, w), adj in adjusted.items():
        contrasts[condition][str(w)]["exact_sign_p_holm_global"] = adj

    condition_results = {}
    for condition in sorted(conditions, key=condition_sort_key):
        condition_results[condition] = {
            "field_correlation_length_x": summary(corr_x[condition]),
            "field_correlation_length_y": summary(corr_y[condition]),
            "field_corr_x_over_y": summary(corr_ratio[condition]),
            "per_width_sky_median_leakage": {
                str(w): per_condition_width_sky[(condition, w)] for w in widths
            },
            "peak_width_counts_across_skies": {
                str(w): int(sum(x == w for x in peak_widths[condition])) for w in widths
            },
            "frozen_width_planned_contrasts": contrasts[condition],
            "within_sky_spearman_log_radius_over_corr_vs_row_peak_width": summary(
                radius_peak_spearman[condition]
            ) if radius_peak_spearman[condition] else {
                "n": 0,
                "mean": float("nan"),
                "median": float("nan"),
                "min": float("nan"),
                "max": float("nan"),
            },
        }

    result = {
        "experiment": "Pontifex CMB metric-isotropic spectrum control",
        "design": {
            "independent_base_skies": args.skies,
            "same_white_noise_across_field_conditions_within_sky": True,
            "theta_panel_fixed_before_fields": True,
            "theta_per_sky": len(thetas),
            "balanced_geometries": list(GEOMETRIES),
            "balanced_occlusions": list(OCCLUSIONS),
            "beam_width_ratios": widths,
            "frozen_reference_width": args.frozen_width,
            "metric_spectral_cutoffs_cycles_per_unit": metric_k0,
            "map_shape": [args.ny, args.nx],
            "replication_unit": "independent base sky seed",
            "null_calibration": "not used: this discriminant tests raw scale-response geometry and field spectrum only",
        },
        "conditions": condition_results,
        "interpretation_contract": {
            "evidence": (
                "the legacy field is audited for metric anisotropy, then the unchanged beam-width ladder is applied to "
                "metric-isotropic fields with predeclared spectral cutoffs using paired white-noise realizations"
            ),
            "geometry_favoring_pattern": (
                "the frozen width 0.5 remains the sky-level leakage peak across substantially different metric-isotropic "
                "field correlation lengths, with no systematic shift of row peak width with radius/correlation-length ratio"
            ),
            "field_coupling_pattern": (
                "the preferred beam width shifts reproducibly with field spectral cutoff or with lesion radius relative "
                "to measured field correlation length"
            ),
            "negative_result_rule": (
                "if correcting the field metric removes the prior width-0.5 preference, the earlier replication is treated "
                "as confounded by the legacy pixel-spectrum generator"
            ),
            "hypothesis": (
                "persistence after this control would strengthen only the synthetic geometric interpretation of the scale "
                "response; it would not establish a physical CMB scale"
            ),
            "not_evidence": (
                "no Planck/ACT data, CMB anomaly, physical nonlocality, topology, or Torus causality is tested here"
            ),
            "dependence_boundary": (
                "theta rows within a sky/field are dependent; inferential contrasts use independent base skies"
            ),
            "data_boundary": (
                "D_assembly, D_student, D_val, and D_test remain disjoint and untouched; none enters this experiment"
            ),
        },
    }

    args.rows.parent.mkdir(parents=True, exist_ok=True)
    with args.rows.open("w", encoding="utf-8") as f:
        for row in persisted:
            f.write(json.dumps(row, allow_nan=True) + "\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, allow_nan=True))


if __name__ == "__main__":
    main()
