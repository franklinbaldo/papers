from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from compound_eye_environment import (
    ACCEPTANCE_DEG,
    ROOM_CEILING_Z,
    ROOM_DEPTH,
    ROOM_FLOOR_Z,
    ROOM_HALF_WIDTH,
    calibrated_angles_numpy,
)


@dataclass(frozen=True)
class SwarmTransport:
    rows: np.ndarray
    cols: np.ndarray
    values: np.ndarray
    baseline: np.ndarray
    flies: int
    receptors: int
    pixels: int
    width: int
    height: int
    poses: np.ndarray
    visible_mass: np.ndarray

    def save(self, path) -> None:
        np.savez_compressed(
            path,
            rows=self.rows.astype(np.int64),
            cols=self.cols.astype(np.int64),
            values=self.values.astype(np.float32),
            baseline=self.baseline.astype(np.float32),
            flies=np.asarray([self.flies], dtype=np.int32),
            receptors=np.asarray([self.receptors], dtype=np.int32),
            pixels=np.asarray([self.pixels], dtype=np.int32),
            width=np.asarray([self.width], dtype=np.int32),
            height=np.asarray([self.height], dtype=np.int32),
            poses=self.poses.astype(np.float64),
            visible_mass=self.visible_mass.astype(np.float32),
        )


def load_transport(path) -> SwarmTransport:
    a = np.load(path, allow_pickle=False)
    scalar = lambda k: int(np.asarray(a[k]).reshape(-1)[0])
    return SwarmTransport(
        rows=np.asarray(a["rows"], dtype=np.int64),
        cols=np.asarray(a["cols"], dtype=np.int64),
        values=np.asarray(a["values"], dtype=np.float32),
        baseline=np.asarray(a["baseline"], dtype=np.float32),
        flies=scalar("flies"),
        receptors=scalar("receptors"),
        pixels=scalar("pixels"),
        width=scalar("width"),
        height=scalar("height"),
        poses=np.asarray(a["poses"], dtype=np.float64),
        visible_mass=np.asarray(a["visible_mass"], dtype=np.float32),
    )


def sample_swarm_poses(*, flies: int, seed: int, min_distance: float = 0.35, max_distance: float = 1.25,
                       max_lateral: float = 0.55, max_heading_offset_deg: float = 55.0) -> np.ndarray:
    """Sample independent fixed receiver poses in the half-space in front of the TV."""
    if flies < 1:
        raise ValueError("flies must be >=1")
    rng = np.random.default_rng(seed)
    x = rng.uniform(min_distance, max_distance, size=flies)
    y = rng.uniform(-max_lateral, max_lateral, size=flies)
    gaze = np.arctan2(-y, -x)
    heading = gaze + rng.uniform(-np.deg2rad(max_heading_offset_deg), np.deg2rad(max_heading_offset_deg), size=flies)
    return np.stack((x, y, heading), axis=1).astype(np.float64)


def _room_hit(ox, oy, dx, dy, dz):
    inf = np.inf
    ts = [
        (-ox / dx) if dx < -1e-12 else inf,
        ((ROOM_DEPTH - ox) / dx) if dx > 1e-12 else inf,
        ((ROOM_HALF_WIDTH - oy) / dy) if dy > 1e-12 else inf,
        ((-ROOM_HALF_WIDTH - oy) / dy) if dy < -1e-12 else inf,
        (ROOM_CEILING_Z / dz) if dz > 1e-12 else inf,
        (ROOM_FLOOR_Z / dz) if dz < -1e-12 else inf,
    ]
    ts = [t if t > 0 else inf for t in ts]
    wall = int(np.argmin(ts))
    t = ts[wall]
    return wall, t, ox + t * dx, oy + t * dy, t * dz


def _surface_luminance(wall: int, hx: float, hy: float, hz: float, ambient: float) -> float:
    base = 0.015 + 0.55 * ambient
    contrast = 0.22 * ambient
    value = np.clip(base + contrast * np.sin(7.0 * hy + 1.7 * hz) * np.cos(4.0 * hz - 0.6 * hx), 0.0, 1.0)
    if wall == 4:
        value = np.clip(value + 0.10 * ambient, 0.0, 1.0)
    elif wall == 5:
        value = np.clip(value * 0.65, 0.0, 1.0)
    return float(value)


def _bilinear(width: int, height: int, u: float, v: float):
    fx = (np.clip(u, -1.0, 1.0) + 1.0) * 0.5 * (width - 1)
    fy = (np.clip(v, -1.0, 1.0) + 1.0) * 0.5 * (height - 1)
    x0 = int(np.floor(fx)); y0 = int(np.floor(fy))
    x1 = min(x0 + 1, width - 1); y1 = min(y0 + 1, height - 1)
    ax = fx - x0; ay = fy - y0
    return (
        (y0 * width + x0, (1 - ax) * (1 - ay)),
        (y0 * width + x1, ax * (1 - ay)),
        (y1 * width + x0, (1 - ax) * ay),
        (y1 * width + x1, ax * ay),
    )


def compile_static_transport(*, receptor_x, receptor_y, resolved, poses: np.ndarray, width: int, height: int,
                             physical_width: float, ambient: float) -> SwarmTransport:
    """Compile static room/TV optics into sparse affine retinal transport b + A@frame."""
    rx = np.asarray(receptor_x, dtype=np.float32).reshape(-1)
    ry = np.asarray(receptor_y, dtype=np.float32).reshape(-1)
    mask = np.asarray(resolved, dtype=bool).reshape(-1)
    poses = np.asarray(poses, dtype=np.float64)
    if poses.ndim != 2 or poses.shape[1] != 3:
        raise ValueError("poses must be Fx3 [x,y,heading]")
    az, el, _ = calibrated_angles_numpy(rx, ry)
    flies = len(poses); receptors = len(rx); pixels = width * height
    sigma = math.radians(ACCEPTANCE_DEG) / 2.355
    subrays = ((0.0, 0.0, .40), (sigma, 0.0, .15), (-sigma, 0.0, .15), (0.0, sigma, .15), (0.0, -sigma, .15))
    tv_half_w = physical_width * 0.5
    tv_half_h = physical_width * 9.0 / 32.0

    rows, cols, vals = [], [], []
    baseline = np.zeros(flies * receptors, dtype=np.float32)
    visible = np.zeros(flies, dtype=np.float64)
    for fi, (ox, oy, heading) in enumerate(poses):
        for ri in range(receptors):
            row = fi * receptors + ri
            if not mask[ri]:
                continue
            for daz, dele, sw in subrays:
                a = float(heading + az[ri] + daz); e = float(el[ri] + dele)
                ce = math.cos(e); dx = ce * math.cos(a); dy = ce * math.sin(a); dz = math.sin(e)
                wall, t, hx, hy, hz = _room_hit(float(ox), float(oy), dx, dy, dz)
                inside_tv = wall == 0 and abs(hy) <= tv_half_w and abs(hz) <= tv_half_h
                if inside_tv:
                    visible[fi] += sw
                    baseline[row] += np.float32(sw * 0.08 * ambient)
                    u = hy / max(tv_half_w, 1e-12)
                    v = -hz / max(tv_half_h, 1e-12)
                    for col, bw in _bilinear(width, height, u, v):
                        if bw:
                            rows.append(row); cols.append(col); vals.append(sw * bw)
                else:
                    baseline[row] += np.float32(sw * _surface_luminance(wall, hx, hy, hz, ambient))
    visible /= max(receptors, 1)
    return SwarmTransport(
        rows=np.asarray(rows, dtype=np.int64), cols=np.asarray(cols, dtype=np.int64), values=np.asarray(vals, dtype=np.float32),
        baseline=baseline, flies=flies, receptors=receptors, pixels=pixels, width=width, height=height,
        poses=poses, visible_mass=visible.astype(np.float32),
    )


def to_torch(transport: SwarmTransport, *, device: str):
    import torch
    indices = torch.from_numpy(np.vstack((transport.rows, transport.cols))).to(device=device, dtype=torch.long)
    values = torch.from_numpy(transport.values).to(device=device, dtype=torch.float32)
    matrix = torch.sparse_coo_tensor(indices, values, size=(transport.flies * transport.receptors, transport.pixels), device=device).coalesce()
    baseline = torch.from_numpy(transport.baseline).to(device=device, dtype=torch.float32)
    return matrix, baseline


def apply_transport(frame, matrix, baseline, *, flies: int, receptors: int):
    import torch
    flat = frame.to(torch.float32).reshape(-1, 1)
    out = torch.sparse.mm(matrix, flat)[:, 0] + baseline
    return torch.clamp(out, 0.0, 1.0).reshape(flies, receptors).T.contiguous()
