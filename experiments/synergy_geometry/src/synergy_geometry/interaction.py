from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable, Iterable, Sequence

import numpy as np
from numpy.typing import ArrayLike, NDArray


FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class BalancedFactorialDecomposition:
    grand_mean: FloatArray
    effect_a: FloatArray
    effect_b: FloatArray
    interaction: FloatArray

    def reconstruct(self) -> FloatArray:
        return (
            self.grand_mean[None, None, :]
            + self.effect_a[:, None, :]
            + self.effect_b[None, :, :]
            + self.interaction
        )

    @property
    def interaction_rms(self) -> float:
        return float(np.sqrt(np.mean(np.square(self.interaction))))


def balanced_factorial_decomposition(activations: ArrayLike) -> BalancedFactorialDecomposition:
    """Decompose a complete balanced A × B activation grid into main effects and interaction.

    `activations` must have shape `(n_a, n_b, d)`.  The centering constraints
    are the empirical functional-ANOVA constraints for the frozen balanced
    design: each main effect has zero mean and the interaction has zero mean
    along either factor axis.
    """

    h = np.asarray(activations, dtype=float)
    if h.ndim != 3:
        raise ValueError("activations must have shape (n_a, n_b, d)")
    if h.shape[0] < 2 or h.shape[1] < 2:
        raise ValueError("both factors need at least two levels")

    grand = h.mean(axis=(0, 1))
    effect_a = h.mean(axis=1) - grand
    effect_b = h.mean(axis=0) - grand
    interaction = h - grand - effect_a[:, None, :] - effect_b[None, :, :]

    return BalancedFactorialDecomposition(
        grand_mean=grand,
        effect_a=effect_a,
        effect_b=effect_b,
        interaction=interaction,
    )


def mixed_finite_difference(
    activations: ArrayLike,
    a1: int,
    a2: int,
    b1: int,
    b2: int,
) -> FloatArray:
    """Return the mixed finite difference on a complete activation grid."""

    h = np.asarray(activations, dtype=float)
    if h.ndim != 3:
        raise ValueError("activations must have shape (n_a, n_b, d)")
    return h[a1, b1] - h[a1, b2] - h[a2, b1] + h[a2, b2]


class MainEffectsInteractionEstimator:
    """Fit only intercept + factor main effects and expose held-out residual interaction.

    The estimator is deliberately simple.  It does not claim that every
    residual is semantic interaction.  It supplies the frozen, identified
    residual used by Gate 1 before stronger nonlinear/marginal baselines are
    compared.

    Factor levels must already be represented in the training design.  New
    *combinations* may be scored, but entirely unseen factor identities are
    rejected instead of silently extrapolated.
    """

    def __init__(self) -> None:
        self._levels_a: tuple[Hashable, ...] | None = None
        self._levels_b: tuple[Hashable, ...] | None = None
        self._coef: FloatArray | None = None

    @staticmethod
    def _ordered_levels(values: Sequence[Hashable]) -> tuple[Hashable, ...]:
        return tuple(dict.fromkeys(values))

    def _design(
        self,
        a: Sequence[Hashable],
        b: Sequence[Hashable],
        *,
        fitting: bool,
    ) -> FloatArray:
        if len(a) != len(b):
            raise ValueError("a and b must have the same number of rows")

        if fitting:
            self._levels_a = self._ordered_levels(a)
            self._levels_b = self._ordered_levels(b)
            if len(self._levels_a) < 2 or len(self._levels_b) < 2:
                raise ValueError("both factors need at least two observed levels")

        if self._levels_a is None or self._levels_b is None:
            raise RuntimeError("estimator has not been fitted")

        index_a = {value: i for i, value in enumerate(self._levels_a)}
        index_b = {value: i for i, value in enumerate(self._levels_b)}
        unknown_a = [value for value in a if value not in index_a]
        unknown_b = [value for value in b if value not in index_b]
        if unknown_a or unknown_b:
            raise ValueError(
                f"unseen factor identities: A={sorted(set(map(str, unknown_a)))} "
                f"B={sorted(set(map(str, unknown_b)))}"
            )

        # Reference coding: intercept + all levels except the first reference.
        width = 1 + (len(index_a) - 1) + (len(index_b) - 1)
        x = np.zeros((len(a), width), dtype=float)
        x[:, 0] = 1.0

        for row, value in enumerate(a):
            idx = index_a[value]
            if idx > 0:
                x[row, idx] = 1.0

        offset = len(index_a)
        for row, value in enumerate(b):
            idx = index_b[value]
            if idx > 0:
                x[row, offset + idx - 1] = 1.0

        return x

    def fit(
        self,
        a: Iterable[Hashable],
        b: Iterable[Hashable],
        activations: ArrayLike,
    ) -> "MainEffectsInteractionEstimator":
        a_rows = list(a)
        b_rows = list(b)
        h = np.asarray(activations, dtype=float)
        if h.ndim != 2:
            raise ValueError("activations must have shape (n_examples, d)")
        if len(a_rows) != h.shape[0] or len(b_rows) != h.shape[0]:
            raise ValueError("factor rows and activations must have matching length")

        x = self._design(a_rows, b_rows, fitting=True)
        self._coef, *_ = np.linalg.lstsq(x, h, rcond=None)
        return self

    def predict_main_effects(
        self,
        a: Iterable[Hashable],
        b: Iterable[Hashable],
    ) -> FloatArray:
        if self._coef is None:
            raise RuntimeError("estimator has not been fitted")
        a_rows = list(a)
        b_rows = list(b)
        x = self._design(a_rows, b_rows, fitting=False)
        return x @ self._coef

    def interaction(
        self,
        a: Iterable[Hashable],
        b: Iterable[Hashable],
        activations: ArrayLike,
    ) -> FloatArray:
        a_rows = list(a)
        b_rows = list(b)
        h = np.asarray(activations, dtype=float)
        if h.ndim != 2:
            raise ValueError("activations must have shape (n_examples, d)")
        if len(a_rows) != h.shape[0] or len(b_rows) != h.shape[0]:
            raise ValueError("factor rows and activations must have matching length")
        return h - self.predict_main_effects(a_rows, b_rows)
