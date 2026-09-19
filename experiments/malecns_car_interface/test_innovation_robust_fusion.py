import unittest

from innovation_robust_fusion import (
    OnlineInnovationScale,
    covariance_relative_precision,
    innovation_huber_weight,
)


class InnovationFusionTests(unittest.TestCase):
    def test_same_standardized_residual_gives_same_weight(self) -> None:
        a = innovation_huber_weight(
            age_s=0.5,
            matched_time_residual=0.5,
            innovation_sigma=0.5,
        )
        b = innovation_huber_weight(
            age_s=0.5,
            matched_time_residual=1.0,
            innovation_sigma=1.0,
        )
        self.assertAlmostEqual(a, b)

    def test_scale_adapts_but_respects_ceiling(self) -> None:
        scale = OnlineInnovationScale(
            initial_sigma=0.5,
            floor_sigma=0.25,
            ceiling_sigma=1.0,
        )
        before = scale.sigma
        for _ in range(50):
            scale.observe(10.0)
        self.assertGreater(scale.sigma, before)
        self.assertLessEqual(scale.sigma, 1.0)

    def test_covariance_merit_starts_from_nominal_precision_ratio(self) -> None:
        precision = covariance_relative_precision(
            raw_innovation_sigma=(0.2**2 + 0.5**2) ** 0.5,
            reference_nominal_sigma=0.2,
            candidate_nominal_sigma=0.5,
        )
        self.assertAlmostEqual(precision, 0.16)

    def test_excess_innovation_increases_candidate_merit_with_cap(self) -> None:
        low = covariance_relative_precision(
            raw_innovation_sigma=0.55,
            reference_nominal_sigma=0.2,
            candidate_nominal_sigma=0.5,
        )
        high = covariance_relative_precision(
            raw_innovation_sigma=2.0,
            reference_nominal_sigma=0.2,
            candidate_nominal_sigma=0.5,
        )
        self.assertGreater(high, low)
        self.assertLessEqual(high, 1.0)


if __name__ == "__main__":
    unittest.main()
