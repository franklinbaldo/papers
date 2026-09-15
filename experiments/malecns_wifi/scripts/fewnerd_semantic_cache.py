"""Build a provenance-checked contextual token cache for Few-NERD.

The cache contains no NER labels. Frozen MiniLM/E5 hidden states are aligned to
Few-NERD's official tokens, mean-pooled over subwords, L2-normalised, and stored
once. Multiscale fields are derived later from the cached token vectors.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Sequence

import numpy as np

from fewnerd_ner_core import canonical_byte_axis

SCHEMA = "papers/malecns-fewnerd-contextual-token-cache-v1"
DEFAULT_MODELS = (
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    "intfloat/multilingual-e5-small",
)


def _unit_rows(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float32)
    norms = np.linalg.norm(values, axis=-1, keepdims=True)
    return values / np.maximum(norms, 1e-12)


def token_char_spans(tokens: Sequence[str], *, prefix_chars: int = 0) -> tuple[tuple[int, int], ...]:
    spans: list[tuple[int, int]] = []
    cursor = int(prefix_chars)
    for i, token in enumerate(tokens):
        if i:
            cursor += 1
        start = cursor
        cursor += len(str(token))
        spans.append((start, cursor))
    return tuple(spans)


def window_bounds(index: int, length: int, width: int) -> tuple[int, int]:
    if width < 1 or not 0 <= index < length:
        raise ValueError("invalid window request")
    left = (width - 1) // 2
    right = width - left - 1
    start = max(0, index - left)
    end = min(length, index + right + 1)
    # Near a boundary, expand on the opposite side to retain the requested width
    # whenever the sentence is long enough.
    target = min(width, length)
    if end - start < target:
        if start == 0:
            end = min(length, target)
        elif end == length:
            start = max(0, length - target)
    return start, end


def multiscale_token_fields(token_vectors: np.ndarray, scales: Sequence[int] = (1, 2, 4, 8)) -> dict[int, np.ndarray]:
    vectors = np.asarray(token_vectors, dtype=np.float32)
    if vectors.ndim != 2:
        raise ValueError("token_vectors must be [tokens, dim]")
    result: dict[int, np.ndarray] = {}
    for width in scales:
        rows = []
        for i in range(len(vectors)):
            start, end = window_bounds(i, len(vectors), int(width))
            rows.append(vectors[start:end].mean(axis=0))
        result[int(width)] = _unit_rows(np.stack(rows)) if rows else np.empty_like(vectors)
    return result


def _model_prefix(model_name: str) -> str:
    return "passage: " if "e5" in model_name.lower() else ""


def _encode_batch(model_name: str, texts: Sequence[str], token_lists: Sequence[Sequence[str]], *, device: str, batch_size: int) -> tuple[np.ndarray, dict]:
    import torch
    from transformers import AutoModel, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
    if not getattr(tokenizer, "is_fast", False):
        raise RuntimeError(f"fast tokenizer with offset mapping required: {model_name}")
    model = AutoModel.from_pretrained(model_name).to(device)
    model.eval()
    max_length = min(int(getattr(tokenizer, "model_max_length", 512)), 512)
    prefix = _model_prefix(model_name)

    per_sentence: list[np.ndarray | None] = [None] * len(texts)
    hidden_size = int(model.config.hidden_size)
    total_chunks = 0

    for batch_start in range(0, len(texts), batch_size):
        batch_texts = list(texts[batch_start : batch_start + batch_size])
        batch_tokens = list(token_lists[batch_start : batch_start + batch_size])
        encoded_texts = [prefix + text for text in batch_texts]
        encoded = tokenizer(
            encoded_texts,
            padding=True,
            truncation=True,
            max_length=max_length,
            stride=min(64, max_length // 4),
            return_overflowing_tokens=True,
            return_offsets_mapping=True,
            return_tensors="pt",
        )
        overflow = encoded.pop("overflow_to_sample_mapping")
        offsets = encoded.pop("offset_mapping")
        attention = encoded["attention_mask"]
        total_chunks += int(offsets.shape[0])
        with torch.inference_mode():
            outputs = model(**{k: v.to(device) for k, v in encoded.items()})
            hidden = outputs.last_hidden_state.detach().cpu().float()

        # Accumulate by original official token. Overlap chunks are deduplicated
        # by tokenizer character offsets so stride does not overweight tokens.
        sample_sums: dict[int, np.ndarray] = {}
        sample_counts: dict[int, np.ndarray] = {}
        sample_seen: dict[int, set[tuple[int, int]]] = {}
        for local_sample, tokens in enumerate(batch_tokens):
            sample_sums[local_sample] = np.zeros((len(tokens), hidden_size), dtype=np.float32)
            sample_counts[local_sample] = np.zeros(len(tokens), dtype=np.int32)
            sample_seen[local_sample] = set()

        prefix_chars = len(prefix)
        spans_by_sample = [token_char_spans(tokens, prefix_chars=prefix_chars) for tokens in batch_tokens]
        for chunk_i in range(hidden.shape[0]):
            local_sample = int(overflow[chunk_i])
            token_spans = spans_by_sample[local_sample]
            for sub_i in range(hidden.shape[1]):
                if not int(attention[chunk_i, sub_i]):
                    continue
                a, b = (int(x) for x in offsets[chunk_i, sub_i])
                if b <= a:
                    continue
                key = (a, b)
                if key in sample_seen[local_sample]:
                    continue
                sample_seen[local_sample].add(key)
                overlapping = [i for i, (s, e) in enumerate(token_spans) if max(a, s) < min(b, e)]
                if not overlapping:
                    continue
                vector = hidden[chunk_i, sub_i].numpy()
                for token_i in overlapping:
                    sample_sums[local_sample][token_i] += vector
                    sample_counts[local_sample][token_i] += 1

        for local_sample, tokens in enumerate(batch_tokens):
            counts = sample_counts[local_sample]
            missing = np.flatnonzero(counts == 0)
            if len(missing):
                raise RuntimeError(
                    f"{model_name}: {len(missing)} official tokens lacked subword coverage "
                    f"in batch sample {local_sample}; first missing={missing[:8].tolist()}"
                )
            pooled = sample_sums[local_sample] / counts[:, None]
            per_sentence[batch_start + local_sample] = _unit_rows(pooled)

    if any(value is None for value in per_sentence):
        raise RuntimeError(f"{model_name}: incomplete sentence cache")
    flat = np.concatenate([value for value in per_sentence if value is not None], axis=0)
    meta = {
        "name": model_name,
        "revision": getattr(model.config, "_commit_hash", None),
        "hidden_size": hidden_size,
        "prefix": prefix,
        "max_length": max_length,
        "overflow_chunks": total_chunks,
    }
    del model
    if device.startswith("cuda"):
        torch.cuda.empty_cache()
    return flat, meta


def build_cache(*, split: str, limit: int, output: Path, models: Sequence[str], device: str, batch_size: int, dtype: str) -> dict:
    from datasets import load_dataset

    started = time.perf_counter()
    ds = load_dataset("DFKI-SLT/few-nerd", "supervised", split=split)
    if limit:
        ds = ds.select(range(min(limit, len(ds))))

    ids: list[str] = []
    texts: list[str] = []
    token_lists: list[list[str]] = []
    token_offsets = [0]
    byte_starts: list[int] = []
    byte_ends: list[int] = []
    fingerprint_rows = []

    for row in ds:
        tokens = [str(x) for x in row["tokens"]]
        axis = canonical_byte_axis(tokens, [0] * len(tokens))
        row_id = str(row["id"])
        ids.append(row_id)
        texts.append(axis.text)
        token_lists.append(tokens)
        token_offsets.append(token_offsets[-1] + len(tokens))
        byte_starts.extend(start for start, _ in axis.token_byte_spans)
        byte_ends.extend(end for _, end in axis.token_byte_spans)
        fingerprint_rows.append({"id": row_id, "tokens": tokens})

    fingerprint_payload = {
        "schema": SCHEMA,
        "dataset": "DFKI-SLT/few-nerd",
        "config": "supervised",
        "split": split,
        "rows": fingerprint_rows,
        "models": list(models),
        "pooling": "mean overlapping subwords -> L2; multiscale local token mean -> L2",
        "scales": [1, 2, 4, 8],
    }
    fingerprint = hashlib.sha256(json.dumps(fingerprint_payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()

    target_dtype = np.float16 if dtype == "float16" else np.float32
    arrays: dict[str, np.ndarray] = {
        "sentence_ids": np.asarray(ids, dtype=str),
        "token_offsets": np.asarray(token_offsets, dtype=np.int64),
        "token_byte_start": np.asarray(byte_starts, dtype=np.int32),
        "token_byte_end": np.asarray(byte_ends, dtype=np.int32),
    }
    model_meta = []
    model_seconds = []
    for i, model_name in enumerate(models):
        t0 = time.perf_counter()
        flat, meta = _encode_batch(model_name, texts, token_lists, device=device, batch_size=batch_size)
        arrays[f"model_{i}_tokens"] = flat.astype(target_dtype)
        seconds = time.perf_counter() - t0
        meta["seconds"] = seconds
        model_meta.append(meta)
        model_seconds.append(seconds)

    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez(output, **arrays)
    manifest = {
        "schema": SCHEMA,
        "claim_status": "semantic cache infrastructure; contains no Few-NERD labels",
        "fingerprint": fingerprint,
        "dataset": "DFKI-SLT/few-nerd",
        "config": "supervised",
        "split": split,
        "sentences": len(ids),
        "tokens": token_offsets[-1],
        "models": model_meta,
        "dtype": dtype,
        "scales": [1, 2, 4, 8],
        "seconds": time.perf_counter() - started,
        "encoder_seconds": model_seconds,
        "npz": output.name,
    }
    manifest_path = output.with_suffix(".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    # Deterministic reload gate.
    with np.load(output, allow_pickle=False) as archive:
        if archive["token_offsets"].tolist() != token_offsets:
            raise RuntimeError("semantic cache reload token offsets mismatch")
        for i, meta in enumerate(model_meta):
            arr = archive[f"model_{i}_tokens"]
            if arr.shape != (token_offsets[-1], int(meta["hidden_size"])):
                raise RuntimeError(f"semantic cache reload shape mismatch for model {i}: {arr.shape}")
    manifest["bytes_on_disk"] = output.stat().st_size
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--split", default="train")
    p.add_argument("--limit", type=int, default=8)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--models", nargs="+", default=list(DEFAULT_MODELS))
    p.add_argument("--device", default="cuda")
    p.add_argument("--batch-size", type=int, default=8)
    p.add_argument("--dtype", choices=("float16", "float32"), default="float16")
    args = p.parse_args()
    manifest = build_cache(
        split=args.split,
        limit=args.limit,
        output=args.output,
        models=args.models,
        device=args.device,
        batch_size=args.batch_size,
        dtype=args.dtype,
    )
    print(json.dumps({"event": "fewnerd_contextual_token_cache_ready", **manifest}), flush=True)


if __name__ == "__main__":
    main()
