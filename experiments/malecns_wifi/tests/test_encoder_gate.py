"""Tests for the real-encoder gate, using a stub encoder with a known answer."""

import numpy as np
import pytest

from malecns_wifi.encoder_gate import (
    average_precision,
    best_f1_threshold,
    build_hierarchy,
    candidate_signals,
    edge_errors,
    plan_chunks,
    score_signal,
)


def test_plan_aligns_parents_to_blocks_containing_each_child() -> None:
    plan = plan_chunks(600, fine_size=64, scales=(256, 1024))
    assert plan.fine_spans[0] == (0, 64)
    assert plan.fine_spans[-1] == (576, 600)
    # The first four fine chunks share the first 256-token parent.
    assert plan.parent_spans[0][:4] == ((0, 256),) * 4
    assert plan.parent_spans[0][4] == (256, 512)
    # Every fine chunk falls inside the single 1024-token parent.
    assert set(plan.parent_spans[1]) == {(0, 600)}


def test_plan_rejects_a_parent_smaller_than_its_children() -> None:
    with pytest.raises(ValueError, match="at least the fine chunk size"):
        plan_chunks(100, fine_size=64, scales=(32,))


def test_average_precision_on_a_known_ranking() -> None:
    # Perfect ranking: both positives on top.
    assert average_precision(np.asarray([4.0, 3.0, 2.0, 1.0]), np.asarray([1, 1, 0, 0])) == 1.0
    # Worst ranking: both positives at the bottom.
    worst = average_precision(np.asarray([4.0, 3.0, 2.0, 1.0]), np.asarray([0, 0, 1, 1]))
    assert worst == pytest.approx((1 / 3 + 2 / 4) / 2)
    # Undefined without both classes.
    assert np.isnan(average_precision(np.asarray([1.0, 2.0]), np.asarray([1, 1])))


def test_best_f1_threshold_recovers_a_separable_split() -> None:
    scores = np.asarray([0.1, 0.2, 0.9, 0.95])
    labels = np.asarray([0, 0, 1, 1])
    threshold, score = best_f1_threshold(scores, labels)
    assert score == 1.0
    assert 0.2 < threshold <= 0.9


def test_edge_errors_are_reported_in_tokens() -> None:
    scores = np.asarray([0.0, 0.0, 1.0, 1.0, 0.0, 0.0])
    labels = np.asarray([0, 0, 1, 1, 0, 0], dtype=bool)
    errors = edge_errors(scores, labels, fine_size=64)
    assert errors["start_error_tokens"] == 0
    assert errors["end_error_tokens"] == 0

    # Best F1 is at threshold 0.5 (predicting chunks 1-3), one chunk early at the
    # start and exactly right at the end.
    shifted = np.asarray([0.0, 1.0, 1.0, 0.5, 0.0, 0.0])
    errors = edge_errors(shifted, labels, fine_size=64)
    assert errors["start_error_tokens"] == 64
    assert errors["end_error_tokens"] == 0
    assert errors["predicted_chunks"] == 3


def test_best_f1_ties_prefer_the_tighter_region() -> None:
    """Predicting everything often ties on F1; it must not win."""
    scores = np.asarray([0.0, 1.0, 1.0, 0.0])
    labels = np.asarray([0, 1, 1, 0], dtype=bool)
    threshold, score = best_f1_threshold(scores, labels)
    assert score == 1.0 and threshold == 1.0


class _StubEncoder:
    """Embeds a text as [contains_marker, length, tag_appended] in a fixed basis.

    Deterministic and tiny, so the gate's plumbing can be tested end to end
    without a model. The marker makes exactly one region 'about' the tag.
    """

    def __init__(self, marker: str = "DISPOSITIVO"):
        self.marker = marker
        self.dimension = 8
        self.calls = 0

    def encode(self, texts):
        self.calls += 1
        rows = []
        for text in texts:
            vector = np.zeros(self.dimension, dtype=np.float32)
            vector[0] = 1.0
            vector[1] = float(self.marker in text)
            vector[2] = min(len(text) / 500.0, 1.0)
            vector[3] = float("__TAG__" in text)
            rows.append(vector)
        return np.stack(rows)


def test_build_hierarchy_encodes_parents_once_per_distinct_span() -> None:
    plan = plan_chunks(256, fine_size=64, scales=(256,))
    encoder = _StubEncoder()
    texts = {span: f"chunk {span}" for span in plan.fine_spans}
    texts.update({span: f"parent {span}" for span in plan.parent_spans[0]})

    hierarchy = build_hierarchy(lambda span: texts[span], plan, encoder, "__TAG__")

    assert hierarchy["child_plain"].shape == (4, encoder.dimension)
    # Parents are repeated to one row per fine chunk.
    assert hierarchy["parents_plain"][0].shape == (4, encoder.dimension)
    assert np.allclose(hierarchy["parents_plain"][0][0], hierarchy["parents_plain"][0][3])
    # Tagging changed the tagged pass and not the plain one.
    assert not np.allclose(hierarchy["child_plain"], hierarchy["child_tagged"])


def test_candidate_signals_cover_every_scale() -> None:
    plan = plan_chunks(512, fine_size=64, scales=(256, 512))
    encoder = _StubEncoder()
    texts = {span: f"body {span}" for span in plan.fine_spans}
    for spans in plan.parent_spans:
        texts.update({span: f"parent {span}" for span in spans})
    # One chunk is the dispositivo.
    texts[plan.fine_spans[5]] = "aqui esta o DISPOSITIVO da decisao"

    hierarchy = build_hierarchy(lambda span: texts[span], plan, encoder, "__TAG__")
    signals = candidate_signals(hierarchy)

    assert {"similarity", "flat_redundancy", "relational_redundancy", "meal_amount"} <= set(
        signals
    )
    assert "relational_scale_0" in signals and "relational_scale_1" in signals
    assert "differential_scale_0" in signals and "differential_scale_1" in signals
    for name, values in signals.items():
        assert values.shape == (len(plan.fine_spans),), name
        assert np.isfinite(values).all(), name


def test_score_signal_returns_every_metric() -> None:
    values = np.asarray([0.1, 0.9, 0.8, 0.2])
    labels = np.asarray([0, 1, 1, 0], dtype=bool)
    scored = score_signal("demo", values, labels, fine_size=64)
    assert scored["signal"] == "demo"
    assert scored["auprc"] == 1.0
    assert scored["best_f1"] == 1.0
    assert scored["point_biserial"] > 0
    assert scored["start_error_tokens"] == 0
