import numpy as np

from synergy_geometry import (
    RidgeRelationDecoder,
    balanced_accuracy,
    paired_bootstrap_accuracy_difference,
)


def test_ridge_relation_decoder_learns_simple_relation():
    x = np.array([[-2.0], [-1.0], [1.0], [2.0]])
    y = np.array([0, 0, 1, 1])
    decoder = RidgeRelationDecoder(alpha=0.01).fit(x, y)
    pred = decoder.predict(x)
    assert balanced_accuracy(y, pred) == 1.0


def test_paired_bootstrap_reports_positive_difference():
    truth = np.array([0, 0, 0, 0, 1, 1, 1, 1] * 6)
    better = truth.copy()
    worse = np.zeros_like(truth)
    ci = paired_bootstrap_accuracy_difference(
        truth, better, worse, n_boot=300, seed=3
    )
    assert ci.observed == 0.5
    assert ci.lower > 0.0
    assert ci.upper <= 0.5
