from __future__ import annotations

import argparse
import json
from pathlib import Path

import run_dynamic_gauge_compression as v1
from semantic_atlas.observation import require_observable_energy, tail_window_texts


def run(manifest_path: Path, output_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    observation = manifest["observation"]
    if observation["mode"] != "tail_chars":
        raise ValueError("DGCT v1.1 supports only observation.mode=tail_chars")

    max_chars = int(observation["max_chars"])
    minimum_energy = float(observation["minimum_mean_squared_step_energy"])
    original_observer_paths = v1._observer_paths

    def observed_paths(
        observer_spec: dict,
        calibration_texts: list[str],
        trajectory_step_texts: list[str],
        *,
        reference_targets,
        srf_dim: int,
    ):
        return original_observer_paths(
            observer_spec,
            tail_window_texts(calibration_texts, max_chars=max_chars),
            tail_window_texts(trajectory_step_texts, max_chars=max_chars),
            reference_targets=reference_targets,
            srf_dim=srf_dim,
        )

    v1._observer_paths = observed_paths
    try:
        result = v1.run(manifest_path, output_path)
    finally:
        v1._observer_paths = original_observer_paths

    zero = result["fields"]["zero:seed=0:scale=1"]
    require_observable_energy(
        observer="reference_observer",
        train_energy=float(zero["reference_observer"]["raw"]["train_energy"]),
        test_energy=float(zero["reference_observer"]["raw"]["test_energy"]),
        minimum=minimum_energy,
    )
    require_observable_energy(
        observer="transfer_observer",
        train_energy=float(zero["transfer_observer"]["raw"]["train_energy"]),
        test_energy=float(zero["transfer_observer"]["raw"]["test_energy"]),
        minimum=minimum_energy,
    )

    result["schema_version"] = 2
    result["experiment"] = manifest["experiment"]
    result["observation"] = observation
    result["amendment"] = manifest["amendment"]
    result["execution_note"] = (
        "DGCT v1.1 changes only the observer-visible text window after v1 was invalidated "
        "by transfer-observer truncation. Field families, field parameters, generation, "
        "trajectory split, amplitude model and complexity metrics remain unchanged."
    )
    output_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("dynamic_gauge_compression_v1_1.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/dynamic_gauge_compression_v1_1.json"),
    )
    args = parser.parse_args()
    result = run(args.manifest, args.output)
    print(
        json.dumps(
            {
                key: {
                    "reference_test_energy_ratio": value["reference_observer"]["test_energy_ratio"],
                    "transfer_test_energy_ratio": value["transfer_observer"]["test_energy_ratio"],
                    "cross_model_delta": value["cross_model"]["delta"],
                }
                for key, value in result["fields"].items()
            },
            indent=2,
        )
    )
    print(f"artifact={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
