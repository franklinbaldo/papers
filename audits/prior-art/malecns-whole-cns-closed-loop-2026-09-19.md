---
type: "Audit Report"
title: "MaleCNS whole-CNS closed-loop control — prior-art and falsification audit — 2026-09-19"
description: "Claim-level temporal, novelty, and adversarial validity audit of the whole-CNS MaleCNS closed-loop driving protocol, including connectome-control baselines and Drosophila reward/credit-assignment biology."
tags: [malecns, prior-art, falsification, closed-loop, reinforcement-learning, connectome, driving, drosophila, reward, plasticity]
timestamp: 2026-09-19T18:00:00Z
---

# MaleCNS whole-CNS closed-loop control — prior-art and falsification audit — 2026-09-19

> **Status:** claim-specific audit of `experiments/malecns_car_interface/PROTOCOL-WHOLE-CNS-CLOSED-LOOP-v1.md` and the intended architecture stated in `malecns_connectome_reservoir_tagging.md`. Priority and truth status are separate axes. This audit does not establish exhaustive novelty, patent novelty, copying, derivation, plagiarism, or misconduct. Negative searches are bounded observations.

## 1. Claims and explicit falsifiers

### C1 — a whole adult Drosophila connectome can provide useful structural inductive bias in embodied closed-loop control

**Falsifier / narrowing condition:** under shared initialization, matched interface capacity, matched optimization and an ensemble of degree-preserving null graphs, the biological topology has no reproducible advantage over rewired/random/conventional controllers.

### C2 — a frozen whole-connectome core plus thin trainable interfaces is a meaningful control architecture

**Falsifier / narrowing condition:** adapter-only or matched random reservoirs recover the same behavior; useful performance depends on trainable internal node dynamics rather than the frozen core; or the biological graph is consistently inferior under matched dynamical scaling.

### C3 — biologically addressed sensory, reinforcement and action populations add information beyond arbitrary graph plumbing

**Falsifier / narrowing condition:** matched random/anatomically implausible input/reward/output assignments perform equivalently or better, or the result is explained entirely by adapter capacity and connectivity-to-readout geometry.

### C4 — the frozen-core protocol tests a biologically meaningful form of reward-driven learning

**Falsifier / narrowing condition:** the behavior is learned entirely by external adapters/policy/value machinery while the biological core never changes, whereas the biological phenomenon being invoked depends materially on dopamine-gated synaptic plasticity or persistent eligibility/trace mechanisms inside the fly circuit.

### C5 — delayed rewards need not be solved before the first driving run; delay tolerance can be measured after a minimal closed-loop baseline

This is an experimental-ordering claim rather than a novelty claim.

**Falsifier / narrowing condition:** the minimal loop cannot learn even the C1 task without an explicit temporal-credit mechanism, or a delayed-reward sweep shows immediate collapse at delays substantially smaller than those tolerated by matched controls.

### C6 — degree-preserving rewiring is an adequate topology control for confirmatory inference

**Falsifier / narrowing condition:** results depend strongly on the particular rewiring, initialization, spectral/activity scale, weight/sign assignment, or optimizer trajectory.

### C7 — one-actuator/one-signal curriculum is an appropriate first step before full driving complexity

**Falsifier / narrowing condition:** the staged task removes the very recurrent/multimodal structure necessary for the hypothesized advantage and systematically produces false negatives relative to a still-small closed-loop task.

## 2. Claim-specific temporal reconstruction

The claims do not share one cutoff.

- **Reality-bounded car interface + one-actuator/one-signal curriculum (C7):** PR #526, `experiment: start reality-bounded MaleCNS car interface`, was created **2026-09-18 20:26:52 UTC**. Its public description already states the Android+OBD reality boundary, E0–E6 ladder and “curriculum from one actuator + one signal.” This is the conservative cutoff for that claim family.
- **Whole-connectome, biologically addressed sensory/reward/action closed loop (C1–C5):** commit `c28695a4fe21730733e2d7da2d3802e9c0d6b92f`, dated **2026-09-19 13:21:09 UTC**, added the explicit biological-interface contract to `malecns_connectome_reservoir_tagging.md` on PR #657. Because Git commit time alone does not prove public branch exposure, the conservative public cutoff is the PR merge time, **2026-09-19 13:32:09 UTC**. The candidate prior art below predates either timestamp, so this ambiguity does not affect classification.
- **Exact frozen protocol / confirmatory decision rule / full comparator bundle (C1–C7 as a preregistered conjunction):** PR #699 was created **2026-09-19 17:30:51 UTC** and merged at 17:31:17 UTC. This later freeze does not reset priority for claim components already public in #526/#657.

## 3. Search protocol

Primary sources were prioritized: arXiv version histories, peer-reviewed publisher pages, PubMed and repository history. Discovery queries covered modern and historical terminology around whole-brain connectome controllers, connectome-constrained reinforcement learning, frozen biological reservoirs, degree-preserving nulls, reward pathways, synaptic plasticity and delayed reinforcement.

Representative overlap queries:

- `whole brain Drosophila connectome reinforcement learning embodied control`
- `adult fly connectome controller degree preserving rewired`
- `Drosophila connectome fixed recurrent network trainable readout`
- `biological processing unit connectome frozen recurrent`
- `connectome reservoir random topology spectral radius`
- `Drosophila sensory motor connectome closed loop reinforcement`

Representative adversarial queries:

- `connectome topology advantage disappears degree preserving rewired initialization`
- `connectome constrained neural network null model confound`
- `Drosophila reward dopamine synaptic plasticity KC MBON`
- `Drosophila trace conditioning delayed reward dopamine`
- `delayed dopamine energy appetitive long term memory Drosophila`
- `connectome reservoir underperform spectral radius regularization`

Exact-title and decomposed post-cutoff searches were also run for the local protocol conjunction. No post-cutoff external work material to the exact conjunction was located in the short window.

## 4. Pre-cutoff novelty / overlap

### 4.1 FlyGM directly occupies whole-connectome embodied reinforcement control

**Zehao Jin, Yaoye Zhu, Chen Zhang, Yanan Sui, “Whole-Brain Connectomic Graph Model Enables Whole-Body Locomotion Control in Fruit Fly.”** arXiv v1 **2026-02-20 05:09:28 UTC**: https://arxiv.org/abs/2602.17997

FlyGM uses the complete adult Drosophila connectome as a directed controller from afferent inputs through intrinsic neurons to efferent motor outputs, closes the loop through a biomechanical fly body, trains with imitation followed by PPO, and compares against a degree-preserving rewired graph, an Erdős–Rényi graph and MLPs.

**Classification:** `prior_art` for the broad claims “whole adult Drosophila connectome in embodied closed-loop control,” “RL around a connectome-constrained policy,” and “degree-preserving rewiring/random/MLP as structural comparators.” Compared claims: C1, C6.

Important residual distinction: FlyGM freezes the synaptic graph operator but learns per-neuron intrinsic descriptors, a shared neural update function, encoder/gating and decoder. It therefore does **not** anticipate the narrower local claim of a frozen biological core whose trainable capacity is deliberately pushed outside the connectome. Its body/task is also a fly, not a reality-bounded car/phone interface.

**Classification for the exact local architecture:** `partial_prior_art`.

### 4.2 Biological Processing Units already establish a fixed connectome core with trained external machinery

**Siyu Yu et al., “Biological Processing Units: Leveraging an Insect Connectome to Pioneer Biofidelic Neural Architectures.”** arXiv v1 **2025-07-15 03:31:57 UTC**: https://arxiv.org/abs/2507.10951

The paper converts the complete larval Drosophila connectome into a fixed recurrent Biological Processing Unit and trains surrounding models/readouts on image and chess tasks.

**Classification:** `prior_art` for the generic architectural pattern `fixed Drosophila connectome core + trainable external interface/readout`; `adjacent_prior_work` for embodied closed-loop control. Compared claim: C2.

### 4.3 Connectome reservoirs and topology/weight ablations are established before the local protocol

**Leone Costi et al., “The Drosophila Connectome as a Computational Reservoir for Time-Series Prediction.”** submitted **2025-04-13**, published **2025-05-21**, DOI: https://doi.org/10.3390/biomimetics10050341

The work constructs fixed recurrent reservoirs from the Drosophila connectome, compares connectome topology/weights against randomized and hybrid alternatives, and includes a whole-connectome reservoir experiment.

**Classification:** `prior_art` for frozen-connectome reservoir computation and topology/weight ablation. Compared claims: C2, C6.

### 4.4 The exact local conjunction was not located

No pre-cutoff source was located that combines all of the following in one protocol: **MaleCNS specifically; a frozen whole-connectome core; biologically declared sensory/reward/aversive/action populations; a real-car-equivalent Android+OBD observation boundary; staged one-actuator/one-signal driving curriculum; matched rewired/random/adapter/conventional controls; and a frozen confirmatory split/decision rule.**

That is a bounded negative search result, not a firstness claim. Novelty of the combination must not be confused with novelty of its occupied components.

## 5. Falsification / contrary-evidence ledger

### 5.1 Biological-topology advantage is fragile to null design and initialization

**Nalin Dhiman, “Topological Sensitivity in Connectome-Constrained Neural Networks.”** arXiv v1 **2026-04-05 09:23:01 UTC**: https://arxiv.org/abs/2604.04033

Under weak controls, a Drosophila-connectome network appeared superior. Shared random initialization removed the early-loss advantage; replacing a weak random null with a degree-preserving null removed the apparent activity advantage; a five-sample degree-preserving ensemble strengthened the revised interpretation. The paper concludes that apparent topology advantages can arise from initialization and null-model confounds and largely disappear under stricter controls.

**Classification:** `contrary_evidence`, strength **strong**, against any broad claim that biological topology itself should improve learning; `boundary_condition`, strength **strong**, for C1/C6. It attacks mechanism attribution, not the possibility that this particular whole-CNS closed-loop task may show an effect.

**Required action:** `add_control + downgrade_confidence`. A confirmatory topology claim must use multiple independently rewired null graphs and matched from-scratch initialization/resource accounting. A single rewiring remains acceptable for a fast exploratory C1 smoke test, but not for a publication-level causal topology inference.

### 5.2 Connectome-reservoir advantage depends materially on dynamical regime

Costi et al. report that connectome reservoirs outperform classical reservoirs near spectral radius 0.99 in their tested setting, but become equivalent or worse at lower spectral radii; at 0.25 the classical ESN is consistently better with few exceptions. Under stronger regularization (`beta=10^-3`), the connectome topology+weights architecture often has the highest error. They also find weight distribution can contribute more than topology in some conditions.

**Classification:** `boundary_condition`, strength **strong**, for generalization of C1/C2; `contrary_evidence`, strength **moderate**, against a topology-only mechanism.

**Required action:** `add_boundary_condition + add_control`. Record activity/spectral/dynamical scale and prevent a favorable dynamical normalization from being silently treated as topology evidence.

### 5.3 A frozen core does not test a major known biological mechanism of reward learning

Drosophila associative learning is not merely a scalar reward arriving at a fixed recurrent graph. **Bennett, Philippides & Nowotny, “Learning with reinforcement prediction errors in a model of the Drosophila mushroom body,” Nature Communications, 2021-05-07**, https://doi.org/10.1038/s41467-021-22592-4, summarizes and models reinforcement through dopamine-dependent modulation of plasticity at Kenyon-cell-to-mushroom-body-output-neuron synapses.

This creates a direct interpretive boundary: if the MaleCNS adjacency/weights are frozen and all long-term learning occurs in external adapters/policy/value machinery, success demonstrates usefulness of a **frozen connectome-constrained dynamical substrate under external learning**, not that the simulated fly circuit learned by its biological reinforcement mechanism.

**Classification:** `boundary_condition`, strength **strong**, for C4; `contrary_evidence`, strength **strong**, against the stronger mechanistic interpretation “this frozen-core protocol tests how the fly learns.”

**Required action:** `narrow_claim + revise_mechanism`. Keep the first driving experiment simple and frozen-core, but name it correctly. A biologically motivated local-plasticity arm should be a later discriminating experiment if reward/credit assignment becomes an observed failure mode, not a prerequisite that delays C1.

### 5.4 Real Drosophila already solves non-zero temporal gaps through internal traces and delayed reinforcement biology

Pre-cutoff evidence includes:

- **“Olfactory trace conditioning in Drosophila”** (2011), PMID 21593308: flies associate odor and shock across a several-second gap, with persistent odor-specific neural traces.
- **Galili et al., “Distinct molecular underpinnings of Drosophila olfactory trace conditioning”** (PNAS, 2011/2012), DOI: https://doi.org/10.1073/pnas.1107489109: mushroom body and D1 dopamine signaling are required for trace conditioning across separated events.
- **Musso, Tchenio & Preat, “Delayed dopamine signaling of energy level builds appetitive long-term memory in Drosophila”** (Cell Reports, online 2015-02-19), DOI: https://doi.org/10.1016/j.celrep.2015.01.036: delayed post-ingestion energy signals and a delayed dopaminergic calcium trace support appetitive long-term memory.
- **Grover et al., “Differential mechanisms underlie trace and delay conditioning in Drosophila”** (Nature, 2022-02-16), DOI: https://doi.org/10.1038/s41586-022-04433-6: persistent ring-neuron activity and dopamine receptor signaling bridge a trace interval.

These results support the user's motivating intuition that the biological system contains mechanisms for delayed reinforcement, but they do **not** imply that a frozen connectome graph automatically inherits them: some mechanisms depend on state persistence and some on plasticity/receptor dynamics absent from a static graph model.

**Classification:** `adjacent_prior_work` for C5; `boundary_condition`, strength **strong**, for extrapolating from connectome topology alone to biological credit assignment.

**Required action:** `no_change` to the drive-first ordering; `add_control` only after the baseline. Measure a reward-delay sweep rather than pre-solving delay. If performance collapses, then compare external eligibility/credit and biologically motivated local-plasticity variants.

### 5.5 Reward pathways are not a context-free positive/negative scalar decomposition

Drosophila dopaminergic reinforcement pathways also encode movement/context, expectation and state; reward and aversion depend on compartment, timing and circuit state. A biologically typed appetitive/aversive/omission interface is therefore a useful engineering abstraction, not a complete model of fly reward biology.

**Classification:** `boundary_condition`, strength **moderate**, for C3/C4.

**Required action:** `narrow_claim`. Do not block C1 by adding a complete dopamine model; simply keep the abstraction explicitly provisional and separately logged.

## 6. Alternative explanations and stronger baselines

A positive C1 result has several simpler explanations than “the fly brain has learned to drive”:

1. the connectome supplies a useful generic recurrent reservoir;
2. degree distribution, synaptic-weight distribution or dynamical scale — not higher-order topology — explains the gain;
3. the external adapters/policy/value learner performs most of the task;
4. favorable initialization or one lucky rewired null exaggerates the biological arm;
5. biologically named input/output locations happen to provide convenient graph distances rather than biologically meaningful computation.

The confirmatory baseline ladder should therefore retain the current adapter-only and conventional controller arms, use matched from-scratch initialization, and evaluate an **ensemble** of independently degree-preserving rewired nulls. A random biological-interface-location ablation is the clean discriminator for C3.

None of these controls should be turned into a reason to postpone the first closed-loop drive. The highest-value sequence remains:

`minimal lawful perception → whole MaleCNS → action → immediate/proximal reward → observe failure → add only the discriminator suggested by that failure`.

## 7. Post-cutoff evidence

For the exact protocol freeze, the latest cutoff is **2026-09-19 17:30:51 UTC**. The only located repository activity immediately afterward is internal readiness bookkeeping; no external scholarly work whose first public disclosure falls after this cutoff and materially overlaps the exact protocol conjunction was found.

No `later_independent`, `later_overlap`, `later_non_citing`, `later_citing`, or `later_derivative` label is assigned. The post-cutoff window is extremely short, so this is weak negative evidence.

## 8. Priority / truth-status matrix

| claim | priority | truth status after audit | required action |
|---|---|---|---|
| C1 whole-connectome embodied control/topology advantage | broad mechanism `prior_art` via FlyGM; exact MaleCNS-car frozen-core conjunction not located | plausible but topology attribution fragile | `add_control + downgrade_confidence` |
| C2 frozen core + thin trainable interface | `prior_art` in generic form via BPU/connectome reservoirs | valid architecture class; no evidence yet for driving advantage | `no_change` to protocol, `add_boundary_condition` |
| C3 biological sensory/reward/action addressing matters | components biologically established; exact car-interface test not located | untested; could be graph-position convenience | `add_control` random-location ablation |
| C4 frozen core represents biological reward learning | not defensible as a broad mechanistic claim | strong boundary: major fly learning mechanisms involve internal plasticity | `narrow_claim + revise_mechanism` |
| C5 do not pre-solve delayed reward before C1 | not a novelty claim | strengthened as experimental ordering; fly biology motivates a later delay sweep | `no_change`; add diagnostic after baseline |
| C6 degree-preserving null is sufficient | basic null `prior_art` | one null realization is insufficient for strong topology inference | `add_control` rewired ensemble + shared init |
| C7 one-actuator/one-signal first curriculum | local design; no firstness claim made | reasonable exploratory simplification, but not a topology proof | `no_change` |

## 9. Resulting claim boundary

The defensible near-term experiment is narrower and cleaner:

> Test whether a frozen whole-MaleCNS connectome, used as a biologically addressed recurrent substrate inside a minimal lawful closed control loop, provides task-level benefit over matched null substrates and conventional controls. Do not interpret success as reproduction of Drosophila reinforcement learning unless internal biological plasticity/trace mechanisms are separately implemented and discriminated.

The audit therefore strengthens — rather than delays — the drive-first programme. FlyGM proves that whole-connectome embodied control is already a real experimental class worth benchmarking against; the open question is whether the more restrictive **frozen MaleCNS + reality-bounded car + biological-addressing** formulation contributes anything once fair nulls are used.