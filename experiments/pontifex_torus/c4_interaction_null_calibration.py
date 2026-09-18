# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
# ]
# ///
"""Calibrate the tiny c4 interaction gain against an exchangeability null.

The preceding c4 learning curve found a very small positive held-out gain from
cross interactions at 560 paired families.  This experiment asks whether that gain
is distinguishable from the benefit that the same model-selection procedure can
obtain from an equally large but sample-misaligned interaction block.

For every outer split, the real interaction model and several null replicas use the
same linear features, targets, inner split, penalty grids, B-side atlas, and outer
held-out families.  A null replica independently permutes rows of the standardized
cross-feature block in outer-train and outer-test, preserving its marginal feature
distribution while destroying sample-specific A→B alignment.  Penalties are still
selected only on the inner split.  Repeated null scoring is calibration, not model
selection: no null result is used to tune the real model.

This is synthetic pairwise cartography only.  It never instantiates, tunes on, or
reads D_assembly, D_student, D_val, or D_test.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.preprocessing import StandardScaler

from c4_interaction_signal_curve import fit_candidate, rmse, select_candidate
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


def _selected_test(
    xtr: np.ndarray,
    ctr: np.ndarray,
    ytr: np.ndarray,
    xte: np.ndarray,
    cte: np.ndarray,
    yte: np.ndarray,
    *,
    linear_penalties: list[float],
    cross_penalties: list[float | None],
    selection_seed: int,
) -> tuple[dict, float]:
    best, _ = select_candidate(
        xtr,
        ctr,
        ytr,
        linear_penalties=linear_penalties,
        cross_penalties=cross_penalties,
        seed=selection_seed,
    )
    lp = float(best["linear_penalty"])
    cp_raw = best["cross_penalty"]
    cp = None if cp_raw is None else float(cp_raw)
    _, pred = fit_candidate(
        xtr,
        ctr,
        ytr,
        xte,
        cte,
        linear_penalty=lp,
        cross_penalty=cp,
    )
    return {
        "linear_penalty": lp,
        "cross_penalty": cp,
        "cross_off": cp is None,
        "inner_val_rmse": float(best["val_rmse"]),
    }, rmse(yte, pred)


def summarize(records: list[dict]) -> dict:
    real = np.asarray([r["real_gain_vs_linear"] for r in records], dtype=float)
    null_by_seed = [np.asarray(r["null_gains_vs_linear"], dtype=float) for r in records]
    null_pooled = np.concatenate(null_by_seed)
    null_means = np.asarray([float(np.mean(x)) for x in null_by_seed], dtype=float)
    paired = real - null_means
    null_ge_real = sum(
        int(np.sum(null >= real_gain))
        for null, real_gain in zip(null_by_seed, real, strict=True)
    )
    total_null = int(sum(len(x) for x in null_by_seed))
    return {
        "outer_splits": int(len(records)),
        "null_replicas_per_split": int(len(null_by_seed[0])) if null_by_seed else 0,
        "real_mean_gain_vs_linear": float(np.mean(real)),
        "real_median_gain_vs_linear": float(np.median(real)),
        "real_wins_vs_linear": int(np.sum(real > 0)),
        "real_cross_off_selections": int(sum(r["real_selection"]["cross_off"] for r in records)),
        "null_mean_gain_vs_linear": float(np.mean(null_pooled)),
        "null_median_gain_vs_linear": float(np.median(null_pooled)),
        "null_gain_std": float(np.std(null_pooled)),
        "null_positive_fraction": float(np.mean(null_pooled > 0)),
        "mean_real_minus_seed_null_mean": float(np.mean(paired)),
        "median_real_minus_seed_null_mean": float(np.median(paired)),
        "real_above_seed_null_mean_splits": int(np.sum(paired > 0)),
        "null_gain_ge_corresponding_real_fraction": float(null_ge_real / total_null),
        "splits_real_above_all_null_replicas": int(
            sum(real_gain > float(np.max(null)) for real_gain, null in zip(real, null_by_seed, strict=True))
        ),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--field-store", type=Path, required=True)
    ap.add_argument("--seeds", type=int, nargs="+", default=list(range(10)))
    ap.add_argument("--train-budget", type=int, default=560)
    ap.add_argument("--null-replicas", type=int, default=8)
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
        default=[1e3, 3e3, 1e4, 3e4, 1e5, 3e5, 1e6, 3e6, 1e7, 3e7, 1e8],
    )
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    d, ids, profiles = raw_size1_profiles(args.field_store)
    b_embed = d["original_b"].astype(float)
    n = len(ids)
    test_n = max(1, int(round(args.test_fraction * n)))
    max_train = n - test_n
    budget = int(args.train_budget)
    if budget > max_train:
        raise ValueError(f"train budget {budget} exceeds outer train pool {max_train}")
    if args.null_replicas < 1:
        raise ValueError("--null-replicas must be >= 1")

    dense_grid = np.linspace(0.0, 1.0, args.dense_train_grid, endpoint=False)
    basis = fourier_basis(dense_grid, args.harmonics)
    linear_penalties = [float(x) for x in args.linear_penalties]
    cross_candidates: list[float | None] = [float(x) for x in args.cross_penalties]
    cross_candidates.append(None)
    records: list[dict] = []

    for seed in args.seeds:
        rng = np.random.default_rng(seed)
        order = np.arange(n)
        rng.shuffle(order)
        test_idx = order[:test_n]
        train_pool = order[test_n:]
        train_idx = train_pool[:budget]

        # Match the preceding c4 curve exactly at budget=560: atlas comes only from
        # outer-train B embeddings, never from outer test.
        atlas_b = b_embed[train_pool]
        anchor_idx = farthest_anchors(atlas_b, min(args.anchors, len(atlas_b)))
        anchor_emb = normalize(atlas_b[anchor_idx])

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

        ytr = normalize(b_embed[train_idx]) @ anchor_emb.T
        yte = normalize(b_embed[test_idx]) @ anchor_emb.T
        selection_seed = int(seed + budget)

        linear_selection, linear_test = _selected_test(
            xtr,
            ctr,
            ytr,
            xte,
            cte,
            yte,
            linear_penalties=linear_penalties,
            cross_penalties=[None],
            selection_seed=selection_seed,
        )
        real_selection, real_test = _selected_test(
            xtr,
            ctr,
            ytr,
            xte,
            cte,
            yte,
            linear_penalties=linear_penalties,
            cross_penalties=cross_candidates,
            selection_seed=selection_seed,
        )

        null_rows: list[dict] = []
        for rep in range(args.null_replicas):
            null_rng = np.random.default_rng(8_841_173 + seed * 10_007 + rep)
            null_ctr = ctr[null_rng.permutation(len(ctr))]
            null_cte = cte[null_rng.permutation(len(cte))]
            null_selection, null_test = _selected_test(
                xtr,
                null_ctr,
                ytr,
                xte,
                null_cte,
                yte,
                linear_penalties=linear_penalties,
                cross_penalties=cross_candidates,
                selection_seed=selection_seed,
            )
            null_rows.append(
                {
                    "replica": int(rep),
                    "selection": null_selection,
                    "test_rmse": float(null_test),
                    "gain_vs_linear": float(linear_test - null_test),
                }
            )

        records.append(
            {
                "seed": int(seed),
                "train_families": budget,
                "test_families": int(len(test_idx)),
                "atlas_families": int(len(train_pool)),
                "atlas_anchors": int(len(anchor_emb)),
                "linear_selection": linear_selection,
                "linear_test_rmse": float(linear_test),
                "real_selection": real_selection,
                "real_test_rmse": float(real_test),
                "real_gain_vs_linear": float(linear_test - real_test),
                "null_gains_vs_linear": [float(r["gain_vs_linear"]) for r in null_rows],
                "null_mean_gain_vs_linear": float(
                    np.mean([r["gain_vs_linear"] for r in null_rows])
                ),
                "null_rows": null_rows,
            }
        )

    metadata: dict = {}
    if "metadata" in d:
        try:
            metadata = json.loads(str(d["metadata"].item()))
        except Exception:
            metadata = {"raw": str(d["metadata"].item())}

    result = {
        "experiment": "Pontifex c4 interaction exchangeability-null calibration",
        "field_store": str(args.field_store),
        "field_metadata": metadata,
        "outer_seeds": args.seeds,
        "train_budget": budget,
        "null_replicas_per_outer_split": int(args.null_replicas),
        "linear_penalty_grid": args.linear_penalties,
        "cross_penalty_grid": args.cross_penalties,
        "cross_off_candidate": True,
        "protocol": {
            "outer_split": "whole-family outer test disjoint from outer train; same split as c4 signal curve",
            "atlas": "B anchor dictionary from outer-train B embeddings only; no outer-test B embedding enters atlas",
            "real_selection": "linear and cross penalties selected only on an inner split of outer train",
            "null": "independent row permutations of standardized train and test cross-feature blocks destroy sample-specific cross alignment while preserving marginal cross-feature distributions",
            "null_selection": "each null replica runs the same inner-only penalty selection as the real interaction model",
            "null_outer_use": "outer test is repeatedly scored only to calibrate a predeclared exchangeability null; null scores do not tune the real model or any hyperparameter",
            "held_out_use": "real outer-test score is computed only after inner selection",
            "evidence_boundary": "synthetic pairwise c4 cartography only; no D_assembly/D_student/D_val/D_test data",
        },
        "summary": summarize(records),
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
