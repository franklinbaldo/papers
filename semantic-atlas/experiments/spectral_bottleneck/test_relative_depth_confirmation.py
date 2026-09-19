import unittest

from confidence_transfer import build_transfer_corpus
from confirmatory_endpoint import build_confirm_corpus
from relative_depth_confirmation import (
    RELATIVE_DEPTH,
    build_fresh_corpus,
    explicit_term_hits,
)
from real_model_experiment import build_corpus


class RelativeDepthConfirmationProtocolTests(unittest.TestCase):
    def test_relative_depth_rule_is_frozen(self):
        self.assertEqual(RELATIVE_DEPTH, 0.56)
        self.assertEqual(round(RELATIVE_DEPTH * 30), 17)
        self.assertEqual(round(RELATIVE_DEPTH * 32), 18)

    def test_fresh_corpus_reuses_no_prior_sentence(self):
        prior = {
            row.text
            for corpus in (build_corpus(), build_confirm_corpus(), build_transfer_corpus())
            for row in corpus
        }
        fresh = {row.text for row in build_fresh_corpus()}
        self.assertTrue(prior.isdisjoint(fresh))

    def test_registered_counts_and_balance(self):
        corpus = build_fresh_corpus()
        train = [row for row in corpus if row.split == "train"]
        test = [row for row in corpus if row.split == "test"]
        self.assertEqual(len(train), 96)
        self.assertEqual(len(test), 24)
        self.assertEqual(
            {label: sum(row.label == label for row in train) for label in (-1, 0, 1)},
            {-1: 32, 0: 32, 1: 32},
        )
        self.assertEqual(
            {label: sum(row.label == label for row in test) for label in (-1, 0, 1)},
            {-1: 8, 0: 8, 1: 8},
        )

    def test_fresh_implicit_test_has_no_forbidden_explicit_terms(self):
        self.assertEqual(explicit_term_hits(build_fresh_corpus()), {})


if __name__ == "__main__":
    unittest.main()
