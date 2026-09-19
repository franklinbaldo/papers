# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
# ]
# ///
"""Canonical-torus prior, cycle residual, and epistemic darkness experiment.

Operationalization:
- T0 (canonical simple torus) closes perfectly by definition: source returns to itself.
  This is a geometric prior, not evidence that the A<->B terrain is known.
- G_n is learned from paired A/B response fields.
- A held-out A field is transported A->Bhat->Ahat through the learned geometry.
- cycle residual = |A - Ahat| measures non-closure under G_n.
- local return fraction = exp(-|A-Ahat| / sigma_A); darkness = 1-return_fraction.
- We test whether cycle residual/darkness predicts actual B-field error and synthetic
  B-embedding error.
- A shuffled-pair control tests whether low cycle error can be misleading when the
  cross-space correspondence itself is wrong.

This does not claim literal optical physics. It tests whether the proposed
light/closure accounting is a useful epistemic signal in the current toy.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from sklearn.cross_decomposition import PLSRegression
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error

from alignment_benchmark import load_profiles, torus_features_from_profile


def rmse_rows(y: np.ndarray, pred: np.ndarray) -> np.ndarray:
    return np.sqrt(np.mean((y - pred) ** 2, axis=1))


def cosine_error_rows(y: np.ndarray, pred: np.ndarray) -> np.ndarray:
    yn = y / np.clip(np.linalg.norm(y, axis=1, keepdims=True), 1e-12, None)
    pn = pred / np.clip(np.linalg.norm(pred, axis=1, keepdims=True), 1e-12, None)
    return 1.0 - np.sum(yn * pn, axis=1)


def pearson(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 2 or np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def ranks(x: np.ndarray) -> np.ndarray:
    # Stable ordinal ranks are sufficient here; exact ties are rare in continuous metrics.
    order = np.argsort(x, kind="mergesort")
    out = np.empty(len(x), dtype=float)
    out[order] = np.arange(len(x), dtype=float)
    return out


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    return pearson(ranks(a), ranks(b))


def fit_torus_model(keys, x: np.ndarray, y: np.ndarray) -> Ridge:
    xf = np.concatenate(torus_features_from_profile(keys, x), axis=0)
    yf = y.reshape(-1)
    return Ridge(alpha=1.0).fit(xf, yf)


def predict_torus(model: Ridge, keys, x: np.ndarray) -> np.ndarray:
    return np.stack([model.predict(z) for z in torus_features_from_profile(keys, x)])


def fit_embedding_decoder(b_field_train: np.ndarray, b_embed_train: np.ndarray) -> PLSRegression:
    n = max(1, min(8, b_field_train.shape[1], b_embed_train.shape[1], len(b_field_train) - 1))
    return PLSRegression(n_components=n, scale=True, max_iter=1000).fit(
        b_field_train, b_embed_train
    )


def summarize_vector(v: np.ndarray) -> dict[str, float]:
    return {
        "mean": float(np.mean(v)),
        "median": float(np.median(v)),
        "std": float(np.std(v, ddof=1)) if len(v) > 1 else 0.0,
        "min": float(np.min(v)),
        "max": float(np.max(v)),
    }


def evaluate_geometry(
    keys,
    a_train: np.ndarray,
    b_train: np.ndarray,
    a_test: np.ndarray,
    b_test: np.ndarray,
    b_embed_train: np.ndarray,
    b_embed_test: np.ndarray,
    *,
    shuffled: bool,
    rng: np.random.Generator,
) -> dict:
    bt = b_train.copy()
    if shuffled:
        bt = bt[rng.permutation(len(bt))]

    forward = fit_torus_model(keys, a_train, bt)
    reverse = fit_torus_model(keys, bt, a_train)

    b_hat = predict_torus(forward, keys, a_test)
    a_cycle = predict_torus(reverse, keys, b_hat)

    field_error = rmse_rows(b_test, b_hat)
    cycle_error = rmse_rows(a_test, a_cycle)

    sigma = np.std(a_train, axis=0, ddof=1)
    sigma = np.clip(sigma, np.median(sigma[sigma > 1e-12]) * 0.05 if np.any(sigma > 1e-12) else 1e-6, None)
    local_z = np.abs(a_test - a_cycle) / sigma[None, :]
    local_return = np.exp(-local_z)
    local_darkness = 1.0 - local_return
    darkness = np.mean(local_darkness, axis=1)

    # Decoder is always trained on true B fields and true B embeddings. This lets us
    # isolate whether the transport geometry produces a field that is useful for
    # reconstructing the target embedding.
    decoder = fit_embedding_decoder(b_train, b_embed_train)
    b_embed_hat = decoder.predict(b_hat)
    embed_error = cosine_error_rows(b_embed_test, b_embed_hat)

    coord_field_error = np.mean(np.abs(b_test - b_hat), axis=0)
    coord_darkness = np.mean(local_darkness, axis=0)

    region_records = []
    for j, ((pos, size), dark, ferr) in enumerate(zip(keys, coord_darkness, coord_field_error)):
        region_records.append({
            "index": int(j),
            "pos": float(pos),
            "size": int(size),
            "darkness": float(dark),
            "mean_abs_B_error": float(ferr),
        })
    region_records.sort(key=lambda x: x["darkness"], reverse=True)

    return {
        "field_error": summarize_vector(field_error),
        "cycle_error": summarize_vector(cycle_error),
        "darkness": summarize_vector(darkness),
        "embedding_cosine_error": summarize_vector(embed_error),
        "correlations": {
            "cycle_vs_B_field_error_pearson": pearson(cycle_error, field_error),
            "cycle_vs_B_field_error_spearman": spearman(cycle_error, field_error),
            "darkness_vs_B_field_error_pearson": pearson(darkness, field_error),
            "darkness_vs_B_field_error_spearman": spearman(darkness, field_error),
            "cycle_vs_embedding_error_pearson": pearson(cycle_error, embed_error),
            "cycle_vs_embedding_error_spearman": spearman(cycle_error, embed_error),
            "darkness_vs_embedding_error_pearson": pearson(darkness, embed_error),
            "darkness_vs_embedding_error_spearman": spearman(darkness, embed_error),
            "regional_darkness_vs_B_error_pearson": pearson(coord_darkness, coord_field_error),
            "regional_darkness_vs_B_error_spearman": spearman(coord_darkness, coord_field_error),
        },
        "darkest_regions": region_records[:8],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--field-store", type=Path, required=True)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    ap.add_argument("--train-sizes", type=int, nargs="+", default=[4, 8, 16, 32, 64, 84])
    ap.add_argument("--test-count", type=int, default=30)
    ap.add_argument("--output", type=Path, default=Path("pontifex-cycle-epistemics.json"))
    args = ap.parse_args()

    data = np.load(args.field_store, allow_pickle=False)
    if "original_b" not in data.files:
        raise RuntimeError("field store must contain original_b embeddings")

    ids, keys, a_field, b_field = load_profiles(args.field_store)
    b_embed = data["original_b"].astype(float)
    if len(ids) != len(b_embed):
        raise RuntimeError("embedding/profile text count mismatch")

    all_records = []

    # Canonical T0: perfect topological closure by definition, but no learned terrain.
    # For a concrete no-terrain prediction we use Bhat=A because the response profile
    # dimensions share intervention coordinates. This deliberately demonstrates that
    # zero cycle loss alone is not proof of correct cross-space knowledge.
    canonical_B_error = rmse_rows(b_field, a_field)
    canonical = {
        "definition": "T0 closes exactly: A -> A, so cycle loss is zero by construction.",
        "cycle_error": 0.0,
        "no_terrain_B_field_error": summarize_vector(canonical_B_error),
    }

    for seed in args.seeds:
        rng = np.random.default_rng(seed)
        order = np.arange(len(ids))
        rng.shuffle(order)
        test_n = min(args.test_count, max(4, len(order) // 4))
        te = order[:test_n]
        pool = order[test_n:]

        for n in args.train_sizes:
            n_eff = min(int(n), len(pool))
            if n_eff < 3:
                continue
            tr = pool[:n_eff]
            for shuffled in (False, True):
                result = evaluate_geometry(
                    keys,
                    a_field[tr],
                    b_field[tr],
                    a_field[te],
                    b_field[te],
                    b_embed[tr],
                    b_embed[te],
                    shuffled=shuffled,
                    rng=np.random.default_rng(seed + 10000 + n_eff),
                )
                all_records.append({
                    "seed": int(seed),
                    "train_texts": int(n_eff),
                    "condition": "shuffled_correspondence" if shuffled else "true_correspondence",
                    **result,
                })

    # Aggregate scalar means across seeds for each training size/condition.
    aggregate = {}
    scalar_paths = [
        ("field_error", "mean"),
        ("cycle_error", "mean"),
        ("darkness", "mean"),
        ("embedding_cosine_error", "mean"),
    ]
    corr_keys = [
        "cycle_vs_B_field_error_pearson",
        "cycle_vs_B_field_error_spearman",
        "darkness_vs_B_field_error_pearson",
        "darkness_vs_B_field_error_spearman",
        "cycle_vs_embedding_error_pearson",
        "cycle_vs_embedding_error_spearman",
        "darkness_vs_embedding_error_pearson",
        "darkness_vs_embedding_error_spearman",
        "regional_darkness_vs_B_error_pearson",
        "regional_darkness_vs_B_error_spearman",
    ]

    for condition in ("true_correspondence", "shuffled_correspondence"):
        aggregate[condition] = {}
        for n in sorted(set(r["train_texts"] for r in all_records if r["condition"] == condition)):
            rs = [r for r in all_records if r["condition"] == condition and r["train_texts"] == n]
            block = {}
            for group, metric in scalar_paths:
                vals = np.asarray([r[group][metric] for r in rs], dtype=float)
                block[f"{group}_{metric}"] = summarize_vector(vals)
            for ck in corr_keys:
                vals = np.asarray([r["correlations"][ck] for r in rs], dtype=float)
                vals = vals[np.isfinite(vals)]
                block[ck] = summarize_vector(vals) if len(vals) else {"mean": float("nan")}
            aggregate[condition][str(n)] = block

    result = {
        "experiment": "Pontifex canonical torus prior and cycle epistemics",
        "hypothesis": (
            "A simple torus provides a known unit-closure prior. Learned terrain is a deformation "
            "from that prior. Non-closure/darkness under the learned A->B->A cycle may serve as "
            "an epistemic signal if it tracks actual target-space and embedding reconstruction error."
        ),
        "canonical_T0": canonical,
        "field_store": str(args.field_store),
        "seeds": args.seeds,
        "train_sizes": args.train_sizes,
        "test_count": args.test_count,
        "records": all_records,
        "aggregate": aggregate,
        "interpretation_contract": {
            "cycle_error": "non-closure after A->Bhat->Ahat",
            "return_fraction": "exp(-local_cycle_residual / local training scale)",
            "darkness": "1 - return_fraction; operational visualization variable",
            "shuffled_control": "tests whether cycle closure can look confident despite incorrect A/B correspondence",
            "canonical_warning": "T0 has perfect closure by definition, so closure alone cannot equal knowledge",
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, allow_nan=True))


if __name__ == "__main__":
    main()
