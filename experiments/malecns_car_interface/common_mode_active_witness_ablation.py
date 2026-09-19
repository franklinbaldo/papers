"""Run 22: common-mode OBD+GNSS false consensus and active independent tie-break.

This harness starts *after* deterministic timebase repair/matched-time
alignment so it isolates a different failure mode: OBD-II and GNSS may agree
while sharing the same wrong speed offset. A phone-camera ego-speed estimate
can expose the contradiction, but one dissenting sensor cannot identify which
side is wrong. The policy therefore requests a low-cost LiDAR ego-speed
estimate only after persistent conflict and uses it as a fourth independent
tie-break witness.

Synthetic truth and injected fault labels exist only for generation/scoring.
The deployable fusion module receives only sensor values that an ordinary car,
a phone, and the declared external LiDAR could produce.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
from dataclasses import dataclass

from active_common_mode_tiebreak import ActiveCommonModeTieBreak

DT = 0.1


@dataclass
class Episode:
    truth: list[float]
    obd: list[float]
    gnss: list[float]
    camera: list[float]
    lidar: list[float]
    common_bias: list[float]


def _trajectory(rng: random.Random, steps: int) -> list[float]:
    truth: list[float] = []
    speed = rng.uniform(8.0, 25.0)
    accel = rng.uniform(-0.5, 0.5)
    for _ in range(steps):
        impulse = rng.gauss(0.0, 0.55)
        if rng.random() < 0.08:
            impulse += rng.uniform(-2.5, 2.5)
        accel = max(-4.0, min(3.5, 0.90 * accel + impulse))
        speed = max(0.0, speed + accel * DT)
        truth.append(speed)
    return truth


def generate_episode(
    seed: int,
    *,
    pair_mode: str,
    camera_mode: str,
    lidar_mode: str,
    steps: int = 250,
) -> Episode:
    rng = random.Random(seed)
    truth = _trajectory(rng, steps)

    common = [0.0] * steps
    if pair_mode == "common_static":
        bias = rng.choice((-1.0, 1.0)) * rng.uniform(1.2, 2.0)
        common = [bias] * steps
    elif pair_mode == "common_drift":
        bias = rng.uniform(-0.2, 0.2)
        direction = rng.choice((-1.0, 1.0))
        for index in range(steps):
            bias += direction * 0.007 + rng.gauss(0.0, 0.008)
            bias = max(-2.2, min(2.2, bias))
            common[index] = bias
    elif pair_mode == "common_jump":
        bias = rng.choice((-1.0, 1.0)) * rng.uniform(1.4, 2.2)
        for index in range(steps // 2, steps):
            common[index] = bias
    elif pair_mode not in {"clean", "obd_only", "gnss_only"}:
        raise ValueError(pair_mode)

    obd_only_bias = (
        rng.choice((-1.0, 1.0)) * rng.uniform(1.2, 2.0)
        if pair_mode == "obd_only"
        else 0.0
    )
    gnss_only_bias = (
        rng.choice((-1.0, 1.0)) * rng.uniform(1.2, 2.0)
        if pair_mode == "gnss_only"
        else 0.0
    )

    obd = [
        value + common[index] + obd_only_bias + rng.gauss(0.0, 0.18)
        for index, value in enumerate(truth)
    ]
    gnss = [
        value + common[index] + gnss_only_bias + rng.gauss(0.0, 0.45)
        for index, value in enumerate(truth)
    ]

    camera_bias = 0.0
    camera_scale = 1.0
    if camera_mode == "bias":
        camera_bias = rng.choice((-1.0, 1.0)) * rng.uniform(1.2, 2.0)
    elif camera_mode == "scale":
        camera_scale = rng.choice((0.94, 1.06))
    elif camera_mode != "clean":
        raise ValueError(camera_mode)

    camera = [
        camera_scale * value + camera_bias + rng.gauss(0.0, 0.55)
        for value in truth
    ]

    lidar_bias = 0.0
    if lidar_mode == "bias":
        lidar_bias = rng.choice((-1.0, 1.0)) * rng.uniform(1.0, 1.8)
    elif lidar_mode != "clean":
        raise ValueError(lidar_mode)

    lidar = [
        value + lidar_bias + rng.gauss(0.0, 0.35)
        for value in truth
    ]
    return Episode(truth, obd, gnss, camera, lidar, common)


def _mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def run_episode(ep: Episode) -> dict[str, float]:
    fusion = ActiveCommonModeTieBreak()
    metrics = {
        "pair_mae": [],
        "naive_three_mae": [],
        "active_mae": [],
        "request_rate": [],
        "request_when_common": [],
        "request_when_not_common": [],
        "scoring_side_accuracy": [],
    }

    for index, truth in enumerate(ep.truth):
        primary = fusion.observe_primary(
            obd_speed=ep.obd[index],
            gnss_speed=ep.gnss[index],
            camera_speed=ep.camera[index],
        )
        pair = primary.pair_estimate
        naive_three = (
            ep.obd[index] + ep.gnss[index] + ep.camera[index]
        ) / 3.0

        if primary.request_aux:
            resolved = fusion.resolve_aux(lidar_speed=ep.lidar[index])
            active = resolved.estimate
        else:
            resolved = None
            active = pair

        metrics["pair_mae"].append(abs(pair - truth))
        metrics["naive_three_mae"].append(abs(naive_three - truth))
        metrics["active_mae"].append(abs(active - truth))
        metrics["request_rate"].append(float(primary.request_aux))

        actual_common = abs(ep.common_bias[index]) >= 0.8
        if actual_common:
            metrics["request_when_common"].append(float(primary.request_aux))
        else:
            metrics["request_when_not_common"].append(float(primary.request_aux))

        if resolved is not None:
            pair_error = abs(pair - truth)
            camera_error = abs(ep.camera[index] - truth)
            if resolved.choice == "camera_aux":
                correct = camera_error < pair_error
            else:
                correct = pair_error <= camera_error
            metrics["scoring_side_accuracy"].append(float(correct))

    return {key: _mean(values) for key, values in metrics.items()}


def evaluate(
    *,
    seeds: int = 3,
    episodes_per_seed: int = 30,
    steps: int = 250,
) -> dict[str, object]:
    pair_modes = (
        "clean",
        "common_static",
        "common_drift",
        "common_jump",
        "obd_only",
        "gnss_only",
    )
    camera_modes = ("clean", "bias", "scale")
    lidar_modes = ("clean", "bias")

    output: dict[str, object] = {
        "config": {
            "seeds": seeds,
            "episodes_per_seed": episodes_per_seed,
            "steps": steps,
            "dt_s": DT,
            "primary_hz_after_alignment": 10,
            "camera_noise_sd_mps": 0.55,
            "lidar_noise_sd_mps": 0.35,
            "obd_noise_sd_mps": 0.18,
            "gnss_noise_sd_mps": 0.45,
            "conflict_window": 8,
            "min_conflicts": 6,
            "pair_agreement_max_mps": 0.90,
            "camera_conflict_min_mps": 0.90,
            "aux_margin_mps": 0.15,
        },
        "regimes": {},
    }

    regimes = output["regimes"]
    assert isinstance(regimes, dict)
    for pair_index, pair_mode in enumerate(pair_modes):
        regimes[pair_mode] = {}
        for camera_index, camera_mode in enumerate(camera_modes):
            regimes[pair_mode][camera_mode] = {}
            for lidar_index, lidar_mode in enumerate(lidar_modes):
                seed_rows = []
                for seed_index in range(seeds):
                    rows = []
                    for episode_index in range(episodes_per_seed):
                        seed = (
                            22_000_000
                            + pair_index * 1_000_000
                            + camera_index * 100_000
                            + lidar_index * 50_000
                            + seed_index * 2_000
                            + episode_index
                        )
                        row = run_episode(
                            generate_episode(
                                seed,
                                pair_mode=pair_mode,
                                camera_mode=camera_mode,
                                lidar_mode=lidar_mode,
                                steps=steps,
                            )
                        )
                        rows.append(row)
                    seed_rows.append(
                        {
                            key: statistics.mean(row[key] for row in rows)
                            for key in rows[0]
                        }
                    )

                regimes[pair_mode][camera_mode][lidar_mode] = {
                    key: {
                        "mean": statistics.mean(row[key] for row in seed_rows),
                        "sd_across_seeds": (
                            statistics.stdev(row[key] for row in seed_rows)
                            if len(seed_rows) > 1
                            else 0.0
                        ),
                    }
                    for key in seed_rows[0]
                }
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=3)
    parser.add_argument("--episodes-per-seed", type=int, default=30)
    parser.add_argument("--steps", type=int, default=250)
    args = parser.parse_args()
    result = evaluate(
        seeds=args.seeds,
        episodes_per_seed=args.episodes_per_seed,
        steps=args.steps,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
