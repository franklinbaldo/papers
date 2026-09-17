"""Experiment 1B: recurrent controls for the frozen MultiEURLEX-21 benchmark.

This complements Exp. 1 without changing its frozen protocol. It asks whether
adding generic recurrence to the matched sensory projection changes macroAP,
so that recurrence itself is not confounded with MaleCNS topology.

Conditions:
- projected_direct_recheck: exact matched direct projection, recomputed as a guard.
- projected_self_recurrent: leaky tanh recurrence with an identity operator.
- projected_sparse_recurrent: leaky tanh recurrence with a fixed random signed sparse operator.

The same 1,000 chunks, document folds, semantic flavours, projection RNG, drive
calibration, gain grid and nested ridge/gain selection used by Exp. 1 are kept.
"""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import numpy as np
import scipy.sparse as sp

from malecns_wifi.multitag import (
    MultitagSpec,
    build_flavours,
    calibrate_drive,
    reservoir_states,
    unit_rows,
)
from run_multieurlex_exp1 import evaluate_kfold, evaluate_nested_kfold

EXPECTED_PROJECTED = {0: 0.1986, 1: 0.2041, 2: 0.2067}


def make_sparse_operator(width: int, seed: int, fan_in: int) -> sp.csr_matrix:
    """Fixed signed random recurrence with exactly ``fan_in`` entries per row.

    Rows are L1-normalized, matching the scale convention used by MaleCNS after
    row normalization while deliberately discarding biological wiring.
    """
    rng = np.random.default_rng(seed + 7001)
    rows = np.repeat(np.arange(width, dtype=np.int32), fan_in)
    cols = np.empty(width * fan_in, dtype=np.int32)
    data = np.empty(width * fan_in, dtype=np.float32)
    for row in range(width):
        start = row * fan_in
        stop = start + fan_in
        cols[start:stop] = rng.choice(width, size=fan_in, replace=False)
        data[start:stop] = rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=fan_in)
    matrix = sp.csr_matrix((data, (rows, cols)), shape=(width, width), dtype=np.float32)
    matrix.data *= np.float32(1.0 / fan_in)
    return matrix


def init_wandb(config: dict):
    """Use a Kaggle W&B secret when available, otherwise an anonymous online run."""
    try:
        import wandb
    except Exception as exc:  # pragma: no cover - telemetry must not block science
        print(f"W&B unavailable: {exc}", flush=True)
        return None

    key = os.environ.get("WANDB_API_KEY", "").strip()
    if not key:
        try:
            from kaggle_secrets import UserSecretsClient

            key = (UserSecretsClient().get_secret("WANDB_API_KEY") or "").strip()
        except Exception:
            key = ""
    try:
        if key:
            wandb.login(key=key, relogin=True)
        run = wandb.init(
            project=os.environ.get("WANDB_PROJECT", "malecns-exp1b-recurrent-controls"),
            name=os.environ.get("WANDB_NAME", "multieurlex-exp1b"),
            tags=["malecns", "multieurlex", "exp1b", "recurrent-control", "kaggle"],
            config=config,
            anonymous="allow",
            force=False,
        )
        print(f"W&B run: {run.url}", flush=True)
        return run
    except Exception as exc:
        print(f"W&B init failed; continuing without online telemetry: {exc}", flush=True)
        return None


def document_states(
    operator,
    block: np.ndarray,
    groups: np.ndarray,
    projection: np.ndarray,
    scale: float,
    spec: MultitagSpec,
) -> np.ndarray:
    width = operator.shape[0]
    indices = np.arange(width, dtype=np.int64)
    pieces = []
    for document in np.unique(groups):
        states, _ = reservoir_states(
            operator,
            block[groups == document],
            input_weights=projection,
            readout_indices=indices,
            input_indices=indices,
            spec=spec,
            scale=scale,
        )
        pieces.append(states)
    return np.vstack(pieces)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("multieurlex-exp1b-results.json"))
    parser.add_argument("--state-dim", type=int, default=8982)
    parser.add_argument("--fan-in", type=int, default=32)
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    parser.add_argument("--steps-per-chunk", type=int, default=4)
    parser.add_argument("--leak", type=float, default=0.4)
    parser.add_argument("--target-drive-rms", type=float, default=0.05)
    parser.add_argument(
        "--gains", type=float, nargs="+", default=[0.0, 0.25, 0.5, 0.95, 1.5, 2.5, 4.0]
    )
    parser.add_argument("--n-folds", type=int, default=10)
    parser.add_argument("--guard-tolerance", type=float, default=0.0020)
    args = parser.parse_args()

    stored = np.load(args.features, allow_pickle=False)
    required = {"absolute", "tag_masks", "groups", "tag_embeddings"}
    missing = required.difference(stored.files)
    if missing:
        raise SystemExit(f"feature bundle missing keys: {sorted(missing)}")
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
    config = {
        "experiment": "multieurlex-exp1b-recurrent-controls",
        "n_chunks": int(len(block)),
        "n_documents": int(len(unique_docs)),
        "n_labels": int(tag_masks.shape[1]),
        "state_dim": args.state_dim,
        "fan_in": args.fan_in,
        "seeds": list(args.seeds),
        "gains": list(args.gains),
        "leak": args.leak,
        "steps_per_chunk": args.steps_per_chunk,
        "target_drive_rms": args.target_drive_rms,
        "n_folds": args.n_folds,
    }
    run = init_wandb(config)
    results: list[dict] = []

    for seed in args.seeds:
        started = time.time()
        flavours = build_flavours(embeddings, spec, seed=seed, source="semantic")
        rng = np.random.default_rng(seed)
        projection = rng.normal(size=(args.state_dim, block.shape[1])).astype(np.float32)
        calibration = calibrate_drive(projection, block, groups, target_rms=spec.input_scale)
        projected = (unit_rows(block) @ projection.T) * np.float32(calibration["mean"])
        direct = evaluate_kfold(
            projected,
            tag_masks,
            flavours,
            chunk_folds,
            penalties=spec.ridge_penalties,
            n_folds=args.n_folds,
        )
        direct_ap = float(direct["macro_tag_auprc"])
        expected = EXPECTED_PROJECTED.get(seed)
        if expected is not None and abs(direct_ap - expected) > args.guard_tolerance:
            raise SystemExit(
                f"protocol guard failed for seed {seed}: projected_direct={direct_ap:.4f}, "
                f"expected≈{expected:.4f} ± {args.guard_tolerance:.4f}"
            )
        row = {"condition": "projected_direct_recheck", "seed": seed, **direct}
        results.append(row)
        if run:
            run.log({"seed": seed, "projected_direct/macroAP": direct_ap})

        operators = {
            "projected_self_recurrent": sp.eye(args.state_dim, format="csr", dtype=np.float32),
            "projected_sparse_recurrent": make_sparse_operator(args.state_dim, seed, args.fan_in),
        }
        for name, operator in operators.items():
            states_by_gain: dict[float, np.ndarray] = {}
            per_gain = {}
            for gain in spec.gain_grid:
                gain_spec = MultitagSpec(
                    seeds=spec.seeds,
                    steps_per_chunk=spec.steps_per_chunk,
                    gain=gain,
                    leak=spec.leak,
                    input_scale=spec.input_scale,
                )
                states = document_states(
                    operator, block, groups, projection, calibration["mean"], gain_spec
                )
                states_by_gain[gain] = states
                scored = evaluate_kfold(
                    states,
                    tag_masks,
                    flavours,
                    chunk_folds,
                    penalties=spec.ridge_penalties,
                    n_folds=args.n_folds,
                )
                per_gain[str(gain)] = float(scored["macro_tag_auprc"])
                if run:
                    run.log(
                        {
                            "seed": seed,
                            "condition": name,
                            "gain": gain,
                            f"{name}/per_gain_macroAP": per_gain[str(gain)],
                        }
                    )
            chosen = evaluate_nested_kfold(
                states_by_gain,
                tag_masks,
                flavours,
                chunk_folds,
                penalties=spec.ridge_penalties,
                n_folds=args.n_folds,
            )
            ap = float(chosen["macro_tag_auprc"])
            record = {
                "condition": name,
                "seed": seed,
                "macro_tag_auprc": ap,
                "delta_vs_projected_direct": ap - direct_ap,
                "per_gain_macro_ap": per_gain,
                "elapsed_seconds": round(time.time() - started, 2),
                **{k: v for k, v in chosen.items() if k != "macro_tag_auprc"},
            }
            results.append(record)
            print(
                f"{name} seed={seed} macroAP={ap:.4f} "
                f"delta_direct={ap - direct_ap:+.4f}",
                flush=True,
            )
            if run:
                run.log(
                    {
                        "seed": seed,
                        f"{name}/macroAP": ap,
                        f"{name}/delta_vs_projected_direct": ap - direct_ap,
                    }
                )

    summary: dict[str, dict] = {}
    for condition in ("projected_self_recurrent", "projected_sparse_recurrent"):
        rows = [r for r in results if r["condition"] == condition]
        values = np.asarray([r["macro_tag_auprc"] for r in rows], dtype=float)
        deltas = np.asarray([r["delta_vs_projected_direct"] for r in rows], dtype=float)
        summary[condition] = {
            "mean_macro_tag_auprc": float(values.mean()),
            "stdev_macro_tag_auprc": float(values.std()),
            "mean_delta_vs_projected_direct": float(deltas.mean()),
            "wins_vs_projected_direct": int(np.sum(deltas > 0)),
            "n_seeds": len(rows),
        }

    payload = {"config": config, "results": results, "summary": summary}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(summary, indent=2), flush=True)

    if run:
        try:
            import wandb

            table = wandb.Table(
                columns=["condition", "seed", "macroAP", "delta_vs_projected_direct"],
                data=[
                    [
                        r["condition"],
                        r["seed"],
                        r["macro_tag_auprc"],
                        r.get("delta_vs_projected_direct"),
                    ]
                    for r in results
                ],
            )
            run.log({"results": table})
            run.summary.update(summary)
            run.finish()
        except Exception as exc:
            print(f"W&B finalization warning: {exc}", flush=True)


if __name__ == "__main__":
    main()
