# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
# ]
# ///
"""Sample-size-matched control for the Pontifex transport regime contrast.

The first short-vs-long contrast used all available texts: 2,000 one-clause texts
versus 800 four-clause texts. That makes input regime and number of training texts
move together. This control fixes both corpora at 800 texts before the outer split,
then repeats the full-response transport comparison.

The 800-text short subset is chosen once with a label-independent RNG seed and is
held fixed across outer seeds. Every learned quantity remains train-only inside each
outer split. This is synthetic pairwise cartography only; it does not instantiate or
read D_assembly, D_student, D_val, or D_test.
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
from transport_regime_contrast import fit_row, summarize, contrasts
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


def run_matched_corpus(
    *,
    corpus: str,
    field_store: Path,
    n_texts: int,
    subset_seed: int,
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
    if n_texts > len(ids):
        raise ValueError(f"requested {n_texts} texts from corpus with only {len(ids)}")

    if n_texts == len(ids):
        pool = np.arange(len(ids), dtype=int)
    else:
        subset_rng = np.random.default_rng(subset_seed)
        pool = np.sort(subset_rng.choice(len(ids), size=n_texts, replace=False))

    dense_grid = np.linspace(0.0, 1.0, dense_train_grid, endpoint=False)
    basis = fourier_basis(dense_grid, harmonics)
    records: list[dict] = []

    for seed in seeds:
        rng = np.random.default_rng(seed)
        order = pool.copy()
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
            xtr=xtr, xte=xte, train_affin=train_affin,
            true_test_affin=true_test_affin, decoder=decoder, bte=bte, alphas=alphas,
        ))

        local_idx = topo["local_frequency"]
        records.append(fit_row(
            corpus=corpus, seed=seed, method="local_frequency",
            xtr=np.concatenate([xtr, ctr[:, local_idx]], axis=1),
            xte=np.concatenate([xte, cte[:, local_idx]], axis=1),
            train_affin=train_affin, true_test_affin=true_test_affin,
            decoder=decoder, bte=bte, alphas=alphas,
        ))

        pool_edges = topo["harmonic_pool"]
        for rep in range(random_reps):
            rg = np.random.default_rng(seed * 1_000_003 + rep * 97_409 + 71_771)
            idx = np.sort(rg.choice(pool_edges, size=edge_budget, replace=False))
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
    metadata.update({
        "available_texts": int(len(ids)),
        "selected_texts": int(len(pool)),
        "subset_seed": None if n_texts == len(ids) else int(subset_seed),
        "observed_positions_mean_selected": float(np.mean([len(profiles[int(i)][0]) for i in pool])),
    })
    return records, metadata


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--short-store", type=Path, required=True)
    ap.add_argument("--long-store", type=Path, required=True)
    ap.add_argument("--texts", type=int, default=800)
    ap.add_argument("--subset-seed", type=int, default=20260918)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    ap.add_argument("--train-frac", type=float, default=0.7)
    ap.add_argument("--dense-train-grid", type=int, default=512)
    ap.add_argument("--harmonics", type=int, default=8)
    ap.add_argument("--anchors", type=int, default=256)
    ap.add_argument("--edge-budget", type=int, default=36)
    ap.add_argument("--random-reps", type=int, default=12)
    ap.add_argument("--alphas", type=float, nargs="+", default=[0.1, 1.0, 10.0])
    ap.add_argument("--output", type=Path, default=Path("pontifex-transport-regime-n-control.json"))
    args = ap.parse_args()

    records: list[dict] = []
    metadata: dict[str, dict] = {}
    for corpus, store in (("short_one_clause_nmatched", args.short_store), ("long_four_clause_nmatched", args.long_store)):
        rs, meta = run_matched_corpus(
            corpus=corpus,
            field_store=store,
            n_texts=args.texts,
            subset_seed=args.subset_seed,
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
        "experiment": "Pontifex sample-size-matched short-vs-long degree-2 transport control",
        "short_store": str(args.short_store),
        "long_store": str(args.long_store),
        "texts_per_corpus": args.texts,
        "short_subset_seed": args.subset_seed,
        "seeds": args.seeds,
        "train_fraction": args.train_frac,
        "dense_train_grid": args.dense_train_grid,
        "harmonics": args.harmonics,
        "anchors_requested": args.anchors,
        "edge_budget": args.edge_budget,
        "random_reps": args.random_reps,
        "corpus_metadata": metadata,
        "protocol": {
            "sample_count_control": "both corpora fixed at the same number of texts before outer splitting",
            "short_subset": "chosen once by label-independent RNG and frozen across outer seeds",
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
    print(json.dumps({"corpus_metadata": metadata, "contrasts": result["contrasts"]}, indent=2))


if __name__ == "__main__":
    main()
