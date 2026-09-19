# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
# ]
# ///
"""Reconstruct B embeddings from reconstructed semantic response fields.

Task decomposition:
  A response profile -> predicted B response profile -> synthetic B embedding.

Controls:
  - oracle B profile -> embedding
  - direct A profile -> embedding
  - raw A embedding -> B embedding (upper-capacity direct stitching baseline)

Decoders:
  - Ridge
  - PLS
  - kNN barycentric
  - anchor-similarity inversion

Metrics:
  - cosine similarity to true B embedding
  - L2-normalized embedding RMSE
  - held-out retrieval top-1 accuracy
  - text-neighbor overlap in B space
  - fit/predict time
  - learned state bytes
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
from sklearn.cross_decomposition import PLSRegression
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.neighbors import NearestNeighbors

from alignment_benchmark import load_profiles, torus_features_from_profile


def normalize(x: np.ndarray) -> np.ndarray:
    return x / np.clip(np.linalg.norm(x, axis=1, keepdims=True), 1e-12, None)


def cosine_mean(y: np.ndarray, pred: np.ndarray) -> float:
    yn, pn = normalize(y), normalize(pred)
    return float(np.mean(np.sum(yn * pn, axis=1)))


def normalized_rmse(y: np.ndarray, pred: np.ndarray) -> float:
    return float(mean_squared_error(normalize(y).ravel(), normalize(pred).ravel()) ** 0.5)


def retrieval_top1(y: np.ndarray, pred: np.ndarray) -> float:
    yn, pn = normalize(y), normalize(pred)
    sim = pn @ yn.T
    return float(np.mean(np.argmax(sim, axis=1) == np.arange(len(y))))


def neighbor_overlap(y: np.ndarray, pred: np.ndarray, k: int = 5) -> float:
    k = min(k, len(y) - 1)
    if k < 1:
        return float("nan")
    yn, pn = normalize(y), normalize(pred)
    yt = NearestNeighbors(n_neighbors=k + 1, metric="cosine").fit(yn).kneighbors(yn, return_distance=False)
    yp = NearestNeighbors(n_neighbors=k + 1, metric="cosine").fit(pn).kneighbors(pn, return_distance=False)
    vals = []
    for i, (a, b) in enumerate(zip(yt, yp)):
        sa = set(int(v) for v in a if int(v) != i)
        sb = set(int(v) for v in b if int(v) != i)
        vals.append(len(sa & sb) / max(1, len(sa | sb)))
    return float(np.mean(vals))


def state_bytes(*arrays) -> int:
    return int(sum(getattr(a, "nbytes", 0) for a in arrays if a is not None))


def fit_ridge(xtr, ytr, xte, alpha=1.0):
    m = Ridge(alpha=alpha).fit(xtr, ytr)
    return m.predict(xte), state_bytes(m.coef_, m.intercept_)


def fit_pls(xtr, ytr, xte, components=8):
    n = max(1, min(components, xtr.shape[1], ytr.shape[1], len(xtr) - 1))
    m = PLSRegression(n_components=n, scale=True, max_iter=1000).fit(xtr, ytr)
    pred = m.predict(xte)
    arrays = [
        getattr(m, name, None)
        for name in ("x_weights_", "y_weights_", "x_loadings_", "y_loadings_", "x_rotations_", "y_rotations_", "coef_")
    ]
    return pred, state_bytes(*arrays)


def fit_knn_barycentric(xtr, ytr, xte, k=5):
    kk = min(k, len(xtr))
    nbrs = NearestNeighbors(n_neighbors=kk).fit(xtr)
    dist, idx = nbrs.kneighbors(xte)
    w = 1.0 / np.clip(dist, 1e-9, None)
    w /= w.sum(axis=1, keepdims=True)
    pred = np.stack([np.sum(ytr[ii] * ww[:, None], axis=0) for ii, ww in zip(idx, w)])
    return pred, state_bytes(xtr, ytr)


def fit_anchor_inverse(xtr, ytr, xte, anchors=16, alpha=1e-3):
    """Predict target-anchor similarities, then invert them back to B coordinates."""
    yn = normalize(ytr)
    na = min(anchors, len(ytr))
    idx = np.linspace(0, len(ytr) - 1, na, dtype=int)
    anchor_matrix = yn[idx]  # [anchors, dim]

    sims_tr = yn @ anchor_matrix.T
    sim_model = Ridge(alpha=1.0).fit(xtr, sims_tr)
    sims_te = sim_model.predict(xte)

    # Solve A z ~= similarities with ridge stabilization.
    gram = anchor_matrix @ anchor_matrix.T + alpha * np.eye(na)
    # z = A^T (A A^T + lambda I)^-1 s
    inv = np.linalg.solve(gram, np.eye(na))
    pred = sims_te @ inv @ anchor_matrix
    pred = normalize(pred)
    return pred, state_bytes(sim_model.coef_, sim_model.intercept_, anchor_matrix, inv)


def fit_torus_field(keys, xtr, ytr, xte):
    trf = torus_features_from_profile(keys, xtr)
    tef = torus_features_from_profile(keys, xte)
    xx = np.concatenate(trf, axis=0)
    yy = ytr.reshape(-1)
    m = Ridge(alpha=1.0).fit(xx, yy)
    pred = np.stack([m.predict(z) for z in tef])
    return pred


def fit_ridge_field(xtr, ytr, xte):
    return Ridge(alpha=1.0).fit(xtr, ytr).predict(xte)


def evaluate(y, pred):
    return {
        "cosine_similarity": cosine_mean(y, pred),
        "normalized_rmse": normalized_rmse(y, pred),
        "retrieval_top1": retrieval_top1(y, pred),
        "neighbor_overlap": neighbor_overlap(y, pred),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--field-store", type=Path, required=True)
    ap.add_argument("--seeds", type=int, nargs="+", default=list(range(10)))
    ap.add_argument("--train-frac", type=float, default=0.7)
    ap.add_argument("--output", type=Path, default=Path("pontifex-embedding-reconstruction.json"))
    args = ap.parse_args()

    data = np.load(args.field_store, allow_pickle=False)
    if "original_b" not in data.files or "original_a" not in data.files:
        raise RuntimeError("field store lacks original_a/original_b; rebuild with current build_field_store.py")

    ids, keys, xa, yb_field = load_profiles(args.field_store)
    original_a = data["original_a"].astype(float)
    original_b = data["original_b"].astype(float)

    if len(ids) != len(original_b):
        raise RuntimeError("embedding/profile text count mismatch")

    records = []

    for seed in args.seeds:
        rng = np.random.default_rng(seed)
        order = np.arange(len(ids))
        rng.shuffle(order)
        cut = max(2, int(args.train_frac * len(order)))
        tr, te = order[:cut], order[cut:]

        xa_tr, xa_te = xa[tr], xa[te]
        bf_tr, bf_te = yb_field[tr], yb_field[te]
        ea_tr, ea_te = original_a[tr], original_a[te]
        eb_tr, eb_te = original_b[tr], original_b[te]

        predicted_fields = {
            "oracle_B_field": bf_te,
            "ridge_A_to_B_field": fit_ridge_field(xa_tr, bf_tr, xa_te),
            "torus_A_to_B_field": fit_torus_field(keys, xa_tr, bf_tr, xa_te),
        }

        tasks = []

        # Direct controls.
        tasks.append(("direct_A_profile_ridge", xa_tr, xa_te, "ridge"))
        tasks.append(("raw_A_embedding_ridge", ea_tr, ea_te, "ridge"))

        # Decode true/predicted B fields using multiple methods.
        for field_name, field_te in predicted_fields.items():
            prefix = field_name
            tasks.extend([
                (f"{prefix}_to_embedding_ridge", bf_tr, field_te, "ridge"),
                (f"{prefix}_to_embedding_pls", bf_tr, field_te, "pls"),
                (f"{prefix}_to_embedding_knn", bf_tr, field_te, "knn"),
                (f"{prefix}_to_embedding_anchor_inverse", bf_tr, field_te, "anchor"),
            ])

        for name, xtr, xte, decoder in tasks:
            t0 = time.perf_counter()
            if decoder == "ridge":
                pred, nbytes = fit_ridge(xtr, eb_tr, xte)
            elif decoder == "pls":
                pred, nbytes = fit_pls(xtr, eb_tr, xte)
            elif decoder == "knn":
                pred, nbytes = fit_knn_barycentric(xtr, eb_tr, xte)
            elif decoder == "anchor":
                pred, nbytes = fit_anchor_inverse(xtr, eb_tr, xte)
            else:
                raise AssertionError(decoder)
            elapsed = time.perf_counter() - t0
            rec = {
                "seed": int(seed),
                "method": name,
                **evaluate(eb_te, pred),
                "fit_predict_seconds": float(elapsed),
                "state_bytes": int(nbytes),
            }
            records.append(rec)

    summary = {}
    methods = sorted(set(r["method"] for r in records))
    metrics = (
        "cosine_similarity",
        "normalized_rmse",
        "retrieval_top1",
        "neighbor_overlap",
        "fit_predict_seconds",
        "state_bytes",
    )
    for method in methods:
        rs = [r for r in records if r["method"] == method]
        summary[method] = {}
        for metric in metrics:
            vals = np.asarray([r[metric] for r in rs], dtype=float)
            summary[method][metric] = {
                "mean": float(vals.mean()),
                "median": float(np.median(vals)),
                "std": float(vals.std(ddof=1)) if len(vals) > 1 else 0.0,
            }

    result = {
        "experiment": "Pontifex synthetic B-embedding reconstruction",
        "task": (
            "Reconstruct held-out BGE-small original embeddings from either A response profiles, "
            "predicted B response profiles, or oracle B response profiles."
        ),
        "field_store": str(args.field_store),
        "seeds": args.seeds,
        "train_fraction": args.train_frac,
        "embedding_dimensions": {
            "A": int(original_a.shape[1]),
            "B": int(original_b.shape[1]),
        },
        "methods": methods,
        "records": records,
        "summary": summary,
        "interpretation_contract": {
            "oracle_B_field": "upper bound on how much original B embedding is recoverable from the intervention-response field alone",
            "ridge_A_to_B_field": "two-stage reconstruction using strong full-profile alignment baseline",
            "torus_A_to_B_field": "two-stage reconstruction using compact Pontifex Torus response-field map",
            "direct_A_profile_ridge": "bypass control: predict B embedding directly from A response profile",
            "raw_A_embedding_ridge": "direct raw-latent stitching baseline with access to A embedding coordinates",
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
