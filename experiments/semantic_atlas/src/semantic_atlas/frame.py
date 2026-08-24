from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def regular_simplex(dim: int) -> np.ndarray:
    """Return dim+1 unit vectors forming a regular simplex in R^dim."""
    if dim < 1:
        raise ValueError("dim must be >= 1")

    eye = np.eye(dim + 1, dtype=np.float64)
    centered = eye - np.ones((dim + 1, dim + 1), dtype=np.float64) / (dim + 1)
    _, _, vh = np.linalg.svd(centered, full_matrices=False)
    basis = vh[:dim].T
    simplex = centered @ basis
    simplex /= np.linalg.norm(simplex, axis=1, keepdims=True)
    return simplex


def _fix_component_signs(components: np.ndarray) -> np.ndarray:
    components = np.asarray(components, dtype=np.float64).copy()
    for row in components:
        pivot = int(np.argmax(np.abs(row)))
        if row[pivot] < 0:
            row *= -1
    return components


def orthogonal_procrustes(source: np.ndarray, target: np.ndarray) -> np.ndarray:
    """Fit R minimizing ||source @ R - target||_F for paired calibration rows."""
    source = np.asarray(source, dtype=np.float64)
    target = np.asarray(target, dtype=np.float64)
    if source.shape != target.shape or source.ndim != 2:
        raise ValueError("source and target must be aligned 2D arrays")
    dim = source.shape[1]
    if len(source) < dim:
        raise ValueError("at least dim paired calibration examples are required")
    if np.linalg.matrix_rank(source) < dim or np.linalg.matrix_rank(target) < dim:
        raise ValueError("calibration correspondences must span the canonical dimension")

    u, _, vh = np.linalg.svd(source.T @ target, full_matrices=False)
    return u @ vh


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
        components = _fix_component_signs(vh[:dim])
        denom = max(x.shape[0] - 1, 1)
        scales = singular_values[:dim] / np.sqrt(denom)
        scales = np.maximum(scales, eps)
        return cls(mean=mean, components=components, scales=scales)

    def transform(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=np.float64)
        return ((x - self.mean) @ self.components.T) / self.scales


@dataclass(frozen=True)
class QuasarFrame:
    """Artificial quasars plus an empirically anchored model-to-SRF calibration.

    The simplex fixes only the geometry of the external gauge. Semantic orientation
    comes from paired calibration examples: every non-reference model is aligned to
    the same frozen canonical targets with orthogonal Procrustes.
    """

    quasars: np.ndarray
    whitening: WhiteningTransform
    rotation: np.ndarray

    @classmethod
    def reference(
        cls, calibration_embeddings: np.ndarray, dim: int
    ) -> tuple["QuasarFrame", np.ndarray]:
        """Freeze one canonical target cloud from the designated reference observer."""
        whitening = WhiteningTransform.fit(calibration_embeddings, dim=dim)
        canonical_targets = whitening.transform(calibration_embeddings)
        frame = cls(
            quasars=regular_simplex(dim),
            whitening=whitening,
            rotation=np.eye(dim, dtype=np.float64),
        )
        return frame, canonical_targets

    @classmethod
    def fit(
        cls,
        calibration_embeddings: np.ndarray,
        canonical_targets: np.ndarray,
    ) -> "QuasarFrame":
        """Align a model to frozen targets using row-wise calibration correspondences."""
        canonical_targets = np.asarray(canonical_targets, dtype=np.float64)
        if canonical_targets.ndim != 2:
            raise ValueError("canonical_targets must be a 2D array")
        if len(calibration_embeddings) != len(canonical_targets):
            raise ValueError("calibration embeddings and canonical targets must be paired")

        dim = canonical_targets.shape[1]
        whitening = WhiteningTransform.fit(calibration_embeddings, dim=dim)
        whitened = whitening.transform(calibration_embeddings)
        rotation = orthogonal_procrustes(whitened, canonical_targets)
        return cls(
            quasars=regular_simplex(dim),
            whitening=whitening,
            rotation=rotation,
        )

    @property
    def dim(self) -> int:
        return self.quasars.shape[1]

    def canonical_vectors(self, embeddings: np.ndarray) -> np.ndarray:
        whitened = self.whitening.transform(embeddings)
        canonical = whitened @ self.rotation
        norms = np.linalg.norm(canonical, axis=-1, keepdims=True)
        return canonical / np.maximum(norms, 1e-12)

    def coordinates(self, embeddings: np.ndarray) -> np.ndarray:
        canonical = self.canonical_vectors(embeddings)
        return canonical @ self.quasars.T
