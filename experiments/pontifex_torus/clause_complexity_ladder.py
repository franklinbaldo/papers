# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
# ]
# ///
"""Paired clause-complexity discriminant for Pontifex degree-2 transport.

The input stores must come from build_paired_clause_ladder.py. That makes c1..c4
nested prefixes of the same text families, adds a long repeat4 control, and fixes
the acquisition budget and relative probe coordinates across regimes.

We compare linear, all-cross, and full-degree-2 transport on identical whole-text
outer splits. All preprocessing, anchors, decoder fitting, and alpha selection are
training-only. This script never instantiates or reads D_assembly, D_student,
D_val, or D_test.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from transport_regime_contrast import run_corpus, summarize

KEEP = {"linear", "all_cross", "full_degree2"}


def regime_contrast(records: list[dict], corpus: str) -> dict:
    per_seed: list[dict] = []
    seeds = sorted({int(r["seed"]) for r in records if r["corpus"] == corpus})
    for seed in seeds:
        rows = {
            r["method"]: r
            for r in records
            if r["corpus"] == corpus and int(r["seed"]) == seed and r["method"] in KEEP
        }
        linear = rows["linear"]
        cross = rows["all_cross"]
        degree2 = rows["full_degree2"]
        per_seed.append(
            {
                "seed": seed,
                "all_cross_rmse_gain_vs_linear": float(linear["affinity_rmse"] - cross["affinity_rmse"]),
                "full_degree2_rmse_gain_vs_linear": float(linear["affinity_rmse"] - degree2["affinity_rmse"]),
                "all_cross_top1_gain_vs_linear": float(cross["retrieval_top1"] - linear["retrieval_top1"]),
                "full_degree2_top1_gain_vs_linear": float(degree2["retrieval_top1"] - linear["retrieval_top1"]),
                "all_cross_overlap_gain_vs_linear": float(cross["neighbor_overlap"] - linear["neighbor_overlap"]),
                "full_degree2_overlap_gain_vs_linear": float(degree2["neighbor_overlap"] - linear["neighbor_overlap"]),
            }
        )
    keys = [k for k in per_seed[0] if k != "seed"]
    return {
        "per_seed": per_seed,
        "means": {k: float(np.mean([x[k] for x in per_seed])) for k in keys},
        "positive_rmse_gain_seeds": {
            "all_cross": int(sum(x["all_cross_rmse_gain_vs_linear"] > 0 for x in per_seed)),
            "full_degree2": int(sum(x["full_degree2_rmse_gain_vs_linear"] > 0 for x in per_seed)),
            "total": len(per_seed),
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--store-dir", type=Path, required=True)
    ap.add_argument("--texts", type=int, default=800)
    ap.add_argument("--positions", type=int, default=8)
    ap.add_argument("--field-seed", type=int, default=20260918)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    ap.add_argument("--train-frac", type=float, default=0.7)
    ap.add_argument("--dense-train-grid", type=int, default=512)
    ap.add_argument("--harmonics", type=int, default=8)
    ap.add_argument("--anchors", type=int, default=256)
    ap.add_argument("--alphas", type=float, nargs="+", default=[0.1, 1.0, 10.0])
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    names = ["c1", "c2", "c3", "c4", "repeat4"]
    all_records: list[dict] = []
    metadata: dict[str, dict] = {}

    for name in names:
        store = args.store_dir / f"field-{name}-n{args.texts}-p{args.positions}-seed{args.field_seed}.npz"
        records, meta = run_corpus(
            corpus=name,
            field_store=store,
            seeds=args.seeds,
            train_frac=args.train_frac,
            dense_train_grid=args.dense_train_grid,
            harmonics=args.harmonics,
            anchors=args.anchors,
            edge_budget=36,
            random_reps=1,
            alphas=args.alphas,
        )
        all_records.extend(r for r in records if r["method"] in KEEP)
        metadata[name] = meta

    contrasts = {name: regime_contrast(all_records, name) for name in names}
    clause_counts = np.asarray([1.0, 2.0, 3.0, 4.0])
    cross_gains = np.asarray([
        contrasts[f"c{i}"]["means"]["all_cross_rmse_gain_vs_linear"] for i in range(1, 5)
    ])
    degree2_gains = np.asarray([
        contrasts[f"c{i}"]["means"]["full_degree2_rmse_gain_vs_linear"] for i in range(1, 5)
    ])

    trend = {
        "all_cross_gain_slope_per_added_clause": float(np.polyfit(clause_counts, cross_gains, 1)[0]),
        "full_degree2_gain_slope_per_added_clause": float(np.polyfit(clause_counts, degree2_gains, 1)[0]),
        "all_cross_gain_monotone_nonincreasing": bool(np.all(np.diff(cross_gains) <= 0)),
        "full_degree2_gain_monotone_nonincreasing": bool(np.all(np.diff(degree2_gains) <= 0)),
        "all_cross_gain_curve": {f"c{i}": float(cross_gains[i - 1]) for i in range(1, 5)},
        "full_degree2_gain_curve": {f"c{i}": float(degree2_gains[i - 1]) for i in range(1, 5)},
    }

    repeat_vs_independent = {}
    for model in ("all_cross", "full_degree2"):
        key = f"{model}_rmse_gain_vs_linear"
        repeat = contrasts["repeat4"]["means"][key]
        independent = contrasts["c4"]["means"][key]
        one_clause = contrasts["c1"]["means"][key]
        repeat_vs_independent[model] = {
            "repeat4_gain": float(repeat),
            "independent_c4_gain": float(independent),
            "c1_gain": float(one_clause),
            "repeat4_minus_independent_c4": float(repeat - independent),
            "repeat4_minus_c1": float(repeat - one_clause),
        }

    result = {
        "experiment": "Pontifex paired clause-complexity ladder and repeat-length control",
        "texts_per_regime": args.texts,
        "positions_per_text": args.positions,
        "field_seed": args.field_seed,
        "outer_seeds": args.seeds,
        "train_fraction": args.train_frac,
        "dense_train_grid": args.dense_train_grid,
        "harmonics": args.harmonics,
        "anchors_requested": args.anchors,
        "corpus_metadata": metadata,
        "protocol": {
            "pairing": "c1..c4 use nested prefixes of the same family index; repeat4 repeats c1 content",
            "acquisition": "exactly the same number of deterministic relative-position probes per text in every regime",
            "outer_split": "same family indices enter train/test for a given seed in every regime",
            "selection": "Ridge alpha selected only inside outer training texts",
            "preprocessing": "source statistics and StandardScaler fitted on outer training texts only",
            "anchors_decoder": "B anchors and diagnostic affinity decoder fitted from outer training texts only",
            "evidence_boundary": "synthetic pairwise cartography only; no D_assembly/D_student/D_val/D_test data",
        },
        "summary": summarize(all_records),
        "contrasts": contrasts,
        "clause_ladder_trend": trend,
        "repeat4_length_composition_control": repeat_vs_independent,
        "records": all_records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({
        "corpus_metadata": metadata,
        "clause_ladder_trend": trend,
        "repeat4_length_composition_control": repeat_vs_independent,
        "contrasts": contrasts,
    }, indent=2))


if __name__ == "__main__":
    main()
