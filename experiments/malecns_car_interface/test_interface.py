import unittest

from interface import public_schema, reject_privileged_state


class RealityBoundaryTests(unittest.TestCase):
    def test_declared_buses_are_accepted(self):
        reject_privileged_state(
            {
                "phone": {},
                "obd": {},
                "navigation": {},
                "body": {},
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

    def test_schema_contains_realistic_sensor_buses(self):
        schema = public_schema()
        self.assertIn("camera_rgb_ref", schema["phone"])
        self.assertIn("gyro_xyz_rps", schema["phone"])
        self.assertIn("speed_kph", schema["obd"])
        self.assertIn("distance_to_next_waypoint_m", schema["navigation"])


if __name__ == "__main__":
    unittest.main()
