"""Semantic-trajectory supervision through an anatomically grounded food teacher.

The tagging experiment should not ask the frozen MaleCNS to rediscover language
from bytes. A language encoder first maps cumulative text chunks into a semantic
space. The connectome receives the *motion* through that space (delta embeddings),
conditioned on the embedding of the tag being sought.

The food circuit is a teacher, not an inference-time label channel. During
training we may stimulate an explicitly identified appetitive gustatory population
to measure the internal state that "food" produces. The student pass sees the
same semantic trajectory with no food pulse and is trained to reproduce the
teacher response over annotated spans. At evaluation/inference there is never an
external food pulse.

This module deliberately contains only geometry/scheduling primitives. Selecting
actual sugar-GRN body IDs is a provenance step against the MaleCNS annotations and
must be recorded explicitly; graph degree is never used as a biological label.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SemanticTrajectory:
    """Interpolated semantic path and its local motion.

    ``states`` are absolute semantic embeddings after interpolation. ``deltas`` are
    the local changes that form the primary recurrent input. ``chunk_index`` maps
    each interpolated step back to the cumulative-text checkpoint that generated
    it, so gold spans can be projected onto the same time axis without guessing.
    """

    states: np.ndarray
    deltas: np.ndarray
    chunk_index: np.ndarray


def interpolate_semantic_chunks(
    embeddings: np.ndarray,
    *,
    steps_per_transition: int = 8,
    normalise: bool = True,
) -> SemanticTrajectory:
    """Turn cumulative chunk embeddings into a smooth left-to-right trajectory.

    ``embeddings[k]`` is the semantic embedding of text from the beginning through
    chunk ``k``. Between checkpoints we linearly interpolate several recurrent
    steps. This keeps expensive encoder calls sparse while exposing the connectome
    to small semantic changes rather than large chunk jumps.

    The first delta is zero because there is no previous semantic state. Every
    later delta is ``state[t] - state[t-1]``.
    """
    vectors = np.asarray(embeddings, dtype=np.float32)
    if vectors.ndim != 2 or vectors.shape[0] < 1 or vectors.shape[1] < 1:
        raise ValueError("embeddings must have shape [chunks, dimensions]")
    if steps_per_transition < 1:
        raise ValueError("steps_per_transition must be >= 1")

    if normalise:
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        vectors = vectors / np.maximum(norms, 1e-12)

    if len(vectors) == 1:
        states = vectors.copy()
        chunk_index = np.zeros(1, dtype=np.int32)
    else:
        pieces: list[np.ndarray] = [vectors[:1]]
        mapping: list[np.ndarray] = [np.zeros(1, dtype=np.int32)]
        for index in range(1, len(vectors)):
            # Exclude alpha=0 because the previous endpoint is already present;
            # include alpha=1 so every real chunk embedding remains on the path.
            alpha = np.linspace(
                1.0 / steps_per_transition,
                1.0,
                steps_per_transition,
                dtype=np.float32,
            )[:, None]
            segment = vectors[index - 1] + alpha * (vectors[index] - vectors[index - 1])
            pieces.append(segment.astype(np.float32, copy=False))
            mapping.append(np.full(steps_per_transition, index, dtype=np.int32))
        states = np.vstack(pieces)
        chunk_index = np.concatenate(mapping)

    deltas = np.empty_like(states)
    deltas[0] = 0.0
    if len(states) > 1:
        deltas[1:] = states[1:] - states[:-1]
    return SemanticTrajectory(states=states, deltas=deltas, chunk_index=chunk_index)


def condition_on_tag(
    trajectory: SemanticTrajectory,
    tag_embedding: np.ndarray,
    *,
    include_absolute_state: bool = False,
) -> np.ndarray:
    """Attach the semantic identity of the tag being sought to every time step.

    The default input is ``[delta_semantics, tag_embedding]``. Absolute semantic
    state can be added as an ablation, producing
    ``[delta_semantics, absolute_semantics, tag_embedding]``.
    """
    tag = np.asarray(tag_embedding, dtype=np.float32).reshape(-1)
    if tag.size != trajectory.deltas.shape[1]:
        raise ValueError("tag embedding must live in the same semantic space as the text")
    norm = np.linalg.norm(tag)
    if norm > 0:
        tag = tag / norm
    repeated = np.broadcast_to(tag, trajectory.deltas.shape)
    blocks = [trajectory.deltas]
    if include_absolute_state:
        blocks.append(trajectory.states)
    blocks.append(repeated)
    return np.concatenate(blocks, axis=1).astype(np.float32, copy=False)


def span_mask_from_chunks(
    chunk_index: np.ndarray,
    spans: list[tuple[int, int]] | tuple[tuple[int, int], ...],
) -> np.ndarray:
    """Project half-open chunk spans onto the interpolated recurrent time axis."""
    mapping = np.asarray(chunk_index)
    mask = np.zeros(mapping.shape, dtype=np.float32)
    for start, end in spans:
        if start < 0 or end <= start:
            raise ValueError(f"invalid chunk span {(start, end)}")
        mask[(mapping >= start) & (mapping < end)] = 1.0
    return mask


def edge_targets(mask: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """START/END impulses derived from one continuous consumption mask."""
    inside = np.asarray(mask, dtype=np.float32).reshape(-1)
    previous = np.concatenate([np.zeros(1, dtype=np.float32), inside[:-1]])
    following = np.concatenate([inside[1:], np.zeros(1, dtype=np.float32)])
    start = ((inside > 0) & (previous <= 0)).astype(np.float32)
    end = ((inside > 0) & (following <= 0)).astype(np.float32)
    return start, end


def matched_random_population(
    sensory_indices: np.ndarray,
    food_indices: np.ndarray,
    *,
    seed: int,
) -> np.ndarray:
    """Random sensory control matched exactly to the size of the food population.

    Real food neurons are excluded. Matching count keeps injected energy and the
    number of directly stimulated cells identical; only anatomical identity moves.
    """
    sensory = np.asarray(sensory_indices, dtype=np.int64)
    food = np.asarray(food_indices, dtype=np.int64)
    candidates = np.setdiff1d(sensory, food, assume_unique=False)
    if food.size == 0:
        raise ValueError("food population is empty")
    if candidates.size < food.size:
        raise ValueError("not enough non-food sensory neurons for a matched control")
    rng = np.random.default_rng(seed)
    return np.sort(rng.choice(candidates, size=food.size, replace=False)).astype(np.int64)


def teacher_food_drive(
    neurons: int,
    time_steps: int,
    food_indices: np.ndarray,
    mask: np.ndarray,
    *,
    amplitude: float = 1.0,
) -> np.ndarray:
    """Dense toy/reference drive for the teacher pass.

    Full-brain training should scatter the same values directly on device rather
    than allocating this dense matrix. Keeping the reference implementation here
    makes scheduling and control tests explicit and reproducible.
    """
    food = np.asarray(food_indices, dtype=np.int64)
    active = np.asarray(mask, dtype=np.float32).reshape(-1)
    if active.size != time_steps:
        raise ValueError("mask length must equal time_steps")
    if np.any(food < 0) or np.any(food >= neurons):
        raise ValueError("food index outside operator")
    drive = np.zeros((time_steps, neurons), dtype=np.float32)
    drive[:, food] = active[:, None] * np.float32(amplitude)
    return drive
