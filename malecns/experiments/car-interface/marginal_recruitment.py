"""Sequential marginal-value recruitment helpers for the MaleCNS sensor colony."""

from __future__ import annotations

from typing import Iterable

from colony import SpecialistReport
from recruitment_bandit import continuous_context_features


def marginal_recruitment_features(
    primary_reports: Iterable[SpecialistReport],
    secondary_reports: Iterable[SpecialistReport],
    *,
    primary_count: int,
    secondary_count: int,
    max_per_modality: int = 8,
    total_budget: int = 12,
) -> tuple[float, ...]:
    """Return lawful context for valuing one additional specialist.

    The first ten values are the continuous sensor-health features already used by
    Run 8. Three budget-state features tell the allocator how much specialist
    capacity has already been committed. No realized error, hidden fault flag, or
    simulator truth enters the decision-time vector.
    """

    if primary_count <= 0 or secondary_count <= 0:
        raise ValueError("specialist counts must be positive")
    if max_per_modality <= 0 or total_budget <= 0:
        raise ValueError("budget limits must be positive")
    if primary_count > max_per_modality or secondary_count > max_per_modality:
        raise ValueError("specialist count exceeds per-modality limit")
    if primary_count + secondary_count > total_budget:
        raise ValueError("specialist counts exceed total budget")

    base = continuous_context_features(primary_reports, secondary_reports)
    return base + (
        primary_count / max_per_modality,
        secondary_count / max_per_modality,
        (primary_count + secondary_count) / total_budget,
    )
