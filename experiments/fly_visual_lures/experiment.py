"""Simulator-neutral scaffold for printable visual lure discovery.

The real fly simulator plugs into this later.  This file freezes the parts that
must not drift across simulators: printable patterns, paired swarm starts,
per-fly behavioural observations, robust scene aggregation and attraction maps.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import atan2, cos, pi, sin
from random import Random
from statistics import mean, median


@dataclass(frozen=True)
class BinaryPattern:
    size: int
    pixels: tuple[int, ...]

    def __post_init__(self) -> None:
        if self.size < 1 or len(self.pixels) != self.size * self.size:
            raise ValueError("pixels must contain size*size entries")
        if any(value not in (0, 1) for value in self.pixels):
            raise ValueError("binary pattern pixels must be 0 or 1")

    @property
    def black_fraction(self) -> float:
        return sum(self.pixels) / len(self.pixels)


def random_pattern(*, size: int = 32, black_probability: float = 0.5, seed: int = 0) -> BinaryPattern:
    if not 0.0 <= black_probability <= 1.0:
        raise ValueError("black_probability must be in [0,1]")
    rng = Random(seed)
    return BinaryPattern(size, tuple(int(rng.random() < black_probability) for _ in range(size * size)))


def mutate(pattern: BinaryPattern, *, flips: int, seed: int) -> BinaryPattern:
    if not 0 <= flips <= len(pattern.pixels):
        raise ValueError("flips out of range")
    rng = Random(seed)
    pixels = list(pattern.pixels)
    for index in rng.sample(range(len(pixels)), flips):
        pixels[index] = 1 - pixels[index]
    return BinaryPattern(pattern.size, tuple(pixels))


@dataclass(frozen=True)
class FlyStart:
    fly_id: int
    x: float
    y: float
    heading: float
    speed: float = 0.0


def radial_swarm(*, flies: int, radius: float, seed: int) -> tuple[FlyStart, ...]:
    """Deterministic multi-view swarm around a target at the origin."""
    if flies < 1 or radius <= 0:
        raise ValueError("flies >= 1 and radius > 0 required")
    rng = Random(seed)
    starts = []
    for fly_id in range(flies):
        angle = 2 * pi * (fly_id / flies)
        jitter = rng.uniform(-pi / flies, pi / flies)
        position_angle = angle + jitter
        x, y = radius * cos(position_angle), radius * sin(position_angle)
        # Random initial heading: the lure must capture orientation rather than
        # receiving agents already pointed at it.
        heading = rng.uniform(-pi, pi)
        starts.append(FlyStart(fly_id, x, y, heading))
    return tuple(starts)


@dataclass(frozen=True)
class FlyObservation:
    fly_id: int
    start_x: float
    start_y: float
    orientation: float
    approach: float
    dwell: float
    landing: float
    avoidance: float

    @property
    def start_angle(self) -> float:
        return atan2(self.start_y, self.start_x)


def fly_score(obs: FlyObservation, weights: dict[str, float]) -> float:
    return (
        weights["orientation"] * obs.orientation
        + weights["approach"] * obs.approach
        + weights["dwell"] * obs.dwell
        + weights["landing"] * obs.landing
        - weights["avoidance"] * obs.avoidance
    )


def scene_summary(observations: tuple[FlyObservation, ...], weights: dict[str, float]) -> dict:
    """Aggregate a shared-scene swarm without pretending flies are independent scenes."""
    if not observations:
        raise ValueError("at least one observation required")
    scores = sorted(fly_score(obs, weights) for obs in observations)
    lower_index = max(0, int(0.25 * (len(scores) - 1)))
    return {
        "flies": len(scores),
        "mean_score": mean(scores),
        "median_score": median(scores),
        "lower_quartile_score": scores[lower_index],
        "approach_rate": mean(float(obs.approach > 0) for obs in observations),
        "mean_dwell": mean(obs.dwell for obs in observations),
        "landing_rate": mean(float(obs.landing > 0) for obs in observations),
    }


def attraction_by_sector(
    observations: tuple[FlyObservation, ...],
    weights: dict[str, float],
    *,
    sectors: int = 8,
) -> tuple[float, ...]:
    """Spatial attraction field around the same frozen drawing."""
    if sectors < 1:
        raise ValueError("sectors must be >= 1")
    buckets: list[list[float]] = [[] for _ in range(sectors)]
    for obs in observations:
        normalized = (obs.start_angle + pi) / (2 * pi)
        index = min(sectors - 1, int(normalized * sectors))
        buckets[index].append(fly_score(obs, weights))
    return tuple(mean(bucket) if bucket else float("nan") for bucket in buckets)


def paired_scene_delta(candidate: dict, control: dict) -> float:
    """Candidate/control must share the exact same scene/swarm seed upstream."""
    return float(candidate["mean_score"] - control["mean_score"])
