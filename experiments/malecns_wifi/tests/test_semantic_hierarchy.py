import numpy as np

from malecns_wifi.semantic_hierarchy import (
    interpolate_relations,
    multiscale_relations,
    multiscale_semantic_trajectory,
    parent_relation,
)


def test_parent_relation_separates_alignment_and_residual() -> None:
    child = np.asarray([[1.0, 0.0], [1.0, 1.0]], dtype=np.float32)
    parent = np.asarray([[1.0, 0.0], [1.0, 0.0]], dtype=np.float32)
    relation = parent_relation(child, parent)

    assert relation.vector.shape == (2, 3)
    assert relation.alignment[0] == 1.0
    assert np.allclose(relation.residual[0], 0.0)
    # The second child shares the parent's x direction but contributes y context.
    assert 0.0 < relation.alignment[1] < 1.0
    assert relation.residual[1, 1] > 0.0


def test_relation_geometry_is_rotation_equivariant_and_alignment_invariant() -> None:
    child = np.asarray([[1.0, 2.0], [-1.0, 1.0]], dtype=np.float32)
    parent = np.asarray([[2.0, 1.0], [1.0, 1.0]], dtype=np.float32)
    rotation = np.asarray([[0.0, -1.0], [1.0, 0.0]], dtype=np.float32)

    original = parent_relation(child, parent)
    rotated = parent_relation(child @ rotation.T, parent @ rotation.T)

    assert np.allclose(original.alignment, rotated.alignment, atol=1e-6)
    assert np.allclose(original.residual @ rotation.T, rotated.residual, atol=1e-6)


def test_multiscale_relations_keep_local_and_global_context_separate() -> None:
    fine = np.asarray([[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0], [0.0, -1.0]], dtype=np.float32)
    medium = np.asarray([[1.0, 1.0], [1.0, 1.0], [-1.0, -1.0], [-1.0, -1.0]], dtype=np.float32)
    global_parent = np.asarray([[1.0, 0.5]] * 4, dtype=np.float32)

    relations, slices = multiscale_relations(fine, [medium, global_parent])

    assert relations.shape == (4, 6)
    assert slices == ((0, 3), (3, 6))
    assert not np.allclose(relations[:, slices[0][0]:slices[0][1]], relations[:, slices[1][0]:slices[1][1]])


def test_interpolation_is_between_adjacent_relation_vectors() -> None:
    relations = np.asarray([[0.0, 0.0], [2.0, 4.0], [4.0, 0.0]], dtype=np.float32)
    trajectory = interpolate_relations(relations, steps_per_transition=2)

    assert trajectory.states.shape == (5, 2)
    assert np.allclose(trajectory.states[0], relations[0])
    assert np.allclose(trajectory.states[2], relations[1])
    assert np.allclose(trajectory.states[-1], relations[2])
    assert np.allclose(trajectory.states[1], [1.0, 2.0])
    assert np.allclose(trajectory.states[3], [3.0, 2.0])
    assert trajectory.chunk_index.tolist() == [0, 1, 1, 2, 2]


def test_parent_boundary_changes_only_when_adjacent_chunk_relation_changes() -> None:
    fine = np.asarray([[1.0, 0.0], [1.0, 0.0], [1.0, 0.0]], dtype=np.float32)
    parents = np.asarray([[1.0, 0.0], [1.0, 0.0], [0.0, 1.0]], dtype=np.float32)

    trajectory = multiscale_semantic_trajectory(fine, [parents], steps_per_transition=2)

    # First two chunks have identical child/parent relation: their interpolated segment is flat.
    assert np.allclose(trajectory.states[0], trajectory.states[1])
    assert np.allclose(trajectory.states[1], trajectory.states[2])
    # Crossing into a new parent changes the relation and therefore the signal.
    assert not np.allclose(trajectory.states[2], trajectory.states[-1])
