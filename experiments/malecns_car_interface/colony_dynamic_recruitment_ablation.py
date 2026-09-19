"""Deterministic fixed-budget dynamic-recruitment ablation for a MaleCNS colony.

The allocator never sees ground truth, realized error, or a hidden sensor-fault flag.
It observes only pilot specialist reports from lawful reality-bounded modalities.
Within-modality disagreement asks whether more independently trained specialists
might reduce cognitive/inference noise; report age prevents wasting compute on a
commonly stale physical stream.
"""

from __future__ import annotations

import random

from colony import SpecialistReport, allocate_recruitment_slots, freshness_weighted_value, summarize_modality


def _make_reports(rng, *, modality, truth, velocity, count, base_age_ms):
    reports = []
    for index in range(count):
        if modality == "camera":
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
        reports.append(SpecialistReport(f"{modality}-{index}", "dynamic-scalar", value, confidence, age_ms=age_ms, modality=modality))
    return reports


def _predict(camera_reports, imu_reports, *, camera_count, imu_count):
    camera_summary = summarize_modality(camera_reports[:camera_count], specialist_id="camera-summary")
    imu_summary = summarize_modality(imu_reports[:imu_count], specialist_id="imu-summary")
    return freshness_weighted_value([camera_summary, imu_summary])


def run_condition(stall_probability, *, trials=10_000, seed=20260918):
    rng = random.Random(seed + int(stall_probability * 1000))
    errors = {name: 0.0 for name in ("camera_heavy_8_4", "balanced_6_6", "imu_heavy_4_8", "dynamic")}
    extra_camera = 0
    extra_imu = 0
    for _ in range(trials):
        truth = rng.uniform(-1.0, 1.0)
        velocity = rng.uniform(-3.0, 3.0)
        camera_stalled = rng.random() < stall_probability
        camera_base_age_ms = rng.uniform(450.0, 900.0) if camera_stalled else rng.uniform(20.0, 60.0)
        camera_reports = _make_reports(rng, modality="camera", truth=truth, velocity=velocity, count=8, base_age_ms=camera_base_age_ms)
        imu_reports = _make_reports(rng, modality="imu", truth=truth, velocity=velocity, count=8, base_age_ms=None)
        allocation = allocate_recruitment_slots({"camera": camera_reports[:2], "imu": imu_reports[:2]}, extra_slots=8)
        extra_camera += allocation["camera"]
        extra_imu += allocation["imu"]
        policies = {
            "camera_heavy_8_4": (8, 4),
            "balanced_6_6": (6, 6),
            "imu_heavy_4_8": (4, 8),
            "dynamic": (2 + allocation["camera"], 2 + allocation["imu"]),
        }
        for name, (camera_count, imu_count) in policies.items():
            prediction = _predict(camera_reports, imu_reports, camera_count=camera_count, imu_count=imu_count)
            errors[name] += abs(prediction - truth)
    result = {name: total / trials for name, total in errors.items()}
    result["mean_extra_camera"] = extra_camera / trials
    result["mean_extra_imu"] = extra_imu / trials
    return result


def main():
    print("stall_prob,camera_heavy_8_4,balanced_6_6,imu_heavy_4_8,dynamic,mean_extra_camera,mean_extra_imu")
    for stall_probability in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
        result = run_condition(stall_probability)
        print(f"{stall_probability:.1f},{result['camera_heavy_8_4']:.6f},{result['balanced_6_6']:.6f},{result['imu_heavy_4_8']:.6f},{result['dynamic']:.6f},{result['mean_extra_camera']:.4f},{result['mean_extra_imu']:.4f}")


if __name__ == "__main__":
    main()
