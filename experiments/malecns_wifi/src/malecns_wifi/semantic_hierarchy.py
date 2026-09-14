"""Multiscale semantic coordinates for left-to-right MaleCNS input.

A document is embedded at several chunk sizes. The fine chunk is not fed as an
absolute point in embedding space; it is represented by its relation to each
larger chunk that contains it. Adjacent fine chunks therefore produce adjacent
*relative semantic coordinates*, and those coordinates are what we interpolate
through recurrent time.

An element-wise child/parent division is deliberately avoided. Embedding axes are
not individually meaningful: a harmless rotation of the embedding space would
change every coordinate-wise ratio, and values near zero make it unstable. The
relation here is geometric and rotation-invariant:

    alignment = <child_hat, parent_hat>
    residual  = child_hat - alignment * parent_hat

``alignment`` says how much of the child points with its containing context;
``residual`` says what semantic direction the child contributes beyond that
context. Together they are the operational "ratio" between child and parent.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ParentRelation:
    """A chunk expressed relative to the larger chunk containing it."""

    alignment: np.ndarray
    residual: np.ndarray
    vector: np.ndarray


@dataclass(frozen=True)
class MultiscaleRelationTrajectory:
    """Interpolated path through concatenated child/parent relations."""

    states: np.ndarray
    deltas: np.ndarray
    chunk_index: np.ndarray
    scale_slices: tuple[tuple[int, int], ...]


def _unit(vectors: np.ndarray) -> np.ndarray:
    values = np.asarray(vectors, dtype=np.float32)
    if values.ndim != 2 or values.shape[0] < 1 or values.shape[1] < 1:
        raise ValueError("embeddings must have shape [chunks, dimensions]")
    norms = np.linalg.norm(values, axis=1, keepdims=True)
    return values / np.maximum(norms, 1e-12)


def parent_relation(child_embeddings: np.ndarray, parent_embeddings: np.ndarray) -> ParentRelation:
    """Express each child embedding in coordinates relative to its containing parent.

    ``parent_embeddings[i]`` must be the embedding of the larger chunk containing
    ``child_embeddings[i]``. The same parent may therefore be repeated for several
    adjacent children.

    ``vector`` is ``[alignment, residual...]`` and is suitable for concatenating
    across scales. Because it depends only on dot products and vector differences
    in the common rotated frame, its geometry is stable under orthogonal rotations
    of the embedding space, unlike element-wise division.
    """
    child = _unit(child_embeddings)
    parent = _unit(parent_embeddings)
    if child.shape != parent.shape:
        raise ValueError("child and parent embeddings must have identical aligned shape")

    alignment = np.sum(child * parent, axis=1).astype(np.float32)
    residual = child - alignment[:, None] * parent
    vector = np.concatenate([alignment[:, None], residual], axis=1).astype(np.float32)
    return ParentRelation(alignment=alignment, residual=residual, vector=vector)


def multiscale_relations(
    child_embeddings: np.ndarray,
    containing_parents: list[np.ndarray] | tuple[np.ndarray, ...],
) -> tuple[np.ndarray, tuple[tuple[int, int], ...]]:
    """Concatenate the fine chunk's relation to every containing context scale.

    Each item in ``containing_parents`` has shape ``[n_fine_chunks, dimensions]``.
    For example, with 64/256/1024-token chunks, the first array may repeat the
    256-token parent's embedding for every 64-token child it contains, and the
    second does the same for the 1024-token parent. The result preserves both local
    and global semantic context at every fine position.
    """
    child = np.asarray(child_embeddings, dtype=np.float32)
    if not containing_parents:
        raise ValueError("at least one containing parent scale is required")

    blocks: list[np.ndarray] = []
    slices: list[tuple[int, int]] = []
    offset = 0
    for parent in containing_parents:
        relation = parent_relation(child, parent).vector
        blocks.append(relation)
        end = offset + relation.shape[1]
        slices.append((offset, end))
        offset = end
    return np.concatenate(blocks, axis=1), tuple(slices)


def interpolate_relations(
    relation_vectors: np.ndarray,
    *,
    steps_per_transition: int = 8,
    scale_slices: tuple[tuple[int, int], ...] = (),
) -> MultiscaleRelationTrajectory:
    """Interpolate only between relations of adjacent chunks.

    This is the key temporal rule: recurrent time does not interpolate absolute
    document embeddings or jump between unrelated scales. It moves smoothly from
    ``R(chunk_i | parents_i)`` to ``R(chunk_{i+1} | parents_{i+1})``. A parent
    boundary therefore appears naturally when the containing-context relation
    changes between two neighbouring fine chunks.
    """
    relations = np.asarray(relation_vectors, dtype=np.float32)
    if relations.ndim != 2 or relations.shape[0] < 1 or relations.shape[1] < 1:
        raise ValueError("relation_vectors must have shape [chunks, relation_dimensions]")
    if steps_per_transition < 1:
        raise ValueError("steps_per_transition must be >= 1")

    if len(relations) == 1:
        states = relations.copy()
        chunk_index = np.zeros(1, dtype=np.int32)
    else:
        pieces = [relations[:1]]
        mapping = [np.zeros(1, dtype=np.int32)]
        for index in range(1, len(relations)):
            alpha = np.linspace(
                1.0 / steps_per_transition,
                1.0,
                steps_per_transition,
                dtype=np.float32,
            )[:, None]
            segment = relations[index - 1] + alpha * (relations[index] - relations[index - 1])
            pieces.append(segment.astype(np.float32, copy=False))
            mapping.append(np.full(steps_per_transition, index, dtype=np.int32))
        states = np.vstack(pieces)
        chunk_index = np.concatenate(mapping)

    deltas = np.empty_like(states)
    deltas[0] = 0.0
    if len(states) > 1:
        deltas[1:] = states[1:] - states[:-1]
    return MultiscaleRelationTrajectory(
        states=states,
        deltas=deltas,
        chunk_index=chunk_index,
        scale_slices=scale_slices,
    )


def multiscale_semantic_trajectory(
    child_embeddings: np.ndarray,
    containing_parents: list[np.ndarray] | tuple[np.ndarray, ...],
    *,
    steps_per_transition: int = 8,
) -> MultiscaleRelationTrajectory:
    """Convenience path: aligned chunk hierarchy -> relative recurrent trajectory."""
    relations, slices = multiscale_relations(child_embeddings, containing_parents)
    return interpolate_relations(
        relations,
        steps_per_transition=steps_per_transition,
        scale_slices=slices,
    )
