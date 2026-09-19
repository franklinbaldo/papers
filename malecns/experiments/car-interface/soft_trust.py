"""Reality-bounded soft robust fusion for already-paid sensor probes.

Unlike hard probe admission, this module never needs to make a binary accept/reject
decision. A candidate report is always retained, but its incremental influence is
shrunk as it becomes stale or inconsistent with the currently available lawful
cross-modal estimate.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from colony import SpecialistReport, freshness_weighted_value, summarize_modality


def soft_probe_weight(
    existing_reports: Iterable[SpecialistReport],
    candidate: SpecialistReport,
    other_modality_reports: Iterable[SpecialistReport],
    *,
    residual_scale: float = 0.75,
    half_life_ms: float = 150.0,
) -> float:
    """Return a smooth bounded-influence weight using lawful report observables.

    The weight combines declared confidence, timestamp-derived freshness and a
    Cauchy residual weight around the current cross-modal estimate. It receives no
    hidden truth, simulator-only state or fault label.
    """

    existing = list(existing_reports)
    other = list(other_modality_reports)
    if not existing or not other:
        raise ValueError("soft trust requires existing and cross-modal reports")
    if residual_scale <= 0.0:
        raise ValueError("residual_scale must be positive")
    if half_life_ms <= 0.0:
        raise ValueError("half_life_ms must be positive")

    channels = {candidate.channel}
    channels.update(report.channel for report in existing)
    channels.update(report.channel for report in other)
    if len(channels) != 1:
        raise ValueError("soft trust requires one shared semantic channel")

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
    current_estimate = freshness_weighted_value(
        [existing_summary, other_summary], half_life_ms=half_life_ms
    )

    freshness = 2 ** (-candidate.age_ms / half_life_ms)
    residual = abs(candidate.value - current_estimate)
    cauchy_weight = 1.0 / (1.0 + (residual / residual_scale) ** 2)
    return candidate.confidence * freshness * cauchy_weight


def soften_probe(
    existing_reports: Iterable[SpecialistReport],
    candidate: SpecialistReport,
    other_modality_reports: Iterable[SpecialistReport],
    *,
    residual_scale: float = 0.75,
    half_life_ms: float = 150.0,
    confidence_floor: float = 0.05,
) -> SpecialistReport:
    """Return a retained report whose incremental influence is smoothly bounded.

    The candidate remains present rather than being rejected. Its value is shrunk
    toward the current lawful fused estimate and its declared confidence is reduced
    by the same robust weight so downstream modality fusion also sees the lower
    reliability.
    """

    if not 0.0 <= confidence_floor <= 1.0:
        raise ValueError("confidence_floor must be in [0, 1]")

    existing = list(existing_reports)
    other = list(other_modality_reports)
    weight = soft_probe_weight(
        existing,
        candidate,
        other,
        residual_scale=residual_scale,
        half_life_ms=half_life_ms,
    )
    existing_summary = summarize_modality(existing, specialist_id="existing-summary")
    other_summary = summarize_modality(other, specialist_id="other-summary")
    current_estimate = freshness_weighted_value(
        [existing_summary, other_summary], half_life_ms=half_life_ms
    )
    softened_value = current_estimate + weight * (candidate.value - current_estimate)
    softened_confidence = max(confidence_floor, candidate.confidence * weight)
    return replace(
        candidate,
        value=softened_value,
        confidence=softened_confidence,
    )
