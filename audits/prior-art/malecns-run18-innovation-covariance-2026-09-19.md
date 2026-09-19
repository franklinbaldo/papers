---
type: "Audit Report"
title: "MaleCNS Run18 innovation-normalized covariance merit — prior-art and falsification audit — 2026-09-19"
description: "Claim-level temporal, novelty, and adversarial validity audit of RUN18 standardized-innovation and asymmetric covariance-merit OBD/GNSS fusion, including post-cutoff RUN19 clock-health evidence."
tags: [malecns, prior-art, falsification, driving, sensor-fusion, innovation, covariance, huber, adaptive-filtering, obd-ii, gnss, clock-health]
timestamp: 2026-09-19T16:10:00Z
---

# MaleCNS Run18 innovation-normalized covariance merit — prior-art and falsification audit — 2026-09-19

> **Status:** claim-specific audit of [`FINDINGS_2026-09-19_RUN18_INNOVATION_COVARIANCE.md`](../../experiments/malecns_car_interface/FINDINGS_2026-09-19_RUN18_INNOVATION_COVARIANCE.md). This separates temporal priority from present truth status. It does not establish exhaustive novelty, patent novelty, copying, causal dependence, plagiarism, or misconduct. Negative searches are bounded observations.

## 1. Claims and explicit falsifiers

### C1 — online innovation normalization is a stronger conventional comparator than fixed physical-unit Huber in the executed stream

**Falsifier / narrowing condition:** paired reruns fail; a conventional adaptive robust filter that separates outlier rejection from covariance adaptation erases the gain; real synchronized data removes the ordering; or persistent bias merely inflates the residual second moment and creates an artifact.

### C2 — a coarse relative-noise/covariance merit can reduce the clean penalty while retaining fault-regime gains

**Falsifier / narrowing condition:** the rule fails when the candidate rather than the reference is biased; both channels fail; errors are correlated/common-mode; the nominal noise ordering reverses; or a symmetric/state-space covariance baseline performs as well without preassigning the suspect side.

### C3 — the deployable estimator does not consume hidden simulator truth or per-episode fault labels

This is literally true at the API boundary.

**Narrowing condition:** it does not imply fault-symmetry or assumption-free identification. `covariance_relative_precision` explicitly assigns excess innovation energy to the **reference** side because the persistent-bias estimator tracks that side.

### C4 — the reported 7.6–15.7% faulty-regime improvements over the bias calibrator are valid for the frozen synthetic harness

**Falsifier:** exact seeds/code do not reproduce the table. **Generalization boundary:** fault-side reversal, common-mode errors, timestamp corruption, state-dependent noise, heterogeneous delays or real data reverse the result.

### C5 — innovation sigma and excess innovation energy are useful low-cost coordinator signals

**Falsifier / narrowing condition:** they mostly encode bias/outliers rather than uncertainty; their marginal value vanishes after robust/gated scale estimation; or they do not predict when an active action improves downstream driving reward beyond simpler residual/history features.

### C6 — RUN18 narrows what should count as a MaleCNS contribution, but should not become another prerequisite before direct closed-loop driving

**Falsifier:** a MaleCNS controller cannot outperform matched random/rewired/recurrent controls on direct closed-loop driving even before sophisticated fusion is introduced.

## 2. Temporal reconstruction

PR [#667](https://github.com/franklinbaldo/papers/pull/667) contains the first located public RUN18 implementation and findings.

- [`be8387f360338e2e5f75d5ada64ffa583496b002`](https://github.com/franklinbaldo/papers/commit/be8387f360338e2e5f75d5ada64ffa583496b002), Git timestamp **2026-09-19 15:08:07 UTC**, contains implementation, ablation, tests and Findings Record.
- GitHub records PR #667 as created at **2026-09-19 15:08:24 UTC** and merged at **15:11:43 UTC**.

A commit timestamp alone does not prove the instant its branch became publicly observable, so the conservative cutoff for C1–C6 is **2026-09-19 15:08:24 UTC**.

## 3. Search protocol

Sources included IEEE/Crossref-discoverable records, Wiley/IET, Springer, SAGE, MDPI/Sensors, PubMed/PMC, arXiv, TechRxiv, Automatica/Elsevier metadata and earlier repository audits.

Representative overlap queries:

- `innovation covariance adaptive Kalman filter noise covariance Mehra`
- `innovation based adaptive estimation INS GPS covariance`
- `adaptive robust Kalman filter residual covariance Huber GPS`
- `adaptive Huber navigation innovation covariance`
- `Mahalanobis innovation adaptive robust Huber navigation`
- `residual covariance Huber robust navigation`

Representative adversarial queries:

- `adaptive robust filtering outlier contaminates covariance estimate`
- `Huber Sage Husa skip covariance update outlier`
- `noise covariance identifiability innovations necessary sufficient conditions`
- `noise covariance not uniquely identifiable unknown inputs`
- `adaptive covariance matching limitations Q R simultaneously`
- `correlated sensor errors innovation variance identify faulty sensor`
- `innovation scale fault masking adaptive threshold`

Post-cutoff searches used the exact RUN18 title, `covariance_relative_precision`, `innovation Huber OBD GNSS` and decomposition variants.

## 4. Pre-cutoff novelty / overlap

### 4.1 Innovation-driven covariance/noise adaptation is old prior art

**R. K. Mehra, “On the identification of variances and adaptive Kalman filtering.”** *IEEE Transactions on Automatic Control* 15(2), 175–184, public **1970-04**, DOI: https://doi.org/10.1109/TAC.1970.1099422.

**Classification:** `prior_art` for innovation-driven adaptive covariance/noise estimation. Compared claims: C1, C5.

### 4.2 Innovations were already fault/anomaly signals in 1971

**R. K. Mehra & J. Peschon, “An innovations approach to fault detection and diagnosis in dynamic systems.”** *Automatica* 7(5), 637–640, **1971**, DOI: https://doi.org/10.1016/0005-1098(71)90028-8.

**Classification:** `prior_art` for innovation behavior as fault signal; `adjacent_prior_work` for its use as a MaleCNS coordinator feature. Compared claim: C5.

### 4.3 Innovation-based adaptive navigation with field evidence predates RUN18

**A. H. Mohamed & K. P. Schwarz, “Adaptive Kalman Filtering for INS/GPS.”** *Journal of Geodesy* 73, 193–203, **1999-05**, DOI: https://doi.org/10.1007/s001900050236.

The paper develops innovation-based adaptive INS/GPS filtering that tunes `Q`, `R`, or both and evaluates two kinematic field tests.

**Classification:** `prior_art` for innovation-based adaptive covariance in integrated navigation; `adjacent_prior_work` for RUN18's scalar OBD/GNSS rule. Compared claims: C1, C2, C5.

### 4.4 Residual-covariance adaptation + Huber robust navigation predates RUN18 directly

**“Adaptive robust Kalman filter for relative navigation using global position system.”** *IET Radar, Sonar & Navigation*, first published **2013-06-01**, DOI: https://doi.org/10.1049/iet-rsn.2012.0170.

It estimates process-noise covariance from residual covariance and uses a Huber-derived robust measurement update. It also notes the difficulty of distinguishing process-noise from measurement-noise uncertainty when both are adapted.

**Classification:** `prior_art` for `residual/innovation covariance adaptation + Huber robust update + navigation`; `partial_prior_art` for RUN18's exact clipped-EWMA scalar implementation. Compared claims: C1, C2.

### 4.5 Adaptive Huber + innovation-based covariance estimation was explicit by 2014

**Rong Wang, Zhi Xiong, Jianye Liu & Lina Zhong, “Adaptive Huber-Based Filter for Hypersonic Cruise Vehicle Navigation.”** First published online **2014-09-01**, DOI: https://doi.org/10.1260/1748-3018.8.3.319.

The method combines innovation-based adaptive estimation, Mahalanobis-distance reasoning, robust covariance estimation and adaptive Huber/Kalman filtering for navigation.

**Classification:** `prior_art` for adaptive innovation/covariance + robust Huber navigation; `partial_prior_art` for RUN18's exact implementation. Compared claims: C1, C2.

### 4.6 Earlier local audit already recorded a 2016 uncertainty-adaptive Huber antecedent

The RUN14 audit records **“Adaptive M-Estimation for Robust Cubature Kalman Filtering,”** IEEE SSPD 2016, DOI: https://doi.org/10.1109/SSPD.2016.7590586, which adjusts measurement-noise covariance inside Huber M-estimation using discrepancy between actual and theoretical innovation covariance.

**Classification:** `prior_art` for uncertainty-adaptive Huber weighting; `partial_prior_art` for RUN18. This source is retained for claim-boundary completeness, not presented as a new discovery.

### 4.7 Exact local conjunction not located

The bounded search did not locate a pre-cutoff source using the exact conjunction of matched-time OBD↔GNSS residuals, clipped EWMA residual second moment, Huber weighting in standardized units, declared relative-noise metadata, and a capped rule that assigns excess residual energy to the reference side.

**Classification:** components are `prior_art`/`partial_prior_art`; exact local conjunction **not located**. This is not a firstness claim.

## 5. Falsification / contrary-evidence ledger

### 5.1 The covariance merit is an asymmetric prior, not general fault identification

RUN18 computes excess mismatch energy above nominal combined noise and assigns that excess to the reference side before increasing candidate influence.

For matched residual `d = e_candidate - e_reference`, in general:

`Var(d) = Var(e_candidate) + Var(e_reference) - 2 Cov(e_candidate, e_reference)`.

A scalar residual variance cannot identify which channel supplied excess error without structural assumptions.

**Boundary work:** Lingyi Zhang et al., **“On the Identification of Noise Covariances and Adaptive Kalman Filtering: A New Look at a 50 Year-Old Problem.”** *IEEE Access* 2020, DOI: https://doi.org/10.1109/ACCESS.2020.2982407, derives necessary/sufficient identifiability conditions from auto/cross-covariances of weighted innovations.

**Special-regime impossibility:** He Kong et al., **“The Noise Covariances of Linear Gaussian Systems with Unknown Inputs Are Not Uniquely Identifiable Using Autocovariance Least-squares.”** arXiv v1 **2022-02-10**, later *Systems & Control Letters* 162:105172, DOI: https://doi.org/10.1016/j.sysconle.2022.105172.

**Classification:** `boundary_condition`, strength **strong**. Target: mechanism/generalization, not frozen MAE.

**Required action:** `narrow_claim + add_control`. Describe RUN18 as an **asymmetric reference-suspect heuristic**. Controls: fault-side swap, both-side faults, correlated/common-mode faults, symmetric/state-space covariance comparator.

### 5.2 `OnlineInnovationScale` is mismatch energy under bias, not a pure covariance estimate

The update is a zero-centered clipped EWMA of `residual²`. With persistent mean mismatch `b`, its second moment contains approximately `variance + b²` before clipping. This can be a useful diagnostic, but it is not identification of a stochastic covariance component.

There is also an adaptation/masking risk: if faults inflate the scale, later `residual / sigma` shrinks and abnormal residuals look less exceptional.

**Direct pre-cutoff counter-design:** Yuxuan Fan et al., **“Adaptive Robust EKF with NARX-Based Velocity Prediction for High Precision AUV Navigation Under DVL Outages.”** *Sensors* 26(13):4240, published **2026-07-03**, DOI: https://doi.org/10.3390/s26134240. Its Huber–Sage–Husa design updates adaptive noise covariance **only when the residual is normal**, explicitly to prevent outliers from contaminating the noise estimate.

**Classification:** `boundary_condition`, strength **strong**; `contrary_evidence`, strength **moderate**, against interpreting unconditional clipped residual-energy adaptation as a clean covariance estimator. It does not contradict RUN18's MAE table.

**Required action:** `revise_mechanism + add_control`. Prefer “bounded innovation/mismatch scale” unless covariance-identification assumptions are met; compare gated/frozen adaptation, robust scale alternatives, and scale trajectories through fault onset/recovery.

### 5.3 The synthetic fault family is aligned with the estimator's structural prior

Persistent `static`, `drift`, and `jump` faults are injected into **OBD/reference**; GNSS gets zero-mean noise, delay and dropout. The covariance merit then assigns excess mismatch to **OBD/reference** and increases GNSS influence.

This is not per-episode label leakage, but the experiment family and estimator share the same fault-side prior.

**Classification:** `boundary_condition`, strength **strong**. Target: external validity/mechanism attribution.

**Required action:** `add_control + downgrade_confidence`. Reverse/alternate fault side; inject simultaneous and correlated faults; compare a symmetric estimator.

### 5.4 Clean regime is already a strong internal boundary

The covariance-aware hybrid remains about **3.4% worse** than bias-calibrator/OBD-only when OBD is clean. RUN18 correctly calls the result a trade-off.

**Classification:** `boundary_condition`, strength **strong**. This is not `failed_replication_or_null` because RUN18 is not a replication attempt.

**Required action:** `no_change` to numbers; `downgrade_confidence` for general use pending fault prevalence/cost and real data.

## 6. Post-cutoff evidence: RUN19 is later derivative, not prior art

RUN19 / PR [#682](https://github.com/franklinbaldo/papers/pull/682) was created at **2026-09-19 16:06:20 UTC** and merged at **16:06:51 UTC**, nearly an hour after the RUN18 cutoff. Its Findings Record explicitly begins from the premise that **RUN18 assumes reported timestamp equals physical measurement instant** and stress-tests the RUN18 covariance baseline with a phone-IMU clock-health witness.

**Classification:** `later_derivative`, high confidence. Dependency is positive and explicit.

With clean OBD + GNSS offset+jitter, RUN19 reports:

- OBD/control `0.148333`;
- RUN18-style covariance `0.199772`;
- covariance + IMU clock merit `0.189464`.

The independent kinematic witness limits damage by about **5.16%**, but the corrected arm still trails the simple OBD control. The signal does not repair the clock.

For RUN18's timestamp-contract premise this is:

- `boundary_condition`, strength **strong**;
- `contrary_evidence`, strength **moderate**, against any broad interpretation that innovation/covariance adaptation alone makes the path robust to asynchronous sensing.

**Required action:** `add_boundary_condition + add_control`. Treat timebase health separately and compare attenuation with explicit timestamp interpolation/clock-offset estimation.

RUN19 reinforces the main mechanism correction: residual energy is not self-interpreting. It may reflect stochastic noise, persistent bias, cross-channel correlation, lawful dynamics, or timestamp corruption.

No external post-cutoff scholarly work material to the exact RUN18 conjunction was located in the immediate window; the window is too short to infer anything from absence. No `later_non_citing` or `later_independent` label is assigned.

## 7. Priority / truth-status matrix

| claim | priority | truth status after audit | required action |
|---|---|---|---|
| C1 innovation normalization | generic mechanism `prior_art` | supported only in frozen RUN18 stream | `narrow_claim` |
| C2 covariance/relative-noise merit | components `prior_art`; exact local rule not located | useful asymmetric heuristic in tested reference-fault regimes | `narrow_claim + add_control` |
| C3 no hidden truth/fault label | not a novelty claim | literally true, but not fault-symmetric | `add_boundary_condition` |
| C4 synthetic gains | local empirical claim | stands for executed harness; broader confidence low | `downgrade_confidence + add_control` |
| C5 coordinator signals | innovation fault signals `prior_art` | plausible low-cost features; action value untested | `add_control` |
| C6 active MaleCNS decisions remain the interesting target | not a firstness claim | useful experimental positioning | `no_change` |

No RUN18 claim is retracted. The central correction is mechanistic: RUN18 did **not** identify which modality caused cross-modal covariance excess. It encoded a reference-side prior and demonstrated a useful heuristic in synthetic regimes where that prior is generally correct.

## 8. Consequence for the car programme: comparator, not prerequisite

This audit should **not** expand the pre-driving checklist. The covariance/innovation machinery belongs in the conventional comparator/remediation library.

The high-value next experiment remains a direct closed perception → MaleCNS → action → reward driving loop. Fault-side swaps, symmetric covariance models, robust scale variants and clock-health controls should be pulled in when an observed driving failure implicates this layer or when a scientific claim specifically depends on it.

RUN18 and RUN19 give stronger baselines and cheap diagnostic signals. They are not a reason to postpone embodied driving until the fusion stack is theoretically complete.

## 9. Negative-search accounting

Preserved negative searches include the exact RUN18 title, exact function name `covariance_relative_precision`, `innovation Huber OBD GNSS`, and variants combining clipped EWMA, matched-time residual, relative precision, Huber and reference-side covariance attribution.

No exact pre-cutoff source matching the complete local scalar rule was located. This does not imply that none exists.
