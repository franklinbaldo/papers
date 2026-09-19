import unittest

from colony_fault_ablation import run_fault_ablation


class ColonyFaultAblationTests(unittest.TestCase):
    def test_redundancy_beats_single_specialist_under_calibrated_faults(self):
        result = run_fault_ablation(trials=2_000, fault_probability=0.2)
        self.assertLess(result.median_mae, result.single_mae)
        self.assertLess(result.confidence_weighted_mae, result.median_mae)

    def test_overconfident_faults_break_confidence_weighting(self):
        calibrated = run_fault_ablation(
            trials=2_000,
            fault_probability=0.2,
            faulty_confidence=0.15,
        )
        overconfident = run_fault_ablation(
            trials=2_000,
            fault_probability=0.2,
            faulty_confidence=0.95,
        )
        self.assertGreater(
            overconfident.confidence_weighted_mae,
            calibrated.confidence_weighted_mae,
        )
        self.assertAlmostEqual(overconfident.median_mae, calibrated.median_mae)


if __name__ == "__main__":
    unittest.main()
