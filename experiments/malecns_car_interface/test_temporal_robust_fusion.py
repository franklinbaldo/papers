from __future__ import annotations

import unittest

from temporal_robust_fusion import (
    fuse,
    robust_fusion_weight,
    transport_by_reference_delta,
)


class TemporalRobustFusionTests(unittest.TestCase):
    def test_transport_uses_only_observed_reference_delta(self):
        self.assertAlmostEqual(transport_by_reference_delta(10.0, 9.5, 11.0), 11.5)

    def test_age_contraction_is_more_conservative_for_same_residual(self):
        fixed = robust_fusion_weight(
            age_s=1.0,
            matched_time_residual=0.8,
            base_scale=0.75,
            age_power=0.0,
        )
        contracted = robust_fusion_weight(
            age_s=1.0,
            matched_time_residual=0.8,
            base_scale=0.75,
            age_power=1.0,
        )
        self.assertLess(contracted, fixed)

    def test_zero_age_matches_fixed_and_age_contracted_radius(self):
        fixed = robust_fusion_weight(
            age_s=0.0,
            matched_time_residual=1.0,
            base_scale=0.75,
            age_power=0.0,
        )
        contracted = robust_fusion_weight(
            age_s=0.0,
            matched_time_residual=1.0,
            base_scale=0.75,
            age_power=1.0,
        )
        self.assertAlmostEqual(fixed, contracted)

    def test_fusion_stays_between_two_inputs_for_nonnegative_weight(self):
        value = fuse(10.0, 14.0, 0.25)
        self.assertGreaterEqual(value, 10.0)
        self.assertLessEqual(value, 14.0)


if __name__ == "__main__":
    unittest.main()
