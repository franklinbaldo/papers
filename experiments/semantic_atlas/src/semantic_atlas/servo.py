from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class LinearFutureHead:
    """Ridge-regression head predicting future SRF displacement from hidden state."""

    weight: np.ndarray
    bias: np.ndarray

    @classmethod
    def fit(
        cls,
        hidden: np.ndarray,
        delta: np.ndarray,
        ridge: float = 1e-3,
    ) -> "LinearFutureHead":
        hidden = np.asarray(hidden, dtype=np.float64)
        delta = np.asarray(delta, dtype=np.float64)
        if hidden.ndim != 2 or delta.ndim != 2 or len(hidden) != len(delta):
            raise ValueError("hidden and delta must be aligned 2D arrays")

        x_mean = hidden.mean(axis=0)
        y_mean = delta.mean(axis=0)
        x = hidden - x_mean
        y = delta - y_mean
        gram = x.T @ x + ridge * np.eye(x.shape[1])
        weight = np.linalg.solve(gram, x.T @ y).T
        bias = y_mean - weight @ x_mean
        return cls(weight=weight, bias=bias)

    def predict(self, hidden: np.ndarray) -> np.ndarray:
        hidden = np.asarray(hidden, dtype=np.float64)
        return hidden @ self.weight.T + self.bias

    @property
    def jacobian(self) -> np.ndarray:
        return self.weight


def control_delta(
    head: LinearFutureHead,
    hidden: np.ndarray,
    desired_delta: np.ndarray,
    regularization: float = 1e-2,
) -> tuple[np.ndarray, dict[str, float]]:
    """Return the unconstrained minimum-energy local hidden-state correction."""

    hidden = np.asarray(hidden, dtype=np.float64)
    desired_delta = np.asarray(desired_delta, dtype=np.float64)
    predicted = np.asarray(head.predict(hidden), dtype=np.float64)
    error = desired_delta - predicted
    j = head.jacobian
    system = j @ j.T + regularization * np.eye(j.shape[0])
    correction = j.T @ np.linalg.solve(system, error)

    residual_before = float(np.linalg.norm(error))
    residual_after = float(np.linalg.norm(desired_delta - head.predict(hidden + correction)))
    return correction, {
        "prediction_error_before": residual_before,
        "prediction_error_after_raw_control": residual_after,
        "raw_control_norm": float(np.linalg.norm(correction)),
    }


@dataclass
class SemanticServo:
    head: LinearFutureHead
    gain: float = 1.0
    regularization: float = 1e-2
    max_norm: float | None = None

    def command(self, hidden: np.ndarray, desired_delta: np.ndarray) -> tuple[np.ndarray, dict[str, float]]:
        correction, diagnostics = control_delta(
            self.head,
            hidden,
            desired_delta,
            regularization=self.regularization,
        )

        command = self.gain * correction
        preclip_norm = float(np.linalg.norm(command))
        clipped = False
        if self.max_norm is not None:
            if self.max_norm < 0:
                raise ValueError("max_norm must be non-negative")
            if preclip_norm > self.max_norm:
                command = command * (self.max_norm / max(preclip_norm, 1e-12))
                clipped = True

        command_norm = float(np.linalg.norm(command))
        hidden = np.asarray(hidden, dtype=np.float64)
        desired_delta = np.asarray(desired_delta, dtype=np.float64)
        diagnostics.update(
            {
                "gain": float(self.gain),
                "preclip_command_norm": preclip_norm,
                "command_norm": command_norm,
                "clipped": float(clipped),
                "prediction_error_after_command": float(
                    np.linalg.norm(desired_delta - self.head.predict(hidden + command))
                ),
            }
        )
        return command, diagnostics
