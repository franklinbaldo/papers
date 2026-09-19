from __future__ import annotations

import math
import unittest

from clock_offset_estimation import RobustClockOffsetEstimator, speed_interval_delta_v


def _prefix(acceleration: list[float], dt: float = 0.1) -> list[float]:
    result = [0.0]
    for sample in acceleration:
        result.append(result[-1] + sample * dt)
    return result


class ClockOffsetEstimatorTests(unittest.TestCase):
    def test_speed_interval_matches_discrete_state_update(self) -> None:
        acceleration = [0.0, 1.0, 2.0, 3.0, 4.0]
        prefix = _prefix(acceleration)
        self.assertAlmostEqual(speed_interval_delta_v(prefix, 1, 3), 0.5)

    def test_recovers_positive_three_step_offset(self) -> None:
        steps = 140
        acceleration = [0.8 * math.sin(index / 5.0) for index in range(steps)]
        speed = [12.0]
        for index in range(1, steps):
            speed.append(speed[-1] + acceleration[index] * 0.1)
        prefix = _prefix(acceleration)
        estimator = RobustClockOffsetEstimator()
        previous = None
        for actual_index in range(10, 110, 5):
            reported = actual_index + 3
            current = (speed[actual_index], reported)
            if previous is not None:
                estimator.observe_pair(
                    previous_speed=previous[0],
                    current_speed=current[0],
                    previous_reported_index=previous[1],
                    current_reported_index=current[1],
                    imu_prefix_delta_v=prefix,
                    available_end_index=actual_index + 8,
                )
            previous = current
        self.assertTrue(estimator.observation().active)
        self.assertEqual(estimator.applied_offset_steps, 3)

    def test_clean_clock_stays_inactive(self) -> None:
        steps = 140
        acceleration = [0.7 * math.sin(index / 4.0) for index in range(steps)]
        speed = [9.0]
        for index in range(1, steps):
            speed.append(speed[-1] + acceleration[index] * 0.1)
        prefix = _prefix(acceleration)
        estimator = RobustClockOffsetEstimator()
        previous = None
        for actual_index in range(10, 110, 5):
            current = (speed[actual_index], actual_index)
            if previous is not None:
                estimator.observe_pair(
                    previous_speed=previous[0],
                    current_speed=current[0],
                    previous_reported_index=previous[1],
                    current_reported_index=current[1],
                    imu_prefix_delta_v=prefix,
                    available_end_index=actual_index + 8,
                )
            previous = current
        self.assertFalse(estimator.observation().active)
        self.assertEqual(estimator.applied_offset_steps, 0)

    def test_future_imu_samples_are_not_eligible(self) -> None:
        prefix = _prefix([0.0] * 30 + [100.0] * 30)
        estimator = RobustClockOffsetEstimator(min_pairs=1, window_pairs=2)
        observation = estimator.observe_pair(
            previous_speed=10.0,
            current_speed=10.0,
            previous_reported_index=20,
            current_reported_index=25,
            imu_prefix_delta_v=prefix,
            available_end_index=22,
        )
        self.assertFalse(observation.active)
        self.assertEqual(observation.applied_offset_steps, 0)
        self.assertEqual(estimator.corrected_index(40, 22), 22)


if __name__ == "__main__":
    unittest.main()
