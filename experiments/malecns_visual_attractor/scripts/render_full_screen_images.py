from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from full_screen_decoder import project_screen_to_receptors
from image_artifacts import rasterize_receptors, write_gray_png
from screen_reward_loop import load_screen_geometry
from visual_attractor import ArenaConfig
from visual_efficiency import matched_offset_starts


def _torch():
    import torch

    return torch


def main() -> None:
    parser = argparse.ArgumentParser(description="Render PNG artifacts for the physical full-screen MaleCNS run.")
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--frame", type=Path, required=True)
    parser.add_argument("--screen-geometry", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    frame_np = np.asarray(np.load(args.frame), dtype=np.float32)
    geometry = load_screen_geometry(args.screen_geometry)
    torch = _torch()

    best = summary["best_training_scenario"]
    scenario = best["scenario"]
    scenarios = summary.get("physics", {}).get("scenarios", [])
    scenario_index = next((i for i, row in enumerate(scenarios) if row.get("name") == scenario.get("name")), 0)
    params = summary["parameters"]
    seed = int(params["seed"]) + 1000 * scenario_index
    flies = int(params["flies"])
    heading_offset = float(params["heading_offset_deg"])
    start_x, start_y, start_h = matched_offset_starts(
        flies=flies,
        radius=float(scenario["radius"]),
        seed=seed,
        heading_offset_deg=heading_offset,
    )

    frame = torch.from_numpy(frame_np).to(device=args.device, dtype=torch.float32)
    receptor_x = torch.from_numpy(np.asarray(geometry.x, dtype=np.float32)).to(args.device)
    receptor_y = torch.from_numpy(np.asarray(geometry.y, dtype=np.float32)).to(args.device)
    resolved = torch.from_numpy(np.asarray(geometry.resolved, dtype=np.float32)).to(args.device)
    x = torch.from_numpy(start_x).to(device=args.device, dtype=torch.float64)
    y = torch.from_numpy(start_y).to(device=args.device, dtype=torch.float64)
    heading = torch.from_numpy(start_h).to(device=args.device, dtype=torch.float64)
    arena = ArenaConfig(dt=0.02)

    learned = project_screen_to_receptors(
        frame,
        receptor_x=receptor_x,
        receptor_y=receptor_y,
        resolved_mask=resolved,
        x=x,
        y=y,
        heading=heading,
        physical_width=float(scenario["screen_width"]),
        target_fov_rad=arena.target_fov_rad,
        ambient=float(scenario["ambient"]),
    )
    uniform_frame = torch.full_like(frame, float(summary["display"]["screen_mean_luminance_fraction"]))
    uniform = project_screen_to_receptors(
        uniform_frame,
        receptor_x=receptor_x,
        receptor_y=receptor_y,
        resolved_mask=resolved,
        x=x,
        y=y,
        heading=heading,
        physical_width=float(scenario["screen_width"]),
        target_fov_rad=arena.target_fov_rad,
        ambient=float(scenario["ambient"]),
    )

    learned_mean = learned.mean(dim=1).detach().cpu().numpy().astype(np.float32)
    uniform_mean = uniform.mean(dim=1).detach().cpu().numpy().astype(np.float32)
    delta = learned_mean - uniform_mean
    np.save(args.output_dir / "best-retina-initial-pose.npy", learned_mean)
    np.save(args.output_dir / "best-retina-vs-uniform.npy", delta)

    retina = rasterize_receptors(learned_mean, geometry.x, geometry.y, geometry.resolved)
    write_gray_png(args.output_dir / "best-full-screen-frame.png", frame_np)
    write_gray_png(args.output_dir / "best-retina-initial-pose-physical.png", retina)
    write_gray_png(args.output_dir / "best-retina-initial-pose-contrast.png", retina, normalize=True)

    max_abs = max(float(np.max(np.abs(delta))), 1e-12)
    signed = 0.5 + 0.5 * (delta / max_abs)
    delta_image = rasterize_receptors(signed, geometry.x, geometry.y, geometry.resolved)
    write_gray_png(args.output_dir / "best-retina-vs-uniform.png", delta_image)

    manifest = {
        "scenario": scenario,
        "pose": "reconstructed initial matched pose for best training scenario; average over flies",
        "resolved_receptors": int(np.sum(geometry.resolved)),
        "files": {
            "screen": "best-full-screen-frame.png",
            "retina_physical": "best-retina-initial-pose-physical.png",
            "retina_contrast": "best-retina-initial-pose-contrast.png",
            "retina_vs_uniform": "best-retina-vs-uniform.png",
        },
    }
    (args.output_dir / "image-artifacts.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"event": "full_screen_images_rendered", **manifest}, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
