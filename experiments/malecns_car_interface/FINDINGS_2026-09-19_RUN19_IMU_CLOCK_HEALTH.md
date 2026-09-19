---
type: "Findings Record"
title: "MaleCNS Car Interface Run 19: phone-IMU kinematic clock-health merit"
description: "A reality-bounded phone-IMU kinematic consistency signal modestly protects covariance fusion from GNSS timestamp corruption, especially fixed offset plus jitter, but does not repair the timebase and should be treated as a guard/decision signal rather than a universal fusion rule."
tags: [malecns, driving, obd-ii, gnss, android, imu, sensor-fusion, timebase, clock-health, experiment]
timestamp: 2026-09-19T11:55:00-04:00
---

# Run 19 — phone IMU as an independent clock-health witness

Run 18 assumes that the reported sensor timestamp corresponds to the physical measurement instant. This run stress-tests that assumption using only signals available from an ordinary car plus phone: OBD-II speed, delayed GNSS speed with its reported time, and longitudinal phone-IMU acceleration on the phone monotonic timebase.

The new signal is:

`GNSS delta-speed over two reported timestamps - integrated phone-IMU acceleration over the same reported interval`

A bounded Huber merit derived from that residual attenuates the GNSS contribution when kinematic timing consistency degrades. It does not rewrite timestamps or receive hidden truth.

## Reality boundary

The estimator receives only observed OBD/GNSS/IMU samples, reported timestamps, residual history, persistent-bias state, and declared nominal noise scales. The generator uses true speed/acceleration and the true measurement instant only to create observations and score MAE; the estimator-facing `GnssFix` intentionally stores **no true measurement index**.

## Executed validation

Exact staged code was run with 3 seeds × 80 episodes per condition × 500 steps across 15 conditions: OBD `clean/static/drift` crossed with GNSS time `clean/offset/jitter/drift/offset+jitter`. GNSS was 2 Hz with 0.4–1.2 s arrival delay and 15% dropout; OBD was 10 Hz. Fixed offset was +0.3 s and jitter was ±0.2 s. The drift arm is deliberately severe (`0.006` index scaling) so it becomes visible inside a 50 s episode; it is a stress test, not a claim about normal Android oscillator drift.

`python -m unittest -v test_kinematic_clock_health.py` → **4/4 passed**.

### Clean OBD

| GNSS time mode | OBD/control | covariance | covariance + IMU clock | delta vs covariance |
|---|---:|---:|---:|---:|
| clean | 0.143546 | 0.148677 | **0.147416** | **0.85% better** |
| drift stress | 0.143748 | 0.158134 | **0.155344** | **1.76% better** |
| jitter | 0.143984 | 0.153535 | **0.150902** | **1.72% better** |
| +0.3 s offset | 0.148179 | 0.192182 | **0.184469** | **4.01% better** |
| offset + jitter | 0.148333 | 0.199772 | **0.189464** | **5.16% better** |

The important negative result is that `0.189464` is still much worse than the OBD/control `0.148333`. The IMU witness limits damage from bad timestamp assignment but does not repair the clock.

### Drifting OBD bias

| GNSS time mode | calibrator | covariance | covariance + IMU clock | delta vs covariance |
|---|---:|---:|---:|---:|
| clean | 0.290881 | **0.270213** | 0.270400 | **0.07% worse** |
| jitter | 0.286883 | 0.267508 | **0.266924** | **0.22% better** |
| +0.3 s offset | 0.300134 | 0.294359 | **0.290718** | **1.24% better** |
| offset + jitter | 0.301529 | 0.299982 | **0.294425** | **1.85% better** |

The new merit is essentially neutral when timing is clean and becomes more useful as the reported time degrades.

### Static OBD bias

Under offset+jitter, calibrator `0.364184`, covariance `0.384641`, covariance+IMU `0.376839`: the IMU witness recovers about **2.03%** relative to covariance but still loses to the simple calibrator. It is therefore not a universal winner.

## Signal quality

In the clean-OBD arm, mean absolute kinematic residual rose from about `0.537 m/s` with clean reported time to `0.601 m/s` under offset+jitter; mean merit fell from about `0.926` to `0.903`. The separation is modest. This is a weak independent witness, not an oracle.

## Architectural consequence

Timebase health should be a first-class coordinator channel. A MaleCNS controller can receive kinematic clock merit alongside freshness, innovation sigma, bias persistence, latency, queue depth, and compute budget, then decide whether to request a fresh fix, spend compute on camera ego-motion, quarantine a timebase, or recruit another independent witness.

It should **not** receive credit for compensating for deterministic timestamp-contract errors that conventional clock synchronization/acquisition-time metadata can fix first.

## Candidate channel record

| signal | cost | rate/latency | real-car availability | mock method | privacy/safety | ablation |
|---|---|---|---|---|---|---|
| phone-IMU kinematic clock merit | prefix-sum at IMU rate + one Huber score per GNSS fix | IMU 50–200 Hz; merit at GNSS rate | yes, ordinary Android phone | inject timestamp offset/jitter/drift | derived scalar; phone mounting/orientation must be handled safely | remove merit while keeping identical OBD/GNSS observations |
| kinematic residual delta-v | same arithmetic | corroborator rate | yes | same stress matrix plus IMU bias/noise sweeps | reveals driving dynamics; retain rolling statistics rather than raw history where possible | merit-only vs raw-residual vs neither |
| timebase quarantine request | negligible decision token | event-driven | yes in interface software | persistent-low-merit trigger | fail safe; never silently remove the only safety-critical channel | attenuation vs quarantine at equal sensor availability |

Camera ego-motion ↔ phone IMU is the natural next independent witness. Active ultrasonic/LiDAR can also timestamp emitted pulses/scans on the controller monotonic clock, making them useful timing anchors as well as geometry sensors.

## Cache/dependency accounting

No CARLA assets, datasets, weights, Python packages, or simulator bundles were downloaded. **No heavyweight cache miss occurred.** The calendar-day MaleCNS embodied-control prior-art scan and autonomous-driving datasets/benchmarks/safety review were already recorded in `RESEARCH_2026-09-19.md`, so this run did not duplicate them.

## Next falsification

The strongest next step is to corrupt the IMU witness itself—mounting rotation, gravity leakage, thermal bias, saturation—and then test continuous timestamp interpolation plus explicit observable clock-offset estimation. Common-mode cross-modal bias where OBD and GNSS agree while jointly wrong also remains pending, as does the first checksum-pinned synchronized real OBD/GNSS or camera/IMU slice.
