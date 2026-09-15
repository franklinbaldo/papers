from pathlib import Path

import numpy as np
import torch

import compound_eye_environment as eyeenv
from compound_eye_artifacts import compound_eye_facets, panoramic_retina, write_rgb_png


def test_compound_eye_projection_is_finite_and_respects_resolved(monkeypatch):
    monkeypatch.setattr(eyeenv, "_reference_table", lambda: {})
    eyeenv._ANGLE_CACHE.clear()
    frame = torch.full((8, 8), 0.8, dtype=torch.float32)
    receptor_x = torch.tensor([-0.5, 0.5, 0.8], dtype=torch.float32)
    receptor_y = torch.tensor([0.0, 0.0, 0.2], dtype=torch.float32)
    resolved = torch.tensor([1.0, 1.0, 0.0], dtype=torch.float32)
    out = eyeenv.project_screen_to_receptors_compound_eye(
        frame,
        receptor_x=receptor_x,
        receptor_y=receptor_y,
        resolved_mask=resolved,
        x=torch.tensor([0.6], dtype=torch.float64),
        y=torch.tensor([0.0], dtype=torch.float64),
        heading=torch.tensor([np.pi], dtype=torch.float64),
        physical_width=0.42,
        target_fov_rad=np.deg2rad(120),
        ambient=0.0,
    )
    assert out.shape == (3, 1)
    assert torch.isfinite(out).all()
    assert float(out[2, 0]) == 0.0
    assert 0.0 <= float(out[:2].min()) <= float(out[:2].max()) <= 1.0


def test_compound_eye_visualizations_are_real_pngs(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(eyeenv, "_reference_table", lambda: {})
    values = np.asarray([0.1, 0.9, 0.4, 0.7], dtype=np.float32)
    x = np.asarray([-0.2, -0.8, 0.2, 0.8], dtype=np.float32)
    y = np.asarray([-0.4, 0.4, -0.4, 0.4], dtype=np.float32)
    side = np.asarray([-1, -1, 1, 1], dtype=np.int8)
    resolved = np.ones(4, dtype=bool)
    for name, image in (
        ("facets.png", compound_eye_facets(values, x, y, side, resolved)),
        ("panorama.png", panoramic_retina(values, x, y, resolved)),
    ):
        path = tmp_path / name
        write_rgb_png(path, image)
        data = path.read_bytes()
        assert data.startswith(b"\x89PNG\r\n\x1a\n")
        assert len(data) > 100
