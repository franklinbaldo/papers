"""Tests for Run 1: multi-tag frozen-state decoding.

The evaluation is bracketed against both ends. A probe handed the masks must score
perfectly, and a probe handed noise must fall to chance; anything that passes one
and fails the other would let a broken decoder look like a result.
"""

import numpy as np
import pytest

from malecns_wifi.multitag import (
    MultitagSpec,
    build_flavours,
    decode,
    evaluate,
    food_targets,
    interpolate,
    reservoir_states,
)

DOCUMENTS, CHUNKS, TAGS, DIMENSION = 8, 12, 4, 32


def _corpus(seed: int = 0):
    rng = np.random.default_rng(seed)
    masks = np.zeros((DOCUMENTS * CHUNKS, TAGS), dtype=np.float32)
    groups = np.repeat(np.arange(DOCUMENTS), CHUNKS)
    for document in range(DOCUMENTS):
        for tag in range(TAGS):
            start = 2 + tag * 2 + (document % 2)
            masks[document * CHUNKS + start : document * CHUNKS + start + 2, tag] = 1.0
    embeddings = rng.normal(size=(TAGS, DIMENSION)).astype(np.float32)
    return masks, groups, embeddings, rng


def _spec() -> MultitagSpec:
    return MultitagSpec(seeds=(0,))


def test_flavours_are_unit_norm_for_both_sources() -> None:
    _, _, embeddings, _ = _corpus()
    for source in ("semantic", "random_codebook"):
        flavours = build_flavours(embeddings, _spec(), seed=0, source=source)
        assert flavours.shape == (TAGS, _spec().flavour_dimension)
        assert np.allclose(np.linalg.norm(flavours, axis=1), 1.0, atol=1e-5)


def test_unknown_flavour_source_is_refused() -> None:
    _, _, embeddings, _ = _corpus()
    with pytest.raises(ValueError, match="unknown flavour source"):
        build_flavours(embeddings, _spec(), seed=0, source="umami")


def test_food_is_zero_outside_every_span_and_decodes_back_to_the_tag() -> None:
    masks, _, embeddings, _ = _corpus()
    flavours = build_flavours(embeddings, _spec(), seed=0, source="semantic")
    targets = food_targets(masks, flavours)

    outside = masks.sum(axis=1) == 0
    assert np.allclose(targets[outside], 0.0)

    magnitude, predicted = decode(targets, flavours)
    inside = ~outside
    assert (magnitude[inside] > 0).all()
    assert (predicted[inside] == np.argmax(masks[inside], axis=1)).all()


def test_overlapping_tags_mix_rather_than_overwrite() -> None:
    """A chunk covered by two tags must taste of both."""
    flavours = build_flavours(
        np.eye(2, 8, dtype=np.float32), MultitagSpec(flavour_dimension=8), seed=0, source="random_codebook"
    )
    masks = np.asarray([[1.0, 1.0]], dtype=np.float32)
    mixed = food_targets(masks, flavours)[0]
    assert np.allclose(mixed, flavours[0] + flavours[1])


def test_evaluate_reaches_the_ceiling_when_the_features_are_the_masks() -> None:
    masks, groups, embeddings, _ = _corpus()
    flavours = build_flavours(embeddings, _spec(), seed=0, source="semantic")
    features = np.hstack([masks, np.zeros((len(masks), 2))]).astype(np.float64)
    scored = evaluate(features, masks, flavours, groups, penalties=(0.01, 1.0))
    assert scored["inside_auprc"] > 0.99
    assert scored["tag_accuracy_on_true_spans"] > 0.99


def test_evaluate_falls_to_chance_on_noise() -> None:
    masks, groups, embeddings, rng = _corpus()
    flavours = build_flavours(embeddings, _spec(), seed=0, source="semantic")
    noise = rng.normal(size=(len(masks), 8))
    scored = evaluate(noise, masks, flavours, groups, penalties=(0.01, 1.0))
    assert scored["inside_auprc"] < scored["random_auprc"] + 0.06
    assert scored["tag_accuracy_on_true_spans"] < scored["tag_chance"] + 0.15


def test_penalty_is_selected_inside_the_training_folds() -> None:
    """One penalty per held-out document, and never chosen on that document."""
    masks, groups, embeddings, rng = _corpus()
    flavours = build_flavours(embeddings, _spec(), seed=0, source="semantic")
    scored = evaluate(
        rng.normal(size=(len(masks), 6)), masks, flavours, groups, penalties=(0.01, 1.0, 100.0)
    )
    assert len(scored["penalties"]) == DOCUMENTS
    assert set(scored["penalties"]) <= {0.01, 1.0, 100.0}


def test_interpolation_keeps_chunk_endpoints_and_maps_owners() -> None:
    features = np.arange(6, dtype=np.float32)[:, None]
    path, owners = interpolate(features, 4)
    assert path.shape == (1 + 5 * 4, 1)
    assert owners[0] == 0 and owners[4] == 1
    # Every chunk's own value survives at the step it owns last.
    for chunk in range(6):
        last = np.flatnonzero(owners == chunk)[-1]
        assert path[last, 0] == pytest.approx(float(chunk), abs=1e-5)


def test_interpolation_rejects_a_zero_step_count() -> None:
    with pytest.raises(ValueError, match="steps_per_chunk"):
        interpolate(np.zeros((3, 2), dtype=np.float32), 0)


def test_reservoir_returns_one_state_per_chunk() -> None:
    import scipy.sparse as sp

    rng = np.random.default_rng(0)
    neurons = 50
    dense = rng.normal(size=(neurons, neurons)).astype(np.float32)
    dense[rng.random((neurons, neurons)) > 0.2] = 0.0
    operator = sp.csr_matrix(dense / max(float(np.abs(dense).sum(axis=1).max()), 1.0))

    sensation = rng.normal(size=(7, 5)).astype(np.float32)
    inputs, readout = np.arange(0, 10), np.arange(10, 18)
    states = reservoir_states(
        operator,
        sensation,
        input_weights=rng.normal(size=(inputs.size, 5)).astype(np.float32),
        readout_indices=readout,
        input_indices=inputs,
        spec=MultitagSpec(steps_per_chunk=3),
    )
    assert states.shape == (7, readout.size)
    assert np.isfinite(states).all()
    # The reservoir is driven: different chunks give different states.
    assert not np.allclose(states[0], states[-1])
