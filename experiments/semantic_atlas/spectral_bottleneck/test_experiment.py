import unittest

import numpy as np

from experiment import (
    evaluate,
    knn_graph,
    make_bottleneck,
    make_continuous_control,
)


class SpectralBottleneckTests(unittest.TestCase):
    def test_knn_graph_is_symmetric_and_has_no_isolates(self):
        points, _ = make_bottleneck(0, n_lobe=50, n_bridge=20)
        graph = knn_graph(points, 8)
        difference = graph - graph.T
        self.assertEqual(difference.nnz, 0)
        degree = np.asarray(graph.sum(axis=1)).ravel()
        self.assertTrue(np.all(degree > 0))

    def test_planted_bottleneck_beats_continuous_control(self):
        positive_points, positive_labels = make_bottleneck(7)
        negative_points, negative_labels = make_continuous_control(
            10_007, len(positive_points)
        )
        positive = evaluate(positive_points, positive_labels, 12)
        negative = evaluate(negative_points, negative_labels, 12)

        self.assertLess(positive["conductance"], 0.6 * negative["conductance"])
        self.assertLess(positive["lambda2"], 0.6 * negative["lambda2"])
        self.assertGreaterEqual(positive["partition_accuracy"], 0.90)
        self.assertGreater(
            positive["left_to_right_hitting_time"],
            2.0 * negative["left_to_right_hitting_time"],
        )


if __name__ == "__main__":
    unittest.main()
