from __future__ import annotations

from dataclasses import dataclass
from math import atan2, pi, sqrt
from pathlib import Path
from typing import Iterable

import numpy as np
import scipy.sparse as sp


def wrap_angle(angle: float | np.ndarray) -> float | np.ndarray:
    return (angle + np.pi) % (2 * np.pi) - np.pi


@dataclass(frozen=True)
class StimulusSpec:
    name: str
    shape: str = "dot"
    physical_size: float = 0.25
    contrast: float = 1.0
    path: str = "sinusoid"
    path_amplitude_deg: float = 18.0
    path_frequency_hz: float = 0.47
    phase_rad: float = 0.0
    flicker_hz: float = 0.0
    random_seed: int = 0

    def __post_init__(self) -> None:
        if self.physical_size <= 0:
            raise ValueError("physical_size must be > 0")
        if not 0 <= self.contrast <= 1:
            raise ValueError("contrast must be in [0, 1]")
        if self.path not in {"static", "sinusoid", "random_motion", "blank"}:
            raise ValueError(f"unsupported path: {self.path}")

    def path_offset_rad(self, t: float) -> float:
        if self.path in {"static", "blank"}:
            return 0.0
        amp = np.deg2rad(self.path_amplitude_deg)
        if self.path == "sinusoid":
            return float(amp * np.sin(2 * np.pi * self.path_frequency_hz * t + self.phase_rad))

        # Deterministic band-limited random motion: reproducible without hidden
        # renderer RNG state, while destroying the smooth positive-control path.
        rng = np.random.default_rng(self.random_seed)
        freqs = rng.uniform(0.25, 2.0, size=5)
        phases = rng.uniform(-np.pi, np.pi, size=5)
        weights = rng.normal(size=5)
        weights /= max(float(np.linalg.norm(weights)), 1e-12)
        value = np.sum(weights * np.sin(2 * np.pi * freqs * t + phases)) / sqrt(5)
        return float(np.clip(value, -1.0, 1.0) * amp)

    def flicker(self, t: float) -> float:
        if self.path == "blank":
            return 0.0
        if self.flicker_hz <= 0:
            return self.contrast
        phase = 2 * np.pi * self.flicker_hz * t
        return self.contrast * (0.5 + 0.5 * np.sin(phase))


@dataclass(frozen=True)
class FlyPose:
    x: float
    y: float
    heading: float


@dataclass(frozen=True)
class Interface:
    visual_indices: np.ndarray
    visual_azimuth: np.ndarray
    descending_left: np.ndarray
    descending_right: np.ndarray
    courtship_indices: np.ndarray

    def __post_init__(self) -> None:
        if self.visual_indices.ndim != 1 or self.visual_azimuth.ndim != 1:
            raise ValueError("visual arrays must be one-dimensional")
        if len(self.visual_indices) != len(self.visual_azimuth):
            raise ValueError("visual_indices and visual_azimuth must align")
        if np.any(self.visual_azimuth < -1.0) or np.any(self.visual_azimuth > 1.0):
            raise ValueError("visual_azimuth must lie in [-1,1]")


@dataclass(frozen=True)
class BrainConfig:
    spectral_scale: float
    gain: float = 1.0
    leak: float = 0.2
    visual_scale: float = 0.5
    prime_scale: float = 0.08

    def __post_init__(self) -> None:
        if self.spectral_scale <= 0:
            raise ValueError("spectral_scale must be > 0")
        if not 0 < self.leak <= 1:
            raise ValueError("leak must be in (0,1]")


@dataclass(frozen=True)
class ArenaConfig:
    dt: float = 0.02
    turn_rate_rad_s: float = 4.0
    base_speed: float = 0.12
    motor_speed_gain: float = 0.20
    motor_turn_gain: float = 4.0
    near_radius: float = 0.5
    target_fov_rad: float = np.pi
    visual_sigma_floor: float = 0.025

    def __post_init__(self) -> None:
        if self.dt <= 0:
            raise ValueError("dt must be > 0")
        if self.turn_rate_rad_s <= 0:
            raise ValueError("turn_rate_rad_s must be > 0")
        if self.base_speed < 0:
            raise ValueError("base_speed must be >= 0")


@dataclass(frozen=True)
class StepRecord:
    t: float
    x: float
    y: float
    heading: float
    distance: float
    target_bearing: float
    angular_size: float
    orientation_error: float
    radial_velocity: float
    descending_left: float
    descending_right: float
    forward_command: float
    turn_command: float
    visual_rms: float


def load_graph(path: Path) -> sp.csr_matrix:
    archive = np.load(path, allow_pickle=False)
    shape = tuple(int(v) for v in archive["shape"])
    return sp.csr_matrix(
        (archive["data"], archive["indices"], archive["indptr"]),
        shape=shape,
        dtype=np.float32,
    )


def load_interface(path: Path) -> Interface:
    archive = np.load(path, allow_pickle=False)
    return Interface(
        visual_indices=archive["visual_indices"].astype(np.int32),
        visual_azimuth=archive["visual_azimuth"].astype(np.float32),
        descending_left=archive["descending_left"].astype(np.int32),
        descending_right=archive["descending_right"].astype(np.int32),
        courtship_indices=archive["courtship_indices"].astype(np.int32),
    )


def target_geometry(pose: FlyPose, stimulus: StimulusSpec, t: float) -> tuple[float, float, float]:
    distance = max(float(np.hypot(pose.x, pose.y)), 1e-9)
    lure_bearing = wrap_angle(atan2(-pose.y, -pose.x) - pose.heading)
    apparent_bearing = wrap_angle(lure_bearing + stimulus.path_offset_rad(t))
    angular_size = 2.0 * np.arctan2(stimulus.physical_size / 2.0, distance)
    return float(apparent_bearing), float(angular_size), distance


def visual_drive(
    n_neurons: int,
    interface: Interface,
    pose: FlyPose,
    stimulus: StimulusSpec,
    t: float,
    arena: ArenaConfig,
) -> np.ndarray:
    drive = np.zeros(n_neurons, dtype=np.float32)
    if stimulus.path == "blank":
        return drive
    bearing, angular_size, _ = target_geometry(pose, stimulus, t)
    target_norm = float(np.clip(bearing / arena.target_fov_rad, -1.0, 1.0))
    sigma = max(arena.visual_sigma_floor, angular_size / arena.target_fov_rad / 2.355)
    delta = interface.visual_azimuth - target_norm
    profile = np.exp(-0.5 * (delta / sigma) ** 2).astype(np.float32)
    drive[interface.visual_indices] = np.float32(stimulus.flicker(t)) * profile
    return drive


def brain_step(
    graph: sp.csr_matrix,
    state: np.ndarray,
    external: np.ndarray,
    interface: Interface,
    config: BrainConfig,
) -> np.ndarray:
    if state.shape != (graph.shape[0],):
        raise ValueError("state shape does not match graph")
    drive = config.visual_scale * external
    if interface.courtship_indices.size:
        drive = drive.copy()
        drive[interface.courtship_indices] += np.float32(config.prime_scale)
    recurrent = (graph @ state) / np.float32(config.spectral_scale)
    return (
        (1.0 - config.leak) * state
        + config.leak * np.tanh(config.gain * recurrent + drive)
    ).astype(np.float32)


def motor_readout(
    state: np.ndarray,
    interface: Interface,
    arena: ArenaConfig,
) -> tuple[float, float, float, float]:
    left = float(np.mean(state[interface.descending_left])) if interface.descending_left.size else 0.0
    right = float(np.mean(state[interface.descending_right])) if interface.descending_right.size else 0.0
    turn = float(np.tanh(arena.motor_turn_gain * (right - left)))

    # This is an engineering locomotor decoder, not a biological velocity claim.
    # Raw descending summaries are retained so alternate decoders can be compared.
    bilateral = 0.5 * (abs(left) + abs(right))
    forward = float(max(0.0, arena.base_speed + arena.motor_speed_gain * np.tanh(4.0 * bilateral)))
    return forward, turn, left, right


def simulate(
    graph: sp.csr_matrix,
    interface: Interface,
    stimulus: StimulusSpec,
    start: FlyPose,
    *,
    steps: int,
    brain: BrainConfig,
    arena: ArenaConfig = ArenaConfig(),
) -> tuple[StepRecord, ...]:
    if steps < 1:
        raise ValueError("steps must be >= 1")
    state = np.zeros(graph.shape[0], dtype=np.float32)
    pose = start
    records: list[StepRecord] = []
    previous_distance = float(np.hypot(pose.x, pose.y))

    for step in range(steps):
        t = step * arena.dt
        external = visual_drive(graph.shape[0], interface, pose, stimulus, t, arena)
        state = brain_step(graph, state, external, interface, brain)
        forward, turn, left, right = motor_readout(state, interface, arena)
        new_heading = float(wrap_angle(pose.heading + turn * arena.turn_rate_rad_s * arena.dt))
        new_x = float(pose.x + forward * np.cos(new_heading) * arena.dt)
        new_y = float(pose.y + forward * np.sin(new_heading) * arena.dt)
        new_pose = FlyPose(new_x, new_y, new_heading)
        bearing, angular_size, distance = target_geometry(new_pose, stimulus, t + arena.dt)
        radial_velocity = (previous_distance - distance) / arena.dt
        records.append(
            StepRecord(
                t=t + arena.dt,
                x=new_x,
                y=new_y,
                heading=new_heading,
                distance=distance,
                target_bearing=bearing,
                angular_size=angular_size,
                orientation_error=abs(float(wrap_angle(atan2(-new_y, -new_x) - new_heading))),
                radial_velocity=float(radial_velocity),
                descending_left=left,
                descending_right=right,
                forward_command=forward,
                turn_command=turn,
                visual_rms=float(np.sqrt(np.mean(external * external))),
            )
        )
        pose = new_pose
        previous_distance = distance

    return tuple(records)


def trajectory_metrics(
    records: tuple[StepRecord, ...],
    initial_distance: float,
    near_radius: float,
) -> dict[str, float]:
    if not records:
        raise ValueError("records cannot be empty")
    distances = np.asarray([r.distance for r in records], dtype=float)
    radial = np.asarray([r.radial_velocity for r in records], dtype=float)
    orient = np.asarray([r.orientation_error for r in records], dtype=float)
    near = distances <= near_radius
    reduction = (initial_distance - float(np.min(distances))) / max(initial_distance, 1e-12)
    return {
        "initial_distance": float(initial_distance),
        "final_distance": float(distances[-1]),
        "minimum_distance": float(distances.min()),
        "normalized_distance_reduction": float(reduction),
        "mean_radial_velocity": float(radial.mean()),
        "orientation_fraction_30deg": float(np.mean(orient <= np.deg2rad(30.0))),
        "near_time_fraction": float(np.mean(near)),
        "approach": float(reduction >= 0.5),
        "avoidance_fraction": float(np.mean(radial < 0.0)),
    }


def radial_swarm(
    *,
    flies: int,
    radius: float,
    seed: int,
    radial_jitter: float = 0.05,
) -> tuple[FlyPose, ...]:
    if flies < 1 or radius <= 0:
        raise ValueError("flies >= 1 and radius > 0 required")
    if radial_jitter < 0:
        raise ValueError("radial_jitter must be >= 0")
    rng = np.random.default_rng(seed)
    starts: list[FlyPose] = []
    for i in range(flies):
        angle = 2 * np.pi * (i / flies) + rng.uniform(-np.pi / flies, np.pi / flies)
        r = radius * (1.0 + rng.uniform(-radial_jitter, radial_jitter))
        starts.append(
            FlyPose(
                float(r * np.cos(angle)),
                float(r * np.sin(angle)),
                float(rng.uniform(-np.pi, np.pi)),
            )
        )
    return tuple(starts)


def evaluate_swarm(
    graph: sp.csr_matrix,
    interface: Interface,
    stimulus: StimulusSpec,
    starts: Iterable[FlyPose],
    *,
    steps: int,
    brain: BrainConfig,
    arena: ArenaConfig = ArenaConfig(),
) -> dict:
    metrics = []
    for start in starts:
        records = simulate(graph, interface, stimulus, start, steps=steps, brain=brain, arena=arena)
        metrics.append(
            trajectory_metrics(records, float(np.hypot(start.x, start.y)), arena.near_radius)
        )
    if not metrics:
        raise ValueError("at least one fly start required")
    keys = metrics[0].keys()
    return {
        "flies": len(metrics),
        **{key: float(np.mean([row[key] for row in metrics])) for key in keys},
        "per_fly": metrics,
    }


def capture_pass(
    candidate_approach: float,
    control_approach: float,
    *,
    p0: float = 0.60,
    margin: float = 0.10,
) -> bool:
    return candidate_approach >= p0 and candidate_approach - control_approach >= margin
