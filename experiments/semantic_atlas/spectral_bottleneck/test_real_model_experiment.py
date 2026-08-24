import unittest

import numpy as np

from real_model_experiment import (
    AXES,
    bridge_ratio,
    build_corpus,
    knn_graph_with_sigma,
    orient_fiedler,
    pole_accuracy,
    spectral_coordinate,
    weighted_extension,
)


class CorpusTests(unittest.TestCase):
    def test_train_and_test_hold_out_contexts_and_phrases(self):
        corpus = build_corpus()
        for axis in AXES:
            train = [row for row in corpus if row.axis == axis.name and row.split == "train"]
            test = [row for row in corpus if row.axis == axis.name and row.split == "test"]
            self.assertTrue(train)
            self.assertTrue(test)
            self.assertTrue(
                {row.context_id for row in train}.isdisjoint(
                    {row.context_id for row in test}
                )
            )
            self.assertTrue(
                {row.phrase_id for row in train}.isdisjoint(
                    {row.phrase_id for row in test}
                )
            )
            self.assertEqual({row.label for row in train}, {-1, 0, 1})
            self.assertEqual({row.label for row in test}, {-1, 0, 1})


class SpectralHelperTests(unittest.TestCase):
    def test_extension_recovers_simple_two_pole_geometry(self):
        rng = np.random.default_rng(7)
        negative = rng.normal(loc=(-2.0, 0.0), scale=0.25, size=(30, 2))
        bridge = rng.normal(loc=(0.0, 0.0), scale=(0.20, 0.08), size=(8, 2))
        positive = rng.normal(loc=(2.0, 0.0), scale=0.25, size=(30, 2))
        train = np.vstack([negative, bridge, positive])
        labels = np.asarray([-1] * 30 + [0] * 8 + [1] * 30)

        graph, sigma = knn_graph_with_sigma(train, 8)
        _, _, fiedler, _ = spectral_coordinate(graph)
        oriented, train_accuracy = orient_fiedler(fiedler, labels)
        self.assertGreaterEqual(train_accuracy, 0.90)

        test = np.asarray(
            [
                [-2.1, 0.05],
                [-1.8, -0.05],
                [0.0, 0.02],
                [1.8, 0.02],
                [2.1, -0.03],
            ]
        )
        test_labels = np.asarray([-1, -1, 0, 1, 1])
        scores = weighted_extension(train, oriented, test, k=8, sigma=sigma)
        self.assertEqual(pole_accuracy(scores, test_labels), 1.0)
        self.assertLess(bridge_ratio(scores, test_labels), 0.8)


if __name__ == "__main__":
    unittest.main()
