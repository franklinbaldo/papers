# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scipy>=1.14",
# ]
# ///
"""Second-stage localization of CMB matched-null calibration error.

Consumes the persisted per-theta score vectors from
``cmb_null_family_localization.py`` and decomposes the residual predictive-t
versus exact-rank mismatch by geometry x occlusion cell.  No new sky or theta
is generated here: this is a preregisterable second-stage read of the fixed,
balanced panel already produced by the upstream experiment.

The unit of independent replication remains the synthetic sky.  Cell counts
and rejection fractions are descriptive diagnostics, not independent
population-level hypothesis tests.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import kurtosis, skew, t

ALPHA = 0.01
NULL_COUNT = 128


def leave_one_out_t(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    _, k = x.shape
    m = k - 1
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


def summarize(values: list[float]) -> dict[str, float | int]:
    x = np.asarray(values, dtype=float)
    x = x[np.isfinite(x)]
    if not x.size:
        return {
            "n": 0,
            "mean": float("nan"),
            "median": float("nan"),
            "min": float("nan"),
            "max": float("nan"),
        }
    return {
        "n": int(x.size),
        "mean": float(np.mean(x)),
        "median": float(np.median(x)),
        "min": float(np.min(x)),
        "max": float(np.max(x)),
    }


def load_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def calibrate(row: dict) -> dict | None:
    null = np.asarray(row["null_scores"][:NULL_COUNT], dtype=float)
    if null.size != NULL_COUNT:
        raise ValueError(
            f"expected at least {NULL_COUNT} null scores, got {null.size}"
        )
    observed = float(row["observed_score"])
    sd = float(np.std(null, ddof=1))
    if not np.isfinite(sd) or sd <= 1e-15:
        return None

    z_like = (observed - float(np.mean(null))) / sd
    t_pred = z_like / np.sqrt(1.0 + 1.0 / NULL_COUNT)
    p_t = float(2.0 * t.sf(abs(t_pred), df=NULL_COUNT - 1))
    joint = np.concatenate(([observed], null))[None, :]
    loo = leave_one_out_t(joint)[0]
    p_rank = float(np.mean(np.abs(loo) >= abs(loo[0])))
    return {
        "sky_id": int(row["sky_id"]),
        "geometry": str(row["geometry"]),
        "occlusion": str(row["occlusion"]),
        "predictive_p": p_t,
        "rank_p": p_rank,
        "null_skew": float(skew(null, bias=False)),
        "null_excess_kurtosis": float(kurtosis(null, fisher=True, bias=False)),
    }


def cell_summary(rows: list[dict]) -> dict:
    pt = np.asarray([r["predictive_p"] for r in rows], dtype=float)
    pr = np.asarray([r["rank_p"] for r in rows], dtype=float)
    pred = pt <= ALPHA
    rank = pr <= ALPHA

    by_sky: dict[int, list[dict]] = defaultdict(list)
    for row in rows:
        by_sky[int(row["sky_id"])].append(row)

    sky_diffs: list[float] = []
    sky_disagreements: list[float] = []
    for sky_rows in by_sky.values():
        spt = np.asarray([r["predictive_p"] for r in sky_rows], dtype=float)
        spr = np.asarray([r["rank_p"] for r in sky_rows], dtype=float)
        spred = spt <= ALPHA
        srank = spr <= ALPHA
        sky_diffs.append(float(np.mean(spred) - np.mean(srank)))
        sky_disagreements.append(float(np.mean(spred != srank)))

    return {
        "rows": len(rows),
        "predictive_t_rejection": float(np.mean(pred)),
        "exact_rank_rejection": float(np.mean(rank)),
        "rate_difference_predictive_minus_rank": float(np.mean(pred) - np.mean(rank)),
        "decision_disagreement": float(np.mean(pred != rank)),
        "sky_blocked": {
            "independent_skies": len(by_sky),
            "rate_difference_by_sky": summarize(sky_diffs),
            "decision_disagreement_by_sky": summarize(sky_disagreements),
            "positive_difference_skies": int(sum(x > 0 for x in sky_diffs)),
            "zero_difference_skies": int(sum(x == 0 for x in sky_diffs)),
            "negative_difference_skies": int(sum(x < 0 for x in sky_diffs)),
        },
        "null_score_shape": {
            "skew": summarize([r["null_skew"] for r in rows]),
            "excess_kurtosis": summarize(
                [r["null_excess_kurtosis"] for r in rows]
            ),
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    source = load_rows(args.scores)
    calibrated = []
    zero_variance = 0
    for row in source:
        item = calibrate(row)
        if item is None:
            zero_variance += 1
        else:
            calibrated.append(item)

    cells: dict[str, dict] = {}
    keys = sorted({(r["geometry"], r["occlusion"]) for r in calibrated})
    for geometry, occlusion in keys:
        rows = [
            r
            for r in calibrated
            if r["geometry"] == geometry and r["occlusion"] == occlusion
        ]
        cells[f"{geometry}::{occlusion}"] = cell_summary(rows)

    overall = cell_summary(calibrated)
    cell_diffs = {
        key: float(
            value["sky_blocked"]["rate_difference_by_sky"]["mean"]
        )
        for key, value in cells.items()
    }
    nonzero = {key: value for key, value in cell_diffs.items() if value != 0.0}

    result = {
        "experiment": "Pontifex CMB geometry x occlusion null-calibration localization",
        "source_rows": len(source),
        "finite_rows": len(calibrated),
        "zero_variance_rows": zero_variance,
        "null_maps": NULL_COUNT,
        "rank_resolution": 1.0 / (NULL_COUNT + 1),
        "alpha": ALPHA,
        "overall": overall,
        "by_geometry_occlusion": cells,
        "localization": {
            "mean_predictive_minus_rank_rate_by_sky": cell_diffs,
            "nonzero_cells": nonzero,
            "nonzero_cell_count": len(nonzero),
            "total_cell_count": len(cells),
        },
        "interpretation_contract": {
            "evidence": (
                "the same fixed balanced theta panel is decomposed into geometry x occlusion "
                "cells, so any observed localization is conditional on the already-run "
                "synthetic experiment rather than on a post-hoc resampling of theta"
            ),
            "negative_result_rule": (
                "if cell-level predictive-minus-rank differences are sparse and appear in "
                "only one of twelve independent skies per affected cell, the data do not "
                "support a stable geometry x occlusion mechanism"
            ),
            "hypothesis": (
                "stable recurrence of the same signed gap across independent skies would "
                "motivate a mechanistic cell-specific follow-up"
            ),
            "not_evidence": (
                "this synthetic localization is not evidence of a real CMB anomaly, physical "
                "topology, or Torus causality"
            ),
            "data_boundary": (
                "no assembly, student, validation, or test data are used; their strict "
                "separation is unchanged"
            ),
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
