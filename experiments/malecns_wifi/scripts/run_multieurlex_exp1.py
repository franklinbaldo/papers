"""Experiment 1: Massive-Scale MultiEURLEX-21 Benchmark.

Frozen Protocol:
- Corpus: 1,000 test chunks from MultiEURLEX Portuguese subset (mteb/eurlex-multilingual).
- Features: 384-dimensional MiniLM-L12-v2 cached embeddings.
- Labels: 21 EuroVoc multi-labels.
- Folds: 10 document-level folds (inner validation selects gain & ridge penalty).
- Gains: [0.0, 0.25, 0.5, 0.95, 1.5, 2.5, 4.0].
- Operators:
    1. Baselines: direct_raw, direct_unit_norm, projected_direct, projected_direct_delay
    2. Recurrent: malecns, rewired_p10, rewired_p50, degree_null
- Seeds: Confirmatory evaluation with seeds [0, 1, 2].
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np

from malecns_wifi import load_graph
from malecns_wifi.characterize import degree_preserving_null, partial_degree_preserving_null
from malecns_wifi.encoder_gate import average_precision
from malecns_wifi.gustation import delayed_stack, effective_delay_window
from malecns_wifi.multitag import (
    CACHE_SCHEMA,
    MultitagSpec,
    array_fingerprint,
    build_flavours,
    calibrate_drive,
    food_targets,
    reservoir_states,
    ridge_multioutput,
    run_fingerprint,
    unit_rows,
)
from malecns_wifi.tagger import row_normalise, select_populations


def _macro_tag_ap(scored: np.ndarray, tag_masks: np.ndarray, flavours: np.ndarray) -> float:
    per_tag = []
    for index in range(flavours.shape[0]):
        target = tag_masks[:, index] > 0
        if not target.any() or target.all():
            continue
        affinity = scored @ flavours[index]
        score = average_precision(affinity, target)
        if np.isfinite(score):
            per_tag.append(score)
    return float(np.mean(per_tag)) if per_tag else float("nan")


def evaluate_kfold(
    features: np.ndarray,
    tag_masks: np.ndarray,
    flavours: np.ndarray,
    chunk_folds: np.ndarray,
    *,
    penalties: tuple[float, ...] = (0.01, 0.1, 1.0, 10.0, 100.0),
    n_folds: int = 10,
) -> dict:
    targets = food_targets(tag_masks, flavours)
    predictions = np.zeros_like(targets)
    chosen_penalties = []

    for fold in range(n_folds):
        test_mask = chunk_folds == fold
        train_mask = ~test_mask
        val_fold = (fold + 1) % n_folds
        val_mask = chunk_folds == val_fold
        inner_tr_mask = train_mask & (~val_mask)

        best = (-np.inf, penalties[0])
        for p in penalties:
            w = ridge_multioutput(features[inner_tr_mask], targets[inner_tr_mask], p)
            scored = np.hstack([features[val_mask], np.ones((int(val_mask.sum()), 1))]) @ w
            score = _macro_tag_ap(scored, tag_masks[val_mask], flavours)
            if score > best[0]:
                best = (score, p)

        best_p = best[1]
        chosen_penalties.append(float(best_p))
        w_final = ridge_multioutput(features[train_mask], targets[train_mask], best_p)
        predictions[test_mask] = np.hstack([features[test_mask], np.ones((int(test_mask.sum()), 1))]) @ w_final

    per_tag = {}
    for index in range(flavours.shape[0]):
        target = tag_masks[:, index] > 0
        if not target.any() or target.all():
            per_tag[index] = float("nan")
            continue
        affinity = predictions @ flavours[index]
        per_tag[index] = float(average_precision(affinity, target))
    finite = [v for v in per_tag.values() if np.isfinite(v)]

    return {
        "macro_tag_auprc": float(np.mean(finite)) if finite else float("nan"),
        "per_tag_auprc": {str(k): v for k, v in per_tag.items()},
        "chosen_penalties": chosen_penalties,
    }


def evaluate_nested_kfold(
    states_by_gain: dict[float, np.ndarray],
    tag_masks: np.ndarray,
    flavours: np.ndarray,
    chunk_folds: np.ndarray,
    *,
    penalties: tuple[float, ...] = (0.01, 0.1, 1.0, 10.0, 100.0),
    n_folds: int = 10,
) -> dict:
    gains = sorted(g for g in states_by_gain if g > 0)
    if not gains:
        raise ValueError("no positive gain available to select from")
    targets = food_targets(tag_masks, flavours)
    predictions = np.zeros_like(targets)
    chosen: dict[str, dict] = {}

    for fold in range(n_folds):
        test_mask = chunk_folds == fold
        train_mask = ~test_mask
        val_fold = (fold + 1) % n_folds
        val_mask = chunk_folds == val_fold
        inner_tr_mask = train_mask & (~val_mask)

        best = (-np.inf, gains[0], penalties[0])
        for g in gains:
            st = states_by_gain[g]
            for p in penalties:
                w = ridge_multioutput(st[inner_tr_mask], targets[inner_tr_mask], p)
                scored = np.hstack([st[val_mask], np.ones((int(val_mask.sum()), 1))]) @ w
                score = _macro_tag_ap(scored, tag_masks[val_mask], flavours)
                if score > best[0]:
                    best = (score, g, p)

        _, best_g, best_p = best
        chosen[str(fold)] = {"gain": float(best_g), "ridge": float(best_p)}
        w_final = ridge_multioutput(states_by_gain[best_g][train_mask], targets[train_mask], best_p)
        predictions[test_mask] = np.hstack([states_by_gain[best_g][test_mask], np.ones((int(test_mask.sum()), 1))]) @ w_final

    per_tag = {}
    for index in range(flavours.shape[0]):
        target = tag_masks[:, index] > 0
        if not target.any() or target.all():
            per_tag[index] = float("nan")
            continue
        affinity = predictions @ flavours[index]
        per_tag[index] = float(average_precision(affinity, target))
    finite = [v for v in per_tag.values() if np.isfinite(v)]

    return {
        "macro_tag_auprc": float(np.mean(finite)) if finite else float("nan"),
        "per_tag_auprc": {str(k): v for k, v in per_tag.items()},
        "selected_by_fold": chosen,
        "selection": f"nested {n_folds}-fold: (gain, ridge) chosen inside each outer fold",
    }


def build_operator(kind: str, matrix, seed: int):
    if kind == "malecns":
        return row_normalise(matrix)
    if kind == "rewired_p10":
        null, _ = partial_degree_preserving_null(matrix, p=0.10, seed=seed + 101)
        return row_normalise(null)
    if kind == "rewired_p50":
        null, _ = partial_degree_preserving_null(matrix, p=0.50, seed=seed + 101)
        return row_normalise(null)
    if kind == "degree_null":
        null, _ = degree_preserving_null(matrix, seed=seed + 101)
        return row_normalise(null)
    raise ValueError(f"unknown operator {kind!r}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, default=Path("artifacts/runtime-v1/multieurlex-1000-features.npz"))
    parser.add_argument("--graph", type=Path, default=Path("artifacts/runtime-v1/graph.npz"))
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    parser.add_argument("--steps-per-chunk", type=int, default=4)
    parser.add_argument(
        "--gains",
        type=float,
        nargs="+",
        default=[0.0, 0.25, 0.5, 0.95, 1.5, 2.5, 4.0],
    )
    parser.add_argument("--leak", type=float, default=0.4)
    parser.add_argument("--target-drive-rms", type=float, default=0.05)
    parser.add_argument(
        "--operators",
        nargs="+",
        default=["malecns", "rewired_p10", "rewired_p50", "degree_null"],
    )
    parser.add_argument("--n-folds", type=int, default=10)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/runtime-v1/multieurlex-exp1-results.json"),
    )
    parser.add_argument("--state-cache", type=Path, default=Path("artifacts/runtime-v1/state-cache"))
    args = parser.parse_args()

    stored = np.load(args.features, allow_pickle=False)
    block = stored["absolute"]
    tag_masks = stored["tag_masks"]
    groups = stored["groups"]
    embeddings = stored["tag_embeddings"]

    unique_docs = np.unique(groups)
    doc_to_fold = {doc: doc % args.n_folds for doc in unique_docs}
    chunk_folds = np.array([doc_to_fold[g] for g in groups])

    spec = MultitagSpec(
        seeds=tuple(args.seeds),
        steps_per_chunk=args.steps_per_chunk,
        leak=args.leak,
        input_scale=args.target_drive_rms,
        gain_grid=tuple(args.gains),
    )
    delay_horizon = effective_delay_window(spec.leak, spec.steps_per_chunk)
    prevalence = float(np.mean([(tag_masks[:, i] > 0).mean() for i in range(tag_masks.shape[1])]))

    config_hash = run_fingerprint(
        schema=CACHE_SCHEMA,
        experiment="multieurlex_exp1",
        gains=list(spec.gain_grid),
        leak=spec.leak,
        steps=spec.steps_per_chunk,
        drive=spec.input_scale,
        seeds=list(spec.seeds),
        graph=str(args.graph),
        features=array_fingerprint(block),
        tag_masks=array_fingerprint(tag_masks),
        tag_embeddings=array_fingerprint(embeddings),
        groups=array_fingerprint(groups.astype(np.float32)),
        n_folds=args.n_folds,
    )

    print(f"=== MultiEURLEX-21 Massive Benchmark (Exp 1) ===")
    print(f"Chunks: {len(block)}, Documents: {len(unique_docs)}, Labels: {tag_masks.shape[1]}")
    print(f"Config Hash: {config_hash}")
    print(f"Macro prevalence: {prevalence:.3f}, Seeds: {spec.seeds}, Folds: {args.n_folds}")

    checkpoint = args.output.with_suffix(".partial.json")
    results: list[dict] = []
    if checkpoint.exists():
        previous = json.loads(checkpoint.read_text())
        if previous.get("config_hash") == config_hash:
            results = previous["results"]
            print(f"Resuming with {len(results)} cells done")
    done = {(row["condition"], row["seed"]) for row in results}

    if args.state_cache:
        args.state_cache.mkdir(parents=True, exist_ok=True)

    def record(row: dict) -> None:
        results.append(row)
        checkpoint.write_text(
            json.dumps({"config_hash": config_hash, "results": results}, indent=2) + "\n"
        )
        print(
            f"{row['condition']:<24}{row['seed']:>5}"
            f"{row['macro_tag_auprc']:>12.4f}",
            flush=True,
        )

    matrix = load_graph(args.graph)
    archive = np.load(args.graph, allow_pickle=False)
    populations = select_populations(archive["superclass"])
    readout = populations.readout_indices

    graph_hash = array_fingerprint(matrix.data) + array_fingerprint(
        matrix.indices.astype(np.float32)
    )
    inputs_hash = array_fingerprint(populations.input_indices.astype(np.float32))
    readout_hash = array_fingerprint(readout.astype(np.float32))

    # 1. Evaluate Direct Baselines
    print(f"\n{'condition':<24}{'seed':>5}{'macroAP':>12}")
    for seed in spec.seeds:
        rng = np.random.default_rng(seed)
        flavours = build_flavours(embeddings, spec, seed=seed, source="semantic")
        projection = rng.normal(
            size=(populations.input_indices.size, block.shape[1])
        ).astype(np.float32)
        calibration = calibrate_drive(projection, block, groups, target_rms=spec.input_scale)
        projected = (unit_rows(block) @ projection.T) * np.float32(calibration["mean"])

        for name, feats in (
            ("direct_raw", block),
            ("direct_unit_norm", unit_rows(block)),
            ("projected_direct", projected),
            ("projected_direct_delay", delayed_stack(projected, groups, delay_horizon)),
        ):
            if (name, seed) in done:
                continue
            scored = evaluate_kfold(
                feats, tag_masks, flavours, chunk_folds,
                penalties=spec.ridge_penalties, n_folds=args.n_folds
            )
            record({"condition": name, "seed": seed, **scored})

    # 2. Evaluate Operators (MaleCNS, Rewired, Degree Null)
    for kind in args.operators:
        for seed in spec.seeds:
            if (kind, seed) in done:
                continue
            t_op_start = time.time()
            operator = build_operator(kind, matrix, seed)
            rng = np.random.default_rng(seed)
            flavours = build_flavours(embeddings, spec, seed=seed, source="semantic")
            projection = rng.normal(
                size=(populations.input_indices.size, block.shape[1])
            ).astype(np.float32)
            calibration = calibrate_drive(projection, block, groups, target_rms=spec.input_scale)

            states_by_gain = {}
            for gain in spec.gain_grid:
                key = None
                if args.state_cache:
                    key = args.state_cache / (run_fingerprint(
                        schema=CACHE_SCHEMA,
                        operator=kind,
                        seed=seed,
                        gain=gain,
                        leak=spec.leak,
                        steps=spec.steps_per_chunk,
                        drive=spec.input_scale,
                        features=array_fingerprint(block),
                        graph=graph_hash,
                        inputs=inputs_hash,
                        readout=readout_hash,
                        projection=array_fingerprint(projection),
                        groups=array_fingerprint(groups.astype(np.float32)),
                        calibration=round(float(calibration["mean"]), 12),
                        normalisation="unit_rows+row_normalise",
                    ) + ".npy")
                    if key.exists():
                        states_by_gain[gain] = np.load(key)
                        continue

                gain_spec = MultitagSpec(
                    seeds=spec.seeds, steps_per_chunk=spec.steps_per_chunk, gain=gain,
                    leak=spec.leak, input_scale=spec.input_scale,
                )
                states = np.vstack([
                    reservoir_states(
                        operator, block[groups == document], input_weights=projection,
                        readout_indices=readout,
                        input_indices=populations.input_indices,
                        spec=gain_spec, scale=calibration["mean"],
                    )[0]
                    for document in unique_docs
                ])
                states_by_gain[gain] = states
                if key is not None:
                    np.save(key, states)

            chosen = evaluate_nested_kfold(
                states_by_gain, tag_masks, flavours, chunk_folds,
                penalties=spec.ridge_penalties, n_folds=args.n_folds,
            )

            recurrence_delta = float("nan")
            if 0.0 in states_by_gain:
                without = evaluate_kfold(
                    states_by_gain[0.0], tag_masks, flavours, chunk_folds,
                    penalties=spec.ridge_penalties, n_folds=args.n_folds
                )
                recurrence_delta = chosen["macro_tag_auprc"] - without["macro_tag_auprc"]
                record({"condition": f"{kind}_gain0", "seed": seed, **without})

            record({
                "condition": kind,
                "seed": seed,
                "recurrence_delta": recurrence_delta,
                "gain_grid": list(spec.gain_grid),
                "per_gain_macro_ap": {
                    str(g): float(evaluate_kfold(
                        s, tag_masks, flavours, chunk_folds,
                        penalties=spec.ridge_penalties, n_folds=args.n_folds
                    )["macro_tag_auprc"])
                    for g, s in sorted(states_by_gain.items())
                },
                "elapsed_seconds": round(time.time() - t_op_start, 2),
                **chosen,
            })

    # Summary and paired contrasts
    by_condition: dict[str, dict[int, float]] = {}
    for row in results:
        by_condition.setdefault(row["condition"], {})[row["seed"]] = row["macro_tag_auprc"]

    summary = {}
    for control in ("direct_raw", "projected_direct", "projected_direct_delay",
                    "rewired_p10", "rewired_p50", "degree_null"):
        if "malecns" in by_condition and control in by_condition:
            seeds = sorted(set(by_condition["malecns"]) & set(by_condition[control]))
            deltas = [by_condition[control][s] - by_condition["malecns"][s] for s in seeds]
            summary[f"{control}_minus_malecns"] = {
                "per_seed": deltas,
                "mean": float(np.mean(deltas)) if deltas else float("nan"),
                "wins": int(sum(1 for d in deltas if d > 0)),
                "seeds": len(deltas),
            }

    final_payload = {
        "config_hash": config_hash,
        "n_chunks": len(block),
        "n_documents": len(unique_docs),
        "n_labels": tag_masks.shape[1],
        "n_folds": args.n_folds,
        "results": results,
        "summary": summary,
    }
    args.output.write_text(json.dumps(final_payload, indent=2) + "\n")
    if checkpoint.exists():
        checkpoint.unlink()
    print(f"\nCompleted successfully! Wrote {args.output}")


if __name__ == "__main__":
    main()
