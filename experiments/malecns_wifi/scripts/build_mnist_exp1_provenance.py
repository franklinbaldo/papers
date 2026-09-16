#!/usr/bin/env python3
"""Build a fail-fast provenance manifest for Canonical MNIST Exp. 1.

Records and verifies the inputs that define the experiment:
MNIST features, sample folds, graph bytes, and the canonical MaleCNS SpMV body order.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

EXPECTED_SAMPLES = 1000
EXPECTED_LABELS = 10
EXPECTED_FEATURE_DIM = 784
EXPECTED_NEURONS = 165122
EXPECTED_FOLDS = 10


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def array_sha256(array: np.ndarray) -> str:
    values = np.ascontiguousarray(array)
    return sha256_bytes(values.tobytes(order="C"))


def fail(message: str) -> None:
    raise SystemExit(f"provenance invariant failed: {message}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, default=Path("artifacts/runtime-v1/mnist-1000-features.npz"))
    parser.add_argument("--graph", type=Path, default=Path("artifacts/runtime-v1/graph.npz"))
    parser.add_argument("--n-folds", type=int, default=EXPECTED_FOLDS)
    parser.add_argument("--output", type=Path, default=Path("artifacts/runtime-v1/mnist-exp1-provenance.json"))
    args = parser.parse_args()

    if args.n_folds != EXPECTED_FOLDS:
        fail(f"n_folds={args.n_folds}, expected frozen value {EXPECTED_FOLDS}")
    if not args.features.is_file():
        fail(f"missing features bundle: {args.features}")
    if not args.graph.is_file():
        fail(f"missing graph bundle: {args.graph}")

    features_bytes_sha256 = sha256_file(args.features)
    graph_bytes_sha256 = sha256_file(args.graph)

    with np.load(args.features, allow_pickle=False) as bundle:
        absolute = np.asarray(bundle["absolute"], dtype=np.float32)
        tag_masks = np.asarray(bundle["tag_masks"], dtype=np.float32)
        groups = np.asarray(bundle["groups"], dtype=np.int64)
        tag_embeddings = np.asarray(bundle["tag_embeddings"], dtype=np.float32)

    if absolute.shape != (EXPECTED_SAMPLES, EXPECTED_FEATURE_DIM):
        fail(f"unexpected absolute shape: {absolute.shape}")
    if tag_masks.shape != (EXPECTED_SAMPLES, EXPECTED_LABELS):
        fail(f"unexpected tag_masks shape: {tag_masks.shape}")
    if groups.shape != (EXPECTED_SAMPLES,):
        fail(f"unexpected groups shape: {groups.shape}")
    if tag_embeddings.shape != (EXPECTED_LABELS, EXPECTED_FEATURE_DIM):
        fail(f"unexpected tag_embeddings shape: {tag_embeddings.shape}")

    chunk_folds = np.array([i % args.n_folds for i in range(EXPECTED_SAMPLES)], dtype=np.int64)
    fold_counts = [int((chunk_folds == fold).sum()) for fold in range(args.n_folds)]
    if any(count == 0 for count in fold_counts):
        fail(f"empty fold detected in {fold_counts}")

    with np.load(args.graph, allow_pickle=False) as bundle:
        if "bodies" not in bundle:
            fail("graph.npz lacks canonical `bodies` array")
        bodies = np.asarray(bundle["bodies"], dtype=np.int64)
        if "shape" not in bundle:
            fail("graph.npz lacks canonical `shape` array")
        shape = tuple(int(x) for x in bundle["shape"])

    if shape != (EXPECTED_NEURONS, EXPECTED_NEURONS):
        fail(f"graph.npz shape {shape} != expected ({EXPECTED_NEURONS}, {EXPECTED_NEURONS})")
    if bodies.shape != (EXPECTED_NEURONS,):
        fail(f"graph.npz bodies {bodies.shape} != expected ({EXPECTED_NEURONS},)")

    bodies_le_bytes = bodies.astype("<i8", copy=False).tobytes(order="C")
    spmv_body_order_sha256 = sha256_bytes(bodies_le_bytes)

    array_hashes = {
        "absolute_sha256": array_sha256(absolute),
        "tag_masks_sha256": array_sha256(tag_masks),
        "groups_sha256": array_sha256(groups),
        "chunk_folds_sha256": array_sha256(chunk_folds),
        "tag_embeddings_sha256": array_sha256(tag_embeddings),
        "spmv_body_order_sha256_le_i64": spmv_body_order_sha256,
    }

    manifest = {
        "format": "papers/malecns-mnist-exp1-provenance-v1",
        "protocol": {
            "dataset": "MNIST",
            "samples": EXPECTED_SAMPLES,
            "feature_dim": EXPECTED_FEATURE_DIM,
            "labels": EXPECTED_LABELS,
            "neurons": EXPECTED_NEURONS,
            "n_folds": args.n_folds,
            "fold_rule": "sample_idx % 10",
        },
        "files": {
            "features": {"path": str(args.features).replace("\\", "/"), "sha256": features_bytes_sha256},
            "graph": {"path": str(args.graph).replace("\\", "/"), "sha256": graph_bytes_sha256},
        },
        "fold_counts": fold_counts,
        "arrays": array_hashes,
    }

    canonical_text = json.dumps(manifest, indent=2, sort_keys=True)
    provenance_hash = sha256_bytes(canonical_text.encode("utf-8"))
    manifest["provenance_sha256"] = provenance_hash

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
