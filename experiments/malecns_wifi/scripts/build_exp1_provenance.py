#!/usr/bin/env python3
"""Build a fail-fast provenance manifest for MultiEURLEX Exp. 1.

This does not change the frozen evaluation protocol. It records and verifies the
inputs that define the experiment: corpus/features, document folds, graph bytes,
and the canonical MaleCNS SpMV body order.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

EXPECTED_CHUNKS = 1000
EXPECTED_DOCUMENTS = 477
EXPECTED_LABELS = 21
EXPECTED_EMBEDDING_DIM = 384
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
    parser.add_argument("--features", type=Path, default=Path("artifacts/runtime-v1/multieurlex-1000-features.npz"))
    parser.add_argument("--graph", type=Path, default=Path("artifacts/runtime-v1/graph.npz"))
    parser.add_argument("--n-folds", type=int, default=EXPECTED_FOLDS)
    parser.add_argument("--output", type=Path, default=Path("artifacts/runtime-v1/multieurlex-exp1-provenance.json"))
    args = parser.parse_args()

    if args.n_folds != EXPECTED_FOLDS:
        fail(f"n_folds={args.n_folds}, expected frozen value {EXPECTED_FOLDS}")
    if not args.features.is_file():
        fail(f"missing features bundle: {args.features}")
    if not args.graph.is_file():
        fail(f"missing graph bundle: {args.graph}")

    features = np.load(args.features, allow_pickle=False)
    required_features = {"absolute", "tag_masks", "groups", "tag_embeddings"}
    missing = required_features - set(features.files)
    if missing:
        fail(f"features bundle missing arrays: {sorted(missing)}")

    absolute = np.asarray(features["absolute"])
    tag_masks = np.asarray(features["tag_masks"])
    groups = np.asarray(features["groups"])
    tag_embeddings = np.asarray(features["tag_embeddings"])

    if absolute.shape != (EXPECTED_CHUNKS, EXPECTED_EMBEDDING_DIM):
        fail(f"absolute.shape={absolute.shape}, expected {(EXPECTED_CHUNKS, EXPECTED_EMBEDDING_DIM)}")
    if tag_masks.shape != (EXPECTED_CHUNKS, EXPECTED_LABELS):
        fail(f"tag_masks.shape={tag_masks.shape}, expected {(EXPECTED_CHUNKS, EXPECTED_LABELS)}")
    if groups.shape != (EXPECTED_CHUNKS,):
        fail(f"groups.shape={groups.shape}, expected {(EXPECTED_CHUNKS,)}")
    if tag_embeddings.shape[0] != EXPECTED_LABELS:
        fail(f"tag_embeddings labels={tag_embeddings.shape[0]}, expected {EXPECTED_LABELS}")

    unique_docs = np.unique(groups)
    if unique_docs.size != EXPECTED_DOCUMENTS:
        fail(f"documents={unique_docs.size}, expected {EXPECTED_DOCUMENTS}")

    doc_to_fold = {int(doc): int(doc) % args.n_folds for doc in unique_docs}
    chunk_folds = np.asarray([doc_to_fold[int(group)] for group in groups], dtype=np.uint8)
    fold_counts = np.bincount(chunk_folds, minlength=args.n_folds)
    if int(fold_counts.sum()) != EXPECTED_CHUNKS:
        fail("fold assignment does not cover every chunk exactly once")

    graph = np.load(args.graph, allow_pickle=False)
    if "bodies" not in graph.files:
        fail("graph.npz lacks canonical `bodies` array")
    bodies = np.asarray(graph["bodies"], dtype=np.int64)
    if bodies.shape != (EXPECTED_NEURONS,):
        fail(f"bodies.shape={bodies.shape}, expected {(EXPECTED_NEURONS,)}")
    if np.unique(bodies).size != EXPECTED_NEURONS:
        fail("canonical body IDs are not unique")
    if np.any(bodies[1:] <= bodies[:-1]):
        fail("canonical body IDs are not strictly increasing")

    body_order_le_i64 = bodies.astype("<i8", copy=False)
    manifest = {
        "format": "papers/malecns-multieurlex-exp1-provenance-v1",
        "protocol": {
            "chunks": EXPECTED_CHUNKS,
            "documents": EXPECTED_DOCUMENTS,
            "labels": EXPECTED_LABELS,
            "embedding_dim": EXPECTED_EMBEDDING_DIM,
            "neurons": EXPECTED_NEURONS,
            "n_folds": EXPECTED_FOLDS,
            "fold_rule": "document_id % 10",
        },
        "files": {
            "features": {"path": str(args.features), "sha256": sha256_file(args.features)},
            "graph": {"path": str(args.graph), "sha256": sha256_file(args.graph)},
        },
        "arrays": {
            "absolute_sha256": array_sha256(absolute),
            "tag_masks_sha256": array_sha256(tag_masks),
            "groups_sha256": array_sha256(groups),
            "tag_embeddings_sha256": array_sha256(tag_embeddings),
            "chunk_folds_sha256": array_sha256(chunk_folds),
            "spmv_body_order_sha256_le_i64": sha256_bytes(body_order_le_i64.tobytes(order="C")),
        },
        "fold_counts": [int(value) for value in fold_counts],
    }

    canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    manifest["provenance_sha256"] = sha256_bytes(canonical)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "provenance_sha256": manifest["provenance_sha256"], "spmv_body_order_sha256_le_i64": manifest["arrays"]["spmv_body_order_sha256_le_i64"], "fold_counts": manifest["fold_counts"]}, indent=2))


if __name__ == "__main__":
    main()
