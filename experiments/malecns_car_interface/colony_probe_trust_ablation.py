"""Run 11: separate paying to probe a specialist from trusting its report.

The experiment starts from two trusted camera and two trusted IMU specialists,
then pays for four additional reports from each modality. Every probe costs the
same compute regardless of whether its report is later admitted into fusion.

Synthetic specialist faults are injected only by the harness. The trust gate does
not receive the fault flag or hidden truth. It sees only lawful specialist value,
confidence, age and the already-trusted cross-modal reports.
"""

from __future__ import annotations

from dataclasses import replace
import random
from statistics import mean, stdev

from colony_continuous_context_ablation import _predict, _sample
from probe_trust import should_trust_probe

DEFAULT_FAULT_PROBABILITY = 0.20
DEFAULT_CALIBRATION_STEPS = 12_000
DEFAULT_EVALUATION_STEPS = 10_000
DEFAULT_THRESHOLD_GRID = tuple(index / 100.0 for index in range(0, 51, 2))


def _inject_specialist_fault(rng, report, *, probability):
    """Inject an unobserved specialist-level high-confidence bias for testing."""

    if rng.random() >= probability:
        return report
    bias = rng.choice((-1.0, 1.0)) * rng.uniform(0.6, 1.4)
    return replace(report, value=report.value + bias, confidence=0.95)


def _episode(rng, *, age_profile, threshold, fault_probability):
    truth, camera, imu = _sample(rng, age_profile=age_profile)

    trusted_camera = list(camera[:2])
    trusted_imu = list(imu[:2])
    always_camera = list(trusted_camera)
    always_imu = list(trusted_imu)

    pilot_only_error = abs(_predict(trusted_camera, trusted_imu, 2, 2) - truth)
    accepted = 0
    probes = 0

    for raw_camera, raw_imu in zip(camera[2:6], imu[2:6]):
        camera_candidate = _inject_specialist_fault(
            rng, raw_camera, probability=fault_probability
        )
        always_camera.append(camera_candidate)
        probes += 1
        if should_trust_probe(
            trusted_camera,
            camera_candidate,
            trusted_imu,
            threshold=threshold,
        ):
            trusted_camera.append(camera_candidate)
            accepted += 1

        imu_candidate = _inject_specialist_fault(
            rng, raw_imu, probability=fault_probability
        )
        always_imu.append(imu_candidate)
        probes += 1
        if should_trust_probe(
            trusted_imu,
            imu_candidate,
            trusted_camera,
            threshold=threshold,
        ):
            trusted_imu.append(imu_candidate)
            accepted += 1

    always_trust_error = abs(
        _predict(always_camera, always_imu, len(always_camera), len(always_imu))
        - truth
    )
    probe_then_trust_error = abs(
        _predict(
            trusted_camera,
            trusted_imu,
            len(trusted_camera),
            len(trusted_imu),
        )
        - truth
    )
    return (
        pilot_only_error,
        always_trust_error,
        probe_then_trust_error,
        accepted / probes,
    )


def evaluate_seed(
    *,
    seed,
    age_profile,
    threshold,
    fault_probability=DEFAULT_FAULT_PROBABILITY,
    steps=DEFAULT_EVALUATION_STEPS,
):
    rng = random.Random(seed)
    totals = [0.0, 0.0, 0.0, 0.0]
    for _ in range(steps):
        values = _episode(
            rng,
            age_profile=age_profile,
            threshold=threshold,
            fault_probability=fault_probability,
        )
        totals = [total + value for total, value in zip(totals, values)]
    return tuple(total / steps for total in totals)


def calibrate_threshold(
    *,
    seed=2026091901,
    steps=DEFAULT_CALIBRATION_STEPS,
    fault_probability=DEFAULT_FAULT_PROBABILITY,
):
    """Calibrate one scalar gate threshold on a disjoint synthetic training stream."""

    choices = []
    for threshold in DEFAULT_THRESHOLD_GRID:
        result = evaluate_seed(
            seed=seed,
            age_profile="uniform",
            threshold=threshold,
            fault_probability=fault_probability,
            steps=steps,
        )
        choices.append((result[2], threshold, result[3]))
    return min(choices)


def _aggregate(rows):
    names = ("pilot_only", "always_trust", "probe_then_trust", "acceptance")
    return {
        name: (mean(row[index] for row in rows), stdev(row[index] for row in rows))
        for index, name in enumerate(names)
    }


def evaluate_profiles(threshold):
    results = {}
    for profile_index, profile in enumerate(
        ("uniform", "fresh_skew", "stale_skew")
    ):
        rows = [
            evaluate_seed(
                seed=2026092000 + profile_index * 100 + seed_offset,
                age_profile=profile,
                threshold=threshold,
            )
            for seed_offset in range(5)
        ]
        results[profile] = _aggregate(rows)
    return results


def evaluate_fault_rates(threshold):
    results = {}
    for probability in (0.0, 0.1, 0.2, 0.3):
        rows = [
            evaluate_seed(
                seed=2026093000 + int(probability * 100) * 10 + seed_offset,
                age_profile="uniform",
                threshold=threshold,
                fault_probability=probability,
            )
            for seed_offset in range(5)
        ]
        results[probability] = _aggregate(rows)
    return results


def main():
    calibration_loss, threshold, calibration_acceptance = calibrate_threshold()
    print(
        f"calibrated_threshold={threshold:.2f},"
        f"calibration_probe_mae={calibration_loss:.6f},"
        f"calibration_acceptance={calibration_acceptance:.6f}"
    )
    print(
        "profile,pilot_mean,pilot_sd,always_mean,always_sd,probe_mean,probe_sd,"
        "accept_mean,accept_sd"
    )
    for profile, result in evaluate_profiles(threshold).items():
        print(
            f"{profile},{result['pilot_only'][0]:.6f},{result['pilot_only'][1]:.6f},"
            f"{result['always_trust'][0]:.6f},{result['always_trust'][1]:.6f},"
            f"{result['probe_then_trust'][0]:.6f},{result['probe_then_trust'][1]:.6f},"
            f"{result['acceptance'][0]:.6f},{result['acceptance'][1]:.6f}"
        )

    print("fault_probability,always_mean,probe_mean,accept_mean")
    for probability, result in evaluate_fault_rates(threshold).items():
        print(
            f"{probability:.1f},{result['always_trust'][0]:.6f},"
            f"{result['probe_then_trust'][0]:.6f},{result['acceptance'][0]:.6f}"
        )


if __name__ == "__main__":
    main()
