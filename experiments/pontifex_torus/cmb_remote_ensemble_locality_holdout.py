# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scipy>=1.14",
# ]
# ///
"""Multi-remote locality discriminant for the Pontifex synthetic CMB harness.

The preceding matched remote-ring experiment showed that one ring translated by
half a period can predict useful observation width about as well as the
lesion-adjacent ring.  A single remote location is still arbitrary, so this
experiment replaces it with three predeclared remote rings.

The geometry filter is outcome-free: a theta is retained only when all remote
context rings are disjoint from the local lesion support and from one another.
All controllers have the same 3-bin form and are learned on development skies
only, then frozen before held-out skies are generated.

Primary test: does the LOCAL controller beat the median performance of the three
independently fitted single-REMOTE controllers on held-out base skies?

Secondary mechanistic control: a deployable REMOTE-ENSEMBLE controller uses the
median roughness across the three remote rings as its sole predictor.  If this
controller retains the scale-adaptation gain, the useful information is better
explained by spatially broad field state than by lesion-specific locality.

No assembly/student/validation/test data enter this experiment.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np

from cmb_beam_scale_holdout import balanced_theta_panel
from cmb_local_spectrum_holdout import bin_index, local_spectral_roughness
from cmb_locality_remote_ring_holdout import choose_rule, holm_adjust, sign_test
from cmb_metric_beam_ladder import responses
from cmb_metric_spectrum_control import filtered_fields
from cmb_nonlocal_observable_ablation import summary
from cmb_occlusion_mc import synthetic_masks


def shifted_theta(theta, shift: float):
    return replace(theta, center_a=float((theta.center_a + shift) % 1.0))


def context_and_support(shape: tuple[int, int], theta) -> tuple[np.ndarray, np.ndarray]:
    core, boundary, _rr, _angle = synthetic_masks(shape, theta)
    return boundary & ~core, core | boundary


def geometry_audit(
    thetas,
    shape: tuple[int, int],
    remote_shifts: list[float],
) -> tuple[list, list[dict]]:
    accepted = []
    audit = []
    for theta in thetas:
        local_context, local_support = context_and_support(shape, theta)
        remote_contexts = []
        remote_sizes = []
        overlaps_local = []
        for shift in remote_shifts:
            rc, _rs = context_and_support(shape, shifted_theta(theta, shift))
            remote_contexts.append(rc)
            remote_sizes.append(int(np.count_nonzero(rc)))
            overlaps_local.append(int(np.count_nonzero(rc & local_support)))

        pairwise_overlaps: dict[str, int] = {}
        max_pair_overlap = 0
        for i in range(len(remote_contexts)):
            for j in range(i + 1, len(remote_contexts)):
                n = int(np.count_nonzero(remote_contexts[i] & remote_contexts[j]))
                pairwise_overlaps[f"{i}-{j}"] = n
                max_pair_overlap = max(max_pair_overlap, n)

        keep = (
            int(np.count_nonzero(local_context)) >= 4
            and all(n >= 4 for n in remote_sizes)
            and max(overlaps_local, default=0) == 0
            and max_pair_overlap == 0
        )
        audit.append(
            {
                "theta_sample": int(theta.sample),
                "radius": float(theta.radius),
                "geometry": str(theta.geometry),
                "occlusion": str(theta.occlusion),
                "remote_shifts": [float(x) for x in remote_shifts],
                "local_context_pixels": int(np.count_nonzero(local_context)),
                "remote_context_pixels": remote_sizes,
                "remote_context_overlap_with_local_support": overlaps_local,
                "remote_pairwise_overlap_pixels": pairwise_overlaps,
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
    remote_shifts: list[float],
) -> list[dict]:
    rows: list[dict] = []
    for base_sky_id, sky_seed in enumerate(base_seeds):
        fields = filtered_fields(ny, nx, sky_seed, metric_k0)
        for condition in [f"metric_k0_{k:g}" for k in metric_k0]:
            field = fields[condition]
            for theta in thetas:
                local_r, local_n = local_spectral_roughness(field, theta)
                remote_r = []
                remote_n = []
                for shift in remote_shifts:
                    r, n = local_spectral_roughness(field, shifted_theta(theta, shift))
                    remote_r.append(float(r))
                    remote_n.append(int(n))
                if (
                    not np.isfinite(local_r)
                    or local_r <= 0
                    or any((not np.isfinite(r) or r <= 0) for r in remote_r)
                ):
                    continue

                rng = np.random.default_rng(sky_seed + 97_409 * (theta.sample + 1))
                core, beam, ratio = responses(field, theta, rng, widths)
                log_remote = [float(np.log(r)) for r in remote_r]
                rows.append(
                    {
                        "stage": stage,
                        "base_sky_id": base_sky_id,
                        "base_sky_seed": sky_seed,
                        "field_condition": condition,
                        "local_spectral_roughness": float(local_r),
                        "log_local_spectral_roughness": float(np.log(local_r)),
                        "remote_spectral_roughness": remote_r,
                        "log_remote_spectral_roughness": log_remote,
                        "remote_ensemble_spectral_roughness": float(np.median(remote_r)),
                        "log_remote_ensemble_spectral_roughness": float(np.median(log_remote)),
                        "local_context_pixels": int(local_n),
                        "remote_context_pixels": remote_n,
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


def fit_and_apply(
    dev_rows: list[dict],
    held_rows: list[dict],
    *,
    predictor_key: str,
    output_prefix: str,
    widths: list[float],
    baseline: float,
    bins: int,
) -> dict:
    edges, selected, diagnostics = choose_rule(
        dev_rows,
        predictor_key=predictor_key,
        widths=widths,
        baseline=baseline,
        bins=bins,
    )
    for r in held_rows:
        b = bin_index(float(r[predictor_key]), edges)
        w = float(selected[b])
        r[f"{output_prefix}_bin"] = int(b)
        r[f"{output_prefix}_width"] = w
        r[f"{output_prefix}_leakage"] = float(r["observed_leakage_ratio"][str(w)])
    return {
        "predictor": predictor_key,
        "edges": [float(x) for x in edges],
        "selected_widths": [float(x) for x in selected],
        "diagnostics": diagnostics,
    }


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
    ap.add_argument("--ny", type=int, default=64)
    ap.add_argument("--nx", type=int, default=128)
    ap.add_argument("--seed", type=int, default=20260923)
    ap.add_argument(
        "--rows", type=Path, default=Path("pontifex-cmb-remote-ensemble-locality.jsonl")
    )
    ap.add_argument(
        "--output", type=Path, default=Path("pontifex-cmb-remote-ensemble-locality.json")
    )
    args = ap.parse_args()

    widths = sorted(set(float(w) for w in args.beam_width_ratios))
    metric_k0 = sorted(set(float(k) for k in args.metric_k0))
    remote_shifts = sorted(set(float(s) % 1.0 for s in args.remote_shifts))
    if args.baseline_width not in widths:
        raise ValueError("baseline width must be among candidate widths")
    if len(remote_shifts) < 3:
        raise ValueError("need at least three distinct remote shifts")
    if any(s <= 0.0 or s >= 1.0 for s in remote_shifts):
        raise ValueError("remote shifts must be strictly within (0,1)")

    raw_thetas = balanced_theta_panel(args.seed, args.theta_per_cell)
    thetas, theta_geometry_audit = geometry_audit(
        raw_thetas, (args.ny, args.nx), remote_shifts
    )
    if len(thetas) < 12:
        raise RuntimeError(
            f"multi-remote geometry left only {len(thetas)} theta rows; need >=12"
        )

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
        remote_shifts=remote_shifts,
    )

    # Expand scalar predictor aliases for the independently fitted remote controls.
    for r in dev_rows:
        for j, value in enumerate(r["log_remote_spectral_roughness"]):
            r[f"log_remote_{j}_spectral_roughness"] = float(value)

    local_rule = fit_and_apply(
        dev_rows,
        [],
        predictor_key="log_local_spectral_roughness",
        output_prefix="local",
        widths=widths,
        baseline=args.baseline_width,
        bins=args.bins,
    )
    remote_rules = []
    for j in range(len(remote_shifts)):
        edges, selected, diagnostics = choose_rule(
            dev_rows,
            predictor_key=f"log_remote_{j}_spectral_roughness",
            widths=widths,
            baseline=args.baseline_width,
            bins=args.bins,
        )
        remote_rules.append(
            {
                "remote_index": j,
                "shift": remote_shifts[j],
                "predictor": f"log_remote_{j}_spectral_roughness",
                "edges": [float(x) for x in edges],
                "selected_widths": [float(x) for x in selected],
                "diagnostics": diagnostics,
            }
        )
    ensemble_edges, ensemble_widths, ensemble_diag = choose_rule(
        dev_rows,
        predictor_key="log_remote_ensemble_spectral_roughness",
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
        remote_shifts=remote_shifts,
    )
    for r in held_rows:
        for j, value in enumerate(r["log_remote_spectral_roughness"]):
            r[f"log_remote_{j}_spectral_roughness"] = float(value)

        lb = bin_index(float(r["log_local_spectral_roughness"]), local_rule["edges"])
        lw = float(local_rule["selected_widths"][lb])
        r["local_bin"] = int(lb)
        r["local_width"] = lw
        r["local_leakage"] = float(r["observed_leakage_ratio"][str(lw)])

        remote_leakages = []
        remote_widths_row = []
        for j, rule in enumerate(remote_rules):
            rb = bin_index(float(r[rule["predictor"]]), rule["edges"])
            rw = float(rule["selected_widths"][rb])
            remote_widths_row.append(rw)
            remote_leakages.append(float(r["observed_leakage_ratio"][str(rw)]))
        r["remote_controller_widths"] = remote_widths_row
        r["remote_controller_leakages"] = remote_leakages

        eb = bin_index(
            float(r["log_remote_ensemble_spectral_roughness"]), ensemble_edges
        )
        ew = float(ensemble_widths[eb])
        r["remote_ensemble_bin"] = int(eb)
        r["remote_ensemble_width"] = ew
        r["remote_ensemble_leakage"] = float(
            r["observed_leakage_ratio"][str(ew)]
        )
        r["baseline_leakage"] = float(
            r["observed_leakage_ratio"][str(args.baseline_width)]
        )

        remote_values = np.asarray(r["log_remote_spectral_roughness"], dtype=float)
        local_value = float(r["log_local_spectral_roughness"])
        r["local_minus_remote_median_log_roughness"] = float(
            local_value - np.median(remote_values)
        )
        r["local_rank_among_local_plus_remotes"] = int(
            1 + np.count_nonzero(remote_values > local_value)
        )

    local_minus_remote_median: list[float] = []
    local_minus_ensemble: list[float] = []
    ensemble_minus_fixed: list[float] = []
    local_ranks: list[int] = []
    per_sky: list[dict] = []

    for sky_id in range(args.heldout_skies):
        subset = [r for r in held_rows if int(r["base_sky_id"]) == sky_id]
        if not subset:
            raise RuntimeError(f"held-out sky {sky_id} has no valid rows")
        local = float(np.median([r["local_leakage"] for r in subset]))
        remote_scores = []
        for j in range(len(remote_shifts)):
            remote_scores.append(
                float(np.median([r["remote_controller_leakages"][j] for r in subset]))
            )
        remote_median = float(np.median(remote_scores))
        ensemble = float(np.median([r["remote_ensemble_leakage"] for r in subset]))
        fixed = float(np.median([r["baseline_leakage"] for r in subset]))
        local_minus_remote_median.append(local - remote_median)
        local_minus_ensemble.append(local - ensemble)
        ensemble_minus_fixed.append(ensemble - fixed)
        rank = int(1 + np.count_nonzero(np.asarray(remote_scores) > local))
        local_ranks.append(rank)
        per_sky.append(
            {
                "base_sky_id": sky_id,
                "local": local,
                "remote_controller_scores": remote_scores,
                "remote_controller_median": remote_median,
                "remote_ensemble": ensemble,
                "fixed": fixed,
                "local_rank_among_controllers": rank,
            }
        )

    tests = {
        "local_minus_median_single_remote": sign_test(local_minus_remote_median),
        "local_minus_remote_ensemble": sign_test(local_minus_ensemble),
        "remote_ensemble_minus_fixed": sign_test(ensemble_minus_fixed),
    }
    raw_p = {k: float(v["exact_two_sided_sign_p"]) for k, v in tests.items()}
    adjusted = holm_adjust(raw_p)
    for name in tests:
        tests[name]["holm_adjusted_p"] = float(adjusted[name])

    local_log = np.asarray(
        [float(r["log_local_spectral_roughness"]) for r in held_rows], dtype=float
    )
    ensemble_log = np.asarray(
        [float(r["log_remote_ensemble_spectral_roughness"]) for r in held_rows],
        dtype=float,
    )
    descriptor_corr = float(np.corrcoef(local_log, ensemble_log)[0, 1])

    result = {
        "experiment": "Pontifex CMB multi-remote locality control",
        "design": {
            "seed": args.seed,
            "raw_theta": len(raw_thetas),
            "accepted_theta": len(thetas),
            "remote_shifts": remote_shifts,
            "remote_geometry_rule": (
                "all remote context rings must be disjoint from local support and "
                "pairwise disjoint from each other before sky outcomes are generated"
            ),
            "dev_skies": args.dev_skies,
            "heldout_skies": args.heldout_skies,
            "metric_k0": metric_k0,
            "candidate_widths": widths,
            "baseline_width": args.baseline_width,
            "bins": args.bins,
            "inferential_unit": "independent base-sky seed",
        },
        "geometry_audit": theta_geometry_audit,
        "development": {
            "rows": len(dev_rows),
            "local_rule": local_rule,
            "single_remote_rules": remote_rules,
            "remote_ensemble_rule": {
                "predictor": "median log roughness across predeclared remote rings",
                "edges": [float(x) for x in ensemble_edges],
                "selected_widths": [float(x) for x in ensemble_widths],
                "diagnostics": ensemble_diag,
            },
        },
        "heldout": {
            "rows": len(held_rows),
            "tests": tests,
            "per_sky": per_sky,
            "local_rank_counts_among_four_controllers": {
                str(rank): int(local_ranks.count(rank)) for rank in range(1, 5)
            },
            "local_vs_remote_ensemble_log_roughness_pearson_r": descriptor_corr,
            "local_minus_remote_median_log_roughness": summary(
                [r["local_minus_remote_median_log_roughness"] for r in held_rows]
            ),
            "row_level_local_rank_among_local_plus_remotes": {
                str(rank): int(
                    sum(r["local_rank_among_local_plus_remotes"] == rank for r in held_rows)
                )
                for rank in range(1, 5)
            },
        },
        "interpretation_contract": {
            "evidence": (
                "all locality and remote-ensemble rules are learned only on development "
                "skies and frozen before held-out generation; geometry exclusions use no outcomes"
            ),
            "positive_locality_rule": (
                "LOCAL must beat the median independently fitted remote controller on held-out "
                "base skies after Holm correction"
            ),
            "broad_state_rule": (
                "if the remote-ensemble controller beats fixed w=0.5 while LOCAL is not "
                "exceptional relative to remote controls, the scale signal is better described "
                "as spatially broad than lesion-local"
            ),
            "not_evidence": (
                "this synthetic control does not establish a physical CMB scale, Planck/ACT "
                "beam law, real-sky anomaly, physical nonlocality, or Torus causality"
            ),
            "downstream_boundary": "D_assembly, D_student, D_val, and D_test remain disjoint and unused",
        },
    }

    args.rows.parent.mkdir(parents=True, exist_ok=True)
    with args.rows.open("w", encoding="utf-8") as f:
        for row in [*dev_rows, *held_rows]:
            f.write(json.dumps(row) + "\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
