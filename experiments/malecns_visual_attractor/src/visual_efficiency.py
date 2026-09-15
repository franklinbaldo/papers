from __future__ import annotations

from dataclasses import dataclass

import numpy as np


CONDITIONS = ("learned", "uniform_tv", "spatial_shuffle", "blank")
DEFAULT_BUDGETS = (0.12, 0.06, 0.03)


@dataclass(frozen=True)
class EfficiencyStage:
    budget: float
    heading_offset_deg: float

    def __post_init__(self) -> None:
        if not 0 < self.budget <= 1:
            raise ValueError("budget must lie in (0, 1]")
        if not 0 <= self.heading_offset_deg < 180:
            raise ValueError("heading_offset_deg must lie in [0, 180)")


def efficiency_curriculum(
    budgets: tuple[float, ...] = DEFAULT_BUDGETS,
    *,
    heading_offset_deg: float = 45.0,
) -> tuple[EfficiencyStage, ...]:
    if not budgets:
        raise ValueError("at least one visual-energy budget is required")
    if any(next_budget >= budget for budget, next_budget in zip(budgets, budgets[1:])):
        raise ValueError("budgets must be strictly decreasing")
    return tuple(EfficiencyStage(float(b), float(heading_offset_deg)) for b in budgets)


def matched_offset_starts(
    *,
    flies: int,
    radius: float,
    seed: int,
    heading_offset_deg: float,
    radial_jitter: float = 0.02,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Matched starts around the display with alternating signed heading offsets.

    Unlike the direct-gaze calibration, the receiver must now correct an angular
    error before a screen pattern can guide it toward the display.  Starts remain
    identical across every energy-matched control.
    """
    if flies < 1 or radius <= 0:
        raise ValueError("flies >= 1 and radius > 0 required")
    if radial_jitter < 0:
        raise ValueError("radial_jitter must be >= 0")
    if not 0 <= heading_offset_deg < 180:
        raise ValueError("heading_offset_deg must lie in [0, 180)")
    rng = np.random.default_rng(seed)
    angles = 2 * np.pi * (np.arange(flies) / flies)
    angles += rng.uniform(-np.pi / flies, np.pi / flies, size=flies)
    radii = radius * (1.0 + rng.uniform(-radial_jitter, radial_jitter, size=flies))
    x = radii * np.cos(angles)
    y = radii * np.sin(angles)
    target_heading = np.arctan2(-y, -x)
    sign = np.where(np.arange(flies) % 2 == 0, -1.0, 1.0)
    heading = target_heading + sign * np.deg2rad(heading_offset_deg)
    heading = (heading + np.pi) % (2 * np.pi) - np.pi
    return x.astype(np.float64), y.astype(np.float64), heading.astype(np.float64)


def normalize_energy_numpy(
    values: np.ndarray,
    resolved: np.ndarray,
    budget: float,
    *,
    iterations: int = 6,
) -> np.ndarray:
    """Match mean intensity over physically resolved receptors to a budget.

    Values at unresolved optic columns are forced to zero so the optimizer cannot
    exploit the side-specific fallback coordinates used only for telemetry.  A
    short rescale/clamp loop approaches the requested mean while preserving the
    candidate's spatial structure and the physical intensity range [0, 1].
    """
    values = np.asarray(values, dtype=np.float32)
    resolved = np.asarray(resolved, dtype=bool)
    if values.shape[0] != resolved.shape[0]:
        raise ValueError("receptor axis and resolved mask must align")
    if not 0 < budget <= 1:
        raise ValueError("budget must lie in (0, 1]")
    if not np.any(resolved):
        raise ValueError("at least one resolved receptor is required")
    out = np.maximum(values, 0.0).astype(np.float32, copy=True)
    out[~resolved, ...] = 0.0
    for _ in range(max(1, int(iterations))):
        current = np.mean(out[resolved, ...], axis=0, keepdims=True)
        scale = np.float32(budget) / np.maximum(current, np.float32(1e-12))
        out[resolved, ...] = np.clip(out[resolved, ...] * scale, 0.0, 1.0)
    return out.astype(np.float32, copy=False)


def fixed_spatial_permutation(resolved: np.ndarray, *, seed: int) -> np.ndarray:
    """Return a deterministic permutation that only shuffles resolved receptors."""
    resolved = np.asarray(resolved, dtype=bool)
    indices = np.arange(len(resolved), dtype=np.int64)
    active = indices[resolved]
    rng = np.random.default_rng(seed)
    shuffled = active.copy()
    rng.shuffle(shuffled)
    permutation = indices.copy()
    permutation[active] = shuffled
    return permutation


def strongest_control_advantage(
    learned: np.ndarray,
    uniform_tv: np.ndarray,
    spatial_shuffle: np.ndarray,
    blank: np.ndarray,
) -> np.ndarray:
    learned = np.asarray(learned, dtype=np.float64)
    controls = np.stack(
        [
            np.asarray(uniform_tv, dtype=np.float64),
            np.asarray(spatial_shuffle, dtype=np.float64),
            np.asarray(blank, dtype=np.float64),
        ],
        axis=0,
    )
    return learned - np.max(controls, axis=0)
