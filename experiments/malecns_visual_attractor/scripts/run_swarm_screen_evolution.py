from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

import run_visual_efficiency_curriculum as v1
from compound_eye_artifacts import compound_eye_facets, panoramic_retina, write_rgb_png
from full_screen_decoder import FullScreenPlasticDecoder, build_hash_projection, normalize_frame_mean, project_generator_state
from gpu_batch import scipy_csr_to_torch
from screen_reward_loop import load_screen_geometry
from swarm_transport import apply_transport, compile_static_transport, sample_swarm_poses, to_torch
from visual_attractor import load_graph, load_interface


def _torch():
    import torch
    return torch


def _idx(values, device):
    torch = _torch()
    return torch.from_numpy(np.asarray(values, dtype=np.int64)).to(device)


def _mutated(weight, *, sigma: float, seed: int, device: str):
    torch = _torch()
    rng = np.random.default_rng(seed)
    noise = rng.normal(0.0, sigma, size=tuple(weight.shape)).astype(np.float32)
    return weight.detach().clone() + torch.from_numpy(noise).to(device=device)


def _evaluate_candidate(
    *, graph, interface, sparse, matrix, baseline, transport, decoder, feature_bins, feature_signs, feature_counts,
    active_mask, steps: int, screen_budget: float, seed: int, spectral_scale: float, gain: float, leak: float,
    visual_scale: float, reward_scale: float, reward_feedback_gain: float, projection_gain: float,
    plastic_reward_gain: float, device: str, learn: bool,
):
    torch = _torch()
    flies = transport.flies
    neurons = graph.shape[0]
    visual_idx = _idx(interface.visual_indices, device)
    desc_l = _idx(interface.descending_left, device)
    desc_r = _idx(interface.descending_right, device)
    desc_all = torch.unique(torch.cat((desc_l, desc_r)))
    active = torch.from_numpy(np.asarray(active_mask, dtype=bool)).to(device=device)
    if not bool(active.any()):
        raise RuntimeError("active swarm is empty")

    generator_state = torch.zeros((neurons, 1), dtype=torch.float32, device=device)
    receiver_state = torch.zeros((neurons, 2 * flies), dtype=torch.float32, device=device)
    rng = np.random.default_rng(seed)
    generator_state.index_copy_(
        0, desc_all,
        torch.from_numpy(rng.normal(0.0, 0.02, size=(desc_all.numel(), 1)).astype(np.float32)).to(device),
    )
    reward_projection_np = rng.normal(0.0, 1.0, size=desc_all.numel()).astype(np.float32)
    reward_projection_np /= max(float(np.linalg.norm(reward_projection_np)), 1e-12)
    reward_projection = torch.from_numpy(reward_projection_np).to(device)
    previous_reward = torch.zeros(1, dtype=torch.float32, device=device)
    fly_integral = torch.zeros(flies, dtype=torch.float64, device=device)
    cumulative_learned = 0.0
    cumulative_uniform = 0.0
    best_delta = -float("inf")
    best_frame = torch.full((decoder.height, decoder.width), float(screen_budget), dtype=torch.float32, device=device)
    reward_signal_sum = 0.0

    uniform_frame = torch.full_like(best_frame, float(screen_budget))
    uniform_retina = apply_transport(
        uniform_frame, matrix, baseline, flies=transport.flies, receptors=transport.receptors
    )

    with torch.no_grad():
        for step in range(steps):
            recurrent_g = torch.sparse.mm(sparse, generator_state) / float(spectral_scale)
            pre_g = float(gain) * recurrent_g
            reward_drive = float(reward_scale) * reward_projection[:, None] * previous_reward[None, :]
            pre_g.index_add_(0, desc_all, reward_drive)
            generator_state = (1.0 - float(leak)) * generator_state + float(leak) * torch.tanh(pre_g)

            features = project_generator_state(
                generator_state[:, 0], feature_bins, feature_signs, feature_counts, gain=projection_gain
            )
            noise = torch.randn(decoder.pixels, device=device, dtype=torch.float32)
            learned_frame = normalize_frame_mean(decoder.propose(features, noise), float(screen_budget))
            learned_retina = apply_transport(
                learned_frame, matrix, baseline, flies=transport.flies, receptors=transport.receptors
            )
            external = torch.cat((learned_retina, uniform_retina), dim=1)

            recurrent_r = torch.sparse.mm(sparse, receiver_state) / float(spectral_scale)
            pre_r = float(gain) * recurrent_r
            pre_r.index_add_(0, visual_idx, float(visual_scale) * external)
            receiver_state = (1.0 - float(leak)) * receiver_state + float(leak) * torch.tanh(pre_r)

            desc_flat = receiver_state.index_select(0, desc_all).abs().mean(dim=0)
            learned_exc = desc_flat[:flies]
            uniform_exc = desc_flat[flies:]
            fly_delta = learned_exc - uniform_exc
            active_delta = fly_delta[active].mean()
            fly_integral += fly_delta.to(torch.float64) * 0.02
            cumulative_learned += float(learned_exc[active].mean().cpu()) * 0.02
            cumulative_uniform += float(uniform_exc[active].mean().cpu()) * 0.02

            reward_signal = float(np.tanh(float(plastic_reward_gain) * float(active_delta.cpu())))
            reward_signal_sum += reward_signal
            if learn:
                decoder.update(features, noise, reward_signal)
            previous_reward = torch.tanh(float(reward_feedback_gain) * active_delta.reshape(1))

            delta_value = float(active_delta.cpu())
            if delta_value > best_delta:
                best_delta = delta_value
                best_frame = learned_frame.clone()

    fly_scores = fly_integral.detach().cpu().numpy().astype(np.float64)
    score = float(fly_scores[np.asarray(active_mask, dtype=bool)].mean())
    return {
        "score": score,
        "fly_scores": fly_scores,
        "learned_integral": cumulative_learned,
        "uniform_integral": cumulative_uniform,
        "best_instant_delta": float(best_delta),
        "mean_reward_signal": reward_signal_sum / max(steps, 1),
        "best_frame": best_frame.detach().clone(),
        "final_weight": decoder.weight.detach().clone(),
        "baseline": float(decoder.baseline),
    }


def _save_screen_png(path: Path, frame) -> None:
    arr = frame.detach().cpu().numpy() if hasattr(frame, "detach") else np.asarray(frame)
    p = np.rint(np.clip(arr, 0.0, 1.0) * 255).astype(np.uint8)
    write_rgb_png(path, np.repeat(p[:, :, None], 3, axis=2))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--graph", type=Path, required=True)
    p.add_argument("--interface", type=Path, required=True)
    p.add_argument("--screen-geometry", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--device", default="cuda")
    p.add_argument("--flies", type=int, default=24)
    p.add_argument("--population", type=int, default=5)
    p.add_argument("--elites", type=int, default=2)
    p.add_argument("--rounds", type=int, default=3)
    p.add_argument("--steps", type=int, default=160)
    p.add_argument("--final-steps", type=int, default=240)
    p.add_argument("--screen-width-px", type=int, default=64)
    p.add_argument("--screen-height-px", type=int, default=36)
    p.add_argument("--feature-dim", type=int, default=256)
    p.add_argument("--screen-budget", type=float, default=0.15)
    p.add_argument("--physical-width", type=float, default=0.42)
    p.add_argument("--ambient", type=float, default=0.08)
    p.add_argument("--seed", type=int, default=20260915)
    p.add_argument("--mutation-sigma", type=float, default=0.015)
    p.add_argument("--spectral-scale", type=float, default=3776.27)
    p.add_argument("--gain", type=float, default=1.0)
    p.add_argument("--leak", type=float, default=0.2)
    p.add_argument("--visual-scale", type=float, default=0.5)
    p.add_argument("--reward-scale", type=float, default=0.08)
    p.add_argument("--reward-feedback-gain", type=float, default=1000.0)
    p.add_argument("--projection-gain", type=float, default=20000.0)
    p.add_argument("--plastic-reward-gain", type=float, default=1e8)
    p.add_argument("--learning-rate", type=float, default=0.001)
    p.add_argument("--exploration-sigma", type=float, default=0.05)
    p.add_argument("--eligibility-decay", type=float, default=0.95)
    p.add_argument("--baseline-rate", type=float, default=0.02)
    args = p.parse_args()

    if args.population < 2 or args.elites < 1 or args.elites >= args.population:
        p.error("require population>=2 and 1<=elites<population")
    if args.flies < 4 or args.rounds < 1 or args.steps < 1:
        p.error("flies>=4, rounds>=1, steps>=1 required")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    progress = args.output_dir / "swarm-progress.jsonl"
    progress.write_text("", encoding="utf-8")
    t0 = time.perf_counter()

    graph = load_graph(args.graph)
    interface = load_interface(args.interface)
    geometry = load_screen_geometry(args.screen_geometry)
    sparse = scipy_csr_to_torch(graph, device=args.device)
    poses = sample_swarm_poses(flies=args.flies, seed=args.seed)
    transport = compile_static_transport(
        receptor_x=geometry.x,
        receptor_y=geometry.y,
        resolved=geometry.resolved,
        poses=poses,
        width=args.screen_width_px,
        height=args.screen_height_px,
        physical_width=args.physical_width,
        ambient=args.ambient,
    )
    if np.any(transport.visible_mass <= 0):
        raise RuntimeError(f"some swarm members cannot see the TV: {transport.visible_mass.tolist()}")
    transport.save(args.output_dir / "retinal-transport.npz")
    matrix, baseline = to_torch(transport, device=args.device)

    feature_bins, feature_signs, feature_counts = build_hash_projection(
        graph.shape[0], args.feature_dim, seed=args.seed + 101, device=args.device
    )
    base_decoder = FullScreenPlasticDecoder.fresh(
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
    parents = [base_decoder.weight.detach().clone()]
    active = np.ones(args.flies, dtype=bool)
    round_rows = []
    winner_result = None
    winner_weight = parents[0]

    for rnd in range(args.rounds):
        candidates = []
        for ci in range(args.population):
            parent = parents[ci % len(parents)]
            weight = parent if (ci == 0 and rnd > 0) else _mutated(
                parent, sigma=args.mutation_sigma, seed=args.seed + rnd * 1000 + ci, device=args.device
            )
            decoder = FullScreenPlasticDecoder.from_weight(
                weight,
                width=args.screen_width_px,
                height=args.screen_height_px,
                device=args.device,
                baseline=0.0,
                learning_rate=args.learning_rate,
                exploration_sigma=args.exploration_sigma,
                eligibility_decay=args.eligibility_decay,
                baseline_rate=args.baseline_rate,
            )
            result = _evaluate_candidate(
                graph=graph, interface=interface, sparse=sparse, matrix=matrix, baseline=baseline,
                transport=transport, decoder=decoder, feature_bins=feature_bins, feature_signs=feature_signs,
                feature_counts=feature_counts, active_mask=active, steps=args.steps, screen_budget=args.screen_budget,
                seed=args.seed + rnd * 1000 + ci, spectral_scale=args.spectral_scale, gain=args.gain, leak=args.leak,
                visual_scale=args.visual_scale, reward_scale=args.reward_scale,
                reward_feedback_gain=args.reward_feedback_gain, projection_gain=args.projection_gain,
                plastic_reward_gain=args.plastic_reward_gain, device=args.device, learn=True,
            )
            result["candidate"] = ci
            candidates.append(result)
            line = {
                "event": "swarm_candidate",
                "round": rnd,
                "candidate": ci,
                "score": result["score"],
                "active_flies": int(active.sum()),
                "positive_full_swarm": int((result["fly_scores"] > 0).sum()),
                "best_instant_delta": result["best_instant_delta"],
                "elapsed_s": round(time.perf_counter() - t0, 3),
            }
            print(json.dumps(line, sort_keys=True), flush=True)
            with progress.open("a", encoding="utf-8") as f:
                f.write(json.dumps(line, sort_keys=True) + "\n")

        ranked = sorted(candidates, key=lambda r: r["score"], reverse=True)
        elites = ranked[:args.elites]
        parents = [row["final_weight"].detach().clone() for row in elites]
        winner_result = ranked[0]
        winner_weight = winner_result["final_weight"].detach().clone()
        positive = winner_result["fly_scores"] > 0
        min_survivors = max(4, args.flies // 4)
        if int(positive.sum()) >= min_survivors:
            active = positive
            selection_rule = "positive attraction-proxy responders"
        else:
            keep = max(min_survivors, args.flies // 2)
            top = np.argsort(winner_result["fly_scores"])[-keep:]
            active = np.zeros(args.flies, dtype=bool); active[top] = True
            selection_rule = "top responders fallback"
        round_row = {
            "round": rnd,
            "winner_candidate": int(winner_result["candidate"]),
            "winner_score": float(winner_result["score"]),
            "active_before": int(sum(1 for _ in np.flatnonzero(active))) if False else None,
            "survivors_next_round": int(active.sum()),
            "selection_rule": selection_rule,
            "candidate_scores": [float(r["score"]) for r in candidates],
            "winner_positive_full_swarm": int((winner_result["fly_scores"] > 0).sum()),
        }
        round_rows.append(round_row)

    # Freeze the evolved decoder and evaluate it on the original full swarm to
    # expose survivor-selection overfitting rather than hiding it.
    frozen = FullScreenPlasticDecoder.from_weight(
        winner_weight,
        width=args.screen_width_px,
        height=args.screen_height_px,
        device=args.device,
        baseline=0.0,
        learning_rate=args.learning_rate,
        exploration_sigma=0.0,
        eligibility_decay=args.eligibility_decay,
        baseline_rate=args.baseline_rate,
    )
    full_mask = np.ones(args.flies, dtype=bool)
    final = _evaluate_candidate(
        graph=graph, interface=interface, sparse=sparse, matrix=matrix, baseline=baseline,
        transport=transport, decoder=frozen, feature_bins=feature_bins, feature_signs=feature_signs,
        feature_counts=feature_counts, active_mask=full_mask, steps=args.final_steps, screen_budget=args.screen_budget,
        seed=args.seed + 99999, spectral_scale=args.spectral_scale, gain=args.gain, leak=args.leak,
        visual_scale=args.visual_scale, reward_scale=args.reward_scale,
        reward_feedback_gain=args.reward_feedback_gain, projection_gain=args.projection_gain,
        plastic_reward_gain=args.plastic_reward_gain, device=args.device, learn=False,
    )

    winner_frame = final["best_frame"]
    np.save(args.output_dir / "swarm-winner-frame.npy", winner_frame.detach().cpu().numpy())
    _save_screen_png(args.output_dir / "swarm-winner-frame.png", winner_frame)
    np.savez_compressed(
        args.output_dir / "swarm-winner-decoder.npz",
        weight=winner_weight.detach().cpu().numpy().astype(np.float32),
    )
    retinal = apply_transport(winner_frame, matrix, baseline, flies=transport.flies, receptors=transport.receptors)
    retinal_np = retinal.detach().cpu().numpy()
    np.save(args.output_dir / "swarm-winner-retinas.npy", retinal_np)
    best_fly = int(np.argmax(final["fly_scores"]))
    hard_fly = int(np.argmin(final["fly_scores"]))
    for label, fi in (("best", best_fly), ("hard", hard_fly)):
        values = retinal_np[:, fi]
        write_rgb_png(
            args.output_dir / f"swarm-{label}-fly-compound-eye.png",
            compound_eye_facets(values, geometry.x, geometry.y, geometry.eye, geometry.resolved, normalize=False),
        )
        write_rgb_png(
            args.output_dir / f"swarm-{label}-fly-panorama.png",
            panoramic_retina(values, geometry.x, geometry.y, geometry.resolved, normalize=False),
        )

    summary = {
        "experiment": "malecns-static-optics-swarm-evolution-v1",
        "swarm": {
            "flies": args.flies,
            "poses": poses.tolist(),
            "visible_mass": transport.visible_mass.tolist(),
            "physics_in_loop": "none; compiled sparse affine retinal transport",
            "transport_nonzeros": int(len(transport.values)),
        },
        "evolution": {
            "population": args.population,
            "elites": args.elites,
            "rounds": args.rounds,
            "steps_per_candidate": args.steps,
            "mutation_sigma": args.mutation_sigma,
            "online_learning_inside_candidate": True,
            "rounds_detail": round_rows,
        },
        "metric": "integrated descending-excitation learned-minus-energy-matched-uniform control; fixed receiver poses",
        "final_full_swarm_frozen": {
            "mean_score": float(final["score"]),
            "positive_responders": int((final["fly_scores"] > 0).sum()),
            "negative_responders": int((final["fly_scores"] <= 0).sum()),
            "fly_scores": final["fly_scores"].tolist(),
            "best_fly": best_fly,
            "hard_fly": hard_fly,
            "best_instant_delta": float(final["best_instant_delta"]),
        },
        "display": {
            "width_px": args.screen_width_px,
            "height_px": args.screen_height_px,
            "mean_luminance_budget": args.screen_budget,
            "physical_width": args.physical_width,
            "ambient": args.ambient,
        },
        "elapsed_s": time.perf_counter() - t0,
    }
    (args.output_dir / "swarm-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"event": "swarm_evolution_complete", "mean_score": final["score"], "positive": int((final["fly_scores"] > 0).sum()), "flies": args.flies}, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
