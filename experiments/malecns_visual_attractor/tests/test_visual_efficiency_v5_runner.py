from __future__ import annotations

import sys
from pathlib import Path

import pytest


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import run_visual_efficiency_curriculum_v5 as v5  # noqa: E402


torch = pytest.importorskip("torch")


def test_v5_common_target_calls_original_v4_boundary_without_recursion():
    resolved = torch.tensor([1.0, 1.0, 1.0, 1.0])
    arm = torch.tensor([0.8, 0.3, 1e-12, 0.4], dtype=torch.float32)[:, None, None]

    target = v5._common_target_v5(
        arm,
        arm.clone(),
        arm.clone(),
        resolved_mask=resolved,
        budget=0.2,
    )

    assert torch.isfinite(target).all()
    assert float(target.max()) <= 0.2 + 1e-7
    # The numerical Gaussian tail is explicitly removed before support accounting.
    assert float(v5._sanitize_raw(arm, resolved)[2, 0, 0]) == 0.0
