from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

import run_visual_efficiency_curriculum as v1
from gpu_batch import scipy_csr_to_torch
from screen_reward_loop import initial_transducer, load_screen_geometry, sensor_grid_ascii, top_receptors
from visual_attractor import ArenaConfig, load_graph, load_interface
from visual_efficiency import CONDITIONS, efficiency_curriculum, fixed_spatial_permutation, matched_offset_starts


def _torch():
    import torch

    return torch


def _normalize_to_target(visual, resolved_mask, target, *, iterations: int = 8):
    """Match delivered mean energy to a scalar or per-candidate/per-fly target.

    The learned arm is first normalized toward the registered ceiling. Its actual
    delivered mean after clipping is then used as the exact target for the two
    nonblank controls in the same frame. This prevents clipping/support geometry
    from giving any condition a hidden energy advantage.
    """
    torch = _torch()
    mask = resolved_mask[:, None, None]
    out = torch.clamp(visual.to(torch.float32), min=0.0, max=1.0) * mask
    count = torch.clamp(resolved_mask.sum().to(torch.float32), min=1.0)
    target_t = torch.as_tensor(target, dtype=torch.float32, device=visual.device)
    for _ in range(max(1, int(iterations))):
        current = out.sum(dim=0) / count
        scale = target_t / torch.clamp(current, min=1e-12)
        out = torch.clamp(out * scale[None, :, :], min=0.0, max=1.0) * mask
    return out


def _delivered_mean(visual, resolved_mask):
    torch = _torch()
    count = torch.clamp(resolved_mask.sum().to(torch.float32), min=1.0)
    return (visual * resolved_mask[:, None, None]).sum(dim=0) / count


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

    physical_size = float(2.0 * radius * np.tan(np.deg2rad(15.0)))
    t0 = time.perf_counter()

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
            learned = _normalize_to_target(learned_raw, resolved, float(budget))
            delivered = _delivered_mean(learned, resolved)

            uniform_raw = v1._render_uniform_tv(
                receptor_x=receptor_x,
                receptor_y=receptor_y,
                x=x[1],
                y=y[1],
                heading=heading[1],
                physical_size=physical_size,
                target_fov_rad=arena.target_fov_rad,
            )
            uniform_tv = _normalize_to_target(uniform_raw, resolved, delivered)

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
            spatial_shuffle = _normalize_to_target(shuffled_raw, resolved, delivered).index_select(0, permutation)
            blank = torch.zeros_like(learned)

            uniform_delivered = _delivered_mean(uniform_tv, resolved)
            shuffled_delivered = _delivered_mean(spatial_shuffle, resolved)
            mismatch = torch.maximum(
                torch.abs(uniform_delivered - delivered),
                torch.abs(shuffled_delivered - delivered),
            )
            max_energy_mismatch = max(max_energy_mismatch, float(mismatch.max().detach().cpu()))

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
                    "event": "efficiency_telemetry_v2",
                    "budget_ceiling": float(budget),
                    "step": step + 1,
                    "steps": steps,
                    "winner": winner,
                    "advantage": float(advantage[winner]),
                    "condition_reward": {
                        CONDITIONS[i]: float(cumulative_cpu[i, winner]) for i in range(conditions)
                    },
                    "delivered_energy": float(delivered[winner].mean().detach().cpu()),
                    "max_energy_mismatch": float(max_energy_mismatch),
                    "body_latent": [round(float(v), 6) for v in latent[winner].detach().cpu().numpy()],
                    "screen": {
                        key: round(float(value[winner].detach().cpu()), 6)
                        for key, value in params.items()
                    },
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
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--interface", type=Path, required=True)
    parser.add_argument("--screen-geometry", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--flies", type=int, default=8)
    parser.add_argument("--steps", type=int, default=300)
    parser.add_argument("--population", type=int, default=7)
    parser.add_argument("--generations-per-budget", type=int, default=2)
    parser.add_argument("--budgets", default="0.12,0.06,0.03")
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
    parser.add_argument("--mutation-sigma", type=float, default=0.18)
    parser.add_argument("--telemetry-every", type=int, default=100)
    args = parser.parse_args()

    budgets = tuple(float(v.strip()) for v in args.budgets.split(",") if v.strip())
    curriculum = efficiency_curriculum(budgets, heading_offset_deg=args.heading_offset_deg)
    if args.flies < 1 or args.steps < 1 or args.population < 1 or args.generations_per_budget < 1:
        parser.error("flies/steps/population/generations-per-budget must be >= 1")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    progress_path = args.output_dir / "progress.jsonl"
    progress_path.write_text("", encoding="utf-8")
    graph = load_graph(args.graph)
    interface = load_interface(args.interface)
    geometry = load_screen_geometry(args.screen_geometry)
    if len(geometry.bodies) != len(interface.visual_indices):
        raise RuntimeError("screen geometry and visual interface receptor counts differ")
    if int(np.sum(geometry.resolved)) == 0:
        raise RuntimeError("no physically resolved visual receptors")
    sparse = scipy_csr_to_torch(graph, device=args.device)
    arena = ArenaConfig(dt=0.02)

    center_weight, _ = initial_transducer(seed=args.seed, scale=0.25)
    stage_rows = []
    lowest_budget_best = None

    for stage_index, stage in enumerate(curriculum):
        best_stage = None
        for generation in range(args.generations_per_budget):
            weights = v1._mutate_weights(
                center_weight,
                population=args.population,
                sigma=args.mutation_sigma,
                seed=args.seed + 1000 * (stage_index + 1) + generation,
            )
            result = run_stage(
                graph=graph,
                interface=interface,
                geometry=geometry,
                sparse=sparse,
                weights_np=weights,
                flies=args.flies,
                steps=args.steps,
                radius=args.radius,
                heading_offset_deg=stage.heading_offset_deg,
                budget=stage.budget,
                start_seed=args.seed,
                generator_seed=args.seed + 10000 + 100 * stage_index + generation,
                spectral_scale=args.spectral_scale,
                gain=args.gain,
                leak=args.leak,
                visual_scale=args.visual_scale,
                reward_scale=args.reward_scale,
                reward_feedback_gain=args.reward_feedback_gain,
                latent_gain=args.latent_gain,
                telemetry_every=args.telemetry_every,
                arena=arena,
                device=args.device,
                progress_path=progress_path,
                permutation_seed=args.seed + 50000 + stage_index,
            )
            winner = int(result["winner"])
            winner_weight = result["weights"][winner].copy()
            row = {
                "budget": float(stage.budget),
                "generation": generation,
                "winner": winner,
                "advantage": float(result["advantage"][winner]),
                "condition_reward": {
                    CONDITIONS[i]: float(result["cumulative_reward"][i, winner])
                    for i in range(len(CONDITIONS))
                },
                "approach": {
                    CONDITIONS[i]: float(result["approach"][i, winner])
                    for i in range(len(CONDITIONS))
                },
                "final_distance": {
                    CONDITIONS[i]: float(result["final_distance"][i, winner])
                    for i in range(len(CONDITIONS))
                },
                "final_orientation_error_rad": {
                    CONDITIONS[i]: float(result["final_orientation_error"][i, winner])
                    for i in range(len(CONDITIONS))
                },
                "peak_step": int(result["peak_step"][winner]),
                "peak_learned_reward": float(result["peak_learned_reward"][winner]),
                "max_energy_mismatch": float(result["max_energy_mismatch"]),
            }
            stage_rows.append(row)
            if best_stage is None or row["advantage"] > best_stage["row"]["advantage"]:
                best_stage = {
                    "row": row,
                    "weight": winner_weight,
                    "peak_visual": result["peak_visual"][winner].copy(),
                }
            center_weight = winner_weight
            print(json.dumps({"event": "efficiency_generation_complete_v2", **row}, sort_keys=True), flush=True)

        assert best_stage is not None
        # The next lower-energy stage starts from the best candidate seen at this
        # budget, not merely the winner of the last generation.
        center_weight = best_stage["weight"].copy()
        lowest_budget_best = best_stage
        (args.output_dir / f"winner-retina-budget-{stage.budget:.3f}.txt").write_text(
            sensor_grid_ascii(best_stage["peak_visual"], geometry, width=64) + "\n",
            encoding="utf-8",
        )

    assert lowest_budget_best is not None
    np.savez_compressed(
        args.output_dir / "best-efficiency-transducer.npz",
        weight=lowest_budget_best["weight"],
        peak_visual=lowest_budget_best["peak_visual"],
    )
    (args.output_dir / "winner-retina.txt").write_text(
        sensor_grid_ascii(lowest_budget_best["peak_visual"], geometry, width=64) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "winner-top-receptors.json").write_text(
        json.dumps(top_receptors(lowest_budget_best["peak_visual"], geometry, k=32), indent=2) + "\n",
        encoding="utf-8",
    )

    summary = {
        "experiment": "malecns-visual-efficiency-curriculum-v2",
        "scientific_status": "engineering calibration; exact delivered-energy matching",
        "question": "Can a reward-coupled MaleCNS screen generator beat controls receiving the same delivered visual energy as energy is reduced?",
        "conditions": list(CONDITIONS),
        "energy_policy": {
            "ceiling_metric": "mean intensity over optic-column-resolved receptors",
            "control_matching": "uniform-TV and spatial-shuffle match the learned arm's actually delivered per-frame energy after clipping",
            "unresolved_receptors": "present in MaleCNS state but receive zero screen drive",
        },
        "generator": {
            "substrate": "full frozen MaleCNS",
            "transducer_bias": "frozen at zero",
            "trained_boundary": "6x6 body-latent-to-screen weight matrix only",
            "latent_gain": args.latent_gain,
            "reward_feedback": "learned receiver descending excitation only",
        },
        "receiver": {
            "visual_receptors_total": int(len(geometry.bodies)),
            "optic_column_resolved": int(np.sum(geometry.resolved)),
            "optic_column_unresolved": int(np.sum(~geometry.resolved)),
            "heading_offset_deg": args.heading_offset_deg,
        },
        "parameters": {
            "flies": args.flies,
            "steps": args.steps,
            "population": args.population,
            "generations_per_budget": args.generations_per_budget,
            "budgets": list(budgets),
            "radius": args.radius,
            "seed": args.seed,
            "visual_scale": args.visual_scale,
            "reward_scale": args.reward_scale,
            "reward_feedback_gain": args.reward_feedback_gain,
            "mutation_sigma": args.mutation_sigma,
        },
        "selection": "integrated learned excitation minus strongest matched control",
        "stages": stage_rows,
        "lowest_budget_best": lowest_budget_best["row"],
    }
    (args.output_dir / "visual-efficiency-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary["lowest_budget_best"], indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
