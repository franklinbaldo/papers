---
type: "Audit Report"
title: "MaleCNS delayed-corroboration trust — prior-art and falsification audit — 2026-09-19"
description: "Claim-level temporal, novelty, and adversarial validity audit of RUN12 learned specialist trust from delayed corroboration, with explicit source-dependence, label-noise, timing, and stronger-baseline controls."
tags: [malecns, prior-art, falsification, sensor-colony, learned-trust, delayed-supervision, sensor-fusion, truth-discovery, vanet, source-dependence]
timestamp: 2026-09-19T10:00:00Z
---

# MaleCNS delayed-corroboration trust — prior-art and falsification audit — 2026-09-19

> **Status:** claim-specific audit of [`FINDINGS_2026-09-19_RUN12_DELAYED_TRUST.md`](../../experiments/malecns_car_interface/FINDINGS_2026-09-19_RUN12_DELAYED_TRUST.md). This record separates temporal priority from present truth status. It does not establish exhaustive novelty, patent novelty, copying, causal dependence, plagiarism, or misconduct. Negative searches are bounded observations, not proof of absence.

## 1. Claims and explicit falsifiers

### C1 — trust/admission can be learned from delayed independent corroboration without direct hidden-truth labels

RUN12 trains a small logistic trust gate from a label derived after the decision from a later corroborating measurement, rather than handing the learner the latent simulator truth or injected fault flag.

**Would be wrong, materially narrower, or scientifically uninformative if:** the corroborator is effectively a privileged oracle in the harness; realistic corroborator errors are correlated with candidate errors; delayed labels become wrong under state evolution, latency, calibration drift, or shared upstream failures; or a simpler non-learned reliability estimator reaches the same result.

### C2 — report confidence, freshness, within-modality disagreement and cross-modal consistency are sufficient useful features for trust learning

The learned gate uses only already-observed report properties and agreement statistics.

**Would be materially weakened if:** these observables fail to separate healthy/faulty reports under realistic distribution shifts; common-mode errors make wrong sources agree; valid abrupt dynamics look inconsistent; or the reference summaries are themselves wrong.

### C3 — learned delayed trust improves on the fixed RUN11 gate at the nominal 20% specialist-fault regime

Across three camera-age profiles, the five-seed means improve by about 0.63–0.95% MAE versus the fixed gate.

**Would be wrong or practically negligible if:** paired seed-level intervals include zero or a practically trivial region; independent reruns fail to preserve the advantage; or stronger soft/statistical reliability baselines close the gap.

### C4 — learned-gate advantage increases as confidently wrong specialists become more prevalent

RUN12 is worse than the fixed gate at 0%, essentially tied at 10%, and better at 20–30% in the executed generator.

**Would fail to generalize if:** the pattern reverses under different fault magnitudes, calibration errors, sensor quality, class imbalance, time correlation, or real data.

### C5 — a gate trained on independent faults transfers to correlated camera-probe bias

The frozen learned gate improves over the fixed gate when all four extra camera probes receive the same signed bias in 10–50% of episodes.

**Would be materially narrower if:** the gain disappears when the trusted camera summary, another modality, the delayed teacher, a shared clock, or a shared upstream perception model participates in the common-mode failure.

### C6 — peer/V2X trust can be updated from later local physical corroboration

RUN12 proposes that a cheap peer token can gain or lose future influence according to later observations from the receiving car's own lawful sensors.

**Would be wrong as a novelty claim if:** VANET literature already validates peer messages from local physical sensors or subsequent vehicle behavior and already learns/contextualizes trust from such evidence. **Would be unsafe as a mechanism** if colluding/dependent peers or correlated local sensors create false corroboration.

## 2. Temporal reconstruction

### 2.1 Content-bearing commits

PR [#628](https://github.com/franklinbaldo/papers/pull/628) contains the relevant sequence:

- [`b0cc9e16aafd7de36dfe2729dbf143b9e49a3112`](https://github.com/franklinbaldo/papers/commit/b0cc9e16aafd7de36dfe2729dbf143b9e49a3112), Git timestamp **2026-09-19 09:04:06 UTC**, `experiment: add delayed-corrob learned trust gate` — first implementation of the delayed-corroboration learner;
- [`6d799b7d01cef264477073eea200ca1ef7b358e1`](https://github.com/franklinbaldo/papers/commit/6d799b7d01cef264477073eea200ca1ef7b358e1), **09:04:46 UTC**, delayed-trust ablation;
- [`2132763ded1f8872973ceb891afebbd985174a99`](https://github.com/franklinbaldo/papers/commit/2132763ded1f8872973ceb891afebbd985174a99), **09:04:58 UTC**, contract tests;
- [`e62e929cfc6774acd76e61e923344f7b2839cb15`](https://github.com/franklinbaldo/papers/commit/e62e929cfc6774acd76e61e923344f7b2839cb15), **09:08:22 UTC**, `docs: record delayed learned trust results` — first occurrence of the complete C3–C6 numerical/interpretive record.

### 2.2 Conservative public cutoff

GitHub records PR #628 as created at **2026-09-19 09:09:03 UTC**. Commit author timestamps alone do not prove the exact instant a branch became publicly accessible, so this audit uses **2026-09-19 09:09:03 UTC** as the conservative public cutoff for C1–C6.

All material classified below as prior art was public years before that cutoff, so the conservative choice does not affect temporal classification.

**Priority confidence:** `1.0` for public availability by PR creation.

## 3. Search protocol

Sources searched included arXiv, IEEE-indexed bibliographic records, ACM/VANET proceedings, PVLDB, SIGMOD, PMLR/ICML, DBLP, institutional author/research pages, and targeted current web searches. The RUN11 audit was also used as an internal predecessor so established robust-gating literature was not redundantly rediscovered.

Representative overlap queries:

- `delayed corroboration trust sensor fusion learned gate`
- `vehicle trust later corroboration local sensor message verification`
- `VANET alert subsequent behavior trust misbehavior detection`
- `onboard radar verify announced coordinates VANET trust`
- `context aware trust VANET reinforcement learning`
- `truth discovery source reliability without ground truth heterogeneous sources`
- `cross-modal consistency learned reliability sensor fusion`
- `delayed supervision source trust corroboration`

Representative adversarial queries:

- `source dependence false corroboration truth discovery copying`
- `correlated errors majority agreement wrong truth discovery`
- `instance dependent label noise identifiability`
- `noisy teacher labels correlated errors learning reliability`
- `sensor time synchronization delayed corroboration dynamic state`
- `cross modal agreement common mode fault`
- `learned trust gate no benefit stronger baseline`
- `fixed versus learned reliability gate calibration shift`

Immediate post-cutoff searches for `MaleCNS delayed trust`, `delayed corroboration learned trust sensor fusion`, `specialist trust delayed corroboration`, and decomposition variants did not locate a material research work first made public after **09:09:03 UTC**. The observation window is less than one hour and therefore provides only weak negative evidence.

## 4. Pre-cutoff novelty / overlap findings

### 4.1 Local physical sensors were already used to corroborate peer claims in VANETs

**Work:** Gongjun Yan, Gyanesh Choudhary, Michele C. Weigle & Stephan Olariu, **“Providing VANET Security Through Active Position Detection.”** Public conference version **2007-09**; expanded *Computer Communications* article 31(12), 2008.

- Conference record: https://doi.org/10.1145/1287748.1287762
- Journal DOI: https://doi.org/10.1016/j.comcom.2008.01.009

The system uses onboard radar to detect neighboring vehicles, compare those physical observations with neighbors' announced coordinates, filter forged reports, and maintain movement history.

**Compared claims:** C2, C6.

**Classification:** `prior_art` for the generic principle “peer message is checked against an independent local physical sensor”; `adjacent_prior_work` for RUN12's learned specialist-admission implementation.

**Consequence:** local physical corroboration of communicated claims is not a RUN12 novelty boundary.

### 4.2 Post-message behavior as later verification predates RUN12 by fifteen years

**Work:** Sushmita Ruj, Marcos Antonio Cavenaghi, Zhen Huang, Amiya Nayak & Ivan Stojmenovic, **“Data-centric Misbehavior Detection in VANETs.”** arXiv v1 **2011-03-12**; VTC Fall 2011.

- Primary preprint: https://arxiv.org/abs/1103.2404

The authors explicitly propose detecting false alert messages and misbehaving nodes **by observing their actions after sending the alert messages**. Each receiver assesses correctness from consistency between recent/new messages and reported/estimated positions, without majority voting.

**Compared claims:** C1, C6.

**Classification:** `prior_art` for the general delayed-consequence/post-event-verification loop; `partial_prior_art` for learning a persistent trust/admission function from that delayed evidence.

**Consequence:** the RUN12 peer-token example is a modern instantiation of an established data-centric verification pattern, not a new principle.

### 4.3 Trust and truth can be jointly inferred without an external oracle

**Work:** Xiaoxin Yin, Jiawei Han & Philip S. Yu, **“Truth Discovery with Multiple Conflicting Information Providers on the Web.”** KDD 2007 / IEEE TKDE 20(6), 2008.

- DOI: https://doi.org/10.1109/TKDE.2007.190745

TruthFinder iteratively infers source trustworthiness and information correctness from one another when conflicting providers exist and true facts are not supplied as labels.

**Compared claims:** C1, C2.

**Classification:** `prior_art` for generic ground-truth-free source-reliability inference from corroboration/conflict; `adjacent_prior_work` for sensor timing and candidate-admission decisions.

### 4.4 Heterogeneous-source reliability without supervision is established prior work

**Work:** Qi Li, Yaliang Li, Jing Gao, Bo Zhao, Wei Fan & Jiawei Han, **“Resolving Conflicts in Heterogeneous Data by Truth Discovery and Source Reliability Estimation.”** SIGMOD **2014-06**.

- DOI: https://doi.org/10.1145/2588555.2610509
- Author-hosted paper: https://cse.buffalo.edu/~jing/doc/sigmod14_crh.pdf

The paper states that no oracle tells which source is reliable or which observation is correct and jointly estimates truths and source reliability across heterogeneous data types.

**Compared claims:** C1, C2.

**Classification:** `partial_prior_art` for heterogeneous, no-oracle reliability learning; the sequential delayed-physical-teacher contract is different.

### 4.5 Context-aware learned vehicle trust already existed before RUN12

**Work:** Jingjing Guo et al., **“TROVE: A Context-Awareness Trust Model for VANETs Using Reinforcement Learning.”** First published online **2020-02-19**, *IEEE Internet of Things Journal* 7(7):6647–6662.

- DOI: https://doi.org/10.1109/JIOT.2020.2975084

TROVE learns/adapts the trust-evaluation strategy to driving context with reinforcement learning in the presence of false information from malicious vehicles or defective sensors.

**Compared claims:** C2, C6.

**Classification:** `prior_art` for the generic idea of learned/context-adaptive vehicle trust; `partial_prior_art` for RUN12's particular delayed sensor-derived supervisory signal.

### 4.6 Incremental boundary inherited from RUN11

The predecessor audit [`malecns-probe-trust-2026-09-19.md`](./malecns-probe-trust-2026-09-19.md) already established that measurement validation/exclusion, cross-sensor conflict, adaptive thresholds, and robust soft weighting predate RUN11/RUN12. Its soft-gating revision further requires a continuous robust-fusion baseline before crediting learned/MaleCNS trust reasoning.

**Compared claims:** C2, C3.

**Classification:** inherited `prior_art` / `partial_prior_art`; not repeated here as a new discovery.

## 5. Falsification and contrary-evidence ledger

### 5.1 The current “physical teacher” is still generated directly from latent synthetic truth

In `colony_delayed_trust_ablation.py`, the corroborator is generated as the same latent synthetic `truth` plus independent Gaussian noise. The learner never receives the latent truth value directly, which correctly preserves the decision/training interface boundary; however, the **teacher-generation mechanism itself has privileged access to truth**.

This matters because a real IMU, camera, OBD, GNSS, ultrasonic or RF channel is not an unbiased oracle-plus-i.i.d.-noise transformation of the same latent scalar. It has calibration errors, latency, heteroscedasticity, shared upstream causes and potentially distinct observability.

**Classification:** `boundary_condition`.

**Strength:** `strong` against the interpretation that RUN12 already demonstrates real physical cross-confirmation as a trustworthy teacher; it does **not** invalidate the executed synthetic MAE table.

**Target attacked:** C1 mechanism/generalization.

**Required change:** `narrow_claim` + `add_boundary_condition` + `add_control`. Describe the current result as an idealized synthetic delayed-corroborator proof of concept until a real independently measured channel pair replaces the oracle-generated proxy.

### 5.2 “Delayed” currently means sequencing, not physical state evolution across delay

The delayed corroborator is sampled from the same episode truth. The harness therefore does not yet model a car whose yaw/speed/range changes between the candidate measurement and the later corroborating measurement. A real delayed teacher needs temporal registration or a dynamical model before disagreement can be interpreted as candidate error.

**Classification:** `boundary_condition`.

**Strength:** `strong` for any latency/real-time interpretation; `no_change` to the static synthetic experiment.

**Target attacked:** C1/C6 mechanism and deployment generalization.

**Required change:** `add_control`: explicitly simulate state evolution, timestamp offsets, latency distributions, interpolation/propagation uncertainty, and a held-out real aligned sensor pair.

### 5.3 Corroboration is unsafe when sources are dependent

**Work:** Xin Luna Dong, Laure Berti-Équille & Divesh Srivastava, **“Integrating Conflicting Data: The Role of Source Dependence.”** PVLDB 2(1), **2009-08**.

- DOI: https://doi.org/10.14778/1687627.1687690

The paper shows why repeated agreement is not independent evidence: a false value can spread through source dependence/copying, making naive majority/corroboration misleading. Explicit dependence modeling materially improves truth discovery.

RUN12's correlated-camera stress is useful but does **not** stress the delayed teacher: the extra camera probes receive a common bias while the corroborator remains an independent `truth + Gaussian noise` channel. It also does not corrupt the trusted reference summaries simultaneously.

**Classification:** `contrary_evidence` against treating corroboration as self-authenticating; `boundary_condition` for RUN12's current stress result.

**Strength:** `strong` for the independence assumption, `moderate` for transfer to the exact synthetic gate.

**Target attacked:** C2, C5, C6 mechanism/generalization.

**Required change:** `add_control`: include shared candidate+teacher bias, trusted-base+candidate bias, shared clock/calibration error, common upstream perception-model error, and colluding/dependent peer reports.

### 5.4 Real proxy labels are likely instance-dependent, not i.i.d. Gaussian noise

**Works:**

- Keren Gu et al., **“An instance-dependent simulation framework for learning with label noise.”** *Machine Learning*, first online **2022-06-27**, https://doi.org/10.1007/s10994-022-06207-7.
- Antonin Berthon et al., **“Confidence Scores Make Instance-dependent Label-noise Learning Possible.”** ICML 2021, https://proceedings.mlr.press/v139/berthon21a.html.

The noisy-label literature documents that real annotation/proxy errors commonly depend on the instance and that learning under general instance-dependent noise needs assumptions or additional information. Gu et al. specifically show that simple independent random label corruption is a poor stand-in for practical noisy labels.

For RUN12, the binary teacher label is a thresholded noisy corroborator. Its errors can become instance-dependent under fast maneuvers, low visibility, GNSS multipath, wheel slip, sensor saturation, packet delay or calibration drift.

**Classification:** `boundary_condition`; not a direct failed replication.

**Strength:** `moderate-to-strong` for the training-mechanism assumption.

**Target attacked:** C1/C2 generalization.

**Required change:** `add_control` + `downgrade_confidence`: sweep biased, heteroscedastic and feature-dependent teacher noise; report label calibration/quality; and avoid treating one low-noise Gaussian corroborator as representative of deployment supervision.

### 5.5 RUN12 itself falsifies universal superiority of the learned gate

At 0% injected specialist faults, the learned gate is about **0.46% worse** than the fixed RUN11 gate. At 10%, the difference is essentially zero. The learned advantage emerges at 20–30% faults.

**Classification:** `boundary_condition`; the 10% condition is effectively an in-harness null and the 0% condition is a small reversal.

**Strength:** `strong` for the statement “benefit is fault-regime dependent” within this generator; `weak-to-moderate` for real sensors.

**Target attacked:** C3/C4 magnitude/generalization.

**Required change:** `no_change` to the executed numbers; `downgrade_confidence` for universal/general benefit. Preserve the fault-regime qualification.

### 5.6 The nominal improvement over the fixed gate is small enough that paired uncertainty should be primary

The nominal gains are 0.63–0.95%, while the report gives across-seed standard deviations for each method but no paired seed-level confidence interval for the **difference**. Because policies are evaluated on matched streams, paired deltas are the appropriate uncertainty object.

**Classification:** `boundary_condition`.

**Strength:** `moderate`; this is not evidence the effect is absent, but it limits confidence in its magnitude.

**Target attacked:** C3 magnitude.

**Required change:** `add_control`: report per-seed paired deltas, confidence intervals/bootstrap intervals, and a predeclared practical-equivalence margin. If the interval overlaps a negligible-effect region, describe the fixed and learned gates as practically tied for that profile.

### 5.7 Stronger simpler alternatives remain live explanations

Truth-discovery/source-reliability methods, adaptive statistical thresholds, and the soft robust-fusion baseline required by the RUN11 audit can all exploit consistency/reliability without a learned trust classifier of RUN12's form.

**Classification:** alternative mechanism / `boundary_condition`.

**Strength:** `strong` for experimental design, not for falsifying RUN12's current comparison.

**Target attacked:** C3's attribution of value to learned trust rather than to generic reliability estimation.

**Required change:** `add_control`: at minimum compare against (a) calibrated adaptive hard gating, (b) soft robust/reliability weighting, and (c) a simple online source-reliability/truth-discovery-style updater under identical observables and compute.

## 6. Priority and truth-status summary

| claim | priority status after search | present truth status | required change |
|---|---|---|---|
| C1 delayed corroboration can supervise trust without direct truth labels | `partial_prior_art` / generic principle predated | plausible in idealized harness; real-teacher validity unproven | `narrow_claim`, `add_boundary_condition`, `add_control` |
| C2 observed consistency/freshness features can learn trust | `partial_prior_art` | supported only in current generator; dependence/teacher quality are load-bearing | `add_control`, `downgrade_confidence` |
| C3 learned gate beats fixed gate at 20% faults | experiment-specific result | supported by five-seed means; effect small and paired CI absent | `no_change`, `add_control` |
| C4 advantage grows with fault prevalence | experiment-specific result | true for executed 0–30% sweep, not universal | `add_boundary_condition` |
| C5 transfer to correlated camera fault | experiment-specific result | encouraging but teacher/base independence remains privileged | `narrow_claim`, `add_control` |
| C6 peer trust updated from later local corroboration | `prior_art` as generic VANET principle | plausible, but dependence/collusion/local-sensor faults matter | `narrow_claim`, `add_control` |

## 7. Discriminating next experiment

A meaningful RUN13/real-data continuation should freeze the current logistic gate and evaluate a **teacher-quality ladder** under the same 12-specialist budget and observables:

1. current independent Gaussian corroborator (anchor);
2. biased corroborator;
3. heteroscedastic/feature-dependent corroborator;
4. candidate and corroborator sharing a common bias;
5. trusted reference and candidate sharing a common bias;
6. shared timestamp/clock drift;
7. actual state evolution between candidate and delayed teacher;
8. missing/late corroboration;
9. a real timestamp-aligned camera–IMU or OBD–GNSS slice.

Matched baselines should include `always trust`, RUN11 fixed hard gate, adaptive hard gate, soft robust/reliability-weighted fusion, and a simple online source-reliability updater. Report paired MAE deltas and intervals, false-admit/false-reject rates where synthetic fault labels exist, trust calibration/Brier score, time-to-recovery after regime shifts, and performance conditioned on teacher failure mode.

**Predeclared falsifier:** if the learned gate loses its advantage once the corroborator has realistic feature-dependent/correlated error, or a simpler reliability updater/soft robust gate matches it within a practical-equivalence margin, do not attribute added value to learned delayed trust. Retain the architecture only as a convenient interface for later lawful supervision.

## 8. Bounded negative findings

No pre-cutoff work located in the searched sources contained the **full** RUN12 conjunction of MaleCNS specialist reports + fixed 12-specialist matched budget + this exact 11-feature vector + thresholded delayed corroborator label + disjoint corroboration-based threshold calibration + five-seed age/fault sweeps + the reported correlated-extra-camera stress result.

This is only a bounded negative search result. It does not justify “first” language. The components — physical corroboration, later-behavior verification, source-reliability inference without ground truth, context-aware learned vehicle trust, robust sensor gating, and dependence-aware truth discovery — all have substantial prior lineages.
