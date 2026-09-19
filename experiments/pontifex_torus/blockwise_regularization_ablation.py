# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
# ]
# ///
"""Test whether c3/c4 residual transport deficits are estimator-conditioning effects.

The previous clause-complexity diagnostic showed that widening a single Ridge alpha
removed most of the apparent c2-c4 sign reversal, but the degree-2 models still hit
the top of the scalar-alpha grid in c3/c4.  This follow-up separates two possible
causes without touching the outer held-out families:

1. feature-scale mismatch in the interaction block;
2. the need for different shrinkage on linear and cross-interaction coefficients.

For each paired clause regime and outer seed, compare:

- linear: standardized Fourier source features only;
- legacy_shared: linear + raw cross terms, one shared Ridge alpha;
- scaled_shared: linear + independently standardized cross terms, one shared alpha;
- blockwise: the same independently standardized blocks, but separate L2 penalties
  for the linear and cross blocks.

Hyperparameters are selected only inside the outer-training families.  The outer
held-out families are scored once after selection.  No Assembly/student/val/test
benchmark partition is instantiated or read; this is still synthetic pairwise
cartography.
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


def inner_split(n: int, seed: int, frac: float = 0.85) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed + 170_141)
    order = np.arange(n)
    rng.shuffle(order)
    cut = min(n - 1, max(8, int(frac * n)))
    return order[:cut], order[cut:]


def select_shared_alpha(
    x: np.ndarray,
    y: np.ndarray,
    alphas: list[float],
    seed: int,
) -> tuple[float, list[dict]]:
    fit_idx, val_idx = inner_split(len(x), seed)
    curve: list[dict] = []
    for alpha in alphas:
        model = Ridge(alpha=float(alpha)).fit(x[fit_idx], y[fit_idx])
        score = rmse(y[val_idx], model.predict(x[val_idx]))
        curve.append({"alpha": float(alpha), "val_rmse": score})
    best = min(curve, key=lambda row: row["val_rmse"])
    return float(best["alpha"]), curve


def block_design(
    linear: np.ndarray,
    cross: np.ndarray,
    linear_penalty: float,
    cross_penalty: float,
) -> np.ndarray:
    # Ridge(alpha=1) on rescaled columns is equivalent to a generalized diagonal
    # L2 penalty in the original block coordinates.
    return np.concatenate(
        [
            linear / np.sqrt(float(linear_penalty)),
            cross / np.sqrt(float(cross_penalty)),
        ],
        axis=1,
    )


def select_block_penalties(
    linear: np.ndarray,
    cross: np.ndarray,
    y: np.ndarray,
    penalties: list[float],
    seed: int,
) -> tuple[float, float, list[dict]]:
    fit_idx, val_idx = inner_split(len(linear), seed)
    curve: list[dict] = []
    for linear_penalty in penalties:
        for cross_penalty in penalties:
            x_fit = block_design(
                linear[fit_idx], cross[fit_idx], linear_penalty, cross_penalty
            )
            x_val = block_design(
                linear[val_idx], cross[val_idx], linear_penalty, cross_penalty
            )
            model = Ridge(alpha=1.0).fit(x_fit, y[fit_idx])
            score = rmse(y[val_idx], model.predict(x_val))
            curve.append(
                {
                    "linear_penalty": float(linear_penalty),
                    "cross_penalty": float(cross_penalty),
                    "val_rmse": score,
                }
            )
    best = min(curve, key=lambda row: row["val_rmse"])
    return (
        float(best["linear_penalty"]),
        float(best["cross_penalty"]),
        curve,
    )


def run_regime(
    *,
    corpus: str,
    store: Path,
    seeds: list[int],
    train_frac: float,
    dense_train_grid: int,
    harmonics: int,
    anchors: int,
    penalties: list[float],
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

        linear_scaler = StandardScaler().fit(train_full)
        xtr = linear_scaler.transform(train_full)
        xte = linear_scaler.transform(test_full)

        ii, jj = pair_indices(xtr.shape[1])
        ctr_raw = cross_matrix(xtr, ii, jj)
        cte_raw = cross_matrix(xte, ii, jj)
        cross_scaler = StandardScaler().fit(ctr_raw)
        ctr_scaled = cross_scaler.transform(ctr_raw)
        cte_scaled = cross_scaler.transform(cte_raw)

        anchor_idx = farthest_anchors(btr, anchors)
        anchor_emb = normalize(btr[anchor_idx])
        train_affin = normalize(btr) @ anchor_emb.T
        test_affin = normalize(bte) @ anchor_emb.T

        # Linear baseline.
        alpha, curve = select_shared_alpha(xtr, train_affin, penalties, seed)
        model = Ridge(alpha=alpha).fit(xtr, train_affin)
        records.append(
            {
                "corpus": corpus,
                "seed": int(seed),
                "method": "linear",
                "linear_penalty": alpha,
                "cross_penalty": None,
                "selected_on_boundary": bool(alpha in (penalties[0], penalties[-1])),
                "train_affinity_rmse": rmse(train_affin, model.predict(xtr)),
                "test_affinity_rmse": rmse(test_affin, model.predict(xte)),
                "selection_curve": curve,
            }
        )

        # Legacy degree-2 parameterization: raw cross block + one shared alpha.
        legacy_tr = np.concatenate([xtr, ctr_raw], axis=1)
        legacy_te = np.concatenate([xte, cte_raw], axis=1)
        alpha, curve = select_shared_alpha(legacy_tr, train_affin, penalties, seed)
        model = Ridge(alpha=alpha).fit(legacy_tr, train_affin)
        records.append(
            {
                "corpus": corpus,
                "seed": int(seed),
                "method": "legacy_shared",
                "linear_penalty": alpha,
                "cross_penalty": alpha,
                "selected_on_boundary": bool(alpha in (penalties[0], penalties[-1])),
                "train_affinity_rmse": rmse(train_affin, model.predict(legacy_tr)),
                "test_affinity_rmse": rmse(test_affin, model.predict(legacy_te)),
                "selection_curve": curve,
            }
        )

        # Same shared-alpha model after independently conditioning the cross block.
        scaled_tr = np.concatenate([xtr, ctr_scaled], axis=1)
        scaled_te = np.concatenate([xte, cte_scaled], axis=1)
        alpha, curve = select_shared_alpha(scaled_tr, train_affin, penalties, seed)
        model = Ridge(alpha=alpha).fit(scaled_tr, train_affin)
        records.append(
            {
                "corpus": corpus,
                "seed": int(seed),
                "method": "scaled_shared",
                "linear_penalty": alpha,
                "cross_penalty": alpha,
                "selected_on_boundary": bool(alpha in (penalties[0], penalties[-1])),
                "train_affinity_rmse": rmse(train_affin, model.predict(scaled_tr)),
                "test_affinity_rmse": rmse(test_affin, model.predict(scaled_te)),
                "selection_curve": curve,
            }
        )

        # Generalized Ridge with separately selected penalties for the two blocks.
        lp, cp, curve = select_block_penalties(
            xtr, ctr_scaled, train_affin, penalties, seed
        )
        block_tr = block_design(xtr, ctr_scaled, lp, cp)
        block_te = block_design(xte, cte_scaled, lp, cp)
        model = Ridge(alpha=1.0).fit(block_tr, train_affin)
        records.append(
            {
                "corpus": corpus,
                "seed": int(seed),
                "method": "blockwise",
                "linear_penalty": lp,
                "cross_penalty": cp,
                "selected_on_boundary": bool(
                    lp in (penalties[0], penalties[-1])
                    or cp in (penalties[0], penalties[-1])
                ),
                "train_affinity_rmse": rmse(train_affin, model.predict(block_tr)),
                "test_affinity_rmse": rmse(test_affin, model.predict(block_te)),
                "selection_curve": curve,
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
        rows = [r for r in records if r["corpus"] == corpus]
        methods = sorted({r["method"] for r in rows})
        linear_by_seed = {
            int(r["seed"]): r for r in rows if r["method"] == "linear"
        }
        block: dict[str, dict] = {}
        for method in methods:
            rs = [r for r in rows if r["method"] == method]
            test = np.asarray([r["test_affinity_rmse"] for r in rs], dtype=float)
            train = np.asarray([r["train_affinity_rmse"] for r in rs], dtype=float)
            gains = np.asarray(
                [
                    linear_by_seed[int(r["seed"])]["test_affinity_rmse"]
                    - r["test_affinity_rmse"]
                    for r in rs
                ],
                dtype=float,
            )
            block[method] = {
                "mean_train_affinity_rmse": float(np.mean(train)),
                "mean_test_affinity_rmse": float(np.mean(test)),
                "mean_test_gain_vs_linear": float(np.mean(gains)),
                "wins_vs_linear": int(np.sum(gains > 0)),
                "selected_linear_penalties": [float(r["linear_penalty"]) for r in rs],
                "selected_cross_penalties": [
                    None if r["cross_penalty"] is None else float(r["cross_penalty"])
                    for r in rs
                ],
                "boundary_selections": int(sum(bool(r["selected_on_boundary"]) for r in rs)),
            }
        out[corpus] = block
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
    ap.add_argument(
        "--penalties",
        type=float,
        nargs="+",
        default=[0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0, 100000.0, 1000000.0],
    )
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    names = ["c1", "c2", "c3", "c4", "repeat4"]
    records: list[dict] = []
    metadata: dict[str, dict] = {}
    for name in names:
        store = args.store_dir / (
            f"field-{name}-n{args.texts}-p{args.positions}-seed{args.field_seed}.npz"
        )
        rs, meta = run_regime(
            corpus=name,
            store=store,
            seeds=args.seeds,
            train_frac=args.train_frac,
            dense_train_grid=args.dense_train_grid,
            harmonics=args.harmonics,
            anchors=args.anchors,
            penalties=args.penalties,
        )
        records.extend(rs)
        metadata[name] = meta

    result = {
        "experiment": "Pontifex blockwise regularization ablation",
        "texts_per_regime": args.texts,
        "positions_per_text": args.positions,
        "field_seed": args.field_seed,
        "outer_seeds": args.seeds,
        "train_fraction": args.train_frac,
        "dense_train_grid": args.dense_train_grid,
        "harmonics": args.harmonics,
        "anchors_requested": args.anchors,
        "penalty_grid": args.penalties,
        "protocol": {
            "pairing": "same paired c1..c4/repeat4 field stores as the clause ladder",
            "outer_split": "whole-family 70/30 train/test split per seed",
            "selection": "all scalar or block penalties selected on an inner split of outer-training families only",
            "cross_scaling": "scaled_shared and blockwise fit StandardScaler on the outer-training cross block only",
            "blockwise_equivalence": "Ridge(alpha=1) on columns divided by sqrt(block penalty), yielding separate L2 penalties for linear and cross coefficients",
            "held_out_use": "outer held-out families are scored only after hyperparameter selection",
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
