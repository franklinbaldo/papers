# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scipy>=1.14",
# ]
# ///
"""Empirical matched-null ladder on independent synthetic skies.

This experiment uses the actual Pontifex CMB score-producing harness rather than
stylized score families. For each independent synthetic sky, theta is sampled
once and evaluated on the sky plus a nested ensemble of 128 phase-scrambled
matched null maps. The same score vectors are then truncated at m=32,64,128.

Two calibrations are compared:
- predictive Student-t, exact only if the matched-null score law is Gaussian;
- exchangeable leave-one-out rank, finite-sample exact under exchangeability.

Rows within a sky share the same field/null maps, so rejection fractions are
diagnostics over interventions, not independent population-level tests.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.stats import kurtosis, skew, t

from cmb_matched_null_robustness_ladder import leave_one_out_t
from cmb_occlusion_mc import make_null, matched_null_stats, run_one, sample_theta, synthetic_map

ALPHAS = (0.05, 0.01)


def summarize(values: list[float]) -> dict[str, float]:
    x = np.asarray(values, dtype=float)
    return {
        "mean": float(np.mean(x)),
        "median": float(np.median(x)),
        "min": float(np.min(x)),
        "max": float(np.max(x)),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skies", type=int, default=6)
    ap.add_argument("--samples-per-sky", type=int, default=48)
    ap.add_argument("--null-counts", nargs="+", type=int, default=[32, 64, 128])
    ap.add_argument("--ny", type=int, default=64)
    ap.add_argument("--nx", type=int, default=128)
    ap.add_argument("--seed", type=int, default=20260918)
    ap.add_argument("--scores", type=Path, default=Path("pontifex-cmb-empirical-null-scores.jsonl"))
    ap.add_argument("--output", type=Path, default=Path("pontifex-cmb-empirical-null-ladder.json"))
    args = ap.parse_args()

    max_m = max(args.null_counts)
    if min(args.null_counts) < 3:
        raise ValueError("all null counts must be >= 3")

    score_rows: list[dict] = []
    cells: dict[int, dict[str, list[float] | int]] = {
        m: {
            "predictive_p": [],
            "rank_p": [],
            "null_skew": [],
            "null_excess_kurtosis": [],
            "abs_p_gap": [],
            "finite": 0,
        }
        for m in args.null_counts
    }

    for sky_id in range(args.skies):
        sky_seed = args.seed + 100_000_007 * sky_id
        field = synthetic_map(args.ny, args.nx, sky_seed)
        theta_rng = np.random.default_rng(sky_seed + 17)
        thetas = [sample_theta(theta_rng, i, 0.008, 0.20) for i in range(args.samples_per_sky)]
        null_maps = [
            make_null(field, np.random.default_rng(sky_seed + 1_000_003 * (i + 1)))
            for i in range(max_m)
        ]

        for theta in thetas:
            obs_rng = np.random.default_rng(sky_seed + 97_409 * (theta.sample + 1))
            obs = float(run_one(field, theta, obs_rng, "synthetic", None)["score"])
            _, _, full_null = matched_null_stats(null_maps, theta, sky_seed, "synthetic", None)
            score_rows.append(
                {
                    "sky_id": sky_id,
                    "sky_seed": sky_seed,
                    "theta_sample": theta.sample,
                    "observed_score": obs,
                    "null_scores": [float(x) for x in full_null],
                }
            )

            for m in args.null_counts:
                null = np.asarray(full_null[:m], dtype=float)
                sd = float(np.std(null, ddof=1))
                if not np.isfinite(sd) or sd <= 1e-15:
                    continue
                z_like = (obs - float(np.mean(null))) / sd
                t_pred = z_like / np.sqrt(1.0 + 1.0 / m)
                p_t = float(2.0 * t.sf(abs(t_pred), df=m - 1))

                joint = np.concatenate(([obs], null))[None, :]
                loo = leave_one_out_t(joint)[0]
                p_rank = float(np.mean(np.abs(loo) >= abs(loo[0])))

                cell = cells[m]
                cell["predictive_p"].append(p_t)
                cell["rank_p"].append(p_rank)
                cell["null_skew"].append(float(skew(null, bias=False)))
                cell["null_excess_kurtosis"].append(float(kurtosis(null, fisher=True, bias=False)))
                cell["abs_p_gap"].append(abs(p_t - p_rank))
                cell["finite"] += 1

    rows = []
    for m in args.null_counts:
        c = cells[m]
        pt = np.asarray(c["predictive_p"], dtype=float)
        pr = np.asarray(c["rank_p"], dtype=float)
        row = {
            "m": m,
            "rows": int(c["finite"]),
            "rank_resolution": 1.0 / (m + 1),
            "predictive_t_rejection": {f"alpha_{a:g}": float(np.mean(pt <= a)) for a in ALPHAS},
            "exact_rank_rejection": {f"alpha_{a:g}": float(np.mean(pr <= a)) for a in ALPHAS},
            "predictive_vs_rank_disagreement": {
                f"alpha_{a:g}": float(np.mean((pt <= a) != (pr <= a))) for a in ALPHAS
            },
            "abs_p_gap": summarize(c["abs_p_gap"]),
            "null_score_shape": {
                "skew": summarize(c["null_skew"]),
                "excess_kurtosis": summarize(c["null_excess_kurtosis"]),
            },
        }
        rows.append(row)

    result = {
        "experiment": "Pontifex CMB empirical matched-null ladder on independent synthetic skies",
        "skies": args.skies,
        "samples_per_sky": args.samples_per_sky,
        "null_counts": args.null_counts,
        "map_shape": [args.ny, args.nx],
        "rows": rows,
        "interpretation_contract": {
            "evidence": (
                "this measures the actual score law emitted by the synthetic Pontifex CMB harness "
                "across independent synthetic skies, using nested matched-null ensembles"
            ),
            "negative_result_rule": (
                "persistent predictive-t versus exact-rank disagreement is evidence against "
                "treating Student-t calibration as distribution-free for this harness"
            ),
            "not_evidence": (
                "rows within a sky are dependent and the nulls are phase-scrambled derivatives "
                "of that sky; rejection fractions are diagnostics, not population p-values"
            ),
            "scope": (
                "synthetic calibration mechanics only; no real-CMB anomaly, Torus causality, "
                "or assembly/student/val/test performance is tested"
            ),
        },
    }

    args.scores.parent.mkdir(parents=True, exist_ok=True)
    with args.scores.open("w", encoding="utf-8") as f:
        for row in score_rows:
            f.write(json.dumps(row) + "\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
