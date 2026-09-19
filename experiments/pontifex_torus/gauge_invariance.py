# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
# ]
# ///
"""Coordinate-gauge invariance test for Pontifex Torus.

The previous seam-rotation experiment cyclically reordered the *raw text*, so any
change mixed two effects: a different semantic sequence and a different circular
seam. This experiment isolates the coordinate question. The response field is kept
fixed and only the arbitrary phase origin used to label intervention positions is
changed.

A representation intended to be toroidal should not change its held-out prediction
merely because theta=0 is declared at another point on the circle. The current
Fourier basis uses complete sin/cos pairs, so changing phase should amount to an
orthogonal change of basis. With isotropic Ridge regularization its predictions
should therefore be gauge-invariant up to numerical precision.

Controls:
- position_agnostic: invariant by construction but cannot exploit position;
- raw_seam_polynomial: uses modulo raw coordinates and should expose sensitivity to
  where the arbitrary seam is placed.

This is an architectural/mechanistic test on the synthetic cartography field. It is
not evidence that natural-language semantics are intrinsically circular and it does
not consume assembly/student/validation/downstream-test data.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error

from alignment_benchmark import load_profiles, row_neighbor_overlap


def rmse(a, b) -> float:
    return float(mean_squared_error(np.asarray(a).ravel(), np.asarray(b).ravel()) ** 0.5)


def summarize(values):
    x = np.asarray(values, dtype=float)
    return {
        "mean": float(np.mean(x)),
        "median": float(np.median(x)),
        "std": float(np.std(x, ddof=1)) if len(x) > 1 else 0.0,
        "max": float(np.max(x)),
    }


def row_features(keys, profile, phase_turns: float, basis: str) -> np.ndarray:
    rows = []
    for (pos, size), av in zip(keys, profile):
        l = math.log2(size)
        if basis == "position_agnostic":
            row = [av, l, l * l, av * l]
        elif basis == "torus_fourier":
            theta = 2.0 * math.pi * (pos + phase_turns)
            row = [
                av,
                math.sin(theta),
                math.cos(theta),
                l,
                l * l,
                av * math.sin(theta),
                av * math.cos(theta),
                av * l,
                math.sin(2.0 * theta),
                math.cos(2.0 * theta),
            ]
        elif basis == "raw_seam_polynomial":
            # Deliberately non-periodic coordinate control. Moving the gauge origin
            # changes where p wraps from nearly 1 back to 0.
            p = (pos + phase_turns) % 1.0
            row = [
                av,
                p,
                p * p,
                l,
                l * l,
                av * p,
                av * l,
                p * l,
                p * p * p,
                av * p * p,
            ]
        else:
            raise ValueError(f"unknown basis: {basis}")
        rows.append(row)
    return np.asarray(rows, dtype=float)


def fit_predict(keys, xtr, ytr, xte, phase_turns: float, basis: str) -> np.ndarray:
    tr = [row_features(keys, x, phase_turns, basis) for x in xtr]
    te = [row_features(keys, x, phase_turns, basis) for x in xte]
    model = Ridge(alpha=1.0).fit(np.concatenate(tr, axis=0), ytr.reshape(-1))
    return np.stack([model.predict(z) for z in te])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--field-store", type=Path, required=True)
    ap.add_argument("--seeds", type=int, nargs="+", default=list(range(10)))
    ap.add_argument(
        "--phase-turns",
        type=float,
        nargs="+",
        default=[0.0, 0.125, 0.25, 0.5, 0.75],
    )
    ap.add_argument("--train-frac", type=float, default=0.7)
    ap.add_argument("--output", type=Path, default=Path("pontifex-gauge-invariance.json"))
    args = ap.parse_args()

    ids, keys, xa, yb = load_profiles(args.field_store)
    bases = ["position_agnostic", "torus_fourier", "raw_seam_polynomial"]
    records = []

    for seed in args.seeds:
        rng = np.random.default_rng(seed)
        order = np.arange(len(ids))
        rng.shuffle(order)
        cut = max(2, int(args.train_frac * len(order)))
        tr, te = order[:cut], order[cut:]
        xtr, ytr, xte, yte = xa[tr], yb[tr], xa[te], yb[te]
        target_scale = max(float(np.std(yte)), 1e-12)

        for basis in bases:
            baseline = fit_predict(keys, xtr, ytr, xte, 0.0, basis)
            for phase in args.phase_turns:
                pred = fit_predict(keys, xtr, ytr, xte, float(phase), basis)
                drift = rmse(baseline, pred)
                records.append(
                    {
                        "seed": int(seed),
                        "basis": basis,
                        "phase_turns": float(phase),
                        "heldout_rmse": rmse(yte, pred),
                        "neighbor_overlap": row_neighbor_overlap(yte, pred),
                        "prediction_drift_rmse": drift,
                        "prediction_drift_nrmse": float(drift / target_scale),
                        "prediction_max_abs_drift": float(np.max(np.abs(baseline - pred))),
                    }
                )

    summary = {}
    nonzero_phases = {float(p) for p in args.phase_turns if abs(float(p)) > 1e-12}
    for basis in bases:
        rows = [
            r
            for r in records
            if r["basis"] == basis and r["phase_turns"] in nonzero_phases
        ]
        task_rows = [r for r in records if r["basis"] == basis]
        summary[basis] = {
            "prediction_drift_rmse_nonzero_phase": summarize(
                [r["prediction_drift_rmse"] for r in rows]
            ),
            "prediction_drift_nrmse_nonzero_phase": summarize(
                [r["prediction_drift_nrmse"] for r in rows]
            ),
            "prediction_max_abs_drift_nonzero_phase": summarize(
                [r["prediction_max_abs_drift"] for r in rows]
            ),
            "heldout_rmse_all_phases": summarize([r["heldout_rmse"] for r in task_rows]),
            "neighbor_overlap_all_phases": summarize(
                [r["neighbor_overlap"] for r in task_rows]
            ),
        }

    # Phase-wise aggregate makes any privileged origin visible rather than hiding it
    # inside one pooled statistic.
    by_phase = {}
    for basis in bases:
        by_phase[basis] = {}
        for phase in args.phase_turns:
            rows = [
                r
                for r in records
                if r["basis"] == basis and r["phase_turns"] == float(phase)
            ]
            by_phase[basis][str(float(phase))] = {
                "heldout_rmse": summarize([r["heldout_rmse"] for r in rows]),
                "neighbor_overlap": summarize([r["neighbor_overlap"] for r in rows]),
                "prediction_drift_rmse": summarize(
                    [r["prediction_drift_rmse"] for r in rows]
                ),
            }

    result = {
        "experiment": "Pontifex coordinate-gauge invariance",
        "texts": int(len(ids)),
        "profile_dimensions": int(len(keys)),
        "seeds": args.seeds,
        "phase_turns": args.phase_turns,
        "train_fraction": args.train_frac,
        "records": records,
        "summary": summary,
        "by_phase": by_phase,
        "interpretation_contract": {
            "gauge_change": "changes only the arbitrary phase origin used to label the same fixed response field; raw text and response values are unchanged",
            "positive_test": "a toroidal representation should keep predictions invariant, up to numerical error, when train and held-out coordinates are relabeled by the same phase shift",
            "raw_control": "a modulo raw-position polynomial has an arbitrary discontinuity at its chosen seam and is expected to change when that seam is moved",
            "agnostic_control": "position-agnostic features are invariant by construction, showing that invariance alone is not evidence of useful geometry",
            "scope": "this validates a coordinate property of the representation, not circular semantics of language and not downstream benchmark performance",
            "data_boundary": "synthetic cartography response field only; no assembly/student/validation/downstream-test partition is consumed",
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
