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

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be in [0, 1]")
        if not 0.0 <= self.novelty <= 1.0:
            raise ValueError("novelty must be in [0, 1]")


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


def disagreement(reports: Iterable[SpecialistReport]) -> float:
    """Mean absolute disagreement around the channel median."""

    items = list(reports)
    if not items:
        raise ValueError("at least one specialist report is required")
    center = median_value(items)
    return sum(abs(report.value - center) for report in items) / len(items)
