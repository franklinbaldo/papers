import numpy as np
import pytest

from semantic_atlas.compiled import (
    LocalLinearDynamics,
    LowRankLexicalMap,
    WeightJacobianOperator,
    topk_overlap,
)


def test_full_rank_lexical_map_reconstructs_output_head():
    rng = np.random.default_rng(12)
    weight = rng.normal(size=(9, 4))
    hidden = rng.normal(size=4)
    compiled = LowRankLexicalMap.from_output_head(weight, rank=4)
    expected = weight @ hidden
    actual = compiled.logits(hidden)
    np.testing.assert_allclose(actual, expected, atol=1e-10)


def test_topk_overlap_is_one_for_identical_logits():
    logits = np.array([0.1, 4.0, 2.0, -1.0, 3.0])
    assert topk_overlap(logits, logits.copy(), k=3) == 1.0


def test_empirical_local_linear_dynamics_recovers_affine_system():
    rng = np.random.default_rng(5)
    states = rng.normal(size=(300, 3))
    matrix = np.array([[0.8, 0.1, 0.0], [0.0, 0.9, 0.1], [0.1, 0.0, 0.7]])
    bias = np.array([0.2, -0.1, 0.05])
    next_states = states @ matrix.T + bias
    model = LocalLinearDynamics.fit(states, next_states, ridge=1e-10)
    np.testing.assert_allclose(model.step(states[0]), next_states[0], atol=1e-8)


def test_jump_matches_repeated_empirical_step():
    dynamics = LocalLinearDynamics(matrix=np.array([[0.5]]), bias=np.array([1.0]))
    state = np.array([0.0])
    manual = dynamics.step(dynamics.step(dynamics.step(state)))
    np.testing.assert_allclose(dynamics.jump(state, 3), manual)


def test_weight_jacobian_operator_predicts_local_affine_map_without_transition_pairs():
    anchor = np.array([0.3, -0.2, 0.5])
    matrix = np.array([[0.8, -0.1, 0.2], [0.0, 0.7, 0.4]])
    bias = np.array([0.2, -0.3])
    anchor_output = matrix @ anchor + bias
    operator = WeightJacobianOperator.from_linearization(anchor, anchor_output, matrix)

    nearby = anchor + np.array([0.01, -0.02, 0.03])
    np.testing.assert_allclose(operator.predict(nearby), matrix @ nearby + bias, atol=1e-12)
    np.testing.assert_allclose(operator.jvp(np.ones(3)), matrix @ np.ones(3), atol=1e-12)


def test_torch_compiler_recovers_jacobian_of_differentiable_weight_map():
    torch = pytest.importorskip("torch")
    matrix = torch.tensor([[1.2, -0.4], [0.3, 0.8]], dtype=torch.float64)
    bias = torch.tensor([0.1, -0.2], dtype=torch.float64)

    def transition(x):
        return matrix @ x + bias

    anchor = torch.tensor([0.5, -0.7], dtype=torch.float64)
    operator = WeightJacobianOperator.from_torch_transition(transition, anchor)
    np.testing.assert_allclose(operator.jacobian, matrix.numpy(), atol=1e-12)
