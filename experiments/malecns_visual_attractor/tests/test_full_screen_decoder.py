from __future__ import annotations

import numpy as np
import torch

from full_screen_decoder import (
    FullScreenPlasticDecoder,
    build_hash_projection,
    normalize_frame_mean,
    project_generator_state,
    project_screen_to_receptors,
)


def test_full_screen_decoder_updates_large_canvas_on_reward():
    decoder = FullScreenPlasticDecoder.fresh(
        features=8,
        width=16,
        height=9,
        seed=1,
        device="cpu",
        learning_rate=0.01,
        exploration_sigma=0.05,
    )
    features = torch.linspace(-1.0, 1.0, 8)
    noise = torch.ones(16 * 9)
    before = decoder.weight.clone()
    frame = decoder.propose(features, noise)
    assert frame.shape == (9, 16)
    decoder.update(features, noise, 1.0)
    assert not torch.equal(before, decoder.weight)


def test_hash_projection_uses_every_neuron_and_is_bounded():
    bins, signs, counts = build_hash_projection(101, 7, seed=9, device="cpu")
    assert bins.shape == (101,)
    assert signs.shape == (101,)
    assert int(counts.sum()) == 101
    state = torch.linspace(-0.1, 0.1, 101)
    features = project_generator_state(state, bins, signs, counts, gain=100.0)
    assert features.shape == (7,)
    assert torch.all(features <= 1.0)
    assert torch.all(features >= -1.0)


def test_frame_mean_is_physical_screen_constraint():
    frame = torch.rand(36, 64)
    out = normalize_frame_mean(frame, 0.15)
    assert abs(float(out.mean()) - 0.15) < 1e-5
    assert float(out.min()) >= 0.0
    assert float(out.max()) <= 1.0


def test_screen_projection_respects_resolved_mask_and_pose():
    frame = torch.ones(9, 16)
    receptor_x = torch.tensor([-0.2, 0.0, 0.2], dtype=torch.float32)
    receptor_y = torch.zeros(3, dtype=torch.float32)
    resolved = torch.tensor([1.0, 0.0, 1.0], dtype=torch.float32)
    # Receiver at +x looking toward origin (heading pi): screen is centered.
    x = torch.tensor([1.0], dtype=torch.float64)
    y = torch.tensor([0.0], dtype=torch.float64)
    heading = torch.tensor([np.pi], dtype=torch.float64)
    visual = project_screen_to_receptors(
        frame,
        receptor_x=receptor_x,
        receptor_y=receptor_y,
        resolved_mask=resolved,
        x=x,
        y=y,
        heading=heading,
        physical_width=1.0,
        target_fov_rad=np.deg2rad(60.0),
        ambient=0.0,
    )
    assert visual.shape == (3, 1)
    assert float(visual[1, 0]) == 0.0
    assert float(visual[0, 0]) > 0.0
    assert float(visual[2, 0]) > 0.0
