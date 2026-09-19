# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scipy>=1.14",
# ]
# ///
"""Development/held-out replication for the Pontifex metric-aware beam scale.

The metric-aware ladder suggested that nonlocal leakage peaks near a beam width
of one half lesion radius, but that observation was made on the same skies used
to inspect the curve.  This experiment removes that adaptivity.

Protocol
--------
1. Fix one balanced theta panel before any sky is generated.
2. On DEVELOPMENT skies only, select one nonzero beam width by a predeclared
   criterion: maximize the median across skies of the per-sky median observed
   leakage ratio. Ties go to the smaller width.
3. Only after the width is frozen, generate disjoint HELD-OUT sky seeds.
4. On held-out skies, compare the frozen width with every alternative width
   using sky-level paired leakage contrasts.  Exact sign tests are Holm-adjusted
   across those planned contrasts.
5. Matched-null calibration is run only for the already-frozen width on held-out
   skies, so the null results cannot feed back into width selection.

The independent synthetic sky is the replication unit. Theta rows within a sky
share a field and are not treated as independent population replicates.
No assembly/student/validation/test data are touched.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

from cmb_metric_beam_ladder import responses
from cmb_nonlocal_observable_ablation import calibrate, finite_corr, summary
from cmb_occlusion_mc import GEOMETRIES, OCCLUSIONS, make_null, sample_theta, synthetic_map


def balanced_theta_panel(seed: int, theta_per_cell: int):
    rng = np.random.default_rng(seed + 17)
    thetas = []
    sample_id = 0
    for occlusion in OCCLUSIONS:
        for geometry in GEOMETRIES:
            for _ in range(theta_per_cell):
                base = sample_theta(rng, sample_id, 0.008, 0.20)
                thetas.append(replace(base, geometry=str(geometry), occlusion=str(occlusion)))
                sample_id += 1
    return thetas


def holm_adjust(raw: dict[float, float]) -> dict[float, float]:
    ordered = sorted(raw.items(), key=lambda kv: kv[1])
    m = len(ordered)
    out: dict[float, float] = {}
    running = 0.0
    for rank, (width, p) in enumerate(ordered):
        adj = min(1.0, (m - rank) * p)
        running = max(running, adj)
        out[width] = running
    return out


def choose_width(
    field_by_sky: list[np.ndarray],
    sky_seeds: list[int],
    thetas,
    widths: list[float],
) -> tuple[float, dict]:
    by_width_sky: dict[float, list[float]] = defaultdict(list)
    persisted = []

    for sky_id, (field, sky_seed) in enumerate(zip(field_by_sky, sky_seeds, strict=True)):
        per_width: dict[float, list[float]] = {w: [] for w in widths}
        for theta in thetas:
            obs_rng = np.random.default_rng(sky_seed + 97_409 * (theta.sample + 1))
            core, beam, ratio = responses(field, theta, obs_rng, widths)
            persisted.append(
                {
                    "stage": "development",
                    "sky_id": sky_id,
                    "sky_seed": sky_seed,
                    **asdict(theta),
                    "observed_core_rmse": core,
                    "observed_leakage_ratio": {str(w): ratio[w] for w in widths},
                }
            )
            for w in widths:
                per_width[w].append(ratio[w])
        for w in widths:
            by_width_sky[w].append(float(np.median(per_width[w])))

    selection_scores = {
        w: float(np.median(np.asarray(by_width_sky[w], dtype=float))) for w in widths
    }
    selected = min(widths, key=lambda w: (-selection_scores[w], w))
    return selected, {
        "criterion": "maximize median_across_dev_skies(per_sky_median_observed_leakage_ratio); ties -> smaller width",
        "selection_scores": {str(w): selection_scores[w] for w in widths},
        "per_sky_medians": {str(w): by_width_sky[w] for w in widths},
        "selected_width": selected,
        "persisted": persisted,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dev-skies", type=int, default=6)
    ap.add_argument("--heldout-skies", type=int, default=12)
    ap.add_argument("--theta-per-cell", type=int, default=3)
    ap.add_argument("--null-maps", type=int, default=32)
    ap.add_argument(
        "--beam-width-ratios",
        nargs="+",
        type=float,
        default=[0.125, 0.25, 0.5, 1.0],
    )
    ap.add_argument("--ny", type=int, default=64)
    ap.add_argument("--nx", type=int, default=128)
    ap.add_argument("--seed", type=int, default=20260919)
    ap.add_argument("--rows", type=Path, default=Path("pontifex-cmb-beam-scale-holdout.jsonl"))
    ap.add_argument("--output", type=Path, default=Path("pontifex-cmb-beam-scale-holdout.json"))
    args = ap.parse_args()

    widths = sorted(set(float(w) for w in args.beam_width_ratios))
    if args.dev_skies < 2 or args.heldout_skies < 2 or args.theta_per_cell < 1:
        raise ValueError("need at least two skies per stage and one theta per cell")
    if args.null_maps < 19:
        raise ValueError("null_maps must be >=19 so exact rank can resolve alpha=0.05")
    if not widths or min(widths) <= 0.0:
        raise ValueError("candidate widths must be strictly positive")

    thetas = balanced_theta_panel(args.seed, args.theta_per_cell)

    # Development and held-out seed ranges are intentionally far apart. Held-out
    # fields are not generated until the development width has been frozen.
    dev_seeds = [args.seed + 100_000_007 * i for i in range(args.dev_skies)]
    dev_fields = [synthetic_map(args.ny, args.nx, s) for s in dev_seeds]
    selected, dev = choose_width(dev_fields, dev_seeds, thetas, widths)

    heldout_seed_base = args.seed + 9_000_000_019
    heldout_seeds = [heldout_seed_base + 100_000_007 * i for i in range(args.heldout_skies)]

    heldout_sky_median_ratio: dict[float, list[float]] = {w: [] for w in widths}
    heldout_peak_widths: list[float] = []
    selected_core_corr: list[float] = []
    selected_rank_gap_by_sky: list[float] = []
    selected_rank_disagreement_by_sky: list[float] = []
    selected_rank_corr_by_sky: list[float] = []
    zero_variance_rows = 0
    persisted = list(dev["persisted"])

    for sky_id, sky_seed in enumerate(heldout_seeds):
        field = synthetic_map(args.ny, args.nx, sky_seed)
        null_maps = [
            make_null(field, np.random.default_rng(sky_seed + 1_000_003 * (i + 1)))
            for i in range(args.null_maps)
        ]
        ratios: dict[float, list[float]] = {w: [] for w in widths}
        obs_core_values: list[float] = []
        obs_selected_values: list[float] = []
        core_rank: list[float] = []
        selected_rank: list[float] = []

        for theta in thetas:
            obs_rng = np.random.default_rng(sky_seed + 97_409 * (theta.sample + 1))
            obs_core, obs_beam, obs_ratio = responses(field, theta, obs_rng, widths)
            for w in widths:
                ratios[w].append(obs_ratio[w])

            null_core = []
            null_selected = []
            for null_id, null_map in enumerate(null_maps):
                null_rng = np.random.default_rng(
                    sky_seed + 10_000_019 * (theta.sample + 1) + null_id
                )
                ncore, nbeam, _ = responses(null_map, theta, null_rng, [selected])
                null_core.append(ncore)
                null_selected.append(nbeam[selected])

            try:
                ccal = calibrate(obs_core, np.asarray(null_core, dtype=float))
                bcal = calibrate(obs_beam[selected], np.asarray(null_selected, dtype=float))
                core_rank.append(ccal["rank_p"])
                selected_rank.append(bcal["rank_p"])
            except ValueError:
                zero_variance_rows += 1
                ccal = None
                bcal = None

            obs_core_values.append(obs_core)
            obs_selected_values.append(obs_beam[selected])
            persisted.append(
                {
                    "stage": "heldout",
                    "sky_id": sky_id,
                    "sky_seed": sky_seed,
                    **asdict(theta),
                    "frozen_selected_width": selected,
                    "observed_core_rmse": obs_core,
                    "observed_beam_boundary_rmse": {str(w): obs_beam[w] for w in widths},
                    "observed_leakage_ratio": {str(w): obs_ratio[w] for w in widths},
                    "core_rank_p": None if ccal is None else ccal["rank_p"],
                    "selected_rank_p": None if bcal is None else bcal["rank_p"],
                }
            )

        sky_medians = {w: float(np.median(ratios[w])) for w in widths}
        for w in widths:
            heldout_sky_median_ratio[w].append(sky_medians[w])
        heldout_peak_widths.append(min(widths, key=lambda w: (-sky_medians[w], w)))
        selected_core_corr.append(finite_corr(obs_core_values, obs_selected_values))

        if core_rank and selected_rank:
            cr = np.asarray(core_rank, dtype=float)
            sr = np.asarray(selected_rank, dtype=float)
            selected_rank_gap_by_sky.append(float(np.median(np.abs(cr - sr))))
            selected_rank_disagreement_by_sky.append(
                float(np.mean((cr <= 0.05) != (sr <= 0.05)))
            )
            selected_rank_corr_by_sky.append(finite_corr(cr, sr))

    raw_sign_p: dict[float, float] = {}
    contrasts: dict[str, dict] = {}
    for w in widths:
        if w == selected:
            continue
        diffs = np.asarray(heldout_sky_median_ratio[selected]) - np.asarray(
            heldout_sky_median_ratio[w]
        )
        nonzero = diffs[np.abs(diffs) > 1e-15]
        positives = int(np.count_nonzero(nonzero > 0))
        raw_p = (
            float(binomtest(positives, n=len(nonzero), p=0.5, alternative="two-sided").pvalue)
            if len(nonzero)
            else 1.0
        )
        raw_sign_p[w] = raw_p
        contrasts[str(w)] = {
            "alternative_width": w,
            "heldout_skies": args.heldout_skies,
            "nonzero_paired_differences": int(len(nonzero)),
            "selected_greater_count": positives,
            "selected_minus_alternative_per_sky": [float(x) for x in diffs],
            "selected_minus_alternative": summary(diffs.tolist()),
            "exact_two_sided_sign_p_raw": raw_p,
        }

    adjusted = holm_adjust(raw_sign_p)
    for w, adj in adjusted.items():
        contrasts[str(w)]["exact_sign_p_holm"] = adj

    result = {
        "experiment": "Pontifex CMB beam-scale development/held-out replication",
        "design": {
            "theta_panel_fixed_before_skies": True,
            "theta_per_sky": len(thetas),
            "balanced_geometries": list(GEOMETRIES),
            "balanced_occlusions": list(OCCLUSIONS),
            "candidate_widths": widths,
            "development_skies": args.dev_skies,
            "heldout_skies": args.heldout_skies,
            "null_maps_on_heldout_only": args.null_maps,
            "rank_resolution": 1.0 / (args.null_maps + 1),
            "heldout_generated_only_after_width_frozen": True,
            "replication_unit": "independent synthetic sky",
        },
        "development_selection": {k: v for k, v in dev.items() if k != "persisted"},
        "heldout_confirmation": {
            "frozen_width": selected,
            "per_width_sky_median_leakage": {
                str(w): heldout_sky_median_ratio[w] for w in widths
            },
            "peak_width_counts_across_heldout_skies": {
                str(w): int(sum(x == w for x in heldout_peak_widths)) for w in widths
            },
            "planned_paired_contrasts": contrasts,
            "frozen_width_core_vs_boundary_pearson_by_sky": summary(selected_core_corr),
            "frozen_width_rank_p_median_abs_gap_by_sky": summary(selected_rank_gap_by_sky),
            "frozen_width_rank_decision_disagreement_0.05_by_sky": summary(
                selected_rank_disagreement_by_sky
            ),
            "frozen_width_core_vs_boundary_rank_p_corr_by_sky": summary(
                selected_rank_corr_by_sky
            ),
            "zero_variance_calibration_rows": zero_variance_rows,
        },
        "interpretation_contract": {
            "evidence": (
                "the selected width is chosen on development skies only; held-out sky-level paired contrasts test whether "
                "that scale-response preference reproduces on unseen synthetic fields"
            ),
            "negative_result_rule": (
                "if the frozen width does not retain its leakage advantage on held-out skies, the apparent development "
                "peak is treated as unstable rather than rescued by choosing a new width"
            ),
            "hypothesis": (
                "a replicated synthetic scale peak motivates, but does not establish, a multiscale observation model"
            ),
            "not_evidence": (
                "this does not identify a physical Planck/ACT beam scale, a CMB anomaly, physical nonlocality, topology, "
                "or Torus causality"
            ),
            "dependence_boundary": (
                "theta rows within a sky share the field; all confirmatory comparisons are summarized at the sky level"
            ),
            "data_boundary": (
                "D_assembly, D_student, D_val, and D_test remain disjoint and untouched; none enters this experiment"
            ),
        },
    }

    args.rows.parent.mkdir(parents=True, exist_ok=True)
    with args.rows.open("w", encoding="utf-8") as f:
        for row in persisted:
            f.write(json.dumps(row) + "\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, allow_nan=True))


if __name__ == "__main__":
    main()
