---
type: "Audit Report"
title: "MaleCNS Run21 OBD witness veto — prior-art and falsification audit — 2026-09-19"
description: "Claim-level temporal, novelty, and adversarial truth-status audit of Run21's OBD-II delta-speed veto for IMU-proposed GNSS clock repair."
tags: [malecns, prior-art, falsification, driving, gnss, imu, obd-ii, clock-offset, fault-detection, integrity-monitoring, active-sensing]
timestamp: 2026-09-19T19:01:12Z
---

# MaleCNS Run21 OBD witness veto — prior-art and falsification audit — 2026-09-19

> **Status:** claim-specific audit of [`FINDINGS_2026-09-19_RUN21_IMU_WITNESS_VETO.md`](../../experiments/malecns_car_interface/FINDINGS_2026-09-19_RUN21_IMU_WITNESS_VETO.md). Priority and present truth status are separate axes. This audit does not establish exhaustive novelty, patent novelty, causal dependence, copying, plagiarism, or misconduct. Negative searches are bounded observations.

## 1. Claims and explicit falsifiers

### C1 — a second physically different vehicle signal can veto some false GNSS clock repairs proposed from phone IMU evidence

Run21 lets the phone-IMU path propose a clock offset and uses OBD-II speed-delta consistency as a veto when the proposed shift makes GNSS/OBD agreement materially worse than leaving the timestamp unchanged.

**Falsifier / narrowing condition:** a matched conventional integrity monitor or robust multi-sensor consistency test achieves the same or better false-repair/true-repair trade-off from the same observations; the OBD veto ceases to help out of sample; or correlated/common-mode faults make the veto affirm the wrong timing hypothesis.

### C2 — OBD speed differences remain useful when absolute OBD speed has a static additive bias

The Run21 rationale is that differencing cancels a constant additive OBD speed bias.

**Falsifier / narrowing condition:** the relevant OBD error is not constant additive bias but scale-factor error, wheel slip, quantization, drift, installation/model error, or a timing error that survives differencing; in those regimes the delta ceases to be a reliable independent witness.

### C3 — the observed veto is a safety/recall trade-off rather than a universal win

In the frozen synthetic harness, the veto reduces false repairs and MAE when the clock is clean, but slightly worsens performance when a real fixed clock offset is present because some true repairs are vetoed.

**Falsifier / narrowing condition:** paired reruns fail to reproduce the sign of this trade-off; threshold calibration moves the operating point enough that the stated trade-off disappears; or a synchronized real sensor slice reverses the ordering.

### C4 — `clock-witness conflict` is a useful signal for an active controller deciding whether to gather more evidence

Run21 proposes exposing disagreement to MaleCNS so a controller can decide whether to request another GNSS fix, camera ego-motion, orientation/gravity diagnostics, or another declared sensor.

**Falsifier / narrowing condition:** a simple passive wait/fixed retry rule matches or beats the active policy at equal sensing/latency/energy cost; the conflict flag adds no predictive value for downstream driving reward; or a standard value-of-information / active-diagnosis policy dominates the MaleCNS policy.

### C5 — the OBD channel is sufficiently independent to serve as evidence about an IMU-proposed clock repair

This is the most important hidden premise of the mechanism. Physical diversity does not by itself establish statistical or failure independence.

**Falsifier / narrowing condition:** OBD and GNSS share a clock, software pipeline, CAN gateway, estimator, vehicle-dynamics confound, or common physical disturbance that produces correlated error; or a two-channel disagreement cannot identify which side is faulty without an additional model/prior/witness.

### C6 — the fixed 8% OBD contradiction threshold is a defensible decision rule

Run21 uses a fixed threshold inherited as a conservative analogue of the Run20 activation margin.

**Falsifier / narrowing condition:** held-out ROC/utility calibration yields a materially different operating point; false veto rate changes sharply with speed/dynamics/sensor quality; or a probabilistic integrity monitor dominates the fixed threshold.

## 2. Temporal reconstruction

The repository already had a broader **clock-health witness** concept in Run19 / PR [#682](https://github.com/franklinbaldo/papers/pull/682), created **2026-09-19 16:06:20 UTC**. That work used phone IMU as a witness about GNSS timing; it did **not** contain the Run21 architecture in which IMU proposes a repair and OBD independently vetoes that proposal.

Issue [#646](https://github.com/franklinbaldo/papers/issues/646) subsequently recorded **IMU witness corruption / mounting / gravity leakage** as an unresolved stress case after Run20. That is evidence that the failure mode was publicly recognized before Run21, but it is not public disclosure of the particular OBD-veto solution.

For the Run21-specific claims C1–C6:

- `0c5afac78a4c94dc75db0980191c2c8e53998d93`, Git author/committer timestamp **2026-09-19 18:08:30 UTC**, first located commit containing the OBD-II witness veto, experiment, tests and findings;
- PR [#703](https://github.com/franklinbaldo/papers/pull/703) was created at **2026-09-19 18:08:46 UTC** and merged at **18:09:14 UTC**;
- squash merge commit: `78eb95a8a0a407f34918690ddf955f6873625789`.

A commit timestamp does not by itself establish when a branch became publicly observable. The conservative public cutoff for the **Run21 OBD-veto claim set** is therefore **2026-09-19 18:08:46 UTC**.

The broader idea “use an additional noisy query/witness when diagnosis is uncertain” is much older and is treated below as prior art rather than being assigned the Run21 cutoff.

## 3. Search protocol

Sources were sought through arXiv, publisher/DOI pages, PubMed/PMC, IEEE/IET/Wiley-visible literature, navigation/integrity-monitoring literature, and GitHub repository history. Aggregator results were used for discovery only when a primary or near-primary source could be confirmed.

Representative overlap queries:

- `GNSS INS odometer fault detection consistency vehicle`
- `GNSS spoofing detection IMU odometer cross check vehicle`
- `integrity monitoring RTK GNSS IMU vehicle odometer consistency`
- `GNSS outlier detection IMU odometer two stage`
- `odometer fault detection exclusion inertial navigation vehicle`
- `multi sensor independent witness veto fault detection vehicle`
- `active diagnosis information gain noisy query fault diagnosis`

Representative adversarial queries:

- `GNSS INS odometer common mode failure`
- `fault isolation two sensors disagreement cannot identify fault`
- `odometer wheel slip scale factor fault detection`
- `integrity monitoring requires error free observation set`
- `GNSS spoofing detection constant speed failure`
- `fault detection threshold false alarm ROC calibration`
- `sensor redundancy correlated faults common mode`

Post-cutoff searches used the exact Run21 title and decompositions around `OBD witness`, `clock repair veto`, `clock-witness conflict`, GNSS/IMU/OBD timing, and active third-witness selection. The post-cutoff window is less than an hour in this audit; absence of a result is correspondingly weak evidence.

## 4. Pre-cutoff novelty / overlap

### 4.1 Cross-checking GNSS against IMU + vehicle odometer is direct prior art

**Ali Broumandan & Gérard Lachapelle, “Spoofing Detection Using GNSS/INS/Odometer Coupling for Vehicular Navigation.”** *Sensors* 18(5):1305. Published **2018-04-24**. DOI: https://doi.org/10.3390/s18051305

The method independently analyzes GNSS and IMU/odometer navigation over an observation window and cross-checks the resulting solutions to detect a bad GNSS hypothesis. It was tested in real vehicular environments and reports ROC/detection-time behavior. The paper also explicitly notes a failure regime: when the vehicle is static or travels straight at constant speed, there may be no distinguishing feature for the attack.

**Classification:** `prior_art` for the generic mechanism “use self-contained IMU/odometer evidence to reject or distrust an inconsistent GNSS hypothesis”; `adjacent_prior_work` for the exact Run21 clock-offset-veto rule. Compared claims: C1, C5, C6.

### 4.2 Vehicle integrity monitoring already uses GNSS/IMU/odometer consistency and explicit false-alarm logic

**Ahmed El-Mowafy & Nobuaki Kubo, “Integrity monitoring for Positioning of intelligent transport systems using integrated RTK-GNSS, IMU and vehicle odometer.”** *IET Intelligent Transport Systems* 12(8):901–908. First published **2018-07-19**. DOI: https://doi.org/10.1049/iet-its.2018.0106

The paper frames safety as fault detection/exclusion plus protection levels, uses consistency among possible observation sets, and makes a load-bearing identifiability statement: faults can be detected only when positioning remains available from at least one error-free observation set. It also uses speed-consistency conditions among GNSS and vehicle-derived speed and calibrates detection around statistical significance / false-alarm risk rather than assuming a single uncalibrated universal threshold.

**Classification:** `prior_art` for multi-sensor consistency gating/integrity monitoring in a GNSS + IMU + vehicle-odometer stack; `boundary_condition` for C5/C6 because redundancy only identifies a fault when there is sufficient fault-free information. Strength for the boundary: **strong**.

### 4.3 Odometer/wheel-speed measurements are themselves fault-bearing and require FDE

**He Chen et al., “SINS/OD Integrated Navigation Algorithm Based on Body Frame Position Increment for Land Vehicles.”** *Mathematical Problems in Engineering*, version of record online **2018-08-13**. DOI: https://doi.org/10.1155/2018/5719472

This work models odometer scale-factor error, installation error and lever arm, and explicitly introduces residual χ² fault detection/exclusion for odometer failures. It gives wheel/vehicle slip on muddy, snowy or icy surfaces as a source of wrong forward-speed measurement and experimentally injects odometer faults in a long-distance vehicle test.

**Classification:** `prior_art` for treating odometer evidence as a fallible sensor that must itself be gated; `boundary_condition` for C2/C5. Strength: **strong**.

### 4.4 Layered GNSS outlier rejection with Doppler, IMU and odometer predates Run21

**Baoshan Song et al., “Two stage GNSS outlier detection for factor graph optimization based GNSS-RTK/INS/odometer fusion.”** arXiv v1 **2025-10-01**, https://arxiv.org/abs/2510.00524

The first stage uses Doppler as a more stable reference for gross pseudorange inconsistency; the second uses pre-integrated IMU and odometer constraints to predict measurements and reject remaining GNSS outliers. The reported deep-urban-canyon experiment reduces RMSE from 0.52 m to 0.30 m relative to the stated fusion baseline.

**Classification:** `prior_art` for staged, complementary-witness GNSS rejection and for the generic principle that one sensor family can veto/downweight another when their predictions conflict; `partial_prior_art` for Run21's particular `IMU proposes temporal repair → OBD delta vetoes` order. Compared claims: C1, C5.

### 4.5 Active selection of additional diagnostic observations is established prior art

**Gowtham Bellala, Jason Stanley, Clayton Scott & Suresh K. Bhavnani, “Active Diagnosis via AUC Maximization: An Efficient Approach for Multiple Fault Identification in Large Scale, Noisy Networks.”** arXiv v1 **2012-02-14**, https://arxiv.org/abs/1202.3701; later *IEEE TPAMI*.

The problem is explicitly formulated as sequentially selecting noisy diagnostic queries to identify faulty vs working objects. The particular AUC objective is not our concern here; the important antecedent is the active-diagnosis abstraction itself.

**Classification:** `prior_art` for the generic C4 concept “uncertainty/conflict can trigger a deliberately selected next observation”; `adjacent_prior_work` for applying that decision through MaleCNS to vehicle sensors.

### Novelty boundary after the search

The bounded search did **not locate** a pre-cutoff publication with the exact Run21 conjunction:

`causal phone-IMU GNSS clock-offset proposer → OBD-II speed-delta contradiction score over the proposed shift → one-sided veto of the repair → expose the resulting conflict as an active-sensing input to a frozen-connectome vehicle controller`.

That exact conjunction is narrower than the prior work above, but its major conceptual components — redundant sensor consistency checks, GNSS/INS/odometer fault detection, staged complementary rejection, and active diagnostic querying — are established. This is a negative search result, **not** a firstness claim.

## 5. Falsification / contrary-evidence ledger

### 5.1 Two disagreeing witnesses detect inconsistency; they do not, by themselves, identify which witness is wrong

Run21 gives OBD an asymmetric role: IMU proposes an offset; OBD may veto it. That is a legitimate policy, but it is not general fault isolation. If IMU and OBD disagree, two channels alone do not establish which channel is faulty without a structural model, reliability prior, or third independent source.

El-Mowafy & Kubo state the broader integrity-monitoring constraint directly: consistency-based fault detection requires at least one error-free observation set capable of producing a solution. Their IMU+odometer mode can even have no degrees of freedom for FDE, illustrating that merely having sensor outputs does not guarantee isolability.

**Classification:** `contrary_evidence`, strength **strong**, against any interpretation that the OBD veto *identifies* a wrong IMU repair. `boundary_condition`, strength **strong**, for the actual narrower engineering claim that the OBD guard can reduce false repairs in a declared fault family.

**Target attacked:** mechanism/identifiability, not the frozen Run21 MAE table.

**Required action:** `narrow_claim + add_boundary_condition + add_control`. The scientifically precise interpretation is: **“OBD-consistency veto reduces false clock-repair activations in the tested fault family under an architectural prior that OBD disagreement is meaningful.”** A third witness or explicit multiple-fault hypothesis model is required before claiming general fault isolation.

### 5.2 Differencing cancels constant additive bias, not arbitrary odometer error

Let the measured OBD speed be

`v_obd(t) = v(t) + b(t) + e(t)`.

Then

`Δv_obd = Δv + [b(t2)-b(t1)] + [e(t2)-e(t1)]`.

A truly constant additive `b` cancels. Drift does not. A multiplicative scale error does not generally cancel; wheel slip changes the physical relation between wheel-derived speed and vehicle ground speed; quantization and timestamp mismatch also survive.

Chen et al. independently motivate online odometer scale-factor modeling and explicit odometer fault detection/exclusion because these failures occur in real land-vehicle operation.

**Classification:** `boundary_condition`, strength **strong**, for C2/C5.

**Target attacked:** premise/generalization.

**Required action:** `narrow_claim + add_control`. Keep “static additive bias largely cancels” exactly that narrow. Do not infer “OBD is robust to bias” or “OBD is independent.” Stress scale-factor error, slip, correlated timing error and CAN/software delay if this mechanism becomes load-bearing.

### 5.3 Low-excitation motion can make the witness uninformative even when every sensor is honest

Broumandan & Lachapelle report that their real-vehicle GNSS-vs-INS/odometer spoof detector lacks a useful distinguishing feature when the vehicle is static or travels straight at constant speed. Run20 already established the same general observability problem for clock-offset estimation: insufficient temporal excitation can flatten or alias the offset objective.

Run21 inherits that limitation twice: the IMU proposal may be ambiguous, and the OBD delta comparison may carry little evidence about which shift is better.

**Classification:** `boundary_condition`, strength **strong**.

**Target attacked:** identifiability/regime.

**Required action:** `add_boundary_condition`. Conflict/support should be treated as low-information when the candidate intervals have insufficient kinematic excitation; the controller may then wait/probe rather than interpreting a near-tie as evidence.

### 5.4 The current 8% veto threshold is an operating point, not a calibrated integrity guarantee

The Run21 findings already contain the relevant negative control. The veto improves the no-offset case but worsens a real +0.3 s offset by **1.84%** on average because noisy OBD evidence sometimes vetoes a true repair; offset+jitter is **1.13% worse**. This is honest evidence of the precision/recall trade-off, but it also means the 8% value is not a general safety threshold.

The pre-cutoff vehicular integrity/spoofing literature evaluates false-alarm/detection trade-offs explicitly through statistical tests, integrity risk, protection levels or ROC curves. That is a stronger validation contract than transferring an 8% margin by analogy from Run20.

**Classification:** `boundary_condition`, strength **strong**; `contrary_evidence`, strength **moderate**, against any claim that the current 8% rule is intrinsically reliable or safety-calibrated.

**Target attacked:** magnitude/decision rule, not the existence of the observed synthetic gain.

**Required action:** `add_control + downgrade_confidence`. If Run21 is promoted beyond a simple remediation baseline, freeze a held-out calibration set and report ROC/precision-recall or application-weighted utility over thresholds, with the clean false-veto and true-offset miss rates explicit.

### 5.5 Common-mode failure is not just a next experiment; it is the central independence boundary

If OBD and GNSS inherit the same timebase error or software delay, or if an environmental/vehicle condition drives correlated error in the compared quantities, they can agree while jointly wrong. Conversely, a real GNSS repair can be vetoed when OBD is the bad witness.

The Run21 finding already identifies common-mode failure as the next adversary. The integrity-monitoring literature makes the reason formal: redundancy is useful only to the extent that at least one usable fault-free hypothesis remains.

**Classification:** `boundary_condition`, strength **strong**.

**Target attacked:** premise of witness independence and generalization.

**Required action:** `add_control`, not `abandon_hypothesis`. The declared next falsifier is correct: OBD+GNSS common-mode failure, then a genuinely different third witness such as camera ego-motion. Importantly, this belongs in the remediation/comparator library and should **not** become a prerequisite before the first direct MaleCNS driving experiment.

### 5.6 The value-of-information idea does not make a positive Run21 result MaleCNS-specific

Bellala et al. and the wider active-diagnosis literature establish that, under uncertain fault state, a controller can select a next noisy query to reduce diagnostic uncertainty. Therefore a future result in which MaleCNS learns to request another sensor after `clock-witness conflict` must be compared against ordinary active-diagnosis/value-of-information policies at matched cost.

**Classification:** `prior_art` for the generic mechanism; `boundary_condition`, strength **strong**, for attribution to MaleCNS.

**Target attacked:** mechanism attribution, not usefulness of the conflict channel.

**Required action:** `add_control`. Compare at least passive wait/fixed retry, a simple uncertainty-threshold policy, and a conventional expected-information/expected-utility policy before crediting the connectome with superior information allocation.

## 6. Alternative explanations and stronger baselines

The Run21 clean-clock gain does not require a connectome-specific explanation. A simpler explanation is **conservative redundant-sensor gating**: when one detector proposes a risky repair, a second sensor occasionally rejects bad proposals. That is useful engineering, but it is a classical fault-detection/integrity-monitoring pattern.

A stronger conventional baseline ladder for the particular Run21 layer is:

`IMU-only Run20 proposal → fixed OBD veto (Run21) → held-out calibrated OBD veto → probabilistic/multi-hypothesis integrity monitor → third-witness isolation under correlated faults`.

For the *active* decision after conflict:

`passive wait → fixed retry/request rule → uncertainty-threshold policy → conventional value-of-information / active-diagnosis policy → MaleCNS policy`.

This preserves the project-order decision already adopted in the repository: **drive first, theorize from observed failures.** Run21 remains a small comparator/remediation primitive and a source of a useful conflict signal. It is not another engineering layer that must be solved before `perception → MaleCNS → action → reward` runs.

## 7. Post-cutoff evidence

The conservative Run21 cutoff is **2026-09-19 18:08:46 UTC**.

The bounded external search immediately after that cutoff found no scholarly work whose first public disclosure falls in the sub-hour post-cutoff window and materially overlaps the exact Run21 conjunction. Exact-title / exact-phrase searches primarily returned no relevant external research.

Repository activity after #703 in the inspected window (#704/#705) concerns Zenodo readiness for a different paper and is unrelated to Run21. No internal Run22-like derivative was located at audit time.

Accordingly, no `later_independent`, `later_overlap`, `later_non_citing`, `later_citing`, or `later_derivative` classification is assigned in this round. The negative search is weak because the post-cutoff window is extremely short.

## 8. Priority / truth-status matrix

| claim | priority | truth status after audit | required action |
|---|---|---|---|
| C1 second vehicle witness can veto some bad GNSS hypothesis | generic consistency/veto mechanism `prior_art`; exact clock-repair conjunction not located | supported only for tested synthetic fault family | `narrow_claim + add_boundary_condition` |
| C2 OBD delta tolerates static additive speed bias | mathematical component is elementary / not a novelty claim | true for constant additive bias; false as a general robustness claim | `narrow_claim + add_control` |
| C3 safety/recall trade-off observed in Run21 | local empirical result, not prior-art claim | supported by frozen harness; real-data/general threshold confidence low | `no_change` to numbers; `downgrade_confidence` outside harness |
| C4 expose conflict and actively buy more evidence | generic active diagnosis is `prior_art` | useful experimental channel; no MaleCNS advantage shown | `add_control` |
| C5 OBD is an independent witness | physical diversity only; general independence not established | strong common-mode / fault-isolation boundary | `narrow_claim + add_boundary_condition + add_control` |
| C6 fixed 8% contradiction threshold | local implementation detail | uncalibrated operating point with demonstrated true-repair cost | `add_control + downgrade_confidence` |

No frozen Run21 numerical result is retracted. The material correction is **attribution and scope**: Run21 is best described as a simple asymmetric integrity guard that improved one side of a synthetic safety/recall trade-off under declared fault injections. It does not establish general fault isolation, statistical independence of OBD, a safety-calibrated threshold, or a MaleCNS-specific active-sensing advantage.

## 9. Search result ledger

| candidate | first public date used | status / venue | compared claims | classification | falsification relation | strength / reason |
|---|---:|---|---|---|---|---|
| Broumandan & Lachapelle, *Spoofing Detection Using GNSS/INS/Odometer Coupling for Vehicular Navigation* | 2018-04-24 | Sensors 18(5), DOI 10.3390/s18051305 | C1, C5, C6 | `prior_art` / `adjacent_prior_work` | real-vehicle cross-check plus low-excitation failure regime | strong overlap for generic witness consistency |
| El-Mowafy & Kubo, *Integrity monitoring for Positioning of intelligent transport systems using integrated RTK-GNSS, IMU and vehicle odometer* | 2018-07-19 | IET ITS 12(8), DOI 10.1049/iet-its.2018.0106 | C1, C5, C6 | `prior_art`; `boundary_condition` | requires at least one error-free observation set; explicit integrity-risk/FDE framework | strong |
| Chen et al., *SINS/OD Integrated Navigation Algorithm Based on Body Frame Position Increment for Land Vehicles* | 2018-08-13 | Mathematical Problems in Engineering, DOI 10.1155/2018/5719472 | C2, C5 | `prior_art`; `boundary_condition` | odometer scale/slip faults require detection/exclusion | strong |
| Song et al., *Two stage GNSS outlier detection for factor graph optimization based GNSS-RTK/INS/odometer fusion* | 2025-10-01 | arXiv:2510.00524 | C1, C5 | `prior_art` / `partial_prior_art` | staged complementary sensors reject GNSS outliers | strong overlap at architecture class, not exact temporal veto |
| Bellala et al., *Active Diagnosis via AUC Maximization* | 2012-02-14 | arXiv:1202.3701; later IEEE TPAMI | C4 | `prior_art` / `adjacent_prior_work` | conventional noisy-query selection is a required active-sensing baseline | strong for generic active diagnosis |

### Negative searches worth preserving

No material pre-cutoff source was located for the exact full conjunction `phone-IMU clock-offset proposer + OBD speed-delta one-sided veto + explicit conflict channel for a frozen MaleCNS active controller`. Exact-title and phrase searches likewise found no post-cutoff external overlap in the very short window available. Neither result proves absence.
