"""Build/load provenance-checked frozen semantic embedding caches."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import numpy as np

import smoke_concept_flavour_gpu as base

SCHEMA = "papers/malecns-semantic-embedding-cache-v1"


def _fingerprint(model_names, examples, scales) -> str:
    payload = {
        "models": list(model_names),
        "scales": list(map(int, scales)),
        "examples": [
            {"text": e.text, "phrase": e.phrase, "positive": bool(e.positive), "group": e.group}
            for e in examples
        ],
        "anchors": {
            "positive": list(base.POSITIVE_ANCHORS),
            "negative": list(base.NEGATIVE_ANCHORS),
            "heldout": list(base.HELDOUT_CONCEPTS),
        },
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _make_model(model_name: str, backend: str, device: str):
    from sentence_transformers import SentenceTransformer
    if backend == "openvino":
        return SentenceTransformer(model_name, backend="openvino", model_kwargs={"device": device.upper()})
    if backend == "torch":
        return SentenceTransformer(model_name, device=device)
    raise ValueError(f"unsupported embedding backend: {backend}")


def _encode_anchor_set(model, model_name: str, texts, *, kind: str, batch_size: int):
    texts = tuple(texts)
    if "e5" in model_name.lower():
        prefix = "query: " if kind == "query" else "passage: "
        texts = tuple(prefix + text for text in texts)
    values = model.encode(list(texts), batch_size=batch_size, convert_to_numpy=True,
                          normalize_embeddings=True, show_progress_bar=False)
    return np.asarray(values, dtype=np.float32)


def _encode_fields(model, model_name: str, examples, scales, *, batch_size: int):
    fields = []
    for example in examples:
        text = example.text
        axis = base.utf8_byte_axis(text)
        local = {}
        for scale in scales:
            spans = base._window_spans(text, int(scale))
            windows = [text[a:b] for a, b in spans]
            if "e5" in model_name.lower():
                windows = ["passage: " + value for value in windows]
            embeddings = model.encode(windows, batch_size=batch_size, convert_to_numpy=True,
                                      normalize_embeddings=False, show_progress_bar=False).astype(np.float32)
            local[int(scale)] = base.byte_aligned_scale(
                embeddings, base._byte_spans(text, spans), byte_length=axis.byte_length
            )
        fields.append(local)
    return fields


def build_cache(*, model_names, examples, scales, output: Path, backend: str = "torch",
                device: str = "cuda", batch_size: int = 64):
    started = time.perf_counter()
    fingerprint = _fingerprint(model_names, examples, scales)
    arrays = {}
    manifest_models = []
    for encoder_index, model_name in enumerate(model_names):
        t0 = time.perf_counter()
        model = _make_model(model_name, backend, device)
        literal = _encode_anchor_set(model, model_name, ("recurso",), kind="query", batch_size=batch_size)[0]
        positives = _encode_anchor_set(model, model_name, base.POSITIVE_ANCHORS, kind="query", batch_size=batch_size)
        negatives = _encode_anchor_set(model, model_name, base.NEGATIVE_ANCHORS, kind="query", batch_size=batch_size)
        heldout = _encode_anchor_set(model, model_name, base.HELDOUT_CONCEPTS, kind="query", batch_size=batch_size)
        fields = _encode_fields(model, model_name, examples, scales, batch_size=batch_size)
        positive_centroid = base._unit_vec_np(positives.mean(axis=0))
        negative_centroid = base._unit_vec_np(negatives.mean(axis=0))
        discriminative = base._unit_vec_np(positive_centroid - negative_centroid)
        literal = base._unit_vec_np(literal)
        heldout_centroid = base._unit_vec_np(heldout.mean(axis=0))
        prefix = f"e{encoder_index}"
        arrays[f"{prefix}_literal"] = literal
        arrays[f"{prefix}_positive_centroid"] = positive_centroid
        arrays[f"{prefix}_negative_centroid"] = negative_centroid
        arrays[f"{prefix}_discriminative"] = discriminative
        arrays[f"{prefix}_heldout_centroid"] = heldout_centroid
        for example_index, local in enumerate(fields):
            for scale, value in local.items():
                arrays[f"{prefix}_example_{example_index}_scale_{scale}"] = np.asarray(value, dtype=np.float32)
        manifest_models.append({
            "name": model_name,
            "dim": int(literal.shape[0]),
            "seconds": time.perf_counter() - t0,
            "geometry": {
                "literal_to_positive": base._cosine_np(literal, positive_centroid),
                "literal_to_negative": base._cosine_np(literal, negative_centroid),
                "discriminative_to_positive": base._cosine_np(discriminative, positive_centroid),
                "discriminative_to_negative": base._cosine_np(discriminative, negative_centroid),
                "discriminative_to_heldout": base._cosine_np(discriminative, heldout.mean(axis=0)),
            },
        })
        del model
    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(output, **arrays)
    manifest = {
        "schema": SCHEMA,
        "fingerprint": fingerprint,
        "backend": backend,
        "device": device,
        "batch_size": int(batch_size),
        "models": manifest_models,
        "scales": list(map(int, scales)),
        "example_count": len(examples),
        "seconds": time.perf_counter() - started,
        "npz": output.name,
    }
    output.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def load_cache(*, model_names, examples, scales, cache: Path):
    manifest = json.loads(cache.with_suffix(".manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema") != SCHEMA:
        raise RuntimeError(f"unexpected embedding cache schema: {manifest.get('schema')}")
    expected = _fingerprint(model_names, examples, scales)
    if manifest.get("fingerprint") != expected:
        raise RuntimeError("embedding cache fingerprint mismatch")
    archive = np.load(cache, allow_pickle=False)
    result = []
    for encoder_index, model_name in enumerate(model_names):
        prefix = f"e{encoder_index}"
        literal = archive[f"{prefix}_literal"].astype(np.float32)
        positive_centroid = archive[f"{prefix}_positive_centroid"].astype(np.float32)
        negative_centroid = archive[f"{prefix}_negative_centroid"].astype(np.float32)
        discriminative = archive[f"{prefix}_discriminative"].astype(np.float32)
        heldout_centroid = archive[f"{prefix}_heldout_centroid"].astype(np.float32)
        fields = []
        for example_index in range(len(examples)):
            local = {int(scale): archive[f"{prefix}_example_{example_index}_scale_{int(scale)}"].astype(np.float32)
                     for scale in scales}
            fields.append(local)
        geometry = next(item["geometry"] for item in manifest["models"] if item["name"] == model_name)
        result.append({
            "name": model_name,
            "dim": int(literal.shape[0]),
            "literal": literal,
            "positive_centroid": positive_centroid,
            "negative_centroid": negative_centroid,
            "discriminative": discriminative,
            "heldout_centroid": heldout_centroid,
            "fields": fields,
            "geometry": geometry,
        })
    return result, manifest
