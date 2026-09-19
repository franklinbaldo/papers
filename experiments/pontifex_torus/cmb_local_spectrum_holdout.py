# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scipy>=1.14",
# ]
# ///
"""Held-out test of a genuinely local spectral descriptor for Pontifex CMB.

The previous radius/global-correlation-length controller recovered only a small
fraction of the per-row oracle gain and did not beat the frozen width-0.5
baseline reliably on held-out skies.  This experiment tests the narrower next
hypothesis: useful scale information, if present, may be local to the lesion
context rather than captured by one global field correlation length.

Protocol
--------
* Freeze a balanced theta panel before generating any sky.
* Use metric-isotropic synthetic fields at predeclared k0 = 4, 8, 16.
* Compute one outcome-free LOCAL descriptor from the unaltered context ring:

      local_roughness = radius * RMS(|grad field|) / SD(field)

  where gradients use the same unit metric as the lesion/beam geometry and the
  context is outside the directly altered core.  Larger values mean more local
  spatial variation per lesion radius.
* On DEVELOPMENT skies only, split log(local_roughness) into three quantile bins
  and choose one of the unchanged beam widths {0.125, 0.25, 0.5, 1.0} per bin.
  Ties favor the already-established 0.5 baseline, then the smaller width.
* Freeze edges and widths before HELD-OUT skies are generated.
* Compare the local adaptive rule with fixed width 0.5 at the independent base-
  sky level.  Spectral conditions are nested repeated measurements, not
  independent replicates.

The descriptor never uses the altered field, leakage outcome, matched-null
scores, or held-out outcomes.  No assembly/student/validation/test data enter.
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
from cmb_metric_spectrum_control import filtered_fields
from cmb_nonlocal_observable_ablation import summary
from cmb_occlusion_mc import GEOMETRIES, OCCLUSIONS, synthetic_masks


def bin_index(x: float, edges: list[float]) -> int:
    return int(np.searchsorted(np.asarray(edges, dtype=float), x, side="right"))


def local_spectral_roughness(field: np.ndarray, theta) -> tuple[float, int]:
    """Outcome-free dimensionless local-frequency proxy around one lesion.

    The context is the synthetic mask's immediate outer ring.  It excludes the
    directly modified core.  Gradients are expressed per unit metric: x spans
    one unit over nx samples and the effective y coordinate (0.5*y in the mask)
    also spans one unit over ny samples.
    """
    core, boundary, _rr, _angle = synthetic_masks(field.shape, theta)
    context = boundary & ~core
    n = int(np.count_nonzero(context))
    if n < 4:
        return float("nan"), n

    ny, nx = field.shape
    # x is periodic in the synthetic geometry.
    gx = (np.roll(field, -1, axis=1) - np.roll(field, 1, axis=1)) / (2.0 / nx)
    # y is not wrapped by synthetic_masks; use a non-periodic finite difference.
    gy = np.gradient(field, 1.0 / ny, axis=0, edge_order=1)

    local = np.asarray(field[context], dtype=float)
    scale = float(np.std(local, ddof=1)) if local.size > 1 else 0.0
    grad_rms = float(np.sqrt(np.mean(gx[context] ** 2 + gy[context] ** 2)))
    if not np.isfinite(scale) or scale <= 1e-12 or not np.isfinite(grad_rms):
        return float("nan"), n
    return float(theta.radius * grad_rms / scale), n


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
            for theta in thetas:
                roughness, context_n = local_spectral_roughness(field, theta)
                if not np.isfinite(roughness) or roughness <= 0:
                    continue
                rng = np.random.default_rng(sky_seed + 97_409 * (theta.sample + 1))
                core, beam, ratio = responses(field, theta, rng, widths)
                rows.append(
                    {
                        "stage": stage,
                        "base_sky_id": base_sky_id,
                        "base_sky_seed": sky_seed,
                        "field_condition": condition,
                        "local_spectral_roughness": roughness,
                        "log_local_spectral_roughness": float(np.log(roughness)),
                        "context_pixels": context_n,
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
    x = np.asarray([float(r["log_local_spectral_roughness"]) for r in rows], dtype=float)
    edges = [float(v) for v in np.quantile(x, [i / bins for i in range(1, bins)])]
    if len(set(round(v, 12) for v in edges)) != len(edges):
        raise RuntimeError("development descriptor quantile edges collapsed")

    sky_ids = sorted({int(r["base_sky_id"]) for r in rows})
    selected: list[float] = []
    diagnostics: dict[str, dict] = {}
    for b in range(bins):
        per_sky_by_width: dict[float, list[float]] = {w: [] for w in widths}
        for sky_id in sky_ids:
            subset = [
                r
                for r in rows
                if int(r["base_sky_id"]) == sky_id
                and bin_index(float(r["log_local_spectral_roughness"]), edges) == b
            ]
            if not subset:
                continue
            for w in widths:
                per_sky_by_width[w].append(
                    float(np.median([float(r["observed_leakage_ratio"][str(w)]) for r in subset]))
                )

        score_by_width: dict[float, float] = {}
        for w in widths:
            if not per_sky_by_width[w]:
                raise RuntimeError(f"development bin {b} has no sky summaries")
            score_by_width[w] = float(np.median(per_sky_by_width[w]))

        winner = min(widths, key=lambda w: (-score_by_width[w], abs(w - baseline), w))
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
    ap.add_argument("--dev-skies", type=int, default=12)
    ap.add_argument("--heldout-skies", type=int, default=24)
    ap.add_argument("--theta-per-cell", type=int, default=2)
    ap.add_argument("--bins", type=int, default=3)
    ap.add_argument(
        "--beam-width-ratios", nargs="+", type=float, default=[0.125, 0.25, 0.5, 1.0]
    )
    ap.add_argument("--baseline-width", type=float, default=0.5)
    ap.add_argument("--metric-k0", nargs="+", type=float, default=[4.0, 8.0, 16.0])
    ap.add_argument("--ny", type=int, default=64)
    ap.add_argument("--nx", type=int, default=128)
    ap.add_argument("--seed", type=int, default=20260920)
    ap.add_argument(
        "--rows", type=Path, default=Path("pontifex-cmb-local-spectrum-holdout.jsonl")
    )
    ap.add_argument(
        "--output", type=Path, default=Path("pontifex-cmb-local-spectrum-holdout.json")
    )
    args = ap.parse_args()

    widths = sorted(set(float(w) for w in args.beam_width_ratios))
    metric_k0 = sorted(set(float(k) for k in args.metric_k0))
    if args.dev_skies < 2 or args.heldout_skies < 2:
        raise ValueError("need at least two independent skies per stage")
    if args.theta_per_cell < 1 or args.bins < 2:
        raise ValueError("need theta_per_cell >= 1 and bins >= 2")
    if args.baseline_width not in widths:
        raise ValueError("baseline width must be a candidate width")
    if min(widths) <= 0 or min(metric_k0) <= 0:
        raise ValueError("widths and spectral cutoffs must be positive")

    # New seed/panel: no sky or theta outcome inspected in prior scale-controller
    # experiments participates in this confirmatory test.
    thetas = balanced_theta_panel(args.seed, args.theta_per_cell)
    dev_seed_base = args.seed + 40_000_000_081
    dev_seeds = [dev_seed_base + 100_000_007 * i for i in range(args.dev_skies)]
    dev_rows = collect_rows(
        base_seeds=dev_seeds,
        thetas=thetas,
        metric_k0=metric_k0,
        widths=widths,
        ny=args.ny,
        nx=args.nx,
        stage="development",
    )
    edges, selected_widths, development_diagnostics = choose_rule(
        dev_rows, widths, args.baseline_width, args.bins
    )

    # Held-out fields are generated only after descriptor edges and width choices
    # are frozen.
    held_seed_base = args.seed + 80_000_000_163
    held_seeds = [held_seed_base + 100_000_007 * i for i in range(args.heldout_skies)]
    held_rows = collect_rows(
        base_seeds=held_seeds,
        thetas=thetas,
        metric_k0=metric_k0,
        widths=widths,
        ny=args.ny,
        nx=args.nx,
        stage="heldout",
    )

    chosen_counts = {str(w): 0 for w in widths}
    for r in held_rows:
        b = bin_index(float(r["log_local_spectral_roughness"]), edges)
        chosen = selected_widths[b]
        r["frozen_local_spectrum_bin"] = b
        r["frozen_adaptive_width"] = chosen
        r["adaptive_leakage"] = float(r["observed_leakage_ratio"][str(chosen)])
        r["baseline_leakage"] = float(r["observed_leakage_ratio"][str(args.baseline_width)])
        r["oracle_leakage"] = float(max(float(v) for v in r["observed_leakage_ratio"].values()))
        chosen_counts[str(chosen)] += 1

    per_sky_diff: list[float] = []
    per_sky_adaptive: list[float] = []
    per_sky_baseline: list[float] = []
    per_sky_oracle: list[float] = []
    per_condition_diffs: dict[str, list[float]] = defaultdict(list)

    for sky_id in range(args.heldout_skies):
        subset = [r for r in held_rows if int(r["base_sky_id"]) == sky_id]
        if not subset:
            raise RuntimeError(f"held-out sky {sky_id} has no valid local-descriptor rows")
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
        float(binomtest(positives, n=len(nonzero), p=0.5, alternative="two-sided").pvalue)
        if len(nonzero)
        else 1.0
    )

    adaptive = np.asarray(per_sky_adaptive, dtype=float)
    baseline = np.asarray(per_sky_baseline, dtype=float)
    oracle = np.asarray(per_sky_oracle, dtype=float)
    possible = oracle - baseline
    realized = adaptive - baseline
    recoverable = np.divide(
        realized,
        possible,
        out=np.full_like(realized, np.nan),
        where=np.abs(possible) > 1e-15,
    )

    dev_descriptor = [float(r["local_spectral_roughness"]) for r in dev_rows]
    held_descriptor = [float(r["local_spectral_roughness"]) for r in held_rows]
    result = {
        "experiment": "Pontifex CMB local-spectrum modulation held-out test",
        "design": {
            "theta_panel_fixed_before_skies": True,
            "new_theta_panel_and_sky_seeds_vs_prior_controller_test": True,
            "theta_per_base_sky_per_condition": len(thetas),
            "balanced_geometries": list(GEOMETRIES),
            "balanced_occlusions": list(OCCLUSIONS),
            "metric_spectral_cutoffs_cycles_per_unit": metric_k0,
            "candidate_widths": widths,
            "fixed_baseline_width": args.baseline_width,
            "development_base_skies": args.dev_skies,
            "heldout_base_skies": args.heldout_skies,
            "modulation_bins": args.bins,
            "descriptor": "radius * RMS(metric gradient in unaltered context ring) / SD(field in context ring)",
            "descriptor_outcome_free": True,
            "heldout_generated_after_rule_frozen": True,
            "replication_unit": "independent base sky seed; spectral conditions are nested repeated measurements",
        },
        "descriptor_audit": {
            "development_rows": len(dev_rows),
            "heldout_rows": len(held_rows),
            "development_local_roughness": summary(dev_descriptor),
            "heldout_local_roughness": summary(held_descriptor),
            "minimum_context_pixels_development": int(min(r["context_pixels"] for r in dev_rows)),
            "minimum_context_pixels_heldout": int(min(r["context_pixels"] for r in held_rows)),
        },
        "frozen_rule": {
            "predictor": "log(local_spectral_roughness)",
            "interior_bin_edges": edges,
            "selected_width_by_bin": selected_widths,
            "development_diagnostics": development_diagnostics,
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
                recoverable[np.isfinite(recoverable)].tolist()
            ),
        },
        "interpretation_contract": {
            "evidence": (
                "one predeclared local, outcome-free spectral descriptor is fit only on development skies and its frozen "
                "width rule is compared with the pre-existing 0.5 baseline on new held-out skies"
            ),
            "positive_result_rule": (
                "a consistent positive held-out sky-level adaptive-minus-fixed contrast supports predictive information "
                "in local pre-intervention field roughness within this synthetic harness"
            ),
            "negative_result_rule": (
                "failure to beat width 0.5 keeps local roughness as a descriptive correlate at most; no richer local "
                "controller should be introduced as a rescue without a new development/held-out protocol"
            ),
            "oracle_boundary": (
                "the row oracle is a descriptive ceiling only and never participates in descriptor definition, binning, "
                "width selection, or inference"
            ),
            "hypothesis": (
                "if this simple local roughness succeeds, a local field-scale interaction becomes a candidate mechanism; "
                "the mechanism itself would still require separate falsification"
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
        for row in dev_rows + held_rows:
            f.write(json.dumps(row) + "\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
