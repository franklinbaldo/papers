# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "scipy>=1.14"]
# ///
"""Held-out placebo test for radius-to-beam-width coupling.

The previous experiment found that a development-fitted RADIUS policy beat fixed
w=0.5 on 24/24 held-out skies, while adding roughness changed no decision.  This
test asks whether that gain depends on assigning widths *by radius* or merely on
using the same marginal mixture of widths.

A fresh theta panel and radius bands are frozen first.  RADIUS is fit on
DEVELOPMENT only.  Then, before any HELD-OUT sky is generated, 255 placebo
assignments shuffle the frozen width labels within every geometry x occlusion
cell.  Thus each placebo preserves the exact per-cell width frequencies but
breaks radius-width coupling.  The primary randomization statistic is the mean
across independent held-out base-sky median leakages.  Spectral/theta rows are
nested repeated measurements.  No assembly/student/validation/test data enter.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from cmb_beam_scale_holdout import balanced_theta_panel
from cmb_local_spectrum_holdout import collect_rows
from cmb_locality_remote_ring_holdout import holm_adjust, sign_test
from cmb_nonlocal_observable_ablation import summary
from cmb_radius_conditioned_roughness_holdout import (
    _strict_quantile_edges,
    annotate_predictor,
    choose_width,
)


def cell(theta) -> tuple[str, str]:
    return str(theta.geometry), str(theta.occlusion)


def counts_by_cell(thetas, assignment: dict[int, float]) -> dict[str, dict[str, int]]:
    groups: dict[tuple[str, str], list] = defaultdict(list)
    for theta in thetas:
        groups[cell(theta)].append(theta)
    out = {}
    for key, group in sorted(groups.items()):
        c = Counter(float(assignment[int(t.sample)]) for t in group)
        out[f"{key[0]}::{key[1]}"] = {str(w): int(n) for w, n in sorted(c.items())}
    return out


def freeze_permutations(thetas, true: dict[int, float], n: int, seed: int):
    groups: dict[tuple[str, str], list] = defaultdict(list)
    for theta in thetas:
        groups[cell(theta)].append(theta)
    groups = {k: sorted(v, key=lambda t: int(t.sample)) for k, v in groups.items()}
    samples = sorted(true)
    true_tuple = tuple(true[s] for s in samples)
    target_counts = counts_by_cell(thetas, true)
    out, seen, attempts = [], set(), 0
    while len(out) < n and attempts < max(10_000, 100 * n):
        rng = np.random.default_rng(seed + 1_000_003 * attempts)
        candidate = {}
        for key in sorted(groups):
            group = groups[key]
            labels = np.asarray([true[int(t.sample)] for t in group], dtype=float)
            for t, w in zip(group, rng.permutation(labels), strict=True):
                candidate[int(t.sample)] = float(w)
        token = tuple(candidate[s] for s in samples)
        attempts += 1
        if token == true_tuple or token in seen:
            continue
        if counts_by_cell(thetas, candidate) != target_counts:
            raise RuntimeError("placebo did not preserve within-cell width counts")
        seen.add(token)
        out.append(candidate)
    if len(out) != n:
        raise RuntimeError(f"could freeze only {len(out)} of {n} unique placebos")
    changed = [float(np.mean([a[s] != true[s] for s in samples])) for a in out]
    radii = np.asarray([next(float(t.radius) for t in thetas if int(t.sample) == s) for s in samples])
    true_w = np.asarray([true[s] for s in samples])
    true_corr = float(np.corrcoef(radii, true_w)[0, 1]) if np.std(true_w) else float("nan")
    perm_corr = []
    for a in out:
        aw = np.asarray([a[s] for s in samples])
        if np.std(aw):
            perm_corr.append(float(np.corrcoef(radii, aw)[0, 1]))
    return out, {
        "frozen_unique_nonidentity_permutations": len(out),
        "generation_attempts": attempts,
        "true_width_counts_by_geometry_occlusion": target_counts,
        "changed_fraction_of_theta_assignments": summary(changed),
        "radius_width_pearson_true": true_corr,
        "radius_width_pearson_placebos": summary(perm_corr),
        "contract": "shuffle width labels within each geometry x occlusion cell; exact cell frequencies preserved",
    }


def score(rows: list[dict], assignment: dict[int, float], skies: int) -> list[float]:
    by_sky: dict[int, list[float]] = defaultdict(list)
    for r in rows:
        w = assignment[int(r["sample"])]
        by_sky[int(r["base_sky_id"])].append(float(r["observed_leakage_ratio"][str(w)]))
    return [float(np.median(by_sky[i])) for i in range(skies)]


def fixed_score(rows: list[dict], width: float, skies: int) -> list[float]:
    by_sky: dict[int, list[float]] = defaultdict(list)
    for r in rows:
        by_sky[int(r["base_sky_id"])].append(float(r["observed_leakage_ratio"][str(width)]))
    return [float(np.median(by_sky[i])) for i in range(skies)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dev-skies", type=int, default=12)
    ap.add_argument("--heldout-skies", type=int, default=24)
    ap.add_argument("--theta-per-cell", type=int, default=8)
    ap.add_argument("--radius-bands", type=int, default=3)
    ap.add_argument("--permutations", type=int, default=255)
    ap.add_argument("--beam-width-ratios", nargs="+", type=float, default=[0.125, 0.25, 0.5, 1.0])
    ap.add_argument("--baseline-width", type=float, default=0.5)
    ap.add_argument("--metric-k0", nargs="+", type=float, default=[4.0, 8.0, 16.0])
    ap.add_argument("--ny", type=int, default=64)
    ap.add_argument("--nx", type=int, default=128)
    ap.add_argument("--seed", type=int, default=20260926)
    ap.add_argument("--rows", type=Path, default=Path("pontifex-cmb-radius-assignment-permutation.jsonl"))
    ap.add_argument("--output", type=Path, default=Path("pontifex-cmb-radius-assignment-permutation.json"))
    args = ap.parse_args()

    widths = sorted(set(float(w) for w in args.beam_width_ratios))
    k0 = sorted(set(float(k) for k in args.metric_k0))
    if args.baseline_width not in widths or args.dev_skies < 2 or args.heldout_skies < 2:
        raise ValueError("invalid baseline or sky budget")

    # Panel/radius strata exist before any sky outcome.
    thetas = balanced_theta_panel(args.seed, args.theta_per_cell)
    edges = _strict_quantile_edges([float(t.radius) for t in thetas], args.radius_bands, "theta radius")

    dev_base = args.seed + 63_000_000_127
    dev_seeds = [dev_base + 100_000_007 * i for i in range(args.dev_skies)]
    dev = collect_rows(base_seeds=dev_seeds, thetas=thetas, metric_k0=k0, widths=widths,
                       ny=args.ny, nx=args.nx, stage="development")
    annotate_predictor(dev, edges)
    policy, diag = {}, {}
    for rb in range(args.radius_bands):
        band = [r for r in dev if int(r["radius_band"]) == rb]
        policy[rb], diag[str(rb)] = choose_width(band, widths=widths, baseline=args.baseline_width)
    true = {int(t.sample): float(policy[int(np.searchsorted(edges, float(t.radius), side="right"))]) for t in thetas}

    # Freeze all placebo assignments before held-out sky seeds are generated.
    perm_seed = args.seed + 31_415_926
    placebos, integrity = freeze_permutations(thetas, true, args.permutations, perm_seed)

    held_base = args.seed + 99_000_000_389
    held_seeds = [held_base + 100_000_007 * i for i in range(args.heldout_skies)]
    held = collect_rows(base_seeds=held_seeds, thetas=thetas, metric_k0=k0, widths=widths,
                        ny=args.ny, nx=args.nx, stage="heldout")
    true_s = score(held, true, args.heldout_skies)
    placebo_s = np.asarray([score(held, a, args.heldout_skies) for a in placebos])
    placebo_med = [float(x) for x in np.median(placebo_s, axis=0)]
    fixed = fixed_score(held, args.baseline_width, args.heldout_skies)

    true_stat = float(np.mean(true_s))
    null_stats = [float(np.mean(x)) for x in placebo_s]
    exceed = int(sum(x >= true_stat - 1e-15 for x in null_stats))
    randomization_p = float((1 + exceed) / (args.permutations + 1))

    diffs = {
        "primary_true_minus_placebo_ensemble": [a - b for a, b in zip(true_s, placebo_med, strict=True)],
        "secondary_true_minus_fixed": [a - b for a, b in zip(true_s, fixed, strict=True)],
        "secondary_placebo_ensemble_minus_fixed": [a - b for a, b in zip(placebo_med, fixed, strict=True)],
    }
    tests = {name: {**sign_test(vals), "difference_summary": summary(vals)} for name, vals in diffs.items()}
    adjusted = holm_adjust({name: float(x["exact_two_sided_sign_p"]) for name, x in tests.items()})
    for name in tests:
        tests[name]["holm_adjusted_p"] = float(adjusted[name])

    result = {
        "experiment": "Pontifex CMB radius assignment frequency-matched permutation holdout",
        "design": {
            "development_skies": args.dev_skies, "heldout_skies": args.heldout_skies,
            "theta_total": len(thetas), "theta_per_geometry_occlusion_cell": args.theta_per_cell,
            "radius_bands": args.radius_bands, "beam_width_ratios": widths,
            "baseline_width": args.baseline_width, "metric_k0": k0,
            "permutations": args.permutations, "inferential_unit": "base-sky seed",
            "freeze_order": ["theta/radius bands", "development policy", "placebos", "held-out skies"],
            "data_boundary": "synthetic development/held-out only; no assembly/student/val/test data",
        },
        "development": {"radius_edges": edges, "selected_width_by_radius_band": {str(k): v for k, v in policy.items()}, "diagnostics": diag},
        "permutation_null": integrity,
        "heldout": {
            "true_assignment": summary(true_s), "placebo_ensemble_median": summary(placebo_med),
            "fixed_0.5": summary(fixed), "planned_sign_tests": tests,
            "randomization_test": {
                "statistic": "mean of independent base-sky median leakages",
                "alternative": "true radius-linked assignment > frequency-matched placebo",
                "true_statistic": true_stat, "null_distribution": summary(null_stats),
                "exceedances_ge_true": exceed, "plus_one_p": randomization_p,
                "resolution": 1.0 / (args.permutations + 1),
            },
        },
        "interpretation_contract": {
            "positive": "radius-width coupling has held-out synthetic value beyond marginal width frequencies",
            "null": "radius specificity is not demonstrated beyond the marginal width mixture",
            "not_supported": ["physical CMB scale", "Planck/ACT behavior", "physical nonlocality", "Torus causality"],
        },
        "reproducibility": {"seed": args.seed, "permutation_seed": perm_seed, "development_seeds": dev_seeds, "heldout_seeds": held_seeds},
    }
    args.rows.parent.mkdir(parents=True, exist_ok=True)
    with args.rows.open("w", encoding="utf-8") as fh:
        for r in dev + held:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"policy": result["development"]["selected_width_by_radius_band"],
                      "randomization": result["heldout"]["randomization_test"],
                      "sign_tests": tests}, indent=2))


if __name__ == "__main__":
    main()
