import numpy as np

from semantic_atlas.relational_dynamics import (
    churn_trace,
    cosine_scores,
    csls_scores,
    empirical_mutual_proximity_scores,
    hubness_summary,
    rankings_from_scores,
    trace_divergence,
)


def test_hubness_controls_are_symmetric_and_finite_off_diagonal():
    rng = np.random.default_rng(7)
    scores = cosine_scores(rng.normal(size=(12, 6)))
    for adjusted in (
        csls_scores(scores, neighborhood=4),
        empirical_mutual_proximity_scores(scores),
    ):
        assert adjusted.shape == scores.shape
        assert np.allclose(adjusted, adjusted.T, equal_nan=True)
        assert np.all(np.isneginf(np.diag(adjusted)))
        mask = ~np.eye(len(adjusted), dtype=bool)
        assert np.all(np.isfinite(adjusted[mask]))


def test_churn_is_zero_when_added_points_cannot_enter_knn():
    n = 8
    scores = np.full((n, n), -10.0)
    np.fill_diagonal(scores, -np.inf)
    for i in range(4):
        for j in range(4):
            if i != j:
                scores[i, j] = 1.0 - 0.1 * abs(i - j)
    trace = churn_trace(scores, np.arange(n), k=2, initial_n=4, batch_size=2)
    assert trace["transitions"][0]["mean_churn"] == 0.0


def test_churn_detects_new_better_neighbor():
    n = 6
    scores = np.full((n, n), -5.0)
    np.fill_diagonal(scores, -np.inf)
    scores[0, 1] = scores[1, 0] = 0.8
    scores[0, 2] = scores[2, 0] = 0.7
    scores[0, 3] = scores[3, 0] = 0.99
    trace = churn_trace(scores, np.arange(n), k=1, initial_n=3, batch_size=1)
    first = trace["transitions"][0]
    assert first["mean_churn"] > 0.0
    assert first["normalized_hazard"] > 0.0


def test_identical_models_have_zero_dynamic_divergence():
    rng = np.random.default_rng(11)
    scores = cosine_scores(rng.normal(size=(24, 8)))
    order = rng.permutation(24)
    a = churn_trace(scores, order, k=3, initial_n=8, batch_size=4)
    b = churn_trace(scores, order, k=3, initial_n=8, batch_size=4)
    assert trace_divergence(a, b) == 0.0


def test_hubness_summary_counts_k_occurrences():
    n = 10
    scores = np.zeros((n, n))
    np.fill_diagonal(scores, -np.inf)
    for i in range(1, n):
        scores[i, 0] = 10.0
        scores[0, i] = 1.0
    summary = hubness_summary(rankings_from_scores(scores), k=1)
    assert summary["max_k_occurrence"] >= n - 1
    assert summary["k_occurrence_skewness"] > 1.0
