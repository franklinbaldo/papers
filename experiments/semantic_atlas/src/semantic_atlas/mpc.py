from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np

from .trajectory import trajectory_metrics


@dataclass(frozen=True)
class Route:
    """Ordered semantic waypoints that the MPC controller must visit."""

    waypoints: np.ndarray
    tolerance: float = 0.25

    def __post_init__(self) -> None:
        waypoints = np.asarray(self.waypoints, dtype=np.float64)
        if waypoints.ndim != 2 or len(waypoints) == 0:
            raise ValueError("waypoints must be a non-empty 2D array")
        if self.tolerance <= 0:
            raise ValueError("tolerance must be positive")
        object.__setattr__(self, "waypoints", waypoints)

    def target(self, index: int) -> np.ndarray:
        if not 0 <= index < len(self.waypoints):
            raise ValueError("waypoint index out of range")
        return self.waypoints[index]

    def advance(self, index: int, point: np.ndarray) -> int:
        point = np.asarray(point, dtype=np.float64)
        while index < len(self.waypoints) - 1:
            if np.linalg.norm(point - self.waypoints[index]) > self.tolerance:
                break
            index += 1
        return index


@dataclass(frozen=True)
class KNNManifoldPenalty:
    """Distance-to-observed-support penalty for candidate SRF paths."""

    reference_points: np.ndarray
    k: int = 1
    scale: float = 1.0

    def __post_init__(self) -> None:
        points = np.asarray(self.reference_points, dtype=np.float64)
        if points.ndim != 2 or len(points) == 0:
            raise ValueError("reference_points must be a non-empty 2D array")
        if not 1 <= self.k <= len(points):
            raise ValueError("k must be between 1 and number of reference points")
        if self.scale <= 0:
            raise ValueError("scale must be positive")
        object.__setattr__(self, "reference_points", points)

    def __call__(self, path: np.ndarray) -> float:
        path = np.asarray(path, dtype=np.float64)
        distances = np.linalg.norm(
            path[:, None, :] - self.reference_points[None, :, :], axis=-1
        )
        nearest = np.partition(distances, self.k - 1, axis=1)[:, : self.k]
        return float(np.mean(nearest) / self.scale)


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


def whitespace_commit_prefix(text: str, token_budget: int) -> str:
    """Cheap toy commit rule; model adapters should provide tokenizer-aware commits."""
    if token_budget < 1:
        raise ValueError("token_budget must be >= 1")
    return " ".join(text.split()[:token_budget])


class SemanticMPC:
    """Closed-loop route-following MPC over short generated continuations."""

    def __init__(
        self,
        propose: Callable[[str, int], Sequence[tuple[str, float]]],
        trace: Callable[[str, str], np.ndarray],
        route: Route,
        off_manifold: Callable[[np.ndarray], float],
        commit_prefix: Callable[[str, int], str] = whitespace_commit_prefix,
        commit_tokens: int = 4,
        weights: MPCWeights = MPCWeights(),
    ) -> None:
        if commit_tokens < 1:
            raise ValueError("commit_tokens must be >= 1")
        self.propose = propose
        self.trace = trace
        self.route = route
        self.off_manifold = off_manifold
        self.commit_prefix = commit_prefix
        self.commit_tokens = commit_tokens
        self.weights = weights
        self.waypoint_index = 0

    @property
    def current_target(self) -> np.ndarray:
        return self.route.target(self.waypoint_index)

    def step(self, prefix: str, candidates: int = 8) -> tuple[str, dict]:
        proposals = self.propose(prefix, candidates)
        target = self.current_target.copy()
        evaluated = []
        for text, logprob in proposals:
            path = np.asarray(self.trace(prefix, text), dtype=np.float64)
            evaluated.append(
                Candidate(
                    text=text,
                    logprob=logprob,
                    path=path,
                    off_manifold_penalty=float(self.off_manifold(path)),
                )
            )

        chosen, scores = choose_candidate(evaluated, goal=target, weights=self.weights)
        committed_text = self.commit_prefix(chosen.text, self.commit_tokens)
        committed_path = np.asarray(self.trace(prefix, committed_text), dtype=np.float64)
        if committed_path.ndim != 2 or len(committed_path) == 0:
            raise ValueError("trace must return a non-empty 2D path")

        waypoint_before = self.waypoint_index
        self.waypoint_index = self.route.advance(
            self.waypoint_index, committed_path[-1]
        )
        return committed_text, {
            "scores": scores,
            "chosen_score": max(scores),
            "candidate_count": len(evaluated),
            "target": target,
            "waypoint_index_before": waypoint_before,
            "waypoint_index_after": self.waypoint_index,
            "chosen_full_text": chosen.text,
            "chosen_off_manifold_penalty": chosen.off_manifold_penalty,
            "candidate_off_manifold_penalties": [
                candidate.off_manifold_penalty for candidate in evaluated
            ],
            "committed_path": committed_path,
        }
