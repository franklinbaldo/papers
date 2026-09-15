from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
import torch


def load_runner():
    path = Path(__file__).parents[1] / "scripts" / "run_visual_efficiency_curriculum_v2.py"
    spec = spec_from_file_location("visual_efficiency_runner_v2", path)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_controls_can_match_delivered_energy_tensor():
    runner = load_runner()
    resolved = torch.tensor([1.0, 1.0, 1.0, 0.0], dtype=torch.float32)
    learned_raw = torch.tensor(
        [
            [[1.0, 0.7]],
            [[0.5, 0.4]],
            [[0.1, 0.2]],
            [[1.0, 1.0]],
        ],
        dtype=torch.float32,
    )
    learned = runner._normalize_to_target(learned_raw, resolved, 0.2)
    target = runner._delivered_mean(learned, resolved)

    control_raw = torch.tensor(
        [
            [[0.2, 1.0]],
            [[0.9, 0.1]],
            [[0.3, 0.5]],
            [[0.8, 0.8]],
        ],
        dtype=torch.float32,
    )
    control = runner._normalize_to_target(control_raw, resolved, target)
    delivered = runner._delivered_mean(control, resolved)

    torch.testing.assert_close(delivered, target, atol=1e-5, rtol=1e-5)
    assert torch.all(control[3] == 0)


def test_v2_imports_v1_without_changing_registered_conditions():
    runner = load_runner()
    assert tuple(runner.CONDITIONS) == ("learned", "uniform_tv", "spatial_shuffle", "blank")
    assert np.isfinite(runner.v1._mutate_weights(np.zeros((6, 6), dtype=np.float32), population=2, sigma=0.1, seed=1)).all()
