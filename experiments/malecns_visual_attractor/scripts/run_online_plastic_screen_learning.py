from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

import run_visual_efficiency_curriculum as v1
import run_visual_efficiency_curriculum_v3 as v3
import run_visual_efficiency_curriculum_v5 as v5
import run_visual_efficiency_curriculum_v6 as v6
from gpu_batch import scipy_csr_to_torch
from reward_plastic_adapter import RewardPlasticAdapter
from screen_reward_loop import initial_transducer, load_screen_geometry, sensor_grid_ascii, top_receptors
from visual_attractor import ArenaConfig, load_graph, load_interface
from visual_efficiency import CONDITIONS, fixed_spatial_permutation, matched_offset_starts


def _torch():
    import torch

    return torch


def _screen_params_from_channels(channels, *, device: str):
    torch = _torch()
    bounded = torch.as_tensor(channels, dtype=torch.float32, device=device)[None, :]
    return {
        "x_offset": 0.30 * bounded[:, 0],
        "y_offset": 0.35 * bounded[:, 1],
        "size_scale": torch.exp(0.55 * bounded[:, 2]),
        "orientation": torch.pi * bounded[:, 3],
        "contrast": 0.5 + 0.5 * bounded[:, 4],
        "wing_spread": 0.15 + 0.09 * bounded[:, 5],
    }


def _load_weight(path: Path | None, *, seed: int) -> tuple[np.ndarray, str]:
    if path is not None:
        archive = np.load(path, allow_pickle=False)
        weight = np.asarray(archive["weight"], dtype=np.float32)
        if weight.shape != (6, 6):
            raise RuntimeError(f"initial transducer must be 6x6, got {weight.shape}")
        return weight, "resumed"
    weight, _ = initial_transducer(seed=seed, scale=0.25)
    return weight, "fresh"


def run_episode(
    *,
    graph,
    interface,
    geometry,
    sparse,
    adapter: RewardPlasticAdapter,
    flies: int,
    steps: int,
    radius: float,
    heading_offset_deg: float,
    budget: float,
    seed: int,
    spectral_scale: float,
    gain: float,
    leak: float,
    visual_scale: float,
    reward_scale: float,
    reward_feedback_gain: float,
    latent_gain: float,
    plastic_reward_gain: float,
    telemetry_every: int,
    arena: ArenaConfig,
    device: str,
    progress_path: Path,
):
    torch = _torch()
    conditions = len(CONDITIONS)
    neurons = graph.shape[0]

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
    permutation_np = fixed_spatial_permutation(geometry.resolved, seed=seed + 70000)
    permutation = torch.from_numpy(permutation_np).to(device=device, dtype=torch.long)

    start_x, start_y, start_h = matched_offset_starts(
        flies=flies,
        radius=radius,
        seed=seed,
        heading_offset_deg=heading_offset_deg,
    )
    x = torch.from_numpy(np.repeat(start_x[None, None, :], conditions, axis=0)).to(device=device, dtype=torch.float64)
    y = torch.from_numpy(np.repeat(start_y[None, None, :], conditions, axis=0)).to(device=device, dtype=torch.float64)
    heading = torch.from_numpy(np.repeat(start_h[None, None, :], conditions, axis=0)).to(device=device, dtype=torch.float64)
    initial_distance = torch.hypot(x, y)
    min_distance = initial_distance.clone()

    generator_state = torch.zeros((neurons, 1), dtype=torch.float32, device=device)
    receiver_state = torch.zeros((neurons, conditions * flies), dtype=torch.float32, device=device)

    rng = np.random.default_rng(seed + 10000)
    seed_state = rng.normal(0.0, 0.02, size=(desc_all.numel(), 1)).astype(np.float32)
    generator_state.index_copy_(0, desc_all, torch.from_numpy(seed_state).to(device))
    reward_projection_np = rng.normal(0.0, 1.0, size=desc_all.numel()).astype(np.float32)
    reward_projection_np /= max(float(np.linalg.norm(reward_projection_np)), 1e-12)
    reward_projection = torch.from_numpy(reward_projection_np).to(device)
    previous_reward = torch.zeros(1, dtype=torch.float32, device=device)

    cumulative = torch.zeros(conditions, dtype=torch.float32, device=device)
    peak_reward = -np.inf
    peak_visual = np.zeros(len(geometry.bodies), dtype=np.float32)
    peak_step = 0
    reward_signal_sum = 0.0
    max_energy_mismatch = 0.0
    physical_size = float(2.0 * radius * np.tan(np.deg2rad(15.0)))
    t0 = time.perf_counter()

    # Same physical display and exact-energy policy as the clean v5 comparison.
    v6._install_v6_renderer()
    v3._install_v3_boundaries()
    v5._install_v5_boundaries()

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
            latent_np = latent[0].detach().cpu().numpy().astype(np.float32)
            noise_np = rng.normal(0.0, 1.0, size=6).astype(np.float32)
            channels_np = adapter.propose(latent_np, noise_np)
            params = _screen_params_from_channels(channels_np, device=device)

            learned_raw, _, _ = v3._render_body_pattern_on_screen(
                receptor_x=receptor_x,
                receptor_y=receptor_y,
                x=x[0],
                y=y[0],
                heading=heading[0],
                physical_size=physical_size,
                params=params,
                target_fov_rad=arena.target_fov_rad,
            )
            uniform_raw = v3._render_uniform_tv_hard(
                receptor_x=receptor_x,
                receptor_y=receptor_y,
                x=x[1],
                y=y[1],
                heading=heading[1],
                physical_size=physical_size,
                target_fov_rad=arena.target_fov_rad,
            )
            shuffled_raw = learned_raw.index_select(0, permutation)

            common_target = v5._common_target_v5(
                learned_raw,
                uniform_raw,
                shuffled_raw,
                resolved_mask=resolved,
                budget=float(budget),
            )
            learned = v5._normalize_exact_v5(learned_raw, resolved, common_target)
            uniform_tv = v5._normalize_exact_v5(uniform_raw, resolved, common_target)
            spatial_shuffle = v5._normalize_exact_v5(shuffled_raw, resolved, common_target)
            blank = torch.zeros_like(learned)
            delivered = [v3._delivered_mean(v, resolved) for v in (learned, uniform_tv, spatial_shuffle)]
            mismatch = torch.maximum(
                torch.abs(delivered[1] - delivered[0]),
                torch.abs(delivered[2] - delivered[0]),
            )
            max_energy_mismatch = max(max_energy_mismatch, float(mismatch.max().detach().cpu()))

            external = torch.cat(
                [v.reshape(len(geometry.bodies), flies) for v in (learned, uniform_tv, spatial_shuffle, blank)],
                dim=1,
            )
            recurrent_r = torch.sparse.mm(sparse, receiver_state) / float(spectral_scale)
            pre_r = float(gain) * recurrent_r
            pre_r.index_add_(0, visual_idx, float(visual_scale) * external)
            receiver_state = (1.0 - float(leak)) * receiver_state + float(leak) * torch.tanh(pre_r)

            desc_exc_flat = receiver_state.index_select(0, desc_all).abs().mean(dim=0)
            desc_exc = desc_exc_flat.reshape(conditions, flies).mean(dim=1)
            cumulative += desc_exc * float(arena.dt)
            previous_reward = torch.tanh(float(reward_feedback_gain) * desc_exc[0:1])

            # The plastic layer learns STRUCTURE, not raw brightness: reward is the
            # receiver excitation advantage over an energy-matched uniform TV.
            reward_delta = float((desc_exc[0] - desc_exc[1]).detach().cpu())
            reward_signal = float(np.tanh(float(plastic_reward_gain) * reward_delta))
            learning_stats = adapter.update(latent_np, noise_np, reward_signal)
            reward_signal_sum += reward_signal

            left = v1._mean_rows(receiver_state, steer_l).reshape(conditions, flies)
            right = v1._mean_rows(receiver_state, steer_r).reshape(conditions, flies)
            turn = torch.tanh(float(arena.motor_turn_gain) * (right - left))
            forward_state = torch.cat((forward_l, forward_r))
            forward_drive = v1._mean_rows(receiver_state, forward_state).reshape(conditions, flies)
            forward = torch.clamp(
                float(arena.base_speed) + float(arena.motor_speed_gain) * torch.tanh(4.0 * forward_drive),
                min=0.0,
            )
            heading = torch.remainder(
                heading + turn[:, None, :].squeeze(1).to(torch.float64)[:, None, :] * float(arena.turn_rate_rad_s * arena.dt) + torch.pi,
                2 * torch.pi,
            ) - torch.pi
            # heading above is conditions x 1 x flies; keep pose shapes aligned.
            x = x + forward[:, None, :].to(torch.float64) * torch.cos(heading) * float(arena.dt)
            y = y + forward[:, None, :].to(torch.float64) * torch.sin(heading) * float(arena.dt)
            min_distance = torch.minimum(min_distance, torch.hypot(x, y))

            learned_now = float(desc_exc[0].detach().cpu())
            if learned_now > peak_reward:
                peak_reward = learned_now
                peak_visual = learned.mean(dim=2)[:, 0].detach().cpu().numpy().astype(np.float32)
                peak_step = step

            if telemetry_every > 0 and ((step + 1) % telemetry_every == 0 or step == steps - 1):
                payload = {
                    "event": "plastic_learning_telemetry",
                    "step": step + 1,
                    "steps": steps,
                    "budget": float(budget),
                    "reward_signal": reward_signal,
                    "reward_signal_mean": reward_signal_sum / float(step + 1),
                    "condition_reward": {
                        CONDITIONS[i]: float(cumulative[i].detach().cpu()) for i in range(conditions)
                    },
                    "weight_norm": learning_stats["weight_norm"],
                    "eligibility_norm": learning_stats["eligibility_norm"],
                    "reward_baseline": learning_stats["baseline"],
                    "max_energy_mismatch": max_energy_mismatch,
                    "elapsed_s": round(time.perf_counter() - t0, 3),
                }
                line = json.dumps(payload, sort_keys=True)
                print(line, flush=True)
                with progress_path.open("a", encoding="utf-8") as stream:
                    stream.write(line + "\n")

    reduction = (initial_distance - min_distance) / torch.clamp(initial_distance, min=1e-12)
    approach = (reduction >= 0.5).to(torch.float32).mean(dim=2)[:, 0].detach().cpu().numpy()
    return {
        "condition_reward": cumulative.detach().cpu().numpy(),
        "approach": approach,
        "peak_reward": float(peak_reward),
        "peak_step": int(peak_step),
        "peak_visual": peak_visual,
        "max_energy_mismatch": float(max_energy_mismatch),
        "mean_reward_signal": float(reward_signal_sum / max(steps, 1)),
        "weight_norm": float(np.linalg.norm(adapter.weight)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--interface", type=Path, required=True)
    parser.add_argument("--screen-geometry", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--initial-transducer", type=Path)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--flies", type=int, default=8)
    parser.add_argument("--steps", type=int, default=600)
    parser.add_argument("--episodes-per-budget", type=int, default=4)
    parser.add_argument("--budgets", default="0.004,0.002,0.001")
    parser.add_argument("--radius", type=float, default=0.75)
    parser.add_argument("--heading-offset-deg", type=float, default=45.0)
    parser.add_argument("--seed", type=int, default=20260915)
    parser.add_argument("--spectral-scale", type=float, default=3776.27)
    parser.add_argument("--gain", type=float, default=1.0)
    parser.add_argument("--leak", type=float, default=0.2)
    parser.add_argument("--visual-scale", type=float, default=0.5)
    parser.add_argument("--reward-scale", type=float, default=0.08)
    parser.add_argument("--reward-feedback-gain", type=float, default=1000.0)
    parser.add_argument("--latent-gain", type=float, default=20000.0)
    parser.add_argument("--plastic-reward-gain", type=float, default=1e8)
    parser.add_argument("--learning-rate", type=float, default=0.02)
    parser.add_argument("--exploration-sigma", type=float, default=0.08)
    parser.add_argument("--eligibility-decay", type=float, default=0.95)
    parser.add_argument("--baseline-rate", type=float, default=0.02)
    parser.add_argument("--telemetry-every", type=int, default=100)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    progress_path = args.output_dir / "plastic-progress.jsonl"
    progress_path.write_text("", encoding="utf-8")
    budgets = [float(v) for v in args.budgets.split(",") if v.strip()]
    graph = load_graph(args.graph)
    interface = load_interface(args.interface)
    geometry = load_screen_geometry(args.screen_geometry)
    sparse = scipy_csr_to_torch(graph, device=args.device)
    arena = ArenaConfig(dt=0.02)

    initial_weight, learning_mode = _load_weight(args.initial_transducer, seed=args.seed)
    adapter = RewardPlasticAdapter.from_weight(
        initial_weight,
        learning_rate=args.learning_rate,
        exploration_sigma=args.exploration_sigma,
        eligibility_decay=args.eligibility_decay,
        baseline_rate=args.baseline_rate,
    )

    episodes = []
    best_peak_visual = np.zeros(len(geometry.bodies), dtype=np.float32)
    best_advantage = -np.inf
    for budget_index, budget in enumerate(budgets):
        for episode in range(args.episodes_per_budget):
            result = run_episode(
                graph=graph,
                interface=interface,
                geometry=geometry,
                sparse=sparse,
                adapter=adapter,
                flies=args.flies,
                steps=args.steps,
                radius=args.radius,
                heading_offset_deg=args.heading_offset_deg,
                budget=budget,
                seed=args.seed + 1000 * budget_index + episode,
                spectral_scale=args.spectral_scale,
                gain=args.gain,
                leak=args.leak,
                visual_scale=args.visual_scale,
                reward_scale=args.reward_scale,
                reward_feedback_gain=args.reward_feedback_gain,
                latent_gain=args.latent_gain,
                plastic_reward_gain=args.plastic_reward_gain,
                telemetry_every=args.telemetry_every,
                arena=arena,
                device=args.device,
                progress_path=progress_path,
            )
            rewards = result["condition_reward"]
            advantage = float(rewards[0] - max(rewards[1:]))
            row = {
                "budget": budget,
                "episode": episode,
                "advantage": advantage,
                "condition_reward": {CONDITIONS[i]: float(rewards[i]) for i in range(len(CONDITIONS))},
                "approach": {CONDITIONS[i]: float(result["approach"][i]) for i in range(len(CONDITIONS))},
                "mean_reward_signal": result["mean_reward_signal"],
                "weight_norm": result["weight_norm"],
                "max_energy_mismatch": result["max_energy_mismatch"],
            }
            episodes.append(row)
            print(json.dumps({"event": "plastic_episode_complete", **row}, sort_keys=True), flush=True)
            if advantage > best_advantage:
                best_advantage = advantage
                best_peak_visual = result["peak_visual"].copy()

    np.savez_compressed(
        args.output_dir / "plastic-adapter.npz",
        weight=adapter.weight,
        eligibility=adapter.eligibility,
        baseline=np.asarray(adapter.baseline, dtype=np.float32),
    )
    # Compatibility checkpoint for subsequent visual-efficiency runners.
    np.savez_compressed(
        args.output_dir / "best-efficiency-transducer.npz",
        weight=adapter.weight,
        peak_visual=best_peak_visual,
    )
    (args.output_dir / "winner-retina.txt").write_text(
        sensor_grid_ascii(best_peak_visual, geometry, width=64) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "winner-top-receptors.json").write_text(
        json.dumps(top_receptors(best_peak_visual, geometry, k=32), indent=2) + "\n",
        encoding="utf-8",
    )
    summary = {
        "experiment": "malecns-online-reward-plastic-screen-v1",
        "scientific_status": "engineering calibration; online reward-modulated plastic adapter",
        "learning_state": {
            "mode": learning_mode,
            "persisted_object": "6x6 reward-plastic body-latent-to-screen adapter",
        },
        "learning_rule": {
            "type": "reward-modulated node perturbation with eligibility trace",
            "reward": "tanh-scaled receiver descending-excitation advantage over energy-matched uniform TV",
            "learning_rate": args.learning_rate,
            "exploration_sigma": args.exploration_sigma,
            "eligibility_decay": args.eligibility_decay,
            "baseline_rate": args.baseline_rate,
            "plastic_reward_gain": args.plastic_reward_gain,
        },
        "parameters": {
            "budgets": budgets,
            "episodes_per_budget": args.episodes_per_budget,
            "steps": args.steps,
            "flies": args.flies,
        },
        "best_training_advantage": best_advantage,
        "episodes": episodes,
        "final_weight_norm": float(np.linalg.norm(adapter.weight)),
        "max_energy_mismatch": max((row["max_energy_mismatch"] for row in episodes), default=0.0),
    }
    (args.output_dir / "plastic-learning-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"event": "plastic_learning_complete", "best_advantage": best_advantage, "learning_mode": learning_mode}, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
