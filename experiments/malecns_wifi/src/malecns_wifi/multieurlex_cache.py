"""Stage A: MultiEURLEX documents -> frozen MiniLM/E5 chunk embeddings as a dataset.

The cache is a first-class, versioned scientific artifact rather than a
throwaway file: one parquet table per frozen encoder, each row one (document,
chunk) with full provenance, joinable by ``(id, split, chunk_index)``. Encoders
can therefore be computed independently, in parallel, on different machines,
and merged afterwards. The intended home is the Hugging Face dataset
``franklinbaldo/multieurlex21-pt-semantic-cache``.

Columns per row::

    id | split | split_index | chunk_index | chunk_count | chunk_chars
    | text_sha256 | embedding (list<float32>) | dataset_path | dataset_revision
    | hf_subset | model_name | model_revision | prefix | chunking_version

Every later stage (MaleCNS reservoir, label-free controls, MTEB evaluator)
looks documents up by ``text_sha256`` so nothing has to re-run the encoders.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from malecns_wifi.document_reservoir import sample_windows, unit_rows

SCHEMA = "papers/malecns-multieurlex-semantic-cache-v2"
CHUNKING_POLICY = "linspace-windows-v1"
TASK_NAME = "MultiEURLEXMultilabelClassification"
HF_SUBSET = "pt"
DATASET_PATH = "mteb/eurlex-multilingual"
DATASET_REVISION = "2aea5a6dc8fdcfeca41d0fb963c0a338930bde5c"
DEFAULT_MODELS = (
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    "intfloat/multilingual-e5-small",
)
DEFAULT_SPLITS = ("train", "validation", "test")
DEFAULT_HUB_REPO = "franklinbaldo/multieurlex21-pt-semantic-cache"
MANIFEST_NAME = "manifest.json"


def text_key(text: str) -> str:
    return hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()


def model_prefix(model_name: str) -> str:
    return "passage: " if "e5" in model_name.lower() else ""


def model_slug(model_name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", model_name.split("/")[-1].lower()).strip("-")


def chunking_version(max_chunks: int, chunk_chars: int) -> str:
    return f"{CHUNKING_POLICY}:max_chunks={int(max_chunks)}:chunk_chars={int(chunk_chars)}"


@dataclass(frozen=True)
class CacheSpec:
    models: tuple[str, ...] = DEFAULT_MODELS
    max_chunks: int = 4
    chunk_chars: int = 3000
    splits: tuple[str, ...] = DEFAULT_SPLITS
    limit_per_split: int | None = None
    dataset_path: str = DATASET_PATH
    dataset_revision: str = DATASET_REVISION
    hf_subset: str = HF_SUBSET

    @property
    def chunking_version(self) -> str:
        return chunking_version(self.max_chunks, self.chunk_chars)

    def data_payload(self) -> dict[str, Any]:
        return {
            "dataset": {
                "path": self.dataset_path,
                "revision": self.dataset_revision,
                "subset": self.hf_subset,
                "splits": list(self.splits),
                "limit_per_split": self.limit_per_split,
            },
            "chunking": self.chunking_version,
            "normalize": "unit-per-model-then-concat",
        }

    def model_fingerprint(self, model_name: str, model_revision: str | None) -> str:
        payload = {
            "schema": SCHEMA,
            **self.data_payload(),
            "encoder": {"name": model_name, "revision": model_revision, "prefix": model_prefix(model_name)},
        }
        return _sha(payload)

    def fingerprint(self, model_revisions: dict[str, str | None]) -> str:
        payload = {
            "schema": SCHEMA,
            **self.data_payload(),
            "encoders": [
                {"name": name, "revision": model_revisions.get(name), "prefix": model_prefix(name)}
                for name in self.models
            ],
        }
        return _sha(payload)


def _sha(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load_task_documents(spec: CacheSpec) -> dict[str, list[dict[str, Any]]]:
    """Official MTEB task data, untouched, optionally capped by a deterministic prefix."""
    import mteb

    task = mteb.get_task(TASK_NAME, hf_subsets=[spec.hf_subset], eval_splits=["test"])
    revision = task.metadata.dataset.get("revision") if isinstance(task.metadata.dataset, dict) else None
    if revision != spec.dataset_revision:
        raise RuntimeError(f"unexpected MultiEURLEX MTEB revision: {revision}; expected {spec.dataset_revision}")
    task.load_data()
    subset = task.dataset[spec.hf_subset]
    documents: dict[str, list[dict[str, Any]]] = {}
    for split in spec.splits:
        rows = subset[split]
        if spec.limit_per_split is not None:
            rows = rows.select(range(min(spec.limit_per_split, len(rows))))
        documents[split] = [{"id": str(i), "text": str(t)} for i, t in zip(rows["id"], rows["text"])]
    return documents


def _model_revision(model) -> str | None:
    try:
        return getattr(model[0].auto_model.config, "_commit_hash", None)
    except Exception:  # pragma: no cover - defensive
        return None


@dataclass
class ChunkTable:
    """Chunk rows (without embeddings) shared by every encoder table."""

    ids: list[str] = field(default_factory=list)
    splits: list[str] = field(default_factory=list)
    split_index: list[int] = field(default_factory=list)
    chunk_index: list[int] = field(default_factory=list)
    chunk_count: list[int] = field(default_factory=list)
    chunk_chars: list[int] = field(default_factory=list)
    text_sha256: list[str] = field(default_factory=list)
    windows: list[str] = field(default_factory=list)

    @classmethod
    def from_documents(cls, spec: CacheSpec, documents: dict[str, list[dict[str, Any]]]) -> "ChunkTable":
        table = cls()
        for split in spec.splits:
            for index, doc in enumerate(documents[split]):
                windows = sample_windows(doc["text"], max_chunks=spec.max_chunks, chunk_chars=spec.chunk_chars)
                key = text_key(doc["text"])
                for chunk_i, window in enumerate(windows):
                    table.ids.append(doc["id"])
                    table.splits.append(split)
                    table.split_index.append(index)
                    table.chunk_index.append(chunk_i)
                    table.chunk_count.append(len(windows))
                    table.chunk_chars.append(len(window))
                    table.text_sha256.append(key)
                    table.windows.append(window)
        return table

    def __len__(self) -> int:
        return len(self.ids)


def encode_model(
    model_name: str,
    windows: list[str],
    *,
    device: str,
    batch_size: int,
    slice_size: int = 2048,
    progress=None,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Encode windows in slices so progress can be reported while running.

    Slicing only changes which windows share a padded batch, never a window's
    own embedding (attention is masked), so it is telemetry, not representation.
    """
    from sentence_transformers import SentenceTransformer

    t0 = time.perf_counter()
    model = SentenceTransformer(model_name, device=device)
    load_seconds = time.perf_counter() - t0
    prefix = model_prefix(model_name)
    t1 = time.perf_counter()
    parts = []
    for start in range(0, len(windows), max(1, slice_size)):
        local = windows[start:start + slice_size]
        parts.append(model.encode(
            [prefix + w for w in local],
            batch_size=batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        ))
        if progress is not None:
            progress(model_name, min(start + len(local), len(windows)), len(windows), t1)
    encode_seconds = time.perf_counter() - t1
    values = np.concatenate(parts, axis=0) if parts else np.zeros((0, 1), dtype=np.float32)
    embeddings = unit_rows(np.asarray(values, dtype=np.float32))
    info = {
        "name": model_name,
        "slug": model_slug(model_name),
        "revision": _model_revision(model),
        "dim": int(embeddings.shape[1]),
        "max_seq_length": int(getattr(model, "max_seq_length", 0) or 0),
        "prefix": prefix,
        "load_seconds": load_seconds,
        "encode_seconds": encode_seconds,
        "seconds": load_seconds + encode_seconds,
        "chunks_per_second": (len(windows) / encode_seconds) if encode_seconds else None,
        "device": device,
        "batch_size": int(batch_size),
    }
    del model
    return embeddings, info


def write_model_table(
    spec: CacheSpec,
    chunks: ChunkTable,
    embeddings: np.ndarray,
    info: dict[str, Any],
    *,
    output_dir: Path,
) -> Path:
    n = len(chunks)
    dim = int(embeddings.shape[1])
    flat = pa.array(np.ascontiguousarray(embeddings, dtype=np.float32).reshape(-1), type=pa.float32())
    table = pa.table({
        "id": pa.array(chunks.ids, type=pa.string()),
        "split": pa.array(chunks.splits, type=pa.string()),
        "split_index": pa.array(chunks.split_index, type=pa.int32()),
        "chunk_index": pa.array(chunks.chunk_index, type=pa.int16()),
        "chunk_count": pa.array(chunks.chunk_count, type=pa.int16()),
        "chunk_chars": pa.array(chunks.chunk_chars, type=pa.int32()),
        "text_sha256": pa.array(chunks.text_sha256, type=pa.string()),
        "embedding": pa.FixedSizeListArray.from_arrays(flat, dim),
        "dataset_path": pa.array([spec.dataset_path] * n, type=pa.string()),
        "dataset_revision": pa.array([spec.dataset_revision] * n, type=pa.string()),
        "hf_subset": pa.array([spec.hf_subset] * n, type=pa.string()),
        "model_name": pa.array([info["name"]] * n, type=pa.string()),
        "model_revision": pa.array([info.get("revision") or ""] * n, type=pa.string()),
        "prefix": pa.array([info["prefix"]] * n, type=pa.string()),
        "chunking_version": pa.array([spec.chunking_version] * n, type=pa.string()),
    })
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{info['slug']}.parquet"
    pq.write_table(table, path, compression="zstd")
    return path


def build_cache(
    spec: CacheSpec,
    *,
    output_dir: Path,
    device: str = "cuda",
    batch_size: int = 64,
    documents: dict[str, list[dict[str, Any]]] | None = None,
    progress=None,
) -> dict[str, Any]:
    """Encode every requested model into ``output_dir`` and update its manifest."""
    started = time.perf_counter()
    if documents is None:
        documents = load_task_documents(spec)
    chunks = ChunkTable.from_documents(spec, documents)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = _read_manifest(output_dir) or _new_manifest(spec, documents, chunks)
    for model_name in spec.models:
        embeddings, info = encode_model(
            model_name, chunks.windows, device=device, batch_size=batch_size, progress=progress
        )
        path = write_model_table(spec, chunks, embeddings, info, output_dir=output_dir)
        info["file"] = path.name
        info["bytes"] = int(path.stat().st_size)
        info["fingerprint"] = spec.model_fingerprint(model_name, info.get("revision"))
        manifest["encoders"] = [e for e in manifest["encoders"] if e["name"] != model_name] + [info]
        _finalise_manifest(manifest, spec, started)
        _write_manifest(output_dir, manifest)
    return manifest


def _new_manifest(spec: CacheSpec, documents, chunks: ChunkTable) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "task": TASK_NAME,
        "dataset": {
            "path": spec.dataset_path,
            "revision": spec.dataset_revision,
            "subset": spec.hf_subset,
            "splits": {split: len(documents[split]) for split in spec.splits},
            "limit_per_split": spec.limit_per_split,
            "partial": spec.limit_per_split is not None,
        },
        "chunking": {
            "policy": CHUNKING_POLICY,
            "max_chunks": spec.max_chunks,
            "chunk_chars": spec.chunk_chars,
            "version": spec.chunking_version,
        },
        "documents": len(set(zip(chunks.splits, chunks.split_index))),
        "chunks": len(chunks),
        "encoders": [],
    }


def canonical_model_order(names) -> list[str]:
    """Fusion order is part of the representation: DEFAULT_MODELS first (MiniLM
    then E5, as in the first official run), any extra encoder alphabetically."""
    names = list(names)
    known = [m for m in DEFAULT_MODELS if m in names]
    return known + sorted(n for n in names if n not in DEFAULT_MODELS)


def _finalise_manifest(manifest: dict[str, Any], spec: CacheSpec, started: float) -> None:
    by_name = {e["name"]: e for e in manifest["encoders"]}
    ordered = [by_name[n] for n in canonical_model_order(by_name)]
    manifest["encoders"] = ordered
    manifest["encoder_order"] = [e["name"] for e in ordered]
    manifest["semantic_dim"] = int(sum(e["dim"] for e in ordered))
    manifest["fingerprint"] = spec.fingerprint({e["name"]: e.get("revision") for e in ordered}) if set(
        e["name"] for e in ordered
    ) == set(spec.models) else None
    manifest["seconds"] = time.perf_counter() - started
    manifest["bytes"] = int(sum(e["bytes"] for e in ordered))


def _read_manifest(output_dir: Path) -> dict[str, Any] | None:
    path = output_dir / MANIFEST_NAME
    if not path.exists():
        return None
    manifest = json.loads(path.read_text(encoding="utf-8"))
    return manifest if manifest.get("schema") == SCHEMA else None


def _write_manifest(output_dir: Path, manifest: dict[str, Any]) -> None:
    (output_dir / MANIFEST_NAME).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# -- loading ---------------------------------------------------------------

@dataclass
class SemanticCache:
    manifest: dict[str, Any]
    doc_id: np.ndarray
    doc_key: np.ndarray
    doc_split: np.ndarray
    doc_split_index: np.ndarray
    offsets: np.ndarray
    models: list[str]
    per_model: list[np.ndarray]

    @property
    def fused(self) -> np.ndarray:
        return np.concatenate(self.per_model, axis=1).astype(np.float32, copy=False)

    @property
    def documents(self) -> int:
        return int(len(self.offsets) - 1)

    @property
    def chunks(self) -> int:
        return int(self.offsets[-1])

    def index_by_key(self) -> dict[str, int]:
        return {str(key): i for i, key in enumerate(self.doc_key.tolist())}


def resolve_cache_dir(location: str | Path) -> Path:
    """A local directory, or ``hf:<repo_id>[@revision]`` fetched from the Hub."""
    text = str(location)
    if text.startswith("hf:"):
        from huggingface_hub import snapshot_download

        repo, _, revision = text[3:].partition("@")
        return Path(snapshot_download(repo_id=repo, repo_type="dataset", revision=revision or None))
    return Path(text)


def load_cache(
    location: str | Path,
    *,
    spec: CacheSpec | None = None,
    models: tuple[str, ...] | None = None,
    splits: tuple[str, ...] | None = None,
) -> SemanticCache:
    """Join the per-encoder parquet tables into per-document chunk arrays.

    Documents are ordered by ``splits`` then ``split_index``; encoder columns are
    ordered as ``models`` (default: the spec's / manifest's order). Every table
    must cover exactly the same ``(id, split, chunk_index)`` rows with the same
    dataset revision and chunking version, otherwise the join is refused.
    """
    directory = resolve_cache_dir(location)
    manifest = _read_manifest(directory)
    if manifest is None:
        raise RuntimeError(f"no {SCHEMA} manifest in {directory}")
    if models is None:
        models = spec.models if spec is not None else tuple(manifest.get("encoder_order") or canonical_model_order(
            e["name"] for e in manifest["encoders"]
        ))
    if splits is None:
        splits = spec.splits if spec is not None else tuple(manifest["dataset"]["splits"].keys())
    by_name = {e["name"]: e for e in manifest["encoders"]}
    missing = [m for m in models if m not in by_name]
    if missing:
        raise RuntimeError(f"semantic cache lacks encoders {missing}")
    if spec is not None:
        for name in models:
            expected = spec.model_fingerprint(name, by_name[name].get("revision"))
            if by_name[name].get("fingerprint") != expected:
                raise RuntimeError(f"semantic cache fingerprint mismatch for {name}: dataset/chunking/encoder differs")

    tables = {name: pq.read_table(directory / by_name[name]["file"]) for name in models}
    reference_keys = None
    per_model = []
    order = None
    meta = None
    for name in models:
        table = tables[name]
        split_col = np.asarray(table.column("split").to_pylist())
        keep = np.isin(split_col, list(splits))
        table = table.filter(pa.array(keep))
        split_col = split_col[keep]
        split_rank = np.asarray([splits.index(s) for s in split_col], dtype=np.int64)
        split_index = np.asarray(table.column("split_index").to_numpy(), dtype=np.int64)
        chunk_index = np.asarray(table.column("chunk_index").to_numpy(), dtype=np.int64)
        local_order = np.lexsort((chunk_index, split_index, split_rank))
        keys = list(zip(
            np.asarray(table.column("id").to_pylist())[local_order].tolist(),
            split_col[local_order].tolist(),
            chunk_index[local_order].tolist(),
        ))
        provenance = {
            "dataset_revision": set(table.column("dataset_revision").to_pylist()),
            "chunking_version": set(table.column("chunking_version").to_pylist()),
        }
        if reference_keys is None:
            reference_keys, order, meta = keys, local_order, provenance
            first_table = table
        elif keys != reference_keys or provenance != meta:
            raise RuntimeError(f"encoder table {name} does not join with {models[0]}: rows or provenance differ")
        embedding = table.column("embedding").combine_chunks()
        values = np.asarray(embedding.values.to_numpy(), dtype=np.float32).reshape(len(table), -1)
        per_model.append(np.ascontiguousarray(values[local_order]))

    chunk_index = np.asarray(first_table.column("chunk_index").to_numpy(), dtype=np.int64)[order]
    doc_starts = np.flatnonzero(chunk_index == 0)
    offsets = np.concatenate([doc_starts, [len(chunk_index)]]).astype(np.int64)
    ids = np.asarray(first_table.column("id").to_pylist())[order][doc_starts]
    keys = np.asarray(first_table.column("text_sha256").to_pylist())[order][doc_starts]
    split_arr = np.asarray(first_table.column("split").to_pylist())[order][doc_starts]
    split_index = np.asarray(first_table.column("split_index").to_numpy(), dtype=np.int64)[order][doc_starts]
    return SemanticCache(
        manifest=manifest,
        doc_id=np.asarray(ids, dtype="U32"),
        doc_key=np.asarray(keys, dtype="U64"),
        doc_split=np.asarray(split_arr, dtype="U16"),
        doc_split_index=split_index,
        offsets=offsets,
        models=list(models),
        per_model=per_model,
    )


def spec_from_manifest(manifest: dict[str, Any]) -> CacheSpec:
    dataset = manifest["dataset"]
    return CacheSpec(
        models=tuple(e["name"] for e in manifest["encoders"]),
        max_chunks=int(manifest["chunking"]["max_chunks"]),
        chunk_chars=int(manifest["chunking"]["chunk_chars"]),
        splits=tuple(dataset["splits"].keys()),
        limit_per_split=dataset.get("limit_per_split"),
        dataset_path=dataset["path"],
        dataset_revision=dataset["revision"],
        hf_subset=dataset["subset"],
    )


# -- publishing ------------------------------------------------------------

def dataset_card(manifest: dict[str, Any]) -> str:
    dataset = manifest["dataset"]
    encoders = "\n".join(
        f"| `{e['name']}` | `{e.get('revision')}` | {e['dim']} | {e.get('max_seq_length')} | `{e['prefix'] or ''}` | `{e['file']}` |"
        for e in manifest["encoders"]
    )
    splits = ", ".join(f"{k}: {v}" for k, v in dataset["splits"].items())
    return f"""---
license: cc-by-4.0
task_categories:
- text-classification
language:
- pt
pretty_name: MultiEURLEX-21 PT frozen semantic cache (MiniLM + E5)
tags:
- mteb
- multieurlex
- embeddings
- malecns
---

# MultiEURLEX-21 PT — frozen semantic chunk embeddings

Precomputed, unit-normalised chunk embeddings of the official MTEB
`{manifest['task']}` Portuguese data, produced once so that
downstream experiments (frozen MaleCNS connectome reservoir, label-free
controls, ablations) never pay the sentence encoders again. No benchmark labels
are stored or used here.

* source dataset: `{dataset['path']}` revision `{dataset['revision']}`, subset `{dataset['subset']}`
* splits: {splits}{' (deterministic prefix, partial)' if dataset.get('partial') else ''}
* documents: {manifest['documents']}, chunks: {manifest['chunks']}
* chunking: `{manifest['chunking']['version']}` — up to {manifest['chunking']['max_chunks']} windows of
  {manifest['chunking']['chunk_chars']} characters sampled with `numpy.linspace` over the document
* combined fingerprint: `{manifest.get('fingerprint')}`

| encoder | revision | dim | max_seq_length | prefix | file |
|---|---|---|---|---|---|
{encoders}

Each parquet row is one (document, chunk): `id`, `split`, `split_index`,
`chunk_index`, `chunk_count`, `chunk_chars`, `text_sha256`, `embedding`
(float32 list), plus provenance columns (`dataset_path`, `dataset_revision`,
`hf_subset`, `model_name`, `model_revision`, `prefix`, `chunking_version`).
Tables join on `(id, split, chunk_index)`. Documents are looked up by
`text_sha256` of the original text.

Generated by `experiments/malecns_wifi/scripts/build_multieurlex_semantic_cache.py`
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
        repo_id=repo_id,
        repo_type="dataset",
        folder_path=str(output_dir),
        allow_patterns=["*.parquet", MANIFEST_NAME, "README.md"],
        commit_message=f"semantic cache {manifest.get('fingerprint') or 'partial'}",
    )
    return getattr(info, "oid", None) or str(info)
