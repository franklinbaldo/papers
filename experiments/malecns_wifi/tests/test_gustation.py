"""Tests for semantic gustation: learning a text-to-taste transduction."""

import numpy as np
import pytest

from malecns_wifi.gustation import (
    FlavourSpec,
    flavour_codebook,
    flavour_only_baseline,
    gustation_conditions,
    target_flavour,
)

TAGS, DOCUMENTS, PER_DOCUMENT = 9, 12, 20


def _corpus(seed: int = 0):
    rng = np.random.default_rng(seed)
    total = DOCUMENTS * PER_DOCUMENT
    groups = np.repeat(np.arange(DOCUMENTS), PER_DOCUMENT)
    masks = np.zeros((total, TAGS), dtype=np.float32)
    for document in range(DOCUMENTS):
        for tag in range(TAGS):
            masks[document * PER_DOCUMENT + 1 + tag * 2, tag] = 1.0
    # Semantics that genuinely carry the tag identity, so transduction can work.
    semantics = np.hstack([masks * 2.0, rng.normal(size=(total, 6))]).astype(np.float32)
    embeddings = rng.normal(size=(TAGS, 64)).astype(np.float32)
    return semantics, masks, embeddings, groups


def test_a_composition_needs_k_well_below_the_tag_count() -> None:
    """k near the tag count is a rotated one-hot, and the flavourizer a classifier."""
    _, _, embeddings, _ = _corpus()
    codebook, diagnostics = flavour_codebook(embeddings, FlavourSpec(channels=4))
    assert codebook.shape == (TAGS, 4)
    assert diagnostics["rank"] == 4
    # Tags are forced to share axes: nine unit vectors in four dimensions cannot
    # be mutually orthogonal.
    assert diagnostics["mean_abs_cosine"] > 0.1

    with pytest.raises(ValueError, match="not a composition"):
        flavour_codebook(embeddings, FlavourSpec(channels=8))


def test_semantically_close_tags_taste_similar() -> None:
    """The property that makes this a sense rather than a labelling."""
    rng = np.random.default_rng(1)
    base = rng.normal(size=64).astype(np.float32)
    embeddings = np.stack([base, base + 0.05 * rng.normal(size=64), *rng.normal(size=(4, 64))])
    codebook, _ = flavour_codebook(embeddings.astype(np.float32), FlavourSpec(channels=3))
    near = float(codebook[0] @ codebook[1])
    far = max(float(codebook[0] @ codebook[index]) for index in range(2, len(codebook)))
    assert near > far


def test_random_codebook_is_the_matched_control() -> None:
    _, _, embeddings, _ = _corpus()
    semantic, _ = flavour_codebook(embeddings, FlavourSpec(channels=4), source="semantic")
    random, _ = flavour_codebook(embeddings, FlavourSpec(channels=4), source="random")
    assert semantic.shape == random.shape
    assert np.allclose(np.linalg.norm(random, axis=1), 1.0, atol=1e-5)
    assert not np.allclose(semantic, random)

    with pytest.raises(ValueError, match="unknown codebook source"):
        flavour_codebook(embeddings, FlavourSpec(channels=4), source="umami")


def test_target_flavour_blends_overlapping_tags() -> None:
    codebook = np.eye(3, dtype=np.float32)
    masks = np.asarray([[1, 1, 0], [0, 0, 0]], dtype=np.float32)
    blended = target_flavour(masks, codebook)
    assert np.allclose(blended[0], codebook[0] + codebook[1])
    assert np.allclose(blended[1], 0.0)


def test_three_streams_are_produced_and_the_oracle_is_the_ceiling() -> None:
    semantics, masks, embeddings, groups = _corpus()
    spec = FlavourSpec(channels=4, seed=0)
    result = gustation_conditions(semantics, masks, embeddings, groups, spec)

    streams = result["streams"]
    assert set(streams) == {"semantic_only", "oracle_flavour", "learned_flavour"}
    assert streams["oracle_flavour"].shape == (len(masks), 4)
    assert streams["learned_flavour"].shape == (len(masks), 4)
    # The transduction is learnable here because the semantics carry the identity.
    assert result["transduction_r2"] > 0.3


def test_flavour_only_baseline_is_measured_before_the_fly() -> None:
    """If k channels already recover the tags, the operator is decoration."""
    semantics, masks, embeddings, groups = _corpus()
    spec = FlavourSpec(channels=4, seed=0)
    result = gustation_conditions(semantics, masks, embeddings, groups, spec)
    baseline = flavour_only_baseline(result["streams"]["learned_flavour"], masks, groups)

    assert baseline["channels"] == 4
    assert 0.0 <= baseline["flavour_only_auprc"] <= 1.0
    assert baseline["random_auprc"] == pytest.approx(float(masks.max(axis=1).mean()))


def test_oracle_flavour_is_not_reported_as_a_result() -> None:
    """A ceiling condition must be labelled; this pins the name it carries."""
    semantics, masks, embeddings, groups = _corpus()
    result = gustation_conditions(semantics, masks, embeddings, groups, FlavourSpec(channels=4))
    assert "oracle_flavour" in result["streams"]
    # The oracle stream is the target itself, so it trivially encodes the tags.
    oracle = result["streams"]["oracle_flavour"]
    outside = masks.max(axis=1) == 0
    assert np.allclose(oracle[outside], 0.0)
