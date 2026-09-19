"""Run 12: learn probe admission from delayed physical corroboration.

A tiny logistic gate sees only decision-time report features. Its training label
arrives after the decision from an independent corroborating measurement that is
intended to stand for a real-car channel such as IMU/OBD/GNSS cross-confirmation.
Synthetic hidden truth is used by the harness only to generate sensor samples and
to score evaluation MAE; it is never a gate feature or training label.
"""

from __future__ import annotations

from dataclasses import replace
import random
from statistics import mean, stdev

from colony_continuous_context_ablation import _predict, _sample
from delayed_trust import DelayedTrustModel, delayed_trust_features
from probe_trust import should_trust_probe

TRAIN_EPISODES = 80_000
CALIBRATION_EPISODES = 12_000
PRIMARY_EVALUATION_STEPS = 10_000
SHIFT_EVALUATION_STEPS = 5_000
DEFAULT_FAULT_PROBABILITY = 0.20
FIXED_GATE_THRESHOLD = 0.12
LEARNED_THRESHOLD_GRID = tuple(index / 100.0 for index in range(10, 51, 2))
PROFILE_OFFSETS = {"uniform": 0, "fresh_skew": 1_000, "stale_skew": 2_000}


def _inject_specialist_fault(
    rng,
    report,
    *,
    probability,
    shared_bias=None,
):
    """Inject an unobserved high-confidence fault for robustness testing."""

    if shared_bias is not None:
        return replace(report, value=report.value + shared_bias, confidence=0.95)
    if rng.random() >= probability:
        return report
    bias = rng.choice((-1.0, 1.0)) * rng.uniform(0.6, 1.4)
    return replace(report, value=report.value + bias, confidence=0.95)


def _delayed_corroboration(rng, truth):
    """Emulate a later independent real-car-compatible scalar measurement.

    The learner receives only the sampled corroboration, never `truth`. A real
    deployment would bind this to a compatible independent channel, for example
    camera ego-motion checked against IMU yaw or visual speed checked against
    OBD/GNSS speed.
    """

    return truth + rng.gauss(0.0, 0.10)


def train_delayed_gate(
    *,
    episodes=TRAIN_EPISODES,
    seed=2026091912,
    fault_probability=DEFAULT_FAULT_PROBABILITY,
    corroboration_tolerance=0.30,
):
    """Train online from delayed independent corroboration, never hidden truth."""

    rng = random.Random(seed)
    model = DelayedTrustModel()
    for _ in range(episodes):
        truth, camera, imu = _sample(rng, age_profile="uniform")
        trusted_camera = list(camera[:2])
        trusted_imu = list(imu[:2])

        for raw_camera, raw_imu in zip(camera[2:6], imu[2:6]):
            for modality, raw_candidate in (
                ("camera", raw_camera),
                ("imu", raw_imu),
            ):
                candidate = _inject_specialist_fault(
                    rng,
                    raw_candidate,
                    probability=fault_probability,
                )
                if modality == "camera":
                    existing, other = trusted_camera, trusted_imu
                else:
                    existing, other = trusted_imu, trusted_camera

                features = delayed_trust_features(existing, candidate, other)
                # This measurement arrives only after the decision-time features
                # have been frozen. It is a sensor-derived teacher, not truth.
                corroboration = _delayed_corroboration(rng, truth)
                label = float(
                    abs(candidate.value - corroboration) <= corroboration_tolerance
                )
                model.update(features, label)

                # Keep the sequential training state reality-bounded too.
                if model.should_trust(features, threshold=0.50):
                    existing.append(candidate)
    return model


def _episode(
    rng,
    *,
    age_profile,
    model,
    learned_threshold,
    fault_probability=DEFAULT_FAULT_PROBABILITY,
    correlated_camera_probability=0.0,
):
    truth, camera, imu = _sample(rng, age_profile=age_profile)

    fixed_camera = list(camera[:2])
    fixed_imu = list(imu[:2])
    learned_camera = list(camera[:2])
    learned_imu = list(imu[:2])
    always_camera = list(camera[:2])
    always_imu = list(imu[:2])

    # Draw this even when probability is zero so seeded runs have one stable RNG
    # contract across the correlated-failure ablation.
    shared_camera_bias = None
    if rng.random() < correlated_camera_probability:
        shared_camera_bias = rng.choice((-1.0, 1.0)) * rng.uniform(0.6, 1.4)

    fixed_accepted = 0
    learned_accepted = 0
    probes = 0

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
        probes += 2

        if should_trust_probe(
            fixed_camera,
            camera_candidate,
            fixed_imu,
            threshold=FIXED_GATE_THRESHOLD,
        ):
            fixed_camera.append(camera_candidate)
            fixed_accepted += 1
        if should_trust_probe(
            fixed_imu,
            imu_candidate,
            fixed_camera,
            threshold=FIXED_GATE_THRESHOLD,
        ):
            fixed_imu.append(imu_candidate)
            fixed_accepted += 1

        camera_features = delayed_trust_features(
            learned_camera,
            camera_candidate,
            learned_imu,
        )
        if model.should_trust(camera_features, threshold=learned_threshold):
            learned_camera.append(camera_candidate)
            learned_accepted += 1

        imu_features = delayed_trust_features(
            learned_imu,
            imu_candidate,
            learned_camera,
        )
        if model.should_trust(imu_features, threshold=learned_threshold):
            learned_imu.append(imu_candidate)
            learned_accepted += 1

    always_prediction = _predict(
        always_camera,
        always_imu,
        len(always_camera),
        len(always_imu),
    )
    fixed_prediction = _predict(
        fixed_camera,
        fixed_imu,
        len(fixed_camera),
        len(fixed_imu),
    )
    learned_prediction = _predict(
        learned_camera,
        learned_imu,
        len(learned_camera),
        len(learned_imu),
    )

    # A second independent measurement can be used for lawful threshold
    # calibration. Hidden truth remains evaluation-only.
    delayed_confirmation = _delayed_corroboration(rng, truth)
    return {
        "always_trust": abs(always_prediction - truth),
        "fixed_gate": abs(fixed_prediction - truth),
        "learned_gate": abs(learned_prediction - truth),
        "learned_delayed_loss": abs(learned_prediction - delayed_confirmation),
        "fixed_acceptance": fixed_accepted / probes,
        "learned_acceptance": learned_accepted / probes,
    }


def calibrate_threshold(
    model,
    *,
    episodes=CALIBRATION_EPISODES,
    seed=2026091913,
):
    """Pick a threshold using delayed sensor loss, not hidden truth MAE."""

    choices = []
    for threshold in LEARNED_THRESHOLD_GRID:
        rng = random.Random(seed)
        total = 0.0
        for _ in range(episodes):
            total += _episode(
                rng,
                age_profile="uniform",
                model=model,
                learned_threshold=threshold,
            )["learned_delayed_loss"]
        choices.append((total / episodes, threshold))
    return min(choices)


def _aggregate(rows):
    return {
        name: (
            mean(row[name] for row in rows),
            stdev(row[name] for row in rows),
        )
        for name in (
            "always_trust",
            "fixed_gate",
            "learned_gate",
            "fixed_acceptance",
            "learned_acceptance",
        )
    }


def evaluate_condition(
    model,
    learned_threshold,
    *,
    age_profile,
    fault_probability=DEFAULT_FAULT_PROBABILITY,
    correlated_camera_probability=0.0,
    steps=PRIMARY_EVALUATION_STEPS,
    base_seed=2026091940,
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
            "always_trust": 0.0,
            "fixed_gate": 0.0,
            "learned_gate": 0.0,
            "fixed_acceptance": 0.0,
            "learned_acceptance": 0.0,
        }
        for _ in range(steps):
            result = _episode(
                rng,
                age_profile=age_profile,
                model=model,
                learned_threshold=learned_threshold,
                fault_probability=fault_probability,
                correlated_camera_probability=correlated_camera_probability,
            )
            for name in totals:
                totals[name] += result[name]
        rows.append({name: total / steps for name, total in totals.items()})
    return _aggregate(rows)


def main():
    model = train_delayed_gate()
    calibration_loss, threshold = calibrate_threshold(model)
    print(
        f"learned_threshold={threshold:.2f},"
        f"calibration_delayed_loss={calibration_loss:.6f}"
    )
    print("weights=" + ",".join(f"{weight:.9f}" for weight in model.weights))

    print(
        "profile,always_mean,always_sd,fixed_mean,fixed_sd,learned_mean,learned_sd,"
        "fixed_accept_mean,learned_accept_mean"
    )
    for profile in ("uniform", "fresh_skew", "stale_skew"):
        result = evaluate_condition(model, threshold, age_profile=profile)
        print(
            f"{profile},{result['always_trust'][0]:.6f},{result['always_trust'][1]:.6f},"
            f"{result['fixed_gate'][0]:.6f},{result['fixed_gate'][1]:.6f},"
            f"{result['learned_gate'][0]:.6f},{result['learned_gate'][1]:.6f},"
            f"{result['fixed_acceptance'][0]:.6f},"
            f"{result['learned_acceptance'][0]:.6f}"
        )

    print("fault_probability,fixed_mean,learned_mean,learned_accept_mean")
    for probability in (0.0, 0.1, 0.2, 0.3):
        result = evaluate_condition(
            model,
            threshold,
            age_profile="uniform",
            fault_probability=probability,
            steps=SHIFT_EVALUATION_STEPS,
            base_seed=2026091970,
        )
        print(
            f"{probability:.1f},{result['fixed_gate'][0]:.6f},"
            f"{result['learned_gate'][0]:.6f},"
            f"{result['learned_acceptance'][0]:.6f}"
        )

    print("correlated_camera_probability,always_mean,fixed_mean,learned_mean")
    for probability in (0.1, 0.3, 0.5):
        result = evaluate_condition(
            model,
            threshold,
            age_profile="uniform",
            fault_probability=0.1,
            correlated_camera_probability=probability,
            steps=SHIFT_EVALUATION_STEPS,
            base_seed=2026091980,
        )
        print(
            f"{probability:.1f},{result['always_trust'][0]:.6f},"
            f"{result['fixed_gate'][0]:.6f},{result['learned_gate'][0]:.6f}"
        )


if __name__ == "__main__":
    main()
