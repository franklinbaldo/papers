from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np

from .trajectory import trajectory_metrics


@dataclass(frozen=True)
class Candidate:
    text: str
    path: np.ndarray
    logprob: float = 0.0
    off_manifold_penalty: float = 0.0


@dataclass(frozen=True)
class MPCWeights:
    progress: float = 1.0
    curvature: float = 0.2
    off_manifold: float = 0.5
    logprob: float = 0.05
    path_length: float = 0.05


def score_candidate(candidate: Candidate, goal: np.ndarray, weights: MPCWeights) -> float:
    metrics = trajectory_metrics(candidate.path, goal=goal)
    return float(
        weights.progress * metrics["goal_progress"]
        - weights.curvature * metrics["mean_turning_angle"]
        - weights.off_manifold * candidate.off_manifold_penalty
        + weights.logprob * candidate.logprob
        - weights.path_length * metrics["path_length"]
    )


def choose_candidate(
    candidates: Sequence[Candidate],
    goal: np.ndarray,
    weights: MPCWeights = MPCWeights(),
) -> tuple[Candidate, list[float]]:
    if not candidates:
        raise ValueError("at least one candidate is required")
    scores = [score_candidate(candidate, goal, weights) for candidate in candidates]
    best = int(np.argmax(scores))
    return candidates[best], scores


class SemanticMPC:
    """Closed-loop semantic MPC over short generated continuations.

    The controller is intentionally backend-agnostic. `propose` generates candidate
    strings from the current text; `trace` maps each candidate to an SRF path. This
    makes it possible to test the controller with deterministic toy backends before
    downloading a language model.
    """

    def __init__(
        self,
        propose: Callable[[str, int], Sequence[tuple[str, float]]],
        trace: Callable[[str, str], np.ndarray],
        weights: MPCWeights = MPCWeights(),
    ) -> None:
        self.propose = propose
        self.trace = trace
        self.weights = weights

    def step(self, prefix: str, goal: np.ndarray, candidates: int = 8) -> tuple[str, dict]:
        proposals = self.propose(prefix, candidates)
        evaluated = [
            Candidate(text=text, logprob=logprob, path=self.trace(prefix, text))
            for text, logprob in proposals
        ]
        chosen, scores = choose_candidate(evaluated, goal=goal, weights=self.weights)
        return chosen.text, {
            "scores": scores,
            "chosen_score": max(scores),
            "candidate_count": len(evaluated),
        }
