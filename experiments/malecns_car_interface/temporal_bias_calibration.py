"""Reality-bounded temporal alignment and persistent cross-modal bias calibration.

The calibrator is modality-generic. It consumes two observations of the same
physical scalar at the same measurement time (for example OBD-II speed and a
later-arriving GNSS fix whose timestamp points back to that instant). It never
accepts simulator truth, a fault label, future state, or privileged pose.
"""

from __future__ import annotations

from dataclasses import dataclass


def _clip(value: float, radius: float) -> float:
    if radius <= 0.0:
        raise ValueError("radius must be positive")
    return max(-radius, min(radius, value))


@dataclass
class PersistentBiasCalibrator:
    """Estimate a persistent signed reference-sensor bias from matched-time residuals.

    ``observe(reference_value, corroborator_value)`` must receive measurements that
    refer to the same physical time. The estimator uses clipped EWMA updates and a
    persistence gate so ordinary zero-mean sensor noise does not immediately create a
    correction. ``correction`` can be subtracted from current reference measurements.
    """

    alpha: float = 0.15
    clip_radius: float = 1.0
    deadband: float = 0.35
    evidence_residual: float = 0.60
    min_evidence: int = 4
    bias_hat: float = 0.0
    evidence: int = 0

    def __post_init__(self) -> None:
        if not 0.0 < self.alpha <= 1.0:
            raise ValueError("alpha must be in (0, 1]")
        if self.clip_radius <= 0.0:
            raise ValueError("clip_radius must be positive")
        if self.deadband < 0.0 or self.evidence_residual < 0.0:
            raise ValueError("deadband/evidence_residual must be non-negative")
        if self.min_evidence < 1:
            raise ValueError("min_evidence must be >= 1")

    @property
    def active(self) -> bool:
        return self.evidence >= self.min_evidence and abs(self.bias_hat) > self.deadband

    @property
    def correction(self) -> float:
        return self.bias_hat if self.active else 0.0

    def observe(self, reference_value: float, corroborator_value: float) -> float:
        """Update from a lawful matched-time residual and return current correction."""

        residual = reference_value - corroborator_value
        if abs(residual) >= self.evidence_residual:
            if self.bias_hat == 0.0 or residual * self.bias_hat >= 0.0:
                self.evidence = min(self.min_evidence + 3, self.evidence + 1)
            else:
                self.evidence = max(0, self.evidence - 2)
        else:
            self.evidence = max(0, self.evidence - 1)

        innovation = _clip(residual - self.bias_hat, self.clip_radius)
        self.bias_hat += self.alpha * innovation
        return self.correction

    def apply(self, reference_value: float) -> float:
        """Remove only the currently evidenced persistent bias estimate."""

        return reference_value - self.correction
