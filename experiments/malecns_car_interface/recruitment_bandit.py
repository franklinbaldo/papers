"""Small learned baselines for reality-bounded specialist recruitment."""

from __future__ import annotations

import random
from statistics import median
from typing import Iterable, Sequence

from colony import SpecialistReport


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
