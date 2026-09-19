"""Run 15: asynchronous OBD-II/GNSS temporal-alignment ablation.

This is deliberately a lightweight synthetic interface test, not a real-driving
result. Hidden truth exists only inside the harness to generate sensor samples and
score MAE. Every deployable algorithm receives only timestamped sensor observations.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics
from dataclasses import dataclass

from temporal_bias_calibration import PersistentBiasCalibrator

DT = 0.1


def huber_weight(residual: float, scale: float) -> float:
    magnitude = abs(residual)
    if magnitude <= scale or magnitude == 0.0:
        return 1.0
    return scale / magnitude


def freshness(age_s: float, tau_s: float = 1.5) -> float:
    return math.exp(-max(0.0, age_s) / tau_s)


def fuse(
    reference: float,
    candidate: float,
    age_s: float,
    residual: float,
    *,
    scale: float = 0.75,
) -> float:
    weight = freshness(age_s) * huber_weight(residual, scale)
    return (reference + weight * candidate) / (1.0 + weight)


@dataclass(frozen=True)
class GnssFix:
    measurement_index: int
    arrival_index: int
    value: float


@dataclass
class Episode:
    truth: list[float]
    obd: list[float]
    arrivals: dict[int, list[GnssFix]]


def generate_episode(
    seed: int,
    *,
    bias_mode: str,
    steps: int = 250,
    dropout: float = 0.15,
) -> Episode:
    rng = random.Random(seed)
    truth: list[float] = []
    speed = rng.uniform(8.0, 25.0)
    acceleration = rng.uniform(-0.5, 0.5)
    for _ in range(steps):
        impulse = rng.gauss(0.0, 0.35)
        if rng.random() < 0.03:
            impulse += rng.uniform(-1.5, 1.5)
        acceleration = max(-3.0, min(2.5, 0.92 * acceleration + impulse))
        speed = max(0.0, speed + acceleration * DT)
        truth.append(speed)

    bias = [0.0] * steps
    if bias_mode == "static":
        value = rng.choice((-1.0, 1.0)) * rng.uniform(1.0, 2.0)
        bias = [value] * steps
    elif bias_mode == "drift":
        value = rng.uniform(-0.5, 0.5)
        for index in range(steps):
            value = max(-2.5, min(2.5, value + rng.gauss(0.0, 0.03)))
            bias[index] = value
    elif bias_mode == "jump":
        jump_index = rng.randint(steps // 4, 3 * steps // 4)
        base = rng.uniform(-0.3, 0.3)
        jump = rng.choice((-1.0, 1.0)) * rng.uniform(1.5, 2.5)
        for index in range(steps):
            bias[index] = base + (jump if index >= jump_index else 0.0)
    elif bias_mode != "clean":
        raise ValueError(f"unknown bias mode: {bias_mode}")

    obd = [
        truth[index] + bias[index] + rng.gauss(0.0, 0.18)
        for index in range(steps)
    ]
    arrivals: dict[int, list[GnssFix]] = {}
    for measurement_index in range(0, steps, 5):  # 2 Hz GNSS, 10 Hz OBD
        if rng.random() < dropout:
            continue
        lag_steps = rng.randint(4, 12)  # 0.4--1.2 s effective delay
        arrival_index = measurement_index + lag_steps
        if arrival_index >= steps:
            continue
        fix = GnssFix(
            measurement_index=measurement_index,
            arrival_index=arrival_index,
            value=truth[measurement_index] + rng.gauss(0.0, 0.45),
        )
        arrivals.setdefault(arrival_index, []).append(fix)
    return Episode(truth=truth, obd=obd, arrivals=arrivals)


def run_episode(episode: Episode, *, aligned_calibration: bool) -> dict[str, float]:
    calibrator = PersistentBiasCalibrator()
    latest: GnssFix | None = None
    errors = {
        name: []
        for name in (
            "obd_only",
            "stale_huber",
            "delta_transport",
            "bias_calibrated",
        )
    }
    active_steps = 0

    for index, truth in enumerate(episode.truth):
        for fix in episode.arrivals.get(index, []):
            reference_index = fix.measurement_index if aligned_calibration else index
            calibrator.observe(episode.obd[reference_index], fix.value)
            if latest is None or fix.measurement_index > latest.measurement_index:
                latest = fix

        obd_now = episode.obd[index]
        calibrated = calibrator.apply(obd_now)
        if calibrator.active:
            active_steps += 1

        stale_huber = obd_now
        delta_transport = obd_now
        if latest is not None:
            measurement_index = latest.measurement_index
            age_s = (index - measurement_index) * DT
            stale_huber = fuse(
                obd_now,
                latest.value,
                age_s,
                latest.value - obd_now,
            )
            transported = latest.value + (
                obd_now - episode.obd[measurement_index]
            )
            delta_transport = fuse(
                obd_now,
                transported,
                age_s,
                latest.value - episode.obd[measurement_index],
            )

        values = {
            "obd_only": obd_now,
            "stale_huber": stale_huber,
            "delta_transport": delta_transport,
            "bias_calibrated": calibrated,
        }
        for name, value in values.items():
            errors[name].append(abs(value - truth))

    result = {name: statistics.mean(values) for name, values in errors.items()}
    result["calibrator_active_fraction"] = active_steps / len(episode.truth)
    return result


def evaluate(*, seeds: int = 5, episodes_per_seed: int = 300) -> dict[str, object]:
    result: dict[str, object] = {
        "config": {
            "seeds": seeds,
            "episodes_per_seed": episodes_per_seed,
            "steps_per_episode": 250,
            "dt_s": DT,
            "obd_rate_hz": 10,
            "gnss_rate_hz": 2,
            "gnss_delay_s": [0.4, 1.2],
            "gnss_dropout": 0.15,
            "obd_noise_sd_mps": 0.18,
            "gnss_noise_sd_mps": 0.45,
        },
        "conditions": {},
    }

    for mode in ("clean", "static", "drift", "jump"):
        per_seed: list[dict[str, float]] = []
        for seed_index in range(seeds):
            rows: list[dict[str, float]] = []
            for episode_index in range(episodes_per_seed):
                seed = 800000 + seed_index * 10000 + episode_index
                episode = generate_episode(seed, bias_mode=mode)
                aligned = run_episode(episode, aligned_calibration=True)
                unaligned = run_episode(episode, aligned_calibration=False)
                rows.append(
                    {
                        **{
                            name: aligned[name]
                            for name in (
                                "obd_only",
                                "stale_huber",
                                "delta_transport",
                                "bias_calibrated",
                            )
                        },
                        "unaligned_bias_calibrated": unaligned["bias_calibrated"],
                        "aligned_active_fraction": aligned[
                            "calibrator_active_fraction"
                        ],
                        "unaligned_active_fraction": unaligned[
                            "calibrator_active_fraction"
                        ],
                    }
                )
            per_seed.append(
                {
                    name: statistics.mean(row[name] for row in rows)
                    for name in rows[0]
                }
            )

        summary = {}
        for name in per_seed[0]:
            values = [row[name] for row in per_seed]
            summary[name] = {
                "mean": statistics.mean(values),
                "sd_across_seeds": statistics.stdev(values),
            }
        result["conditions"][mode] = summary
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--episodes-per-seed", type=int, default=300)
    args = parser.parse_args()
    print(
        json.dumps(
            evaluate(seeds=args.seeds, episodes_per_seed=args.episodes_per_seed),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
