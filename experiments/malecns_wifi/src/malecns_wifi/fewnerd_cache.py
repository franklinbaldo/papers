"""Stage A: Few-NERD tokens -> frozen MiniLM/E5 per-token embeddings as a dataset.

Same design as ``multieurlex_cache`` (one parquet per frozen encoder, joined by
row key, published as a versioned HF dataset), but the unit is a **token**, not
a document chunk: every pre-tokenized word gets its own row and its own
embedding, taken from the encoder's ``last_hidden_state`` (mean-pooled over the
word's subwords), not from the pooled sentence vector used for MultiEURLEX.

Deviation from the document pipeline, preregistered: E5's ``"query: "``/
``"passage: "`` prefix is a pooled-sentence-embedding convention and has no
well-defined per-token alignment, so it is **not** applied here -- both
encoders see the raw pre-tokenized words. This only changes what each frozen
encoder is asked to compute; it does not touch labels or splits.

Columns per row::

    id | config | split | split_index | token_index | token | text_sha256
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

from malecns_wifi.multieurlex_cache import (
    MANIFEST_NAME,
    _sha,
    model_slug,
)


def _read_manifest(output_dir: Path) -> dict[str, Any] | None:
    path = output_dir / MANIFEST_NAME
    if not path.exists():
        return None
    manifest = json.loads(path.read_text(encoding="utf-8"))
    return manifest if manifest.get("schema") == SCHEMA else None


def _write_manifest(output_dir: Path, manifest: dict[str, Any]) -> None:
    (output_dir / MANIFEST_NAME).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

SCHEMA = "papers/malecns-fewnerd-token-cache-v1"
CHUNKING_POLICY = "word-pooled-subwords-v1"
DATASET_PATH = "DFKI-SLT/few-nerd"
DATASET_REVISION = "205f3e9c9f3577ea2561d43f2f62dc249ab92d5b"
DEFAULT_MODELS = (
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    "intfloat/multilingual-e5-small",
)
DEFAULT_SPLITS = ("train", "validation", "test")
DEFAULT_CONFIG = "supervised"
DEFAULT_HUB_REPO = "franklinbaldo/fewnerd-semantic-cache"


def sentence_key(tokens: list[str]) -> str:
    return hashlib.sha256(" ".join(tokens).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class TokenCacheSpec:
    config: str = DEFAULT_CONFIG
    models: tuple[str, ...] = DEFAULT_MODELS
    splits: tuple[str, ...] = DEFAULT_SPLITS
    limit_per_split: int | None = None
    max_tokens: int = 256
    dataset_path: str = DATASET_PATH
    dataset_revision: str = DATASET_REVISION

    @property
    def chunking_version(self) -> str:
        return f"{CHUNKING_POLICY}:max_tokens={self.max_tokens}"

    def data_payload(self) -> dict[str, Any]:
        return {
            "dataset": {
                "path": self.dataset_path,
                "revision": self.dataset_revision,
                "config": self.config,
                "splits": list(self.splits),
                "limit_per_split": self.limit_per_split,
            },
            "chunking": self.chunking_version,
            "normalize": "unit-per-model-then-concat",
        }

    def model_fingerprint(self, model_name: str, model_revision: str | None) -> str:
        payload = {"schema": SCHEMA, **self.data_payload(),
                   "encoder": {"name": model_name, "revision": model_revision, "prefix": ""}}
        return _sha(payload)

    def fingerprint(self, model_revisions: dict[str, str | None]) -> str:
        payload = {"schema": SCHEMA, **self.data_payload(),
                   "encoders": [{"name": n, "revision": model_revisions.get(n), "prefix": ""} for n in self.models]}
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


def word_pool_hidden_states(hidden_states: np.ndarray, word_ids: list[int | None], num_words: int) -> np.ndarray:
    from malecns_wifi.token_reservoir import word_pool_hidden_states as _pool

    return _pool(hidden_states, word_ids, num_words)


def _model_revision(model) -> str | None:
    try:
        return getattr(model.config, "_commit_hash", None)
    except Exception:  # pragma: no cover
        return None


@dataclass
class TokenTable:
    ids: list[str] = field(default_factory=list)
    splits: list[str] = field(default_factory=list)
    split_index: list[int] = field(default_factory=list)
    token_index: list[int] = field(default_factory=list)
    tokens: list[str] = field(default_factory=list)
    text_sha256: list[str] = field(default_factory=list)
    fine_label: list[int] = field(default_factory=list)
    coarse_label: list[int] = field(default_factory=list)
    sentence_tokens: list[list[str]] = field(default_factory=list)  # parallel to unique sentences, for encoding

    @classmethod
    def from_documents(cls, spec: TokenCacheSpec, documents: dict[str, list[dict[str, Any]]]) -> "TokenTable":
        table = cls()
        for split in spec.splits:
            for index, doc in enumerate(documents[split]):
                words = doc["tokens"][: spec.max_tokens]
                key = sentence_key(words)
                for token_i, (word, fine, coarse) in enumerate(
                    zip(words, doc["fine"][: spec.max_tokens], doc["coarse"][: spec.max_tokens])
                ):
                    table.ids.append(doc["id"])
                    table.splits.append(split)
                    table.split_index.append(index)
                    table.token_index.append(token_i)
                    table.tokens.append(word)
                    table.text_sha256.append(key)
                    table.fine_label.append(int(fine))
                    table.coarse_label.append(int(coarse))
                table.sentence_tokens.append(words)
        return table

    def __len__(self) -> int:
        return len(self.ids)


def encode_model(model_name: str, sentences: list[list[str]], *, device: str, batch_size: int, max_tokens: int):
    import torch
    from transformers import AutoModel, AutoTokenizer

    t0 = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name).to(device).eval()
    load_seconds = time.perf_counter() - t0
    dim = model.config.hidden_size

    t1 = time.perf_counter()
    rows: list[np.ndarray] = []
    with torch.no_grad():
        for start in range(0, len(sentences), batch_size):
            batch = sentences[start:start + batch_size]
            encoding = tokenizer(
                batch, is_split_into_words=True, return_tensors="pt",
                truncation=True, max_length=max_tokens + 8, padding=True,
            ).to(device)
            hidden = model(**encoding).last_hidden_state.cpu().numpy().astype(np.float32)
            for row in range(len(batch)):
                word_ids = encoding.word_ids(batch_index=row)
                pooled = word_pool_hidden_states(hidden[row], word_ids, len(batch[row]))
                norm = np.maximum(np.linalg.norm(pooled, axis=1, keepdims=True), 1e-12)
                rows.append((pooled / norm).astype(np.float32))
    encode_seconds = time.perf_counter() - t1
    embeddings = np.concatenate(rows, axis=0) if rows else np.zeros((0, dim), dtype=np.float32)
    info = {
        "name": model_name, "slug": model_slug(model_name), "revision": _model_revision(model),
        "dim": int(dim), "load_seconds": load_seconds, "encode_seconds": encode_seconds,
        "seconds": load_seconds + encode_seconds,
        "tokens_per_second": (len(embeddings) / encode_seconds) if encode_seconds else None,
        "device": device, "batch_size": int(batch_size), "prefix": "",
    }
    del model
    return embeddings, info


def write_model_table(spec: TokenCacheSpec, tokens: TokenTable, embeddings: np.ndarray, info: dict[str, Any], *, output_dir: Path) -> Path:
    n = len(tokens)
    dim = int(embeddings.shape[1])
    flat = pa.array(np.ascontiguousarray(embeddings, dtype=np.float32).reshape(-1), type=pa.float32())
    table = pa.table({
        "id": pa.array(tokens.ids, type=pa.string()),
        "split": pa.array(tokens.splits, type=pa.string()),
        "split_index": pa.array(tokens.split_index, type=pa.int32()),
        "token_index": pa.array(tokens.token_index, type=pa.int16()),
        "token": pa.array(tokens.tokens, type=pa.string()),
        "text_sha256": pa.array(tokens.text_sha256, type=pa.string()),
        "embedding": pa.FixedSizeListArray.from_arrays(flat, dim),
        "fine_label": pa.array(tokens.fine_label, type=pa.int16()),
        "coarse_label": pa.array(tokens.coarse_label, type=pa.int16()),
        "dataset_path": pa.array([spec.dataset_path] * n, type=pa.string()),
        "dataset_revision": pa.array([spec.dataset_revision] * n, type=pa.string()),
        "hf_subset": pa.array([spec.config] * n, type=pa.string()),
        "model_name": pa.array([info["name"]] * n, type=pa.string()),
        "model_revision": pa.array([info.get("revision") or ""] * n, type=pa.string()),
        "chunking_version": pa.array([spec.chunking_version] * n, type=pa.string()),
    })
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{info['slug']}.parquet"
    pq.write_table(table, path, compression="zstd")
    return path


def build_cache(spec: TokenCacheSpec, *, output_dir: Path, device: str = "cuda", batch_size: int = 64,
                 loaded: dict[str, Any] | None = None, progress=None) -> dict[str, Any]:
    started = time.perf_counter()
    if loaded is None:
        loaded = load_fewnerd(spec)
    tokens = TokenTable.from_documents(spec, loaded["documents"])
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = _read_manifest(output_dir)
    if manifest is None or manifest.get("schema") != SCHEMA:
        manifest = {
            "schema": SCHEMA,
            "task": "fine-grained NER (Few-NERD)",
            "dataset": {
                "path": spec.dataset_path, "revision": spec.dataset_revision, "config": spec.config,
                "splits": {s: len(loaded["documents"][s]) for s in spec.splits},
                "limit_per_split": spec.limit_per_split, "partial": spec.limit_per_split is not None,
            },
            "chunking": {"policy": CHUNKING_POLICY, "max_tokens": spec.max_tokens, "version": spec.chunking_version},
            "labels": {"fine": loaded["fine_names"], "coarse": loaded["coarse_names"]},
            "sentences": len(tokens.sentence_tokens), "tokens": len(tokens), "encoders": [],
        }
    for model_name in spec.models:
        embeddings, info = encode_model(model_name, tokens.sentence_tokens, device=device, batch_size=batch_size,
                                         max_tokens=spec.max_tokens)
        if progress is not None:
            progress(model_name, len(embeddings), len(embeddings), started)
        path = write_model_table(spec, tokens, embeddings, info, output_dir=output_dir)
        info["file"] = path.name
        info["bytes"] = int(path.stat().st_size)
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
        manifest["bytes"] = int(sum(e["bytes"] for e in ordered))
        _write_manifest(output_dir, manifest)
    return manifest


# -- loading -----------------------------------------------------------------

@dataclass
class TokenSemanticCache:
    manifest: dict[str, Any]
    doc_id: np.ndarray
    doc_split: np.ndarray
    doc_split_index: np.ndarray
    offsets: np.ndarray  # one entry per sentence, token rows offset
    fine_label: np.ndarray
    coarse_label: np.ndarray
    tokens: np.ndarray
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
    if manifest is None or manifest.get("schema") != SCHEMA:
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
        raise RuntimeError(f"token cache lacks encoders {missing}")
    if spec is not None:
        for name in models:
            expected = spec.model_fingerprint(name, by_name[name].get("revision"))
            if by_name[name].get("fingerprint") != expected:
                raise RuntimeError(f"token cache fingerprint mismatch for {name}: dataset/chunking/encoder differs")

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
        token_index = np.asarray(table.column("token_index").to_numpy(), dtype=np.int64)
        local_order = np.lexsort((token_index, split_index, split_rank))
        keys = list(zip(
            np.asarray(table.column("id").to_pylist())[local_order].tolist(),
            split_col[local_order].tolist(), token_index[local_order].tolist(),
        ))
        if reference_keys is None:
            reference_keys, order, first_table = keys, local_order, table
        elif keys != reference_keys:
            raise RuntimeError(f"encoder table {name} does not join with {models[0]}: rows differ")
        embedding = table.column("embedding").combine_chunks()
        values = np.asarray(embedding.values.to_numpy(), dtype=np.float32).reshape(len(table), -1)
        per_model.append(np.ascontiguousarray(values[local_order]))

    token_index = np.asarray(first_table.column("token_index").to_numpy(), dtype=np.int64)[order]
    sentence_starts = np.flatnonzero(token_index == 0)
    offsets = np.concatenate([sentence_starts, [len(token_index)]]).astype(np.int64)
    ids = np.asarray(first_table.column("id").to_pylist())[order][sentence_starts]
    split_arr = np.asarray(first_table.column("split").to_pylist())[order][sentence_starts]
    split_index = np.asarray(first_table.column("split_index").to_numpy(), dtype=np.int64)[order][sentence_starts]
    fine_label = np.asarray(first_table.column("fine_label").to_numpy(), dtype=np.int64)[order]
    coarse_label = np.asarray(first_table.column("coarse_label").to_numpy(), dtype=np.int64)[order]
    tokens = np.asarray(first_table.column("token").to_pylist())[order]
    return TokenSemanticCache(
        manifest=manifest, doc_id=np.asarray(ids, dtype="U64"), doc_split=np.asarray(split_arr, dtype="U16"),
        doc_split_index=split_index, offsets=offsets, fine_label=fine_label, coarse_label=coarse_label,
        tokens=tokens, models=list(models), per_model=per_model,
    )


def dataset_card(manifest: dict[str, Any]) -> str:
    dataset = manifest["dataset"]
    encoders = "\n".join(
        f"| `{e['name']}` | `{e.get('revision')}` | {e['dim']} | `{e['file']}` |" for e in manifest["encoders"]
    )
    splits = ", ".join(f"{k}: {v}" for k, v in dataset["splits"].items())
    return f"""---
license: cc-by-sa-4.0
task_categories:
- token-classification
language:
- en
pretty_name: Few-NERD frozen token-level semantic cache (MiniLM + E5)
tags:
- few-nerd
- ner
- embeddings
- malecns
---

# Few-NERD ({dataset['config']}) — frozen per-token semantic embeddings

Precomputed, unit-normalised, word-pooled hidden-state embeddings of the
official `{dataset['path']}` dataset (`{dataset['config']}` config), produced
once so downstream experiments (frozen MaleCNS positional reservoir, linear
probes, ablations) never pay the encoders again. No benchmark labels are used
to produce these embeddings; `fine_label`/`coarse_label` columns carry the
official Few-NERD labels for convenience, not as encoder input.

* source dataset: `{dataset['path']}` revision `{dataset['revision']}`, config `{dataset['config']}`
* splits: {splits}{' (deterministic prefix, partial)' if dataset.get('partial') else ''}
* sentences: {manifest['sentences']}, tokens: {manifest['tokens']}
* chunking: `{manifest['chunking']['version']}` — one row per pre-tokenized word, embedding
  mean-pooled over its subwords from the encoder's `last_hidden_state` (not the pooled
  sentence embedding; E5's `"query: "`/`"passage: "` prefix is not applied)
* combined fingerprint: `{manifest.get('fingerprint')}`

| encoder | revision | dim | file |
|---|---|---|---|
{encoders}

Each parquet row is one token: `id`, `split`, `split_index`, `token_index`,
`token`, `text_sha256` (sentence hash), `embedding` (float32 list),
`fine_label`/`coarse_label` (Few-NERD's own IDs), plus provenance columns.
Tables join on `(id, split, token_index)`.

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
        commit_message=f"token cache {manifest.get('fingerprint') or 'partial'}",
    )
    return getattr(info, "oid", None) or str(info)
