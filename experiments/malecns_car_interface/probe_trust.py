"""Reality-bounded probe-then-trust primitives for the MaleCNS sensor colony.

A probe may reveal a specialist report without automatically admitting that report
into the actuator-facing fusion path. Trust scoring uses only already observed,
physically reproducible specialist outputs and timestamp/confidence metadata.
"""

from __future__ import annotations

from math import exp
from typing import Iterable

from colony import (
    SpecialistReport,
    freshness_weighted_value,
    summarize_modality,
)


def probe_trust_score(
    existing_reports: Iterable[SpecialistReport],
    candidate: SpecialistReport,
    other_modality_reports: Iterable[SpecialistReport],
    *,
    half_life_ms: float = 150.0,
    agreement_scale: float = 0.35,
) -> float:
    """Score whether an already-paid-for candidate should enter fusion.

    The score is the product of declared confidence, temporal freshness and
    agreement with the colony's current cross-modal estimate. It never receives
    hidden truth, a fault flag, simulator geometry or the candidate's realized
    future error.
    """

    existing = list(existing_reports)
    other = list(other_modality_reports)
    if not existing or not other:
        raise ValueError("probe trust requires existing and cross-modal reports")
    if half_life_ms <= 0.0:
        raise ValueError("half_life_ms must be positive")
    if agreement_scale <= 0.0:
        raise ValueError("agreement_scale must be positive")

    channels = {candidate.channel}
    channels.update(report.channel for report in existing)
    channels.update(report.channel for report in other)
    if len(channels) != 1:
        raise ValueError("probe trust requires one shared semantic channel")

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

    existing_summary = summarize_modality(
        existing, specialist_id=f"{candidate.modality}-trusted-summary"
    )
    other_summary = summarize_modality(other, specialist_id="other-trusted-summary")
    current_estimate = freshness_weighted_value(
        [existing_summary, other_summary], half_life_ms=half_life_ms
    )

    freshness = 2 ** (-candidate.age_ms / half_life_ms)
    agreement = exp(-abs(candidate.value - current_estimate) / agreement_scale)
    return candidate.confidence * freshness * agreement


def should_trust_probe(
    existing_reports: Iterable[SpecialistReport],
    candidate: SpecialistReport,
    other_modality_reports: Iterable[SpecialistReport],
    *,
    threshold: float,
    half_life_ms: float = 150.0,
    agreement_scale: float = 0.35,
) -> bool:
    """Return whether a probed specialist is admitted into fusion."""

    if threshold < 0.0:
        raise ValueError("threshold must be non-negative")
    return probe_trust_score(
        existing_reports,
        candidate,
        other_modality_reports,
        half_life_ms=half_life_ms,
        agreement_scale=agreement_scale,
    ) >= threshold
