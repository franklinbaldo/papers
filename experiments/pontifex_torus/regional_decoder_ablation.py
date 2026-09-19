# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
# ]
# ///
"""Discriminate transport loss from the regional/barycentric decoder bottleneck.

The previous 2,000-text anchor sweep showed that increasing B-side anchors beyond
~32 gives only small gains. This experiment keeps the same source representation,
splits, K=8 real probes and M=128 virtual integration, then decomposes the regional
pipeline into two stages:

    source Fourier features -> predicted anchor affinities -> B embedding

Four readouts separate distinct failure modes:

1. predicted affinities + softmax barycentric readout (current Torus decoder);
2. predicted affinities + learned affine decoder from affinity space to B;
3. oracle true B affinities + softmax barycentric readout;
4. oracle true B affinities + learned affine decoder.

The matched direct Fourier Ridge remains the same-input control. If (2) closes much
of the gap to direct Ridge while (1) does not, the barycentric positivity/simplex
constraint is a major bottleneck. If even (4) is weak, anchor-affinity coordinates
are themselves too lossy. If (4) is strong but (2) remains weak, transport from the
A-side source field into regional affinities is the dominant bottleneck.
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
    functional_features,
    fourier_basis,
    infer_features,
    normalize,
    raw_size1_profiles,
    region_to_embedding,
    source_stats,
)


def mean_block(records, method, anchors):
    rs = [r for r in records if r["method"] == method and r["anchors"] == anchors]
    metrics = ("cosine_similarity", "normalized_rmse", "retrieval_top1", "neighbor_overlap")
    block = {}
    for metric in metrics:
        vals = np.asarray([r[metric] for r in rs], dtype=float)
        block[metric] = {
            "mean": float(vals.mean()),
            "median": float(np.median(vals)),
            "std": float(vals.std(ddof=1)) if len(vals) > 1 else 0.0,
        }
    return block


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--field-store", type=Path, required=True)
    ap.add_argument("--seeds", type=int, nargs="+", default=list(range(10)))
    ap.add_argument("--train-frac", type=float, default=0.7)
    ap.add_argument("--real-probes", type=int, default=8)
    ap.add_argument("--virtual-steps", type=int, default=128)
    ap.add_argument("--dense-train-grid", type=int, default=512)
    ap.add_argument("--harmonics", type=int, default=8)
    ap.add_argument("--anchors", type=int, nargs="+", default=[16, 32, 128, 256])
    ap.add_argument("--output", type=Path, default=Path("pontifex-regional-decoder-ablation.json"))
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
        mean_dense, scale_dense = source_stats(train_dense)
        train_z = (train_dense - mean_dense[None, :]) / scale_dense[None, :]
        train_basis = fourier_basis(dense_grid, args.harmonics)
        train_feats = functional_features(train_z, train_basis)

        # Model-state shell used by infer_features; anchor-specific fields are not needed.
        source_state = {
            "mean_dense": mean_dense,
            "scale_dense": scale_dense,
        }
        test_feats, counts = infer_features(
            profiles,
            te,
            args.real_probes,
            args.virtual_steps,
            dense_grid,
            source_state,
            args.harmonics,
        )

        direct_model = Ridge(alpha=1.0).fit(train_feats, btr)
        pred_direct = direct_model.predict(test_feats)

        for anchor_count in args.anchors:
            anchor_idx = farthest_anchors(btr, anchor_count)
            anchor_emb = normalize(btr[anchor_idx])
            train_affin = normalize(btr) @ anchor_emb.T
            true_test_affin = normalize(bte) @ anchor_emb.T

            region_model = Ridge(alpha=1.0).fit(train_feats, train_affin)
            pred_affin = region_model.predict(test_feats)

            # Existing positive-simplex / barycentric regional decoder.
            pred_softmax, _ = region_to_embedding(pred_affin, anchor_emb)
            oracle_softmax, _ = region_to_embedding(true_test_affin, anchor_emb)

            # Less constrained decoder: the regional affinity coordinates remain the
            # bottleneck, but their readout may use signed learned combinations.
            affinity_decoder = Ridge(alpha=1.0).fit(train_affin, btr)
            pred_affine = affinity_decoder.predict(pred_affin)
            oracle_affine = affinity_decoder.predict(true_test_affin)

            methods = {
                "predicted_affinity_softmax_barycentric": pred_softmax,
                "predicted_affinity_learned_affine": pred_affine,
                "oracle_affinity_softmax_barycentric": oracle_softmax,
                "oracle_affinity_learned_affine": oracle_affine,
                "matched_direct_fourier_ridge": pred_direct,
            }
            for method, pred in methods.items():
                records.append({
                    "seed": int(seed),
                    "anchors": int(anchor_count),
                    "method": method,
                    "real_probe_count_mean": float(np.mean(counts)),
                    **evaluate(bte, pred),
                })

    methods = sorted(set(r["method"] for r in records))
    summary = {}
    for anchor_count in args.anchors:
        for method in methods:
            summary[f"A={anchor_count}|{method}"] = mean_block(records, method, anchor_count)

    result = {
        "experiment": "Pontifex regional decoder factorization ablation",
        "field_store": str(args.field_store),
        "seeds": args.seeds,
        "train_fraction": args.train_frac,
        "real_probes": args.real_probes,
        "virtual_steps": args.virtual_steps,
        "dense_train_grid": args.dense_train_grid,
        "harmonics": args.harmonics,
        "anchors": args.anchors,
        "records": records,
        "summary": summary,
        "interpretation_contract": {
            "predicted_affinity_softmax_barycentric": "current regional Torus readout; predicted anchor affinities converted to a positive simplex and averaged over anchors",
            "predicted_affinity_learned_affine": "same predicted regional affinities, but a learned signed affine decoder maps affinity coordinates to B; tests the barycentric readout constraint",
            "oracle_affinity_softmax_barycentric": "true held-out B-to-anchor affinities with the current barycentric readout; an oracle diagnostic, not a deployable method",
            "oracle_affinity_learned_affine": "true held-out B-to-anchor affinities with a learned decoder; upper-bound diagnostic for information retained by affinity coordinates",
            "matched_direct_fourier_ridge": "same sparse A-side source features mapped directly to B coordinates; matched-input control",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
