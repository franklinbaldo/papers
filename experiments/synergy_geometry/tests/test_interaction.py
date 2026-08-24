import numpy as np
import pytest

from synergy_geometry import (
    MainEffectsInteractionEstimator,
    additive_control,
    balanced_factorial_decomposition,
    mixed_finite_difference,
    xor_control,
)


def test_gate0_additive_null_has_zero_interaction():
    h = additive_control(seed=7)
    dec = balanced_factorial_decomposition(h)

    np.testing.assert_allclose(dec.reconstruct(), h, atol=1e-12)
    np.testing.assert_allclose(dec.effect_a.mean(axis=0), 0.0, atol=1e-12)
    np.testing.assert_allclose(dec.effect_b.mean(axis=0), 0.0, atol=1e-12)
    np.testing.assert_allclose(dec.interaction, 0.0, atol=1e-12)
    np.testing.assert_allclose(
        mixed_finite_difference(h, 0, 1, 0, 1), 0.0, atol=1e-12
    )


def test_gate0_xor_positive_control_is_pure_joint_signal():
    h, labels = xor_control()
    dec = balanced_factorial_decomposition(h)

    np.testing.assert_allclose(dec.interaction[..., :2], 0.0, atol=1e-12)
    assert dec.interaction_rms > 0.5
    relation_sign = (dec.interaction[..., 2] > 0).astype(int)
    np.testing.assert_array_equal(relation_sign, labels)


def test_main_effect_estimator_scores_unseen_combinations_without_refitting():
    a_train = ["a0", "a0", "a1"]
    b_train = ["b0", "b1", "b0"]
    h_train = np.array([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0]])

    estimator = MainEffectsInteractionEstimator().fit(a_train, b_train, h_train)
    predicted = estimator.predict_main_effects(["a1"], ["b1"])
    np.testing.assert_allclose(predicted, [[1.0, 1.0]], atol=1e-12)

    observed_joint = np.array([[1.0, 3.0]])
    residual = estimator.interaction(["a1"], ["b1"], observed_joint)
    np.testing.assert_allclose(residual, [[0.0, 2.0]], atol=1e-12)


def test_main_effect_estimator_rejects_unseen_factor_identity():
    estimator = MainEffectsInteractionEstimator().fit(
        ["a0", "a0", "a1", "a1"],
        ["b0", "b1", "b0", "b1"],
        np.zeros((4, 2)),
    )
    with pytest.raises(ValueError, match="unseen factor identities"):
        estimator.predict_main_effects(["a2"], ["b0"])
