import json
from pathlib import Path


def _manifest() -> dict:
    path = Path(__file__).parents[1] / "model_backed_a_v1.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_model_backed_a_revisions_are_pinned():
    manifest = _manifest()
    for key in ("reference_observer", "transfer_observer", "generator"):
        revision = manifest[key]["revision"]
        assert revision
        assert revision != "main"


def test_model_backed_a_has_enough_calibration_rows_for_srf_dimension():
    manifest = _manifest()
    assert manifest["corpus"]["calibration_count"] >= manifest["srf_dim"]


def test_model_backed_a_splits_are_disjoint_by_construction():
    manifest = _manifest()
    corpus = manifest["corpus"]
    assert corpus["calibration_count"] > 0
    assert corpus["heldout_count"] > 0
    assert corpus["trajectory_count"] > 0
    assert "first 80 calibration, next 24 heldout, next 12 trajectory" in corpus["selection"]


def test_model_backed_a_negative_control_is_required():
    manifest = _manifest()
    assert manifest["gate"]["require_shuffled_worse_than_paired"] is True
