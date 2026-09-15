"""Core Few-NERD IO/span utilities for MaleCNS NER experiments.

Few-NERD uses IO tagging, not BIO.  Entity identity is therefore the maximal
contiguous run of a non-zero label id; a label change starts a new entity.
The primary benchmark uses ``fine_ner_tags`` (66 fine-grained entity types).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class ByteAxis:
    text: str
    token_byte_spans: tuple[tuple[int, int], ...]
    byte_labels: tuple[int, ...]


@dataclass(frozen=True, order=True)
class Entity:
    start_token: int
    end_token: int  # exclusive
    label: int


def canonical_byte_axis(tokens: Sequence[str], labels: Sequence[int]) -> ByteAxis:
    """Reconstruct one sentence and project token labels onto UTF-8 bytes."""
    if len(tokens) != len(labels):
        raise ValueError("token/label length mismatch")

    parts: list[str] = []
    spans: list[tuple[int, int]] = []
    byte_labels: list[int] = []
    cursor = 0

    for i, (token, label) in enumerate(zip(tokens, labels, strict=True)):
        token = str(token)
        label = int(label)
        if i:
            parts.append(" ")
            byte_labels.append(0)
            cursor += 1

        raw = token.encode("utf-8")
        start = cursor
        end = start + len(raw)
        parts.append(token)
        spans.append((start, end))
        byte_labels.extend([label] * len(raw))
        cursor = end

    text = "".join(parts)
    encoded = text.encode("utf-8")
    if len(encoded) != len(byte_labels):
        raise RuntimeError("byte-axis length mismatch")

    for token, (start, end) in zip(tokens, spans, strict=True):
        if encoded[start:end] != str(token).encode("utf-8"):
            raise RuntimeError("token-byte roundtrip mismatch")

    return ByteAxis(text, tuple(spans), tuple(byte_labels))


def io_entities(labels: Sequence[int]) -> tuple[Entity, ...]:
    """Convert Few-NERD IO labels into exact token spans plus entity type."""
    entities: list[Entity] = []
    start: int | None = None
    active = 0

    for i, raw_label in enumerate([*labels, 0]):
        label = int(raw_label)
        if label == active:
            continue
        if active != 0 and start is not None:
            entities.append(Entity(start, i, active))
        if label == 0:
            start = None
        else:
            start = i
        active = label

    return tuple(entities)


def byte_labels_to_token_labels(
    byte_labels: Sequence[int], token_byte_spans: Sequence[tuple[int, int]]
) -> tuple[int, ...]:
    """Collapse byte predictions back to tokens by deterministic majority vote.

    Ties are resolved by the smallest label id.  Separator bytes are absent from
    token spans and therefore cannot vote for a token label.
    """
    out: list[int] = []
    for start, end in token_byte_spans:
        if not (0 <= start < end <= len(byte_labels)):
            raise ValueError("invalid token byte span")
        counts: dict[int, int] = {}
        for raw in byte_labels[start:end]:
            label = int(raw)
            counts[label] = counts.get(label, 0) + 1
        best_count = max(counts.values())
        out.append(min(label for label, count in counts.items() if count == best_count))
    return tuple(out)


def exact_entity_prf(
    gold_sequences: Iterable[Sequence[int]],
    pred_sequences: Iterable[Sequence[int]],
) -> dict[str, float | int]:
    """Micro precision/recall/F1 with exact token span + type matching."""
    tp = fp = fn = 0
    pairs = 0
    for gold, pred in zip(gold_sequences, pred_sequences, strict=True):
        if len(gold) != len(pred):
            raise ValueError("gold/pred token length mismatch")
        gold_entities = set(io_entities(gold))
        pred_entities = set(io_entities(pred))
        tp += len(gold_entities & pred_entities)
        fp += len(pred_entities - gold_entities)
        fn += len(gold_entities - pred_entities)
        pairs += 1

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "sentences": pairs,
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }
