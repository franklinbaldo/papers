from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from gpu_batch import simulate_stimulus_swarm_batch
from visual_attractor import ArenaConfig, BrainConfig, FlyPose, StimulusSpec, load_graph, load_interface


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--interface", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--steps", type=int, default=200)
    parser.add_argument("--spectral-scale", type=float, default=3776.27)
    parser.add_argument("--visual-scale", type=float, default=0.5)
    parser.add_argument("--prime-scale", type=float, default=0.08)
    args = parser.parse_args()

    graph = load_graph(args.graph)
    interface = load_interface(args.interface)
    starts = (FlyPose(1.0, 0.0, np.pi),)
    result = simulate_stimulus_swarm_batch(
        graph,
        interface,
        (
            StimulusSpec("blank", path="blank"),
            StimulusSpec("static", path="static"),
            StimulusSpec("moving", path="sinusoid"),
        ),
        starts,
        steps=args.steps,
        brain=BrainConfig(
            spectral_scale=args.spectral_scale,
            visual_scale=args.visual_scale,
            prime_scale=args.prime_scale,
        ),
        arena=ArenaConfig(),
        device=args.device,
    )

    cols = {name: i for i, name in enumerate(result.stimulus_names)}
    traces = result.trajectory
    signals = (
        "visual_rms",
        "descending_left",
        "descending_right",
        "forward_command",
        "turn_command",
        "x",
        "y",
        "heading",
        "distance",
    )
    report = {
        "steps": args.steps,
        "stimuli": {},
        "deltas_vs_blank": {},
    }
    blank = cols["blank"]
    for name, col in cols.items():
        report["stimuli"][name] = {
            signal: {
                "mean": float(np.mean(traces[signal][:, col])),
                "max_abs": float(np.max(np.abs(traces[signal][:, col]))),
                "final": float(traces[signal][-1, col]),
            }
            for signal in signals
        }
        if name != "blank":
            report["deltas_vs_blank"][name] = {
                signal: {
                    "rms": float(np.sqrt(np.mean((traces[signal][:, col] - traces[signal][:, blank]) ** 2))),
                    "max_abs": float(np.max(np.abs(traces[signal][:, col] - traces[signal][:, blank]))),
                }
                for signal in signals
            }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
