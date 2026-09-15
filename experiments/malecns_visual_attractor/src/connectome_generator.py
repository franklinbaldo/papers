from __future__ import annotations

from dataclasses import dataclass
from math import atan2

import numpy as np
import scipy.sparse as sp

from visual_attractor import (
    ArenaConfig,
    BrainConfig,
    FlyPose,
    Interface,
    StepRecord,
    StimulusSpec,
    brain_step,
    motor_readout,
    trajectory_metrics,
    wrap_angle,
)


CONTEXT_DIM = 6
OUTPUT_DIM = 4


@dataclass(frozen=True)
class GeneratorConfig:
    spectral_scale: float
    gain: float = 1.0
    leak: float = 0.2
    input_scale: float = 0.10
    max_bearing_offset_deg: float = 35.0
    max_log_size_scale: float = float(np.log(2.0))

    def __post_init__(self) -> None:
        if self.spectral_scale <= 0:
            raise ValueError("spectral_scale must be > 0")
        if not 0 < self.leak <= 1:
            raise ValueError("leak must be in (0,1]")
        if self.input_scale < 0:
            raise ValueError("input_scale must be >= 0")
        if self.max_bearing_offset_deg <= 0:
            raise ValueError("max_bearing_offset_deg must be > 0")
        if self.max_log_size_scale < 0:
            raise ValueError("max_log_size_scale must be >= 0")


@dataclass(frozen=True)
class GeneratorAdapter:
    """Trainable boundary around a frozen emitter MaleCNS.

    Context is projected into emitter photoreceptors. The recurrent graph itself
    is never trained. An output adapter reads emitter descending neurons and emits
    a four-dimensional visual-control vector.
    """

    input_indices: np.ndarray
    readout_indices: np.ndarray
    input_weight: np.ndarray
    input_bias: np.ndarray
    output_weight: np.ndarray
    output_bias: np.ndarray

    def __post_init__(self) -> None:
        if self.input_indices.ndim != 1 or self.readout_indices.ndim != 1:
            raise ValueError("adapter indices must be one-dimensional")
        if self.input_weight.shape != (len(self.input_indices), CONTEXT_DIM):
            raise ValueError("input_weight shape mismatch")
        if self.input_bias.shape != (len(self.input_indices),):
            raise ValueError("input_bias shape mismatch")
        if self.output_weight.shape != (OUTPUT_DIM, len(self.readout_indices)):
            raise ValueError("output_weight shape mismatch")
        if self.output_bias.shape != (OUTPUT_DIM,):
            raise ValueError("output_bias shape mismatch")

    @property
    def trainable_parameters(self) -> int:
        return int(
            self.input_weight.size
            + self.input_bias.size
            + self.output_weight.size
            + self.output_bias.size
        )


@dataclass(frozen=True)
class GeneratedFrame:
    bearing_offset_rad: float
    size_scale: float
    contrast: float
    temporal_gate: float
    raw: tuple[float, float, float, float]


@dataclass(frozen=True)
class ConnectomeRollout:
    records: tuple[StepRecord, ...]
    generated: tuple[GeneratedFrame, ...]
    metrics: dict[str, float]


def make_adapter(interface: Interface, *, seed: int, scale: float = 0.05) -> GeneratorAdapter:
    """Deterministic adapter initialization for a MaleCNS emitter.

    The input boundary uses the emitter's photoreceptors; the output boundary
    reads all declared descending neurons. This keeps the biological graph in the
    middle while making the learned boundary explicit and parameter-countable.
    """
    inputs = np.asarray(interface.visual_indices, dtype=np.int32)
    readout = np.unique(
        np.concatenate(
            [
                np.asarray(interface.descending_left, dtype=np.int32),
                np.asarray(interface.descending_right, dtype=np.int32),
            ]
        )
    )
    if inputs.size == 0 or readout.size == 0:
        raise ValueError("generator requires visual inputs and descending readouts")
    rng = np.random.default_rng(seed)
    return GeneratorAdapter(
        input_indices=inputs,
        readout_indices=readout,
        input_weight=rng.normal(0.0, scale, size=(inputs.size, CONTEXT_DIM)).astype(np.float32),
        input_bias=np.zeros(inputs.size, dtype=np.float32),
        output_weight=rng.normal(0.0, scale, size=(OUTPUT_DIM, readout.size)).astype(np.float32),
        output_bias=np.zeros(OUTPUT_DIM, dtype=np.float32),
    )


def receiver_context(
    pose: FlyPose,
    *,
    distance_scale: float,
    previous_radial_velocity: float = 0.0,
) -> np.ndarray:
    """Small closed-loop context visible to the emitter.

    No receiver neural state is exposed. The emitter sees only geometry/behaviour
    that an external tracking system could in principle measure.
    """
    if distance_scale <= 0:
        raise ValueError("distance_scale must be > 0")
    distance = float(np.hypot(pose.x, pose.y))
    bearing = float(wrap_angle(atan2(-pose.y, -pose.x) - pose.heading))
    return np.asarray(
        [
            np.clip(distance / distance_scale, 0.0, 4.0),
            np.sin(bearing),
            np.cos(bearing),
            np.sin(pose.heading),
            np.cos(pose.heading),
            np.tanh(previous_radial_velocity),
        ],
        dtype=np.float32,
    )


def generator_step(
    graph: sp.csr_matrix,
    state: np.ndarray,
    context: np.ndarray,
    adapter: GeneratorAdapter,
    config: GeneratorConfig,
) -> tuple[np.ndarray, GeneratedFrame]:
    if state.shape != (graph.shape[0],):
        raise ValueError("generator state shape mismatch")
    context = np.asarray(context, dtype=np.float32)
    if context.shape != (CONTEXT_DIM,):
        raise ValueError(f"context must have shape ({CONTEXT_DIM},)")

    external = np.zeros(graph.shape[0], dtype=np.float32)
    projected = adapter.input_weight @ context + adapter.input_bias
    external[adapter.input_indices] = np.float32(config.input_scale) * np.tanh(projected)

    recurrent = (graph @ state) / np.float32(config.spectral_scale)
    next_state = (
        (1.0 - config.leak) * state
        + config.leak * np.tanh(config.gain * recurrent + external)
    ).astype(np.float32)

    raw = adapter.output_weight @ next_state[adapter.readout_indices] + adapter.output_bias
    bounded = np.tanh(raw).astype(np.float32)
    max_bearing = np.deg2rad(config.max_bearing_offset_deg)
    frame = GeneratedFrame(
        bearing_offset_rad=float(max_bearing * bounded[0]),
        size_scale=float(np.exp(config.max_log_size_scale * bounded[1])),
        contrast=float(0.5 + 0.5 * bounded[2]),
        temporal_gate=float(0.5 + 0.5 * bounded[3]),
        raw=tuple(float(value) for value in raw),
    )
    return next_state, frame


def generated_visual_drive(
    n_neurons: int,
    interface: Interface,
    receiver_pose: FlyPose,
    base_stimulus: StimulusSpec,
    frame: GeneratedFrame,
    arena: ArenaConfig,
) -> np.ndarray:
    """Render one connectome-generated frame onto receiver photoreceptors."""
    drive = np.zeros(n_neurons, dtype=np.float32)
    distance = max(float(np.hypot(receiver_pose.x, receiver_pose.y)), 1e-9)
    target_bearing = float(wrap_angle(atan2(-receiver_pose.y, -receiver_pose.x) - receiver_pose.heading))
    apparent_bearing = float(wrap_angle(target_bearing + frame.bearing_offset_rad))
    physical_size = base_stimulus.physical_size * frame.size_scale
    angular_size = 2.0 * np.arctan2(physical_size / 2.0, distance)
    target_norm = float(np.clip(apparent_bearing / arena.target_fov_rad, -1.0, 1.0))
    sigma = max(arena.visual_sigma_floor, angular_size / arena.target_fov_rad / 2.355)
    delta = interface.visual_azimuth - target_norm
    profile = np.exp(-0.5 * (delta / sigma) ** 2).astype(np.float32)
    amplitude = base_stimulus.contrast * frame.contrast * frame.temporal_gate
    drive[interface.visual_indices] = np.float32(amplitude) * profile
    return drive


def simulate_connectome_generator(
    graph: sp.csr_matrix,
    interface: Interface,
    adapter: GeneratorAdapter,
    receiver_start: FlyPose,
    *,
    steps: int,
    emitter: GeneratorConfig,
    receiver: BrainConfig,
    arena: ArenaConfig = ArenaConfig(),
    base_stimulus: StimulusSpec | None = None,
) -> ConnectomeRollout:
    """Closed loop: frozen MaleCNS A invents frames seen by frozen MaleCNS B."""
    if steps < 1:
        raise ValueError("steps must be >= 1")
    base_stimulus = base_stimulus or StimulusSpec("connectome_generated", path="static")
    emitter_state = np.zeros(graph.shape[0], dtype=np.float32)
    receiver_state = np.zeros(graph.shape[0], dtype=np.float32)
    pose = receiver_start
    initial_distance = float(np.hypot(pose.x, pose.y))
    previous_distance = initial_distance
    previous_radial_velocity = 0.0
    records: list[StepRecord] = []
    generated: list[GeneratedFrame] = []

    for step in range(steps):
        t = step * arena.dt
        context = receiver_context(
            pose,
            distance_scale=initial_distance,
            previous_radial_velocity=previous_radial_velocity,
        )
        emitter_state, frame = generator_step(
            graph, emitter_state, context, adapter, emitter
        )
        external = generated_visual_drive(
            graph.shape[0], interface, pose, base_stimulus, frame, arena
        )
        receiver_state = brain_step(graph, receiver_state, external, interface, receiver)
        forward, turn, left, right = motor_readout(receiver_state, interface, arena)

        new_heading = float(wrap_angle(pose.heading + turn * arena.turn_rate_rad_s * arena.dt))
        new_x = float(pose.x + forward * np.cos(new_heading) * arena.dt)
        new_y = float(pose.y + forward * np.sin(new_heading) * arena.dt)
        distance = float(np.hypot(new_x, new_y))
        radial_velocity = (previous_distance - distance) / arena.dt
        target_bearing = float(wrap_angle(atan2(-new_y, -new_x) - new_heading))
        physical_size = base_stimulus.physical_size * frame.size_scale
        angular_size = 2.0 * np.arctan2(physical_size / 2.0, max(distance, 1e-9))
        records.append(
            StepRecord(
                t=t + arena.dt,
                x=new_x,
                y=new_y,
                heading=new_heading,
                distance=distance,
                target_bearing=target_bearing,
                angular_size=float(angular_size),
                orientation_error=abs(target_bearing),
                radial_velocity=float(radial_velocity),
                descending_left=left,
                descending_right=right,
                forward_command=forward,
                turn_command=turn,
                visual_rms=float(np.sqrt(np.mean(external * external))),
            )
        )
        generated.append(frame)
        pose = FlyPose(new_x, new_y, new_heading)
        previous_distance = distance
        previous_radial_velocity = radial_velocity

    record_tuple = tuple(records)
    metrics = trajectory_metrics(record_tuple, initial_distance, arena.near_radius)
    return ConnectomeRollout(record_tuple, tuple(generated), metrics)
