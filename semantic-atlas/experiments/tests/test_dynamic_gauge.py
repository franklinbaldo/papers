import numpy as np

from semantic_atlas.dynamic_gauge import (
    FrozenFieldSpec,
    compression_report,
    effective_rank,
    evaluate_field,
    fit_amplitude,
    paired_concordance,
    residuals,
)
from semantic_atlas.frame import regular_simplex


def _synthetic_states(n: int = 96, dim: int = 6) -> np.ndarray:
    rng = np.random.default_rng(44)
    states = rng.normal(size=(n, dim))
    states /= np.maximum(np.linalg.norm(states, axis=1, keepdims=True), 1e-12)
    return states


def test_frozen_field_is_deterministic_and_fingerprinted():
    states = _synthetic_states()
    centers = regular_simplex(states.shape[1])
    spec = FrozenFieldSpec("random_divergence_free", dim=states.shape[1], seed=19)
    other = FrozenFieldSpec("random_divergence_free", dim=states.shape[1], seed=20)

    first = evaluate_field(states, centers, spec)
    second = evaluate_field(states, centers, spec)
    changed = evaluate_field(states, centers, other)

    assert np.allclose(first, second)
    assert not np.allclose(first, changed)
    assert spec.fingerprint == FrozenFieldSpec(
        "random_divergence_free", dim=states.shape[1], seed=19
    ).fingerprint
    assert spec.fingerprint != other.fingerprint


def test_constant_amplitude_recovers_known_shared_flow():
    states = _synthetic_states()
    centers = regular_simplex(states.shape[1])
    spec = FrozenFieldSpec("vortex_smooth", dim=states.shape[1], seed=7, scale=1.2)
    field = evaluate_field(states, centers, spec)
    rng = np.random.default_rng(8)
    noise = 0.01 * rng.normal(size=field.shape)
    dynamics = 2.75 * field + noise

    fit = fit_amplitude(states, dynamics, field, basis="constant", ridge=1e-10)
    remainder = residuals(states, dynamics, field, fit)

    assert fit.coefficients.shape == (1,)
    assert abs(float(fit.coefficients[0]) - 2.75) < 0.02
    assert np.mean(remainder**2) < np.mean(dynamics**2) * 0.01


def test_matching_gauge_compresses_better_than_wrong_field():
    states = _synthetic_states(n=120)
    centers = regular_simplex(states.shape[1])
    correct = FrozenFieldSpec("vortex_smooth", dim=states.shape[1], seed=5, scale=1.0)
    wrong = FrozenFieldSpec("radial_gradient", dim=states.shape[1], seed=5, scale=1.0)
    field = evaluate_field(states, centers, correct)
    rng = np.random.default_rng(99)
    # Deliberately low-rank residual so the correct gauge should expose it.
    direction = rng.normal(size=states.shape[1])
    direction /= np.linalg.norm(direction)
    coefficient = 0.03 * states[:, :1]
    low_rank_residual = coefficient * direction[None, :]
    dynamics = 1.8 * field + low_rank_residual

    train = slice(0, 80)
    test = slice(80, None)
    common = dict(
        train_states=states[train],
        train_dynamics=dynamics[train],
        test_states=states[test],
        test_dynamics=dynamics[test],
        centers=centers,
        amplitude_basis="constant",
        sample_fractions=(0.5, 1.0),
    )
    correct_report = compression_report(spec=correct, **common)
    wrong_report = compression_report(spec=wrong, **common)

    assert correct_report["test_energy_ratio"] < 0.02
    assert correct_report["test_energy_ratio"] < wrong_report["test_energy_ratio"]
    assert correct_report["test_effective_rank_ratio"] < 1.0


def test_zero_field_is_exact_un_gauged_baseline():
    states = _synthetic_states(n=72)
    centers = regular_simplex(states.shape[1])
    rng = np.random.default_rng(2)
    dynamics = rng.normal(size=states.shape)
    zero = FrozenFieldSpec("zero", dim=states.shape[1])

    report = compression_report(
        states[:48],
        dynamics[:48],
        states[48:],
        dynamics[48:],
        centers,
        zero,
        sample_fractions=(1.0,),
    )

    assert np.isclose(report["test_energy_ratio"], 1.0)
    assert np.isclose(report["test_effective_rank_ratio"], 1.0)
    assert np.allclose(report["test_residuals"], dynamics[48:])


def test_effective_rank_detects_low_rank_structure():
    rng = np.random.default_rng(13)
    latent = rng.normal(size=(200, 1))
    direction = rng.normal(size=(1, 8))
    low_rank = latent @ direction
    full = rng.normal(size=(200, 8))

    assert effective_rank(low_rank) < 1.01
    assert effective_rank(full) > 5.0


def test_paired_concordance_rewards_shared_residual_geometry():
    rng = np.random.default_rng(123)
    base = rng.normal(size=(64, 5))
    close = base + 0.01 * rng.normal(size=base.shape)
    unrelated = rng.normal(size=base.shape)

    shared = paired_concordance(base, close)
    random = paired_concordance(base, unrelated)

    assert shared["mean_row_cosine"] > random["mean_row_cosine"]
    assert shared["normalized_rmse"] < random["normalized_rmse"]
    assert shared["pairwise_distance_correlation"] > random["pairwise_distance_correlation"]
