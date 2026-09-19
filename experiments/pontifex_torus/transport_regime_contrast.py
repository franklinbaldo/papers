# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
# ]
# ///
"""Discriminate topology failure from collapse of degree-2 transport signal.

The acquisition/topology curve produced opposite full-response behavior on the
original one-clause corpus and on a longer four-clause corpus. This experiment asks
whether the reversal is specifically about the proposed Fourier-local graph or
whether second-order transport itself stops helping in the longer regime.

For each corpus and outer seed we keep the whole-text train/test split, B anchors,
affinity decoder, scaling, and inner alpha selection isolated to training texts.
Using the observed A response only, we compare:

- linear transport;
- the 36-edge Fourier-local graph;
- repeated 36-edge random harmonic graphs;
- all cross terms x_i*x_j;
- the full degree-2 expansion (linear + squares + all cross terms).

If all-cross/full-degree-2 still beat linear on the longer corpus while the local
graph does not, the narrow topology hypothesis failed but nonlinear transport
survived. If degree-2 also loses to linear, the regime change is upstream of the
specific graph and the earlier local enrichment should not be generalized.

This is a synthetic pairwise-cartography diagnostic. It never instantiates or reads
D_assembly, D_student, D_val, or D_test.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

from interaction_topology_ablation import topology_indices
from quadratic_term_ablation import choose_alpha, cross_matrix, pair_indices
from transport_bottleneck_ablation import affinity_metrics
from virtual_resolution import (
    build_dense_training,
    evaluate,
    farthest_anchors,
    fourier_basis,
    functional_features,
    normalize,
    raw_size1_profiles,
    source_stats,
)


def fit_row(
    *,
    corpus: str,
    seed: int,
    method: str,
    xtr: np.ndarray,
    xte: np.ndarray,
    train_affin: np.ndarray,
    true_test_affin: np.ndarray,
    decoder: Ridge,
    bte: np.ndarray,
    alphas: list[float],
    graph_rep: int | None = None,
) -> dict:
    salt = 0 if graph_rep is None else graph_rep + 1
    alpha = choose_alpha(xtr, train_affin, alphas, seed + 100_003 * salt)
    model = Ridge(alpha=alpha).fit(xtr, train_affin)
    pred_affin = model.predict(xte)
    return {
        "corpus": corpus,
        "seed": int(seed),
        "method": method,
        "graph_rep": None if graph_rep is None else int(graph_rep),
        "selected_alpha": float(alpha),
        "feature_dim": int(xtr.shape[1]),
        "model_state_scalars": int(xtr.shape[1] * train_affin.shape[1] + train_affin.shape[1]),
        **affinity_metrics(true_test_affin, pred_affin),
        **evaluate(bte, decoder.predict(pred_affin)),
    }


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
    out: dict[str, dict] = {}
    groups = sorted(set((r["corpus"], r["method"]) for r in records))
    for corpus, method in groups:
        rs = [r for r in records if r["corpus"] == corpus and r["method"] == method]
        block: dict[str, object] = {
            "n": len(rs),
            "feature_dim": int(rs[0]["feature_dim"]),
            "model_state_scalars": int(rs[0]["model_state_scalars"]),
            "selected_alpha_values": [float(r["selected_alpha"]) for r in rs],
        }
        for metric in metrics:
            vals = np.asarray([r[metric] for r in rs], dtype=float)
            block[metric] = {
                "mean": float(np.mean(vals)),
                "std": float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0,
            }
        out[f"{corpus}|{method}"] = block
    return out


def contrasts(records: list[dict]) -> dict:
    out: dict[str, dict] = {}
    for corpus in sorted(set(r["corpus"] for r in records)):
        per_seed = []
        for seed in sorted(set(r["seed"] for r in records if r["corpus"] == corpus)):
            rows = [r for r in records if r["corpus"] == corpus and r["seed"] == seed]
            linear = next(r for r in rows if r["method"] == "linear")
            local = next(r for r in rows if r["method"] == "local_frequency")
            all_cross = next(r for r in rows if r["method"] == "all_cross")
            degree2 = next(r for r in rows if r["method"] == "full_degree2")
            randoms = [r for r in rows if r["method"] == "random_harmonic"]
            random_rmse = float(np.mean([r["affinity_rmse"] for r in randoms]))
            random_overlap = float(np.mean([r["neighbor_overlap"] for r in randoms]))
            per_seed.append({
                "seed": int(seed),
                "local_rmse_gain_vs_linear": float(linear["affinity_rmse"] - local["affinity_rmse"]),
                "all_cross_rmse_gain_vs_linear": float(linear["affinity_rmse"] - all_cross["affinity_rmse"]),
                "full_degree2_rmse_gain_vs_linear": float(linear["affinity_rmse"] - degree2["affinity_rmse"]),
                "local_overlap_gain_vs_linear": float(local["neighbor_overlap"] - linear["neighbor_overlap"]),
                "all_cross_overlap_gain_vs_linear": float(all_cross["neighbor_overlap"] - linear["neighbor_overlap"]),
                "full_degree2_overlap_gain_vs_linear": float(degree2["neighbor_overlap"] - linear["neighbor_overlap"]),
                "local_rmse_advantage_vs_random": float(random_rmse - local["affinity_rmse"]),
                "local_overlap_advantage_vs_random": float(local["neighbor_overlap"] - random_overlap),
                "fraction_random_rmse_beaten_by_local": float(np.mean([local["affinity_rmse"] < r["affinity_rmse"] for r in randoms])),
                "fraction_random_overlap_beaten_by_local": float(np.mean([local["neighbor_overlap"] > r["neighbor_overlap"] for r in randoms])),
            })
        keys = [k for k in per_seed[0] if k != "seed"]
        out[corpus] = {
            "per_seed": per_seed,
            "means": {k: float(np.mean([r[k] for r in per_seed])) for k in keys},
        }
    return out


def run_corpus(
    *,
    corpus: str,
    field_store: Path,
    seeds: list[int],
    train_frac: float,
    dense_train_grid: int,
    harmonics: int,
    anchors: int,
    edge_budget: int,
    random_reps: int,
    alphas: list[float],
) -> tuple[list[dict], dict]:
    d, ids, profiles = raw_size1_profiles(field_store)
    b_embed = d["original_b"].astype(float)
    dense_grid = np.linspace(0.0, 1.0, dense_train_grid, endpoint=False)
    basis = fourier_basis(dense_grid, harmonics)
    records: list[dict] = []

    for seed in seeds:
        rng = np.random.default_rng(seed)
        order = np.arange(len(ids))
        rng.shuffle(order)
        cut = max(4, int(train_frac * len(order)))
        tr, te = order[:cut], order[cut:]
        btr, bte = b_embed[tr], b_embed[te]

        train_dense = build_dense_training(profiles, tr, dense_grid)
        test_dense = build_dense_training(profiles, te, dense_grid)
        mean_dense, scale_dense = source_stats(train_dense)
        train_full = functional_features((train_dense - mean_dense[None, :]) / scale_dense[None, :], basis)
        test_full = functional_features((test_dense - mean_dense[None, :]) / scale_dense[None, :], basis)

        scaler = StandardScaler().fit(train_full)
        xtr = scaler.transform(train_full)
        xte = scaler.transform(test_full)

        anchor_idx = farthest_anchors(btr, anchors)
        anchor_emb = normalize(btr[anchor_idx])
        train_affin = normalize(btr) @ anchor_emb.T
        true_test_affin = normalize(bte) @ anchor_emb.T
        decoder = Ridge(alpha=1.0).fit(train_affin, btr)

        ii, jj = pair_indices(xtr.shape[1])
        ctr = cross_matrix(xtr, ii, jj)
        cte = cross_matrix(xte, ii, jj)
        squares_tr = xtr * xtr
        squares_te = xte * xte
        topo = topology_indices(xtr.shape[1], harmonics, edge_budget)

        records.append(fit_row(
            corpus=corpus, seed=seed, method="linear",
            xtr=xtr, xte=xte, train_affin=train_affin, true_test_affin=true_test_affin,
            decoder=decoder, bte=bte, alphas=alphas,
        ))

        local_idx = topo["local_frequency"]
        records.append(fit_row(
            corpus=corpus, seed=seed, method="local_frequency",
            xtr=np.concatenate([xtr, ctr[:, local_idx]], axis=1),
            xte=np.concatenate([xte, cte[:, local_idx]], axis=1),
            train_affin=train_affin, true_test_affin=true_test_affin,
            decoder=decoder, bte=bte, alphas=alphas,
        ))

        pool = topo["harmonic_pool"]
        for rep in range(random_reps):
            rg = np.random.default_rng(seed * 1_000_003 + rep * 97_409 + 71_771)
            idx = np.sort(rg.choice(pool, size=edge_budget, replace=False))
            records.append(fit_row(
                corpus=corpus, seed=seed, method="random_harmonic",
                xtr=np.concatenate([xtr, ctr[:, idx]], axis=1),
                xte=np.concatenate([xte, cte[:, idx]], axis=1),
                train_affin=train_affin, true_test_affin=true_test_affin,
                decoder=decoder, bte=bte, alphas=alphas, graph_rep=rep,
            ))

        all_idx = topo["all_cross"]
        records.append(fit_row(
            corpus=corpus, seed=seed, method="all_cross",
            xtr=np.concatenate([xtr, ctr[:, all_idx]], axis=1),
            xte=np.concatenate([xte, cte[:, all_idx]], axis=1),
            train_affin=train_affin, true_test_affin=true_test_affin,
            decoder=decoder, bte=bte, alphas=alphas,
        ))
        records.append(fit_row(
            corpus=corpus, seed=seed, method="full_degree2",
            xtr=np.concatenate([xtr, squares_tr, ctr[:, all_idx]], axis=1),
            xte=np.concatenate([xte, squares_te, cte[:, all_idx]], axis=1),
            train_affin=train_affin, true_test_affin=true_test_affin,
            decoder=decoder, bte=bte, alphas=alphas,
        ))

    metadata: dict = {}
    if "metadata" in d:
        try:
            metadata = json.loads(str(d["metadata"].item()))
        except Exception:
            metadata = {"raw": str(d["metadata"].item())}
    metadata["observed_positions_mean"] = float(np.mean([len(profiles[int(i)][0]) for i in ids]))
    return records, metadata


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--short-store", type=Path, required=True)
    ap.add_argument("--long-store", type=Path, required=True)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    ap.add_argument("--train-frac", type=float, default=0.7)
    ap.add_argument("--dense-train-grid", type=int, default=512)
    ap.add_argument("--harmonics", type=int, default=8)
    ap.add_argument("--anchors", type=int, default=256)
    ap.add_argument("--edge-budget", type=int, default=36)
    ap.add_argument("--random-reps", type=int, default=12)
    ap.add_argument("--alphas", type=float, nargs="+", default=[0.1, 1.0, 10.0])
    ap.add_argument("--output", type=Path, default=Path("pontifex-transport-regime-contrast.json"))
    args = ap.parse_args()

    records: list[dict] = []
    metadata: dict[str, dict] = {}
    for corpus, store in (("short_one_clause", args.short_store), ("long_four_clause", args.long_store)):
        rs, meta = run_corpus(
            corpus=corpus,
            field_store=store,
            seeds=args.seeds,
            train_frac=args.train_frac,
            dense_train_grid=args.dense_train_grid,
            harmonics=args.harmonics,
            anchors=args.anchors,
            edge_budget=args.edge_budget,
            random_reps=args.random_reps,
            alphas=args.alphas,
        )
        records.extend(rs)
        metadata[corpus] = meta

    result = {
        "experiment": "Pontifex short-vs-long degree-2 transport regime contrast",
        "short_store": str(args.short_store),
        "long_store": str(args.long_store),
        "seeds": args.seeds,
        "train_fraction": args.train_frac,
        "dense_train_grid": args.dense_train_grid,
        "harmonics": args.harmonics,
        "anchors_requested": args.anchors,
        "edge_budget": args.edge_budget,
        "random_reps": args.random_reps,
        "corpus_metadata": metadata,
        "protocol": {
            "outer_split": "whole-text train/test split per corpus and seed",
            "selection": "Ridge alpha selected only inside outer training texts",
            "preprocessing": "dense source statistics and StandardScaler fitted on training texts only",
            "anchors_decoder": "B anchors and diagnostic affinity decoder fitted from training texts only",
            "graph_controls": "local graph deterministic; random graphs capacity-matched and seeded independently of labels",
            "evidence_boundary": "synthetic pairwise cartography only; no D_assembly/D_student/D_val/D_test data",
        },
        "summary": summarize(records),
        "contrasts": contrasts(records),
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({
        "corpus_metadata": metadata,
        "contrasts": result["contrasts"],
    }, indent=2))


if __name__ == "__main__":
    main()
