---
type: "Audit Report"
title: "MaleCNS Run14 age-normalized Huber fusion — prior-art and falsification audit — 2026-09-19"
description: "Claim-level temporal, novelty, and adversarial validity audit of RUN14 freshness-dependent Huber robust fusion, including asynchronous/OOSM prior art and post-cutoff RUN15 temporal-alignment evidence."
tags: [malecns, prior-art, falsification, sensor-colony, robust-fusion, huber, freshness, asynchronous-fusion, oosm, sensor-fusion, temporal-alignment]
timestamp: 2026-09-19T12:00:00Z
---

# MaleCNS Run14 age-normalized Huber fusion — prior-art and falsification audit — 2026-09-19

> **Status:** claim-specific audit of [`FINDINGS_2026-09-19_RUN14_ADAPTIVE_ROBUST_TRUST.md`](../../experiments/malecns_car_interface/FINDINGS_2026-09-19_RUN14_ADAPTIVE_ROBUST_TRUST.md). This record separates temporal priority from present truth status. It does not establish exhaustive novelty, patent novelty, copying, causal dependence, plagiarism, or misconduct. Negative searches are bounded observations, not proof of absence.

## 1. Claims and explicit falsifiers

### C1 — a second bounded-influence estimator family improves the frozen Run13 fixed-Cauchy baseline in the current generator

RUN14 reports lower MAE for fixed Huber and lower still for age-normalized Huber under the executed camera-age profiles, fault-rate shifts, and shared-camera-bias stress.

**Would be wrong, too narrow, or practically uninformative if:** paired reruns fail; a stronger matched robust estimator such as standardized-innovation Huber, Student-t/correntropy, or an asynchronous robust filter erases the advantage; or the gain is specific to the generator's scaling and disappears on a synchronized real sensor slice.

### C2 — freshness should both directly discount a report and contract its Huber residual radius

The implementation uses `freshness = 2 ** (-age_ms / half_life_ms)` both as a direct multiplicative discount and through `effective_scale = max(min_scale, base_scale * freshness ** age_power)`.

**Would be wrong as a general mechanism if:** after time alignment or uncertainty-standardization, the extra age-dependent radius gives no benefit; legitimate dynamics cause old-but-correct measurements to be rejected as outliers; or the optimal residual tolerance grows rather than shrinks because prediction uncertainty increases with latency.

### C3 — the selected Huber scale/age exponent can be calibrated without hidden-truth supervision by a later independent corroborating measurement

The optimizer scores candidates against a delayed corroborator rather than against the evaluation MAE.

**Would be materially overstated if:** that corroborator is generated from privileged simulator truth; realistic teacher errors are biased, heteroscedastic, temporally misaligned, or correlated with the candidate; or calibration ranking changes when those effects are introduced.

### C4 — the age-aware gain transfers across freshness and independent fault-rate shifts

RUN14 reports a positive paired improvement over frozen Run13 Cauchy under uniform/fresh-skewed/stale-skewed age profiles and fault probabilities from 0% to 40%.

**Would fail to generalize if:** timestamp uncertainty, changing dynamics, calibration bias, modality-specific latency, missing data, or real-world noise reverses the ranking.

### C5 — the estimator is robust to shared camera bias because another modality provides an independent residual reference

The shared-camera-bias stress makes four additional camera probes share one signed bias while the other modality remains independently generated.

**Would be materially narrower if:** both modalities share a calibration/clock/upstream-model error; the cross-modal reference is itself stale or biased; the common-mode fault reaches the trusted summaries; or rapid true state change creates legitimate cross-modal disagreement.

### C6 — robust estimation should remain ahead of learned/MaleCNS trust coordination for ordinary fusion until a coordinator clears stronger statistical controls

RUN14 interprets the new statistical baseline as evidence that a learned/MaleCNS coordinator has not yet earned ordinary robust averaging as its job in this generator.

**Would be too broad if:** a lawful learned coordinator beats matched time-aligned/covariance-aware robust baselines on real data and under equal information/compute, or if the coordinator supplies value in resource/action decisions that the static estimator cannot perform.

## 2. Temporal reconstruction

### 2.1 Content-bearing commits

PR [#640](https://github.com/franklinbaldo/papers/pull/640) contains the relevant sequence:

- [`52d629421c009618b03d2f95aeb1413ea8b81dce`](https://github.com/franklinbaldo/papers/commit/52d629421c009618b03d2f95aeb1413ea8b81dce), Git timestamp **2026-09-19 11:02:08 UTC**, `experiment: add age-normalized Huber trust primitive` — first implementation of the freshness-dependent Huber radius;
- [`d843618f60421a61b8a070ff65deccce592ae9cb`](https://github.com/franklinbaldo/papers/commit/d843618f60421a61b8a070ff65deccce592ae9cb), **11:04:51 UTC**, first matched RUN14 ablation;
- [`561c276b6a61744bd3354054b8e8caf85435b769`](https://github.com/franklinbaldo/papers/commit/561c276b6a61744bd3354054b8e8caf85435b769), **11:05:23 UTC**, simplified matched controls;
- [`aad9a6955619b125ede1aa790f7108c861a69c9c`](https://github.com/franklinbaldo/papers/commit/aad9a6955619b125ede1aa790f7108c861a69c9c), **11:05:38 UTC**, invariant tests;
- [`a644312bda312981449f783725b690126e401a05`](https://github.com/franklinbaldo/papers/commit/a644312bda312981449f783725b690126e401a05), **11:06:50 UTC**, first complete findings record and numerical C1/C4/C5 interpretation.

### 2.2 Conservative public cutoff

GitHub records PR #640 as created at **2026-09-19 11:07:03 UTC**. Commit timestamps alone do not prove the exact instant the head branch became publicly accessible, so this audit uses **2026-09-19 11:07:03 UTC** as the conservative public cutoff for C1–C6.

All external works classified as prior art below were public before that cutoff; the conservative choice therefore does not alter their temporal class.

**Priority confidence:** `1.0` for public availability by PR creation.

## 3. Search protocol

Sources searched included IEEE Xplore, Springer/DOI records, SAGE, MDPI/Sensors, arXiv, PubMed/Crossref-discoverable records, DBLP, and targeted current web discovery. Queries were decomposed across robust estimation, asynchronous fusion, out-of-sequence measurements, Age of Information/freshness, temporal calibration, correlated sensor errors, and innovation-standardized Huber filtering.

Representative overlap queries:

- `adaptive Huber sensor fusion measurement noise`
- `Huber asynchronous fusion multi-rate sensor`
- `Huber delayed measurement robust fusion age`
- `freshness Huber sensor fusion stale measurement`
- `Age of Information sensor fusion stale measurement gating`
- `age-aware UWB IMU fusion stale measurement`
- `out-of-sequence measurement vehicle sensor fusion`
- `adaptive M-estimation innovation covariance Huber`

Representative adversarial queries:

- `out-of-sequence measurement old observation optimal update dynamics`
- `delayed measurement merit depends on system dynamics noise`
- `sensor fusion temporal misalignment failure`
- `time synchronization error GNSS INS covariance`
- `Huber standardized residual innovation covariance`
- `correlated noise robust sensor fusion outlier`
- `stale measurement still useful delayed observation`
- `age-aware fusion limitation abrupt dynamics`

Post-cutoff searches used `age-normalized Huber fusion`, `freshness-dependent Huber radius`, `Huber freshness sensor fusion`, and decomposition variants. No external research work first made public after **11:07:03 UTC** and materially overlapping the exact RUN14 conjunction was located in the roughly one-hour observation window. A **local post-cutoff RUN15**, however, was published during this audit and is handled separately in §6 because it is both temporally later and directly derivative from RUN14.

## 4. Pre-cutoff novelty / overlap findings

### 4.1 Adaptive Huber robust filtering is established prior art

**Work:** Wei Li, Meihong Liu & Dengping Duan, **“Adaptive Huber-based Kalman filtering for spacecraft attitude estimation.”** First published online **2014-04-03**, *Transactions of the Institute of Measurement and Control* 36(6), DOI: https://doi.org/10.1177/0142331213519358.

The filter combines Huber robust estimation with adaptation to model error and unknown measurement noise, tested on gyroscope + star-tracker fusion.

**Compared claims:** C1, C6.

**Classification:** `prior_art` for adaptive Huber robust sensor/state estimation; `adjacent_prior_work` for RUN14's exact freshness-to-radius mapping.

**Consequence:** neither Huber bounded influence nor adapting a Huber filter to changing uncertainty is a RUN14 novelty boundary.

### 4.2 Huber filtering for asynchronous multi-rate multisensor systems predates RUN14 directly

**Work:** Jang-Seong Park, Gyeong-Hun Kim, Hyuck-Hoon Kwon & Jong-Han Kim, **“Huber-based Asynchronous Fusion Filter for Robust Multi-rate Sensor Processing.”** *International Journal of Control, Automation and Systems* 23(10), **2025**, DOI: https://doi.org/10.1007/s12555-025-0069-7.

The paper extends asynchronous fusion filtering with a Huber cost for an arbitrary number of sensors at different rates and evaluates synchronous/asynchronous setups under Gaussian and non-Gaussian measurement errors.

**Compared claims:** C1, C4, C6.

**Classification:** `prior_art` for the generic combination `Huber robust estimation + asynchronous/multi-rate multisensor fusion`; `partial_prior_art` for RUN14. The located abstract does not disclose RUN14's specific freshness-dependent contraction of the Huber residual radius.

**Temporal note:** the bibliographic record identifies volume 23(10), 2025; exact first-online day was not independently recovered in this pass, but the work is unambiguously public in 2025, well before the 2026-09-19 cutoff.

### 4.3 Adaptive M-estimation already scales Huber behavior using innovation statistics

**Work:** **“Adaptive M-Estimation for Robust Cubature Kalman Filtering.”** IEEE SSPD 2016, conference **2016-09-22/23**, DOI: https://doi.org/10.1109/SSPD.2016.7590586.

The method adjusts the measurement-noise covariance used inside Huber M-estimation from the discrepancy between actual and theoretical innovation covariance.

**Compared claims:** C1, C2.

**Classification:** `prior_art` for uncertainty-adaptive Huber weighting; `partial_prior_art` for RUN14's adaptation rule.

**Consequence:** the meaningful question is not whether Huber can adapt, but whether **age/freshness is the right variable and functional coupling once uncertainty and dynamics are accounted for**.

### 4.4 Delayed/out-of-sequence observations have long been handled with explicit dynamics

**Work:** Yaakov Bar-Shalom, **“One-step solution for the multistep out-of-sequence-measurement problem in tracking.”** *IEEE Transactions on Aerospace and Electronic Systems* 40(1), **2004-01-31**, DOI: https://doi.org/10.1109/TAES.2004.1292140.

The paper treats the nonstandard problem of updating a current estimate using an older measurement with arbitrary lag and evaluates covariance consistency.

**Compared claims:** C2, C4.

**Classification:** `adjacent_prior_work` for RUN14 novelty; `boundary_condition` for its mechanism interpretation.

**Consequence:** age is not only a reliability score. A stale observation may refer to a different physical state and can be useful after a dynamics-aware update/retrodiction.

### 4.5 The same issue is established specifically in automotive multisensor fusion

**Work:** Antje Westenberger, Steffen Wäldele, Balaganesh Dora, Bharanidhar Duraisamy, Marc M. Muntzinger & Klaus Dietmayer, **“Multi-sensor fusion with out-of-sequence measurements for vehicle environment perception.”** ICRA **2013-05-06/10**, DOI: https://doi.org/10.1109/ICRA.2013.6631147.

The work handles asynchronous/out-of-sequence measurements in vehicle perception and evaluates the approach on real crash-test data.

**Compared claims:** C2, C4, C6.

**Classification:** `adjacent_prior_work`; strong domain-specific boundary for interpreting simple freshness penalties as the full solution to latency.

### 4.6 Exponential decay of old-measurement merit is prior work — but it is dynamics- and noise-dependent

**Work:** Josiah Yoder, Stanley Baek, Hyukseong Kwon & Daniel Pack, **“Exploring the Exponentially Decaying Merit of an Out-of-Sequence Observation.”** Published **2018-06-15**, *Sensors* 18(6):1947, DOI: https://doi.org/10.3390/s18061947.

The paper finds approximately exponentially decreasing value of older observations, but derives that merit from the ideal filter and explicitly includes the state-transition model, observation model, process noise, observation noise, sensing rate, delay and target dynamics.

**Compared claims:** C2, C4.

**Classification:** `prior_art` for exponential age-dependent measurement merit; `boundary_condition` against age-only interpretation.

**Consequence:** RUN14's use of exponential freshness is not novel by itself, and the literature directly warns that the correct decay depends on more than timestamp age.

### 4.7 Age-of-information-aware cross-modal fusion is pre-cutoff recent prior art

**Work:** Tehmina Bibi, Anselm Köhler, Jan-Thomas Fischer & Falko Dressler, **“AoI-FusionNet: Age-Aware Tightly Coupled Fusion of UWB-IMU under Sparse Ranging Conditions.”** arXiv v1 **2026-03-13 09:50:57 UTC**, https://arxiv.org/abs/2603.12849.

AoI-FusionNet explicitly uses an Age-of-Information-aware decay module to reduce the influence of stale UWB measurements and an attention gate to balance UWB and IMU by temporal freshness, evaluated on real-world alpine measurements.

**Compared claims:** C2, C4, C6.

**Classification:** `prior_art` for age-aware downweighting in multimodal fusion; `partial_prior_art` for the combination of freshness and robust residual gating.

### 4.8 Age-of-Sensing trust modulation also predates RUN14

**Work:** **“Time-Aware Graph Neural Network for Asynchronous Multi-Station Integrated Sensing and Communications Fusion in Open RAN.”** *Sensors* 26(8):2376, published **2026-04-12**, DOI: https://doi.org/10.3390/s26082376.

Its TA-Gate computes trust weights from Age-of-Sensing metadata and suppresses stale outliers before aggregation.

**Compared claims:** C2, C4.

**Classification:** `prior_art` for explicit freshness-to-trust gating; `adjacent_prior_work` for RUN14's Huber rule.

### 4.9 No exact pre-cutoff match to the full RUN14 formula was located in this pass

The searches above located all major components independently — Huber robust estimation, adaptive Huber filtering, Huber asynchronous fusion, exponential merit decay for old measurements, and explicit AoI/freshness gating in multimodal fusion. They did **not** locate a source before the cutoff that uses the exact conjunction

`confidence × exponential freshness × Huber(residual / (base_scale × freshness^age_power))`

with the particular reality-bounded cross-modal report contract used in RUN14.

**Classification:** components are `prior_art`/`partial_prior_art`; the exact conjunction remains **not located** after the bounded searches above. This is not a claim of firstness.

## 5. Falsification and contrary-evidence ledger

### 5.1 The strongest mechanistic problem: RUN14's raw residual mixes sensor error with lawful state evolution

The generator in `colony_continuous_context_ablation.py` creates each report as

`value = truth - velocity * (age_ms / 1000) + noise`.

A stale report is therefore intentionally a measurement of an **earlier physical state** under constant velocity. RUN14 then compares that candidate value against a cross-modal estimate made from currently available summaries and contracts the allowed Huber residual as age grows.

Consequently, a large stale residual can be exactly what a correct sensor should produce when the state is changing. The mechanism can classify legitimate dynamics as outlierness unless temporal state evolution is modeled first.

This is not merely theoretical. The OOSM literature above solves the update by accounting for lag/dynamics, and Yoder et al. derive old-measurement merit from system dynamics and noise rather than age alone.

**Classification:** `boundary_condition`; potentially `contrary_evidence` against the broad verbal mechanism “stale means must agree more closely with current evidence.”

**Strength:** `strong` for general mechanism interpretation; `no_change` to the executed RUN14 synthetic MAE table.

**Target attacked:** C2 mechanism and C4 generalization.

**Required change:** `narrow_claim` + `add_control` + `revise_mechanism`. Treat age-dependent radius contraction as a tested heuristic for the present generator until it beats a time-aligned/OOSM estimator and an uncertainty-standardized robust estimator.

### 5.2 Temporal misalignment is itself a failure mode, not just a confidence feature

**Work:** **“Sync or Sink? The Robustness of Sensor Fusion Against Temporal Misalignment.”** IEEE RTAS 2024, DOI: https://doi.org/10.1109/RTAS61025.2024.00018.

The study formalizes temporal robustness and finds materially different sensitivity to sensor misalignment in camera-LiDAR fusion, with especially high sensitivity for some sensor timing shifts.

Older GPS/INS work reaches the same engineering point. Ding et al., **“Time Synchronization Error and Calibration in Integrated GPS/INS Systems”** (first published **2008-02-01**, DOI: https://doi.org/10.4218/etrij.08.0106.0306), treats synchronization accuracy as critical to fusion performance; **“Effects of time synchronization errors in GNSS-aided INS”** (IEEE/ION PLANS **2008-05-05/08**, DOI: https://doi.org/10.1109/PLANS.2008.4570010) shows increased estimation covariance/bias and benefits from explicitly modeling timing error.

**Classification:** `boundary_condition`.

**Strength:** `strong` for external validity.

**Target attacked:** C2/C4 generalization.

**Required change:** `add_control`: inject timestamp offset, clock drift and jitter separately from ordinary observation age and test time-registration/OOSM baselines.

### 5.3 Correlated sensor errors weaken the meaning of a cross-modal residual reference

**Work:** Yan Zhou, Dongli Wang, Tingrui Pei & Shujuan Tian, **“Robust Estimation Fusion in Wireless Sensor Networks with Outliers and Correlated Noises.”** First published online **2014-04-02**, DOI: https://doi.org/10.1155/2014/393802.

The paper explicitly handles outlier-contaminated measurements together with correlated process/sensor noise and unknown cross-correlation among local estimates.

RUN14's shared-camera-bias stress is useful, but the other modality and delayed calibration teacher remain independently generated. That does not test shared calibration, clock, environmental or upstream-model errors across both sides of the residual.

**Classification:** `boundary_condition`.

**Strength:** `strong` against generalizing C5 beyond one-sided common-mode bias; `moderate` for the exact executed stress.

**Target attacked:** C5 mechanism/generalization.

**Required change:** `add_control`: corrupt both modalities/reference summaries with shared calibration and time errors and include unknown correlation in the estimator baseline.

### 5.4 The calibration API is truth-free, but the synthetic teacher-generation mechanism is not

`colony_adaptive_soft_trust_ablation.py` defines the delayed corroborator as

`truth + rng.gauss(0.0, 0.10)`.

RUN14 is therefore correct that hyperparameter search is not performed against hidden-truth MAE and that the estimator API does not consume hidden truth. But the calibration teacher is still an **oracle-generated proxy from latent truth plus independent Gaussian noise**. This is materially easier than a real sensor teacher with bias, latency, shared causes, missingness and heteroscedasticity.

**Classification:** `boundary_condition`.

**Strength:** `strong` against interpreting C3 as demonstrated real-world truth-free calibration; it does not invalidate the synthetic selection result.

**Target attacked:** C3 mechanism/generalization.

**Required change:** `narrow_claim` + `add_control`: say that calibration is evaluation-truth-free at the API boundary but currently uses an oracle-generated synthetic corroborator; repeat with biased/delayed/heteroscedastic teachers and real synchronized sensor data.

### 5.5 A stronger robust-estimation baseline could explain the remaining gain with fewer assumptions

Adaptive Huber and asynchronous Huber filtering already exist, and robust filtering commonly adjusts residual influence using measurement/innovation uncertainty. The simpler alternative mechanism is therefore not “freshness is physically the correct Huber radius,” but “RUN14 is approximating an uncertainty-standardized robust residual using age as a proxy for uncertainty.”

If that alternative is correct, then age should add little once the innovation is properly time-aligned and normalized by its predicted variance.

**Classification:** `boundary_condition` / alternative mechanism.

**Strength:** `moderate` now; it becomes `strong contrary_evidence` if a covariance-aware/OOSM Huber baseline dominates RUN14 on matched data.

**Target attacked:** C2 mechanism, not C1's measured table.

**Required change:** `add_control` + potentially `revise_mechanism`.

## 6. Post-cutoff evidence: RUN15 directly tests the temporal-alignment concern

During this audit the repository advanced with PR [#647](https://github.com/franklinbaldo/papers/pull/647), created at **2026-09-19 12:06:42 UTC**, nearly one hour **after** RUN14's 11:07:03 UTC cutoff. Its Findings Record explicitly begins from RUN14's unresolved temporal-identification problem, so there is positive evidence of direct dependency.

**Work:** local RUN15, **“Matched-time OBD/GNSS calibration.”** Merge commit [`14850cb0716a8567504cc5ff4c22cc23bbf775d0`](https://github.com/franklinbaldo/papers/commit/14850cb0716a8567504cc5ff4c22cc23bbf775d0), merged **2026-09-19 12:07:59 UTC**.

**Temporal classification:** `later_derivative`. It is not prior art against RUN14.

RUN15 is not a direct replication of the exact age-normalized Huber formula, so it does **not** falsify C1's RUN14 numerical result. It does, however, run a more targeted asynchronous OBD/GNSS experiment in which the exact same persistent-bias calibrator is fed either:

- matched-time residual `OBD(t_measure) - GNSS(t_measure)`; or
- physically wrong unaligned residual `OBD(t_arrival) - GNSS(t_measure)`.

The unaligned path false-activates on about **7.99%** of clean steps versus about **0.011%** for matched-time calibration, with clean-condition MAE `0.187025` versus `0.143489`. Under static offset, matched-time calibration reaches `0.427450` MAE versus `0.572579` for the unaligned version; under drift, `0.318175` versus `0.347018`. RUN15 also reports that a stale-Huber fusion arm is worse than matched-time calibration in all four tested bias regimes (`0.203328` vs `0.143489` clean; `1.257023` vs `0.427450` static; `0.344795` vs `0.318175` drift; `0.966666` vs `0.579356` step bias).

**Classification on truth axis:** `contrary_evidence` against the broad mechanism “robustly downweight stale disagreement and temporal mismatch is thereby handled”; `boundary_condition` for RUN14's exact age-Huber mechanism.

**Strength:** `strong` for the need to separate timestamp alignment from trust/outlier weighting; `moderate` for the exact RUN14 formula because RUN15's stale-Huber arm is not the same estimator and uses a different harness/channel pair.

**Target attacked:** C2 mechanism and C4 transfer; supports C6's conservative estimator-first interpretation.

**Required action:** `revise_mechanism` + `add_boundary_condition`. Timestamp alignment is now empirically demonstrated inside the same research programme as a first-class interface primitive. The remaining unresolved discriminator is whether age-dependent Huber radius still adds value **after** matched-time alignment and covariance/innovation standardization.

## 7. Present truth status and required paper changes

| claim | priority status | truth-status assessment | force | required action |
|---|---|---|---|---|
| C1 adaptive Huber improves Run13 in current generator | generic method is `prior_art`; exact executed result is local | supported for executed synthetic runs | — | `no_change` to numbers; `add_control` for generality |
| C2 double-use of freshness is a physical mechanism | components are `prior_art`/`partial_prior_art` | useful heuristic in RUN14; OOSM literature + later RUN15 show temporal alignment is load-bearing | strong | `narrow_claim`, `revise_mechanism`, `add_control` |
| C3 delayed corroborator enables truth-free calibration | generic delayed/indirect calibration is not a novelty boundary | API is truth-free, teacher generation is oracle-derived synthetic truth | strong | `narrow_claim`, `add_boundary_condition`, `add_control` |
| C4 gains transfer across age/fault shifts | local empirical result | supported only inside current generator family; RUN15 shows a distinct asynchronous regime where time alignment dominates stale robust fusion | moderate | `downgrade_confidence` externally, `add_control` |
| C5 handles common-mode camera bias | local empirical result | supported for one-sided camera bias, not shared cross-modal causes | strong boundary | `add_boundary_condition`, `add_control` |
| C6 robust estimator should precede coordinator | broad robust-estimation lineage is prior art | well supported **for this programme's current evidence ladder**, not universal | moderate | `narrow_claim` to current ladder |

The central correction is not to retract RUN14. The synthetic result is real under its harness. The correction is to avoid elevating the successful formula into a general physical law before testing **time alignment, dynamics and uncertainty normalization**.

## 8. Discriminating next experiment

Issue [#646](https://github.com/franklinbaldo/papers/issues/646) freezes the next test. RUN15 has already supplied a strong first matched-time control, so the remaining ladder should now reuse that primitive and directly compare:

1. Run13 fixed Cauchy;
2. fixed Huber;
3. current age-normalized Huber;
4. standardized-innovation / covariance-aware Huber;
5. matched-time / lawful OOSM treatment using explicit timestamp alignment and, where necessary, a declared dynamical model;
6. an age-only exponential-merit baseline separating ordinary stale-data discount from the extra age-dependent robust radius.

Stress abrupt acceleration/turns, timestamp offset/drift/jitter, systematic modality latency, simultaneous correlated calibration/common-mode faults, missing modalities, and biased/heteroscedastic delayed teachers. Then repeat the frozen ladder on at least one checksum/version-pinned real synchronized pair such as camera↔IMU yaw or OBD-II↔GNSS speed.

**Predeclared falsification rule:** if current age-normalized Huber loses its residual advantage after matched-time alignment or innovation standardization, downgrade the mechanism to a useful heuristic for this synthetic generator and remove any statement that contracting the Huber radius with age is a general physical law. If the age exponent adds no gain over a properly aligned/covariance-aware estimator, do not attribute causal value to the double use of freshness.

## 9. Post-cutoff / citation-dependence summary

No **external** material work first published after **2026-09-19 11:07:03 UTC** was located in the immediate post-cutoff searches. Because the observation window is roughly one hour, this is weak negative evidence only.

The one material post-cutoff item is local RUN15/PR #647, classified `later_derivative` because it explicitly takes RUN14's temporal-identification gap as its starting point. That category documents verified dependence inside our own programme; it says nothing about outside copying or citation behavior.

No external candidate justified `later_independent`, `later_overlap`, `later_non_citing`, `later_citing`, or `later_derivative` in this run.

## 10. Audit conclusion

RUN14 remains a useful negative control against prematurely assigning ordinary robust fusion to a learned/MaleCNS coordinator. Its numerical ranking inside the current synthetic harness is unchanged.

The novelty boundary is narrower than the original findings record suggested: adaptive Huber filtering, Huber asynchronous fusion, exponential decay of old-measurement merit, and age-aware multimodal trust/downweighting are all pre-cutoff work. The exact RUN14 formula was not located, but its components are established.

The more important update is epistemic. The RUN14 generator makes stale reports historical physical states, so raw disagreement with a current estimate confounds **measurement corruption with lawful temporal evolution**. OOSM literature already predicts this boundary, and post-cutoff RUN15 independently demonstrates it inside the same programme: matched-time residuals sharply reduce false corrections compared with arrival-time mismatch. A covariance-aware/standardized-innovation Huber control remains outstanding. Until RUN14 clears that control and a non-oracle real sensor slice, its age-dependent Huber radius should be described as a successful synthetic heuristic, not as a generally validated physical principle.
