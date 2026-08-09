import numpy as np

from semantic_atlas.mpc import Candidate, MPCWeights, SemanticMPC, choose_candidate


def test_choose_candidate_prefers_progress_with_equal_other_costs():
    goal = np.array([2.0, 0.0])
    candidates = [
        Candidate("away", np.array([[0.0, 0.0], [-1.0, 0.0]])),
        Candidate("toward", np.array([[0.0, 0.0], [1.0, 0.0]])),
    ]
    chosen, scores = choose_candidate(candidates, goal, MPCWeights())
    assert chosen.text == "toward"
    assert scores[1] > scores[0]


def test_curvature_penalty_breaks_equal_progress_tie():
    goal = np.array([2.0, 0.0])
    straight = Candidate("straight", np.array([[0.0, 0.0], [0.5, 0.0], [1.0, 0.0]]))
    bent = Candidate("bent", np.array([[0.0, 0.0], [0.5, 0.5], [1.0, 0.0]]))
    chosen, _ = choose_candidate(
        [bent, straight],
        goal,
        MPCWeights(progress=1.0, curvature=1.0, path_length=0.0, logprob=0.0),
    )
    assert chosen.text == "straight"


def test_semantic_mpc_is_backend_agnostic():
    def propose(prefix: str, count: int):
        assert count == 2
        return [("left", -1.0), ("right", -1.0)]

    def trace(prefix: str, continuation: str):
        endpoint = -1.0 if continuation == "left" else 1.0
        return np.array([[0.0, 0.0], [endpoint, 0.0]])

    controller = SemanticMPC(propose=propose, trace=trace)
    text, diagnostics = controller.step("origin", goal=np.array([2.0, 0.0]), candidates=2)
    assert text == "right"
    assert diagnostics["candidate_count"] == 2
