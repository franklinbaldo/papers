"""Reality-bounded phone-IMU kinematic consistency for sensor-clock health.

The helpers compare speed change reported by a delayed scalar-speed channel with
longitudinal acceleration integrated on the phone monotonic timebase. They use
only already-observed sensor samples and reported timestamps. No truth, fault
label, future sample, simulator pose, or map state is accepted.
"""

from __future__ import annotations

from dataclasses import dataclass
import math


def _huber_merit(standardized_residual: float, k: float) -> float:
    if k <= 0.0:
        raise ValueError("k must be positive")
    magnitude = abs(standardized_residual)
    if magnitude == 0.0 or magnitude <= k:
        return 1.0
    return k / magnitude


def integrated_acceleration(
    prefix_delta_v: list[float], start_index: int, end_index: int
) -> float:
    """Return observed IMU delta-v over [start_index, end_index)."""
    if start_index < 0 or end_index < start_index:
        raise ValueError("invalid integration interval")
    if end_index >= len(prefix_delta_v):
        raise ValueError("end_index exceeds prefix buffer")
    return prefix_delta_v[end_index] - prefix_delta_v[start_index]


@dataclass(frozen=True)
class KinematicClockObservation:
    residual_delta_v: float
    merit: float


def kinematic_clock_observation(
    *,
    previous_speed: float,
    current_speed: float,
    previous_reported_index: int,
    current_reported_index: int,
    imu_prefix_delta_v: list[float],
    nominal_delta_v_sigma: float = 0.55,
    huber_k: float = 1.345,
) -> KinematicClockObservation:
    """Score timestamp/kinematic consistency from speed delta versus phone IMU.

    ``imu_prefix_delta_v`` is a prefix sum built from observed longitudinal IMU
    acceleration on the phone monotonic clock. A fixed nominal scale is used on
    purpose: if the clock becomes inconsistent, the gate must not simply learn
    the larger residual away as a new normal.
    """
    if current_reported_index <= previous_reported_index:
        raise ValueError("reported indices must increase")
    if nominal_delta_v_sigma <= 0.0:
        raise ValueError("nominal_delta_v_sigma must be positive")

    observed_speed_delta = current_speed - previous_speed
    imu_delta = integrated_acceleration(
        imu_prefix_delta_v,
        previous_reported_index,
        current_reported_index,
    )
    residual = observed_speed_delta - imu_delta
    merit = _huber_merit(residual / nominal_delta_v_sigma, huber_k)
    if not math.isfinite(merit):
        raise ValueError("non-finite clock merit")
    return KinematicClockObservation(residual_delta_v=residual, merit=merit)
