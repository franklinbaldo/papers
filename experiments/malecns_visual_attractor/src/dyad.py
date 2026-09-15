from __future__ import annotations

from dataclasses import dataclass
from math import pi, tan
from typing import Sequence

import numpy as np
import scipy.sparse as sp

from gpu_batch import scipy_csr_to_torch
from visual_attractor import ArenaConfig, BrainConfig, FlyPose, Interface


DYAD_CONDITIONS = ("reciprocal", "one_way", "static_pair", "blank_pair")


def _torch():
    try:
        import torch
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("dyad simulation needs the optional gpu dependency") from exc
    return torch


def direct_gaze_distance(physical_size: float, apparent_width_deg: float) -> float:
    if physical_size <= 0 or not 0 < apparent_width_deg < 180:
        raise ValueError("invalid target size/apparent width")
    return (physical_size / 2.0) / tan(np.deg2rad(apparent_width_deg / 2.0))


def dyad_starts(*, pairs: int, distance: float, seed: int) -> tuple[tuple[FlyPose, ...], tuple[FlyPose, ...]]:
    """Matched pair starts for every condition.

    The two bodies begin at the registered separation on a random arena axis.
    Body headings are independent. Direct-gaze rendering keeps the partner image
    centered on the receiver retina, so this calibration does not require the
    body heading to find the partner before the visual channel is tested.
    """
    if pairs < 1 or distance <= 0:
        raise ValueError("pairs >= 1 and distance > 0 required")
    rng = np.random.default_rng(seed)
    a: list[FlyPose] = []
    b: list[FlyPose] = []
    for _ in range(pairs):
        axis = float(rng.uniform(-pi, pi))
        dx = 0.5 * distance * np.cos(axis)
        dy = 0.5 * distance * np.sin(axis)
        a.append(FlyPose(float(-dx), float(-dy), float(rng.uniform(-pi, pi))))
        b.append(FlyPose(float(dx), float(dy), float(rng.uniform(-pi, pi))))
    return tuple(a), tuple(b)


@dataclass(frozen=True)
class DyadBatchSimulation:
    condition_names: tuple[str, ...]
    pairs_per_condition: int
    trajectory: dict[str, np.ndarray]
    metrics: dict[str, np.ndarray]

    def condition_summary(self) -> dict[str, dict[str, float]]:
        out: dict[str, dict[str, float]] = {}
        p = self.pairs_per_condition
        for i, name in enumerate(self.condition_names):
            sl = slice(i * p, (i + 1) * p)
            out[name] = {
                key: float(np.mean(values[sl])) for key, values in self.metrics.items()
            }
        return out


def _wrap_torch(angle):
    torch = _torch()
    return torch.remainder(angle + torch.pi, 2 * torch.pi) - torch.pi


def _partner_pattern(
    visual_azimuth,
    distance,
    source_turn,
    *,
    physical_size: float,
    arena: ArenaConfig,
):
    """Render a direct-gaze fly-like 1-D retinal pattern on every mapped receptor.

    The body is centered at zero azimuth. Two side lobes provide a simple
    fly-like silhouette; their asymmetry is driven by the emitter's previous
    turn command. Apparent size is determined by current pair distance. This is
    an engineering visual coupling, not a claim that the pattern is a natural
    Drosophila social signal.
    """
    torch = _torch()
    distance = torch.clamp(distance, min=1e-6)
    angular_size = 2.0 * torch.atan2(
        torch.full_like(distance, float(physical_size / 2.0)), distance
    )
    sigma = torch.clamp(
        (angular_size / float(arena.target_fov_rad) / 2.355).to(torch.float32),
        min=float(arena.visual_sigma_floor),
    )
    az = visual_azimuth[:, None]
    body = torch.exp(-0.5 * (az / sigma[None, :]) ** 2)

    wing_center = 1.35 * sigma
    wing_sigma = torch.clamp(0.55 * sigma, min=float(arena.visual_sigma_floor) / 2.0)
    left_wing = torch.exp(
        -0.5 * ((az + wing_center[None, :]) / wing_sigma[None, :]) ** 2
    )
    right_wing = torch.exp(
        -0.5 * ((az - wing_center[None, :]) / wing_sigma[None, :]) ** 2
    )
    bias = 0.5 * torch.tanh(2.0 * source_turn.to(torch.float32))
    left_amp = 0.35 * (1.0 - bias)
    right_amp = 0.35 * (1.0 + bias)
    return torch.clamp(
        body + left_wing * left_amp[None, :] + right_wing * right_amp[None, :],
        min=0.0,
        max=1.0,
    )


def simulate_direct_gaze_dyads(
    operator: sp.csr_matrix,
    interface: Interface,
    starts_a: Sequence[FlyPose],
    starts_b: Sequence[FlyPose],
    *,
    steps: int,
    brain: BrainConfig,
    physical_size: float = 0.25,
    arena: ArenaConfig = ArenaConfig(),
    device: str = "cuda",
) -> DyadBatchSimulation:
    """Run reciprocal MaleCNS dyads with full mapped visual input.

    Conditions share identical starts:
    - reciprocal: A sees B and B sees A, with distance/turn feedback;
    - one_way: B sees A while A receives no partner image;
    - static_pair: both see the same frozen centered partner pattern;
    - blank_pair: neither receives visual input.

    The full currently mapped visual population is used. Direct gaze deliberately
    removes target acquisition from this calibration: every rendered partner is
    centered on the receiver retina. Both connectomes are frozen.
    """
    torch = _torch()
    a_values = tuple(starts_a)
    b_values = tuple(starts_b)
    if not a_values or len(a_values) != len(b_values):
        raise ValueError("starts_a and starts_b must have the same non-zero length")
    if steps < 1:
        raise ValueError("steps must be >= 1")
    if physical_size <= 0:
        raise ValueError("physical_size must be > 0")

    pairs = len(a_values)
    conditions = DYAD_CONDITIONS
    c_count = len(conditions)
    batch = c_count * pairs
    neurons = operator.shape[0]
    sparse = scipy_csr_to_torch(operator, device=device)

    def tiled(values):
        return np.tile(np.asarray(values, dtype=np.float64), c_count)

    ax = torch.from_numpy(tiled([p.x for p in a_values])).to(device=device)
    ay = torch.from_numpy(tiled([p.y for p in a_values])).to(device=device)
    ah = torch.from_numpy(tiled([p.heading for p in a_values])).to(device=device)
    bx = torch.from_numpy(tiled([p.x for p in b_values])).to(device=device)
    by = torch.from_numpy(tiled([p.y for p in b_values])).to(device=device)
    bh = torch.from_numpy(tiled([p.heading for p in b_values])).to(device=device)

    initial_pair_distance = torch.hypot(ax - bx, ay - by)
    min_pair_distance = initial_pair_distance.clone()
    condition_id = torch.from_numpy(np.repeat(np.arange(c_count), pairs)).to(device)
    reciprocal = (condition_id == 0).to(torch.float32)
    one_way = (condition_id == 1).to(torch.float32)
    static_pair = (condition_id == 2).to(torch.float32)

    visual_idx = torch.from_numpy(np.asarray(interface.visual_indices, dtype=np.int64)).to(device)
    visual_azimuth = torch.from_numpy(np.asarray(interface.visual_azimuth, dtype=np.float32)).to(device)
    courtship_idx = torch.from_numpy(np.asarray(interface.courtship_indices, dtype=np.int64)).to(device)
    steer_l_np = interface.steer_left if interface.steer_left.size else interface.descending_left
    steer_r_np = interface.steer_right if interface.steer_right.size else interface.descending_right
    steer_l = torch.from_numpy(np.asarray(steer_l_np, dtype=np.int64)).to(device)
    steer_r = torch.from_numpy(np.asarray(steer_r_np, dtype=np.int64)).to(device)
    forward_np = np.concatenate((interface.forward_left, interface.forward_right)).astype(np.int64, copy=False)
    forward_idx = torch.from_numpy(forward_np).to(device)

    state = torch.zeros((neurons, 2 * batch), dtype=torch.float32, device=device)
    previous_turn_a = torch.zeros(batch, dtype=torch.float32, device=device)
    previous_turn_b = torch.zeros(batch, dtype=torch.float32, device=device)

    static_zero = torch.zeros(batch, dtype=torch.float32, device=device)
    static_pattern = _partner_pattern(
        visual_azimuth,
        initial_pair_distance,
        static_zero,
        physical_size=physical_size,
        arena=arena,
    )

    trace_names = (
        "pair_distance",
        "visual_rms_a",
        "visual_rms_b",
        "receptor_rms_a",
        "receptor_rms_b",
        "forward_a",
        "forward_b",
        "turn_a",
        "turn_b",
        "x_a",
        "y_a",
        "x_b",
        "y_b",
    )
    traces = {
        name: torch.empty((steps, batch), dtype=torch.float32, device=device)
        for name in trace_names
    }

    gain = float(brain.gain)
    leak = float(brain.leak)
    recurrent_scale = float(brain.spectral_scale)

    def readout(part):
        left = part.index_select(0, steer_l).mean(dim=0) if steer_l.numel() else torch.zeros(batch, device=device)
        right = part.index_select(0, steer_r).mean(dim=0) if steer_r.numel() else torch.zeros(batch, device=device)
        turn = torch.tanh(float(arena.motor_turn_gain) * (right - left))
        if forward_idx.numel():
            forward_drive = part.index_select(0, forward_idx).mean(dim=0)
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
        return forward, turn

    with torch.no_grad():
        for step in range(steps):
            pair_distance = torch.clamp(torch.hypot(ax - bx, ay - by), min=1e-6)
            dynamic_for_a = _partner_pattern(
                visual_azimuth,
                pair_distance,
                previous_turn_b,
                physical_size=physical_size,
                arena=arena,
            )
            dynamic_for_b = _partner_pattern(
                visual_azimuth,
                pair_distance,
                previous_turn_a,
                physical_size=physical_size,
                arena=arena,
            )

            visual_a = (
                dynamic_for_a * reciprocal[None, :]
                + static_pattern * static_pair[None, :]
            )
            visual_b = (
                dynamic_for_b * (reciprocal + one_way)[None, :]
                + static_pattern * static_pair[None, :]
            )
            external = torch.cat((visual_a, visual_b), dim=1)

            recurrent = torch.sparse.mm(sparse, state) / recurrent_scale
            pre = recurrent * gain
            pre.index_add_(0, visual_idx, float(brain.visual_scale) * external)
            if courtship_idx.numel() and brain.prime_scale != 0.0:
                prime = torch.full(
                    (courtship_idx.numel(), 2 * batch),
                    float(brain.prime_scale),
                    dtype=torch.float32,
                    device=device,
                )
                pre.index_add_(0, courtship_idx, prime)
            state = (1.0 - leak) * state + leak * torch.tanh(pre)

            state_a = state[:, :batch]
            state_b = state[:, batch:]
            forward_a, turn_a = readout(state_a)
            forward_b, turn_b = readout(state_b)

            ah = _wrap_torch(ah + turn_a.to(torch.float64) * float(arena.turn_rate_rad_s * arena.dt))
            bh = _wrap_torch(bh + turn_b.to(torch.float64) * float(arena.turn_rate_rad_s * arena.dt))
            ax = ax + forward_a.to(torch.float64) * torch.cos(ah) * float(arena.dt)
            ay = ay + forward_a.to(torch.float64) * torch.sin(ah) * float(arena.dt)
            bx = bx + forward_b.to(torch.float64) * torch.cos(bh) * float(arena.dt)
            by = by + forward_b.to(torch.float64) * torch.sin(bh) * float(arena.dt)

            new_pair_distance = torch.clamp(torch.hypot(ax - bx, ay - by), min=1e-6)
            min_pair_distance = torch.minimum(min_pair_distance, new_pair_distance)
            receptor_a = torch.sqrt(torch.mean(state_a.index_select(0, visual_idx) ** 2, dim=0))
            receptor_b = torch.sqrt(torch.mean(state_b.index_select(0, visual_idx) ** 2, dim=0))
            visual_rms_a = torch.sqrt(torch.mean(visual_a * visual_a, dim=0))
            visual_rms_b = torch.sqrt(torch.mean(visual_b * visual_b, dim=0))

            step_values = {
                "pair_distance": new_pair_distance,
                "visual_rms_a": visual_rms_a,
                "visual_rms_b": visual_rms_b,
                "receptor_rms_a": receptor_a,
                "receptor_rms_b": receptor_b,
                "forward_a": forward_a,
                "forward_b": forward_b,
                "turn_a": turn_a,
                "turn_b": turn_b,
                "x_a": ax,
                "y_a": ay,
                "x_b": bx,
                "y_b": by,
            }
            for name, value in step_values.items():
                traces[name][step] = value.to(torch.float32)
            previous_turn_a = turn_a
            previous_turn_b = turn_b

    reduction = (
        initial_pair_distance.to(torch.float32) - min_pair_distance.to(torch.float32)
    ) / torch.clamp(initial_pair_distance.to(torch.float32), min=1e-12)
    mean_visual = 0.5 * (traces["visual_rms_a"].mean(dim=0) + traces["visual_rms_b"].mean(dim=0))
    mean_receptor = 0.5 * (traces["receptor_rms_a"].mean(dim=0) + traces["receptor_rms_b"].mean(dim=0))
    mean_forward = 0.5 * (traces["forward_a"].mean(dim=0) + traces["forward_b"].mean(dim=0))
    mean_abs_turn = 0.5 * (traces["turn_a"].abs().mean(dim=0) + traces["turn_b"].abs().mean(dim=0))
    metrics_t = {
        "initial_pair_distance": initial_pair_distance.to(torch.float32),
        "final_pair_distance": traces["pair_distance"][-1],
        "minimum_pair_distance": min_pair_distance.to(torch.float32),
        "normalized_pair_distance_reduction": reduction,
        "mean_visual_rms": mean_visual,
        "mean_receptor_rms": mean_receptor,
        "mean_forward": mean_forward,
        "mean_abs_turn": mean_abs_turn,
        "capture": (reduction >= 0.5).to(torch.float32),
    }

    return DyadBatchSimulation(
        condition_names=conditions,
        pairs_per_condition=pairs,
        trajectory={name: value.cpu().numpy() for name, value in traces.items()},
        metrics={name: value.cpu().numpy() for name, value in metrics_t.items()},
    )
