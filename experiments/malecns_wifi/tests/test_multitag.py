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
    states, drive_rms = reservoir_states(
        operator,
        sensation,
        input_weights=rng.normal(size=(inputs.size, 5)).astype(np.float32),
        readout_indices=readout,
        input_indices=inputs,
        spec=MultitagSpec(steps_per_chunk=3),
    )
    assert states.shape == (7, readout.size)
    assert np.isfinite(states).all()
    assert drive_rms > 0
    # The reservoir is driven: different chunks give different states.
    assert not np.allclose(states[0], states[-1])


def test_drive_energy_does_not_depend_on_representation_width() -> None:
    """Otherwise a wider representation is simply driven harder.

    With w ~ N(0, s^2/d) the drive RMS is s*||x||/sqrt(d), so a 1540-dimensional
    relation block would receive half the current a 384-dimensional embedding
    block does, and any difference between them would be partly a difference in
    drive strength.
    """
    import scipy.sparse as sp

    rng = np.random.default_rng(0)
    neurons = 60
    operator = sp.csr_matrix(np.zeros((neurons, neurons), dtype=np.float32))
    inputs, readout = np.arange(0, 30), np.arange(30, 40)

    measured = []
    for width in (16, 128, 512):
        sensation = rng.normal(size=(6, width)).astype(np.float32)
        _, drive_rms = reservoir_states(
            operator,
            sensation,
            input_weights=rng.normal(size=(inputs.size, width)).astype(np.float32),
            readout_indices=readout,
            input_indices=inputs,
            spec=MultitagSpec(steps_per_chunk=2),
        )
        measured.append(drive_rms)
    assert max(measured) / min(measured) < 1.2, measured


def test_unit_rows_normalises_each_sensation_vector() -> None:
    from malecns_wifi.multitag import unit_rows

    rng = np.random.default_rng(1)
    scaled = rng.normal(size=(5, 9)).astype(np.float32) * np.asarray([[0.01], [1], [10], [100], [1]])
    assert np.allclose(np.linalg.norm(unit_rows(scaled), axis=1), 1.0, atol=1e-5)


def test_changing_only_the_gain_produces_a_cache_miss() -> None:
    """The invariant that would otherwise fail silently and produce a wrong number.

    The cache key was once (operator, representation, seed), which omits gain. A
    gain sweep against that key reloads one gain's states and reports them as
    another's -- no error, no warning, a wrong result from machinery introduced
    for efficiency.
    """
    from malecns_wifi.multitag import run_fingerprint

    base = dict(operator="malecns", representation="rel", seed=0, leak=0.4, steps=4)
    assert run_fingerprint(**base, gain=0.95) != run_fingerprint(**base, gain=2.5)
    # Every other axis that changes the states must also change the key.
    assert run_fingerprint(**base, gain=0.95) != run_fingerprint(
        **{**base, "leak": 0.2}, gain=0.95
    )
    assert run_fingerprint(**base, gain=0.95) != run_fingerprint(
        **{**base, "steps": 8}, gain=0.95
    )
    assert run_fingerprint(**base, gain=0.95) != run_fingerprint(
        **{**base, "seed": 1}, gain=0.95
    )
    # And an identical configuration must hit.
    assert run_fingerprint(**base, gain=0.95) == run_fingerprint(**base, gain=0.95)


def test_changed_features_invalidate_the_cache() -> None:
    """A different corpus must not be served from an old run's states."""
    from malecns_wifi.multitag import array_fingerprint

    rng = np.random.default_rng(0)
    values = rng.normal(size=(20, 5)).astype(np.float32)
    assert array_fingerprint(values) == array_fingerprint(values.copy())
    changed = values.copy()
    changed[3, 2] += 0.001
    assert array_fingerprint(values) != array_fingerprint(changed)
    assert array_fingerprint(values) != array_fingerprint(values[:, :4])


def test_outer_document_labels_cannot_influence_its_own_selection() -> None:
    """The leakage the nested form exists to remove, tested at the boundary.

    Changing only the held-out document's labels must not change the (gain, ridge)
    chosen for that fold: the selection sees sixteen documents, and the
    seventeenth is not among them. The previous two-stage form failed this,
    because a gain picked over 80% of the corpus was then used to score documents
    inside that 80%.
    """
    from malecns_wifi.multitag import build_flavours, evaluate_nested

    masks, groups, embeddings, rng = _corpus()
    flavours = build_flavours(embeddings, _spec(), seed=0, source="semantic")
    states = {
        gain: np.hstack([masks * gain, rng.normal(size=(len(masks), 4))])
        for gain in (0.5, 1.0, 2.0)
    }

    first = evaluate_nested(states, masks, flavours, groups, penalties=(0.1, 1.0))
    held_out = "0"
    altered = masks.copy()
    rows = np.flatnonzero(groups == 0)
    altered[rows] = altered[rows][::-1]          # scramble only that document
    second = evaluate_nested(states, altered, flavours, groups, penalties=(0.1, 1.0))

    assert first["selected_by_fold"][held_out] == second["selected_by_fold"][held_out]


def test_nested_selection_may_choose_a_different_gain_per_fold() -> None:
    """A single gain for every fold is the signature of the leaky form."""
    from malecns_wifi.multitag import build_flavours, evaluate_nested

    masks, groups, embeddings, rng = _corpus()
    flavours = build_flavours(embeddings, _spec(), seed=0, source="semantic")
    states = {gain: rng.normal(size=(len(masks), 6)) for gain in (0.5, 1.0, 2.0)}
    result = evaluate_nested(states, masks, flavours, groups, penalties=(0.1, 1.0))
    assert len(result["selected_by_fold"]) == len(np.unique(groups))
    assert all(row["gain"] > 0 for row in result["selected_by_fold"].values())


def test_graph_content_change_at_the_same_path_is_a_cache_miss() -> None:
    """A recompiled graph.npz at the same path must not be served from cache."""
    from malecns_wifi.multitag import array_fingerprint, run_fingerprint

    rng = np.random.default_rng(0)
    original = rng.normal(size=(50,)).astype(np.float32)
    recompiled = original.copy()
    recompiled[7] += 1e-3
    base = dict(operator="malecns", seed=0, gain=0.95, leak=0.4, steps=4)
    assert run_fingerprint(**base, graph=array_fingerprint(original)) != run_fingerprint(
        **base, graph=array_fingerprint(recompiled)
    )


def test_a_different_readout_of_the_same_size_is_a_cache_miss() -> None:
    """readout=1314 is not an identity; which 1,314 neurons is."""
    from malecns_wifi.multitag import array_fingerprint, run_fingerprint

    first = np.arange(1314, dtype=np.float32)
    second = np.arange(1, 1315, dtype=np.float32)
    assert first.size == second.size
    base = dict(operator="malecns", seed=0, gain=0.95, leak=0.4, steps=4)
    assert run_fingerprint(**base, readout=array_fingerprint(first)) != run_fingerprint(
        **base, readout=array_fingerprint(second)
    )
