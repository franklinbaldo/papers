---
type: "Findings Record"
title: "MaleCNS Car Interface Run 20: causal clock-offset estimation and repair"
description: "A causal GNSS↔phone-IMU offset estimator can repair fixed timestamp offsets before OBD/GNSS fusion and materially reduce error under offset and offset+jitter, but it slightly harms clean/jitter-only regimes and only weakly tracks drift."
tags: [malecns, driving, obd-ii, gnss, android, imu, sensor-fusion, timebase, clock-offset, experiment]
timestamp: 2026-09-19T12:54:00-04:00
---

# Run 20 — repair the clock instead of merely distrusting it

Run 19 exposed phone-IMU kinematic consistency as a weak clock-health witness. Run 20 asks a stricter question: can the same lawful observations estimate a persistent GNSS timestamp offset and repair the matching time before robust OBD/GNSS fusion?

The new `RobustClockOffsetEstimator` searches offsets from -6 to +6 OBD steps over a causal rolling window of GNSS speed-delta pairs. Each candidate is scored by robust Huber loss between GNSS delta-speed and phone-IMU delta-v integrated over the shifted reported interval. A non-zero offset is applied only when its magnitude is at least two 100 ms steps and it reduces robust loss versus zero offset by at least 8%.

A positive estimate means the GNSS-reported time is ahead of the phone monotonic/IMU timebase and is shifted backwards before matching against OBD history.

## Reality boundary

The estimator sees only already-observed GNSS speed values, GNSS-reported measurement indices, phone longitudinal IMU samples, OBD history, residual history, and declared nominal noise scales. Candidate intervals whose end would lie after the current arrival time are not eligible even when a synthetic harness has later samples in memory. Synthetic true speed and actual GNSS measurement time exist only on the generator/scoring side.

The discrete helper in this run explicitly matches the harness state-update convention (`v[e]-v[s]` integrates acceleration samples `s+1..e`). Real deployment must replace integer indices with monotonic timestamps plus interpolation/integration; this run does not claim the integer helper is production clock synchronization.

## Executed validation

The staged algorithm was exercised with 3 seeds × 100 episodes × 15 conditions × 500 steps: OBD `clean/static/drift` crossed with GNSS time `clean/offset/jitter/drift/offset+jitter`. GNSS remained 2 Hz with 0.4–1.2 s arrival delay and 15% dropout; OBD remained 10 Hz. Fixed clock offset was +0.3 s, jitter ±0.2 s, and the drift arm retained the deliberately severe Run-19 stress setting.

`python -m unittest -v test_clock_offset_estimation.py` → **4/4 passed**.

### Clean OBD

| GNSS time mode | covariance, raw reported time | covariance after offset repair | delta |
|---|---:|---:|---:|
| clean | 0.148438 | 0.150057 | **1.09% worse** |
| +0.3 s offset | 0.194520 | **0.157802** | **18.88% better** |
| jitter only | 0.153766 | 0.157580 | **2.48% worse** |
| drift stress | 0.159260 | **0.156827** | **1.53% better** |
| offset + jitter | 0.200688 | **0.165437** | **17.57% better** |

Under the fixed-offset arm the mean applied correction was about `2.526` 100 ms steps and it was active for about `79.0%` of eligible updates; under offset+jitter those figures were `2.368` steps and `70.7%`. The true injected fixed offset was three steps, but that truth was not exposed to the estimator.

The clean-clock arm is an important negative control. Offset repair activated on about `9.0%` of eligible updates and made MAE ~1.09% worse. Jitter-only also worsened by ~2.48%. The 8% loss-improvement gate therefore reduces false repair substantially but does not eliminate it.

### Static OBD bias

| GNSS time mode | raw-time covariance | offset-repaired covariance | delta |
|---|---:|---:|---:|
| clean | 0.306358 | 0.309941 | 1.17% worse |
| +0.3 s offset | 0.373899 | **0.323550** | **13.47% better** |
| jitter only | 0.317982 | 0.324077 | 1.92% worse |
| drift stress | 0.335593 | **0.327470** | **2.42% better** |
| offset + jitter | 0.376805 | **0.338648** | **10.13% better** |

### Drifting OBD bias

| GNSS time mode | raw-time covariance | offset-repaired covariance | delta |
|---|---:|---:|---:|
| clean | 0.270602 | 0.271748 | 0.42% worse |
| +0.3 s offset | 0.289562 | **0.267791** | **7.52% better** |
| jitter only | 0.268993 | 0.270429 | 0.53% worse |
| drift stress | 0.275443 | 0.275199 | 0.09% better |
| offset + jitter | 0.298586 | **0.280322** | **6.12% better** |

The repair remains useful when OBD itself has persistent error, but its advantage shrinks because time repair does not solve sensor bias. Slow clock drift is also only weakly handled by a single integer offset.

## Interpretation

This result changes the role of `timebase_health`. A low clock-merit scalar is useful as a warning, but a sufficiently evidenced persistent offset can be treated first as an engineering synchronization problem and explicitly repaired. The MaleCNS coordinator should not get credit for learning around a deterministic offset that an observable clock estimator can remove.

The remaining decision problem is more suitable for an active coordinator: when offset evidence is weak or inconsistent, decide whether to request another GNSS fix, recruit camera ego-motion, inspect Android rotation/gravity quality, spend compute on another witness, or temporarily quarantine a timing domain.

## Candidate channel record

| signal | cost | rate/latency | real-car availability | simulator/mock method | privacy/safety | ablation |
|---|---|---|---|---|---|---|
| estimated clock offset | small robust search over <=13 offsets × <=40 recent fix pairs | updates at GNSS fix rate after enough pairs | yes; derived from phone IMU + GNSS reports | inject offset/jitter/drift while hiding actual measurement time | derived scalar; no raw location history required beyond rolling window | disable repair while preserving identical observations |
| offset evidence / relative loss gain | negligible after same search | GNSS rate | yes | same stress matrix | safe as diagnostic; avoid interpreting as proof of sensor correctness | fixed threshold sweep on held-out calibration streams |
| offset-active flag | one bit | GNSS rate | yes | same | should trigger conservative interface behavior, not direct actuation | repair vs warning-only at equal sensor availability |

The same pattern can generalize to camera frame timestamps vs IMU rotation, low-cost LiDAR scan timestamps vs IMU, or emitted ultrasonic pulse timestamps vs monotonic phone/controller time, provided the witness is physically observed rather than simulator-provided.

## Cache/dependency accounting

No CARLA assets, datasets, model weights, Python packages, or simulator bundles were downloaded. **No heavyweight cache miss occurred.** The run reused the existing standard-library synthetic harness and previously committed fusion/calibration code. The calendar-day MaleCNS embodied-control prior-art scan and autonomous-driving dataset/benchmark/safety review were already present in the repository for 2026-09-19, so this run did not duplicate them.

## Limits and next falsification

1. The estimator is integer-step only; production needs continuous monotonic timestamps and interpolation/sub-step offset estimation.
2. It slightly harms clean and jitter-only streams, so the activation policy is not yet strong enough to be a universal preprocessor.
3. The IMU witness can itself fail through mounting rotation, gravity leakage, thermal bias, clipping/saturation, or Android sensor-pipeline artifacts; these must be stress-tested next.
4. Slow clock drift is not well represented by one persistent offset. A joint offset+drift model should be compared against this control.
5. The first checksum-pinned synchronized real OBD/GNSS or camera/IMU slice remains required before any road-data performance claim.
