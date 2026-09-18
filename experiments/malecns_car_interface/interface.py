"""Reality-bounded sensor contract for MaleCNS driving experiments.

This module intentionally contains no CARLA dependency. A simulator backend must
translate its internal state into these public buses before the agent sees it.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Mapping, Sequence


@dataclass(frozen=True)
class PhoneObservation:
    camera_rgb_ref: str
    gps_lat: float | None = None
    gps_lon: float | None = None
    gps_accuracy_m: float | None = None
    accel_xyz_mps2: tuple[float, float, float] | None = None
    gyro_xyz_rps: tuple[float, float, float] | None = None
    magnetometer_xyz_ut: tuple[float, float, float] | None = None
    orientation_xyzw: tuple[float, float, float, float] | None = None


@dataclass(frozen=True)
class ObdObservation:
    speed_kph: float | None = None
    rpm: float | None = None
    throttle_pct: float | None = None
    engine_load_pct: float | None = None
    coolant_c: float | None = None


@dataclass(frozen=True)
class NavigationIntent:
    distance_to_next_waypoint_m: float | None = None
    bearing_error_rad: float | None = None
    route_progress: float | None = None


@dataclass(frozen=True)
class BodilySignals:
    route_aversive: float = 0.0
    wrong_way_aversive: float = 0.0
    collision_aversive: float = 0.0
    progress_appetitive: float = 0.0


@dataclass(frozen=True)
class AgentObservation:
    phone: PhoneObservation
    obd: ObdObservation
    navigation: NavigationIntent
    body: BodilySignals


_ALLOWED_TOP_LEVEL = {"phone", "obd", "navigation", "body"}
_FORBIDDEN_SIMULATOR_HINTS = {
    "world_pose",
    "exact_pose",
    "lane_center",
    "lane_offset",
    "object_distance",
    "nearest_object_distance",
    "semantic_segmentation",
    "ground_truth_objects",
    "collision_prediction",
    "perfect_map_position",
}


def reject_privileged_state(payload: Mapping[str, object]) -> None:
    """Raise when a backend attempts to leak simulator-only cognition."""

    unexpected = set(payload) - _ALLOWED_TOP_LEVEL
    privileged = unexpected & _FORBIDDEN_SIMULATOR_HINTS
    if privileged:
        names = ", ".join(sorted(privileged))
        raise ValueError(f"privileged simulator state is forbidden: {names}")
    if unexpected:
        names = ", ".join(sorted(unexpected))
        raise ValueError(f"undeclared observation fields: {names}")


def public_schema() -> dict[str, Sequence[str]]:
    """Return the explicit fields visible at the reality boundary."""

    return {
        "phone": tuple(field.name for field in fields(PhoneObservation)),
        "obd": tuple(field.name for field in fields(ObdObservation)),
        "navigation": tuple(field.name for field in fields(NavigationIntent)),
        "body": tuple(field.name for field in fields(BodilySignals)),
    }
