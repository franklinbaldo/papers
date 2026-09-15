import numpy as np
import scipy.sparse as sp

from dyad import DYAD_CONDITIONS, direct_gaze_distance, dyad_starts, simulate_direct_gaze_dyads
from visual_attractor import BrainConfig, Interface


def toy():
    # Two central visual receptors drive two descending readouts.
    rows = np.array([2, 3], dtype=np.int32)
    cols = np.array([0, 1], dtype=np.int32)
    data = np.array([1.0, 1.0], dtype=np.float32)
    graph = sp.csr_matrix((data, (rows, cols)), shape=(4, 4))
    interface = Interface(
        visual_indices=np.array([0, 1], dtype=np.int32),
        visual_azimuth=np.array([-0.03, 0.03], dtype=np.float32),
        descending_left=np.array([2], dtype=np.int32),
        descending_right=np.array([3], dtype=np.int32),
        steer_left=np.array([2], dtype=np.int32),
        steer_right=np.array([3], dtype=np.int32),
        forward_left=np.array([], dtype=np.int32),
        forward_right=np.array([], dtype=np.int32),
        courtship_indices=np.array([], dtype=np.int32),
    )
    return graph, interface


def test_direct_gaze_distance_shrinks_for_larger_apparent_target():
    assert direct_gaze_distance(0.25, 30.0) < direct_gaze_distance(0.25, 15.0)


def test_dyad_starts_are_deterministic_and_registered_distance():
    distance = direct_gaze_distance(0.25, 30.0)
    a1, b1 = dyad_starts(pairs=4, distance=distance, seed=7)
    a2, b2 = dyad_starts(pairs=4, distance=distance, seed=7)
    assert a1 == a2
    assert b1 == b2
    for a, b in zip(a1, b1, strict=True):
        np.testing.assert_allclose(np.hypot(a.x - b.x, a.y - b.y), distance)


def test_reciprocal_uses_visual_channel_and_blank_is_zero():
    graph, interface = toy()
    distance = direct_gaze_distance(0.25, 30.0)
    starts_a, starts_b = dyad_starts(pairs=2, distance=distance, seed=9)
    result = simulate_direct_gaze_dyads(
        graph,
        interface,
        starts_a,
        starts_b,
        steps=20,
        brain=BrainConfig(spectral_scale=1.0, visual_scale=1.0, prime_scale=0.0),
        device="cpu",
    )
    summary = result.condition_summary()
    assert tuple(summary) == DYAD_CONDITIONS
    assert summary["reciprocal"]["mean_visual_rms"] > 0.0
    assert summary["reciprocal"]["mean_receptor_rms"] > 0.0
    assert summary["blank_pair"]["mean_visual_rms"] == 0.0
    assert summary["blank_pair"]["mean_receptor_rms"] == 0.0


def test_conditions_reuse_exact_initial_pair_distances():
    graph, interface = toy()
    distance = direct_gaze_distance(0.25, 30.0)
    starts_a, starts_b = dyad_starts(pairs=3, distance=distance, seed=11)
    result = simulate_direct_gaze_dyads(
        graph,
        interface,
        starts_a,
        starts_b,
        steps=4,
        brain=BrainConfig(spectral_scale=1.0, visual_scale=1.0, prime_scale=0.0),
        device="cpu",
    )
    p = result.pairs_per_condition
    base = result.metrics["initial_pair_distance"][:p]
    for i in range(1, len(DYAD_CONDITIONS)):
        np.testing.assert_allclose(
            result.metrics["initial_pair_distance"][i * p : (i + 1) * p],
            base,
        )
