# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
# ]
# ///
"""Test whether useful quadratic transport interactions have Fourier topology.

The preceding quadratic-term ablation found that cross terms x_i*x_j explain nearly
all of the degree-2 gain over linear transport, while tiny screened subsets do not.
This experiment asks a sharper question: are those useful interactions distributed
arbitrarily, or do they respect the topology of the Fourier response coordinates?

With H=8, the standardized A-response is represented by 17 coefficients:
DC, then sin/cos pairs for harmonics 1..8. Among the 120 harmonic-harmonic cross
terms, exactly 36 couple coefficients from the same or adjacent harmonic frequency
(|h_i-h_j| <= 1). We compare that deterministic local-frequency graph against:

- linear transport (no cross terms);
- a capacity-matched nonlocal graph: the 36 harmonic pairs with largest frequency gap;
- repeated capacity-matched random harmonic graphs (36 edges each);
- all 136 cross terms (including DC couplings), as the prior high-capacity ceiling.

All graph definitions are label-free. Ridge alpha is chosen using training texts only.
Whole held-out texts remain untouched until final scoring. Random graph draws are
fixed by outer seed and replicate id.

Interpretation boundary: beating matched random graphs would support compact topology
in this Fourier parametrization. It would *not* establish that semantic space is a
torus, that Fourier coordinates are uniquely correct, or that the future Pontifex
assembly/student benchmark has been solved. This diagnostic uses only the synthetic
pairwise-cartography field and never accesses D_assembly/D_student/D_val/D_test.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

from quadratic_term_ablation import choose_alpha, cross_matrix, pair_indices
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


def fourier_feature_metadata(harmonics: int) -> tuple[np.ndarray, np.ndarray]:
    """Return frequency and phase-family metadata matching fourier_basis column order."""
    freq = [0]
    phase = ["dc"]
    for h in range(1, int(harmonics) + 1):
        freq.extend([h, h])
        phase.extend(["sin", "cos"])
    return np.asarray(freq, dtype=int), np.asarray(phase, dtype=object)


def topology_indices(d: int, harmonics: int, budget: int) -> dict[str, np.ndarray]:
    freq, _phase = fourier_feature_metadata(harmonics)
    if len(freq) != d:
        raise ValueError(f"feature dimension {d} does not match 1+2*harmonics={len(freq)}")

    ii, jj = pair_indices(d)
    harmonic = (freq[ii] > 0) & (freq[jj] > 0)
    gap = np.abs(freq[ii] - freq[jj])
    harmonic_idx = np.flatnonzero(harmonic)
    local_idx = np.flatnonzero(harmonic & (gap <= 1))

    if len(local_idx) != budget:
        raise ValueError(
            f"expected local-frequency graph to have budget={budget} edges, got {len(local_idx)}; "
            "adjust --edge-budget or --harmonics"
        )
    if budget > len(harmonic_idx):
        raise ValueError("edge budget exceeds harmonic-harmonic pair count")

    # Stable deterministic ordering: larger frequency gap first, then original pair order.
    nonlocal_order = harmonic_idx[np.argsort(-gap[harmonic_idx], kind="stable")]
    nonlocal_idx = nonlocal_order[:budget]

    return {
        "local_frequency": local_idx,
        "nonlocal_frequency": nonlocal_idx,
        "harmonic_pool": harmonic_idx,
        "all_cross": np.arange(len(ii), dtype=int),
    }


def model_row(
    *,
    seed: int,
    source: str,
    method: str,
    xtr: np.ndarray,
    xte: np.ndarray,
    train_affin: np.ndarray,
    true_test_affin: np.ndarray,
    affinity_decoder: Ridge,
    bte: np.ndarray,
    alphas: list[float],
    actual_probe_count_mean: float,
    extra_terms: int,
    graph_rep: int | None = None,
) -> dict:
    alpha = choose_alpha(xtr, train_affin, alphas, seed + 10_000 * (0 if graph_rep is None else graph_rep + 1))
    model = Ridge(alpha=alpha).fit(xtr, train_affin)
    pred_affin = model.predict(xte)
    row = {
        "seed": int(seed),
        "source": source,
        "method": method,
        "graph_rep": None if graph_rep is None else int(graph_rep),
        "actual_probe_count_mean": float(actual_probe_count_mean),
        "selected_alpha": float(alpha),
        "feature_dim": int(xtr.shape[1]),
        "extra_terms": int(extra_terms),
        "model_state_scalars": int(xtr.shape[1] * train_affin.shape[1] + train_affin.shape[1]),
        **affinity_metrics(true_test_affin, pred_affin),
        **evaluate(bte, affinity_decoder.predict(pred_affin)),
    }
    return row


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
        "feature_dim",
        "model_state_scalars",
    )
    out: dict[str, dict] = {}
    for source, method in sorted(set((r["source"], r["method"]) for r in records)):
        rs = [r for r in records if r["source"] == source and r["method"] == method]
        block: dict[str, object] = {
            "n": len(rs),
            "extra_terms": int(rs[0]["extra_terms"]),
            "actual_probe_count_mean": float(np.mean([r["actual_probe_count_mean"] for r in rs])),
            "selected_alpha_values": [float(r["selected_alpha"]) for r in rs],
        }
        for metric in metrics:
            vals = np.asarray([r[metric] for r in rs], dtype=float)
            block[metric] = {
                "mean": float(np.mean(vals)),
                "median": float(np.median(vals)),
                "std": float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0,
            }
        out[f"{source}|{method}"] = block
    return out


def matched_random_comparison(records: list[dict]) -> dict:
    """Compare local-frequency graph with same-seed random graph distribution."""
    out: dict[str, dict] = {}
    for source in sorted(set(r["source"] for r in records)):
        per_seed = []
        for seed in sorted(set(r["seed"] for r in records if r["source"] == source)):
            local = next(
                r for r in records
                if r["source"] == source and r["seed"] == seed and r["method"] == "local_frequency"
            )
            randoms = [
                r for r in records
                if r["source"] == source and r["seed"] == seed and r["method"] == "random_harmonic"
            ]
            rr = np.asarray([r["affinity_rmse"] for r in randoms], dtype=float)
            rn = np.asarray([r["neighbor_overlap"] for r in randoms], dtype=float)
            per_seed.append({
                "seed": int(seed),
                "local_affinity_rmse": float(local["affinity_rmse"]),
                "random_affinity_rmse_mean": float(np.mean(rr)),
                "random_affinity_rmse_std": float(np.std(rr, ddof=1)) if len(rr) > 1 else 0.0,
                "fraction_random_rmse_beaten_by_local": float(np.mean(local["affinity_rmse"] < rr)),
                "local_neighbor_overlap": float(local["neighbor_overlap"]),
                "random_neighbor_overlap_mean": float(np.mean(rn)),
                "random_neighbor_overlap_std": float(np.std(rn, ddof=1)) if len(rn) > 1 else 0.0,
                "fraction_random_overlap_beaten_by_local": float(np.mean(local["neighbor_overlap"] > rn)),
            })
        out[source] = {"per_seed": per_seed}
    return out


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
    ap.add_argument("--edge-budget", type=int, default=36)
    ap.add_argument("--random-reps", type=int, default=12)
    ap.add_argument("--alphas", type=float, nargs="+", default=[0.1, 1.0, 10.0])
    ap.add_argument("--output", type=Path, default=Path("pontifex-interaction-topology-ablation.json"))
    args = ap.parse_args()

    d, ids, profiles = raw_size1_profiles(args.field_store)
    b_embed = d["original_b"].astype(float)
    dense_grid = np.linspace(0.0, 1.0, args.dense_train_grid, endpoint=False)
    basis = fourier_basis(dense_grid, args.harmonics)
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
        train_sparse, _ = infer_features(
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
            ii, jj = pair_indices(xtr.shape[1])
            ctr = cross_matrix(xtr, ii, jj)
            cte = cross_matrix(xte, ii, jj)
            topo = topology_indices(xtr.shape[1], args.harmonics, args.edge_budget)

            records.append(model_row(
                seed=seed, source=source, method="linear", xtr=xtr, xte=xte,
                train_affin=train_affin, true_test_affin=true_test_affin,
                affinity_decoder=affinity_decoder, bte=bte, alphas=args.alphas,
                actual_probe_count_mean=count, extra_terms=0,
            ))

            for method in ("local_frequency", "nonlocal_frequency"):
                idx = topo[method]
                fxtr = np.concatenate([xtr, ctr[:, idx]], axis=1)
                fxte = np.concatenate([xte, cte[:, idx]], axis=1)
                records.append(model_row(
                    seed=seed, source=source, method=method, xtr=fxtr, xte=fxte,
                    train_affin=train_affin, true_test_affin=true_test_affin,
                    affinity_decoder=affinity_decoder, bte=bte, alphas=args.alphas,
                    actual_probe_count_mean=count, extra_terms=len(idx),
                ))

            all_idx = topo["all_cross"]
            records.append(model_row(
                seed=seed, source=source, method="all_cross", 
                xtr=np.concatenate([xtr, ctr[:, all_idx]], axis=1),
                xte=np.concatenate([xte, cte[:, all_idx]], axis=1),
                train_affin=train_affin, true_test_affin=true_test_affin,
                affinity_decoder=affinity_decoder, bte=bte, alphas=args.alphas,
                actual_probe_count_mean=count, extra_terms=len(all_idx),
            ))

            pool = topo["harmonic_pool"]
            for rep in range(args.random_reps):
                rg = np.random.default_rng(seed * 1_000_003 + rep * 97_409 + 71_771)
                idx = np.sort(rg.choice(pool, size=args.edge_budget, replace=False))
                records.append(model_row(
                    seed=seed, source=source, method="random_harmonic",
                    xtr=np.concatenate([xtr, ctr[:, idx]], axis=1),
                    xte=np.concatenate([xte, cte[:, idx]], axis=1),
                    train_affin=train_affin, true_test_affin=true_test_affin,
                    affinity_decoder=affinity_decoder, bte=bte, alphas=args.alphas,
                    actual_probe_count_mean=count, extra_terms=len(idx), graph_rep=rep,
                ))

    freq, phase = fourier_feature_metadata(args.harmonics)
    ii, jj = pair_indices(len(freq))
    topo = topology_indices(len(freq), args.harmonics, args.edge_budget)
    result = {
        "experiment": "Pontifex Fourier interaction-topology ablation",
        "field_store": str(args.field_store),
        "seeds": args.seeds,
        "train_fraction": args.train_frac,
        "real_probe_budget": args.real_probes,
        "virtual_steps": args.virtual_steps,
        "dense_train_grid": args.dense_train_grid,
        "harmonics": args.harmonics,
        "anchors_requested": args.anchors,
        "edge_budget": args.edge_budget,
        "random_reps": args.random_reps,
        "alphas": args.alphas,
        "graph": {
            "feature_frequencies": freq.tolist(),
            "feature_phase_family": phase.tolist(),
            "pair_count_all": int(len(ii)),
            "pair_count_harmonic_only": int(len(topo["harmonic_pool"])),
            "local_rule": "both harmonic and abs(f_i-f_j)<=1",
            "local_edge_count": int(len(topo["local_frequency"])),
            "nonlocal_rule": "same edge budget, harmonic pairs sorted by descending abs(f_i-f_j)",
            "nonlocal_edge_count": int(len(topo["nonlocal_frequency"])),
        },
        "protocol": {
            "outer_split": "whole-text train/test split per seed",
            "selection": "Ridge alpha selected using training texts only; graph definitions use no labels",
            "matched_test": "local, nonlocal, and every random graph contain the same number of cross edges",
            "random_control": "random graphs sampled only from harmonic-harmonic pairs",
            "evidence_boundary": "synthetic pairwise cartography only; no D_assembly/D_student/D_val/D_test benchmark data",
        },
        "summary": summarize(records),
        "matched_random_comparison": matched_random_comparison(records),
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({
        "summary": result["summary"],
        "matched_random_comparison": result["matched_random_comparison"],
    }, indent=2))


if __name__ == "__main__":
    main()
