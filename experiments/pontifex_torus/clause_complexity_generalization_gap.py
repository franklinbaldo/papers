# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
# ]
# ///
"""Diagnose whether the clause-complexity sign flip is an overfitting effect.

This is a follow-up to clause_complexity_ladder.py.  It keeps exactly the same
paired corpora, outer family splits, acquisition budget, Fourier representation,
anchor construction, and train-only alpha selection, but records both final
outer-train and held-out affinity RMSE for linear, all-cross, and full degree-2
transport.

The discriminant is intentionally narrow:

* train gain > 0 and test gain < 0 is direct evidence of a variance/overfitting
  signature under this protocol;
* train gain <= 0 and test gain < 0 would instead indicate that the richer basis
  fails even to fit the outer training relation better under selected regularization.

No reserved Assembly/student/val/test partition is instantiated or read.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

from quadratic_term_ablation import choose_alpha, cross_matrix, pair_indices
from virtual_resolution import (
    build_dense_training,
    farthest_anchors,
    fourier_basis,
    functional_features,
    normalize,
    raw_size1_profiles,
    source_stats,
)

METHODS = ("linear", "all_cross", "full_degree2")


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def features_for(method: str, x: np.ndarray, cross: np.ndarray) -> np.ndarray:
    if method == "linear":
        return x
    if method == "all_cross":
        return np.concatenate([x, cross], axis=1)
    if method == "full_degree2":
        return np.concatenate([x, x * x, cross], axis=1)
    raise ValueError(method)


def run_regime(
    *,
    corpus: str,
    store: Path,
    seeds: list[int],
    train_frac: float,
    dense_train_grid: int,
    harmonics: int,
    anchors: int,
    alphas: list[float],
) -> tuple[list[dict], dict]:
    d, ids, profiles = raw_size1_profiles(store)
    b_embed = d["original_b"].astype(float)
    dense_grid = np.linspace(0.0, 1.0, dense_train_grid, endpoint=False)
    basis = fourier_basis(dense_grid, harmonics)
    records: list[dict] = []

    for seed in seeds:
        rng = np.random.default_rng(seed)
        order = np.arange(len(ids))
        rng.shuffle(order)
        cut = max(4, int(train_frac * len(order)))
        tr, te = order[:cut], order[cut:]
        btr, bte = b_embed[tr], b_embed[te]

        train_dense = build_dense_training(profiles, tr, dense_grid)
        test_dense = build_dense_training(profiles, te, dense_grid)
        mean_dense, scale_dense = source_stats(train_dense)
        train_full = functional_features(
            (train_dense - mean_dense[None, :]) / scale_dense[None, :], basis
        )
        test_full = functional_features(
            (test_dense - mean_dense[None, :]) / scale_dense[None, :], basis
        )

        scaler = StandardScaler().fit(train_full)
        xtr = scaler.transform(train_full)
        xte = scaler.transform(test_full)

        anchor_idx = farthest_anchors(btr, anchors)
        anchor_emb = normalize(btr[anchor_idx])
        train_affin = normalize(btr) @ anchor_emb.T
        test_affin = normalize(bte) @ anchor_emb.T

        ii, jj = pair_indices(xtr.shape[1])
        ctr = cross_matrix(xtr, ii, jj)
        cte = cross_matrix(xte, ii, jj)

        for method in METHODS:
            ftr = features_for(method, xtr, ctr)
            fte = features_for(method, xte, cte)
            alpha = choose_alpha(ftr, train_affin, alphas, seed)
            model = Ridge(alpha=alpha).fit(ftr, train_affin)
            train_error = rmse(train_affin, model.predict(ftr))
            test_error = rmse(test_affin, model.predict(fte))
            records.append(
                {
                    "corpus": corpus,
                    "seed": int(seed),
                    "method": method,
                    "selected_alpha": float(alpha),
                    "feature_dim": int(ftr.shape[1]),
                    "train_affinity_rmse": train_error,
                    "test_affinity_rmse": test_error,
                    "generalization_gap": float(test_error - train_error),
                }
            )

    metadata: dict = {}
    if "metadata" in d:
        try:
            metadata = json.loads(str(d["metadata"].item()))
        except Exception:
            metadata = {"raw": str(d["metadata"].item())}
    return records, metadata


def summarize(records: list[dict], names: list[str]) -> dict:
    out: dict[str, dict] = {}
    for corpus in names:
        per_seed: list[dict] = []
        seeds = sorted({int(r["seed"]) for r in records if r["corpus"] == corpus})
        for seed in seeds:
            rows = {
                r["method"]: r
                for r in records
                if r["corpus"] == corpus and int(r["seed"]) == seed
            }
            linear = rows["linear"]
            entry: dict[str, object] = {
                "seed": seed,
                "linear_train_rmse": linear["train_affinity_rmse"],
                "linear_test_rmse": linear["test_affinity_rmse"],
                "linear_generalization_gap": linear["generalization_gap"],
            }
            for method in ("all_cross", "full_degree2"):
                row = rows[method]
                train_gain = float(linear["train_affinity_rmse"] - row["train_affinity_rmse"])
                test_gain = float(linear["test_affinity_rmse"] - row["test_affinity_rmse"])
                entry[f"{method}_train_rmse"] = row["train_affinity_rmse"]
                entry[f"{method}_test_rmse"] = row["test_affinity_rmse"]
                entry[f"{method}_generalization_gap"] = row["generalization_gap"]
                entry[f"{method}_train_gain_vs_linear"] = train_gain
                entry[f"{method}_test_gain_vs_linear"] = test_gain
                entry[f"{method}_overfit_signature"] = bool(train_gain > 0 and test_gain < 0)
            per_seed.append(entry)

        numeric_keys = [
            k
            for k, v in per_seed[0].items()
            if k != "seed" and not isinstance(v, bool)
        ]
        means = {
            key: float(np.mean([float(row[key]) for row in per_seed]))
            for key in numeric_keys
        }
        out[corpus] = {
            "per_seed": per_seed,
            "means": means,
            "overfit_signature_seeds": {
                method: int(sum(bool(row[f"{method}_overfit_signature"]) for row in per_seed))
                for method in ("all_cross", "full_degree2")
            },
            "total_seeds": len(per_seed),
        }
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--store-dir", type=Path, required=True)
    ap.add_argument("--texts", type=int, default=800)
    ap.add_argument("--positions", type=int, default=8)
    ap.add_argument("--field-seed", type=int, default=20260918)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    ap.add_argument("--train-frac", type=float, default=0.7)
    ap.add_argument("--dense-train-grid", type=int, default=512)
    ap.add_argument("--harmonics", type=int, default=8)
    ap.add_argument("--anchors", type=int, default=256)
    ap.add_argument("--alphas", type=float, nargs="+", default=[0.1, 1.0, 10.0])
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    names = ["c1", "c2", "c3", "c4", "repeat4"]
    records: list[dict] = []
    metadata: dict[str, dict] = {}
    for name in names:
        store = args.store_dir / f"field-{name}-n{args.texts}-p{args.positions}-seed{args.field_seed}.npz"
        rs, meta = run_regime(
            corpus=name,
            store=store,
            seeds=args.seeds,
            train_frac=args.train_frac,
            dense_train_grid=args.dense_train_grid,
            harmonics=args.harmonics,
            anchors=args.anchors,
            alphas=args.alphas,
        )
        records.extend(rs)
        metadata[name] = meta

    result = {
        "experiment": "Pontifex clause-complexity train-vs-held-out generalization gap",
        "texts_per_regime": args.texts,
        "positions_per_text": args.positions,
        "field_seed": args.field_seed,
        "outer_seeds": args.seeds,
        "train_fraction": args.train_frac,
        "dense_train_grid": args.dense_train_grid,
        "harmonics": args.harmonics,
        "anchors_requested": args.anchors,
        "protocol": {
            "pairing": "same paired c1..c4/repeat4 field stores as clause_complexity_ladder.py",
            "selection": "Ridge alpha selected only inside outer training families",
            "reported_train_error": "final model in-sample RMSE on the full outer-training families after alpha selection",
            "reported_test_error": "held-out RMSE on untouched outer-test families",
            "overfit_signature": "richer model improves final train RMSE over linear but worsens held-out RMSE",
            "evidence_boundary": "synthetic pairwise cartography only; no D_assembly/D_student/D_val/D_test data",
        },
        "corpus_metadata": metadata,
        "summary": summarize(records, names),
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
