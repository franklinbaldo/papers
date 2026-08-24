from __future__ import annotations

import unittest

from core import (
    count_lifts_of_c2_with_duplicate_zero,
    default_hypothesis_class,
    transport_preserves_operation,
    transported_table,
    version_space,
)


class TruthPreservingRepresentationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.groups = default_hypothesis_class()

    def test_arbitrary_bijective_codes_preserve_c4_exactly(self) -> None:
        c4 = self.groups[0]
        labels = (37, 12, 83, 51)
        self.assertTrue(transport_preserves_operation(c4, labels))
        self.assertEqual(
            transported_table(c4, labels),
            {
                37: (37, 12, 83, 51),
                12: (12, 83, 51, 37),
                83: (83, 51, 37, 12),
                51: (51, 37, 12, 83),
            },
        )

    def test_local_i_truth_does_not_identify_ambient_group(self) -> None:
        self.assertEqual(
            version_space(self.groups, require_i_like=True),
            ("C4", "C8", "D4"),
        )

    def test_background_restriction_can_make_same_truth_identifying(self) -> None:
        self.assertEqual(
            version_space(self.groups, require_i_like=True, carrier_order=4),
            ("C4",),
        )

    def test_commutativity_still_leaves_ambiguity(self) -> None:
        self.assertEqual(
            version_space(self.groups, require_i_like=True, require_commutative=True),
            ("C4", "C8"),
        )

    def test_noninjective_decoder_allows_many_latent_lifts(self) -> None:
        self.assertEqual(
            count_lifts_of_c2_with_duplicate_zero(),
            {
                "labeled_lifts": 32,
                "magma_isomorphism_classes": 16,
                "associative_lifts": 4,
                "semigroup_isomorphism_classes": 2,
                "monoid_lifts": 2,
                "monoid_isomorphism_classes": 1,
            },
        )


if __name__ == "__main__":
    unittest.main()
