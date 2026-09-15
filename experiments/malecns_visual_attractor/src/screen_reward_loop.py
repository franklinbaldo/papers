from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


PALETTE = " .:-=+*#%@"
LATENT_DIM = 6
SCREEN_DIM = 6


@dataclass(frozen=True)
class ScreenGeometry:
    bodies: np.ndarray
    x: np.ndarray
    y: np.ndarray
    resolved: np.ndarray
    eye: np.ndarray

    def __post_init__(self) -> None:
        n = len(self.bodies)
        if any(len(v) != n for v in (self.x, self.y, self.resolved, self.eye)):
            raise ValueError("screen geometry arrays must align")


def load_screen_geometry(path: Path) -> ScreenGeometry:
    archive = np.load(path, allow_pickle=False)
    return ScreenGeometry(
        bodies=archive["visual_bodies"].astype(np.int64),
        x=archive["visual_x"].astype(np.float32),
        y=archive["visual_y"].astype(np.float32),
        resolved=archive["visual_resolved"].astype(bool),
        eye=archive["visual_eye"].astype(np.int8),
    )


def matched_direct_gaze_starts(*, flies: int, radius: float, seed: int, radial_jitter: float = 0.02):
    """Planar receiver starts facing the stationary display at the origin."""
    if flies < 1 or radius <= 0:
        raise ValueError("flies >= 1 and radius > 0 required")
    rng = np.random.default_rng(seed)
    angles = 2 * np.pi * (np.arange(flies) / flies)
    angles += rng.uniform(-np.pi / flies, np.pi / flies, size=flies)
    radii = radius * (1.0 + rng.uniform(-radial_jitter, radial_jitter, size=flies))
    x = radii * np.cos(angles)
    y = radii * np.sin(angles)
    heading = np.arctan2(-y, -x)
    return x.astype(np.float64), y.astype(np.float64), heading.astype(np.float64)


def make_transducer_population(
    center_weight: np.ndarray,
    center_bias: np.ndarray,
    *,
    population: int,
    sigma: float,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    """One-plus-lambda ES population around a persistent center."""
    if population < 1:
        raise ValueError("population must be >= 1")
    if center_weight.shape != (LATENT_DIM, SCREEN_DIM):
        raise ValueError("center_weight shape mismatch")
    if center_bias.shape != (SCREEN_DIM,):
        raise ValueError("center_bias shape mismatch")
    rng = np.random.default_rng(seed)
    weights = np.repeat(center_weight[None, :, :], population, axis=0)
    biases = np.repeat(center_bias[None, :], population, axis=0)
    if population > 1 and sigma > 0:
        weights[1:] += rng.normal(0.0, sigma, size=weights[1:].shape).astype(np.float32)
        biases[1:] += rng.normal(0.0, sigma, size=biases[1:].shape).astype(np.float32)
    return weights.astype(np.float32), biases.astype(np.float32)


def initial_transducer(*, seed: int, scale: float = 0.25) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    weight = rng.normal(0.0, scale, size=(LATENT_DIM, SCREEN_DIM)).astype(np.float32)
    bias = np.zeros(SCREEN_DIM, dtype=np.float32)
    return weight, bias


def screen_params_numpy(latent: np.ndarray, weight: np.ndarray, bias: np.ndarray) -> np.ndarray:
    raw = latent @ weight + bias
    return np.tanh(raw).astype(np.float32)


def sensor_grid_ascii(
    values: np.ndarray,
    geometry: ScreenGeometry,
    *,
    width: int = 64,
    palette: str = PALETTE,
) -> str:
    """Render every receptor exactly once as one character in a compact raster.

    Resolved optic-column sensors are ordered by eye/y/x; unresolved sensors are
    retained after them in deterministic body-id order. This is a telemetry
    raster, not a claim that the rectangular layout is the fly's native retina.
    """
    values = np.asarray(values, dtype=np.float32)
    if values.shape != geometry.bodies.shape:
        raise ValueError("values must contain one entry per visual receptor")
    if width < 8:
        raise ValueError("width must be >= 8")
    resolved_key = (~geometry.resolved).astype(np.int8)
    order = np.lexsort(
        (
            geometry.bodies,
            geometry.x,
            geometry.y,
            geometry.eye,
            resolved_key,
        )
    )
    ordered = np.maximum(values[order], 0.0)
    vmax = float(np.max(ordered)) if ordered.size else 0.0
    if vmax <= 0:
        levels = np.zeros_like(ordered, dtype=np.int32)
    else:
        scaled = np.clip(ordered / vmax, 0.0, 1.0)
        levels = np.rint(scaled * (len(palette) - 1)).astype(np.int32)
    chars = [palette[int(level)] for level in levels]
    rows = ["".join(chars[i : i + width]) for i in range(0, len(chars), width)]
    return "\n".join(rows)


def top_receptors(values: np.ndarray, geometry: ScreenGeometry, *, k: int = 12) -> list[dict]:
    values = np.asarray(values, dtype=np.float32)
    if values.shape != geometry.bodies.shape:
        raise ValueError("values must contain one entry per visual receptor")
    k = max(1, min(int(k), len(values)))
    order = np.argsort(values)[-k:][::-1]
    return [
        {
            "body": int(geometry.bodies[i]),
            "activation": float(values[i]),
            "x": float(geometry.x[i]),
            "y": float(geometry.y[i]),
            "eye": "L" if int(geometry.eye[i]) < 0 else "R" if int(geometry.eye[i]) > 0 else "?",
            "optic_column_resolved": bool(geometry.resolved[i]),
        }
        for i in order
    ]


def select_winner(cumulative_reward: np.ndarray) -> int:
    cumulative_reward = np.asarray(cumulative_reward, dtype=float)
    if cumulative_reward.ndim != 1 or cumulative_reward.size == 0:
        raise ValueError("cumulative_reward must be a non-empty vector")
    return int(np.argmax(cumulative_reward))
