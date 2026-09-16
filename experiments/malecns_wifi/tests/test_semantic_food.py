import numpy as np
import pytest

from malecns_wifi.semantic_food import (
    condition_on_tag,
    counterfactual_tag_food,
    edge_targets,
    food_population_drive,
    interpolate_semantic_chunks,
    matched_random_population,
    span_mask_from_chunks,
    teacher_food_drive,
)


def test_interpolation_preserves_real_checkpoints_and_exposes_small_deltas() -> None:
    embeddings = np.asarray([[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0]], dtype=np.float32)
    trajectory = interpolate_semantic_chunks(
        embeddings, steps_per_transition=4, normalise=False
    )

    assert trajectory.states.shape == (9, 2)
    assert np.allclose(trajectory.states[0], embeddings[0])
    assert np.allclose(trajectory.states[4], embeddings[1])
    assert np.allclose(trajectory.states[-1], embeddings[2])
    assert np.allclose(trajectory.deltas[0], 0.0)
    assert np.allclose(trajectory.deltas[1:].sum(axis=0), embeddings[-1] - embeddings[0])
    assert np.max(np.linalg.norm(trajectory.deltas[1:], axis=1)) < np.sqrt(2.0)


def test_tag_is_a_constant_semantic_query_not_a_class_id() -> None:
    trajectory = interpolate_semantic_chunks(
        np.asarray([[1.0, 0.0], [0.5, 0.5]], dtype=np.float32),
        steps_per_transition=2,
        normalise=False,
    )
    conditioned = condition_on_tag(trajectory, np.asarray([0.0, 2.0], dtype=np.float32))

    assert conditioned.shape[1] == 4
    assert np.allclose(conditioned[:, -2:], np.asarray([0.0, 1.0]))


def test_counterfactual_food_is_exact_semantic_displacement() -> None:
    base = np.asarray([[1.0, 0.0], [1.0, 1.0]], dtype=np.float32)
    tagged = np.asarray([[1.0, 0.0], [3.0, 1.0]], dtype=np.float32)
    food = counterfactual_tag_food(
        base, tagged, steps_per_transition=1, normalise=False
    )

    assert np.allclose(food.difference[0], [0.0, 0.0])
    assert np.allclose(food.difference[1], [2.0, 0.0])
    assert food.intensity.tolist() == pytest.approx([0.0, 2.0])
    assert np.allclose(food.direction[0], 0.0)
    assert np.allclose(food.direction[1], [1.0, 0.0])
    assert np.allclose(food.deltas[1], [2.0, 0.0])


def test_identical_with_and_without_tag_means_no_food() -> None:
    embeddings = np.asarray([[1.0, 2.0], [2.0, 3.0]], dtype=np.float32)
    food = counterfactual_tag_food(
        embeddings, embeddings.copy(), steps_per_transition=3, normalise=False
    )
    indices, drive = food_population_drive(food, np.asarray([2, 4, 6]), seed=5)

    assert indices.tolist() == [2, 4, 6]
    assert np.allclose(food.intensity, 0.0)
    assert np.allclose(drive, 0.0)


def test_food_population_encodes_flavour_but_preserves_total_amount() -> None:
    base = np.zeros((3, 4), dtype=np.float32)
    tagged = np.asarray(
        [[1.0, 0.0, 0.0, 0.0], [0.0, 2.0, 0.0, 0.0], [0.0, 0.0, 3.0, 0.0]],
        dtype=np.float32,
    )
    signal = counterfactual_tag_food(
        base, tagged, steps_per_transition=1, normalise=False
    )
    _, drive = food_population_drive(
        signal, np.asarray([1, 3, 5, 7]), seed=11, amplitude=2.0
    )

    assert np.all(drive >= 0.0)
    assert drive.sum(axis=1) == pytest.approx(2.0 * signal.intensity)
    # Different semantic directions should produce different population flavours.
    assert not np.allclose(drive[0] / drive[0].sum(), drive[1] / drive[1].sum())
    assert not np.allclose(drive[1] / drive[1].sum(), drive[2] / drive[2].sum())


def test_food_population_projection_is_seeded_and_reproducible() -> None:
    base = np.zeros((1, 3), dtype=np.float32)
    tagged = np.asarray([[1.0, 2.0, 3.0]], dtype=np.float32)
    signal = counterfactual_tag_food(base, tagged, normalise=False)
    food = np.asarray([0, 2, 4, 6])

    _, first = food_population_drive(signal, food, seed=9)
    _, repeat = food_population_drive(signal, food, seed=9)
    _, other = food_population_drive(signal, food, seed=10)

    assert np.allclose(first, repeat)
    assert not np.allclose(first, other)


def test_span_becomes_continuous_consumption_plus_start_and_end_edges() -> None:
    trajectory = interpolate_semantic_chunks(
        np.eye(4, dtype=np.float32), steps_per_transition=2, normalise=False
    )
    inside = span_mask_from_chunks(trajectory.chunk_index, [(1, 3)])
    start, end = edge_targets(inside)

    assert inside.sum() > 2
    assert start.sum() == 1
    assert end.sum() == 1
    assert np.argmax(start) < np.argmax(end)


def test_random_food_control_matches_population_size_and_excludes_real_food() -> None:
    sensory = np.arange(20)
    food = np.asarray([2, 4, 6, 8])
    control = matched_random_population(sensory, food, seed=7)

    assert len(control) == len(food)
    assert not set(control) & set(food)
    assert np.array_equal(control, matched_random_population(sensory, food, seed=7))


def test_gold_span_food_pulse_remains_only_as_teacher_ablation() -> None:
    mask = np.asarray([0, 1, 1, 0], dtype=np.float32)
    food = np.asarray([1, 3])
    drive = teacher_food_drive(5, 4, food, mask, amplitude=2.0)

    assert np.allclose(drive[0], 0.0)
    assert np.allclose(drive[3], 0.0)
    assert np.allclose(drive[1, food], 2.0)
    assert np.allclose(drive[2, food], 2.0)
    assert np.count_nonzero(drive) == 4


def test_food_helpers_refuse_empty_population() -> None:
    with pytest.raises(ValueError, match="food population is empty"):
        matched_random_population(np.arange(5), np.asarray([], dtype=np.int64), seed=0)

    signal = counterfactual_tag_food(
        np.asarray([[0.0, 0.0]], dtype=np.float32),
        np.asarray([[1.0, 0.0]], dtype=np.float32),
        normalise=False,
    )
    with pytest.raises(ValueError, match="food population is empty"):
        food_population_drive(signal, np.asarray([], dtype=np.int64))
