from __future__ import annotations

import gzip
import hashlib
import json
from collections.abc import Iterable, Sequence
from pathlib import Path

import numpy as np


OBSERVER_SPECS = {
    "qwen": {
        "model": "Qwen/Qwen3-Embedding-0.6B",
        "revision": "97b0c61",
        "dimension": 1024,
        "batch_size": 8,
    },
    "minilm": {
        "model": "sentence-transformers/all-MiniLM-L6-v2",
        "revision": "1110a24",
        "dimension": 384,
        "batch_size": 64,
    },
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_corpus(path: Path) -> list[dict]:
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        rows = [json.loads(line) for line in stream if line.strip()]
    ids = [str(row["arxiv_id"]) for row in rows]
    if len(ids) != len(set(ids)):
        raise RuntimeError("frozen corpus contains duplicate arXiv ids")
    for row in rows:
        abstract = str(row["abstract"])
        observed = hashlib.sha256(abstract.encode("utf-8")).hexdigest()
        if observed != row["abstract_sha256"]:
            raise RuntimeError(f"abstract hash mismatch for {row['arxiv_id']}")
        if int(row["minilm_wordpieces_including_special"]) > 256:
            raise RuntimeError(f"length guard violated for {row['arxiv_id']}")
    return rows


def shard_bounds(total: int, shard_index: int, shard_count: int) -> tuple[int, int]:
    if total < 1 or shard_count < 1 or not 0 <= shard_index < shard_count:
        raise ValueError("invalid shard specification")
    start = total * shard_index // shard_count
    end = total * (shard_index + 1) // shard_count
    return start, end


def l2_normalize(matrix: np.ndarray) -> np.ndarray:
    values = np.asarray(matrix, dtype=np.float32)
    norms = np.linalg.norm(values, axis=1, keepdims=True)
    if np.any(~np.isfinite(norms)) or np.any(norms <= 0):
        raise RuntimeError("embedding matrix contains a non-finite or zero-norm row")
    return values / norms


def verify_token_lengths(model, texts: Sequence[str]) -> list[int]:
    tokenizer = model.tokenizer
    encoded = tokenizer(
        list(texts),
        add_special_tokens=True,
        truncation=False,
        padding=False,
        return_attention_mask=False,
        return_token_type_ids=False,
    )["input_ids"]
    lengths = [len(ids) for ids in encoded]
    limit = int(model.max_seq_length)
    if max(lengths, default=0) > limit:
        raise RuntimeError(
            f"runtime tokenizer would truncate: max={max(lengths)}, model_limit={limit}"
        )
    return lengths


def encode_texts(spec: dict, texts: Sequence[str]) -> tuple[np.ndarray, list[int]]:
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(
        spec["model"], revision=spec["revision"], trust_remote_code=True, device="cpu"
    )
    lengths = verify_token_lengths(model, texts)
    raw = model.encode(
        list(texts),
        batch_size=int(spec["batch_size"]),
        convert_to_numpy=True,
        normalize_embeddings=False,
        show_progress_bar=True,
    )
    raw = np.asarray(raw, dtype=np.float32)
    if raw.ndim != 2 or raw.shape[1] != int(spec["dimension"]):
        raise RuntimeError(
            f"unexpected embedding shape {raw.shape}; expected (*,{spec['dimension']})"
        )
    return raw, lengths


def write_shard(
    *,
    output_dir: Path,
    observer_key: str,
    spec: dict,
    rows: Sequence[dict],
    global_start: int,
    global_end: int,
    shard_index: int,
    shard_count: int,
    raw: np.ndarray,
    token_lengths: Sequence[int],
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{observer_key}-shard-{shard_index:03d}-of-{shard_count:03d}"
    raw_path = output_dir / f"{stem}-raw.npy"
    normalized_path = output_dir / f"{stem}-normalized.npy"
    np.save(raw_path, np.asarray(raw, dtype=np.float32), allow_pickle=False)
    np.save(normalized_path, l2_normalize(raw), allow_pickle=False)
    ids = [str(row["arxiv_id"]) for row in rows]
    manifest = {
        "schema_version": 1,
        "observer_key": observer_key,
        "observer": {key: spec[key] for key in ("model", "revision", "dimension")},
        "shard_index": shard_index,
        "shard_count": shard_count,
        "global_start": global_start,
        "global_end": global_end,
        "rows": len(rows),
        "first_arxiv_id": ids[0] if ids else None,
        "last_arxiv_id": ids[-1] if ids else None,
        "ordered_ids_sha256": hashlib.sha256("\n".join(ids).encode("utf-8")).hexdigest(),
        "token_lengths": {
            "minimum": min(token_lengths, default=None),
            "maximum": max(token_lengths, default=None),
        },
        "raw": {
            "path": raw_path.name,
            "sha256": sha256_file(raw_path),
            "dtype": "float32",
            "shape": list(raw.shape),
        },
        "normalized": {
            "path": normalized_path.name,
            "sha256": sha256_file(normalized_path),
            "dtype": "float32",
            "shape": list(raw.shape),
        },
    }
    manifest_path = output_dir / f"{stem}.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def load_matrix(shard_dir: Path, observer_key: str, view: str = "normalized") -> np.ndarray:
    if view not in {"raw", "normalized"}:
        raise ValueError("view must be raw or normalized")
    manifests = []
    for path in shard_dir.glob(f"{observer_key}-shard-*.json"):
        manifests.append(json.loads(path.read_text(encoding="utf-8")))
    manifests.sort(key=lambda item: int(item["shard_index"]))
    if not manifests:
        raise RuntimeError(f"no {observer_key} shard manifests found in {shard_dir}")
    expected_count = int(manifests[0]["shard_count"])
    if len(manifests) != expected_count:
        raise RuntimeError(
            f"incomplete {observer_key} shards: expected {expected_count}, found {len(manifests)}"
        )
    arrays = []
    cursor = 0
    for expected_index, manifest in enumerate(manifests):
        if int(manifest["shard_index"]) != expected_index:
            raise RuntimeError("non-contiguous shard indices")
        if int(manifest["global_start"]) != cursor:
            raise RuntimeError("non-contiguous shard row bounds")
        file_path = shard_dir / str(manifest[view]["path"])
        if sha256_file(file_path) != manifest[view]["sha256"]:
            raise RuntimeError(f"shard hash mismatch: {file_path}")
        array = np.load(file_path, allow_pickle=False)
        if list(array.shape) != manifest[view]["shape"]:
            raise RuntimeError(f"shard shape mismatch: {file_path}")
        arrays.append(np.asarray(array, dtype=np.float32))
        cursor = int(manifest["global_end"])
    return np.vstack(arrays)


def summarize_release_assets(paths: Iterable[Path]) -> list[dict]:
    return [
        {"path": path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)}
        for path in sorted(paths)
    ]
