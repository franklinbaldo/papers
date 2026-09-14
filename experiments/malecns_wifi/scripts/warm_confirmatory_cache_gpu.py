"""Warm the frozen F2/F3 state cache on CUDA without changing the runner.

The CPU ``run_confirmatory.py`` remains authoritative.  This script only writes
state arrays under the *same* content-addressed keys.  Every gain for one
(operator, seed, document) is evolved in parallel so the ~10M-edge matrix is read
once per timestep rather than once per gain.

A real CPU<->GPU parity check is mandatory before any cache file is written.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from malecns_wifi import load_graph
from malecns_wifi.characterize import degree_preserving_null, random_esn
from malecns_wifi.gpu_cache import (
    compare_states,
    reservoir_states_multi_gain,
    scipy_csr_to_torch,
)
from malecns_wifi.multitag import (
    CACHE_SCHEMA,
    MultitagSpec,
    array_fingerprint,
    calibrate_drive,
    reservoir_states,
    run_fingerprint,
)
from malecns_wifi.tagger import row_normalise, select_populations


def build_operator(kind: str, matrix, seed: int):
    """Exact operator construction used by run_confirmatory.py @ 437083a."""
    if kind == "malecns":
        return row_normalise(matrix)
    if kind == "degree_null":
        null, _ = degree_preserving_null(matrix, seed=seed + 101)
        return row_normalise(null)
    if kind == "random_esn":
        esn, _ = random_esn(matrix, seed=seed + 202)
        return row_normalise(esn)
    raise ValueError(f"unknown operator {kind!r}")


def cache_key(
    *,
    kind: str,
    representation: str,
    seed: int,
    gain: float,
    leak: float,
    steps: int,
    drive: float,
    block: np.ndarray,
    graph_hash: str,
    inputs_hash: str,
    readout_hash: str,
    projection: np.ndarray,
    groups: np.ndarray,
    calibration: float,
) -> str:
    """Byte-for-byte key recipe from the frozen CPU runner."""
    return run_fingerprint(
        schema=CACHE_SCHEMA,
        operator=kind,
        representation=representation,
        seed=seed,
        gain=gain,
        leak=leak,
        steps=steps,
        drive=drive,
        features=array_fingerprint(block),
        graph=graph_hash,
        inputs=inputs_hash,
        readout=readout_hash,
        projection=array_fingerprint(projection),
        groups=array_fingerprint(groups.astype(np.float32)),
        calibration=round(float(calibration), 12),
        normalisation="unit_rows+row_normalise",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, required=True)
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--state-cache", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument("--seeds", type=int, nargs="+", default=list(range(10)))
    parser.add_argument(
        "--gains", type=float, nargs="+",
        default=[0.0, 0.25, 0.5, 0.95, 1.5, 2.5, 4.0],
    )
    parser.add_argument(
        "--operators", nargs="+",
        default=["malecns", "degree_null", "random_esn"],
        choices=["malecns", "degree_null", "random_esn"],
    )
    parser.add_argument("--representation", default="absolute_plus_relations")
    parser.add_argument("--leak", type=float, default=0.4)
    parser.add_argument("--steps-per-chunk", type=int, default=4)
    parser.add_argument("--target-drive-rms", type=float, default=0.05)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--parity-gain", type=float, default=0.95)
    parser.add_argument("--parity-max-abs", type=float, default=2e-3)
    parser.add_argument("--parity-relative-rmse", type=float, default=2e-3)
    parser.add_argument("--expected-features-hash", default="")
    parser.add_argument("--expected-graph-hash", default="")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    try:
        import torch
    except ImportError as exc:
        raise SystemExit("torch is required; install the train extra") from exc
    if args.device.startswith("cuda") and not torch.cuda.is_available():
        raise SystemExit("CUDA was requested but torch.cuda.is_available() is false")

    stored = np.load(args.features, allow_pickle=False)
    groups = np.asarray(stored["groups"])
    blocks = {
        "absolute": stored["absolute"],
        "relations": stored["sensation"],
        "absolute_plus_relations": np.hstack([stored["absolute"], stored["sensation"]]),
    }
    block = np.asarray(blocks[args.representation], dtype=np.float32)
    features_hash = array_fingerprint(block)
    if args.expected_features_hash and features_hash != args.expected_features_hash:
        raise SystemExit(
            f"feature fingerprint mismatch: {features_hash} != {args.expected_features_hash}"
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
    if args.expected_graph_hash and graph_hash != args.expected_graph_hash:
        raise SystemExit(f"graph fingerprint mismatch: {graph_hash} != {args.expected_graph_hash}")

    args.state_cache.mkdir(parents=True, exist_ok=True)
    manifest_path = args.manifest or args.state_cache / "gpu-cache-manifest.json"
    documents = np.unique(groups)
    gains = tuple(float(g) for g in args.gains)
    if args.parity_gain not in gains:
        raise SystemExit("--parity-gain must be present in --gains")

    report: dict = {
        "format": "papers/malecns-confirmatory-gpu-cache-v1",
        "cache_schema": CACHE_SCHEMA,
        "device": args.device,
        "torch": torch.__version__,
        "cuda": torch.version.cuda,
        "features_hash": features_hash,
        "graph_hash": graph_hash,
        "inputs_hash": inputs_hash,
        "readout_hash": readout_hash,
        "gains": list(gains),
        "seeds": list(args.seeds),
        "operators": list(args.operators),
        "cells": [],
        "parity": None,
    }

    parity_done = False
    started = time.perf_counter()
    for kind in args.operators:
        for seed in args.seeds:
            operator = build_operator(kind, matrix, seed)
            torch_operator = scipy_csr_to_torch(operator, device=args.device)

            rng = np.random.default_rng(seed)
            projection = rng.normal(
                size=(populations.input_indices.size, block.shape[1])
            ).astype(np.float32)
            calibration = calibrate_drive(
                projection, block, groups, target_rms=args.target_drive_rms
            )

            keys = {
                gain: cache_key(
                    kind=kind,
                    representation=args.representation,
                    seed=seed,
                    gain=gain,
                    leak=args.leak,
                    steps=args.steps_per_chunk,
                    drive=args.target_drive_rms,
                    block=block,
                    graph_hash=graph_hash,
                    inputs_hash=inputs_hash,
                    readout_hash=readout_hash,
                    projection=projection,
                    groups=groups,
                    calibration=calibration["mean"],
                )
                for gain in gains
            }
            paths = {gain: args.state_cache / f"{key}.npy" for gain, key in keys.items()}
            if not args.force and all(path.exists() for path in paths.values()):
                report["cells"].append(
                    {"operator": kind, "seed": seed, "status": "already_cached", "keys": keys}
                )
                continue

            per_gain_parts: dict[float, list[np.ndarray]] = {gain: [] for gain in gains}
            for document_index, document in enumerate(documents):
                rows = groups == document
                gpu = reservoir_states_multi_gain(
                    operator,
                    block[rows],
                    input_weights=projection,
                    readout_indices=readout,
                    input_indices=populations.input_indices,
                    gains=gains,
                    leak=args.leak,
                    steps_per_chunk=args.steps_per_chunk,
                    scale=calibration["mean"],
                    device=args.device,
                    torch_operator=torch_operator,
                )

                # Mandatory real parity before the first cache write.  It uses the
                # actual 165k-neuron operator, actual document and actual projection.
                if not parity_done:
                    cpu_spec = MultitagSpec(
                        seeds=tuple(args.seeds),
                        steps_per_chunk=args.steps_per_chunk,
                        gain=args.parity_gain,
                        leak=args.leak,
                        input_scale=args.target_drive_rms,
                    )
                    cpu, _ = reservoir_states(
                        operator,
                        block[rows],
                        input_weights=projection,
                        readout_indices=readout,
                        input_indices=populations.input_indices,
                        spec=cpu_spec,
                        scale=calibration["mean"],
                    )
                    parity = compare_states(cpu, gpu[args.parity_gain])
                    parity_record = {
                        "operator": kind,
                        "seed": seed,
                        "document": int(document),
                        "gain": args.parity_gain,
                        "max_abs": parity.max_abs,
                        "rmse": parity.rmse,
                        "reference_rms": parity.reference_rms,
                        "relative_rmse": parity.relative_rmse,
                        "max_abs_limit": args.parity_max_abs,
                        "relative_rmse_limit": args.parity_relative_rmse,
                    }
                    report["parity"] = parity_record
                    manifest_path.parent.mkdir(parents=True, exist_ok=True)
                    manifest_path.write_text(json.dumps(report, indent=2) + "\n")
                    if (
                        parity.max_abs > args.parity_max_abs
                        or parity.relative_rmse > args.parity_relative_rmse
                    ):
                        raise SystemExit(
                            "CPU/GPU parity failed; refusing to write cache: "
                            + json.dumps(parity_record)
                        )
                    parity_done = True

                for gain in gains:
                    per_gain_parts[gain].append(gpu[gain])

            cell_seconds = time.perf_counter() - started
            for gain in gains:
                states = np.vstack(per_gain_parts[gain]).astype(np.float32, copy=False)
                np.save(paths[gain], states)
            report["cells"].append(
                {
                    "operator": kind,
                    "seed": seed,
                    "status": "written",
                    "keys": keys,
                    "shapes": {str(g): list(np.vstack(per_gain_parts[g]).shape) for g in gains},
                    "elapsed_total_seconds": round(cell_seconds, 3),
                }
            )
            manifest_path.write_text(json.dumps(report, indent=2) + "\n")
            print(
                f"{kind} seed={seed}: wrote {len(gains)} gains "
                f"({time.perf_counter() - started:.1f}s total)",
                flush=True,
            )

            del torch_operator, operator
            if args.device.startswith("cuda"):
                torch.cuda.empty_cache()

    report["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    manifest_path.write_text(json.dumps(report, indent=2) + "\n")
    print(f"wrote cache to {args.state_cache}")
    print(f"manifest: {manifest_path}")


if __name__ == "__main__":
    main()
