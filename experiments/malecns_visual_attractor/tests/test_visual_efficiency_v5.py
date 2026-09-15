from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

import torch


def load_runner():
    scripts = Path(__file__).parents[1] / "scripts"
    sys.path.insert(0, str(scripts))
    path = scripts / "run_visual_efficiency_curriculum_v5.py"
    spec = spec_from_file_location("visual_efficiency_runner_v5", path)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_tiny_gaussian_tails_do_not_count_as_support():
    runner = load_runner()
    resolved = torch.ones(4, dtype=torch.float32)
    raw = torch.tensor([[[1.0]], [[1e-7]], [[1e-12]], [[0.0]]], dtype=torch.float32)
    sanitized = runner._sanitize_raw(raw, resolved)
    assert sanitized[0, 0, 0] == 1.0
    assert sanitized[1, 0, 0] == 0.0
    assert sanitized[2, 0, 0] == 0.0
    assert sanitized[3, 0, 0] == 0.0


def test_common_target_uses_real_finite_support_after_flooring():
    runner = load_runner()
    resolved = torch.ones(4, dtype=torch.float32)
    learned = torch.tensor([[[1.0]], [[0.5]], [[1e-12]], [[1e-20]]], dtype=torch.float32)
    uniform = torch.tensor([[[1.0]], [[1.0]], [[0.0]], [[0.0]]], dtype=torch.float32)
    shuffle = torch.tensor([[[0.8]], [[0.2]], [[1e-10]], [[0.0]]], dtype=torch.float32)
    target = runner._common_target_v5(
        learned,
        uniform,
        shuffle,
        resolved_mask=resolved,
        budget=0.9,
    )
    # All three arms have exactly two physically useful receptors after flooring.
    torch.testing.assert_close(target, torch.tensor([[0.5]], dtype=torch.float32))


def test_v5_normalizer_hits_common_target_with_tiny_tails_removed():
    runner = load_runner()
    resolved = torch.tensor([1.0, 1.0, 1.0, 1.0, 0.0], dtype=torch.float32)
    learned = torch.tensor([[[1.0]], [[0.2]], [[1e-10]], [[0.0]], [[1.0]]], dtype=torch.float32)
    uniform = torch.tensor([[[0.8]], [[0.6]], [[0.0]], [[0.0]], [[1.0]]], dtype=torch.float32)
    shuffle = torch.tensor([[[0.7]], [[0.3]], [[1e-12]], [[0.0]], [[1.0]]], dtype=torch.float32)
    target = runner._common_target_v5(
        learned,
        uniform,
        shuffle,
        resolved_mask=resolved,
        budget=0.2,
    )
    arms = [runner._normalize_exact_v5(x, resolved, target) for x in (learned, uniform, shuffle)]
    for arm in arms:
        delivered = runner.v3._delivered_mean(arm, resolved)
        torch.testing.assert_close(delivered, target, atol=1e-6, rtol=1e-6)
        assert torch.all(arm[4] == 0)
