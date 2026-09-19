---
type: "Audit Report"
title: "MaleCNS Run18 innovation-normalized covariance merit — prior-art and falsification audit — 2026-09-19"
description: "Claim-level temporal, novelty, and adversarial validity audit of RUN18 standardized-innovation and asymmetric covariance-merit OBD/GNSS fusion, separating priority from present truth status."
tags: [malecns, prior-art, falsification, driving, sensor-fusion, innovation, covariance, huber, adaptive-filtering, obd-ii, gnss]
timestamp: 2026-09-19T16:00:00Z
---

# MaleCNS Run18 innovation-normalized covariance merit — prior-art and falsification audit — 2026-09-19

> **Status:** claim-specific audit of [`FINDINGS_2026-09-19_RUN18_INNOVATION_COVARIANCE.md`](../../experiments/malecns_car_interface/FINDINGS_2026-09-19_RUN18_INNOVATION_COVARIANCE.md). This record separates temporal priority from present truth status. It does not establish exhaustive novelty, patent novelty, copying, causal dependence, plagiarism, or misconduct. A negative search is a bounded result, not evidence of nonexistence.

## 1. Claims and explicit falsifiers

### C1 — online innovation normalization is a stronger conventional comparator than a fixed physical-unit Huber radius in the executed asynchronous OBD/GNSS stream

RUN18 reports that `innovation_huber` is almost neutral relative to transported fixed Huber when OBD is clean and improves all three persistent-reference-bias regimes.

**Would be wrong, too narrow, or uninformative if:** paired reruns do not reproduce the ordering; a conventional adaptive robust filter that keeps robust outlier handling separate from covariance adaptation erases the gain; the gain disappears when the adaptive scale is estimated on a real synchronized slice; or the apparent improvement is mostly an artifact of letting persistent bias inflate the residual second moment.

### C2 — a coarse relative-noise/covariance merit can reduce the clean penalty while retaining useful fault-regime gains

RUN18 starts from declared nominal OBD/GNSS noise scales and increases GNSS candidate influence when observed cross-modal innovation energy exceeds the nominal combined level.

**Would be wrong or materially narrower if:** the same rule fails when the candidate rather than the reference is biased; faults affect both channels; cross-channel errors are correlated; the nominal noise ordering reverses; or a symmetric/state-space covariance baseline performs as well without preassigning the suspect side.

### C3 — the deployable estimator does not consume hidden simulator truth or per-episode fault labels

This is true at the function/API boundary: estimator inputs are observations, timestamps/history, derived residual/bias summaries, and declared channel metadata.

**Would be overstated if interpreted as fault-symmetric or assumption-free:** the algorithm can still encode a structural prior about *which side* is expected to be wrong. In RUN18, `covariance_relative_precision` explicitly assigns excess innovation energy to the **reference** side because the persistent-bias estimator tracks that side.

### C4 — the reported 7.6–15.7% faulty-regime improvements of the covariance-aware hybrid over the bias calibrator are valid evidence for this frozen synthetic harness

**Would be wrong if:** the exact seeds/code do not reproduce them. **Would fail to generalize if:** reversing the fault side, adding common-mode/correlated faults, clock uncertainty, heterogeneous delays, state-dependent noise, or real data reverses the result.

### C5 — online innovation sigma and excess innovation energy are useful low-cost coordinator signals

**Would be too broad if:** these signals mainly encode persistent bias/outliers rather than stochastic uncertainty; their value collapses after robust/gated scale estimation; or they cannot predict when an active action (probe, quarantine, extra sensor, extra compute) improves downstream driving reward beyond a simpler residual/history feature.

### C6 — RUN18 should narrow what counts as a MaleCNS contribution, not become another prerequisite before putting MaleCNS in closed-loop driving

The Findings Record correctly says that ordinary residual standardization and robust fusion are conventional estimation problems. The project-level hypothesis is that MaleCNS may add value in active, temporally extended sensor/action/resource decisions.

**Would be wrong if:** a MaleCNS controller cannot beat matched simple recurrent/random controls on closed-loop driving even before sophisticated fusion is introduced, or if all apparent value is reproduced by a simpler conventional controller under equal information and budget.

## 2. Temporal reconstruction of our claims

PR [#667](https://github.com/franklinbaldo/papers/pull/667) contains the first located public RUN18 implementation and findings.

- [`be8387f360338e2e5f75d5ada64ffa583496b002`](https://github.com/franklinbaldo/papers/commit/be8387f360338e2e5f75d5ada64ffa583496b002), Git author/committer timestamp **2026-09-19 15:08:07 UTC**, contains the implementation, ablation, tests and Findings Record.
- GitHub records PR #667 as created at **2026-09-19 15:08:24 UTC** and merged at **15:11:43 UTC**.

A commit timestamp does not by itself establish the instant at which its branch became publicly observable. This audit therefore uses **2026-09-19 15:08:24 UTC** — PR creation — as the conservative public cutoff for C1–C6.

All external work classified as `prior_art`, `partial_prior_art`, `adjacent_prior_work`, `contrary_evidence`, or `boundary_condition` below was publicly available before that cutoff.

## 3. Search protocol

Sources queried or used for primary-record confirmation included IEEE/Crossref-discoverable records, Wiley/IET, Springer, SAGE, MDPI/Sensors, PubMed/PMC, arXiv, TechRxiv, Automatica/Elsevier metadata and the repository's earlier RUN14/RUN17 audits. Searches decomposed the RUN18 mechanism rather than relying on its local names.

Representative overlap queries:

- `innovation covariance adaptive Kalman filter noise covariance Mehra`
- `innovation based adaptive estimation INS GPS covariance`
- `adaptive robust Kalman filter residual covariance Huber GPS`
- `adaptive Huber navigation innovation covariance`
- `Mahalanobis innovation adaptive robust Huber navigation`
- `Huber innovation covariance adaptive filtering`
- `residual covariance Huber robust navigation`

Representative adversarial/falsification queries:

- `adaptive robust filtering outlier contaminates covariance estimate`
- `Huber Sage Husa skip covariance update outlier`
- `noise covariance identifiability innovations necessary sufficient conditions`
- `noise covariance not uniquely identifiable unknown inputs`
- `adaptive covariance matching limitations Q R simultaneously`
- `robust adaptivity conflict Kalman innovation outlier masking`
- `correlated sensor errors innovation variance identify faulty sensor`
- `innovation scale fault masking adaptive threshold`

Post-cutoff discovery used the exact RUN18 title, `covariance_relative_precision`, `innovation Huber OBD GNSS`, and decomposition variants. No material external scholarly work first made public after **15:08:24 UTC** and before this audit was located. Given the sub-hour window, that is only a weak bounded negative result.

## 4. Pre-cutoff novelty / overlap findings

### 4.1 Innovation-based covariance/noise adaptation is decades-old prior art

**Work:** R. K. Mehra, **“On the identification of variances and adaptive Kalman filtering.”** *IEEE Transactions on Automatic Control* 15(2), pp. 175–184, public **1970-04**, DOI: https://doi.org/10.1109/TAC.1970.1099422.

Mehra's work is foundational prior art for estimating unknown stochastic variance/covariance information from innovation behavior in adaptive filtering.

**Compared claims:** C1, C5.

**Classification:** `prior_art` for innovation-driven adaptive covariance/noise estimation.

**Consequence:** RUN18 cannot claim novelty for using observed innovation statistics to adapt an estimator's scale or covariance assumptions.

### 4.2 Innovations were already used for fault detection in 1971

**Work:** R. K. Mehra & J. Peschon, **“An innovations approach to fault detection and diagnosis in dynamic systems.”** *Automatica* 7(5), 637–640, **1971**, DOI: https://doi.org/10.1016/0005-1098(71)90028-8.

**Compared claims:** C5.

**Classification:** `prior_art` for using innovation behavior as a low-cost fault/anomaly signal; `adjacent_prior_work` for RUN18's use of it as a coordinator feature.

### 4.3 Innovation-based adaptive navigation is established and has real kinematic evidence

**Work:** A. H. Mohamed & K. P. Schwarz, **“Adaptive Kalman Filtering for INS/GPS.”** *Journal of Geodesy* 73, 193–203, **1999-05**, DOI: https://doi.org/10.1007/s001900050236.

The paper explicitly reviews innovation-based adaptive estimation and develops an innovation-based adaptive INS/GPS filter that tunes `Q`, `R`, or both, with two kinematic field tests.

**Compared claims:** C1, C2, C5.

**Classification:** `prior_art` for innovation-based adaptive covariance in integrated navigation; `adjacent_prior_work` for RUN18's scalar OBD/GNSS rule.

### 4.4 Residual-covariance adaptation + Huber robust navigation directly predates RUN18

**Work:** **“Adaptive robust Kalman filter for relative navigation using global position system.”** *IET Radar, Sonar & Navigation*, first published **2013-06-01**, DOI: https://doi.org/10.1049/iet-rsn.2012.0170.

The method estimates process-noise covariance from the residual covariance sequence and uses a Huber-derived robust measurement update. The paper explicitly discusses the difficulty of separating process-noise error from measurement-noise uncertainty when both are adapted.

**Compared claims:** C1, C2.

**Classification:** `prior_art` for the generic conjunction `residual/innovation covariance adaptation + Huber robust update + navigation`; `partial_prior_art` for RUN18's exact clipped-EWMA scalar contract.

### 4.5 Adaptive Huber + innovation-based covariance estimation was explicit by 2014

**Work:** Rong Wang, Zhi Xiong, Jianye Liu & Lina Zhong, **“Adaptive Huber-Based Filter for Hypersonic Cruise Vehicle Navigation.”** First published online **2014-09-01**, DOI: https://doi.org/10.1260/1748-3018.8.3.319.

The method combines innovation-based adaptive estimation, Mahalanobis-distance reasoning, robust covariance estimation and adaptive Huber/Kalman filtering for navigation.

**Compared claims:** C1, C2.

**Classification:** `prior_art` for adaptive innovation/covariance + robust Huber navigation; `partial_prior_art` for RUN18's exact implementation.

### 4.6 The repository's earlier RUN14 audit had already located a 2016 uncertainty-adaptive Huber antecedent

**Work:** **“Adaptive M-Estimation for Robust Cubature Kalman Filtering.”** IEEE SSPD 2016, DOI: https://doi.org/10.1109/SSPD.2016.7590586.

That method adjusts measurement-noise covariance inside Huber M-estimation using the discrepancy between actual and theoretical innovation covariance.

**Compared claims:** C1, C2.

**Classification:** `prior_art` for uncertainty-adaptive Huber weighting; `partial_prior_art` for RUN18.

**Incremental note:** this source was already recorded by the RUN14 audit; this run does not present it as a newly discovered repository antecedent. It is retained because it lands directly on RUN18's claim boundary.

### 4.7 No exact pre-cutoff match to the full RUN18 scalar rule was located

The bounded search did not locate a source before the cutoff using the exact conjunction:

1. matched-time OBD↔GNSS residuals;
2. clipped EWMA residual second-moment scale;
3. Huber weighting in those standardized units;
4. declared nominal relative-noise metadata; and
5. a capped rule that assigns residual energy above nominal combined variance to the reference side and thereby increases candidate precision/weight.

**Classification:** the central ingredients are `prior_art`/`partial_prior_art`; the exact local conjunction is **not located** in this pass. This is not a firstness claim.

## 5. Falsification / contrary-evidence ledger

### 5.1 The `covariance_relative_precision` arm is not fault-symmetric; it embeds a reference-side attribution prior

The implementation computes

`excess = max(0, raw_innovation_sigma² - reference_nominal_sigma² - candidate_nominal_sigma²)`

and then uses

`relative_precision = (reference_nominal_sigma² + excess) / candidate_nominal_sigma²`.

The code comments explain why: excess energy is **conservatively assigned to the reference side**, which is the side tracked by the persistent-bias estimator.

That is a legitimate engineering prior, but it is not inference of fault identity from covariance alone. If matched residual `d = e_candidate - e_reference`, then, in general,

`Var(d) = Var(e_candidate) + Var(e_reference) - 2 Cov(e_candidate, e_reference)`.

One scalar residual-energy observation cannot tell us which channel supplied the excess variance/bias without structural assumptions. Modern covariance-identification work likewise treats identifiability as a nontrivial condition rather than an automatic consequence of observing innovations.

**Relevant work:** Lingyi Zhang et al., **“On the Identification of Noise Covariances and Adaptive Kalman Filtering: A New Look at a 50 Year-Old Problem.”** *IEEE Access* 2020, DOI: https://doi.org/10.1109/ACCESS.2020.2982407; TechRxiv public record https://doi.org/10.36227/techrxiv.11663871.v5. The paper derives necessary/sufficient identifiability conditions using auto/cross-covariances of weighted innovations.

**Additional boundary:** He Kong et al., **“The Noise Covariances of Linear Gaussian Systems with Unknown Inputs Are Not Uniquely Identifiable Using Autocovariance Least-squares.”** arXiv v1 **2022-02-10**, later *Systems & Control Letters* 162:105172, DOI: https://doi.org/10.1016/j.sysconle.2022.105172. In its stated unknown-input/ALS regime, process and measurement covariances are not uniquely identifiable.

**Classification:** `boundary_condition`, strength **strong**.

**Target attacked:** mechanism/generalization, not the reported synthetic MAE.

**Required action:** `narrow_claim + add_control`. Describe the RUN18 merit as an **asymmetric reference-suspect heuristic**, not general covariance/fault identification. Required controls are fault-side swap (bias GNSS instead of OBD), both-side faults, correlated/common-mode faults, and a symmetric/state-space covariance comparator.

### 5.2 `OnlineInnovationScale` is a clipped residual second moment; under persistent bias it is not a pure noise covariance estimate

The scale update is a zero-centered EWMA of `clipped_residual²`. If the matched residual has persistent mean bias `b`, its expectation contains approximately `variance + b²` before clipping. Thus the reported `innovation_sigma` can intentionally grow because of systematic mismatch, not only because stochastic noise variance increased.

That behavior can be useful as a generic mismatch-energy feature — and RUN18's synthetic numbers show that it can be useful — but it should not be interpreted as identification of a stochastic covariance component.

There is also a robustness/adaptation feedback risk: if an outlier or persistent fault inflates the scale, subsequent `residual / sigma` values shrink, making later large residuals look less exceptional. This is a classic way adaptive thresholds can mask the process they are meant to reject.

**Direct pre-cutoff counter-design:** Yuxuan Fan et al., **“Adaptive Robust EKF with NARX-Based Velocity Prediction for High Precision AUV Navigation Under DVL Outages.”** *Sensors* 26(13):4240, published **2026-07-03**, DOI: https://doi.org/10.3390/s26134240. Its adaptive Huber–Sage–Husa design explicitly updates noise covariance **only when the residual is normal**, skipping adaptation on outliers so that abnormal measurements do not contaminate the noise estimate.

**Classification:** `boundary_condition`, strength **strong**; `contrary_evidence`, strength **moderate**, against the *general mechanism interpretation* that unconditional clipped residual-energy adaptation is a clean covariance estimator. It is not contrary evidence against the frozen RUN18 MAE table.

**Target attacked:** mechanism and generalization.

**Required action:** `revise_mechanism + add_control`. Call the current statistic a bounded **innovation/mismatch scale** unless covariance identification assumptions are satisfied. Compare it with (a) Huber-gated/frozen scale adaptation, (b) robust scale estimation such as MAD/IRLS/Tukey-style alternatives, and (c) a scale trajectory through fault onset and recovery.

### 5.3 The synthetic fault family is aligned with the estimator's asymmetric prior

In the frozen generator, persistent `static`, `drift`, and `jump` faults are injected into **OBD/reference**, while GNSS receives zero-mean noise, delay and dropout. The covariance-merit arm then assigns excess mismatch energy to **reference/OBD** and increases candidate/GNSS influence.

This is not hidden per-episode fault-label leakage: the estimator is never handed `bias_mode`. But the experiment family and the estimator share a structural assumption about the likely faulty side.

That matters because C4's 7.6–15.7% gains are exactly measured in regimes where that prior is correct by construction.

**Classification:** `boundary_condition`, strength **strong**.

**Target attacked:** external validity and mechanism attribution.

**Required action:** `add_control + downgrade_confidence`. Run the same ablation with GNSS-only persistent bias, alternating fault side, simultaneous bias, and correlated/common-mode error before describing the merit as generally covariance-aware rather than scenario-aware.

### 5.4 Existing literature shows why robustness and covariance adaptation must be separated carefully

The 2013 adaptive robust GPS-navigation paper already notes that simultaneously adapting multiple uncertainty sources is hard because process and measurement uncertainty are difficult to distinguish. The 2026 AHR-EKF paper uses conditional updates precisely to prevent abnormal residuals from corrupting adaptive covariance.

This provides a simpler alternative explanation for RUN18's success: the method is a useful handcrafted **mismatch detector plus asymmetric reliability prior**, not necessarily an estimator that has recovered the physical covariance decomposition.

**Classification:** `boundary_condition`, strength **moderate-to-strong**.

**Required action:** `narrow_claim`; no change to the numerical results.

### 5.5 The clean-regime result is already a useful internal null/boundary

Even after adding the coarse covariance merit, the hybrid remains about **3.4% worse** than the bias-calibrator/OBD-only control when OBD is clean. The Findings Record already describes the result as a trade-off rather than a universal winner.

**Classification:** `failed_replication_or_null` does **not** apply — the experiment was not a failed replication. This is a `boundary_condition`, strength **strong**, on any universal-performance interpretation.

**Required action:** `no_change` to the table; `downgrade_confidence` for general use until fault prevalence/cost and real data justify the trade-off.

## 6. Priority and truth-status conclusions

| claim | priority status | truth status after this audit | evidence strength | required action |
|---|---|---|---|---|
| C1 innovation normalization as conventional fusion primitive | `prior_art` at generic mechanism level | supported only for frozen RUN18 stream | strong prior-art boundary | `narrow_claim` |
| C2 coarse covariance/relative-noise merit | components `prior_art`; exact scalar rule not located | useful asymmetric heuristic in tested reference-fault regimes | strong boundary | `narrow_claim + add_control` |
| C3 no privileged truth/fault label at API boundary | not a novelty claim | true literally, but does not imply fault-symmetry; structural reference-suspect prior is encoded | strong | `add_boundary_condition` |
| C4 reported synthetic gains | local empirical claim | stands for executed harness; generalization low until fault-side swap/real slice | strong within harness | `downgrade_confidence + add_control` |
| C5 innovation sigma/excess energy as coordinator features | innovation fault signals are `prior_art` | plausible low-cost features; incremental control value untested | moderate | `add_control` |
| C6 MaleCNS value should be sought in active decisions rather than rediscovering ordinary robust fusion | not a firstness claim | remains a useful experimental positioning hypothesis | moderate | `no_change` |

No claim is retracted on the basis of this audit. The main correction is semantic and mechanistic: RUN18 did **not** identify which modality caused cross-modal covariance excess. It encoded a reasonable reference-side prior and showed that the resulting heuristic works in synthetic regimes where that prior is usually correct.

## 7. Consequence for the car programme: comparator, not prerequisite

This audit should not expand the pre-driving checklist. It points the other way.

The covariance/innovation machinery belongs in the **conventional comparator/remediation library**. The high-value next experiment for the MaleCNS car programme is still to put the connectome-derived controller in a closed perception→MaleCNS→action→reward loop and observe concrete failures. Fault-side swaps, symmetric covariance models and robust scale variants become relevant when a driving failure implicates this fusion layer or when a scientific claim specifically depends on RUN18.

In other words: RUN18 gives us a stronger baseline and two cheap diagnostic signals. It does not justify postponing embodied driving until the fusion stack is theoretically complete.

## 8. Later work / dependency check

No material external scholarly work first made public after the conservative cutoff **2026-09-19 15:08:24 UTC** was located in the immediate post-cutoff searches. The interval is too short for absence to carry evidential weight, so no `later_independent`, `later_overlap`, `later_non_citing`, `later_citing`, or `later_derivative` classification is assigned here.

## 9. Search result accounting

Important negative searches preserved in this pass:

- exact RUN18 title;
- exact local function name `covariance_relative_precision`;
- `innovation Huber OBD GNSS`;
- variants combining clipped EWMA, relative precision, Huber, matched-time residual and reference-side covariance attribution.

No exact prior source matching the complete local scalar rule was located. This does not imply that none exists.
