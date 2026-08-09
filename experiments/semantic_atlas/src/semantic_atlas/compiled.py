from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class LowRankLexicalMap:
    """Truncated-SVD view of a language model output head."""

    decoder: np.ndarray
    projector: np.ndarray
    singular_values: np.ndarray

    @classmethod
    def from_output_head(cls, weight: np.ndarray, rank: int) -> "LowRankLexicalMap":
        weight = np.asarray(weight, dtype=np.float64)
        if weight.ndim != 2:
            raise ValueError("weight must be [vocab, hidden]")
        if not 1 <= rank <= min(weight.shape):
            raise ValueError("invalid rank")
        u, s, vh = np.linalg.svd(weight, full_matrices=False)
        return cls(
            decoder=u[:, :rank] * s[:rank],
            projector=vh[:rank],
            singular_values=s[:rank],
        )

    def project(self, hidden: np.ndarray) -> np.ndarray:
        hidden = np.asarray(hidden, dtype=np.float64)
        return hidden @ self.projector.T

    def logits(self, hidden: np.ndarray) -> np.ndarray:
        latent = self.project(hidden)
        return latent @ self.decoder.T


def topk_overlap(full_logits: np.ndarray, approx_logits: np.ndarray, k: int = 10) -> float:
    full_logits = np.asarray(full_logits)
    approx_logits = np.asarray(approx_logits)
    if full_logits.shape != approx_logits.shape:
        raise ValueError("logit arrays must have the same shape")
    if full_logits.ndim != 1:
        raise ValueError("topk_overlap expects one vocabulary vector")
    if not 1 <= k <= len(full_logits):
        raise ValueError("invalid k")
    full = set(np.argpartition(full_logits, -k)[-k:].tolist())
    approx = set(np.argpartition(approx_logits, -k)[-k:].tolist())
    return len(full & approx) / k


@dataclass(frozen=True)
class LocalLinearDynamics:
    """Affine reduced-order model q_(t+1) ~= A q_t + b."""

    matrix: np.ndarray
    bias: np.ndarray

    @classmethod
    def fit(cls, states: np.ndarray, next_states: np.ndarray, ridge: float = 1e-4) -> "LocalLinearDynamics":
        states = np.asarray(states, dtype=np.float64)
        next_states = np.asarray(next_states, dtype=np.float64)
        if states.shape != next_states.shape or states.ndim != 2:
            raise ValueError("states and next_states must be aligned 2D arrays")

        mean_x = states.mean(axis=0)
        mean_y = next_states.mean(axis=0)
        x = states - mean_x
        y = next_states - mean_y
        gram = x.T @ x + ridge * np.eye(x.shape[1])
        matrix = np.linalg.solve(gram, x.T @ y).T
        bias = mean_y - matrix @ mean_x
        return cls(matrix=matrix, bias=bias)

    def step(self, state: np.ndarray) -> np.ndarray:
        state = np.asarray(state, dtype=np.float64)
        return state @ self.matrix.T + self.bias

    def jump(self, state: np.ndarray, steps: int) -> np.ndarray:
        if steps < 0:
            raise ValueError("steps must be >= 0")
        result = np.asarray(state, dtype=np.float64)
        for _ in range(steps):
            result = self.step(result)
        return result
