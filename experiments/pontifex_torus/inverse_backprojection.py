# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
# ]
# ///
"""Inverse light backprojection through the learned Pontifex terrain.

Pipeline under test:

    occlusion center
        -> unit-normalized cheap-space light
        -> inverse propagation through K_G
        -> accumulation over B-side semantic regions
        -> barycentric synthetic B embedding

The regional basis is defined by representative B-embedding anchors learned only
from training texts. K_G maps source probe deviations at normalized occlusion
coordinates into target-region affinity deviations. At inference, only selected
occlusion centers are allowed to emit light; all unseen centers contribute zero
deviation from the canonical prior.

This is intentionally not a generic A-profile -> B-vector decoder. The learned
cross-space object is a probe-to-region transport kernel. Vector reconstruction
happens only after regional evidence has been accumulated.

Two source variants are tested:
- smallest_lens: one scalar response (size=1) at each selected center;
- all_lenses: all available lens sizes at a selected center.

Budgets count occlusion centers, not scalar lens observations.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.neighbors import NearestNeighbors

from alignment_benchmark import load_profiles


def normalize(x: np.ndarray) -> np.ndarray:
    return x / np.clip(np.linalg.norm(x, axis=1, keepdims=True), 1e-12, None)


def cosine_mean(y: np.ndarray, pred: np.ndarray) -> float:
    yn, pn = normalize(y), normalize(pred)
    return float(np.mean(np.sum(yn * pn, axis=1)))


def normalized_rmse(y: np.ndarray, pred: np.ndarray) -> float:
    return float(mean_squared_error(normalize(y).ravel(), normalize(pred).ravel()) ** 0.5)


def retrieval_top1(y: np.ndarray, pred: np.ndarray) -> float:
    yn, pn = normalize(y), normalize(pred)
    return float(np.mean(np.argmax(pn @ yn.T, axis=1) == np.arange(len(y))))


def neighbor_overlap(y: np.ndarray, pred: np.ndarray, k: int = 5) -> float:
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


def farthest_anchors(emb: np.ndarray, count: int) -> np.ndarray:
    """Deterministic farthest-point anchor selection in cosine geometry."""
    en = normalize(emb)
    count = min(count, len(en))
    # Start with the point closest to the training mean direction.
    mean = normalize(np.mean(en, axis=0, keepdims=True))[0]
    first = int(np.argmax(en @ mean))
    chosen = [first]
    best_dist = 1.0 - (en @ en[first])
    while len(chosen) < count:
        nxt = int(np.argmax(best_dist))
        chosen.append(nxt)
        best_dist = np.minimum(best_dist, 1.0 - (en @ en[nxt]))
    return np.asarray(chosen, dtype=int)


def center_groups(keys):
    positions = sorted(set(float(p) for p, _ in keys))
    groups = {}
    for p in positions:
        groups[p] = [i for i, (q, _) in enumerate(keys) if abs(float(q) - p) < 1e-12]
    return positions, groups


def uniform_centers(positions: list[float], budget: int) -> list[float]:
    budget = min(max(1, int(budget)), len(positions))
    idx = np.linspace(0, len(positions) - 1, budget)
    idx = np.unique(np.rint(idx).astype(int))
    # In rare rounding collisions, fill with farthest unused indices.
    while len(idx) < budget:
        unused = [i for i in range(len(positions)) if i not in set(idx.tolist())]
        if not unused:
            break
        if len(idx) == 0:
            pick = unused[0]
        else:
            pick = max(unused, key=lambda u: min(abs(u - int(v)) for v in idx))
        idx = np.sort(np.append(idx, pick))
    return [positions[int(i)] for i in idx[:budget]]


def feature_indices(keys, selected_centers, mode):
    selected = set(float(p) for p in selected_centers)
    out = []
    for j, (p, size) in enumerate(keys):
        if float(p) not in selected:
            continue
        if mode == "smallest_lens" and int(size) != 1:
            continue
        out.append(j)
    return np.asarray(out, dtype=int)


class TerrainBackprojector:
    """Probe-space -> B-region inverse transport with a canonical mean prior."""

    def __init__(self, alpha: float = 1.0, anchors: int = 16):
        self.alpha = alpha
        self.anchors = anchors

    def fit(self, a_train: np.ndarray, b_embed_train: np.ndarray):
        self.a_mean_ = a_train.mean(axis=0)
        self.a_scale_ = a_train.std(axis=0, ddof=1)
        fallback = float(np.median(self.a_scale_[self.a_scale_ > 1e-12])) if np.any(
            self.a_scale_ > 1e-12
        ) else 1.0
        self.a_scale_ = np.clip(self.a_scale_, fallback * 0.05, None)

        anchor_idx = farthest_anchors(b_embed_train, self.anchors)
        self.anchor_emb_ = normalize(b_embed_train[anchor_idx])
        bnorm = normalize(b_embed_train)
        affin = bnorm @ self.anchor_emb_.T

        self.affin_mean_ = affin.mean(axis=0)
        z = (a_train - self.a_mean_) / self.a_scale_

        # K_G is the terrain transport kernel. Ridge regularization keeps the
        # multi-probe inverse operator stable. Coefficients are [regions, probes].
        model = Ridge(alpha=self.alpha, fit_intercept=True).fit(z, affin)
        self.kernel_ = model.coef_.T  # [probe, region]
        self.bias_ = model.intercept_
        return self

    def backproject(self, a_test: np.ndarray, active_idx: np.ndarray):
        z = (a_test - self.a_mean_) / self.a_scale_
        # Canonical prior: unseen centers contribute no deviation. Only active
        # occlusion centers emit light into the inverse operator.
        if len(active_idx) == 0:
            regional = np.repeat(self.bias_[None, :], len(a_test), axis=0)
        else:
            regional = self.bias_[None, :] + z[:, active_idx] @ self.kernel_[active_idx]

        # Convert regional evidence into nonnegative light mass. Temperature is
        # intentionally fixed so this is not tuned on test labels.
        shift = regional - np.max(regional, axis=1, keepdims=True)
        mass = np.exp(shift)
        mass /= np.clip(np.sum(mass, axis=1, keepdims=True), 1e-12, None)

        # Accumulated regional light is converted to a point in the empirical B
        # manifold by barycentric combination of anchor embeddings.
        emb = mass @ self.anchor_emb_
        return normalize(emb), mass, regional


def direct_ridge(a_train, b_train, a_test):
    m = Ridge(alpha=1.0).fit(a_train, b_train)
    return m.predict(a_test)


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
    ap.add_argument("--anchors", type=int, default=16)
    ap.add_argument("--budgets", type=int, nargs="+", default=[1, 2, 4, 8])
    ap.add_argument("--grid-points", type=int, default=8)
    ap.add_argument("--lens-sizes", type=int, nargs="+", default=None)
    ap.add_argument("--output", type=Path, default=Path("pontifex-inverse-backprojection.json"))
    args = ap.parse_args()

    data = np.load(args.field_store, allow_pickle=False)
    if "original_b" not in data.files:
        raise RuntimeError("field store lacks original_b")

    ids, keys, a_field, _ = load_profiles(args.field_store, grid_points=args.grid_points)
    if args.lens_sizes is not None:
        wanted = set(int(x) for x in args.lens_sizes)
        keep = np.asarray([int(size) in wanted for _, size in keys], dtype=bool)
        keys = [k for k, ok in zip(keys, keep) if ok]
        a_field = a_field[:, keep]
        if not keys:
            raise RuntimeError(f"no requested lens sizes present: {sorted(wanted)}")
    b_embed = data["original_b"].astype(float)
    positions, _ = center_groups(keys)

    records = []
    for seed in args.seeds:
        rng = np.random.default_rng(seed)
        order = np.arange(len(ids))
        rng.shuffle(order)
        cut = max(4, int(args.train_frac * len(order)))
        tr, te = order[:cut], order[cut:]
        a_tr, a_te = a_field[tr], a_field[te]
        b_tr, b_te = b_embed[tr], b_embed[te]

        terrain = TerrainBackprojector(alpha=1.0, anchors=args.anchors).fit(a_tr, b_tr)

        # Capacity control: unconstrained direct vector regression.
        pred_direct = direct_ridge(a_tr, b_tr, a_te)
        records.append({
            "seed": int(seed),
            "method": "direct_A_profile_to_B_embedding_ridge",
            "budget_centers": len(positions),
            "scalar_probe_count": int(a_te.shape[1]),
            **evaluate(b_te, pred_direct),
        })

        # Canonical no-terrain prior: barycenter from target anchors with no emitted
        # probe deviations.
        pred0, _, _ = terrain.backproject(a_te, np.asarray([], dtype=int))
        records.append({
            "seed": int(seed),
            "method": "canonical_prior_only",
            "budget_centers": 0,
            "scalar_probe_count": 0,
            **evaluate(b_te, pred0),
        })

        for mode in ("smallest_lens", "all_lenses"):
            for budget in args.budgets:
                centers = uniform_centers(positions, budget)
                idx = feature_indices(keys, centers, mode)
                pred, mass, regional = terrain.backproject(a_te, idx)
                records.append({
                    "seed": int(seed),
                    "method": f"inverse_backprojection_{mode}",
                    "budget_centers": int(len(centers)),
                    "scalar_probe_count": int(len(idx)),
                    "selected_centers": [float(x) for x in centers],
                    "regional_entropy_mean": float(
                        np.mean(-np.sum(mass * np.log(np.clip(mass, 1e-12, None)), axis=1))
                    ),
                    **evaluate(b_te, pred),
                })

    summary = {}
    keys_group = sorted(set((r["method"], r["budget_centers"]) for r in records))
    metrics = ("cosine_similarity", "normalized_rmse", "retrieval_top1", "neighbor_overlap")
    for method, budget in keys_group:
        rs = [r for r in records if r["method"] == method and r["budget_centers"] == budget]
        block = {}
        for metric in metrics:
            vals = np.asarray([r[metric] for r in rs], dtype=float)
            block[metric] = {
                "mean": float(vals.mean()),
                "median": float(np.median(vals)),
                "std": float(vals.std(ddof=1)) if len(vals) > 1 else 0.0,
            }
        block["scalar_probe_count"] = int(rs[0]["scalar_probe_count"])
        summary[f"{method}|B={budget}"] = block

    result = {
        "experiment": "Pontifex inverse light backprojection to synthetic B embedding",
        "pipeline": (
            "occlusion center -> cheap-space light -> K_G inverse terrain propagation -> "
            "regional accumulation -> barycentric B embedding"
        ),
        "field_store": str(args.field_store),
        "texts": int(len(ids)),
        "positions": positions,
        "lens_sizes": sorted(set(int(s) for _, s in keys)),
        "grid_points": int(args.grid_points),
        "anchors": args.anchors,
        "train_fraction": args.train_frac,
        "seeds": args.seeds,
        "budgets": args.budgets,
        "records": records,
        "summary": summary,
        "interpretation_contract": {
            "budget_centers": "number of occlusion centers visited while walking the text",
            "smallest_lens": "one size=1 response emitted per center",
            "all_lenses": "all available lens responses emitted at each visited center",
            "kernel": "learned probe-to-B-region transport operator; no direct B-vector coefficients",
            "barycentric_reconstruction": "synthetic B vector is formed only from accumulated regional light over B anchors",
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
