import numpy as np
import torch

import swarm_transport as st


def test_static_transport_applies_sparse_screen_and_background(monkeypatch):
    monkeypatch.setattr(
        st,
        "calibrated_angles_numpy",
        lambda x, y: (
            np.asarray([0.0, 0.20, -0.20], dtype=np.float32),
            np.asarray([0.0, 0.05, -0.05], dtype=np.float32),
            "test",
        ),
    )
    poses = np.asarray([[0.60, 0.0, np.pi], [0.85, 0.15, np.pi - 0.1]], dtype=np.float64)
    tr = st.compile_static_transport(
        receptor_x=np.asarray([-0.2, 0.2, 0.5], dtype=np.float32),
        receptor_y=np.asarray([0.0, 0.1, -0.1], dtype=np.float32),
        resolved=np.asarray([True, True, False]),
        poses=poses,
        width=8,
        height=4,
        physical_width=0.42,
        ambient=0.08,
    )
    assert tr.flies == 2
    assert tr.receptors == 3
    assert tr.pixels == 32
    assert tr.values.size > 0
    assert np.all(tr.visible_mass > 0)
    matrix, baseline = st.to_torch(tr, device="cpu")
    dark = st.apply_transport(torch.zeros((4, 8)), matrix, baseline, flies=2, receptors=3)
    bright = st.apply_transport(torch.ones((4, 8)), matrix, baseline, flies=2, receptors=3)
    assert dark.shape == (3, 2)
    assert torch.all(bright[:2] >= dark[:2])
    assert torch.all(bright[2] == 0)


def test_pose_sampler_is_reproducible_and_in_front_of_tv():
    a = st.sample_swarm_poses(flies=12, seed=44)
    b = st.sample_swarm_poses(flies=12, seed=44)
    np.testing.assert_array_equal(a, b)
    assert np.all(a[:, 0] > 0)
    assert np.ptp(a[:, 1]) > 0
    assert np.ptp(a[:, 2]) > 0
