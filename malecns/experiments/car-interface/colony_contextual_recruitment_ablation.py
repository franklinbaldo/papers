"""Deterministic learned policy-selection ablation for specialist recruitment.

Decision-time inputs are reality-bounded specialist reports only. The synthetic
harness uses latent truth solely to supply a delayed training/evaluation loss;
that truth never appears in the context given to the selector.
"""

from __future__ import annotations

import random

from colony import (
    SpecialistReport,
    allocate_recruitment_slots,
    freshness_weighted_value,
    summarize_modality,
)
from recruitment_bandit import ContextualPolicyBandit, freshness_context

ACTIONS = ("fixed_imu_heavy", "stateless_dynamic")


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


def _sample(rng, stall_probability):
    truth = rng.uniform(-1.0, 1.0)
    velocity = rng.uniform(-3.0, 3.0)
    stalled = rng.random() < stall_probability
    camera_age_ms = rng.uniform(450.0, 900.0) if stalled else rng.uniform(20.0, 60.0)
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
    return truth, camera, imu, freshness_context(camera[:2])


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


def train(*, steps=20_000, stall_probability=0.5, seed=20260918):
    bandit = ContextualPolicyBandit(ACTIONS, epsilon=0.10, seed=seed)
    rng = random.Random(seed + 1)
    for _ in range(steps):
        truth, camera, imu, context = _sample(rng, stall_probability)
        action = bandit.select(context)
        bandit.update(context, action, -_loss(action, truth, camera, imu))
    return bandit


def evaluate(bandit, stall_probability, *, steps=30_000, seed=20260918):
    rng = random.Random(seed + 2 + int(stall_probability * 1000))
    totals = {"fixed_imu_heavy": 0.0, "stateless_dynamic": 0.0, "contextual_bandit": 0.0}
    context_counts = {"fresh": 0, "stale": 0}
    for _ in range(steps):
        truth, camera, imu, context = _sample(rng, stall_probability)
        context_counts[context] += 1
        totals["fixed_imu_heavy"] += _loss("fixed_imu_heavy", truth, camera, imu)
        totals["stateless_dynamic"] += _loss("stateless_dynamic", truth, camera, imu)
        totals["contextual_bandit"] += _loss(bandit.best_action(context), truth, camera, imu)
    return {name: total / steps for name, total in totals.items()}, context_counts


def main():
    bandit = train()
    print("learned_fresh," + bandit.best_action("fresh"))
    print("learned_stale," + bandit.best_action("stale"))
    print("stall_prob,fixed_imu_heavy,stateless_dynamic,contextual_bandit,fresh_n,stale_n")
    for stall_probability in (0.2, 0.5, 0.8):
        result, counts = evaluate(bandit, stall_probability)
        print(
            f"{stall_probability:.1f},{result['fixed_imu_heavy']:.6f},"
            f"{result['stateless_dynamic']:.6f},{result['contextual_bandit']:.6f},"
            f"{counts['fresh']},{counts['stale']}"
        )


if __name__ == "__main__":
    main()
