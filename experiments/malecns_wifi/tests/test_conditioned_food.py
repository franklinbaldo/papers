"""Tests for mask-gated, tag-flavoured food."""

import numpy as np
import pytest

from malecns_wifi.semantic_food import conditioned_food, tag_flavour


def test_food_exists_only_inside_the_mask() -> None:
    mask = np.zeros(20, dtype=np.float32)
    mask[8:12] = 1.0
    food = conditioned_food(mask, np.asarray([1.0, -2.0, 0.5], dtype=np.float32))
    assert np.allclose(food[mask == 0], 0.0)
    assert np.abs(food[mask == 1]).sum() > 0


def test_flavour_is_constant_in_time_and_cannot_leak_position() -> None:
    """The tag colours the food; it must not be able to say where the food is."""
    mask = np.zeros(12, dtype=np.float32)
    mask[3:7] = 1.0
    food = conditioned_food(mask, np.asarray([1.0, 2.0, 3.0], dtype=np.float32))
    inside = food[mask == 1]
    directions = inside / np.linalg.norm(inside, axis=1, keepdims=True)
    assert np.allclose(directions, directions[0], atol=1e-6)


def test_every_tag_delivers_the_same_total_energy() -> None:
    """Otherwise a bigger embedding is just fed harder, wearing a semantic costume."""
    rng = np.random.default_rng(0)
    mask = np.zeros(20, dtype=np.float32)
    mask[5:9] = 1.0
    energies = []
    for scale in (0.1, 1.0, 9.0):
        flavour = tag_flavour(rng.normal(size=32).astype(np.float32) * scale, 7, seed=1)
        energies.append(float((conditioned_food(mask, flavour) ** 2).sum()))
    assert np.allclose(energies, energies[0], atol=1e-5)


def test_energy_is_also_matched_across_span_lengths() -> None:
    rng = np.random.default_rng(1)
    flavour = tag_flavour(rng.normal(size=32).astype(np.float32), 7, seed=2)
    energies = []
    for width in (2, 5, 11):
        mask = np.zeros(30, dtype=np.float32)
        mask[4 : 4 + width] = 1.0
        energies.append(float((conditioned_food(mask, flavour) ** 2).sum()))
    assert np.allclose(energies, energies[0], atol=1e-5)


def test_unnormalised_food_keeps_the_raw_scale() -> None:
    mask = np.ones(4, dtype=np.float32)
    flavour = np.asarray([3.0, 4.0], dtype=np.float32)
    food = conditioned_food(mask, flavour, normalise_energy=False)
    assert np.allclose(np.linalg.norm(food, axis=1), 5.0)


def test_contrast_flavour_lives_in_the_tag_space() -> None:
    rng = np.random.default_rng(2)
    tag = rng.normal(size=16).astype(np.float32)
    contrast = rng.normal(size=(9, 16)).astype(np.float32)
    assert tag_flavour(tag, 5, seed=0, contrast=contrast).shape == (5,)
    with pytest.raises(ValueError, match="tag's embedding space"):
        tag_flavour(tag, 5, seed=0, contrast=rng.normal(size=(9, 8)).astype(np.float32))


def test_different_tags_taste_different() -> None:
    rng = np.random.default_rng(3)
    mask = np.ones(6, dtype=np.float32)
    first = conditioned_food(mask, tag_flavour(rng.normal(size=32).astype(np.float32), 9, seed=1))
    second = conditioned_food(mask, tag_flavour(rng.normal(size=32).astype(np.float32), 9, seed=1))
    cosine = float(
        (first[0] @ second[0]) / (np.linalg.norm(first[0]) * np.linalg.norm(second[0]))
    )
    assert abs(cosine) < 0.9, "two random tags should not taste nearly identical"
