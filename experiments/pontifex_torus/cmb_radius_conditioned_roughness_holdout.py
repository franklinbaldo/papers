# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scipy>=1.14",
# ]
# ///
"""Radius-conditioned roughness holdout for the Pontifex CMB synthetic harness.

The preceding locality controls showed that adaptive beam-width gains are highly
sensitive to lesion-scale composition.  A radius-matched analysis then removed
the apparent cohort effect and caused the roughness controller to collapse.
That leaves a narrower, discriminating question: does pre-intervention context
roughness carry predictive information *after conditioning on lesion radius*,
or was roughness mainly acting as a proxy for scale?

Protocol
--------
1. Freeze a new balanced theta panel before any sky is generated.
2. Define three radius strata from theta radii only (no sky/outcome information).
3. On DEVELOPMENT skies only, fit two policies over the same candidate widths:
   * RADIUS: one width per predeclared radius stratum;
   * RADIUS+ROUGHNESS: within each radius stratum, split an outcome-free local
     frequency proxy into two development quantile bins and choose one width per
     cell.
4. The frequency proxy removes the explicit radius multiplier from the earlier
   dimensionless descriptor:

       context_frequency = local_spectral_roughness / radius
                         = RMS(|grad field|) / SD(field)

   It is measured in the unaltered context ring and never uses the altered map,
   leakage outcomes, matched-null scores, or held-out results.
5. Freeze radius edges, roughness edges, and all selected widths before HELD-OUT
   sky seeds are generated.
6. Primary held-out contrast: RADIUS+ROUGHNESS minus RADIUS at the independent
   base-sky level.  Two secondary planned contrasts compare each policy with the
   inherited fixed w=0.5 baseline; exact sign tests are Holm-adjusted across the
   three planned tests.

A positive primary result supports incremental predictive information in local
field texture conditional on coarse lesion scale *within this synthetic harness*.
A negative result says the added roughness split has not earned complexity over a
radius-only policy.  It does not license post-hoc radius bands, extra roughness
bins, richer models, or CMB/Planck/ACT/Torus physical claims.

No assembly/student/validation/test data enter this experiment.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from cmb_beam_scale_holdout import balanced_theta_panel
from cmb_local_spectrum_holdout import bin_index, collect_rows
from cmb_locality_remote_ring_holdout import holm_adjust, sign_test
from cmb_nonlocal_observable_ablation import summary
from cmb_occlusion_mc import GEOMETRIES, OCCLUSIONS


def _strict_quantile_edges(values: list[float], bins: int, label: str) -> list[float]:
    x = np.asarray(values, dtype=float)
    if len(x) < bins:
        raise RuntimeError(f"{label}: not enough values for {bins} bins")
    edges = [float(v) for v in np.quantile(x, [i / bins for i in range(1, bins)])]
    if len(set(round(v, 12) for v in edges)) != len(edges):
        raise RuntimeError(f"{label}: quantile edges collapsed")
    return edges


def annotate_predictor(rows: list[dict], radius_edges: list[float]) -> None:
    for row in rows:
        radius = float(row["radius"])
        roughness = float(row["local_spectral_roughness"])
        if radius <= 0 or roughness <= 0:
            raise RuntimeError("radius and local roughness must be positive")
        frequency = roughness / radius
        if not np.isfinite(frequency) or frequency <= 0:
            raise RuntimeError("context frequency proxy must be finite and positive")
        row["radius_band"] = int(bin_index(radius, radius_edges))
        row["context_frequency_proxy"] = float(frequency)
        row["log_context_frequency_proxy"] = float(np.log(frequency))


def choose_width(
    rows: list[dict],
    *,
    widths: list[float],
    baseline: float,
) -> tuple[float, dict]:
    sky_ids = sorted({int(r["base_sky_id"]) for r in rows})
    if not sky_ids:
        raise RuntimeError("development selection cell is empty")
    per_sky_by_width: dict[float, list[float]] = {w: [] for w in widths}
    for sky_id in sky_ids:
        sky = [r for r in rows if int(r["base_sky_id"]) == sky_id]
        if not sky:
            continue
        for w in widths:
            per_sky_by_width[w].append(
                float(np.median([float(r["observed_leakage_ratio"][str(w)]) for r in sky]))
            )
    scores = {
        w: float(np.median(per_sky_by_width[w]))
        for w in widths
        if per_sky_by_width[w]
    }
    if len(scores) != len(widths):
        raise RuntimeError("selection cell lacks summaries for one or more widths")
    winner = min(widths, key=lambda w: (-scores[w], abs(w - baseline), w))
    return float(winner), {
        "selected_width": float(winner),
        "score_by_width": {str(w): float(scores[w]) for w in widths},
        "per_sky_median_leakage_by_width": {
            str(w): [float(v) for v in per_sky_by_width[w]] for w in widths
        },
        "n_rows": len(rows),
    }


def fit_policies(
    dev_rows: list[dict],
    *,
    radius_bands: int,
    roughness_bins: int,
    widths: list[float],
    baseline: float,
) -> tuple[dict, dict]:
    radius_policy: dict[str, float] = {}
    radius_diag: dict[str, dict] = {}
    rough_edges: dict[str, list[float]] = {}
    full_policy: dict[str, dict[str, float]] = {}
    full_diag: dict[str, dict[str, dict]] = {}

    for rb in range(radius_bands):
        band = [r for r in dev_rows if int(r["radius_band"]) == rb]
        if not band:
            raise RuntimeError(f"radius band {rb} is empty in development")
        winner, diag = choose_width(band, widths=widths, baseline=baseline)
        radius_policy[str(rb)] = winner
        radius_diag[str(rb)] = diag

        edges = _strict_quantile_edges(
            [float(r["log_context_frequency_proxy"]) for r in band],
            roughness_bins,
            f"radius band {rb} roughness",
        )
        rough_edges[str(rb)] = edges
        full_policy[str(rb)] = {}
        full_diag[str(rb)] = {}
        for qb in range(roughness_bins):
            cell = [
                r
                for r in band
                if bin_index(float(r["log_context_frequency_proxy"]), edges) == qb
            ]
            winner, diag = choose_width(cell, widths=widths, baseline=baseline)
            full_policy[str(rb)][str(qb)] = winner
            full_diag[str(rb)][str(qb)] = diag

    return (
        {
            "selected_width_by_radius_band": radius_policy,
            "diagnostics": radius_diag,
        },
        {
            "roughness_edges_by_radius_band": rough_edges,
            "selected_width_by_radius_and_roughness_bin": full_policy,
            "diagnostics": full_diag,
        },
    )


def apply_policies(
    rows: list[dict],
    *,
    radius_policy: dict,
    full_policy: dict,
    baseline: float,
) -> None:
    rough_edges = full_policy["roughness_edges_by_radius_band"]
    width_map = full_policy["selected_width_by_radius_and_roughness_bin"]
    radius_map = radius_policy["selected_width_by_radius_band"]
    for row in rows:
        rb = str(int(row["radius_band"]))
        qb = int(
            bin_index(
                float(row["log_context_frequency_proxy"]),
                [float(v) for v in rough_edges[rb]],
            )
        )
        radius_w = float(radius_map[rb])
        full_w = float(width_map[rb][str(qb)])
        row["roughness_bin_within_radius"] = qb
        row["radius_policy_width"] = radius_w
        row["radius_roughness_policy_width"] = full_w
        row["radius_policy_leakage"] = float(row["observed_leakage_ratio"][str(radius_w)])
        row["radius_roughness_policy_leakage"] = float(
            row["observed_leakage_ratio"][str(full_w)]
        )
        row["fixed_leakage"] = float(row["observed_leakage_ratio"][str(baseline)])


def sky_metrics(rows: list[dict], heldout_skies: int) -> list[dict]:
    out: list[dict] = []
    for sky_id in range(heldout_skies):
        sky = [r for r in rows if int(r["base_sky_id"]) == sky_id]
        if not sky:
            raise RuntimeError(f"held-out sky {sky_id} has no rows")
        radius = float(np.median([float(r["radius_policy_leakage"]) for r in sky]))
        full = float(
            np.median([float(r["radius_roughness_policy_leakage"]) for r in sky])
        )
        fixed = float(np.median([float(r["fixed_leakage"]) for r in sky]))
        out.append(
            {
                "base_sky_id": sky_id,
                "radius_policy_median_leakage": radius,
                "radius_roughness_policy_median_leakage": full,
                "fixed_0.5_median_leakage": fixed,
                "radius_roughness_minus_radius": full - radius,
                "radius_minus_fixed": radius - fixed,
                "radius_roughness_minus_fixed": full - fixed,
            }
        )
    return out


def planned_tests(per_sky: list[dict]) -> dict:
    values = {
        "primary_radius_roughness_minus_radius": [
            float(r["radius_roughness_minus_radius"]) for r in per_sky
        ],
        "secondary_radius_minus_fixed": [float(r["radius_minus_fixed"]) for r in per_sky],
        "secondary_radius_roughness_minus_fixed": [
            float(r["radius_roughness_minus_fixed"]) for r in per_sky
        ],
    }
    tests = {name: sign_test(v) for name, v in values.items()}
    adjusted = holm_adjust(
        {name: float(result["exact_two_sided_sign_p"]) for name, result in tests.items()}
    )
    for name, result in tests.items():
        result["holm_adjusted_p"] = float(adjusted[name])
    return tests


def descriptive_by_radius(rows: list[dict], radius_bands: int) -> dict:
    out = {}
    for rb in range(radius_bands):
        band = [r for r in rows if int(r["radius_band"]) == rb]
        by_sky: dict[int, list[float]] = defaultdict(list)
        for row in band:
            by_sky[int(row["base_sky_id"])].append(
                float(row["radius_roughness_policy_leakage"])
                - float(row["radius_policy_leakage"])
            )
        medians = [float(np.median(v)) for _, v in sorted(by_sky.items()) if v]
        out[str(rb)] = {
            "n_rows": len(band),
            "radius": summary([float(r["radius"]) for r in band]),
            "radius_roughness_minus_radius_per_sky_descriptive": summary(medians),
        }
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dev-skies", type=int, default=12)
    ap.add_argument("--heldout-skies", type=int, default=24)
    ap.add_argument("--theta-per-cell", type=int, default=8)
    ap.add_argument("--radius-bands", type=int, default=3)
    ap.add_argument("--roughness-bins", type=int, default=2)
    ap.add_argument(
        "--beam-width-ratios", nargs="+", type=float, default=[0.125, 0.25, 0.5, 1.0]
    )
    ap.add_argument("--baseline-width", type=float, default=0.5)
    ap.add_argument("--metric-k0", nargs="+", type=float, default=[4.0, 8.0, 16.0])
    ap.add_argument("--ny", type=int, default=64)
    ap.add_argument("--nx", type=int, default=128)
    ap.add_argument("--seed", type=int, default=20260925)
    ap.add_argument(
        "--rows", type=Path, default=Path("pontifex-cmb-radius-conditioned-roughness.jsonl")
    )
    ap.add_argument(
        "--output", type=Path, default=Path("pontifex-cmb-radius-conditioned-roughness.json")
    )
    args = ap.parse_args()

    widths = sorted(set(float(w) for w in args.beam_width_ratios))
    metric_k0 = sorted(set(float(k) for k in args.metric_k0))
    if args.baseline_width not in widths:
        raise ValueError("baseline width must be one of candidate widths")
    if args.dev_skies < 2 or args.heldout_skies < 2 or args.theta_per_cell < 2:
        raise ValueError("need >=2 skies per stage and >=2 theta per cell")
    if args.radius_bands < 2 or args.roughness_bins < 2:
        raise ValueError("need at least two radius bands and two roughness bins")

    # Radius strata are fixed from theta geometry before any synthetic sky exists.
    thetas = balanced_theta_panel(args.seed, args.theta_per_cell)
    radius_edges = _strict_quantile_edges(
        [float(t.radius) for t in thetas], args.radius_bands, "theta radius"
    )

    dev_seed_base = args.seed + 61_000_000_123
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
    annotate_predictor(dev_rows, radius_edges)
    radius_policy, full_policy = fit_policies(
        dev_rows,
        radius_bands=args.radius_bands,
        roughness_bins=args.roughness_bins,
        widths=widths,
        baseline=args.baseline_width,
    )

    # Held-out skies are generated only after all policy choices are frozen.
    held_seed_base = args.seed + 97_000_000_321
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
    annotate_predictor(held_rows, radius_edges)
    apply_policies(
        held_rows,
        radius_policy=radius_policy,
        full_policy=full_policy,
        baseline=args.baseline_width,
    )

    per_sky = sky_metrics(held_rows, args.heldout_skies)
    tests = planned_tests(per_sky)

    radius_band_counts = {
        str(rb): sum(int(r["radius_band"]) == rb for r in held_rows)
        for rb in range(args.radius_bands)
    }
    chosen_radius_counts: dict[str, int] = defaultdict(int)
    chosen_full_counts: dict[str, int] = defaultdict(int)
    for row in held_rows:
        chosen_radius_counts[str(row["radius_policy_width"])] += 1
        chosen_full_counts[str(row["radius_roughness_policy_width"])] += 1

    result = {
        "experiment": "Pontifex CMB radius-conditioned roughness held-out control",
        "design": {
            "theta_panel_fixed_before_skies": True,
            "new_theta_and_sky_seeds_vs_prior_scale_locality_controls": True,
            "theta_per_cell": args.theta_per_cell,
            "theta_count": len(thetas),
            "balanced_geometries": list(GEOMETRIES),
            "balanced_occlusions": list(OCCLUSIONS),
            "radius_bands": args.radius_bands,
            "roughness_bins_within_radius": args.roughness_bins,
            "radius_edges_fixed_without_outcomes": radius_edges,
            "metric_spectral_cutoffs_cycles_per_unit": metric_k0,
            "candidate_widths": widths,
            "fixed_baseline_width": args.baseline_width,
            "development_base_skies": args.dev_skies,
            "heldout_base_skies": args.heldout_skies,
            "replication_unit": "independent base sky seed; theta and spectral rows are nested repeated measurements",
            "heldout_generated_after_policies_frozen": True,
        },
        "predictor_contract": {
            "source_descriptor": "local_spectral_roughness = radius * RMS(metric gradient in unaltered context ring) / SD(context field)",
            "conditional_predictor": "context_frequency_proxy = local_spectral_roughness / radius",
            "explicit_radius_multiplier_removed": True,
            "outcome_free": True,
            "caveat": "the context-ring support still depends on theta geometry and radius; conditioning is coarse, not exact residualization",
        },
        "development": {
            "rows": len(dev_rows),
            "radius_policy": radius_policy,
            "radius_plus_roughness_policy": full_policy,
        },
        "heldout": {
            "rows": len(held_rows),
            "radius_band_row_counts": radius_band_counts,
            "radius_policy_width_counts": dict(sorted(chosen_radius_counts.items())),
            "radius_plus_roughness_policy_width_counts": dict(sorted(chosen_full_counts.items())),
            "per_sky": per_sky,
            "planned_tests": tests,
            "by_radius_band_descriptive_only": descriptive_by_radius(
                held_rows, args.radius_bands
            ),
        },
        "interpretation_contract": {
            "evidence": (
                "the primary held-out test asks whether a frozen context-frequency split adds predictive leakage gain beyond a frozen radius-only policy"
            ),
            "positive_result_rule": (
                "a consistent positive radius+roughness minus radius contrast supports incremental pre-intervention texture information conditional on coarse lesion scale in this synthetic harness"
            ),
            "negative_result_rule": (
                "failure of the primary contrast means roughness has not earned complexity beyond radius stratification; no post-hoc bands, extra bins, or richer controller are licensed"
            ),
            "hypothesis": (
                "any surviving incremental effect may reflect interaction between lesion scale and local field spectrum, but mechanism and locality require separate tests"
            ),
            "not_evidence": (
                "the experiment does not establish a physical CMB scale, Planck/ACT beam law, anomaly, physical nonlocality, topology, or Torus causality"
            ),
            "data_boundary": (
                "D_assembly, D_student, D_val, and D_test remain disjoint and untouched; none enters this synthetic experiment"
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
