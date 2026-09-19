"""Small learned baselines for reality-bounded specialist recruitment."""

from __future__ import annotations

import random
from statistics import median
from typing import Iterable, Sequence

from colony import SpecialistReport, age_spread_ms, disagreement


class ContextualPolicyBandit:
    """Epsilon-greedy policy selector using only declared context labels.

    The selector never derives reward itself. A caller may update it only with a
    lawful delayed task/prediction reward in a physical deployment. Synthetic
    experiments may use hidden truth in the harness for evaluation/training, but
    that truth is not part of the decision-time observation.
    """

    def __init__(self, actions: Sequence[str], *, epsilon: float = 0.1, seed: int = 0):
        self.actions = tuple(actions)
        if not self.actions:
            raise ValueError("at least one action is required")
        if not 0.0 <= epsilon <= 1.0:
            raise ValueError("epsilon must be in [0, 1]")
        self.epsilon = epsilon
        self._rng = random.Random(seed)
        self.counts: dict[tuple[str, str], int] = {}
        self.values: dict[tuple[str, str], float] = {}

    def select(self, context: str) -> str:
        if self._rng.random() < self.epsilon:
            return self._rng.choice(self.actions)
        return max(
            self.actions,
            key=lambda action: (self.values.get((context, action), 0.0), action),
        )

    def update(self, context: str, action: str, reward: float) -> None:
        if action not in self.actions:
            raise ValueError(f"unknown action: {action}")
        key = (context, action)
        count = self.counts.get(key, 0) + 1
        old = self.values.get(key, 0.0)
        self.counts[key] = count
        self.values[key] = old + (reward - old) / count

    def best_action(self, context: str) -> str:
        seen = [action for action in self.actions if (context, action) in self.counts]
        if not seen:
            raise ValueError(f"context has not been trained: {context}")
        return max(seen, key=lambda action: (self.values[(context, action)], action))


class LinearContextualPolicy:
    """Tiny ridge-regression policy over continuous lawful coordinator signals.

    Each action gets an independent linear reward model. ``observe`` accumulates
    sufficient statistics, so training memory does not grow with episode count.
    The policy sees only the supplied feature vector; delayed reward remains an
    external training signal.
    """

    def __init__(
        self,
        actions: Sequence[str],
        *,
        feature_dim: int,
        ridge: float = 0.1,
    ) -> None:
        self.actions = tuple(actions)
        if not self.actions:
            raise ValueError("at least one action is required")
        if feature_dim <= 0:
            raise ValueError("feature_dim must be positive")
        if ridge <= 0.0:
            raise ValueError("ridge must be positive")
        self.feature_dim = feature_dim
        self.ridge = ridge
        self._gram = {
            action: [[0.0] * feature_dim for _ in range(feature_dim)]
            for action in self.actions
        }
        self._target = {action: [0.0] * feature_dim for action in self.actions}
        self._weights: dict[str, tuple[float, ...]] | None = None

    def observe(self, action: str, features: Sequence[float], reward: float) -> None:
        if action not in self.actions:
            raise ValueError(f"unknown action: {action}")
        x = _validated_features(features, self.feature_dim)
        gram = self._gram[action]
        target = self._target[action]
        for row in range(self.feature_dim):
            target[row] += x[row] * reward
            for col in range(self.feature_dim):
                gram[row][col] += x[row] * x[col]
        self._weights = None

    def fit(self) -> None:
        weights: dict[str, tuple[float, ...]] = {}
        for action in self.actions:
            matrix = [row[:] for row in self._gram[action]]
            for index in range(self.feature_dim):
                matrix[index][index] += self.ridge
            weights[action] = tuple(
                _solve_linear_system(matrix, self._target[action])
            )
        self._weights = weights

    def predict_reward(self, action: str, features: Sequence[float]) -> float:
        if action not in self.actions:
            raise ValueError(f"unknown action: {action}")
        if self._weights is None:
            raise ValueError("policy must be fit before prediction")
        x = _validated_features(features, self.feature_dim)
        return sum(weight * value for weight, value in zip(self._weights[action], x))

    def select(self, features: Sequence[float]) -> str:
        return max(
            self.actions,
            key=lambda action: (self.predict_reward(action, features), action),
        )


def freshness_context(
    reports: Iterable[SpecialistReport],
    *,
    stale_after_ms: float = 150.0,
) -> str:
    """Bucket a modality by lawful report age only."""

    items = list(reports)
    if not items:
        raise ValueError("at least one report is required")
    if stale_after_ms < 0.0:
        raise ValueError("stale_after_ms must be non-negative")
    age_ms = float(median(report.age_ms for report in items))
    return "stale" if age_ms > stale_after_ms else "fresh"


def continuous_context_features(
    primary_reports: Iterable[SpecialistReport],
    secondary_reports: Iterable[SpecialistReport],
    *,
    half_life_ms: float = 150.0,
) -> tuple[float, ...]:
    """Build a continuous reality-bounded context from two modality pilots.

    The features intentionally use only report metadata and interpretations that
    can exist in a physical deployment: age, freshness, disagreement, confidence
    and age spread. No hidden fault flag or realized error is included.
    """

    primary = list(primary_reports)
    secondary = list(secondary_reports)
    if not primary or not secondary:
        raise ValueError("both modalities require at least one report")
    if half_life_ms <= 0.0:
        raise ValueError("half_life_ms must be positive")

    primary_age_ms = float(median(report.age_ms for report in primary))
    secondary_age_ms = float(median(report.age_ms for report in secondary))
    primary_confidence = float(median(report.confidence for report in primary))
    secondary_confidence = float(median(report.confidence for report in secondary))
    primary_age_s = primary_age_ms / 1000.0

    return (
        1.0,
        primary_age_s,
        primary_age_s**2,
        2 ** (-primary_age_ms / half_life_ms),
        disagreement(primary),
        primary_confidence,
        age_spread_ms(primary) / 1000.0,
        disagreement(secondary),
        secondary_confidence,
        secondary_age_ms / 1000.0,
    )


def _validated_features(features: Sequence[float], expected: int) -> tuple[float, ...]:
    values = tuple(float(value) for value in features)
    if len(values) != expected:
        raise ValueError(f"expected {expected} features, got {len(values)}")
    return values


def _solve_linear_system(matrix: list[list[float]], target: Sequence[float]) -> list[float]:
    """Solve a small dense linear system with pivoted Gauss-Jordan elimination."""

    size = len(target)
    augmented = [list(matrix[row]) + [float(target[row])] for row in range(size)]
    for col in range(size):
        pivot = max(range(col, size), key=lambda row: abs(augmented[row][col]))
        if abs(augmented[pivot][col]) < 1e-12:
            raise ValueError("singular linear system")
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        scale = augmented[col][col]
        for index in range(col, size + 1):
            augmented[col][index] /= scale
        for row in range(size):
            if row == col:
                continue
            factor = augmented[row][col]
            if factor == 0.0:
                continue
            for index in range(col, size + 1):
                augmented[row][index] -= factor * augmented[col][index]
    return [augmented[row][size] for row in range(size)]
