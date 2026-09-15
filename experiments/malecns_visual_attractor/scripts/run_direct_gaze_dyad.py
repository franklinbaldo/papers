from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np

from dyad import DYAD_CONDITIONS, direct_gaze_distance, dyad_starts, simulate_direct_gaze_dyads
from visual_attractor import ArenaConfig, BrainConfig, load_graph, load_interface


DEFAULT_SEED_BASE = 20260950


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_scales(value: str) -> tuple[float, ...]:
    try:
        scales = tuple(float(x.strip()) for x in value.split(",") if x.strip())
    except ValueError as exc:
        raise argparse.ArgumentTypeError("visual scales must be comma-separated floats") from exc
    if not scales or any(v <= 0 for v in scales):
        raise argparse.ArgumentTypeError("visual scales must all be > 0")
    return scales


def aggregate_scene_summaries(rows: list[dict]) -> dict:
    out: dict[str, dict[str, dict[str, float]]] = {}
    for condition in DYAD_CONDITIONS:
        out[condition] = {}
        metric_names = rows[0]["conditions"][condition].keys()
        for metric in metric_names:
            values = np.asarray([row["conditions"][condition][metric] for row in rows], dtype=float)
            out[condition][metric] = {
                "mean": float(values.mean()),
                "median": float(np.median(values)),
                "min": float(values.min()),
                "max": float(values.max()),
            }
    return out


def scene_diagnostics(result) -> dict[str, float]:
    p = result.pairs_per_condition
    index = {name: i for i, name in enumerate(result.condition_names)}

    def values(condition: str, metric: str) -> np.ndarray:
        i = index[condition]
        return result.metrics[metric][i * p : (i + 1) * p]

    rec_forward = values("reciprocal", "mean_forward")
    rec_turn = values("reciprocal", "mean_abs_turn")
    rec_receptor = values("reciprocal", "mean_receptor_rms")
    rec_reduction = values("reciprocal", "normalized_pair_distance_reduction")
    one_forward = values("one_way", "mean_forward")
    one_turn = values("one_way", "mean_abs_turn")
    blank_forward = values("blank_pair", "mean_forward")
    blank_turn = values("blank_pair", "mean_abs_turn")
    blank_receptor = values("blank_pair", "mean_receptor_rms")
    blank_reduction = values("blank_pair", "normalized_pair_distance_reduction")

    reciprocal_motor_l1 = np.abs(rec_forward - blank_forward) + np.abs(rec_turn - blank_turn)
    one_way_motor_l1 = np.abs(one_forward - blank_forward) + np.abs(one_turn - blank_turn)
    receptor_l1 = np.abs(rec_receptor - blank_receptor)
    return {
        "reciprocal_vs_blank_motor_l1": float(np.mean(reciprocal_motor_l1)),
        "one_way_vs_blank_motor_l1": float(np.mean(one_way_motor_l1)),
        "reciprocal_vs_blank_receptor_l1": float(np.mean(receptor_l1)),
        "reciprocal_vs_blank_distance_reduction_delta": float(np.mean(rec_reduction - blank_reduction)),
        "feedback_motor_gain_over_one_way": float(
            np.mean(reciprocal_motor_l1) / max(float(np.mean(one_way_motor_l1)), 1e-12)
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--interface", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--scenes", type=int, default=6)
    parser.add_argument("--pairs", type=int, default=32)
    parser.add_argument("--steps", type=int, default=300)
    parser.add_argument("--seed-base", type=int, default=DEFAULT_SEED_BASE)
    parser.add_argument("--physical-size", type=float, default=0.25)
    parser.add_argument("--apparent-width-deg", type=float, default=30.0)
    parser.add_argument("--visual-scales", type=parse_scales, default=parse_scales("0.5,2,8"))
    parser.add_argument("--spectral-scale", type=float, default=3776.27)
    parser.add_argument("--gain", type=float, default=1.0)
    parser.add_argument("--leak", type=float, default=0.2)
    parser.add_argument("--dt", type=float, default=0.02)
    args = parser.parse_args()

    if args.scenes < 1 or args.pairs < 1 or args.steps < 1:
        parser.error("--scenes, --pairs and --steps must be >= 1")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    trajectory_dir = args.output_dir / "trajectories"
    trajectory_dir.mkdir(exist_ok=True)
    progress_path = args.output_dir / "progress.jsonl"
    progress_path.write_text("", encoding="utf-8")

    graph = load_graph(args.graph)
    interface = load_interface(args.interface)
    if interface.visual_indices.size < 1000:
        raise RuntimeError(
            f"direct-gaze calibration requires the full mapped visual receptor set; got {interface.visual_indices.size}"
        )

    arena = ArenaConfig(dt=args.dt)
    distance = direct_gaze_distance(args.physical_size, args.apparent_width_deg)
    scale_results: list[dict] = []
    run_started = time.perf_counter()

    for scale_index, visual_scale in enumerate(args.visual_scales):
        scale_started = time.perf_counter()
        scene_rows: list[dict] = []
        diagnostic_rows: list[dict] = []
        scale_dir = trajectory_dir / f"scale-{visual_scale:g}"
        scale_dir.mkdir(exist_ok=True)
        brain = BrainConfig(
            spectral_scale=args.spectral_scale,
            gain=args.gain,
            leak=args.leak,
            visual_scale=visual_scale,
            prime_scale=0.0,
        )

        for scene_index in range(args.scenes):
            scene_started = time.perf_counter()
            seed = args.seed_base + scene_index
            starts_a, starts_b = dyad_starts(pairs=args.pairs, distance=distance, seed=seed)
            result = simulate_direct_gaze_dyads(
                graph,
                interface,
                starts_a,
                starts_b,
                steps=args.steps,
                brain=brain,
                physical_size=args.physical_size,
                arena=arena,
                device=args.device,
            )
            conditions = result.condition_summary()
            diagnostics = scene_diagnostics(result)
            scene_rows.append({"scene": scene_index, "seed": seed, "conditions": conditions})
            diagnostic_rows.append(diagnostics)

            trajectory_path = scale_dir / f"scene-{scene_index:03d}-seed-{seed}.npz"
            np.savez_compressed(
                trajectory_path,
                **result.trajectory,
                **{f"metric_{key}": value for key, value in result.metrics.items()},
            )

            scene_seconds = time.perf_counter() - scene_started
            completed = scene_index + 1
            scale_elapsed = time.perf_counter() - scale_started
            mean_scene = scale_elapsed / completed
            eta = mean_scene * (args.scenes - completed)
            progress = {
                "event": "scene_complete",
                "scale_index": scale_index,
                "visual_scale": visual_scale,
                "scene": scene_index,
                "seed": seed,
                "completed_scenes": completed,
                "total_scenes": args.scenes,
                "scene_seconds": round(scene_seconds, 3),
                "scale_elapsed_seconds": round(scale_elapsed, 3),
                "eta_seconds": round(eta, 3),
                "conditions": {
                    name: {
                        "capture": round(values["capture"], 4),
                        "mean_visual_rms": round(values["mean_visual_rms"], 8),
                        "mean_receptor_rms": round(values["mean_receptor_rms"], 8),
                        "mean_forward": round(values["mean_forward"], 8),
                        "mean_abs_turn": round(values["mean_abs_turn"], 8),
                        "distance_reduction": round(values["normalized_pair_distance_reduction"], 8),
                    }
                    for name, values in conditions.items()
                },
                "diagnostics": {k: round(v, 10) for k, v in diagnostics.items()},
            }
            with progress_path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(progress, sort_keys=True) + "\n")
            print(json.dumps(progress, sort_keys=True), flush=True)

        aggregate = aggregate_scene_summaries(scene_rows)
        diagnostics = {
            key: float(np.mean([row[key] for row in diagnostic_rows]))
            for key in diagnostic_rows[0]
        }
        reciprocal_visual = aggregate["reciprocal"]["mean_visual_rms"]["mean"]
        blank_visual = aggregate["blank_pair"]["mean_visual_rms"]["mean"]
        receptor_delta = diagnostics["reciprocal_vs_blank_receptor_l1"]
        motor_delta = diagnostics["reciprocal_vs_blank_motor_l1"]
        channel_live = bool(
            reciprocal_visual > 0.0
            and blank_visual == 0.0
            and receptor_delta > 1e-7
            and motor_delta > 1e-7
        )
        scale_result = {
            "visual_scale": visual_scale,
            "channel_live": channel_live,
            "aggregate": aggregate,
            "diagnostics": diagnostics,
            "scenes_detail": scene_rows,
            "elapsed_seconds": time.perf_counter() - scale_started,
        }
        scale_results.append(scale_result)
        print(
            json.dumps(
                {
                    "event": "scale_complete",
                    "visual_scale": visual_scale,
                    "channel_live": channel_live,
                    "diagnostics": diagnostics,
                },
                sort_keys=True,
            ),
            flush=True,
        )

    selected_scale = next(
        (row["visual_scale"] for row in scale_results if row["channel_live"]),
        None,
    )
    manifest = {
        "experiment": "malecns-direct-gaze-dyad-calibration-v1",
        "status": "calibration-not-scientific-result",
        "purpose": "establish a live full-visual reciprocal MaleCNS channel before Run 2",
        "graph": {"path": args.graph.name, "sha256": sha256(args.graph)},
        "interface": {
            "path": args.interface.name,
            "sha256": sha256(args.interface),
            "visual_receptors": int(interface.visual_indices.size),
        },
        "conditions": list(DYAD_CONDITIONS),
        "direct_gaze": True,
        "courtship_prime": False,
        "prime_scale": 0.0,
        "physical_size": args.physical_size,
        "apparent_width_deg": args.apparent_width_deg,
        "initial_pair_distance": distance,
        "visual_scales": list(args.visual_scales),
        "scenes": args.scenes,
        "pairs_per_condition_per_scene": args.pairs,
        "steps": args.steps,
        "scene_seeds": [args.seed_base + i for i in range(args.scenes)],
        "arena": {
            "dt": arena.dt,
            "base_speed": arena.base_speed,
            "motor_speed_gain": arena.motor_speed_gain,
            "motor_turn_gain": arena.motor_turn_gain,
            "turn_rate_rad_s": arena.turn_rate_rad_s,
        },
        "brain": {
            "spectral_scale": args.spectral_scale,
            "gain": args.gain,
            "leak": args.leak,
        },
        "scale_results": scale_results,
        "diagnostic_selection": {
            "smallest_channel_live_visual_scale": selected_scale,
            "selection_is_calibration_only": True,
            "run2_requires_new_preregistration": True,
        },
        "elapsed_seconds": time.perf_counter() - run_started,
    }
    summary_path = args.output_dir / "direct-gaze-dyad-summary.json"
    summary_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest["diagnostic_selection"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
