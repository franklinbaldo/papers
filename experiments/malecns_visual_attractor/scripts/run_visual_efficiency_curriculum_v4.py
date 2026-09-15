from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

import run_visual_efficiency_curriculum as v1
import run_visual_efficiency_curriculum_v2 as v2
import run_visual_efficiency_curriculum_v3 as v3
from gpu_batch import scipy_csr_to_torch
from screen_reward_loop import initial_transducer, load_screen_geometry, sensor_grid_ascii, top_receptors
from visual_attractor import ArenaConfig, load_graph, load_interface
from visual_efficiency import CONDITIONS, efficiency_curriculum, fixed_spatial_permutation, matched_offset_starts


def _torch():
    import torch

    return torch


def _attainable_mean(visual, resolved_mask):
    """Maximum mean intensity attainable by positive rescaling under clamp[0,1]."""
    torch = _torch()
    mask = resolved_mask[:, None, None].to(torch.float32)
    base = torch.clamp(visual.to(torch.float32), min=0.0) * mask
    count = torch.clamp(resolved_mask.sum().to(torch.float32), min=1.0)
    return ((base > 0).to(torch.float32) * mask).sum(dim=0) / count


def _common_target(*raw_arms, resolved_mask, budget: float):
    """Per candidate/fly energy target all nonblank arms can physically attain."""
    torch = _torch()
    attainable = [_attainable_mean(arm, resolved_mask) for arm in raw_arms]
    target = torch.full_like(attainable[0], float(budget))
    for value in attainable:
        target = torch.minimum(target, value)
    return target


def run_stage(
    *,
    graph,
    interface,
    geometry,
    sparse,
    weights_np,
    flies: int,
    steps: int,
    radius: float,
    heading_offset_deg: float,
    budget: float,
    start_seed: int,
    generator_seed: int,
    spectral_scale: float,
    gain: float,
    leak: float,
    visual_scale: float,
    reward_scale: float,
    reward_feedback_gain: float,
    latent_gain: float,
    telemetry_every: int,
    arena: ArenaConfig,
    device: str,
    progress_path: Path,
    permutation_seed: int,
):
    torch = _torch()
    conditions = len(CONDITIONS)
    candidates = weights_np.shape[0]
    neurons = graph.shape[0]
    batch_per_condition = candidates * flies
    total_batch = conditions * batch_per_condition

    def idx(values):
        return torch.from_numpy(np.asarray(values, dtype=np.int64)).to(device)

    visual_idx = idx(interface.visual_indices)
    steer_l = idx(interface.steer_left)
    steer_r = idx(interface.steer_right)
    forward_l = idx(interface.forward_left)
    forward_r = idx(interface.forward_right)
    desc_l = idx(interface.descending_left)
    desc_r = idx(interface.descending_right)
    desc_all = torch.unique(torch.cat((desc_l, desc_r)))

    receptor_x = torch.from_numpy(geometry.x).to(device=device, dtype=torch.float32)
    receptor_y = torch.from_numpy(geometry.y).to(device=device, dtype=torch.float32)
    resolved = torch.from_numpy(geometry.resolved.astype(np.float32)).to(device=device)
    permutation_np = fixed_spatial_permutation(geometry.resolved, seed=permutation_seed)
    permutation = torch.from_numpy(permutation_np).to(device=device, dtype=torch.long)
    weights = torch.from_numpy(weights_np).to(device=device, dtype=torch.float32)

    start_x, start_y, start_h = matched_offset_starts(
        flies=flies,
        radius=radius,
        seed=start_seed,
        heading_offset_deg=heading_offset_deg,
    )
    x0 = np.repeat(start_x[None, :], candidates, axis=0)
    y0 = np.repeat(start_y[None, :], candidates, axis=0)
    h0 = np.repeat(start_h[None, :], candidates, axis=0)
    x = torch.from_numpy(np.repeat(x0[None, :, :], conditions, axis=0)).to(device=device, dtype=torch.float64)
    y = torch.from_numpy(np.repeat(y0[None, :, :], conditions, axis=0)).to(device=device, dtype=torch.float64)
    heading = torch.from_numpy(np.repeat(h0[None, :, :], conditions, axis=0)).to(device=device, dtype=torch.float64)
    initial_distance = torch.hypot(x, y)
    min_distance = initial_distance.clone()

    generator_state = torch.zeros((neurons, candidates), dtype=torch.float32, device=device)
    receiver_state = torch.zeros((neurons, total_batch), dtype=torch.float32, device=device)

    rng = np.random.default_rng(generator_seed)
    seed_state = rng.normal(0.0, 0.02, size=(desc_all.numel(), candidates)).astype(np.float32)
    generator_state.index_copy_(0, desc_all, torch.from_numpy(seed_state).to(device))
    reward_projection_np = rng.normal(0.0, 1.0, size=desc_all.numel()).astype(np.float32)
    reward_projection_np /= max(float(np.linalg.norm(reward_projection_np)), 1e-12)
    reward_projection = torch.from_numpy(reward_projection_np).to(device)

    cumulative = torch.zeros((conditions, candidates), dtype=torch.float32, device=device)
    previous_reward = torch.zeros(candidates, dtype=torch.float32, device=device)
    peak_learned_reward = np.full(candidates, -np.inf, dtype=np.float64)
    peak_visual = np.zeros((candidates, len(geometry.bodies)), dtype=np.float32)
    peak_step = np.zeros(candidates, dtype=np.int32)
    max_energy_mismatch = 0.0
    min_common_target = float("inf")
    max_common_target = 0.0
    sum_common_target = 0.0
    common_target_count = 0

    physical_size = float(2.0 * radius * np.tan(np.deg2rad(15.0)))
    t0 = time.perf_counter()

    # Install the common physical aperture used by v3, but v4 controls the
    # common-target normalization explicitly below.
    v3._install_v3_boundaries()

    with torch.no_grad():
        for step in range(steps):
            recurrent_g = torch.sparse.mm(sparse, generator_state) / float(spectral_scale)
            pre_g = float(gain) * recurrent_g
            reward_drive = float(reward_scale) * reward_projection[:, None] * previous_reward[None, :]
            pre_g.index_add_(0, desc_all, reward_drive)
            generator_state = (1.0 - float(leak)) * generator_state + float(leak) * torch.tanh(pre_g)

            latent = v1._body_latent(
                generator_state,
                steer_l=steer_l,
                steer_r=steer_r,
                forward_l=forward_l,
                forward_r=forward_r,
                desc_l=desc_l,
                desc_r=desc_r,
                latent_gain=latent_gain,
            )
            params = v1._screen_params_no_bias(latent, weights)

            learned_raw, _, _ = v1._render_body_pattern(
                receptor_x=receptor_x,
                receptor_y=receptor_y,
                x=x[0],
                y=y[0],
                heading=heading[0],
                physical_size=physical_size,
                params=params,
                target_fov_rad=arena.target_fov_rad,
            )
            uniform_raw = v1._render_uniform_tv(
                receptor_x=receptor_x,
                receptor_y=receptor_y,
                x=x[1],
                y=y[1],
                heading=heading[1],
                physical_size=physical_size,
                target_fov_rad=arena.target_fov_rad,
            )
            shuffled_raw, _, _ = v1._render_body_pattern(
                receptor_x=receptor_x,
                receptor_y=receptor_y,
                x=x[2],
                y=y[2],
                heading=heading[2],
                physical_size=physical_size,
                params=params,
                target_fov_rad=arena.target_fov_rad,
            )
            shuffled_raw = shuffled_raw.index_select(0, permutation)

            common_target = _common_target(
                learned_raw,
                uniform_raw,
                shuffled_raw,
                resolved_mask=resolved,
                budget=float(budget),
            )
            learned = v3._normalize_exact(learned_raw, resolved, common_target)
            uniform_tv = v3._normalize_exact(uniform_raw, resolved, common_target)
            spatial_shuffle = v3._normalize_exact(shuffled_raw, resolved, common_target)
            blank = torch.zeros_like(learned)

            delivered = [v3._delivered_mean(v, resolved) for v in (learned, uniform_tv, spatial_shuffle)]
            mismatch = torch.maximum(
                torch.abs(delivered[1] - delivered[0]),
                torch.abs(delivered[2] - delivered[0]),
            )
            max_energy_mismatch = max(max_energy_mismatch, float(mismatch.max().detach().cpu()))
            target_np = common_target.detach().cpu().numpy()
            min_common_target = min(min_common_target, float(target_np.min()))
            max_common_target = max(max_common_target, float(target_np.max()))
            sum_common_target += float(target_np.sum())
            common_target_count += int(target_np.size)

            visuals = (learned, uniform_tv, spatial_shuffle, blank)
            external = torch.cat(
                [v.reshape(len(geometry.bodies), batch_per_condition) for v in visuals],
                dim=1,
            )

            recurrent_r = torch.sparse.mm(sparse, receiver_state) / float(spectral_scale)
            pre_r = float(gain) * recurrent_r
            pre_r.index_add_(0, visual_idx, float(visual_scale) * external)
            receiver_state = (1.0 - float(leak)) * receiver_state + float(leak) * torch.tanh(pre_r)

            desc_exc_flat = receiver_state.index_select(0, desc_all).abs().mean(dim=0)
            desc_exc = v1._condition_blocks(
                desc_exc_flat,
                conditions=conditions,
                candidates=candidates,
                flies=flies,
            ).mean(dim=2)
            cumulative += desc_exc * float(arena.dt)
            previous_reward = torch.tanh(float(reward_feedback_gain) * desc_exc[0])

            left = v1._condition_blocks(
                v1._mean_rows(receiver_state, steer_l),
                conditions=conditions,
                candidates=candidates,
                flies=flies,
            )
            right = v1._condition_blocks(
                v1._mean_rows(receiver_state, steer_r),
                conditions=conditions,
                candidates=candidates,
                flies=flies,
            )
            turn = torch.tanh(float(arena.motor_turn_gain) * (right - left))
            forward_state = torch.cat((forward_l, forward_r))
            forward_drive = v1._condition_blocks(
                v1._mean_rows(receiver_state, forward_state),
                conditions=conditions,
                candidates=candidates,
                flies=flies,
            )
            forward = torch.clamp(
                float(arena.base_speed) + float(arena.motor_speed_gain) * torch.tanh(4.0 * forward_drive),
                min=0.0,
            )
            heading = torch.remainder(
                heading + turn.to(torch.float64) * float(arena.turn_rate_rad_s * arena.dt) + torch.pi,
                2 * torch.pi,
            ) - torch.pi
            x = x + forward.to(torch.float64) * torch.cos(heading) * float(arena.dt)
            y = y + forward.to(torch.float64) * torch.sin(heading) * float(arena.dt)
            distance_after = torch.hypot(x, y)
            min_distance = torch.minimum(min_distance, distance_after)

            learned_reward_cpu = desc_exc[0].detach().cpu().numpy()
            mean_visual_cpu = learned.mean(dim=2).detach().cpu().numpy().T
            for candidate in range(candidates):
                if learned_reward_cpu[candidate] > peak_learned_reward[candidate]:
                    peak_learned_reward[candidate] = float(learned_reward_cpu[candidate])
                    peak_visual[candidate] = mean_visual_cpu[candidate]
                    peak_step[candidate] = step

            if telemetry_every > 0 and ((step + 1) % telemetry_every == 0 or step == steps - 1):
                cumulative_cpu = cumulative.detach().cpu().numpy()
                advantage = cumulative_cpu[0] - np.max(cumulative_cpu[1:], axis=0)
                winner = int(np.argmax(advantage))
                payload = {
                    "event": "efficiency_telemetry_v4",
                    "budget_ceiling": float(budget),
                    "step": step + 1,
                    "steps": steps,
                    "winner": winner,
                    "advantage": float(advantage[winner]),
                    "condition_reward": {CONDITIONS[i]: float(cumulative_cpu[i, winner]) for i in range(conditions)},
                    "common_target": {
                        "winner_mean": float(common_target[winner].mean().detach().cpu()),
                        "winner_min": float(common_target[winner].min().detach().cpu()),
                        "winner_max": float(common_target[winner].max().detach().cpu()),
                    },
                    "delivered_energy": {
                        CONDITIONS[i]: float(delivered[i][winner].mean().detach().cpu()) for i in range(3)
                    },
                    "max_energy_mismatch": float(max_energy_mismatch),
                    "body_latent": [round(float(v), 6) for v in latent[winner].detach().cpu().numpy()],
                    "screen": {key: round(float(value[winner].detach().cpu()), 6) for key, value in params.items()},
                    "peak_step": int(peak_step[winner]),
                    "elapsed_s": round(time.perf_counter() - t0, 3),
                    "top_receptors": top_receptors(peak_visual[winner], geometry, k=12),
                }
                line = json.dumps(payload, sort_keys=True)
                print(line, flush=True)
                print("RETINA_GRID_BEGIN", flush=True)
                print(sensor_grid_ascii(peak_visual[winner], geometry, width=64), flush=True)
                print("RETINA_GRID_END", flush=True)
                with progress_path.open("a", encoding="utf-8") as stream:
                    stream.write(line + "\n")

    cumulative_cpu = cumulative.detach().cpu().numpy()
    advantage = cumulative_cpu[0] - np.max(cumulative_cpu[1:], axis=0)
    winner = int(np.argmax(advantage))
    reduction = (initial_distance - min_distance) / torch.clamp(initial_distance, min=1e-12)
    approach = (reduction >= 0.5).to(torch.float32).mean(dim=2).detach().cpu().numpy()
    final_distance = torch.hypot(x, y).mean(dim=2).detach().cpu().numpy()
    target_bearing = torch.remainder(torch.atan2(-y, -x) - heading + torch.pi, 2 * torch.pi) - torch.pi
    final_orientation_error = torch.abs(target_bearing).mean(dim=2).detach().cpu().numpy()
    return {
        "winner": winner,
        "advantage": advantage,
        "cumulative_reward": cumulative_cpu,
        "approach": approach,
        "final_distance": final_distance,
        "final_orientation_error": final_orientation_error,
        "peak_visual": peak_visual,
        "peak_step": peak_step,
        "peak_learned_reward": peak_learned_reward,
        "weights": weights_np,
        "max_energy_mismatch": float(max_energy_mismatch),
        "common_target_min": float(min_common_target),
        "common_target_max": float(max_common_target),
        "common_target_mean": float(sum_common_target / max(common_target_count, 1)),
    }


def main() -> None:
    # Reuse v2's curriculum/output orchestration, replacing only the stage physics.
    v2.run_stage = run_stage
    v2.main()

    try:
        output_dir = Path(__import__("sys").argv[__import__("sys").argv.index("--output-dir") + 1])
    except (ValueError, IndexError) as exc:
        raise RuntimeError("v4 requires explicit --output-dir") from exc

    summary_path = output_dir / "visual-efficiency-summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["experiment"] = "malecns-visual-efficiency-curriculum-v4"
    summary["scientific_status"] = "engineering calibration; common physical aperture + common attainable exact energy"
    summary["energy_policy"] = {
        "ceiling_metric": "mean intensity over optic-column-resolved receptors",
        "screen_aperture": "same hard 16:9 physical screen aperture for learned and uniform-TV",
        "common_target": "per candidate/fly/frame min(nominal budget, attainable learned, attainable uniform-TV, attainable spatial-shuffle)",
        "normalization": "all three nonblank arms, including learned, are scaled by bisection to the common target",
        "spatial_shuffle": "retinal structure-destruction control; energy matched but not a physical display candidate",
        "unresolved_receptors": "present in MaleCNS state but receive zero screen drive",
        "mismatch_gate": 1e-5,
    }
    max_mismatch = max(float(row["max_energy_mismatch"]) for row in summary["stages"])
    summary["max_energy_mismatch_all_stages"] = max_mismatch
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"event": "visual_efficiency_v4_gate", "max_energy_mismatch": max_mismatch}, sort_keys=True), flush=True)
    if max_mismatch > 1e-5:
        raise RuntimeError(f"energy matching gate failed: {max_mismatch} > 1e-5")


if __name__ == "__main__":
    main()
