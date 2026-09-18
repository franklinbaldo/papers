"""Deterministic ablation for robust consensus in MaleCNS sensor colonies.

This isolates one architecture question before expensive MaleCNS training: can a
cheap cross-specialist consensus rule protect the coordinator when a faulty fly
is confidently wrong? No dataset, model, or simulator download is required.
"""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Iterable

from colony import (
    SpecialistReport,
    confidence_weighted_value,
    consensus_weighted_value,
    median_value,
)


@dataclass(frozen=True)
class ConsensusAblationResult:
    fault_probability: float
    faulty_confidence: float
    single_mae: float
    mean_mae: float
    median_mae: float
    confidence_weighted_mae: float
    consensus_weighted_mae: float


def mean_value(reports: Iterable[SpecialistReport]) -> float:
    items = list(reports)
    if not items:
        raise ValueError("at least one specialist report is required")
    return sum(report.value for report in items) / len(items)


def run_consensus_ablation(
    *,
    seed: int = 20260918,
    trials: int = 10_000,
    specialists: int = 5,
    fault_probability: float = 0.2,
    healthy_sigma: float = 0.05,
    faulty_sigma: float = 0.08,
    fault_bias: float = 0.8,
    healthy_confidence: float = 0.9,
    faulty_confidence: float = 0.95,
) -> ConsensusAblationResult:
    if trials <= 0 or specialists <= 0:
        raise ValueError("trials and specialists must be positive")
    if not 0.0 <= fault_probability <= 1.0:
        raise ValueError("fault_probability must be in [0, 1]")

    rng = random.Random(seed)
    totals = {
        "single": 0.0,
        "mean": 0.0,
        "median": 0.0,
        "confidence": 0.0,
        "consensus": 0.0,
    }

    for _ in range(trials):
        truth = rng.uniform(-1.0, 1.0)
        reports: list[SpecialistReport] = []
        for index in range(specialists):
            faulty = rng.random() < fault_probability
            if faulty:
                value = truth + fault_bias + rng.gauss(0.0, faulty_sigma)
                confidence = faulty_confidence
            else:
                value = truth + rng.gauss(0.0, healthy_sigma)
                confidence = healthy_confidence
            reports.append(
                SpecialistReport(
                    specialist_id=f"specialist-{index}",
                    channel="synthetic_scalar",
                    value=value,
                    confidence=confidence,
                    novelty=float(faulty),
                )
            )

        predictions = {
            "single": reports[0].value,
            "mean": mean_value(reports),
            "median": median_value(reports),
            "confidence": confidence_weighted_value(reports),
            "consensus": consensus_weighted_value(reports),
        }
        for name, prediction in predictions.items():
            totals[name] += abs(prediction - truth)

    denom = float(trials)
    return ConsensusAblationResult(
        fault_probability=fault_probability,
        faulty_confidence=faulty_confidence,
        single_mae=totals["single"] / denom,
        mean_mae=totals["mean"] / denom,
        median_mae=totals["median"] / denom,
        confidence_weighted_mae=totals["confidence"] / denom,
        consensus_weighted_mae=totals["consensus"] / denom,
    )


def main() -> None:
    print(
        "faulty_confidence,fault_p,single_mae,mean_mae,median_mae,"
        "confidence_weighted_mae,consensus_weighted_mae"
    )
    for faulty_confidence in (0.15, 0.95):
        for probability in (0.0, 0.1, 0.2, 0.3, 0.4):
            result = run_consensus_ablation(
                fault_probability=probability,
                faulty_confidence=faulty_confidence,
            )
            print(
                f"{result.faulty_confidence:.2f},"
                f"{result.fault_probability:.1f},"
                f"{result.single_mae:.6f},"
                f"{result.mean_mae:.6f},"
                f"{result.median_mae:.6f},"
                f"{result.confidence_weighted_mae:.6f},"
                f"{result.consensus_weighted_mae:.6f}"
            )


if __name__ == "__main__":
    main()
