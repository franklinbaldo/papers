from __future__ import annotations

import json
import sys
from pathlib import Path

import run_visual_efficiency_curriculum_v3 as v3
import run_visual_efficiency_curriculum_v4 as v4


INTENSITY_FLOOR = 1e-6
_ORIGINAL_NORMALIZE_EXACT = v3._normalize_exact
_ORIGINAL_COMMON_TARGET = v4._common_target


def _torch():
    import torch

    return torch


def _sanitize_raw(visual, resolved_mask, *, floor: float = INTENSITY_FLOOR):
    """Drop numerically tiny retinal tails before energy/support accounting.

    A Gaussian is mathematically positive almost everywhere, but an arbitrarily
    small tail is not a physically useful display pixel. Counting such tails as
    saturatable support made the theoretical attainable-energy calculation
    disagree with finite numerical normalization. v5 declares an explicit
    intensity floor and applies it symmetrically to every nonblank arm.
    """
    torch = _torch()
    mask = resolved_mask[:, None, None].to(torch.float32)
    out = torch.clamp(visual.to(torch.float32), min=0.0, max=1.0) * mask
    return torch.where(out >= float(floor), out, torch.zeros_like(out))


def _common_target_v5(*raw_arms, resolved_mask, budget: float):
    sanitized = [_sanitize_raw(arm, resolved_mask) for arm in raw_arms]
    return _ORIGINAL_COMMON_TARGET(
        *sanitized,
        resolved_mask=resolved_mask,
        budget=budget,
    )


def _normalize_exact_v5(visual, resolved_mask, target, *, iterations: int = 40):
    sanitized = _sanitize_raw(visual, resolved_mask)
    return _ORIGINAL_NORMALIZE_EXACT(
        sanitized,
        resolved_mask,
        target,
        iterations=iterations,
    )


def _install_v5_boundaries() -> None:
    v4._common_target = _common_target_v5
    v3._normalize_exact = _normalize_exact_v5


def main() -> None:
    _install_v5_boundaries()
    v4.main()

    try:
        output_dir = Path(sys.argv[sys.argv.index("--output-dir") + 1])
    except (ValueError, IndexError) as exc:
        raise RuntimeError("v5 requires explicit --output-dir") from exc

    summary_path = output_dir / "visual-efficiency-summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["experiment"] = "malecns-visual-efficiency-curriculum-v5"
    summary["scientific_status"] = "engineering calibration; common aperture + common attainable exact energy + explicit retinal intensity floor"
    summary["energy_policy"]["intensity_floor"] = INTENSITY_FLOOR
    summary["energy_policy"]["budget_note"] = (
        "Budgets are chosen below the observed ~0.01-0.02 full-retina mean "
        "capacity of the physical screen aperture so successive stages really reduce light."
    )
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "event": "visual_efficiency_v5_complete",
                "max_energy_mismatch": summary.get("max_energy_mismatch_all_stages"),
                "budgets": summary.get("parameters", {}).get("budgets"),
                "intensity_floor": INTENSITY_FLOOR,
            },
            sort_keys=True,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
