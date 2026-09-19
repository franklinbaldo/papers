"""Reality-bounded age-normalized Huber fusion for already-paid probes.

This is a stronger statistical control for the MaleCNS car colony. It keeps every
paid specialist report but bounds incremental influence with a Huber weight whose
residual scale contracts as the candidate becomes stale. The only inputs are
report values, declared confidence, timestamps/freshness, modality identity and a
lawful cross-modal estimate. No simulator truth, fault label, pose oracle or hidden
world state is accepted by the API.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from colony import SpecialistReport, freshness_weighted_value, summarize_modality


def _current_cross_modal_estimate(
    existing_reports: Iterable[SpecialistReport],
    other_modality_reports: Iterable[SpecialistReport],
    *,
    half_life_ms: float,
) -> tuple[list[SpecialistReport], list[SpecialistReport], float]:
    existing = list(existing_reports)
    other = list(other_modality_reports)
    if not existing or not other:
        raise ValueError("adaptive soft trust requires existing and cross-modal reports")
    if half_life_ms <= 0.0:
        raise ValueError("half_life_ms must be positive")

    channels = {report.channel for report in existing + other}
    if len(channels) != 1:
        raise ValueError("adaptive soft trust requires one shared semantic channel")

    existing_modalities = {report.modality for report in existing}
    other_modalities = {report.modality for report in other}
    if len(existing_modalities) != 1 or None in existing_modalities:
        raise ValueError("existing reports require one declared modality")
    if len(other_modalities) != 1 or None in other_modalities:
        raise ValueError("other reports require one declared modality")
    if existing_modalities == other_modalities:
        raise ValueError("cross-modal reports must come from another modality")

    existing_summary = summarize_modality(existing, specialist_id="existing-summary")
    other_summary = summarize_modality(other, specialist_id="other-summary")
    estimate = freshness_weighted_value(
        [existing_summary, other_summary], half_life_ms=half_life_ms
    )
    return existing, other, estimate


def age_normalized_huber_weight(
    existing_reports: Iterable[SpecialistReport],
    candidate: SpecialistReport,
    other_modality_reports: Iterable[SpecialistReport],
    *,
    base_scale: float = 0.35,
    age_power: float = 1.0,
    min_scale: float = 0.03,
    half_life_ms: float = 150.0,
) -> float:
    """Return a smooth Huber influence weight from lawful observables only.

    ``base_scale`` is the residual radius for a fresh report. The effective radius
    contracts with timestamp-derived freshness, so stale reports must agree more
    closely with the currently available cross-modal estimate before receiving the
    same influence. This encodes a physical fact rather than a hidden failure flag:
    old measurements are less informative about a changing world.
    """

    if base_scale <= 0.0:
        raise ValueError("base_scale must be positive")
    if age_power < 0.0:
        raise ValueError("age_power must be non-negative")
    if min_scale <= 0.0:
        raise ValueError("min_scale must be positive")

    existing, other, estimate = _current_cross_modal_estimate(
        existing_reports,
        other_modality_reports,
        half_life_ms=half_life_ms,
    )
    existing_modality = existing[0].modality
    if candidate.modality != existing_modality:
        raise ValueError("candidate modality must match existing reports")
    if candidate.channel != existing[0].channel:
        raise ValueError("candidate channel must match existing reports")

    freshness = 2 ** (-candidate.age_ms / half_life_ms)
    effective_scale = max(min_scale, base_scale * freshness**age_power)
    residual = abs(candidate.value - estimate)
    huber = 1.0 if residual <= effective_scale else effective_scale / residual
    return candidate.confidence * freshness * huber


def soften_probe_huber(
    existing_reports: Iterable[SpecialistReport],
    candidate: SpecialistReport,
    other_modality_reports: Iterable[SpecialistReport],
    *,
    base_scale: float = 0.35,
    age_power: float = 1.0,
    min_scale: float = 0.03,
    half_life_ms: float = 150.0,
    confidence_floor: float = 0.05,
) -> SpecialistReport:
    """Retain a paid candidate while bounding how much it can move the estimate."""

    if not 0.0 <= confidence_floor <= 1.0:
        raise ValueError("confidence_floor must be in [0, 1]")

    existing, other, estimate = _current_cross_modal_estimate(
        existing_reports,
        other_modality_reports,
        half_life_ms=half_life_ms,
    )
    weight = age_normalized_huber_weight(
        existing,
        candidate,
        other,
        base_scale=base_scale,
        age_power=age_power,
        min_scale=min_scale,
        half_life_ms=half_life_ms,
    )
    softened_value = estimate + weight * (candidate.value - estimate)
    softened_confidence = max(confidence_floor, candidate.confidence * weight)
    return replace(
        candidate,
        value=softened_value,
        confidence=softened_confidence,
    )
