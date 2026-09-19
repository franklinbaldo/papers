"""Run 18: covariance/innovation-normalized robust fusion after matched-time transport.

The harness reuses Run 17's asynchronous OBD-II/GNSS generator and compares
conventional robust baselines under identical seeds. Latent truth exists only to
generate sensor observations and score MAE. Every estimator receives only
measurements, timestamps, observable matched-time residual history, and declared
channel-noise metadata available to a real car/phone interface.
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
from dataclasses import dataclass

from innovation_robust_fusion import (
    OnlineInnovationScale,
    covariance_relative_precision,
    innovation_huber_weight,
)
from temporal_bias_calibration import PersistentBiasCalibrator
from temporal_robust_fusion import (
    fuse,
    robust_fusion_weight,
    transport_by_reference_delta,
)

DT = 0.1
BASE_SCALE = 0.75
AGE_POWER = 1.0
REFERENCE_NOMINAL_SIGMA = 0.20
CANDIDATE_NOMINAL_SIGMA = 0.50


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
    maneuver_heavy: bool,
    steps: int = 250,
    dropout: float = 0.15,
) -> Episode:
    rng = random.Random(seed)
    truth: list[float] = []
    speed = rng.uniform(8.0, 25.0)
    acceleration = rng.uniform(-0.5, 0.5)

    impulse_sigma = 0.65 if maneuver_heavy else 0.35
    maneuver_probability = 0.12 if maneuver_heavy else 0.03
    impulse_radius = 3.0 if maneuver_heavy else 1.5
    min_acceleration = -5.0 if maneuver_heavy else -3.0
    max_acceleration = 4.0 if maneuver_heavy else 2.5

    for _ in range(steps):
        impulse = rng.gauss(0.0, impulse_sigma)
        if rng.random() < maneuver_probability:
            impulse += rng.uniform(-impulse_radius, impulse_radius)
        acceleration = max(
            min_acceleration,
            min(max_acceleration, 0.92 * acceleration + impulse),
        )
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
    for measurement_index in range(0, steps, 5):
        if rng.random() < dropout:
            continue
        lag_steps = rng.randint(4, 12)
        arrival_index = measurement_index + lag_steps
        if arrival_index >= steps:
            continue
        arrivals.setdefault(arrival_index, []).append(
            GnssFix(
                measurement_index=measurement_index,
                arrival_index=arrival_index,
                value=truth[measurement_index] + rng.gauss(0.0, 0.45),
            )
        )
    return Episode(truth=truth, obd=obd, arrivals=arrivals)


def run_episode(episode: Episode) -> dict[str, float]:
    latest: GnssFix | None = None
    calibrator = PersistentBiasCalibrator()
    raw_scale = OnlineInnovationScale()
    corrected_scale = OnlineInnovationScale()

    methods = (
        "obd_only",
        "transport_fixed_huber",
        "transport_age_huber",
        "innovation_huber",
        "bias_calibrated",
        "bias_innovation_huber",
        "bias_covariance_huber",
    )
    errors = {name: [] for name in methods}

    for index, truth in enumerate(episode.truth):
        for fix in episode.arrivals.get(index, []):
            measurement_index = fix.measurement_index
            raw_residual = fix.value - episode.obd[measurement_index]
            raw_scale.observe(raw_residual)

            calibrator.observe(episode.obd[measurement_index], fix.value)
            corrected_residual = (
                fix.value - calibrator.apply(episode.obd[measurement_index])
            )
            corrected_scale.observe(corrected_residual)

            if latest is None or measurement_index > latest.measurement_index:
                latest = fix

        obd_now = episode.obd[index]
        corrected_now = calibrator.apply(obd_now)
        values = {name: obd_now for name in methods}
        values["bias_calibrated"] = corrected_now
        values["bias_innovation_huber"] = corrected_now
        values["bias_covariance_huber"] = corrected_now

        if latest is not None:
            measurement_index = latest.measurement_index
            age_s = (index - measurement_index) * DT
            raw_residual = latest.value - episode.obd[measurement_index]
            transported = transport_by_reference_delta(
                latest.value,
                episode.obd[measurement_index],
                obd_now,
            )

            values["transport_fixed_huber"] = fuse(
                obd_now,
                transported,
                robust_fusion_weight(
                    age_s=age_s,
                    matched_time_residual=raw_residual,
                    base_scale=BASE_SCALE,
                    age_power=0.0,
                ),
            )
            values["transport_age_huber"] = fuse(
                obd_now,
                transported,
                robust_fusion_weight(
                    age_s=age_s,
                    matched_time_residual=raw_residual,
                    base_scale=BASE_SCALE,
                    age_power=AGE_POWER,
                ),
            )
            values["innovation_huber"] = fuse(
                obd_now,
                transported,
                innovation_huber_weight(
                    age_s=age_s,
                    matched_time_residual=raw_residual,
                    innovation_sigma=raw_scale.sigma,
                ),
            )

            corrected_at_measurement = calibrator.apply(
                episode.obd[measurement_index]
            )
            corrected_residual = latest.value - corrected_at_measurement
            corrected_transported = transport_by_reference_delta(
                latest.value,
                corrected_at_measurement,
                corrected_now,
            )
            equal_precision_weight = innovation_huber_weight(
                age_s=age_s,
                matched_time_residual=corrected_residual,
                innovation_sigma=corrected_scale.sigma,
            )
            values["bias_innovation_huber"] = fuse(
                corrected_now,
                corrected_transported,
                equal_precision_weight,
            )

            relative_precision = covariance_relative_precision(
                raw_innovation_sigma=raw_scale.sigma,
                reference_nominal_sigma=REFERENCE_NOMINAL_SIGMA,
                candidate_nominal_sigma=CANDIDATE_NOMINAL_SIGMA,
            )
            values["bias_covariance_huber"] = fuse(
                corrected_now,
                corrected_transported,
                innovation_huber_weight(
                    age_s=age_s,
                    matched_time_residual=corrected_residual,
                    innovation_sigma=corrected_scale.sigma,
                    relative_precision=relative_precision,
                ),
            )

        for name, value in values.items():
            errors[name].append(abs(value - truth))

    return {
        name: statistics.mean(method_errors)
        for name, method_errors in errors.items()
    }


def evaluate(
    *,
    seeds: int = 5,
    episodes_per_seed: int = 300,
) -> dict[str, object]:
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
            "base_huber_scale_mps": BASE_SCALE,
            "age_power": AGE_POWER,
            "innovation_huber_k": 1.345,
            "innovation_alpha": 0.08,
            "innovation_initial_sigma": 0.50,
            "innovation_floor_sigma": 0.25,
            "innovation_ceiling_sigma": 2.0,
            "innovation_clip_sigma": 3.0,
            "reference_nominal_sigma_mps": REFERENCE_NOMINAL_SIGMA,
            "candidate_nominal_sigma_mps": CANDIDATE_NOMINAL_SIGMA,
        },
        "profiles": {},
    }

    for profile_index, profile in enumerate(("ordinary", "maneuver_heavy")):
        profile_result = {}
        maneuver_heavy = profile == "maneuver_heavy"
        for mode_index, mode in enumerate(("clean", "static", "drift", "jump")):
            per_seed: list[dict[str, float]] = []
            for seed_index in range(seeds):
                rows = []
                for episode_index in range(episodes_per_seed):
                    seed = (
                        910000
                        + profile_index * 1_000_000
                        + mode_index * 100_000
                        + seed_index * 10_000
                        + episode_index
                    )
                    rows.append(
                        run_episode(
                            generate_episode(
                                seed,
                                bias_mode=mode,
                                maneuver_heavy=maneuver_heavy,
                            )
                        )
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
            profile_result[mode] = summary
        result["profiles"][profile] = profile_result
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--episodes-per-seed", type=int, default=300)
    args = parser.parse_args()
    print(
        json.dumps(
            evaluate(
                seeds=args.seeds,
                episodes_per_seed=args.episodes_per_seed,
            ),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
