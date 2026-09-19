---
type: "Audit Report"
title: "MaleCNS paid probe-then-trust gating — prior-art and falsification audit — 2026-09-19"
description: "Claim-level temporal, novelty, and adversarial validity audit of RUN11 specialist probing versus admission, fixed trust gating, cross-modal agreement, fault-prevalence dependence, and stronger robust-fusion controls."
tags: [malecns, prior-art, falsification, sensor-colony, probe-then-trust, fault-detection, sensor-fusion, robustness, integrity-monitoring]
timestamp: 2026-09-19T08:59:00Z
---

# MaleCNS paid probe-then-trust gating — prior-art and falsification audit — 2026-09-19

> **Status:** claim-specific audit of [`FINDINGS_2026-09-19_RUN11_PROBE_TRUST.md`](../../experiments/malecns_car_interface/FINDINGS_2026-09-19_RUN11_PROBE_TRUST.md). This record separates temporal priority from present truth status. It does not establish exhaustive novelty, patent novelty, copying, causal dependence, plagiarism, or misconduct. Negative searches are bounded observations, not proof of absence.

## 1. Claims and explicit falsifiers

### C1 — probe/acquisition and trust/admission are distinct decisions

RUN11 pays for a specialist report first and only afterward decides whether that report is admitted into the actuator-facing fusion path.

**Would be wrong as a claimed novelty, or scientifically unnecessary, if:** established measurement-validation/fault-detection systems already separate obtaining a measurement from accepting/excluding it; or a matched robust fusion rule that never makes a hard admission decision performs as well or better.

### C2 — lawful observed report properties can identify harmful paid probes without hidden truth

The fixed gate uses declared confidence, timestamp-derived freshness, and agreement with already-trusted cross-modal evidence. Synthetic truth and injected fault identity are unavailable at decision time.

**Would be materially weakened if:** healthy and faulty reports are not separable in those observables under realistic shifts; the reference estimate is itself wrong; correlated faults make wrong modalities agree; or abrupt legitimate state changes look like inconsistency and are rejected.

### C3 — the fixed score and threshold improve robustness in the RUN11 synthetic regime

At the default 20% high-confidence injected specialist-fault rate, threshold `0.12` lowers MAE by roughly 1.71–2.08% relative to automatically admitting every paid probe, across three camera-age profiles.

**Would be wrong or materially narrower if:** independent reruns do not preserve the paired advantage; a threshold calibrated under another fault prevalence/noise regime reverses the effect; or stronger hard/soft robust-estimation baselines close the gap.

### C4 — benefit grows when confidently wrong probes are more prevalent

The held threshold is nearly neutral at 0% faults, slightly worse at 10%, beneficial at 20%, and more beneficial at 30% in the synthetic generator.

**Would fail to generalize if:** this monotonic pattern disappears under different fault magnitudes, correlated faults, calibration errors, modality shifts, or real sensor data. The executed table remains valid for its generator even if generalization fails.

### C5 — cross-modal agreement is a useful trust signal

RUN11 penalizes a candidate that disagrees with a current estimate built from its own modality plus an independent modality.

**Would be unsafe as a general rule if:** disagreement cannot identify which source is wrong; multiple sensors share a fault; the model/reference estimate is wrong; or a true environmental transition causes one healthy modality to move first.

### C6 — a learned/adaptive trust gate is the appropriate next escalation

The Findings Record proposes learning admission from delayed lawful outcomes, retaining the fixed gate as a control.

**Would lack value if:** an adaptive statistical threshold, robust M-estimator/soft weighting, calibrated integrity monitor, or other simpler baseline matches or exceeds the learned policy under fault-rate and modality-correlation shifts.

## 2. Temporal reconstruction

### 2.1 Content-bearing commits

PR [#618](https://github.com/franklinbaldo/papers/pull/618) contains the relevant sequence:

- [`b11948f492bcb136ec942ccd6dd9dbaa54ab364d`](https://github.com/franklinbaldo/papers/commit/b11948f492bcb136ec942ccd6dd9dbaa54ab364d), Git timestamp **2026-09-19 07:59:50 UTC**, `Add reality-bounded probe-then-trust gate` — first implementation of the generic C1/C2 mechanism;
- [`ec3b7c55a79badde7c08cc5b089f3112920b28b8`](https://github.com/franklinbaldo/papers/commit/ec3b7c55a79badde7c08cc5b089f3112920b28b8), **08:00:10 UTC**, `Add probe-then-trust ablation`;
- [`1b8fdfe14b984932c6c2f475363e1777cd3dffd0`](https://github.com/franklinbaldo/papers/commit/1b8fdfe14b984932c6c2f475363e1777cd3dffd0), **08:00:23 UTC**, contract tests;
- [`8c6912b9afb2a7c3197bb1507bdf0065723af816`](https://github.com/franklinbaldo/papers/commit/8c6912b9afb2a7c3197bb1507bdf0065723af816), **08:01:01 UTC**, `Record Run 11 probe-then-trust results` — first occurrence of the complete C3/C4 numerical result and C6 follow-on.

### 2.2 Conservative public cutoff

GitHub records PR #618 as created at **2026-09-19 08:01:19 UTC**. Commit author timestamps alone do not establish the exact instant a branch became public, so this audit uses **2026-09-19 08:01:19 UTC** as the conservative public cutoff for C1–C6.

All work classified below as prior art was public years before that cutoff, so this conservative choice does not affect the temporal classification.

**Priority confidence:** `1.0` for public availability by PR creation.

## 3. Search protocol

Sources searched included NASA/NTRS, GNSS/RAIM/FDE literature, *The Journal of Navigation*, NAVIGATION/Institute of Navigation, sensor-fault-diagnosis literature, robust state estimation, Dempster–Shafer conflict detection, data-association/validation gating, and targeted current/post-cutoff web and arXiv searches.

Representative overlap queries:

- `fault detection exclusion multisensor navigation accept reject measurement`
- `measurement validation gate sensor fusion fault detection exclusion`
- `probe then trust sensor fusion admission measurement`
- `cross sensor conflict without ground truth fault detection`
- `sensor reliability conflict weighted evidence fusion`
- `residual based all source fault detection exclusion heterogeneous sensors`
- `robust Kalman outlier rejection measurement gating`
- `paid probe specialist trust sensor fusion`

Representative adversarial queries:

- `fixed threshold sensor fault false alarm missed detection adaptive threshold`
- `wrong exclusion fault detection exclusion probability`
- `correlated simultaneous sensor faults consensus fault isolation`
- `hard gating rejects valid measurement transient`
- `innovation gating measurement starvation divergence`
- `soft gating robust Kalman hard rejection comparison`
- `cross-modal disagreement cannot identify faulty sensor`
- `common mode sensor fault consensus agreement`

Immediate post-cutoff exact/decomposition searches for `MaleCNS probe trust`, `paid probe trust gate`, and `specialist trust gating sensor fusion` did not locate a material first-public-after-cutoff research work. The post-cutoff observation window is less than one hour and therefore provides only weak negative evidence.

## 4. Pre-cutoff novelty / overlap findings

### 4.1 Multisensor fault detection/isolation already separates measurement acquisition from exclusion

**Work:** Paul A. Kline & Frank van Graas, **“Fault Detection and Isolation for Multisensor Navigation Systems.”** NASA/Ohio University, public conference record dated **1991-12-01**.

- Primary record: https://ntrs.nasa.gov/citations/19920008750

The system compares redundant measurements/estimators to detect and isolate erroneous measurement data. The scientific object is already “measurement exists, then decide whether it is inconsistent/faulty enough to isolate from the navigation solution.”

**Compared claims:** C1, C2.

**Classification:** `prior_art` for the generic acquisition/validation/exclusion split; `adjacent_prior_work` for the exact MaleCNS specialist abstraction.

**Consequence:** “paying to hear a fly is not the same action as trusting that fly” is a useful architecture slogan for this project, but it is not defensible as a generic sensor-fusion novelty claim.

### 4.2 GNSS FDE makes detect-then-exclude an explicit integrity architecture

**Work:** Ling Yang, Nathan L. Knight, Yong Li & Chris Rizos, **“Optimal Fault Detection and Exclusion Applied in GNSS Positioning.”** *The Journal of Navigation* 66(5), first published online **2013-05-17**.

- Primary article: https://doi.org/10.1017/S0373463313000155

The paper states that detection alone is insufficient in primary navigation: after identifying a faulty pseudorange, it should be excluded before navigation continues. It also quantifies missed detection and **wrong exclusion**, showing that exclusion itself is a fallible decision that can worsen positioning.

**Compared claims:** C1, C3, C5.

**Classification:** `prior_art` for detect/identify/exclude architecture; `boundary_condition` for RUN11 hard admission.

### 4.3 Cross-sensor conflict without ground truth predates RUN11

**Work:** Jennifer Carlson & Robin R. Murphy, **“Use of Dempster-Shafer Conflict Metric to Detect Interpretation Inconsistency.”** Public arXiv version **2012-07-04** (paper associated with UAI work).

- Primary preprint: https://arxiv.org/abs/1207.1374

The work asks whether a system can determine that something is wrong **using only the sensor data used to construct the world model**, without ground truth. It evaluates conflict indicators on sonar and laser data for classification, discrepancy estimation, and problem isolation.

**Compared claims:** C2, C5.

**Classification:** `partial_prior_art`.

**Why partial:** it anticipates the no-hidden-truth, cross-sensor-conflict diagnostic principle, but not RUN11’s exact confidence × freshness × exponential disagreement score, paid-specialist contract, or fixed-compute MaleCNS ablation.

### 4.4 All-source residual consensus already distinguishes inconsistency from fault identity

**Work:** Juan Jurado, John Raquet, Christine M. Schubert Kabban & Jonathon Gipson, **“Residual-based multi-filter methodology for all-source fault detection, exclusion, and performance monitoring.”** *NAVIGATION* 67(3), first published **2020-08-25**.

- Primary article: https://doi.org/10.1002/navi.384

This method explicitly moves beyond identical synchronous sensors to heterogeneous/asynchronous all-source sensors. Critically, it states that a residual inconsistency for sensor `i` does **not** imply that sensor `i` is faulty: the mismatch can arise from the candidate measurement or from the estimate influenced by other sensors. It therefore introduces a fault-consensus process and extends it to simultaneous faults.

**Compared claims:** C2, C5, C6.

**Classification:** `partial_prior_art` for heterogeneous cross-sensor consistency and exclusion; `boundary_condition` for interpreting disagreement as candidate unreliability.

### 4.5 Fixed-threshold fault gating has known false-alarm/missed-detection limits

**Work:** Lifeng Wu, Beibei Yao, Zhen Peng & Yong Guan, **“An adaptive threshold algorithm for sensor fault based on the grey theory.”** First published online **2017-02-09**.

- Primary article: https://doi.org/10.1177/1687814017693193

The authors explicitly motivate adaptive thresholds because a fixed threshold ignores system state/noise and can create false alarms or missed faults. Their experiments report lower false-positive rates for an adaptive residual threshold across abrupt, drift, and complete sensor faults.

**Compared claims:** C3, C4, C6.

**Classification:** `prior_art` for adaptive fault-gating thresholds; `boundary_condition` for RUN11’s single threshold calibrated at one fault prevalence and generator.

### 4.6 Reliability/conflict-aware fusion and robust downweighting are established alternatives

Fault-tolerant fusion literature long predates RUN11 in weighting or rejecting measurements based on reliability, residuals, conflict, and robust statistics. A representative earlier line includes robust Kalman/M-estimation and evidence-theoretic sensor reliability, while the GNSS/RAIM lineage uses explicit exclusion after fault detection.

**Compared claims:** C2, C3, C6.

**Classification:** `adjacent_prior_work` / `partial_prior_art`.

**Consequence:** the next learned trust gate must beat not only `always trust`, but at least one statistically calibrated hard gate and one **soft** robust/downweighting baseline. Otherwise the learned/MaleCNS layer has not earned its complexity.

## 5. Falsification and contrary-evidence ledger

### 5.1 RUN11 itself is a boundary condition against universal trust gating

At 0% injected high-confidence faults, the fixed gate is essentially neutral. At 10%, the five-seed mean is slightly **worse** than always-trust. Benefit appears at 20% and grows at 30%.

**Classification:** `boundary_condition`; the 10% condition is a small in-harness null/reversal rather than a failed replication of the 20% claim.

**Strength:** `strong` for the statement “the benefit is fault-regime dependent” inside this generator; `weak-to-moderate` for real sensors.

**Target attacked:** C3/C4 generalization and magnitude.

**Required change:** `no_change` to the existing numerical result; `add_boundary_condition` and retain the explicit non-universality statement.

### 5.2 A fixed threshold is not transportable across arbitrary noise/state regimes

Wu et al. directly show the false-alarm/missed-detection trade-off of fixed thresholds under changing status/noise, and adaptive thresholding improves their sensor-fault tests.

**Classification:** `boundary_condition`.

**Strength:** `strong` against treating `0.12` as a production/default trust constant; `moderate` in transfer to RUN11’s different score.

**Target attacked:** C3/C6 generalization.

**Required change:** `add_control` + `downgrade_confidence`: compare fixed `0.12` against adaptive/statistically calibrated thresholds under fault prevalence, noise, age, and calibration shifts.

### 5.3 Hard exclusion can exclude the wrong source and worsen the estimate

Yang et al. analyze probabilities of correct identification, missed detection, and **wrong exclusion**. Their GNSS experiment shows classical FDE can sometimes identify the wrong measurement and negatively affect position accuracy.

**Classification:** `contrary_evidence` against any assumption that detecting inconsistency makes hard exclusion automatically beneficial; `boundary_condition` for RUN11.

**Strength:** `strong` for the generic decision-theoretic risk; `moderate` for transfer to the specific synthetic gate.

**Target attacked:** C2/C5 mechanism.

**Required change:** `add_control`: report false-rejection/false-acceptance or equivalent admission confusion conditioned on known synthetic fault state, not MAE alone. On real data where fault labels are unavailable, use integrity/consistency proxies and event-centered analysis.

### 5.4 Disagreement does not identify which participant is wrong

Jurado et al. explicitly note that low-likelihood residuals can arise from a faulty measurement **or** a faulty estimated measurement influenced by other sensors. Carlson & Murphy similarly frame conflict as an indicator that the interpretation may be wrong, not a magical ground-truth label for one sensor.

**Classification:** `boundary_condition`.

**Strength:** `strong` for C5’s causal interpretation; does not negate disagreement as a useful feature.

**Target attacked:** mechanism and attribution, not observed RUN11 MAE.

**Required change:** `narrow_claim`: cross-modal disagreement is an evidence feature, not proof that the candidate is faulty. Add leave-one-source-out / competing-hypothesis controls when moving toward real sensors.

### 5.5 Correlated/simultaneous faults can create false consensus

The all-source FDE literature treats simultaneous faults as a separate problem precisely because single-fault assumptions break. Jurado et al. require additional filter layers/consensus structure to identify multiple simultaneous faulty sensors and discuss the growing observability/compute burden.

**Classification:** `boundary_condition`.

**Strength:** `strong` for the need to test modality-correlated failures before deployment; it does not show the current independent-fault experiment is wrong.

**Target attacked:** C5 generalization.

**Required change:** `add_control`: inject correlated camera+IMU/report faults, shared timestamp/calibration bias, and common upstream model errors. If wrong sources agree, the current exponential-disagreement term can assign high trust for the wrong reason.

### 5.6 Legitimate regime changes can look like faults to a consistency gate

A consistency gate compares a new report to an estimate built from past/already-admitted evidence. Under abrupt legitimate state change or model mismatch, the **reference** may be the stale/wrong object. Classical innovation-gating literature treats threshold/model calibration as load-bearing, and fault-diagnosis literature documents false positives under changing dynamics/noise.

**Classification:** `boundary_condition`.

**Strength:** `moderate` here because no direct RUN11 real-transition test exists.

**Target attacked:** C2/C5 generalization.

**Required change:** `add_control`: include abrupt-but-real state transitions and sensor-latency asymmetry, and measure recovery time/update starvation, not only stationary MAE.

### 5.7 Mean MAE is not an integrity guarantee

Fault detection/exclusion literature evaluates missed detection, false alert/wrong exclusion, availability, and protection/integrity metrics in addition to mean estimation error. A small average MAE gain can coexist with unacceptable rare wrong exclusions.

**Classification:** `boundary_condition`.

**Strength:** `strong` for any safety interpretation; `weak` against the narrow synthetic prediction claim.

**Target attacked:** scope of C3, not the reported mean.

**Required change:** `add_control`: report tail error, worst quantiles, false admission/rejection, and fault-conditional risk before using this gate in an actuator-facing safety argument.

## 6. Alternative mechanisms and stronger baselines

Before attributing an advantage to a learned or MaleCNS trust coordinator, compare against simpler explanations and controls:

1. **statistical residual gating:** normalized innovation / residual threshold calibrated to a target false-alarm rate;
2. **adaptive thresholding:** threshold changes with residual/noise/state statistics rather than one global `0.12`;
3. **soft robust weighting:** Huber/M-estimation or reliability inflation/downweighting rather than binary accept/reject;
4. **leave-one-sensor-out consistency:** ask which source restores consistency when excluded, instead of assuming the candidate is the culprit;
5. **fault-prior calibration:** explicitly condition on expected fault prevalence/cost asymmetry;
6. **change-point-aware recovery:** distinguish persistent sensor fault from legitimate system transition;
7. **correlated-fault hypotheses:** allow multiple sources/common upstream components to fail together.

These controls generally make fewer architectural assumptions than a recurrent MaleCNS trust coordinator.

## 7. Current priority boundary

### Not defensible as standalone novelty

The following ideas clearly predate RUN11:

- acquiring a sensor measurement and then deciding whether to accept/exclude it;
- fault detection followed by measurement exclusion;
- validation gates before estimator update;
- using residual/cross-sensor inconsistency without direct ground truth as a fault/interpretation signal;
- reliability/conflict-aware fusion;
- robust outlier rejection/downweighting;
- adaptive fault thresholds;
- multiple-fault consensus/isolation.

### What remains specific to RUN11 after this search

No pre-cutoff source was located that exactly combines all of:

1. the repository’s MaleCNS specialist-colony abstraction;
2. a paid activation whose output can be rejected after compute has already been spent;
3. the exact lawful `SpecialistReport` inputs of declared confidence, freshness, and independent-modality agreement;
4. the exact score `confidence × freshness × exp(-disagreement/0.35)` and calibrated scalar threshold;
5. the fixed 12-specialist budget with equal paid probes under both compared admission policies;
6. the synthetic high-confidence specialist-fault stressor and five-seed 0/10/20/30% fault-prevalence ablation;
7. the explicit no-hidden-truth decision-time contract and planned hurdle before a MaleCNS coordinator.

This is a bounded negative search result, **not** a claim that the authors are first.

The scientifically defensible contribution of RUN11 is therefore the **executed MaleCNS-specific control result**: within this synthetic specialist colony, separating paid acquisition from hard admission can improve mean error once confidently wrong reports are sufficiently prevalent, while the same gate is neutral or slightly harmful at lower fault prevalence.

## 8. Post-cutoff work

The conservative cutoff is **2026-09-19 08:01:19 UTC**. Immediate searches for the exact/decomposed mechanism found no materially overlapping work first released after that instant.

**Result:** no `later_independent`, `later_overlap`, `later_non_citing`, `later_citing`, or `later_derivative` candidate is assigned in this run.

Because the observation window is under one hour, this negative result is intentionally weak.

## 9. Classification ledger

| Work/result | First verified public date | Compared claim | Priority classification | Truth-status relation | Consequence |
|---|---:|---|---|---|---|
| Kline & van Graas, multisensor FDI | 1991-12-01 | C1/C2 | `prior_art` generic | — | measurement acquisition then detection/isolation long predates RUN11 |
| Carlson & Murphy, conflict without ground truth | 2012-07-04 public preprint | C2/C5 | `partial_prior_art` | boundary on attribution | cross-sensor conflict is established but does not identify truth by itself |
| Yang et al., GNSS FDE | 2013-05-17 | C1/C3/C5 | `prior_art` generic | `contrary_evidence` / `boundary_condition` | wrong exclusion and missed detection must be measured |
| Wu et al., adaptive fault threshold | 2017-02-09 | C3/C4/C6 | `prior_art` for adaptive gating | `boundary_condition` | one fixed threshold is regime/noise dependent |
| Jurado et al., all-source FDE | 2020-08-25 | C2/C5/C6 | `partial_prior_art` | `boundary_condition` | disagreement may reflect candidate or reference failure; simultaneous faults need richer isolation |
| RUN11 0–30% ablation | cutoff 2026-09-19 08:01:19 | C3/C4 | n/a | `boundary_condition` | benefit is not universal; 10% condition slightly reverses |

## 10. Required next discriminating test

The existing Findings Record already points in the right direction, but the next test should be strengthened before escalating to a learned/MaleCNS coordinator.

Freeze a generator/data split and compare under identical paid-probe/latency budgets:

1. always admit;
2. current fixed gate;
3. statistically/adaptively calibrated hard gate;
4. soft robust/reliability-weighted admission;
5. learned lawful gate;
6. only after those, a MaleCNS coordinator.

Stress at minimum:

- fault prevalence and fault magnitude shift;
- confidence miscalibration;
- correlated simultaneous faults across modalities;
- common upstream/model/calibration bias;
- abrupt legitimate state transitions;
- stale-reference and asynchronous-latency conditions.

Report not only mean MAE but paired deltas, tail errors, admission fraction, false reject/false accept against synthetic labels, recovery after genuine transitions, and compute/latency.

**Decision rule:** if adaptive/soft robust baselines match the learned gate under the shifted conditions, do not credit the gain to learned trust coordination. If correlated faults or legitimate transitions cause systematic false consensus/rejection, revise the trust mechanism before connecting it to actuator control. Only promote a MaleCNS coordinator if it beats the strongest simpler lawful gate under the same information and compute contract.

## 11. Epistemic update

- **Priority:** materially narrowed. The generic probe/validate/exclude architecture and cross-sensor consistency gating are established prior art.
- **C1:** `narrow_claim` to a project-specific implementation/result, not a generic architecture novelty.
- **C2/C5:** retain as useful features, but `add_boundary_condition`; disagreement is evidence, not fault identity.
- **C3:** `no_change` to the executed five-seed result; `downgrade_confidence` for transport beyond the synthetic generator and `add_control` against adaptive/soft robust baselines.
- **C4:** `no_change` to the executed table; do not generalize monotonic fault-prevalence benefit without shifted fault models.
- **C6:** `add_control`; a learned gate is a reasonable next experiment only after simpler adaptive and robust baselines are included.

No evidence found in this run warrants `abandon_hypothesis`. The strongest update is architectural discipline: RUN11 demonstrates a useful conditional robustness effect, but neither the acquire/accept split nor disagreement-based fault gating is new, and hard admission must now clear a substantially stronger integrity/fault-regime benchmark before a MaleCNS coordinator is scientifically justified.
