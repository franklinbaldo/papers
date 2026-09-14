"""Tests for conditional channel utility and the gated mixer.

The synthetic pyramid is built so the answer is known: three correlated coarse
channels that carry nothing about the boundary, and one fine channel that carries
it exactly. A measure that cannot find the fine channel, or that credits the
coarse ones, is broken.
"""

import numpy as np
import pytest

from malecns_wifi.channel_utility import (
    Channel,
    channel_utility,
    fit_channel_gates,
    mix_channels,
    softmax_simplex,
)

DOCUMENTS, PER_DOCUMENT = 12, 20


def _pyramid(seed: int = 0):
    rng = np.random.default_rng(seed)
    total = DOCUMENTS * PER_DOCUMENT
    groups = np.repeat(np.arange(DOCUMENTS), PER_DOCUMENT)
    labels = np.zeros(total, dtype=bool)
    for document in range(DOCUMENTS):
        labels[document * PER_DOCUMENT + 7 + (document % 3)] = True

    # Three coarse channels sharing one latent block: mutually redundant, and
    # none of them informative about the boundary.
    shared = rng.normal(size=(total, 6))
    coarse = [
        Channel(f"c{scale}", shared + 0.1 * rng.normal(size=(total, 6)), "A", scale, parent)
        for scale, parent in ((1024, None), (512, 1024), (256, 512))
    ]
    fine = Channel(
        "c16", np.hstack([labels[:, None] * 2.0, rng.normal(size=(total, 5))]), "B", 16, 64
    )
    return coarse + [fine], labels, groups


def test_the_informative_fine_channel_is_found_by_every_measure() -> None:
    channels, labels, groups = _pyramid()
    utility = channel_utility(channels, labels, groups, order=[c.name for c in channels])

    assert utility["singleton"]["c16"] > 0.9
    assert utility["leave_one_out"]["c16"] > 0.5
    assert utility["add_one"]["c16"] > 0.5
    assert utility["bank_auprc"] > 0.9


def test_uninformative_coarse_channels_are_not_credited() -> None:
    channels, labels, groups = _pyramid()
    utility = channel_utility(channels, labels, groups, order=[c.name for c in channels])
    for name in ("c1024", "c512", "c256"):
        assert utility["singleton"][name] < 0.2
        assert utility["leave_one_out"][name] < 0.1


def test_leave_one_out_understates_grouped_importance_under_collinearity() -> None:
    """The caveat the report has to carry, demonstrated rather than asserted.

    Three mutually redundant channels are each individually removable, so every
    leave-one-out delta is near zero even though the first of them added a real
    amount to an empty bank. A reader taking leave-one-out alone would conclude
    all three are worthless; add-one shows the first is not.
    """
    channels, labels, groups = _pyramid()
    utility = channel_utility(channels, labels, groups, order=[c.name for c in channels])

    individually_removable = max(
        abs(utility["leave_one_out"][name]) for name in ("c1024", "c512", "c256")
    )
    first_added = utility["add_one"]["c1024"]
    assert individually_removable < 0.1
    assert first_added > individually_removable


def test_alpha_stays_on_the_simplex() -> None:
    weights = softmax_simplex(np.asarray([0.0, 1.0, -3.0, 2.5]))
    assert weights.min() >= 0
    assert float(weights.sum()) == pytest.approx(1.0)


def test_mixer_holds_energy_constant_regardless_of_channel_count() -> None:
    """Nine channels must not shout louder than two."""
    channels, _, _ = _pyramid()
    rng = np.random.default_rng(1)
    projections = {c.name: rng.normal(size=(40, c.values.shape[1])).astype(np.float32)
                   for c in channels}
    realised = []
    for count in (2, 3, 4):
        subset = channels[:count]
        alpha = np.full(count, 1.0 / count)
        _, report = mix_channels(subset, projections, alpha, target_rms=0.05)
        realised.append(report["realised_rms"])
    assert np.allclose(realised, 0.05, atol=1e-6), realised


def test_mixer_refuses_weights_off_the_simplex() -> None:
    channels, _, _ = _pyramid()
    rng = np.random.default_rng(2)
    projections = {c.name: rng.normal(size=(30, c.values.shape[1])).astype(np.float32)
                   for c in channels}
    with pytest.raises(ValueError, match="sum to one"):
        mix_channels(channels, projections, np.ones(len(channels)))


def test_gates_have_one_parameter_per_channel_and_cannot_tag() -> None:
    """The mixer's whole safety argument is its parameter count."""
    channels, labels, groups = _pyramid()
    alpha = fit_channel_gates(channels, labels, groups, steps=25, seed=0)
    assert alpha.size == len(channels)
    assert alpha.min() >= 0 and float(alpha.sum()) == pytest.approx(1.0)

    rng = np.random.default_rng(3)
    projections = {c.name: rng.normal(size=(40, c.values.shape[1])).astype(np.float32)
                   for c in channels}
    _, report = mix_channels(channels, projections, alpha)
    # Four numbers, shared across every document, position and tag.
    assert report["parameters"] == len(channels)


def test_gates_favour_the_informative_channel() -> None:
    channels, labels, groups = _pyramid()
    alpha = fit_channel_gates(channels, labels, groups, steps=80, seed=1)
    fine = [c.name for c in channels].index("c16")
    assert alpha[fine] == pytest.approx(max(alpha)), alpha


def test_pyramid_is_scale_first_and_emits_both_sensor_types() -> None:
    """A relation is one sensor a scale can provide, not the pyramid's definition.

    Defining the pyramid as child/parent relations silently forbids the
    comparison that matters: what each *scale* contributes, independent of how it
    is sensed.
    """
    from malecns_wifi.channel_utility import pyramid_channels

    rng = np.random.default_rng(0)
    levels = {scale: rng.normal(size=(60, 8)).astype(np.float32) for scale in (256, 64, 16)}
    channels = pyramid_channels(levels, encoder="A", parents={64: 256, 16: 64})

    assert [c.name for c in channels] == [
        "A:abs256", "A:abs64", "A:rel64|256", "A:abs16", "A:rel16|64",
    ]
    # The top level has no parent, so it contributes an absolute sensor only.
    assert not channels[0].is_relational
    assert {c.scale for c in channels} == {256, 64, 16}
    # Both sensor types are available at every level that has a parent.
    for scale in (64, 16):
        kinds = {c.is_relational for c in channels if c.scale == scale}
        assert kinds == {True, False}

    only_absolute = pyramid_channels(
        levels, encoder="A", parents={64: 256, 16: 64}, include_relational=False
    )
    assert all(not c.is_relational for c in only_absolute)


def test_specialisation_matrix_is_flat_when_channels_measure_the_same_thing() -> None:
    """The falsifying shape for the retina claim, made measurable.

    If every channel is equally useful for every tag, the field is one sensor at
    several volumes rather than several sensors. That should not be reported as a
    retina even where the bank works.
    """
    from malecns_wifi.channel_utility import Channel, per_tag_channel_utility

    rng = np.random.default_rng(0)
    documents, per_document, tags = 10, 20, 3
    total = documents * per_document
    groups = np.repeat(np.arange(documents), per_document)
    masks = np.zeros((total, tags), dtype=np.float32)
    for document in range(documents):
        for tag in range(tags):
            masks[document * per_document + 3 + tag * 4, tag] = 1.0

    # Specialised: each channel carries exactly one tag.
    specialised = [
        Channel(f"s{tag}", np.hstack([masks[:, [tag]] * 3.0, rng.normal(size=(total, 3))]),
                "A", 16 << tag, None)
        for tag in range(tags)
    ]
    # Flat: every channel carries the union, so none distinguishes the tags.
    union = masks.max(axis=1, keepdims=True)
    flat = [
        Channel(f"f{index}", np.hstack([union * 3.0, rng.normal(size=(total, 3))]),
                "A", 16 << index, None)
        for index in range(tags)
    ]

    names = [f"tag{index}" for index in range(tags)]
    sharp = per_tag_channel_utility(specialised, masks, names, groups)
    blunt = per_tag_channel_utility(flat, masks, names, groups)

    sharp_spread = np.nanmean(list(sharp["specialisation_spread"].values()))
    blunt_spread = np.nanmean(list(blunt["specialisation_spread"].values()))
    assert sharp_spread > blunt_spread, (sharp_spread, blunt_spread)
