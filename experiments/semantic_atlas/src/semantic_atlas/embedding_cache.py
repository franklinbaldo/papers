from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np

_FORBIDDEN_IDENTITY_KEYS = {
    "api_key",
    "authorization",
    "credential",
    "credentials",
    "header",
    "headers",
    "password",
    "secret",
    "token",
}


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _validate_identity(value: object, path: str = "observer") -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            lowered = str(key).lower()
            if lowered in _FORBIDDEN_IDENTITY_KEYS:
                raise ValueError(f"secret-bearing key is forbidden in cache identity: {path}.{key}")
            _validate_identity(nested, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, nested in enumerate(value):
            _validate_identity(nested, f"{path}[{index}]")


def _corpus_record(
    source_commit: str,
    paths_by_split: Mapping[str, Sequence[str]],
    texts_by_split: Mapping[str, Sequence[str]],
) -> tuple[dict[str, list[dict[str, str]]], str]:
    if set(paths_by_split) != set(texts_by_split):
        raise ValueError("paths/text splits must match")

    record: dict[str, list[dict[str, str]]] = {}
    for split in sorted(paths_by_split):
        paths = list(paths_by_split[split])
        texts = list(texts_by_split[split])
        if len(paths) != len(texts):
            raise ValueError(f"path/text count mismatch for split {split}")
        if len(paths) != len(set(paths)):
            raise ValueError(f"duplicate corpus path in split {split}")
        record[split] = [
            {"path": path, "text_sha256": _sha256(text.encode("utf-8"))}
            for path, text in zip(paths, texts, strict=True)
        ]

    all_paths = [item["path"] for items in record.values() for item in items]
    if len(all_paths) != len(set(all_paths)):
        raise ValueError("corpus paths must be disjoint across splits")

    identity = {
        "source_commit": source_commit,
        "splits": record,
    }
    return record, _sha256(_canonical_json(identity))


@dataclass(frozen=True)
class EmbeddingCacheRef:
    manifest_path: Path
    data_path: Path
    data_sha256: str
    corpus_sha256: str


def write_embedding_cache(
    directory: Path,
    *,
    observer: Mapping[str, object],
    source_commit: str,
    paths_by_split: Mapping[str, Sequence[str]],
    texts_by_split: Mapping[str, Sequence[str]],
    raw_by_split: Mapping[str, np.ndarray],
    normalized_by_split: Mapping[str, np.ndarray],
) -> EmbeddingCacheRef:
    """Persist observer outputs once, then address them by their content hash.

    The NPZ is the primary numeric observation. The JSON sidecar records corpus
    identity and observer provenance but deliberately excludes credentials.
    """

    _validate_identity(observer)
    split_names = set(paths_by_split)
    if split_names != set(raw_by_split) or split_names != set(normalized_by_split):
        raise ValueError("corpus and embedding splits must match")

    corpus, corpus_sha256 = _corpus_record(source_commit, paths_by_split, texts_by_split)
    arrays: dict[str, np.ndarray] = {}
    array_meta: dict[str, dict[str, object]] = {}
    for split in sorted(split_names):
        raw = np.asarray(raw_by_split[split])
        normalized = np.asarray(normalized_by_split[split])
        expected_rows = len(paths_by_split[split])
        if raw.ndim != 2 or normalized.ndim != 2:
            raise ValueError(f"embeddings must be 2D for split {split}")
        if len(raw) != expected_rows or len(normalized) != expected_rows:
            raise ValueError(f"embedding row count mismatch for split {split}")
        if raw.shape != normalized.shape:
            raise ValueError(f"raw/normalized shape mismatch for split {split}")
        if not np.all(np.isfinite(raw)) or not np.all(np.isfinite(normalized)):
            raise ValueError(f"non-finite embedding value in split {split}")

        arrays[f"raw_{split}"] = raw
        arrays[f"normalized_{split}"] = normalized
        array_meta[split] = {
            "shape": list(raw.shape),
            "raw_dtype": str(raw.dtype),
            "normalized_dtype": str(normalized.dtype),
        }

    directory.mkdir(parents=True, exist_ok=True)
    staging = directory / ".embedding-cache-staging.npz"
    np.savez_compressed(staging, **arrays)
    data_bytes = staging.read_bytes()
    data_sha256 = _sha256(data_bytes)
    data_name = f"embeddings-{data_sha256}.npz"
    data_path = directory / data_name
    if data_path.exists() and data_path.read_bytes() != data_bytes:
        raise RuntimeError("content-address collision")
    if not data_path.exists():
        staging.replace(data_path)
    else:
        staging.unlink()

    manifest = {
        "schema_version": 1,
        "kind": "semantic-atlas-embedding-cache",
        "observer": dict(observer),
        "source_commit": source_commit,
        "corpus_sha256": corpus_sha256,
        "corpus": corpus,
        "arrays": array_meta,
        "normalization": "l2 row normalization stored separately from raw observer output",
        "data_file": data_name,
        "data_sha256": data_sha256,
    }
    manifest_bytes = _canonical_json(manifest) + b"\n"
    manifest_path = directory / f"embeddings-{data_sha256}.json"
    manifest_path.write_bytes(manifest_bytes)
    return EmbeddingCacheRef(
        manifest_path=manifest_path,
        data_path=data_path,
        data_sha256=data_sha256,
        corpus_sha256=corpus_sha256,
    )


def load_embedding_cache(manifest_path: Path) -> tuple[dict, dict[str, np.ndarray]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or manifest.get("kind") != "semantic-atlas-embedding-cache":
        raise ValueError("unsupported embedding cache manifest")
    _validate_identity(manifest.get("observer", {}))
    data_path = manifest_path.parent / manifest["data_file"]
    data_bytes = data_path.read_bytes()
    if _sha256(data_bytes) != manifest["data_sha256"]:
        raise ValueError("embedding cache data hash mismatch")

    with np.load(data_path, allow_pickle=False) as stored:
        arrays = {name: np.asarray(stored[name]) for name in stored.files}

    for split, meta in manifest["arrays"].items():
        raw = arrays[f"raw_{split}"]
        normalized = arrays[f"normalized_{split}"]
        if list(raw.shape) != meta["shape"] or list(normalized.shape) != meta["shape"]:
            raise ValueError(f"embedding cache shape mismatch for split {split}")
    return manifest, arrays
