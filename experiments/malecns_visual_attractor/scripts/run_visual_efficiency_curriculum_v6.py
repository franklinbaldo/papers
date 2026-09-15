from __future__ import annotations

import json
import sys
from pathlib import Path

import run_visual_efficiency_curriculum_v3 as v3
import run_visual_efficiency_curriculum_v5 as v5


BLOB_COUNT = 6


def _torch():
    import torch

    return torch


def _bounded_channels(params):
    """Recover the six bounded screen channels from the v1 named controls.

    v1 maps a six-dimensional body latent through a 6x6 trainable transducer and
    then turns those bounded outputs into named screen controls.  v6 keeps the
    exact same trainable boundary and reconstructs those six bounded outputs so
    each can actuate one display blob instead of deforming a fixed three-lobe
    glyph.
    """
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
    """Render six independently actuated blobs on one stationary 16:9 screen.

    The physical display remains fixed at the world origin.  Receiver pose sets
    the display bearing/apparent size.  The six generator screen channels control
    six blob amplitudes and small radial displacements around a hexagonal field.
    v3 subsequently clips this raw pattern to the same hard physical aperture as
    the uniform-TV control; v5 then applies the same energy floor/matching policy.
    """
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

    channels = _bounded_channels(params)  # candidates x 6, each in [-1, 1]
    amplitudes = 0.5 + 0.5 * channels

    # Global rotation is still driven by one of the six body-derived channels,
    # while every channel independently changes the radius and brightness of its
    # own blob. This creates a richer spatial vocabulary without adding trainable
    # dimensions to the 6x6 body-to-screen transducer.
    rotation = params["orientation"][:, None]
    phase = torch.arange(BLOB_COUNT, device=x.device, dtype=torch.float32)[None, :]
    phase = phase * (2.0 * torch.pi / float(BLOB_COUNT)) + rotation
    radial = 0.48 + 0.16 * channels
    local_x = radial * torch.cos(phase)
    local_y = radial * torch.sin(phase)

    blob_x = center_x[:, :, None] + half_x[:, :, None] * local_x[:, None, :]
    blob_y = center_y[:, :, None] + half_y[:, :, None] * local_y[:, None, :]

    # Blob width is controlled by the old size channel but remains comfortably
    # inside the screen aperture. Energy normalization, not raw width/contrast,
    # determines the delivered-light budget downstream.
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
    weighted = gaussians * amplitudes.T[:, :, None, None].permute(1, 2, 3, 0)
    visual = torch.clamp(weighted.sum(dim=-1), 0.0, 1.0)
    return visual.to(dtype=receptor_x.dtype), distance, bearing


def _install_v6_renderer() -> None:
    # v3's hard-aperture wrapper calls this captured renderer. Replacing the
    # captured callable is safer than monkey-patching v1 directly because v4
    # reinstalls the v3 aperture boundary at the start of every stage.
    v3._ORIGINAL_BODY_RENDER = _render_six_blob_pattern


def main() -> None:
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
            },
            sort_keys=True,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
