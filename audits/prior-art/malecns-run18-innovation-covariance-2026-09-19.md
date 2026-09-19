---
type: "Audit Report"
title: "MaleCNS Run18 innovation-normalized covariance merit — prior-art and falsification audit — 2026-09-19"
description: "Claim-level temporal, novelty, and adversarial validity audit of RUN18 standardized-innovation and asymmetric covariance-merit OBD/GNSS fusion, separating priority from present truth status."
tags: [malecns, prior-art, falsification, driving, sensor-fusion, innovation, covariance, huber, adaptive-filtering, obd-ii, gnss]
timestamp: 2026-09-19T16:00:00Z
---

# MaleCNS Run18 innovation-normalized covariance merit — prior-art and falsification audit — 2026-09-19

> **Status:** claim-specific audit of [`FINDINGS_2026-09-19_RUN18_INNOVATION_COVARIANCE.md`](../../experiments/malecns_car_interface/FINDINGS_2026-09-19_RUN18_INNOVATION_COVARIANCE.md). This record separates temporal priority from present truth status. It does not establish exhaustive novelty, patent novelty, copying, causal dependence, plagiarism, or misconduct. Negative searches are bounded observations, not proof of absence.

## 1. Claims and falsifiers

### C1 — online innovation normalization is a stronger conventional comparator than a fixed physical-unit Huber radius in the executed stream

RUN18 reports that `innovation_huber` is nearly neutral relative to transported fixed Huber when OBD is clean and better under persistent-reference-bias regimes.

**Falsifier / narrowing condition:** paired reruns fail; a conventional adaptive robust filter that separates outlier rejection from covariance adaptation erases the gain; a real synchronized slice removes the ordering; or the gain is mostly caused by persistent bias inflating the residual second moment.

### C2 — a coarse relative-noise/covariance merit can reduce the clean penalty while retaining fault-regime gains

**Falsifier / narrowing condition:** the rule fails when the candidate rather than the reference is biased; faults affect both channels; errors are correlated/common-mode; nominal noise ordering reverses; or a symmetric/state-space covariance baseline performs as well without preassigning the suspect side.

### C3 — the deployable estimator does not consume hidden simulator truth or per-episode fault labels

This is literally true at the function boundary.

**Falsifier / narrowing condition:** interpreting it as fault-symmetric or assumption-free. RUN18's `covariance_relative_precision` explicitly assigns excess innovation energy to the **reference** side because the persistent-bias estimator tracks that side. No fault label is passed per episode, but a structural reference-suspect prior is encoded.

### C4 — the 7.6–15.7% faulty-regime improvements over the bias calibrator are valid evidence for the frozen synthetic harness

**Falsifier:** exact seeds/code do not reproduce the table. **Generalization boundary:** reversing fault side, common-mode faults, clock uncertainty, state-dependent noise, heterogeneous delays or real data reverses the result.

### C5 — innovation sigma and excess innovation energy are useful low-cost coordinator signals

**Falsifier / narrowing condition:** they mainly encode bias/outliers rather than uncertainty; value collapses after robust/gated scale estimation; or they fail to predict when an active action improves downstream driving reward beyond simpler residual/history features.

### C6 — RUN18 narrows what should count as a MaleCNS contribution, but should not become another prerequisite before closed-loop driving

**Falsifier:** a MaleCNS controller cannot beat matched random/rewired/recurrent controls in a direct closed-loop driving curriculum even before sophisticated fusion is introduced.

## 2. Temporal reconstruction

PR [#667](https://github.com/franklinbaldo/papers/pull/667) contains the first located public RUN18 implementation and findings.

- [`be8387f360338e2e5f75d5ada64ffa583496b002`](https://github.com/franklinbaldo/papers/commit/be8387f360338e2e5f75d5ada64ffa583496b002), Git author/committer timestamp **2026-09-19 15:08:07 UTC**, contains implementation, ablation, tests and Findings Record.
- GitHub records PR #667 as created at **2026-09-19 15:08:24 UTC** and merged at **15:11:43 UTC**.

A commit timestamp alone does not prove public visibility of its head branch. The conservative claim cutoff is therefore **2026-09-19 15:08:24 UTC**.

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

Post-cutoff searches used the exact RUN18 title, `covariance_relative_precision`, `innovation Huber OBD GNSS` and decomposition variants. No material external scholarly work first made public after **15:08:24 UTC** and before this audit was located. The observation window is too short for that absence to carry meaningful evidential weight.

## 4. Pre-cutoff novelty / overlap

### 4.1 Innovation-based covariance adaptation is decades-old prior art

**R. K. Mehra, “On the identification of variances and adaptive Kalman filtering.”** *IEEE Transactions on Automatic Control* 15(2), 175–184, public **1970-04**, DOI: https://doi.org/10.1109/TAC.1970.1099422.

**Classification:** `prior_art` for innovation-driven adaptive covariance/noise estimation. Compared claims: C1, C5.

### 4.2 Innovation behavior was already used for fault detection in 1971

**R. K. Mehra & J. Peschon, “An innovations approach to fault detection and diagnosis in dynamic systems.”** *Automatica* 7(5), 637–640, **1971**, DOI: https://doi.org/10.1016/0005-1098(71)90028-8.

**Classification:** `prior_art` for innovations as a fault/anomaly signal; `adjacent_prior_work` for its use as a MaleCNS coordinator feature. Compared claim: C5.

### 4.3 Innovation-based adaptive navigation with field evidence predates RUN18

**A. H. Mohamed & K. P. Schwarz, “Adaptive Kalman Filtering for INS/GPS.”** *Journal of Geodesy* 73, 193–203, **1999-05**, DOI: https://doi.org/10.1007/s001900050236.

The work develops innovation-based adaptive INS/GPS filtering that tunes `Q`, `R`, or both and evaluates two kinematic field tests.

**Classification:** `prior_art` for innovation-based adaptive covariance in integrated navigation; `adjacent_prior_work` for RUN18's scalar OBD/GNSS rule. Compared claims: C1, C2, C5.

### 4.4 Residual-covariance adaptation plus Huber robust navigation directly predates RUN18

**“Adaptive robust Kalman filter for relative navigation using global position system.”** *IET Radar, Sonar & Navigation*, first published **2013-06-01**, DOI: https://doi.org/10.1049/iet-rsn.2012.0170.

It estimates process-noise covariance from residual covariance and uses a Huber-derived robust measurement update. It also explicitly notes the difficulty of distinguishing process-noise from measurement-noise uncertainty when both are adapted.

**Classification:** `prior_art` for `residual/innovation covariance adaptation + Huber robust update + navigation`; `partial_prior_art` for RUN18's exact clipped-EWMA scalar implementation. Compared claims: C1, C2.

### 4.5 Adaptive Huber + innovation-based covariance estimation was explicit by 2014

**Rong Wang, Zhi Xiong, Jianye Liu & Lina Zhong, “Adaptive Huber-Based Filter for Hypersonic Cruise Vehicle Navigation.”** First published online **2014-09-01**, DOI: https://doi.org/10.1260/1748-3018.8.3.319.

The method combines innovation-based adaptive estimation, Mahalanobis-distance reasoning, robust covariance estimation and adaptive Huber/Kalman filtering for navigation.

**Classification:** `prior_art` for adaptive innovation/covariance + robust Huber navigation; `partial_prior_art` for RUN18's exact implementation. Compared claims: C1, C2.

### 4.6 Existing repository prior art also includes 2016 uncertainty-adaptive Huber M-estimation

The RUN14 audit already recorded **“Adaptive M-Estimation for Robust Cubature Kalman Filtering,”** IEEE SSPD 2016, DOI: https://doi.org/10.1109/SSPD.2016.7590586, which adjusts measurement-noise covariance inside Huber M-estimation using the discrepancy between actual and theoretical innovation covariance.

**Classification:** `prior_art` for uncertainty-adaptive Huber weighting; `partial_prior_art` for RUN18. This is retained for claim-boundary completeness, not presented as a newly discovered repository antecedent.

### 4.7 Exact local conjunction not located

The bounded search did not locate a pre-cutoff source using the exact combination of matched-time OBD↔GNSS residuals, clipped EWMA residual second moment, Huber weighting in standardized units, declared relative-noise metadata, and a capped rule that assigns excess residual energy to the reference side.

**Classification:** components are `prior_art`/`partial_prior_art`; exact local conjunction **not located**. This is not a firstness claim.

## 5. Falsification and contrary-evidence ledger

### 5.1 The covariance merit is an asymmetric prior, not fault identification

RUN18 computes excess mismatch energy above nominal combined noise and explicitly assigns that excess to the reference side before increasing candidate influence.

For matched residual `d = e_candidate - e_reference`, in general:

`Var(d) = Var(e_candidate) + Var(e_reference) - 2 Cov(e_candidate, e_reference)`.

A scalar residual variance does not identify which channel supplied excess error without structural assumptions.

**Relevant boundary work:** Lingyi Zhang et al., **“On the Identification of Noise Covariances and Adaptive Kalman Filtering: A New Look at a 50 Year-Old Problem.”** *IEEE Access* 2020, DOI: https://doi.org/10.1109/ACCESS.2020.2982407. It derives necessary/sufficient identifiability conditions from auto/cross-covariances of weighted innovations.

**Stronger special-regime limit:** He Kong et al., **“The Noise Covariances of Linear Gaussian Systems with Unknown Inputs Are Not Uniquely Identifiable Using Autocovariance Least-squares.”** arXiv v1 **2022-02-10**, later *Systems & Control Letters* 162:105172, DOI: https://doi.org/10.1016/j.sysconle.2022.105172.

**Classification:** `boundary_condition`, strength **strong**.

**Target:** mechanism/generalization, not frozen MAE.

**Required action:** `narrow_claim + add_control`. Describe RUN18 as an **asymmetric reference-suspect heuristic**, not general covariance/fault identification. Controls: fault-side swap, both-side faults, correlated/common-mode faults, symmetric/state-space covariance comparator.

### 5.2 `OnlineInnovationScale` is mismatch energy under bias, not a pure covariance estimate

The update is a zero-centered clipped EWMA of `residual²`. With persistent mean mismatch `b`, the second moment contains approximately `variance + b²` before clipping. That can be useful diagnostically, but it is not identification of a stochastic noise covariance.

There is also a masking risk: a fault that inflates the adaptive scale reduces later `residual / sigma`, making persistent large residuals look less exceptional.

**Direct pre-cutoff counter-design:** Yuxuan Fan et al., **“Adaptive Robust EKF with NARX-Based Velocity Prediction for High Precision AUV Navigation Under DVL Outages.”** *Sensors* 26(13):4240, published **2026-07-03**, DOI: https://doi.org/10.3390/s26134240. Its Huber–Sage–Husa design updates adaptive noise covariance **only when the residual is normal**, explicitly to prevent outliers from contaminating the noise estimate.

**Classification:** `boundary_condition`, strength **strong**; `contrary_evidence`, strength **moderate**, against interpreting unconditional clipped residual-energy adaptation as a clean covariance estimator. It does not contradict the RUN18 MAE table.

**Target:** mechanism/generalization.

**Required action:** `revise_mechanism + add_control`. Prefer “bounded innovation/mismatch scale” unless covariance-identification assumptions are met. Compare gated/frozen adaptation, robust scale alternatives, and fault onset/recovery trajectories.

### 5.3 The synthetic fault family is aligned with the method's structural prior

Persistent `static`, `drift`, and `jump` faults are injected into **OBD/reference**; GNSS gets zero-mean noise, delay and dropout. The covariance-merit arm then assigns excess mismatch to **OBD/reference** and increases GNSS influence.

This is not per-episode label leakage, but it means the experiment family and estimator share the same fault-side prior.

**Classification:** `boundary_condition`, strength **strong**.

**Target:** external validity and mechanism attribution.

**Required action:** `add_control + downgrade_confidence`. Reverse/alternate fault side; inject simultaneous and correlated faults; then compare a symmetric estimator.

### 5.4 Robustness and adaptation are known to require careful separation

The 2013 adaptive robust GPS paper already notes the difficulty of distinguishing uncertainty sources. The 2026 AHR-EKF uses conditional covariance updates precisely so abnormal residuals do not corrupt adaptation.

A simpler interpretation of RUN18 is therefore: **handcrafted mismatch detector + asymmetric reliability prior**, rather than recovered physical covariance decomposition.

**Classification:** `boundary_condition`, strength **moderate-to-strong**. Required action: `narrow_claim`; numerical result unchanged.

### 5.5 Clean regime is already a strong internal boundary

The covariance-aware hybrid remains about **3.4% worse** than bias-calibrator/OBD-only when OBD is clean. RUN18 correctly calls this a trade-off rather than a universal winner.

**Classification:** `boundary_condition`, strength **strong**. This is not `failed_replication_or_null` because RUN18 is not a replication attempt.

**Required action:** `no_change` to numbers; `downgrade_confidence` for general use pending fault-prevalence/cost modeling and real data.

## 6. Priority / truth-status matrix

| claim | priority | truth status after audit | required action |
|---|---|---|---|
| C1 innovation normalization | generic mechanism is `prior_art` | supported only in frozen RUN18 stream | `narrow_claim` |
| C2 relative-noise/covariance merit | components `prior_art`; exact local rule not located | useful asymmetric heuristic in tested reference-fault regimes | `narrow_claim + add_control` |
| C3 no hidden truth/fault label | not a novelty claim | literally true, but does not imply fault-symmetry | `add_boundary_condition` |
| C4 reported synthetic gains | local empirical claim | stands for executed harness; broader confidence low | `downgrade_confidence + add_control` |
| C5 coordinator signals | innovation fault signals are `prior_art` | plausible low-cost features; incremental action value untested | `add_control` |
| C6 active MaleCNS decisions remain the interesting target | not a firstness claim | reasonable experimental positioning | `no_change` |

No claim is retracted. The central correction is mechanistic: RUN18 did **not** identify which modality caused cross-modal covariance excess. It encoded a reference-side prior and demonstrated a useful heuristic in synthetic regimes where that prior is generally correct.

## 7. Consequence for the car programme: comparator, not prerequisite

This audit should **not** expand the pre-driving checklist. The covariance/innovation machinery belongs in the conventional comparator/remediation library.

The high-value next experiment remains a direct closed perception → MaleCNS → action → reward driving loop. Fault-side swaps, symmetric covariance models and robust scale variants should be pulled in when an observed driving failure implicates this layer or when a scientific claim specifically depends on RUN18.

RUN18 gives a stronger baseline and cheap diagnostic signals; it is not a reason to postpone embodied driving until the fusion stack is theoretically complete.

## 8. Later work / dependency check

No material external scholarly work first made public after **2026-09-19 15:08:24 UTC** was located in the immediate post-cutoff search. The window is too short for absence to carry evidential weight, so no `later_independent`, `later_overlap`, `later_non_citing`, `later_citing`, or `later_derivative` label is assigned.

## 9. Negative-search accounting

Preserved negative searches include the exact RUN18 title, exact local function name `covariance_relative_precision`, `innovation Huber OBD GNSS`, and variants combining clipped EWMA, matched-time residual, relative precision, Huber and reference-side covariance attribution.

No exact prior source matching the complete local scalar rule was located. This does not imply that none exists.
