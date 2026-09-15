from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
import scipy.sparse as sp

from connectome_generator import (
    CONTEXT_DIM,
    GeneratorAdapter,
    GeneratorConfig,
)
from gpu_batch import _torch, _wrap_torch, scipy_csr_to_torch
from visual_attractor import ArenaConfig, BrainConfig, FlyPose, Interface, StimulusSpec


@dataclass(frozen=True)
class GeneratorPopulationBatch:
    metrics: dict[str, np.ndarray]

    @property
    def candidates(self) -> int:
        return next(iter(self.metrics.values())).shape[0]

    @property
    def flies(self) -> int:
        return next(iter(self.metrics.values())).shape[1]

    def candidate_summary(self) -> dict[str, np.ndarray]:
        return {name: values.mean(axis=1) for name, values in self.metrics.items()}


def _stack_adapters(adapters: Sequence[GeneratorAdapter]):
    values = tuple(adapters)
    if not values:
        raise ValueError("at least one adapter required")
    first = values[0]
    for adapter in values[1:]:
        if not np.array_equal(adapter.input_indices, first.input_indices):
            raise ValueError("all adapters must share input_indices")
        if not np.array_equal(adapter.readout_indices, first.readout_indices):
            raise ValueError("all adapters must share readout_indices")
        if adapter.input_weight.shape != first.input_weight.shape:
            raise ValueError("input adapter shapes differ")
        if adapter.output_weight.shape != first.output_weight.shape:
            raise ValueError("output adapter shapes differ")
    return (
        first.input_indices,
        first.readout_indices,
        np.stack([a.input_weight for a in values]),
        np.stack([a.input_bias for a in values]),
        np.stack([a.output_weight for a in values]),
        np.stack([a.output_bias for a in values]),
    )


def simulate_adapter_population_batch(
    operator: sp.csr_matrix,
    interface: Interface,
    adapters: Sequence[GeneratorAdapter],
    starts: Sequence[FlyPose],
    *,
    steps: int,
    emitter: GeneratorConfig,
    receiver: BrainConfig,
    arena: ArenaConfig = ArenaConfig(),
    base_stimulus: StimulusSpec | None = None,
    device: str = "cuda",
    torch_operator=None,
) -> GeneratorPopulationBatch:
    """Evaluate P emitter adapters x F matched receivers with two sparse W@X calls/step.

    Each column contains an independent emitter A and receiver B trajectory. The
    recurrent MaleCNS operator is identical and frozen for every column; only the
    boundary adapter differs across candidate blocks. Receiver starts are repeated
    exactly across candidates, giving common random numbers to the optimizer.
    """
    torch = _torch()
    adapter_values = tuple(adapters)
    start_values = tuple(starts)
    if not start_values:
        raise ValueError("at least one receiver start required")
    if steps < 1:
        raise ValueError("steps must be >= 1")
    base_stimulus = base_stimulus or StimulusSpec("connectome_generated", path="static")

    (
        input_indices_np,
        readout_indices_np,
        input_weight_np,
        input_bias_np,
        output_weight_np,
        output_bias_np,
    ) = _stack_adapters(adapter_values)

    p_count = len(adapter_values)
    f_count = len(start_values)
    batch = p_count * f_count
    neurons = operator.shape[0]
    sparse = torch_operator if torch_operator is not None else scipy_csr_to_torch(operator, device=device)

    emitter_state = torch.zeros((neurons, batch), dtype=torch.float32, device=device)
    receiver_state = torch.zeros((neurons, batch), dtype=torch.float32, device=device)

    start_x = np.asarray([p.x for p in start_values], dtype=np.float64)
    start_y = np.asarray([p.y for p in start_values], dtype=np.float64)
    start_h = np.asarray([p.heading for p in start_values], dtype=np.float64)
    x = torch.from_numpy(np.tile(start_x, p_count)).to(device=device, dtype=torch.float64)
    y = torch.from_numpy(np.tile(start_y, p_count)).to(device=device, dtype=torch.float64)
    heading = torch.from_numpy(np.tile(start_h, p_count)).to(device=device, dtype=torch.float64)
    initial_distance = torch.clamp(torch.hypot(x, y), min=1e-9)
    previous_distance = initial_distance.clone()
    previous_radial_velocity = torch.zeros(batch, dtype=torch.float64, device=device)

    input_indices = torch.from_numpy(np.asarray(input_indices_np, dtype=np.int64)).to(device)
    readout_indices = torch.from_numpy(np.asarray(readout_indices_np, dtype=np.int64)).to(device)
    input_weight = torch.from_numpy(input_weight_np.astype(np.float32, copy=False)).to(device)
    input_bias = torch.from_numpy(input_bias_np.astype(np.float32, copy=False)).to(device)
    output_weight = torch.from_numpy(output_weight_np.astype(np.float32, copy=False)).to(device)
    output_bias = torch.from_numpy(output_bias_np.astype(np.float32, copy=False)).to(device)

    visual_idx = torch.from_numpy(np.asarray(interface.visual_indices, dtype=np.int64)).to(device)
    visual_azimuth = torch.from_numpy(np.asarray(interface.visual_azimuth, dtype=np.float32)).to(device)[:, None]
    courtship_idx = torch.from_numpy(np.asarray(interface.courtship_indices, dtype=np.int64)).to(device)

    steer_l_np = interface.steer_left if interface.steer_left.size else interface.descending_left
    steer_r_np = interface.steer_right if interface.steer_right.size else interface.descending_right
    steer_l = torch.from_numpy(np.asarray(steer_l_np, dtype=np.int64)).to(device)
    steer_r = torch.from_numpy(np.asarray(steer_r_np, dtype=np.int64)).to(device)
    forward_np = np.concatenate((interface.forward_left, interface.forward_right)).astype(np.int64, copy=False)
    forward_idx = torch.from_numpy(forward_np).to(device)

    minimum_distance = initial_distance.clone()
    radial_sum = torch.zeros(batch, dtype=torch.float64, device=device)
    orientation_hits = torch.zeros(batch, dtype=torch.float32, device=device)
    near_hits = torch.zeros(batch, dtype=torch.float32, device=device)
    avoidance_hits = torch.zeros(batch, dtype=torch.float32, device=device)

    with torch.no_grad():
        for _step in range(steps):
            distance = torch.clamp(torch.hypot(x, y), min=1e-9)
            bearing = _wrap_torch(torch.atan2(-y, -x) - heading)
            context = torch.stack(
                (
                    torch.clamp(distance / initial_distance, 0.0, 4.0),
                    torch.sin(bearing),
                    torch.cos(bearing),
                    torch.sin(heading),
                    torch.cos(heading),
                    torch.tanh(previous_radial_velocity),
                ),
                dim=1,
            ).to(torch.float32).reshape(p_count, f_count, CONTEXT_DIM)

            projected = torch.einsum("pic,pfc->pfi", input_weight, context)
            projected = projected + input_bias[:, None, :]
            emitter_drive = float(emitter.input_scale) * torch.tanh(projected)
            emitter_drive = emitter_drive.permute(2, 0, 1).reshape(len(input_indices_np), batch)

            emitter_recurrent = torch.sparse.mm(sparse, emitter_state) / float(emitter.spectral_scale)
            emitter_pre = float(emitter.gain) * emitter_recurrent
            emitter_pre.index_add_(0, input_indices, emitter_drive)
            emitter_state = (
                (1.0 - float(emitter.leak)) * emitter_state
                + float(emitter.leak) * torch.tanh(emitter_pre)
            )

            readout = emitter_state.index_select(0, readout_indices)
            readout = readout.reshape(len(readout_indices_np), p_count, f_count).permute(1, 2, 0)
            raw = torch.einsum("por,pfr->pfo", output_weight, readout) + output_bias[:, None, :]
            bounded = torch.tanh(raw)
            max_bearing = float(np.deg2rad(emitter.max_bearing_offset_deg))
            bearing_offset = max_bearing * bounded[:, :, 0]
            size_scale = torch.exp(float(emitter.max_log_size_scale) * bounded[:, :, 1])
            contrast = 0.5 + 0.5 * bounded[:, :, 2]
            temporal_gate = 0.5 + 0.5 * bounded[:, :, 3]

            apparent_bearing = _wrap_torch(bearing + bearing_offset.reshape(batch).to(torch.float64))
            physical_size = float(base_stimulus.physical_size) * size_scale.reshape(batch).to(torch.float64)
            angular_size = 2.0 * torch.atan2(physical_size / 2.0, distance)
            target_norm = torch.clamp(apparent_bearing / float(arena.target_fov_rad), -1.0, 1.0).to(torch.float32)
            sigma = torch.clamp(
                (angular_size / float(arena.target_fov_rad) / 2.355).to(torch.float32),
                min=float(arena.visual_sigma_floor),
            )
            delta = visual_azimuth - target_norm[None, :]
            visual = torch.exp(-0.5 * (delta / sigma[None, :]) ** 2)
            amplitude = (
                float(base_stimulus.contrast)
                * contrast.reshape(batch)
                * temporal_gate.reshape(batch)
            )
            visual *= amplitude[None, :]

            receiver_recurrent = torch.sparse.mm(sparse, receiver_state) / float(receiver.spectral_scale)
            receiver_pre = float(receiver.gain) * receiver_recurrent
            receiver_pre.index_add_(0, visual_idx, float(receiver.visual_scale) * visual)
            if courtship_idx.numel():
                prime = torch.full(
                    (courtship_idx.numel(), batch),
                    float(receiver.prime_scale),
                    dtype=torch.float32,
                    device=device,
                )
                receiver_pre.index_add_(0, courtship_idx, prime)
            receiver_state = (
                (1.0 - float(receiver.leak)) * receiver_state
                + float(receiver.leak) * torch.tanh(receiver_pre)
            )

            left = receiver_state.index_select(0, steer_l).mean(dim=0) if steer_l.numel() else torch.zeros(batch, device=device)
            right = receiver_state.index_select(0, steer_r).mean(dim=0) if steer_r.numel() else torch.zeros(batch, device=device)
            turn = torch.tanh(float(arena.motor_turn_gain) * (right - left))
            if forward_idx.numel():
                forward_drive = receiver_state.index_select(0, forward_idx).mean(dim=0)
                forward = torch.clamp(
                    float(arena.base_speed) + float(arena.motor_speed_gain) * torch.tanh(4.0 * forward_drive),
                    min=0.0,
                )
            else:
                bilateral = 0.5 * (torch.abs(left) + torch.abs(right))
                forward = torch.clamp(
                    float(arena.base_speed) + float(arena.motor_speed_gain) * torch.tanh(4.0 * bilateral),
                    min=0.0,
                )

            heading = _wrap_torch(
                heading + turn.to(torch.float64) * float(arena.turn_rate_rad_s * arena.dt)
            )
            x = x + forward.to(torch.float64) * torch.cos(heading) * float(arena.dt)
            y = y + forward.to(torch.float64) * torch.sin(heading) * float(arena.dt)
            new_distance = torch.clamp(torch.hypot(x, y), min=1e-9)
            radial_velocity = (previous_distance - new_distance) / float(arena.dt)
            physical_bearing = _wrap_torch(torch.atan2(-y, -x) - heading)

            minimum_distance = torch.minimum(minimum_distance, new_distance)
            radial_sum += radial_velocity
            orientation_hits += (torch.abs(physical_bearing) <= np.deg2rad(30.0)).to(torch.float32)
            near_hits += (new_distance <= float(arena.near_radius)).to(torch.float32)
            avoidance_hits += (radial_velocity < 0).to(torch.float32)
            previous_distance = new_distance
            previous_radial_velocity = radial_velocity

    reduction = (initial_distance - minimum_distance) / torch.clamp(initial_distance, min=1e-12)
    metrics_t = {
        "initial_distance": initial_distance,
        "final_distance": previous_distance,
        "minimum_distance": minimum_distance,
        "normalized_distance_reduction": reduction,
        "mean_radial_velocity": radial_sum / float(steps),
        "orientation_fraction_30deg": orientation_hits / float(steps),
        "near_time_fraction": near_hits / float(steps),
        "approach": (reduction >= 0.5).to(torch.float32),
        "avoidance_fraction": avoidance_hits / float(steps),
    }
    return GeneratorPopulationBatch(
        metrics={
            name: value.reshape(p_count, f_count).to(torch.float32).cpu().numpy()
            for name, value in metrics_t.items()
        }
    )
