from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np


def _as_2d(x: np.ndarray, name: str) -> np.ndarray:
    value = np.asarray(x, dtype=np.float64)
    if value.ndim != 2:
        raise ValueError(f"{name} must be a 2D array")
    if not np.all(np.isfinite(value)):
        raise ValueError(f"{name} contains non-finite values")
    return value


def l2_rows(x: np.ndarray) -> np.ndarray:
    value = _as_2d(x, "x")
    return value / np.maximum(np.linalg.norm(value, axis=1, keepdims=True), 1e-12)


@dataclass(frozen=True)
class AffineAlignment:
    matrix: np.ndarray
    intercept: np.ndarray
    alpha: float

    def transform(self, x: np.ndarray) -> np.ndarray:
        value = _as_2d(x, "x")
        if value.shape[1] != self.matrix.shape[0]:
            raise ValueError("input feature dimension does not match affine map")
        return l2_rows(value @ self.matrix + self.intercept)


def fit_affine_ridge(
    source: np.ndarray,
    target: np.ndarray,
    *,
    alpha: float,
) -> AffineAlignment:
    source = _as_2d(source, "source")
    target = _as_2d(target, "target")
    if len(source) != len(target):
        raise ValueError("source and target must have paired rows")
    if alpha < 0:
        raise ValueError("alpha must be >= 0")

    source_mean = source.mean(axis=0)
    target_mean = target.mean(axis=0)
    centered_source = source - source_mean
    centered_target = target - target_mean
    gram = centered_source.T @ centered_source
    rhs = centered_source.T @ centered_target
    matrix = np.linalg.solve(gram + alpha * np.eye(source.shape[1]), rhs)
    intercept = target_mean - source_mean @ matrix
    return AffineAlignment(matrix=matrix, intercept=intercept, alpha=float(alpha))


def _inverse_sqrt(matrix: np.ndarray, *, eps: float = 1e-10) -> np.ndarray:
    values, vectors = np.linalg.eigh(matrix)
    values = np.maximum(values, eps)
    return (vectors * (1.0 / np.sqrt(values))) @ vectors.T


@dataclass(frozen=True)
class CCAAlignment:
    transfer_mean: np.ndarray
    transfer_whitener: np.ndarray
    transfer_components: np.ndarray
    canonical_map: AffineAlignment
    regularization: float
    components: int

    def transform(self, transfer: np.ndarray) -> np.ndarray:
        transfer = _as_2d(transfer, "transfer")
        if transfer.shape[1] != self.transfer_mean.shape[0]:
            raise ValueError("transfer feature dimension does not match CCA fit")
        shared = (
            (transfer - self.transfer_mean)
            @ self.transfer_whitener
            @ self.transfer_components
        )
        return self.canonical_map.transform(shared)


def fit_regularized_cca(
    reference: np.ndarray,
    transfer: np.ndarray,
    canonical_targets: np.ndarray,
    *,
    regularization: float,
    components: int,
    canonical_alpha: float = 1e-6,
) -> CCAAlignment:
    """Fit paired CCA and orient the transfer side into frozen canonical targets.

    CCA estimates shared correlated directions without using held-out rows. The
    transfer-side canonical variates are then mapped onto the same frozen target
    cloud used by Experiment A, so evaluation stays in the existing SRF gauge.
    """

    reference = _as_2d(reference, "reference")
    transfer = _as_2d(transfer, "transfer")
    canonical_targets = _as_2d(canonical_targets, "canonical_targets")
    if len(reference) != len(transfer) or len(reference) != len(canonical_targets):
        raise ValueError("reference, transfer, and targets must have paired rows")
    if regularization <= 0:
        raise ValueError("regularization must be > 0")

    max_components = min(reference.shape[1], transfer.shape[1], len(reference) - 1)
    if not 1 <= components <= max_components:
        raise ValueError("components exceeds the paired calibration rank bound")

    reference_mean = reference.mean(axis=0)
    transfer_mean = transfer.mean(axis=0)
    x = reference - reference_mean
    y = transfer - transfer_mean
    denom = max(len(reference) - 1, 1)
    covariance_x = (x.T @ x) / denom + regularization * np.eye(reference.shape[1])
    covariance_y = (y.T @ y) / denom + regularization * np.eye(transfer.shape[1])
    covariance_xy = (x.T @ y) / denom

    whitening_x = _inverse_sqrt(covariance_x)
    whitening_y = _inverse_sqrt(covariance_y)
    coupling = whitening_x @ covariance_xy @ whitening_y
    _, _, vh = np.linalg.svd(coupling, full_matrices=False)
    transfer_components = vh.T[:, :components]
    transfer_shared = y @ whitening_y @ transfer_components
    canonical_map = fit_affine_ridge(
        transfer_shared,
        canonical_targets,
        alpha=canonical_alpha,
    )
    return CCAAlignment(
        transfer_mean=transfer_mean,
        transfer_whitener=whitening_y,
        transfer_components=transfer_components,
        canonical_map=canonical_map,
        regularization=float(regularization),
        components=int(components),
    )


def deterministic_folds(paths: Sequence[str], *, folds: int) -> list[np.ndarray]:
    """Return stable calibration-only validation folds from path identity."""

    if folds < 2:
        raise ValueError("folds must be >= 2")
    if len(paths) < folds:
        raise ValueError("number of paths must be >= folds")
    import hashlib

    ordered = sorted(
        range(len(paths)),
        key=lambda index: hashlib.sha256(paths[index].encode("utf-8")).digest(),
    )
    buckets: list[list[int]] = [[] for _ in range(folds)]
    for position, index in enumerate(ordered):
        buckets[position % folds].append(index)
    return [np.asarray(bucket, dtype=np.int64) for bucket in buckets]


def complement_indices(size: int, validation: np.ndarray) -> np.ndarray:
    mask = np.ones(size, dtype=bool)
    mask[np.asarray(validation, dtype=np.int64)] = False
    return np.flatnonzero(mask)


def row_cosine(reference: np.ndarray, candidate: np.ndarray) -> float:
    reference = l2_rows(reference)
    candidate = l2_rows(candidate)
    if reference.shape != candidate.shape:
        raise ValueError("reference and candidate must have the same shape")
    return float(np.mean(np.sum(reference * candidate, axis=1)))


def coordinate_rmse(reference: np.ndarray, candidate: np.ndarray) -> float:
    reference = _as_2d(reference, "reference")
    candidate = _as_2d(candidate, "candidate")
    if reference.shape != candidate.shape:
        raise ValueError("reference and candidate must have the same shape")
    return float(np.sqrt(np.mean((reference - candidate) ** 2)))


def _pairwise_distances(x: np.ndarray) -> np.ndarray:
    x = _as_2d(x, "x")
    squared = np.sum(x * x, axis=1, keepdims=True)
    distances_sq = np.maximum(squared + squared.T - 2.0 * (x @ x.T), 0.0)
    return np.sqrt(distances_sq)


def local_distance_correlation(reference: np.ndarray, candidate: np.ndarray) -> float:
    reference_distances = _pairwise_distances(reference)
    candidate_distances = _pairwise_distances(candidate)
    indices = np.triu_indices(len(reference_distances), k=1)
    a = reference_distances[indices]
    b = candidate_distances[indices]
    if len(a) < 2 or np.std(a) <= 1e-12 or np.std(b) <= 1e-12:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def knn_overlap(reference: np.ndarray, candidate: np.ndarray, *, k: int) -> float:
    reference = _as_2d(reference, "reference")
    candidate = _as_2d(candidate, "candidate")
    if len(reference) != len(candidate):
        raise ValueError("reference and candidate must have the same row count")
    if not 1 <= k < len(reference):
        raise ValueError("k must be between 1 and n_rows - 1")

    def neighborhoods(x: np.ndarray) -> list[set[int]]:
        distances = _pairwise_distances(x)
        np.fill_diagonal(distances, np.inf)
        nearest = np.argsort(distances, axis=1)[:, :k]
        return [set(int(value) for value in row) for row in nearest]

    left = neighborhoods(reference)
    right = neighborhoods(candidate)
    return float(np.mean([len(a & b) / k for a, b in zip(left, right, strict=True)]))


def summarize_metrics(
    reference: np.ndarray,
    candidate: np.ndarray,
    *,
    knn_values: Iterable[int] = (3, 5),
) -> dict[str, float]:
    result = {
        "coordinate_rmse": coordinate_rmse(reference, candidate),
        "canonical_cosine": row_cosine(reference, candidate),
        "local_distance_correlation": local_distance_correlation(reference, candidate),
    }
    for k in knn_values:
        if k < len(reference):
            result[f"knn_overlap_k{k}"] = knn_overlap(reference, candidate, k=k)
    return result
