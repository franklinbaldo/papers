import unittest

from colony import SpecialistReport
from probe_trust import probe_trust_score, should_trust_probe


class ProbeTrustTests(unittest.TestCase):
    def setUp(self):
        self.camera = [
            SpecialistReport(
                "camera-0",
                "dynamic-scalar",
                0.20,
                0.90,
                age_ms=20.0,
                modality="camera",
            ),
            SpecialistReport(
                "camera-1",
                "dynamic-scalar",
                0.24,
                0.88,
                age_ms=24.0,
                modality="camera",
            ),
        ]
        self.imu = [
            SpecialistReport(
                "imu-0",
                "dynamic-scalar",
                0.22,
                0.86,
                age_ms=10.0,
                modality="imu",
            ),
            SpecialistReport(
                "imu-1",
                "dynamic-scalar",
                0.19,
                0.84,
                age_ms=12.0,
                modality="imu",
            ),
        ]

    def test_stale_candidate_scores_lower(self):
        fresh = SpecialistReport(
            "camera-fresh",
            "dynamic-scalar",
            0.21,
            0.90,
            age_ms=20.0,
            modality="camera",
        )
        stale = SpecialistReport(
            "camera-stale",
            "dynamic-scalar",
            0.21,
            0.90,
            age_ms=800.0,
            modality="camera",
        )
        self.assertGreater(
            probe_trust_score(self.camera, fresh, self.imu),
            probe_trust_score(self.camera, stale, self.imu),
        )

    def test_disagreeing_candidate_scores_lower(self):
        agreeing = SpecialistReport(
            "camera-agree",
            "dynamic-scalar",
            0.21,
            0.90,
            age_ms=20.0,
            modality="camera",
        )
        disagreeing = SpecialistReport(
            "camera-disagree",
            "dynamic-scalar",
            1.20,
            0.90,
            age_ms=20.0,
            modality="camera",
        )
        self.assertGreater(
            probe_trust_score(self.camera, agreeing, self.imu),
            probe_trust_score(self.camera, disagreeing, self.imu),
        )

    def test_threshold_separates_probe_from_trust(self):
        candidate = SpecialistReport(
            "camera-probe",
            "dynamic-scalar",
            1.20,
            0.95,
            age_ms=20.0,
            modality="camera",
        )
        self.assertFalse(
            should_trust_probe(
                self.camera,
                candidate,
                self.imu,
                threshold=0.12,
            )
        )

    def test_rejects_same_modality_cross_check(self):
        candidate = SpecialistReport(
            "camera-probe",
            "dynamic-scalar",
            0.21,
            0.90,
            age_ms=20.0,
            modality="camera",
        )
        with self.assertRaises(ValueError):
            probe_trust_score(self.camera, candidate, self.camera)


if __name__ == "__main__":
    unittest.main()
