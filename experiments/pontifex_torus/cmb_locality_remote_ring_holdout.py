# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scipy>=1.14",
# ]
# ///
"""Matched remote-ring locality control for the Pontifex CMB scale controller.

The preceding held-out experiment found that an outcome-free descriptor measured
in the immediate, unaltered ring around a lesion predicts which observation
width is useful.  That result does not yet establish locality because the ring is
theta-dependent and can carry geometry/global-field information.

This experiment gives locality a direct falsification test.  For every theta we
construct a matched remote theta by translating its center by half a period in
the periodic x coordinate while preserving radius, geometry, aspect, phase and
y coordinate.  The remote descriptor uses the same roughness formula and the
same field realization, but on that translated ring.  Theta rows whose complete
remote context ring overlaps the local lesion support are excluded by geometry
alone before any sky outcome is generated.

Two controllers have identical degrees of freedom:

* LOCAL: 3 quantile bins of lesion-adjacent pre-intervention roughness;
* REMOTE: 3 quantile bins of matched-remote pre-intervention roughness.

Each controller learns bin edges and one width per bin on development skies
only.  Both rules are frozen before held-out skies are generated.  The primary
held-out contrast is LOCAL minus REMOTE at the independent base-sky level.
Fixed width 0.5 remains the pre-existing baseline.  Three planned sign tests
(local-vs-remote, local-vs-fixed, remote-vs-fixed) are Holm-adjusted.

No assembly/student/validation/test data enter this experiment.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

from cmb_beam_scale_holdout import balanced_theta_panel
from cmb_local_spectrum_holdout import bin_index, local_spectral_roughness
from cmb_metric_beam_ladder import responses
from cmb_metric_spectrum_control import filtered_fields
from cmb_nonlocal_observable_ablation import summary
from cmb_occlusion_mc import GEOMETRIES, OCCLUSIONS, synthetic_masks


def remote_theta(theta, shift: float = 0.5):
    """Translate theta on the periodic x coordinate without changing its shape."""
    return replace(theta, center_a=float((theta.center_a + shift) % 1.0))


def context_mask(shape: tuple[int, int], theta) -> np.ndarray:
    core, boundary, _rr, _angle = synthetic_masks(shape, theta)
    return boundary & ~core


def geometry_audit(
    thetas,
    shape: tuple[int, int],
    remote_shift: float,
) -> tuple[list, list[dict]]:
    """Keep only theta rows whose full remote context is outside local support."""
    accepted = []
    audit = []
    for theta in thetas:
        local_core, local_boundary, _rr, _angle = synthetic_masks(shape, theta)
        rt = remote_theta(theta, remote_shift)
        remote_core, remote_boundary, _rr2, _angle2 = synthetic_masks(shape, rt)
        local_support = local_core | local_boundary
        remote_context = remote_boundary & ~remote_core
        overlap = int(np.count_nonzero(local_support & remote_context))
        local_context_n = int(np.count_nonzero(local_boundary & ~local_core))
        remote_context_n = int(np.count_nonzero(remote_context))
        keep = overlap == 0 and local_context_n >= 4 and remote_context_n >= 4
        audit.append(
            {
                "theta_sample": int(theta.sample),
                "radius": float(theta.radius),
                "geometry": str(theta.geometry),
                "occlusion": str(theta.occlusion),
                "remote_shift": float(remote_shift),
                "local_context_pixels": local_context_n,
                "remote_context_pixels": remote_context_n,
                "remote_context_overlap_with_local_support": overlap,
                "accepted": bool(keep),
            }
        )
        if keep:
            accepted.append(theta)
    return accepted, audit


def collect_rows(
    *,
    base_seeds: list[int],
    thetas,
    metric_k0: list[float],
    widths: list[float],
    ny: int,
    nx: int,
    stage: str,
    remote_shift: float,
) -> list[dict]:
    rows: list[dict] = []
    for base_sky_id, sky_seed in enumerate(base_seeds):
        fields = filtered_fields(ny, nx, sky_seed, metric_k0)
        for condition in [f"metric_k0_{k:g}" for k in metric_k0]:
            field = fields[condition]
            for theta in thetas:
                local_r, local_n = local_spectral_roughness(field, theta)
                remote_r, remote_n = local_spectral_roughness(
                    field, remote_theta(theta, remote_shift)
                )
                if (
                    not np.isfinite(local_r)
                    or local_r <= 0
                    or not np.isfinite(remote_r)
                    or remote_r <= 0
                ):
                    continue
                rng = np.random.default_rng(sky_seed + 97_409 * (theta.sample + 1))
                core, beam, ratio = responses(field, theta, rng, widths)
                rows.append(
                    {
                        "stage": stage,
                        "base_sky_id": base_sky_id,
                        "base_sky_seed": sky_seed,
                        "field_condition": condition,
                        "local_spectral_roughness": float(local_r),
                        "log_local_spectral_roughness": float(np.log(local_r)),
                        "remote_spectral_roughness": float(remote_r),
                        "log_remote_spectral_roughness": float(np.log(remote_r)),
                        "local_context_pixels": int(local_n),
                        "remote_context_pixels": int(remote_n),
                        **asdict(theta),
                        "observed_core_rmse": float(core),
                        "observed_beam_boundary_rmse": {
                            str(w): float(beam[w]) for w in widths
                        },
                        "observed_leakage_ratio": {
                            str(w): float(ratio[w]) for w in widths
                        },
                    }
                )
    return rows


def choose_rule(
    rows: list[dict],
    *,
    predictor_key: str,
    widths: list[float],
    baseline: float,
    bins: int,
) -> tuple[list[float], list[float], dict]:
    x = np.asarray([float(r[predictor_key]) for r in rows], dtype=float)
    edges = [float(v) for v in np.quantile(x, [i / bins for i in range(1, bins)])]
    if len(set(round(v, 12) for v in edges)) != len(edges):
        raise RuntimeError(f"development edges collapsed for {predictor_key}")

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
                and bin_index(float(r[predictor_key]), edges) == b
            ]
            if not subset:
                continue
            for w in widths:
                per_sky_by_width[w].append(
                    float(
                        np.median(
                            [float(r["observed_leakage_ratio"][str(w)]) for r in subset]
                        )
                    )
                )

        score_by_width = {
            w: float(np.median(per_sky_by_width[w])) for w in widths if per_sky_by_width[w]
        }
        if len(score_by_width) != len(widths):
            raise RuntimeError(f"development bin {b} lacks sky summaries")
        winner = min(widths, key=lambda w: (-score_by_width[w], abs(w - baseline), w))
        selected.append(float(winner))
        diagnostics[str(b)] = {
            "selected_width": float(winner),
            "score_by_width": {str(w): float(score_by_width[w]) for w in widths},
            "per_sky_median_leakage_by_width": {
                str(w): [float(v) for v in per_sky_by_width[w]] for w in widths
            },
        }
    return edges, selected, diagnostics


def sign_test(values: list[float]) -> dict:
    x = np.asarray(values, dtype=float)
    nz = x[np.abs(x) > 1e-15]
    pos = int(np.count_nonzero(nz > 0))
    p = (
        float(binomtest(pos, n=len(nz), p=0.5, alternative="two-sided").pvalue)
        if len(nz)
        else 1.0
    )
    return {
        "summary": summary(x.tolist()),
        "positive_count": pos,
        "negative_count": int(np.count_nonzero(nz < 0)),
        "ties": int(len(x) - len(nz)),
        "nonzero": int(len(nz)),
        "exact_two_sided_sign_p": p,
    }


def holm_adjust(raw: dict[str, float]) -> dict[str, float]:
    ordered = sorted(raw.items(), key=lambda kv: kv[1])
    m = len(ordered)
    adjusted: dict[str, float] = {}
    running = 0.0
    for rank, (name, p) in enumerate(ordered):
        candidate = min(1.0, (m - rank) * float(p))
        running = max(running, candidate)
        adjusted[name] = running
    return adjusted


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dev-skies", type=int, default=12)
    ap.add_argument("--heldout-skies", type=int, default=24)
    ap.add_argument("--theta-per-cell", type=int, default=3)
    ap.add_argument("--bins", type=int, default=3)
    ap.add_argument(
        "--beam-width-ratios", nargs="+", type=float, default=[0.125, 0.25, 0.5, 1.0]
    )
    ap.add_argument("--baseline-width", type=float, default=0.5)
    ap.add_argument("--metric-k0", nargs="+", type=float, default=[4.0, 8.0, 16.0])
    ap.add_argument("--remote-shift", type=float, default=0.5)
    ap.add_argument("--ny", type=int, default=64)
    ap.add_argument("--nx", type=int, default=128)
    ap.add_argument("--seed", type=int, default=20260921)
    ap.add_argument(
        "--rows", type=Path, default=Path("pontifex-cmb-locality-remote-ring.jsonl")
    )
    ap.add_argument(
        "--output", type=Path, default=Path("pontifex-cmb-locality-remote-ring.json")
    )
    args = ap.parse_args()

    widths = sorted(set(float(w) for w in args.beam_width_ratios))
    metric_k0 = sorted(set(float(k) for k in args.metric_k0))
    if args.baseline_width not in widths:
        raise ValueError("baseline width must be among candidate widths")
    if args.dev_skies < 2 or args.heldout_skies < 2 or args.theta_per_cell < 1:
        raise ValueError("need >=2 skies per stage and theta_per_cell >=1")
    if args.bins < 2 or min(widths) <= 0 or min(metric_k0) <= 0:
        raise ValueError("invalid bins, widths, or metric cutoffs")
    if not (0.0 < args.remote_shift <= 0.5):
        raise ValueError("remote shift must be in (0, 0.5]")

    raw_thetas = balanced_theta_panel(args.seed, args.theta_per_cell)
    thetas, theta_geometry_audit = geometry_audit(
        raw_thetas, (args.ny, args.nx), args.remote_shift
    )
    if len(thetas) < len(raw_thetas) // 2:
        raise RuntimeError("remote-ring geometry exclusion removed too much of theta panel")

    # Development is generated first. Both controller rules are frozen before
    # any held-out field is generated.
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
        remote_shift=args.remote_shift,
    )

    local_edges, local_widths, local_dev = choose_rule(
        dev_rows,
        predictor_key="log_local_spectral_roughness",
        widths=widths,
        baseline=args.baseline_width,
        bins=args.bins,
    )
    remote_edges, remote_widths, remote_dev = choose_rule(
        dev_rows,
        predictor_key="log_remote_spectral_roughness",
        widths=widths,
        baseline=args.baseline_width,
        bins=args.bins,
    )

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
        remote_shift=args.remote_shift,
    )

    local_counts = {str(w): 0 for w in widths}
    remote_counts = {str(w): 0 for w in widths}
    for r in held_rows:
        lb = bin_index(float(r["log_local_spectral_roughness"]), local_edges)
        rb = bin_index(float(r["log_remote_spectral_roughness"]), remote_edges)
        lw = local_widths[lb]
        rw = remote_widths[rb]
        r["frozen_local_bin"] = int(lb)
        r["frozen_remote_bin"] = int(rb)
        r["frozen_local_width"] = float(lw)
        r["frozen_remote_width"] = float(rw)
        r["local_adaptive_leakage"] = float(r["observed_leakage_ratio"][str(lw)])
        r["remote_adaptive_leakage"] = float(r["observed_leakage_ratio"][str(rw)])
        r["baseline_leakage"] = float(
            r["observed_leakage_ratio"][str(args.baseline_width)]
        )
        local_counts[str(lw)] += 1
        remote_counts[str(rw)] += 1

    local_minus_remote: list[float] = []
    local_minus_fixed: list[float] = []
    remote_minus_fixed: list[float] = []
    per_condition: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: {"local_minus_remote": [], "local_minus_fixed": [], "remote_minus_fixed": []}
    )

    for sky_id in range(args.heldout_skies):
        subset = [r for r in held_rows if int(r["base_sky_id"]) == sky_id]
        if not subset:
            raise RuntimeError(f"held-out sky {sky_id} has no valid rows")
        local = float(np.median([r["local_adaptive_leakage"] for r in subset]))
        remote = float(np.median([r["remote_adaptive_leakage"] for r in subset]))
        fixed = float(np.median([r["baseline_leakage"] for r in subset]))
        local_minus_remote.append(local - remote)
        local_minus_fixed.append(local - fixed)
        remote_minus_fixed.append(remote - fixed)

        for condition in [f"metric_k0_{k:g}" for k in metric_k0]:
            c = [r for r in subset if r["field_condition"] == condition]
            if not c:
                continue
            cl = float(np.median([r["local_adaptive_leakage"] for r in c]))
            cr = float(np.median([r["remote_adaptive_leakage"] for r in c]))
            cf = float(np.median([r["baseline_leakage"] for r in c]))
            per_condition[condition]["local_minus_remote"].append(cl - cr)
            per_condition[condition]["local_minus_fixed"].append(cl - cf)
            per_condition[condition]["remote_minus_fixed"].append(cr - cf)

    tests = {
        "local_minus_remote": sign_test(local_minus_remote),
        "local_minus_fixed": sign_test(local_minus_fixed),
        "remote_minus_fixed": sign_test(remote_minus_fixed),
    }
    raw_p = {k: float(v["exact_two_sided_sign_p"]) for k, v in tests.items()}
    holm = holm_adjust(raw_p)
    for name in tests:
        tests[name]["holm_adjusted_p_across_three_planned_contrasts"] = float(holm[name])

    local_desc = np.asarray([r["local_spectral_roughness"] for r in held_rows], dtype=float)
    remote_desc = np.asarray([r["remote_spectral_roughness"] for r in held_rows], dtype=float)
    descriptor_corr = (
        float(np.corrcoef(local_desc, remote_desc)[0, 1])
        if len(local_desc) > 2 and np.std(local_desc) > 1e-15 and np.std(remote_desc) > 1e-15
        else float("nan")
    )

    result = {
        "experiment": "Pontifex CMB matched remote-ring locality control",
        "design": {
            "theta_panel_fixed_before_skies": True,
            "new_seed_vs_prior_local_controller": True,
            "raw_theta_count": len(raw_thetas),
            "accepted_theta_count_after_geometry_only_remote_separation": len(thetas),
            "balanced_geometries": list(GEOMETRIES),
            "balanced_occlusions": list(OCCLUSIONS),
            "remote_translation_fraction_of_periodic_x": float(args.remote_shift),
            "remote_preserves_radius_geometry_aspect_phase_and_y": True,
            "remote_context_overlap_with_local_support_required_zero": True,
            "metric_spectral_cutoffs_cycles_per_unit": metric_k0,
            "candidate_widths": widths,
            "fixed_baseline_width": float(args.baseline_width),
            "development_base_skies": int(args.dev_skies),
            "heldout_base_skies": int(args.heldout_skies),
            "modulation_bins_per_controller": int(args.bins),
            "heldout_generated_after_both_rules_frozen": True,
            "primary_replication_unit": "independent base sky seed; spectral conditions are nested repeated measurements",
        },
        "theta_geometry_audit": theta_geometry_audit,
        "development": {
            "rows": len(dev_rows),
            "local_rule": {
                "predictor": "log(local_spectral_roughness)",
                "interior_bin_edges": local_edges,
                "selected_width_by_bin": local_widths,
                "diagnostics": local_dev,
            },
            "remote_rule": {
                "predictor": "log(remote_spectral_roughness)",
                "interior_bin_edges": remote_edges,
                "selected_width_by_bin": remote_widths,
                "diagnostics": remote_dev,
            },
        },
        "heldout": {
            "rows": len(held_rows),
            "local_width_counts": local_counts,
            "remote_width_counts": remote_counts,
            "local_remote_descriptor_pearson_correlation_descriptive": descriptor_corr,
            "planned_contrasts": tests,
            "per_condition_descriptive": {
                condition: {name: summary(values) for name, values in contrasts.items()}
                for condition, contrasts in sorted(per_condition.items())
            },
        },
        "interpretation_contract": {
            "evidence": (
                "local and matched-remote descriptors have identical formulas and controller flexibility; both are fit only on development skies and frozen before held-out generation"
            ),
            "positive_locality_rule": (
                "a consistently positive held-out local-minus-remote sky-level contrast, surviving the predeclared three-contrast Holm correction, supports lesion-local predictive information within this synthetic harness"
            ),
            "negative_locality_rule": (
                "if the remote controller matches the local controller, the prior gain cannot be attributed specifically to lesion-local spectral structure"
            ),
            "geometry_boundary": (
                "theta rows with any remote-context overlap with the local lesion support are excluded using geometry only, before any sky outcome"
            ),
            "hypothesis": (
                "even a successful locality control would leave open which local field statistic is mechanistic; local roughness remains one candidate descriptor rather than a causal identification"
            ),
            "not_evidence": (
                "this does not establish a physical CMB scale, Planck/ACT beam law, real-sky anomaly, physical nonlocality, topology, or Torus causality"
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
