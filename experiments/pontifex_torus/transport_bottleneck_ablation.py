# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
# ]
# ///
"""Discriminate sparse-observation shift from response-field information loss.

The regional-decoder ablation showed that true B-anchor affinities contain abundant
information, while predicted affinities from the sparse A response field are the
remaining bottleneck. This experiment asks *why* that transport is weak.

It separates three candidate causes:

1. train/inference mismatch: the current transport is trained on complete A response
   functions but evaluated on functions reconstructed from only K held-out probes;
2. observation loss: even a matched-sparse learner may simply need more A probes;
3. representation loss: the scalar A occlusion-response field may discard semantic
   information that remains present in the original A embedding.

For each whole-text split and K, we compare:

- dense-trained transport -> sparse held-out inference (current protocol);
- matched-sparse-trained transport -> the same sparse held-out inference;
- dense-trained transport -> full held-out A response profile (observation upper bound);
- original A embedding -> B-anchor affinities (representation upper bound).

All predicted affinities use the same learned affine affinity->B readout established
by the previous diagnostic. Direct source->B Ridge controls are reported for the same
source representations. Oracle B affinities remain diagnostic only.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import Ridge

from virtual_resolution import (
    build_dense_training,
    evaluate,
    farthest_anchors,
    fourier_basis,
    functional_features,
    infer_features,
    normalize,
    raw_size1_profiles,
    source_stats,
)


def affinity_metrics(true: np.ndarray, pred: np.ndarray, topk: int = 10) -> dict:
    diff = np.asarray(pred, dtype=float) - np.asarray(true, dtype=float)
    rmse = float(np.sqrt(np.mean(diff * diff)))

    t = np.asarray(true, dtype=float).ravel()
    p = np.asarray(pred, dtype=float).ravel()
    if np.std(t) > 1e-12 and np.std(p) > 1e-12:
        flat_pearson = float(np.corrcoef(t, p)[0, 1])
    else:
        flat_pearson = float("nan")

    row_corr = []
    overlaps = []
    k = min(int(topk), true.shape[1])
    for a, b in zip(true, pred):
        if np.std(a) > 1e-12 and np.std(b) > 1e-12:
            row_corr.append(float(np.corrcoef(a, b)[0, 1]))
        ia = set(np.argpartition(a, -k)[-k:].tolist())
        ib = set(np.argpartition(b, -k)[-k:].tolist())
        overlaps.append(len(ia & ib) / max(1, k))

    return {
        "affinity_rmse": rmse,
        "affinity_flat_pearson": flat_pearson,
        "affinity_row_pearson_mean": float(np.mean(row_corr)) if row_corr else float("nan"),
        "affinity_topk_overlap": float(np.mean(overlaps)),
    }


def summarize(records: list[dict]) -> dict:
    metrics = (
        "affinity_rmse",
        "affinity_flat_pearson",
        "affinity_row_pearson_mean",
        "affinity_topk_overlap",
        "cosine_similarity",
        "normalized_rmse",
        "retrieval_top1",
        "neighbor_overlap",
    )
    groups = sorted(set((r["method"], r["real_probe_budget_requested"]) for r in records))
    out = {}
    for method, k in groups:
        rs = [
            r for r in records
            if r["method"] == method and r["real_probe_budget_requested"] == k
        ]
        block = {
            "real_probe_count_train_mean": float(np.mean([r["real_probe_count_train_mean"] for r in rs])),
            "real_probe_count_test_mean": float(np.mean([r["real_probe_count_test_mean"] for r in rs])),
            "source_feature_shift_rmse": float(np.mean([r["source_feature_shift_rmse"] for r in rs])),
        }
        for metric in metrics:
            vals = np.asarray([r[metric] for r in rs], dtype=float)
            finite = vals[np.isfinite(vals)]
            block[metric] = {
                "mean": float(np.mean(finite)) if len(finite) else float("nan"),
                "median": float(np.median(finite)) if len(finite) else float("nan"),
                "std": float(np.std(finite, ddof=1)) if len(finite) > 1 else 0.0,
            }
        out[f"{method}|K={k}"] = block
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--field-store", type=Path, required=True)
    ap.add_argument("--seeds", type=int, nargs="+", default=list(range(10)))
    ap.add_argument("--train-frac", type=float, default=0.7)
    ap.add_argument("--real-probes", type=int, nargs="+", default=[2, 4, 8, 16])
    ap.add_argument("--virtual-steps", type=int, default=128)
    ap.add_argument("--dense-train-grid", type=int, default=512)
    ap.add_argument("--harmonics", type=int, default=8)
    ap.add_argument("--anchors", type=int, default=256)
    ap.add_argument("--ridge-alpha", type=float, default=1.0)
    ap.add_argument("--output", type=Path, default=Path("pontifex-transport-bottleneck.json"))
    args = ap.parse_args()

    d, ids, profiles = raw_size1_profiles(args.field_store)
    a_embed = d["original_a"].astype(float)
    b_embed = d["original_b"].astype(float)
    a_embed_n = normalize(a_embed)
    dense_grid = np.linspace(0.0, 1.0, args.dense_train_grid, endpoint=False)
    basis = fourier_basis(dense_grid, args.harmonics)
    records: list[dict] = []

    for seed in args.seeds:
        rng = np.random.default_rng(seed)
        order = np.arange(len(ids))
        rng.shuffle(order)
        cut = max(4, int(args.train_frac * len(order)))
        tr, te = order[:cut], order[cut:]
        btr, bte = b_embed[tr], b_embed[te]

        train_dense = build_dense_training(profiles, tr, dense_grid)
        test_dense = build_dense_training(profiles, te, dense_grid)
        mean_dense, scale_dense = source_stats(train_dense)
        train_full_feats = functional_features(
            (train_dense - mean_dense[None, :]) / scale_dense[None, :], basis
        )
        test_full_feats = functional_features(
            (test_dense - mean_dense[None, :]) / scale_dense[None, :], basis
        )
        state = {"mean_dense": mean_dense, "scale_dense": scale_dense}

        anchor_idx = farthest_anchors(btr, args.anchors)
        anchor_emb = normalize(btr[anchor_idx])
        train_affin = normalize(btr) @ anchor_emb.T
        true_test_affin = normalize(bte) @ anchor_emb.T

        affinity_decoder = Ridge(alpha=args.ridge_alpha).fit(train_affin, btr)
        dense_affinity_model = Ridge(alpha=args.ridge_alpha).fit(train_full_feats, train_affin)
        dense_direct_model = Ridge(alpha=args.ridge_alpha).fit(train_full_feats, btr)
        original_a_affinity_model = Ridge(alpha=args.ridge_alpha).fit(a_embed_n[tr], train_affin)
        original_a_direct_model = Ridge(alpha=args.ridge_alpha).fit(a_embed_n[tr], btr)

        pred_orig_affin = original_a_affinity_model.predict(a_embed_n[te])
        pred_orig_b_via_affin = affinity_decoder.predict(pred_orig_affin)
        pred_orig_b_direct = original_a_direct_model.predict(a_embed_n[te])
        orig_aff_metrics = affinity_metrics(true_test_affin, pred_orig_affin)

        for k_real in args.real_probes:
            train_sparse_feats, train_counts = infer_features(
                profiles,
                tr,
                k_real,
                args.virtual_steps,
                dense_grid,
                state,
                args.harmonics,
            )
            test_sparse_feats, test_counts = infer_features(
                profiles,
                te,
                k_real,
                args.virtual_steps,
                dense_grid,
                state,
                args.harmonics,
            )

            matched_affinity_model = Ridge(alpha=args.ridge_alpha).fit(
                train_sparse_feats, train_affin
            )
            matched_direct_model = Ridge(alpha=args.ridge_alpha).fit(
                train_sparse_feats, btr
            )

            pred_current_affin = dense_affinity_model.predict(test_sparse_feats)
            pred_matched_affin = matched_affinity_model.predict(test_sparse_feats)
            pred_full_affin = dense_affinity_model.predict(test_full_feats)

            source_shift = float(np.sqrt(np.mean((test_sparse_feats - test_full_feats) ** 2)))
            train_count = float(np.mean(train_counts))
            test_count = float(np.mean(test_counts))

            methods = [
                (
                    "dense_trained_to_sparse_affinity",
                    pred_current_affin,
                    affinity_decoder.predict(pred_current_affin),
                    affinity_metrics(true_test_affin, pred_current_affin),
                ),
                (
                    "matched_sparse_to_sparse_affinity",
                    pred_matched_affin,
                    affinity_decoder.predict(pred_matched_affin),
                    affinity_metrics(true_test_affin, pred_matched_affin),
                ),
                (
                    "dense_trained_to_full_response_affinity",
                    pred_full_affin,
                    affinity_decoder.predict(pred_full_affin),
                    affinity_metrics(true_test_affin, pred_full_affin),
                ),
                (
                    "original_a_embedding_to_affinity",
                    pred_orig_affin,
                    pred_orig_b_via_affin,
                    orig_aff_metrics,
                ),
                (
                    "matched_sparse_direct_b_ridge",
                    None,
                    matched_direct_model.predict(test_sparse_feats),
                    affinity_metrics(true_test_affin, pred_matched_affin),
                ),
                (
                    "dense_full_response_direct_b_ridge",
                    None,
                    dense_direct_model.predict(test_full_feats),
                    affinity_metrics(true_test_affin, pred_full_affin),
                ),
                (
                    "original_a_embedding_direct_b_ridge",
                    None,
                    pred_orig_b_direct,
                    orig_aff_metrics,
                ),
                (
                    "oracle_true_b_affinity_affine",
                    true_test_affin,
                    affinity_decoder.predict(true_test_affin),
                    affinity_metrics(true_test_affin, true_test_affin),
                ),
            ]

            for method, _, pred_b, am in methods:
                records.append({
                    "seed": int(seed),
                    "method": method,
                    "real_probe_budget_requested": int(k_real),
                    "real_probe_count_train_mean": train_count,
                    "real_probe_count_test_mean": test_count,
                    "source_feature_shift_rmse": source_shift,
                    **am,
                    **evaluate(bte, pred_b),
                })

    result = {
        "experiment": "Pontifex source-to-affinity transport bottleneck ablation",
        "field_store": str(args.field_store),
        "seeds": args.seeds,
        "train_fraction": args.train_frac,
        "real_probe_budgets": args.real_probes,
        "virtual_steps": args.virtual_steps,
        "dense_train_grid": args.dense_train_grid,
        "harmonics": args.harmonics,
        "anchors": args.anchors,
        "ridge_alpha": args.ridge_alpha,
        "records": records,
        "summary": summarize(records),
        "interpretation_contract": {
            "dense_trained_to_sparse_affinity": "current distribution shift: transport trained on complete A response functions, evaluated on K-probe reconstructed held-out functions",
            "matched_sparse_to_sparse_affinity": "same K-probe observation process used in training and held-out inference; isolates train/inference mismatch",
            "dense_trained_to_full_response_affinity": "complete held-out A response profile; tests how much the K-probe observation bottleneck costs",
            "original_a_embedding_to_affinity": "original MiniLM embedding mapped to the same B-anchor affinity chart; representation-information diagnostic, not a sparse Pontifex method",
            "*_direct_b_ridge": "same source representation mapped directly to B coordinates; controls for extra loss introduced by the affinity factorization",
            "oracle_true_b_affinity_affine": "true held-out B-anchor affinities through the learned affine decoder; non-deployable upper bound",
            "data_boundary": "uses only the synthetic pairwise cartography corpus and whole-text train/test splits; no future Assembly/student/validation/test benchmark partition is accessed",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
