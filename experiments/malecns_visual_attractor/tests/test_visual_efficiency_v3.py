from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

import torch


def load_runner():
    scripts = Path(__file__).parents[1] / "scripts"
    sys.path.insert(0, str(scripts))
    path = scripts / "run_visual_efficiency_curriculum_v3.py"
    spec = spec_from_file_location("visual_efficiency_runner_v3", path)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_exact_normalizer_matches_sparse_support_target():
    runner = load_runner()
    resolved = torch.tensor([1.0, 1.0, 1.0, 1.0, 0.0], dtype=torch.float32)
    raw = torch.tensor(
        [
            [[0.01, 0.9]],
            [[0.02, 0.1]],
            [[0.7, 0.03]],
            [[0.4, 0.02]],
            [[1.0, 1.0]],
        ],
        dtype=torch.float32,
    )
    target = torch.tensor([[0.30, 0.20]], dtype=torch.float32)
    normalized = runner._normalize_exact(raw, resolved, target)
    delivered = runner._delivered_mean(normalized, resolved)
    torch.testing.assert_close(delivered, target, atol=1e-6, rtol=1e-6)
    assert torch.all(normalized[4] == 0)


def test_body_pattern_is_clipped_to_same_hard_tv_aperture():
    runner = load_runner()
    receptor_x = torch.tensor([-0.9, -0.2, 0.0, 0.2, 0.9], dtype=torch.float32)
    receptor_y = torch.zeros(5, dtype=torch.float32)
    x = torch.tensor([[0.75]], dtype=torch.float64)
    y = torch.tensor([[0.0]], dtype=torch.float64)
    heading = torch.tensor([[3.141592653589793]], dtype=torch.float64)
    params = {
        "x_offset": torch.tensor([0.0], dtype=torch.float32),
        "y_offset": torch.tensor([0.0], dtype=torch.float32),
        "size_scale": torch.tensor([1.0], dtype=torch.float32),
        "orientation": torch.tensor([0.0], dtype=torch.float32),
        "contrast": torch.tensor([1.0], dtype=torch.float32),
        "wing_spread": torch.tensor([0.1], dtype=torch.float32),
    }
    aperture = runner._hard_screen_aperture(
        receptor_x=receptor_x,
        receptor_y=receptor_y,
        x=x,
        y=y,
        heading=heading,
        physical_size=0.4,
        target_fov_rad=3.141592653589793,
    )
    visual, _, _ = runner._render_body_pattern_on_screen(
        receptor_x=receptor_x,
        receptor_y=receptor_y,
        x=x,
        y=y,
        heading=heading,
        physical_size=0.4,
        params=params,
        target_fov_rad=3.141592653589793,
    )
    assert torch.all(visual[aperture == 0] == 0)
    assert torch.any(visual[aperture > 0] > 0)
