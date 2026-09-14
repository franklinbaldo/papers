"""Associative completion for sparse semantic pyramids.

Exact embedding cache and semantic memory are intentionally different things:

* cache: exact text -> exact embedding, lossless;
* memory: similar cheap key -> historically associated expensive channel,
  approximate and confidence-bearing.

The key and value spaces may differ.  A 64-d tiny-encoder key can retrieve a
1024-d Jina value because retrieval stores an empirical association; no vector
arithmetic is performed across the two spaces.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SemanticMemory:
    """A fixed key->value memory with provenance needed to prevent leakage."""

    keys: np.ndarray
    values: np.ndarray
    document_ids: np.ndarray
    positions: np.ndarray
    key_schema: str
    value_schema: str

    def __post_init__(self) -> None:
        keys = np.asarray(self.keys)
        values = np.asarray(self.values)
        documents = np.asarray(self.document_ids)
        positions = np.asarray(self.positions)
        rows = len(keys)
        if keys.ndim != 2 or values.ndim != 2:
            raise ValueError("memory keys and values must both be rank-2")
        if len(values) != rows or len(documents) != rows or len(positions) != rows:
            raise ValueError("keys, values and provenance must have the same row count")
        if not self.key_schema or not self.value_schema:
            raise ValueError("key_schema and value_schema are required")


@dataclass(frozen=True)
class Retrieval:
    value: np.ndarray
    confidence: float
    indices: np.ndarray
    similarities: np.ndarray
    weights: np.ndarray


@dataclass(frozen=True)
class Completion:
    value: np.ndarray
    source: str
    confidence: float
    retrieval: Retrieval | None


def unit_rows(values: np.ndarray) -> np.ndarray:
    rows = np.asarray(values, dtype=np.float32)
    return rows / np.maximum(np.linalg.norm(rows, axis=1, keepdims=True), 1e-12)


def admissible_memory_mask(
    memory: SemanticMemory,
    *,
    query_document: int | str,
    query_position: int,
    allow_same_document_prefix: bool = False,
) -> np.ndarray:
    """Rows the query is allowed to see.

    Confirmatory LODO sets ``allow_same_document_prefix=False`` and therefore
    excludes the held-out document completely.  The optional prefix mode is a
    separately reported online-memory ablation and only exposes records created
    strictly before the current position.
    """

    documents = np.asarray(memory.document_ids)
    positions = np.asarray(memory.positions)
    different_document = documents != query_document
    if not allow_same_document_prefix:
        return different_document
    earlier_same_document = (documents == query_document) & (positions < query_position)
    return different_document | earlier_same_document


def retrieve(
    query: np.ndarray,
    memory: SemanticMemory,
    *,
    k: int = 4,
    temperature: float = 0.1,
    allowed: np.ndarray | None = None,
    mode: str = "topk_barycenter",
) -> Retrieval:
    """Cosine retrieval from a cheap key into an arbitrary value space."""

    if k < 1:
        raise ValueError("k must be >= 1")
    if temperature <= 0:
        raise ValueError("temperature must be > 0")

    keys = unit_rows(memory.keys)
    q = np.asarray(query, dtype=np.float32).reshape(-1)
    if q.size != keys.shape[1]:
        raise ValueError("query dimension does not match the memory key space")
    q = q / max(float(np.linalg.norm(q)), 1e-12)
    similarities = keys @ q

    mask = np.ones(len(keys), dtype=bool) if allowed is None else np.asarray(allowed, dtype=bool)
    if mask.shape != (len(keys),):
        raise ValueError("allowed mask has wrong shape")
    candidates = np.flatnonzero(mask)
    if not len(candidates):
        raise ValueError("no admissible memory rows for this query")

    order = candidates[np.argsort(-similarities[candidates])]
    chosen = order[: min(k, len(order))]
    chosen_scores = similarities[chosen].astype(np.float32)

    if mode == "top1":
        chosen = chosen[:1]
        chosen_scores = chosen_scores[:1]
        weights = np.ones(1, dtype=np.float32)
    elif mode == "topk_barycenter":
        logits = (chosen_scores - float(chosen_scores.max())) / temperature
        weights = np.exp(logits).astype(np.float32)
        weights /= max(float(weights.sum()), 1e-12)
    else:
        raise ValueError(f"unknown retrieval mode {mode!r}")

    value = weights @ np.asarray(memory.values, dtype=np.float32)[chosen]
    return Retrieval(
        value=np.asarray(value, dtype=np.float32),
        confidence=float(chosen_scores.max()),
        indices=np.asarray(chosen, dtype=np.int64),
        similarities=chosen_scores,
        weights=weights,
    )


def complete_channel(
    query: np.ndarray,
    memory: SemanticMemory,
    *,
    query_document: int | str,
    query_position: int,
    threshold: float,
    real_value: np.ndarray | None = None,
    k: int = 4,
    temperature: float = 0.1,
    mode: str = "topk_barycenter",
    allow_same_document_prefix: bool = False,
) -> Completion:
    """Retrieve a missing channel or fall back to a real observation.

    ``real_value`` represents the expensive encoder call that would be made when
    memory is not trustworthy.  Leaving it as ``None`` makes low-confidence
    retrieval an explicit failure instead of silently fabricating a value.
    """

    allowed = admissible_memory_mask(
        memory,
        query_document=query_document,
        query_position=query_position,
        allow_same_document_prefix=allow_same_document_prefix,
    )
    found = retrieve(
        query,
        memory,
        k=k,
        temperature=temperature,
        allowed=allowed,
        mode=mode,
    )
    if found.confidence >= threshold:
        return Completion(found.value, "retrieved", found.confidence, found)
    if real_value is None:
        raise ValueError(
            "retrieval confidence is below threshold and no real fallback was supplied"
        )
    return Completion(
        np.asarray(real_value, dtype=np.float32),
        "real_fallback",
        found.confidence,
        found,
    )


def completion_ledger(completions: list[Completion]) -> dict:
    total = len(completions)
    retrieved = sum(item.source == "retrieved" for item in completions)
    fallback = sum(item.source == "real_fallback" for item in completions)
    confidences = [item.confidence for item in completions]
    return {
        "total_missing_channels": total,
        "retrieved": retrieved,
        "real_fallbacks": fallback,
        "encoder_calls_avoided": retrieved,
        "retrieval_fraction": retrieved / total if total else 0.0,
        "fallback_fraction": fallback / total if total else 0.0,
        "mean_retrieval_confidence": float(np.mean(confidences)) if confidences else float("nan"),
    }
