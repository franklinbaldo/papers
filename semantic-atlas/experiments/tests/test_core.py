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


def _invertible_mix(rng: np.random.Generator, dim: int) -> np.ndarray:
    left, _ = np.linalg.qr(rng.normal(size=(dim, dim)))
    right, _ = np.linalg.qr(rng.normal(size=(dim, dim)))
    scales = np.linspace(0.4, 2.0, dim)
    return left @ np.diag(scales) @ right


def test_shared_calibration_resolves_rotational_gauge_on_heldout_points():
    rng = np.random.default_rng(7)
    dim = 6
    latent_calibration = rng.normal(size=(256, dim))
    latent_heldout = rng.normal(size=(48, dim))

    mix_a = _invertible_mix(rng, dim)
    mix_b = _invertible_mix(rng, dim)
    bias_a = rng.normal(size=dim)
    bias_b = rng.normal(size=dim)

    calibration_a = latent_calibration @ mix_a + bias_a
    calibration_b = latent_calibration @ mix_b + bias_b
    heldout_a = latent_heldout @ mix_a + bias_a
    heldout_b = latent_heldout @ mix_b + bias_b

    reference, canonical_targets = QuasarFrame.reference(calibration_a, dim=dim)
    aligned = QuasarFrame.fit(calibration_b, canonical_targets=canonical_targets)

    np.testing.assert_allclose(
        aligned.canonical_vectors(heldout_b),
        reference.canonical_vectors(heldout_a),
        atol=1e-8,
    )
    np.testing.assert_allclose(
        aligned.coordinates(heldout_b),
        reference.coordinates(heldout_a),
        atol=1e-8,
    )


def test_correspondence_is_semantic_information_not_a_quasar_label():
    rng = np.random.default_rng(19)
    dim = 5
    latent_calibration = rng.normal(size=(192, dim))
    latent_heldout = rng.normal(size=(32, dim))
    mix_a = _invertible_mix(rng, dim)
    mix_b = _invertible_mix(rng, dim)

    reference, targets = QuasarFrame.reference(latent_calibration @ mix_a, dim=dim)
    correctly_aligned = QuasarFrame.fit(latent_calibration @ mix_b, targets)
    wrongly_aligned = QuasarFrame.fit(latent_calibration @ mix_b, targets[rng.permutation(len(targets))])

    expected = reference.canonical_vectors(latent_heldout @ mix_a)
    correct_error = np.mean(np.linalg.norm(correctly_aligned.canonical_vectors(latent_heldout @ mix_b) - expected, axis=1))
    wrong_error = np.mean(np.linalg.norm(wrongly_aligned.canonical_vectors(latent_heldout @ mix_b) - expected, axis=1))
    assert correct_error < 1e-7
    assert wrong_error > correct_error + 0.2


def test_quasar_coordinates_are_finite_and_normalized():
    rng = np.random.default_rng(23)
    calibration = rng.normal(size=(64, 12))
    frame, _ = QuasarFrame.reference(calibration, dim=6)
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
