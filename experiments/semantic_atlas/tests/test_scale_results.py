from __future__ import annotations

from semantic_atlas.scale_results import aggregate_random_draws, apply_gate


def _result(draw: int, cross_1k: float, cross_100k: float, ceiling: float) -> dict:
    rows = []
    for n, cross in ((1_000, cross_1k), (100_000, cross_100k)):
        for k in (5, 10, 20):
            rows.append(
                {
                    "gallery_n": n,
                    "k": k,
                    "cross_model": {"raw_mknn": cross, "calibrated_mknn": cross},
                    "same_observer_gallery_jackknife": {
                        "qwen": {"calibrated_mknn": ceiling},
                        "minilm": {"calibrated_mknn": ceiling},
                    },
                    "category_purity": {
                        "qwen": 0.5,
                        "minilm": 0.5,
                        "shuffled_label_expected": 0.1,
                    },
                }
            )
    return {"gallery_kind": "stratified_random", "draw": draw, "rows": rows}


def _manifest() -> dict:
    return {
        "primary_gate": {
            "k": 5,
            "scale_stable": {"retention_gte": 0.75, "S100k_gte": 0.2},
            "collapse": {"retention_lte": 0.5, "S100k_lte": 0.1},
        },
        "observer_specific_gate": {
            "survives_if_Q_lte": 0.8,
            "near_ceiling_if_Q_gte": 0.9,
        },
    }


def test_gate_releases_only_when_both_conditions_hold():
    aggregated = aggregate_random_draws([_result(i, 0.4, 0.35, 0.6) for i in range(32)])
    gate = apply_gate(aggregated, _manifest())
    assert gate["scale_gate"] == "scale_stable"
    assert gate["observer_specific_gate"] == "observer_specific_gap_survives"
    assert gate["static_paper_released"] is True


def test_gate_kills_collapsed_curve():
    aggregated = aggregate_random_draws([_result(i, 0.4, 0.08, 0.6) for i in range(32)])
    gate = apply_gate(aggregated, _manifest())
    assert gate["scale_gate"] == "gallery_size_collapse"
    assert gate["static_paper_released"] is False
