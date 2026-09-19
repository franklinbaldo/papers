import unittest

from colony import SpecialistReport
from recruitment_bandit import LinearContextualPolicy, continuous_context_features


class ContinuousRecruitmentTests(unittest.TestCase):
    def test_features_are_reality_bounded_and_fixed_width(self):
        camera = [
            SpecialistReport("c1", "yaw", 0.1, 0.9, age_ms=40.0, modality="camera"),
            SpecialistReport("c2", "yaw", 0.2, 0.8, age_ms=50.0, modality="camera"),
        ]
        imu = [
            SpecialistReport("i1", "yaw", 0.15, 0.85, age_ms=10.0, modality="imu"),
            SpecialistReport("i2", "yaw", 0.12, 0.80, age_ms=20.0, modality="imu"),
        ]
        features = continuous_context_features(camera, imu)
        self.assertEqual(len(features), 10)
        self.assertEqual(features[0], 1.0)
        self.assertGreater(features[3], 0.0)
        self.assertLessEqual(features[3], 1.0)

    def test_policy_requires_fit(self):
        policy = LinearContextualPolicy(("a", "b"), feature_dim=2)
        with self.assertRaises(ValueError):
            policy.select((1.0, 0.5))

    def test_policy_learns_context_dependent_action(self):
        policy = LinearContextualPolicy(("a", "b"), feature_dim=2, ridge=0.01)
        for x in (0.0, 0.1, 0.2, 0.8, 0.9, 1.0):
            features = (1.0, x)
            policy.observe("a", features, 1.0 - x)
            policy.observe("b", features, x)
        policy.fit()
        self.assertEqual(policy.select((1.0, 0.05)), "a")
        self.assertEqual(policy.select((1.0, 0.95)), "b")

    def test_feature_dimension_is_enforced(self):
        policy = LinearContextualPolicy(("a",), feature_dim=2)
        with self.assertRaises(ValueError):
            policy.observe("a", (1.0,), 0.0)


if __name__ == "__main__":
    unittest.main()
