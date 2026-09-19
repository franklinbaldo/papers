---
type: "Audit Report"
title: "MaleCNS Run17 reference-delta temporal transport — prior-art and falsification audit — 2026-09-19"
description: "Claim-level temporal, novelty, and adversarial validity audit of RUN17 delayed-GNSS reference-delta transport, including classical OOSM/time-delay baselines and the limits introduced by reference-sensor error."
tags: [malecns, prior-art, falsification, sensor-fusion, temporal-alignment, delayed-measurement, oosm, obd-ii, gnss, huber]
timestamp: 2026-09-19T15:00:00Z
---

# MaleCNS Run17 reference-delta temporal transport — prior-art and falsification audit — 2026-09-19

> **Status:** claim-specific audit of [`FINDINGS_2026-09-19_RUN17_TEMPORAL_HUBER_FALSIFICATION.md`](../../experiments/malecns_car_interface/FINDINGS_2026-09-19_RUN17_TEMPORAL_HUBER_FALSIFICATION.md). This record separates temporal priority from present truth status. It does not establish exhaustive novelty, patent novelty, copying, causal dependence, plagiarism, or misconduct. Negative searches are bounded observations, not proof of absence.

## 1. Claims and explicit falsifiers

### C1 — transport a delayed GNSS candidate toward the current time using an already-observed reference-sensor increment before robust fusion

RUN17 implements

`GNSS_now_proxy = GNSS(t0) + [OBD(t1) - OBD(t0)]`.

**Would be wrong, too narrow, or without advantage if:** exact/standard out-of-sequence-measurement (OOSM) processing, buffered state propagation, continuous-time fusion, or delay-estimating filters match or beat it at equal information/compute; the reference increment is biased or not commensurate with the candidate quantity; the candidate/reference clocks are uncertain enough that `t0`/`t1` do not denote the intended physical interval; or real synchronized data do not reproduce the synthetic gain.

### C2 — reference-delta transport reduces disagreement caused by lawful motion and improves the fixed-Huber baseline in the current harness

RUN17 reports material MAE reductions for `transport_fixed_huber` relative to `raw_fixed_huber`, especially in maneuver-heavy drift.

**Would be wrong or practically uninformative if:** paired reruns do not reproduce the effect; a stronger OOSM baseline removes the apparent advantage; the gain vanishes when measurement-time uncertainty is modeled; or the transport merely transfers reference-sensor error into the delayed candidate.

### C3 — after transport, age-contracted Huber is a regime-dependent conservative heuristic rather than a general physical rule

RUN17 finds the age-contracted radius better than fixed Huber when OBD is clean and GNSS is noisier, but worse under persistent static/drift/jump OBD-bias regimes.

**Would be wrong or too broad if:** covariance/innovation-normalized Huber restores a stable independent benefit from the age exponent across reference-fault regimes; a real synchronized slice shows a materially different interaction; or the apparent split is seed/generator specific.

### C4 — persistent matched-time disagreement history can be more informative than a one-shot robust residual when one stream has persistent bias

The Run15 persistent-bias calibrator remains much stronger for static/jump OBD faults than one-shot Huber fusion in RUN17.

**Would be wrong or too narrow if:** the history aliases lawful regime changes, correlated/common-mode faults invalidate the reference, or a conventional dynamic/covariance-aware estimator without the persistence heuristic matches it.

### C5 — the coordinator should not receive credit for ordinary fusion until it beats temporally correct and uncertainty-aware conventional estimators

RUN17 uses its negative result to move the proposed MaleCNS role toward active sensing/resource/quarantine/escalation decisions rather than ordinary scalar fusion.

**Would be wrong if:** a lawful learned/MaleCNS estimator beats matched OOSM/covariance-aware baselines under equal information, compute, latency and real-data conditions; or conventional active-sensing/resource policies already explain the apparent coordinator gain.

### C6 — the OBD/GNSS transport is a reality-bounded proxy worth carrying into a real-car test

The estimator consumes only timestamped sensor observations and historical values already observable on a car/phone interface.

**Would be materially narrower if:** vehicle-dependent OBD speed error, wheel slip, clock uncertainty, sampling/quantization, GNSS latency, or cross-sensor calibration makes the reference increment an unreliable transport operator; or a pinned real synchronized slice reverses the synthetic ordering.

## 2. Temporal reconstruction

### 2.1 Content-bearing history

PR [#660](https://github.com/franklinbaldo/papers/pull/660) contains the RUN17 sequence:

- [`4557263f4967b2738f123dc0b062d5fcbe9e6efc`](https://github.com/franklinbaldo/papers/commit/4557263f4967b2738f123dc0b062d5fcbe9e6efc), Git timestamp **2026-09-19 14:00:49 UTC**, first `matched-time robust fusion` primitive;
- [`6b8acbca501f35087c24308e1e4e7486e1290d14`](https://github.com/franklinbaldo/papers/commit/6b8acbca501f35087c24308e1e4e7486e1290d14), **14:01:00 UTC**, invariant tests;
- [`200dcd1d145b0db52b043b1d9515435f29066675`](https://github.com/franklinbaldo/papers/commit/200dcd1d145b0db52b043b1d9515435f29066675), **14:01:58 UTC**, matched comparison of raw vs reference-delta-transported Huber variants;
- [`9342a0d189bb7f6910f29be5fd17bb1db797c1f9`](https://github.com/franklinbaldo/papers/commit/9342a0d189bb7f6910f29be5fd17bb1db797c1f9), **14:03:01 UTC**, first complete findings record.

PR #660 was created at **2026-09-19 14:03:50 UTC** and merged at 14:04:17 UTC.

### 2.2 Conservative public cutoff

Commit timestamps alone do not establish when an unmerged branch became publicly discoverable. This audit therefore uses **2026-09-19 14:03:50 UTC**, the independently verifiable PR-creation time, as the conservative public cutoff for C1–C6.

All works classified as prior art below were public before that cutoff.

## 3. Search protocol

Sources searched included IEEE Xplore, arXiv, DOI/publisher records, DTU Research Database, MDPI/Sensors, and targeted current-web discovery. The search decomposed RUN17 into delayed-measurement extrapolation, OOSM state updates, cross-sensor delay compensation, asynchronous automotive fusion, unknown-delay estimation, continuous-time sensor fusion, age/merit of old observations, and OBD speed-error models.

Representative overlap queries:

- `delayed measurement extrapolate to present Kalman filter`
- `GPS delay compensation IMU VO factor graph`
- `out-of-sequence measurement vehicle sensor fusion`
- `GNSS delay buffered IMU predict current state`
- `continuous-time asynchronous GNSS speed IMU fusion`
- `reference sensor delta delayed measurement compensation`
- `OBD GNSS speed delay compensation`

Representative adversarial queries:

- `delayed measurement failure reference sensor bias`
- `OOSM uncertain time delay consistent estimator`
- `GNSS time delay unknown online estimation failure EKF`
- `old measurement merit target maneuverability observation noise`
- `OBD-II speed error characteristics vehicle`
- `wheel speed slip bias odometry`
- `temporal alignment sensor fusion limitations`

Post-cutoff queries included the exact phrases `age-contracted Huber`, `transport_by_reference_delta`, `temporal alignment Huber delayed GNSS OBD`, and the RUN17/MaleCNS wording. No external scholarly work first made public after the cutoff and materially overlapping RUN17 was located in this bounded same-day search.

## 4. Pre-cutoff novelty / overlap findings

### 4.1 Extrapolating a delayed measurement to the present is established prior art

**Work:** Thomas Dall Larsen, Nils Axel Andersen, Ole Ravn & Niels Kjølstad Poulsen, **“Incorporation of Time Delayed Measurements in a Discrete-time Kalman Filter.”** IEEE CDC 1998, conference 16–18 December 1998, DOI: https://doi.org/10.1109/CDC.1998.761918 ; record: https://orbit.dtu.dk/en/publications/incorporation-of-time-delayed-measurements-in-a-discrete-time-kal/

The paper explicitly proposes **extrapolating a delayed measurement to present time using past and present filter estimates**, followed by an appropriate gain.

**Compared claims:** C1, C2.

**Classification:** `prior_art` for the generic mechanism “move a delayed measurement to the present before fusion”; `partial_prior_art` for RUN17 because its exact scalar cross-sensor increment `GNSS(t0)+OBD(t1)-OBD(t0)` and Huber comparison are not the same estimator.

**Priority impact:** temporal transport/extrapolation itself is not a RUN17 novelty boundary.

### 4.2 Exact and optimal OOSM updates long predate RUN17

**Work:** Yaakov Bar-Shalom, **“Update with out-of-sequence measurements in tracking: exact solution.”** *IEEE Transactions on Aerospace and Electronic Systems* 38(3), published **2002-07-31**, DOI: https://doi.org/10.1109/TAES.2002.1039398.

The paper gives the exact state-update equation for measurements that arrive after newer measurements have already been processed.

**Compared claims:** C1, C2, C5.

**Classification:** `prior_art` for delayed/OOSM fusion; `adjacent_prior_work` to RUN17's inexpensive reference-delta approximation.

**Consequence:** a “time-aware” baseline ladder must include an estimator that respects the state model/covariance, not only raw-vs-transported scalar Huber.

### 4.3 Vehicle multisensor OOSM is established and has real-world evaluation

**Work:** Antje Westenberger et al., **“Multi-sensor fusion with out-of-sequence measurements for vehicle environment perception.”** ICRA 2013, conference 6–10 May 2013, DOI: https://doi.org/10.1109/ICRA.2013.6631147.

The work handles asynchronous/OOS measurements in vehicle perception and evaluates on real crash-test data.

**Compared claims:** C1, C2, C5, C6.

**Classification:** `prior_art` for the automotive OOSM problem and conventional solution class; `adjacent_prior_work` to the exact OBD/GNSS speed experiment.

### 4.4 Cross-sensor compensation of delayed GPS is direct prior art for the transport pattern

**Work:** **“Compensation Method of GPS Signal Delay Based on Factor Graph.”** 2021 IEEE ICEICT, conference 18–20 August 2021, added to IEEE Xplore **2021-09-15**, DOI: https://doi.org/10.1109/ICEICT53123.2021.9531148.

When delayed GPS arrives, the method uses VO and IMU measurements to compensate the delayed GPS information and inserts the compensated observation at the arrival moment for fusion.

**Compared claims:** C1, C2, C6.

**Classification:** `prior_art` for cross-sensor compensation of a delayed GNSS/GPS observation before fusion; `partial_prior_art` for RUN17's exact OBD-speed delta formula and robust-Huber ablation.

### 4.5 Unknown delay is itself a state/uncertainty, not merely an age scalar

**Work:** M. Choi, J. Choi & W.K. Chung, **“State estimation with delayed measurements incorporating time-delay uncertainty.”** *IET Control Theory & Applications* 6(15), published **2012-10-11**, DOI: https://doi.org/10.1049/iet-cta.2010.0278.

The estimator models uncertain measurement delay probabilistically and uses state augmentation to obtain consistent estimates.

**Compared claims:** C1, C2, C6.

**Classification:** `adjacent_prior_work`; `boundary_condition` (`strong`) for treating known timestamps/arrival delay as exact enough without a clock/delay uncertainty model.

**Required action:** `add_boundary_condition + add_control` for clock offset/drift/jitter, already present in issue #646.

### 4.6 Buffered high-rate reference data used to carry delayed GNSS forward is current pre-cutoff state of the art

**Work:** Giulio Delama et al., **“Galilean State Estimation for Inertial Navigation Systems with Unknown Time Delay.”** arXiv v1 **2026-05-13 09:46:18 UTC**, https://arxiv.org/abs/2605.13266.

The paper describes the established pattern of buffering IMU data and predicting the current state by forward integration when GNSS is delayed, then proposes an EqF that jointly estimates navigation state and delay. It reports degradation/inconsistency of the compared EKF as delay grows and validates on two UAVs with real GNSS lags.

**Compared claims:** C1, C2, C5, C6.

**Classification:** `partial_prior_art` for using a fast reference stream to propagate delayed global measurements/state to the present; `boundary_condition` (`strong`) showing that delay estimation/geometry can be load-bearing.

**Required action:** `add_control` before generalizing the scalar OBD-delta transport as the relevant conventional ceiling.

### 4.7 Continuous-time factor-graph fusion is a stronger conventional asynchronous baseline

**Work:** **“GNSS/Multisensor Fusion Using Continuous-Time Factor Graph Optimization for Robust Localization.”** *IEEE Transactions on Robotics* 40, published **2024-08-15**, DOI: https://doi.org/10.1109/TRO.2024.3443699.

The method represents the trajectory continuously and fuses asynchronous GNSS, speed, IMU and LiDAR-odometry observations at arbitrary timestamps; it is evaluated on real urban driving data.

**Compared claims:** C1, C2, C5, C6.

**Classification:** `adjacent_prior_work`; a substantially stronger conventional baseline family than RUN17's scalar transport.

### 4.8 Age/latency value depends on dynamics and uncertainty, not age alone

**Work:** Josiah Yoder et al., **“Exploring the Exponentially Decaying Merit of an Out-of-Sequence Observation.”** *Sensors* 18(6):1947, published **2018-06-15**, DOI: https://doi.org/10.3390/s18061947.

The paper finds approximately exponential decay in the merit of old observations but derives merit from the state transition, observation model, process noise, observation noise, sensing rate, delay and target maneuverability.

**Compared claims:** C3, C5.

**Classification:** `boundary_condition` (`strong`) for any interpretation in which age itself supplies the correct residual tolerance/weight after alignment.

**Required action:** `add_control` using standardized innovation/covariance-aware robust fusion; if that removes the age-exponent advantage, `revise_mechanism` rather than preserving age contraction as causal.

### 4.9 OBD speed is not a universal clean transport reference

**Work:** Hany Ragab, Sidney Givigi & Aboelmagd Noureldin, **“Automotive Speed Estimation: Sensor Types and Error Characteristics from OBD-II to ADAS.”** arXiv:2501.00242 / IEEE-ION PLANS 2025, DOI: https://doi.org/10.1109/PLANS61210.2025.11028310 ; preprint: https://arxiv.org/abs/2501.00242.

The authors emphasize that OBD-II/wheel-speed derivation and sensor technology vary across vehicles and produce different error characteristics, validated on real road trajectories.

**Compared claims:** C1, C2, C6.

**Classification:** `boundary_condition` (`moderate-to-strong`) for generalizing from the synthetic OBD stream to arbitrary cars.

**Required action:** `add_boundary_condition + add_control` on the checksum-pinned real synchronized slice already required by issue #646.

### 4.10 Exact RUN17 conjunction not located

The bounded search did **not** locate a pre-cutoff source with the exact conjunction

`delayed GNSS scalar speed + already-observed OBD speed increment transport + fixed-vs-age-contracted Huber + persistent-bias control + the repository's reality-bounded SpecialistReport/MaleCNS baseline contract`.

This does not imply firstness. Its major components and its central transport principle have substantial prior art.

## 5. Falsification and contrary-evidence ledger

### 5.1 The main novelty correction: “transport delayed observation to now” is not new

Larsen et al. (1998), exact OOSM work, automotive OOSM work, and the 2021 GPS factor-graph method collectively anticipate the central generic operation well before the RUN17 cutoff.

**Target:** novelty of C1/C2.

**Classification:** `prior_art` / `partial_prior_art`.

**Strength:** `strong` for the generic operation; `moderate` for the exact scalar instantiation.

**Action:** `narrow_claim`. RUN17 should be presented as a specific cheap diagnostic/control inside this harness, not as a new principle of temporal sensor fusion.

### 5.2 Reference-delta transport inherits changes in reference error

Let the reference observation be `R(t)=x(t)+b(t)+e(t)`. RUN17 transports a delayed candidate by `R(t1)-R(t0)`, which contains the desired state increment **plus** `[b(t1)-b(t0)] + [e(t1)-e(t0)]`.

A constant reference bias cancels from the increment; a drifting, step-changing, clock-misaligned, or state-dependent reference error does not. Thus the same mechanism that removes lawful state evolution can inject reference error into the candidate.

This is visible qualitatively in RUN17's own split result and is consistent with the literature's emphasis on covariance, delay state and sensor-error models.

**Target:** mechanism/generalization of C1/C2/C6.

**Classification:** `boundary_condition`.

**Strength:** `strong` because it follows directly from the estimator algebra.

**Action:** `narrow_claim + add_control`. Prefer the wording **reference-delta temporal transport** or **matched-time proxy transport** over implying that the operation is universally “proper temporal alignment.”

### 5.3 Cross-sensor increment transport assumes compatible state semantics

`candidate(t0) + [reference(t1)-reference(t0)]` is meaningful only when the reference increment is a valid state-transition proxy for the candidate quantity. OBD speed → GNSS speed satisfies this approximately because both are scalar speed measurements. The formula does **not** automatically generalize to arbitrary pairs such as camera pose ↔ IMU yaw, LiDAR range ↔ ultrasonic range, or measurements in different coordinate/state spaces without an explicit dynamics/observation model.

**Target:** generalization of C1/C6 and the suggested analogy to other modalities.

**Classification:** `boundary_condition`.

**Strength:** `strong`.

**Action:** `narrow_claim`; each proposed sensor pair needs a declared transport map/state model and dimensional/coordinate invariants.

### 5.4 RUN17 already falsifies the universal age-contraction mechanism

The executed result is itself contrary evidence against RUN14's stronger mechanism: after identical reference-delta transport, age contraction helps only with the declared clean-OBD/noisier-GNSS relationship and is worse in all six persistent-reference-fault cells reported across ordinary/maneuver-heavy dynamics.

**Target:** C3 and the earlier RUN14 mechanism.

**Classification:** `failed_replication_or_null` / `contrary_evidence` against a general age-radius rule; `boundary_condition` for the surviving clean-reference regime.

**Strength:** `strong` inside this synthetic harness; `moderate` for external generalization because no real slice has been run.

**Action:** `revise_mechanism + downgrade_confidence`. The repository has already narrowed the rule to a heuristic; no retraction of the numerical RUN14 result is required.

### 5.5 The remaining age-contraction gain may be uncertainty normalization in disguise

Yoder et al. and conventional filtering theory make observation value a function of dynamics and uncertainty. In RUN17, age is correlated with the uncertainty of the transported GNSS candidate; the age exponent may therefore be acting as a crude proxy for missing innovation covariance rather than capturing an independent causal “freshness law.”

**Target:** mechanism of C3.

**Classification:** `boundary_condition`.

**Strength:** `moderate-to-strong`.

**Action:** `add_control`. Compare transported fixed Huber and transported age-Huber against a matched standardized-innovation/covariance-aware Huber using the same information budget. If age adds no residual advantage, `revise_mechanism` and keep it only as a compact heuristic.

### 5.6 Synthetic truth boundary remains load-bearing

RUN17 correctly keeps latent truth out of decision-time estimator inputs, but all performance conclusions still come from a synthetic generator with declared Gaussian sensor noise, explicit OBD fault modes, and known delay/dropout distributions. This is valid simulation evidence, not evidence that real OBD/GNSS error obeys the same model.

**Target:** magnitude/generalization of C2–C6.

**Classification:** `boundary_condition`.

**Strength:** `strong` for external validity, not for the internal arithmetic result.

**Action:** `downgrade_confidence + add_control`; retain issue #646 until a pinned synchronized real slice clears the admission gate.

## 6. Alternative mechanisms with fewer assumptions

The same RUN17 observations can be explained without treating age contraction as a physical law or reference-delta transport as a new fusion principle:

1. **Classical OOSM/state propagation:** the improvement arises because measurements are compared at compatible physical times.
2. **Uncertainty normalization:** the surviving clean-regime age benefit is a proxy for increasing prediction/measurement uncertainty with delay.
3. **Reference-quality asymmetry:** age contraction helps when the reference is cleaner than the candidate and hurts when the reference is persistently wrong.
4. **Persistent bias estimation:** repeated matched-time residuals identify systematic disagreement better than a one-step robust gate.

These mechanisms are simpler and should remain the conventional baseline ladder a MaleCNS coordinator must exceed.

## 7. Post-cutoff work

The cutoff is **2026-09-19 14:03:50 UTC**. Bounded same-day searches for the exact RUN17 terminology and decompositions did not locate an external scholarly work first made public after that time and materially overlapping RUN17.

**Classification:** no `later_independent`, `later_overlap`, `later_non_citing`, `later_citing`, or `later_derivative` external candidate is assigned from this search. “Not located” is not evidence of nonexistence.

Inside this repository, RUN17 is explicitly derivative from RUN14, RUN15 and issue #646; that lineage is already documented and is not a credit/priority dispute.

## 8. Classification summary and required changes

| Claim | Priority status | Present truth status | Contrary/boundary strength | Required action |
|---|---|---|---|---|
| C1 reference-delta transport | generic principle is `prior_art`; exact instantiation `partial_prior_art` | plausible cheap approximation | strong boundary | `narrow_claim`, `add_control` |
| C2 transport improves fixed Huber here | no novelty claim needed | supported in executed synthetic harness | moderate external boundary | `no_change` to numbers; `downgrade_confidence` externally |
| C3 age contraction is regime-dependent | mechanism components prior work | supported as a negative/generalization result | strong within harness | `revise_mechanism` already satisfied; `add_control` covariance baseline |
| C4 persistence helps persistent bias | adjacent established bias-estimation ideas | supported in this harness | moderate | `add_boundary_condition` |
| C5 conventional estimation before coordinator credit | not a novelty claim | scientifically prudent, still prospective | moderate | `no_change`; strengthen baseline ladder |
| C6 real-car relevance | automotive delayed fusion is prior art | unvalidated on real synchronized slice | strong external-validity boundary | `add_control`, `downgrade_confidence` |

## 9. Repository action

The RUN17 Findings Record already preserves the crucial negative result and keeps issue #646 open, so this audit does **not** rewrite its historical numerical record. However, future prose should avoid treating the specific OBD-delta formula as universally “proper temporal alignment”; the defensible term is **reference-delta temporal transport** unless a state/delay model justifies a stronger claim.

Issue #646 remains the correct single remediation gate. No duplicate issue is needed. Its remaining high-value discriminator is now sharper:

`reference-delta transport + fixed Huber` → `reference-delta transport + covariance/innovation Huber` → `standard OOSM / buffered-propagation or continuous-time baseline` → pinned real synchronized OBD/GNSS slice, with clock offset/drift/jitter and correlated/reference faults.

The MaleCNS coordinator should receive estimation credit only for residual gain beyond that ladder under equal information, latency, compute and sensor budget.