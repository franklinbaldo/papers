# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scipy>=1.14",
# ]
# ///
"""Nested-cohort ablation for the Pontifex synthetic CMB locality result.

The matched single-remote experiment and the later multi-remote experiment used
slightly different theta panels and geometry gates.  The multi-remote gate also
collapsed the LOCAL controller to the fixed w=0.5 baseline.  That leaves a
specific ambiguity: did the adaptive effect disappear because the stricter
outcome-free geometry gate changed the theta cohort, or because replacing one
remote ring by several remotes changed the controller itself?

This experiment isolates those explanations without touching outcomes:

1. Generate ONE balanced theta panel.
2. Define two nested, outcome-free masks on that same panel:
   SINGLE: the +0.5 remote context is disjoint from local lesion support.
   MULTI: +0.25/+0.5/+0.75 remotes are all disjoint from local support and from
   one another.
3. Generate ONE set of development skies and ONE set of held-out skies.
4. Fit the same 3-bin LOCAL and +0.5 REMOTE controllers separately on each
   cohort, using development skies only.
5. Freeze all rules before held-out generation/evaluation.
6. On the MULTI cohort also fit the median-remote ensemble used by the previous
   experiment.

The primary planned contrast is the paired base-sky change in the +0.5 remote
controller's advantage over fixed w=0.5 when moving from SINGLE to MULTI.  This
directly measures cohort-gate sensitivity while holding raw theta candidates,
skies, field realizations, candidate widths, and controller class fixed.

No assembly/student/validation/test data enter this experiment.  The only
stages here are synthetic development and synthetic held-out skies, with no
held-out outcomes used to choose gates, predictors, bins, or widths.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from cmb_beam_scale_holdout import balanced_theta_panel
from cmb_local_spectrum_holdout import bin_index
from cmb_locality_remote_ring_holdout import (
    choose_rule,
    geometry_audit as single_geometry_audit,
    holm_adjust,
    sign_test,
)
from cmb_nonlocal_observable_ablation import summary
from cmb_remote_ensemble_locality_holdout import (
    collect_rows,
    geometry_audit as multi_geometry_audit,
)


def sample_ids(thetas) -> set[int]:
    return {int(theta.sample) for theta in thetas}


def add_remote_aliases(rows: list[dict], remote_shifts: list[float]) -> None:
    for row in rows:
        values = row["log_remote_spectral_roughness"]
        if len(values) != len(remote_shifts):
            raise RuntimeError("remote descriptor count does not match remote shifts")
        for j, value in enumerate(values):
            row[f"log_remote_{j}_spectral_roughness"] = float(value)


def fit_rule(
    rows: list[dict],
    *,
    predictor: str,
    widths: list[float],
    baseline: float,
    bins: int,
) -> dict:
    edges, selected, diagnostics = choose_rule(
        rows,
        predictor_key=predictor,
        widths=widths,
        baseline=baseline,
        bins=bins,
    )
    return {
        "predictor": predictor,
        "edges": [float(x) for x in edges],
        "selected_widths": [float(x) for x in selected],
        "diagnostics": diagnostics,
    }


def apply_rule(row: dict, rule: dict) -> tuple[float, float, int]:
    b = bin_index(float(row[rule["predictor"]]), rule["edges"])
    w = float(rule["selected_widths"][b])
    value = float(row["observed_leakage_ratio"][str(w)])
    return value, w, int(b)


def theta_descriptor(theta) -> dict:
    return {
        "sample": int(theta.sample),
        "radius": float(theta.radius),
        "aspect": float(theta.aspect),
        "geometry": str(theta.geometry),
        "occlusion": str(theta.occlusion),
    }


def cohort_description(thetas) -> dict:
    if not thetas:
        return {
            "n": 0,
            "radius": summary([]),
            "aspect": summary([]),
            "geometry_counts": {},
            "occlusion_counts": {},
            "samples": [],
        }
    return {
        "n": len(thetas),
        "radius": summary([float(t.radius) for t in thetas]),
        "aspect": summary([float(t.aspect) for t in thetas]),
        "geometry_counts": dict(Counter(str(t.geometry) for t in thetas)),
        "occlusion_counts": dict(Counter(str(t.occlusion) for t in thetas)),
        "samples": [int(t.sample) for t in thetas],
    }


def per_sky_metrics(
    rows: list[dict],
    *,
    sky_ids: list[int],
    single_samples: set[int],
    multi_samples: set[int],
    single_local_rule: dict,
    single_remote_rule: dict,
    multi_local_rule: dict,
    multi_remote_rule: dict,
    multi_ensemble_rule: dict,
    baseline: float,
) -> list[dict]:
    out = []
    for sky_id in sky_ids:
        sky = [r for r in rows if int(r["base_sky_id"]) == sky_id]
        single = [r for r in sky if int(r["sample"]) in single_samples]
        multi = [r for r in sky if int(r["sample"]) in multi_samples]
        if not single or not multi:
            raise RuntimeError(f"sky {sky_id} lacks one of the nested cohorts")

        def med_rule(subset: list[dict], rule: dict) -> float:
            return float(np.median([apply_rule(r, rule)[0] for r in subset]))

        def med_fixed(subset: list[dict]) -> float:
            return float(
                np.median(
                    [float(r["observed_leakage_ratio"][str(baseline)]) for r in subset]
                )
            )

        single_local = med_rule(single, single_local_rule)
        single_remote = med_rule(single, single_remote_rule)
        single_fixed = med_fixed(single)
        multi_local = med_rule(multi, multi_local_rule)
        multi_remote = med_rule(multi, multi_remote_rule)
        multi_ensemble = med_rule(multi, multi_ensemble_rule)
        multi_fixed = med_fixed(multi)
        single_remote_gain = single_remote - single_fixed
        multi_remote_gain = multi_remote - multi_fixed

        out.append(
            {
                "base_sky_id": int(sky_id),
                "single_local": single_local,
                "single_remote_0p5": single_remote,
                "single_fixed": single_fixed,
                "single_remote_gain": single_remote_gain,
                "single_local_gain": single_local - single_fixed,
                "multi_local": multi_local,
                "multi_remote_0p5": multi_remote,
                "multi_remote_ensemble": multi_ensemble,
                "multi_fixed": multi_fixed,
                "multi_remote_gain": multi_remote_gain,
                "multi_local_gain": multi_local - multi_fixed,
                "multi_ensemble_gain": multi_ensemble - multi_fixed,
                "remote_gain_gate_shift": multi_remote_gain - single_remote_gain,
                "multi_remote_minus_ensemble": multi_remote - multi_ensemble,
            }
        )
    return out


def planned_tests(per_sky: list[dict]) -> dict:
    contrasts = {
        "remote_gain_gate_shift": [r["remote_gain_gate_shift"] for r in per_sky],
        "single_remote_vs_fixed": [r["single_remote_gain"] for r in per_sky],
        "multi_remote_vs_fixed": [r["multi_remote_gain"] for r in per_sky],
        "multi_ensemble_vs_fixed": [r["multi_ensemble_gain"] for r in per_sky],
    }
    tests = {name: sign_test(values) for name, values in contrasts.items()}
    adjusted = holm_adjust(
        {name: float(result["exact_two_sided_sign_p"]) for name, result in tests.items()}
    )
    for name, result in tests.items():
        result["holm_adjusted_p"] = float(adjusted[name])
    return tests


def condition_diagnostics(
    rows: list[dict],
    *,
    sky_ids: list[int],
    single_samples: set[int],
    multi_samples: set[int],
    single_remote_rule: dict,
    multi_remote_rule: dict,
    baseline: float,
) -> dict:
    conditions = sorted({str(r["field_condition"]) for r in rows})
    out: dict[str, dict] = {}
    for condition in conditions:
        single_gain = []
        multi_gain = []
        gate_shift = []
        for sky_id in sky_ids:
            sky = [
                r
                for r in rows
                if int(r["base_sky_id"]) == sky_id
                and str(r["field_condition"]) == condition
            ]
            single = [r for r in sky if int(r["sample"]) in single_samples]
            multi = [r for r in sky if int(r["sample"]) in multi_samples]
            if not single or not multi:
                continue
            sr = float(np.median([apply_rule(r, single_remote_rule)[0] for r in single]))
            sf = float(
                np.median(
                    [float(r["observed_leakage_ratio"][str(baseline)]) for r in single]
                )
            )
            mr = float(np.median([apply_rule(r, multi_remote_rule)[0] for r in multi]))
            mf = float(
                np.median(
                    [float(r["observed_leakage_ratio"][str(baseline)]) for r in multi]
                )
            )
            single_gain.append(sr - sf)
            multi_gain.append(mr - mf)
            gate_shift.append((mr - mf) - (sr - sf))
        out[condition] = {
            "single_remote_gain": summary(single_gain),
            "multi_remote_gain": summary(multi_gain),
            "remote_gain_gate_shift": summary(gate_shift),
        }
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dev-skies", type=int, default=12)
    ap.add_argument("--heldout-skies", type=int, default=24)
    ap.add_argument("--theta-per-cell", type=int, default=4)
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
    ap.add_argument("--ny", type=int, default=64)
    ap.add_argument("--nx", type=int, default=128)
    ap.add_argument("--seed", type=int, default=20260923)
    ap.add_argument(
        "--rows", type=Path, default=Path("pontifex-cmb-locality-cohort-shift.jsonl")
    )
    ap.add_argument(
        "--output", type=Path, default=Path("pontifex-cmb-locality-cohort-shift.json")
    )
    args = ap.parse_args()

    widths = sorted(set(float(w) for w in args.beam_width_ratios))
    metric_k0 = sorted(set(float(k) for k in args.metric_k0))
    remote_shifts = sorted(set(float(s) % 1.0 for s in args.remote_shifts))
    if args.baseline_width not in widths:
        raise ValueError("baseline width must be among candidate widths")
    if args.single_remote_shift not in remote_shifts:
        raise ValueError("single remote shift must be included in multi remote shifts")
    if len(remote_shifts) < 3:
        raise ValueError("need at least three remote shifts")
    if args.dev_skies < 2 or args.heldout_skies < 2 or args.theta_per_cell < 1:
        raise ValueError("need >=2 skies per stage and theta_per_cell >=1")

    raw_thetas = balanced_theta_panel(args.seed, args.theta_per_cell)
    single_thetas, single_audit = single_geometry_audit(
        raw_thetas,
        (args.ny, args.nx),
        args.single_remote_shift,
    )
    multi_thetas, multi_audit = multi_geometry_audit(
        raw_thetas,
        (args.ny, args.nx),
        remote_shifts,
    )
    single_samples = sample_ids(single_thetas)
    multi_samples = sample_ids(multi_thetas)
    if not multi_samples <= single_samples:
        raise RuntimeError("MULTI geometry mask must be a subset of SINGLE mask")
    if len(multi_thetas) < 12:
        raise RuntimeError("MULTI geometry mask left too few theta rows")

    remote_index = remote_shifts.index(float(args.single_remote_shift))
    remote_predictor = f"log_remote_{remote_index}_spectral_roughness"

    dev_seed_base = args.seed + 40_000_000_081
    dev_seeds = [dev_seed_base + 100_000_007 * i for i in range(args.dev_skies)]
    dev_rows = collect_rows(
        base_seeds=dev_seeds,
        thetas=single_thetas,
        metric_k0=metric_k0,
        widths=widths,
        ny=args.ny,
        nx=args.nx,
        stage="development",
        remote_shifts=remote_shifts,
    )
    add_remote_aliases(dev_rows, remote_shifts)
    single_dev = [r for r in dev_rows if int(r["sample"]) in single_samples]
    multi_dev = [r for r in dev_rows if int(r["sample"]) in multi_samples]

    single_local_rule = fit_rule(
        single_dev,
        predictor="log_local_spectral_roughness",
        widths=widths,
        baseline=args.baseline_width,
        bins=args.bins,
    )
    single_remote_rule = fit_rule(
        single_dev,
        predictor=remote_predictor,
        widths=widths,
        baseline=args.baseline_width,
        bins=args.bins,
    )
    multi_local_rule = fit_rule(
        multi_dev,
        predictor="log_local_spectral_roughness",
        widths=widths,
        baseline=args.baseline_width,
        bins=args.bins,
    )
    multi_remote_rule = fit_rule(
        multi_dev,
        predictor=remote_predictor,
        widths=widths,
        baseline=args.baseline_width,
        bins=args.bins,
    )
    multi_ensemble_rule = fit_rule(
        multi_dev,
        predictor="log_remote_ensemble_spectral_roughness",
        widths=widths,
        baseline=args.baseline_width,
        bins=args.bins,
    )

    # Held-out skies are generated only after every rule above is frozen.
    held_seed_base = args.seed + 80_000_000_163
    held_seeds = [held_seed_base + 100_000_007 * i for i in range(args.heldout_skies)]
    held_rows = collect_rows(
        base_seeds=held_seeds,
        thetas=single_thetas,
        metric_k0=metric_k0,
        widths=widths,
        ny=args.ny,
        nx=args.nx,
        stage="heldout",
        remote_shifts=remote_shifts,
    )
    add_remote_aliases(held_rows, remote_shifts)

    for row in dev_rows + held_rows:
        sample = int(row["sample"])
        row["single_geometry_cohort"] = bool(sample in single_samples)
        row["multi_geometry_cohort"] = bool(sample in multi_samples)

    per_sky = per_sky_metrics(
        held_rows,
        sky_ids=list(range(args.heldout_skies)),
        single_samples=single_samples,
        multi_samples=multi_samples,
        single_local_rule=single_local_rule,
        single_remote_rule=single_remote_rule,
        multi_local_rule=multi_local_rule,
        multi_remote_rule=multi_remote_rule,
        multi_ensemble_rule=multi_ensemble_rule,
        baseline=args.baseline_width,
    )
    tests = planned_tests(per_sky)

    single_only = [t for t in single_thetas if int(t.sample) not in multi_samples]
    output = {
        "experiment": "pontifex_cmb_locality_cohort_shift_ablation",
        "design": {
            "seed": args.seed,
            "raw_theta": len(raw_thetas),
            "single_accepted_theta": len(single_thetas),
            "multi_accepted_theta": len(multi_thetas),
            "single_only_theta": len(single_only),
            "single_remote_shift": float(args.single_remote_shift),
            "remote_shifts": remote_shifts,
            "dev_skies": args.dev_skies,
            "heldout_skies": args.heldout_skies,
            "metric_k0": metric_k0,
            "candidate_widths": widths,
            "baseline_width": float(args.baseline_width),
            "bins": args.bins,
            "inferential_unit": "independent base-sky seed",
            "primary_contrast": "(MULTI remote+0.5 - MULTI fixed) - (SINGLE remote+0.5 - SINGLE fixed)",
            "multiplicity": "two-sided exact sign tests across four predeclared contrasts with Holm adjustment",
        },
        "geometry": {
            "single_audit": single_audit,
            "multi_audit": multi_audit,
            "single_cohort": cohort_description(single_thetas),
            "multi_cohort": cohort_description(multi_thetas),
            "removed_by_multi_gate": cohort_description(single_only),
            "removed_theta": [theta_descriptor(t) for t in single_only],
        },
        "development": {
            "rows_single": len(single_dev),
            "rows_multi": len(multi_dev),
            "single_local_rule": single_local_rule,
            "single_remote_0p5_rule": single_remote_rule,
            "multi_local_rule": multi_local_rule,
            "multi_remote_0p5_rule": multi_remote_rule,
            "multi_remote_ensemble_rule": multi_ensemble_rule,
        },
        "heldout": {
            "rows_single": len(held_rows),
            "rows_multi": sum(int(r["sample"]) in multi_samples for r in held_rows),
            "planned_tests": tests,
            "descriptive_local_gain_single": summary(
                [float(r["single_local_gain"]) for r in per_sky]
            ),
            "descriptive_local_gain_multi": summary(
                [float(r["multi_local_gain"]) for r in per_sky]
            ),
            "descriptive_multi_remote_minus_ensemble": summary(
                [float(r["multi_remote_minus_ensemble"]) for r in per_sky]
            ),
            "per_condition": condition_diagnostics(
                held_rows,
                sky_ids=list(range(args.heldout_skies)),
                single_samples=single_samples,
                multi_samples=multi_samples,
                single_remote_rule=single_remote_rule,
                multi_remote_rule=multi_remote_rule,
                baseline=args.baseline_width,
            ),
            "per_sky": per_sky,
        },
        "interpretation_contract": {
            "evidence_if_gate_shift_is_negative": "the stricter outcome-free multi-remote geometry cohort reduces the held-out value of the otherwise identical +0.5 remote controller under matched skies and raw theta candidates",
            "evidence_if_gate_shift_is_null": "cohort restriction alone does not explain the earlier single-vs-multi discrepancy",
            "not_established": [
                "that any retained controller is a physical CMB scale law",
                "that remote roughness is lesion-local information",
                "that Planck/ACT data exhibit this synthetic effect",
                "physical non-locality or Pontifex/Torus causality",
            ],
            "partition_statement": "D_assembly, D_student, D_val, and D_test are absent from this synthetic experiment; development and held-out sky seeds are disjoint, and held-out outcomes do not choose gates or controller rules.",
        },
    }

    args.rows.parent.mkdir(parents=True, exist_ok=True)
    with args.rows.open("w", encoding="utf-8") as fh:
        for row in dev_rows + held_rows:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({"design": output["design"], "development": output["development"], "heldout": {"planned_tests": tests, "descriptive_local_gain_single": output["heldout"]["descriptive_local_gain_single"], "descriptive_local_gain_multi": output["heldout"]["descriptive_local_gain_multi"], "per_condition": output["heldout"]["per_condition"]}}, indent=2))


if __name__ == "__main__":
    main()
