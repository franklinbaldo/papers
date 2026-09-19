"""Run 19: phone-IMU kinematic clock-health stress for OBD-II/GNSS fusion.

Synthetic truth exists only to generate observations and score MAE. Deployable
arms receive only timestamped OBD-II speed, delayed GNSS speed with its reported
time, phone longitudinal IMU samples on a monotonic clock, observed residual
history, and declared nominal noise metadata.
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
from kinematic_clock_health import kinematic_clock_observation
from temporal_bias_calibration import PersistentBiasCalibrator
from temporal_robust_fusion import fuse, transport_by_reference_delta

DT = 0.1
REFERENCE_NOMINAL_SIGMA = 0.20
CANDIDATE_NOMINAL_SIGMA = 0.50
KINEMATIC_DELTA_V_SIGMA = 0.55


@dataclass(frozen=True)
class GnssFix:
    reported_measurement_index: int
    arrival_index: int
    value: float


@dataclass
class Episode:
    truth: list[float]
    obd: list[float]
    imu_acceleration: list[float]
    arrivals: dict[int, list[GnssFix]]


def generate_episode(
    seed: int,
    *,
    clock_mode: str,
    obd_mode: str,
    steps: int = 500,
    dropout: float = 0.15,
) -> Episode:
    rng = random.Random(seed)
    truth: list[float] = []
    acceleration: list[float] = []
    speed = rng.uniform(8.0, 25.0)
    accel = rng.uniform(-0.5, 0.5)

    for _ in range(steps):
        impulse = rng.gauss(0.0, 0.55)
        if rng.random() < 0.08:
            impulse += rng.uniform(-2.5, 2.5)
        accel = max(-4.0, min(3.5, 0.90 * accel + impulse))
        speed = max(0.0, speed + accel * DT)
        truth.append(speed)
        acceleration.append(accel)

    obd_bias = [0.0] * steps
    if obd_mode == "static":
        value = rng.choice((-1.0, 1.0)) * rng.uniform(1.0, 2.0)
        obd_bias = [value] * steps
    elif obd_mode == "drift":
        value = rng.uniform(-0.3, 0.3)
        for index in range(steps):
            value = max(-2.0, min(2.0, value + rng.gauss(0.0, 0.025)))
            obd_bias[index] = value
    elif obd_mode != "clean":
        raise ValueError(f"unknown OBD mode: {obd_mode}")

    obd = [
        truth[index] + obd_bias[index] + rng.gauss(0.0, 0.18)
        for index in range(steps)
    ]

    # A phone-mounted IMU is not privileged truth: add realistic-ish white noise
    # plus an episode-level bias. The exact generator values are not exposed.
    imu_bias = rng.gauss(0.0, 0.06)
    imu_acceleration = [
        acceleration[index] + imu_bias + rng.gauss(0.0, 0.22)
        for index in range(steps)
    ]

    if clock_mode not in {"clean", "offset", "jitter", "drift", "offset_jitter"}:
        raise ValueError(f"unknown clock mode: {clock_mode}")
    base_offset_steps = 3 if clock_mode in {"offset", "offset_jitter"} else 0
    drift_per_index = 0.006 if clock_mode == "drift" else 0.0

    arrivals: dict[int, list[GnssFix]] = {}
    for actual_index in range(0, steps, 5):
        if rng.random() < dropout:
            continue
        jitter_steps = (
            rng.randint(-2, 2) if clock_mode in {"jitter", "offset_jitter"} else 0
        )
        drift_steps = round(drift_per_index * actual_index)
        reported_index = max(
            0,
            min(
                steps - 1,
                actual_index + base_offset_steps + jitter_steps + drift_steps,
            ),
        )
        lag_steps = rng.randint(4, 12)
        arrival_index = actual_index + lag_steps
        if arrival_index >= steps:
            continue
        arrivals.setdefault(arrival_index, []).append(
            GnssFix(
                reported_measurement_index=reported_index,
                arrival_index=arrival_index,
                value=truth[actual_index] + rng.gauss(0.0, 0.45),
            )
        )

    return Episode(
        truth=truth,
        obd=obd,
        imu_acceleration=imu_acceleration,
        arrivals=arrivals,
    )


def _mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def run_episode(episode: Episode) -> dict[str, float]:
    latest: GnssFix | None = None
    previous_fix: GnssFix | None = None
    raw_scale = OnlineInnovationScale()
    corrected_scale = OnlineInnovationScale()
    calibrator = PersistentBiasCalibrator()

    imu_prefix_delta_v = [0.0]
    for sample in episode.imu_acceleration:
        imu_prefix_delta_v.append(imu_prefix_delta_v[-1] + sample * DT)

    errors = {
        name: []
        for name in (
            "obd_or_calibrator",
            "covariance",
            "covariance_imu_clock",
        )
    }
    clock_merits: list[float] = []
    kinematic_abs_residuals: list[float] = []
    clock_merit = 1.0

    for index, truth in enumerate(episode.truth):
        for fix in episode.arrivals.get(index, []):
            reported = fix.reported_measurement_index
            raw_residual = fix.value - episode.obd[reported]
            raw_scale.observe(raw_residual)
            calibrator.observe(episode.obd[reported], fix.value)
            corrected_residual = fix.value - calibrator.apply(episode.obd[reported])
            corrected_scale.observe(corrected_residual)

            if (
                previous_fix is not None
                and fix.reported_measurement_index
                > previous_fix.reported_measurement_index
            ):
                observation = kinematic_clock_observation(
                    previous_speed=previous_fix.value,
                    current_speed=fix.value,
                    previous_reported_index=previous_fix.reported_measurement_index,
                    current_reported_index=fix.reported_measurement_index,
                    imu_prefix_delta_v=imu_prefix_delta_v,
                    nominal_delta_v_sigma=KINEMATIC_DELTA_V_SIGMA,
                )
                clock_merit = observation.merit
                clock_merits.append(clock_merit)
                kinematic_abs_residuals.append(abs(observation.residual_delta_v))
            previous_fix = fix

            if latest is None or reported > latest.reported_measurement_index:
                latest = fix

        reference_now = calibrator.apply(episode.obd[index])
        values = {
            "obd_or_calibrator": reference_now,
            "covariance": reference_now,
            "covariance_imu_clock": reference_now,
        }

        if latest is not None and latest.reported_measurement_index <= index:
            reported = latest.reported_measurement_index
            age_s = (index - reported) * DT
            corrected_at_measurement = calibrator.apply(episode.obd[reported])
            corrected_residual = latest.value - corrected_at_measurement
            transported = transport_by_reference_delta(
                latest.value,
                corrected_at_measurement,
                reference_now,
            )
            relative_precision = covariance_relative_precision(
                raw_innovation_sigma=raw_scale.sigma,
                reference_nominal_sigma=REFERENCE_NOMINAL_SIGMA,
                candidate_nominal_sigma=CANDIDATE_NOMINAL_SIGMA,
            )
            covariance_weight = innovation_huber_weight(
                age_s=age_s,
                matched_time_residual=corrected_residual,
                innovation_sigma=corrected_scale.sigma,
                relative_precision=relative_precision,
            )
            values["covariance"] = fuse(
                reference_now,
                transported,
                covariance_weight,
            )
            values["covariance_imu_clock"] = fuse(
                reference_now,
                transported,
                covariance_weight * clock_merit,
            )

        for name, value in values.items():
            errors[name].append(abs(value - truth))

    result = {
        name: _mean(method_errors)
        for name, method_errors in errors.items()
    }
    result["clock_merit"] = _mean(clock_merits)
    result["kinematic_abs_residual"] = _mean(kinematic_abs_residuals)
    return result


def evaluate(*, seeds: int = 5, episodes_per_seed: int = 200) -> dict[str, object]:
    result: dict[str, object] = {
        "config": {
            "seeds": seeds,
            "episodes_per_seed": episodes_per_seed,
            "steps_per_episode": 500,
            "dt_s": DT,
            "obd_rate_hz": 10,
            "gnss_rate_hz": 2,
            "gnss_delay_s": [0.4, 1.2],
            "gnss_dropout": 0.15,
            "clock_offset_s": 0.3,
            "clock_jitter_s": [-0.2, 0.2],
            "clock_drift_stress_fraction": 0.006,
            "imu_noise_sd_mps2": 0.22,
            "imu_episode_bias_sd_mps2": 0.06,
            "kinematic_delta_v_sigma": KINEMATIC_DELTA_V_SIGMA,
        },
        "regimes": {},
    }

    clock_modes = ("clean", "offset", "jitter", "drift", "offset_jitter")
    obd_modes = ("clean", "static", "drift")
    for obd_index, obd_mode in enumerate(obd_modes):
        obd_result = {}
        for clock_index, clock_mode in enumerate(clock_modes):
            per_seed: list[dict[str, float]] = []
            for seed_index in range(seeds):
                rows = []
                for episode_index in range(episodes_per_seed):
                    seed = (
                        1_900_000
                        + obd_index * 500_000
                        + clock_index * 100_000
                        + seed_index * 10_000
                        + episode_index
                    )
                    rows.append(
                        run_episode(
                            generate_episode(
                                seed,
                                clock_mode=clock_mode,
                                obd_mode=obd_mode,
                            )
                        )
                    )
                per_seed.append(
                    {
                        name: statistics.mean(row[name] for row in rows)
                        for name in rows[0]
                    }
                )
            obd_result[clock_mode] = {
                name: {
                    "mean": statistics.mean(row[name] for row in per_seed),
                    "sd_across_seeds": statistics.stdev(row[name] for row in per_seed),
                }
                for name in per_seed[0]
            }
        result["regimes"][obd_mode] = obd_result
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--episodes-per-seed", type=int, default=200)
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
