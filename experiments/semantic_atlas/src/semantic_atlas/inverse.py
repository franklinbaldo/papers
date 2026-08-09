from __future__ import annotations

from dataclasses import dataclass, field
from math import log
from typing import Callable, Sequence

import numpy as np


@dataclass(frozen=True)
class InferenceRecord:
    """One observed causal state and a lexical realization produced from it."""

    state: np.ndarray
    token_id: int
    text: str
    context: str = ""
    velocity: np.ndarray | None = None
    next_state: np.ndarray | None = None
    topk: dict[int, float] = field(default_factory=dict)
    model_revision: str = ""
    tokenizer_revision: str = ""

    def __post_init__(self) -> None:
        state = np.asarray(self.state, dtype=np.float64)
        if state.ndim != 1:
            raise ValueError("state must be a 1D SRF vector")
        object.__setattr__(self, "state", state)

        if self.velocity is not None:
            velocity = np.asarray(self.velocity, dtype=np.float64)
            if velocity.shape != state.shape:
                raise ValueError("velocity must have the same shape as state")
            object.__setattr__(self, "velocity", velocity)

        if self.next_state is not None:
            next_state = np.asarray(self.next_state, dtype=np.float64)
            if next_state.shape != state.shape:
                raise ValueError("next_state must have the same shape as state")
            object.__setattr__(self, "next_state", next_state)


@dataclass(frozen=True)
class Neighbor:
    record: InferenceRecord
    distance: float
    history_alignment: float
    route_alignment: float
    weight: float


def _cosine_alignment(a: np.ndarray | None, b: np.ndarray | None) -> float:
    if a is None or b is None:
        return 0.0
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    if a.shape != b.shape:
        raise ValueError("alignment vectors must share a shape")
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom <= 1e-12:
        return 0.0
    return float(np.dot(a, b) / denom)


class InferenceMemory:
    """Toy non-parametric inverse atlas over previously observed inference states."""

    def __init__(self, records: Sequence[InferenceRecord] = ()) -> None:
        self.records = list(records)
        self._validate_dimensions()

    def _validate_dimensions(self) -> None:
        if not self.records:
            return
        dim = self.records[0].state.shape
        if any(record.state.shape != dim for record in self.records):
            raise ValueError("all records must share one SRF dimension")

    def add(self, record: InferenceRecord) -> None:
        if self.records and record.state.shape != self.records[0].state.shape:
            raise ValueError("record dimension does not match memory")
        self.records.append(record)

    def query(
        self,
        state: np.ndarray,
        k: int = 8,
        incoming_velocity: np.ndarray | None = None,
        desired_delta: np.ndarray | None = None,
        bandwidth: float = 0.25,
        history_weight: float = 1.0,
        route_weight: float = 1.0,
    ) -> list[Neighbor]:
        if not self.records:
            raise ValueError("memory is empty")
        if not 1 <= k <= len(self.records):
            raise ValueError("k must be between 1 and memory size")
        if bandwidth <= 0:
            raise ValueError("bandwidth must be positive")

        state = np.asarray(state, dtype=np.float64)
        states = np.stack([record.state for record in self.records])
        if state.shape != states.shape[1:]:
            raise ValueError("query state dimension does not match memory")

        incoming = None
        if incoming_velocity is not None:
            incoming = np.asarray(incoming_velocity, dtype=np.float64)
            if incoming.shape != state.shape:
                raise ValueError("incoming_velocity must match state dimension")

        desired = None
        if desired_delta is not None:
            desired = np.asarray(desired_delta, dtype=np.float64)
            if desired.shape != state.shape:
                raise ValueError("desired_delta must match state dimension")

        distances = np.linalg.norm(states - state, axis=1)
        indices = np.argpartition(distances, k - 1)[:k]
        indices = indices[np.argsort(distances[indices])]

        neighbors: list[Neighbor] = []
        for index in indices:
            record = self.records[int(index)]
            history_alignment = _cosine_alignment(record.velocity, incoming)
            observed_delta = (
                None
                if record.next_state is None
                else record.next_state - record.state
            )
            route_alignment = _cosine_alignment(observed_delta, desired)

            positional = np.exp(-0.5 * (float(distances[index]) / bandwidth) ** 2)
            historical = (
                np.exp(history_weight * history_alignment)
                if incoming is not None
                else 1.0
            )
            directional = (
                np.exp(route_weight * route_alignment)
                if desired is not None
                else 1.0
            )
            weight = float(positional * historical * directional)
            neighbors.append(
                Neighbor(
                    record=record,
                    distance=float(distances[index]),
                    history_alignment=history_alignment,
                    route_alignment=route_alignment,
                    weight=weight,
                )
            )
        return neighbors

    def token_distribution(
        self,
        state: np.ndarray,
        k: int = 8,
        incoming_velocity: np.ndarray | None = None,
        desired_delta: np.ndarray | None = None,
        bandwidth: float = 0.25,
        history_weight: float = 1.0,
        route_weight: float = 1.0,
        use_stored_topk: bool = True,
    ) -> dict[int, float]:
        neighbors = self.query(
            state,
            k=k,
            incoming_velocity=incoming_velocity,
            desired_delta=desired_delta,
            bandwidth=bandwidth,
            history_weight=history_weight,
            route_weight=route_weight,
        )
        distribution: dict[int, float] = {}
        total = 0.0
        for neighbor in neighbors:
            sources = (
                neighbor.record.topk
                if use_stored_topk and neighbor.record.topk
                else {neighbor.record.token_id: 1.0}
            )
            for token_id, probability in sources.items():
                contribution = neighbor.weight * float(probability)
                distribution[int(token_id)] = distribution.get(int(token_id), 0.0) + contribution
                total += contribution

        if total <= 0:
            raise ValueError("neighbors produced zero lexical mass")
        return {token_id: value / total for token_id, value in distribution.items()}

    def lexical_entropy(self, *args, **kwargs) -> float:
        distribution = self.token_distribution(*args, **kwargs)
        return float(-sum(p * log(p) for p in distribution.values() if p > 0))


def interpolate_with_generator(
    target_state: np.ndarray,
    neighbors: Sequence[Neighbor],
    synthesize: Callable[[Sequence[InferenceRecord]], str],
    embed: Callable[[str], np.ndarray],
    attempts: int = 4,
) -> tuple[str, float]:
    """Use an LLM as an inverse solver and verify every proposal in SRF coordinates.

    No midpoint assumption is made. Neighbor texts are only hints for the generator;
    the candidate is accepted by measured distance to `target_state`.
    """
    if attempts < 1:
        raise ValueError("attempts must be >= 1")
    if not neighbors:
        raise ValueError("at least one neighbor is required")

    target = np.asarray(target_state, dtype=np.float64)
    best_text = ""
    best_distance = float("inf")
    records = [neighbor.record for neighbor in neighbors]
    for _ in range(attempts):
        candidate = synthesize(records)
        candidate_state = np.asarray(embed(candidate), dtype=np.float64)
        if candidate_state.shape != target.shape:
            raise ValueError("embedded candidate must match target SRF dimension")
        distance = float(np.linalg.norm(candidate_state - target))
        if distance < best_distance:
            best_text = candidate
            best_distance = distance
    return best_text, best_distance
