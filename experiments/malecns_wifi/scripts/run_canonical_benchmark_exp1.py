"""Evaluate MaleCNS and synthetic null connectomes as a reservoir on canonical ML benchmarks (MNIST)."""
from __future__ import annotations

import argparse
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

CACHE_SCHEMA = "papers/canonical-benchmark-exp1-v1"


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


def evaluate_canonical_kfold(
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

    affinities = predictions @ flavours.T
    pred_labels = np.argmax(affinities, axis=1)
    true_labels = np.argmax(tag_masks, axis=1)
    accuracy = float((pred_labels == true_labels).mean())

    return {
        "macro_tag_auprc": float(np.mean(finite)) if finite else float("nan"),
        "accuracy": accuracy,
        "per_tag_auprc": {str(k): v for k, v in per_tag.items()},
        "chosen_penalties": chosen_penalties,
    }


def evaluate_canonical_nested_kfold(
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

    affinities = predictions @ flavours.T
    pred_labels = np.argmax(affinities, axis=1)
    true_labels = np.argmax(tag_masks, axis=1)
    accuracy = float((pred_labels == true_labels).mean())

    return {
        "macro_tag_auprc": float(np.mean(finite)) if finite else float("nan"),
        "accuracy": accuracy,
        "per_tag_auprc": {str(k): v for k, v in per_tag.items()},
    }


def build_operator(kind: str, matrix, seed: int):
    if kind == "none":
        return None
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
    parser.add_argument("--features", type=Path, default=Path("artifacts/runtime-v1/mnist-1000-features.npz"))
    parser.add_argument("--graph", type=Path, default=Path("artifacts/runtime-v1/graph.npz"))
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    parser.add_argument("--gains", type=float, nargs="+", default=[0.0, 0.25, 0.5, 0.75])
    parser.add_argument("--steps-per-chunk", type=int, default=10)
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
        default=Path("artifacts/runtime-v1/mnist-exp1-results.json"),
    )
    parser.add_argument("--state-cache", type=Path, default=Path("artifacts/runtime-v1/state-cache"))
    args = parser.parse_args()

    stored = np.load(args.features, allow_pickle=False)
    block = stored["absolute"]
    tag_masks = stored["tag_masks"]
    groups = stored["groups"]
    embeddings = stored["tag_embeddings"]

    n_samples = len(block)
    chunk_folds = np.array([i % args.n_folds for i in range(n_samples)])

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
        experiment="mnist_exp1",
        gains=list(spec.gain_grid),
        leak=spec.leak,
        steps=spec.steps_per_chunk,
        drive=spec.input_scale,
        seeds=list(spec.seeds),
        graph=str(args.graph),
        features=array_fingerprint(block),
        tag_masks=array_fingerprint(tag_masks),
        tag_embeddings=array_fingerprint(embeddings),
        n_folds=args.n_folds,
    )

    print(f"=== Canonical MNIST Connectome Benchmark (Exp 1) ===")
    print(f"Samples: {n_samples}, Features: {block.shape[1]}, Classes: {tag_masks.shape[1]}")
    print(f"Config Hash: {config_hash}")
    print(f"Prevalence: {prevalence:.3f}, Seeds: {spec.seeds}, Folds: {args.n_folds}")

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
            f"{row['macro_tag_auprc']:>12.4f}"
            f"{row.get('accuracy', float('nan')):>12.4f}",
            flush=True,
        )

    matrix = load_graph(args.graph)
    archive = np.load(args.graph, allow_pickle=False)
    populations = select_populations(archive["superclass"])
    readout = populations.readout_indices

    # 1. Direct Baselines
    print(f"\n{'condition':<24}{'seed':>5}{'macroAP':>12}{'accuracy':>12}")
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
            scored = evaluate_canonical_kfold(
                feats, tag_masks, flavours, chunk_folds,
                penalties=spec.ridge_penalties, n_folds=args.n_folds,
            )
            record({"condition": name, "seed": seed, **scored})

    # 2. Reservoir Operators
    for kind in args.operators:
        if kind == "none":
            continue
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
                        projection=array_fingerprint(projection),
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
                        operator, block[i:i+1], input_weights=projection,
                        readout_indices=readout,
                        input_indices=populations.input_indices,
                        spec=gain_spec, scale=calibration["mean"],
                    )[0]
                    for i in range(n_samples)
                ])
                states_by_gain[gain] = states
                if key is not None:
                    np.save(key, states)

            chosen = evaluate_canonical_nested_kfold(
                states_by_gain, tag_masks, flavours, chunk_folds,
                penalties=spec.ridge_penalties, n_folds=args.n_folds,
            )

            recurrence_delta = float("nan")
            if 0.0 in states_by_gain:
                without = evaluate_canonical_kfold(
                    states_by_gain[0.0], tag_masks, flavours, chunk_folds,
                    penalties=spec.ridge_penalties, n_folds=args.n_folds,
                )
                recurrence_delta = chosen["macro_tag_auprc"] - without["macro_tag_auprc"]
                record({"condition": f"{kind}_gain0", "seed": seed, **without})

            record({
                "condition": kind,
                "seed": seed,
                "recurrence_delta": recurrence_delta,
                "gain_grid": list(spec.gain_grid),
                "elapsed_s": time.time() - t_op_start,
                **chosen,
            })

    # Save final
    summary = {
        "config_hash": config_hash,
        "n_samples": n_samples,
        "n_features": block.shape[1],
        "n_classes": tag_masks.shape[1],
        "results": results,
    }
    args.output.write_text(json.dumps(summary, indent=2) + "\n")
    print(f"\nFinal results saved to {args.output}")


if __name__ == "__main__":
    main()
