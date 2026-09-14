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


# --- food as a change in hierarchical relation -------------------------------
#
# The flat contrast E(text+tag) - E(text) asks "does this passage resemble the
# tag". Differencing the *relations* instead asks something better posed:
#
#     F_i = R_i(text + tag) - R_i(text)
#
# "in what way does the presence of this tag change how this chunk sits inside
# its local and global context". A passage can resemble the tag while playing the
# same role it always played, and a passage can keep its wording while its role
# inside the surrounding argument changes completely. Only the second is what a
# tag boundary actually is.
#
# The tag is appended to every scale, child and parents alike, so both sides of
# the relation are read in the tag's presence and the difference isolates the
# change in relation rather than a change in what was embedded.


@dataclass(frozen=True)
class RelationalTagContrast:
    """Change in multiscale relation caused by the tag.

    Attribute names match :class:`TagContrast` on purpose: the gustatory
    projection and the direct control take either formulation unchanged.
    """

    contrast: np.ndarray
    intensity: np.ndarray
    alignment_shift: np.ndarray
    residual_shift: np.ndarray
    scale_slices: tuple[tuple[int, int], ...]
    intensity_mode: str

    @property
    def scales(self) -> int:
        return len(self.scale_slices)


def relational_tag_contrast(
    child_plain: np.ndarray,
    parents_plain,
    child_tagged: np.ndarray,
    parents_tagged,
    *,
    intensity: str = "norm",
    tag_embedding: np.ndarray | None = None,
) -> RelationalTagContrast:
    """Difference the multiscale relations read with and without the tag.

    ``parents_plain`` and ``parents_tagged`` are sequences of
    ``[n_fine_chunks, dimensions]`` arrays, one per containing scale, exactly as
    :func:`multiscale_relations` takes them.

    Polarity is not assumed here either. The redundancy that makes ``||F||``
    inverted for the flat contrast -- a passage already about the tag barely moves
    when the tag is appended -- may or may not survive the relational form, since
    the relation is a normalised geometric quantity and the tag perturbs child and
    parent together. Measure it with :func:`intensity_polarity` against gold spans
    using the real encoder before choosing a mode.

    * ``norm``            -- ``||F_i||`` over the concatenated relation
    * ``alignment_shift`` -- summed ``|delta a_i|`` across scales, i.e. how much
      the tag changes the degree to which this chunk follows its contexts
    * ``similarity``      -- ``<child_hat, tag_hat>``, the polarity-safe reference,
      which ignores the relation entirely and needs ``tag_embedding``
    """
    plain, slices = multiscale_relations(child_plain, parents_plain)
    tagged, tagged_slices = multiscale_relations(child_tagged, parents_tagged)
    if slices != tagged_slices or plain.shape != tagged.shape:
        raise ValueError("plain and tagged hierarchies must have the same scale structure")

    contrast = (tagged - plain).astype(np.float32)
    # Within each scale the relation vector is [alignment, residual...].
    alignment_shift = np.stack([contrast[:, start] for start, _ in slices], axis=1)
    residual_shift = np.stack(
        [np.linalg.norm(contrast[:, start + 1 : end], axis=1) for start, end in slices], axis=1
    ).astype(np.float32)

    if intensity == "norm":
        values = np.linalg.norm(contrast, axis=1)
    elif intensity == "alignment_shift":
        values = np.abs(alignment_shift).sum(axis=1)
    elif intensity == "similarity":
        if tag_embedding is None:
            raise ValueError("similarity intensity needs tag_embedding")
        tag = np.asarray(tag_embedding, dtype=np.float32).reshape(-1)
        child = _unit(child_plain)
        if tag.size != child.shape[1]:
            raise ValueError("tag embedding must live in the same semantic space as the text")
        values = child @ (tag / max(float(np.linalg.norm(tag)), 1e-12))
    else:
        raise ValueError(f"unknown intensity mode {intensity!r}")

    return RelationalTagContrast(
        contrast=contrast,
        intensity=values.astype(np.float32),
        alignment_shift=alignment_shift.astype(np.float32),
        residual_shift=residual_shift,
        scale_slices=slices,
        intensity_mode=intensity,
    )


def per_scale_intensity(contrast: RelationalTagContrast) -> np.ndarray:
    """``[chunks, scales]`` contrast magnitude, one column per context scale.

    Says which context scale carries the signal: a tag boundary visible only
    against the 4096-token parent is a different claim from one visible against
    the 256-token parent, and averaging them hides exactly that.
    """
    return np.stack(
        [np.linalg.norm(contrast.contrast[:, start:end], axis=1) for start, end in
         contrast.scale_slices],
        axis=1,
    ).astype(np.float32)


def interpolate_contrast(
    contrast: RelationalTagContrast, *, steps_per_transition: int = 8
) -> RelationalTagContrast:
    """Put the contrast on the same interpolated time axis as the trajectory.

    The relations are interpolated between adjacent chunks, so the food signal has
    to be too, or the fly would receive a smooth semantic path alongside a
    step-function taste.
    """
    path = interpolate_relations(
        contrast.contrast,
        steps_per_transition=steps_per_transition,
        scale_slices=contrast.scale_slices,
    )
    intensity = interpolate_relations(
        contrast.intensity[:, None], steps_per_transition=steps_per_transition
    ).states[:, 0]
    alignment = interpolate_relations(
        contrast.alignment_shift, steps_per_transition=steps_per_transition
    ).states
    residual = interpolate_relations(
        contrast.residual_shift, steps_per_transition=steps_per_transition
    ).states
    return RelationalTagContrast(
        contrast=path.states,
        intensity=intensity.astype(np.float32),
        alignment_shift=alignment.astype(np.float32),
        residual_shift=residual.astype(np.float32),
        scale_slices=contrast.scale_slices,
        intensity_mode=contrast.intensity_mode,
    )
