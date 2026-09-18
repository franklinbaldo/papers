---
type: "Audit Report"
title: "MaleCNS Sensor Colony — claim-level prior-art audit — 2026-09-19"
description: "Temporal, claim-specific audit of specialist MaleCNS sensor colonies, hierarchical coordination, redundant fusion, failure robustness, and the exact multi-connectome conjunction."
tags: [malecns, prior-art, sensor-fusion, mixture-of-experts, autonomous-driving, robustness, citation-debt]
timestamp: 2026-09-19T00:00:00Z
---

# MaleCNS Sensor Colony — claim-level prior-art audit — 2026-09-19

> **Status:** first claim-specific temporal audit of [`experiments/malecns_car_interface/COLONY_ARCHITECTURE.md`](../../experiments/malecns_car_interface/COLONY_ARCHITECTURE.md). This audit narrows the originality boundary substantially. It does not establish exhaustive novelty, patent novelty, copying, causal dependence, or priority beyond the public record and searches described here.

## 1. Claims audited

The sensor-colony note contains several separable claims. They must not be treated as one indivisible novelty claim.

- **C1 — redundant same-channel specialists:** several independently initialized/trained specialists may observe one sensor channel, with single, mean, median, confidence-weighted, and learned-coordinator baselines; redundancy is expected to improve tolerance to noise or individual failures.
- **C2 — modality-specialist decomposition:** different specialists process camera, detection, IMU, GNSS, OBD, ranging, RF/navigation, and discrepancy channels rather than one monolithic controller consuming the complete sensorium.
- **C3 — recursive hierarchical coordination:** specialist outputs feed modality coordinators and then a driving coordinator; the coordinator may itself be a MaleCNS instance and the hierarchy may recurse.
- **C4 — graceful degradation and distrust:** the system should remain useful under sensor/specialist loss, delay, noise, contradiction, or confident error; the coordinator should learn when to distrust a specialist.
- **C5 — compact lawful report contract:** specialists expose bounded semantic values, confidence, novelty/surprise and optional compact state references rather than privileged simulator state.
- **C6 — modularity:** sensors/specialists can be added or removed without forcing retraining of every existing specialist, subject to coordinator adaptation.
- **C7 — exact MaleCNS conjunction:** multiple copies of the measured MaleCNS connectome are assigned narrow sensor-specialist roles, possibly redundantly per channel, communicate through a reality-bounded report interface, and are fused by one or more higher-level MaleCNS coordinators under matched-compute and connectome controls.

The audit distinguishes novelty of **C7's conjunction** from novelty of C1–C6's ingredients.

## 2. Temporal reconstruction of our claims

### 2.1 Relevant cutoff: 2026-09-18 22:04:30 UTC

The current file timestamp and the repository merge time are not used as the priority cutoff.

The earliest public GitHub commit located that already contains C1–C7 is:

- commit [`e2d045bcb0faba4525b1546664eb2c32469d8f2b`](https://github.com/franklinbaldo/papers/commit/e2d045bcb0faba4525b1546664eb2c32469d8f2b)
- authored/committed: **2026-09-18 22:04:30 UTC**
- message: `Add MaleCNS sensor-colony architecture`
- public branch/PR: `experiment/malecns-car-interface`, later merged by PR #526.

That commit already states the specialist-per-modality architecture, redundant same-channel specialists, compact value/confidence/novelty reports, recursive MaleCNS coordinators, modularity/graceful-degradation hypotheses, C0–C5 curriculum, median/confidence-weighted baselines, and confidently-wrong specialist stress test.

A later commit at 22:04:33 UTC added the executable `SpecialistReport`/fusion baselines, but it does not move the cutoff for the architectural claims already public at 22:04:30 UTC.

**Priority confidence for the subject claim set:** `1.0` for public Git provenance. This is evidence of public timing, not of novelty.

## 3. Search protocol

Searches were claim-led and date-sensitive. Sources included arXiv, DOI/publisher pages, AAAI, CVPR records, GitHub primary repositories, autonomous-driving multimodal-fusion literature, robust distributed sensor-fusion literature, and mixture-of-experts literature.

Representative queries included:

- `hierarchical mixture of experts specialists gating robot dynamics`
- `autonomous driving mixture domain specific experts gating`
- `sensor-specific experts autonomous driving sensor failure router`
- `multi-modal expert fusion sensor failure LiDAR camera`
- `missing modality mixture of experts confidence gate`
- `sensor confidence weighted fusion fault tolerant`
- `median consensus sensor faults UAV fusion`
- `sensor-specific adapters validity signals sparse experts`
- `modular sensor fusion missing modalities without retraining`
- `MaleCNS multiple copies swarm independent brains`
- `MaleCNS sensor specialist coordinator`
- `MaleCNS sensor colony`
- `MaleCNS multi-agent connectome`

Negative search results are bounded results of these searches, not proof of non-existence.

## 4. Pre-cutoff findings

### 4.1 Hierarchical mixtures of experts predate the recursive specialist/coordinator pattern

**Work:** Michael I. Jordan & Robert A. Jacobs, **“Hierarchical Mixtures of Experts and the EM Algorithm.”** *Neural Computation* 6(2), 181–214, published 1994-03-01, DOI 10.1162/neco.1994.6.2.181.

- Primary record: https://doi.org/10.1162/neco.1994.6.2.181
- The paper presents a **tree-structured** architecture with expert components and higher-level mixture/gating structure, and reports robot-dynamics simulations.

**Compared claims:** C3; generic part of C2.

**Classification:** `partial_prior_art`.

**Why:** hierarchical experts coordinated by learned gates are old. The distinctive issue in our note cannot be “experts arranged hierarchically.” Jordan/Jacobs does not anticipate the sensor-specific MaleCNS/connectome instantiation, the reality boundary, or the particular report contract.

### 4.2 Value + confidence reports and confidence-weighted averaging are direct prior art

**Work:** Wilfried Elmenreich, **“Fusion of Continuous-valued Sensor Measurements using Confidence-weighted Averaging.”** *Journal of Vibration and Control* 13(9–10), first published September 2007, DOI 10.1177/1077546307077457.

- Primary record: https://doi.org/10.1177/1077546307077457
- Each sensor measurement is represented by a **measurement value and a confidence marker**; the proposed Confidence-weighted Averaging algorithm fuses them according to estimated error variance.

**Compared claims:** C1, C5.

**Classification:** `prior_art` for the generic `value + confidence -> confidence-weighted fusion` component; `partial_prior_art` for the richer MaleCNS report contract.

**Consequence:** neither confidence-tagged sensor reports nor confidence-weighted fusion should be described as original to the sensor-colony architecture. `novelty/surprise`, connectome state references, and the lawful-interface constraint are additional elements, not a reset of that prior art.

### 4.3 Median-based robust fusion under faulty distributed sensors is established prior art

**Work:** Y. Kim, D.-W. Gu & I. Postlethwaite, **“Fault-tolerant Cooperative Target Tracking in Distributed UAV Networks.”** IFAC Proceedings Volumes 41(2), 8878–8883, 2008, DOI 10.3182/20080706-5-KR-1001.01500.

- Primary record: https://doi.org/10.3182/20080706-5-KR-1001.01500
- The method assumes sensors may report target position incorrectly and uses a **median-consensus** fusion strategy together with fault detection.

**Compared claims:** C1, C4.

**Classification:** `prior_art` for median-style robust aggregation of redundant faulty sensing agents; `adjacent_prior_work` for the learned MaleCNS coordinator.

**Consequence:** the synthetic RUN2 result that median fusion is robust to biased faulty specialists is an important baseline verification, not evidence that robust median fusion itself is novel.

### 4.4 Domain-specialized experts with gating already control autonomous-driving policies

**Work:** Inhan Kim, Joonyeong Lee & Daijin Kim, **“Learning Mixture of Domain-Specific Experts via Disentangled Factors for Autonomous Driving.”** AAAI 2022, published 2022-06-28, DOI 10.1609/aaai.v36i1.20000.

- Primary record: https://doi.org/10.1609/aaai.v36i1.20000
- The method decomposes behavior cloning into domain-specific subspaces, trains specialized policy experts, and combines them through a gating function to predict vehicle controls.

**Compared claims:** C2, C3.

**Classification:** `partial_prior_art`.

**Why:** specialized experts + learned cooperation/gating in an autonomous-driving controller are already established. The experts are domain/policy specialists, not separately embodied MaleCNS sensor specialists.

### 4.5 MetaBEV already uses modality-specific processing and selective aggregation under sensor failures

**Work:** Chongjian Ge et al., **“MetaBEV: Solving Sensor Failures for BEV Detection and Map Segmentation.”** arXiv:2304.09801 v1, **2023-04-19 16:37:17 UTC**.

- Primary preprint: https://arxiv.org/abs/2304.09801
- Signals from multiple sensors are first processed by **modal-specific encoders**; a decoder selectively aggregates LiDAR, camera, or both, and the system is explicitly evaluated under sensor corruption and complete missing-sensor conditions.

**Compared claims:** C2, C4, C6.

**Classification:** `partial_prior_art`.

**Consequence:** modality specialization plus graceful degradation under missing sensors is not novel at the architectural level.

### 4.6 UniBEV explicitly targets missing sensor modalities without retraining

**Work:** Shiming Wang et al., **“UniBEV: Multi-modal 3D Object Detection with Uniform BEV Encoders for Robustness against Missing Sensor Modalities.”** arXiv:2309.14516 v1, **2023-09-25 20:22:47 UTC**.

- Primary preprint: https://arxiv.org/abs/2309.14516
- The same model operates on LiDAR+camera, LiDAR-only, or camera-only **without retraining** and compares concatenation, averaging, and weighted averaging fusion strategies.

**Compared claims:** C4, C6; baseline component of C1.

**Classification:** `partial_prior_art`.

**Consequence:** “missing sensor should not collapse the system” and weighted/average fusion baselines have mature autonomous-driving antecedents.

### 4.7 FuseMoE handles varying and missing modality sets through a mixture-of-experts gate

**Work:** Xing Han et al., **“FuseMoE: Mixture-of-Experts Transformers for Fleximodal Fusion.”** arXiv:2402.03226 v1, **2024-02-05 17:37:46 UTC**.

- Primary preprint: https://arxiv.org/abs/2402.03226
- FuseMoE is designed to integrate a diverse number of modalities and handle missing modalities through an expert/gating architecture.

**Compared claims:** C2, C6.

**Classification:** `partial_prior_art`.

### 4.8 ReliFusion directly anticipates reliability/confidence-driven sensor weighting under failure

**Work:** Reza Sadeghian et al., **“Reliability-Driven LiDAR-Camera Fusion for Robust 3D Object Detection.”** arXiv:2502.01856 v1, **2025-02-03 22:07:14 UTC**.

- Primary preprint: https://arxiv.org/abs/2502.01856
- ReliFusion assigns **confidence scores** to each modality and dynamically balances LiDAR/camera information through confidence-weighted cross-attention under sensor malfunctions.

**Compared claims:** C4, C5.

**Classification:** `partial_prior_art`.

**Consequence:** learning or computing modality reliability and using it downstream to reweight fusion is directly anticipated.

### 4.9 MoME is particularly close: sensor/modal experts + adaptive quality router + failure robustness

**Work:** Konyul Park, Yecheol Kim, Daehun Kim & Jun Won Choi, **“Resilient Sensor Fusion under Adverse Sensor Failures via Multi-Modal Expert Fusion.”** arXiv:2503.19776 v1, **2025-03-25 15:46:18 UTC**; CVPR 2025.

- Primary preprint: https://arxiv.org/abs/2503.19776
- DOI/proceedings: https://doi.org/10.1109/CVPR52734.2025.00630
- MoME uses parallel camera, LiDAR, and fused expert decoders plus an **Adaptive Query Router** that selects the best expert based on sensor-feature quality, explicitly targeting sensor drops, limited field of view, occlusion and other failures.

**Compared claims:** C2, C4, C5.

**Classification:** `partial_prior_art` with **high substantive overlap at the architecture level**.

**Why not full C7 prior art:** MoME is a perception architecture, not a population of independent measured MaleCNS recurrent connectomes with sensor-specialist learning and a MaleCNS coordinator.

### 4.10 Conf-SMoE establishes modality-specialized experts plus confidence-guided gating for missing modalities

**Work:** Liangwei Nathan Zheng et al., **“Rethinking Gating Mechanism in Sparse MoE: Handling Arbitrary Modality Inputs with Confidence-Guided Gate.”** arXiv:2505.19525 v1, **2025-05-26 05:18:55 UTC**.

- Primary preprint: https://arxiv.org/abs/2505.19525
- The paper explicitly frames individual experts as specializing in different modalities and proposes confidence-guided gating for missing-modality robustness.

**Compared claims:** C2, C4, C5.

**Classification:** `partial_prior_art`.

### 4.11 MEOX is a very recent pre-cutoff sensor-specific expert architecture

**Work:** Mohanad Albughdadi, **“MEOX: Compact Multimodal Mixture-of-Experts for Earth Observation.”** arXiv:2609.05351 v1, **2026-09-04 16:59:36 UTC**.

- Primary preprint: https://arxiv.org/abs/2609.05351
- MEOX uses **sensor-specific adapters**, explicit validity signals, sparse experts, learned fusion, and structured sensor dropout to preserve modality-dependent processing while tolerating heterogeneous/missing observations.

**Compared claims:** C2, C4, C6.

**Classification:** `partial_prior_art`.

**Temporal note:** it predates our C1–C7 cutoff by about two weeks. It must therefore remain on the prior side of the ledger even though it is contemporaneous in calendar terms.

### 4.12 FlyDrones predates us on multiple independent MaleCNS copies — but not on sensor-specialist hierarchy

**Project:** SpikeCalls, **FlyDrones**.

- Repository: https://github.com/SpikeCalls/FlyDrones
- Repository created: 2026-09-15 20:52:47 UTC.
- Earliest README commit located that already documents the relevant swarm claim: [`6e273a9eec704319fe2468e1d26b09bf06084328`](https://github.com/SpikeCalls/FlyDrones/commit/6e273a9eec704319fe2468e1d26b09bf06084328), **2026-09-15 21:23:12 UTC**.
- That README states that `flydrones swarm` copies one connectome into **three independent brains with the same wiring and separate spikes** to control three simulated drone pilots.

**Compared claims:** population-diversity/redundancy component of C1; multi-instance MaleCNS component of C7.

**Classification:** `partial_prior_art`.

**Important boundary:** FlyDrones uses multiple independent copies as separate pilots. It does **not** establish the C7 pattern in which copies are assigned narrow sensor-specialist roles and fused by a higher-level MaleCNS coordinator.

**Correction to our previous sweep:** the 2026-09-18 vehicle/robotics note recorded a social/project-page claim suggesting three **physical** drones. The primary FlyDrones README is more conservative: its documented swarm output is simulated, the browser uses an 850-neuron synthetic MiniFly stand-in, and the hardware adapters are explicitly stated not to have been flight-tested by the authors at that point. The earlier “physical drone swarm” characterization therefore remains unverified and should not be cited as established evidence.

## 5. What is and is not plausibly distinctive after this audit

### Not defensible as standalone novelty

The following components have clear pre-cutoff antecedents and should be treated as established techniques or strong prior art:

- hierarchical expert/coordinator architectures;
- sensor/modality-specific experts or encoders;
- learned gating/routing among experts;
- confidence/reliability scoring for sensor fusion;
- confidence-weighted fusion;
- median-based robust fusion under faulty distributed sensing;
- robustness to missing/corrupted modalities;
- modular operation under different sensor subsets;
- multiple independent copies of the same MaleCNS wiring running with separate neural states.

### Remaining combination-level research question

After the searches above, **no pre-cutoff work was located that combines all of the following in one architecture**:

1. measured MaleCNS connectome instances as the actual recurrent substrates of the specialists;
2. narrow **sensor-specialist** assignment rather than each connectome being a whole-agent pilot;
3. multiple redundant MaleCNS specialists per sensor as an explicit controlled variable;
4. compact reality-bounded reports carrying values, confidence, novelty/surprise and optional internal state references;
5. a higher-level coordinator that is itself another MaleCNS instance, with recursive modality→driving hierarchy;
6. matched-capacity, rewired/random-connectome, fixed-fusion and confidently-wrong-specialist controls.

This is a bounded negative search result, **not** a claim that the conjunction is globally first.

The scientific burden is now clearer: the experiment must show that the **MaleCNS-specific instantiation** contributes something beyond well-established robust sensor fusion and mixture-of-experts baselines. If ordinary MoE/router, median, confidence-weighted, or modality-fusion systems match the result, the connectome hierarchy has not earned a distinct scientific claim.

## 6. Later-work search

The cutoff is 2026-09-18 22:04:30 UTC. Fresh searches for sensor-fusion experts, modality routing, MaleCNS multi-agent/sensor-specialist systems, and autonomous-driving MoE work released after that time did **not locate a material post-cutoff candidate** in this round.

Therefore this audit creates no `later_independent`, `later_overlap`, `later_non_citing`, `later_citing`, or `later_derivative` record.

“No later candidate located” is a search result, not evidence that none exists.

## 7. Citation-debt / Schmidhuber-Meter readiness

The subject-side provenance needed for future Citation Debt Assessments is now frozen:

- `subject_claim`: MaleCNS sensor-colony C1–C7 as decomposed above
- `subject_artifact`: `experiments/malecns_car_interface/COLONY_ARCHITECTURE.md`
- `subject_cutoff`: `2026-09-18T22:04:30Z`
- `priority_confidence`: `1.0`
- `formula_version`: `0.1`

All material candidates found in this round are **pre-cutoff**, so they cannot owe citation debt to us and no Schmidhuber score is applicable to those pairs.

If a materially overlapping post-cutoff work appears, future audits should separately record overlap (concept/mechanism/experiment/prediction/rare conjunction), historical discoverability, credit received, impact-as-of, and dependency evidence. `later_non_citing` alone must never be used to infer derivation.

## 8. Classification summary

| Candidate | First public date used | Claims | Classification | Main implication |
|---|---:|---|---|---|
| Jordan & Jacobs, HME | 1994-03-01 | C3 | `partial_prior_art` | recursive expert hierarchies are old |
| Elmenreich, confidence-weighted sensor fusion | 2007-09 | C1/C5 | `prior_art` (component) | value+confidence and confidence weighting are old |
| Kim/Gu/Postlethwaite, median-consensus UAV fusion | 2008 | C1/C4 | `prior_art` (component) | median robustness to faulty sensing is old |
| Kim/Lee/Kim, MoDE autonomous driving | 2022-06-28 | C2/C3 | `partial_prior_art` | specialized driving experts + gating predate us |
| MetaBEV | 2023-04-19 | C2/C4/C6 | `partial_prior_art` | modal encoders + missing-sensor robustness predate us |
| UniBEV | 2023-09-25 | C1/C4/C6 | `partial_prior_art` | missing modality without retraining + weighted fusion |
| FuseMoE | 2024-02-05 | C2/C6 | `partial_prior_art` | fleximodal experts handle missing modality sets |
| ReliFusion | 2025-02-03 | C4/C5 | `partial_prior_art` | explicit reliability/confidence-driven fusion |
| MoME | 2025-03-25 | C2/C4/C5 | `partial_prior_art` | sensor experts + adaptive quality router is very close |
| Conf-SMoE | 2025-05-26 | C2/C4/C5 | `partial_prior_art` | modality-specialized experts + confidence gating |
| MEOX | 2026-09-04 | C2/C4/C6 | `partial_prior_art` | sensor adapters + validity + sparse experts + dropout |
| FlyDrones | 2026-09-15 21:23:12Z | C1/C7 | `partial_prior_art` | multiple independent MaleCNS copies predate our colony note |

## 9. Revision rule

This audit should be revised if a primary source establishes an earlier complete sensor-specialist MaleCNS hierarchy, if the FlyDrones hardware/swarm evidence changes materially, or if a post-cutoff system becomes sufficiently close to require a Citation Debt Assessment. Revisions should preserve the old classification and state why it changed rather than silently replacing it.
