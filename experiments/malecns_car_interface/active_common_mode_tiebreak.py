"""Reality-bounded common-mode conflict detector with on-demand independent tie-break.

The primary path observes only matched-time OBD-II speed, GNSS speed, and
camera ego-speed. It detects a persistent pattern where OBD and GNSS agree
with one another while jointly disagreeing with camera ego-motion. That
pattern is evidence of *conflict*, not proof that either side is correct.

When requested, an external low-cost LiDAR ego-speed estimate can be supplied
as a fourth, independent witness. The resolver compares which side the LiDAR
supports and either keeps the OBD/GNSS pair, combines camera+LiDAR, or conservatively keeps the OBD/GNSS pair when the auxiliary witness is
ambiguous. No simulator truth, fault label, pose, map,
future sample, or hidden timestamp enters this module.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
import statistics


@dataclass(frozen=True)
class PrimaryConflictObservation:
    pair_estimate: float
    request_aux: bool
    conflict_score: float
    pair_gap: float
    pair_camera_gap: float
    supporting_samples: int


@dataclass(frozen=True)
class TieBreakObservation:
    estimate: float
    choice: str
    lidar_pair_gap: float
    lidar_camera_gap: float


@dataclass
class ActiveCommonModeTieBreak:
    window: int = 8
    min_conflicts: int = 6
    pair_agreement_max: float = 0.90
    camera_conflict_min: float = 0.90
    aux_margin: float = 0.15
    _flags: deque[bool] = field(init=False, repr=False)
    _signed_pair_camera: deque[float] = field(init=False, repr=False)
    _last_pair: float = field(default=0.0, init=False, repr=False)
    _last_camera: float = field(default=0.0, init=False, repr=False)
    _last_request: bool = field(default=False, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.window < 2:
            raise ValueError("window must be >= 2")
        if not 1 <= self.min_conflicts <= self.window:
            raise ValueError("min_conflicts must be within the window")
        self._flags = deque(maxlen=self.window)
        self._signed_pair_camera = deque(maxlen=self.window)

    def observe_primary(
        self,
        *,
        obd_speed: float,
        gnss_speed: float,
        camera_speed: float,
    ) -> PrimaryConflictObservation:
        pair = (obd_speed + gnss_speed) / 2.0
        pair_gap = abs(obd_speed - gnss_speed)
        signed = pair - camera_speed
        conflict = (
            pair_gap <= self.pair_agreement_max
            and abs(signed) >= self.camera_conflict_min
        )

        self._flags.append(conflict)
        self._signed_pair_camera.append(signed)

        request = False
        score = 0.0
        if len(self._flags) == self.window:
            median_signed = statistics.median(self._signed_pair_camera)
            majority_positive = median_signed >= 0.0
            same_sign = sum(
                1
                for value in self._signed_pair_camera
                if (value >= 0.0) == majority_positive
            )
            request = (
                sum(self._flags) >= self.min_conflicts
                and same_sign >= self.min_conflicts
            )
            score = (
                sum(self._flags) / self.window
            ) * abs(median_signed)

        self._last_pair = pair
        self._last_camera = camera_speed
        self._last_request = request
        return PrimaryConflictObservation(
            pair_estimate=pair,
            request_aux=request,
            conflict_score=score,
            pair_gap=pair_gap,
            pair_camera_gap=abs(signed),
            supporting_samples=len(self._flags),
        )

    def resolve_aux(self, *, lidar_speed: float) -> TieBreakObservation:
        if not self._last_request:
            return TieBreakObservation(
                estimate=self._last_pair,
                choice="pair_no_request",
                lidar_pair_gap=abs(lidar_speed - self._last_pair),
                lidar_camera_gap=abs(lidar_speed - self._last_camera),
            )

        lidar_pair_gap = abs(lidar_speed - self._last_pair)
        lidar_camera_gap = abs(lidar_speed - self._last_camera)

        if lidar_camera_gap + self.aux_margin < lidar_pair_gap:
            return TieBreakObservation(
                estimate=(lidar_speed + self._last_camera) / 2.0,
                choice="camera_aux",
                lidar_pair_gap=lidar_pair_gap,
                lidar_camera_gap=lidar_camera_gap,
            )

        if lidar_pair_gap + self.aux_margin < lidar_camera_gap:
            return TieBreakObservation(
                estimate=self._last_pair,
                choice="pair_aux",
                lidar_pair_gap=lidar_pair_gap,
                lidar_camera_gap=lidar_camera_gap,
            )

        return TieBreakObservation(
            estimate=self._last_pair,
            choice="ambiguous_hold_pair",
            lidar_pair_gap=lidar_pair_gap,
            lidar_camera_gap=lidar_camera_gap,
        )
