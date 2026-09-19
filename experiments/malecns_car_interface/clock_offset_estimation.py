"""Reality-bounded clock-offset estimation from GNSS speed change and phone IMU.

The estimator searches a small causal window of candidate timestamp offsets and
scores each candidate by how well GNSS speed deltas agree with longitudinal
phone-IMU delta-v over the shifted interval. It consumes only already-observed
sensor samples and reported timestamps. No simulator truth, fault label, future
sample, pose, or map state is accepted.
"""

from __future__ import annotations

from dataclasses import dataclass, field


def _huber_loss(residual: float, delta: float) -> float:
    if delta <= 0.0:
        raise ValueError("delta must be positive")
    magnitude = abs(residual)
    if magnitude <= delta:
        return 0.5 * magnitude * magnitude
    return delta * (magnitude - 0.5 * delta)


def speed_interval_delta_v(
    prefix_delta_v: list[float], start_speed_index: int, end_speed_index: int
) -> float:
    """Integrate IMU acceleration between two sampled speed states.

    The Run-20 discrete harness updates speed with acceleration sample ``i`` and
    then stores speed state ``i``. Therefore ``v[e] - v[s]`` corresponds to
    acceleration samples ``s+1 .. e``. Real deployments should replace this
    integer-index helper with monotonic timestamp interpolation/integration.
    """

    if start_speed_index < 0 or end_speed_index <= start_speed_index:
        raise ValueError("invalid speed interval")
    if end_speed_index + 1 >= len(prefix_delta_v):
        raise ValueError("speed interval exceeds IMU prefix buffer")
    return (
        prefix_delta_v[end_speed_index + 1]
        - prefix_delta_v[start_speed_index + 1]
    )


@dataclass(frozen=True)
class ClockOffsetObservation:
    applied_offset_steps: int
    candidate_offset_steps: int
    relative_gain_over_zero: float
    active: bool
    pairs_used: int


@dataclass
class RobustClockOffsetEstimator:
    """Estimate a persistent reported-clock offset from observed kinematics.

    A positive offset means the candidate sensor timestamp is ahead of the phone
    monotonic/IMU timebase and should be shifted backwards before matching it to
    OBD history. The correction is activated only when a non-trivial candidate
    beats zero offset by a declared relative robust-loss margin.
    """

    max_offset_steps: int = 6
    window_pairs: int = 40
    min_pairs: int = 8
    huber_delta_v: float = 0.55
    min_abs_offset_steps: int = 2
    min_relative_gain: float = 0.08
    applied_offset_steps: int = 0
    candidate_offset_steps: int = 0
    relative_gain_over_zero: float = 0.0
    _pairs: list[tuple[float, float, int, int]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.max_offset_steps < 1:
            raise ValueError("max_offset_steps must be >= 1")
        if self.window_pairs < 1 or self.min_pairs < 1:
            raise ValueError("window_pairs/min_pairs must be >= 1")
        if self.min_pairs > self.window_pairs:
            raise ValueError("min_pairs must not exceed window_pairs")
        if self.huber_delta_v <= 0.0:
            raise ValueError("huber_delta_v must be positive")
        if self.min_abs_offset_steps < 1:
            raise ValueError("min_abs_offset_steps must be >= 1")
        if not 0.0 <= self.min_relative_gain < 1.0:
            raise ValueError("min_relative_gain must be in [0, 1)")

    def observe_pair(
        self,
        *,
        previous_speed: float,
        current_speed: float,
        previous_reported_index: int,
        current_reported_index: int,
        imu_prefix_delta_v: list[float],
        available_end_index: int,
    ) -> ClockOffsetObservation:
        """Update using one causal pair of reported speed fixes.

        Candidate intervals ending after ``available_end_index`` are discarded,
        even if the caller's in-memory prefix buffer happens to contain later
        samples. This makes future leakage structurally unnecessary.
        """

        if available_end_index < 0:
            raise ValueError("available_end_index must be non-negative")
        if current_reported_index <= previous_reported_index:
            return self.observation()

        self._pairs.append(
            (
                previous_speed,
                current_speed,
                previous_reported_index,
                current_reported_index,
            )
        )
        if len(self._pairs) > self.window_pairs:
            self._pairs = self._pairs[-self.window_pairs :]
        if len(self._pairs) < self.min_pairs:
            return self.observation()

        losses: dict[int, float] = {}
        pair_counts: dict[int, int] = {}
        for offset_steps in range(-self.max_offset_steps, self.max_offset_steps + 1):
            candidate_losses: list[float] = []
            for prev_speed, cur_speed, prev_reported, cur_reported in self._pairs:
                start_index = prev_reported - offset_steps
                end_index = cur_reported - offset_steps
                if (
                    start_index < 0
                    or end_index <= start_index
                    or end_index > available_end_index
                    or end_index + 1 >= len(imu_prefix_delta_v)
                ):
                    continue
                imu_delta_v = speed_interval_delta_v(
                    imu_prefix_delta_v,
                    start_index,
                    end_index,
                )
                residual = (cur_speed - prev_speed) - imu_delta_v
                candidate_losses.append(_huber_loss(residual, self.huber_delta_v))
            if len(candidate_losses) >= self.min_pairs:
                losses[offset_steps] = sum(candidate_losses) / len(candidate_losses)
                pair_counts[offset_steps] = len(candidate_losses)

        if 0 not in losses:
            return self.observation()

        best_offset = min(
            losses,
            key=lambda offset: (
                losses[offset],
                abs(offset - self.candidate_offset_steps),
                abs(offset),
            ),
        )
        zero_loss = losses[0]
        best_loss = losses[best_offset]
        gain = max(0.0, (zero_loss - best_loss) / max(zero_loss, 1e-12))

        self.candidate_offset_steps = best_offset
        self.relative_gain_over_zero = gain
        if (
            abs(best_offset) >= self.min_abs_offset_steps
            and gain >= self.min_relative_gain
        ):
            self.applied_offset_steps = best_offset
        else:
            self.applied_offset_steps = 0

        return ClockOffsetObservation(
            applied_offset_steps=self.applied_offset_steps,
            candidate_offset_steps=self.candidate_offset_steps,
            relative_gain_over_zero=self.relative_gain_over_zero,
            active=self.applied_offset_steps != 0,
            pairs_used=pair_counts.get(best_offset, 0),
        )

    def corrected_index(self, reported_index: int, available_end_index: int) -> int:
        if reported_index < 0 or available_end_index < 0:
            raise ValueError("indices must be non-negative")
        return max(
            0,
            min(
                available_end_index,
                reported_index - self.applied_offset_steps,
            ),
        )

    def observation(self) -> ClockOffsetObservation:
        return ClockOffsetObservation(
            applied_offset_steps=self.applied_offset_steps,
            candidate_offset_steps=self.candidate_offset_steps,
            relative_gain_over_zero=self.relative_gain_over_zero,
            active=self.applied_offset_steps != 0,
            pairs_used=min(len(self._pairs), self.window_pairs),
        )
