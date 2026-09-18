# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
# ]
# ///
"""Learn regional reflectance/darkness from previous laps.

The previous experiment showed that local A->B->A cycle residual is not a valid
regional darkness map. This experiment operationalizes the user's stronger idea:
after traversing terrain, we know how reliably each region transports information.

For each region (normalized position x occlusion size):
1. estimate out-of-fold A->B transport error on already observed texts;
2. convert normalized error to reflectance exp(-error/scale);
3. darkness = 1-reflectance;
4. fit the full map and test whether learned regional darkness predicts held-out
   regional B error;
5. for each held-out text, weight regional darkness by the light/source response
   emitted at that text's probes and test whether predicted darkness tracks field and
   embedding reconstruction error.

A shuffled A/B correspondence is the negative control.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.cross_decomposition import PLSRegression
from sklearn.linear_model import Ridge

from alignment_benchmark import load_profiles, torus_features_from_profile


def fit_torus(keys, x, y):
    xx = np.concatenate(torus_features_from_profile(keys, x), axis=0)
    yy = y.reshape(-1)
    return Ridge(alpha=1.0).fit(xx, yy)


def predict_torus(model, keys, x):
    return np.stack([model.predict(z) for z in torus_features_from_profile(keys, x)])


def pearson(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if len(a) < 2 or np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def ranks(x):
    x = np.asarray(x, dtype=float)
    order = np.argsort(x, kind="mergesort")
    out = np.empty(len(x), dtype=float)
    out[order] = np.arange(len(x), dtype=float)
    return out


def spearman(a, b):
    return pearson(ranks(a), ranks(b))


def cosine_error_rows(y, pred):
    yn = y / np.clip(np.linalg.norm(y, axis=1, keepdims=True), 1e-12, None)
    pn = pred / np.clip(np.linalg.norm(pred, axis=1, keepdims=True), 1e-12, None)
    return 1.0 - np.sum(yn * pn, axis=1)


def summary(v):
    v = np.asarray(v, dtype=float)
    return {
        "mean": float(np.mean(v)),
        "median": float(np.median(v)),
        "std": float(np.std(v, ddof=1)) if len(v) > 1 else 0.0,
        "min": float(np.min(v)),
        "max": float(np.max(v)),
    }


def oof_regional_darkness(keys, a, b, folds=4):
    n = len(a)
    folds = max(2, min(folds, n))
    pred = np.empty_like(b)
    fold_ids = np.arange(n) % folds
    for f in range(folds):
        va = fold_ids == f
        tr = ~va
        if tr.sum() < 2:
            continue
        m = fit_torus(keys, a[tr], b[tr])
        pred[va] = predict_torus(m, keys, a[va])

    abs_err = np.abs(b - pred)
    # Normalize by empirical target variation per region. This turns the transport
    # residual into a dimensionless terrain difficulty.
    scale = np.std(b, axis=0, ddof=1)
    fallback = float(np.median(scale[scale > 1e-12])) if np.any(scale > 1e-12) else 1e-6
    scale = np.clip(scale, fallback * 0.05, None)
    normalized = np.mean(abs_err, axis=0) / scale
    reflectance = np.exp(-normalized)
    darkness = 1.0 - reflectance
    return darkness, reflectance, scale, pred


def run_condition(keys, a_train, b_train, a_test, b_test, eb_train, eb_test, shuffled, seed):
    bt = b_train.copy()
    if shuffled:
        bt = bt[np.random.default_rng(seed).permutation(len(bt))]

    darkness, reflectance, scale, _ = oof_regional_darkness(keys, a_train, bt)
    model = fit_torus(keys, a_train, bt)
    b_hat = predict_torus(model, keys, a_test)

    test_abs = np.abs(b_test - b_hat)
    test_coord_norm_error = np.mean(test_abs, axis=0) / scale
    test_field_error = np.sqrt(np.mean((b_test - b_hat) ** 2, axis=1))

    # Light/source weighting: regions contribute according to how strongly this text's
    # A-side probes respond. Add a tiny floor so a silent region is not undefined.
    source = np.abs(a_test) + 1e-9
    source /= np.sum(source, axis=1, keepdims=True)
    predicted_text_darkness = source @ darkness

    ncomp = max(1, min(8, b_train.shape[1], eb_train.shape[1], len(b_train) - 1))
    decoder = PLSRegression(n_components=ncomp, scale=True, max_iter=1000).fit(
        b_train, eb_train
    )
    eb_hat = decoder.predict(b_hat)
    embedding_error = cosine_error_rows(eb_test, eb_hat)

    regions = []
    for j, ((pos, size), dark, refl, err) in enumerate(
        zip(keys, darkness, reflectance, test_coord_norm_error)
    ):
        regions.append({
            "index": int(j),
            "pos": float(pos),
            "size": int(size),
            "reflectance": float(refl),
            "darkness": float(dark),
            "heldout_normalized_B_error": float(err),
        })
    regions.sort(key=lambda x: x["darkness"], reverse=True)

    return {
        "regional_darkness": summary(darkness),
        "regional_reflectance": summary(reflectance),
        "heldout_field_error": summary(test_field_error),
        "embedding_cosine_error": summary(embedding_error),
        "predicted_text_darkness": summary(predicted_text_darkness),
        "correlations": {
            "regional_darkness_vs_B_error_pearson": pearson(darkness, test_coord_norm_error),
            "regional_darkness_vs_B_error_spearman": spearman(darkness, test_coord_norm_error),
            "text_darkness_vs_field_error_pearson": pearson(predicted_text_darkness, test_field_error),
            "text_darkness_vs_field_error_spearman": spearman(predicted_text_darkness, test_field_error),
            "text_darkness_vs_embedding_error_pearson": pearson(predicted_text_darkness, embedding_error),
            "text_darkness_vs_embedding_error_spearman": spearman(predicted_text_darkness, embedding_error),
        },
        "darkest_regions": regions[:8],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--field-store", type=Path, required=True)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0,1,2,3,4])
    ap.add_argument("--train-sizes", type=int, nargs="+", default=[8,16,32,64,84])
    ap.add_argument("--test-count", type=int, default=30)
    ap.add_argument("--output", type=Path, default=Path("pontifex-terrain-reflectance.json"))
    args = ap.parse_args()

    data = np.load(args.field_store, allow_pickle=False)
    ids, keys, a, b = load_profiles(args.field_store)
    eb = data["original_b"].astype(float)

    records = []
    for seed in args.seeds:
        rng = np.random.default_rng(seed)
        order = np.arange(len(ids))
        rng.shuffle(order)
        tn = min(args.test_count, max(4, len(order)//4))
        te = order[:tn]
        pool = order[tn:]
        for n in args.train_sizes:
            ne = min(int(n), len(pool))
            tr = pool[:ne]
            if len(tr) < 4:
                continue
            for shuffled in (False, True):
                records.append({
                    "seed": int(seed),
                    "train_texts": int(ne),
                    "condition": "shuffled_correspondence" if shuffled else "true_correspondence",
                    **run_condition(
                        keys, a[tr], b[tr], a[te], b[te], eb[tr], eb[te],
                        shuffled=shuffled, seed=seed + ne + 5000,
                    ),
                })

    aggregate = {}
    corr_names = [
        "regional_darkness_vs_B_error_pearson",
        "regional_darkness_vs_B_error_spearman",
        "text_darkness_vs_field_error_pearson",
        "text_darkness_vs_field_error_spearman",
        "text_darkness_vs_embedding_error_pearson",
        "text_darkness_vs_embedding_error_spearman",
    ]
    for condition in ("true_correspondence", "shuffled_correspondence"):
        aggregate[condition] = {}
        sizes = sorted(set(r["train_texts"] for r in records if r["condition"] == condition))
        for n in sizes:
            rs = [r for r in records if r["condition"] == condition and r["train_texts"] == n]
            block = {
                "regional_darkness_mean": summary([r["regional_darkness"]["mean"] for r in rs]),
                "heldout_field_error_mean": summary([r["heldout_field_error"]["mean"] for r in rs]),
                "embedding_cosine_error_mean": summary([r["embedding_cosine_error"]["mean"] for r in rs]),
            }
            for name in corr_names:
                vals = [r["correlations"][name] for r in rs]
                vals = [v for v in vals if np.isfinite(v)]
                block[name] = summary(vals) if vals else {"mean": float("nan")}
            aggregate[condition][str(n)] = block

    result = {
        "experiment": "Pontifex learned terrain reflectance",
        "definition": (
            "Regional darkness is learned from out-of-fold transport error on previous laps, "
            "not from instantaneous cycle non-closure. Reflectance=exp(-normalized OOF error)."
        ),
        "field_store": str(args.field_store),
        "seeds": args.seeds,
        "train_sizes": args.train_sizes,
        "records": records,
        "aggregate": aggregate,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, allow_nan=True))


if __name__ == "__main__":
    main()
