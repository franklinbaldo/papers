import math
import unittest

from interface import ObdObservation, PhoneObservation, public_schema, reject_privileged_state
from signals import derive_signals


class RealityBoundaryTests(unittest.TestCase):
    def test_declared_buses_are_accepted(self):
        reject_privileged_state(
            {
                "phone": {},
                "obd": {},
                "navigation": {},
                "body": {},
                "range": {},
                "perception": {},
                "radio": {},
                "semantic": {},
                "derived": {},
            }
        )

    def test_exact_object_distance_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "privileged"):
            reject_privileged_state(
                {
                    "phone": {},
                    "obd": {},
                    "navigation": {},
                    "body": {},
                    "object_distance": 3.2,
                }
            )

    def test_lane_center_truth_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "privileged"):
            reject_privileged_state(
                {
                    "phone": {},
                    "obd": {},
                    "navigation": {},
                    "body": {},
                    "lane_center": 0.01,
                }
            )

    def test_schema_contains_modular_realistic_buses(self):
        schema = public_schema()
        self.assertIn("camera_rgb_ref", schema["phone"])
        self.assertIn("wheel_speeds_kph", schema["obd"])
        self.assertIn("ultrasonic_ranges_m", schema["range"])
        self.assertIn("visual_ttc_s", schema["perception"])
        self.assertIn("peer_vehicle_count", schema["radio"])
        self.assertIn("local_llm_confidence", schema["semantic"])
        self.assertIn("speed_disagreement_kph", schema["derived"])

    def test_cross_sensor_signals_are_computed_from_public_inputs(self):
        phone = PhoneObservation(
            camera_rgb_ref="frame://1",
            gps_accuracy_m=4.0,
            gps_speed_kph=50.0,
            gyro_xyz_rps=(0.0, 0.0, 0.20),
        )
        obd = ObdObservation(
            speed_kph=54.0,
            steering_angle_rad=0.01,
            wheel_speeds_kph=(53.5, 54.0, 54.3, 53.8),
        )
        derived = derive_signals(phone, obd, wheelbase_m=2.7)
        self.assertAlmostEqual(derived.speed_disagreement_kph, 4.0)
        self.assertAlmostEqual(derived.wheel_speed_spread_kph, 0.8)
        expected_yaw = (54.0 / 3.6) / 2.7 * math.tan(0.01)
        self.assertAlmostEqual(
            derived.steering_yaw_residual_rps,
            abs(0.20 - expected_yaw),
        )
        self.assertGreater(derived.gnss_confidence, 0.9)

    def test_missing_inputs_do_not_get_filled_from_magic(self):
        phone = PhoneObservation(camera_rgb_ref="frame://1")
        obd = ObdObservation()
        derived = derive_signals(phone, obd)
        self.assertIsNone(derived.speed_disagreement_kph)
        self.assertIsNone(derived.wheel_speed_spread_kph)
        self.assertIsNone(derived.steering_yaw_residual_rps)
        self.assertIsNone(derived.gnss_confidence)


if __name__ == "__main__":
    unittest.main()
