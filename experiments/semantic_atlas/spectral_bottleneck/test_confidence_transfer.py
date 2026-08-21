import unittest

from confidence_transfer import (
    AXIS,
    build_transfer_corpus,
    explicit_term_hits,
)
from confirmatory_endpoint import build_confirm_corpus


class ConfidenceTransferProtocolTests(unittest.TestCase):
    def test_implicit_test_avoids_registered_explicit_terms(self):
        corpus = build_transfer_corpus()
        self.assertEqual(explicit_term_hits(corpus), {})

    def test_registered_sample_counts(self):
        corpus = build_transfer_corpus()
        train = [row for row in corpus if row.axis == AXIS and row.split == "train"]
        test = [row for row in corpus if row.axis == AXIS and row.split == "test"]
        self.assertEqual(len(train), 96)
        self.assertEqual(len(test), 24)
        self.assertEqual(
            {label: sum(row.label == label for row in test) for label in (-1, 0, 1)},
            {-1: 8, 0: 8, 1: 8},
        )

    def test_implicit_test_sentences_are_new(self):
        confirmation = {row.text for row in build_confirm_corpus()}
        transfer_test = {
            row.text for row in build_transfer_corpus() if row.split == "test"
        }
        self.assertTrue(confirmation.isdisjoint(transfer_test))

    def test_transfer_train_is_exact_confidence_confirmation_train(self):
        source = sorted(
            row.text
            for row in build_confirm_corpus()
            if row.axis == "confidence_confirm" and row.split == "train"
        )
        transfer = sorted(
            row.text
            for row in build_transfer_corpus()
            if row.axis == AXIS and row.split == "train"
        )
        self.assertEqual(source, transfer)


if __name__ == "__main__":
    unittest.main()
