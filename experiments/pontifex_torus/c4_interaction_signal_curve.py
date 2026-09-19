# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
# ]
# ///
"""Test whether c4 cross-interaction signal is absent or merely sample-limited.

This follow-up to the blockwise-regularization ablation keeps a fixed outer held-out
family set and varies only how many paired outer-training families are made
available.  For each nested training budget, linear and cross penalties are selected
strictly on an inner split.  The cross-penalty grid is fine on a logarithmic scale
and contains an explicit `cross=off` candidate, so the held-out comparison does not
infer "off" from an arbitrarily large finite penalty.

The B-side anchor atlas is built once from the full OUTER-TRAIN pool and then held
fixed across all nested paired-training budgets for that seed.  This isolates the
number of paired A→B transport examples from changes in the output coordinate
system.  It does mean the smaller-budget question is specifically "how many paired
examples are needed given a fixed B atlas?", not end-to-end data efficiency.

The outer held-out families are scored exactly once for the inner-selected model at
each training budget.  The complete penalty risk curves saved by the experiment are
INNER-validation curves; outer test is not used to choose a penalty.  This remains
synthetic pairwise cartography and never instantiates D_assembly, D_student, D_val,
or D_test.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

from quadratic_term_ablation import cross_matrix, pair_indices
from virtual_resolution import (
    build_dense_training,
    farthest_anchors,
    fourier_basis,
    functional_features,
    normalize,
    raw_size1_profiles,
    source_stats,
)


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def inner_split(n: int, seed: int, frac: float = 0.8) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed + 911_731)
    order = np.arange(n)
    rng.shuffle(order)
    cut = min(n - 1, max(8, int(frac * n)))
    return order[:cut], order[cut:]


def block_design(
    linear: np.ndarray,
    cross: np.ndarray,
    linear_penalty: float,
    cross_penalty: float | None,
) -> np.ndarray:
    linear_part = linear / np.sqrt(float(linear_penalty))
    if cross_penalty is None:
        return linear_part
    return np.concatenate(
        [linear_part, cross / np.sqrt(float(cross_penalty))], axis=1
    )


def fit_candidate(
    linear_fit: np.ndarray,
    cross_fit: np.ndarray,
    y_fit: np.ndarray,
    linear_eval: np.ndarray,
    cross_eval: np.ndarray,
    *,
    linear_penalty: float,
    cross_penalty: float | None,
) -> tuple[Ridge, np.ndarray]:
    x_fit = block_design(linear_fit, cross_fit, linear_penalty, cross_penalty)
    x_eval = block_design(linear_eval, cross_eval, linear_penalty, cross_penalty)
    model = Ridge(alpha=1.0).fit(x_fit, y_fit)
    return model, model.predict(x_eval)


def select_candidate(
    linear: np.ndarray,
    cross: np.ndarray,
    y: np.ndarray,
    *,
    linear_penalties: list[float],
    cross_penalties: list[float | None],
    seed: int,
) -> tuple[dict, list[dict]]:
    fit_idx, val_idx = inner_split(len(linear), seed)
    curve: list[dict] = []
    for cp in cross_penalties:
        for lp in linear_penalties:
            _, pred = fit_candidate(
                linear[fit_idx],
                cross[fit_idx],
                y[fit_idx],
                linear[val_idx],
                cross[val_idx],
                linear_penalty=lp,
                cross_penalty=cp,
            )
            curve.append(
                {
                    "linear_penalty": float(lp),
                    "cross_penalty": None if cp is None else float(cp),
                    "cross_off": cp is None,
                    "val_rmse": rmse(y[val_idx], pred),
                }
            )
    best = min(curve, key=lambda row: row["val_rmse"])
    return best, curve


def summarize(records: list[dict], budgets: list[int]) -> dict:
    out: dict[str, dict] = {}
    for budget in budgets:
        rows = [r for r in records if r["train_families"] == budget]
        gains = np.asarray([r["test_gain_vs_linear"] for r in rows], dtype=float)
        cps = [r["selected_cross_penalty"] for r in rows]
        contrib = np.asarray([r["cross_prediction_rms"] for r in rows], dtype=float)
        out[str(budget)] = {
            "mean_linear_test_rmse": float(
                np.mean([r["linear_test_rmse"] for r in rows])
            ),
            "mean_selected_test_rmse": float(
                np.mean([r["selected_test_rmse"] for r in rows])
            ),
            "mean_test_gain_vs_linear": float(np.mean(gains)),
            "median_test_gain_vs_linear": float(np.median(gains)),
            "wins_vs_linear": int(np.sum(gains > 0)),
            "cross_off_selections": int(sum(cp is None for cp in cps)),
            "finite_cross_selections": int(sum(cp is not None for cp in cps)),
            "selected_cross_penalties": cps,
            "mean_cross_prediction_rms": float(np.mean(contrib)),
        }
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--field-store", type=Path, required=True)
    ap.add_argument("--seeds", type=int, nargs="+", default=list(range(10)))
    ap.add_argument(
        "--train-budgets", type=int, nargs="+", default=[140, 280, 560]
    )
    ap.add_argument("--test-fraction", type=float, default=0.3)
    ap.add_argument("--dense-train-grid", type=int, default=512)
    ap.add_argument("--harmonics", type=int, default=8)
    ap.add_argument("--anchors", type=int, default=256)
    ap.add_argument(
        "--linear-penalties",
        type=float,
        nargs="+",
        default=[3.0, 10.0, 30.0, 100.0, 300.0, 1000.0],
    )
    ap.add_argument(
        "--cross-penalties",
        type=float,
        nargs="+",
        default=[
            1e3,
            3e3,
            1e4,
            3e4,
            1e5,
            3e5,
            1e6,
            3e6,
            1e7,
            3e7,
            1e8,
        ],
    )
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    d, ids, profiles = raw_size1_profiles(args.field_store)
    b_embed = d["original_b"].astype(float)
    n = len(ids)
    test_n = max(1, int(round(args.test_fraction * n)))
    max_train = n - test_n
    budgets = sorted(set(int(x) for x in args.train_budgets))
    if budgets[-1] > max_train:
        raise ValueError(
            f"largest train budget {budgets[-1]} exceeds outer train pool {max_train}"
        )

    dense_grid = np.linspace(0.0, 1.0, args.dense_train_grid, endpoint=False)
    basis = fourier_basis(dense_grid, args.harmonics)
    cross_candidates: list[float | None] = [float(x) for x in args.cross_penalties]
    cross_candidates.append(None)  # explicit nested cross=off model
    records: list[dict] = []

    for seed in args.seeds:
        rng = np.random.default_rng(seed)
        order = np.arange(n)
        rng.shuffle(order)
        test_idx = order[:test_n]
        train_pool = order[test_n:]

        # Fix the B coordinate system before varying the number of PAIRED examples.
        # The atlas uses B embeddings from outer-train only and never sees test_idx.
        atlas_b = b_embed[train_pool]
        anchor_idx = farthest_anchors(atlas_b, min(args.anchors, len(atlas_b)))
        anchor_emb = normalize(atlas_b[anchor_idx])

        # Nested budgets are deterministic prefixes of the SAME shuffled outer pool,
        # while test_idx and anchor_emb are fixed across budgets for this seed.
        for budget in budgets:
            train_idx = train_pool[:budget]
            btr, bte = b_embed[train_idx], b_embed[test_idx]

            train_dense = build_dense_training(profiles, train_idx, dense_grid)
            test_dense = build_dense_training(profiles, test_idx, dense_grid)
            mean_dense, scale_dense = source_stats(train_dense)
            train_full = functional_features(
                (train_dense - mean_dense[None, :]) / scale_dense[None, :], basis
            )
            test_full = functional_features(
                (test_dense - mean_dense[None, :]) / scale_dense[None, :], basis
            )

            linear_scaler = StandardScaler().fit(train_full)
            xtr = linear_scaler.transform(train_full)
            xte = linear_scaler.transform(test_full)
            ii, jj = pair_indices(xtr.shape[1])
            ctr_raw = cross_matrix(xtr, ii, jj)
            cte_raw = cross_matrix(xte, ii, jj)
            cross_scaler = StandardScaler().fit(ctr_raw)
            ctr = cross_scaler.transform(ctr_raw)
            cte = cross_scaler.transform(cte_raw)

            ytr = normalize(btr) @ anchor_emb.T
            yte = normalize(bte) @ anchor_emb.T

            # Baseline is selected on the same inner split but cannot use cross terms.
            linear_best, linear_curve = select_candidate(
                xtr,
                ctr,
                ytr,
                linear_penalties=[float(x) for x in args.linear_penalties],
                cross_penalties=[None],
                seed=seed + budget,
            )
            lp_linear = float(linear_best["linear_penalty"])
            _, linear_pred = fit_candidate(
                xtr,
                ctr,
                ytr,
                xte,
                cte,
                linear_penalty=lp_linear,
                cross_penalty=None,
            )
            linear_test = rmse(yte, linear_pred)

            best, risk_curve = select_candidate(
                xtr,
                ctr,
                ytr,
                linear_penalties=[float(x) for x in args.linear_penalties],
                cross_penalties=cross_candidates,
                seed=seed + budget,
            )
            lp = float(best["linear_penalty"])
            cp = best["cross_penalty"]
            cp = None if cp is None else float(cp)
            selected_model, selected_pred = fit_candidate(
                xtr,
                ctr,
                ytr,
                xte,
                cte,
                linear_penalty=lp,
                cross_penalty=cp,
            )
            selected_test = rmse(yte, selected_pred)

            if cp is None:
                cross_rms = 0.0
            else:
                xte_block = block_design(xte, cte, lp, cp)
                xte_no_cross = np.concatenate(
                    [xte / np.sqrt(lp), np.zeros_like(cte)], axis=1
                )
                pred_full = selected_model.predict(xte_block)
                pred_no_cross = selected_model.predict(xte_no_cross)
                cross_rms = float(np.sqrt(np.mean((pred_full - pred_no_cross) ** 2)))

            records.append(
                {
                    "seed": int(seed),
                    "train_families": int(budget),
                    "test_families": int(len(test_idx)),
                    "atlas_families": int(len(train_pool)),
                    "atlas_anchors": int(len(anchor_emb)),
                    "linear_penalty": lp_linear,
                    "linear_test_rmse": linear_test,
                    "selected_linear_penalty": lp,
                    "selected_cross_penalty": cp,
                    "selected_cross_off": cp is None,
                    "selected_inner_val_rmse": float(best["val_rmse"]),
                    "selected_test_rmse": selected_test,
                    "test_gain_vs_linear": linear_test - selected_test,
                    "cross_prediction_rms": cross_rms,
                    "linear_inner_curve": linear_curve,
                    "interaction_inner_risk_curve": risk_curve,
                }
            )

    metadata: dict = {}
    if "metadata" in d:
        try:
            metadata = json.loads(str(d["metadata"].item()))
        except Exception:
            metadata = {"raw": str(d["metadata"].item())}

    result = {
        "experiment": "Pontifex c4 interaction signal learning curve",
        "field_store": str(args.field_store),
        "field_metadata": metadata,
        "outer_seeds": args.seeds,
        "train_budgets": budgets,
        "fixed_test_fraction": args.test_fraction,
        "fixed_test_families_per_seed": test_n,
        "fixed_atlas_pool_families_per_seed": max_train,
        "linear_penalty_grid": args.linear_penalties,
        "cross_penalty_grid": args.cross_penalties,
        "cross_off_candidate": True,
        "protocol": {
            "outer_split": "fixed whole-family test set per seed; nested prefixes of the disjoint outer-training pool form the paired-example learning curve",
            "atlas": "B anchor dictionary is built once from the full outer-training pool and held fixed across budgets; no outer-test B embeddings enter the atlas",
            "estimand": "paired A→B transport sample efficiency conditional on a fixed B atlas, not end-to-end atlas construction sample efficiency",
            "selection": "linear and cross penalties selected only on an inner split of the current paired outer-training budget",
            "risk_curve": "saved risk curves contain inner-validation RMSE only; outer test is not scanned to choose penalties",
            "held_out_use": "for each seed and budget, outer held-out families are scored once after inner selection",
            "cross_off": "explicit nested model with no cross features, not a finite-penalty approximation",
            "evidence_boundary": "synthetic pairwise c4 cartography only; no D_assembly/D_student/D_val/D_test data",
        },
        "summary": summarize(records, budgets),
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
