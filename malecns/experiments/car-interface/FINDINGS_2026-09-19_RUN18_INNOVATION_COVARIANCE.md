---
type: "Findings Record"
title: "MaleCNS Car Interface Run 18: innovation-normalized covariance merit after matched-time transport"
description: "A reality-bounded online innovation-scale baseline was tested after matched-time OBD-II/GNSS transport. Standardizing residuals helps persistent-fault regimes, and adding a coarse declared relative-noise prior removes most of the clean-regime penalty, but the covariance-aware hybrid still trails the bias calibrator by about 3.4% when the reference stream is clean. It improves the same calibrator by about 7.6-15.7% under static, drift, and jump bias."
tags: [malecns, driving, obd-ii, gnss, sensor-fusion, covariance, innovation, huber, robust-estimation, experiment]
timestamp: 2026-09-19T11:05:00-04:00
---

# Run 18 — normalize disagreement by observed innovation scale

## Question

Run 17 falsified the idea that contracting the Huber radius with signal age is a general physical rule. After lawful matched-time transport, age contraction helped only when the OBD reference was clean and the delayed GNSS channel was noisier; it hurt whenever OBD carried persistent bias.

Issue #646 therefore left a stronger conventional baseline pending: **standardize the matched-time residual by an observable innovation/covariance scale before applying robust influence control**.

Run 18 asks two narrower questions:

1. does online innovation normalization improve on a fixed physical-unit Huber radius under the same asynchronous stream; and
2. can a coarse declared relative-noise prior avoid over-trusting the noisier GNSS channel when OBD is healthy, without using simulator truth or fault identity?

This is still a synthetic interface test, not a real-road result and not evidence that MaleCNS itself improves driving.

## Reality boundary

Deployable methods receive only quantities reproducible from an ordinary car plus phone/OBD-II adapter:

- timestamped OBD speed;
- timestamped phone GNSS speed;
- already-observed historical OBD samples needed for matched-time transport;
- signal age;
- matched-time cross-modal residual history;
- persistent-bias evidence derived from that history;
- declared nominal per-channel noise scales.

The covariance-aware arm uses deliberately rounded nominal metadata of **0.20 m/s for OBD** and **0.50 m/s for GNSS**, rather than the generator's exact noise values (0.18 and 0.45 m/s). These are static channel-characterization parameters, not hidden episode state. No estimator receives latent true speed, bias mode, fault flag, future samples, perfect pose, map/object truth, or CARLA-only state.

## Implementation

Added `innovation_robust_fusion.py` with three reusable primitives:

- `OnlineInnovationScale`: clipped EWMA second-moment scale over matched-time residuals, bounded by declared floor/ceiling;
- `innovation_huber_weight`: applies the standard Huber threshold in **innovation units** (`residual / sigma`) rather than meters per second, then multiplies by freshness;
- `covariance_relative_precision`: a conservative scalar merit term. It starts from the declared reference/candidate nominal precision ratio and increases candidate influence only when observed cross-modal innovation energy exceeds nominal combined noise. Excess is assigned to the reference side because this experiment explicitly tracks persistent reference-sensor bias. This is a scalar robust baseline, not a full Kalman covariance model.

`obd_gnss_innovation_ablation.py` compares seven methods on the exact same episodes:

- `obd_only`;
- Run-17 `transport_fixed_huber`;
- Run-17 `transport_age_huber`;
- `innovation_huber`: matched-time transport + online innovation normalization, no bias correction;
- Run-15 `bias_calibrated`;
- `bias_innovation_huber`: bias correction + innovation Huber with equal reference/candidate precision;
- `bias_covariance_huber`: bias correction + innovation Huber + coarse relative-noise/covariance merit.

The final pair isolates an important confound: equal-precision fusion can look strong under faults simply by giving the independent GNSS channel too much influence, but that same behavior is expensive when clean OBD is already the lower-noise measurement.

## Executed validation

The staged standard-library implementation was executed with the Run-17 frozen stream:

- 5 independent seeds;
- 300 episodes per seed and condition;
- 250 steps per episode at 10 Hz;
- OBD 10 Hz, generator noise SD 0.18 m/s;
- GNSS 2 Hz, generator noise SD 0.45 m/s;
- GNSS delay 0.4-1.2 s;
- 15% GNSS dropout;
- two dynamics profiles: `ordinary` and `maneuver_heavy`;
- four OBD regimes: `clean`, persistent `static`, slow `drift`, and persistent `jump` bias;
- innovation Huber `k=1.345`;
- innovation-scale EWMA alpha 0.08, initial sigma 0.50, floor 0.25, ceiling 2.0, clip 3 sigma;
- covariance metadata 0.20 m/s OBD and 0.50 m/s GNSS.

Unit validation for the new primitives:

`python -m unittest -v test_innovation_robust_fusion.py`

Result: **4 passed**. The tests verify scale invariance in standardized residual units, bounded online scale adaptation, the nominal precision ratio, and monotonic/capped response to excess innovation energy.

### MAE — ordinary dynamics

| OBD regime | OBD only | transported fixed Huber | transported age Huber | innovation Huber | bias calibrator | bias + innovation Huber | bias + covariance Huber |
|---|---:|---:|---:|---:|---:|---:|---:|
| clean | 0.143769 | 0.185861 | 0.169391 | 0.184763 | **0.143836** | 0.184825 | 0.148763 |
| static bias | 1.499707 | 1.223290 | 1.337485 | 1.046164 | 0.426224 | **0.388921** | 0.393304 |
| drift | 0.382071 | 0.319713 | 0.336694 | 0.312779 | 0.320909 | **0.284476** | 0.294363 |
| jump bias | 1.097012 | 0.958704 | 1.015918 | 0.833918 | 0.578183 | 0.491388 | **0.488461** |

### MAE — maneuver-heavy dynamics

| OBD regime | OBD only | transported fixed Huber | transported age Huber | innovation Huber | bias calibrator | bias + innovation Huber | bias + covariance Huber |
|---|---:|---:|---:|---:|---:|---:|---:|
| clean | 0.143852 | 0.185626 | 0.169294 | 0.184541 | **0.143892** | 0.184574 | 0.148740 |
| static bias | 1.502874 | 1.225795 | 1.340251 | 1.047305 | 0.425924 | **0.389054** | 0.393754 |
| drift | 0.378684 | 0.317906 | 0.334208 | 0.310742 | 0.317338 | **0.281512** | 0.291129 |
| jump bias | 1.108329 | 0.969266 | 1.026711 | 0.841672 | 0.581699 | 0.493378 | **0.490646** |

Bold marks the best method among the new/reference conventional estimators in each condition; it is not a statistical significance marker.

## What the result says

### 1. Innovation normalization beats a fixed physical-unit radius when persistent mismatch exists

Without any persistent-bias correction, `innovation_huber` is nearly identical to transported fixed Huber in the clean condition (`0.184763` vs `0.185861` ordinary), but is better under all three persistent-bias regimes. For example, ordinary static bias falls from `1.223290` to `1.046164` and jump bias from `0.958704` to `0.833918`.

That is the intended behavior of standardization: the same absolute residual does not mean the same thing when the observed innovation distribution itself has widened.

### 2. Bias history plus innovation scale is substantially stronger than either alone under faults

`bias_innovation_huber` combines the Run-15 persistent matched-time bias estimate with the standardized residual. Relative to the bias calibrator alone, it reduces MAE in every faulty condition, including drift and jump.

But it has a serious clean-regime defect: treating the noisier GNSS candidate as equal-precision raises clean MAE from about `0.1438` to about `0.1846-0.1848`. That is not acceptable as a general baseline.

### 3. A coarse covariance merit removes most of the clean penalty

The covariance-aware hybrid starts from the declared nominal precision ratio `(0.20^2 / 0.50^2) = 0.16` and increases candidate merit only as observed innovation energy exceeds nominal combined noise.

This reduces the equal-precision clean MAE by about **19.5%** (`0.184825 → 0.148763` ordinary; `0.184574 → 0.148740` maneuver-heavy). It still remains about **3.4% worse** than the bias calibrator/OBD-only control when the reference is clean, so the clean case is not solved.

Under persistent faults, however, the covariance-aware hybrid improves on the bias calibrator itself by:

- ordinary static: **7.72%**;
- ordinary drift: **8.27%**;
- ordinary jump: **15.52%**;
- maneuver-heavy static: **7.55%**;
- maneuver-heavy drift: **8.26%**;
- maneuver-heavy jump: **15.65%**.

The covariance merit is deliberately conservative: compared with the equal-precision bias+innovation arm it is slightly worse under static/drift bias (about 1.1-3.5%) but slightly better under jump bias (~0.6%), while dramatically reducing the clean penalty. The result therefore supports a **trade-off**, not a universal winner.

## Scientific interpretation

Run 18 strengthens the conventional baseline and further narrows what should count as a MaleCNS contribution.

A controller should not receive credit merely for learning that a residual of `0.8 m/s` is suspicious. A conventional estimator can already express the more appropriate quantity:

`standardized innovation = matched-time residual / observed innovation sigma`

and can combine it with coarse channel-noise metadata and persistent bias evidence.

The remaining interesting decision problem is active and asymmetric: when conventional fusion is uncertain, should the system spend resources to obtain a better observation, quarantine a modality, trigger YOLO/LLM processing, fire ultrasonic/LiDAR, or request a corroborating peer token?

## New nearly-free coordinator channels

| candidate signal | cost | rate/latency | real-car availability | simulator/mock emulation | privacy/safety | marginal-value ablation |
|---|---|---|---|---|---|---|
| online innovation sigma | one clipped EWMA update per matched pair | corroborator rate; ~2 Hz in this OBD/GNSS harness | yes for any timestamp-alignable sensor pair | vary noise, dropout, drift and heteroscedasticity | derived scalar; lower privacy risk than raw sensor stream | remove sigma while retaining raw residual, timestamps and bias evidence |
| excess innovation energy above nominal noise | negligible arithmetic | same as innovation sigma | yes if nominal channel-noise metadata exists | inject correlated/common-mode bias and noise-regime changes | must not be interpreted as fault identity by itself | compare fixed nominal precision against adaptive excess-energy merit |

The same signals can be computed for camera ego-motion↔IMU yaw, LiDAR↔ultrasonic range, redundant wheel-speed sources, or later peer-token corroboration. For ambient Wi-Fi/RF, a peer report remains an untrusted observation; later local sensor confirmation may update a peer-specific innovation/reputation state without exposing privileged world truth.

## Cache/dependency accounting

No CARLA asset, dataset, model, Python package, or other heavyweight dependency was downloaded. This run reused the existing synthetic stream design and standard-library code, so there was **no heavyweight cache miss**. The checksum-pinned real-slice path from Run 16 remains the required gate before any real-road performance claim.

The dedicated 2026-09-19 MaleCNS embodied-control prior-art scan and autonomous-driving dataset/benchmark/safety review are already recorded in `RESEARCH_2026-09-19.md`; this run does not duplicate the same calendar-day searches.

## Remaining issue #646 work

This run completes the standardized-innovation/covariance-aware scalar baseline requested by #646, but the issue should remain open. Still pending are:

- explicit timestamp offset, clock drift, and jitter stress beyond ordinary arrival latency;
- correlated/common-mode cross-modal bias;
- biased and heteroscedastic delayed corroboration;
- a checksum/version-pinned synchronized real OBD/GNSS or camera/IMU slice;
- a symmetric or state-space covariance model that does not preassign the reference side as the suspect modality.

The next high-value stress is **clock drift/jitter plus correlated bias**. If the observable innovation baseline survives that, it becomes a much harder comparator for an active MaleCNS coordinator; if it fails, the failure mode itself defines the decision signal that an active controller may be able to exploit.
