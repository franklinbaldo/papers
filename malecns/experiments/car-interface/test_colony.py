import unittest

from colony import (
    SpecialistReport,
    age_spread_ms,
    allocate_recruitment_slots,
    confidence_weighted_value,
    consensus_weighted_value,
    disagreement,
    freshness_weighted_value,
    median_value,
    recruitment_score,
    summarize_modality,
)


class ColonyTests(unittest.TestCase):
    def test_confidence_is_bounded(self):
        with self.assertRaises(ValueError):
            SpecialistReport("imu-1", "imu", 0.2, 1.1)

    def test_age_is_non_negative(self):
        with self.assertRaises(ValueError):
            SpecialistReport("imu-1", "imu", 0.2, 0.9, age_ms=-1.0)

    def test_median_is_robust_to_one_bad_specialist(self):
        reports = [
            SpecialistReport("a", "yaw", 0.10, 0.9),
            SpecialistReport("b", "yaw", 0.12, 0.8),
            SpecialistReport("bad", "yaw", 5.0, 0.1),
        ]
        self.assertAlmostEqual(median_value(reports), 0.12)

    def test_confidence_weighting_downweights_bad_specialist(self):
        reports = [
            SpecialistReport("a", "danger", 0.2, 1.0),
            SpecialistReport("b", "danger", 0.3, 1.0),
            SpecialistReport("bad", "danger", 1.0, 0.0),
        ]
        self.assertAlmostEqual(confidence_weighted_value(reports), 0.25)

    def test_freshness_weighting_downweights_old_report(self):
        reports = [
            SpecialistReport("fresh", "yaw", 0.1, 1.0, age_ms=0.0),
            SpecialistReport("stale", "yaw", 1.0, 1.0, age_ms=150.0),
        ]
        self.assertAlmostEqual(freshness_weighted_value(reports, half_life_ms=150.0), 0.4)

    def test_freshness_weighting_rejects_non_positive_half_life(self):
        reports = [SpecialistReport("a", "speed", 1.0, 1.0)]
        with self.assertRaises(ValueError):
            freshness_weighted_value(reports, half_life_ms=0.0)

    def test_consensus_weighting_rejects_overconfident_outlier(self):
        reports = [
            SpecialistReport("a", "yaw", 0.10, 0.7),
            SpecialistReport("b", "yaw", 0.12, 0.8),
            SpecialistReport("c", "yaw", 0.11, 0.9),
            SpecialistReport("bad", "yaw", 1.20, 1.0),
        ]
        value = consensus_weighted_value(reports, min_radius=0.05)
        self.assertGreater(value, 0.10)
        self.assertLess(value, 0.12)

    def test_consensus_weighting_rejects_negative_radius(self):
        reports = [SpecialistReport("a", "speed", 1.0, 1.0)]
        with self.assertRaises(ValueError):
            consensus_weighted_value(reports, min_radius=-0.1)

    def test_disagreement_detects_conflict(self):
        calm = [SpecialistReport("a", "speed", 10.0, 1.0), SpecialistReport("b", "speed", 10.1, 1.0)]
        conflict = calm + [SpecialistReport("c", "speed", 30.0, 1.0)]
        self.assertGreater(disagreement(conflict), disagreement(calm))

    def test_age_spread_is_a_lawful_coordinator_signal(self):
        reports = [
            SpecialistReport("a", "speed", 10.0, 1.0, age_ms=15.0),
            SpecialistReport("b", "speed", 10.1, 1.0, age_ms=85.0),
        ]
        self.assertEqual(age_spread_ms(reports), 70.0)

    def test_modality_summary_preserves_common_mode_staleness(self):
        reports = [
            SpecialistReport("camera-1", "yaw-rate", 0.10, 0.9, age_ms=620.0, modality="camera"),
            SpecialistReport("camera-2", "yaw-rate", 0.12, 0.8, age_ms=640.0, modality="camera"),
            SpecialistReport("camera-3", "yaw-rate", 0.11, 0.85, age_ms=630.0, modality="camera"),
        ]
        summary = summarize_modality(reports, specialist_id="camera-summary")
        self.assertEqual(summary.modality, "camera")
        self.assertEqual(summary.channel, "yaw-rate")
        self.assertAlmostEqual(summary.value, 0.11)
        self.assertAlmostEqual(summary.age_ms, 630.0)

    def test_modality_summary_rejects_mixed_modalities(self):
        reports = [
            SpecialistReport("camera", "yaw-rate", 0.1, 0.9, modality="camera"),
            SpecialistReport("imu", "yaw-rate", 0.1, 0.9, modality="imu"),
        ]
        with self.assertRaises(ValueError):
            summarize_modality(reports, specialist_id="mixed")

    def test_recruitment_score_prefers_fresh_uncertain_modality(self):
        fresh_uncertain = [
            SpecialistReport("a", "yaw-rate", 0.0, 0.9, age_ms=20.0, modality="imu"),
            SpecialistReport("b", "yaw-rate", 0.3, 0.9, age_ms=25.0, modality="imu"),
        ]
        stale_uncertain = [
            SpecialistReport("a", "yaw-rate", 0.0, 0.9, age_ms=600.0, modality="camera"),
            SpecialistReport("b", "yaw-rate", 0.3, 0.9, age_ms=610.0, modality="camera"),
        ]
        self.assertGreater(recruitment_score(fresh_uncertain), recruitment_score(stale_uncertain))

    def test_dynamic_recruitment_avoids_stale_common_mode(self):
        groups = {
            "camera": [
                SpecialistReport("c1", "yaw-rate", 0.0, 0.9, age_ms=700.0, modality="camera"),
                SpecialistReport("c2", "yaw-rate", 0.2, 0.9, age_ms=710.0, modality="camera"),
            ],
            "imu": [
                SpecialistReport("i1", "yaw-rate", 0.0, 0.9, age_ms=20.0, modality="imu"),
                SpecialistReport("i2", "yaw-rate", 0.12, 0.9, age_ms=25.0, modality="imu"),
            ],
        }
        allocation = allocate_recruitment_slots(groups, extra_slots=8)
        self.assertGreater(allocation["imu"], allocation["camera"])
        self.assertEqual(sum(allocation.values()), 8)

    def test_recruitment_requires_shared_semantic_channel(self):
        groups = {
            "camera": [SpecialistReport("c", "yaw-rate", 0.0, 0.9, modality="camera")],
            "imu": [SpecialistReport("i", "speed", 0.0, 0.9, modality="imu")],
        }
        with self.assertRaises(ValueError):
            allocate_recruitment_slots(groups, extra_slots=2)


if __name__ == "__main__":
    unittest.main()
