import unittest

from kinematic_clock_health import (
    integrated_acceleration,
    kinematic_clock_observation,
)


class KinematicClockHealthTests(unittest.TestCase):
    def test_integrates_prefix_delta_v(self) -> None:
        prefix = [0.0, 0.1, 0.3, 0.6]
        self.assertAlmostEqual(integrated_acceleration(prefix, 1, 3), 0.5)

    def test_consistent_speed_delta_gets_full_merit(self) -> None:
        prefix = [0.0, 0.1, 0.3, 0.6]
        observation = kinematic_clock_observation(
            previous_speed=10.0,
            current_speed=10.5,
            previous_reported_index=1,
            current_reported_index=3,
            imu_prefix_delta_v=prefix,
        )
        self.assertAlmostEqual(observation.residual_delta_v, 0.0)
        self.assertAlmostEqual(observation.merit, 1.0)

    def test_large_kinematic_mismatch_is_downweighted(self) -> None:
        prefix = [0.0, 0.0, 0.0, 0.0]
        observation = kinematic_clock_observation(
            previous_speed=10.0,
            current_speed=12.0,
            previous_reported_index=0,
            current_reported_index=3,
            imu_prefix_delta_v=prefix,
            nominal_delta_v_sigma=0.5,
        )
        self.assertLess(observation.merit, 0.5)

    def test_rejects_non_increasing_reported_time(self) -> None:
        with self.assertRaises(ValueError):
            kinematic_clock_observation(
                previous_speed=10.0,
                current_speed=11.0,
                previous_reported_index=2,
                current_reported_index=2,
                imu_prefix_delta_v=[0.0, 0.0, 0.0],
            )


if __name__ == "__main__":
    unittest.main()
