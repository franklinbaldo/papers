"""Run 14: test an age-normalized Huber robust-fusion control.

Run 13 showed that fixed-scale Cauchy soft fusion dominates the current hard trust
gates. This run asks whether a second robust-estimation family improves further
without adding privileged state. The Huber residual radius contracts with report
freshness, so stale measurements must agree more tightly with already-observed
cross-modal evidence before receiving the same influence.

All tuning uses a delayed independent corroborating measurement. Hidden synthetic
truth is evaluation-only.
"""

from __future__ import annotations

from dataclasses import replace
import random
from statistics import mean, stdev

from adaptive_soft_trust import soften_probe_huber
from colony_continuous_context_ablation import _predict, _sample
from soft_trust import soften_probe

DEFAULT_FAULT_PROBABILITY = 0.20
PROFILE_OFFSETS = {"uniform": 0, "fresh_skew": 1_000, "stale_skew": 2_000}
HUBER_SCALE_GRID = (0.18, 0.25, 0.35, 0.50, 0.75, 1.00)
AGE_POWER_GRID = (0.0, 0.5, 1.0)
CALIBRATION_EPISODES = 3_000
PRIMARY_EVALUATION_STEPS = 5_000
SHIFT_EVALUATION_STEPS = 3_000
RUN13_CAUCHY_SCALE = 0.75


def _inject_specialist_fault(rng, report, *, probability, shared_bias=None):
    if shared_bias is not None:
        return replace(report, value=report.value + shared_bias, confidence=0.95)
    if rng.random() >= probability:
        return report
    bias = rng.choice((-1.0, 1.0)) * rng.uniform(0.6, 1.4)
    return replace(report, value=report.value + bias, confidence=0.95)


def _delayed_corroboration(rng, truth):
    return truth + rng.gauss(0.0, 0.10)


def _episode(
    rng,
    *,
    age_profile,
    huber_scale,
    age_power,
    fault_probability=DEFAULT_FAULT_PROBABILITY,
    correlated_camera_probability=0.0,
):
    truth, camera, imu = _sample(rng, age_profile=age_profile)
    states = {
        name: [list(camera[:2]), list(imu[:2])]
        for name in ("cauchy_fixed", "huber_fixed", "huber_age")
    }

    shared_camera_bias = None
    if rng.random() < correlated_camera_probability:
        shared_camera_bias = rng.choice((-1.0, 1.0)) * rng.uniform(0.6, 1.4)

    for raw_camera, raw_imu in zip(camera[2:6], imu[2:6]):
        camera_candidate = _inject_specialist_fault(
            rng,
            raw_camera,
            probability=fault_probability,
            shared_bias=shared_camera_bias,
        )
        imu_candidate = _inject_specialist_fault(
            rng,
            raw_imu,
            probability=fault_probability,
        )

        camera_reports, imu_reports = states["cauchy_fixed"]
        camera_reports.append(
            soften_probe(
                camera_reports,
                camera_candidate,
                imu_reports,
                residual_scale=RUN13_CAUCHY_SCALE,
            )
        )
        imu_reports.append(
            soften_probe(
                imu_reports,
                imu_candidate,
                camera_reports,
                residual_scale=RUN13_CAUCHY_SCALE,
            )
        )

        camera_reports, imu_reports = states["huber_fixed"]
        camera_reports.append(
            soften_probe_huber(
                camera_reports,
                camera_candidate,
                imu_reports,
                base_scale=huber_scale,
                age_power=0.0,
            )
        )
        imu_reports.append(
            soften_probe_huber(
                imu_reports,
                imu_candidate,
                camera_reports,
                base_scale=huber_scale,
                age_power=0.0,
            )
        )

        camera_reports, imu_reports = states["huber_age"]
        camera_reports.append(
            soften_probe_huber(
                camera_reports,
                camera_candidate,
                imu_reports,
                base_scale=huber_scale,
                age_power=age_power,
            )
        )
        imu_reports.append(
            soften_probe_huber(
                imu_reports,
                imu_candidate,
                camera_reports,
                base_scale=huber_scale,
                age_power=age_power,
            )
        )

    predictions = {
        name: _predict(reports[0], reports[1], len(reports[0]), len(reports[1]))
        for name, reports in states.items()
    }
    delayed_confirmation = _delayed_corroboration(rng, truth)
    result = {name: abs(value - truth) for name, value in predictions.items()}
    result["huber_age_delayed_loss"] = abs(
        predictions["huber_age"] - delayed_confirmation
    )
    return result


def calibrate_huber(
    *,
    episodes=CALIBRATION_EPISODES,
    seed=2026091916,
):
    """Tune Huber scale and age exponent using delayed sensor loss only."""

    choices = []
    for age_power in AGE_POWER_GRID:
        for scale in HUBER_SCALE_GRID:
            rng = random.Random(seed)
            total = 0.0
            for _ in range(episodes):
                total += _episode(
                    rng,
                    age_profile="uniform",
                    huber_scale=scale,
                    age_power=age_power,
                )["huber_age_delayed_loss"]
            choices.append((total / episodes, scale, age_power))
    return min(choices)


def _aggregate(rows):
    return {
        name: (
            mean(row[name] for row in rows),
            stdev(row[name] for row in rows),
        )
        for name in ("cauchy_fixed", "huber_fixed", "huber_age")
    }


def evaluate_condition(
    huber_scale,
    age_power,
    *,
    age_profile,
    fault_probability=DEFAULT_FAULT_PROBABILITY,
    correlated_camera_probability=0.0,
    steps=PRIMARY_EVALUATION_STEPS,
    base_seed=2026092020,
):
    rows = []
    for seed_offset in range(5):
        seed = (
            base_seed
            + PROFILE_OFFSETS[age_profile]
            + seed_offset
            + int(fault_probability * 100) * 10_000
            + int(correlated_camera_probability * 100) * 1_000_000
        )
        rng = random.Random(seed)
        totals = {
            "cauchy_fixed": 0.0,
            "huber_fixed": 0.0,
            "huber_age": 0.0,
        }
        for _ in range(steps):
            result = _episode(
                rng,
                age_profile=age_profile,
                huber_scale=huber_scale,
                age_power=age_power,
                fault_probability=fault_probability,
                correlated_camera_probability=correlated_camera_probability,
            )
            for name in totals:
                totals[name] += result[name]
        rows.append({name: total / steps for name, total in totals.items()})
    return _aggregate(rows)


def main():
    calibration_loss, huber_scale, age_power = calibrate_huber()
    print(
        f"huber_scale={huber_scale:.2f},age_power={age_power:.2f},"
        f"calibration_delayed_loss={calibration_loss:.6f}"
    )
    print("profile,cauchy_fixed,huber_fixed,huber_age")
    for profile in ("uniform", "fresh_skew", "stale_skew"):
        result = evaluate_condition(huber_scale, age_power, age_profile=profile)
        print(
            f"{profile},{result['cauchy_fixed'][0]:.6f},"
            f"{result['huber_fixed'][0]:.6f},{result['huber_age'][0]:.6f}"
        )

    print("fault_probability,cauchy_fixed,huber_age")
    for probability in (0.0, 0.1, 0.2, 0.3, 0.4):
        result = evaluate_condition(
            huber_scale,
            age_power,
            age_profile="uniform",
            fault_probability=probability,
            steps=SHIFT_EVALUATION_STEPS,
            base_seed=2026092040,
        )
        print(
            f"{probability:.1f},{result['cauchy_fixed'][0]:.6f},"
            f"{result['huber_age'][0]:.6f}"
        )

    print("correlated_camera_probability,cauchy_fixed,huber_age")
    for probability in (0.1, 0.3, 0.5, 0.7):
        result = evaluate_condition(
            huber_scale,
            age_power,
            age_profile="uniform",
            fault_probability=0.1,
            correlated_camera_probability=probability,
            steps=SHIFT_EVALUATION_STEPS,
            base_seed=2026092050,
        )
        print(
            f"{probability:.1f},{result['cauchy_fixed'][0]:.6f},"
            f"{result['huber_age'][0]:.6f}"
        )


if __name__ == "__main__":
    main()
