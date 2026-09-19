"""Tests for the frozen meal: amount gates, flavour carries the signed detail."""

import numpy as np
import pytest

from malecns_wifi.semantic_food import contrast_food_drive, intensity_polarity
from malecns_wifi.semantic_hierarchy import compose_meal, meal_direct_control_features
from malecns_wifi.semantic_hierarchy import interpolate_relations

from test_redundancy_differential import _corpus, CHUNKS, SCALES


def test_amount_gates_and_flavour_carries_both_parts() -> None:
    child, parents, child_tagged, parents_tagged, _, answer, section = _corpus()
    meal = compose_meal(child, child_tagged, parents, parents_tagged)

    assert meal.amount.shape == (CHUNKS,)
    start, end = meal.differential_slice
    assert end - start == SCALES
    assert meal.flavour.shape == (CHUNKS, end)
    # Relational contrasts occupy everything before the differential block.
    assert meal.scale_slices[-1][1] == start


def test_chunk_amount_gates_where_the_relational_one_does_not() -> None:
    """Amount must be low on irrelevant text, or the tap never closes."""
    child, parents, child_tagged, parents_tagged, _, answer, section = _corpus()
    by_chunk = compose_meal(child, child_tagged, parents, parents_tagged, amount_source="chunk")
    by_relation = compose_meal(
        child, child_tagged, parents, parents_tagged, amount_source="relational"
    )

    assert intensity_polarity(by_chunk.amount, answer)["point_biserial"] > 0.5
    assert by_chunk.amount[answer].mean() > by_chunk.amount[~section].mean()
    # The relational reading measures something else and does not gate here.
    assert intensity_polarity(by_relation.amount, answer)["point_biserial"] < 0.3


def test_differential_enters_signed_and_is_not_an_amount() -> None:
    """A may be negative; that must not reduce how much food there is."""
    child, parents, child_tagged, parents_tagged, *_ = _corpus()
    meal = compose_meal(child, child_tagged, parents, parents_tagged)
    start, end = meal.differential_slice
    block = meal.flavour[:, start:end]
    assert (block < 0).any(), "this corpus is expected to produce negative A"
    assert np.all(meal.amount > 0), "amount is independent of the sign of A"


def test_unknown_amount_source_is_refused() -> None:
    child, parents, child_tagged, parents_tagged, *_ = _corpus()
    with pytest.raises(ValueError, match="unknown amount_source"):
        compose_meal(child, child_tagged, parents, parents_tagged, amount_source="vibes")


def test_gustatory_projection_takes_a_meal_unchanged() -> None:
    child, parents, child_tagged, parents_tagged, *_ = _corpus()
    meal = compose_meal(child, child_tagged, parents, parents_tagged)
    drive = contrast_food_drive(meal, np.arange(15), seed=4)
    assert drive.shape == (CHUNKS, 15)
    # Flavour sets the direction, amount sets the magnitude.
    assert np.allclose(np.linalg.norm(drive, axis=1), np.abs(meal.amount), atol=1e-4)


def test_direct_control_receives_the_same_amount_and_flavour() -> None:
    child, parents, child_tagged, parents_tagged, *_ = _corpus()
    meal = compose_meal(child, child_tagged, parents, parents_tagged)
    trajectory = interpolate_relations(meal.flavour, steps_per_transition=1)
    features = meal_direct_control_features(trajectory, meal)

    width = meal.flavour.shape[1]
    assert features.shape == (CHUNKS, width + 1 + width + width)
    assert np.allclose(features[:, width], meal.amount, atol=1e-6)
    assert np.allclose(features[:, width + 1 : 2 * width + 1], meal.flavour, atol=1e-6)


def test_direct_control_rejects_a_mismatched_time_axis() -> None:
    child, parents, child_tagged, parents_tagged, *_ = _corpus()
    meal = compose_meal(child, child_tagged, parents, parents_tagged)
    trajectory = interpolate_relations(meal.flavour, steps_per_transition=3)
    with pytest.raises(ValueError, match="share the time axis"):
        meal_direct_control_features(trajectory, meal)
