# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
# ]
# ///
"""Same-task semantic-space alignment benchmark for Pontifex Torus.

Each text is represented by its complete intervention-response profile in space A
and the corresponding profile in space B (same positions and occlusion sizes).
Methods train on paired A/B profiles and predict B profiles for held-out texts.

This directly benchmarks the current Pontifex task: cross-space response-field
alignment/prediction, not continual-learning behavior and not raw-vector stitching.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
from sklearn.cross_decomposition import CCA
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.neighbors import NearestNeighbors


def load_profiles(path: Path):
    d = np.load(path, allow_pickle=False)
    tid = d["text_id"].astype(int)
    pos = d["pos"].astype(float)
    size = d["size"].astype(int)
    a = d["response_a"].astype(float)
    b = d["response_b"].astype(float)

    ids = np.unique(tid)
    keys = sorted(set((float(p), int(s)) for p, s in zip(pos, size)))
    key_index = {k: i for i, k in enumerate(keys)}

    xa = np.full((len(ids), len(keys)), np.nan, dtype=float)
    yb = np.full_like(xa, np.nan)
    for t, p, s, av, bv in zip(tid, pos, size, a, b):
        i = int(np.where(ids == t)[0][0])
        j = key_index[(float(p), int(s))]
        xa[i, j] = av
        yb[i, j] = bv

    if np.isnan(xa).any() or np.isnan(yb).any():
        raise RuntimeError(
            "Response profiles are not rectangular; use a field with identical intervention coordinates per text."
        )
    return ids, keys, xa, yb


def rmse(y, pred):
    return float(mean_squared_error(y.ravel(), pred.ravel()) ** 0.5)


def row_neighbor_overlap(y_true, y_pred, k=5):
    k = min(k, len(y_true) - 1)
    if k < 1:
        return float("nan")
    nn_t = NearestNeighbors(n_neighbors=k + 1).fit(y_true).kneighbors(y_true, return_distance=False)
    nn_p = NearestNeighbors(n_neighbors=k + 1).fit(y_pred).kneighbors(y_pred, return_distance=False)
    vals = []
    for i, (a, b) in enumerate(zip(nn_t, nn_p)):
        sa = set(int(x) for x in a if int(x) != i)
        sb = set(int(x) for x in b if int(x) != i)
        vals.append(len(sa & sb) / max(1, len(sa | sb)))
    return float(np.mean(vals))


def bytes_of(*arrays):
    return int(sum(getattr(x, "nbytes", 0) for x in arrays))


def fit_mean(xtr, ytr, xte):
    mean = ytr.mean(axis=0, keepdims=True)
    return np.repeat(mean, len(xte), axis=0), bytes_of(mean)


def fit_ridge(xtr, ytr, xte, alpha=1.0):
    m = Ridge(alpha=alpha).fit(xtr, ytr)
    return m.predict(xte), bytes_of(m.coef_, m.intercept_)


def fit_procrustes(xtr, ytr, xte):
    mx = xtr.mean(axis=0, keepdims=True)
    my = ytr.mean(axis=0, keepdims=True)
    xc, yc = xtr - mx, ytr - my
    u, _, vt = np.linalg.svd(xc.T @ yc, full_matrices=False)
    r = u @ vt
    pred = (xte - mx) @ r + my
    return pred, bytes_of(mx, my, r)


def fit_cca(xtr, ytr, xte, components):
    n = max(1, min(components, xtr.shape[1], ytr.shape[1], len(xtr) - 1))
    m = CCA(n_components=n, max_iter=2000, scale=True).fit(xtr, ytr)
    pred = m.predict(xte)
    state = 0
    for name in ("x_weights_", "y_weights_", "x_loadings_", "y_loadings_", "x_rotations_", "y_rotations_"):
        arr = getattr(m, name, None)
        if arr is not None:
            state += arr.nbytes
    return pred, int(state)


def cosine_rows(x):
    n = np.linalg.norm(x, axis=1, keepdims=True)
    return x / np.clip(n, 1e-12, None)


def fit_relative_knn(xtr, ytr, xte, anchors, k):
    # Shared anchor identities, but similarities are computed independently
    # inside each semantic space, following relative-representation logic.
    na = min(anchors, len(xtr))
    anchor_idx = np.linspace(0, len(xtr) - 1, na, dtype=int)
    ax = cosine_rows(xtr)
    aa = cosine_rows(xtr[anchor_idx])
    rel_tr = ax @ aa.T
    rel_te = cosine_rows(xte) @ aa.T

    kk = min(k, len(xtr))
    nbrs = NearestNeighbors(n_neighbors=kk, metric="euclidean").fit(rel_tr)
    dist, idx = nbrs.kneighbors(rel_te)
    w = 1.0 / np.clip(dist, 1e-9, None)
    w /= w.sum(axis=1, keepdims=True)
    pred = np.stack([np.sum(ytr[ii] * ww[:, None], axis=0) for ii, ww in zip(idx, w)])
    state_bytes = bytes_of(aa, rel_tr, ytr)
    return pred, state_bytes


def torus_features_from_profile(keys, x):
    # Expand each A response profile into the current row-wise torus basis.
    rows = []
    for profile in x:
        per = []
        for (pos, size), av in zip(keys, profile):
            theta = 2.0 * math.pi * pos
            l = math.log2(size)
            per.append([
                av,
                math.sin(theta),
                math.cos(theta),
                l,
                l * l,
                av * math.sin(theta),
                av * math.cos(theta),
                av * l,
                math.sin(2 * theta),
                math.cos(2 * theta),
            ])
        rows.append(np.asarray(per))
    return rows


def fit_torus(keys, xtr, ytr, xte):
    trf = torus_features_from_profile(keys, xtr)
    tef = torus_features_from_profile(keys, xte)
    xx = np.concatenate(trf, axis=0)
    yy = ytr.reshape(-1)
    m = Ridge(alpha=1.0).fit(xx, yy)
    pred = np.stack([m.predict(z) for z in tef])
    return pred, bytes_of(m.coef_, np.asarray([m.intercept_]))


METHODS = {
    "mean_B": lambda keys, xtr, ytr, xte: fit_mean(xtr, ytr, xte),
    "ridge_profile": lambda keys, xtr, ytr, xte: fit_ridge(xtr, ytr, xte),
    "orthogonal_procrustes": lambda keys, xtr, ytr, xte: fit_procrustes(xtr, ytr, xte),
    "cca_8": lambda keys, xtr, ytr, xte: fit_cca(xtr, ytr, xte, 8),
    "relative_knn_16anchors": lambda keys, xtr, ytr, xte: fit_relative_knn(xtr, ytr, xte, 16, 5),
    "pontifex_torus": lambda keys, xtr, ytr, xte: fit_torus(keys, xtr, ytr, xte),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--field-store", type=Path, required=True)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0,1,2,3,4,5,6,7,8,9])
    ap.add_argument("--train-frac", type=float, default=0.7)
    ap.add_argument("--output", type=Path, default=Path("pontifex-alignment-benchmark.json"))
    args = ap.parse_args()

    ids, keys, xa, yb = load_profiles(args.field_store)
    records = []

    for seed in args.seeds:
        rng = np.random.default_rng(seed)
        order = np.arange(len(ids))
        rng.shuffle(order)
        cut = max(2, int(args.train_frac * len(order)))
        tr, te = order[:cut], order[cut:]
        xtr, ytr, xte, yte = xa[tr], yb[tr], xa[te], yb[te]

        for name, fn in METHODS.items():
            t0 = time.perf_counter()
            pred, state_bytes = fn(keys, xtr, ytr, xte)
            elapsed = time.perf_counter() - t0
            records.append({
                "seed": int(seed),
                "method": name,
                "heldout_rmse": rmse(yte, pred),
                "text_neighbor_overlap": row_neighbor_overlap(yte, pred),
                "fit_predict_seconds": elapsed,
                "map_state_bytes": int(state_bytes),
            })

    summary = {}
    for name in METHODS:
        rs = [r for r in records if r["method"] == name]
        for metric in ("heldout_rmse", "text_neighbor_overlap", "fit_predict_seconds", "map_state_bytes"):
            vals = np.asarray([r[metric] for r in rs], dtype=float)
            summary.setdefault(name, {})[metric] = {
                "mean": float(vals.mean()),
                "median": float(np.median(vals)),
                "std": float(vals.std(ddof=1)) if len(vals) > 1 else 0.0,
            }

    result = {
        "experiment": "Pontifex same-task semantic response-field alignment benchmark",
        "task": (
            "Given paired intervention-response profiles from semantic spaces A and B "
            "for training texts, predict the unseen B response profile from A for held-out texts."
        ),
        "field_store": str(args.field_store),
        "texts": int(len(ids)),
        "profile_dimensions": int(len(keys)),
        "train_fraction": args.train_frac,
        "seeds": args.seeds,
        "methods": list(METHODS),
        "records": records,
        "summary": summary,
        "interpretation": (
            "This benchmark compares methods on the same response-field alignment task. "
            "It does not yet compare raw embedding-vector stitching or synthetic-rich embedding reconstruction."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
