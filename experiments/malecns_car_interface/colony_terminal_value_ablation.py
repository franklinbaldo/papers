"""Run 10: train specialist recruitment on delayed terminal value.

Run 9 used the immediate error change caused by one newly recruited specialist.
This harness instead assigns an action the final loss after the rest of the
12-specialist budget is spent by a fixed randomized continuation policy. Hidden
synthetic truth is used only after the complete allocation to score delayed
terminal reward; it is never a decision-time feature.
"""

from __future__ import annotations

import random

from colony import allocate_recruitment_slots
from colony_continuous_context_ablation import _predict, _sample
from colony_marginal_recruitment_ablation import train_marginal
from marginal_recruitment import marginal_recruitment_features
from recruitment_bandit import LinearContextualPolicy

ACTIONS = ("camera", "imu")
FEATURE_DIM = 13


def _loss(truth, camera, imu, camera_count, imu_count):
    return abs(_predict(camera, imu, camera_count, imu_count) - truth)


def _available_actions(camera_count, imu_count):
    available = []
    if camera_count < 8:
        available.append("camera")
    if imu_count < 8:
        available.append("imu")
    return available


def _apply(action, camera_count, imu_count):
    if action == "camera":
        return camera_count + 1, imu_count
    if action == "imu":
        return camera_count, imu_count + 1
    raise ValueError(f"unknown action: {action}")


def _random_continuation(rng, camera_count, imu_count):
    """Spend the remaining budget without inspecting hidden truth."""

    while camera_count + imu_count < 12:
        action = rng.choice(_available_actions(camera_count, imu_count))
        camera_count, imu_count = _apply(action, camera_count, imu_count)
    return camera_count, imu_count


def train_terminal(*, steps=120_000, seed=20260919):
    """Learn Q(action, lawful state) from delayed final allocation loss."""

    policy = LinearContextualPolicy(ACTIONS, feature_dim=FEATURE_DIM, ridge=0.2)
    rng = random.Random(seed + 101)
    for _ in range(steps):
        truth, camera, imu = _sample(rng, age_profile="uniform")

        used_extra = rng.randrange(0, 8)
        min_camera_extra = max(0, used_extra - 6)
        max_camera_extra = min(6, used_extra)
        camera_extra = rng.randint(min_camera_extra, max_camera_extra)
        imu_extra = used_extra - camera_extra
        camera_count = 2 + camera_extra
        imu_count = 2 + imu_extra

        action = rng.choice(_available_actions(camera_count, imu_count))
        features = marginal_recruitment_features(
            camera[:camera_count],
            imu[:imu_count],
            primary_count=camera_count,
            secondary_count=imu_count,
        )

        camera_count, imu_count = _apply(action, camera_count, imu_count)
        camera_count, imu_count = _random_continuation(
            rng, camera_count, imu_count
        )
        policy.observe(
            action,
            features,
            -_loss(truth, camera, imu, camera_count, imu_count),
        )

    policy.fit()
    return policy


def sequential_allocation(policy, camera, imu):
    """Spend eight extra slots using only current lawful reports and budget state."""

    camera_count = 2
    imu_count = 2
    while camera_count + imu_count < 12:
        features = marginal_recruitment_features(
            camera[:camera_count],
            imu[:imu_count],
            primary_count=camera_count,
            secondary_count=imu_count,
        )
        available = _available_actions(camera_count, imu_count)
        action = max(
            available,
            key=lambda candidate: (
                policy.predict_reward(candidate, features),
                candidate,
            ),
        )
        camera_count, imu_count = _apply(action, camera_count, imu_count)
    return camera_count, imu_count


def _final_allocation_oracle(truth, camera, imu):
    choices = [
        (_loss(truth, camera, imu, camera_count, 12 - camera_count), camera_count)
        for camera_count in range(4, 9)
    ]
    best_loss, camera_count = min(choices)
    return best_loss, camera_count, 12 - camera_count


def evaluate(
    terminal_policy,
    marginal_policy,
    age_profile,
    *,
    steps=30_000,
    seed=20260919,
):
    offsets = {"uniform": 901, "fresh_skew": 902, "stale_skew": 903}
    rng = random.Random(seed + offsets[age_profile])
    totals = {
        "fixed_4_8": 0.0,
        "stateless_dynamic": 0.0,
        "one_step_marginal": 0.0,
        "terminal_value": 0.0,
        "final_allocation_oracle": 0.0,
    }
    marginal_camera_total = 0
    terminal_camera_total = 0

    for _ in range(steps):
        truth, camera, imu = _sample(rng, age_profile=age_profile)
        totals["fixed_4_8"] += _loss(truth, camera, imu, 4, 8)

        allocation = allocate_recruitment_slots(
            {"camera": camera[:2], "imu": imu[:2]}, extra_slots=8
        )
        totals["stateless_dynamic"] += _loss(
            truth,
            camera,
            imu,
            2 + allocation["camera"],
            2 + allocation["imu"],
        )

        camera_count, imu_count = sequential_allocation(
            marginal_policy, camera, imu
        )
        totals["one_step_marginal"] += _loss(
            truth, camera, imu, camera_count, imu_count
        )
        marginal_camera_total += camera_count

        camera_count, imu_count = sequential_allocation(
            terminal_policy, camera, imu
        )
        totals["terminal_value"] += _loss(
            truth, camera, imu, camera_count, imu_count
        )
        terminal_camera_total += camera_count

        oracle_loss, _, _ = _final_allocation_oracle(truth, camera, imu)
        totals["final_allocation_oracle"] += oracle_loss

    return (
        {name: total / steps for name, total in totals.items()},
        marginal_camera_total / steps,
        terminal_camera_total / steps,
    )


def main():
    marginal_policy = train_marginal()
    terminal_policy = train_terminal()
    print(
        "profile,fixed_4_8,stateless_dynamic,one_step_marginal,terminal_value,"
        "final_allocation_oracle,one_step_camera_count,terminal_camera_count"
    )
    for profile in ("uniform", "fresh_skew", "stale_skew"):
        result, marginal_camera_count, terminal_camera_count = evaluate(
            terminal_policy, marginal_policy, profile
        )
        print(
            f"{profile},{result['fixed_4_8']:.6f},"
            f"{result['stateless_dynamic']:.6f},"
            f"{result['one_step_marginal']:.6f},"
            f"{result['terminal_value']:.6f},"
            f"{result['final_allocation_oracle']:.6f},"
            f"{marginal_camera_count:.3f},{terminal_camera_count:.3f}"
        )


if __name__ == "__main__":
    main()
