"""Byte-aligned multiscale semantic channels.

Every semantic scale lives on the same physical text axis.  Large-context
embeddings are computed at sparse anchors (typically overlapping window centres)
and linearly interpolated to every UTF-8 byte position.  Fine and coarse channels
can therefore be compared at exactly the same point in the source text instead of
being repeated piecewise-constantly across an arbitrary chunk.

Vector relations stay vector-valued.  Scalar summaries (norm, cosine, intensity)
are diagnostics only and must not replace the vector channel before the MaleCNS
input interface.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ByteAxis:
    """Canonical UTF-8 byte axis plus character-boundary lookup."""

    byte_length: int
    char_to_byte: np.ndarray


def utf8_byte_axis(text: str) -> ByteAxis:
    """Return exact UTF-8 byte coordinates for each Python character boundary.

    ``char_to_byte[i]`` is the byte offset at the start of ``text[i]`` and the
    final entry is the total byte length.  The byte axis is canonical for cached
    files and hashing; character offsets remain available for human annotations.
    """
    offsets = [0]
    total = 0
    for char in text:
        total += len(char.encode("utf-8"))
        offsets.append(total)
    return ByteAxis(byte_length=total, char_to_byte=np.asarray(offsets, dtype=np.int64))


def window_spans(text: str, scale: int) -> list[tuple[int, int]]:
    """Overlapping ``scale``-character windows spanning ``text`` (stride = scale//2).

    Same policy the flavour/food smoke scripts use for their anchor windows
    (``_window_spans`` there); published here as public API so every
    byte-synchronised-channel consumer, including token-classification tasks,
    shares one definition instead of re-deriving it.
    """
    n = len(text)
    if n == 0:
        return [(0, 1)]
    if n <= scale:
        return [(0, n)]
    stride = max(1, scale // 2)
    starts = list(range(0, n - scale + 1, stride))
    last = n - scale
    if starts[-1] != last:
        starts.append(last)
    return [(start, start + scale) for start in starts]


def char_spans_to_byte_spans(text: str, char_spans: list[tuple[int, int]]) -> np.ndarray:
    """Convert ``[char_start, char_end)`` spans to UTF-8 byte coordinates."""
    axis = utf8_byte_axis(text)
    return np.asarray(
        [(int(axis.char_to_byte[a]), int(axis.char_to_byte[b])) for a, b in char_spans],
        dtype=np.int64,
    )


def fixed_chunks(text: str, size: int) -> list[tuple[int, int]]:
    """Consecutive, non-overlapping ``[char_start, char_end)`` chunks of ``size``.

    The final chunk may be shorter than ``size`` (never padded, never dropped).
    Cuts are on character boundaries (safe for later UTF-8 byte conversion via
    ``char_spans_to_byte_spans``), unlike ``window_spans``, which overlaps.
    """
    if size <= 0:
        raise ValueError("size must be positive")
    n = len(text)
    if n == 0:
        return [(0, 0)]
    return [(start, min(start + size, n)) for start in range(0, n, size)]


def span_centres(spans: np.ndarray) -> np.ndarray:
    """Centre byte coordinate for aligned ``[start, end)`` spans."""
    values = np.asarray(spans, dtype=np.float64)
    if values.ndim != 2 or values.shape[1] != 2 or len(values) == 0:
        raise ValueError("spans must have shape [anchors, 2]")
    if np.any(values[:, 1] <= values[:, 0]):
        raise ValueError("every span must satisfy end > start")
    centres = (values[:, 0] + values[:, 1] - 1.0) / 2.0
    if np.any(np.diff(centres) <= 0):
        raise ValueError("anchor centres must be strictly increasing")
    return centres


def interpolate_to_bytes(
    anchor_embeddings: np.ndarray,
    anchor_centres: np.ndarray,
    *,
    byte_length: int,
) -> np.ndarray:
    """Linearly interpolate vector anchors to every byte position.

    Values before the first anchor and after the last anchor are held at the edge
    anchor.  Between centres the full embedding vector is interpolated coordinate
    by coordinate.  This makes a 1024-token context change slowly over the text
    while an 8-token context can change rapidly, yet both are sampled at the same
    byte coordinate.
    """
    values = np.asarray(anchor_embeddings, dtype=np.float32)
    centres = np.asarray(anchor_centres, dtype=np.float64).reshape(-1)
    if values.ndim != 2 or len(values) != len(centres):
        raise ValueError("anchor_embeddings must be [anchors, dimensions]")
    if byte_length < 0:
        raise ValueError("byte_length must be non-negative")
    if len(values) == 0:
        raise ValueError("at least one anchor is required")
    if np.any(np.diff(centres) <= 0):
        raise ValueError("anchor centres must be strictly increasing")
    if byte_length == 0:
        return np.empty((0, values.shape[1]), dtype=np.float32)
    if len(values) == 1:
        return np.repeat(values, byte_length, axis=0)

    positions = np.arange(byte_length, dtype=np.float64)
    right = np.searchsorted(centres, positions, side="right")
    right = np.clip(right, 1, len(centres) - 1)
    left = right - 1

    denom = centres[right] - centres[left]
    alpha = ((positions - centres[left]) / denom).astype(np.float32)
    alpha = np.clip(alpha, 0.0, 1.0)[:, None]
    out = values[left] * (1.0 - alpha) + values[right] * alpha
    out[positions <= centres[0]] = values[0]
    out[positions >= centres[-1]] = values[-1]
    return out.astype(np.float32, copy=False)


def elementwise_ratio(
    numerator: np.ndarray,
    denominator: np.ndarray,
    *,
    epsilon: float = 1e-4,
) -> np.ndarray:
    """Vector-valued elementwise ratio with sign-preserving denominator clamp."""
    left = np.asarray(numerator, dtype=np.float32)
    right = np.asarray(denominator, dtype=np.float32)
    if left.shape != right.shape:
        raise ValueError("ratio operands must share shape")
    if epsilon <= 0:
        raise ValueError("epsilon must be positive")
    sign = np.where(right < 0.0, -1.0, 1.0).astype(np.float32)
    safe = np.where(np.abs(right) < epsilon, sign * np.float32(epsilon), right)
    return (left / safe).astype(np.float32)


def vector_relations(left: np.ndarray, right: np.ndarray, *, epsilon: float = 1e-4) -> dict:
    """Keep several relation channels as full vectors, never scalarise early."""
    a = np.asarray(left, dtype=np.float32)
    b = np.asarray(right, dtype=np.float32)
    if a.shape != b.shape:
        raise ValueError("relation operands must share shape")
    return {
        "ratio": elementwise_ratio(a, b, epsilon=epsilon),
        "difference": (a - b).astype(np.float32),
        "product": (a * b).astype(np.float32),
    }


def byte_aligned_scale(
    anchor_embeddings: np.ndarray,
    anchor_spans: np.ndarray,
    *,
    byte_length: int,
) -> np.ndarray:
    """Convenience wrapper: span anchors -> full byte-resolution vector field."""
    return interpolate_to_bytes(
        anchor_embeddings,
        span_centres(anchor_spans),
        byte_length=byte_length,
    )
