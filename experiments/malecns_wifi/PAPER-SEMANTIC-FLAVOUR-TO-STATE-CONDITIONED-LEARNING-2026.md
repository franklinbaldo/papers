---
type: "Paper Draft"
title: "From Semantic Flavours to State-Conditioned Peer Learning"
description: "Why progressively structured peer learning around a frozen recurrent connectome may be more promising than using the connectome as a static feature transform."
tags: [malecns, semantic-flavour, peer-learning, reliability, directed-learning, state-conditioned, closed-loop]
timestamp: 2026-09-16T16:00:00-04:00
status: draft
---

# From Semantic Flavours to State-Conditioned Peer Learning

## Abstract

Most experiments with frozen connectomes ask a static question: can a biological recurrent graph transform an input representation into a better feature space for a downstream readout? This paper develops a different research programme. We argue that the strongest use of a frozen recurrent connectome may not be as a classifier, encoder, or replacement for a conventional neural network, but as a **shared dynamical context that regulates learning among heterogeneous semantic channels**.

The programme is an architectural ladder:

`semantic flavour → coupled flavour → reliability → directed reliability → state-conditioned feedback`

Each rung repairs a specific weakness of the previous one. Semantic flavours give channels task-specific directions rather than anonymous scalar scores. Coupling allows channels to transfer information. Reliability prevents weak channels from teaching as strongly as strong ones. Directed reliability recognizes that teaching ability is relation-specific: channel `j` may be useful for channel `i` without being equally useful for channel `k`. State conditioning makes this relation depend on the current recurrent MaleCNS state, so the amount of peer teaching can vary with context, uncertainty, disagreement, reward error, missing channels, and recent history.

The resulting closed learning loop is:

`channel_i → MaleCNS state → confidence/error/context → how much channel_j teaches channel_i → updated channel_i → new MaleCNS state → ...`

This construction combines ideas from reservoir computing, mutual learning, confidence-weighted learning, mixture-of-experts style specialization, and neuromodulatory/state-dependent plasticity. Our hypothesis is not that biological wiring is automatically superior to artificial recurrence. It is that a large fixed recurrent graph can serve as a **contextual plasticity controller**: a high-dimensional state machine that decides when and how external trainable components should learn from one another.

We state falsifiable predictions for every rung of the ladder and describe the experiments needed to distinguish genuine state-dependent coordination from simpler explanations such as ensembling, fixed averaging, parameter count, or generic recurrence.

---

## 1. The change in question

The simplest MaleCNS language architecture is:

`embedding → MaleCNS → readout`

That architecture asks whether the connectome computes a representation that is useful to a downstream decoder. It is scientifically clean and remains an important baseline. But it uses the recurrent graph only as a fixed transformation. The graph has memory and high-dimensional state, yet the learning rule outside the graph does not use that state to decide how learning itself should proceed.

The programme studied here asks a stronger question:

> Can the recurrent state of a frozen connectome become part of the learning rule of the surrounding system?

Instead of demanding that MaleCNS directly solve the semantic task, we ask it to help answer a meta-level question: **given the current inputs, history, channel agreement and task error, which semantic channel should influence which other channel, and by how much?**

This is attractive because the task is naturally contextual. A semantic view that is reliable on one expression, scale or lexical regime can be misleading on another. A fixed peer weight cannot represent that variation. A state-dependent recurrent controller potentially can.

---

## 2. The architectural ladder

### 2.1 Semantic flavour: from scalar relevance to direction

A scalar score can say that a chunk is relevant, but it cannot express *what kind* of relevance is present. A semantic flavour assigns a task- or concept-specific direction in an embedding space. The same input representation can therefore be compared against multiple concept directions without collapsing all structure into one scalar too early.

This matters for two reasons.

First, the system can preserve geometry among concepts. Similar concepts may induce related directions, while unrelated concepts need not share the same activation axis.

Second, a flavour becomes an object that can itself move during learning. Instead of training only a final classifier, the architecture can modify the local semantic reference by which a channel interprets evidence.

**Prediction F1.** A trainable flavour should outperform an otherwise matched fixed/random flavour when the task requires semantic generalization rather than memorization.

**Control.** Equal-capacity random codebooks and direct linear probes.

### 2.2 Coupled flavour: channels become peers

Independent channels discard a major source of information: disagreement and agreement across representations. MiniLM at one scale, E5 at another scale, or any pair of heterogeneous encoders do not make identical errors. Coupling lets one channel provide a soft training signal to another.

This is related to mutual-learning results in which peer networks can improve by teaching each other during training without requiring a single privileged teacher. The important shift is from isolated optimization to a population of learners whose trajectories are partly coupled.

A generic peer target for receiver `i` can be written:

`teacher_i = (1 - α) * hard_target + α * peer_evidence_i`

The hard target remains primary. Peer evidence is an auxiliary plasticity signal rather than a replacement for supervision.

**Prediction F2.** Coupled channels should improve held-out semantic generalization or missing-channel robustness relative to independent training, even when inference-time architecture is unchanged.

**Control.** Independent channels with identical initialization, optimization and parameter count.

### 2.3 Reliability: peers should not vote equally

Coupling introduces a new failure mode: a weak or systematically biased channel can contaminate the others. Equal peer averaging assumes exchangeability that is rarely true for heterogeneous encoders and scales.

Reliability weights address this by estimating channel competence from training data only. For sender `j`, a simple scalar reliability may be:

`r_j ∝ exp(-L_j)`

where `L_j` is a pre-learning or early-training balanced loss. The peer evidence received by `i` becomes a weighted combination of the other channels rather than a flat mean.

This step changes the role of disagreement. Disagreement is no longer averaged away blindly; it is interpreted through an estimate of which channels have earned more influence.

**Prediction F3.** Reliability-weighted coupling should outperform equal coupling on held-out generalization and degrade less severely when a noisy/weak channel is present.

**Controls.** Equal-weight coupling; shuffled reliability weights; reliability computed from disjoint training data; no validation-derived weights.

### 2.4 Directed reliability: teaching is relational

A scalar `r_j` still assumes that sender quality is universal. But teaching is not a unary property of a sender; it can be a property of a sender-receiver pair.

One encoder may be especially useful for correcting another encoder at short scales but redundant for a third encoder at long scales. Therefore the natural object is a directed matrix:

`R[j → i]`

with zero diagonal and receiver-specific normalization.

A useful decomposition is:

`R[j → i] = competence(j) × need(i) × compatibility(j, i)`

where all terms must be estimated without validation leakage.

This turns peer learning into a directed graph over semantic channels. The graph of learning need not match the graph used at inference.

**Prediction F4.** Directed reliability should beat scalar reliability when channel errors are heterogeneous and complementary, but should converge toward scalar behavior when channels become exchangeable.

**Controls.** Row/column-shuffled directed matrices; symmetric `R`; scalar reliability broadcast to every receiver; equal coupling.

### 2.5 State-conditioned feedback: influence should depend on the current situation

Even a directed matrix is static. It says that `j` is generally useful for `i`, but not whether `j` is useful **now**.

This is the key step. Let `x_t` be the recurrent MaleCNS state after processing the current multi-channel evidence and recent history. We define a state-dependent peer gain:

`λ_{j→i,t} = λ_max · g(x_t, e_t, j, i)`

where `e_t` may include a training-only reward/error signal and `g` is a bounded gate.

Two simple gates already define useful falsifiable cases:

- **uncertainty gate:** peer teaching increases when the current state is uncertain;
- **reward-error gate:** peer teaching increases when the current state disagrees with the available training reward.

More generally, the state can encode recent context, channel conflict, sequence history and dynamical regime. The recurrent substrate therefore becomes a controller of plasticity rather than merely a feature transform.

**Prediction F5.** State-conditioned directed coupling should outperform the best static directed rule when reliability changes across examples or through time, while offering little or no advantage on stationary exchangeable data.

**Critical control.** Replace MaleCNS with matched random recurrent reservoirs. If state-conditioned learning improves equally under generic recurrence, the result supports the architecture but not biological topology specifically.

---

## 3. Why a recurrent state is a natural plasticity signal

Reservoir computing provides a useful conceptual foundation. A fixed recurrent system maps current and recent inputs into a high-dimensional state that can expose temporal and nonlinear structure to a simple trainable readout. The same property can be used one level higher: instead of reading `x_t` only to predict the task output, the system can read `x_t` to predict **how learning should be routed**.

This is a crucial distinction:

- conventional reservoir use: `x_t → prediction`;
- proposed use: `x_t → plasticity policy`.

The latter may require less from the reservoir. MaleCNS need not linearly separate every semantic class. It only needs to carry enough information to distinguish learning regimes such as "channels agree", "channel A is failing", "evidence is ambiguous", "recent context supports channel B", or "the system is currently confident and peer teaching should shut down".

That makes the hypothesis plausible even if direct MaleCNS classification remains modest.

---

## 4. Why the progression is stronger than any single rung

The ladder is cumulative because each stage introduces information that the previous one cannot represent:

| Stage | New information available to the learning rule | Failure it addresses |
| --- | --- | --- |
| semantic flavour | concept direction | scalar relevance is semantically anonymous |
| coupled flavour | cross-channel evidence | independent learners cannot transfer complementary information |
| reliability | sender competence | equal peer voting propagates bad teachers |
| directed reliability | sender→receiver usefulness | competence is not universally transferable |
| state-conditioned feedback | current context/history/error | static relationships cannot adapt example by example |

The important scientific object is therefore not one magic formula. It is the **monotonic increase in conditional structure available to plasticity**.

Each rung should only survive if its added conditional information earns measurable predictive value. This gives the programme unusually clean ablations: remove one conditioning variable at a time and observe whether performance, robustness or calibration deteriorates.

---

## 5. Why MaleCNS might be especially useful here

There are three increasingly strong hypotheses, and the experiments must keep them separate.

### H1 — recurrence hypothesis

Any sufficiently rich recurrent state may improve state-conditioned peer learning. If a matched random ESN works as well as MaleCNS, this hypothesis is supported and the biological topology claim is not.

### H2 — structured-reservoir hypothesis

MaleCNS topology may produce a more useful plasticity state than matched random recurrence because its heterogeneous connectivity, recurrent motifs, sensory convergence and descending organization create nonuniform dynamical responses to conflicting inputs.

### H3 — biological-topology hypothesis

The specific biological wiring may provide a measurable advantage over degree-preserving, weight-preserving, rewired or otherwise matched controls. This is the strongest and hardest claim and must not be assumed from H1/H2.

The architecture is scientifically useful even if only H1 survives. H2 and H3 determine whether the fly connectome itself contributes beyond the generic computational principle.

---

## 6. The closed-loop view

The natural endpoint of the programme is not a one-shot transformation but a recurrent learning loop:

```text
semantic channels
      ↓
local adapters + flavours
      ↓
MaleCNS recurrent state x_t
      ↓
confidence / disagreement / reward error
      ↓
directed peer-plasticity matrix Λ_t
      ↓
adapter + flavour updates
      ↓
changed semantic drives at t+1
      └────────────────────────────→ MaleCNS
```

The output of the system changes the conditions of its next input. This makes the architecture closer to an adaptive dynamical system than to a conventional frozen feature extractor.

Importantly, no biological synapse needs to be trained for this claim. MaleCNS can remain frozen while the external interfaces learn under a state-dependent policy derived from its dynamics.

---

## 7. Experimental programme

### Experiment A — ladder ablation

Using identical semantic caches, seeds, adapters, optimizer, projections and train/validation splits, compare:

1. independent semantic flavours;
2. equal peer coupling;
3. scalar reliability coupling;
4. directed reliability coupling;
5. directed + state-uncertainty gate;
6. directed + reward-error gate.

Primary readouts should include held-out semantic generalization and global task performance. Secondary readouts should include missing-channel robustness, variance across seeds, calibration, realized peer weights and adapter movement.

### Experiment B — topology control

Repeat the strongest state-conditioned arm with:

- MaleCNS;
- degree-preserving rewiring;
- partial rewiring continuum;
- matched sparse random recurrent reservoir;
- self-recurrent/diagonal control;
- no recurrence.

This separates "state conditioning works" from "MaleCNS biology matters".

### Experiment C — nonstationary reliability

Construct or identify regimes where channel competence changes across examples or time. The prediction is specific: static reliability should become suboptimal, while state-conditioned routing should gain relative advantage.

### Experiment D — missing and corrupted channels

Drop or corrupt expensive semantic channels at inference. A useful peer-learning architecture should have learned distributed semantic competence rather than dependence on one dominant teacher.

### Experiment E — transfer beyond tagging

The strongest test of architectural generality is to keep the same state-conditioned peer-learning core and change only the environment/adapters:

- embedding-space translation;
- sequence tagging / NER;
- semantic multilabel tagging;
- waveform/TTS control;
- visual or embodied control.

If the same learning controller transfers across these tasks, the claim becomes one about a general `MaleCNSClosedLoop` architecture rather than one benchmark.

---

## 8. Failure modes and falsification

The programme should be considered unsuccessful, or substantially narrowed, under any of the following outcomes:

1. equal coupling consistently matches all reliability-based variants;
2. directed reliability does not beat scalar reliability when channel complementarity is demonstrably asymmetric;
3. state-conditioned gates collapse to nearly constant values and behave like a tuned static lambda;
4. improvements vanish under fresh seeds;
5. gains are explained entirely by parameter count or additional optimization steps;
6. direct disagreement statistics without recurrence predict the same gates as well as MaleCNS state;
7. matched random recurrence consistently equals or beats MaleCNS, eliminating a biological-topology interpretation;
8. peer learning improves validation metrics only when reliability/gates have access to validation information.

These are productive negative results: each one identifies which rung of the ladder adds no measurable information.

---

## 9. Relation to prior work

This programme is intentionally compositional rather than claiming that any individual mechanism is new in isolation.

**Reservoir computing.** Fixed recurrent reservoirs are well established as high-dimensional dynamical mappings for temporal/sequential signals. See Lukoševičius & Jaeger, *Reservoir computing approaches to recurrent neural network training*, Computer Science Review 3(3), 2009, DOI: 10.1016/j.cosrev.2009.03.005; and Tanaka et al., *Recent advances in physical reservoir computing: A review*, Neural Networks 115, 2019, DOI: 10.1016/j.neunet.2019.03.005.

**Mutual learning.** Peer models can teach one another during training without a privileged fixed teacher. See Zhang et al., *Deep Mutual Learning*, CVPR 2018, arXiv:1706.00384.

**Uncertainty- and difficulty-weighted learning.** Curriculum/self-paced methods provide precedent for changing learning weight according to estimated difficulty or uncertainty. The present proposal differs in using the shared recurrent state as part of that controller rather than treating difficulty as a static sample property.

**State-dependent plasticity and neuromodulation.** Biological and machine-learning models of neuromodulation motivate separating the fast activity state from the slower rule that decides when plasticity should occur. Our construction is deliberately modest: MaleCNS is not claimed to reproduce a biological learning rule; its state is tested as a computational signal for gating external plasticity.

The proposed contribution is the **specific composition and experimental ladder**: semantic flavour, peer coupling, reliability, directed reliability and recurrent state conditioning, evaluated under topology-matched controls.

---

## 10. Current implementation mapping

The repository already contains successive approximations to this ladder:

- semantic/coupled flavour experiments;
- PR #452: reliability-weighted peer coupling;
- PR #453: fresh-seed reliability replication;
- PR #454: directed sender→receiver teaching gains;
- PR #459: coupling-strength regimes;
- PR #460: state-conditioned peer coupling using MaleCNS uncertainty and reward error.

PR #460 is therefore not an isolated experiment. It is the current endpoint of a cumulative architectural programme.

The next clean experiment should compare the whole ladder under a common runner rather than treating each historical PR as an unrelated branch.

---

## 11. Central claim boundary

The strongest claim this programme can eventually support is:

> A fixed recurrent connectome can provide a useful context-dependent state for controlling directed plasticity among heterogeneous trainable semantic channels.

A stronger biological claim requires topology controls:

> The specific MaleCNS wiring provides a better plasticity-control state than appropriately matched artificial recurrent graphs.

Until those controls win, the first claim and the second claim must remain separate.

---

## 12. The reason this direction is promising

The architecture gives the connectome a job that is unusually well matched to what recurrence naturally provides.

We do not ask 165,122 frozen neurons to become a modern language model. We ask them to maintain a rich dynamical summary of what the surrounding learners are experiencing, and to use that summary to modulate who should teach whom next.

That turns MaleCNS from a strange fixed layer inserted between embeddings and a decoder into something more coherent:

**a recurrent context engine for plasticity.**

If successful, that role is reusable. The semantic channels can later be replaced by embedding translators, NER heads, audio adapters, visual receptors or motor controllers without changing the core principle.

That is why the progression

`semantic flavour → coupled flavour → reliability → directed reliability → state-conditioned feedback`

is more interesting than any one of its stages in isolation: it is the shortest path we currently have from "use a fly connectome as a reservoir" to a general closed-loop learning architecture in which the connectome participates in deciding how learning itself unfolds.
