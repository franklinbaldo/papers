import numpy as np

from semantic_atlas.mpc import (
    Candidate,
    KNNManifoldPenalty,
    MPCWeights,
    Route,
    SemanticMPC,
    choose_candidate,
)


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


def test_route_targets_waypoint_before_final_goal_and_commits_only_prefix():
    def propose(prefix: str, count: int):
        assert count == 2
        return [
            ("via bridge then continue", -1.0),
            ("jump straight to final", -1.0),
        ]

    def trace(prefix: str, continuation: str):
        if continuation == "via bridge then continue":
            return np.array([[0.0, 0.0], [1.0, 0.0]])
        if continuation == "via bridge":
            return np.array([[0.0, 0.0], [1.0, 0.0]])
        return np.array([[0.0, 0.0], [2.0, 1.0]])

    route = Route(np.array([[1.0, 0.0], [2.0, 1.0]]), tolerance=0.1)
    controller = SemanticMPC(
        propose=propose,
        trace=trace,
        route=route,
        off_manifold=lambda path: 0.0,
        commit_tokens=2,
        weights=MPCWeights(curvature=0.0, off_manifold=0.0, logprob=0.0, path_length=0.0),
    )
    text, diagnostics = controller.step("origin", candidates=2)
    assert text == "via bridge"
    assert diagnostics["chosen_full_text"] == "via bridge then continue"
    assert diagnostics["waypoint_index_before"] == 0
    assert diagnostics["waypoint_index_after"] == 1


def test_manifold_penalty_makes_registered_ablation_a_real_condition():
    reference = np.array([[0.0, 0.0], [0.5, 0.0], [1.0, 0.0]])
    estimator = KNNManifoldPenalty(reference_points=reference)
    on_manifold = Candidate(
        "supported",
        np.array([[0.0, 0.0], [0.5, 0.0], [1.0, 0.0]]),
        off_manifold_penalty=estimator(np.array([[0.0, 0.0], [0.5, 0.0], [1.0, 0.0]])),
    )
    off_manifold = Candidate(
        "shortcut",
        np.array([[0.0, 0.0], [0.5, 3.0], [1.0, 0.0]]),
        off_manifold_penalty=estimator(np.array([[0.0, 0.0], [0.5, 3.0], [1.0, 0.0]])),
    )
    goal = np.array([1.0, 0.0])

    with_penalty, _ = choose_candidate(
        [off_manifold, on_manifold],
        goal,
        MPCWeights(progress=1.0, curvature=0.0, off_manifold=2.0, logprob=0.0, path_length=0.0),
    )
    without_penalty, _ = choose_candidate(
        [off_manifold, on_manifold],
        goal,
        MPCWeights(progress=1.0, curvature=0.0, off_manifold=0.0, logprob=0.0, path_length=0.0),
    )
    assert with_penalty.text == "supported"
    assert without_penalty.text == "shortcut"
    assert off_manifold.off_manifold_penalty > on_manifold.off_manifold_penalty


def test_semantic_mpc_reports_explicit_manifold_costs():
    def propose(prefix: str, count: int):
        return [("left", -1.0), ("right", -1.0)]

    def trace(prefix: str, continuation: str):
        endpoint = -1.0 if continuation == "left" else 1.0
        return np.array([[0.0, 0.0], [endpoint, 0.0]])

    controller = SemanticMPC(
        propose=propose,
        trace=trace,
        route=Route(np.array([[2.0, 0.0]])),
        off_manifold=KNNManifoldPenalty(np.array([[0.0, 0.0], [1.0, 0.0]])),
        commit_tokens=1,
    )
    text, diagnostics = controller.step("origin", candidates=2)
    assert text == "right"
    assert diagnostics["candidate_count"] == 2
    assert len(diagnostics["candidate_off_manifold_penalties"]) == 2
