"""Run 13: compare hard trust gates with a soft bounded-influence baseline.

The soft baseline is intentionally simpler than the Run-12 learned gate. It never
uses hidden simulator truth, fault flags or privileged state. Every paid probe is
retained, but its influence is smoothly shrunk using only confidence, freshness and
cross-modal residuals. Its one scale parameter is calibrated against a delayed
independent corroborating measurement, not hidden-truth MAE.
"""

from __future__ import annotations

import random
from statistics import mean, stdev

from colony_continuous_context_ablation import _predict, _sample
from colony_delayed_trust_ablation import (
    DEFAULT_FAULT_PROBABILITY,
    FIXED_GATE_THRESHOLD,
    PROFILE_OFFSETS,
    _delayed_corroboration,
    _inject_specialist_fault,
)
from delayed_trust import DelayedTrustModel, delayed_trust_features
from probe_trust import should_trust_probe
from soft_trust import soften_probe

RUN12_THRESHOLD = 0.20
RUN12_WEIGHTS = (
    -0.556652302,
    0.015637646,
    0.417766738,
    0.853379985,
    -1.091529353,
    -0.536889066,
    -6.645120574,
    0.368008312,
    -0.216254525,
    0.706676814,
    3.858181588,
)
SOFT_SCALE_GRID = (0.10, 0.15, 0.22, 0.33, 0.50, 0.75)
CALIBRATION_EPISODES = 3_000
PRIMARY_EVALUATION_STEPS = 5_000
SHIFT_EVALUATION_STEPS = 3_000


def run12_model() -> DelayedTrustModel:
    """Reconstruct the frozen Run-12 learned gate for a matched comparison."""

    model = DelayedTrustModel()
    model.weights[:] = RUN12_WEIGHTS
    return model


def _episode(
    rng,
    *,
    age_profile,
    model,
    soft_scale,
    fault_probability=DEFAULT_FAULT_PROBABILITY,
    correlated_camera_probability=0.0,
):
    truth, camera, imu = _sample(rng, age_profile=age_profile)
    pilot_prediction = _predict(camera, imu, 2, 2)

    always_camera = list(camera[:2])
    always_imu = list(imu[:2])
    fixed_camera = list(camera[:2])
    fixed_imu = list(imu[:2])
    learned_camera = list(camera[:2])
    learned_imu = list(imu[:2])
    soft_camera = list(camera[:2])
    soft_imu = list(imu[:2])

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

        always_camera.append(camera_candidate)
        always_imu.append(imu_candidate)

        if should_trust_probe(
            fixed_camera,
            camera_candidate,
            fixed_imu,
            threshold=FIXED_GATE_THRESHOLD,
        ):
            fixed_camera.append(camera_candidate)
        if should_trust_probe(
            fixed_imu,
            imu_candidate,
            fixed_camera,
            threshold=FIXED_GATE_THRESHOLD,
        ):
            fixed_imu.append(imu_candidate)

        camera_features = delayed_trust_features(
            learned_camera,
            camera_candidate,
            learned_imu,
        )
        if model.should_trust(camera_features, threshold=RUN12_THRESHOLD):
            learned_camera.append(camera_candidate)

        imu_features = delayed_trust_features(
            learned_imu,
            imu_candidate,
            learned_camera,
        )
        if model.should_trust(imu_features, threshold=RUN12_THRESHOLD):
            learned_imu.append(imu_candidate)

        soft_camera.append(
            soften_probe(
                soft_camera,
                camera_candidate,
                soft_imu,
                residual_scale=soft_scale,
            )
        )
        soft_imu.append(
            soften_probe(
                soft_imu,
                imu_candidate,
                soft_camera,
                residual_scale=soft_scale,
            )
        )

    predictions = {
        "pilot_only": pilot_prediction,
        "always_trust": _predict(
            always_camera,
            always_imu,
            len(always_camera),
            len(always_imu),
        ),
        "fixed_gate": _predict(
            fixed_camera,
            fixed_imu,
            len(fixed_camera),
            len(fixed_imu),
        ),
        "learned_gate": _predict(
            learned_camera,
            learned_imu,
            len(learned_camera),
            len(learned_imu),
        ),
        "soft_robust": _predict(
            soft_camera,
            soft_imu,
            len(soft_camera),
            len(soft_imu),
        ),
    }
    delayed_confirmation = _delayed_corroboration(rng, truth)
    result = {name: abs(value - truth) for name, value in predictions.items()}
    result["soft_delayed_loss"] = abs(
        predictions["soft_robust"] - delayed_confirmation
    )
    return result


def calibrate_soft_scale(
    model,
    *,
    episodes=CALIBRATION_EPISODES,
    seed=2026091914,
):
    """Select residual scale using delayed sensor loss, never hidden-truth MAE."""

    choices = []
    for scale in SOFT_SCALE_GRID:
        rng = random.Random(seed)
        total = 0.0
        for _ in range(episodes):
            total += _episode(
                rng,
                age_profile="uniform",
                model=model,
                soft_scale=scale,
            )["soft_delayed_loss"]
        choices.append((total / episodes, scale))
    return min(choices)


def _aggregate(rows):
    names = ("pilot_only", "always_trust", "fixed_gate", "learned_gate", "soft_robust")
    return {
        name: (
            mean(row[name] for row in rows),
            stdev(row[name] for row in rows),
        )
        for name in names
    }


def evaluate_condition(
    model,
    soft_scale,
    *,
    age_profile,
    fault_probability=DEFAULT_FAULT_PROBABILITY,
    correlated_camera_probability=0.0,
    steps=PRIMARY_EVALUATION_STEPS,
    base_seed=2026091950,
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
            "pilot_only": 0.0,
            "always_trust": 0.0,
            "fixed_gate": 0.0,
            "learned_gate": 0.0,
            "soft_robust": 0.0,
        }
        for _ in range(steps):
            result = _episode(
                rng,
                age_profile=age_profile,
                model=model,
                soft_scale=soft_scale,
                fault_probability=fault_probability,
                correlated_camera_probability=correlated_camera_probability,
            )
            for name in totals:
                totals[name] += result[name]
        rows.append({name: total / steps for name, total in totals.items()})
    return _aggregate(rows)


def main():
    model = run12_model()
    calibration_loss, soft_scale = calibrate_soft_scale(model)
    print(
        f"soft_scale={soft_scale:.2f},"
        f"calibration_delayed_loss={calibration_loss:.6f}"
    )
    print("profile,pilot,always,fixed,learned,soft")
    for profile in ("uniform", "fresh_skew", "stale_skew"):
        result = evaluate_condition(model, soft_scale, age_profile=profile)
        print(
            f"{profile},{result['pilot_only'][0]:.6f},"
            f"{result['always_trust'][0]:.6f},{result['fixed_gate'][0]:.6f},"
            f"{result['learned_gate'][0]:.6f},{result['soft_robust'][0]:.6f}"
        )

    print("fault_probability,pilot,fixed,learned,soft")
    for probability in (0.0, 0.1, 0.2, 0.3):
        result = evaluate_condition(
            model,
            soft_scale,
            age_profile="uniform",
            fault_probability=probability,
            steps=SHIFT_EVALUATION_STEPS,
            base_seed=2026091970,
        )
        print(
            f"{probability:.1f},{result['pilot_only'][0]:.6f},"
            f"{result['fixed_gate'][0]:.6f},{result['learned_gate'][0]:.6f},"
            f"{result['soft_robust'][0]:.6f}"
        )

    print("correlated_camera_probability,pilot,always,fixed,learned,soft")
    for probability in (0.1, 0.3, 0.5):
        result = evaluate_condition(
            model,
            soft_scale,
            age_profile="uniform",
            fault_probability=0.1,
            correlated_camera_probability=probability,
            steps=SHIFT_EVALUATION_STEPS,
            base_seed=2026091980,
        )
        print(
            f"{probability:.1f},{result['pilot_only'][0]:.6f},"
            f"{result['always_trust'][0]:.6f},{result['fixed_gate'][0]:.6f},"
            f"{result['learned_gate'][0]:.6f},{result['soft_robust'][0]:.6f}"
        )


if __name__ == "__main__":
    main()
