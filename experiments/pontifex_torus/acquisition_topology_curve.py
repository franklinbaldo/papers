# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
# ]
# ///
"""Test whether Fourier-local interaction evidence emerges as acquisition improves.

The previous topology ablation found a weak local-frequency advantage with the full
stored A response, but no advantage at K=8 on short texts. That comparison was
confounded because the short corpus had only about ten observable positions per text.

This experiment uses a separately built longer synthetic field and freezes, per outer
seed, the train/test split, B anchors, graph definitions, random graph controls, and
decoder. Only the A-side acquisition budget changes. K is swept from 4 to 24, plus an
`observed_full` condition using every stored A observation for that text.

A monotone increase in local-vs-random advantage as K rises would support the narrow
hypothesis that sparse acquisition masks a latent Fourier-local relation. Failure to
show such a curve argues that the earlier full-response enrichment was weak or
non-structural. Neither outcome establishes toroidal semantic geometry.

This is a synthetic pairwise-cartography diagnostic only. It does not instantiate or
access D_assembly, D_student, D_val, or D_test.
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
    infer_features,
    normalize,
    raw_size1_profiles,
    source_stats,
)


def fit_row(
    *, seed: int, budget_label: str, actual_count: float, method: str,
    xtr: np.ndarray, xte: np.ndarray, train_affin: np.ndarray,
    true_test_affin: np.ndarray, decoder: Ridge, bte: np.ndarray,
    alphas: list[float], graph_rep: int | None = None,
) -> dict:
    salt = 0 if graph_rep is None else graph_rep + 1
    alpha = choose_alpha(xtr, train_affin, alphas, seed + 100_003 * salt)
    model = Ridge(alpha=alpha).fit(xtr, train_affin)
    pred_affin = model.predict(xte)
    return {
        "seed": int(seed),
        "budget": budget_label,
        "actual_probe_count_mean": float(actual_count),
        "method": method,
        "graph_rep": None if graph_rep is None else int(graph_rep),
        "selected_alpha": float(alpha),
        "feature_dim": int(xtr.shape[1]),
        **affinity_metrics(true_test_affin, pred_affin),
        **evaluate(bte, decoder.predict(pred_affin)),
    }


def summarize(records: list[dict]) -> dict:
    metrics = ("affinity_rmse", "retrieval_top1", "neighbor_overlap")
    out: dict[str, dict] = {}
    groups = sorted(set((r["budget"], r["method"]) for r in records))
    for budget, method in groups:
        rs = [r for r in records if r["budget"] == budget and r["method"] == method]
        block = {
            "n": len(rs),
            "actual_probe_count_mean": float(np.mean([r["actual_probe_count_mean"] for r in rs])),
        }
        for metric in metrics:
            vals = np.asarray([r[metric] for r in rs], dtype=float)
            block[metric] = {
                "mean": float(np.mean(vals)),
                "std": float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0,
            }
        out[f"{budget}|{method}"] = block
    return out


def local_random_curve(records: list[dict], ordered_budgets: list[str]) -> dict:
    per_budget: dict[str, dict] = {}
    for budget in ordered_budgets:
        seed_rows = []
        for seed in sorted(set(r["seed"] for r in records)):
            local = next(r for r in records if r["seed"] == seed and r["budget"] == budget and r["method"] == "local_frequency")
            randoms = [r for r in records if r["seed"] == seed and r["budget"] == budget and r["method"] == "random_harmonic"]
            random_rmse = float(np.mean([r["affinity_rmse"] for r in randoms]))
            random_overlap = float(np.mean([r["neighbor_overlap"] for r in randoms]))
            seed_rows.append({
                "seed": int(seed),
                "actual_probe_count_mean": float(local["actual_probe_count_mean"]),
                "rmse_advantage_random_minus_local": float(random_rmse - local["affinity_rmse"]),
                "overlap_advantage_local_minus_random": float(local["neighbor_overlap"] - random_overlap),
                "fraction_random_rmse_beaten": float(np.mean([local["affinity_rmse"] < r["affinity_rmse"] for r in randoms])),
                "fraction_random_overlap_beaten": float(np.mean([local["neighbor_overlap"] > r["neighbor_overlap"] for r in randoms])),
            })
        per_budget[budget] = {
            "per_seed": seed_rows,
            "actual_probe_count_mean": float(np.mean([r["actual_probe_count_mean"] for r in seed_rows])),
            "rmse_advantage_mean": float(np.mean([r["rmse_advantage_random_minus_local"] for r in seed_rows])),
            "overlap_advantage_mean": float(np.mean([r["overlap_advantage_local_minus_random"] for r in seed_rows])),
            "fraction_random_rmse_beaten_mean": float(np.mean([r["fraction_random_rmse_beaten"] for r in seed_rows])),
            "fraction_random_overlap_beaten_mean": float(np.mean([r["fraction_random_overlap_beaten"] for r in seed_rows])),
        }

    numeric = [b for b in ordered_budgets if b.startswith("K=")]
    x = np.asarray([per_budget[b]["actual_probe_count_mean"] for b in numeric], dtype=float)
    yr = np.asarray([per_budget[b]["rmse_advantage_mean"] for b in numeric], dtype=float)
    yo = np.asarray([per_budget[b]["overlap_advantage_mean"] for b in numeric], dtype=float)
    return {
        "by_budget": per_budget,
        "trend_over_sparse_budgets": {
            "rmse_advantage_pearson_with_probe_count": float(np.corrcoef(x, yr)[0, 1]) if len(x) > 1 else float("nan"),
            "overlap_advantage_pearson_with_probe_count": float(np.corrcoef(x, yo)[0, 1]) if len(x) > 1 else float("nan"),
            "rmse_advantage_consecutive_increase_fraction": float(np.mean(np.diff(yr) > 0)) if len(yr) > 1 else float("nan"),
            "overlap_advantage_consecutive_increase_fraction": float(np.mean(np.diff(yo) > 0)) if len(yo) > 1 else float("nan"),
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--field-store", type=Path, required=True)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    ap.add_argument("--train-frac", type=float, default=0.7)
    ap.add_argument("--real-probes", type=int, nargs="+", default=[4, 6, 8, 10, 12, 16, 24])
    ap.add_argument("--virtual-steps", type=int, default=128)
    ap.add_argument("--dense-train-grid", type=int, default=512)
    ap.add_argument("--harmonics", type=int, default=8)
    ap.add_argument("--anchors", type=int, default=128)
    ap.add_argument("--edge-budget", type=int, default=36)
    ap.add_argument("--random-reps", type=int, default=10)
    ap.add_argument("--alphas", type=float, nargs="+", default=[0.1, 1.0, 10.0])
    ap.add_argument("--output", type=Path, default=Path("pontifex-acquisition-topology-curve.json"))
    args = ap.parse_args()

    d, ids, profiles = raw_size1_profiles(args.field_store)
    b_embed = d["original_b"].astype(float)
    dense_grid = np.linspace(0.0, 1.0, args.dense_train_grid, endpoint=False)
    basis = fourier_basis(dense_grid, args.harmonics)
    records: list[dict] = []
    budget_labels = [f"K={k}" for k in args.real_probes] + ["observed_full"]

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
        state = {"mean_dense": mean_dense, "scale_dense": scale_dense}
        train_full = functional_features((train_dense - mean_dense[None, :]) / scale_dense[None, :], basis)
        test_full = functional_features((test_dense - mean_dense[None, :]) / scale_dense[None, :], basis)

        anchor_idx = farthest_anchors(btr, args.anchors)
        anchor_emb = normalize(btr[anchor_idx])
        train_affin = normalize(btr) @ anchor_emb.T
        true_test_affin = normalize(bte) @ anchor_emb.T
        decoder = Ridge(alpha=1.0).fit(train_affin, btr)

        conditions: list[tuple[str, np.ndarray, np.ndarray, float]] = []
        for k in args.real_probes:
            train_sparse, _train_counts = infer_features(profiles, tr, k, args.virtual_steps, dense_grid, state, args.harmonics)
            test_sparse, test_counts = infer_features(profiles, te, k, args.virtual_steps, dense_grid, state, args.harmonics)
            conditions.append((f"K={k}", train_sparse, test_sparse, float(np.mean(test_counts))))
        conditions.append((
            "observed_full", train_full, test_full,
            float(np.mean([len(profiles[int(i)][0]) for i in te])),
        ))

        for budget_label, xtr_raw, xte_raw, actual_count in conditions:
            scaler = StandardScaler().fit(xtr_raw)
            xtr = scaler.transform(xtr_raw)
            xte = scaler.transform(xte_raw)
            ii, jj = pair_indices(xtr.shape[1])
            ctr = cross_matrix(xtr, ii, jj)
            cte = cross_matrix(xte, ii, jj)
            topo = topology_indices(xtr.shape[1], args.harmonics, args.edge_budget)

            records.append(fit_row(
                seed=seed, budget_label=budget_label, actual_count=actual_count, method="linear",
                xtr=xtr, xte=xte, train_affin=train_affin, true_test_affin=true_test_affin,
                decoder=decoder, bte=bte, alphas=args.alphas,
            ))

            for method in ("local_frequency", "nonlocal_frequency"):
                idx = topo[method]
                records.append(fit_row(
                    seed=seed, budget_label=budget_label, actual_count=actual_count, method=method,
                    xtr=np.concatenate([xtr, ctr[:, idx]], axis=1),
                    xte=np.concatenate([xte, cte[:, idx]], axis=1),
                    train_affin=train_affin, true_test_affin=true_test_affin,
                    decoder=decoder, bte=bte, alphas=args.alphas,
                ))

            pool = topo["harmonic_pool"]
            for rep in range(args.random_reps):
                # Deliberately independent of K: the same graph draws are reused across the curve.
                rg = np.random.default_rng(seed * 1_000_003 + rep * 97_409 + 71_771)
                idx = np.sort(rg.choice(pool, size=args.edge_budget, replace=False))
                records.append(fit_row(
                    seed=seed, budget_label=budget_label, actual_count=actual_count, method="random_harmonic",
                    xtr=np.concatenate([xtr, ctr[:, idx]], axis=1),
                    xte=np.concatenate([xte, cte[:, idx]], axis=1),
                    train_affin=train_affin, true_test_affin=true_test_affin,
                    decoder=decoder, bte=bte, alphas=args.alphas, graph_rep=rep,
                ))

    metadata = {}
    if "metadata" in d:
        try:
            metadata = json.loads(str(d["metadata"].item()))
        except Exception:
            metadata = {"raw": str(d["metadata"].item())}

    result = {
        "experiment": "Pontifex acquisition-budget x interaction-topology curve on longer synthetic texts",
        "field_store": str(args.field_store),
        "field_metadata": metadata,
        "seeds": args.seeds,
        "train_fraction": args.train_frac,
        "real_probe_budgets": args.real_probes,
        "observed_full_definition": "all stored size-1 A observations for each text; not necessarily every token start",
        "virtual_steps": args.virtual_steps,
        "dense_train_grid": args.dense_train_grid,
        "harmonics": args.harmonics,
        "anchors_requested": args.anchors,
        "edge_budget": args.edge_budget,
        "random_reps": args.random_reps,
        "protocol": {
            "outer_split": "whole-text train/test split per seed; unchanged across acquisition budgets",
            "selection": "Ridge alpha selected only inside outer training texts",
            "graph_freeze": "local/nonlocal rules and random graph draws are fixed across K for a given outer seed",
            "anchor_freeze": "B anchors and diagnostic affinity decoder are fixed across K for a given outer seed",
            "evidence_boundary": "longer synthetic pairwise cartography only; no D_assembly/D_student/D_val/D_test data",
        },
        "summary": summarize(records),
        "local_vs_random_curve": local_random_curve(records, budget_labels),
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({
        "field_metadata": metadata,
        "local_vs_random_curve": result["local_vs_random_curve"],
    }, indent=2))


if __name__ == "__main__":
    main()
