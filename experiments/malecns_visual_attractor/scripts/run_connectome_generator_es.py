from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from connectome_generator import GeneratorConfig, make_adapter
from connectome_generator_gpu import simulate_adapter_population_batch
from generator_optimizer import (
    adapter_from_vector,
    adapter_to_vector,
    elite_center,
    mirrored_population,
    weighted_score,
)
from visual_attractor import ArenaConfig, BrainConfig, load_graph, load_interface, radial_swarm


def load_weights(path: Path) -> dict[str, float]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not data:
        raise ValueError("score JSON must be a non-empty object")
    return {str(k): float(v) for k, v in data.items()}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--interface", type=Path, required=True)
    parser.add_argument("--score-json", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--distance", type=float, required=True)
    parser.add_argument("--steps", type=int, required=True)
    parser.add_argument("--scene-seeds", type=int, nargs="+", required=True)
    parser.add_argument("--flies", type=int, required=True)
    parser.add_argument("--population", type=int, required=True)
    parser.add_argument("--elite", type=int, required=True)
    parser.add_argument("--generations", type=int, required=True)
    parser.add_argument("--sigma", type=float, required=True)
    parser.add_argument("--adapter-seed", type=int, required=True)
    parser.add_argument("--es-seed", type=int, required=True)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--spectral-scale", type=float, default=3776.27)
    parser.add_argument("--emitter-gain", type=float, default=1.0)
    parser.add_argument("--emitter-leak", type=float, default=0.2)
    parser.add_argument("--emitter-input-scale", type=float, default=0.10)
    parser.add_argument("--receiver-gain", type=float, default=1.0)
    parser.add_argument("--receiver-leak", type=float, default=0.2)
    parser.add_argument("--visual-scale", type=float, default=0.5)
    parser.add_argument("--prime-scale", type=float, default=0.08)
    parser.add_argument("--dt", type=float, default=0.02)
    args = parser.parse_args()

    if args.distance <= 0 or args.steps < 1 or args.flies < 1 or args.generations < 1:
        parser.error("distance/steps/flies/generations must be positive")
    if args.population < 3 or args.population % 2 == 0:
        parser.error("--population must be odd and >= 3")
    if not 1 <= args.elite <= args.population:
        parser.error("--elite must be in [1,population]")

    score_weights = load_weights(args.score_json)
    graph = load_graph(args.graph)
    interface = load_interface(args.interface)
    template = make_adapter(interface, seed=args.adapter_seed)
    center = adapter_to_vector(template)
    emitter = GeneratorConfig(
        spectral_scale=args.spectral_scale,
        gain=args.emitter_gain,
        leak=args.emitter_leak,
        input_scale=args.emitter_input_scale,
    )
    receiver = BrainConfig(
        spectral_scale=args.spectral_scale,
        gain=args.receiver_gain,
        leak=args.receiver_leak,
        visual_scale=args.visual_scale,
        prime_scale=args.prime_scale,
    )
    arena = ArenaConfig(dt=args.dt)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    history: list[dict] = []
    best_score = -np.inf
    best_vector = center.copy()
    best_generation = -1

    for generation in range(args.generations):
        vectors = mirrored_population(
            center,
            sigma=args.sigma,
            population=args.population,
            seed=args.es_seed + generation,
        )
        adapters = tuple(adapter_from_vector(template, vector) for vector in vectors)
        scene_summaries: list[dict[str, np.ndarray]] = []

        for seed in args.scene_seeds:
            starts = radial_swarm(flies=args.flies, radius=args.distance, seed=seed)
            result = simulate_adapter_population_batch(
                graph,
                interface,
                adapters,
                starts,
                steps=args.steps,
                emitter=emitter,
                receiver=receiver,
                arena=arena,
                device=args.device,
            )
            scene_summaries.append(result.candidate_summary())

        metric_names = tuple(scene_summaries[0])
        aggregate = {
            name: np.mean(
                np.stack([scene[name] for scene in scene_summaries], axis=0),
                axis=0,
            )
            for name in metric_names
        }
        scores = weighted_score(aggregate, score_weights)
        order = np.argsort(-scores, kind="stable")
        winner = int(order[0])
        if float(scores[winner]) > best_score:
            best_score = float(scores[winner])
            best_vector = vectors[winner].copy()
            best_generation = generation

        generation_record = {
            "generation": generation,
            "candidate_scores": [float(x) for x in scores],
            "winner": winner,
            "winner_score": float(scores[winner]),
            "winner_metrics": {
                name: float(values[winner]) for name, values in aggregate.items()
            },
            "population_seed": args.es_seed + generation,
        }
        history.append(generation_record)
        (args.output_dir / f"generation-{generation:04d}.json").write_text(
            json.dumps(generation_record, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        center = elite_center(vectors, scores, elite=args.elite)
        print(json.dumps(generation_record, sort_keys=True), flush=True)

    np.savez_compressed(
        args.output_dir / "best-adapter.npz",
        vector=best_vector,
        input_indices=template.input_indices,
        readout_indices=template.readout_indices,
    )
    manifest = {
        "experiment": "malecns-connectome-generator-es-v1",
        "score_weights": score_weights,
        "distance": args.distance,
        "steps": args.steps,
        "scene_seeds": args.scene_seeds,
        "flies": args.flies,
        "population": args.population,
        "elite": args.elite,
        "generations": args.generations,
        "sigma": args.sigma,
        "adapter_seed": args.adapter_seed,
        "es_seed": args.es_seed,
        "device": args.device,
        "trainable_parameters": template.trainable_parameters,
        "best_generation": best_generation,
        "best_score": best_score,
        "history": history,
    }
    (args.output_dir / "optimizer-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
