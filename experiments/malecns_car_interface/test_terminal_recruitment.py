import unittest

from colony_continuous_context_ablation import _sample
from colony_terminal_value_ablation import sequential_allocation, train_terminal


class TerminalRecruitmentTests(unittest.TestCase):
    def test_terminal_policy_spends_exact_budget(self):
        policy = train_terminal(steps=500, seed=17)
        _, camera, imu = _sample(__import__("random").Random(19), age_profile="uniform")
        camera_count, imu_count = sequential_allocation(policy, camera, imu)
        self.assertEqual(camera_count + imu_count, 12)
        self.assertGreaterEqual(camera_count, 2)
        self.assertGreaterEqual(imu_count, 2)
        self.assertLessEqual(camera_count, 8)
        self.assertLessEqual(imu_count, 8)

    def test_terminal_policy_is_deterministic_after_fit(self):
        policy = train_terminal(steps=500, seed=23)
        _, camera, imu = _sample(__import__("random").Random(29), age_profile="fresh_skew")
        first = sequential_allocation(policy, camera, imu)
        second = sequential_allocation(policy, camera, imu)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
