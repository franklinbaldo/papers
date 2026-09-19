"""Run 9: test greedy learned marginal recruitment of sensor specialists.

The allocator starts from two lawful pilot reports per modality and allocates eight
more specialist slots one at a time. Its decision features are entirely derived
from reports already available at that point plus the current budget state.
Hidden synthetic truth is used only after a training action to score its delayed
one-step marginal reward, never as a decision-time input.
"""

from __future__ import annotations

import random

from colony import allocate_recruitment_slots
from colony_continuous_context_ablation import _predict, _sample
from marginal_recruitment import marginal_recruitment_features
from recruitment_bandit import LinearContextualPolicy

ACTIONS = ("camera", "imu")
FEATURE_DIM = 13


def _loss(truth, camera, imu, camera_count, imu_count):
    return abs(_predict(camera, imu, camera_count, imu_count) - truth)


def train_marginal(*, steps=60_000, seed=20260919):
    """Learn one-step marginal value from randomized reachable budget states."""

    policy = LinearContextualPolicy(ACTIONS, feature_dim=FEATURE_DIM, ridge=0.2)
    rng = random.Random(seed)
    for _ in range(steps):
        truth, camera, imu = _sample(rng, age_profile="uniform")

        # Sample a reachable state after 0..7 of the eight extra slots.
        used_extra = rng.randrange(0, 8)
        min_camera_extra = max(0, used_extra - 6)
        max_camera_extra = min(6, used_extra)
        camera_extra = rng.randint(min_camera_extra, max_camera_extra)
        imu_extra = used_extra - camera_extra
        camera_count = 2 + camera_extra
        imu_count = 2 + imu_extra

        available = []
        if camera_count < 8:
            available.append("camera")
        if imu_count < 8:
            available.append("imu")
        action = rng.choice(available)

        features = marginal_recruitment_features(
            camera[:camera_count],
            imu[:imu_count],
            primary_count=camera_count,
            secondary_count=imu_count,
        )
        before = _loss(truth, camera, imu, camera_count, imu_count)
        if action == "camera":
            after = _loss(truth, camera, imu, camera_count + 1, imu_count)
        else:
            after = _loss(truth, camera, imu, camera_count, imu_count + 1)

        # Positive reward means that the newly recruited specialist reduced error.
        policy.observe(action, features, before - after)

    policy.fit()
    return policy


def sequential_allocation(policy, camera, imu):
    camera_count = 2
    imu_count = 2
    for _ in range(8):
        features = marginal_recruitment_features(
            camera[:camera_count],
            imu[:imu_count],
            primary_count=camera_count,
            secondary_count=imu_count,
        )
        available = []
        if camera_count < 8:
            available.append("camera")
        if imu_count < 8:
            available.append("imu")
        action = max(
            available,
            key=lambda candidate: (
                policy.predict_reward(candidate, features),
                candidate,
            ),
        )
        if action == "camera":
            camera_count += 1
        else:
            imu_count += 1
    return camera_count, imu_count


def _final_allocation_oracle(truth, camera, imu):
    """Evaluation-only clairvoyant lower bound over matched 12-specialist splits."""

    choices = [
        (_loss(truth, camera, imu, camera_count, 12 - camera_count), camera_count)
        for camera_count in range(4, 9)
    ]
    best_loss, camera_count = min(choices)
    return best_loss, camera_count, 12 - camera_count


def _marginal_diagnostic(*, steps=40_000, seed=20260919):
    """Measure how often one more specialist helps at randomized reachable states."""

    rng = random.Random(seed)
    stats = {
        "camera": {"n": 0, "worse": 0, "delta": 0.0},
        "imu": {"n": 0, "worse": 0, "delta": 0.0},
    }
    for _ in range(steps):
        truth, camera, imu = _sample(rng, age_profile="uniform")
        used_extra = rng.randrange(0, 8)
        min_camera_extra = max(0, used_extra - 6)
        max_camera_extra = min(6, used_extra)
        camera_extra = rng.randint(min_camera_extra, max_camera_extra)
        imu_extra = used_extra - camera_extra
        camera_count = 2 + camera_extra
        imu_count = 2 + imu_extra
        before = _loss(truth, camera, imu, camera_count, imu_count)

        for action in ACTIONS:
            if action == "camera" and camera_count >= 8:
                continue
            if action == "imu" and imu_count >= 8:
                continue
            if action == "camera":
                after = _loss(truth, camera, imu, camera_count + 1, imu_count)
            else:
                after = _loss(truth, camera, imu, camera_count, imu_count + 1)
            delta = before - after
            stats[action]["n"] += 1
            stats[action]["worse"] += int(delta < 0.0)
            stats[action]["delta"] += delta
    return stats


def evaluate(marginal_policy, age_profile, *, steps=10_000, seed=20260919):
    offsets = {"uniform": 51, "fresh_skew": 52, "stale_skew": 53}
    rng = random.Random(seed + offsets[age_profile])
    totals = {
        "fixed_4_8": 0.0,
        "stateless_dynamic": 0.0,
        "learned_marginal": 0.0,
        "final_allocation_oracle": 0.0,
    }
    marginal_camera_total = 0
    oracle_camera_total = 0

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

        camera_count, imu_count = sequential_allocation(marginal_policy, camera, imu)
        totals["learned_marginal"] += _loss(
            truth, camera, imu, camera_count, imu_count
        )
        marginal_camera_total += camera_count

        oracle_loss, oracle_camera, _ = _final_allocation_oracle(truth, camera, imu)
        totals["final_allocation_oracle"] += oracle_loss
        oracle_camera_total += oracle_camera

    return (
        {name: total / steps for name, total in totals.items()},
        marginal_camera_total / steps,
        oracle_camera_total / steps,
    )


def main():
    marginal_policy = train_marginal()
    diagnostics = _marginal_diagnostic()
    print("diagnostic,action,worsen_fraction,mean_one_step_improvement")
    for action in ACTIONS:
        item = diagnostics[action]
        print(
            f"marginal,{action},{item['worse'] / item['n']:.6f},"
            f"{item['delta'] / item['n']:.6f}"
        )

    print(
        "profile,fixed_4_8,stateless_dynamic,learned_marginal,"
        "final_allocation_oracle,marginal_camera_count,oracle_camera_count"
    )
    for profile in ("uniform", "fresh_skew", "stale_skew"):
        result, marginal_camera_count, oracle_camera_count = evaluate(
            marginal_policy, profile
        )
        print(
            f"{profile},{result['fixed_4_8']:.6f},"
            f"{result['stateless_dynamic']:.6f},"
            f"{result['learned_marginal']:.6f},"
            f"{result['final_allocation_oracle']:.6f},"
            f"{marginal_camera_count:.3f},{oracle_camera_count:.3f}"
        )


if __name__ == "__main__":
    main()
