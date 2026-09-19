---
type: "Audit Report"
title: "MaleCNS Run22 common-mode active tie-break — prior-art and falsification audit — 2026-09-19"
description: "Claim-level temporal, novelty, and adversarial truth-status audit of Run22's conflict-triggered auxiliary sensor acquisition for OBD/GNSS common-mode disagreement."
tags: [malecns, prior-art, falsification, driving, sensor-fusion, active-sensing, value-of-information, fault-detection, common-mode, lidar, camera]
timestamp: 2026-09-19T19:59:13Z
---

# MaleCNS Run22 common-mode active tie-break — prior-art and falsification audit — 2026-09-19

> **Status:** claim-specific audit of [`FINDINGS_2026-09-19_RUN22_COMMON_MODE_ACTIVE_TIEBREAK.md`](../../experiments/malecns_car_interface/FINDINGS_2026-09-19_RUN22_COMMON_MODE_ACTIVE_TIEBREAK.md). Priority and present truth status are separate axes. This audit does not establish exhaustive novelty, patent novelty, copying, causal dependence, plagiarism, or misconduct. Negative searches are bounded observations.

## 1. Claims and explicit falsifiers

### C1 — persistent disagreement between an agreeing OBD/GNSS pair and camera ego-speed is useful as a conflict signal

Run22 treats the pattern `OBD≈GNSS`, `pair≠camera`, persistent with stable sign, as evidence of unresolved cross-modal conflict rather than proof that either side is correct.

**Falsifier / narrowing condition:** on held-out or real data the same pattern is produced as often by camera failure, calibration drift, road geometry, scale error, or timing error as by OBD/GNSS common-mode error; a conventional residual/integrity model dominates the detector at equal false-alarm rate; or the conflict score adds no predictive value for downstream control.

### C2 — after unresolved conflict, requesting an additional physical observation can improve estimation while avoiding always-on sensing

Run22 requests LiDAR ego-speed only after persistent conflict and compares against both pair-only and naive always-three-sensor fusion.

**Falsifier / narrowing condition:** after measuring real latency/energy/compute cost, always-on sensing or a fixed periodic schedule has equal or better utility; a passive wait/retry policy matches performance; the request policy activates mainly on false conflicts; or auxiliary acquisition arrives too late to affect the control decision.

### C3 — an auxiliary LiDAR witness can disambiguate some OBD/GNSS common-mode failures

In the frozen synthetic harness, healthy LiDAR frequently sides with the healthy camera under injected shared OBD/GNSS bias and sharply reduces MAE.

**Falsifier / narrowing condition:** the LiDAR channel shares the relevant common cause, calibration, timebase, software, environmental degradation, or model error; a corrupted auxiliary channel reverses the arbitration; or a real synchronized slice does not preserve the synthetic ordering.

### C4 — the Run22 policy is a useful ordinary baseline for a future MaleCNS information-acquisition controller

The intended scientific role is comparative: MaleCNS should receive credit for active sensing only if it beats a conventional policy under equal information and cost budgets.

**Falsifier / narrowing condition:** a standard active-diagnosis, POMDP sensor-selection, event-triggered sensing, or cost-sensitive feature-acquisition policy matches or exceeds MaleCNS; the fixed Run22 policy is too weak to constitute a meaningful comparator; or the MaleCNS gain disappears after matching request budgets and latency.

### C5 — the auxiliary sensor is sufficiently independent to function as a tie-break

The current generator models camera and LiDAR errors separately. Physical modality diversity is not itself proof of statistical or common-cause independence.

**Falsifier / narrowing condition:** camera and LiDAR share timing, pose/extrinsic calibration, scene observability, compute, power, mounting, weather, or downstream ego-motion code; correlated error causes both auxiliary channels to support the same wrong hypothesis.

### C6 — the current persistence and decision thresholds are stable enough to support the reported mechanism

Run22 uses an 8-sample window, 6 supporting samples, 0.90 m/s pair and camera gates, and a 0.15 m/s LiDAR decision margin. The findings correctly state that these were heuristic and not held-out calibrated.

**Falsifier / narrowing condition:** modest threshold perturbations reverse method ordering; a held-out ROC/utility calibration chooses materially different thresholds; performance depends strongly on speed, acceleration, road surface, sensor rate, or noise regime; or the reported gains shrink after selection-bias control.

### C7 — the phrase “value-of-information primitive” should be interpreted narrowly

Run22 performs selective information acquisition, but its current policy does not explicitly estimate expected posterior utility minus sensing cost.

**Falsifier / narrowing condition:** if the phrase is read as a formal decision-theoretic VOI algorithm, the current implementation fails that definition because request cost is not an optimization term and physical cost is represented only by request rate.

## 2. Temporal reconstruction

Run21 / PR [#703](https://github.com/franklinbaldo/papers/pull/703), created **2026-09-19 18:08:46 UTC**, had already proposed exposing `clock-witness conflict` to an active controller and listed possible follow-up observations. That is an earlier internal disclosure of the broad “conflict may justify buying another observation” direction, but not of the Run22 common-mode detector or camera→LiDAR arbitration rule.

For the Run22-specific claim set:

- `a1ec9a4d773076fbb217d01e24e04fc6b05d4997`, author/committer timestamp **2026-09-19 19:05:14 UTC** — first located commit containing the active common-mode tie-break primitive;
- `eb3253192e2456564e3d3cba672aaf5df5c85f8d`, **19:05:25 UTC** — tests;
- `e76d0b9b53543c0ef6b55cf63134d53f611a969d`, **19:05:48 UTC** — common-mode active-witness ablation;
- `a663dc0b23b4d1b42507638365f9487237f2cad9`, **19:06:16 UTC** — findings record;
- PR [#707](https://github.com/franklinbaldo/papers/pull/707) was created **2026-09-19 19:06:37 UTC** and merged **19:08:27 UTC**;
- squash merge commit: `b8eb03163a55aaaebb5ae408eb06818c9c6fa8c8`.

A local commit timestamp does not by itself prove that a branch was publicly discoverable at that instant. The conservative public cutoff for C1–C7 is therefore **2026-09-19 19:06:37 UTC**, the creation time of PR #707.

## 3. Search protocol

Sources were sought through arXiv, DOI/publisher pages, IEEE-visible literature, PubMed, fault-diagnosis and navigation literature, autonomous-driving perception/fault-tolerance literature, and GitHub history.

Representative overlap queries:

- `active diagnosis sensor selection value of information fault identification`
- `dynamic sensor selection POMDP sensor cost`
- `sensor scheduling fault isolation bandwidth`
- `event-triggered fault detection isolation sensor`
- `autonomous vehicle multi sensor fault detection camera lidar`
- `fault tolerant sensor fusion autonomous driving camera lidar`
- `common mode sensor redundancy fault isolation`
- `costly feature acquisition reinforcement learning sensor request`

Representative adversarial queries:

- `common cause failure defeats redundancy sensor`
- `multiple sensor fault isolability identifiability`
- `correlated sensor errors fusion independence assumption`
- `camera lidar simultaneous sensor faults autonomous driving`
- `active sensor selection no benefit cost latency`
- `event triggered sensing false alarms threshold calibration`
- `sensor fusion auxiliary sensor wrong fault isolation`

Post-cutoff searches used the exact Run22 title and decompositions around `common-mode active tie-break`, `false consensus sensor fusion`, `active tie-break sensor vehicle`, `request LiDAR uncertainty`, and OBD/GNSS/camera/LiDAR conflict. The post-cutoff window is under one hour, so a negative result carries little evidentiary weight.

## 4. Pre-cutoff novelty / overlap

### 4.1 Active diagnosis by deliberately choosing the next noisy observation is established prior art

**Gowtham Bellala, Jason Stanley, Clayton Scott & Suresh K. Bhavnani, “Active Diagnosis via AUC Maximization: An Efficient Approach for Multiple Fault Identification in Large Scale, Noisy Networks.”** arXiv v1 **2012-02-14**. https://arxiv.org/abs/1202.3701

The task is explicitly to identify faults by sequentially selecting noisy diagnostic queries. The particular AUC objective is not Run22's method, but the core abstraction “uncertainty about a fault state can justify buying/selecting another observation” predates Run22 by more than a decade.

**Classification:** `prior_art` for generic C2/C4 active diagnostic acquisition; `adjacent_prior_work` for the exact vehicle-sensor policy.

### 4.2 Dynamic sensor selection under resource cost is established prior art

**Yash Satsangi, Shimon Whiteson & Frans Oliehoek, “Exploiting Submodular Value Functions for Faster Dynamic Sensor Selection.”** AAAI 2015. DOI: https://doi.org/10.1609/aaai.v29i1.9666

The paper formulates dynamic sensor selection as a POMDP in which a subset of sensors must be selected because bandwidth, CPU, or energy are scarce. It explicitly optimizes the estimation/value trade-off and provides approximation guarantees under submodularity conditions.

**Classification:** `prior_art` for the generic C2/C4 notion of selective sensing under resource cost; `partial_prior_art` for Run22's proposed future controller that chooses which physical information to buy.

### 4.3 Sensor scheduling has been designed jointly with fault isolation

**M. A. Sid, “Sensor scheduling strategies for fault isolation in networked control system.”** *ISA Transactions*. DOI: https://doi.org/10.1016/j.isatra.2014.07.005

The work jointly designs a fault-isolation filter and sensor scheduling under limited bandwidth, including strategies intended to improve fault isolability and robustness to packet dropouts.

**Classification:** `prior_art` for scheduling observations specifically to support fault isolation; compared claims C2/C4/C6.

### 4.4 Event-triggered fault detection/isolation predates Run22

**Shahram Hajshirmohamadi, Mohammadreza Davoodi, Nader Meskin & Farid Sheikholeslam, “Event-triggered fault detection and isolation for discrete-time linear systems.”** First published **2016-03-01**. DOI: https://doi.org/10.1049/iet-cta.2015.0762

This establishes the general idea that fault-diagnosis sensing/communication need not run continuously: an event condition can govern when information is transmitted/processed.

**Classification:** `partial_prior_art` for C2; the exact trigger and physical-sensor arbitration are different.

### 4.5 All-source fault detection already treats sensor/model mismatch and fault isolation as a structured inference problem

**Juan Jurado, John Raquet, Christine M. Schubert Kabban & Jonathon Gipson, “Residual-based multi-filter methodology for all-source fault detection, exclusion, and performance monitoring.”** First published **2020-08-25**. DOI: https://doi.org/10.1002/navi.384

The paper explicitly addresses heterogeneous, asynchronous all-source navigation sensors and notes that adding sensors also adds opportunities for model error, interference, and undetected faults. Its culprit-identification logic relies on structural assumptions including, in the analyzed case, at most one failed sensor so that at least one leave-one-out filter remains unaffected.

**Classification:** `prior_art` for conventional multi-sensor consistency/FDE; `boundary_condition` for C3/C5 because isolability depends on fault-structure assumptions.

### 4.6 Adaptive routing among camera/LiDAR experts under sensor failure predates Run22

**Konyul Park et al., “Resilient Sensor Fusion under Adverse Sensor Failures via Multi-Modal Expert Fusion.”** arXiv v1 **2025-03-25**. https://arxiv.org/abs/2503.19776

MoME uses separate camera, LiDAR, and fused experts and an adaptive query router to select which expert handles a query based on modality quality. This does not purchase a sensor observation on demand, but it directly occupies the space of quality-aware modality routing under camera/LiDAR failures.

**Classification:** `adjacent_prior_work` for C2/C4 and a stronger conventional comparator for future MaleCNS modality arbitration.

### 4.7 Autonomous-driving fusion has documented severe failures under camera/LiDAR faults

**Haoxiang Tian et al., “Testing the Fault-Tolerance of Multi-Sensor Fusion Perception in Autonomous Driving Systems.”** arXiv v1 **2025-04-18**. https://arxiv.org/abs/2504.13420

FADE systematically injects camera and LiDAR fault models into Baidu Apollo and validates some findings on a physical Apollo vehicle. Its result is directly relevant to Run22's current synthetic boundary: multimodal redundancy does not automatically imply system-level fault tolerance.

**Classification:** `adjacent_prior_work`; `boundary_condition` for C3/C5 and for generalizing synthetic scalar ego-speed results to a real perception stack. Strength: **moderate-to-strong**.

### 4.8 Common-cause failure is a known hard limit on redundancy

**Harry W. Jones, “Common Cause Failures Dominate and Defeat Redundancy.”** NASA Ames / RAMS 2025; DOI: https://doi.org/10.1109/RAMS48127.2025.10935209; NASA record: https://ntrs.nasa.gov/citations/20240013667

The central result is directly relevant: redundancy improves reliability primarily when failures are sufficiently independent; common-cause failures place a floor on the benefit of adding redundant components. The paper recommends diversity, separation, and avoidance of shared control/power/location, while noting that shared vulnerabilities can remain.

**Classification:** `boundary_condition` for C3/C5, strength **strong**.

### Novelty boundary after the search

The bounded search did **not locate** a pre-cutoff publication with the exact Run22 conjunction:

`matched-time OBD/GNSS pair agreement + persistent signed disagreement with phone-camera ego-speed → conflict flag, not diagnosis → conditionally request a low-cost LiDAR ego-speed witness → arbitrate between pair and camera by relative LiDAR support → expose conflict/support/cost to a future frozen-connectome driving controller`.

That exact conjunction is narrower than the established prior work. However, its main conceptual ingredients — active diagnosis, dynamic sensor selection under cost, event-triggered measurement use, fault-isolation scheduling, heterogeneous sensor FDE, and quality-aware multimodal routing — are all pre-cutoff prior art. This is a negative search result, **not** a claim that the exact conjunction is first.

## 5. Falsification / contrary-evidence ledger

### 5.1 Run22 itself falsifies the broad claim that “one more sensor resolves the disagreement”

When OBD/GNSS are healthy but the camera is biased, the detector requests LiDAR on **77.44%** of steps. Even with healthy LiDAR, active MAE is `0.202737` versus pair-only `0.192639`, **5.24% worse**. With ±6% camera scale error, the penalty is **2.67%**.

When OBD/GNSS share static bias but LiDAR is biased, active MAE is `1.210898`: **24.20% better** than the faulty pair, but **13.81% worse** than naive three-way fusion, and side-selection accuracy falls to about **54%**.

**Classification:** `contrary_evidence`, strength **strong**, against any broad statement that an extra witness identifies the faulty side. `boundary_condition`, strength **strong**, for the narrower statement that the current policy helps when the modeled auxiliary witnesses are healthy enough.

**Target attacked:** mechanism/identifiability and generalization, not the frozen healthy-witness MAE table.

**Required action:** `narrow_claim + add_boundary_condition`. Preserve “conflict, not diagnosis” and do not promote LiDAR or camera to privileged truth.

### 5.2 “Independent LiDAR witness” is currently a generator property, not an established real-world property

The harness gives camera and LiDAR separately generated scalar error processes. A real vehicle can couple modalities through timestamping, extrinsic calibration, mounting motion, weather, occlusion, shared compute, shared power, ego-motion software, or an upstream state estimate. Jones's common-cause analysis makes the underlying point formal at the reliability level: redundant channels cannot be treated as independent merely because there are more of them.

**Classification:** `boundary_condition`, strength **strong**.

**Target attacked:** premise/causal interpretation.

**Required action:** `narrow_claim + add_control`. In prose, read “independent” as **independently generated in this synthetic harness** until a real failure-dependency matrix or empirical residual-correlation analysis supports more. Stress correlated auxiliary faults and shared calibration/timebase faults.

### 5.3 The current method is selective acquisition, but not yet a formal value-of-information optimizer

A decision-theoretic VOI policy compares expected downstream utility after an observation against its acquisition cost. Run22 uses a conflict trigger and reports request rate; it does not put energy, latency, compute, wear, monetary cost, or expected posterior error reduction into the decision objective. Satsangi et al. and the broader dynamic-sensor-selection literature are therefore not merely background: they define a stronger comparator.

**Classification:** `boundary_condition`, strength **strong**, for C7; `contrary_evidence`, strength **moderate**, only against a literal reading that the current hand-written rule computes VOI.

**Target attacked:** terminology/mechanism, not empirical performance.

**Required action:** `narrow_claim + add_control`. Prefer “active information-acquisition baseline” or “VOI-motivated primitive” for Run22. Before claiming VOI advantage, predeclare a utility such as `driving loss + λ_energy*energy + λ_latency*latency + λ_requests*requests` and compare to POMDP/greedy/event-triggered baselines under the same budget.

### 5.4 A single active tie-break does not solve multiple-fault identifiability

Jurado et al.'s multi-filter identification argument illustrates the structural issue: culprit identification requires assumptions that leave at least one unaffected hypothesis/filter. Run22's own biased-camera and biased-LiDAR cases expose the same limit empirically. If OBD/GNSS, camera, and LiDAR can fail simultaneously or share a common cause, relative agreement alone may not identify truth.

**Classification:** `boundary_condition`, strength **strong**.

**Target attacked:** identifiability/generalization.

**Required action:** `add_boundary_condition + add_control`. Include simultaneous/correlated fault families and allow explicit abstention. A future controller should be rewarded for refusing to diagnose when evidence is non-identifying.

### 5.5 Heuristic thresholds have not earned an integrity interpretation

Run22 correctly says its thresholds were chosen heuristically before the final run and were not calibrated on an independent set. The reported 0% clean request rate is encouraging for this generator, but it is not a bound on false alarm under distribution shift.

**Classification:** `boundary_condition`, strength **moderate**.

**Target attacked:** magnitude/generalization.

**Required action:** `add_control + downgrade_confidence` for threshold-level claims. Freeze a development/calibration split, report ROC/precision-recall or cost curves, and test threshold sensitivity across sensor-rate/noise/dynamics regimes.

### 5.6 Synthetic scalar witnesses are materially easier than real visual/LiDAR ego-motion

FADE demonstrates that sensor faults propagate through a real ADS stack and can produce system-level failures; Park et al. likewise treats severe modality degradation inside learned perception rather than as a scalar additive-noise channel. Run22's camera/LiDAR inputs bypass feature tracking, scene degeneracy, calibration, correspondence, occlusion, weather, and estimator failure.

**Classification:** `boundary_condition`, strength **strong**, for external validity.

**Target attacked:** generalization, not the synthetic comparison.

**Required action:** `add_control + downgrade_confidence`. The next evidentiary step is at least one checksum/version-pinned real synchronized slice with an actual camera or LiDAR ego-motion pipeline, exactly as the findings already propose.

### 5.7 A future MaleCNS active-sensing result needs stronger baselines than the Run22 rule alone

Bellala-style active diagnosis, Satsangi-style dynamic sensor selection, event-triggered FDI, and modern quality-aware modality routing all predate the MaleCNS proposal. A MaleCNS policy beating only a hand-written threshold policy would therefore establish improvement over that baseline, not a special connectome advantage.

**Classification:** `boundary_condition`, strength **strong**, for C4.

**Target attacked:** mechanism/special advantage.

**Required action:** `add_control`. At equal sensing budget compare at least:

1. fixed always-on acquisition;
2. fixed periodic acquisition;
3. conflict-threshold Run22 policy;
4. greedy expected-error-reduction / VOI policy;
5. small POMDP or contextual-bandit sensor-selection baseline;
6. matched-capacity MLP/RNN controller;
7. frozen MaleCNS controller;
8. degree-preserving rewired MaleCNS controls when moving to confirmatory connectome claims.

## 6. Alternative explanations favored by the evidence

### A1 — Run22 gains come from fault-family specialization, not from a general information-acquisition principle

The detector is constructed around a specific observable signature: OBD and GNSS agree while camera disagrees. The excellent shared-bias results and zero benefit on one-sensor faults are exactly what that specialization predicts.

**Discriminating test:** expand the generator to unlabeled mixtures of fault families and score a single frozen policy without giving it family-specific gates.

### A2 — modality diversity helps because it changes failure correlation, not because LiDAR is intrinsically more truthful

The healthy-witness gains can be explained by lower error correlation between the auxiliary channel and the common-mode pair. That is a simpler explanation than assigning semantic privilege to LiDAR.

**Discriminating test:** match marginal noise while sweeping cross-channel correlation and shared calibration/timebase faults. Plot gain against empirical residual correlation, not sensor name.

### A3 — the benefit is event-triggered resource allocation, a classical control/sensing effect

Requesting expensive information only when a cheap detector says it may matter is already expected from event-triggered sensing and dynamic sensor-selection theory.

**Discriminating test:** compare Run22 to a generic cost-aware trigger that has the same observable state but no domain-specific hand-crafted pair/camera logic.

### A4 — future MaleCNS benefit may come from learning nonlinear request timing rather than connectome-specific structure

If a learned controller beats the fixed rule, that could be due to generic function approximation or memory.

**Discriminating test:** compare frozen MaleCNS against matched trainable MLP/RNN/reservoir and degree-preserving rewired connectome under identical adapters, seeds, observations, reward, and request budget.

## 7. Priority and truth-status summary

| Claim | Priority result | Truth status after this audit | Required action |
|---|---|---|---|
| C1 persistent pair-vs-camera conflict is informative | exact detector not located; residual/consistency FDI is established | useful in tested family; non-identifying in general | `add_boundary_condition` |
| C2 conflict-triggered auxiliary acquisition can save resources | generic active diagnosis, event-triggering and sensor scheduling are `prior_art` | plausible; physical cost not yet measured | `narrow_claim + add_control` |
| C3 LiDAR can arbitrate common-mode pair faults | multimodal fault-aware fusion is established; exact arbitration not located | supported only when auxiliary witness is healthy/sufficiently independent | `add_boundary_condition + downgrade_confidence` |
| C4 Run22 is a baseline for MaleCNS active sensing | generic active/costly sensing is `prior_art` | good baseline, but not strong enough alone for connectome advantage | `add_control` |
| C5 LiDAR is independent | no novelty claim | not established outside generator | `narrow_claim + add_control` |
| C6 heuristic thresholds are stable | no novelty claim | uncalibrated outside frozen generator | `add_control + downgrade_confidence` |
| C7 Run22 is a “VOI primitive” | formal VOI/dynamic sensor selection is `prior_art` | selective-acquisition claim survives; literal VOI interpretation is too strong | `narrow_claim` |

## 8. Posterior work / dependency axis

Post-cutoff searches covered the exact Run22 title and decompositions around common-mode tie-break, false sensor consensus, conflict-triggered LiDAR acquisition, and OBD/GNSS/camera/LiDAR arbitration.

No materially overlapping external work with a first public date after **2026-09-19 19:06:37 UTC** was located in the sub-hour search window. No `later_independent`, `later_overlap`, `later_non_citing`, `later_citing`, or `later_derivative` classification is assigned on that basis. This negative result is weak because the window is extremely short.

Repository activity after PR #707 in the inspected interval concerns publication-readiness edits to unrelated legal papers; no internal Run23-like derivative was located at audit time.

## 9. Practical consequence for the MaleCNS car program

This audit does **not** recommend adding more preconditions before trying to drive with MaleCNS. Run22 belongs in the comparator/remediation library, not in a mandatory pre-driving stack.

The shortest high-value sequence remains:

`perception → small input adapter → frozen MaleCNS → small output adapter → steering/throttle → environment → reward → repeat`.

If active information acquisition later becomes a measured bottleneck, Run22 and the conventional baselines above provide a clean test bed. The experimental claim should then be whether MaleCNS buys information more effectively at equal cost — not whether active diagnosis or dynamic sensor selection is new.

## 10. Search conclusion

Material findings:

1. **Priority narrowed:** active diagnosis, dynamic sensor selection under cost, event-triggered FDI, sensor scheduling for fault isolation, and quality-aware multimodal routing all predate Run22.
2. **Exact combination not located:** the specific OBD/GNSS false-consensus → camera conflict → on-demand LiDAR arbitration → future frozen-connectome controller conjunction was not found pre-cutoff in the bounded search.
3. **Strong internal contrary evidence:** camera and LiDAR corruption already show that one additional witness does not generally identify the faulty side.
4. **Strong external boundary:** common-cause failure can defeat redundancy; modality count is not independence.
5. **Terminology narrowed:** the current implementation is best described as an active information-acquisition / VOI-motivated baseline, not yet a formal VOI optimizer.
6. **Next discriminant:** real synchronized ego-motion data + correlated/common-cause faults + explicit sensing cost + strong active-sensor-selection baselines, only if this layer becomes relevant after the first closed-loop MaleCNS driving experiments.
