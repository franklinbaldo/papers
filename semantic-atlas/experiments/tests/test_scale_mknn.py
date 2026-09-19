from __future__ import annotations

import numpy as np

from semantic_atlas.scale_mknn import (
    analytic_null,
    exact_topk,
    jackknife_masks,
    mknn,
    stratified_gallery,
)


def test_stratified_gallery_is_exact_deterministic_and_changes_by_draw():
    ids = [f"id-{i}" for i in range(30)]
    categories = ["a"] * 18 + ["b"] * 12
    first = stratified_gallery(ids, categories, 10, draw=0, seed=7)
    again = stratified_gallery(ids, categories, 10, draw=0, seed=7)
    second = stratified_gallery(ids, categories, 10, draw=1, seed=7)
    assert np.array_equal(first, again)
    assert not np.array_equal(first, second)
    assert sum(categories[index] == "a" for index in first) == 6
    assert sum(categories[index] == "b" for index in first) == 4


def test_exact_topk_matches_bruteforce():
    rng = np.random.default_rng(3)
    matrix = rng.normal(size=(20, 7)).astype(np.float32)
    matrix /= np.linalg.norm(matrix, axis=1, keepdims=True)
    gallery = np.asarray([1, 3, 4, 8, 9, 12, 15, 19], dtype=np.int64)
    observed = exact_topk(matrix, gallery, k=3, query_block=2, candidate_block=3)
    scores = matrix[gallery] @ matrix[gallery].T
    np.fill_diagonal(scores, -np.inf)
    expected = np.argsort(-scores, axis=1, kind="stable")[:, :3]
    assert np.array_equal(observed, expected)


def test_exact_topk_respects_query_and_candidate_masks():
    matrix = np.eye(6, dtype=np.float32)
    matrix[0, 1] = matrix[1, 0] = 0.9
    matrix[0, 2] = matrix[2, 0] = 0.8
    matrix /= np.linalg.norm(matrix, axis=1, keepdims=True)
    mask = np.asarray([True, False, True, True, True, True])
    found = exact_topk(
        matrix, np.arange(6), k=1, queries=np.asarray([0]), candidate_mask=mask
    )
    assert found[0, 0] == 2


def test_mknn_and_analytic_null_boundaries():
    neighbors = np.asarray([[1, 2], [0, 2], [0, 1]], dtype=np.int64)
    assert mknn(neighbors, neighbors, 2) == 1.0
    null = analytic_null(100, 5)
    assert 0 < null["mean"] < null["q95_independent_query_approx"] < 1


def test_jackknife_always_retains_anchors():
    ids = [f"id-{i}" for i in range(100)]
    anchors, left, right = jackknife_masks(
        ids, draw=2, seed=9, anchor_fraction=0.2, retention=0.95
    )
    assert len(anchors) == 20
    assert np.all(left[anchors]) and np.all(right[anchors])
