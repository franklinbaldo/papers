# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
# ]
# ///
"""Fixed-real-probe / arbitrary-virtual-resolution Pontifex experiment.

This isolates the proposed Torus advantage:

  K expensive/real occlusion observations are fixed.
  M virtual integration positions may be arbitrarily large.

Training:
- one lens only (size=1);
- all observed raw positions on training texts;
- interpolate training response functions densely;
- learn a continuous Fourier transport kernel K_G(theta, region) from A response
  functions to B anchor affinities.

Held-out inference:
- reveal only K real A-side probes at actual raw token-start positions;
- build a circular piecewise-linear source function from those K observations;
- integrate that same inferred source function through K_G using M virtual points;
- accumulate B-region evidence and barycentrically reconstruct a B embedding.

Thus increasing M does not reveal any additional held-out encoder observations.

A matched direct baseline maps the same Fourier-integrated source representation to
B coordinates via Ridge. This controls for whether the regional factorization itself
adds value.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.neighbors import NearestNeighbors


def normalize(x):
    return x / np.clip(np.linalg.norm(x, axis=1, keepdims=True), 1e-12, None)


def cosine_mean(y, pred):
    yn, pn = normalize(y), normalize(pred)
    return float(np.mean(np.sum(yn * pn, axis=1)))


def normalized_rmse(y, pred):
    return float(mean_squared_error(normalize(y).ravel(), normalize(pred).ravel()) ** 0.5)


def retrieval_top1(y, pred):
    yn, pn = normalize(y), normalize(pred)
    return float(np.mean(np.argmax(pn @ yn.T, axis=1) == np.arange(len(y))))


def neighbor_overlap(y, pred, k=5):
    k = min(k, len(y) - 1)
    if k < 1:
        return float("nan")
    yn, pn = normalize(y), normalize(pred)
    yt = NearestNeighbors(n_neighbors=k + 1, metric="cosine").fit(yn).kneighbors(
        yn, return_distance=False
    )
    yp = NearestNeighbors(n_neighbors=k + 1, metric="cosine").fit(pn).kneighbors(
        pn, return_distance=False
    )
    vals = []
    for i, (a, b) in enumerate(zip(yt, yp)):
        sa = set(int(v) for v in a if int(v) != i)
        sb = set(int(v) for v in b if int(v) != i)
        vals.append(len(sa & sb) / max(1, len(sa | sb)))
    return float(np.mean(vals))


def evaluate(y, pred):
    return {
        "cosine_similarity": cosine_mean(y, pred),
        "normalized_rmse": normalized_rmse(y, pred),
        "retrieval_top1": retrieval_top1(y, pred),
        "neighbor_overlap": neighbor_overlap(y, pred),
    }


def farthest_anchors(emb, count):
    en = normalize(emb)
    count = min(int(count), len(en))
    mean = normalize(np.mean(en, axis=0, keepdims=True))[0]
    first = int(np.argmax(en @ mean))
    chosen = [first]
    best = 1.0 - en @ en[first]
    while len(chosen) < count:
        nxt = int(np.argmax(best))
        chosen.append(nxt)
        best = np.minimum(best, 1.0 - en @ en[nxt])
    return np.asarray(chosen, dtype=int)


def raw_size1_profiles(path: Path):
    d = np.load(path, allow_pickle=False)
    tid = d["text_id"].astype(int)
    pos = d["pos"].astype(float)
    size = d["size"].astype(int)
    a = d["response_a"].astype(float)
    ids = np.unique(tid)

    profiles = []
    for text_id in ids:
        mask = (tid == text_id) & (size == 1)
        p = pos[mask]
        v = a[mask]
        order = np.argsort(p)
        p, v = p[order], v[order]
        # Collapse any accidental duplicate position by averaging.
        uniq = np.unique(p)
        vv = np.asarray([np.mean(v[p == q]) for q in uniq], dtype=float)
        profiles.append((uniq.astype(float), vv))

    return d, ids, profiles


def circular_interp(obs_pos, obs_val, grid):
    """Periodic linear interpolation over phase [0,1)."""
    p = np.asarray(obs_pos, dtype=float)
    v = np.asarray(obs_val, dtype=float)
    if len(p) == 1:
        return np.repeat(v[0], len(grid))
    # Periodic copies allow interpolation across the identified 0/1 boundary.
    xp = np.concatenate([p - 1.0, p, p + 1.0])
    fp = np.concatenate([v, v, v])
    order = np.argsort(xp)
    return np.interp(grid, xp[order], fp[order])


def uniform_raw_subset(pos, val, k):
    n = len(pos)
    k = min(max(1, int(k)), n)
    idx = np.unique(np.rint(np.linspace(0, n - 1, k)).astype(int))
    while len(idx) < k:
        unused = [i for i in range(n) if i not in set(idx.tolist())]
        pick = max(unused, key=lambda u: min(abs(u - int(j)) for j in idx))
        idx = np.sort(np.append(idx, pick))
    return pos[idx[:k]], val[idx[:k]]


def fourier_basis(grid, harmonics):
    theta = 2.0 * math.pi * np.asarray(grid, dtype=float)
    cols = [np.ones(len(grid), dtype=float)]
    for h in range(1, int(harmonics) + 1):
        cols.append(np.sin(h * theta))
        cols.append(np.cos(h * theta))
    return np.stack(cols, axis=1)  # [M, basis]


def functional_features(values, basis):
    # Numerical integral over one cycle. Mean is the uniform quadrature rule.
    return np.mean(values[:, :, None] * basis[None, :, :], axis=1)


def build_dense_training(profiles, indices, grid):
    return np.stack([circular_interp(*profiles[int(i)], grid) for i in indices])


def source_stats(train_dense):
    mean = np.mean(train_dense, axis=0)
    scale = np.std(train_dense, axis=0, ddof=1)
    fallback = float(np.median(scale[scale > 1e-12])) if np.any(scale > 1e-12) else 1.0
    scale = np.clip(scale, fallback * 0.05, None)
    return mean, scale


def standardize_on_grid(values, grid, dense_grid, mean_dense, scale_dense):
    mean = np.interp(grid, dense_grid, mean_dense)
    scale = np.interp(grid, dense_grid, scale_dense)
    return (values - mean[None, :]) / scale[None, :]


def train_models(train_dense, b_train, dense_grid, harmonics, anchors):
    mean_dense, scale_dense = source_stats(train_dense)
    z = (train_dense - mean_dense[None, :]) / scale_dense[None, :]
    basis = fourier_basis(dense_grid, harmonics)
    feats = functional_features(z, basis)

    anchor_idx = farthest_anchors(b_train, anchors)
    anchor_emb = normalize(b_train[anchor_idx])
    affin = normalize(b_train) @ anchor_emb.T

    region_model = Ridge(alpha=1.0).fit(feats, affin)
    direct_model = Ridge(alpha=1.0).fit(feats, b_train)
    return {
        "mean_dense": mean_dense,
        "scale_dense": scale_dense,
        "anchor_emb": anchor_emb,
        "region_model": region_model,
        "direct_model": direct_model,
    }


def infer_features(profiles, indices, k_real, virtual_m, dense_grid, model_state, harmonics):
    grid = np.linspace(0.0, 1.0, int(virtual_m), endpoint=False)
    vals = []
    actual_counts = []
    for i in indices:
        p, v = profiles[int(i)]
        pp, vv = uniform_raw_subset(p, v, k_real)
        vals.append(circular_interp(pp, vv, grid))
        actual_counts.append(len(pp))
    vals = np.stack(vals)
    z = standardize_on_grid(
        vals,
        grid,
        dense_grid,
        model_state["mean_dense"],
        model_state["scale_dense"],
    )
    basis = fourier_basis(grid, harmonics)
    return functional_features(z, basis), actual_counts


def region_to_embedding(region_scores, anchor_emb):
    shift = region_scores - np.max(region_scores, axis=1, keepdims=True)
    mass = np.exp(shift)
    mass /= np.clip(np.sum(mass, axis=1, keepdims=True), 1e-12, None)
    return normalize(mass @ anchor_emb), mass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--field-store", type=Path, required=True)
    ap.add_argument("--seeds", type=int, nargs="+", default=list(range(10)))
    ap.add_argument("--train-frac", type=float, default=0.7)
    ap.add_argument("--real-probes", type=int, nargs="+", default=[2, 4, 8])
    ap.add_argument("--virtual-steps", type=int, nargs="+", default=[8,16,32,64,128,256,512])
    ap.add_argument("--dense-train-grid", type=int, default=512)
    ap.add_argument("--harmonics", type=int, default=8)
    ap.add_argument("--anchors", type=int, default=16)
    ap.add_argument("--output", type=Path, default=Path("pontifex-virtual-resolution.json"))
    args = ap.parse_args()

    d, ids, profiles = raw_size1_profiles(args.field_store)
    b_embed = d["original_b"].astype(float)
    dense_grid = np.linspace(0.0, 1.0, args.dense_train_grid, endpoint=False)

    records = []
    for seed in args.seeds:
        rng = np.random.default_rng(seed)
        order = np.arange(len(ids))
        rng.shuffle(order)
        cut = max(4, int(args.train_frac * len(order)))
        tr, te = order[:cut], order[cut:]
        btr, bte = b_embed[tr], b_embed[te]

        train_dense = build_dense_training(profiles, tr, dense_grid)
        state = train_models(
            train_dense, btr, dense_grid, args.harmonics, args.anchors
        )

        for k_real in args.real_probes:
            for virtual_m in args.virtual_steps:
                feats, counts = infer_features(
                    profiles, te, k_real, virtual_m, dense_grid, state, args.harmonics
                )

                region_scores = state["region_model"].predict(feats)
                pred_region, mass = region_to_embedding(
                    region_scores, state["anchor_emb"]
                )
                pred_direct = state["direct_model"].predict(feats)

                records.append({
                    "seed": int(seed),
                    "method": "torus_region_backprojection",
                    "real_probe_budget_requested": int(k_real),
                    "real_probe_count_mean": float(np.mean(counts)),
                    "virtual_steps": int(virtual_m),
                    "regional_entropy_mean": float(
                        np.mean(-np.sum(mass * np.log(np.clip(mass, 1e-12, None)), axis=1))
                    ),
                    **evaluate(bte, pred_region),
                })
                records.append({
                    "seed": int(seed),
                    "method": "matched_direct_fourier_ridge",
                    "real_probe_budget_requested": int(k_real),
                    "real_probe_count_mean": float(np.mean(counts)),
                    "virtual_steps": int(virtual_m),
                    **evaluate(bte, pred_direct),
                })

    summary = {}
    groups = sorted(set(
        (r["method"], r["real_probe_budget_requested"], r["virtual_steps"])
        for r in records
    ))
    metrics = ("cosine_similarity", "normalized_rmse", "retrieval_top1", "neighbor_overlap")
    for method, k_real, virtual_m in groups:
        rs = [
            r for r in records
            if r["method"] == method
            and r["real_probe_budget_requested"] == k_real
            and r["virtual_steps"] == virtual_m
        ]
        block = {
            "real_probe_count_mean": float(np.mean([r["real_probe_count_mean"] for r in rs])),
        }
        for metric in metrics:
            vals = np.asarray([r[metric] for r in rs], dtype=float)
            block[metric] = {
                "mean": float(vals.mean()),
                "median": float(np.median(vals)),
                "std": float(vals.std(ddof=1)) if len(vals) > 1 else 0.0,
            }
        summary[f"{method}|K={k_real}|M={virtual_m}"] = block

    result = {
        "experiment": "Pontifex fixed-real-probe arbitrary-virtual-resolution test",
        "one_lens_only": 1,
        "field_store": str(args.field_store),
        "seeds": args.seeds,
        "train_fraction": args.train_frac,
        "real_probe_budgets": args.real_probes,
        "virtual_steps": args.virtual_steps,
        "dense_train_grid": args.dense_train_grid,
        "harmonics": args.harmonics,
        "anchors": args.anchors,
        "records": records,
        "summary": summary,
        "interpretation_contract": {
            "K": "actual held-out A-side occlusion observations revealed to inference",
            "M": "virtual quadrature positions on the learned continuous torus; increasing M reveals no new held-out encoder observations",
            "torus_region_backprojection": "continuous Fourier transport to B anchor regions followed by barycentric embedding reconstruction",
            "matched_direct_fourier_ridge": "same K-observation reconstructed source function and same Fourier integral, but direct B-coordinate regression",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
