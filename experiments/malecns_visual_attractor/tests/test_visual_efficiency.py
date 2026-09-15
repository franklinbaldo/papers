import numpy as np

from visual_efficiency import (
    efficiency_curriculum,
    fixed_spatial_permutation,
    matched_offset_starts,
    normalize_energy_numpy,
    strongest_control_advantage,
)


def test_curriculum_is_strictly_decreasing():
    stages = efficiency_curriculum((0.12, 0.06, 0.03), heading_offset_deg=45.0)
    assert [stage.budget for stage in stages] == [0.12, 0.06, 0.03]
    assert all(stage.heading_offset_deg == 45.0 for stage in stages)


def test_offset_starts_are_exactly_off_target():
    x, y, heading = matched_offset_starts(
        flies=8,
        radius=0.75,
        seed=7,
        heading_offset_deg=45.0,
    )
    target = np.arctan2(-y, -x)
    error = np.angle(np.exp(1j * (heading - target)))
    np.testing.assert_allclose(np.abs(error), np.deg2rad(45.0), atol=1e-12)


def test_energy_normalization_uses_only_resolved_receptors():
    values = np.asarray([0.2, 0.8, 0.4, 0.9, 0.3, 0.7], dtype=np.float32)[:, None]
    resolved = np.asarray([True, True, False, True, False, True])
    out = normalize_energy_numpy(values, resolved, 0.25)
    assert out.dtype == np.float32
    np.testing.assert_allclose(out[~resolved], 0.0)
    assert abs(float(out[resolved].mean()) - 0.25) < 1e-4
    assert np.all((out >= 0.0) & (out <= 1.0))


def test_spatial_permutation_never_moves_into_unresolved_slots():
    resolved = np.asarray([True, False, True, True, False, True])
    p = fixed_spatial_permutation(resolved, seed=11)
    unresolved = np.flatnonzero(~resolved)
    np.testing.assert_array_equal(p[unresolved], unresolved)
    assert set(p[resolved]) == set(np.flatnonzero(resolved))


def test_advantage_is_against_strongest_control():
    learned = np.asarray([3.0, 4.0])
    uniform = np.asarray([1.0, 5.0])
    shuffled = np.asarray([2.0, 2.0])
    blank = np.asarray([0.0, 0.0])
    np.testing.assert_array_equal(
        strongest_control_advantage(learned, uniform, shuffled, blank),
        np.asarray([1.0, -1.0]),
    )
