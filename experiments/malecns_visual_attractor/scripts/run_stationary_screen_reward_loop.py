from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from gpu_batch import scipy_csr_to_torch
from screen_reward_loop import (
    LATENT_DIM,
    SCREEN_DIM,
    initial_transducer,
    load_screen_geometry,
    make_transducer_population,
    matched_direct_gaze_starts,
    select_winner,
    sensor_grid_ascii,
    top_receptors,
)
from visual_attractor import ArenaConfig, load_graph, load_interface


def _torch():
    import torch

    return torch


def _mean_rows(state, indices):
    torch = _torch()
    if indices.numel() == 0:
        return torch.zeros(state.shape[1], dtype=state.dtype, device=state.device)
    return state.index_select(0, indices).mean(dim=0)


def _body_latent(state, *, steer_l, steer_r, forward_l, forward_r, desc_l, desc_r):
    torch = _torch()
    values = torch.stack(
        [
            _mean_rows(state, steer_l),
            _mean_rows(state, steer_r),
            _mean_rows(state, forward_l),
            _mean_rows(state, forward_r),
            _mean_rows(state, desc_l),
            _mean_rows(state, desc_r),
        ],
        dim=1,
    )
    return torch.tanh(4.0 * values)


def _screen_params(latent, weight, bias):
    torch = _torch()
    raw = torch.einsum("cl,cls->cs", latent, weight) + bias
    bounded = torch.tanh(raw)
    return {
        "x_offset": 0.30 * bounded[:, 0],
        "y_offset": 0.35 * bounded[:, 1],
        "size_scale": torch.exp(0.55 * bounded[:, 2]),
        "orientation": torch.pi * bounded[:, 3],
        "contrast": 0.5 + 0.5 * bounded[:, 4],
        "wing_spread": 0.06 + 0.18 * (0.5 + 0.5 * bounded[:, 5]),
    }


def _render_body_pattern(
    *,
    receptor_x,
    receptor_y,
    x,
    y,
    heading,
    physical_size,
    params,
    target_fov_rad,
):
    """Render a stationary screen whose content is a three-lobe body glyph.

    The screen itself stays at the world origin. Receiver motion changes the
    screen bearing and apparent size. Generator body latents move/deform only
    the pattern *inside* the stationary screen.
    """
    torch = _torch()
    candidates, flies = x.shape
    bearing = torch.remainder(torch.atan2(-y, -x) - heading + torch.pi, 2 * torch.pi) - torch.pi
    distance = torch.clamp(torch.hypot(x, y), min=1e-9)
    angular_size = 2.0 * torch.atan2(
        physical_size * params["size_scale"][:, None] / 2.0,
        distance,
    )
    center_x = torch.clamp(
        bearing / float(target_fov_rad) + params["x_offset"][:, None],
        -1.0,
        1.0,
    )
    center_y = params["y_offset"][:, None].expand(candidates, flies)
    sigma_x = torch.clamp(
        angular_size / float(target_fov_rad) / 2.355,
        min=0.020,
    )
    sigma_y = torch.clamp(0.65 * sigma_x, min=0.018)

    theta = params["orientation"][:, None]
    spread = params["wing_spread"][:, None]
    dx = spread * torch.cos(theta)
    dy = spread * torch.sin(theta)

    rx = receptor_x[:, None, None]
    ry = receptor_y[:, None, None]
    cx = center_x[None, :, :]
    cy = center_y[None, :, :]
    sx = sigma_x[None, :, :]
    sy = sigma_y[None, :, :]

    def gaussian(px, py):
        return torch.exp(-0.5 * (((rx - px) / sx) ** 2 + ((ry - py) / sy) ** 2))

    body = gaussian(cx, cy)
    wing_a = gaussian(cx + dx[None, :, :], cy + dy[None, :, :])
    wing_b = gaussian(cx - dx[None, :, :], cy - dy[None, :, :])
    visual = torch.clamp(body + 0.55 * wing_a + 0.55 * wing_b, 0.0, 1.0)
    visual *= params["contrast"][None, :, None]
    # Geometry is intentionally float64, but the neural boundary is float32.
    # Cast the rendered retina exactly once at that boundary so sparse recurrent
    # state and visual injection always share a dtype on CPU and CUDA.
    visual = visual.to(dtype=receptor_x.dtype)
    return visual, distance, bearing


def run_generation(
    *,
    graph,
    interface,
    geometry,
    sparse,
    weight_np,
    bias_np,
    flies,
    steps,
    radius,
    start_seed,
    spectral_scale,
    gain,
    leak,
    visual_scale,
    reward_scale,
    reward_feedback_gain,
    generator_seed,
    telemetry_every,
    arena,
    device,
    progress_path,
):
    torch = _torch()
    candidates = weight_np.shape[0]
    batch = candidates * flies
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
    weight = torch.from_numpy(weight_np).to(device=device, dtype=torch.float32)
    bias = torch.from_numpy(bias_np).to(device=device, dtype=torch.float32)

    start_x, start_y, start_h = matched_direct_gaze_starts(
        flies=flies, radius=radius, seed=start_seed
    )
    x = torch.from_numpy(np.repeat(start_x[None, :], candidates, axis=0)).to(device=device, dtype=torch.float64)
    y = torch.from_numpy(np.repeat(start_y[None, :], candidates, axis=0)).to(device=device, dtype=torch.float64)
    heading = torch.from_numpy(np.repeat(start_h[None, :], candidates, axis=0)).to(device=device, dtype=torch.float64)
    initial_distance = torch.hypot(x, y)
    min_distance = initial_distance.clone()

    generator_state = torch.zeros((neurons, candidates), dtype=torch.float32, device=device)
    receiver_state = torch.zeros((neurons, batch), dtype=torch.float32, device=device)

    rng = np.random.default_rng(generator_seed)
    seed_state = rng.normal(0.0, 0.02, size=(desc_all.numel(), candidates)).astype(np.float32)
    generator_state.index_copy_(0, desc_all, torch.from_numpy(seed_state).to(device))
    reward_projection_np = rng.normal(0.0, 1.0, size=desc_all.numel()).astype(np.float32)
    reward_projection_np /= max(float(np.linalg.norm(reward_projection_np)), 1e-12)
    reward_projection = torch.from_numpy(reward_projection_np).to(device)

    cumulative = torch.zeros(candidates, dtype=torch.float32, device=device)
    previous_reward = torch.zeros(candidates, dtype=torch.float32, device=device)
    peak_reward = np.full(candidates, -np.inf, dtype=np.float64)
    peak_visual = np.zeros((candidates, len(geometry.bodies)), dtype=np.float32)
    peak_step = np.zeros(candidates, dtype=np.int32)

    physical_size = float(2.0 * radius * np.tan(np.deg2rad(15.0)))
    t0 = time.perf_counter()

    with torch.no_grad():
        for step in range(steps):
            recurrent_g = torch.sparse.mm(sparse, generator_state) / float(spectral_scale)
            pre_g = float(gain) * recurrent_g
            reward_drive = (
                float(reward_scale)
                * reward_projection[:, None]
                * previous_reward[None, :]
            )
            pre_g.index_add_(0, desc_all, reward_drive)
            generator_state = (1.0 - float(leak)) * generator_state + float(leak) * torch.tanh(pre_g)

            latent = _body_latent(
                generator_state,
                steer_l=steer_l,
                steer_r=steer_r,
                forward_l=forward_l,
                forward_r=forward_r,
                desc_l=desc_l,
                desc_r=desc_r,
            )
            params = _screen_params(latent, weight, bias)
            visual, distance_before, bearing = _render_body_pattern(
                receptor_x=receptor_x,
                receptor_y=receptor_y,
                x=x,
                y=y,
                heading=heading,
                physical_size=physical_size,
                params=params,
                target_fov_rad=arena.target_fov_rad,
            )

            visual_flat = visual.reshape(len(geometry.bodies), batch)
            recurrent_r = torch.sparse.mm(sparse, receiver_state) / float(spectral_scale)
            pre_r = float(gain) * recurrent_r
            pre_r.index_add_(0, visual_idx, float(visual_scale) * visual_flat)
            receiver_state = (1.0 - float(leak)) * receiver_state + float(leak) * torch.tanh(pre_r)

            desc_exc = receiver_state.index_select(0, desc_all).abs().mean(dim=0)
            desc_exc = desc_exc.reshape(candidates, flies).mean(dim=1)
            previous_reward = torch.tanh(float(reward_feedback_gain) * desc_exc)
            cumulative += desc_exc * float(arena.dt)

            left = _mean_rows(receiver_state, steer_l).reshape(candidates, flies)
            right = _mean_rows(receiver_state, steer_r).reshape(candidates, flies)
            turn = torch.tanh(float(arena.motor_turn_gain) * (right - left))
            forward_state = torch.cat((forward_l, forward_r))
            forward_drive = _mean_rows(receiver_state, forward_state).reshape(candidates, flies)
            forward = torch.clamp(
                float(arena.base_speed)
                + float(arena.motor_speed_gain) * torch.tanh(4.0 * forward_drive),
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

            reward_cpu = desc_exc.detach().cpu().numpy()
            mean_visual_cpu = visual.mean(dim=2).detach().cpu().numpy().T
            for candidate in range(candidates):
                if reward_cpu[candidate] > peak_reward[candidate]:
                    peak_reward[candidate] = float(reward_cpu[candidate])
                    peak_visual[candidate] = mean_visual_cpu[candidate]
                    peak_step[candidate] = step

            if telemetry_every > 0 and ((step + 1) % telemetry_every == 0 or step == steps - 1):
                cumulative_cpu = cumulative.detach().cpu().numpy()
                winner = select_winner(cumulative_cpu)
                elapsed = time.perf_counter() - t0
                payload = {
                    "event": "retina_telemetry",
                    "step": step + 1,
                    "steps": steps,
                    "winner": winner,
                    "reward_now": float(reward_cpu[winner]),
                    "cumulative_reward": float(cumulative_cpu[winner]),
                    "peak_reward": float(peak_reward[winner]),
                    "peak_step": int(peak_step[winner]),
                    "elapsed_s": round(elapsed, 3),
                    "body_latent": [round(float(v), 6) for v in latent[winner].detach().cpu().numpy()],
                    "screen": {
                        key: round(float(value[winner].detach().cpu()), 6)
                        for key, value in params.items()
                    },
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
    reduction = (initial_distance - min_distance) / torch.clamp(initial_distance, min=1e-12)
    approach = (reduction >= 0.5).to(torch.float32).mean(dim=1).detach().cpu().numpy()
    final_distance = torch.hypot(x, y).mean(dim=1).detach().cpu().numpy()
    winner = select_winner(cumulative_cpu)
    return {
        "winner": winner,
        "cumulative_reward": cumulative_cpu,
        "approach": approach,
        "final_distance": final_distance,
        "peak_reward": peak_reward,
        "peak_step": peak_step,
        "peak_visual": peak_visual,
        "weight": weight_np,
        "bias": bias_np,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--interface", type=Path, required=True)
    parser.add_argument("--screen-geometry", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--flies", type=int, default=8)
    parser.add_argument("--steps", type=int, default=400)
    parser.add_argument("--population", type=int, default=9)
    parser.add_argument("--generations", type=int, default=3)
    parser.add_argument("--radius", type=float, default=0.75)
    parser.add_argument("--seed", type=int, default=20260914)
    parser.add_argument("--spectral-scale", type=float, default=3776.27)
    parser.add_argument("--gain", type=float, default=1.0)
    parser.add_argument("--leak", type=float, default=0.2)
    parser.add_argument("--visual-scale", type=float, default=0.5)
    parser.add_argument("--reward-scale", type=float, default=0.08)
    parser.add_argument("--reward-feedback-gain", type=float, default=1000.0)
    parser.add_argument("--mutation-sigma", type=float, default=0.18)
    parser.add_argument("--telemetry-every", type=int, default=100)
    args = parser.parse_args()

    if args.flies < 1 or args.steps < 1 or args.population < 1 or args.generations < 1:
        parser.error("flies/steps/population/generations must be >= 1")

    torch = _torch()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    progress_path = args.output_dir / "progress.jsonl"
    progress_path.write_text("", encoding="utf-8")

    graph = load_graph(args.graph)
    interface = load_interface(args.interface)
    geometry = load_screen_geometry(args.screen_geometry)
    if len(geometry.bodies) != len(interface.visual_indices):
        raise RuntimeError("screen geometry and visual interface receptor counts differ")
    sparse = scipy_csr_to_torch(graph, device=args.device)
    arena = ArenaConfig(dt=0.02)

    center_weight, center_bias = initial_transducer(seed=args.seed)
    generations = []
    best_ever = None
    best_ever_score = -np.inf

    for generation in range(args.generations):
        weight, bias = make_transducer_population(
            center_weight,
            center_bias,
            population=args.population,
            sigma=args.mutation_sigma,
            seed=args.seed + 1000 + generation,
        )
        result = run_generation(
            graph=graph,
            interface=interface,
            geometry=geometry,
            sparse=sparse,
            weight_np=weight,
            bias_np=bias,
            flies=args.flies,
            steps=args.steps,
            radius=args.radius,
            start_seed=args.seed,
            spectral_scale=args.spectral_scale,
            gain=args.gain,
            leak=args.leak,
            visual_scale=args.visual_scale,
            reward_scale=args.reward_scale,
            reward_feedback_gain=args.reward_feedback_gain,
            generator_seed=args.seed + 2000 + generation,
            telemetry_every=args.telemetry_every,
            arena=arena,
            device=args.device,
            progress_path=progress_path,
        )
        winner = int(result["winner"])
        score = float(result["cumulative_reward"][winner])
        center_weight = result["weight"][winner].copy()
        center_bias = result["bias"][winner].copy()
        if score > best_ever_score:
            best_ever_score = score
            best_ever = {
                "generation": generation,
                "candidate": winner,
                "weight": center_weight.copy(),
                "bias": center_bias.copy(),
                "peak_visual": result["peak_visual"][winner].copy(),
                "peak_reward": float(result["peak_reward"][winner]),
                "peak_step": int(result["peak_step"][winner]),
                "approach": float(result["approach"][winner]),
                "final_distance": float(result["final_distance"][winner]),
            }
        row = {
            "generation": generation,
            "winner": winner,
            "winner_score": score,
            "scores": [float(v) for v in result["cumulative_reward"]],
            "approach": [float(v) for v in result["approach"]],
            "final_distance": [float(v) for v in result["final_distance"]],
        }
        generations.append(row)
        print(json.dumps({"event": "generation_complete", **row}, sort_keys=True), flush=True)

    assert best_ever is not None
    np.savez_compressed(
        args.output_dir / "best-screen-transducer.npz",
        weight=best_ever["weight"],
        bias=best_ever["bias"],
        peak_visual=best_ever["peak_visual"],
    )
    retina_text = sensor_grid_ascii(best_ever["peak_visual"], geometry, width=64)
    (args.output_dir / "winner-retina.txt").write_text(retina_text + "\n", encoding="utf-8")
    (args.output_dir / "winner-top-receptors.json").write_text(
        json.dumps(top_receptors(best_ever["peak_visual"], geometry, k=32), indent=2) + "\n",
        encoding="utf-8",
    )

    summary = {
        "experiment": "malecns-stationary-screen-reward-loop-calibration-v1",
        "scientific_status": "calibration; not Run 2 and not evidence of capture",
        "generator": {
            "substrate": "full frozen MaleCNS",
            "screen": "stationary world origin; body-latent three-lobe visual glyph",
            "reward_input": "synthetic reward projection into generator descending pool",
            "trained_boundary": "6x6 body-latent-to-screen transducer selected by one-plus-lambda ES",
        },
        "receiver": {
            "substrate": "full frozen MaleCNS",
            "visual_receptors": int(len(geometry.bodies)),
            "direct_gaze_initialization": True,
            "courtship_prime": False,
        },
        "reward": "mean absolute receiver descending activity; fed back one step later",
        "selection": "integral of receiver descending excitation over time",
        "parameters": {
            "flies": args.flies,
            "steps": args.steps,
            "population": args.population,
            "generations": args.generations,
            "radius": args.radius,
            "seed": args.seed,
            "spectral_scale": args.spectral_scale,
            "gain": args.gain,
            "leak": args.leak,
            "visual_scale": args.visual_scale,
            "reward_scale": args.reward_scale,
            "reward_feedback_gain": args.reward_feedback_gain,
            "mutation_sigma": args.mutation_sigma,
            "telemetry_every": args.telemetry_every,
        },
        "generations_detail": generations,
        "best": {
            "generation": int(best_ever["generation"]),
            "candidate": int(best_ever["candidate"]),
            "score": float(best_ever_score),
            "peak_reward": float(best_ever["peak_reward"]),
            "peak_step": int(best_ever["peak_step"]),
            "approach": float(best_ever["approach"]),
            "final_distance": float(best_ever["final_distance"]),
            "top_receptors": top_receptors(best_ever["peak_visual"], geometry, k=12),
        },
    }
    (args.output_dir / "screen-reward-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary["best"], indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()