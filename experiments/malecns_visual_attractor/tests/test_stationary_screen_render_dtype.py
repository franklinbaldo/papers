from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import torch


def load_runner():
    path = Path(__file__).parents[1] / "scripts" / "run_stationary_screen_reward_loop.py"
    spec = spec_from_file_location("stationary_screen_runner", path)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_render_retina_stays_float32_with_float64_pose_geometry():
    runner = load_runner()
    receptor_x = torch.tensor([-0.2, 0.0, 0.2], dtype=torch.float32)
    receptor_y = torch.tensor([0.0, 0.0, 0.0], dtype=torch.float32)
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

    visual, distance, bearing = runner._render_body_pattern(
        receptor_x=receptor_x,
        receptor_y=receptor_y,
        x=x,
        y=y,
        heading=heading,
        physical_size=0.4,
        params=params,
        target_fov_rad=3.141592653589793,
    )

    assert visual.dtype == torch.float32
    assert distance.dtype == torch.float64
    assert bearing.dtype == torch.float64
    assert visual.shape == (3, 1, 1)
    assert torch.any(visual > 0)
