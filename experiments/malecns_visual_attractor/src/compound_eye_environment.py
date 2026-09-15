from __future__ import annotations

import json
import math
import urllib.request
from functools import lru_cache

import numpy as np


# Pinned recent reference used only to calibrate MaleCNS optic-column directions.
# closed-loop-fly is MIT; the column table itself records CC BY 4.0 MaleCNS provenance.
REFERENCE_COMMIT = "0cbaa96cbac72cccad1fa04692b5f4d4a4e64673"
REFERENCE_COLUMNS_URL = (
    "https://raw.githubusercontent.com/ZeroXClem/closed-loop-fly/"
    f"{REFERENCE_COMMIT}/src/eye/columns.json"
)
SPACING_DEG = 5.0
ACCEPTANCE_DEG = 5.0
H1_MAX = 36
H2_MAX = 39


def _torch():
    import torch

    return torch


def _fallback_angles(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """FlyVis-like two-eye angular fallback when the pinned table is unavailable."""
    side = np.where(x < 0, -1.0, 1.0)
    frac = np.clip((np.abs(x) - 0.06) / 0.94, 0.0, 1.0)
    local_x = frac * 30.0 - 15.0
    local_y = np.clip(y, -1.0, 1.0) * 15.0
    az = side * np.deg2rad(75.0 - local_x * SPACING_DEG)
    el = np.deg2rad(local_y * SPACING_DEG)
    return az.astype(np.float32), el.astype(np.float32)


@lru_cache(maxsize=1)
def _reference_table() -> dict[tuple[int, int, int], tuple[float, float]]:
    """Load the pinned calibrated MaleCNS column directions used by closed-loop-fly."""
    try:
        with urllib.request.urlopen(REFERENCE_COLUMNS_URL, timeout=20) as response:
            payload = json.load(response)
    except Exception:
        return {}
    required = ("side", "h1", "h2", "az", "el")
    if not all(key in payload for key in required):
        return {}
    table: dict[tuple[int, int, int], tuple[float, float]] = {}
    for side, h1, h2, az, el in zip(
        payload["side"], payload["h1"], payload["h2"], payload["az"], payload["el"], strict=True
    ):
        table[(int(side), int(h1), int(h2))] = (float(az), float(el))
    return table


def calibrated_angles_numpy(receptor_x, receptor_y) -> tuple[np.ndarray, np.ndarray, str]:
    """Recover h1/h2 from our screen geometry and join calibrated azimuth/elevation."""
    x = np.asarray(receptor_x, dtype=np.float32).reshape(-1)
    y = np.asarray(receptor_y, dtype=np.float32).reshape(-1)
    az, el = _fallback_angles(x, y)
    table = _reference_table()
    if not table:
        return az, el, "flyvis-fallback"

    side01 = (x >= 0).astype(np.int8)
    frac1 = np.clip((np.abs(x) - 0.06) / 0.94, 0.0, 1.0)
    h1 = np.rint(1.0 + frac1 * (H1_MAX - 1)).astype(np.int16)
    h2 = np.rint(1.0 + np.clip((y + 1.0) * 0.5, 0.0, 1.0) * (H2_MAX - 1)).astype(np.int16)
    matched = 0
    for i, key in enumerate(zip(side01, h1, h2, strict=True)):
        value = table.get((int(key[0]), int(key[1]), int(key[2])))
        if value is None:
            continue
        az[i], el[i] = value
        matched += 1
    mode = "closed-loop-fly-calibrated" if matched else "flyvis-fallback"
    return az, el, mode


_ANGLE_CACHE: dict[tuple[str, int], tuple[object, object, str]] = {}


def calibrated_angles_torch(receptor_x, receptor_y):
    torch = _torch()
    key = (str(receptor_x.device), int(receptor_x.numel()))
    cached = _ANGLE_CACHE.get(key)
    if cached is not None:
        return cached
    az_np, el_np, mode = calibrated_angles_numpy(
        receptor_x.detach().cpu().numpy(), receptor_y.detach().cpu().numpy()
    )
    result = (
        torch.from_numpy(az_np).to(device=receptor_x.device, dtype=torch.float64),
        torch.from_numpy(el_np).to(device=receptor_x.device, dtype=torch.float64),
        mode,
    )
    _ANGLE_CACHE[key] = result
    return result


def project_screen_to_receptors_compound_eye(
    frame,
    *,
    receptor_x,
    receptor_y,
    resolved_mask,
    x,
    y,
    heading,
    physical_width: float,
    target_fov_rad: float,
    ambient: float = 0.0,
):
    """Render a screen into a two-eye MaleCNS/FlyVis-style compound-eye environment.

    Unlike the old rectangular retinal raster, each optic-column receptor has an
    azimuth/elevation direction.  A world-fixed striped surround provides visual
    context, the display occupies an angular aperture determined by distance, and
    ommatidial acceptance softens the display boundary with a ~5 degree Gaussian.
    The returned tensor is exactly what is injected into the visual receptors.
    """
    torch = _torch()
    import torch.nn.functional as F

    if frame.ndim != 2:
        raise ValueError("frame must be HxW")
    if physical_width <= 0:
        raise ValueError("physical_width must be > 0")
    if not 0.0 <= float(ambient) <= 1.0:
        raise ValueError("ambient must be in [0,1]")

    x = x.to(torch.float64).reshape(-1)
    y = y.to(torch.float64).reshape(-1)
    heading = heading.to(torch.float64).reshape(-1)
    flies = int(x.numel())
    distance = torch.clamp(torch.hypot(x, y), min=1e-9)
    bearing = torch.remainder(torch.atan2(-y, -x) - heading + torch.pi, 2 * torch.pi) - torch.pi

    angular_width = 2.0 * torch.atan2(
        torch.full_like(distance, float(physical_width / 2.0)), distance
    )
    angular_height = 2.0 * torch.atan2(
        torch.full_like(distance, float(physical_width * 9.0 / 32.0)), distance
    )
    half_w = torch.clamp(angular_width * 0.5, min=1e-6)
    half_h = torch.clamp(angular_height * 0.5, min=1e-6)

    az, el, _ = calibrated_angles_torch(receptor_x, receptor_y)
    az = az[:, None]
    el = el[:, None]
    rel_az = torch.remainder(az - bearing[None, :] + torch.pi, 2 * torch.pi) - torch.pi
    rel_el = el

    u = rel_az / half_w[None, :]
    v = rel_el / half_h[None, :]
    grid = torch.stack((torch.clamp(u, -1.0, 1.0), torch.clamp(v, -1.0, 1.0)), dim=-1)
    grid = grid.permute(1, 0, 2).unsqueeze(2).to(torch.float32)
    image = frame.to(torch.float32)[None, None, :, :].expand(flies, 1, -1, -1)
    sampled = F.grid_sample(
        image,
        grid,
        mode="bilinear",
        padding_mode="border",
        align_corners=True,
    )[:, 0, :, 0].T.contiguous()

    # FlyVis-style finite ommatidial acceptance: an edge slightly outside a facet
    # still contributes, instead of switching on/off at a rectangular pixel edge.
    outside_az = torch.clamp(torch.abs(rel_az) - half_w[None, :], min=0.0)
    outside_el = torch.clamp(torch.abs(rel_el) - half_h[None, :], min=0.0)
    angular_miss = torch.hypot(outside_az, outside_el)
    sigma = math.radians(ACCEPTANCE_DEG) / 2.355
    acceptance = torch.exp(-0.5 * (angular_miss / sigma) ** 2).to(torch.float32)

    # A striped cylindrical surround is world-fixed, so turning the fly produces
    # retinal motion rather than a featureless background.  Neutral gray follows
    # the FlyVis convention; ambient light washes the contrast out.
    world_az = heading[None, :] + az
    base = 0.5 + 0.5 * float(ambient)
    contrast = 0.28 * (1.0 - float(ambient))
    surround = torch.clamp(
        base + contrast * torch.sin(8.0 * world_az) * torch.cos(el), 0.0, 1.0
    ).to(torch.float32)
    luminance = surround + acceptance * (sampled - surround)

    resolved = resolved_mask.to(device=frame.device, dtype=torch.float32)[:, None]
    return luminance * resolved


def physics_manifest() -> dict:
    return {
        "model": "MaleCNS calibrated compound-eye + FlyVis-style acceptance + striped visual surround",
        "reference_repo": "ZeroXClem/closed-loop-fly",
        "reference_commit": REFERENCE_COMMIT,
        "reference_columns": REFERENCE_COLUMNS_URL,
        "column_spacing_deg": SPACING_DEG,
        "ommatidial_acceptance_fwhm_deg": ACCEPTANCE_DEG,
        "surround": "world-fixed gray striped cylinder; contrast washed out by ambient",
    }
