import unittest

import numpy as np

from confirmatory_endpoint import (
    CONFIRM_AXES,
    build_confirm_corpus,
    choose_connected_k,
)
from real_model_experiment import build_corpus


class ConfirmatoryCorpusTests(unittest.TestCase):
    def test_confirmation_reuses_no_first_smoke_sentence(self):
        old = {row.text for row in build_corpus()}
        new = {row.text for row in build_confirm_corpus()}
        self.assertTrue(old.isdisjoint(new))

    def test_contexts_and_paraphrases_are_held_out(self):
        corpus = build_confirm_corpus()
        for axis in CONFIRM_AXES:
            train = [r for r in corpus if r.axis == axis.name and r.split == "train"]
            test = [r for r in corpus if r.axis == axis.name and r.split == "test"]
            self.assertTrue(
                {r.context_id for r in train}.isdisjoint(
                    {r.context_id for r in test}
                )
            )
            self.assertTrue(
                {r.phrase_id for r in train}.isdisjoint(
                    {r.phrase_id for r in test}
                )
            )
            self.assertEqual({r.label for r in train}, {-1, 0, 1})
            self.assertEqual({r.label for r in test}, {-1, 0, 1})

    def test_connectivity_rule_uses_smallest_connected_candidate(self):
        corpus = build_confirm_corpus()
        axis = CONFIRM_AXES[0].name
        train_count = sum(
            1 for r in corpus if r.axis == axis and r.split == "train"
        )
        rng = np.random.default_rng(4)
        embeddings = rng.normal(size=(len(corpus), 5))
        embeddings /= np.linalg.norm(embeddings, axis=1, keepdims=True)
        k, trace = choose_connected_k(
            embeddings, corpus, axis, [2, 4, 8, 12, 20]
        )
        self.assertIn(k, {2, 4, 8, 12, 20})
        selected = next(item for item in trace if item["k"] == k)
        self.assertEqual(selected["components"], 1)
        self.assertEqual(train_count, 96)


if __name__ == "__main__":
    unittest.main()
