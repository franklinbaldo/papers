"""Tests for food derived from a change in hierarchical relation.

The synthetic corpus below separates the two things the flat contrast conflates:
a region that *resembles* the tag, and a region whose *role inside its context*
the tag changes. They are placed at different positions, so a signal that tracks
one cannot be credited for the other.
"""

import numpy as np
import pytest

from malecns_wifi.semantic_food import contrast_food_drive, intensity_polarity
from malecns_wifi.semantic_hierarchy import (
    interpolate_contrast,
    per_scale_intensity,
    relational_tag_contrast,
)

CHUNKS, DIMENSIONS, SCALES = 48, 24, 3


def _hierarchy(seed: int = 0):
    """Topic-similar region at 10:20; role-changing region at 30:40."""
    rng = np.random.default_rng(seed)
    tag = rng.normal(size=DIMENSIONS).astype(np.float32)
    tag /= np.linalg.norm(tag)

    child = rng.normal(size=(CHUNKS, DIMENSIONS)).astype(np.float32) * 0.5
    topic = np.zeros(CHUNKS, dtype=bool)
    topic[10:20] = True
    child[topic] += 2.0 * tag

    parents = [rng.normal(size=(CHUNKS, DIMENSIONS)).astype(np.float32) for _ in range(SCALES)]

    role = np.zeros(CHUNKS, dtype=bool)
    role[30:40] = True
    # The tag reorients the *parents* only where the role changes, so the relation
    # moves there without the child text resembling the tag any more than before.
    child_tagged = child + 0.05 * rng.normal(size=child.shape).astype(np.float32)
    parents_tagged = []
    for parent in parents:
        shifted = parent + 0.05 * rng.normal(size=parent.shape).astype(np.float32)
        shifted[role] += 1.5 * tag
        parents_tagged.append(shifted.astype(np.float32))
    return child, parents, child_tagged, parents_tagged, tag, topic, role


def test_relational_contrast_tracks_role_change_not_topic_similarity() -> None:
    child, parents, child_tagged, parents_tagged, tag, topic, role = _hierarchy()
    contrast = relational_tag_contrast(child, parents, child_tagged, parents_tagged)

    on_role = intensity_polarity(contrast.intensity, role)["point_biserial"]
    on_topic = intensity_polarity(contrast.intensity, topic)["point_biserial"]
    assert on_role > 0.5, "relational contrast should rise where the role changes"
    assert on_role > on_topic, "it should track role change more than topic similarity"


def test_similarity_reference_tracks_topic_not_role() -> None:
    """The polarity-safe flat reference answers the other question, by design."""
    child, parents, child_tagged, parents_tagged, tag, topic, role = _hierarchy()
    contrast = relational_tag_contrast(
        child, parents, child_tagged, parents_tagged,
        intensity="similarity", tag_embedding=tag,
    )
    assert intensity_polarity(contrast.intensity, topic)["point_biserial"] > 0.5
    assert (
        intensity_polarity(contrast.intensity, topic)["point_biserial"]
        > intensity_polarity(contrast.intensity, role)["point_biserial"]
    )


def test_alignment_shift_is_reported_per_scale() -> None:
    child, parents, child_tagged, parents_tagged, *_ = _hierarchy()
    contrast = relational_tag_contrast(child, parents, child_tagged, parents_tagged)
    assert contrast.scales == SCALES
    assert contrast.alignment_shift.shape == (CHUNKS, SCALES)
    assert contrast.residual_shift.shape == (CHUNKS, SCALES)
    assert per_scale_intensity(contrast).shape == (CHUNKS, SCALES)


def test_per_scale_intensity_localises_the_scale_that_moved() -> None:
    """A signal visible only against one context scale must not be averaged away."""
    child, parents, child_tagged, parents_tagged, tag, _, role = _hierarchy()
    # Move only the coarsest parent inside the role region.
    parents_tagged = [parent.copy() for parent in parents]
    parents_tagged[-1][role] += 2.0 * tag
    contrast = relational_tag_contrast(child, parents, child, parents_tagged)

    scaled = per_scale_intensity(contrast)
    inside = scaled[role].mean(axis=0)
    assert inside[-1] > 5 * max(inside[0], 1e-6), f"expected the coarse scale to carry it: {inside}"


def test_similarity_intensity_requires_a_tag() -> None:
    child, parents, child_tagged, parents_tagged, *_ = _hierarchy()
    with pytest.raises(ValueError, match="needs tag_embedding"):
        relational_tag_contrast(
            child, parents, child_tagged, parents_tagged, intensity="similarity"
        )


def test_mismatched_hierarchies_are_refused() -> None:
    child, parents, child_tagged, parents_tagged, *_ = _hierarchy()
    with pytest.raises(ValueError, match="same scale structure"):
        relational_tag_contrast(child, parents, child_tagged, parents_tagged[:-1])


def test_interpolated_contrast_matches_the_trajectory_time_axis() -> None:
    child, parents, child_tagged, parents_tagged, *_ = _hierarchy()
    contrast = relational_tag_contrast(child, parents, child_tagged, parents_tagged)
    steps = 4
    interpolated = interpolate_contrast(contrast, steps_per_transition=steps)
    expected = 1 + (CHUNKS - 1) * steps
    assert interpolated.contrast.shape == (expected, contrast.contrast.shape[1])
    assert interpolated.intensity.shape == (expected,)
    # Chunk endpoints survive interpolation unchanged.
    assert np.allclose(interpolated.contrast[0], contrast.contrast[0], atol=1e-5)
    assert np.allclose(interpolated.contrast[steps], contrast.contrast[1], atol=1e-5)


def test_gustatory_projection_accepts_the_relational_contrast_unchanged() -> None:
    """Same attribute names, so the food projection takes either formulation."""
    child, parents, child_tagged, parents_tagged, *_ = _hierarchy()
    contrast = relational_tag_contrast(child, parents, child_tagged, parents_tagged)
    drive = contrast_food_drive(contrast, np.arange(13), seed=2)
    assert drive.shape == (CHUNKS, 13)
    assert np.allclose(np.linalg.norm(drive, axis=1), np.abs(contrast.intensity), atol=1e-4)
