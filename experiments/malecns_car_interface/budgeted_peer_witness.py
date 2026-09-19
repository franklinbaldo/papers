"""Budgeted peer-Wi-Fi witness before LiDAR escalation.

The policy sees only OBD/GNSS/camera values, a peer token containing a peer-observed
host-speed estimate plus declared confidence/age, and optional LiDAR speed. It never
receives simulator truth, fault labels, pose, map, or future samples.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

from active_common_mode_tiebreak import (
    ActiveCommonModeTieBreak,
    PrimaryConflictObservation,
)


@dataclass(frozen=True)
class PeerToken:
    speed: float
    confidence: float
    age_s: float


@dataclass(frozen=True)
class PeerDecision:
    estimate: float
    choice: str
    resolved: bool
    effective_confidence: float
    pair_gap: float
    camera_gap: float
    margin: float


@dataclass
class AcquisitionBudget:
    total_units: int = 150
    remaining_units: int = 150
    spent_peer: int = 0
    spent_lidar: int = 0
    peer_cost: int = 1
    lidar_cost: int = 5

    def __post_init__(self) -> None:
        if self.total_units <= 0 or self.peer_cost <= 0 or self.lidar_cost <= 0:
            raise ValueError("budget and costs must be positive")
        self.remaining_units = self.total_units

    def buy_peer(self) -> bool:
        if self.remaining_units < self.peer_cost:
            return False
        self.remaining_units -= self.peer_cost
        self.spent_peer += self.peer_cost
        return True

    def buy_lidar(self) -> bool:
        if self.remaining_units < self.lidar_cost:
            return False
        self.remaining_units -= self.lidar_cost
        self.spent_lidar += self.lidar_cost
        return True

    @property
    def spent_total(self) -> int:
        return self.spent_peer + self.spent_lidar


@dataclass
class PeerFirstResolver:
    min_effective_confidence: float = 0.55
    decisive_margin_mps: float = 0.20
    age_decay_s: float = 0.75

    def resolve(
        self,
        *,
        pair_speed: float,
        camera_speed: float,
        token: PeerToken,
    ) -> PeerDecision:
        confidence = max(0.0, min(1.0, token.confidence))
        age = max(0.0, token.age_s)
        effective = confidence * math.exp(-age / self.age_decay_s)
        pair_gap = abs(token.speed - pair_speed)
        camera_gap = abs(token.speed - camera_speed)
        margin = abs(pair_gap - camera_gap)
        if effective < self.min_effective_confidence or margin < self.decisive_margin_mps:
            return PeerDecision(
                pair_speed,
                "peer_ambiguous",
                False,
                effective,
                pair_gap,
                camera_gap,
                margin,
            )
        if camera_gap < pair_gap:
            weight = min(0.75, max(0.50, effective))
            estimate = weight * token.speed + (1.0 - weight) * camera_speed
            return PeerDecision(
                estimate,
                "camera_peer",
                True,
                effective,
                pair_gap,
                camera_gap,
                margin,
            )
        return PeerDecision(
            pair_speed,
            "pair_peer",
            True,
            effective,
            pair_gap,
            camera_gap,
            margin,
        )


@dataclass
class BudgetedPeerFirstPolicy:
    budget_units: int = 150
    peer_cost: int = 1
    lidar_cost: int = 5
    lidar_escalation_score_min: float = 1.50

    def __post_init__(self) -> None:
        self.detector = ActiveCommonModeTieBreak()
        self.peer = PeerFirstResolver()
        self.budget = AcquisitionBudget(
            self.budget_units,
            self.budget_units,
            peer_cost=self.peer_cost,
            lidar_cost=self.lidar_cost,
        )

    def observe_primary(
        self,
        *,
        obd_speed: float,
        gnss_speed: float,
        camera_speed: float,
    ) -> PrimaryConflictObservation:
        return self.detector.observe_primary(
            obd_speed=obd_speed,
            gnss_speed=gnss_speed,
            camera_speed=camera_speed,
        )

    def resolve(
        self,
        *,
        primary: PrimaryConflictObservation,
        camera_speed: float,
        peer_token: PeerToken | None,
        lidar_speed: float | None,
    ) -> tuple[float, str]:
        if not primary.request_aux:
            return primary.pair_estimate, "no_conflict"

        if peer_token is not None and self.budget.buy_peer():
            peer = self.peer.resolve(
                pair_speed=primary.pair_estimate,
                camera_speed=camera_speed,
                token=peer_token,
            )
            if peer.resolved:
                return peer.estimate, peer.choice

        if (
            lidar_speed is not None
            and primary.conflict_score >= self.lidar_escalation_score_min
            and self.budget.buy_lidar()
        ):
            obs = self.detector.resolve_aux(lidar_speed=lidar_speed)
            return obs.estimate, obs.choice

        return primary.pair_estimate, "budget_or_witness_unavailable"
