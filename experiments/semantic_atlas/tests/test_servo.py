import numpy as np

from semantic_atlas.servo import LinearFutureHead, SemanticServo


def test_future_head_recovers_linear_semantic_dynamics():
    rng = np.random.default_rng(42)
    hidden = rng.normal(size=(300, 6))
    true_weight = rng.normal(size=(3, 6))
    true_bias = rng.normal(size=3)
    delta = hidden @ true_weight.T + true_bias

    head = LinearFutureHead.fit(hidden[:250], delta[:250], ridge=1e-8)
    prediction = head.predict(hidden[250:])
    np.testing.assert_allclose(prediction, delta[250:], atol=1e-6)


def test_servo_reduces_linear_prediction_error():
    rng = np.random.default_rng(9)
    hidden = rng.normal(size=(200, 5))
    weight = rng.normal(size=(2, 5))
    delta = hidden @ weight.T
    head = LinearFutureHead.fit(hidden, delta, ridge=1e-8)

    state = hidden[0]
    desired = head.predict(state) + np.array([0.4, -0.2])
    correction, diagnostics = SemanticServo(head=head, regularization=1e-8).command(state, desired)

    assert np.linalg.norm(correction) > 0
    assert diagnostics["prediction_error_after_command"] < diagnostics["prediction_error_before"]


def test_servo_respects_control_norm_bound_after_gain():
    rng = np.random.default_rng(3)
    hidden = rng.normal(size=(100, 4))
    delta = hidden[:, :2]
    head = LinearFutureHead.fit(hidden, delta)
    command, diagnostics = SemanticServo(head=head, gain=10.0, max_norm=0.05).command(
        hidden[0], np.array([9.0, -9.0])
    )
    assert np.linalg.norm(command) <= 0.0500001
    assert diagnostics["preclip_command_norm"] > 0.05
    assert diagnostics["command_norm"] <= 0.0500001
    assert diagnostics["clipped"] == 1.0
