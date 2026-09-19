"""Deterministic ablation for stale-but-confident MaleCNS specialist reports.

The synthetic channel represents any rapidly changing scalar that could be
measured on a real vehicle (yaw rate, speed error, visual TTC, etc.). Specialist
reports are delayed according to their age metadata; no simulator-only truth is
passed into the fusion rules.
"""

from __future__ import annotations

import random

from colony import (
    SpecialistReport,
    confidence_weighted_value,
    consensus_weighted_value,
    freshness_weighted_value,
    median_value,
)


def run_condition(
    stale_probability: float,
    *,
    trials: int = 10_000,
    specialists: int = 5,
    seed: int = 20260918,
) -> dict[str, float]:
    rng = random.Random(seed + int(stale_probability * 1000))
    errors = {
        key: 0.0
        for key in ("single", "median", "confidence", "consensus", "freshness")
    }

    for _ in range(trials):
        truth = rng.uniform(-1.0, 1.0)
        velocity = rng.uniform(-3.0, 3.0)
        reports: list[SpecialistReport] = []

        for index in range(specialists):
            stale = rng.random() < stale_probability
            age_ms = rng.uniform(450.0, 900.0) if stale else rng.uniform(10.0, 60.0)
            noise = rng.gauss(0.0, 0.03)
            value = truth - velocity * (age_ms / 1000.0) + noise
            reports.append(
                SpecialistReport(
                    specialist_id=f"specialist-{index}",
                    channel="dynamic-scalar",
                    value=value,
                    confidence=0.9,
                    age_ms=age_ms,
                )
            )

        predictions = {
            "single": reports[0].value,
            "median": median_value(reports),
            "confidence": confidence_weighted_value(reports),
            "consensus": consensus_weighted_value(reports, min_radius=0.08),
            "freshness": freshness_weighted_value(reports, half_life_ms=150.0),
        }
        for key, prediction in predictions.items():
            errors[key] += abs(prediction - truth)

    return {key: value / trials for key, value in errors.items()}


def main() -> None:
    print("stale_prob,single,median,confidence,consensus,freshness")
    for stale_probability in (0.0, 0.2, 0.4, 0.6, 0.8):
        result = run_condition(stale_probability)
        values = ",".join(f"{result[key]:.6f}" for key in result)
        print(f"{stale_probability:.1f},{values}")


if __name__ == "__main__":
    main()
