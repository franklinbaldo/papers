from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray


FloatArray = NDArray[np.float64]


def balanced_accuracy(y_true: ArrayLike, y_pred: ArrayLike) -> float:
    truth = np.asarray(y_true)
    pred = np.asarray(y_pred)
    if truth.shape != pred.shape:
        raise ValueError("y_true and y_pred must have matching shapes")
    classes = np.unique(truth)
    if classes.size < 2:
        raise ValueError("balanced accuracy requires at least two classes")
    recalls = []
    for cls in classes:
        mask = truth == cls
        recalls.append(float(np.mean(pred[mask] == truth[mask])))
    return float(np.mean(recalls))


class RidgeRelationDecoder:
    """Small deterministic ridge classifier used for cheap apparatus tests.

    This is not a privileged confirmatory decoder.  The model-backed manifest
    must freeze decoder capacity and hyperparameters before Gate 1 is opened.
    """

    def __init__(self, alpha: float = 1.0) -> None:
        if alpha < 0:
            raise ValueError("alpha must be non-negative")
        self.alpha = float(alpha)
        self._classes: NDArray | None = None
        self._coef: FloatArray | None = None

    def fit(self, x: ArrayLike, y: ArrayLike) -> "RidgeRelationDecoder":
        features = np.asarray(x, dtype=float)
        labels = np.asarray(y)
        if features.ndim != 2:
            raise ValueError("x must have shape (n_examples, n_features)")
        if labels.ndim != 1 or labels.shape[0] != features.shape[0]:
            raise ValueError("y must be a vector matching x rows")

        classes = np.unique(labels)
        if classes.size < 2:
            raise ValueError("decoder requires at least two classes")

        x_aug = np.concatenate([np.ones((features.shape[0], 1)), features], axis=1)
        targets = -np.ones((features.shape[0], classes.size), dtype=float)
        for col, cls in enumerate(classes):
            targets[labels == cls, col] = 1.0

        penalty = np.eye(x_aug.shape[1], dtype=float) * self.alpha
        penalty[0, 0] = 0.0
        gram = x_aug.T @ x_aug + penalty
        self._coef = np.linalg.pinv(gram) @ x_aug.T @ targets
        self._classes = classes
        return self

    def predict(self, x: ArrayLike) -> NDArray:
        if self._coef is None or self._classes is None:
            raise RuntimeError("decoder has not been fitted")
        features = np.asarray(x, dtype=float)
        if features.ndim != 2:
            raise ValueError("x must have shape (n_examples, n_features)")
        x_aug = np.concatenate([np.ones((features.shape[0], 1)), features], axis=1)
        scores = x_aug @ self._coef
        return self._classes[np.argmax(scores, axis=1)]


@dataclass(frozen=True)
class BootstrapDifference:
    observed: float
    lower: float
    upper: float


def paired_bootstrap_accuracy_difference(
    y_true: ArrayLike,
    pred_a: ArrayLike,
    pred_b: ArrayLike,
    *,
    n_boot: int = 2000,
    seed: int = 0,
) -> BootstrapDifference:
    """Paired bootstrap CI for balanced-accuracy(A) - balanced-accuracy(B)."""

    truth = np.asarray(y_true)
    a = np.asarray(pred_a)
    b = np.asarray(pred_b)
    if truth.ndim != 1 or a.shape != truth.shape or b.shape != truth.shape:
        raise ValueError("truth and predictions must be matching vectors")
    if n_boot < 100:
        raise ValueError("n_boot must be at least 100")

    observed = balanced_accuracy(truth, a) - balanced_accuracy(truth, b)
    rng = np.random.default_rng(seed)
    diffs = np.empty(n_boot, dtype=float)
    n = truth.shape[0]
    expected_classes = np.unique(truth).size
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        sample_truth = truth[idx]
        attempts = 0
        while np.unique(sample_truth).size != expected_classes:
            idx = rng.integers(0, n, size=n)
            sample_truth = truth[idx]
            attempts += 1
            if attempts > 1000:
                raise RuntimeError("could not draw a class-complete bootstrap sample")
        diffs[i] = balanced_accuracy(sample_truth, a[idx]) - balanced_accuracy(
            sample_truth, b[idx]
        )

    lower, upper = np.quantile(diffs, [0.025, 0.975])
    return BootstrapDifference(
        observed=float(observed),
        lower=float(lower),
        upper=float(upper),
    )
