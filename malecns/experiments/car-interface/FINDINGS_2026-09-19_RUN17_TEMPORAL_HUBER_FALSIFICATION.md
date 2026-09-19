---
type: "Findings Record"
title: "MaleCNS Car Interface Run 17: temporal alignment falsifies a universal age-contracted Huber rule"
description: "On the asynchronous OBD-II/GNSS harness, transporting delayed GNSS by an already-observed OBD delta removes lawful motion from the residual. After that alignment, contracting the Huber radius with age helps the clean/noisy-GNSS case but is consistently worse than a fixed Huber radius when OBD has persistent static, drifting, or step bias. The Run-14 age-radius mechanism is therefore retained only as a conservative heuristic, not a general physical law."
tags: [malecns, driving, obd-ii, gnss, sensor-fusion, temporal-alignment, huber, robust-estimation, falsification, experiment]
timestamp: 2026-09-19T09:58:00-04:00
---

# Run 17 — align time before deciding how much age should matter

## Question and predeclared discriminator

Run 14 found that a Huber residual radius contracting with freshness improved on a fixed-scale Cauchy baseline in a snapshot synthetic generator. The later prior-art/falsification audit opened issue #646 with a harder discriminator: stale observations in a moving system should first be compared at the same physical time, and the age-dependent radius should lose any mechanism-level claim if proper temporal handling removes its advantage.

Run 15 then demonstrated the identification problem directly for asynchronous OBD-II/GNSS: comparing `GNSS(t_measurement)` with `OBD(t_arrival)` can manufacture disagreement out of ordinary acceleration. Run 17 joins those threads.

The concrete question is:

> after transporting a delayed GNSS fix to the current time using only the OBD change already observed between measurement and arrival, does the Run-14 age-contracted Huber radius still dominate a fixed Huber radius?

This is a falsification-oriented synthetic interface test, **not a real-road performance result** and not a test of MaleCNS itself yet. Its purpose is to strengthen the conventional baseline that a later MaleCNS coordinator must beat.

## Reality boundary

Every deployable estimator in this run receives only quantities reproducible in an ordinary car with a phone and OBD-II adapter:

- timestamped OBD speed already observed at 10 Hz;
- timestamped GNSS speed from the phone at 2 Hz;
- the GNSS measurement timestamp and its arrival time;
- historical OBD samples that were already observed;
- the age of the most recent GNSS fix.

No estimator receives latent true speed, the injected bias mode, a fault flag, future samples, perfect pose, map/object truth, CARLA state, or any other privileged simulator quantity. Latent speed exists only inside the harness to generate sensor observations and score final MAE.

## Concrete implementation

Added `temporal_robust_fusion.py` with three small reusable primitives:

1. `transport_by_reference_delta()` transports a delayed candidate using the reference sensor's already-observed change:

   `GNSS_now_proxy = GNSS(t0) + [OBD(t1) - OBD(t0)]`

2. `robust_fusion_weight()` computes freshness times a Huber residual weight from a **matched-time residual**. `age_power=0` is the fixed-radius control; `age_power=1` reproduces the age-contracted radius mechanism.
3. `fuse()` applies the resulting non-negative influence weight.

Added `obd_gnss_temporal_robustness_ablation.py`, which compares six methods on the same episodes:

- `obd_only`;
- `raw_fixed_huber`: delayed GNSS fused directly, fixed Huber radius;
- `raw_age_huber`: delayed GNSS fused directly, age-contracted radius;
- `transport_fixed_huber`: GNSS first transported with observed OBD delta, then fixed Huber radius using the matched-time residual;
- `transport_age_huber`: the same proper temporal transport, but with the Run-14 age-contracted radius;
- `bias_calibrated`: the Run-15 persistent matched-time cross-modal bias calibrator.

`test_temporal_robust_fusion.py` adds four deterministic invariants: reference-delta transport, age contraction being more conservative at nonzero age, equality of fixed/age-contracted radii at zero age, and bounded convex fusion.

## Executed experiment

The exact standard-library implementation staged for this run was executed with:

- 5 independent seeds;
- 300 episodes per seed and condition;
- 250 steps per episode at 10 Hz;
- OBD speed at 10 Hz, Gaussian noise SD 0.18 m/s;
- GNSS speed at 2 Hz, Gaussian noise SD 0.45 m/s;
- GNSS delay uniformly 0.4–1.2 s;
- 15% GNSS dropout;
- fixed Huber base scale 0.75 m/s;
- age exponent 1.0 for the age-contracted variant;
- two dynamics profiles: `ordinary` and `maneuver_heavy`;
- four OBD regimes: `clean`, persistent `static` bias, slow `drift`, and persistent `jump` bias.

The maneuver-heavy profile increases acceleration-process noise, abrupt-maneuver probability, maneuver magnitude, and allowed acceleration range. It is intentionally a harder case for using a stale observation without first removing lawful state evolution.

### Unit validation

`python -m unittest -v test_temporal_robust_fusion.py`

Result: **4 passed**.

### MAE — ordinary dynamics

| OBD regime | OBD only | raw fixed Huber | raw age Huber | transported fixed Huber | transported age Huber | matched-time bias calibration |
|---|---:|---:|---:|---:|---:|---:|
| clean | 0.143769 | 0.204077 | 0.165229 | 0.185861 | **0.169391** | **0.143836** |
| static bias | 1.499707 | 1.258992 | 1.356714 | **1.223290** | 1.337485 | **0.426224** |
| drift | 0.382071 | 0.343080 | 0.349235 | **0.319713** | 0.336694 | 0.320909 |
| jump bias | 1.097012 | 0.966139 | 1.015347 | **0.958704** | 1.015918 | **0.578183** |

### MAE — maneuver-heavy dynamics

| OBD regime | OBD only | raw fixed Huber | raw age Huber | transported fixed Huber | transported age Huber | matched-time bias calibration |
|---|---:|---:|---:|---:|---:|---:|
| clean | 0.143852 | 0.247587 | 0.182645 | 0.185626 | **0.169294** | **0.143892** |
| static bias | 1.502874 | 1.322730 | 1.396444 | **1.225795** | 1.340251 | **0.425924** |
| drift | 0.378684 | 0.381320 | 0.367458 | 0.317906 | 0.334208 | **0.317338** |
| jump bias | 1.108329 | 1.025387 | 1.050872 | **0.969266** | 1.026711 | **0.581699** |

Bold within the Huber pair marks the better transported Huber variant; the calibration column is a separate estimator family rather than another Huber parameterization.

## What changed after proper temporal alignment

Temporal transport itself is valuable when motion is strong or the reference sensor is biased. Comparing `transport_fixed_huber` with `raw_fixed_huber`:

- ordinary static bias: MAE improves by about **2.84%**;
- ordinary drift: **6.81%**;
- ordinary jump: **0.77%**;
- maneuver-heavy static bias: **7.33%**;
- maneuver-heavy drift: **16.63%**;
- maneuver-heavy jump: **5.47%**.

In the maneuver-heavy clean condition, temporal transport cuts the fixed-Huber error by about **25.03%** (`0.247587 → 0.185626`). It still does not beat OBD-only because GNSS is deliberately noisier than OBD in the clean generator; this is an important control rather than a failure of time alignment.

## Falsification result: age contraction is a trade-off, not a law

Once both Huber variants receive the same time-aligned candidate and the same matched-time residual, the age-contracted radius has a clear split behavior.

Against transported fixed-radius Huber, age contraction is better only when OBD is clean:

- ordinary clean: `0.185861 → 0.169391`, about **8.86% lower MAE**;
- maneuver-heavy clean: `0.185626 → 0.169294`, about **8.80% lower MAE**.

But it is consistently worse when the reference OBD stream carries a persistent error:

- ordinary static bias: **9.34% worse**;
- ordinary drift: **5.31% worse**;
- ordinary jump: **5.97% worse**;
- maneuver-heavy static bias: **9.34% worse**;
- maneuver-heavy drift: **5.13% worse**;
- maneuver-heavy jump: **5.93% worse**.

The mechanism is straightforward. Contracting the Huber radius with age is conservative: it protects a clean, low-noise OBD reference from a noisier delayed GNSS candidate. The same conservatism becomes harmful when OBD itself is persistently wrong, because it suppresses the independent modality that could correct the reference.

Therefore the stronger Run-14 interpretation does **not** survive this discriminator. The supported statement is narrower:

> age-dependent Huber contraction is a useful conservative heuristic under some relative-noise/fault regimes; it is not a general physical rule for asynchronous sensor fusion.

This is exactly the kind of baseline failure mode a MaleCNS coordinator must not be credited for merely rediscovering.

## Why persistent matched-time history matters

A one-shot robust residual cannot by itself identify which modality is biased. The Run-15 `PersistentBiasCalibrator`, which accumulates matched-time residual evidence across arrivals, remains almost neutral in the clean condition (`0.143769 → 0.143836` ordinary; `0.143852 → 0.143892` maneuver-heavy) while strongly improving persistent static and jump faults.

In ordinary dynamics it reaches:

- static bias: **0.426224** versus 1.223290 for transported fixed Huber;
- jump bias: **0.578183** versus 0.958704;
- drift: 0.320909 versus 0.319713, effectively a near tie in this configuration.

This suggests a better architectural division of labor:

- deterministic time alignment removes disagreement caused by lawful dynamics;
- robust estimation bounds one-off influence;
- persistent cross-modal history identifies systematic disagreement;
- a learned/MaleCNS coordinator should spend its capacity on **active decisions**: whether to ask for another observation, activate a costly sensor, quarantine a modality, negotiate a corroborating Wi-Fi token, or escalate to YOLO/LLM processing.

## New coordinator channels exposed by this run

Two almost-free signals become legitimate candidate channels for the colony:

| candidate signal | cost | expected rate/latency | real-car availability | simulator/mock emulation | privacy/safety | required ablation |
|---|---|---|---|---|---|---|
| matched-time cross-modal residual | negligible arithmetic; uses existing buffers | whenever a delayed corroborator arrives; OBD/GNSS example ~2 Hz with 0.4–1.2 s delay | yes, from timestamped OBD + phone GNSS; analogous camera ego-motion↔IMU, LiDAR↔ultrasonic | delay/dropout/jitter plus declared sensor noise; no truth exposed | no new raw personal data beyond already-declared sensors; buffer timestamps carefully | remove it from coordinator state while holding sensors/compute fixed |
| residual persistence/evidence count | negligible state | updated per corroborating arrival | yes; derived locally from repeated matched-time residuals | inject persistent, drifting, step, and common-mode biases | avoid treating peer reputation or sensor quarantine as safety authority without independent corroboration | compare stateless residual threshold vs persistence vs learned policy under same fault schedule |

For Wi-Fi/RF multi-agent use, the same pattern can score a peer token only after later local corroboration; a message such as “hard braking/obstacle ahead” can be remembered without being trusted as privileged world truth.

## Cache and dependency accounting

This run downloaded **no CARLA assets, datasets, models, Python packages, or other heavyweight dependencies**. There was no heavyweight cache miss. The experiment reuses the existing Run-15 synthetic interface model and standard-library code. The real-data path remains gated by Run 16: a future synchronized OBD/GNSS slice must be checksum/version pinned and pass the preserved-timebase admission gate before it may be called real-data evidence.

The dedicated 2026-09-19 MaleCNS embodied-control prior-art review and autonomous-driving dataset/benchmark/safety review are already recorded in `RESEARCH_2026-09-19.md`; this run does not duplicate those daily scans.

## Limits and remaining issue #646 work

This run executes the temporal-alignment discriminator and the abrupt-maneuver stress, but it does **not** complete all of issue #646. Still pending are, at minimum:

- standardized-innovation/covariance-aware Huber under the same stream;
- explicit clock offset/drift/jitter stress beyond arrival latency;
- correlated cross-modal/reference bias;
- delayed corroboration with biased/heteroscedastic error;
- the checksum-pinned synchronized real sensor slice admitted by Run 16.

So issue #646 should remain open. The concrete next conventional baseline is covariance/innovation-normalized robust fusion **after** matched-time transport. Only after that and a real synchronized slice should a MaleCNS coordinator be credited for gains beyond ordinary sensor engineering.
