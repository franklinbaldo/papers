from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict
from math import pi, tan
from pathlib import Path

import numpy as np

from gpu_batch import simulate_stimulus_swarm_batch
from visual_attractor import (
    ArenaConfig,
    BrainConfig,
    StimulusSpec,
    capture_pass,
    load_graph,
    load_interface,
    radial_swarm,
)


DEFAULT_SPECTRAL_SCALE = 3776.27
DEFAULT_SEED_BASE = 20260914


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def reference_distance(
    physical_size: float, apparent_width_deg: float = 15.0
) -> float:
    if physical_size <= 0 or not 0 < apparent_width_deg < 180:
        raise ValueError("invalid target size/apparent width")
    return (physical_size / 2.0) / tan(np.deg2rad(apparent_width_deg / 2.0))


def horizon_steps(
    distance: float,
    arena: ArenaConfig,
    *,
    acquisition_seconds: float = 2.0,
) -> int:
    if arena.base_speed <= 0:
        raise ValueError("base_speed must be positive for a distance-scaled horizon")
    seconds = 1.5 * distance / arena.base_speed + acquisition_seconds
    return int(np.ceil(seconds / arena.dt))


def stimuli() -> tuple[StimulusSpec, ...]:
    # 18 degrees at 0.47 Hz has peak angular velocity about 53 deg/s:
    # 2*pi*f*A ~= 53.2 deg/s.
    return (
        StimulusSpec(
            "moving_target",
            path="sinusoid",
            path_amplitude_deg=18.0,
            path_frequency_hz=0.47,
        ),
        StimulusSpec("static_equivalent", path="static"),
        StimulusSpec("blank", path="blank"),
        StimulusSpec(
            "random_motion",
            path="random_motion",
            path_amplitude_deg=18.0,
            random_seed=DEFAULT_SEED_BASE,
        ),
    )


def sector_approach(
    approach: np.ndarray, starts, *, sectors: int = 8
) -> list[float | None]:
    buckets: list[list[float]] = [[] for _ in range(sectors)]
    for value, start in zip(approach, starts, strict=True):
        angle = (np.arctan2(start.y, start.x) + pi) / (2 * pi)
        index = min(sectors - 1, int(angle * sectors))
        buckets[index].append(float(value))
    return [float(np.mean(bucket)) if bucket else None for bucket in buckets]


def aggregate_scenes(scene_rows: list[dict]) -> dict:
    names = tuple(scene_rows[0]["stimuli"].keys())
    metrics = tuple(next(iter(scene_rows[0]["stimuli"].values())).keys())
    result = {}
    for name in names:
        result[name] = {}
        for metric in metrics:
            values = np.asarray(
                [row["stimuli"][name][metric] for row in scene_rows], dtype=float
            )
            result[name][metric] = {
                "mean": float(values.mean()),
                "median": float(np.median(values)),
                "q25": float(np.quantile(values, 0.25)),
                "q75": float(np.quantile(values, 0.75)),
            }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--interface", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--scenes", type=int, default=32)
    parser.add_argument("--flies", type=int, default=64)
    parser.add_argument("--seed-base", type=int, default=DEFAULT_SEED_BASE)
    parser.add_argument("--spectral-scale", type=float, default=DEFAULT_SPECTRAL_SCALE)
    parser.add_argument("--gain", type=float, default=1.0)
    parser.add_argument("--leak", type=float, default=0.2)
    parser.add_argument("--visual-scale", type=float, default=0.5)
    parser.add_argument("--prime-scale", type=float, default=0.08)
    parser.add_argument("--dt", type=float, default=0.02)
    parser.add_argument("--acquisition-seconds", type=float, default=2.0)
    args = parser.parse_args()

    if args.scenes < 1 or args.flies < 1:
        parser.error("--scenes and --flies must be >= 1")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    trajectory_dir = args.output_dir / "trajectories"
    trajectory_dir.mkdir(exist_ok=True)

    graph = load_graph(args.graph)
    interface = load_interface(args.interface)
    arena = ArenaConfig(dt=args.dt)
    brain = BrainConfig(
        spectral_scale=args.spectral_scale,
        gain=args.gain,
        leak=args.leak,
        visual_scale=args.visual_scale,
        prime_scale=args.prime_scale,
    )
    stimulus_values = stimuli()
    d0 = reference_distance(stimulus_values[0].physical_size)
    steps = horizon_steps(
        d0,
        arena,
        acquisition_seconds=args.acquisition_seconds,
    )

    scene_rows: list[dict] = []
    for scene_index in range(args.scenes):
        seed = args.seed_base + scene_index
        starts = radial_swarm(flies=args.flies, radius=d0, seed=seed)
        result = simulate_stimulus_swarm_batch(
            graph,
            interface,
            stimulus_values,
            starts,
            steps=steps,
            brain=brain,
            arena=arena,
            device=args.device,
        )
        summary = result.stimulus_summary()
        sectors = {}
        for stimulus_index, stimulus in enumerate(stimulus_values):
            lo = stimulus_index * args.flies
            hi = (stimulus_index + 1) * args.flies
            sectors[stimulus.name] = sector_approach(
                result.metrics["approach"][lo:hi], starts
            )

        trajectory_path = (
            trajectory_dir / f"scene-{scene_index:03d}-seed-{seed}.npz"
        )
        np.savez_compressed(
            trajectory_path,
            **result.trajectory,
            **{
                f"metric_{key}": value
                for key, value in result.metrics.items()
            },
        )
        scene_rows.append(
            {
                "scene": scene_index,
                "seed": seed,
                "stimuli": summary,
                "approach_by_sector": sectors,
                "trajectory": trajectory_path.name,
            }
        )
        print(
            json.dumps(
                {
                    "scene": scene_index,
                    "seed": seed,
                    "approach": {
                        name: round(values["approach"], 4)
                        for name, values in summary.items()
                    },
                },
                sort_keys=True,
            ),
            flush=True,
        )

    aggregate = aggregate_scenes(scene_rows)
    moving = aggregate["moving_target"]["approach"]["mean"]
    controls = {
        name: aggregate[name]["approach"]["mean"]
        for name in ("static_equivalent", "blank", "random_motion")
    }
    strongest_control_name = max(controls, key=controls.get)
    strongest_control = controls[strongest_control_name]

    manifest = {
        "experiment": "malecns-visual-attractor-positive-control-v1",
        "graph": {"path": args.graph.name, "sha256": sha256(args.graph)},
        "interface": {
            "path": args.interface.name,
            "sha256": sha256(args.interface),
        },
        "device": args.device,
        "scene_seeds": [args.seed_base + i for i in range(args.scenes)],
        "scenes": args.scenes,
        "flies_per_stimulus_per_scene": args.flies,
        "stimuli": [asdict(value) for value in stimulus_values],
        "reference_distance": d0,
        "reference_apparent_width_deg": 15.0,
        "nominal_peak_angular_velocity_deg_s": 2 * pi * 0.47 * 18.0,
        "steps": steps,
        "arena": asdict(arena),
        "brain": asdict(brain),
        "acquisition_seconds": args.acquisition_seconds,
        "decision": {
            "p0": 0.60,
            "control_margin": 0.10,
            "moving_approach_probability": moving,
            "strongest_control": strongest_control_name,
            "strongest_control_approach_probability": strongest_control,
            "capture_pass": capture_pass(moving, strongest_control),
        },
        "aggregate": aggregate,
        "scenes_detail": scene_rows,
    }
    summary_path = args.output_dir / "positive-control-summary.json"
    summary_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest["decision"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
