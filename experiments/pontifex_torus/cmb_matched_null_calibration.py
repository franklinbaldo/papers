# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scipy>=1.14",
# ]
# ///
"""Audit the small-ensemble matched-null calibration used by Pontifex CMB stress tests.

The upstream Monte Carlo reports

    z_like = (observed - mean(nulls)) / sd(nulls)

When the null mean and variance are estimated from only ``m`` null maps, this is
*not* a standard normal z-score. Under an exchangeable Gaussian null,

    t_pred = z_like / sqrt(1 + 1/m)

has a Student-t distribution with ``m - 1`` degrees of freedom. This audit
compares the anti-conservative Gaussian interpretation with the predictive-t
calibration on the synthetic smoke output.

The rows reuse one synthetic sky and many overlapping interventions, so the KS
and rejection rates below are calibration diagnostics, not independent
population-level hypothesis tests.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import kstest, norm, t


def finite_summary(values: np.ndarray) -> dict[str, float]:
    x = np.asarray(values, dtype=float)
    x = x[np.isfinite(x)]
    if x.size == 0:
        return {
            "count": 0,
            "mean": float("nan"),
            "median": float("nan"),
            "std": float("nan"),
        }
    return {
        "count": int(x.size),
        "mean": float(np.mean(x)),
        "median": float(np.median(x)),
        "std": float(np.std(x, ddof=1)) if x.size > 1 else 0.0,
        "p95_abs": float(np.quantile(np.abs(x), 0.95)),
        "max_abs": float(np.max(np.abs(x))),
    }


def rejection_rates(p: np.ndarray) -> dict[str, float]:
    good = p[np.isfinite(p)]
    return {
        "alpha_0_05": float(np.mean(good < 0.05)),
        "alpha_0_01": float(np.mean(good < 0.01)),
        "alpha_0_001": float(np.mean(good < 0.001)),
    }


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def audit(rows: list[dict[str, str]]) -> dict:
    if not rows:
        raise ValueError("input CSV contains no rows")

    z_like = np.asarray([float(r["z_matched_null"]) for r in rows], dtype=float)
    m = np.asarray([int(r["null_n"]) for r in rows], dtype=int)
    if np.any(m < 2):
        raise ValueError("predictive Student-t calibration requires null_n >= 2")

    finite = np.isfinite(z_like)
    z_like = z_like[finite]
    m = m[finite]
    finite_rows = [r for r, keep in zip(rows, finite, strict=True) if keep]

    predictive_t = z_like / np.sqrt(1.0 + 1.0 / m)
    predictive_p = np.asarray(
        [
            2.0 * t.sf(abs(stat), df=int(mi - 1))
            for stat, mi in zip(predictive_t, m, strict=True)
        ],
        dtype=float,
    )
    naive_normal_p = 2.0 * norm.sf(np.abs(z_like))

    ks = kstest(predictive_p, "uniform")

    by_occlusion: dict[str, list[int]] = defaultdict(list)
    for i, row in enumerate(finite_rows):
        by_occlusion[row["occlusion"]].append(i)

    family = {}
    for name, idx in sorted(by_occlusion.items()):
        ii = np.asarray(idx, dtype=int)
        family[name] = {
            "n": int(ii.size),
            "predictive_t": finite_summary(predictive_t[ii]),
            "predictive_t_rejection_rates": rejection_rates(predictive_p[ii]),
            "naive_normal_rejection_rates": rejection_rates(naive_normal_p[ii]),
        }

    null_counts = sorted({int(x) for x in m.tolist()})
    naive_005 = float(np.mean(naive_normal_p < 0.05))
    pred_005 = float(np.mean(predictive_p < 0.05))

    return {
        "experiment": "Pontifex CMB matched-null calibration audit",
        "rows": int(z_like.size),
        "null_maps_per_theta": null_counts,
        "statistical_correction": {
            "reported_upstream": "z_like = (observed - mean(nulls)) / sd(nulls)",
            "predictive_student_t": "t_pred = z_like / sqrt(1 + 1/m)",
            "degrees_of_freedom": "m - 1",
            "reason": "the null mean and variance are estimated from the same small null ensemble, so z_like is not N(0,1)",
        },
        "z_like": {
            "summary": finite_summary(z_like),
            "if_incorrectly_treated_as_standard_normal": {
                "rejection_rates": rejection_rates(naive_normal_p),
            },
        },
        "predictive_student_t": {
            "summary": finite_summary(predictive_t),
            "two_sided_p_rejection_rates": rejection_rates(predictive_p),
            "p_value_quantiles": {
                "p01": float(np.quantile(predictive_p, 0.01)),
                "p05": float(np.quantile(predictive_p, 0.05)),
                "p50": float(np.quantile(predictive_p, 0.50)),
                "p95": float(np.quantile(predictive_p, 0.95)),
                "p99": float(np.quantile(predictive_p, 0.99)),
            },
            "uniformity_smoke": {
                "ks_statistic": float(ks.statistic),
                "ks_pvalue_diagnostic_only": float(ks.pvalue),
            },
        },
        "headline_discriminant": {
            "naive_normal_alpha_0_05_rate": naive_005,
            "predictive_t_alpha_0_05_rate": pred_005,
            "inflation_factor_if_called_z": (
                float(naive_005 / pred_005) if pred_005 > 0 else float("inf")
            ),
        },
        "by_occlusion": family,
        "interpretation_contract": {
            "evidence": "on this synthetic smoke, predictive-t calibration can be compared directly with the same rows under the naive Gaussian-z interpretation",
            "not_evidence": "the KS statistic and rejection fractions are not formal population tests because theta rows share one sky and overlap spatially",
            "scientific_boundary": "this audit validates or falsifies calibration mechanics only; it says nothing about a real CMB anomaly, Pontifex/Torus causality, or downstream assembly/student performance",
            "production_rule": "do not interpret z_matched_null as a standard-normal z-score when null_maps is small; use predictive Student-t or a larger empirical null ensemble",
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    result = audit(load_rows(args.rows))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, allow_nan=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, allow_nan=True))


if __name__ == "__main__":
    main()
