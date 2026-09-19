# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scipy>=1.14",
# ]
# ///
"""Robustness ladder for Pontifex matched-null calibration.

The current CMB audit correctly replaces a naive Gaussian interpretation of

    z_like = (observed - mean(nulls)) / sd(nulls)

with the predictive Student-t law under an exchangeable *Gaussian* null. This
experiment asks the next discriminating question: how dependent is that repair
on Gaussianity, and what can be claimed without a parametric shape assumption?

For each null-ensemble size m and several exchangeable score distributions, we
simulate m+1 iid scores. Item 0 plays the observed map and the other m items are
its matched nulls. We report three calibrations:

* naive_normal: the old, known-bad N(0,1) reading of z_like;
* predictive_t: exact under Gaussian scores with unknown mean/variance;
* exact_rank: permutation rank of the candidate leave-one-out studentized
  residual among all m+1 exchangeable leave-one-out residuals.

The rank p-value is finite-sample valid for any continuous exchangeable score
distribution, but its resolution is 1/(m+1). This makes the trade-off explicit:
small m can support a parametric predictive-t diagnostic, but cannot provide a
fine-grained distribution-free tail claim.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.stats import norm, t


FAMILIES = ("gaussian", "student_t5", "lognormal", "contaminated_gaussian")
ALPHAS = (0.05, 0.01)


def draw_scores(
    rng: np.random.Generator, family: str, shape: tuple[int, int]
) -> np.ndarray:
    if family == "gaussian":
        return rng.normal(size=shape)
    if family == "student_t5":
        # Unit variance; tail shape, not scale, is the perturbation of interest.
        return rng.standard_t(5, size=shape) / np.sqrt(5.0 / 3.0)
    if family == "lognormal":
        raw = np.exp(rng.normal(size=shape))
        mean = np.exp(0.5)
        sd = np.sqrt((np.exp(1.0) - 1.0) * np.exp(1.0))
        return (raw - mean) / sd
    if family == "contaminated_gaussian":
        x = rng.normal(size=shape)
        contam = rng.random(shape) < 0.05
        x[contam] *= 5.0
        return x / np.sqrt(0.95 + 0.05 * 25.0)
    raise ValueError(f"unknown family: {family}")


def leave_one_out_t(x: np.ndarray) -> np.ndarray:
    """Predictive-t statistic for every possible held-out member of each row."""
    _, k = x.shape
    m = k - 1
    if m < 2:
        raise ValueError("m must be >= 2")
    total = np.sum(x, axis=1, keepdims=True)
    total_sq = np.sum(x * x, axis=1, keepdims=True)
    mean_excl = (total - x) / m
    centered_ss = (total_sq - x * x) - m * mean_excl * mean_excl
    var_excl = np.maximum(centered_ss / (m - 1), 0.0)
    sd_excl = np.sqrt(var_excl)
    z_like = np.divide(
        x - mean_excl,
        sd_excl,
        out=np.full_like(x, np.nan),
        where=sd_excl > 1e-15,
    )
    return z_like / np.sqrt(1.0 + 1.0 / m)


def simulate_cell(
    family: str,
    m: int,
    trials: int,
    batch_size: int,
    seed: int,
) -> dict:
    rng = np.random.default_rng(seed)
    counts = {
        "naive_normal": {a: 0 for a in ALPHAS},
        "predictive_t": {a: 0 for a in ALPHAS},
        "exact_rank": {a: 0 for a in ALPHAS},
    }
    finite = 0

    for start in range(0, trials, batch_size):
        b = min(batch_size, trials - start)
        x = draw_scores(rng, family, (b, m + 1))
        t_loo = leave_one_out_t(x)
        t_obs = t_loo[:, 0]
        good = np.isfinite(t_obs) & np.all(np.isfinite(t_loo), axis=1)
        if not np.any(good):
            continue
        tt = t_obs[good]
        all_t = t_loo[good]
        finite += int(tt.size)

        # Recover z_like because t_pred = z_like / sqrt(1 + 1/m).
        z_like = tt * np.sqrt(1.0 + 1.0 / m)
        p_normal = 2.0 * norm.sf(np.abs(z_like))
        p_t = 2.0 * t.sf(np.abs(tt), df=m - 1)

        # Exact randomization p under exchangeability. Computing the same
        # leave-one-out statistic for every member makes the ranking symmetric.
        p_rank = np.mean(np.abs(all_t) >= np.abs(tt)[:, None], axis=1)

        for alpha in ALPHAS:
            counts["naive_normal"][alpha] += int(np.count_nonzero(p_normal <= alpha))
            counts["predictive_t"][alpha] += int(np.count_nonzero(p_t <= alpha))
            counts["exact_rank"][alpha] += int(np.count_nonzero(p_rank <= alpha))

    if finite == 0:
        raise RuntimeError("no finite trials")

    rates = {
        method: {f"alpha_{alpha:g}": count / finite for alpha, count in vals.items()}
        for method, vals in counts.items()
    }
    return {
        "family": family,
        "m": m,
        "trials": finite,
        "rank_resolution": 1.0 / (m + 1),
        "rates": rates,
        "predictive_t_error_at_0.05": rates["predictive_t"]["alpha_0.05"] - 0.05,
        "predictive_t_error_at_0.01": rates["predictive_t"]["alpha_0.01"] - 0.01,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--null-counts", nargs="+", type=int, default=[4, 8, 16, 32, 64, 128]
    )
    ap.add_argument(
        "--families", nargs="+", choices=FAMILIES, default=list(FAMILIES)
    )
    ap.add_argument("--trials", type=int, default=100_000)
    ap.add_argument("--batch-size", type=int, default=5_000)
    ap.add_argument("--seed", type=int, default=20260918)
    ap.add_argument(
        "--output", type=Path, default=Path("pontifex-cmb-null-robustness.json")
    )
    args = ap.parse_args()

    rows = []
    for fi, family in enumerate(args.families):
        for m in args.null_counts:
            rows.append(
                simulate_cell(
                    family,
                    m,
                    args.trials,
                    args.batch_size,
                    args.seed + fi * 10_000_019 + m * 1_000_003,
                )
            )

    gaussian = [r for r in rows if r["family"] == "gaussian"]
    non_gaussian = [r for r in rows if r["family"] != "gaussian"]
    max_gaussian_err = max(
        abs(r["predictive_t_error_at_0.05"]) for r in gaussian
    )
    max_non_gaussian_inflation_005 = max(
        r["rates"]["predictive_t"]["alpha_0.05"] / 0.05 for r in non_gaussian
    )
    max_non_gaussian_inflation_001 = max(
        r["rates"]["predictive_t"]["alpha_0.01"] / 0.01 for r in non_gaussian
    )

    result = {
        "experiment": "Pontifex CMB matched-null robustness ladder",
        "null_counts": args.null_counts,
        "families": args.families,
        "trials_per_cell": args.trials,
        "rows": rows,
        "headline": {
            "max_abs_predictive_t_fpr_error_at_0.05_under_gaussian": max_gaussian_err,
            "max_predictive_t_inflation_at_0.05_non_gaussian": max_non_gaussian_inflation_005,
            "max_predictive_t_inflation_at_0.01_non_gaussian": max_non_gaussian_inflation_001,
            "distribution_free_min_nulls_for_p_le_0.05": 19,
            "distribution_free_min_nulls_for_p_le_0.01": 99,
        },
        "interpretation_contract": {
            "evidence": (
                "predictive Student-t is calibrated under the Gaussian score null, while "
                "the exact leave-one-out rank calibration remains finite-sample valid "
                "across all simulated exchangeable score families"
            ),
            "negative_result": (
                "predictive Student-t is not distribution-free; skewed/heavy-tailed score "
                "families can retain material tail inflation even as m grows"
            ),
            "not_evidence": (
                "the non-Gaussian families are adversarial stylized score distributions, "
                "not measurements of the actual Pontifex CMB score law"
            ),
            "production_rule": (
                "treat predictive-t as a parametric diagnostic unless Gaussianity of the "
                "matched-null score law is supported; for calibration-free tail claims, "
                "increase m enough for an exact rank test to resolve the target alpha"
            ),
            "scope": (
                "calibration mechanics only; no real-CMB anomaly, Torus causality, or "
                "assembly/student/val/test performance is tested here"
            ),
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
