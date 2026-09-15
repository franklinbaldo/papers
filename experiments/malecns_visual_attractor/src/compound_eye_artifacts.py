from __future__ import annotations

import struct
import zlib
from pathlib import Path

import numpy as np

from compound_eye_environment import calibrated_angles_numpy


def _chunk(kind: bytes, payload: bytes) -> bytes:
    body = kind + payload
    return struct.pack(">I", len(payload)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)


def write_rgb_png(path: Path, image) -> None:
    arr = np.asarray(image, dtype=np.uint8)
    if arr.ndim != 3 or arr.shape[2] != 3:
        raise ValueError("image must be HxWx3 uint8")
    height, width, _ = arr.shape
    raw = b"".join(b"\x00" + row.tobytes() for row in arr)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(raw, level=9))
    png += _chunk(b"IEND", b"")
    Path(path).write_bytes(png)


def _paint_disc(image: np.ndarray, cx: int, cy: int, radius: int, rgb) -> None:
    h, w, _ = image.shape
    x0, x1 = max(0, cx - radius), min(w - 1, cx + radius)
    y0, y1 = max(0, cy - radius), min(h - 1, cy + radius)
    r2 = radius * radius
    for yy in range(y0, y1 + 1):
        dy2 = (yy - cy) ** 2
        for xx in range(x0, x1 + 1):
            if (xx - cx) ** 2 + dy2 <= r2:
                image[yy, xx] = rgb


def _rgb(value: float, *, signed: bool, gamma: float = 0.5) -> tuple[int, int, int]:
    if signed:
        v = float(np.clip(value, -1.0, 1.0))
        if v >= 0:
            return int(35 + 220 * v), int(30 + 55 * (1 - v)), int(30 + 40 * (1 - v))
        v = -v
        return int(30 + 40 * (1 - v)), int(50 + 80 * (1 - v)), int(45 + 210 * v)
    v = float(np.clip(value, 0.0, 1.0)) ** gamma
    g = int(round(18 + 237 * v))
    return g, g, g


def compound_eye_facets(
    values,
    receptor_x,
    receptor_y,
    eye,
    resolved,
    *,
    width: int = 1200,
    height: int = 520,
    signed: bool = False,
    normalize: bool = False,
) -> np.ndarray:
    """Two compound eyes as facet mosaics, front of both eyes toward the center."""
    values = np.asarray(values, dtype=np.float32).reshape(-1)
    x = np.asarray(receptor_x, dtype=np.float32).reshape(-1)
    y = np.asarray(receptor_y, dtype=np.float32).reshape(-1)
    eye = np.asarray(eye, dtype=np.int8).reshape(-1)
    mask = np.asarray(resolved, dtype=bool).reshape(-1)
    if not (values.size == x.size == y.size == eye.size == mask.size):
        raise ValueError("receptor arrays must align")
    if normalize:
        if signed:
            scale = max(float(np.max(np.abs(values[mask]))) if mask.any() else 0.0, 1e-12)
            values = values / scale
        else:
            lo = float(np.min(values[mask])) if mask.any() else 0.0
            hi = float(np.max(values[mask])) if mask.any() else 1.0
            values = (values - lo) / max(hi - lo, 1e-12)

    image = np.zeros((height, width, 3), dtype=np.uint8)
    image[:] = (5, 7, 10)
    # Reconstruct the native column coordinates encoded by build_screen_geometry.
    frac = np.clip((np.abs(x) - 0.06) / 0.94, 0.0, 1.0)
    col_x = frac * 30.0 - 15.0
    col_y = np.clip(y, -1.0, 1.0) * 15.0
    scale = min(width * 0.19 / 15.0, height * 0.43 / 15.0)
    radius = max(2, int(round(scale * 0.45)))

    for side, center_frac, mirror in ((-1, 0.27, 1.0), (1, 0.73, -1.0)):
        cx0 = center_frac * width
        for i in np.flatnonzero(mask & (eye == side)):
            cx = int(round(cx0 + mirror * col_x[i] * scale))
            cy = int(round(height * 0.52 - col_y[i] * scale))
            _paint_disc(image, cx, cy, radius, _rgb(float(values[i]), signed=signed))
    return image


def panoramic_retina(
    values,
    receptor_x,
    receptor_y,
    resolved,
    *,
    width: int = 1400,
    height: int = 560,
    signed: bool = False,
    normalize: bool = False,
) -> np.ndarray:
    """Equirectangular retinal field using calibrated MaleCNS azimuth/elevation."""
    values = np.asarray(values, dtype=np.float32).reshape(-1)
    mask = np.asarray(resolved, dtype=bool).reshape(-1)
    az, el, _ = calibrated_angles_numpy(receptor_x, receptor_y)
    if normalize:
        if signed:
            scale = max(float(np.max(np.abs(values[mask]))) if mask.any() else 0.0, 1e-12)
            values = values / scale
        else:
            lo = float(np.min(values[mask])) if mask.any() else 0.0
            hi = float(np.max(values[mask])) if mask.any() else 1.0
            values = (values - lo) / max(hi - lo, 1e-12)

    image = np.zeros((height, width, 3), dtype=np.uint8)
    image[:] = (5, 7, 10)
    # Same visual range used by the recent eye HUD: ~340 degrees azimuth, -60..+75 elevation.
    az_span = np.deg2rad(340.0)
    el_top = np.deg2rad(75.0)
    el_bottom = np.deg2rad(-60.0)
    radius = max(2, int(round(width / 470.0)))
    for i in np.flatnonzero(mask):
        a = float(np.remainder(az[i] + np.pi, 2 * np.pi) - np.pi)
        if abs(a) > az_span / 2:
            continue
        xx = int(round((a + az_span / 2) / az_span * (width - 1)))
        yy = int(round((el_top - float(el[i])) / (el_top - el_bottom) * (height - 1)))
        if 0 <= yy < height:
            _paint_disc(image, xx, yy, radius, _rgb(float(values[i]), signed=signed))
    return image
