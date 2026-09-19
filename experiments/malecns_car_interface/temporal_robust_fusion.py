"""Reality-bounded temporal transport and robust fusion primitives.

The functions in this module only consume measurements and timestamps that a real
car interface can observe. They do not accept simulator truth, fault labels,
perfect pose, future trajectory, or hidden world state.
"""

from __future__ import annotations

import math


def freshness(age_s: float, tau_s: float = 1.5) -> float:
    if age_s < 0.0:
        raise ValueError("age_s must be non-negative")
    if tau_s <= 0.0:
        raise ValueError("tau_s must be positive")
    return math.exp(-age_s / tau_s)


def huber_weight(residual: float, scale: float) -> float:
    if scale <= 0.0:
        raise ValueError("scale must be positive")
    magnitude = abs(residual)
    if magnitude == 0.0 or magnitude <= scale:
        return 1.0
    return scale / magnitude


def transport_by_reference_delta(
    candidate_at_measurement: float,
    reference_at_measurement: float,
    reference_now: float,
) -> float:
    """Transport a delayed candidate with an observed reference-sensor delta.

    Example: a GNSS speed fix stamped at ``t0`` arrives at ``t1``. The OBD stream
    has already observed speed at both times, so ``OBD(t1)-OBD(t0)`` can transport
    the GNSS value toward ``t1`` without requiring true speed or a future sample.
    """

    return candidate_at_measurement + (reference_now - reference_at_measurement)


def robust_fusion_weight(
    *,
    age_s: float,
    matched_time_residual: float,
    base_scale: float,
    age_power: float = 0.0,
    min_scale: float = 0.03,
    tau_s: float = 1.5,
) -> float:
    """Return freshness × Huber weight from matched-time observable evidence.

    ``age_power=0`` is the fixed-radius control. Positive ``age_power`` contracts
    the Huber radius with age, reproducing the Run-14 mechanism while keeping the
    residual itself correctly matched in time.
    """

    if base_scale <= 0.0:
        raise ValueError("base_scale must be positive")
    if age_power < 0.0:
        raise ValueError("age_power must be non-negative")
    if min_scale <= 0.0:
        raise ValueError("min_scale must be positive")

    merit = freshness(age_s, tau_s=tau_s)
    effective_scale = max(min_scale, base_scale * merit**age_power)
    return merit * huber_weight(matched_time_residual, effective_scale)


def fuse(reference_now: float, candidate_now: float, weight: float) -> float:
    if weight < 0.0:
        raise ValueError("weight must be non-negative")
    return (reference_now + weight * candidate_now) / (1.0 + weight)
