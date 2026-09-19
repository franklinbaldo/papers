"""Ablation for correlated/common-mode sensor stalls in a MaleCNS colony.

Several specialists may redundantly interpret the same physical sensor. That
protects against independent specialist failures, but cannot create new
information when the *sensor itself* stalls: all specialists can agree and be
confident about the same old sample.

This deterministic experiment compares five camera specialists estimating one
fast-changing lawful scalar against a second independent modality (three IMU
specialists) that estimates the same scalar. Camera stalls are common-mode: all
camera flies receive the same old sensor state. The hierarchical condition first
summarizes each modality, then freshness-weights the modality summaries.
"""

from __future__ import annotations

import random

from colony import (
    SpecialistReport,
    freshness_weighted_value,
    median_value,
    summarize_modality,
)


def run_condition(
    stall_probability: float,
    *,
    trials: int = 10_000,
    seed: int = 20260918,
) -> dict[str, float]:
    """Return mean absolute error for one common-mode stall condition."""

    rng = random.Random(seed + int(stall_probability * 1000))
    errors = {
        key: 0.0
        for key in (
            "visual_single",
            "visual_five_median",
            "visual_five_freshness",
            "hierarchy_median",
            "hierarchy_freshness",
        )
    }

    for _ in range(trials):
        truth = rng.uniform(-1.0, 1.0)
        velocity = rng.uniform(-3.0, 3.0)

        camera_stalled = rng.random() < stall_probability
        camera_base_age_ms = (
            rng.uniform(450.0, 900.0)
            if camera_stalled
            else rng.uniform(20.0, 60.0)
        )

        camera_reports: list[SpecialistReport] = []
        for index in range(5):
            age_ms = max(0.0, camera_base_age_ms + rng.uniform(-5.0, 5.0))
            value = truth - velocity * (age_ms / 1000.0) + rng.gauss(0.0, 0.025)
            camera_reports.append(
                SpecialistReport(
                    specialist_id=f"camera-{index}",
                    channel="dynamic-scalar",
                    value=value,
                    confidence=0.90,
                    age_ms=age_ms,
                    modality="camera",
                )
            )

        imu_reports: list[SpecialistReport] = []
        for index in range(3):
            age_ms = rng.uniform(5.0, 30.0)
            value = truth - velocity * (age_ms / 1000.0) + rng.gauss(0.0, 0.04)
            imu_reports.append(
                SpecialistReport(
                    specialist_id=f"imu-{index}",
                    channel="dynamic-scalar",
                    value=value,
                    confidence=0.85,
                    age_ms=age_ms,
                    modality="imu",
                )
            )

        camera_summary = summarize_modality(
            camera_reports,
            specialist_id="camera-summary",
        )
        imu_summary = summarize_modality(
            imu_reports,
            specialist_id="imu-summary",
        )
        modality_summaries = [camera_summary, imu_summary]

        predictions = {
            "visual_single": camera_reports[0].value,
            "visual_five_median": median_value(camera_reports),
            "visual_five_freshness": freshness_weighted_value(camera_reports),
            "hierarchy_median": median_value(modality_summaries),
            "hierarchy_freshness": freshness_weighted_value(modality_summaries),
        }
        for key, prediction in predictions.items():
            errors[key] += abs(prediction - truth)

    return {key: value / trials for key, value in errors.items()}


def main() -> None:
    print(
        "stall_prob,visual_single,visual_five_median,visual_five_freshness,"
        "hierarchy_median,hierarchy_freshness"
    )
    for stall_probability in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
        result = run_condition(stall_probability)
        values = ",".join(f"{result[key]:.6f}" for key in result)
        print(f"{stall_probability:.1f},{values}")


if __name__ == "__main__":
    main()
