# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
# ]
# ///
"""Test whether the remaining A-response -> B-affinity error is a model-class bottleneck.

The previous transport ablation separated observation loss, train/inference mismatch,
and representation loss.  This follow-up keeps the same whole-text held-out protocol
and asks a narrower question: does a modest nonlinear transport recover information
that linear Ridge misses?

For each split and K we compare three transports on exactly the same source features:

- fixed linear Ridge(alpha=1), matching the previous protocol;
- linear Ridge with alpha selected only inside the training partition;
- degree-2 polynomial features + Ridge, with alpha selected only inside training.

The same learned affine B-anchor-affinity -> B-embedding decoder is used for every
condition.  Hyperparameter selection never sees held-out texts.  This remains a
synthetic pairwise-cartography diagnostic: it does not access or instantiate the
future Assembly/student/validation/test benchmark partitions.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures

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


def choose_alpha(x: np.ndarray, y: np.ndarray, alphas: list[float], seed: int) -> float:
    """Choose Ridge alpha on an inner text-level validation split only."""
    rng = np.random.default_rng(seed + 100_003)
    order = np.arange(len(x))
    rng.shuffle(order)
    cut = max(8, int(0.85 * len(order)))
    fit_idx, val_idx = order[:cut], order[cut:]
    best_alpha = float(alphas[0])
    best_rmse = float("inf")
    for alpha in alphas:
        model = Ridge(alpha=float(alpha)).fit(x[fit_idx], y[fit_idx])
        pred = model.predict(x[val_idx])
        rmse = float(np.sqrt(np.mean((pred - y[val_idx]) ** 2)))
        if rmse < best_rmse:
            best_rmse = rmse
            best_alpha = float(alpha)
    return best_alpha


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
    groups = sorted(set((r["source"], r["method"], r["real_probe_budget_requested"]) for r in records))
    out: dict[str, dict] = {}
    for source, method, k in groups:
        rs = [r for r in records if r["source"] == source and r["method"] == method and r["real_probe_budget_requested"] == k]
        block = {
            "selected_alpha_mean": float(np.mean([r["selected_alpha"] for r in rs])),
            "selected_alpha_values": [float(r["selected_alpha"]) for r in rs],
            "actual_probe_count_mean": float(np.mean([r["actual_probe_count_mean"] for r in rs])),
        }
        for metric in metrics:
            vals = np.asarray([r[metric] for r in rs], dtype=float)
            finite = vals[np.isfinite(vals)]
            block[metric] = {
                "mean": float(np.mean(finite)) if len(finite) else float("nan"),
                "median": float(np.median(finite)) if len(finite) else float("nan"),
                "std": float(np.std(finite, ddof=1)) if len(finite) > 1 else 0.0,
            }
        out[f"{source}|{method}|K={k}"] = block
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--field-store", type=Path, required=True)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    ap.add_argument("--train-frac", type=float, default=0.7)
    ap.add_argument("--real-probes", type=int, nargs="+", default=[4, 8, 16])
    ap.add_argument("--virtual-steps", type=int, default=128)
    ap.add_argument("--dense-train-grid", type=int, default=512)
    ap.add_argument("--harmonics", type=int, default=8)
    ap.add_argument("--anchors", type=int, default=256)
    ap.add_argument("--alphas", type=float, nargs="+", default=[0.1, 1.0, 10.0])
    ap.add_argument("--output", type=Path, default=Path("pontifex-transport-model-class.json"))
    args = ap.parse_args()

    d, ids, profiles = raw_size1_profiles(args.field_store)
    b_embed = d["original_b"].astype(float)
    dense_grid = np.linspace(0.0, 1.0, args.dense_train_grid, endpoint=False)
    basis = fourier_basis(dense_grid, args.harmonics)
    poly = PolynomialFeatures(degree=2, include_bias=False)
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

        anchor_idx = farthest_anchors(btr, args.anchors)
        anchor_emb = normalize(btr[anchor_idx])
        train_affin = normalize(btr) @ anchor_emb.T
        true_test_affin = normalize(bte) @ anchor_emb.T
        affinity_decoder = Ridge(alpha=1.0).fit(train_affin, btr)

        for k_real in args.real_probes:
            train_sparse, train_counts = infer_features(
                profiles, tr, k_real, args.virtual_steps, dense_grid, state, args.harmonics
            )
            test_sparse, test_counts = infer_features(
                profiles, te, k_real, args.virtual_steps, dense_grid, state, args.harmonics
            )

            for source, xtr, xte, count in (
                ("matched_sparse", train_sparse, test_sparse, float(np.mean(test_counts))),
                ("full_response", train_full, test_full, float(np.mean([len(profiles[int(i)][0]) for i in te]))),
            ):
                alpha_linear = choose_alpha(xtr, train_affin, args.alphas, seed)
                pred_fixed = Ridge(alpha=1.0).fit(xtr, train_affin).predict(xte)
                pred_tuned = Ridge(alpha=alpha_linear).fit(xtr, train_affin).predict(xte)

                xtr2 = poly.fit_transform(xtr)
                xte2 = poly.transform(xte)
                alpha_quad = choose_alpha(xtr2, train_affin, args.alphas, seed)
                pred_quad = Ridge(alpha=alpha_quad).fit(xtr2, train_affin).predict(xte2)

                for method, pred_affin, selected_alpha in (
                    ("linear_fixed", pred_fixed, 1.0),
                    ("linear_tuned", pred_tuned, alpha_linear),
                    ("quadratic_tuned", pred_quad, alpha_quad),
                ):
                    records.append({
                        "seed": int(seed),
                        "source": source,
                        "method": method,
                        "real_probe_budget_requested": int(k_real),
                        "actual_probe_count_mean": count,
                        "selected_alpha": float(selected_alpha),
                        **affinity_metrics(true_test_affin, pred_affin),
                        **evaluate(bte, affinity_decoder.predict(pred_affin)),
                    })

    result = {
        "experiment": "Pontifex transport model-class ablation",
        "field_store": str(args.field_store),
        "seeds": args.seeds,
        "train_fraction": args.train_frac,
        "real_probe_budgets": args.real_probes,
        "virtual_steps": args.virtual_steps,
        "dense_train_grid": args.dense_train_grid,
        "harmonics": args.harmonics,
        "anchors": args.anchors,
        "alpha_candidates": args.alphas,
        "records": records,
        "summary": summarize(records),
        "interpretation_contract": {
            "linear_fixed": "exact Ridge(alpha=1) model class used in the preceding transport diagnostic",
            "linear_tuned": "same linear model with alpha selected only on an inner split of training texts",
            "quadratic_tuned": "degree-2 interactions among Fourier response coefficients plus Ridge; alpha selected only inside training",
            "matched_sparse": "the same K-probe observation/reconstruction process is used for train and held-out inference",
            "full_response": "complete A response functions; isolates model class from sparse-observation loss",
            "decoder": "all conditions pass predicted B-anchor affinities through the same affine affinity-to-B decoder fit on training texts",
            "data_boundary": "synthetic pairwise cartography only; no future Assembly/student/validation/test benchmark partition is accessed",
            "claim_boundary": "a quadratic improvement would identify recoverable nonlinear transport structure, not validate the multi-teacher Assembly, tokenizer-free inference, or long-context claims",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
