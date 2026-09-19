# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scipy>=1.14",
# ]
# ///
"""Held-out test of field-scale modulation for the Pontifex CMB beam response.

Prior controls established two facts inside the synthetic harness:

1. a fixed beam width near 0.5 lesion radii is a reproducible sky-level optimum;
2. row-level preferred width still covaries with lesion radius relative to the
   field correlation length.

This experiment asks whether that second pattern has predictive value rather
than merely descriptive value.

Protocol
--------
* A balanced theta panel is frozen before any sky is generated.
* Development and held-out base sky seeds are disjoint.
* Each base sky yields the same predeclared metric-isotropic spectral conditions.
* On DEVELOPMENT only, log(radius / field-correlation-length) is split into three
  quantile bins. For each bin, one width is selected by maximizing the median
  across development base skies of within-sky median leakage. Ties prefer the
  previously frozen 0.5 baseline, then the smaller width.
* Bin edges and widths are frozen before HELD-OUT skies are generated.
* On held-out base skies, the adaptive rule is compared with the fixed width 0.5.
  The independent base sky seed is the inferential replication unit.

The exact same field realization is used across spectral conditions within a
base sky, so spectral conditions are nested repeated measurements, not
independent replicates.

No assembly/student/validation/test data enter this experiment.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

from cmb_beam_scale_holdout import balanced_theta_panel
from cmb_metric_beam_ladder import responses
from cmb_metric_spectrum_control import e_fold_length, filtered_fields
from cmb_nonlocal_observable_ablation import summary
from cmb_occlusion_mc import GEOMETRIES, OCCLUSIONS


def bin_index(x: float, edges: list[float]) -> int:
    # edges are the interior cut points; outer bins are open-ended so held-out
    # observations never require extrapolating a new model class.
    return int(np.searchsorted(np.asarray(edges, dtype=float), x, side="right"))


def collect_rows(
    *,
    base_seeds: list[int],
    thetas,
    metric_k0: list[float],
    widths: list[float],
    ny: int,
    nx: int,
    stage: str,
) -> list[dict]:
    rows: list[dict] = []
    for base_sky_id, sky_seed in enumerate(base_seeds):
        fields = filtered_fields(ny, nx, sky_seed, metric_k0)
        for condition in [f"metric_k0_{k:g}" for k in metric_k0]:
            field = fields[condition]
            lx = e_fold_length(field, axis=1)
            ly = e_fold_length(field, axis=0)
            corr = float(np.sqrt(lx * ly)) if lx > 0 and ly > 0 else float("nan")
            if not np.isfinite(corr) or corr <= 0:
                raise RuntimeError(f"invalid field correlation length for {condition}")

            for theta in thetas:
                rng = np.random.default_rng(sky_seed + 97_409 * (theta.sample + 1))
                core, beam, ratio = responses(field, theta, rng, widths)
                x = float(np.log(theta.radius / corr))
                rows.append(
                    {
                        "stage": stage,
                        "base_sky_id": base_sky_id,
                        "base_sky_seed": sky_seed,
                        "field_condition": condition,
                        "field_corr_length_x": lx,
                        "field_corr_length_y": ly,
                        "field_corr_length_geomean": corr,
                        "log_radius_over_corr": x,
                        **asdict(theta),
                        "observed_core_rmse": core,
                        "observed_beam_boundary_rmse": {str(w): beam[w] for w in widths},
                        "observed_leakage_ratio": {str(w): ratio[w] for w in widths},
                    }
                )
    return rows


def choose_rule(
    rows: list[dict], widths: list[float], baseline: float, bins: int
) -> tuple[list[float], list[float], dict]:
    x = np.asarray([float(r["log_radius_over_corr"]) for r in rows], dtype=float)
    quantiles = [i / bins for i in range(1, bins)]
    edges = [float(v) for v in np.quantile(x, quantiles)]
    if len(set(round(v, 12) for v in edges)) != len(edges):
        raise RuntimeError("development quantile edges collapsed")

    selected: list[float] = []
    diagnostics: dict[str, dict] = {}
    sky_ids = sorted({int(r["base_sky_id"]) for r in rows})

    for b in range(bins):
        score_by_width: dict[float, float] = {}
        per_sky_by_width: dict[float, list[float]] = {w: [] for w in widths}
        for sky_id in sky_ids:
            subset = [
                r
                for r in rows
                if int(r["base_sky_id"]) == sky_id
                and bin_index(float(r["log_radius_over_corr"]), edges) == b
            ]
            if not subset:
                continue
            for w in widths:
                vals = [float(r["observed_leakage_ratio"][str(w)]) for r in subset]
                per_sky_by_width[w].append(float(np.median(vals)))

        for w in widths:
            if not per_sky_by_width[w]:
                raise RuntimeError(f"development bin {b} has no rows")
            score_by_width[w] = float(np.median(per_sky_by_width[w]))

        # Primary criterion is score. The tie-break is predeclared and favors
        # the established fixed baseline rather than gratuitous complexity.
        winner = min(
            widths,
            key=lambda w: (
                -score_by_width[w],
                abs(w - baseline),
                w,
            ),
        )
        selected.append(float(winner))
        diagnostics[str(b)] = {
            "selected_width": float(winner),
            "score_by_width": {str(w): score_by_width[w] for w in widths},
            "per_sky_median_leakage_by_width": {
                str(w): per_sky_by_width[w] for w in widths
            },
        }

    return edges, selected, diagnostics


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dev-skies", type=int, default=8)
    ap.add_argument("--heldout-skies", type=int, default=16)
    ap.add_argument("--theta-per-cell", type=int, default=2)
    ap.add_argument("--bins", type=int, default=3)
    ap.add_argument(
        "--beam-width-ratios",
        nargs="+",
        type=float,
        default=[0.125, 0.25, 0.5, 1.0],
    )
    ap.add_argument("--baseline-width", type=float, default=0.5)
    ap.add_argument(
        "--metric-k0", nargs="+", type=float, default=[4.0, 8.0, 16.0]
    )
    ap.add_argument("--ny", type=int, default=64)
    ap.add_argument("--nx", type=int, default=128)
    ap.add_argument("--seed", type=int, default=20260919)
    ap.add_argument(
        "--rows",
        type=Path,
        default=Path("pontifex-cmb-scale-modulation-holdout.jsonl"),
    )
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("pontifex-cmb-scale-modulation-holdout.json"),
    )
    args = ap.parse_args()

    widths = sorted(set(float(w) for w in args.beam_width_ratios))
    metric_k0 = sorted(set(float(k) for k in args.metric_k0))
    if args.dev_skies < 2 or args.heldout_skies < 2:
        raise ValueError("need at least two independent skies per stage")
    if args.theta_per_cell < 1 or args.bins < 2:
        raise ValueError("need theta_per_cell >= 1 and bins >= 2")
    if args.baseline_width not in widths:
        raise ValueError("baseline width must be in candidate widths")
    if min(widths) <= 0 or not metric_k0 or min(metric_k0) <= 0:
        raise ValueError("widths and metric spectral cutoffs must be positive")

    thetas = balanced_theta_panel(args.seed, args.theta_per_cell)
    dev_seeds = [args.seed + 100_000_007 * i for i in range(args.dev_skies)]
    dev_rows = collect_rows(
        base_seeds=dev_seeds,
        thetas=thetas,
        metric_k0=metric_k0,
        widths=widths,
        ny=args.ny,
        nx=args.nx,
        stage="development",
    )
    edges, selected_widths, dev_diag = choose_rule(
        dev_rows, widths, args.baseline_width, args.bins
    )

    # Held-out fields are not generated until the entire adaptive rule is frozen.
    heldout_seed_base = args.seed + 20_000_000_033
    heldout_seeds = [
        heldout_seed_base + 100_000_007 * i for i in range(args.heldout_skies)
    ]
    heldout_rows = collect_rows(
        base_seeds=heldout_seeds,
        thetas=thetas,
        metric_k0=metric_k0,
        widths=widths,
        ny=args.ny,
        nx=args.nx,
        stage="heldout",
    )

    per_sky_diff: list[float] = []
    per_sky_adaptive: list[float] = []
    per_sky_baseline: list[float] = []
    per_sky_oracle: list[float] = []
    chosen_counts: dict[str, int] = {str(w): 0 for w in widths}
    per_condition_diffs: dict[str, list[float]] = defaultdict(list)

    for r in heldout_rows:
        b = bin_index(float(r["log_radius_over_corr"]), edges)
        chosen = selected_widths[b]
        r["frozen_modulation_bin"] = b
        r["frozen_adaptive_width"] = chosen
        r["adaptive_leakage"] = float(r["observed_leakage_ratio"][str(chosen)])
        r["baseline_leakage"] = float(
            r["observed_leakage_ratio"][str(args.baseline_width)]
        )
        r["oracle_leakage"] = float(
            max(float(v) for v in r["observed_leakage_ratio"].values())
        )
        chosen_counts[str(chosen)] += 1

    for sky_id in range(args.heldout_skies):
        subset = [r for r in heldout_rows if int(r["base_sky_id"]) == sky_id]
        adaptive = float(np.median([r["adaptive_leakage"] for r in subset]))
        baseline = float(np.median([r["baseline_leakage"] for r in subset]))
        oracle = float(np.median([r["oracle_leakage"] for r in subset]))
        per_sky_adaptive.append(adaptive)
        per_sky_baseline.append(baseline)
        per_sky_oracle.append(oracle)
        per_sky_diff.append(adaptive - baseline)

        for condition in [f"metric_k0_{k:g}" for k in metric_k0]:
            c = [r for r in subset if r["field_condition"] == condition]
            if c:
                per_condition_diffs[condition].append(
                    float(np.median([r["adaptive_leakage"] for r in c]))
                    - float(np.median([r["baseline_leakage"] for r in c]))
                )

    diffs = np.asarray(per_sky_diff, dtype=float)
    nonzero = diffs[np.abs(diffs) > 1e-15]
    positives = int(np.count_nonzero(nonzero > 0))
    sign_p = (
        float(
            binomtest(
                positives, n=len(nonzero), p=0.5, alternative="two-sided"
            ).pvalue
        )
        if len(nonzero)
        else 1.0
    )

    adaptive = np.asarray(per_sky_adaptive, dtype=float)
    baseline = np.asarray(per_sky_baseline, dtype=float)
    oracle = np.asarray(per_sky_oracle, dtype=float)
    possible = oracle - baseline
    realized = adaptive - baseline
    recoverable_fraction = np.divide(
        realized,
        possible,
        out=np.full_like(realized, np.nan),
        where=np.abs(possible) > 1e-15,
    )

    result = {
        "experiment": "Pontifex CMB radius/correlation-length modulation held-out test",
        "design": {
            "theta_panel_fixed_before_skies": True,
            "theta_per_base_sky_per_condition": len(thetas),
            "balanced_geometries": list(GEOMETRIES),
            "balanced_occlusions": list(OCCLUSIONS),
            "metric_spectral_cutoffs_cycles_per_unit": metric_k0,
            "candidate_widths": widths,
            "fixed_baseline_width": args.baseline_width,
            "development_base_skies": args.dev_skies,
            "heldout_base_skies": args.heldout_skies,
            "modulation_bins": args.bins,
            "replication_unit": "independent base sky seed; spectral conditions are nested repeated measurements",
            "heldout_generated_after_rule_frozen": True,
        },
        "frozen_rule": {
            "predictor": "log(lesion_radius / measured_field_correlation_length_geomean)",
            "interior_bin_edges": edges,
            "selected_width_by_bin": selected_widths,
            "development_diagnostics": dev_diag,
        },
        "heldout": {
            "adaptive_width_counts": chosen_counts,
            "per_sky_adaptive_median_leakage": per_sky_adaptive,
            "per_sky_fixed_0.5_median_leakage": per_sky_baseline,
            "per_sky_oracle_median_leakage_descriptive_only": per_sky_oracle,
            "adaptive_minus_fixed_per_sky": per_sky_diff,
            "adaptive_minus_fixed": summary(per_sky_diff),
            "adaptive_greater_count": positives,
            "nonzero_paired_differences": int(len(nonzero)),
            "exact_two_sided_sign_p": sign_p,
            "per_condition_adaptive_minus_fixed_descriptive": {
                k: summary(v) for k, v in sorted(per_condition_diffs.items())
            },
            "recoverable_oracle_gain_fraction_descriptive": summary(
                recoverable_fraction[np.isfinite(recoverable_fraction)].tolist()
            ),
        },
        "interpretation_contract": {
            "evidence": (
                "a modulation rule learned only on development base skies is compared against the previously frozen "
                "width-0.5 baseline on disjoint held-out base skies"
            ),
            "positive_result_rule": (
                "a consistent positive held-out sky-level adaptive-minus-fixed contrast supports predictive value in "
                "radius/correlation-length modulation within the synthetic harness"
            ),
            "negative_result_rule": (
                "if the adaptive rule does not beat the frozen 0.5 baseline on held-out base skies, the earlier row-level "
                "Spearman pattern is retained as descriptive covariance, not promoted to a predictive control law"
            ),
            "oracle_boundary": (
                "the per-row oracle is reported only as a ceiling and never participates in rule fitting, binning, or inference"
            ),
            "not_evidence": (
                "this does not establish a physical CMB scale, Planck/ACT beam law, anomaly, physical nonlocality, topology, "
                "or Torus causality"
            ),
            "data_boundary": (
                "D_assembly, D_student, D_val, and D_test remain disjoint and untouched; none enters this experiment"
            ),
        },
    }

    args.rows.parent.mkdir(parents=True, exist_ok=True)
    with args.rows.open("w", encoding="utf-8") as f:
        for row in dev_rows + heldout_rows:
            f.write(json.dumps(row) + "\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, allow_nan=True))


if __name__ == "__main__":
    main()
