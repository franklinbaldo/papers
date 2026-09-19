"""Minimal contracts and baselines for a colony of MaleCNS sensor specialists."""

from __future__ import annotations

from dataclasses import dataclass
from math import floor
from statistics import median
from typing import Iterable, Mapping


@dataclass(frozen=True)
class SpecialistReport:
    """Small lawful report emitted by one sensor-specialist MaleCNS."""

    specialist_id: str
    channel: str
    value: float
    confidence: float
    novelty: float = 0.0
    age_ms: float = 0.0
    modality: str | None = None

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be in [0, 1]")
        if not 0.0 <= self.novelty <= 1.0:
            raise ValueError("novelty must be in [0, 1]")
        if self.age_ms < 0.0:
            raise ValueError("age_ms must be non-negative")


def median_value(reports: Iterable[SpecialistReport]) -> float:
    """Robust fixed baseline for several specialists interpreting one channel."""

    values = [report.value for report in reports]
    if not values:
        raise ValueError("at least one specialist report is required")
    return float(median(values))


def confidence_weighted_value(reports: Iterable[SpecialistReport]) -> float:
    """Cheap fusion baseline to beat with a learned MaleCNS coordinator."""

    items = list(reports)
    if not items:
        raise ValueError("at least one specialist report is required")
    weight_sum = sum(report.confidence for report in items)
    if weight_sum <= 0.0:
        return median_value(items)
    return sum(report.value * report.confidence for report in items) / weight_sum


def freshness_weighted_value(
    reports: Iterable[SpecialistReport],
    *,
    half_life_ms: float = 150.0,
) -> float:
    """Downweight old specialist reports using only lawful timestamp metadata."""

    items = list(reports)
    if not items:
        raise ValueError("at least one specialist report is required")
    if half_life_ms <= 0.0:
        raise ValueError("half_life_ms must be positive")

    weights = [
        report.confidence * 2 ** (-report.age_ms / half_life_ms)
        for report in items
    ]
    weight_sum = sum(weights)
    if weight_sum <= 0.0:
        return median_value(items)
    return sum(report.value * weight for report, weight in zip(items, weights)) / weight_sum


def consensus_weighted_value(
    reports: Iterable[SpecialistReport],
    *,
    mad_scale: float = 3.0,
    min_radius: float = 0.15,
) -> float:
    """Fuse confidence only inside a robust consensus neighborhood."""

    items = list(reports)
    if not items:
        raise ValueError("at least one specialist report is required")
    if mad_scale < 0.0 or min_radius < 0.0:
        raise ValueError("mad_scale and min_radius must be non-negative")

    center = median_value(items)
    mad = float(median(abs(report.value - center) for report in items))
    radius = max(min_radius, mad_scale * mad)
    inliers = [report for report in items if abs(report.value - center) <= radius]

    weight_sum = sum(report.confidence for report in inliers)
    if weight_sum <= 0.0:
        return center
    return sum(report.value * report.confidence for report in inliers) / weight_sum


def summarize_modality(
    reports: Iterable[SpecialistReport],
    *,
    specialist_id: str,
) -> SpecialistReport:
    """Collapse redundant specialists into one lawful modality-level report."""

    items = list(reports)
    if not items:
        raise ValueError("at least one specialist report is required")

    channels = {report.channel for report in items}
    modalities = {report.modality for report in items}
    if len(channels) != 1:
        raise ValueError("modality summary requires one semantic channel")
    if len(modalities) != 1 or None in modalities:
        raise ValueError("modality summary requires one declared modality")

    return SpecialistReport(
        specialist_id=specialist_id,
        channel=next(iter(channels)),
        value=median_value(items),
        confidence=float(median(report.confidence for report in items)),
        novelty=float(median(report.novelty for report in items)),
        age_ms=float(median(report.age_ms for report in items)),
        modality=next(iter(modalities)),
    )


def disagreement(reports: Iterable[SpecialistReport]) -> float:
    """Mean absolute disagreement around the channel median."""

    items = list(reports)
    if not items:
        raise ValueError("at least one specialist report is required")
    center = median_value(items)
    return sum(abs(report.value - center) for report in items) / len(items)


def age_spread_ms(reports: Iterable[SpecialistReport]) -> float:
    """Return the oldest-minus-newest report age as a coordinator signal."""

    items = list(reports)
    if not items:
        raise ValueError("at least one specialist report is required")
    ages = [report.age_ms for report in items]
    return max(ages) - min(ages)


def recruitment_score(
    reports: Iterable[SpecialistReport],
    *,
    half_life_ms: float = 150.0,
    uncertainty_floor: float = 0.005,
) -> float:
    """Estimate where another specialist could be useful without privileged truth.

    Recruitment targets fresh but epistemically unsettled modalities. Within-
    modality disagreement is a proxy for specialist-level uncertainty, while
    exponential freshness prevents wasting compute on a commonly stale stream.
    Scores are comparable only for modalities estimating the same normalized
    semantic channel.
    """

    items = list(reports)
    if not items:
        raise ValueError("at least one specialist report is required")
    if half_life_ms <= 0.0:
        raise ValueError("half_life_ms must be positive")
    if uncertainty_floor < 0.0:
        raise ValueError("uncertainty_floor must be non-negative")

    channels = {report.channel for report in items}
    modalities = {report.modality for report in items}
    if len(channels) != 1:
        raise ValueError("recruitment score requires one semantic channel")
    if len(modalities) != 1 or None in modalities:
        raise ValueError("recruitment score requires one declared modality")

    age_ms = float(median(report.age_ms for report in items))
    freshness = 2 ** (-age_ms / half_life_ms)
    return freshness * (disagreement(items) + uncertainty_floor)


def allocate_recruitment_slots(
    modality_reports: Mapping[str, Iterable[SpecialistReport]],
    *,
    extra_slots: int,
    half_life_ms: float = 150.0,
    uncertainty_floor: float = 0.005,
) -> dict[str, int]:
    """Allocate a fixed extra-specialist budget from lawful colony signals."""

    if extra_slots < 0:
        raise ValueError("extra_slots must be non-negative")
    if not modality_reports:
        raise ValueError("at least one modality is required")

    materialized: dict[str, list[SpecialistReport]] = {}
    channels: set[str] = set()
    for name, reports in modality_reports.items():
        items = list(reports)
        if not items:
            raise ValueError(f"modality {name!r} has no pilot reports")
        group_channels = {report.channel for report in items}
        if len(group_channels) != 1:
            raise ValueError("each modality must estimate one semantic channel")
        channels.update(group_channels)
        materialized[name] = items

    if len(channels) != 1:
        raise ValueError("recruitment allocation requires one shared semantic channel")

    allocation = {name: 0 for name in materialized}
    if extra_slots == 0:
        return allocation

    scores = {
        name: recruitment_score(
            items,
            half_life_ms=half_life_ms,
            uncertainty_floor=uncertainty_floor,
        )
        for name, items in materialized.items()
    }
    score_sum = sum(scores.values())

    if score_sum <= 0.0:
        names = sorted(materialized)
        for index in range(extra_slots):
            allocation[names[index % len(names)]] += 1
        return allocation

    quotas = {name: extra_slots * score / score_sum for name, score in scores.items()}
    for name, quota in quotas.items():
        allocation[name] = floor(quota)

    remainder = extra_slots - sum(allocation.values())
    ranked = sorted(
        quotas,
        key=lambda name: (quotas[name] - allocation[name], name),
        reverse=True,
    )
    for name in ranked[:remainder]:
        allocation[name] += 1
    return allocation
