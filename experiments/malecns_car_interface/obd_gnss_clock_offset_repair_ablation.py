"""Run 20: causal clock-offset estimation and repair for OBD-II/GNSS fusion.

This run reuses the Run-19 observation generator but replaces passive attenuation
with an explicit observable clock-offset estimator. Synthetic truth remains on
the generator/scoring side only. Deployable arms receive timestamped OBD speed,
GNSS speed/report time, phone longitudinal IMU, observed residual history, and
declared nominal noise scales.
"""

from __future__ import annotations

import argparse
import json
import statistics

from clock_offset_estimation import RobustClockOffsetEstimator
from innovation_robust_fusion import (
    OnlineInnovationScale,
    covariance_relative_precision,
    innovation_huber_weight,
)
from obd_gnss_clock_integrity_ablation import DT, Episode, generate_episode
from temporal_bias_calibration import PersistentBiasCalibrator
from temporal_robust_fusion import fuse, transport_by_reference_delta

REFERENCE_NOMINAL_SIGMA = 0.20
CANDIDATE_NOMINAL_SIGMA = 0.50


def _mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def _update_path(
    *,
    calibrator: PersistentBiasCalibrator,
    raw_scale: OnlineInnovationScale,
    corrected_scale: OnlineInnovationScale,
    reference_value: float,
    candidate_value: float,
) -> None:
    raw_scale.observe(candidate_value - reference_value)
    calibrator.observe(reference_value, candidate_value)
    corrected_scale.observe(candidate_value - calibrator.apply(reference_value))


def _fused_value(
    *,
    reference_now: float,
    reference_at_measurement: float,
    candidate_at_measurement: float,
    age_s: float,
    raw_scale: OnlineInnovationScale,
    corrected_scale: OnlineInnovationScale,
) -> float:
    corrected_residual = candidate_at_measurement - reference_at_measurement
    transported = transport_by_reference_delta(
        candidate_at_measurement,
        reference_at_measurement,
        reference_now,
    )
    relative_precision = covariance_relative_precision(
        raw_innovation_sigma=raw_scale.sigma,
        reference_nominal_sigma=REFERENCE_NOMINAL_SIGMA,
        candidate_nominal_sigma=CANDIDATE_NOMINAL_SIGMA,
    )
    weight = innovation_huber_weight(
        age_s=age_s,
        matched_time_residual=corrected_residual,
        innovation_sigma=corrected_scale.sigma,
        relative_precision=relative_precision,
    )
    return fuse(reference_now, transported, weight)


def run_episode(episode: Episode) -> dict[str, float]:
    imu_prefix_delta_v = [0.0]
    for sample in episode.imu_acceleration:
        imu_prefix_delta_v.append(imu_prefix_delta_v[-1] + sample * DT)

    raw_calibrator = PersistentBiasCalibrator()
    raw_scale = OnlineInnovationScale()
    raw_corrected_scale = OnlineInnovationScale()

    repaired_calibrator = PersistentBiasCalibrator()
    repaired_scale = OnlineInnovationScale()
    repaired_corrected_scale = OnlineInnovationScale()
    offset_estimator = RobustClockOffsetEstimator()

    latest_raw = None
    latest_repaired = None
    previous_fix = None
    offset_observations = []

    errors = {
        name: []
        for name in (
            "reference_raw_time",
            "covariance_raw_time",
            "reference_offset_repaired",
            "covariance_offset_repaired",
        )
    }

    for index, truth in enumerate(episode.truth):
        for fix in episode.arrivals.get(index, []):
            reported = fix.reported_measurement_index
            if reported <= index:
                _update_path(
                    calibrator=raw_calibrator,
                    raw_scale=raw_scale,
                    corrected_scale=raw_corrected_scale,
                    reference_value=episode.obd[reported],
                    candidate_value=fix.value,
                )
                if latest_raw is None or reported > latest_raw.reported_measurement_index:
                    latest_raw = fix

            if previous_fix is not None:
                observation = offset_estimator.observe_pair(
                    previous_speed=previous_fix.value,
                    current_speed=fix.value,
                    previous_reported_index=previous_fix.reported_measurement_index,
                    current_reported_index=fix.reported_measurement_index,
                    imu_prefix_delta_v=imu_prefix_delta_v,
                    available_end_index=index,
                )
                offset_observations.append(observation)
            previous_fix = fix

            repaired_index = offset_estimator.corrected_index(reported, index)
            _update_path(
                calibrator=repaired_calibrator,
                raw_scale=repaired_scale,
                corrected_scale=repaired_corrected_scale,
                reference_value=episode.obd[repaired_index],
                candidate_value=fix.value,
            )
            latest_repaired = (fix, repaired_index)

        raw_reference_now = raw_calibrator.apply(episode.obd[index])
        values = {
            "reference_raw_time": raw_reference_now,
            "covariance_raw_time": raw_reference_now,
        }
        if latest_raw is not None:
            reported = latest_raw.reported_measurement_index
            if reported <= index:
                raw_reference_at_measurement = raw_calibrator.apply(episode.obd[reported])
                values["covariance_raw_time"] = _fused_value(
                    reference_now=raw_reference_now,
                    reference_at_measurement=raw_reference_at_measurement,
                    candidate_at_measurement=latest_raw.value,
                    age_s=(index - reported) * DT,
                    raw_scale=raw_scale,
                    corrected_scale=raw_corrected_scale,
                )

        repaired_reference_now = repaired_calibrator.apply(episode.obd[index])
        values["reference_offset_repaired"] = repaired_reference_now
        values["covariance_offset_repaired"] = repaired_reference_now
        if latest_repaired is not None:
            latest_fix, repaired_index = latest_repaired
            repaired_reference_at_measurement = repaired_calibrator.apply(
                episode.obd[repaired_index]
            )
            values["covariance_offset_repaired"] = _fused_value(
                reference_now=repaired_reference_now,
                reference_at_measurement=repaired_reference_at_measurement,
                candidate_at_measurement=latest_fix.value,
                age_s=(index - repaired_index) * DT,
                raw_scale=repaired_scale,
                corrected_scale=repaired_corrected_scale,
            )

        for name, value in values.items():
            errors[name].append(abs(value - truth))

    active_fraction = _mean(
        [1.0 if observation.active else 0.0 for observation in offset_observations]
    )
    applied_offset = _mean(
        [float(observation.applied_offset_steps) for observation in offset_observations]
    )
    relative_gain = _mean(
        [observation.relative_gain_over_zero for observation in offset_observations]
    )

    return {
        **{name: _mean(method_errors) for name, method_errors in errors.items()},
        "offset_active_fraction": active_fraction,
        "mean_applied_offset_steps": applied_offset,
        "mean_relative_gain_over_zero": relative_gain,
    }


def evaluate(*, seeds: int = 3, episodes_per_seed: int = 100) -> dict[str, object]:
    result: dict[str, object] = {
        "config": {
            "seeds": seeds,
            "episodes_per_seed": episodes_per_seed,
            "steps_per_episode": 500,
            "dt_s": DT,
            "obd_rate_hz": 10,
            "gnss_rate_hz": 2,
            "gnss_delay_s": [0.4, 1.2],
            "gnss_dropout": 0.15,
            "clock_offset_s": 0.3,
            "clock_jitter_s": [-0.2, 0.2],
            "clock_drift_stress_fraction": 0.006,
            "offset_search_steps": [-6, 6],
            "offset_window_pairs": 40,
            "offset_min_pairs": 8,
            "offset_activation_min_steps": 2,
            "offset_activation_min_relative_gain": 0.08,
        },
        "regimes": {},
    }

    clock_modes = ("clean", "offset", "jitter", "drift", "offset_jitter")
    obd_modes = ("clean", "static", "drift")
    for obd_index, obd_mode in enumerate(obd_modes):
        obd_result = {}
        for clock_index, clock_mode in enumerate(clock_modes):
            per_seed = []
            for seed_index in range(seeds):
                rows = []
                for episode_index in range(episodes_per_seed):
                    seed = (
                        2_000_000
                        + obd_index * 500_000
                        + clock_index * 100_000
                        + seed_index * 10_000
                        + episode_index
                    )
                    rows.append(
                        run_episode(
                            generate_episode(
                                seed,
                                clock_mode=clock_mode,
                                obd_mode=obd_mode,
                            )
                        )
                    )
                per_seed.append(
                    {
                        name: statistics.mean(row[name] for row in rows)
                        for name in rows[0]
                    }
                )
            obd_result[clock_mode] = {
                name: {
                    "mean": statistics.mean(row[name] for row in per_seed),
                    "sd_across_seeds": statistics.stdev(row[name] for row in per_seed),
                }
                for name in per_seed[0]
            }
        result["regimes"][obd_mode] = obd_result
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=3)
    parser.add_argument("--episodes-per-seed", type=int, default=100)
    args = parser.parse_args()
    print(json.dumps(evaluate(seeds=args.seeds, episodes_per_seed=args.episodes_per_seed), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
