import numpy as np
import pytest

from malecns_wifi.semantic_food import (
    condition_on_tag,
    edge_targets,
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
    # The connectome sees small changes, not the whole chunk jump in one step.
    assert np.max(np.linalg.norm(trajectory.deltas[1:], axis=1)) < np.sqrt(2.0)


def test_tag_is_a_constant_semantic_query_not_a_class_id() -> None:
    trajectory = interpolate_semantic_chunks(
        np.asarray([[1.0, 0.0], [0.5, 0.5]], dtype=np.float32),
        steps_per_transition=2,
        normalise=False,
    )
    conditioned = condition_on_tag(trajectory, np.asarray([0.0, 2.0], dtype=np.float32))

    assert conditioned.shape[1] == 4
    # Tag is normalised and repeated at every recurrent step.
    assert np.allclose(conditioned[:, -2:], np.asarray([0.0, 1.0]))


def test_span_becomes_continuous_consumption_plus_start_and_end_edges() -> None:
    trajectory = interpolate_semantic_chunks(
        np.eye(4, dtype=np.float32), steps_per_transition=2, normalise=False
    )
    inside = span_mask_from_chunks(trajectory.chunk_index, [(1, 3)])
    start, end = edge_targets(inside)

    assert inside.sum() > 2, "interpolation should make the semantic region temporally extended"
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


def test_teacher_food_drive_only_exists_inside_gold_span() -> None:
    mask = np.asarray([0, 1, 1, 0], dtype=np.float32)
    food = np.asarray([1, 3])
    drive = teacher_food_drive(5, 4, food, mask, amplitude=2.0)

    assert np.allclose(drive[0], 0.0)
    assert np.allclose(drive[3], 0.0)
    assert np.allclose(drive[1, food], 2.0)
    assert np.allclose(drive[2, food], 2.0)
    assert np.count_nonzero(drive) == 4


def test_food_teacher_refuses_empty_population() -> None:
    with pytest.raises(ValueError, match="food population is empty"):
        matched_random_population(np.arange(5), np.asarray([], dtype=np.int64), seed=0)
