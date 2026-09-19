import unittest

from active_common_mode_tiebreak import ActiveCommonModeTieBreak


class ActiveCommonModeTieBreakTest(unittest.TestCase):
    def test_clean_agreement_does_not_request_aux(self):
        f = ActiveCommonModeTieBreak()
        obs = None
        for _ in range(12):
            obs = f.observe_primary(
                obd_speed=15.0,
                gnss_speed=15.2,
                camera_speed=15.1,
            )
        self.assertIsNotNone(obs)
        self.assertFalse(obs.request_aux)

    def test_common_mode_pair_requests_aux_and_lidar_can_support_camera(self):
        f = ActiveCommonModeTieBreak()
        obs = None
        for _ in range(8):
            obs = f.observe_primary(
                obd_speed=17.0,
                gnss_speed=17.2,
                camera_speed=15.1,
            )
        self.assertTrue(obs.request_aux)
        resolved = f.resolve_aux(lidar_speed=15.0)
        self.assertEqual(resolved.choice, "camera_aux")
        self.assertLess(resolved.estimate, 15.2)

    def test_camera_fault_can_be_rejected_by_independent_lidar(self):
        f = ActiveCommonModeTieBreak()
        obs = None
        for _ in range(8):
            obs = f.observe_primary(
                obd_speed=15.0,
                gnss_speed=15.2,
                camera_speed=17.0,
            )
        self.assertTrue(obs.request_aux)
        resolved = f.resolve_aux(lidar_speed=15.1)
        self.assertEqual(resolved.choice, "pair_aux")
        self.assertAlmostEqual(resolved.estimate, 15.1, places=6)

    def test_ambiguous_aux_holds_pair(self):
        f = ActiveCommonModeTieBreak(aux_margin=0.30)
        for _ in range(8):
            obs = f.observe_primary(
                obd_speed=17.0,
                gnss_speed=17.2,
                camera_speed=15.0,
            )
        self.assertTrue(obs.request_aux)
        resolved = f.resolve_aux(lidar_speed=16.1)
        self.assertEqual(resolved.choice, "ambiguous_hold_pair")
        self.assertAlmostEqual(resolved.estimate, 17.1, places=6)

    def test_custom_window_is_respected(self):
        f = ActiveCommonModeTieBreak(window=4, min_conflicts=3)
        for _ in range(3):
            obs = f.observe_primary(
                obd_speed=17.0,
                gnss_speed=17.1,
                camera_speed=15.0,
            )
            self.assertFalse(obs.request_aux)
        obs = f.observe_primary(
            obd_speed=17.0,
            gnss_speed=17.1,
            camera_speed=15.0,
        )
        self.assertTrue(obs.request_aux)


if __name__ == "__main__":
    unittest.main()
