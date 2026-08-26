from __future__ import annotations

import numpy as np

from semantic_atlas.gallery_scale import (
    aggregate_curve,
    apply_static_gate,
    deterministic_subset,
    markdown_format_view,
    mknn_for_correspondence,
    permutation_calibration,
)


def test_markdown_format_view_preserves_lexical_content_and_removes_markup():
    source = "---\n# Title\n- **Alpha** and [Beta](https://example.test).\n```py\ncode()\n```"
    viewed = markdown_format_view(source)

    for token in ("Title", "Alpha", "Beta", "https://example.test", "code()"):
        assert token in viewed
    for marker in ("**", "[Beta]", "```", "# Title"):
        assert marker not in viewed


def test_deterministic_subset_is_stable_and_replicates_change():
    paths = [f"doc-{index}.md" for index in range(30)]
    first = deterministic_subset(paths, 10, replicate=0, seed=7)
    again = deterministic_subset(paths, 10, replicate=0, seed=7)
    second = deterministic_subset(paths, 10, replicate=1, seed=7)

    assert np.array_equal(first, again)
    assert len(np.unique(first)) == 10
    assert not np.array_equal(first, second)


def test_mknn_identity_is_one_and_permutation_reduces_it():
    rank = np.asarray(
        [
            [1, 2, 3, 4, 0],
            [0, 2, 3, 4, 1],
            [1, 3, 0, 4, 2],
            [2, 4, 1, 0, 3],
            [3, 2, 1, 0, 4],
        ],
        dtype=np.int64,
    )
    identity = mknn_for_correspondence(rank, rank, np.arange(5), [1, 2])
    permuted = mknn_for_correspondence(rank, rank, np.asarray([2, 4, 1, 0, 3]), [1, 2])

    assert np.allclose(identity, 1.0)
    assert np.any(permuted < 1.0)


def test_permutation_calibration_reports_raw_and_calibrated_scores():
    rank = np.asarray(
        [
            [1, 2, 3, 4, 0],
            [0, 2, 3, 4, 1],
            [1, 3, 0, 4, 2],
            [2, 4, 1, 0, 3],
            [3, 2, 1, 0, 4],
        ],
        dtype=np.int64,
    )
    permutations = [
        np.asarray([1, 0, 2, 4, 3]),
        np.asarray([2, 4, 1, 0, 3]),
        np.asarray([4, 3, 2, 1, 0]),
    ]
    result = permutation_calibration(rank, rank, ks=[1], permutations=permutations)

    assert result["1"]["raw_mknn"] == 1.0
    assert 0.0 <= result["1"]["calibrated_mknn"] <= 1.0
    assert result["1"]["null_mean"] < 1.0


def _row(n: int, pair: str, calibrated: float) -> dict:
    return {
        "gallery_n": n,
        "pair": pair,
        "k": 5,
        "raw_mknn": calibrated,
        "null_mean": 0.05,
        "null_q95": 0.08,
        "p_upper_plus1": 0.001,
        "calibrated_mknn": calibrated,
    }


def test_gate_has_terminal_non_defensive_decisions():
    rows = []
    for n, cross in ((116, 0.40), (176, 0.38), (256, 0.36), (382, 0.34)):
        rows.extend(
            [
                _row(n, "cross_model", cross),
                _row(n, "reference_format_stability", 0.80),
                _row(n, "transfer_format_stability", 0.75),
            ]
        )
    gate = {
        "primary_k": 5,
        "anchor_gallery_n": 116,
        "full_gallery_n": 382,
        "minimum_full_calibrated_mknn": 0.20,
        "minimum_retention_vs_anchor": 0.75,
        "minimum_same_observer_ceiling": 0.50,
        "minimum_same_observer_gap": 0.10,
        "observer_gap_final_points": 3,
    }
    result = apply_static_gate(aggregate_curve(rows), gate)
    assert result["decision"] == "static_shared_but_observer_specific_structure"

    collapsed = [dict(row) for row in rows]
    for row in collapsed:
        if row["pair"] == "cross_model" and row["gallery_n"] == 382:
            row["calibrated_mknn"] = 0.10
    result = apply_static_gate(aggregate_curve(collapsed), gate)
    assert result["decision"] == "small_gallery_artifact"

    invalid_control = [dict(row) for row in rows]
    for row in invalid_control:
        if row["pair"].endswith("format_stability") and row["gallery_n"] >= 176:
            row["calibrated_mknn"] = 0.40
    result = apply_static_gate(aggregate_curve(invalid_control), gate)
    assert result["decision"] == "invalid_same_observer_stability_control"
