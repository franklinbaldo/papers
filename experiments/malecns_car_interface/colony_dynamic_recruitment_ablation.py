"""Deterministic fixed-budget dynamic-recruitment ablation for a MaleCNS colony.

The allocator never sees ground truth, realized error, or a hidden sensor-fault flag.
It observes only pilot specialist reports from lawful reality-bounded modalities.
Within-modality disagreement asks whether more independently trained specialists
might reduce cognitive/inference noise; report age prevents wasting compute on a
commonly stale physical stream.
"""

from __future__ import annotations

import random

from colony import (
    SpecialistReport,
    allocate_recruitment_slots,
    freshness_weighted_value,
    summarize_modality,
)


def _make_reports(
    rng: random.Random,
    *,
    modality: str,
    truth: float,
    velocity: float,
    count: int,
    base_age_ms: float | None,
) -> list[SpecialistReport]:
    reports: list[SpecialistReport] = []
    for index in range(count):
        if modality == "camera":
            assert base_age_ms is not None
            age_ms = max(0.0, base_age_ms + rng.uniform(-5.0, 5.0))
            burst = rng.random() < 0.15
            sigma = 0.20 if burst else 0.055
            confidence = 0.65 if burst else 0.90
        elif modality == "imu":
            age_ms = rng.uniform(5.0, 30.0)
            burst = rng.random() < 0.35
            sigma = 0.28 if burst else 0.11
            confidence = 0.62 if burst else 0.86
        else:
            raise ValueError(f"unknown modality: {modality}")

        value = truth - velocity * (age_ms / 1000.0) + rng.gauss(0.0, sigma)
        reports.append(
            SpecialistReport(
                specialist_id=f"{modality}-{index}",
                channel="dynamic-scalar",
                value=value,
                confidence=confidence,
                age_ms=age_ms,
                modality=modality,
            )
        )
    return reports


def _predict(
    camera_reports: list[SpecialistReport],
    imu_reports: list[SpecialistReport],
    *,
    camera_count: int,
    imu_count: int,
) -> float:
    camera_summary = summarize_modality(
        camera_reports[:camera_count], specialist_id="camera-summary"
    )
    imu_summary = summarize_modality(
        imu_reports[:imu_count], specialist_id="imu-summary"
    )
    return freshness_weighted_value([camera_summary, imu_summary])


def run_condition(
    stall_probability: float,
    *,
    trials: int = 10_000,
    seed: int = 20260918,
) -> dict[str, float]:
    """Compare static 12-fly splits with lawful dynamic recruitment."""

    rng = random.Random(seed + int(stall_probability * 1000))
    errors = {
        key: 0.0
        for key in (
            "camera_heavy_8_4",
            "balanced_6_6",
            "imu_heavy_4_8",
            "dynamic",
        )
    }
    extra_camera = 0
    extra_imu = 0

    for _ in range(trials):
        truth = rng.uniform(-1.0, 1.0)
        velocity = rng.uniform(-3.0, 3.0)

        camera_stalled = rng.random() < stall_probability
        camera_base_age_ms = (
            rng.uniform(450.0, 900.0)
            if camera_stalled
            else rng.uniform(20.0, 60.0)
        )

        # Generate enough independent specialist inference traces for every
        # matched-compute policy. The common camera acquisition age is shared.
        camera_reports = _make_reports(
            rng,
            modality="camera",
            truth=truth,
            velocity=velocity,
            count=8,
            base_age_ms=camera_base_age_ms,
        )
        imu_reports = _make_reports(
            rng,
            modality="imu",
            truth=truth,
            velocity=velocity,
            count=8,
            base_age_ms=None,
        )

        # Four pilot flies are always active. The remaining eight slots are
        # allocated without access to truth or the camera_stalled flag.
        allocation = allocate_recruitment_slots(
            {"camera": camera_reports[:2], "imu": imu_reports[:2]},
            extra_slots=8,
        )
        extra_camera += allocation["camera"]
        extra_imu += allocation["imu"]

        policies = {
            "camera_heavy_8_4": (8, 4),
            "balanced_6_6": (6, 6),
            "imu_heavy_4_8": (4, 8),
            "dynamic": (
                2 + allocation["camera"],
                2 + allocation["imu"],
            ),
        }
        for name, (camera_count, imu_count) in policies.items():
            prediction = _predict(
                camera_reports,
                imu_reports,
                camera_count=camera_count,
                imu_count=imu_count,
            )
            errors[name] += abs(prediction - truth)

    result = {name: total / trials for name, total in errors.items()}
    result["mean_extra_camera"] = extra_camera / trials
    result["mean_extra_imu"] = extra_imu / trials
    return result


def main() -> None:
    print(
        "stall_prob,camera_heavy_8_4,balanced_6_6,imu_heavy_4_8,dynamic,"
        "mean_extra_camera,mean_extra_imu"
    )
    for stall_probability in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
        result = run_condition(stall_probability)
        print(
            f"{stall_probability:.1f},"
            f"{result['camera_heavy_8_4']:.6f},"
            f"{result['balanced_6_6']:.6f},"
            f"{result['imu_heavy_4_8']:.6f},"
            f"{result['dynamic']:.6f},"
            f"{result['mean_extra_camera']:.4f},"
            f"{result['mean_extra_imu']:.4f}"
        )


if __name__ == "__main__":
    main()
