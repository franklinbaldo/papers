# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
# ]
# ///
"""Discriminate coordinate curvature from cross-feature interactions in Pontifex transport.

The capacity-matched ablation showed that a degree-2 polynomial transport predicts
B-anchor affinities better than linear Ridge, RBF random Fourier features, and a small
MLP at approximately matched total state. This experiment asks *which degree-2 terms*
carry that gain.

For the same standardized A-response feature vector x, compare nested and
capacity-matched models:

- linear: x;
- squares: [x, x_i^2] (d extra terms);
- matched random cross: [x, d randomly chosen x_i x_j] (same dimensionality as squares);
- matched screened cross: [x, d cross terms selected using training-only covariance
  with B-anchor affinities] (same dimensionality as squares);
- all cross: [x, all x_i x_j, i<j] but no squares;
- full quadratic: [x, x_i^2, all x_i x_j].

Ridge alpha selection and supervised cross-term screening use training texts only.
Held-out texts are untouched until final scoring. The random matched-cross subset is
deterministic per outer seed.

This remains a synthetic pairwise-cartography diagnostic. It does not instantiate or
access the future D_assembly / D_student / D_val / D_test benchmark partitions.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

from transport_bottleneck_ablation import affinity_metrics
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


def inner_split(n: int, seed: int, frac: float = 0.85) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed + 93_701)
    order = np.arange(n)
    rng.shuffle(order)
    cut = min(n - 1, max(8, int(frac * n)))
    return order[:cut], order[cut:]


def rmse(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((pred - y) ** 2)))


def choose_alpha(x: np.ndarray, y: np.ndarray, alphas: list[float], seed: int) -> float:
    fit_idx, val_idx = inner_split(len(x), seed)
    best_score = float("inf")
    best_alpha = float(alphas[0])
    for alpha in alphas:
        pred = Ridge(alpha=float(alpha)).fit(x[fit_idx], y[fit_idx]).predict(x[val_idx])
        score = rmse(y[val_idx], pred)
        if score < best_score:
            best_score = score
            best_alpha = float(alpha)
    return best_alpha


def pair_indices(d: int) -> tuple[np.ndarray, np.ndarray]:
    return np.triu_indices(d, k=1)


def cross_matrix(x: np.ndarray, ii: np.ndarray, jj: np.ndarray) -> np.ndarray:
    return x[:, ii] * x[:, jj]


def select_cross_by_training_covariance(cross: np.ndarray, y: np.ndarray, k: int) -> np.ndarray:
    """Screen cross terms on training data only using multivariate covariance energy."""
    xc = cross - cross.mean(axis=0, keepdims=True)
    yc = y - y.mean(axis=0, keepdims=True)
    # Feature-target covariance vector, then L2 energy across all affinity targets.
    cov = xc.T @ yc / max(1, len(cross) - 1)
    score = np.linalg.norm(cov, axis=1)
    # Stable sort makes tie behavior deterministic.
    return np.argsort(-score, kind="stable")[:k]


def feature_sets(
    xtr: np.ndarray,
    xte: np.ndarray,
    ytr: np.ndarray,
    seed: int,
) -> dict[str, tuple[np.ndarray, np.ndarray, dict]]:
    d = xtr.shape[1]
    ii, jj = pair_indices(d)
    ctr = cross_matrix(xtr, ii, jj)
    cte = cross_matrix(xte, ii, jj)
    sqtr = xtr * xtr
    sqte = xte * xte
    k = min(d, ctr.shape[1])

    rng = np.random.default_rng(seed + 51_337)
    random_idx = np.sort(rng.choice(ctr.shape[1], size=k, replace=False))
    screened_idx = np.sort(select_cross_by_training_covariance(ctr, ytr, k))

    return {
        "linear": (xtr, xte, {"extra_terms": 0}),
        "squares": (
            np.concatenate([xtr, sqtr], axis=1),
            np.concatenate([xte, sqte], axis=1),
            {"extra_terms": d},
        ),
        "matched_cross_random": (
            np.concatenate([xtr, ctr[:, random_idx]], axis=1),
            np.concatenate([xte, cte[:, random_idx]], axis=1),
            {"extra_terms": int(k), "selected_cross_indices": random_idx.tolist()},
        ),
        "matched_cross_screened": (
            np.concatenate([xtr, ctr[:, screened_idx]], axis=1),
            np.concatenate([xte, cte[:, screened_idx]], axis=1),
            {"extra_terms": int(k), "selected_cross_indices": screened_idx.tolist()},
        ),
        "all_cross": (
            np.concatenate([xtr, ctr], axis=1),
            np.concatenate([xte, cte], axis=1),
            {"extra_terms": int(ctr.shape[1])},
        ),
        "full_quadratic": (
            np.concatenate([xtr, sqtr, ctr], axis=1),
            np.concatenate([xte, sqte, cte], axis=1),
            {"extra_terms": int(d + ctr.shape[1])},
        ),
    }


def summarize(records: list[dict]) -> dict:
    out: dict[str, dict] = {}
    metric_names = (
        "affinity_rmse",
        "affinity_flat_pearson",
        "affinity_row_pearson_mean",
        "affinity_topk_overlap",
        "cosine_similarity",
        "normalized_rmse",
        "retrieval_top1",
        "neighbor_overlap",
        "feature_dim",
        "model_state_scalars",
    )
    for source, method in sorted(set((r["source"], r["method"]) for r in records)):
        rs = [r for r in records if r["source"] == source and r["method"] == method]
        block: dict[str, object] = {
            "selected_alpha_values": [float(r["selected_alpha"]) for r in rs],
            "actual_probe_count_mean": float(np.mean([r["actual_probe_count_mean"] for r in rs])),
            "extra_terms": int(rs[0]["extra_terms"]),
        }
        for metric in metric_names:
            vals = np.asarray([r[metric] for r in rs], dtype=float)
            block[metric] = {
                "mean": float(np.mean(vals)),
                "median": float(np.median(vals)),
                "std": float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0,
            }
        out[f"{source}|{method}"] = block
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--field-store", type=Path, required=True)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    ap.add_argument("--train-frac", type=float, default=0.7)
    ap.add_argument("--real-probes", type=int, default=8)
    ap.add_argument("--virtual-steps", type=int, default=128)
    ap.add_argument("--dense-train-grid", type=int, default=512)
    ap.add_argument("--harmonics", type=int, default=8)
    ap.add_argument("--anchors", type=int, default=256)
    ap.add_argument("--alphas", type=float, nargs="+", default=[0.1, 1.0, 10.0])
    ap.add_argument("--output", type=Path, default=Path("pontifex-quadratic-term-ablation.json"))
    args = ap.parse_args()

    d, ids, profiles = raw_size1_profiles(args.field_store)
    b_embed = d["original_b"].astype(float)
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
        train_full = functional_features((train_dense - mean_dense[None, :]) / scale_dense[None, :], basis)
        test_full = functional_features((test_dense - mean_dense[None, :]) / scale_dense[None, :], basis)
        state = {"mean_dense": mean_dense, "scale_dense": scale_dense}
        train_sparse, _ = infer_features(
            profiles, tr, args.real_probes, args.virtual_steps, dense_grid, state, args.harmonics
        )
        test_sparse, test_counts = infer_features(
            profiles, te, args.real_probes, args.virtual_steps, dense_grid, state, args.harmonics
        )

        anchor_idx = farthest_anchors(btr, args.anchors)
        anchor_emb = normalize(btr[anchor_idx])
        train_affin = normalize(btr) @ anchor_emb.T
        true_test_affin = normalize(bte) @ anchor_emb.T
        affinity_decoder = Ridge(alpha=1.0).fit(train_affin, btr)

        for source, xtr_raw, xte_raw, count in (
            ("matched_sparse", train_sparse, test_sparse, float(np.mean(test_counts))),
            ("full_response", train_full, test_full, float(np.mean([len(profiles[int(i)][0]) for i in te]))),
        ):
            scaler = StandardScaler().fit(xtr_raw)
            xtr = scaler.transform(xtr_raw)
            xte = scaler.transform(xte_raw)

            for method, (fxtr, fxte, meta) in feature_sets(xtr, xte, train_affin, seed).items():
                alpha = choose_alpha(fxtr, train_affin, args.alphas, seed)
                model = Ridge(alpha=alpha).fit(fxtr, train_affin)
                pred_affin = model.predict(fxte)
                state_count = fxtr.shape[1] * train_affin.shape[1] + train_affin.shape[1]
                records.append({
                    "seed": int(seed),
                    "source": source,
                    "method": method,
                    "real_probe_budget_requested": int(args.real_probes),
                    "actual_probe_count_mean": count,
                    "selected_alpha": float(alpha),
                    "feature_dim": int(fxtr.shape[1]),
                    "extra_terms": int(meta["extra_terms"]),
                    "model_state_scalars": int(state_count),
                    **affinity_metrics(true_test_affin, pred_affin),
                    **evaluate(bte, affinity_decoder.predict(pred_affin)),
                })

    result = {
        "experiment": "Pontifex quadratic-term transport ablation",
        "field_store": str(args.field_store),
        "seeds": args.seeds,
        "train_fraction": args.train_frac,
        "real_probe_budget": args.real_probes,
        "virtual_steps": args.virtual_steps,
        "dense_train_grid": args.dense_train_grid,
        "harmonics": args.harmonics,
        "anchors_requested": args.anchors,
        "alphas": args.alphas,
        "protocol": {
            "outer_split": "whole-text train/test split per seed",
            "selection": "Ridge alpha and screened cross terms selected using training texts only",
            "matched_test": "squares, random matched-cross, and screened matched-cross add exactly d nonlinear terms",
            "evidence_boundary": "synthetic pairwise cartography only; no D_assembly/D_student/D_val/D_test benchmark data",
        },
        "summary": summarize(records),
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
