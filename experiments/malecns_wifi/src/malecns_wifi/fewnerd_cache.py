"""Stage A: Few-NERD -> frozen, deduplicated, byte-synchronised multiscale channels.

The channel construction follows this programme's established convention
(``text_axis_channels.py``, ``smoke_concept_flavour_gpu.py``): for each scale in
``spec.scales``, overlapping character windows are pooled by a frozen encoder,
and the resulting anchor embeddings are linearly interpolated to *every* byte
position of the sentence. There is no tokenizer, no subword pooling, and no
per-token hidden state anywhere in this stage.

Persisting the byte-interpolated field directly does not scale: on the full
Few-NERD supervised corpus (~25M bytes) it would be ~860 GB before compression
and OOMs during construction (74M window occurrences held in memory at once).
Measured on the real corpus, window text is enormously redundant at small
scales (scale=1: 17,342x duplicate ratio; scale=2: 2,356x; scale=4: 50x) and
mildly redundant even at scale=8 (2.9x); across all 12 scales combined, only
**7.3M of 74.4M** window occurrences are textually unique. So this cache
stores each **unique window text once** (keyed by a 16-byte BLAKE2b digest,
model-independent), and stage B recomputes window spans deterministically
(``window_spans`` is a pure function of text and scale) and looks embeddings
up by hash -- the byte-resolution field is never written to disk, only
assembled transiently, per sentence batch, inside the reservoir's forward pass.

This cache is not published (no Hub upload): it is a local intermediate,
regenerated per experiment, kept in a raw memory-mappable layout instead of
parquet's row-per-embedding format specifically to bound RAM.

Layout::

    <output_dir>/
      manifest.json
      sentences.parquet        # id, split, split_index, text, fine_label, coarse_label
                                #   (fine_label/coarse_label are list<int16>, one entry per byte)
      <model-slug>/
        keys.npy                # sorted (N,) array of dtype 'S16' BLAKE2b digests
        embeddings.f32           # raw flat float32, shape (N, base_dim), row i matches keys[i]
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from malecns_wifi.multieurlex_cache import MANIFEST_NAME, _sha, model_prefix, model_slug
from malecns_wifi.text_axis_channels import (
    char_spans_to_byte_spans,
    interpolate_to_bytes,
    span_centres,
    utf8_byte_axis,
    window_spans,
)

SCHEMA = "papers/malecns-fewnerd-dedup-channel-cache-v1"
CHUNKING_POLICY = "byte-synchronised-multiscale-dedup-v1"
DATASET_PATH = "DFKI-SLT/few-nerd"
DATASET_REVISION = "205f3e9c9f3577ea2561d43f2f62dc249ab92d5b"
DEFAULT_MODELS = (
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    "intfloat/multilingual-e5-small",
)
DEFAULT_SCALES = tuple(2**i for i in range(0, 12))  # 1, 2, 4, ..., 2048 bytes
DEFAULT_SPLITS = ("train", "validation", "test")
DEFAULT_CONFIG = "supervised"
KEY_DIGEST_SIZE = 16
SENTENCES_FILE = "sentences.parquet"


def _read_manifest(output_dir: Path) -> dict[str, Any] | None:
    path = output_dir / MANIFEST_NAME
    if not path.exists():
        return None
    manifest = json.loads(path.read_text(encoding="utf-8"))
    return manifest if manifest.get("schema") == SCHEMA else None


def _write_manifest(output_dir: Path, manifest: dict[str, Any]) -> None:
    (output_dir / MANIFEST_NAME).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sentence_key(words: list[str]) -> str:
    return hashlib.sha256(" ".join(words).encode("utf-8")).hexdigest()


def window_key(text: str) -> bytes:
    """Model-independent identity of a window's text: same text, same key."""
    return hashlib.blake2b(text.encode("utf-8"), digest_size=KEY_DIGEST_SIZE).digest()


def reconstruct_text(words: list[str]) -> tuple[str, list[tuple[int, int]]]:
    """``" ".join(words)`` plus each word's ``[char_start, char_end)`` span in it."""
    parts, spans = [], []
    cursor = 0
    for i, word in enumerate(words):
        if i > 0:
            parts.append(" ")
            cursor += 1
        start = cursor
        parts.append(word)
        cursor += len(word)
        spans.append((start, cursor))
    return "".join(parts), spans


def byte_labels(
    words: list[str], fine: list[int], coarse: list[int]
) -> tuple[str, np.ndarray, np.ndarray]:
    """Reconstructed text plus per-byte fine/coarse labels (spaces -> `O` = 0)."""
    text, char_spans = reconstruct_text(words)
    axis = utf8_byte_axis(text)
    byte_fine = np.zeros(axis.byte_length, dtype=np.int64)
    byte_coarse = np.zeros(axis.byte_length, dtype=np.int64)
    for (a, b), f, c in zip(char_spans, fine, coarse):
        ba, bb = int(axis.char_to_byte[a]), int(axis.char_to_byte[b])
        byte_fine[ba:bb] = f
        byte_coarse[ba:bb] = c
    return text, byte_fine, byte_coarse


@dataclass(frozen=True)
class TokenCacheSpec:
    config: str = DEFAULT_CONFIG
    models: tuple[str, ...] = DEFAULT_MODELS
    scales: tuple[int, ...] = DEFAULT_SCALES
    splits: tuple[str, ...] = DEFAULT_SPLITS
    limit_per_split: int | None = None
    max_tokens: int = 64  # cap on pre-tokenized WORDS per sentence, bounding byte length
    dataset_path: str = DATASET_PATH
    dataset_revision: str = DATASET_REVISION

    @property
    def chunking_version(self) -> str:
        scales = "-".join(map(str, self.scales))
        return f"{CHUNKING_POLICY}:scales={scales}:max_words={self.max_tokens}"

    def data_payload(self) -> dict[str, Any]:
        return {
            "dataset": {
                "path": self.dataset_path, "revision": self.dataset_revision, "config": self.config,
                "splits": list(self.splits), "limit_per_split": self.limit_per_split,
            },
            "chunking": self.chunking_version,
            "normalize": "unit-per-model-per-scale-then-concat",
        }

    def model_fingerprint(self, model_name: str, model_revision: str | None) -> str:
        payload = {"schema": SCHEMA, **self.data_payload(),
                   "encoder": {"name": model_name, "revision": model_revision, "prefix": model_prefix(model_name)}}
        return _sha(payload)

    def fingerprint(self, model_revisions: dict[str, str | None]) -> str:
        payload = {"schema": SCHEMA, **self.data_payload(),
                   "encoders": [{"name": n, "revision": model_revisions.get(n), "prefix": model_prefix(n)} for n in self.models]}
        return _sha(payload)


def load_fewnerd(spec: TokenCacheSpec) -> dict[str, Any]:
    """Official Few-NERD split, untouched, optionally capped by a deterministic prefix."""
    from datasets import load_dataset

    ds = load_dataset(spec.dataset_path, spec.config, revision=spec.dataset_revision)
    fine_names = ds["train"].features["fine_ner_tags"].feature.names
    coarse_names = ds["train"].features["ner_tags"].feature.names
    documents: dict[str, list[dict[str, Any]]] = {}
    for split in spec.splits:
        rows = ds[split]
        if spec.limit_per_split is not None:
            rows = rows.select(range(min(spec.limit_per_split, len(rows))))
        documents[split] = [
            {"id": row["id"], "tokens": row["tokens"], "fine": row["fine_ner_tags"], "coarse": row["ner_tags"]}
            for row in rows
        ]
    return {"documents": documents, "fine_names": fine_names, "coarse_names": coarse_names}


def _model_revision(model) -> str | None:
    try:
        return getattr(model[0].auto_model.config, "_commit_hash", None)
    except Exception:  # pragma: no cover
        return None


@dataclass
class SentenceRecord:
    id: str
    split: str
    split_index: int
    text: str
    byte_fine: np.ndarray
    byte_coarse: np.ndarray


def build_sentence_records(spec: TokenCacheSpec, documents: dict[str, list[dict[str, Any]]]) -> list[SentenceRecord]:
    records = []
    for split in spec.splits:
        for index, doc in enumerate(documents[split]):
            words = doc["tokens"][: spec.max_tokens]
            fine = doc["fine"][: spec.max_tokens]
            coarse = doc["coarse"][: spec.max_tokens]
            text, byte_fine, byte_coarse = byte_labels(words, fine, coarse)
            records.append(SentenceRecord(doc["id"], split, index, text, byte_fine, byte_coarse))
    return records


def write_sentences(records: list[SentenceRecord], *, output_dir: Path) -> Path:
    table = pa.table({
        "id": pa.array([r.id for r in records], type=pa.string()),
        "split": pa.array([r.split for r in records], type=pa.string()),
        "split_index": pa.array([r.split_index for r in records], type=pa.int32()),
        "text": pa.array([r.text for r in records], type=pa.string()),
        "fine_label": pa.array([r.byte_fine.astype(np.int16).tolist() for r in records], type=pa.list_(pa.int16())),
        "coarse_label": pa.array([r.byte_coarse.astype(np.int16).tolist() for r in records], type=pa.list_(pa.int16())),
    })
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / SENTENCES_FILE
    pq.write_table(table, path, compression="zstd")
    return path


def collect_unique_windows(texts: list[str], scales: tuple[int, ...]) -> dict[bytes, str]:
    """Every distinct window text across all sentences and scales, keyed once."""
    unique: dict[bytes, str] = {}
    for text in texts:
        for scale in scales:
            for a, b in window_spans(text, scale):
                window = text[a:b]
                key = window_key(window)
                if key not in unique:
                    unique[key] = window
    return unique


def encode_unique_windows(
    model_name: str, unique: dict[bytes, str], *, device: str, batch_size: int, slice_size: int = 4096,
    progress=None,
) -> tuple[np.ndarray, list[bytes], dict[str, Any]]:
    """Encode every unique window once; returns (embeddings, sorted_keys, info).

    ``embeddings[i]`` corresponds to ``sorted_keys[i]``; keys are sorted so
    stage B can binary-search them without loading a hash map into memory.
    """
    from sentence_transformers import SentenceTransformer

    t0 = time.perf_counter()
    model = SentenceTransformer(model_name, device=device)
    load_seconds = time.perf_counter() - t0
    prefix = model_prefix(model_name)
    dim = int(model.get_sentence_embedding_dimension())

    sorted_keys = sorted(unique.keys())
    texts = [unique[k] for k in sorted_keys]

    t1 = time.perf_counter()
    parts = []
    for start in range(0, len(texts), slice_size):
        local = texts[start:start + slice_size]
        parts.append(model.encode(
            [prefix + w for w in local], batch_size=batch_size, convert_to_numpy=True,
            normalize_embeddings=False, show_progress_bar=False,
        ).astype(np.float32))
        if progress is not None:
            progress(model_name, min(start + len(local), len(texts)), len(texts), t1)
    encode_seconds = time.perf_counter() - t1
    embeddings = np.concatenate(parts, axis=0) if parts else np.zeros((0, dim), dtype=np.float32)

    info = {
        "name": model_name, "slug": model_slug(model_name), "revision": _model_revision(model),
        "base_dim": dim, "load_seconds": load_seconds, "encode_seconds": encode_seconds,
        "seconds": load_seconds + encode_seconds, "unique_windows": len(sorted_keys),
        "windows_per_second": (len(sorted_keys) / encode_seconds) if encode_seconds else None,
        "device": device, "batch_size": int(batch_size), "prefix": prefix,
    }
    del model
    return embeddings, sorted_keys, info


def write_dedup_table(model_dir: Path, embeddings: np.ndarray, sorted_keys: list[bytes]) -> dict[str, int]:
    model_dir.mkdir(parents=True, exist_ok=True)
    keys_array = np.frombuffer(b"".join(sorted_keys), dtype=f"S{KEY_DIGEST_SIZE}")
    np.save(model_dir / "keys.npy", keys_array)
    embeddings = np.ascontiguousarray(embeddings, dtype=np.float32)
    embeddings.tofile(model_dir / "embeddings.f32")
    return {
        "keys_bytes": int((model_dir / "keys.npy").stat().st_size),
        "embeddings_bytes": int((model_dir / "embeddings.f32").stat().st_size),
    }


def build_cache(
    spec: TokenCacheSpec, *, output_dir: Path, device: str = "cuda", batch_size: int = 256,
    loaded: dict[str, Any] | None = None, progress=None,
) -> dict[str, Any]:
    started = time.perf_counter()
    if loaded is None:
        loaded = load_fewnerd(spec)
    records = build_sentence_records(spec, loaded["documents"])
    texts = [r.text for r in records]
    total_bytes = int(sum(len(r.byte_fine) for r in records))

    output_dir.mkdir(parents=True, exist_ok=True)
    write_sentences(records, output_dir=output_dir)

    t0 = time.perf_counter()
    unique = collect_unique_windows(texts, spec.scales)
    dedup_seconds = time.perf_counter() - t0
    total_occurrences = sum(len(window_spans(t, s)) for t in texts for s in spec.scales)

    manifest = {
        "schema": SCHEMA,
        "task": "fine-grained NER (Few-NERD), byte-resolution, deduplicated windows",
        "dataset": {
            "path": spec.dataset_path, "revision": spec.dataset_revision, "config": spec.config,
            "splits": {s: len(loaded["documents"][s]) for s in spec.splits},
            "limit_per_split": spec.limit_per_split, "partial": spec.limit_per_split is not None,
        },
        "chunking": {"policy": CHUNKING_POLICY, "scales": list(spec.scales), "max_words": spec.max_tokens,
                    "version": spec.chunking_version},
        "labels": {"fine": loaded["fine_names"], "coarse": loaded["coarse_names"]},
        "sentences": len(records), "bytes": total_bytes,
        "dedup": {"unique_windows": len(unique), "total_occurrences": total_occurrences,
                  "dedup_ratio": (total_occurrences / len(unique)) if unique else None, "seconds": dedup_seconds},
        "encoders": [],
    }

    for model_name in spec.models:
        embeddings, sorted_keys, info = encode_unique_windows(
            model_name, unique, device=device, batch_size=batch_size, progress=progress
        )
        sizes = write_dedup_table(output_dir / info["slug"], embeddings, sorted_keys)
        info.update(sizes)
        info["fingerprint"] = spec.model_fingerprint(model_name, info.get("revision"))
        manifest["encoders"] = [e for e in manifest["encoders"] if e["name"] != model_name] + [info]
        ordered = sorted(manifest["encoders"], key=lambda e: DEFAULT_MODELS.index(e["name"]) if e["name"] in DEFAULT_MODELS else 99)
        manifest["encoders"] = ordered
        manifest["encoder_order"] = [e["name"] for e in ordered]
        manifest["semantic_dim"] = int(sum(e["base_dim"] for e in ordered) * len(spec.scales))
        manifest["fingerprint"] = (
            spec.fingerprint({e["name"]: e.get("revision") for e in ordered})
            if {e["name"] for e in ordered} == set(spec.models) else None
        )
        manifest["seconds"] = time.perf_counter() - started
        manifest["total_bytes_on_disk"] = int(sum(e["keys_bytes"] + e["embeddings_bytes"] for e in ordered))
        _write_manifest(output_dir, manifest)
    return manifest


# -- loading / assembly -------------------------------------------------------

@dataclass
class DedupEncoder:
    name: str
    base_dim: int
    sorted_keys: np.ndarray  # (N,) dtype S16, sorted
    embeddings: np.ndarray   # memory-mapped (N, base_dim) float32

    def lookup(self, text: str) -> np.ndarray:
        key = np.frombuffer(window_key(text), dtype=f"S{KEY_DIGEST_SIZE}")[0]
        index = np.searchsorted(self.sorted_keys, key)
        if index >= len(self.sorted_keys) or self.sorted_keys[index] != key:
            raise KeyError(f"window not found in dedup cache: {text!r}")
        return self.embeddings[index]

    def lookup_many(self, texts: list[str]) -> np.ndarray:
        keys = np.array([np.frombuffer(window_key(t), dtype=f"S{KEY_DIGEST_SIZE}")[0] for t in texts])
        indices = np.searchsorted(self.sorted_keys, keys)
        indices = np.clip(indices, 0, len(self.sorted_keys) - 1)
        found = self.sorted_keys[indices] == keys
        if not np.all(found):
            missing = [t for t, ok in zip(texts, found) if not ok]
            raise KeyError(f"{len(missing)} window(s) not found in dedup cache, e.g. {missing[0]!r}")
        return np.asarray(self.embeddings[indices], dtype=np.float32)


def resolve_cache_dir(location: str | Path) -> Path:
    text = str(location)
    if text.startswith("hf:"):
        from huggingface_hub import snapshot_download

        repo, _, revision = text[3:].partition("@")
        return Path(snapshot_download(repo_id=repo, repo_type="dataset", revision=revision or None))
    return Path(text)


@dataclass
class FewnerdCache:
    manifest: dict[str, Any]
    directory: Path
    sentences: Any  # pyarrow.Table: id, split, split_index, text, fine_label, coarse_label
    encoders: dict[str, DedupEncoder]
    scales: tuple[int, ...]

    @property
    def label_names(self) -> dict[str, list[str]]:
        return self.manifest["labels"]

    def assemble_channel(self, model_names: tuple[str, ...], text: str) -> np.ndarray:
        """Byte-synchronised fused channel for one sentence: [byte_length, sum(base_dim)*len(scales)]."""
        axis = utf8_byte_axis(text)
        pieces = []
        for name in model_names:
            enc = self.encoders[name]
            for scale in self.scales:
                spans = window_spans(text, scale)
                windows = [text[a:b] for a, b in spans]
                anchors = enc.lookup_many(windows)
                byte_spans = char_spans_to_byte_spans(text, spans)
                field = interpolate_to_bytes(anchors, span_centres(byte_spans), byte_length=axis.byte_length)
                norm = np.maximum(np.linalg.norm(field, axis=1, keepdims=True), 1e-12)
                pieces.append((field / norm).astype(np.float32))
        return np.concatenate(pieces, axis=1) if len(pieces) > 1 else pieces[0]


def load_cache(
    location: str | Path, *, spec: TokenCacheSpec | None = None, models: tuple[str, ...] | None = None,
) -> FewnerdCache:
    directory = resolve_cache_dir(location)
    manifest = _read_manifest(directory)
    if manifest is None:
        raise RuntimeError(f"no {SCHEMA} manifest in {directory}")
    if models is None:
        models = spec.models if spec is not None else tuple(
            manifest.get("encoder_order") or [e["name"] for e in manifest["encoders"]]
        )
    by_name = {e["name"]: e for e in manifest["encoders"]}
    missing = [m for m in models if m not in by_name]
    if missing:
        raise RuntimeError(f"dedup cache lacks encoders {missing}")
    if spec is not None:
        for name in models:
            expected = spec.model_fingerprint(name, by_name[name].get("revision"))
            if by_name[name].get("fingerprint") != expected:
                raise RuntimeError(f"dedup cache fingerprint mismatch for {name}: dataset/chunking/encoder differs")

    encoders = {}
    for name in models:
        info = by_name[name]
        model_dir = directory / info["slug"]
        keys = np.load(model_dir / "keys.npy")
        embeddings = np.memmap(model_dir / "embeddings.f32", dtype=np.float32, mode="r",
                               shape=(len(keys), info["base_dim"]))
        encoders[name] = DedupEncoder(name=name, base_dim=info["base_dim"], sorted_keys=keys, embeddings=embeddings)

    sentences = pq.read_table(directory / SENTENCES_FILE)
    scales = tuple(manifest["chunking"]["scales"])
    return FewnerdCache(manifest=manifest, directory=directory, sentences=sentences, encoders=encoders, scales=scales)
