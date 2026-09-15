from __future__ import annotations

import numpy as np


def encode_swarm_field(
    x,
    y,
    heading,
    *,
    radial_bins: int = 6,
    angular_bins: int = 12,
    max_radius: float = 1.5,
    previous_distance=None,
):
    """Encode receiver positions around the TV into a dense spatial field.

    The lure sees population geometry rather than individual identities. Channels:
    occupancy, mean heading-toward-TV alignment, and radial progress. The result is
    deterministic and permutation-invariant over receiver flies.
    """
    x = np.asarray(x, dtype=np.float64).reshape(-1)
    y = np.asarray(y, dtype=np.float64).reshape(-1)
    heading = np.asarray(heading, dtype=np.float64).reshape(-1)
    if not (x.size == y.size == heading.size):
        raise ValueError("x/y/heading must align")
    if radial_bins < 1 or angular_bins < 1 or max_radius <= 0:
        raise ValueError("invalid swarm field dimensions")

    distance = np.hypot(x, y)
    angle = np.arctan2(y, x)
    bearing_to_tv = np.arctan2(-y, -x)
    alignment = np.cos(heading - bearing_to_tv)
    if previous_distance is None:
        progress = np.zeros_like(distance)
    else:
        prev = np.asarray(previous_distance, dtype=np.float64).reshape(-1)
        if prev.size != distance.size:
            raise ValueError("previous_distance must align")
        progress = np.clip(prev - distance, -0.1, 0.1) / 0.1

    rb = np.minimum((distance / max_radius * radial_bins).astype(np.int64), radial_bins - 1)
    rb = np.clip(rb, 0, radial_bins - 1)
    ab = np.floor((angle + np.pi) / (2 * np.pi) * angular_bins).astype(np.int64) % angular_bins

    occupancy = np.zeros((radial_bins, angular_bins), dtype=np.float32)
    align_sum = np.zeros_like(occupancy)
    progress_sum = np.zeros_like(occupancy)
    for r, a, al, pr in zip(rb, ab, alignment, progress, strict=True):
        occupancy[r, a] += 1.0
        align_sum[r, a] += np.float32(al)
        progress_sum[r, a] += np.float32(pr)
    denom = np.maximum(occupancy, 1.0)
    align_mean = align_sum / denom
    progress_mean = progress_sum / denom
    occupancy /= max(float(x.size), 1.0)
    return np.concatenate((occupancy.ravel(), align_mean.ravel(), progress_mean.ravel())).astype(np.float32)


def attraction_reward(previous_distance, distance, *, capture_radius: float = 0.12, near_radius: float = 0.35):
    """Population reward for moving receivers toward the TV and into capture zones."""
    prev = np.asarray(previous_distance, dtype=np.float64).reshape(-1)
    cur = np.asarray(distance, dtype=np.float64).reshape(-1)
    if prev.size != cur.size:
        raise ValueError("distance arrays must align")
    progress = np.clip(prev - cur, -0.05, 0.05) / 0.05
    near = (cur <= near_radius).astype(np.float64)
    capture = (cur <= capture_radius).astype(np.float64)
    # Progress remains the dense signal; entering close/capture zones dominates.
    per_fly = progress + 1.5 * near + 5.0 * capture
    return float(per_fly.mean()), per_fly.astype(np.float32)
