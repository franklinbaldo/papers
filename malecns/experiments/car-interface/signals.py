"""Cheap lawful scalar channels derived from reality-bounded observations."""

from __future__ import annotations

import math

from interface import DerivedSignals, ObdObservation, PhoneObservation


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def derive_signals(
    phone: PhoneObservation,
    obd: ObdObservation,
    *,
    wheelbase_m: float = 2.7,
    gnss_good_accuracy_m: float = 3.0,
    gnss_bad_accuracy_m: float = 25.0,
) -> DerivedSignals:
    """Fuse only real-car-observable channels into compact scalars.

    Missing inputs remain missing rather than being imputed from simulator truth.
    """

    speed_disagreement = None
    if phone.gps_speed_kph is not None and obd.speed_kph is not None:
        speed_disagreement = abs(phone.gps_speed_kph - obd.speed_kph)

    wheel_spread = None
    if obd.wheel_speeds_kph is not None and len(obd.wheel_speeds_kph) > 0:
        wheel_spread = max(obd.wheel_speeds_kph) - min(obd.wheel_speeds_kph)

    steering_yaw_residual = None
    if (
        obd.speed_kph is not None
        and obd.steering_angle_rad is not None
        and phone.gyro_xyz_rps is not None
        and wheelbase_m > 0
    ):
        speed_mps = obd.speed_kph / 3.6
        expected_yaw_rps = speed_mps / wheelbase_m * math.tan(obd.steering_angle_rad)
        measured_yaw_rps = phone.gyro_xyz_rps[2]
        steering_yaw_residual = abs(measured_yaw_rps - expected_yaw_rps)

    gnss_confidence = None
    if phone.gps_accuracy_m is not None:
        if gnss_bad_accuracy_m <= gnss_good_accuracy_m:
            raise ValueError("gnss_bad_accuracy_m must exceed gnss_good_accuracy_m")
        normalized = (gnss_bad_accuracy_m - phone.gps_accuracy_m) / (
            gnss_bad_accuracy_m - gnss_good_accuracy_m
        )
        gnss_confidence = clamp01(normalized)

    return DerivedSignals(
        speed_disagreement_kph=speed_disagreement,
        wheel_speed_spread_kph=wheel_spread,
        steering_yaw_residual_rps=steering_yaw_residual,
        gnss_confidence=gnss_confidence,
    )
