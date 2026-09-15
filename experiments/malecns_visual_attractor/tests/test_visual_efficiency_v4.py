from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

import torch


def load_runner():
    scripts = Path(__file__).parents[1] / "scripts"
    sys.path.insert(0, str(scripts))
    path = scripts / "run_visual_efficiency_curriculum_v4.py"
    spec = spec_from_file_location("visual_efficiency_runner_v4", path)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_common_target_scales_learned_down_to_weakest_support():
    runner = load_runner()
    resolved = torch.tensor([1.0, 1.0, 1.0, 1.0, 0.0], dtype=torch.float32)
    learned_raw = torch.tensor([[[1.0]], [[0.8]], [[0.6]], [[0.4]], [[1.0]]], dtype=torch.float32)
    uniform_raw = torch.tensor([[[1.0]], [[1.0]], [[0.0]], [[0.0]], [[1.0]]], dtype=torch.float32)
    shuffle_raw = torch.tensor([[[0.2]], [[0.3]], [[0.4]], [[0.0]], [[1.0]]], dtype=torch.float32)

    target = runner._common_target(
        learned_raw,
        uniform_raw,
        shuffle_raw,
        resolved_mask=resolved,
        budget=0.9,
    )
    # Supports are 4/4, 2/4, 3/4 respectively; common physical target is 0.5.
    torch.testing.assert_close(target, torch.tensor([[0.5]], dtype=torch.float32))

    learned = runner.v3._normalize_exact(learned_raw, resolved, target)
    uniform = runner.v3._normalize_exact(uniform_raw, resolved, target)
    shuffle = runner.v3._normalize_exact(shuffle_raw, resolved, target)
    delivered = [runner.v3._delivered_mean(x, resolved) for x in (learned, uniform, shuffle)]
    for value in delivered:
        torch.testing.assert_close(value, target, atol=1e-6, rtol=1e-6)


def test_common_target_respects_nominal_budget_when_all_arms_can_attain_it():
    runner = load_runner()
    resolved = torch.ones(4, dtype=torch.float32)
    arms = [torch.ones((4, 2, 3), dtype=torch.float32) for _ in range(3)]
    target = runner._common_target(*arms, resolved_mask=resolved, budget=0.03)
    torch.testing.assert_close(target, torch.full((2, 3), 0.03, dtype=torch.float32))
