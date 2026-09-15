from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
import scipy.sparse as sp

from visual_attractor import ArenaConfig, BrainConfig, FlyPose, Interface, StimulusSpec


def _torch():
    try:
        import torch
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "batched simulation needs the optional gpu dependency: pip install -e '.[gpu]'"
        ) from exc
    return torch


def scipy_csr_to_torch(matrix: sp.csr_matrix, *, device: str):
    torch = _torch()
    csr = matrix.tocsr().astype(np.float32, copy=False)
    crow = torch.from_numpy(csr.indptr.astype(np.int64, copy=False)).to(device)
    col = torch.from_numpy(csr.indices.astype(np.int64, copy=False)).to(device)
    values = torch.from_numpy(csr.data.astype(np.float32, copy=False)).to(device)
    return torch.sparse_csr_tensor(
        crow,
        col,
        values,
        size=csr.shape,
        dtype=torch.float32,
        device=device,
    )


def _wrap_torch(angle):
    torch = _torch()
    return torch.remainder(angle + torch.pi, 2 * torch.pi) - torch.pi


@dataclass(frozen=True)
class BatchSimulation:
    stimulus_names: tuple[str, ...]
    flies_per_stimulus: int
    trajectory: dict[str, np.ndarray]
    metrics: dict[str, np.ndarray]

    def stimulus_summary(self) -> dict[str, dict[str, float]]:
        out: dict[str, dict[str, float]] = {}
        f = self.flies_per_stimulus
        for i, name in enumerate(self.stimulus_names):
            sl = slice(i * f, (i + 1) * f)
            out[name] = {
                key: float(np.mean(values[sl]))
                for key, values in self.metrics.items()
            }
        return out


def simulate_stimulus_swarm_batch(
    operator: sp.csr_matrix,
    interface: Interface,
    stimuli: Sequence[StimulusSpec],
    starts: Sequence[FlyPose],
    *,
    steps: int,
    brain: BrainConfig,
    arena: ArenaConfig = ArenaConfig(),
    device: str = "cuda",
    torch_operator=None,
) -> BatchSimulation:
    """Evaluate S stimuli x F matched starts with one sparse ``W @ X`` per step.

    Columns are independent recurrent trajectories. Starts are repeated exactly
    across stimuli, so candidate/control comparisons use common random numbers.
    Only behavioural/readout trajectories are retained; full 165k-neuron state
    histories are intentionally discarded.
    """
    torch = _torch()
    stimulus_values = tuple(stimuli)
    start_values = tuple(starts)
    if not stimulus_values:
        raise ValueError("at least one stimulus required")
    if not start_values:
        raise ValueError("at least one fly start required")
    if steps < 1:
        raise ValueError("steps must be >= 1")

    s_count = len(stimulus_values)
    f_count = len(start_values)
    batch = s_count * f_count
    neurons = operator.shape[0]

    sparse = (
        torch_operator
        if torch_operator is not None
        else scipy_csr_to_torch(operator, device=device)
    )
    state = torch.zeros((neurons, batch), dtype=torch.float32, device=device)

    # Stimulus-major columns: [stim0/fly0..F, stim1/fly0..F, ...].
    start_x = np.asarray([p.x for p in start_values], dtype=np.float64)
    start_y = np.asarray([p.y for p in start_values], dtype=np.float64)
    start_h = np.asarray([p.heading for p in start_values], dtype=np.float64)
    x = torch.from_numpy(np.tile(start_x, s_count)).to(device=device, dtype=torch.float64)
    y = torch.from_numpy(np.tile(start_y, s_count)).to(device=device, dtype=torch.float64)
    heading = torch.from_numpy(np.tile(start_h, s_count)).to(device=device, dtype=torch.float64)
    initial_distance = torch.hypot(x, y)
    previous_distance = initial_distance.clone()

    physical_size = torch.tensor(
        np.repeat([v.physical_size for v in stimulus_values], f_count),
        device=device,
        dtype=torch.float64,
    )
    offsets = np.asarray(
        [
            [v.path_offset_rad(step * arena.dt) for v in stimulus_values]
            for step in range(steps + 1)
        ],
        dtype=np.float64,
    )
    amplitudes = np.asarray(
        [
            [v.flicker(step * arena.dt) for v in stimulus_values]
            for step in range(steps)
        ],
        dtype=np.float32,
    )
    offsets_t = torch.from_numpy(np.repeat(offsets, f_count, axis=1)).to(
        device=device, dtype=torch.float64
    )
    amplitudes_t = torch.from_numpy(np.repeat(amplitudes, f_count, axis=1)).to(
        device=device
    )

    visual_idx = torch.from_numpy(
        np.asarray(interface.visual_indices, dtype=np.int64)
    ).to(device)
    visual_azimuth = torch.from_numpy(
        np.asarray(interface.visual_azimuth, dtype=np.float32)
    ).to(device)[:, None]
    courtship_idx = torch.from_numpy(
        np.asarray(interface.courtship_indices, dtype=np.int64)
    ).to(device)

    steer_l_np = (
        interface.steer_left
        if interface.steer_left.size
        else interface.descending_left
    )
    steer_r_np = (
        interface.steer_right
        if interface.steer_right.size
        else interface.descending_right
    )
    steer_l = torch.from_numpy(np.asarray(steer_l_np, dtype=np.int64)).to(device)
    steer_r = torch.from_numpy(np.asarray(steer_r_np, dtype=np.int64)).to(device)
    forward_np = np.concatenate(
        (interface.forward_left, interface.forward_right)
    ).astype(np.int64, copy=False)
    forward_idx = torch.from_numpy(forward_np).to(device)

    fields = (
        "x",
        "y",
        "heading",
        "distance",
        "target_bearing",
        "angular_size",
        "orientation_error",
        "radial_velocity",
        "descending_left",
        "descending_right",
        "forward_command",
        "turn_command",
        "visual_rms",
    )
    traces = {
        name: torch.empty((steps, batch), dtype=torch.float32, device=device)
        for name in fields
    }

    gain = float(brain.gain)
    leak = float(brain.leak)
    recurrent_scale = float(brain.spectral_scale)

    with torch.no_grad():
        for step in range(steps):
            lure_bearing = _wrap_torch(torch.atan2(-y, -x) - heading)
            apparent_bearing = _wrap_torch(lure_bearing + offsets_t[step])
            distance = torch.clamp(torch.hypot(x, y), min=1e-9)
            angular_size = 2.0 * torch.atan2(physical_size / 2.0, distance)
            target_norm = torch.clamp(
                apparent_bearing / float(arena.target_fov_rad), -1.0, 1.0
            ).to(torch.float32)
            sigma = torch.clamp(
                (
                    angular_size
                    / float(arena.target_fov_rad)
                    / 2.355
                ).to(torch.float32),
                min=float(arena.visual_sigma_floor),
            )
            delta = visual_azimuth - target_norm[None, :]
            visual = torch.exp(-0.5 * (delta / sigma[None, :]) ** 2)
            visual *= amplitudes_t[step][None, :]

            recurrent = torch.sparse.mm(sparse, state) / recurrent_scale
            pre = recurrent * gain
            pre.index_add_(0, visual_idx, float(brain.visual_scale) * visual)
            if courtship_idx.numel():
                prime = torch.full(
                    (courtship_idx.numel(), batch),
                    float(brain.prime_scale),
                    dtype=torch.float32,
                    device=device,
                )
                pre.index_add_(0, courtship_idx, prime)
            state = (1.0 - leak) * state + leak * torch.tanh(pre)

            left = (
                state.index_select(0, steer_l).mean(dim=0)
                if steer_l.numel()
                else torch.zeros(batch, device=device)
            )
            right = (
                state.index_select(0, steer_r).mean(dim=0)
                if steer_r.numel()
                else torch.zeros(batch, device=device)
            )
            turn = torch.tanh(float(arena.motor_turn_gain) * (right - left))
            if forward_idx.numel():
                forward_drive = state.index_select(0, forward_idx).mean(dim=0)
                forward = torch.clamp(
                    float(arena.base_speed)
                    + float(arena.motor_speed_gain)
                    * torch.tanh(4.0 * forward_drive),
                    min=0.0,
                )
            else:
                bilateral = 0.5 * (torch.abs(left) + torch.abs(right))
                forward = torch.clamp(
                    float(arena.base_speed)
                    + float(arena.motor_speed_gain)
                    * torch.tanh(4.0 * bilateral),
                    min=0.0,
                )

            heading = _wrap_torch(
                heading
                + turn.to(torch.float64)
                * float(arena.turn_rate_rad_s * arena.dt)
            )
            x = x + forward.to(torch.float64) * torch.cos(heading) * float(arena.dt)
            y = y + forward.to(torch.float64) * torch.sin(heading) * float(arena.dt)

            new_distance = torch.clamp(torch.hypot(x, y), min=1e-9)
            new_lure_bearing = _wrap_torch(torch.atan2(-y, -x) - heading)
            new_target_bearing = _wrap_torch(
                new_lure_bearing + offsets_t[step + 1]
            )
            new_angular_size = 2.0 * torch.atan2(
                physical_size / 2.0, new_distance
            )
            radial_velocity = (previous_distance - new_distance) / float(arena.dt)
            orientation_error = torch.abs(new_lure_bearing)
            visual_rms = torch.sqrt(
                torch.sum(visual * visual, dim=0) / float(neurons)
            )

            values = {
                "x": x,
                "y": y,
                "heading": heading,
                "distance": new_distance,
                "target_bearing": new_target_bearing,
                "angular_size": new_angular_size,
                "orientation_error": orientation_error,
                "radial_velocity": radial_velocity,
                "descending_left": left,
                "descending_right": right,
                "forward_command": forward,
                "turn_command": turn,
                "visual_rms": visual_rms,
            }
            for name, value in values.items():
                traces[name][step] = value.to(torch.float32)
            previous_distance = new_distance

    distance_trace = traces["distance"]
    radial_trace = traces["radial_velocity"]
    orientation_trace = traces["orientation_error"]
    minimum_distance = torch.min(distance_trace, dim=0).values
    reduction = (
        initial_distance.to(torch.float32) - minimum_distance
    ) / torch.clamp(initial_distance.to(torch.float32), min=1e-12)
    metrics_t = {
        "initial_distance": initial_distance.to(torch.float32),
        "final_distance": distance_trace[-1],
        "minimum_distance": minimum_distance,
        "normalized_distance_reduction": reduction,
        "mean_radial_velocity": radial_trace.mean(dim=0),
        "orientation_fraction_30deg": (
            orientation_trace <= np.deg2rad(30.0)
        ).to(torch.float32).mean(dim=0),
        "near_time_fraction": (
            distance_trace <= float(arena.near_radius)
        ).to(torch.float32).mean(dim=0),
        "approach": (reduction >= 0.5).to(torch.float32),
        "avoidance_fraction": (radial_trace < 0).to(torch.float32).mean(dim=0),
    }

    return BatchSimulation(
        stimulus_names=tuple(v.name for v in stimulus_values),
        flies_per_stimulus=f_count,
        trajectory={name: value.cpu().numpy() for name, value in traces.items()},
        metrics={name: value.cpu().numpy() for name, value in metrics_t.items()},
    )
