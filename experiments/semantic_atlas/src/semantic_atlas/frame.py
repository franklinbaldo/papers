from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def regular_simplex(dim: int) -> np.ndarray:
    """Return dim+1 unit vectors forming a regular simplex in R^dim."""
    if dim < 1:
        raise ValueError("dim must be >= 1")

    # Start with the centered standard basis in R^(dim+1), then project the
    # dim-dimensional zero-sum subspace onto an orthonormal basis.
    eye = np.eye(dim + 1, dtype=np.float64)
    centered = eye - np.ones((dim + 1, dim + 1), dtype=np.float64) / (dim + 1)
    _, _, vh = np.linalg.svd(centered, full_matrices=False)
    basis = vh[:dim].T
    simplex = centered @ basis
    simplex /= np.linalg.norm(simplex, axis=1, keepdims=True)
    return simplex


@dataclass(frozen=True)
class WhiteningTransform:
    mean: np.ndarray
    components: np.ndarray
    scales: np.ndarray

    @classmethod
    def fit(cls, x: np.ndarray, dim: int, eps: float = 1e-8) -> "WhiteningTransform":
        x = np.asarray(x, dtype=np.float64)
        if x.ndim != 2:
            raise ValueError("x must be a 2D array")
        if not 1 <= dim <= min(x.shape):
            raise ValueError("dim must be between 1 and min(n_samples, n_features)")

        mean = x.mean(axis=0)
        centered = x - mean
        _, singular_values, vh = np.linalg.svd(centered, full_matrices=False)
        components = vh[:dim]
        # Convert singular values to sample-standard-deviation scale.
        denom = max(x.shape[0] - 1, 1)
        scales = singular_values[:dim] / np.sqrt(denom)
        scales = np.maximum(scales, eps)
        return cls(mean=mean, components=components, scales=scales)

    def transform(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=np.float64)
        return ((x - self.mean) @ self.components.T) / self.scales


@dataclass(frozen=True)
class QuasarFrame:
    """A mathematically fixed frame plus a model-specific calibration."""

    quasars: np.ndarray
    whitening: WhiteningTransform
    rotation: np.ndarray

    @classmethod
    def fit(cls, calibration_embeddings: np.ndarray, dim: int) -> "QuasarFrame":
        whitening = WhiteningTransform.fit(calibration_embeddings, dim=dim)
        whitened = whitening.transform(calibration_embeddings)

        # The SVD of the whitened calibration cloud gives a deterministic
        # orientation up to sign. Fix each sign by requiring the largest-magnitude
        # coordinate in a component to be positive.
        _, _, vh = np.linalg.svd(whitened, full_matrices=False)
        rotation = vh[:dim].T
        for j in range(rotation.shape[1]):
            column = rotation[:, j]
            pivot = int(np.argmax(np.abs(column)))
            if column[pivot] < 0:
                rotation[:, j] *= -1

        return cls(
            quasars=regular_simplex(dim),
            whitening=whitening,
            rotation=rotation,
        )

    @property
    def dim(self) -> int:
        return self.quasars.shape[1]

    def coordinates(self, embeddings: np.ndarray) -> np.ndarray:
        whitened = self.whitening.transform(embeddings)
        canonical = whitened @ self.rotation
        norms = np.linalg.norm(canonical, axis=-1, keepdims=True)
        canonical = canonical / np.maximum(norms, 1e-12)
        return canonical @ self.quasars.T

    def canonical_vectors(self, embeddings: np.ndarray) -> np.ndarray:
        whitened = self.whitening.transform(embeddings)
        canonical = whitened @ self.rotation
        norms = np.linalg.norm(canonical, axis=-1, keepdims=True)
        return canonical / np.maximum(norms, 1e-12)
