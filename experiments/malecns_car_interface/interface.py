"""Reality-bounded sensor contract for MaleCNS driving experiments.

This module intentionally contains no CARLA dependency. A simulator backend must
translate its internal state into these public buses before the agent sees it.

Every field below must be reproducible on a real retrofit vehicle from a phone,
OBD/CAN, or an explicitly declared inexpensive sensor/transducer.
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
    gps_speed_kph: float | None = None
    gps_bearing_rad: float | None = None
    accel_xyz_mps2: tuple[float, float, float] | None = None
    gyro_xyz_rps: tuple[float, float, float] | None = None
    magnetometer_xyz_ut: tuple[float, float, float] | None = None
    orientation_xyzw: tuple[float, float, float, float] | None = None
    ambient_light_lux: float | None = None
    barometer_hpa: float | None = None


@dataclass(frozen=True)
class ObdObservation:
    speed_kph: float | None = None
    rpm: float | None = None
    throttle_pct: float | None = None
    engine_load_pct: float | None = None
    coolant_c: float | None = None
    steering_angle_rad: float | None = None
    wheel_speeds_kph: tuple[float, float, float, float] | None = None
    brake_active: bool | None = None
    turn_signal: str | None = None
    abs_active: bool | None = None
    traction_control_active: bool | None = None
    wiper_active: bool | None = None


@dataclass(frozen=True)
class NavigationIntent:
    distance_to_next_waypoint_m: float | None = None
    bearing_error_rad: float | None = None
    route_progress: float | None = None
    speed_limit_kph: float | None = None
    distance_to_intersection_m: float | None = None
    road_curvature_ahead_1pm: float | None = None


@dataclass(frozen=True)
class BodilySignals:
    route_aversive: float = 0.0
    wrong_way_aversive: float = 0.0
    collision_aversive: float = 0.0
    progress_appetitive: float = 0.0


@dataclass(frozen=True)
class RangeObservation:
    """Explicit physical range sensors; never simulator object truth."""

    ultrasonic_ranges_m: tuple[float, ...] | None = None
    ultrasonic_echo_energy: tuple[float, ...] | None = None
    lidar_ranges_m: tuple[float, ...] | None = None


@dataclass(frozen=True)
class PerceptionObservation:
    """On-device camera-derived perception, e.g. YOLO/tiny segmentation."""

    object_count: int | None = None
    pedestrian_count: int | None = None
    cyclist_count: int | None = None
    vehicle_count: int | None = None
    nearest_box_scale: float | None = None
    detection_entropy: float | None = None
    drivable_area_fraction: float | None = None
    lane_confidence: float | None = None
    traffic_light_confidence: float | None = None
    optical_flow_magnitude: float | None = None
    visual_ttc_s: float | None = None


@dataclass(frozen=True)
class RadioObservation:
    """Passive RF context and lawful peer-to-peer vehicle communication stats."""

    wifi_ap_count: int | None = None
    wifi_rssi_mean_dbm: float | None = None
    bluetooth_peer_count: int | None = None
    cellular_signal_dbm: float | None = None
    peer_vehicle_count: int | None = None
    peer_packet_loss: float | None = None
    peer_latency_ms: float | None = None


@dataclass(frozen=True)
class SemanticObservation:
    """Optional local semantic transducers; no simulator-only inputs."""

    hazard_score: float | None = None
    route_instruction_embedding_ref: str | None = None
    local_llm_confidence: float | None = None


@dataclass(frozen=True)
class DerivedSignals:
    """Lawful scalar fusion channels computed only from public buses."""

    speed_disagreement_kph: float | None = None
    wheel_speed_spread_kph: float | None = None
    steering_yaw_residual_rps: float | None = None
    gnss_confidence: float | None = None


@dataclass(frozen=True)
class AgentObservation:
    phone: PhoneObservation
    obd: ObdObservation
    navigation: NavigationIntent
    body: BodilySignals
    range: RangeObservation = RangeObservation()
    perception: PerceptionObservation = PerceptionObservation()
    radio: RadioObservation = RadioObservation()
    semantic: SemanticObservation = SemanticObservation()
    derived: DerivedSignals = DerivedSignals()


_ALLOWED_TOP_LEVEL = {
    "phone",
    "obd",
    "navigation",
    "body",
    "range",
    "perception",
    "radio",
    "semantic",
    "derived",
}
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
        "range": tuple(field.name for field in fields(RangeObservation)),
        "perception": tuple(field.name for field in fields(PerceptionObservation)),
        "radio": tuple(field.name for field in fields(RadioObservation)),
        "semantic": tuple(field.name for field in fields(SemanticObservation)),
        "derived": tuple(field.name for field in fields(DerivedSignals)),
    }
