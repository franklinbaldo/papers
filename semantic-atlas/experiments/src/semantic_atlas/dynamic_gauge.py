from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from typing import Iterable

import numpy as np


_EPS = 1e-12


@dataclass(frozen=True)
class FrozenFieldSpec:
    """Fully frozen artificial field specification for DGCT.

    The specification is intentionally independent of model transition data.  A
    serialized spec can be hashed and persisted before any evaluation dynamics
    are exposed.
    """

    family: str
    dim: int
    seed: int = 0
    scale: float = 1.0
    strength: float = 1.0

    def __post_init__(self) -> None:
        if self.family not in {
            "zero",
            "vortex_smooth",
            "random_divergence_free",
            "radial_gradient",
        }:
            raise ValueError(f"unsupported field family: {self.family}")
        if self.dim < 2:
            raise ValueError("dim must be >= 2")
        if self.scale <= 0:
            raise ValueError("scale must be > 0")
        if self.strength < 0:
            raise ValueError("strength must be >= 0")

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @property
    def fingerprint(self) -> str:
        payload = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _validate_points(points: np.ndarray, dim: int, *, name: str) -> np.ndarray:
    values = np.asarray(points, dtype=np.float64)
    if values.ndim != 2 or values.shape[1] != dim:
        raise ValueError(f"{name} must have shape [n, {dim}]")
    return values


def _simple_vortex_generator(dim: int, seed: int) -> np.ndarray:
    """Sparse antisymmetric generator fixed only by dimension and seed."""
    rng = np.random.default_rng(seed)
    order = rng.permutation(dim)
    generator = np.zeros((dim, dim), dtype=np.float64)
    for offset in range(0, dim - 1, 2):
        i = int(order[offset])
        j = int(order[offset + 1])
        chirality = 1.0 if rng.integers(0, 2) else -1.0
        generator[i, j] = -chirality
        generator[j, i] = chirality
    if dim % 2 == 1:
        i = int(order[-1])
        j = int(order[0])
        chirality = 1.0 if rng.integers(0, 2) else -1.0
        generator[i, j] += -chirality / np.sqrt(2.0)
        generator[j, i] += chirality / np.sqrt(2.0)
    return generator


def _dense_antisymmetric_generator(dim: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    raw = rng.standard_normal((dim, dim))
    generator = raw - raw.T
    fro = float(np.linalg.norm(generator))
    if fro <= _EPS:
        raise RuntimeError("degenerate antisymmetric generator")
    return generator * (np.sqrt(dim) / fro)


def evaluate_field(
    points: np.ndarray,
    centers: np.ndarray,
    spec: FrozenFieldSpec,
) -> np.ndarray:
    """Evaluate a frozen artificial field at canonical states.

    `vortex_smooth` and `random_divergence_free` are sums of radially enveloped
    antisymmetric fields around the supplied artificial quasar centers.  For an
    antisymmetric matrix A and radial envelope g(||r||),

        div(g A r) = grad(g) . A r + g tr(A) = 0,

    because r . A r = 0 and tr(A) = 0.  Their finite superposition therefore
    remains divergence-free in the canonical Euclidean coordinates.
    """
    q = _validate_points(points, spec.dim, name="points")
    c = _validate_points(centers, spec.dim, name="centers")
    if len(c) == 0:
        raise ValueError("centers must be non-empty")
    if spec.family == "zero" or spec.strength == 0:
        return np.zeros_like(q)

    if spec.family == "vortex_smooth":
        generator = _simple_vortex_generator(spec.dim, spec.seed)
    elif spec.family == "random_divergence_free":
        generator = _dense_antisymmetric_generator(spec.dim, spec.seed)
    else:
        generator = None

    result = np.zeros_like(q)
    scale2 = spec.scale * spec.scale
    center_norm = np.sqrt(float(len(c)))
    for center in c:
        rel = q - center
        radius2 = np.sum(rel * rel, axis=1)
        envelope = np.exp(-radius2 / (2.0 * scale2))[:, None]
        if spec.family == "radial_gradient":
            # Gradient of a Gaussian potential, up to the frozen strength.
            local = -(rel / scale2) * envelope
        else:
            local = (rel @ generator.T) * envelope
        result += local

    return (spec.strength / center_norm) * result


def _basis_matrix(states: np.ndarray, basis: str) -> np.ndarray:
    states = np.asarray(states, dtype=np.float64)
    if basis == "constant":
        return np.ones((len(states), 1), dtype=np.float64)
    if basis == "affine":
        return np.column_stack(
            [np.ones(len(states), dtype=np.float64), states / np.sqrt(states.shape[1])]
        )
    raise ValueError(f"unsupported amplitude basis: {basis}")


@dataclass(frozen=True)
class AmplitudeFit:
    basis: str
    coefficients: np.ndarray
    ridge: float

    def predict(self, states: np.ndarray) -> np.ndarray:
        phi = _basis_matrix(states, self.basis)
        return phi @ self.coefficients


def fit_amplitude(
    states: np.ndarray,
    dynamics: np.ndarray,
    field: np.ndarray,
    *,
    basis: str = "constant",
    ridge: float = 1e-8,
) -> AmplitudeFit:
    """Fit the low-capacity scalar amplitude a(q) in F ~= a(q) V(q)."""
    q = np.asarray(states, dtype=np.float64)
    f = np.asarray(dynamics, dtype=np.float64)
    v = np.asarray(field, dtype=np.float64)
    if q.ndim != 2 or f.shape != q.shape or v.shape != q.shape:
        raise ValueError("states, dynamics, and field must have equal [n, dim] shape")
    if len(q) == 0:
        raise ValueError("cannot fit amplitude on an empty sample")
    if ridge < 0:
        raise ValueError("ridge must be >= 0")

    phi = _basis_matrix(q, basis)
    design = (v[:, :, None] * phi[:, None, :]).reshape(-1, phi.shape[1])
    target = f.reshape(-1)
    gram = design.T @ design
    rhs = design.T @ target
    penalty = ridge * np.eye(gram.shape[0], dtype=np.float64)
    coefficients = np.linalg.solve(gram + penalty, rhs)
    return AmplitudeFit(basis=basis, coefficients=coefficients, ridge=ridge)


def residuals(
    states: np.ndarray,
    dynamics: np.ndarray,
    field: np.ndarray,
    fit: AmplitudeFit,
) -> np.ndarray:
    q = np.asarray(states, dtype=np.float64)
    f = np.asarray(dynamics, dtype=np.float64)
    v = np.asarray(field, dtype=np.float64)
    if q.shape != f.shape or q.shape != v.shape:
        raise ValueError("states, dynamics, and field must have equal shape")
    amplitude = fit.predict(q)
    return f - amplitude[:, None] * v


def effective_rank(values: np.ndarray) -> float:
    """Entropy effective rank of the centered sample covariance spectrum."""
    x = np.asarray(values, dtype=np.float64)
    if x.ndim != 2 or len(x) < 2:
        return 0.0
    centered = x - x.mean(axis=0, keepdims=True)
    singular = np.linalg.svd(centered, compute_uv=False)
    power = singular * singular
    total = float(np.sum(power))
    if total <= _EPS:
        return 0.0
    probabilities = power / total
    entropy = -float(np.sum(probabilities * np.log(np.maximum(probabilities, _EPS))))
    return float(np.exp(entropy))


def _ridge_predict(
    train_states: np.ndarray,
    train_targets: np.ndarray,
    test_states: np.ndarray,
    *,
    ridge: float,
) -> np.ndarray:
    x_train = _basis_matrix(train_states, "affine")
    x_test = _basis_matrix(test_states, "affine")
    gram = x_train.T @ x_train + ridge * np.eye(x_train.shape[1], dtype=np.float64)
    weights = np.linalg.solve(gram, x_train.T @ train_targets)
    return x_test @ weights


def _relative_prediction_mse(
    train_states: np.ndarray,
    train_targets: np.ndarray,
    test_states: np.ndarray,
    test_targets: np.ndarray,
    *,
    ridge: float,
) -> float:
    prediction = _ridge_predict(
        train_states, train_targets, test_states, ridge=ridge
    )
    mse = float(np.mean((prediction - test_targets) ** 2))
    baseline = float(np.mean((test_targets - train_targets.mean(axis=0)) ** 2))
    return mse / max(baseline, _EPS)


def sample_complexity_curve(
    train_states: np.ndarray,
    train_targets: np.ndarray,
    test_states: np.ndarray,
    test_targets: np.ndarray,
    *,
    sample_fractions: Iterable[float] = (0.25, 0.5, 1.0),
    ridge: float = 1e-6,
    target_relative_mse: float = 0.8,
) -> dict[str, object]:
    q_train = np.asarray(train_states, dtype=np.float64)
    y_train = np.asarray(train_targets, dtype=np.float64)
    q_test = np.asarray(test_states, dtype=np.float64)
    y_test = np.asarray(test_targets, dtype=np.float64)
    if q_train.shape != y_train.shape or q_test.shape != y_test.shape:
        raise ValueError("state and target shapes must match within each split")
    if len(q_train) < 2 or len(q_test) < 1:
        raise ValueError("sample-complexity curve needs >=2 train and >=1 test samples")

    curve: list[dict[str, float | int]] = []
    hit: int | None = None
    for fraction in sample_fractions:
        fraction = float(fraction)
        if not 0 < fraction <= 1:
            raise ValueError("sample fractions must lie in (0, 1]")
        count = max(2, min(len(q_train), int(np.ceil(len(q_train) * fraction))))
        relative = _relative_prediction_mse(
            q_train[:count], y_train[:count], q_test, y_test, ridge=ridge
        )
        curve.append(
            {"fraction": fraction, "sample_count": count, "relative_mse": relative}
        )
        if hit is None and relative <= target_relative_mse:
            hit = count
    return {
        "target_relative_mse": float(target_relative_mse),
        "sample_count_at_target": hit,
        "curve": curve,
    }


def local_sensitivity(states: np.ndarray, values: np.ndarray) -> float:
    """Median nearest-neighbor Lipschitz ratio on observed support."""
    q = np.asarray(states, dtype=np.float64)
    y = np.asarray(values, dtype=np.float64)
    if q.shape != y.shape or len(q) < 2:
        return 0.0
    delta = q[:, None, :] - q[None, :, :]
    distances = np.linalg.norm(delta, axis=2)
    np.fill_diagonal(distances, np.inf)
    neighbor = np.argmin(distances, axis=1)
    ratios = []
    for i, j in enumerate(neighbor):
        denominator = float(np.linalg.norm(q[i] - q[j]))
        numerator = float(np.linalg.norm(y[i] - y[j]))
        if denominator > _EPS:
            ratios.append(numerator / denominator)
    return float(np.median(ratios)) if ratios else 0.0


def complexity_metrics(
    train_states: np.ndarray,
    train_values: np.ndarray,
    test_states: np.ndarray,
    test_values: np.ndarray,
    *,
    sample_fractions: Iterable[float] = (0.25, 0.5, 1.0),
    predictor_ridge: float = 1e-6,
    target_relative_mse: float = 0.8,
) -> dict[str, object]:
    y_train = np.asarray(train_values, dtype=np.float64)
    y_test = np.asarray(test_values, dtype=np.float64)
    if y_train.ndim != 2 or y_test.ndim != 2:
        raise ValueError("complexity metrics expect 2D target arrays")
    train_energy = float(np.mean(np.sum(y_train * y_train, axis=1)))
    test_energy = float(np.mean(np.sum(y_test * y_test, axis=1)))
    return {
        "train_energy": train_energy,
        "test_energy": test_energy,
        "train_effective_rank": effective_rank(y_train),
        "test_effective_rank": effective_rank(y_test),
        "train_local_sensitivity": local_sensitivity(train_states, y_train),
        "test_local_sensitivity": local_sensitivity(test_states, y_test),
        "sample_complexity": sample_complexity_curve(
            train_states,
            y_train,
            test_states,
            y_test,
            sample_fractions=sample_fractions,
            ridge=predictor_ridge,
            target_relative_mse=target_relative_mse,
        ),
    }


def paired_concordance(a: np.ndarray, b: np.ndarray) -> dict[str, float]:
    """Cross-observer agreement for row-paired dynamics in the common SRF."""
    x = np.asarray(a, dtype=np.float64)
    y = np.asarray(b, dtype=np.float64)
    if x.shape != y.shape or x.ndim != 2:
        raise ValueError("paired arrays must have equal 2D shape")
    x_norm = np.linalg.norm(x, axis=1)
    y_norm = np.linalg.norm(y, axis=1)
    cosine = np.sum(x * y, axis=1) / np.maximum(x_norm * y_norm, _EPS)
    scale = max(
        float(np.sqrt(np.mean(x * x))),
        float(np.sqrt(np.mean(y * y))),
        _EPS,
    )
    normalized_rmse = float(np.sqrt(np.mean((x - y) ** 2)) / scale)

    if len(x) < 3:
        pairwise_corr = float("nan")
    else:
        upper = np.triu_indices(len(x), k=1)
        dx = np.linalg.norm(x[:, None, :] - x[None, :, :], axis=2)[upper]
        dy = np.linalg.norm(y[:, None, :] - y[None, :, :], axis=2)[upper]
        if np.std(dx) <= _EPS or np.std(dy) <= _EPS:
            pairwise_corr = float("nan")
        else:
            pairwise_corr = float(np.corrcoef(dx, dy)[0, 1])
    return {
        "mean_row_cosine": float(np.mean(cosine)),
        "normalized_rmse": normalized_rmse,
        "pairwise_distance_correlation": pairwise_corr,
    }


def compression_report(
    train_states: np.ndarray,
    train_dynamics: np.ndarray,
    test_states: np.ndarray,
    test_dynamics: np.ndarray,
    centers: np.ndarray,
    spec: FrozenFieldSpec,
    *,
    amplitude_basis: str = "constant",
    amplitude_ridge: float = 1e-8,
    predictor_ridge: float = 1e-6,
    sample_fractions: Iterable[float] = (0.25, 0.5, 1.0),
    target_relative_mse: float = 0.8,
) -> dict[str, object]:
    train_field = evaluate_field(train_states, centers, spec)
    test_field = evaluate_field(test_states, centers, spec)
    fit = fit_amplitude(
        train_states,
        train_dynamics,
        train_field,
        basis=amplitude_basis,
        ridge=amplitude_ridge,
    )
    train_residual = residuals(train_states, train_dynamics, train_field, fit)
    test_residual = residuals(test_states, test_dynamics, test_field, fit)
    raw = complexity_metrics(
        train_states,
        train_dynamics,
        test_states,
        test_dynamics,
        sample_fractions=sample_fractions,
        predictor_ridge=predictor_ridge,
        target_relative_mse=target_relative_mse,
    )
    residual = complexity_metrics(
        train_states,
        train_residual,
        test_states,
        test_residual,
        sample_fractions=sample_fractions,
        predictor_ridge=predictor_ridge,
        target_relative_mse=target_relative_mse,
    )
    raw_test_energy = float(raw["test_energy"])
    residual_test_energy = float(residual["test_energy"])
    return {
        "field_spec": spec.to_dict(),
        "field_fingerprint": spec.fingerprint,
        "amplitude": {
            "basis": fit.basis,
            "ridge": fit.ridge,
            "coefficients": fit.coefficients.tolist(),
        },
        "raw": raw,
        "residual": residual,
        "test_energy_ratio": residual_test_energy / max(raw_test_energy, _EPS),
        "test_effective_rank_ratio": float(residual["test_effective_rank"])
        / max(float(raw["test_effective_rank"]), _EPS),
        "train_residuals": train_residual,
        "test_residuals": test_residual,
    }
