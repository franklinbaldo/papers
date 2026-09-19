# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
# ]
# ///
"""Test whether the tiny c4 interaction signal depends on atlas/train overlap.

Earlier c4 experiments build the B-side anchor dictionary from outer-train B
embeddings.  This is not outer-test leakage, but it means some of the same paired
families both define the output coordinate system and train the A→B transport.
This ablation asks a narrower robustness question: does the cross-interaction gain
survive when the B atlas is built from a pool that is disjoint from both transport
training families and outer-test families?

For every outer seed we hold the A-side transport train/test split fixed and compare
two equal-size B atlases with the same number of anchors:

* shared: atlas candidates are a deterministic subset of transport-training B;
* disjoint: atlas candidates come from an auxiliary B-only pool disjoint from both
  transport train and outer test.

The two coordinate systems are different, so absolute RMSE is not compared across
atlas protocols.  The primary estimand is the within-protocol held-out gain of the
inner-selected interaction model over its linear baseline, followed by the paired
difference of those gains across outer seeds.

The disjoint protocol consumes extra B-only observations and therefore is a
separation/robustness control, not a total-data-efficiency comparison.  All model
selection remains inside transport outer-train.  This is synthetic pairwise
cartography only and never instantiates, tunes on, or reads D_assembly, D_student,
D_val, or D_test.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.preprocessing import StandardScaler

from c4_interaction_signal_curve import fit_candidate, rmse, select_candidate
from quadratic_term_ablation import cross_matrix, pair_indices
from virtual_resolution import (
    build_dense_training,
    farthest_anchors,
    fourier_basis,
    functional_features,
    normalize,
    raw_size1_profiles,
    source_stats,
)


def selected_score(
    xtr: np.ndarray,
    ctr: np.ndarray,
    ytr: np.ndarray,
    xte: np.ndarray,
    cte: np.ndarray,
    yte: np.ndarray,
    *,
    linear_penalties: list[float],
    cross_penalties: list[float | None],
    seed: int,
) -> tuple[dict, float]:
    best, _ = select_candidate(
        xtr,
        ctr,
        ytr,
        linear_penalties=linear_penalties,
        cross_penalties=cross_penalties,
        seed=seed,
    )
    lp = float(best["linear_penalty"])
    cp_raw = best["cross_penalty"]
    cp = None if cp_raw is None else float(cp_raw)
    _, pred = fit_candidate(
        xtr,
        ctr,
        ytr,
        xte,
        cte,
        linear_penalty=lp,
        cross_penalty=cp,
    )
    return {
        "linear_penalty": lp,
        "cross_penalty": cp,
        "cross_off": cp is None,
        "inner_val_rmse": float(best["val_rmse"]),
    }, rmse(yte, pred)


def summarize(records: list[dict]) -> dict:
    out: dict[str, dict] = {}
    for protocol in ("shared", "disjoint"):
        rows = [r[protocol] for r in records]
        gains = np.asarray([r["gain_vs_linear"] for r in rows], dtype=float)
        out[protocol] = {
            "mean_linear_test_rmse": float(np.mean([r["linear_test_rmse"] for r in rows])),
            "mean_selected_test_rmse": float(np.mean([r["selected_test_rmse"] for r in rows])),
            "mean_gain_vs_linear": float(np.mean(gains)),
            "median_gain_vs_linear": float(np.median(gains)),
            "wins_vs_linear": int(np.sum(gains > 0)),
            "cross_off_selections": int(sum(r["selection"]["cross_off"] for r in rows)),
        }

    shared = np.asarray([r["shared"]["gain_vs_linear"] for r in records], dtype=float)
    disjoint = np.asarray([r["disjoint"]["gain_vs_linear"] for r in records], dtype=float)
    delta = disjoint - shared
    out["paired_disjoint_minus_shared_gain"] = {
        "mean": float(np.mean(delta)),
        "median": float(np.median(delta)),
        "disjoint_larger_splits": int(np.sum(delta > 0)),
        "shared_larger_splits": int(np.sum(delta < 0)),
        "equal_splits": int(np.sum(delta == 0)),
        "per_seed": [float(x) for x in delta],
    }
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--field-store", type=Path, required=True)
    ap.add_argument("--seeds", type=int, nargs="+", default=list(range(10)))
    ap.add_argument("--test-families", type=int, default=120)
    ap.add_argument("--atlas-families", type=int, default=120)
    ap.add_argument("--train-budget", type=int, default=560)
    ap.add_argument("--dense-train-grid", type=int, default=512)
    ap.add_argument("--harmonics", type=int, default=8)
    ap.add_argument("--anchors", type=int, default=64)
    ap.add_argument(
        "--linear-penalties",
        type=float,
        nargs="+",
        default=[3.0, 10.0, 30.0, 100.0, 300.0, 1000.0],
    )
    ap.add_argument(
        "--cross-penalties",
        type=float,
        nargs="+",
        default=[1e3, 3e3, 1e4, 3e4, 1e5, 3e5, 1e6, 3e6, 1e7, 3e7, 1e8],
    )
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    d, ids, profiles = raw_size1_profiles(args.field_store)
    b_embed = d["original_b"].astype(float)
    n = len(ids)
    required = args.test_families + args.atlas_families + args.train_budget
    if required > n:
        raise ValueError(f"need {required} families but field contains only {n}")
    if args.anchors > args.atlas_families:
        raise ValueError("--anchors cannot exceed --atlas-families")
    if args.atlas_families > args.train_budget:
        raise ValueError("shared control needs atlas_families <= train_budget")

    dense_grid = np.linspace(0.0, 1.0, args.dense_train_grid, endpoint=False)
    basis = fourier_basis(dense_grid, args.harmonics)
    linear_penalties = [float(x) for x in args.linear_penalties]
    cross_candidates: list[float | None] = [float(x) for x in args.cross_penalties]
    cross_candidates.append(None)
    records: list[dict] = []

    for seed in args.seeds:
        rng = np.random.default_rng(seed)
        order = np.arange(n)
        rng.shuffle(order)

        test_idx = order[: args.test_families]
        aux_start = args.test_families
        aux_stop = aux_start + args.atlas_families
        disjoint_atlas_idx = order[aux_start:aux_stop]
        train_idx = order[aux_stop : aux_stop + args.train_budget]
        shared_atlas_idx = train_idx[: args.atlas_families]

        # A-side representation is identical between atlas protocols and fitted only
        # from transport train; the auxiliary atlas never affects A preprocessing.
        train_dense = build_dense_training(profiles, train_idx, dense_grid)
        test_dense = build_dense_training(profiles, test_idx, dense_grid)
        mean_dense, scale_dense = source_stats(train_dense)
        train_full = functional_features(
            (train_dense - mean_dense[None, :]) / scale_dense[None, :], basis
        )
        test_full = functional_features(
            (test_dense - mean_dense[None, :]) / scale_dense[None, :], basis
        )
        linear_scaler = StandardScaler().fit(train_full)
        xtr = linear_scaler.transform(train_full)
        xte = linear_scaler.transform(test_full)
        ii, jj = pair_indices(xtr.shape[1])
        ctr_raw = cross_matrix(xtr, ii, jj)
        cte_raw = cross_matrix(xte, ii, jj)
        cross_scaler = StandardScaler().fit(ctr_raw)
        ctr = cross_scaler.transform(ctr_raw)
        cte = cross_scaler.transform(cte_raw)

        record: dict = {
            "seed": int(seed),
            "test_families": int(len(test_idx)),
            "train_families": int(len(train_idx)),
            "atlas_families": int(args.atlas_families),
            "atlas_anchors": int(args.anchors),
        }

        for protocol, atlas_idx in (
            ("shared", shared_atlas_idx),
            ("disjoint", disjoint_atlas_idx),
        ):
            atlas_b = b_embed[atlas_idx]
            anchor_local = farthest_anchors(atlas_b, args.anchors)
            anchor_emb = normalize(atlas_b[anchor_local])
            ytr = normalize(b_embed[train_idx]) @ anchor_emb.T
            yte = normalize(b_embed[test_idx]) @ anchor_emb.T
            selection_seed = int(seed + 73_001)

            linear_selection, linear_test = selected_score(
                xtr,
                ctr,
                ytr,
                xte,
                cte,
                yte,
                linear_penalties=linear_penalties,
                cross_penalties=[None],
                seed=selection_seed,
            )
            selection, selected_test = selected_score(
                xtr,
                ctr,
                ytr,
                xte,
                cte,
                yte,
                linear_penalties=linear_penalties,
                cross_penalties=cross_candidates,
                seed=selection_seed,
            )
            record[protocol] = {
                "atlas_overlap_with_train": bool(protocol == "shared"),
                "linear_selection": linear_selection,
                "linear_test_rmse": float(linear_test),
                "selection": selection,
                "selected_test_rmse": float(selected_test),
                "gain_vs_linear": float(linear_test - selected_test),
            }

        records.append(record)

    metadata: dict = {}
    if "metadata" in d:
        try:
            metadata = json.loads(str(d["metadata"].item()))
        except Exception:
            metadata = {"raw": str(d["metadata"].item())}

    result = {
        "experiment": "Pontifex c4 B-atlas independence ablation",
        "field_store": str(args.field_store),
        "field_metadata": metadata,
        "outer_seeds": args.seeds,
        "test_families": int(args.test_families),
        "atlas_families": int(args.atlas_families),
        "train_budget": int(args.train_budget),
        "anchors": int(args.anchors),
        "linear_penalty_grid": args.linear_penalties,
        "cross_penalty_grid": args.cross_penalties,
        "cross_off_candidate": True,
        "protocol": {
            "outer_partition": "whole families partitioned into outer test, auxiliary B-only atlas pool, and transport train; all three are disjoint",
            "shared_atlas_control": "same transport train/test, but atlas candidates are the first atlas_families transport-training B embeddings",
            "disjoint_atlas": "atlas candidates are B embeddings from the auxiliary pool, disjoint from transport train and outer test",
            "matched_between_protocols": "same A features, transport train/test families, atlas candidate count, anchor count, penalty grids, and inner-selection seed",
            "primary_estimand": "within-protocol interaction gain over linear baseline; paired disjoint-minus-shared difference in that gain",
            "absolute_rmse_warning": "absolute RMSE is not directly compared across protocols because their B anchor coordinate systems differ",
            "resource_warning": "disjoint atlas consumes extra B-only observations; this is a strict-separation robustness control, not a total-data-efficiency comparison",
            "selection": "linear and cross penalties are selected only on an inner split of transport outer-train",
            "held_out_use": "outer test is scored only after inner selection and never enters atlas construction or preprocessing",
            "evidence_boundary": "synthetic pairwise c4 cartography only; no D_assembly/D_student/D_val/D_test data",
        },
        "summary": summarize(records),
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
