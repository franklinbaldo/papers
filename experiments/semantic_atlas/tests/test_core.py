import numpy as np

from semantic_atlas.atlas import SemanticAtlas
from semantic_atlas.frame import QuasarFrame, regular_simplex
from semantic_atlas.trajectory import trajectory_metrics


def test_regular_simplex_has_expected_geometry():
    simplex = regular_simplex(4)
    assert simplex.shape == (5, 4)
    np.testing.assert_allclose(np.linalg.norm(simplex, axis=1), 1.0, atol=1e-10)
    gram = simplex @ simplex.T
    off_diagonal = gram[~np.eye(5, dtype=bool)]
    np.testing.assert_allclose(off_diagonal, -0.25, atol=1e-10)


def test_quasar_coordinates_are_finite_and_normalized():
    rng = np.random.default_rng(7)
    calibration = rng.normal(size=(64, 12))
    frame = QuasarFrame.fit(calibration, dim=6)
    points = rng.normal(size=(8, 12))
    canonical = frame.canonical_vectors(points)
    coordinates = frame.coordinates(points)
    assert coordinates.shape == (8, 7)
    assert np.isfinite(coordinates).all()
    np.testing.assert_allclose(np.linalg.norm(canonical, axis=1), 1.0, atol=1e-10)


def test_trajectory_metrics_reward_straight_paths():
    straight = np.array([[0.0, 0.0], [1.0, 0.0], [2.0, 0.0]])
    bent = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0]])
    assert trajectory_metrics(straight)["straightness"] > trajectory_metrics(bent)["straightness"]
    assert trajectory_metrics(straight)["mean_turning_angle"] < trajectory_metrics(bent)["mean_turning_angle"]


def test_atlas_observes_directed_path_and_routes():
    atlas = SemanticAtlas(np.array([[0.0, 0.0], [1.0, 0.0], [2.0, 0.0]]))
    atlas.observe_path(np.array([[0.0, 0.0], [1.0, 0.0], [2.0, 0.0]]))
    cost, path = atlas.shortest_path(0, 2)
    assert path == [0, 1, 2]
    assert cost > 0
    assert atlas.cells[1].count == 1
