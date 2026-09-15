from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import torch


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

SPEC = importlib.util.spec_from_file_location(
    "run_visual_efficiency_curriculum_v6",
    SCRIPTS / "run_visual_efficiency_curriculum_v6.py",
)
assert SPEC is not None and SPEC.loader is not None
V6 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V6)


def _params(value: float, candidates: int = 2):
    u = torch.full((candidates,), float(value), dtype=torch.float32)
    return {
        "x_offset": 0.30 * u,
        "y_offset": 0.35 * u,
        "size_scale": torch.exp(0.55 * u),
        "orientation": torch.pi * u,
        "contrast": 0.5 + 0.5 * u,
        "wing_spread": 0.15 + 0.09 * u,
    }


def test_six_blob_renderer_shape_dtype_and_channel_effect():
    receptor_x = torch.linspace(-0.5, 0.5, 81, dtype=torch.float32)
    receptor_y = torch.linspace(-0.28, 0.28, 81, dtype=torch.float32)
    x = torch.full((2, 3), 0.75, dtype=torch.float64)
    y = torch.zeros((2, 3), dtype=torch.float64)
    heading = torch.full((2, 3), torch.pi, dtype=torch.float64)

    low, distance, bearing = V6._render_six_blob_pattern(
        receptor_x=receptor_x,
        receptor_y=receptor_y,
        x=x,
        y=y,
        heading=heading,
        physical_size=0.30,
        params=_params(-0.7),
        target_fov_rad=1.2,
    )
    high, _, _ = V6._render_six_blob_pattern(
        receptor_x=receptor_x,
        receptor_y=receptor_y,
        x=x,
        y=y,
        heading=heading,
        physical_size=0.30,
        params=_params(0.7),
        target_fov_rad=1.2,
    )

    assert low.shape == (81, 2, 3)
    assert high.shape == (81, 2, 3)
    assert distance.shape == (2, 3)
    assert bearing.shape == (2, 3)
    assert low.dtype == torch.float32
    assert high.dtype == torch.float32
    assert torch.isfinite(low).all()
    assert torch.isfinite(high).all()
    assert bool(torch.all((low >= 0.0) & (low <= 1.0)))
    assert bool(torch.all((high >= 0.0) & (high <= 1.0)))
    assert not torch.allclose(low, high)
