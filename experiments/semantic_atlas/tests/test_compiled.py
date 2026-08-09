import numpy as np

from semantic_atlas.compiled import LocalLinearDynamics, LowRankLexicalMap, topk_overlap


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


def test_local_linear_dynamics_recovers_affine_system():
    rng = np.random.default_rng(5)
    states = rng.normal(size=(300, 3))
    matrix = np.array([[0.8, 0.1, 0.0], [0.0, 0.9, 0.1], [0.1, 0.0, 0.7]])
    bias = np.array([0.2, -0.1, 0.05])
    next_states = states @ matrix.T + bias
    model = LocalLinearDynamics.fit(states, next_states, ridge=1e-10)
    np.testing.assert_allclose(model.step(states[0]), next_states[0], atol=1e-8)


def test_jump_matches_repeated_step():
    dynamics = LocalLinearDynamics(matrix=np.array([[0.5]]), bias=np.array([1.0]))
    state = np.array([0.0])
    manual = dynamics.step(dynamics.step(dynamics.step(state)))
    np.testing.assert_allclose(dynamics.jump(state, 3), manual)
