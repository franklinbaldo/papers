from __future__ import annotations

import json
import sys
from pathlib import Path

import run_visual_efficiency_curriculum as v1
import run_visual_efficiency_curriculum_v2 as v2


def _torch():
    import torch

    return torch


_ORIGINAL_BODY_RENDER = v1._render_body_pattern
_ORIGINAL_TV_RENDER = v1._render_uniform_tv


def _hard_screen_aperture(*, receptor_x, receptor_y, x, y, heading, physical_size, target_fov_rad):
    """One physical 16:9 screen aperture shared by every nonblank arm."""
    raw = _ORIGINAL_TV_RENDER(
        receptor_x=receptor_x,
        receptor_y=receptor_y,
        x=x,
        y=y,
        heading=heading,
        physical_size=physical_size,
        target_fov_rad=target_fov_rad,
    )
    return (raw >= 0.5).to(dtype=receptor_x.dtype)


def _render_uniform_tv_hard(**kwargs):
    return _hard_screen_aperture(**kwargs)


def _render_body_pattern_on_screen(**kwargs):
    visual, distance, bearing = _ORIGINAL_BODY_RENDER(**kwargs)
    aperture = _hard_screen_aperture(
        receptor_x=kwargs["receptor_x"],
        receptor_y=kwargs["receptor_y"],
        x=kwargs["x"],
        y=kwargs["y"],
        heading=kwargs["heading"],
        physical_size=kwargs["physical_size"],
        target_fov_rad=kwargs["target_fov_rad"],
    )
    return visual * aperture, distance, bearing


def _delivered_mean(visual, resolved_mask):
    torch = _torch()
    count = torch.clamp(resolved_mask.sum().to(torch.float32), min=1.0)
    return (visual * resolved_mask[:, None, None]).sum(dim=0) / count


def _normalize_exact(visual, resolved_mask, target, *, iterations: int = 40):
    """Solve mean(clamp(scale*x, 0, 1)) == target by vectorized bisection.

    Targets are clipped to the maximum attainable mean for the supplied support.
    The function is deterministic and works independently per candidate/fly.
    """
    torch = _torch()
    mask = resolved_mask[:, None, None].to(torch.float32)
    base = torch.clamp(visual.to(torch.float32), min=0.0, max=1.0) * mask
    count = torch.clamp(resolved_mask.sum().to(torch.float32), min=1.0)
    target_t = torch.as_tensor(target, dtype=torch.float32, device=visual.device)
    target_t = torch.broadcast_to(target_t, base.shape[1:]).clone()

    attainable = ((base > 0).to(torch.float32) * mask).sum(dim=0) / count
    desired = torch.minimum(torch.clamp(target_t, min=0.0), attainable)

    lo = torch.zeros_like(desired)
    hi = torch.ones_like(desired)
    for _ in range(32):
        delivered = torch.clamp(base * hi[None, :, :], max=1.0).sum(dim=0) / count
        hi = torch.where(delivered < desired, hi * 2.0, hi)

    for _ in range(max(16, int(iterations))):
        mid = (lo + hi) * 0.5
        delivered = torch.clamp(base * mid[None, :, :], max=1.0).sum(dim=0) / count
        low = delivered < desired
        lo = torch.where(low, mid, lo)
        hi = torch.where(low, hi, mid)

    return torch.clamp(base * hi[None, :, :], max=1.0) * mask


def _install_v3_boundaries() -> None:
    # v2.run_stage resolves these through the imported modules at runtime.
    v1._render_body_pattern = _render_body_pattern_on_screen
    v1._render_uniform_tv = _render_uniform_tv_hard
    v2._normalize_to_target = _normalize_exact
    v2._delivered_mean = _delivered_mean


def main() -> None:
    _install_v3_boundaries()
    v2.main()

    # v2 owns argument parsing/output. Locate --output-dir without introducing a
    # second parser, then relabel and enforce the v3 scientific gate.
    try:
        output_dir = Path(sys.argv[sys.argv.index("--output-dir") + 1])
    except (ValueError, IndexError) as exc:
        raise RuntimeError("v3 requires explicit --output-dir") from exc

    summary_path = output_dir / "visual-efficiency-summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["experiment"] = "malecns-visual-efficiency-curriculum-v3"
    summary["scientific_status"] = "engineering calibration; common physical screen aperture + exact delivered-energy gate"
    summary["energy_policy"] = {
        "ceiling_metric": "mean intensity over optic-column-resolved receptors",
        "screen_aperture": "same hard 16:9 physical screen aperture for learned and uniform-TV",
        "control_matching": "all nonblank controls match learned delivered energy per candidate/fly/frame by bisection",
        "spatial_shuffle": "retinal structure-destruction control; energy matched but not a physical display candidate",
        "unresolved_receptors": "present in MaleCNS state but receive zero screen drive",
        "mismatch_gate": 1e-5,
    }
    max_mismatch = max(float(row["max_energy_mismatch"]) for row in summary["stages"])
    summary["max_energy_mismatch_all_stages"] = max_mismatch
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"event": "visual_efficiency_v3_gate", "max_energy_mismatch": max_mismatch}, sort_keys=True), flush=True)
    if max_mismatch > 1e-5:
        raise RuntimeError(f"energy matching gate failed: {max_mismatch} > 1e-5")


if __name__ == "__main__":
    main()
