import unittest

from colony import (
    SpecialistReport,
    age_spread_ms,
    confidence_weighted_value,
    consensus_weighted_value,
    disagreement,
    freshness_weighted_value,
    median_value,
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
        self.assertAlmostEqual(
            freshness_weighted_value(reports, half_life_ms=150.0),
            0.4,
        )

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
        calm = [
            SpecialistReport("a", "speed", 10.0, 1.0),
            SpecialistReport("b", "speed", 10.1, 1.0),
        ]
        conflict = calm + [SpecialistReport("c", "speed", 30.0, 1.0)]
        self.assertGreater(disagreement(conflict), disagreement(calm))

    def test_age_spread_is_a_lawful_coordinator_signal(self):
        reports = [
            SpecialistReport("a", "speed", 10.0, 1.0, age_ms=15.0),
            SpecialistReport("b", "speed", 10.1, 1.0, age_ms=85.0),
        ]
        self.assertEqual(age_spread_ms(reports), 70.0)


if __name__ == "__main__":
    unittest.main()
