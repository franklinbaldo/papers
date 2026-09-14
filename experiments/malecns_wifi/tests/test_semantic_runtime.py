import numpy as np
import pytest
import scipy.sparse as sp

from malecns_wifi.semantic_runtime import direct_semantic_features, run_semantic_food


def _operator() -> sp.csr_matrix:
    # 0,1 sensory; 2,3 food candidates; 4,5 recurrent/readout.
    dense = np.zeros((6, 6), dtype=np.float32)
    dense[4, 0] = 0.7
    dense[4, 2] = 0.9
    dense[5, 1] = 0.6
    dense[5, 3] = 0.8
    dense[5, 4] = 0.5
    return sp.csr_matrix(dense)


def test_zero_food_matches_a_no_food_trajectory() -> None:
    semantic = np.asarray([[1.0, 0.0], [0.0, 1.0], [0.5, 0.5]], dtype=np.float32)
    zero = np.zeros((3, 2), dtype=np.float32)

    result = run_semantic_food(
        _operator(), semantic, np.asarray([0, 1]), zero, np.asarray([2, 3]), np.asarray([4, 5])
    )
    repeated = run_semantic_food(
        _operator(), semantic, np.asarray([0, 1]), np.zeros_like(zero), np.asarray([2, 3]), np.asarray([4, 5])
    )

    assert np.allclose(result.readout_states, repeated.readout_states)
    assert result.food_rms == 0.0


def test_food_changes_the_readout_and_can_persist_through_recurrence() -> None:
    semantic = np.zeros((4, 2), dtype=np.float32)
    food = np.zeros((4, 2), dtype=np.float32)
    food[1, 0] = 1.0

    fed = run_semantic_food(
        _operator(), semantic, np.asarray([0, 1]), food, np.asarray([2, 3]), np.asarray([4, 5]), leak=1.0
    )
    unfed = run_semantic_food(
        _operator(), semantic, np.asarray([0, 1]), np.zeros_like(food), np.asarray([2, 3]), np.asarray([4, 5]), leak=1.0
    )

    assert not np.allclose(fed.readout_states, unfed.readout_states)
    assert fed.readout_states[1, 0] != pytest.approx(0.0)
    # Node 4 feeds node 5, so the one-step food pulse leaves a later recurrent trace.
    assert fed.readout_states[2, 1] != pytest.approx(0.0)


def test_same_food_values_can_be_replayed_at_a_different_location() -> None:
    semantic = np.zeros((2, 2), dtype=np.float32)
    drive = np.asarray([[0.2, 0.8], [0.7, 0.3]], dtype=np.float32)

    anatomical = run_semantic_food(
        _operator(), semantic, np.asarray([0, 1]), drive, np.asarray([2, 3]), np.asarray([4, 5])
    )
    swapped = run_semantic_food(
        _operator(), semantic, np.asarray([0, 1]), drive, np.asarray([3, 2]), np.asarray([4, 5])
    )

    # Input energy is byte-identical; only anatomical location changes.
    assert anatomical.food_rms == pytest.approx(swapped.food_rms)
    assert not np.allclose(anatomical.readout_states, swapped.readout_states)


def test_direct_control_uses_exact_same_streams_without_operator() -> None:
    semantic = np.asarray([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
    food = np.asarray([[0.2], [0.8]], dtype=np.float32)
    features = direct_semantic_features(semantic, food)

    joined = np.concatenate([semantic, food], axis=1)
    expected = np.concatenate([joined[-1], joined.mean(axis=0)])
    assert np.allclose(features, expected)


def test_runtime_requires_synchronised_streams() -> None:
    with pytest.raises(ValueError, match="same number of time steps"):
        run_semantic_food(
            _operator(),
            np.zeros((3, 2), dtype=np.float32),
            np.asarray([0, 1]),
            np.zeros((2, 2), dtype=np.float32),
            np.asarray([2, 3]),
            np.asarray([4, 5]),
        )
