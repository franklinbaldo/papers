# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
# ]
# ///
"""Capacity-matched test of nonlinear A-response -> B-affinity transport.

The preceding model-class ablation found that degree-2 interactions improve transport
from A response features to B-anchor affinities.  That result is ambiguous because a
quadratic expansion also buys substantially more coefficients than a linear Ridge.

This experiment compares nonlinear families at approximately the *same scalar model
state* as the quadratic readout:

- standardized linear Ridge (small baseline);
- degree-2 PolynomialFeatures + Ridge (reference nonlinear model);
- random Fourier features (RBF) + Ridge, with the number of random features chosen so
  projection state + readout state approximately matches the quadratic coefficient
  count;
- a one-hidden-layer MLP whose trainable parameter count approximately matches the
  quadratic coefficient count.

All preprocessing statistics, Ridge alphas, RFF gamma, and MLP alpha are selected or
fit using training texts only.  The outer held-out texts are untouched until final
scoring.  We report both predictive quality and explicit scalar-state / timing costs.

This remains a synthetic pairwise-cartography diagnostic.  It does not instantiate or
access the future D_assembly / D_student / D_val / D_test benchmark partitions.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
from sklearn.kernel_approximation import RBFSampler
from sklearn.linear_model import Ridge
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

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
    rng = np.random.default_rng(seed + 71_911)
    order = np.arange(n)
    rng.shuffle(order)
    cut = min(n - 1, max(8, int(frac * n)))
    return order[:cut], order[cut:]


def rmse(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((pred - y) ** 2)))


def choose_ridge_alpha(x: np.ndarray, y: np.ndarray, alphas: list[float], seed: int) -> tuple[float, float]:
    fit_idx, val_idx = inner_split(len(x), seed)
    started = time.perf_counter()
    best = (float("inf"), float(alphas[0]))
    for alpha in alphas:
        pred = Ridge(alpha=float(alpha)).fit(x[fit_idx], y[fit_idx]).predict(x[val_idx])
        score = rmse(y[val_idx], pred)
        if score < best[0]:
            best = (score, float(alpha))
    return best[1], time.perf_counter() - started


def choose_rff(
    x: np.ndarray,
    y: np.ndarray,
    *,
    components: int,
    gammas: list[float],
    alphas: list[float],
    seed: int,
) -> tuple[float, float, float]:
    fit_idx, val_idx = inner_split(len(x), seed)
    started = time.perf_counter()
    best = (float("inf"), float(gammas[0]), float(alphas[0]))
    for gamma in gammas:
        rff = RBFSampler(gamma=float(gamma), n_components=components, random_state=seed + 404)
        z = rff.fit_transform(x)
        for alpha in alphas:
            pred = Ridge(alpha=float(alpha)).fit(z[fit_idx], y[fit_idx]).predict(z[val_idx])
            score = rmse(y[val_idx], pred)
            if score < best[0]:
                best = (score, float(gamma), float(alpha))
    return best[1], best[2], time.perf_counter() - started


def choose_mlp_alpha(
    x: np.ndarray,
    y: np.ndarray,
    *,
    hidden: int,
    alphas: list[float],
    seed: int,
    max_iter: int,
) -> tuple[float, float]:
    fit_idx, val_idx = inner_split(len(x), seed)
    started = time.perf_counter()
    best = (float("inf"), float(alphas[0]))
    for alpha in alphas:
        model = MLPRegressor(
            hidden_layer_sizes=(hidden,),
            activation="tanh",
            solver="adam",
            alpha=float(alpha),
            learning_rate_init=1e-3,
            max_iter=max_iter,
            early_stopping=False,
            tol=1e-5,
            random_state=seed + 808,
        )
        pred = model.fit(x[fit_idx], y[fit_idx]).predict(x[val_idx])
        score = rmse(y[val_idx], pred)
        if score < best[0]:
            best = (score, float(alpha))
    return best[1], time.perf_counter() - started


def model_state_counts(d: int, q: int, out: int) -> tuple[int, int, int, int]:
    """Return linear, quadratic, matched-RFF components, matched-MLP hidden width."""
    linear = d * out + out
    quadratic = q * out + out
    # RFF stores random projection d*n, random offsets n, and Ridge n*out + out.
    rff_components = max(1, round((quadratic - out) / (d + 1 + out)))
    # MLP stores d*h+h + h*out+out trainable scalars.
    mlp_hidden = max(1, round((quadratic - out) / (d + 1 + out)))
    return linear, quadratic, rff_components, mlp_hidden


def summarize(records: list[dict]) -> dict:
    keys = sorted(set((r["source"], r["method"]) for r in records))
    metric_names = (
        "affinity_rmse",
        "affinity_flat_pearson",
        "affinity_row_pearson_mean",
        "affinity_topk_overlap",
        "cosine_similarity",
        "normalized_rmse",
        "retrieval_top1",
        "neighbor_overlap",
        "model_state_scalars",
        "model_state_bytes_float64",
        "selection_seconds",
        "final_fit_seconds",
        "predict_seconds",
    )
    out: dict[str, dict] = {}
    for source, method in keys:
        rs = [r for r in records if r["source"] == source and r["method"] == method]
        block: dict[str, dict | list | float] = {
            "selected_alpha_values": [float(r["selected_alpha"]) for r in rs],
            "selected_gamma_values": [r.get("selected_gamma") for r in rs],
            "actual_probe_count_mean": float(np.mean([r["actual_probe_count_mean"] for r in rs])),
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


def timed_predict(model, x: np.ndarray) -> tuple[np.ndarray, float]:
    started = time.perf_counter()
    pred = model.predict(x)
    return pred, time.perf_counter() - started


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
    ap.add_argument("--rff-gammas", type=float, nargs="+", default=[0.01, 0.1, 1.0])
    ap.add_argument("--mlp-alphas", type=float, nargs="+", default=[0.0001, 0.001, 0.01])
    ap.add_argument("--mlp-max-iter", type=int, default=350)
    ap.add_argument("--output", type=Path, default=Path("pontifex-transport-capacity-matched.json"))
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
        train_sparse, train_counts = infer_features(
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
            xtr2 = poly.fit_transform(xtr)
            xte2 = poly.transform(xte)
            input_dim = xtr.shape[1]
            quad_dim = xtr2.shape[1]
            out_dim = train_affin.shape[1]
            linear_state, quadratic_state, rff_components, mlp_hidden = model_state_counts(
                input_dim, quad_dim, out_dim
            )
            rff_state = rff_components * (input_dim + 1 + out_dim) + out_dim
            mlp_state = (input_dim + 1) * mlp_hidden + (mlp_hidden + 1) * out_dim

            # Linear Ridge.
            alpha_linear, select_linear = choose_ridge_alpha(xtr, train_affin, args.alphas, seed)
            started = time.perf_counter()
            linear = Ridge(alpha=alpha_linear).fit(xtr, train_affin)
            fit_linear = time.perf_counter() - started
            pred_linear, predict_linear = timed_predict(linear, xte)

            # Quadratic reference.
            alpha_quad, select_quad = choose_ridge_alpha(xtr2, train_affin, args.alphas, seed)
            started = time.perf_counter()
            quad = Ridge(alpha=alpha_quad).fit(xtr2, train_affin)
            fit_quad = time.perf_counter() - started
            pred_quad, predict_quad = timed_predict(quad, xte2)

            # Capacity-matched random Fourier features.
            gamma_rff, alpha_rff, select_rff = choose_rff(
                xtr,
                train_affin,
                components=rff_components,
                gammas=args.rff_gammas,
                alphas=args.alphas,
                seed=seed,
            )
            rff = RBFSampler(gamma=gamma_rff, n_components=rff_components, random_state=seed + 404)
            ztr = rff.fit_transform(xtr)
            zte = rff.transform(xte)
            started = time.perf_counter()
            rff_ridge = Ridge(alpha=alpha_rff).fit(ztr, train_affin)
            fit_rff = time.perf_counter() - started
            pred_rff, predict_rff = timed_predict(rff_ridge, zte)

            # Capacity-matched one-hidden-layer MLP.
            alpha_mlp, select_mlp = choose_mlp_alpha(
                xtr,
                train_affin,
                hidden=mlp_hidden,
                alphas=args.mlp_alphas,
                seed=seed,
                max_iter=args.mlp_max_iter,
            )
            mlp = MLPRegressor(
                hidden_layer_sizes=(mlp_hidden,),
                activation="tanh",
                solver="adam",
                alpha=alpha_mlp,
                learning_rate_init=1e-3,
                max_iter=args.mlp_max_iter,
                early_stopping=False,
                tol=1e-5,
                random_state=seed + 808,
            )
            started = time.perf_counter()
            mlp.fit(xtr, train_affin)
            fit_mlp = time.perf_counter() - started
            pred_mlp, predict_mlp = timed_predict(mlp, xte)

            for method, pred_affin, alpha, gamma, state_count, selection_s, fit_s, predict_s in (
                ("linear_tuned", pred_linear, alpha_linear, None, linear_state, select_linear, fit_linear, predict_linear),
                ("quadratic_tuned", pred_quad, alpha_quad, None, quadratic_state, select_quad, fit_quad, predict_quad),
                ("rff_ridge_matched", pred_rff, alpha_rff, gamma_rff, rff_state, select_rff, fit_rff, predict_rff),
                ("mlp_tanh_matched", pred_mlp, alpha_mlp, None, mlp_state, select_mlp, fit_mlp, predict_mlp),
            ):
                records.append({
                    "seed": int(seed),
                    "source": source,
                    "method": method,
                    "real_probe_budget_requested": int(args.real_probes),
                    "actual_probe_count_mean": count,
                    "input_dim": int(input_dim),
                    "quadratic_feature_dim": int(quad_dim),
                    "rff_components": int(rff_components),
                    "mlp_hidden": int(mlp_hidden),
                    "selected_alpha": float(alpha),
                    "selected_gamma": None if gamma is None else float(gamma),
                    "model_state_scalars": int(state_count),
                    "model_state_bytes_float64": int(state_count * 8),
                    "selection_seconds": float(selection_s),
                    "final_fit_seconds": float(fit_s),
                    "predict_seconds": float(predict_s),
                    **affinity_metrics(true_test_affin, pred_affin),
                    **evaluate(bte, affinity_decoder.predict(pred_affin)),
                })

    result = {
        "experiment": "Pontifex capacity-matched nonlinear transport ablation",
        "field_store": str(args.field_store),
        "seeds": args.seeds,
        "train_fraction": args.train_frac,
        "real_probe_budget": args.real_probes,
        "virtual_steps": args.virtual_steps,
        "dense_train_grid": args.dense_train_grid,
        "harmonics": args.harmonics,
        "anchors": args.anchors,
        "ridge_alpha_candidates": args.alphas,
        "rff_gamma_candidates": args.rff_gammas,
        "mlp_alpha_candidates": args.mlp_alphas,
        "mlp_max_iter": args.mlp_max_iter,
        "records": records,
        "summary": summarize(records),
        "interpretation_contract": {
            "capacity_match": "quadratic Ridge, RFF+Ridge, and one-hidden-layer MLP are matched approximately on scalar model state; exact counts are reported",
            "linear_tuned": "small-capacity standardized linear Ridge baseline",
            "quadratic_tuned": "degree-2 expansion plus Ridge; reference nonlinear result from the prior ablation, now under common standardization",
            "rff_ridge_matched": "RBF random Fourier map plus Ridge; random projection state is counted in the capacity budget",
            "mlp_tanh_matched": "one tanh hidden layer; width selected algebraically to match quadratic scalar parameter state, not by held-out performance",
            "hyperparameter_boundary": "all alpha/gamma choices use only an inner split of outer-training texts; held-out texts are scored once after selection",
            "timing_boundary": "selection, final fit, and prediction wall times are reported separately and are runner-dependent diagnostic costs",
            "decoder": "every transport is scored through the same affine affinity-to-B decoder fit only on outer-training texts",
            "data_boundary": "synthetic pairwise cartography only; future Assembly/student/validation/test benchmark partitions are not accessed",
            "claim_boundary": "a nonlinear win at matched state would support compact nonlinear transport structure; it would not validate the Torus topology, multi-teacher Assembly, tokenizer-free inference, or long-context claims",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
