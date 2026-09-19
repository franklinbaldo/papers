"""Tests for the unsupervised, contrast-derived food signal."""

import numpy as np
import pytest

from malecns_wifi.semantic_food import (
    contrast_food_drive,
    direct_control_features,
    intensity_polarity,
    interpolate_semantic_chunks,
    tag_contrast,
)

STEPS, DIMENSIONS = 40, 32


def _corpus(seed: int = 0):
    """A text whose meaning drifts into the tag's region and back out again.

    The pull toward the tag is proportional to the component of the tag that the
    text does *not* already have, which is the redundancy effect a real encoder is
    expected to show: appending a tag to text already about that tag changes
    little.
    """
    rng = np.random.default_rng(seed)
    tag = rng.normal(size=DIMENSIONS).astype(np.float32)
    tag /= np.linalg.norm(tag)

    base = rng.normal(size=(STEPS, DIMENSIONS)).astype(np.float32) * 0.4
    mask = np.zeros(STEPS, dtype=bool)
    mask[15:28] = True
    base[mask] += 2.0 * tag
    plain = base / np.linalg.norm(base, axis=1, keepdims=True)
    tagged = plain + 0.8 * (tag[None, :] - plain * (plain @ tag)[:, None])
    return plain, tagged, tag, mask


def test_contrast_shape_and_normalisation() -> None:
    plain, tagged, tag, _ = _corpus()
    contrast = tag_contrast(plain, tagged, tag)
    assert contrast.contrast.shape == (STEPS, DIMENSIONS)
    assert contrast.intensity.shape == (STEPS,)
    assert np.allclose(np.linalg.norm(contrast.plain, axis=1), 1.0, atol=1e-5)


def test_norm_and_alignment_intensities_are_inverted() -> None:
    """The redundancy effect: the contrast is *smallest* where the tag applies.

    This is the reason the intensity definition cannot be chosen by intuition.
    Feeding the fly on ``norm`` or ``alignment`` would starve it exactly over the
    region being looked for.
    """
    plain, tagged, tag, mask = _corpus()
    for mode in ("norm", "alignment"):
        polarity = intensity_polarity(tag_contrast(plain, tagged, tag, intensity=mode).intensity,
                                      mask)
        assert polarity["point_biserial"] < -0.5, f"{mode} was expected to be inverted"


def test_similarity_intensity_has_the_intended_polarity() -> None:
    plain, tagged, tag, mask = _corpus()
    polarity = intensity_polarity(
        tag_contrast(plain, tagged, tag, intensity="similarity").intensity, mask
    )
    assert polarity["point_biserial"] > 0.5
    assert polarity["separation"] > 0


def test_polarity_reports_degenerate_masks_rather_than_a_number() -> None:
    values = np.linspace(0, 1, 10)
    assert intensity_polarity(values, np.ones(10))["degenerate"]
    assert intensity_polarity(values, np.zeros(10))["degenerate"]


def test_flavour_is_a_pattern_not_a_scalar() -> None:
    """Different semantic directions must produce different taste patterns."""
    plain, tagged, tag, _ = _corpus()
    contrast = tag_contrast(plain, tagged, tag)
    drive = contrast_food_drive(contrast, np.arange(11), seed=1)
    assert drive.shape == (STEPS, 11)

    directions = drive / np.maximum(np.linalg.norm(drive, axis=1, keepdims=True), 1e-12)
    # If flavour were a scalar times a fixed pattern, every row would be parallel.
    similarity = directions @ directions[0]
    assert similarity.min() < 0.99


def test_amount_and_flavour_separate() -> None:
    """With separation on, the pattern norm is the intensity and nothing else."""
    plain, tagged, tag, _ = _corpus()
    contrast = tag_contrast(plain, tagged, tag, intensity="norm")
    drive = contrast_food_drive(contrast, np.arange(9), seed=3)
    assert np.allclose(np.linalg.norm(drive, axis=1), np.abs(contrast.intensity), atol=1e-4)

    raw = contrast_food_drive(
        contrast, np.arange(9), seed=3, separate_flavour_from_amount=False
    )
    assert not np.allclose(np.linalg.norm(raw, axis=1), np.abs(contrast.intensity), atol=1e-4)


def test_food_drive_rejects_an_empty_population() -> None:
    plain, tagged, tag, _ = _corpus()
    with pytest.raises(ValueError, match="food population is empty"):
        contrast_food_drive(tag_contrast(plain, tagged, tag), np.asarray([], dtype=np.int64), seed=0)


def test_direct_control_sees_everything_the_fly_sees() -> None:
    plain, tagged, tag, _ = _corpus()
    contrast = tag_contrast(plain, tagged, tag)
    trajectory = interpolate_semantic_chunks(plain, steps_per_transition=1)
    features = direct_control_features(trajectory, contrast)
    assert features.shape == (STEPS, 3 * DIMENSIONS)
    # E_t, F_t and dE_t are all present, in that order.
    assert np.allclose(features[:, :DIMENSIONS], trajectory.states, atol=1e-5)
    assert np.allclose(features[:, DIMENSIONS : 2 * DIMENSIONS], contrast.contrast, atol=1e-5)
    assert np.allclose(features[:, 2 * DIMENSIONS :], trajectory.deltas, atol=1e-5)


def test_direct_control_rejects_a_mismatched_time_axis() -> None:
    plain, tagged, tag, _ = _corpus()
    contrast = tag_contrast(plain, tagged, tag)
    trajectory = interpolate_semantic_chunks(plain, steps_per_transition=4)
    with pytest.raises(ValueError, match="share the time axis"):
        direct_control_features(trajectory, contrast)


def test_tag_must_live_in_the_text_space() -> None:
    plain, tagged, _, _ = _corpus()
    with pytest.raises(ValueError, match="same semantic space"):
        tag_contrast(plain, tagged, np.zeros(DIMENSIONS + 1, dtype=np.float32))


def test_unknown_intensity_mode_is_refused() -> None:
    plain, tagged, tag, _ = _corpus()
    with pytest.raises(ValueError, match="unknown intensity mode"):
        tag_contrast(plain, tagged, tag, intensity="tastiness")
