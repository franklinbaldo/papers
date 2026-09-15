from __future__ import annotations

import json
import math
import urllib.request
from functools import lru_cache

import numpy as np


# Pinned recent reference used only to calibrate MaleCNS optic-column directions.
# closed-loop-fly is MIT; the column table records CC BY 4.0 MaleCNS provenance.
REFERENCE_COMMIT = "0cbaa96cbac72cccad1fa04692b5f4d4a4e64673"
REFERENCE_COLUMNS_URL = (
    "https://raw.githubusercontent.com/ZeroXClem/closed-loop-fly/"
    f"{REFERENCE_COMMIT}/src/eye/columns.json"
)
SPACING_DEG = 5.0
ACCEPTANCE_DEG = 5.0
H1_MAX = 36
H2_MAX = 39

# A small physical room.  The TV is a 16:9 rectangle on the x=0 wall, centred
# at the fly eye height z=0.  Independent batched flies are independent rooms.
ROOM_DEPTH = 2.20
ROOM_HALF_WIDTH = 1.40
ROOM_FLOOR_Z = -0.65
ROOM_CEILING_Z = 1.15


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
    """Recover h1/h2 from our optic-column geometry and join calibrated az/el."""
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


def front_of_tv_starts(
    *,
    flies: int,
    radius: float,
    seed: int,
    heading_offset_deg: float = 0.0,
):
    """Independent physical-room replicates, all starting in front of one TV wall."""
    if flies < 1 or radius <= 0:
        raise ValueError("flies >= 1 and radius > 0 required")
    rng = np.random.default_rng(seed)
    x = radius * (1.0 + rng.uniform(-0.025, 0.025, size=flies))
    lateral = min(0.25, 0.28 * radius)
    y = rng.uniform(-lateral, lateral, size=flies)
    gaze = np.arctan2(-y, -x)
    if heading_offset_deg:
        max_offset = np.deg2rad(float(heading_offset_deg))
        gaze = gaze + rng.uniform(-max_offset, max_offset, size=flies)
    return x.astype(np.float64), y.astype(np.float64), gaze.astype(np.float64)


def _ray_room_luminance(
    frame,
    *,
    az,
    el,
    x,
    y,
    heading,
    physical_width: float,
    ambient: float,
):
    """One ray per receptor into an axis-aligned room containing a physical TV plane."""
    torch = _torch()
    import torch.nn.functional as F

    eps = 1e-9
    ox = x[None, :]
    oy = y[None, :]
    oz = torch.zeros_like(ox)
    world_az = heading[None, :] + az[:, None]
    el2 = el[:, None]
    cos_el = torch.cos(el2)
    dx = cos_el * torch.cos(world_az)
    dy = cos_el * torch.sin(world_az)
    dz = torch.sin(el2).expand_as(dx)

    inf = torch.full_like(dx, float("inf"))

    def positive_t(numerator, direction, valid):
        t = numerator / torch.where(torch.abs(direction) > eps, direction, torch.ones_like(direction))
        return torch.where(valid & (t > 0), t, inf)

    t_front = positive_t(-ox, dx, dx < -eps)  # x=0, TV wall
    t_back = positive_t(ROOM_DEPTH - ox, dx, dx > eps)
    t_right = positive_t(ROOM_HALF_WIDTH - oy, dy, dy > eps)
    t_left = positive_t(-ROOM_HALF_WIDTH - oy, dy, dy < -eps)
    t_ceiling = positive_t(ROOM_CEILING_Z - oz, dz, dz > eps)
    t_floor = positive_t(ROOM_FLOOR_Z - oz, dz, dz < -eps)
    candidates = torch.stack((t_front, t_back, t_right, t_left, t_ceiling, t_floor), dim=0)
    t_hit, wall = torch.min(candidates, dim=0)
    hx = ox + t_hit * dx
    hy = oy + t_hit * dy
    hz = oz + t_hit * dz

    # Physical surface luminance.  In a dark room the unlit room is almost black;
    # ambient illumination reveals textured walls/floor so body rotation creates optic flow.
    amb = float(ambient)
    wall_base = 0.015 + 0.55 * amb
    wall_contrast = 0.22 * amb
    wall_texture = torch.sin(7.0 * hy + 1.7 * hz) * torch.cos(4.0 * hz - 0.6 * hx)
    luminance = torch.clamp(wall_base + wall_contrast * wall_texture, 0.0, 1.0).to(torch.float32)
    luminance = torch.where(wall == 4, torch.clamp(luminance + 0.10 * amb, 0.0, 1.0), luminance)
    luminance = torch.where(wall == 5, torch.clamp(luminance * 0.65, 0.0, 1.0), luminance)

    # TV rectangle lives on the x=0 wall; its physical 16:9 dimensions and ray
    # intersection determine what each receptor samples.  No screen-space shortcut.
    tv_half_w = float(physical_width) * 0.5
    tv_half_h = float(physical_width) * 9.0 / 32.0
    on_front = wall == 0
    inside_tv = on_front & (torch.abs(hy) <= tv_half_w) & (torch.abs(hz) <= tv_half_h)
    u = torch.clamp(hy / max(tv_half_w, 1e-9), -1.0, 1.0)
    v = torch.clamp(-hz / max(tv_half_h, 1e-9), -1.0, 1.0)
    grid = torch.stack((u, v), dim=-1).permute(1, 0, 2).unsqueeze(2).to(torch.float32)
    flies = int(x.numel())
    image = frame.to(torch.float32)[None, None, :, :].expand(flies, 1, -1, -1)
    sampled = F.grid_sample(
        image,
        grid,
        mode="bilinear",
        padding_mode="border",
        align_corners=True,
    )[:, 0, :, 0].T.contiguous()
    # Ambient reflection on the panel is deliberately small relative to emission.
    tv_luminance = torch.clamp(sampled + 0.08 * amb, 0.0, 1.0)
    return torch.where(inside_tv, tv_luminance, luminance)


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
    """Ray-cast a physical room through a calibrated two-eye MaleCNS compound eye.

    Each resolved optic-column receptor has an azimuth/elevation direction. Five
    deterministic sub-rays approximate a 5-degree ommatidial acceptance field,
    following the same front-end principles used by recent FlyVis/MaleCNS projects.
    """
    torch = _torch()
    if frame.ndim != 2:
        raise ValueError("frame must be HxW")
    if physical_width <= 0:
        raise ValueError("physical_width must be > 0")
    if not 0.0 <= float(ambient) <= 1.0:
        raise ValueError("ambient must be in [0,1]")

    x = x.to(torch.float64).reshape(-1)
    y = y.to(torch.float64).reshape(-1)
    heading = heading.to(torch.float64).reshape(-1)
    az, el, _ = calibrated_angles_torch(receptor_x, receptor_y)

    # Gaussian-like five-ray quadrature around the optical axis.  At ±sigma a
    # Gaussian has substantial weight; weighted averaging avoids hard pixel-edge aliasing.
    sigma = math.radians(ACCEPTANCE_DEG) / 2.355
    samples = (
        (0.0, 0.0, 0.40),
        (+sigma, 0.0, 0.15),
        (-sigma, 0.0, 0.15),
        (0.0, +sigma, 0.15),
        (0.0, -sigma, 0.15),
    )
    luminance = None
    for daz, dele, weight in samples:
        ray = _ray_room_luminance(
            frame,
            az=az + daz,
            el=el + dele,
            x=x,
            y=y,
            heading=heading,
            physical_width=float(physical_width),
            ambient=float(ambient),
        )
        luminance = weight * ray if luminance is None else luminance + weight * ray

    resolved = resolved_mask.to(device=frame.device, dtype=torch.float32)[:, None]
    return luminance.to(torch.float32) * resolved


def physics_manifest() -> dict:
    return {
        "model": "ray-cast physical room through calibrated MaleCNS compound eye",
        "reference_repo": "ZeroXClem/closed-loop-fly + Jhongdlp/FlyBrain + Lulzx/fly-brain",
        "reference_commit": REFERENCE_COMMIT,
        "reference_columns": REFERENCE_COLUMNS_URL,
        "column_spacing_deg": SPACING_DEG,
        "ommatidial_acceptance_fwhm_deg": ACCEPTANCE_DEG,
        "acceptance_sampling": "five deterministic sub-rays per receptor",
        "room": {
            "depth": ROOM_DEPTH,
            "half_width": ROOM_HALF_WIDTH,
            "floor_z": ROOM_FLOOR_Z,
            "ceiling_z": ROOM_CEILING_Z,
        },
        "display": "physical 16:9 emissive rectangle on x=0 wall; ray-plane sampling",
        "ambient": "room surfaces become visible/textured with ambient illumination",
    }
