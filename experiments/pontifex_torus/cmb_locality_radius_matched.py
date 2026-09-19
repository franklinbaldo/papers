# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scipy>=1.14",
# ]
# ///
"""Radius/shape-matched follow-up to the Pontifex CMB locality cohort shift.

The preceding nested-cohort ablation showed that the multi-remote geometry gate
strongly changed held-out controller gain and preferentially removed large
lesions.  In that sparse 60-theta panel, however, the removed and retained
cohorts had *zero lesion-radius common support*: every SINGLE-only lesion was
larger than every MULTI-retained lesion.  A radius-matched analysis on that panel
would therefore be impossible rather than merely underpowered.

This experiment repairs that identifiability problem without using outcomes:

1. Generate a denser balanced theta panel.
2. Apply the same outcome-free SINGLE (+0.5 remote) and MULTI
   (+0.25/+0.5/+0.75 remotes) geometry gates.
3. Inside each exact geometry x occlusion stratum, match SINGLE-only theta rows
   one-to-one to MULTI-retained rows by Hungarian assignment using only
   log-radius and log-aspect, under fixed calipers.
4. Generate development skies only after the matched theta pairs are frozen.
5. Fit one shared +0.5 remote-roughness controller on the union of both matched
   groups, using development skies only.
6. Freeze the controller, generate disjoint held-out skies, and compare
   controller gain (adaptive - fixed w=0.5) within each matched pair.

The independent inferential unit is the held-out base-sky seed.  Pair- and
spectrum-level rows are aggregated within each sky before exact sign tests.
Matching, gates, calipers, predictor, bins, widths, and tests are all fixed before
held-out outcomes exist.

No assembly/student/validation/test data enter this experiment.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment

from cmb_beam_scale_holdout import balanced_theta_panel
from cmb_local_spectrum_holdout import bin_index
from cmb_locality_remote_ring_holdout import (
    choose_rule,
    collect_rows,
    geometry_audit as single_geometry_audit,
    holm_adjust,
    sign_test,
)
from cmb_nonlocal_observable_ablation import summary
from cmb_remote_ensemble_locality_holdout import geometry_audit as multi_geometry_audit


def sample_ids(thetas) -> set[int]:
    return {int(theta.sample) for theta in thetas}


def theta_meta(theta) -> dict:
    return {
        "sample": int(theta.sample),
        "radius": float(theta.radius),
        "aspect": float(theta.aspect),
        "geometry": str(theta.geometry),
        "occlusion": str(theta.occlusion),
    }


def cohort_summary(thetas) -> dict:
    if not thetas:
        return {
            "n": 0,
            "radius": summary([]),
            "aspect": summary([]),
            "geometry_counts": {},
            "occlusion_counts": {},
        }
    return {
        "n": len(thetas),
        "radius": summary([float(t.radius) for t in thetas]),
        "aspect": summary([float(t.aspect) for t in thetas]),
        "geometry_counts": dict(Counter(str(t.geometry) for t in thetas)),
        "occlusion_counts": dict(Counter(str(t.occlusion) for t in thetas)),
    }


def match_pairs(
    rejected,
    retained,
    *,
    max_abs_log_radius: float,
    max_abs_log_aspect: float,
    aspect_weight: float,
) -> list[dict]:
    """Outcome-free 1:1 matching within exact geometry x occlusion strata."""
    pairs: list[dict] = []
    pair_id = 0
    for geometry in sorted({str(t.geometry) for t in rejected + retained}):
        for occlusion in sorted({str(t.occlusion) for t in rejected + retained}):
            left = [
                t
                for t in rejected
                if str(t.geometry) == geometry and str(t.occlusion) == occlusion
            ]
            right = [
                t
                for t in retained
                if str(t.geometry) == geometry and str(t.occlusion) == occlusion
            ]
            if not left or not right:
                continue

            invalid = 1e9
            cost = np.full((len(left), len(right)), invalid, dtype=float)
            dr_cache = np.full_like(cost, np.nan)
            da_cache = np.full_like(cost, np.nan)
            for i, a in enumerate(left):
                for j, b in enumerate(right):
                    dr = abs(float(np.log(a.radius) - np.log(b.radius)))
                    da = abs(float(np.log(a.aspect) - np.log(b.aspect)))
                    dr_cache[i, j] = dr
                    da_cache[i, j] = da
                    if dr <= max_abs_log_radius and da <= max_abs_log_aspect:
                        cost[i, j] = dr + aspect_weight * da

            rows, cols = linear_sum_assignment(cost)
            for i, j in zip(rows, cols, strict=True):
                if cost[i, j] >= invalid / 2:
                    continue
                a = left[int(i)]
                b = right[int(j)]
                pairs.append(
                    {
                        "pair_id": pair_id,
                        "single_only_sample": int(a.sample),
                        "multi_retained_sample": int(b.sample),
                        "geometry": geometry,
                        "occlusion": occlusion,
                        "single_only_radius": float(a.radius),
                        "multi_retained_radius": float(b.radius),
                        "radius_ratio_single_only_over_retained": float(
                            a.radius / b.radius
                        ),
                        "abs_log_radius_diff": float(dr_cache[i, j]),
                        "single_only_aspect": float(a.aspect),
                        "multi_retained_aspect": float(b.aspect),
                        "abs_log_aspect_diff": float(da_cache[i, j]),
                        "matching_cost": float(cost[i, j]),
                    }
                )
                pair_id += 1
    return pairs


def annotate_rows(rows: list[dict], pairs: list[dict]) -> None:
    lookup: dict[int, tuple[int, str]] = {}
    for pair in pairs:
        lookup[int(pair["single_only_sample"])] = (int(pair["pair_id"]), "single_only")
        lookup[int(pair["multi_retained_sample"])] = (
            int(pair["pair_id"]),
            "multi_retained",
        )
    for row in rows:
        pair_id, role = lookup[int(row["sample"])]
        row["pair_id"] = int(pair_id)
        row["match_role"] = role


def apply_controller(
    rows: list[dict],
    *,
    edges: list[float],
    selected_widths: list[float],
    baseline: float,
) -> None:
    for row in rows:
        b = bin_index(float(row["log_remote_spectral_roughness"]), edges)
        width = float(selected_widths[b])
        adaptive = float(row["observed_leakage_ratio"][str(width)])
        fixed = float(row["observed_leakage_ratio"][str(baseline)])
        row["controller_bin"] = int(b)
        row["controller_width"] = width
        row["controller_leakage"] = adaptive
        row["fixed_leakage"] = fixed
        row["controller_gain"] = adaptive - fixed


def sky_pair_metrics(rows: list[dict], heldout_skies: int) -> list[dict]:
    per_sky: list[dict] = []
    for sky_id in range(heldout_skies):
        sky = [r for r in rows if int(r["base_sky_id"]) == sky_id]
        grouped: dict[tuple[int, str], list[dict]] = defaultdict(list)
        for row in sky:
            grouped[(int(row["pair_id"]), str(row["field_condition"]))].append(row)

        pair_diffs = []
        single_gains = []
        retained_gains = []
        for (_pair_id, _condition), group in grouped.items():
            by_role = {str(r["match_role"]): r for r in group}
            if set(by_role) != {"single_only", "multi_retained"}:
                raise RuntimeError("matched pair/condition is incomplete")
            single_gain = float(by_role["single_only"]["controller_gain"])
            retained_gain = float(by_role["multi_retained"]["controller_gain"])
            pair_diffs.append(single_gain - retained_gain)
            single_gains.append(single_gain)
            retained_gains.append(retained_gain)

        if not pair_diffs:
            raise RuntimeError(f"held-out sky {sky_id} has no matched pairs")
        per_sky.append(
            {
                "base_sky_id": int(sky_id),
                "single_only_gain": float(np.median(single_gains)),
                "multi_retained_gain": float(np.median(retained_gains)),
                "matched_gain_difference": float(np.median(pair_diffs)),
                "n_pair_condition_rows": len(pair_diffs),
            }
        )
    return per_sky


def planned_tests(per_sky: list[dict]) -> dict:
    values = {
        "matched_single_only_minus_retained": [
            float(r["matched_gain_difference"]) for r in per_sky
        ],
        "single_only_vs_fixed": [float(r["single_only_gain"]) for r in per_sky],
        "multi_retained_vs_fixed": [
            float(r["multi_retained_gain"]) for r in per_sky
        ],
    }
    tests = {name: sign_test(v) for name, v in values.items()}
    adjusted = holm_adjust(
        {name: float(result["exact_two_sided_sign_p"]) for name, result in tests.items()}
    )
    for name, result in tests.items():
        result["holm_adjusted_p"] = float(adjusted[name])
    return tests


def condition_diagnostics(rows: list[dict]) -> dict:
    out = {}
    for condition in sorted({str(r["field_condition"]) for r in rows}):
        sub = [r for r in rows if str(r["field_condition"]) == condition]
        by_sky_pair: dict[tuple[int, int], dict[str, float]] = defaultdict(dict)
        for row in sub:
            by_sky_pair[(int(row["base_sky_id"]), int(row["pair_id"]))][
                str(row["match_role"])
            ] = float(row["controller_gain"])
        diffs = []
        for roles in by_sky_pair.values():
            if set(roles) == {"single_only", "multi_retained"}:
                diffs.append(roles["single_only"] - roles["multi_retained"])
        out[condition] = summary(diffs)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dev-skies", type=int, default=12)
    ap.add_argument("--heldout-skies", type=int, default=24)
    ap.add_argument("--theta-per-cell", type=int, default=40)
    ap.add_argument("--bins", type=int, default=3)
    ap.add_argument(
        "--beam-width-ratios", nargs="+", type=float, default=[0.125, 0.25, 0.5, 1.0]
    )
    ap.add_argument("--baseline-width", type=float, default=0.5)
    ap.add_argument("--metric-k0", nargs="+", type=float, default=[4.0, 8.0, 16.0])
    ap.add_argument(
        "--remote-shifts", nargs="+", type=float, default=[0.25, 0.5, 0.75]
    )
    ap.add_argument("--single-remote-shift", type=float, default=0.5)
    ap.add_argument("--max-abs-log-radius", type=float, default=0.10)
    ap.add_argument("--max-abs-log-aspect", type=float, default=0.70)
    ap.add_argument("--aspect-weight", type=float, default=0.25)
    ap.add_argument("--ny", type=int, default=64)
    ap.add_argument("--nx", type=int, default=128)
    ap.add_argument("--seed", type=int, default=20260924)
    ap.add_argument(
        "--rows", type=Path, default=Path("pontifex-cmb-locality-radius-matched.jsonl")
    )
    ap.add_argument(
        "--output", type=Path, default=Path("pontifex-cmb-locality-radius-matched.json")
    )
    args = ap.parse_args()

    widths = sorted(set(float(w) for w in args.beam_width_ratios))
    metric_k0 = sorted(set(float(k) for k in args.metric_k0))
    remote_shifts = sorted(set(float(s) % 1.0 for s in args.remote_shifts))
    if args.baseline_width not in widths:
        raise ValueError("baseline width must be among candidate widths")
    if args.single_remote_shift not in remote_shifts:
        raise ValueError("single remote shift must be included in remote shifts")
    if args.theta_per_cell < 2 or args.dev_skies < 2 or args.heldout_skies < 2:
        raise ValueError("need theta_per_cell >=2 and at least two skies per stage")

    raw_thetas = balanced_theta_panel(args.seed, args.theta_per_cell)
    single_thetas, single_audit = single_geometry_audit(
        raw_thetas, (args.ny, args.nx), args.single_remote_shift
    )
    multi_thetas, multi_audit = multi_geometry_audit(
        raw_thetas, (args.ny, args.nx), remote_shifts
    )
    single_ids = sample_ids(single_thetas)
    multi_ids = sample_ids(multi_thetas)
    if not multi_ids <= single_ids:
        raise RuntimeError("MULTI geometry mask must be a subset of SINGLE mask")

    single_only = [t for t in single_thetas if int(t.sample) not in multi_ids]
    retained = list(multi_thetas)
    pairs = match_pairs(
        single_only,
        retained,
        max_abs_log_radius=args.max_abs_log_radius,
        max_abs_log_aspect=args.max_abs_log_aspect,
        aspect_weight=args.aspect_weight,
    )
    if len(pairs) < 12:
        raise RuntimeError(f"outcome-free matching produced only {len(pairs)} pairs; need >=12")

    theta_by_id = {int(t.sample): t for t in single_thetas}
    matched_ids = {
        sample_id
        for pair in pairs
        for sample_id in (
            int(pair["single_only_sample"]),
            int(pair["multi_retained_sample"]),
        )
    }
    matched_thetas = [theta_by_id[i] for i in sorted(matched_ids)]

    dev_seed_base = args.seed + 50_000_000_091
    dev_seeds = [dev_seed_base + 100_000_007 * i for i in range(args.dev_skies)]
    dev_rows = collect_rows(
        base_seeds=dev_seeds,
        thetas=matched_thetas,
        metric_k0=metric_k0,
        widths=widths,
        ny=args.ny,
        nx=args.nx,
        stage="development",
        remote_shift=args.single_remote_shift,
    )
    annotate_rows(dev_rows, pairs)

    edges, selected_widths, diagnostics = choose_rule(
        dev_rows,
        predictor_key="log_remote_spectral_roughness",
        widths=widths,
        baseline=args.baseline_width,
        bins=args.bins,
    )
    controller = {
        "predictor": "log_remote_spectral_roughness",
        "edges": [float(x) for x in edges],
        "selected_widths": [float(x) for x in selected_widths],
        "diagnostics": diagnostics,
    }

    # Held-out skies are generated only after matching and controller fitting are frozen.
    held_seed_base = args.seed + 90_000_000_181
    held_seeds = [held_seed_base + 100_000_007 * i for i in range(args.heldout_skies)]
    held_rows = collect_rows(
        base_seeds=held_seeds,
        thetas=matched_thetas,
        metric_k0=metric_k0,
        widths=widths,
        ny=args.ny,
        nx=args.nx,
        stage="heldout",
        remote_shift=args.single_remote_shift,
    )
    annotate_rows(held_rows, pairs)
    apply_controller(
        held_rows,
        edges=controller["edges"],
        selected_widths=controller["selected_widths"],
        baseline=args.baseline_width,
    )

    per_sky = sky_pair_metrics(held_rows, args.heldout_skies)
    tests = planned_tests(per_sky)

    pair_radius_diffs = [float(p["abs_log_radius_diff"]) for p in pairs]
    pair_aspect_diffs = [float(p["abs_log_aspect_diff"]) for p in pairs]
    pair_radius_ratios = [float(p["radius_ratio_single_only_over_retained"]) for p in pairs]

    output = {
        "experiment": "pontifex_cmb_locality_radius_matched",
        "design": {
            "seed": args.seed,
            "raw_theta": len(raw_thetas),
            "single_accepted_theta": len(single_thetas),
            "multi_accepted_theta": len(multi_thetas),
            "single_only_theta": len(single_only),
            "matched_pairs": len(pairs),
            "matched_theta": len(matched_thetas),
            "theta_per_cell": args.theta_per_cell,
            "dev_skies": args.dev_skies,
            "heldout_skies": args.heldout_skies,
            "metric_k0": metric_k0,
            "candidate_widths": widths,
            "baseline_width": float(args.baseline_width),
            "bins": args.bins,
            "single_remote_shift": float(args.single_remote_shift),
            "remote_shifts": remote_shifts,
            "matching": {
                "exact_strata": ["geometry", "occlusion"],
                "cost": "abs(log radius diff) + aspect_weight * abs(log aspect diff)",
                "max_abs_log_radius": float(args.max_abs_log_radius),
                "max_abs_log_aspect": float(args.max_abs_log_aspect),
                "aspect_weight": float(args.aspect_weight),
                "assignment": "one-to-one Hungarian without replacement; outcome-free",
            },
            "primary_contrast": "matched SINGLE-only controller gain - matched MULTI-retained controller gain",
            "inferential_unit": "independent held-out base-sky seed",
            "multiplicity": "three predeclared two-sided exact sign tests with Holm adjustment",
        },
        "geometry": {
            "single_audit": single_audit,
            "multi_audit": multi_audit,
            "single_cohort": cohort_summary(single_thetas),
            "multi_cohort": cohort_summary(multi_thetas),
            "single_only_cohort": cohort_summary(single_only),
            "radius_common_support_before_matching": {
                "single_only_min": float(min(t.radius for t in single_only)),
                "single_only_max": float(max(t.radius for t in single_only)),
                "multi_retained_min": float(min(t.radius for t in retained)),
                "multi_retained_max": float(max(t.radius for t in retained)),
            },
            "matched_balance": {
                "abs_log_radius_diff": summary(pair_radius_diffs),
                "radius_ratio_single_only_over_retained": summary(pair_radius_ratios),
                "abs_log_aspect_diff": summary(pair_aspect_diffs),
                "pairs_by_geometry": dict(Counter(str(p["geometry"]) for p in pairs)),
                "pairs_by_occlusion": dict(Counter(str(p["occlusion"]) for p in pairs)),
            },
            "pairs": pairs,
        },
        "development": {
            "rows": len(dev_rows),
            "controller": controller,
        },
        "heldout": {
            "rows": len(held_rows),
            "planned_tests": tests,
            "per_condition_matched_gain_difference": condition_diagnostics(held_rows),
            "per_sky": per_sky,
        },
        "interpretation_contract": {
            "evidence_if_primary_is_null": "after outcome-free radius/aspect matching within exact geometry and occlusion strata, the previous gate-associated gain difference is not detectably preserved; this weakens claims that MULTI-gate membership itself carries predictive information beyond matched lesion geometry",
            "evidence_if_primary_is_nonzero": "the gate-associated gain difference survives strict outcome-free matching on radius, aspect, geometry, and occlusion; lesion scale/composition alone is insufficient to explain the cohort sensitivity",
            "not_established": [
                "that any controller is a physical CMB scale law",
                "that remote roughness is lesion-local information",
                "that the matching eliminates all geometry or field-state confounding",
                "that Planck/ACT data exhibit this synthetic effect",
                "physical non-locality or Pontifex/Torus causality",
            ],
            "partition_statement": "D_assembly, D_student, D_val, and D_test are absent; matching uses geometry only, development and held-out sky seeds are disjoint, and held-out outcomes choose neither pairs nor controller rules.",
        },
    }

    args.rows.parent.mkdir(parents=True, exist_ok=True)
    with args.rows.open("w", encoding="utf-8") as fh:
        for row in dev_rows + held_rows:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "design": output["design"],
                "geometry": {
                    "matched_balance": output["geometry"]["matched_balance"],
                    "radius_common_support_before_matching": output["geometry"][
                        "radius_common_support_before_matching"
                    ],
                },
                "development": output["development"],
                "heldout": {
                    "planned_tests": tests,
                    "per_condition_matched_gain_difference": output["heldout"][
                        "per_condition_matched_gain_difference"
                    ],
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
