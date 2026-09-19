"""Continuous-context recruitment ablation for the MaleCNS sensor colony.

The learned selector sees only lawful specialist-report features. Hidden truth is
used by this synthetic harness only after the allocation decision to compute a
delayed training/evaluation loss.
"""

from __future__ import annotations

import random
from statistics import median

from colony import (
    SpecialistReport,
    allocate_recruitment_slots,
    freshness_weighted_value,
    summarize_modality,
)
from recruitment_bandit import LinearContextualPolicy, continuous_context_features

ACTIONS = ("fixed_imu_heavy", "stateless_dynamic")
FEATURE_DIM = 10


def _make_reports(rng, *, modality, truth, velocity, count, base_age_ms=None):
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
        reports.append(
            SpecialistReport(
                f"{modality}-{index}",
                "dynamic-scalar",
                value,
                confidence,
                age_ms=age_ms,
                modality=modality,
            )
        )
    return reports


def _sample(rng, *, age_profile):
    truth = rng.uniform(-1.0, 1.0)
    velocity = rng.uniform(-3.0, 3.0)
    u = rng.random()
    if age_profile == "uniform":
        camera_age_ms = 20.0 + 880.0 * u
    elif age_profile == "fresh_skew":
        camera_age_ms = 20.0 + 880.0 * (u**2)
    elif age_profile == "stale_skew":
        camera_age_ms = 20.0 + 880.0 * (u**0.5)
    else:
        raise ValueError(f"unknown age profile: {age_profile}")

    camera = _make_reports(
        rng,
        modality="camera",
        truth=truth,
        velocity=velocity,
        count=8,
        base_age_ms=camera_age_ms,
    )
    imu = _make_reports(
        rng,
        modality="imu",
        truth=truth,
        velocity=velocity,
        count=8,
    )
    return truth, camera, imu


def _predict(camera, imu, camera_count, imu_count):
    camera_summary = summarize_modality(camera[:camera_count], specialist_id="camera-summary")
    imu_summary = summarize_modality(imu[:imu_count], specialist_id="imu-summary")
    return freshness_weighted_value([camera_summary, imu_summary])


def _loss(action, truth, camera, imu):
    if action == "fixed_imu_heavy":
        camera_count, imu_count = 4, 8
    elif action == "stateless_dynamic":
        allocation = allocate_recruitment_slots(
            {"camera": camera[:2], "imu": imu[:2]},
            extra_slots=8,
        )
        camera_count = 2 + allocation["camera"]
        imu_count = 2 + allocation["imu"]
    else:
        raise ValueError(f"unknown action: {action}")
    return abs(_predict(camera, imu, camera_count, imu_count) - truth)


def train(*, steps=200_000, seed=20260919):
    """Fit from randomized actions so every reward is delayed and on-policy lawful."""

    policy = LinearContextualPolicy(ACTIONS, feature_dim=FEATURE_DIM, ridge=0.1)
    rng = random.Random(seed)
    for _ in range(steps):
        truth, camera, imu = _sample(rng, age_profile="uniform")
        features = continuous_context_features(camera[:2], imu[:2])
        action = rng.choice(ACTIONS)
        policy.observe(action, features, -_loss(action, truth, camera, imu))
    policy.fit()
    return policy


def evaluate(policy, age_profile, *, steps=30_000, seed=20260919):
    profile_offsets = {"uniform": 1, "fresh_skew": 2, "stale_skew": 3}
    rng = random.Random(seed + profile_offsets[age_profile])
    totals = {
        "fixed_imu_heavy": 0.0,
        "stateless_dynamic": 0.0,
        "discrete_150": 0.0,
        "linear_context": 0.0,
        "oracle": 0.0,
    }
    choices = {action: 0 for action in ACTIONS}

    for _ in range(steps):
        truth, camera, imu = _sample(rng, age_profile=age_profile)
        fixed_loss = _loss("fixed_imu_heavy", truth, camera, imu)
        dynamic_loss = _loss("stateless_dynamic", truth, camera, imu)
        features = continuous_context_features(camera[:2], imu[:2])
        learned_action = policy.select(features)
        choices[learned_action] += 1

        camera_age_ms = float(median(report.age_ms for report in camera[:2]))
        discrete_action = (
            "fixed_imu_heavy" if camera_age_ms <= 150.0 else "stateless_dynamic"
        )

        totals["fixed_imu_heavy"] += fixed_loss
        totals["stateless_dynamic"] += dynamic_loss
        totals["discrete_150"] += (
            fixed_loss if discrete_action == "fixed_imu_heavy" else dynamic_loss
        )
        totals["linear_context"] += (
            fixed_loss if learned_action == "fixed_imu_heavy" else dynamic_loss
        )
        totals["oracle"] += min(fixed_loss, dynamic_loss)

    return {name: total / steps for name, total in totals.items()}, choices


def main():
    policy = train()
    print(
        "profile,fixed_imu_heavy,stateless_dynamic,discrete_150,"
        "linear_context,oracle,learned_fixed_n,learned_dynamic_n"
    )
    for profile in ("uniform", "fresh_skew", "stale_skew"):
        result, choices = evaluate(policy, profile)
        print(
            f"{profile},{result['fixed_imu_heavy']:.6f},"
            f"{result['stateless_dynamic']:.6f},{result['discrete_150']:.6f},"
            f"{result['linear_context']:.6f},{result['oracle']:.6f},"
            f"{choices['fixed_imu_heavy']},{choices['stateless_dynamic']}"
        )


if __name__ == "__main__":
    main()
