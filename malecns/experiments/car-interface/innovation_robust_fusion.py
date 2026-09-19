"""Reality-bounded online innovation scale and standardized robust fusion.

This module consumes only matched-time residuals, signal ages, and declared
channel noise metadata available to a real car/phone interface. It never accepts
simulator truth, fault identity, future state, or privileged pose.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from temporal_robust_fusion import freshness, huber_weight


@dataclass
class OnlineInnovationScale:
    """Robust EWMA scale estimate for matched-time cross-modal innovations."""

    alpha: float = 0.08
    initial_sigma: float = 0.50
    floor_sigma: float = 0.25
    ceiling_sigma: float = 2.0
    clip_sigma: float = 3.0

    def __post_init__(self) -> None:
        if not 0.0 < self.alpha <= 1.0:
            raise ValueError("alpha must be in (0, 1]")
        for name in ("initial_sigma", "floor_sigma", "ceiling_sigma", "clip_sigma"):
            if getattr(self, name) <= 0.0:
                raise ValueError(f"{name} must be positive")
        if self.floor_sigma > self.ceiling_sigma:
            raise ValueError("floor_sigma must not exceed ceiling_sigma")
        self._second_moment = self.initial_sigma**2

    @property
    def sigma(self) -> float:
        variance = max(
            self.floor_sigma**2,
            min(self.ceiling_sigma**2, self._second_moment),
        )
        return math.sqrt(variance)

    def standardized(self, residual: float) -> float:
        return residual / self.sigma

    def observe(self, residual: float) -> float:
        radius = self.clip_sigma * self.sigma
        clipped = max(-radius, min(radius, residual))
        self._second_moment = (
            (1.0 - self.alpha) * self._second_moment
            + self.alpha * clipped**2
        )
        return self.sigma


def innovation_huber_weight(
    *,
    age_s: float,
    matched_time_residual: float,
    innovation_sigma: float,
    huber_k: float = 1.345,
    relative_precision: float = 1.0,
    tau_s: float = 1.5,
) -> float:
    """Freshness × relative precision × Huber weight in innovation units."""

    if innovation_sigma <= 0.0:
        raise ValueError("innovation_sigma must be positive")
    if huber_k <= 0.0:
        raise ValueError("huber_k must be positive")
    if relative_precision < 0.0:
        raise ValueError("relative_precision must be non-negative")
    standardized = matched_time_residual / innovation_sigma
    return (
        relative_precision
        * freshness(age_s, tau_s=tau_s)
        * huber_weight(standardized, huber_k)
    )


def covariance_relative_precision(
    *,
    raw_innovation_sigma: float,
    reference_nominal_sigma: float,
    candidate_nominal_sigma: float,
    min_precision: float = 0.05,
    max_precision: float = 1.0,
) -> float:
    """Observable scalar covariance merit for a reference/candidate pair.

    Nominal sigmas are declared channel metadata (for example from bench or
    stationary calibration), not simulator state. Excess matched-time innovation
    energy above nominal combined noise is conservatively assigned to the
    reference side, which is the side tracked by the persistent-bias estimator.
    This is a robust scalar baseline, not a full Kalman covariance model.
    """

    if (
        raw_innovation_sigma <= 0.0
        or reference_nominal_sigma <= 0.0
        or candidate_nominal_sigma <= 0.0
    ):
        raise ValueError("sigmas must be positive")
    if min_precision < 0.0 or max_precision < min_precision:
        raise ValueError("invalid precision bounds")

    nominal_combined_variance = (
        reference_nominal_sigma**2 + candidate_nominal_sigma**2
    )
    excess = max(
        0.0,
        raw_innovation_sigma**2 - nominal_combined_variance,
    )
    precision = (
        reference_nominal_sigma**2 + excess
    ) / candidate_nominal_sigma**2
    return max(min_precision, min(max_precision, precision))
