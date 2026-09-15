from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np

import run_visual_efficiency_curriculum as v1
from full_screen_decoder import (
    FullScreenPlasticDecoder,
    build_hash_projection,
    frame_ascii,
    normalize_frame_mean,
    project_generator_state,
    project_screen_to_receptors,
)
from gpu_batch import scipy_csr_to_torch
from screen_reward_loop import load_screen_geometry
from visual_attractor import ArenaConfig, load_graph, load_interface
from visual_efficiency import matched_offset_starts


CONDITIONS = ("learned", "uniform_tv", "spatial_shuffle", "temporal_delay", "blank")


def _torch():
    import torch

    return torch


def _load_decoder(path: Path | None, *, features: int, width: int, height: int, seed: int, device: str, **kwargs):
    if path is None:
        return FullScreenPlasticDecoder.fresh(
            features=features,
            width=width,
            height=height,
            seed=seed,
            device=device,
            **kwargs,
        ), "fresh"
    archive = np.load(path, allow_pickle=False)
    weight = np.asarray(archive["weight"], dtype=np.float32)
    baseline = float(np.asarray(archive.get("baseline", 0.0)).reshape(-1)[0])
    if weight.shape != (features, width * height):
        raise RuntimeError(f"checkpoint weight shape {weight.shape} != {(features, width * height)}")
    return FullScreenPlasticDecoder.from_weight(
        weight,
        width=width,
        height=height,
        device=device,
        baseline=baseline,
        **kwargs,
    ), "resumed"


def _save_pgm(path: Path, frame) -> None:
    arr = frame.detach().cpu().numpy() if hasattr(frame, "detach") else np.asarray(frame)
    pixels = np.rint(np.clip(arr, 0.0, 1.0) * 255.0).astype(np.uint8)
    path.write_bytes(f"P5\n{pixels.shape[1]} {pixels.shape[0]}\n255\n".encode("ascii") + pixels.tobytes())


def _scenario(name: str, *, radius: float, ambient: float, screen_width: float) -> dict:
    return {
        "name": name,
        "radius": float(radius),
        "ambient": float(ambient),
        "screen_width": float(screen_width),
    }


def run_scenario(
    *,
    graph,
    interface,
    geometry,
    sparse,
    decoder: FullScreenPlasticDecoder,
    feature_bins,
    feature_signs,
    feature_counts,
    scenario: dict,
    flies: int,
    steps: int,
    screen_budget: float,
    heading_offset_deg: float,
    seed: int,
    spectral_scale: float,
    gain: float,
    leak: float,
    visual_scale: float,
    reward_scale: float,
    reward_feedback_gain: float,
    projection_gain: float,
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

    start_x, start_y, start_h = matched_offset_starts(
        flies=flies,
        radius=float(scenario["radius"]),
        seed=seed,
        heading_offset_deg=heading_offset_deg,
    )
    x = torch.from_numpy(np.repeat(start_x[None, :], conditions, axis=0)).to(device=device, dtype=torch.float64)
    y = torch.from_numpy(np.repeat(start_y[None, :], conditions, axis=0)).to(device=device, dtype=torch.float64)
    heading = torch.from_numpy(np.repeat(start_h[None, :], conditions, axis=0)).to(device=device, dtype=torch.float64)
    initial_distance = torch.hypot(x, y)
    min_distance = initial_distance.clone()

    generator_state = torch.zeros((neurons, 1), dtype=torch.float32, device=device)
    receiver_state = torch.zeros((neurons, conditions * flies), dtype=torch.float32, device=device)
    rng = np.random.default_rng(seed + 10_000)
    seed_state = rng.normal(0.0, 0.02, size=(desc_all.numel(), 1)).astype(np.float32)
    generator_state.index_copy_(0, desc_all, torch.from_numpy(seed_state).to(device))
    reward_projection_np = rng.normal(0.0, 1.0, size=desc_all.numel()).astype(np.float32)
    reward_projection_np /= max(float(np.linalg.norm(reward_projection_np)), 1e-12)
    reward_projection = torch.from_numpy(reward_projection_np).to(device)
    previous_reward = torch.zeros(1, dtype=torch.float32, device=device)

    pixel_perm = torch.from_numpy(rng.permutation(decoder.pixels).astype(np.int64)).to(device)
    previous_frame = torch.full(
        (decoder.height, decoder.width),
        float(screen_budget),
        device=device,
        dtype=torch.float32,
    )
    cumulative = torch.zeros(conditions, dtype=torch.float32, device=device)
    retinal_energy_sum = torch.zeros(conditions, dtype=torch.float64, device=device)
    best_reward = -float("inf")
    best_frame = previous_frame.clone()
    best_step = 0
    reward_signal_sum = 0.0
    t0 = time.perf_counter()

    with torch.no_grad():
        for step in range(steps):
            recurrent_g = torch.sparse.mm(sparse, generator_state) / float(spectral_scale)
            pre_g = float(gain) * recurrent_g
            reward_drive = float(reward_scale) * reward_projection[:, None] * previous_reward[None, :]
            pre_g.index_add_(0, desc_all, reward_drive)
            generator_state = (1.0 - float(leak)) * generator_state + float(leak) * torch.tanh(pre_g)

            features = project_generator_state(
                generator_state[:, 0],
                feature_bins,
                feature_signs,
                feature_counts,
                gain=projection_gain,
            )
            noise = torch.randn(decoder.pixels, device=device, dtype=torch.float32)
            raw_frame = decoder.propose(features, noise)
            learned_frame = normalize_frame_mean(raw_frame, float(screen_budget))
            uniform_frame = torch.full_like(learned_frame, float(screen_budget))
            shuffled_frame = learned_frame.reshape(-1).index_select(0, pixel_perm).reshape_as(learned_frame)
            temporal_frame = previous_frame
            blank_frame = torch.zeros_like(learned_frame)
            frames = (learned_frame, uniform_frame, shuffled_frame, temporal_frame, blank_frame)

            visuals = []
            for ci, frame in enumerate(frames):
                visual = project_screen_to_receptors(
                    frame,
                    receptor_x=receptor_x,
                    receptor_y=receptor_y,
                    resolved_mask=resolved,
                    x=x[ci],
                    y=y[ci],
                    heading=heading[ci],
                    physical_width=float(scenario["screen_width"]),
                    target_fov_rad=arena.target_fov_rad,
                    ambient=float(scenario["ambient"]),
                )
                visuals.append(visual)
                retinal_energy_sum[ci] += visual.mean().to(torch.float64)

            external = torch.cat(visuals, dim=1)
            recurrent_r = torch.sparse.mm(sparse, receiver_state) / float(spectral_scale)
            pre_r = float(gain) * recurrent_r
            pre_r.index_add_(0, visual_idx, float(visual_scale) * external)
            receiver_state = (1.0 - float(leak)) * receiver_state + float(leak) * torch.tanh(pre_r)

            desc_exc_flat = receiver_state.index_select(0, desc_all).abs().mean(dim=0)
            desc_exc = desc_exc_flat.reshape(conditions, flies).mean(dim=1)
            cumulative += desc_exc * float(arena.dt)
            previous_reward = torch.tanh(float(reward_feedback_gain) * desc_exc[0:1])

            reward_delta = float((desc_exc[0] - desc_exc[1]).detach().cpu())
            reward_signal = float(np.tanh(float(plastic_reward_gain) * reward_delta))
            learning_stats = decoder.update(features, noise, reward_signal)
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
                heading + turn.to(torch.float64) * float(arena.turn_rate_rad_s * arena.dt) + torch.pi,
                2 * torch.pi,
            ) - torch.pi
            x = x + forward.to(torch.float64) * torch.cos(heading) * float(arena.dt)
            y = y + forward.to(torch.float64) * torch.sin(heading) * float(arena.dt)
            min_distance = torch.minimum(min_distance, torch.hypot(x, y))

            if reward_delta > best_reward:
                best_reward = reward_delta
                best_frame = learned_frame.clone()
                best_step = step
            previous_frame = learned_frame.clone()

            if telemetry_every > 0 and ((step + 1) % telemetry_every == 0 or step == steps - 1):
                payload = {
                    "event": "full_screen_learning_telemetry",
                    "scenario": scenario["name"],
                    "step": step + 1,
                    "steps": steps,
                    "screen_mean_luminance": float(learned_frame.mean().detach().cpu()),
                    "ambient": float(scenario["ambient"]),
                    "radius": float(scenario["radius"]),
                    "screen_width": float(scenario["screen_width"]),
                    "reward_signal": reward_signal,
                    "reward_signal_mean": reward_signal_sum / float(step + 1),
                    "condition_reward": {
                        CONDITIONS[i]: float(cumulative[i].detach().cpu()) for i in range(conditions)
                    },
                    "retinal_energy_mean": {
                        CONDITIONS[i]: float((retinal_energy_sum[i] / float(step + 1)).detach().cpu())
                        for i in range(conditions)
                    },
                    "feature_rms": float(torch.sqrt(torch.mean(features * features)).detach().cpu()),
                    "weight_norm": learning_stats["weight_norm"],
                    "eligibility_norm": learning_stats["eligibility_norm"],
                    "reward_baseline": learning_stats["baseline"],
                    "best_reward_delta": float(best_reward),
                    "best_step": int(best_step),
                    "elapsed_s": round(time.perf_counter() - t0, 3),
                }
                line = json.dumps(payload, sort_keys=True)
                print(line, flush=True)
                with progress_path.open("a", encoding="utf-8") as stream:
                    stream.write(line + "\n")

    reduction = (initial_distance - min_distance) / torch.clamp(initial_distance, min=1e-12)
    approach = (reduction >= 0.5).to(torch.float32).mean(dim=1).detach().cpu().numpy()
    cumulative_np = cumulative.detach().cpu().numpy()
    return {
        "scenario": dict(scenario),
        "condition_reward": {CONDITIONS[i]: float(cumulative_np[i]) for i in range(conditions)},
        "advantage_vs_uniform": float(cumulative_np[0] - cumulative_np[1]),
        "advantage_vs_strongest_nonblank_control": float(cumulative_np[0] - np.max(cumulative_np[1:4])),
        "approach": {CONDITIONS[i]: float(approach[i]) for i in range(conditions)},
        "retinal_energy_mean": {
            CONDITIONS[i]: float((retinal_energy_sum[i] / float(max(steps, 1))).detach().cpu())
            for i in range(conditions)
        },
        "mean_reward_signal": float(reward_signal_sum / float(max(steps, 1))),
        "best_reward_delta": float(best_reward),
        "best_step": int(best_step),
        "best_frame": best_frame,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--interface", type=Path, required=True)
    parser.add_argument("--screen-geometry", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--initial-decoder", type=Path)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--flies", type=int, default=8)
    parser.add_argument("--steps", type=int, default=350)
    parser.add_argument("--screen-width-px", type=int, default=64)
    parser.add_argument("--screen-height-px", type=int, default=36)
    parser.add_argument("--feature-dim", type=int, default=256)
    parser.add_argument("--screen-budget", type=float, default=0.15)
    parser.add_argument("--heading-offset-deg", type=float, default=30.0)
    parser.add_argument("--seed", type=int, default=20260915)
    parser.add_argument("--spectral-scale", type=float, default=3776.27)
    parser.add_argument("--gain", type=float, default=1.0)
    parser.add_argument("--leak", type=float, default=0.2)
    parser.add_argument("--visual-scale", type=float, default=0.5)
    parser.add_argument("--reward-scale", type=float, default=0.08)
    parser.add_argument("--reward-feedback-gain", type=float, default=1000.0)
    parser.add_argument("--projection-gain", type=float, default=200.0)
    parser.add_argument("--plastic-reward-gain", type=float, default=1e8)
    parser.add_argument("--learning-rate", type=float, default=0.001)
    parser.add_argument("--exploration-sigma", type=float, default=0.05)
    parser.add_argument("--eligibility-decay", type=float, default=0.95)
    parser.add_argument("--baseline-rate", type=float, default=0.02)
    parser.add_argument("--telemetry-every", type=int, default=100)
    args = parser.parse_args()

    if args.screen_width_px < 2 or args.screen_height_px < 2 or args.feature_dim < 1:
        parser.error("screen dimensions must be >=2 and feature-dim >=1")
    if not 0.0 < args.screen_budget <= 1.0:
        parser.error("screen-budget must be in (0,1]")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    progress_path = args.output_dir / "full-screen-progress.jsonl"
    progress_path.write_text("", encoding="utf-8")

    graph = load_graph(args.graph)
    interface = load_interface(args.interface)
    geometry = load_screen_geometry(args.screen_geometry)
    sparse = scipy_csr_to_torch(graph, device=args.device)
    arena = ArenaConfig(dt=0.02)

    decoder, learning_mode = _load_decoder(
        args.initial_decoder,
        features=args.feature_dim,
        width=args.screen_width_px,
        height=args.screen_height_px,
        seed=args.seed,
        device=args.device,
        learning_rate=args.learning_rate,
        exploration_sigma=args.exploration_sigma,
        eligibility_decay=args.eligibility_decay,
        baseline_rate=args.baseline_rate,
    )
    feature_bins, feature_signs, feature_counts = build_hash_projection(
        graph.shape[0],
        args.feature_dim,
        seed=args.seed + 77,
        device=args.device,
    )

    scenarios = [
        _scenario("dark_near_large", radius=0.55, ambient=0.0, screen_width=0.42),
        _scenario("dark_far_large", radius=0.90, ambient=0.0, screen_width=0.42),
        _scenario("lit_near_large", radius=0.55, ambient=0.12, screen_width=0.42),
        _scenario("lit_far_medium", radius=0.90, ambient=0.12, screen_width=0.30),
    ]

    rows = []
    global_best = None
    for i, scenario in enumerate(scenarios):
        row = run_scenario(
            graph=graph,
            interface=interface,
            geometry=geometry,
            sparse=sparse,
            decoder=decoder,
            feature_bins=feature_bins,
            feature_signs=feature_signs,
            feature_counts=feature_counts,
            scenario=scenario,
            flies=args.flies,
            steps=args.steps,
            screen_budget=args.screen_budget,
            heading_offset_deg=args.heading_offset_deg,
            seed=args.seed + 1000 * i,
            spectral_scale=args.spectral_scale,
            gain=args.gain,
            leak=args.leak,
            visual_scale=args.visual_scale,
            reward_scale=args.reward_scale,
            reward_feedback_gain=args.reward_feedback_gain,
            projection_gain=args.projection_gain,
            plastic_reward_gain=args.plastic_reward_gain,
            telemetry_every=args.telemetry_every,
            arena=arena,
            device=args.device,
            progress_path=progress_path,
        )
        best_frame = row.pop("best_frame")
        rows.append(row)
        if global_best is None or row["advantage_vs_uniform"] > global_best["row"]["advantage_vs_uniform"]:
            global_best = {"row": row, "frame": best_frame.clone()}
        print(json.dumps({"event": "full_screen_scenario_complete", **row}, sort_keys=True), flush=True)

    assert global_best is not None
    np.savez_compressed(
        args.output_dir / "full-screen-decoder.npz",
        weight=decoder.weight.detach().cpu().numpy().astype(np.float32),
        baseline=np.asarray([decoder.baseline], dtype=np.float32),
        feature_dim=np.asarray([args.feature_dim], dtype=np.int32),
        width=np.asarray([args.screen_width_px], dtype=np.int32),
        height=np.asarray([args.screen_height_px], dtype=np.int32),
        projection_seed=np.asarray([args.seed + 77], dtype=np.int64),
    )
    np.save(args.output_dir / "best-full-screen-frame.npy", global_best["frame"].detach().cpu().numpy().astype(np.float32))
    _save_pgm(args.output_dir / "best-full-screen-frame.pgm", global_best["frame"])
    (args.output_dir / "best-full-screen-frame.txt").write_text(frame_ascii(global_best["frame"]) + "\n", encoding="utf-8")

    summary = {
        "experiment": "malecns-physical-full-screen-attractor-v1",
        "scientific_status": "engineering/scientific calibration; unrestricted physical screen canvas with online reward plasticity",
        "learning_state": {
            "mode": learning_mode,
            "persisted_object": "256-to-2304 full-screen plastic decoder" if args.feature_dim == 256 and args.screen_width_px * args.screen_height_px == 2304 else "full-screen plastic decoder",
        },
        "generator": {
            "connectome_neurons": int(graph.shape[0]),
            "feature_dim": int(args.feature_dim),
            "projection": "fixed deterministic signed hash pooling; every generator neuron contributes",
            "connectome_frozen": True,
        },
        "display": {
            "width_px": int(args.screen_width_px),
            "height_px": int(args.screen_height_px),
            "grayscale": True,
            "screen_mean_luminance_fraction": float(args.screen_budget),
            "constraint": "frame content unrestricted; only physical screen luminance/aperture/geometry constrain output",
        },
        "physics": {
            "retinal_sampling": "bilinear physical-screen projection into optic-column-resolved receptors",
            "resolved_receptors": int(np.sum(geometry.resolved)),
            "total_visual_receptors": int(len(geometry.bodies)),
            "unresolved_receptors_stimulated_by_screen": False,
            "scenarios": scenarios,
        },
        "learning_rule": {
            "type": "online reward-modulated node perturbation with eligibility trace",
            "reward": "tanh(gain * (receiver descending excitation learned - uniform-TV))",
            "learning_rate": float(args.learning_rate),
            "exploration_sigma": float(args.exploration_sigma),
            "eligibility_decay": float(args.eligibility_decay),
            "baseline_rate": float(args.baseline_rate),
        },
        "parameters": {
            "flies": int(args.flies),
            "steps_per_scenario": int(args.steps),
            "heading_offset_deg": float(args.heading_offset_deg),
            "seed": int(args.seed),
            "projection_gain": float(args.projection_gain),
        },
        "conditions": list(CONDITIONS),
        "scenarios": rows,
        "best_training_scenario": global_best["row"],
        "final_decoder_weight_norm": float(_torch().linalg.vector_norm(decoder.weight).detach().cpu()),
    }
    (args.output_dir / "full-screen-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "event": "physical_full_screen_attractor_complete",
        "learning_mode": learning_mode,
        "best_advantage_vs_uniform": global_best["row"]["advantage_vs_uniform"],
        "screen": f"{args.screen_width_px}x{args.screen_height_px}",
        "feature_dim": args.feature_dim,
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
