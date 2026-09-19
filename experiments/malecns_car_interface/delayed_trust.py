"""Learned reality-bounded trust gate for already-paid sensor specialists.

The model only receives features derived from observed specialist reports. Training
supervision may arrive later from an independent, physically reproducible
corroborating channel; hidden simulator truth is not a model input.
"""

from __future__ import annotations

from math import exp
from typing import Iterable, Sequence

from colony import (
    SpecialistReport,
    disagreement,
    freshness_weighted_value,
    summarize_modality,
)

FEATURE_DIM = 11


def _clip_unit(value: float) -> float:
    return max(0.0, min(1.0, value))


def delayed_trust_features(
    existing_reports: Iterable[SpecialistReport],
    candidate: SpecialistReport,
    other_modality_reports: Iterable[SpecialistReport],
    *,
    half_life_ms: float = 150.0,
    agreement_scale: float = 0.35,
) -> tuple[float, ...]:
    """Build generic decision-time features from lawful report metadata only."""

    existing = list(existing_reports)
    other = list(other_modality_reports)
    if not existing or not other:
        raise ValueError("delayed trust requires existing and cross-modal reports")
    if half_life_ms <= 0.0:
        raise ValueError("half_life_ms must be positive")
    if agreement_scale <= 0.0:
        raise ValueError("agreement_scale must be positive")

    channels = {candidate.channel}
    channels.update(report.channel for report in existing)
    channels.update(report.channel for report in other)
    if len(channels) != 1:
        raise ValueError("delayed trust requires one shared semantic channel")

    existing_modalities = {report.modality for report in existing}
    other_modalities = {report.modality for report in other}
    if len(existing_modalities) != 1 or None in existing_modalities:
        raise ValueError("existing reports require one declared modality")
    if len(other_modalities) != 1 or None in other_modalities:
        raise ValueError("other reports require one declared modality")
    if candidate.modality != next(iter(existing_modalities)):
        raise ValueError("candidate modality must match existing reports")
    if candidate.modality == next(iter(other_modalities)):
        raise ValueError("cross-modal reports must come from another modality")

    existing_summary = summarize_modality(existing, specialist_id="existing-summary")
    other_summary = summarize_modality(other, specialist_id="other-summary")
    fused = freshness_weighted_value(
        [existing_summary, other_summary], half_life_ms=half_life_ms
    )

    freshness = 2 ** (-candidate.age_ms / half_life_ms)
    within_residual = abs(candidate.value - existing_summary.value)
    cross_residual = abs(candidate.value - other_summary.value)
    fused_residual = abs(candidate.value - fused)
    within_disagreement = disagreement(existing)
    cross_modal_residual = abs(existing_summary.value - other_summary.value)
    agreement = exp(-fused_residual / agreement_scale)

    return (
        1.0,
        candidate.confidence,
        freshness,
        _clip_unit(candidate.age_ms / 900.0),
        _clip_unit(within_residual / 2.0),
        _clip_unit(cross_residual / 2.0),
        _clip_unit(fused_residual / 2.0),
        _clip_unit(within_disagreement),
        _clip_unit(cross_modal_residual / 2.0),
        candidate.confidence * freshness,
        freshness * agreement,
    )


class DelayedTrustModel:
    """Tiny online logistic baseline to beat with a MaleCNS coordinator."""

    def __init__(
        self,
        *,
        feature_dim: int = FEATURE_DIM,
        learning_rate: float = 0.03,
        l2: float = 0.001,
    ) -> None:
        if feature_dim <= 0:
            raise ValueError("feature_dim must be positive")
        if learning_rate <= 0.0:
            raise ValueError("learning_rate must be positive")
        if l2 < 0.0:
            raise ValueError("l2 must be non-negative")
        self.weights = [0.0] * feature_dim
        self.learning_rate = learning_rate
        self.l2 = l2

    def probability(self, features: Sequence[float]) -> float:
        if len(features) != len(self.weights):
            raise ValueError("feature length does not match model")
        z = sum(weight * value for weight, value in zip(self.weights, features))
        if z >= 0.0:
            return 1.0 / (1.0 + exp(-z))
        ez = exp(z)
        return ez / (1.0 + ez)

    def update(self, features: Sequence[float], label: float) -> float:
        """Apply one logistic SGD update and return the pre-update probability."""

        if label not in (0.0, 1.0):
            raise ValueError("label must be 0.0 or 1.0")
        probability = self.probability(features)
        error = probability - label
        for index, value in enumerate(features):
            gradient = error * value + self.l2 * self.weights[index]
            self.weights[index] -= self.learning_rate * gradient
        return probability

    def should_trust(self, features: Sequence[float], *, threshold: float) -> bool:
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold must be in [0, 1]")
        return self.probability(features) >= threshold
