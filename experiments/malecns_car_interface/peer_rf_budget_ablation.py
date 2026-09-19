"""Run 23: cheap Wi-Fi peer token before costlier LiDAR under equal budgets."""
from __future__ import annotations

import argparse
import json
import random
import statistics
from dataclasses import dataclass

from active_common_mode_tiebreak import ActiveCommonModeTieBreak
from budgeted_peer_witness import (
    AcquisitionBudget,
    BudgetedPeerFirstPolicy,
    PeerFirstResolver,
    PeerToken,
)

DT = 0.1


@dataclass
class Episode:
    truth: list[float]
    obd: list[float]
    gnss: list[float]
    camera: list[float]
    lidar: list[float]
    peer: list[PeerToken | None]
    common: list[float]


def _trajectory(rng: random.Random, steps: int) -> list[float]:
    out: list[float] = []
    speed = rng.uniform(8.0, 25.0)
    accel = rng.uniform(-0.5, 0.5)
    for _ in range(steps):
        impulse = rng.gauss(0.0, 0.55)
        if rng.random() < 0.08:
            impulse += rng.uniform(-2.5, 2.5)
        accel = max(-4.0, min(3.5, 0.90 * accel + impulse))
        speed = max(0.0, speed + accel * DT)
        out.append(speed)
    return out


def generate_episode(
    seed: int,
    *,
    pair_mode: str,
    camera_mode: str,
    peer_mode: str,
    lidar_mode: str,
    steps: int = 250,
) -> Episode:
    rng = random.Random(seed)
    truth = _trajectory(rng, steps)
    common = [0.0] * steps

    if pair_mode == "common_static":
        bias = rng.choice((-1.0, 1.0)) * rng.uniform(1.2, 2.0)
        common = [bias] * steps
    elif pair_mode == "common_drift":
        bias = rng.uniform(-0.2, 0.2)
        direction = rng.choice((-1.0, 1.0))
        for index in range(steps):
            bias += direction * 0.007 + rng.gauss(0.0, 0.008)
            bias = max(-2.2, min(2.2, bias))
            common[index] = bias
    elif pair_mode == "common_jump":
        bias = rng.choice((-1.0, 1.0)) * rng.uniform(1.4, 2.2)
        for index in range(steps // 2, steps):
            common[index] = bias
    elif pair_mode != "clean":
        raise ValueError(pair_mode)

    obd = [
        value + common[index] + rng.gauss(0.0, 0.18)
        for index, value in enumerate(truth)
    ]
    gnss = [
        value + common[index] + rng.gauss(0.0, 0.45)
        for index, value in enumerate(truth)
    ]

    camera_bias = 0.0
    if camera_mode == "bias":
        camera_bias = rng.choice((-1.0, 1.0)) * rng.uniform(1.2, 2.0)
    elif camera_mode != "clean":
        raise ValueError(camera_mode)
    camera = [value + camera_bias + rng.gauss(0.0, 0.55) for value in truth]

    lidar_bias = 0.0
    if lidar_mode == "bias":
        lidar_bias = rng.choice((-1.0, 1.0)) * rng.uniform(1.0, 1.8)
    elif lidar_mode != "clean":
        raise ValueError(lidar_mode)
    lidar = [value + lidar_bias + rng.gauss(0.0, 0.35) for value in truth]

    peer_bias = 0.0
    confidence = 0.92
    dropout = 0.10
    if peer_mode == "bias":
        peer_bias = rng.choice((-1.0, 1.0)) * rng.uniform(1.2, 2.0)
    elif peer_mode == "low_conf_bias":
        peer_bias = rng.choice((-1.0, 1.0)) * rng.uniform(1.2, 2.0)
        confidence = 0.38
    elif peer_mode != "clean":
        raise ValueError(peer_mode)

    peer: list[PeerToken | None] = []
    for value in truth:
        if rng.random() < dropout:
            peer.append(None)
            continue
        age = rng.uniform(0.04, 0.28)
        peer.append(
            PeerToken(
                value + peer_bias + rng.gauss(0.0, 0.50),
                max(0.05, min(1.0, confidence + rng.gauss(0.0, 0.05))),
                age,
            )
        )

    return Episode(truth, obd, gnss, camera, lidar, peer, common)


def _mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def run_episode(ep: Episode, budget_units: int = 150) -> dict[str, float]:
    # Separate state prevents one policy's interventions from leaking into another.
    lidar_detector = ActiveCommonModeTieBreak()
    rf_detector = ActiveCommonModeTieBreak()
    rf_resolver = PeerFirstResolver()
    rf_budget = AcquisitionBudget(budget_units, budget_units)
    hybrid = BudgetedPeerFirstPolicy(budget_units=budget_units)
    lidar_budget = AcquisitionBudget(budget_units, budget_units)

    metrics = {
        key: []
        for key in (
            "pair_mae",
            "three_mae",
            "lidar_only_mae",
            "rf_only_mae",
            "rf_first_mae",
            "rf_first_peer_resolve",
            "rf_first_lidar_escalate",
        )
    }

    for index, truth in enumerate(ep.truth):
        pair = (ep.obd[index] + ep.gnss[index]) / 2.0
        three = (ep.obd[index] + ep.gnss[index] + ep.camera[index]) / 3.0

        primary_lidar = lidar_detector.observe_primary(
            obd_speed=ep.obd[index],
            gnss_speed=ep.gnss[index],
            camera_speed=ep.camera[index],
        )
        lidar_estimate = primary_lidar.pair_estimate
        if primary_lidar.request_aux and lidar_budget.buy_lidar():
            lidar_estimate = lidar_detector.resolve_aux(
                lidar_speed=ep.lidar[index]
            ).estimate

        primary_rf = rf_detector.observe_primary(
            obd_speed=ep.obd[index],
            gnss_speed=ep.gnss[index],
            camera_speed=ep.camera[index],
        )
        rf_estimate = primary_rf.pair_estimate
        if (
            primary_rf.request_aux
            and ep.peer[index] is not None
            and rf_budget.buy_peer()
        ):
            decision = rf_resolver.resolve(
                pair_speed=primary_rf.pair_estimate,
                camera_speed=ep.camera[index],
                token=ep.peer[index],
            )
            if decision.resolved:
                rf_estimate = decision.estimate

        primary_hybrid = hybrid.observe_primary(
            obd_speed=ep.obd[index],
            gnss_speed=ep.gnss[index],
            camera_speed=ep.camera[index],
        )
        lidar_before = hybrid.budget.spent_lidar
        hybrid_estimate, choice = hybrid.resolve(
            primary=primary_hybrid,
            camera_speed=ep.camera[index],
            peer_token=ep.peer[index],
            lidar_speed=ep.lidar[index],
        )

        metrics["pair_mae"].append(abs(pair - truth))
        metrics["three_mae"].append(abs(three - truth))
        metrics["lidar_only_mae"].append(abs(lidar_estimate - truth))
        metrics["rf_only_mae"].append(abs(rf_estimate - truth))
        metrics["rf_first_mae"].append(abs(hybrid_estimate - truth))
        metrics["rf_first_peer_resolve"].append(
            float(choice in {"camera_peer", "pair_peer"})
        )
        metrics["rf_first_lidar_escalate"].append(
            float(hybrid.budget.spent_lidar > lidar_before)
        )

    output = {key: _mean(values) for key, values in metrics.items()}
    output["lidar_only_cost"] = float(lidar_budget.spent_total)
    output["rf_only_cost"] = float(rf_budget.spent_total)
    output["rf_first_cost"] = float(hybrid.budget.spent_total)
    output["rf_first_peer_units"] = float(hybrid.budget.spent_peer)
    output["rf_first_lidar_units"] = float(hybrid.budget.spent_lidar)
    return output


def evaluate(
    *,
    seeds: int = 3,
    episodes_per_seed: int = 20,
    steps: int = 250,
    budget_units: int = 150,
) -> dict[str, object]:
    pair_modes = ("clean", "common_static", "common_drift", "common_jump")
    camera_modes = ("clean", "bias")
    peer_modes = ("clean", "bias", "low_conf_bias")
    lidar_modes = ("clean", "bias")

    output: dict[str, object] = {
        "config": {
            "seeds": seeds,
            "episodes_per_seed": episodes_per_seed,
            "steps": steps,
            "budget_units_per_episode": budget_units,
            "peer_cost_units": 1,
            "lidar_cost_units": 5,
            "peer_dropout": 0.10,
            "peer_noise_sd_mps": 0.50,
            "peer_age_s": [0.04, 0.28],
            "lidar_escalation_score_min": 1.50,
        },
        "regimes": {},
    }

    regimes = output["regimes"]
    assert isinstance(regimes, dict)
    for pair_index, pair_mode in enumerate(pair_modes):
        regimes[pair_mode] = {}
        for camera_index, camera_mode in enumerate(camera_modes):
            regimes[pair_mode][camera_mode] = {}
            for peer_index, peer_mode in enumerate(peer_modes):
                regimes[pair_mode][camera_mode][peer_mode] = {}
                for lidar_index, lidar_mode in enumerate(lidar_modes):
                    seed_rows = []
                    for seed_index in range(seeds):
                        rows = []
                        for episode_index in range(episodes_per_seed):
                            seed = (
                                23_000_000
                                + pair_index * 1_000_000
                                + camera_index * 200_000
                                + peer_index * 50_000
                                + lidar_index * 20_000
                                + seed_index * 2_000
                                + episode_index
                            )
                            rows.append(
                                run_episode(
                                    generate_episode(
                                        seed,
                                        pair_mode=pair_mode,
                                        camera_mode=camera_mode,
                                        peer_mode=peer_mode,
                                        lidar_mode=lidar_mode,
                                        steps=steps,
                                    ),
                                    budget_units,
                                )
                            )
                        seed_rows.append(
                            {
                                key: statistics.mean(row[key] for row in rows)
                                for key in rows[0]
                            }
                        )

                    regimes[pair_mode][camera_mode][peer_mode][lidar_mode] = {
                        key: {
                            "mean": statistics.mean(row[key] for row in seed_rows),
                            "sd_across_seeds": (
                                statistics.stdev(row[key] for row in seed_rows)
                                if len(seed_rows) > 1
                                else 0.0
                            ),
                        }
                        for key in seed_rows[0]
                    }
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=3)
    parser.add_argument("--episodes-per-seed", type=int, default=20)
    parser.add_argument("--steps", type=int, default=250)
    parser.add_argument("--budget-units", type=int, default=150)
    args = parser.parse_args()
    print(
        json.dumps(
            evaluate(
                seeds=args.seeds,
                episodes_per_seed=args.episodes_per_seed,
                steps=args.steps,
                budget_units=args.budget_units,
            ),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
