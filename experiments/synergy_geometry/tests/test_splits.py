import copy

import pytest

from synergy_geometry import SplitRegistry, manifest_sha256, validate_manifest


def manifest():
    return {
        "calibration": [{"id": "c0", "a": "a0", "b": "b0"}],
        "train": [
            {"id": "t0", "a": "a0", "b": "b0"},
            {"id": "t1", "a": "a0", "b": "b1"},
            {"id": "t2", "a": "a1", "b": "b0"},
        ],
        "interaction_test": [
            {"id": "i0", "a": "a0", "b": "b1"},
            {"id": "i1", "a": "a1", "b": "b0"},
        ],
        "composition_test": [{"id": "p0", "a": "a1", "b": "b1"}],
        "relation_holdout": [],
    }


def test_manifest_separates_gate1_and_gate2_and_hash_is_stable():
    data = manifest()
    validate_manifest(data)
    first = manifest_sha256(data)

    reordered = {key: value for key, value in reversed(list(data.items()))}
    assert manifest_sha256(reordered) == first

    registry = SplitRegistry(data)
    assert registry.rows("interaction_test", purpose="confirm_gate1")[0]["id"] == "i0"
    assert registry.rows("composition_test", purpose="confirm_gate2")[0]["id"] == "p0"


@pytest.mark.parametrize("purpose", ["fit", "tune", "confirm_gate1"])
def test_composition_test_is_guarded_against_early_use(purpose):
    registry = SplitRegistry(manifest())
    with pytest.raises(PermissionError):
        registry.rows("composition_test", purpose=purpose)


def test_composition_test_must_contain_unseen_combinations():
    data = copy.deepcopy(manifest())
    data["composition_test"] = [{"id": "p0", "a": "a0", "b": "b1"}]
    with pytest.raises(ValueError, match="contains train combinations"):
        validate_manifest(data)


def test_confirmatory_factor_identities_must_be_seen_in_train():
    data = copy.deepcopy(manifest())
    data["composition_test"] = [{"id": "p0", "a": "a2", "b": "b1"}]
    with pytest.raises(ValueError, match="factor identities unseen in train"):
        validate_manifest(data)


def test_example_ids_cannot_cross_split_roles():
    data = copy.deepcopy(manifest())
    data["composition_test"][0]["id"] = "t0"
    with pytest.raises(ValueError, match="appears in both"):
        validate_manifest(data)
