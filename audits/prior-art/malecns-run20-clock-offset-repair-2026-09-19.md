---
type: "Audit Report"
title: "MaleCNS Run20 clock-offset repair — prior-art and falsification audit — 2026-09-19"
description: "Claim-level temporal, novelty, and adversarial validity audit of Run20 causal GNSS↔phone-IMU clock-offset estimation and repair."
tags: [malecns, prior-art, falsification, driving, gnss, imu, obd-ii, temporal-calibration, clock-offset, sensor-fusion]
timestamp: 2026-09-19T17:22:00Z
---

# MaleCNS Run20 clock-offset repair — prior-art and falsification audit — 2026-09-19

> **Status:** claim-specific audit of [`FINDINGS_2026-09-19_RUN20_CLOCK_OFFSET_REPAIR.md`](../../experiments/malecns_car_interface/FINDINGS_2026-09-19_RUN20_CLOCK_OFFSET_REPAIR.md). Priority and present truth status are separate axes. This audit does not establish exhaustive novelty, patent novelty, causal dependence, copying, plagiarism, or misconduct. Negative searches are bounded observations.

## 1. Claims and explicit falsifiers

### C1 — a persistent relative timestamp offset can be estimated online from common vehicle kinematics

Run20 searches candidate GNSS timestamp shifts and scores each by robust disagreement between GNSS speed change and phone-IMU integrated delta-v.

**Falsifier / narrowing condition:** the loss surface is flat or multimodal under ordinary vehicle motion; a conventional temporal-calibration method is equally or more accurate with the same observations; or the estimator cannot distinguish offset from sensor bias, spatial misalignment, gravity leakage, scale error, or dynamics-model error.

### C2 — applying an evidenced offset before OBD/GNSS fusion materially repairs fixed-offset failure

**Falsifier / narrowing condition:** paired reruns do not reproduce the fixed-offset gain; standard interpolation/continuous-time temporal calibration erases the advantage; or real synchronized data does not preserve the ordering.

### C3 — the estimator is causal/reality-bounded at its API boundary

The implementation rejects candidate intervals ending after the current available IMU index and accepts no simulator truth or injected fault label.

**Falsifier:** hidden true measurement time, future sensor samples, generator state, map/pose truth, or fault identity enters estimation rather than scoring.

### C4 — the current 13-way search plus 8% relative-loss gate provides usable evidence that a non-zero offset is real

**Falsifier / narrowing condition:** synchronized streams trigger repair materially above a calibrated false-positive target; a second independent/held-out segment fails to confirm the selected offset; or multiple near-equal minima make the chosen shift unstable.

### C5 — one persistent integer offset is an adequate model for the timing failure being repaired

**Falsifier / narrowing condition:** sub-step offset, clock drift/skew, packet jitter, timestamp quantization or changing latency dominate and require a time-varying/continuous model.

### C6 — the same pattern can transfer to other sensor pairs

**Falsifier / narrowing condition:** the two modalities do not expose a genuinely commensurate physical witness, spatial/extrinsic errors alias into time offset, or the candidate motion does not provide sufficient excitation for temporal identifiability.

### C7 — deterministic synchronization faults should be conventional repair/comparator territory rather than a source of MaleCNS credit

This is experimental positioning rather than a novelty claim.

**Falsifier / narrowing condition:** the offset cannot be robustly identified from lawful observations but an active coordinator can improve downstream driving reward by choosing probes, witnesses, quarantine, or sensing actions.

## 2. Temporal reconstruction

PR [#697](https://github.com/franklinbaldo/papers/pull/697) is the first located public Run20 branch containing the mechanism and findings.

- `ebd1a64c42083a3c18d21ec14a8a860ca5bb206d`, Git timestamp **2026-09-19 17:03:21 UTC**, first adds the observable clock-offset estimator.
- `889999ad59b8145572dd2453ceb51a211a5df759`, **17:03:33 UTC**, adds deterministic tests.
- `ed1d84c27947212fde89009af5e8c90eb9784657`, **17:03:56 UTC**, adds the ablation.
- `74a77ae8d32447efb945ba31e6df6c11977a6611`, **17:04:18 UTC**, records the findings.
- GitHub records PR #697 as created at **2026-09-19 17:04:29 UTC** and merged at **17:05:28 UTC**.

A commit timestamp does not by itself prove when the branch became publicly observable. The conservative public cutoff for C1–C7 is therefore **2026-09-19 17:04:29 UTC**.

## 3. Search protocol

Primary/near-primary sources were sought through IEEE/Xplore-visible metadata, DOI publisher pages, arXiv, robotics/navigation literature, and repository history. Discovery queries also covered Crossref/Scholar-indexed variants surfaced by web search.

Representative overlap queries:

- `temporal calibration multisensor tracking cross correlation time offset`
- `online temporal calibration camera IMU identifiability`
- `radar inertial online temporal delay calibration velocity acceleration`
- `radar ego velocity IMU acceleration temporal offset`
- `GNSS velocity IMU time offset calibration acceleration`
- `GPS velocity IMU acceleration time offset`
- `vehicle speed IMU time offset calibration GNSS`

Representative adversarial queries:

- `time delay estimation false peak low SNR cross correlation`
- `temporal calibration degenerate motion observability`
- `time offset unobservable constant acceleration IMU velocity`
- `online temporal calibration insufficient excitation failure`
- `clock offset drift skew jitter temporal calibration`
- `time delay estimation multiple peaks ambiguity`

Post-cutoff searches used the exact Run20 title and decompositions around GNSS speed-delta, IMU delta-v, robust offset search and online clock repair. The post-cutoff window is extremely short and absence is not evidence of nonexistence.

## 4. Pre-cutoff novelty / overlap

### 4.1 Generic signal-alignment temporal calibration is established prior art

**“Temporal calibration in multisensor tracking setups.”** IEEE ISMAR 2009, DOI: https://doi.org/10.1109/ISMAR.2009.5336465. The conference ran **2009-10-19 through 2009-10-22**; IEEE Xplore records addition on **2009-11-17**. It presents a general method to calibrate the temporal offset between sensor signals using normalized cross-correlation.

**Classification:** `prior_art` for the generic principle “search relative time alignment by optimizing agreement of a common observed signal.” Compared claims: C1, C4.

### 4.2 Online sensor time-offset estimation and identifiability analysis long predate Run20

**Mingyang Li & Anastasios I. Mourikis, “Online temporal calibration for camera–IMU systems: Theory and algorithms.”** *International Journal of Robotics Research*, first published online **2014-05-01**, DOI: https://doi.org/10.1177/0278364913515286.

The work estimates camera–IMU time offset online and explicitly analyzes when that offset is identifiable, including degenerate motion cases.

**Classification:** `prior_art` for online temporal-offset calibration; `adjacent_prior_work` for Run20's particular GNSS-speed/IMU-delta-v statistic. Compared claims: C1, C5, C6.

### 4.3 Vehicular radar–IMU online time calibration is direct prior art

**Vlaho-Josip Štironja et al., “Impact of Temporal Delay on Radar-Inertial Odometry.”** arXiv v1 **2025-03-04**, https://arxiv.org/abs/2503.02509.

The paper performs online radar–IMU temporal-delay calibration inside factor-graph odometry and validates it on real-world radar/IMU data, reporting materially lower localization error than ignoring synchronization.

**Classification:** `prior_art` for online relative sensor-time calibration in embodied/vehicular navigation and for explicit repair before attributing downstream performance to the controller. Compared claims: C1, C2, C7.

### 4.4 A 2026 pre-cutoff method closely occupies the velocity-observation + integrated-IMU + robust-offset mechanism

**Vlaho-Josip Štironja et al., “Radar-Inertial Odometry with Online Spatio-Temporal Calibration via Continuous-Time IMU Modeling.”** arXiv v1 **2026-03-20**, https://arxiv.org/abs/2603.19958.

The radar ego-velocity residual depends explicitly on the temporal offset. The method computes the velocity increment over the offset interval by integrating continuous-time IMU acceleration after gravity/bias correction, estimates the offset online, uses a Huber loss for radar ego-velocity outliers, and evaluates against 2025 temporal-calibration baselines. It also reports that performance and convergence depend on sufficient motion excitation.

**Classification:** `prior_art` for the central mechanism class `velocity observation + inertial acceleration/increment + online temporal offset + robust residual`; `partial_prior_art` for the exact Run20 scalar discrete procedure. Compared claims: C1, C2, C4, C5, C6.

The exact Run20 conjunction — GNSS speed-pair differences, phone longitudinal delta-v integrated over each candidate shifted interval, a causal integer grid, Huber mean loss, and an explicit relative-gain activation gate before OBD matching — was **not located** in the bounded search. That is a negative search result, not a firstness claim.

## 5. Falsification / contrary-evidence ledger

### 5.1 Offset is not identifiable from this witness without temporal excitation

For a GNSS pair whose reported interval length is fixed, Run20 compares a measured speed difference with IMU acceleration integrated over candidate-shifted intervals of the same duration. If longitudinal acceleration is constant across every candidate interval,

`∫[r1-o,r2-o] a dt = a · (r2-r1)`

for every candidate offset `o`. The loss surface is therefore flat with respect to offset. Zero acceleration is the simplest case; repetitive/periodic motion can produce multiple equivalent or near-equivalent shifts.

Li & Mourikis (2014) independently establish the broader point that temporal-offset calibration has motion-dependent degenerate cases. The 2026 radar–IMU work likewise reports that rich excitation improves temporal/extrinsic observability and performance.

**Classification:** `boundary_condition`, strength **strong**. Target: premise/identifiability and generalization, not the frozen Run20 MAE table.

**Required action:** `add_boundary_condition + add_control`. Treat offset evidence as undefined/weak when the temporal information content is low; record loss-surface curvature/ambiguity or another excitation/observability metric before applying a repair.

### 5.2 The current gate selects the best of 13 offsets and validates it on the same window

Run20 searches `-6..+6`, chooses the minimum robust loss, then asks whether that same selected minimum beats zero offset by 8%. Even when the true offset is zero, choosing a minimum across many noisy candidates creates an optimistic selection effect unless the gain threshold is calibrated against that search.

The Run20 clean negative control already observes the practical consequence: repair activates on about **9.0%** of eligible clean-clock updates and worsens clean MAE by about **1.09%**; jitter-only worsens by about **2.48%**.

Classic time-delay literature gives the same qualitative warning. **“Time delay estimation via cross-correlation in the presence of large estimation errors”** (*IEEE TASSP*, **1982-12-31**, DOI: https://doi.org/10.1109/TASSP.1982.1163992) shows anomalous large errors rise sharply as post-integration SNR falls, especially when the estimator takes the largest peak over the full delay range. **Choi & Eom, “Minimizing False Peak Errors in Generalized Cross-Correlation Time Delay Estimation…”**, published **2013-01-01**, DOI: https://doi.org/10.1587/transfun.E96.A.304, directly studies false correlation peaks under noise.

**Classification:** `boundary_condition`, strength **strong**; `contrary_evidence`, strength **moderate**, against interpreting the current 8% in-sample gain as calibrated evidence of a real offset.

**Required action:** `add_control + downgrade_confidence`. Before claiming reliable detection, compare a held-out confirmation window, block/bootstrap null calibration, or an explicit peak-ambiguity/confidence statistic. Preserve the current gate as a simple baseline.

### 5.3 Run20 is not a universal temporal preprocessor even in its own harness

The method improves fixed `+0.3 s` offset strongly but slightly harms clean and jitter-only timing; a single persistent offset also only weakly improves the drift stress arm.

**Classification:** `boundary_condition`, strength **strong**. Target: generalization/regime, not reproduction.

**Required action:** `no_change` to the measured table; `narrow_claim + add_boundary_condition`. Describe the mechanism as a fixed-offset repair baseline, not a universal timebase repair.

### 5.4 Constant integer offset is weaker than pre-cutoff continuous/time-varying baselines

Li & Mourikis (2014) explicitly evaluate constant and time-varying offsets. The 2026 radar–IMU method represents IMU signals continuously and estimates a slowly evolving temporal-offset state; its velocity correction integrates acceleration over the offset interval rather than restricting the correction to integer samples.

**Classification:** `boundary_condition`, strength **strong**; stronger-baseline evidence for C5.

**Required action:** `add_control`, but **not as a prerequisite to direct MaleCNS driving**. If Run20 is promoted beyond a simple remediation baseline, compare against continuous/sub-step offset plus offset+skew/drift modeling.

### 5.5 Cross-modality generalization requires more than swapping signal names

The 2026 radar–IMU formulation corrects gravity and accelerometer bias, models radar–IMU extrinsics, and integrates both acceleration and rotation over the offset interval. Those terms are not optional bookkeeping when modalities live in different frames or observe different physical quantities.

**Classification:** `boundary_condition`, strength **strong**, for C6.

**Required action:** `narrow_claim`. Generalization is plausible only when a physically commensurate witness and the needed spatial/bias model are explicit. Camera↔IMU, LiDAR↔IMU and ultrasonic timing should not inherit the scalar GNSS-speed recipe by analogy alone.

## 6. Alternative explanations and stronger baselines

The observed fixed-offset gain does not require a MaleCNS-specific mechanism. A simpler explanation is that the experiment contains a conventional synchronization error and the estimator repairs part of it. Established alternatives include correlation-based temporal calibration, state-augmented online temporal calibration, continuous-time inertial modeling, and joint spatio-temporal factor-graph estimation.

For Run20's scientific role, the strongest conventional baseline ladder is:

`raw reported time → discrete Run20 offset search → held-out/null-calibrated discrete search → continuous/sub-step offset → offset+skew/drift → joint spatio-temporal calibration when spatial terms matter`.

This ladder belongs in the **comparator/remediation library**. It should not delay the higher-value direct experiment `perception → MaleCNS → action → reward`; only an observed driving failure attributable to timing should pull the more sophisticated synchronization machinery into that loop.

## 7. Post-cutoff evidence

The conservative Run20 cutoff is **2026-09-19 17:04:29 UTC**. Searches immediately after that time found no external scholarly work whose first public disclosure falls into the tiny post-cutoff window and materially overlaps the exact Run20 conjunction.

No `later_independent`, `later_overlap`, `later_non_citing`, `later_citing`, or `later_derivative` classification is assigned on that basis. The negative search is weak because the window is only minutes.

## 8. Priority / truth-status matrix

| claim | priority | truth status after audit | required action |
|---|---|---|---|
| C1 estimate offset from shared kinematics | generic mechanism `prior_art`; exact local scalar rule not located | valid only when the witness is temporally informative | `narrow_claim + add_boundary_condition` |
| C2 repair fixed offset before fusion | concept `prior_art`; local synthetic effect is new evidence for this harness | strongly supported for the fixed-offset synthetic arm | `no_change` to numbers; `add_control` before real-data generalization |
| C3 causal/reality-bounded API | not a novelty claim | structurally supported by current implementation | `no_change` |
| C4 13-way search + 8% gate | local implementation not located | uncalibrated; clean false activation is material | `add_control + downgrade_confidence` |
| C5 persistent integer offset model | narrower than established continuous/time-varying approaches | useful fixed-offset baseline; weak for drift/jitter/sub-step timing | `add_boundary_condition` |
| C6 transfer to other modality pairs | generic temporal-calibration idea `prior_art` | plausible only with explicit commensurate witness/extrinsics/bias model | `narrow_claim` |
| C7 conventional repair before MaleCNS credit | not a firstness claim | strengthened as experimental hygiene | `no_change` |

No frozen Run20 numerical result is retracted. The important correction is priority and scope: online temporal calibration, including velocity/inertial mechanisms in embodied navigation, is established prior art; Run20 is best treated as a deliberately small, causal conventional repair baseline whose main value is exposing a concrete timing failure mode without blocking direct MaleCNS driving.
