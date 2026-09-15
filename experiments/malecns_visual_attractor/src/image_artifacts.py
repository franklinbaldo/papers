from __future__ import annotations

import struct
import zlib
from pathlib import Path

import numpy as np


def _chunk(kind: bytes, payload: bytes) -> bytes:
    body = kind + payload
    return struct.pack(">I", len(payload)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)


def write_gray_png(path: Path, image, *, normalize: bool = False) -> None:
    """Write a 2-D grayscale array to PNG using only the stdlib + NumPy."""
    arr = np.asarray(image, dtype=np.float32)
    if arr.ndim != 2:
        raise ValueError("image must be 2-D")
    finite = np.isfinite(arr)
    if not finite.all():
        arr = np.where(finite, arr, 0.0)
    if normalize:
        lo = float(arr.min())
        hi = float(arr.max())
        if hi > lo:
            arr = (arr - lo) / (hi - lo)
        else:
            arr = np.zeros_like(arr)
    pixels = np.rint(np.clip(arr, 0.0, 1.0) * 255.0).astype(np.uint8)
    height, width = pixels.shape
    raw = b"".join(b"\x00" + row.tobytes() for row in pixels)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(raw, level=9))
    png += _chunk(b"IEND", b"")
    Path(path).write_bytes(png)


def rasterize_receptors(values, receptor_x, receptor_y, resolved, *, width: int = 640, height: int = 320, radius: int = 2):
    """Rasterize optic-column-resolved receptor values onto a viewable image."""
    values = np.asarray(values, dtype=np.float32).reshape(-1)
    x = np.asarray(receptor_x, dtype=np.float32).reshape(-1)
    y = np.asarray(receptor_y, dtype=np.float32).reshape(-1)
    mask = np.asarray(resolved, dtype=bool).reshape(-1)
    if not (values.size == x.size == y.size == mask.size):
        raise ValueError("receptor arrays must have equal length")
    if width < 2 or height < 2 or radius < 0:
        raise ValueError("invalid raster dimensions")
    image = np.zeros((height, width), dtype=np.float32)
    xs = np.rint((np.clip(x, -1.0, 1.0) + 1.0) * 0.5 * (width - 1)).astype(np.int32)
    ys = np.rint((1.0 - (np.clip(y, -1.0, 1.0) + 1.0) * 0.5) * (height - 1)).astype(np.int32)
    for px, py, value, ok in zip(xs, ys, values, mask, strict=True):
        if not ok:
            continue
        x0 = max(0, px - radius)
        x1 = min(width, px + radius + 1)
        y0 = max(0, py - radius)
        y1 = min(height, py + radius + 1)
        image[y0:y1, x0:x1] = np.maximum(image[y0:y1, x0:x1], float(value))
    return image
