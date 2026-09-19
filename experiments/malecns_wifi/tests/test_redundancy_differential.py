"""Tests for food read as semantic redundancy, and for the chunk/parent differential.

The corpus here models the redundancy effect explicitly: appending the tag pulls an
embedding toward the tag in proportion to the component of the tag it does *not*
already have. Text that already says the tag therefore barely moves, which is the
whole premise of reading relevance as redundancy.
"""

import numpy as np
import pytest

from malecns_wifi.semantic_food import intensity_polarity, tag_contrast
from malecns_wifi.semantic_hierarchy import contrast_norm, redundancy_differential

CHUNKS, DIMENSIONS, SCALES = 60, 24, 2


def _append_tag(embeddings: np.ndarray, tag: np.ndarray, strength: float = 0.9) -> np.ndarray:
    """Redundancy-aware tagging: the pull is what the text does not already have."""
    unit = embeddings / np.maximum(np.linalg.norm(embeddings, axis=1, keepdims=True), 1e-12)
    residual = tag[None, :] - unit * (unit @ tag)[:, None]
    return (unit + strength * residual).astype(np.float32)


def _corpus(seed: int = 0):
    """A narrow answer at 25:30 inside a broad, only-partly-relevant section at 20:40.

    Both the answer and the section are about the tag, so absolute redundancy marks
    the whole section. Only the chunk-against-parent differential can say where
    inside the section the answer actually sits.
    """
    rng = np.random.default_rng(seed)
    tag = rng.normal(size=DIMENSIONS).astype(np.float32)
    tag /= np.linalg.norm(tag)

    answer = np.zeros(CHUNKS, dtype=bool)
    answer[25:30] = True
    section = np.zeros(CHUNKS, dtype=bool)
    section[20:40] = True

    child = rng.normal(size=(CHUNKS, DIMENSIONS)).astype(np.float32) * 0.6
    child[section] += 1.0 * tag        # the section is somewhat about the tag
    child[answer] += 3.0 * tag         # the answer is squarely about it

    # The parent repeats one embedding for every fine chunk it contains: the
    # section's parent is the section's average, diluted by the surrounding text.
    parents = []
    for span in (6, 20):
        parent = np.empty_like(child)
        for start in range(0, CHUNKS, span):
            stop = min(start + span, CHUNKS)
            parent[start:stop] = child[start:stop].mean(axis=0)
        parents.append(parent.astype(np.float32))

    child_tagged = _append_tag(child, tag)
    parents_tagged = [_append_tag(parent, tag) for parent in parents]
    return child, parents, child_tagged, parents_tagged, tag, answer, section


def test_redundancy_intensity_recovers_the_intended_polarity() -> None:
    """exp(-||F||/tau) marks the relevant text, where ||F|| alone is inverted."""
    child, _, child_tagged, _, tag, answer, _ = _corpus()
    raw = tag_contrast(child, child_tagged, tag, intensity="norm")
    redundancy = tag_contrast(child, child_tagged, tag, intensity="redundancy")

    assert intensity_polarity(raw.intensity, answer)["point_biserial"] < 0
    assert intensity_polarity(redundancy.intensity, answer)["point_biserial"] > 0.5


def test_redundancy_keeps_the_tag_conditioning_that_similarity_discards() -> None:
    """Both work here; only one still depends on what the tag does to the text."""
    child, _, child_tagged, _, tag, answer, _ = _corpus()
    redundancy = tag_contrast(child, child_tagged, tag, intensity="redundancy")
    similarity = tag_contrast(child, child_tagged, tag, intensity="similarity")
    assert intensity_polarity(redundancy.intensity, answer)["point_biserial"] > 0.5
    assert intensity_polarity(similarity.intensity, answer)["point_biserial"] > 0.5

    # Similarity ignores the tagged pass entirely: perturbing it changes nothing.
    perturbed = child_tagged + 0.5
    assert np.allclose(
        tag_contrast(child, perturbed, tag, intensity="similarity").intensity,
        similarity.intensity,
        atol=1e-5,
    )
    assert not np.allclose(
        tag_contrast(child, perturbed, tag, intensity="redundancy").intensity,
        redundancy.intensity,
        atol=1e-3,
    )


def test_contrast_norm_is_smaller_where_the_tag_is_redundant() -> None:
    child, _, child_tagged, _, _, answer, _ = _corpus()
    distances = contrast_norm(child, child_tagged)
    assert distances[answer].mean() < distances[~answer].mean()


def test_differential_localises_the_answer_inside_a_relevant_section() -> None:
    """The point of A = D(parent) - D(child): absolute redundancy marks the section."""
    child, parents, child_tagged, parents_tagged, tag, answer, section = _corpus()
    inside_section = section & ~answer

    absolute = tag_contrast(child, child_tagged, tag, intensity="redundancy").intensity
    differential = redundancy_differential(child, child_tagged, parents, parents_tagged)

    # Absolute redundancy cannot separate the answer from the rest of its section.
    absolute_gap = absolute[answer].mean() - absolute[inside_section].mean()
    # The differential compares each chunk against the very context containing it.
    coarse = differential[:, -1]
    differential_gap = coarse[answer].mean() - coarse[inside_section].mean()

    assert differential_gap > 0, "the answer should out-explain its own section"
    assert differential_gap > absolute_gap


def test_differential_ranks_within_a_section_without_a_guaranteed_sign() -> None:
    """The ranking is the robust property; the absolute sign is encoder-dependent.

    ``A = D(parent) - D(child)`` is only positive where the chunk explains the tag
    better than its context *if* a longer chunk's embedding does not concentrate
    the shared topic more than its constituents do. When parents behave like
    averages of their children, the averaging cancels per-chunk noise, the parent
    looks more tag-pure than any single child, and ``A`` goes negative across the
    board -- including in the answer, where this corpus measures about -0.26.

    Whether a real encoder does that is an encoder property, not something this
    construction can settle, so nothing here depends on the sign.

    What survives is narrower than "A marks the answer" and needs saying plainly:
    ``A`` is a *within-context* discriminator, not a global one. Outside the
    relevant section both child and parent are equally unrelated to the tag, so
    their contrasts cancel and ``A`` sits near zero -- higher than inside the
    section, where both are relevant and the pooled parent is the purer of the
    two. Ranking irrelevant text above the answer is exactly what a global marker
    must not do, so ``A`` has to be read against the section it belongs to, or
    paired with absolute redundancy to gate where it applies.
    """
    child, parents, child_tagged, parents_tagged, _, answer, section = _corpus()
    differential = redundancy_differential(child, child_tagged, parents, parents_tagged)
    assert differential.shape == (CHUNKS, SCALES)

    coarse = differential[:, -1]
    inside_section = section & ~answer
    # Within the section, the answer out-explains its neighbours.
    assert coarse[answer].mean() > coarse[inside_section].mean()
    # But it does not beat unrelated text, which is why this is not a global marker.
    assert coarse[~section].mean() > coarse[answer].mean()


def test_differential_requires_aligned_parent_scales() -> None:
    child, parents, child_tagged, parents_tagged, *_ = _corpus()
    with pytest.raises(ValueError, match="aligned between plain and tagged"):
        redundancy_differential(child, child_tagged, parents, parents_tagged[:-1])
    with pytest.raises(ValueError, match="at least one containing parent"):
        redundancy_differential(child, child_tagged, [], [])


def test_differential_rejects_unrepeated_parents() -> None:
    """Parents must be repeated to one row per fine chunk, not given once per parent."""
    child, parents, child_tagged, parents_tagged, *_ = _corpus()
    with pytest.raises(ValueError, match="repeated to one row per fine chunk"):
        redundancy_differential(
            child, child_tagged, [parents[0][:5]], [parents_tagged[0][:5]]
        )
