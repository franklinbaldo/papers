"""Stage A: Few-NERD -> frozen, byte-synchronised multiscale semantic channels.

Same design as ``multieurlex_cache`` (one parquet per frozen encoder, joined by
row key, published as a versioned HF dataset), but the unit is a **UTF-8 byte**
of the reconstructed sentence text, not a document chunk -- and the channel
construction follows this programme's established convention
(``text_axis_channels.py``, ``smoke_concept_flavour_gpu.py``): for each scale in
``spec.scales``, overlapping character windows are pooled by the frozen
encoder, and the resulting anchor embeddings are linearly interpolated to
*every* byte position. Channels from every (model, scale) pair are
unit-normalised and concatenated -- there is no tokenizer, no subword pooling,
and no per-token hidden state anywhere in this stage.

Few-NERD gives pre-tokenized words, not raw text, so the sentence is
reconstructed as ``" ".join(words)``; each word's fine/coarse label is
broadcast onto its own byte span (via the same `utf8_byte_axis` used for the
channels), and the single-space bytes between words carry label `O`. This is a
preregistered, documented approximation of the original text, not a change to
any label.

Columns per row::

    id | config | split | split_index | byte_index | text_sha256
    | embedding (list<float32>) | fine_label | coarse_label | dataset_revision
    | hf_subset (=config) | model_name | model_revision | chunking_version
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
from malecns_wifi.text_axis_channels import char_spans_to_byte_spans, utf8_byte_axis, window_spans

SCHEMA = "papers/malecns-fewnerd-byte-channel-cache-v1"
CHUNKING_POLICY = "byte-synchronised-multiscale-v1"
DATASET_PATH = "DFKI-SLT/few-nerd"
DATASET_REVISION = "205f3e9c9f3577ea2561d43f2f62dc249ab92d5b"
DEFAULT_MODELS = (
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    "intfloat/multilingual-e5-small",
)
DEFAULT_SCALES = tuple(2**i for i in range(0, 12))  # 1, 2, 4, ..., 2048 bytes
DEFAULT_SPLITS = ("train", "validation", "test")
DEFAULT_CONFIG = "supervised"
DEFAULT_HUB_REPO = "franklinbaldo/fewnerd-semantic-cache"


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
class ByteTable:
    """Per-byte rows (labels only; embeddings are encoded separately per model)."""

    ids: list[str] = field(default_factory=list)
    splits: list[str] = field(default_factory=list)
    split_index: list[int] = field(default_factory=list)
    byte_index: list[int] = field(default_factory=list)
    text_sha256: list[str] = field(default_factory=list)
    fine_label: list[int] = field(default_factory=list)
    coarse_label: list[int] = field(default_factory=list)
    sentence_texts: list[str] = field(default_factory=list)  # one per sentence, for encoding

    @classmethod
    def from_documents(cls, spec: TokenCacheSpec, documents: dict[str, list[dict[str, Any]]]) -> "ByteTable":
        table = cls()
        for split in spec.splits:
            for index, doc in enumerate(documents[split]):
                words = doc["tokens"][: spec.max_tokens]
                fine = doc["fine"][: spec.max_tokens]
                coarse = doc["coarse"][: spec.max_tokens]
                text, byte_fine, byte_coarse = byte_labels(words, fine, coarse)
                key = sentence_key(words)
                for byte_i in range(len(byte_fine)):
                    table.ids.append(doc["id"])
                    table.splits.append(split)
                    table.split_index.append(index)
                    table.byte_index.append(byte_i)
                    table.text_sha256.append(key)
                    table.fine_label.append(int(byte_fine[byte_i]))
                    table.coarse_label.append(int(byte_coarse[byte_i]))
                table.sentence_texts.append(text)
        return table

    def __len__(self) -> int:
        return len(self.ids)


def encode_model(
    model_name: str, texts: list[str], *, scales: tuple[int, ...], device: str, batch_size: int,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Byte-synchronised multiscale channel for every sentence, one frozen encoder.

    For each scale, overlapping character windows are pooled by the encoder and
    linearly interpolated onto the sentence's byte axis (``text_axis_channels``);
    each (scale) field is unit-normalised per byte, then concatenated across
    scales. All windows of all sentences and scales are encoded in one batched
    pass for throughput.
    """
    from sentence_transformers import SentenceTransformer

    t0 = time.perf_counter()
    model = SentenceTransformer(model_name, device=device)
    load_seconds = time.perf_counter() - t0
    prefix = model_prefix(model_name)
    dim = int(model.get_sentence_embedding_dimension())

    axes = [utf8_byte_axis(text) for text in texts]
    spans_by_sentence: list[dict[int, list[tuple[int, int]]]] = []
    flat_windows: list[str] = []
    provenance: list[tuple[int, int]] = []  # (sentence_index, scale)
    for si, text in enumerate(texts):
        local = {}
        for scale in scales:
            spans = window_spans(text, scale)
            local[scale] = spans
            for a, b in spans:
                flat_windows.append(text[a:b])
                provenance.append((si, scale))
        spans_by_sentence.append(local)

    t1 = time.perf_counter()
    parts = []
    for start in range(0, len(flat_windows), 2048):
        local = flat_windows[start:start + 2048]
        parts.append(model.encode(
            [prefix + w for w in local], batch_size=batch_size, convert_to_numpy=True,
            normalize_embeddings=False, show_progress_bar=False,
        ))
    encode_seconds = time.perf_counter() - t1
    flat_embeddings = np.concatenate(parts, axis=0) if parts else np.zeros((0, dim), dtype=np.float32)

    grouped: dict[tuple[int, int], list[np.ndarray]] = {}
    for (si, scale), vector in zip(provenance, flat_embeddings):
        grouped.setdefault((si, scale), []).append(vector)

    per_sentence_fields = []
    for si, text in enumerate(texts):
        axis = axes[si]
        scale_fields = []
        for scale in scales:
            spans = spans_by_sentence[si][scale]
            anchors = np.asarray(grouped[(si, scale)], dtype=np.float32)
            byte_spans = char_spans_to_byte_spans(text, spans)
            field = _byte_aligned_scale(anchors, byte_spans, byte_length=axis.byte_length)
            norm = np.maximum(np.linalg.norm(field, axis=1, keepdims=True), 1e-12)
            scale_fields.append((field / norm).astype(np.float32))
        per_sentence_fields.append(np.concatenate(scale_fields, axis=1))
    embeddings = (
        np.concatenate(per_sentence_fields, axis=0) if per_sentence_fields else np.zeros((0, dim * len(scales)), dtype=np.float32)
    )
    info = {
        "name": model_name, "slug": model_slug(model_name), "revision": _model_revision(model),
        "dim": int(embeddings.shape[1]), "base_dim": dim, "scales": list(scales),
        "load_seconds": load_seconds, "encode_seconds": encode_seconds, "seconds": load_seconds + encode_seconds,
        "windows": len(flat_windows), "bytes_per_second": (len(embeddings) / encode_seconds) if encode_seconds else None,
        "device": device, "batch_size": int(batch_size), "prefix": prefix,
    }
    del model
    return embeddings, info


def _byte_aligned_scale(anchor_embeddings: np.ndarray, anchor_spans: np.ndarray, *, byte_length: int) -> np.ndarray:
    from malecns_wifi.text_axis_channels import interpolate_to_bytes, span_centres

    return interpolate_to_bytes(anchor_embeddings, span_centres(anchor_spans), byte_length=byte_length)


def write_model_table(spec: TokenCacheSpec, table: ByteTable, embeddings: np.ndarray, info: dict[str, Any], *, output_dir: Path) -> Path:
    n = len(table)
    dim = int(embeddings.shape[1])
    flat = pa.array(np.ascontiguousarray(embeddings, dtype=np.float32).reshape(-1), type=pa.float32())
    pa_table = pa.table({
        "id": pa.array(table.ids, type=pa.string()),
        "split": pa.array(table.splits, type=pa.string()),
        "split_index": pa.array(table.split_index, type=pa.int32()),
        "byte_index": pa.array(table.byte_index, type=pa.int32()),
        "text_sha256": pa.array(table.text_sha256, type=pa.string()),
        "embedding": pa.FixedSizeListArray.from_arrays(flat, dim),
        "fine_label": pa.array(table.fine_label, type=pa.int16()),
        "coarse_label": pa.array(table.coarse_label, type=pa.int16()),
        "dataset_path": pa.array([spec.dataset_path] * n, type=pa.string()),
        "dataset_revision": pa.array([spec.dataset_revision] * n, type=pa.string()),
        "hf_subset": pa.array([spec.config] * n, type=pa.string()),
        "model_name": pa.array([info["name"]] * n, type=pa.string()),
        "model_revision": pa.array([info.get("revision") or ""] * n, type=pa.string()),
        "chunking_version": pa.array([spec.chunking_version] * n, type=pa.string()),
    })
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{info['slug']}.parquet"
    pq.write_table(pa_table, path, compression="zstd")
    return path


def build_cache(
    spec: TokenCacheSpec, *, output_dir: Path, device: str = "cuda", batch_size: int = 64,
    loaded: dict[str, Any] | None = None, progress=None,
) -> dict[str, Any]:
    started = time.perf_counter()
    if loaded is None:
        loaded = load_fewnerd(spec)
    table = ByteTable.from_documents(spec, loaded["documents"])
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = _read_manifest(output_dir)
    if manifest is None:
        manifest = {
            "schema": SCHEMA,
            "task": "fine-grained NER (Few-NERD), byte-resolution",
            "dataset": {
                "path": spec.dataset_path, "revision": spec.dataset_revision, "config": spec.config,
                "splits": {s: len(loaded["documents"][s]) for s in spec.splits},
                "limit_per_split": spec.limit_per_split, "partial": spec.limit_per_split is not None,
            },
            "chunking": {"policy": CHUNKING_POLICY, "scales": list(spec.scales), "max_words": spec.max_tokens,
                        "version": spec.chunking_version},
            "labels": {"fine": loaded["fine_names"], "coarse": loaded["coarse_names"]},
            "sentences": len(table.sentence_texts), "bytes": len(table), "encoders": [],
        }
    for model_name in spec.models:
        embeddings, info = encode_model(model_name, table.sentence_texts, scales=spec.scales, device=device, batch_size=batch_size)
        if progress is not None:
            progress(model_name, len(embeddings), len(embeddings), started)
        path = write_model_table(spec, table, embeddings, info, output_dir=output_dir)
        info["file"] = path.name
        info["bytes_on_disk"] = int(path.stat().st_size)
        info["fingerprint"] = spec.model_fingerprint(model_name, info.get("revision"))
        manifest["encoders"] = [e for e in manifest["encoders"] if e["name"] != model_name] + [info]
        ordered = sorted(manifest["encoders"], key=lambda e: DEFAULT_MODELS.index(e["name"]) if e["name"] in DEFAULT_MODELS else 99)
        manifest["encoders"] = ordered
        manifest["encoder_order"] = [e["name"] for e in ordered]
        manifest["semantic_dim"] = int(sum(e["dim"] for e in ordered))
        manifest["fingerprint"] = (
            spec.fingerprint({e["name"]: e.get("revision") for e in ordered})
            if {e["name"] for e in ordered} == set(spec.models) else None
        )
        manifest["seconds"] = time.perf_counter() - started
        manifest["total_bytes_on_disk"] = int(sum(e["bytes_on_disk"] for e in ordered))
        _write_manifest(output_dir, manifest)
    return manifest


# -- loading -----------------------------------------------------------------

@dataclass
class TokenSemanticCache:
    manifest: dict[str, Any]
    doc_id: np.ndarray
    doc_split: np.ndarray
    doc_split_index: np.ndarray
    offsets: np.ndarray  # one entry per sentence, byte-row offsets
    fine_label: np.ndarray
    coarse_label: np.ndarray
    models: list[str]
    per_model: list[np.ndarray]

    @property
    def fused(self) -> np.ndarray:
        return np.concatenate(self.per_model, axis=1).astype(np.float32, copy=False)

    @property
    def sentences(self) -> int:
        return int(len(self.offsets) - 1)

    @property
    def label_names(self) -> dict[str, list[str]]:
        return self.manifest["labels"]


def resolve_cache_dir(location: str | Path) -> Path:
    text = str(location)
    if text.startswith("hf:"):
        from huggingface_hub import snapshot_download

        repo, _, revision = text[3:].partition("@")
        return Path(snapshot_download(repo_id=repo, repo_type="dataset", revision=revision or None))
    return Path(text)


def load_cache(
    location: str | Path, *, spec: TokenCacheSpec | None = None,
    models: tuple[str, ...] | None = None, splits: tuple[str, ...] | None = None,
) -> TokenSemanticCache:
    directory = resolve_cache_dir(location)
    manifest = _read_manifest(directory)
    if manifest is None:
        raise RuntimeError(f"no {SCHEMA} manifest in {directory}")
    if models is None:
        models = spec.models if spec is not None else tuple(
            manifest.get("encoder_order") or [e["name"] for e in manifest["encoders"]]
        )
    if splits is None:
        splits = spec.splits if spec is not None else tuple(manifest["dataset"]["splits"].keys())
    by_name = {e["name"]: e for e in manifest["encoders"]}
    missing = [m for m in models if m not in by_name]
    if missing:
        raise RuntimeError(f"byte cache lacks encoders {missing}")
    if spec is not None:
        for name in models:
            expected = spec.model_fingerprint(name, by_name[name].get("revision"))
            if by_name[name].get("fingerprint") != expected:
                raise RuntimeError(f"byte cache fingerprint mismatch for {name}: dataset/chunking/encoder differs")

    tables = {name: pq.read_table(directory / by_name[name]["file"]) for name in models}
    reference_keys = None
    per_model = []
    order = None
    first_table = None
    for name in models:
        table = tables[name]
        split_col = np.asarray(table.column("split").to_pylist())
        keep = np.isin(split_col, list(splits))
        table = table.filter(pa.array(keep))
        split_col = split_col[keep]
        split_rank = np.asarray([splits.index(s) for s in split_col], dtype=np.int64)
        split_index = np.asarray(table.column("split_index").to_numpy(), dtype=np.int64)
        byte_index = np.asarray(table.column("byte_index").to_numpy(), dtype=np.int64)
        local_order = np.lexsort((byte_index, split_index, split_rank))
        keys = list(zip(
            np.asarray(table.column("id").to_pylist())[local_order].tolist(),
            split_col[local_order].tolist(), byte_index[local_order].tolist(),
        ))
        if reference_keys is None:
            reference_keys, order, first_table = keys, local_order, table
        elif keys != reference_keys:
            raise RuntimeError(f"encoder table {name} does not join with {models[0]}: rows differ")
        embedding = table.column("embedding").combine_chunks()
        values = np.asarray(embedding.values.to_numpy(), dtype=np.float32).reshape(len(table), -1)
        per_model.append(np.ascontiguousarray(values[local_order]))

    byte_index = np.asarray(first_table.column("byte_index").to_numpy(), dtype=np.int64)[order]
    sentence_starts = np.flatnonzero(byte_index == 0)
    offsets = np.concatenate([sentence_starts, [len(byte_index)]]).astype(np.int64)
    ids = np.asarray(first_table.column("id").to_pylist())[order][sentence_starts]
    split_arr = np.asarray(first_table.column("split").to_pylist())[order][sentence_starts]
    split_index = np.asarray(first_table.column("split_index").to_numpy(), dtype=np.int64)[order][sentence_starts]
    fine_label = np.asarray(first_table.column("fine_label").to_numpy(), dtype=np.int64)[order]
    coarse_label = np.asarray(first_table.column("coarse_label").to_numpy(), dtype=np.int64)[order]
    return TokenSemanticCache(
        manifest=manifest, doc_id=np.asarray(ids, dtype="U64"), doc_split=np.asarray(split_arr, dtype="U16"),
        doc_split_index=split_index, offsets=offsets, fine_label=fine_label, coarse_label=coarse_label,
        models=list(models), per_model=per_model,
    )


def dataset_card(manifest: dict[str, Any]) -> str:
    dataset = manifest["dataset"]
    encoders = "\n".join(
        f"| `{e['name']}` | `{e.get('revision')}` | {e['dim']} (base {e['base_dim']} x {len(e['scales'])} scales) | `{e['file']}` |"
        for e in manifest["encoders"]
    )
    splits = ", ".join(f"{k}: {v}" for k, v in dataset["splits"].items())
    return f"""---
license: cc-by-sa-4.0
task_categories:
- token-classification
language:
- en
pretty_name: Few-NERD frozen byte-synchronised semantic cache (MiniLM + E5)
tags:
- few-nerd
- ner
- embeddings
- malecns
---

# Few-NERD ({dataset['config']}) — frozen byte-synchronised multiscale semantic cache

Precomputed, byte-resolution semantic channels of the official
`{dataset['path']}` dataset (`{dataset['config']}` config), built with this
research programme's established multiscale byte-axis convention
(`text_axis_channels.py`): for each scale, overlapping character windows are
pooled by a frozen encoder and linearly interpolated to every UTF-8 byte
position of the (word-joined) sentence text. No benchmark labels are used to
produce these embeddings; `fine_label`/`coarse_label` carry the official
Few-NERD word labels broadcast onto their byte spans, for convenience only.

* source dataset: `{dataset['path']}` revision `{dataset['revision']}`, config `{dataset['config']}`
* splits: {splits}{' (deterministic prefix, partial)' if dataset.get('partial') else ''}
* sentences: {manifest['sentences']}, bytes: {manifest['bytes']}
* chunking: `{manifest['chunking']['version']}` — scales {manifest['chunking']['scales']} chars, word cap {manifest['chunking']['max_words']}
* combined fingerprint: `{manifest.get('fingerprint')}`

| encoder | revision | dim | file |
|---|---|---|---|
{encoders}

Each parquet row is one byte of the reconstructed sentence text: `id`, `split`,
`split_index`, `byte_index`, `text_sha256` (hash of the original word list),
`embedding` (float32 list, concatenated unit-normalised per-scale channels),
`fine_label`/`coarse_label` (Few-NERD's own IDs, broadcast per word span),
plus provenance columns. Tables join on `(id, split, byte_index)`.

Generated by `experiments/malecns_wifi/scripts/build_fewnerd_semantic_cache.py`
in `franklinbaldo/papers`.
"""


def push_to_hub(output_dir: Path, *, repo_id: str = DEFAULT_HUB_REPO, token: str | None = None, private: bool = False) -> str:
    from huggingface_hub import HfApi

    manifest = _read_manifest(output_dir)
    if manifest is None:
        raise RuntimeError(f"no manifest in {output_dir}")
    (output_dir / "README.md").write_text(dataset_card(manifest), encoding="utf-8")
    api = HfApi(token=token)
    api.create_repo(repo_id, repo_type="dataset", exist_ok=True, private=private)
    info = api.upload_folder(
        repo_id=repo_id, repo_type="dataset", folder_path=str(output_dir),
        allow_patterns=["*.parquet", MANIFEST_NAME, "README.md"],
        commit_message=f"byte channel cache {manifest.get('fingerprint') or 'partial'}",
    )
    return getattr(info, "oid", None) or str(info)
