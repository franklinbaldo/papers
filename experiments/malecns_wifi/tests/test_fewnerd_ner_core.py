from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from fewnerd_ner_core import (  # noqa: E402
    Entity,
    byte_labels_to_token_labels,
    canonical_byte_axis,
    exact_entity_prf,
    io_entities,
)
from fewnerd_semantic_cache import multiscale_token_fields, token_char_spans, window_bounds  # noqa: E402


def test_io_entities_split_on_o_and_type_change() -> None:
    assert io_entities([0, 1, 1, 0, 2, 2, 3, 3]) == (
        Entity(1, 3, 1),
        Entity(4, 6, 2),
        Entity(6, 8, 3),
    )


def test_utf8_byte_axis_roundtrips_token_labels() -> None:
    tokens = ["José", "visited", "Zürich"]
    labels = [51, 0, 14]
    axis = canonical_byte_axis(tokens, labels)
    assert axis.text == "José visited Zürich"
    assert axis.text.encode("utf-8")[axis.token_byte_spans[0][0] : axis.token_byte_spans[0][1]] == "José".encode("utf-8")
    assert byte_labels_to_token_labels(axis.byte_labels, axis.token_byte_spans) == tuple(labels)


def test_exact_entity_prf_requires_span_and_type() -> None:
    gold = [[0, 1, 1, 0, 2, 2]]
    pred = [[0, 1, 1, 0, 3, 3]]
    score = exact_entity_prf(gold, pred)
    assert score["true_positive"] == 1
    assert score["false_positive"] == 1
    assert score["false_negative"] == 1
    assert score["precision"] == 0.5
    assert score["recall"] == 0.5
    assert score["f1"] == 0.5


def test_identity_is_perfect() -> None:
    labels = [[0, 4, 4, 0], [7, 7, 0, 12]]
    assert exact_entity_prf(labels, labels)["f1"] == 1.0


def test_token_char_spans_account_for_prefix_and_spaces() -> None:
    assert token_char_spans(["New", "York"], prefix_chars=9) == ((9, 12), (13, 17))


def test_multiscale_window_is_deterministic_at_boundaries() -> None:
    assert window_bounds(0, 6, 4) == (0, 4)
    assert window_bounds(3, 6, 4) == (2, 6)
    assert window_bounds(5, 6, 4) == (2, 6)


def test_multiscale_fields_keep_one_unit_vector_per_token() -> None:
    vectors = np.eye(4, dtype=np.float32)
    fields = multiscale_token_fields(vectors, scales=(1, 2, 4))
    assert set(fields) == {1, 2, 4}
    assert all(value.shape == (4, 4) for value in fields.values())
    assert np.allclose(np.linalg.norm(fields[1], axis=1), 1.0)
    assert np.allclose(np.linalg.norm(fields[4], axis=1), 1.0)
