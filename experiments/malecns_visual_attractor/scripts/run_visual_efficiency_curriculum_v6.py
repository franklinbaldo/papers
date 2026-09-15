from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

import run_visual_efficiency_curriculum_v2 as v2
import run_visual_efficiency_curriculum_v3 as v3
import run_visual_efficiency_curriculum_v5 as v5


BLOB_COUNT = 6
_ORIGINAL_INITIAL_TRANSDUCER = v2.initial_transducer


def _torch():
    import torch

    return torch


def _bounded_channels(params):
    """Recover the six bounded screen channels from the v1 named controls."""
    torch = _torch()
    return torch.stack(
        [
            torch.clamp(params["x_offset"] / 0.30, -1.0, 1.0),
            torch.clamp(params["y_offset"] / 0.35, -1.0, 1.0),
            torch.clamp(torch.log(params["size_scale"]) / 0.55, -1.0, 1.0),
            torch.clamp(params["orientation"] / torch.pi, -1.0, 1.0),
            torch.clamp(2.0 * params["contrast"] - 1.0, -1.0, 1.0),
            torch.clamp((params["wing_spread"] - 0.15) / 0.09, -1.0, 1.0),
        ],
        dim=1,
    )


def _find_resume_checkpoint() -> Path | None:
    candidates = (
        Path.cwd() / "initial-transducer.npz",
        Path("/kaggle/src/initial-transducer.npz"),
        Path(__file__).with_name("initial-transducer.npz"),
    )
    return next((path for path in candidates if path.exists()), None)


def _install_resume_checkpoint() -> Path | None:
    checkpoint = _find_resume_checkpoint()
    if checkpoint is None:
        return None
    archive = np.load(checkpoint, allow_pickle=False)
    weight = np.asarray(archive["weight"], dtype=np.float32)
    if weight.shape != (6, 6):
        raise RuntimeError(f"resume transducer must be 6x6, got {weight.shape}")

    def resumed_initial_transducer(*, seed: int, scale: float = 0.25):
        del seed, scale
        return weight.copy(), np.zeros(6, dtype=np.float32)

    v2.initial_transducer = resumed_initial_transducer
    return checkpoint


def _render_six_blob_pattern(
    *,
    receptor_x,
    receptor_y,
    x,
    y,
    heading,
    physical_size,
    params,
    target_fov_rad,
):
    """Render six body-controlled blobs on one stationary 16:9 screen."""
    torch = _torch()
    candidates, flies = x.shape
    bearing = torch.remainder(torch.atan2(-y, -x) - heading + torch.pi, 2 * torch.pi) - torch.pi
    distance = torch.clamp(torch.hypot(x, y), min=1e-9)
    angular_width = 2.0 * torch.atan2(
        torch.full_like(distance, float(physical_size / 2.0)),
        distance,
    )
    center_x = torch.clamp(bearing / float(target_fov_rad), -1.0, 1.0)
    center_y = torch.zeros_like(center_x)
    half_x = torch.clamp(0.5 * angular_width / float(target_fov_rad), min=0.025)
    half_y = torch.clamp(half_x * (9.0 / 16.0), min=0.018)

    channels = _bounded_channels(params)
    amplitudes = 0.5 + 0.5 * channels
    rotation = params["orientation"][:, None]
    phase = torch.arange(BLOB_COUNT, device=x.device, dtype=torch.float32)[None, :]
    phase = phase * (2.0 * torch.pi / float(BLOB_COUNT)) + rotation
    radial = 0.48 + 0.16 * channels
    local_x = radial * torch.cos(phase)
    local_y = radial * torch.sin(phase)

    blob_x = center_x[:, :, None] + half_x[:, :, None] * local_x[:, None, :]
    blob_y = center_y[:, :, None] + half_y[:, :, None] * local_y[:, None, :]
    size_u = channels[:, 2]
    sigma_x = half_x[:, :, None] * (0.12 + 0.08 * (0.5 + 0.5 * size_u[:, None, None]))
    sigma_y = half_y[:, :, None] * (0.15 + 0.08 * (0.5 + 0.5 * size_u[:, None, None]))
    sigma_x = torch.clamp(sigma_x, min=0.006)
    sigma_y = torch.clamp(sigma_y, min=0.006)

    rx = receptor_x[:, None, None, None]
    ry = receptor_y[:, None, None, None]
    dx = (rx - blob_x[None, :, :, :]) / sigma_x[None, :, :, :]
    dy = (ry - blob_y[None, :, :, :]) / sigma_y[None, :, :, :]
    gaussians = torch.exp(-0.5 * (dx * dx + dy * dy))
    weighted = gaussians * amplitudes[None, :, None, :]
    visual = torch.clamp(weighted.sum(dim=-1), 0.0, 1.0)
    return visual.to(dtype=receptor_x.dtype), distance, bearing


def _install_v6_renderer() -> None:
    v3._ORIGINAL_BODY_RENDER = _render_six_blob_pattern


def main() -> None:
    resumed_from = _install_resume_checkpoint()
    _install_v6_renderer()
    v5.main()

    try:
        output_dir = Path(sys.argv[sys.argv.index("--output-dir") + 1])
    except (ValueError, IndexError) as exc:
        raise RuntimeError("v6 requires explicit --output-dir") from exc

    summary_path = output_dir / "visual-efficiency-summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["experiment"] = "malecns-visual-efficiency-curriculum-v6-six-blob"
    summary["scientific_status"] = (
        "engineering calibration; v5 exact-energy policy + six-blob screen vocabulary"
    )
    summary["learning_state"] = {
        "mode": "resumed" if resumed_from is not None else "fresh",
        "checkpoint": resumed_from.name if resumed_from is not None else None,
        "persisted_object": "6x6 body-latent-to-screen transducer weight",
    }
    summary["renderer"] = {
        "name": "six-blob body-latent field",
        "blobs": BLOB_COUNT,
        "trainable_boundary": "unchanged 6x6 body-latent-to-screen matrix",
        "channel_use": "one recovered bounded screen channel controls each blob brightness/radial displacement",
        "aperture": "same hard 16:9 physical TV aperture as uniform-TV control",
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "event": "visual_efficiency_v6_complete",
                "max_energy_mismatch": summary.get("max_energy_mismatch_all_stages"),
                "budgets": summary.get("parameters", {}).get("budgets"),
                "renderer": "six-blob",
                "learning_mode": summary["learning_state"]["mode"],
            },
            sort_keys=True,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
