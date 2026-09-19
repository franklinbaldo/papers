import unittest

from colony import SpecialistReport
from delayed_trust import FEATURE_DIM, DelayedTrustModel, delayed_trust_features


class DelayedTrustTests(unittest.TestCase):
    def _report(self, identifier, value, *, modality, age_ms=20.0, confidence=0.9):
        return SpecialistReport(
            identifier,
            "dynamic-scalar",
            value,
            confidence,
            age_ms=age_ms,
            modality=modality,
        )

    def test_features_are_generic_across_declared_modalities(self):
        existing = [
            self._report("lidar-a", 0.10, modality="lidar"),
            self._report("lidar-b", 0.12, modality="lidar"),
        ]
        candidate = self._report("lidar-c", 0.11, modality="lidar")
        other = [
            self._report("obd-a", 0.09, modality="obd"),
            self._report("obd-b", 0.10, modality="obd"),
        ]
        features = delayed_trust_features(existing, candidate, other)
        self.assertEqual(len(features), FEATURE_DIM)
        self.assertTrue(all(0.0 <= value <= 1.0 for value in features))

    def test_cross_modal_reference_must_be_independent(self):
        existing = [self._report("imu-a", 0.0, modality="imu")]
        candidate = self._report("imu-b", 0.1, modality="imu")
        same_modality = [self._report("imu-c", 0.0, modality="imu")]
        with self.assertRaises(ValueError):
            delayed_trust_features(existing, candidate, same_modality)

    def test_online_update_can_learn_delayed_binary_teacher(self):
        model = DelayedTrustModel(feature_dim=2, learning_rate=0.1, l2=0.0)
        good = (1.0, 1.0)
        bad = (1.0, -1.0)
        for _ in range(100):
            model.update(good, 1.0)
            model.update(bad, 0.0)
        self.assertGreater(model.probability(good), 0.8)
        self.assertLess(model.probability(bad), 0.2)

    def test_threshold_validation(self):
        model = DelayedTrustModel(feature_dim=1)
        with self.assertRaises(ValueError):
            model.should_trust((1.0,), threshold=1.1)


if __name__ == "__main__":
    unittest.main()
