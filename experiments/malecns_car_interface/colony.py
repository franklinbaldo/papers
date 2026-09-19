"""Minimal contracts and baselines for a colony of MaleCNS sensor specialists."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import median
from typing import Iterable


@dataclass(frozen=True)
class SpecialistReport:
    """Small lawful report emitted by one sensor-specialist MaleCNS."""

    specialist_id: str
    channel: str
    value: float
    confidence: float
    novelty: float = 0.0
    age_ms: float = 0.0

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
    """Downweight old specialist reports using only lawful timestamp metadata.

    Sensor buses in a real retrofit car are asynchronous. A specialist may be
    confident and internally consistent while describing a state that is already
    hundreds of milliseconds old. This baseline exponentially decays each
    report's confidence with age, using ``half_life_ms`` as the decay half-life.
    It needs only acquisition/processing timestamps that a real implementation
    can measure; no simulator truth is involved.
    """

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
    """Fuse confidence only inside a robust consensus neighborhood.

    Specialist self-reported confidence can itself fail. This baseline first
    finds the channel median, estimates median absolute deviation (MAD), rejects
    reports outside ``max(min_radius, mad_scale * MAD)``, then confidence-weights
    only the remaining reports. It uses no simulator truth and is intentionally
    simple enough that a learned MaleCNS coordinator should be expected to beat
    it.
    """

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
