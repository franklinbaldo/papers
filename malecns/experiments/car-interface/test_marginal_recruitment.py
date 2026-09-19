import unittest

from colony import SpecialistReport
from marginal_recruitment import marginal_recruitment_features


class MarginalRecruitmentFeatureTests(unittest.TestCase):
    def setUp(self):
        self.camera = [
            SpecialistReport(
                "camera-0",
                "dynamic-scalar",
                0.2,
                0.9,
                age_ms=20.0,
                modality="camera",
            ),
            SpecialistReport(
                "camera-1",
                "dynamic-scalar",
                0.3,
                0.8,
                age_ms=24.0,
                modality="camera",
            ),
        ]
        self.imu = [
            SpecialistReport(
                "imu-0",
                "dynamic-scalar",
                0.25,
                0.85,
                age_ms=8.0,
                modality="imu",
            ),
            SpecialistReport(
                "imu-1",
                "dynamic-scalar",
                0.22,
                0.88,
                age_ms=10.0,
                modality="imu",
            ),
        ]

    def test_feature_vector_extends_run8_context_with_budget_state(self):
        features = marginal_recruitment_features(
            self.camera,
            self.imu,
            primary_count=2,
            secondary_count=2,
        )
        self.assertEqual(len(features), 13)
        self.assertAlmostEqual(features[-3], 0.25)
        self.assertAlmostEqual(features[-2], 0.25)
        self.assertAlmostEqual(features[-1], 4 / 12)

    def test_rejects_impossible_budget_state(self):
        with self.assertRaises(ValueError):
            marginal_recruitment_features(
                self.camera,
                self.imu,
                primary_count=8,
                secondary_count=8,
            )


if __name__ == "__main__":
    unittest.main()
