from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

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
    """Empirical affine baseline fit from observed SRF transitions.

    This object is deliberately *not* weight-derived. It remains in Experiment D as
    the reduced-dynamics baseline against which a compiled Jacobian operator is
    compared.
    """

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


@dataclass(frozen=True)
class WeightJacobianOperator:
    """Local semantic operator compiled from a differentiable frozen-weight map.

    The operator linearizes a model-derived function f around `anchor_input`:

        f(x) ~= anchor_output + J @ (x - anchor_input)

    No `(state, next_state)` trajectory pairs are accepted by this constructor.
    The empirical atlas is used only later for evaluation/calibration curves.
    """

    anchor_input: np.ndarray
    anchor_output: np.ndarray
    jacobian: np.ndarray

    @classmethod
    def from_linearization(
        cls,
        anchor_input: np.ndarray,
        anchor_output: np.ndarray,
        jacobian: np.ndarray,
    ) -> "WeightJacobianOperator":
        anchor_input = np.asarray(anchor_input, dtype=np.float64)
        anchor_output = np.asarray(anchor_output, dtype=np.float64)
        jacobian = np.asarray(jacobian, dtype=np.float64)
        if anchor_input.ndim != 1 or anchor_output.ndim != 1:
            raise ValueError("anchors must be 1D vectors")
        if jacobian.shape != (len(anchor_output), len(anchor_input)):
            raise ValueError("jacobian shape must be [output_dim, input_dim]")
        return cls(anchor_input, anchor_output, jacobian)

    @classmethod
    def from_torch_transition(
        cls,
        transition: Callable,
        anchor_input,
    ) -> "WeightJacobianOperator":
        """Differentiate a frozen PyTorch transition without empirical transition fitting."""
        try:
            import torch
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("install semantic-atlas-toy[models]") from exc

        anchor = anchor_input.detach().clone().requires_grad_(True)
        output = transition(anchor)
        if output.ndim != 1:
            raise ValueError("transition must return one 1D semantic vector")
        jacobian = torch.autograd.functional.jacobian(
            transition,
            anchor,
            vectorize=True,
            create_graph=False,
        )
        return cls.from_linearization(
            anchor.detach().cpu().double().numpy(),
            output.detach().cpu().double().numpy(),
            jacobian.detach().cpu().double().numpy(),
        )

    def predict(self, value: np.ndarray) -> np.ndarray:
        value = np.asarray(value, dtype=np.float64)
        return self.anchor_output + self.jacobian @ (value - self.anchor_input)

    def jvp(self, direction: np.ndarray) -> np.ndarray:
        direction = np.asarray(direction, dtype=np.float64)
        return self.jacobian @ direction
