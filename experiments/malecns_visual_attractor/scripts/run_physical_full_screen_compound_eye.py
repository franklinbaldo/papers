from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

import run_physical_full_screen_attractor as base
from compound_eye_artifacts import compound_eye_facets, panoramic_retina, write_rgb_png
from compound_eye_environment import (
    calibrated_angles_numpy,
    physics_manifest,
    project_screen_to_receptors_compound_eye,
)
from screen_reward_loop import load_screen_geometry


def _arg(name: str, default: str | None = None) -> str:
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 >= len(sys.argv):
            raise RuntimeError(f"missing value after {name}")
        return sys.argv[i + 1]
    if default is None:
        raise RuntimeError(f"missing required argument {name}")
    return default


def main() -> None:
    conditions = len(base.CONDITIONS)
    recorded: dict[int, list[np.ndarray]] = {0: [], 1: []}
    call_index = 0

    def traced_projection(*args, **kwargs):
        nonlocal call_index
        out = project_screen_to_receptors_compound_eye(*args, **kwargs)
        ci = call_index % conditions
        # Keep the actual retinal vector of one real receiver for learned and
        # uniform control at every tick.  This is not reconstructed later.
        if ci in recorded:
            recorded[ci].append(out[:, 0].detach().cpu().numpy().astype(np.float32, copy=True))
        call_index += 1
        return out

    # The base experiment stays responsible for learning and controls; only the
    # environment/retinal transport is replaced.
    base.project_screen_to_receptors = traced_projection
    base.main()

    output_dir = Path(_arg("--output-dir"))
    geometry_path = Path(_arg("--screen-geometry"))
    steps = int(_arg("--steps", "350"))
    summary_path = output_dir / "full-screen-summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    geometry = load_screen_geometry(geometry_path)

    best = summary["best_training_scenario"]
    best_name = best["scenario"]["name"]
    scenario_index = next(
        i for i, row in enumerate(summary["scenarios"]) if row["scenario"]["name"] == best_name
    )
    best_step = int(best["best_step"])
    sample_index = scenario_index * steps + best_step
    if sample_index >= len(recorded[0]) or sample_index >= len(recorded[1]):
        raise RuntimeError(
            f"recorded retina index {sample_index} outside learned/uniform traces "
            f"{len(recorded[0])}/{len(recorded[1])}"
        )

    learned = recorded[0][sample_index]
    uniform = recorded[1][sample_index]
    delta = learned - uniform
    np.save(output_dir / "best-retina-actual-learned.npy", learned)
    np.save(output_dir / "best-retina-actual-uniform.npy", uniform)
    np.save(output_dir / "best-retina-actual-vs-uniform.npy", delta)

    write_rgb_png(
        output_dir / "best-retina-actual-compound-eye.png",
        compound_eye_facets(
            learned,
            geometry.x,
            geometry.y,
            geometry.eye,
            geometry.resolved,
            normalize=False,
        ),
    )
    write_rgb_png(
        output_dir / "best-retina-actual-compound-eye-contrast.png",
        compound_eye_facets(
            learned,
            geometry.x,
            geometry.y,
            geometry.eye,
            geometry.resolved,
            normalize=True,
        ),
    )
    write_rgb_png(
        output_dir / "best-retina-actual-panorama.png",
        panoramic_retina(
            learned,
            geometry.x,
            geometry.y,
            geometry.resolved,
            normalize=False,
        ),
    )
    write_rgb_png(
        output_dir / "best-retina-actual-panorama-contrast.png",
        panoramic_retina(
            learned,
            geometry.x,
            geometry.y,
            geometry.resolved,
            normalize=True,
        ),
    )
    write_rgb_png(
        output_dir / "best-retina-vs-uniform-compound-eye.png",
        compound_eye_facets(
            delta,
            geometry.x,
            geometry.y,
            geometry.eye,
            geometry.resolved,
            signed=True,
            normalize=True,
        ),
    )
    write_rgb_png(
        output_dir / "best-retina-vs-uniform-panorama.png",
        panoramic_retina(
            delta,
            geometry.x,
            geometry.y,
            geometry.resolved,
            signed=True,
            normalize=True,
        ),
    )

    _, _, calibration_mode = calibrated_angles_numpy(geometry.x, geometry.y)
    physics = summary.setdefault("physics", {})
    physics.update(physics_manifest())
    physics["column_calibration_mode"] = calibration_mode
    physics["retinal_sampling"] = (
        "optic-column azimuth/elevation + Gaussian ommatidial acceptance in a world-fixed visual surround"
    )
    summary["visualization"] = {
        "source": "actual retinal vector delivered at the best training tick; receiver index 0",
        "best_scenario": best_name,
        "best_step_zero_based": best_step,
        "facets": "two compound eyes; fronts toward image center",
        "panorama": "equirectangular calibrated azimuth/elevation field",
        "outputs": [
            "best-retina-actual-compound-eye.png",
            "best-retina-actual-compound-eye-contrast.png",
            "best-retina-actual-panorama.png",
            "best-retina-actual-panorama-contrast.png",
            "best-retina-vs-uniform-compound-eye.png",
            "best-retina-vs-uniform-panorama.png",
        ],
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_dir / "compound-eye-environment.json").write_text(
        json.dumps({**physics_manifest(), "column_calibration_mode": calibration_mode}, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "event": "compound_eye_visualization_complete",
                "calibration_mode": calibration_mode,
                "scenario": best_name,
                "best_step": best_step,
                "actual_retina_files": summary["visualization"]["outputs"],
            },
            sort_keys=True,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
