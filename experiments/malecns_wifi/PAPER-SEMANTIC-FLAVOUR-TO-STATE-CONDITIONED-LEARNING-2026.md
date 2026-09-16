---
type: "Paper Draft"
title: "From Semantic Flavours to State-Conditioned Memory and Spectral Action"
description: "Why progressively structured peer learning, state-conditioned external memory, cycle consistency, and embodied spectral action around a frozen recurrent connectome may be more promising than using the connectome as a static feature transform."
tags: [malecns, semantic-flavour, peer-learning, reliability, directed-learning, state-conditioned, external-memory, vector-search, cycle-consistency, spectral-action, closed-loop]
timestamp: 2026-09-16T16:00:00-04:00
status: draft
---

# From Semantic Flavours to State-Conditioned Memory and Spectral Action

## Abstract

Most experiments with frozen connectomes ask a static question: can a biological recurrent graph transform an input representation into a better feature space for a downstream readout? This paper develops a different research programme. We argue that the strongest use of a frozen recurrent connectome may not be as a classifier, encoder, or replacement for a conventional neural network, but as a **shared dynamical context that regulates learning, memory access, and action among heterogeneous semantic channels**.

The programme is an architectural ladder:

`semantic flavour → coupled flavour → reliability → directed reliability → state-conditioned feedback → state-conditioned external memory → bidirectional cycle consistency → embodied spectral navigation`

Each rung repairs a specific weakness of the previous one. Semantic flavours give channels task-specific directions rather than anonymous scalar scores. Coupling allows channels to transfer information. Reliability prevents weak channels from teaching as strongly as strong ones. Directed reliability recognizes that teaching ability is relation-specific: channel `j` may be useful for channel `i` without being equally useful for channel `k`. State conditioning makes this relation depend on the current recurrent MaleCNS state, so the amount of peer teaching can vary with context, uncertainty, disagreement, reward error, missing channels, and recent history.

The next step moves memory itself outside the connectome. A deterministic vector database stores paired observations from embedding spaces A and B. The database does not learn. Instead, the recurrent MaleCNS state helps decide **how to query it, which neighbourhood to inspect, how much confidence to place in the retrieved neighbourhood, and whether another retrieval/action cycle is needed**. The system therefore does not need to compress semantic memory into biological synapses or adapter weights: it can learn a policy for using arbitrarily large external memory.

Bidirectional retrieval and cycle consistency then provide an inference-time self-check. A candidate translation `A → B̂` is mapped back through the external memory `B → Â`; disagreement between `Â` and the original A is evidence that the current transformation is geometrically inconsistent even when the exact supervised B target is absent. Finally, the descending output of MaleCNS can be interpreted as motor control over spectral deformations of the embedding geometry. The fly does not need to output B directly; it can learn a policy for repeatedly changing the geometry of A until memory plausibility, cycle consistency, and—when supervision is available—target similarity improve.

The resulting closed loop is therefore broader than peer learning alone:

`semantic state → MaleCNS state → what to retrieve / whom to trust / how to move → external memory + spectral action → changed semantic state → new MaleCNS state → ...`

This construction combines ideas from reservoir computing, mutual learning, confidence-weighted learning, associative memory, non-parametric retrieval, cycle consistency, and state-dependent plasticity. Our hypothesis is not that biological wiring is automatically superior to artificial recurrence. It is that a large fixed recurrent graph can serve as a **contextual controller** for plasticity, retrieval, and action: a high-dimensional state machine that decides when and how external trainable components should learn, what external memory should be consulted, and how the represented geometry should be changed.

We state falsifiable predictions for every rung of the ladder and describe the experiments needed to distinguish genuine state-dependent coordination from simpler explanations such as ensembling, fixed averaging, ordinary kNN retrieval, gradient descent in embedding space, parameter count, or generic recurrence.

---

## 1. The change in question

The simplest MaleCNS language architecture is:

`embedding → MaleCNS → readout`

That architecture asks whether the connectome computes a representation that is useful to a downstream decoder. It is scientifically clean and remains an important baseline. But it uses the recurrent graph only as a fixed transformation. The graph has memory and high-dimensional state, yet the learning rule outside the graph does not use that state to decide how learning itself should proceed.

The programme studied here asks a stronger question:

> Can the recurrent state of a frozen connectome become part of the learning, memory-access, and action policy of the surrounding system?

Instead of demanding that MaleCNS directly solve the semantic task, we ask it to help answer meta-level questions:

- given the current inputs, history, channel agreement and task error, which semantic channel should influence which other channel, and by how much?
- given the current semantic state, what should the system retrieve from an external associative memory?
- how confident should the system be in that retrieved neighbourhood?
- should it retrieve again, change the query, or act on the embedding geometry?
- after acting, did the new state become more compatible with the target manifold and more cycle-consistent with the original observation?

This is attractive because all of these questions are contextual. A semantic view that is reliable on one expression, scale or lexical regime can be misleading on another. A fixed peer weight cannot represent that variation. Likewise, a fixed nearest-neighbour query cannot represent the possibility that the useful memory depends on the current recurrent state and the trajectory taken so far. A state-dependent recurrent controller potentially can.

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

### 2.6 State-conditioned external memory: remembering by controlling retrieval

The previous stages still force most useful knowledge into trainable adapters, flavours, or the current recurrent state. That is unnecessarily restrictive. A frozen connectome need not internally store a large semantic corpus if it can learn how to use an external deterministic memory.

Let the external memory contain paired embeddings for the same observations in two spaces:

`M = {(a_i, b_i)}_{i=1..N}`

The database itself is non-parametric. It can be implemented as a vector index, cosine search, HNSW/FAISS-like index, DuckDB-backed store, or another deterministic retrieval system. Adding a new memory means adding a record, not retraining the connectome.

For a current A-space state `a_t`, the simplest retrieval is a top-k neighbourhood:

`N_k(a_t) = top-k_i cosine(a_t, a_i)`

with a local B-space reference given by a similarity-weighted barycenter:

`b̄_t = Σ_i w_i b_i / Σ_i w_i`

where the weights depend monotonically on the A-space similarity.

The important extension is that retrieval itself becomes state-conditioned. The MaleCNS state does not need to contain the memories; it can determine **how to index them**. Instead of always querying with `q_t = a_t`, the system may use:

`q_t = Q(a_t, x_t)`

where `x_t` is the current recurrent state. The state may control a query displacement, spectral weighting, temperature, top-k width, feature weighting, A/B balance, or a learned projection used only to address the deterministic store.

The retrieved memory should return more than one vector. A useful sensory packet is:

`m_t = (b̄_t, similarity distribution, neighbourhood variance, retrieval confidence, neighbour identities, retrieval stability)`

and this packet becomes another input to MaleCNS. Retrieval is therefore not a one-shot preprocessing step but an action/perception loop:

`state → retrieval policy → memory → retrieved neighbourhood → new state → new retrieval policy → ...`

This resembles attention by movement rather than a conventional attention layer. The system changes what it can recall by changing its state and query trajectory.

**Prediction F6.** State-conditioned retrieval should outperform fixed-query top-k retrieval when the useful neighbourhood is context-dependent, while converging to the fixed-query baseline on locally smooth unambiguous regions.

**Controls.** Fixed cosine top-k; random query perturbations; direct learned retrieval projection without recurrence; matched random reservoir controlling the same retrieval parameters.

### 2.7 Bidirectional memory and cycle consistency: self-checking without the exact target

During supervised training, a paired target `b*` can directly score whether a transformation from A to B improved. At inference, the exact target is absent. A bidirectional external memory provides a deterministic substitute for part of this supervisory signal.

Maintain two views of the same paired store:

`M_{A→B}` and `M_{B→A}`.

Given a candidate translated point `b̂_t`, retrieve a reconstruction of the original space:

`â_t = M_{B→A}(b̂_t)`

and compare it with the original input `a_0`. The cycle error is:

`E_cycle(t) = d(â_t, a_0)`

A candidate that looks plausible in B but cannot reconstruct the original A is geometrically suspect. The exact supervised B target is therefore not required to detect every bad move.

This creates three distinct signals:

1. **memory plausibility:** is the candidate in a populated/consistent region of B?
2. **cycle consistency:** can it return to the original A?
3. **supervised target similarity:** when a true paired B target is available during training, did the move approach it?

At inference the third signal can disappear while the first two remain available.

The cycle can also be iterated:

`A_0 → B_1 → A_1 → B_2 → A_2 → ...`

with convergence defined by neighbourhood stability, small cycle error, and diminishing improvement.

**Prediction F7.** Bidirectional cycle checks should reject locally plausible but semantically destructive transformations that one-way retrieval accepts, and should improve out-of-memory generalization when exact test pairs are withheld from the store.

**Controls.** One-way memory only; shuffled A↔B pairing; cycle computed through an independently fitted linear map; exact-pair leakage checks.

### 2.8 Embodied spectral navigation: descending activity as action on embedding geometry

The final step treats translation not as a one-shot map `f(A)=B`, but as an iterative control problem over representation geometry.

Let the current representation be `z_t`. A Fourier-domain action can be written abstractly as:

`z_{t+1} = F^{-1}(H_{θ_t} ⊙ F(z_t))`

where `H_{θ_t}` may control amplitude, phase, band gains, local spectral mixing, or other constrained deformations. The parameters are determined from descending MaleCNS activity:

`θ_t = P(a_t^desc)`

or by a small trainable action adapter around the frozen connectome.

The key interpretation is that the descending layer becomes a **motor interface to semantic geometry**. The fly does not have to generate the target embedding directly. It learns which small deformations tend to improve correspondence.

With a supervised target available, a simple progress reward is:

`r_target(t) = sim(z_{t+1}, b*) - sim(z_t, b*)`

Positive progress is rewarded; movement in the wrong direction is penalized. Additional terms can reward reduced cycle error and penalize excessive deformation:

`r_t = α Δtarget + β Δcycle + γ Δmemory_plausibility - η ||action_t||²`

Crucially, the system should not be allowed to improve one direction by destroying the other. Candidate updates can be evaluated on a protected memory set and accepted only if they improve the joint bidirectional objective without unacceptable regression. This yields a conservative geometry-learning principle:

`improve B→A while preserving A→B; improve A→B while preserving B→A`.

The external paired memory supplies anchors across the manifold. The MaleCNS supplies a stateful policy for choosing local actions. Fourier operations supply a compact controllable family of geometric deformations.

This architecture makes the semantic world genuinely closed-loop:

```text
current embedding / retrieved memory
            ↓
        MaleCNS state
            ↓
   descending motor action
            ↓
 spectral geometry deformation
            ↓
      new embedding state
            ↓
      new memory retrieval
            ↓
 target progress / cycle error / plausibility
            └──────────────────────────────→ MaleCNS
```

**Prediction F8.** An iterative MaleCNS-controlled spectral policy should outperform (or achieve similar quality with fewer effective degrees of freedom than) fixed spectral filters, ordinary iterative kNN barycenters, and matched random recurrent controllers on held-out A↔B translation.

**Critical controls.** Diagonal transform in the original basis; diagonal Fourier filter; full linear ridge A→B; gradient-based spectral optimizer without MaleCNS; random ESN controller; no-memory controller.

---

## 3. Why a recurrent state is a natural plasticity, retrieval, and action signal

Reservoir computing provides a useful conceptual foundation. A fixed recurrent system maps current and recent inputs into a high-dimensional state that can expose temporal and nonlinear structure to a simple trainable readout. The same property can be used one level higher: instead of reading `x_t` only to predict the task output, the system can read `x_t` to predict **how learning should be routed, what memory should be consulted, and which action should be taken next**.

This is a crucial distinction:

- conventional reservoir use: `x_t → prediction`;
- proposed plasticity use: `x_t → plasticity policy`;
- proposed memory use: `x_t → retrieval policy`;
- proposed embodied use: `x_t → action on representation geometry`.

These latter jobs may require less from the reservoir than direct semantic decoding. MaleCNS need not linearly separate every semantic class or reconstruct B exactly. It only needs to carry enough information to distinguish regimes such as "channels agree", "channel A is failing", "evidence is ambiguous", "recent context supports channel B", "this retrieved neighbourhood is unstable", "the cycle is worsening", or "the system is currently confident and further movement should stop".

That makes the hypothesis plausible even if direct MaleCNS classification remains modest.

---

## 4. Why the progression is stronger than any single rung

The ladder is cumulative because each stage introduces information or control that the previous one cannot represent:

| Stage | New information/control available | Failure it addresses |
| --- | --- | --- |
| semantic flavour | concept direction | scalar relevance is semantically anonymous |
| coupled flavour | cross-channel evidence | independent learners cannot transfer complementary information |
| reliability | sender competence | equal peer voting propagates bad teachers |
| directed reliability | sender→receiver usefulness | competence is not universally transferable |
| state-conditioned feedback | current context/history/error | static relationships cannot adapt example by example |
| state-conditioned external memory | context-dependent access to large deterministic memory | useful knowledge need not fit in adapters or connectome state |
| bidirectional cycle consistency | inference-time geometric self-check | one-way plausibility can accept destructive translations |
| embodied spectral navigation | iterative action over representation geometry | one-shot maps cannot exploit recurrent search/control |

The important scientific object is therefore not one magic formula. It is the **monotonic increase in conditional structure and controllable feedback available to the system**.

Each rung should only survive if its added conditional information earns measurable predictive value. This gives the programme unusually clean ablations: remove one conditioning variable or action channel at a time and observe whether performance, robustness, calibration, retrieval quality, cycle consistency, or sample efficiency deteriorates.

---

## 5. Why MaleCNS might be especially useful here

There are three increasingly strong hypotheses, and the experiments must keep them separate.

### H1 — recurrence hypothesis

Any sufficiently rich recurrent state may improve state-conditioned peer learning, retrieval, or iterative action. If a matched random ESN works as well as MaleCNS, this hypothesis is supported and the biological topology claim is not.

### H2 — structured-reservoir hypothesis

MaleCNS topology may produce a more useful control state than matched random recurrence because its heterogeneous connectivity, recurrent motifs, sensory convergence and descending organization create nonuniform dynamical responses to conflicting inputs, retrieved memory, and action outcomes.

### H3 — biological-topology hypothesis

The specific biological wiring may provide a measurable advantage over degree-preserving, weight-preserving, rewired or otherwise matched controls. This is the strongest and hardest claim and must not be assumed from H1/H2.

The architecture is scientifically useful even if only H1 survives. H2 and H3 determine whether the fly connectome itself contributes beyond the generic computational principle.

---

## 6. The closed-loop view

The natural endpoint of the programme is not a one-shot transformation but a recurrent adaptive loop:

```text
semantic channels / current embedding
              ↓
      local adapters + flavours
              ↓
       MaleCNS recurrent state x_t
          ↙          ↓           ↘
 plasticity      retrieval       action
   policy          policy        policy
     ↓               ↓             ↓
peer updates   external memory   spectral move
     ↓               ↓             ↓
     └────── changed semantic world ──────┐
                                         ↓
                              new MaleCNS state x_{t+1}
```

The output of the system changes the conditions of its next input. This makes the architecture closer to an adaptive dynamical agent than to a conventional frozen feature extractor.

Importantly, no biological synapse needs to be trained for this claim. MaleCNS can remain frozen while the external interfaces learn under policies derived from its dynamics, and while factual/semantic memory lives in an ordinary deterministic database.

The conceptual separation is deliberate:

- **MaleCNS state:** transient contextual dynamics;
- **external vector memory:** durable semantic observations and A↔B correspondences;
- **trainable adapters:** policy interfaces that learn how to sense, retrieve, and act;
- **spectral action space:** constrained geometry-changing moves;
- **cycle/reward signals:** evidence about whether those moves improve correspondence.

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

The strongest test of architectural generality is to keep the same state-conditioned core and change only the environment/adapters:

- embedding-space translation;
- sequence tagging / NER;
- semantic multilabel tagging;
- waveform/TTS control;
- visual or embodied control.

If the same controller transfers across these tasks, the claim becomes one about a general `MaleCNSClosedLoop` architecture rather than one benchmark.

### Experiment F — associative memory translation

Build a large deterministic paired store `{(A_i, B_i)}` from texts encoded by two frozen embedding models. Withhold exact test pairs from the memory. Compare:

1. nearest-1 B retrieval;
2. top-k similarity-weighted B barycenter;
3. iterative top-k retrieval with a fixed query;
4. state-conditioned retrieval controlled by MaleCNS;
5. the same retrieval policy controlled by a matched random reservoir.

Measure similarity to the true held-out B, retrieval stability, neighbourhood entropy, and downstream task preservation.

A key success criterion is **improvement beyond the retrieved barycenter**. If the final produced B is closer to the unseen true B than the best deterministic memory estimate that seeded the trajectory, the system is doing more than copying memory.

### Experiment G — bidirectional cycle and conservative updates

Maintain deterministic A→B and B→A indices over the same paired memory. For each candidate spectral action, measure:

- A→B correspondence;
- B→A reconstruction;
- cycle error;
- regression on a protected memory set.

Candidate updates should be rejected or penalized when they improve one direction by damaging already-good correspondences in the other. Compare one-way optimization against a joint bidirectional objective.

### Experiment H — embodied spectral translation

Use descending MaleCNS activity to control incremental spectral transformations. Compare:

1. no transform;
2. fixed diagonal transform in the original basis;
3. fixed Fourier-diagonal transform;
4. full linear ridge A→B;
5. gradient-based iterative spectral optimization;
6. random recurrent controller + spectral actions;
7. MaleCNS controller + spectral actions;
8. MaleCNS controller + spectral actions + state-conditioned memory + cycle feedback.

Report target cosine similarity when supervised targets are available, held-out retrieval/downstream preservation, cycle error, number of action steps, action energy, and protected-memory regression.

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
8. peer learning improves validation metrics only when reliability/gates have access to validation information;
9. fixed top-k retrieval matches state-conditioned memory access, making recurrent retrieval control unnecessary;
10. exact-pair removal collapses performance, showing that the system copied memory rather than generalized locally;
11. cycle consistency fails to reject transformations that damage semantic correspondence;
12. Fourier-space actions provide no advantage in compactness, controllability, or performance over equally constrained transforms in the original basis;
13. iterative MaleCNS actions do not outperform a deterministic optimizer using the same memory and action family;
14. bidirectional improvement requires degrading previously good A↔B correspondences beyond the preregistered tolerance.

These are productive negative results: each one identifies which rung of the ladder adds no measurable information.

---

## 9. Relation to prior work

This programme is intentionally compositional rather than claiming that any individual mechanism is new in isolation.

**Reservoir computing.** Fixed recurrent reservoirs are well established as high-dimensional dynamical mappings for temporal/sequential signals. See Lukoševičius & Jaeger, *Reservoir computing approaches to recurrent neural network training*, Computer Science Review 3(3), 2009, DOI: 10.1016/j.cosrev.2009.03.005; and Tanaka et al., *Recent advances in physical reservoir computing: A review*, Neural Networks 115, 2019, DOI: 10.1016/j.neunet.2019.03.005.

**Mutual learning.** Peer models can teach one another during training without a privileged fixed teacher. See Zhang et al., *Deep Mutual Learning*, CVPR 2018, arXiv:1706.00384.

**Uncertainty- and difficulty-weighted learning.** Curriculum/self-paced methods provide precedent for changing learning weight according to estimated difficulty or uncertainty. The present proposal differs in using the shared recurrent state as part of that controller rather than treating difficulty as a static sample property.

**State-dependent plasticity and neuromodulation.** Biological and machine-learning models of neuromodulation motivate separating the fast activity state from the slower rule that decides when plasticity should occur. Our construction is deliberately modest: MaleCNS is not claimed to reproduce a biological learning rule; its state is tested as a computational signal for gating external plasticity.

**External associative memory and vector retrieval.** Non-parametric retrieval shows that useful knowledge need not be compressed into model weights. Our proposal keeps the store itself deliberately ordinary and deterministic; the experimental question is whether a recurrent biological state provides a useful policy for *addressing and iterating over* that memory.

**Cycle consistency.** Bidirectional reconstruction provides a way to constrain mappings even when the exact paired target is unavailable at inference. Here cycle consistency is not treated only as a training regularizer; it becomes an online sensory signal that can trigger another retrieval/action step.

**Spectral parameterization.** Fourier-domain filters provide a compact family of transformations whose amplitude/phase components can be controlled incrementally. We do not assume that Fourier is privileged a priori; original-basis diagonal transforms and full linear maps are required controls.

The proposed contribution is the **specific composition and experimental ladder**: semantic flavour, peer coupling, reliability, directed reliability, recurrent state conditioning, state-conditioned external memory, bidirectional cycle checks, and recurrent spectral action, evaluated under topology- and capacity-matched controls.

---

## 10. Current implementation mapping

The repository already contains successive approximations to the first half of this ladder:

- semantic/coupled flavour experiments;
- PR #452: reliability-weighted peer coupling;
- PR #453: fresh-seed reliability replication;
- PR #454: directed sender→receiver teaching gains;
- PR #459: coupling-strength regimes;
- PR #460: state-conditioned peer coupling using MaleCNS uncertainty and reward error.

PR #460 is therefore not an isolated experiment. It is the current implemented endpoint of a cumulative architectural programme.

The second half of the ladder—state-conditioned external memory, bidirectional cycle consistency, and embodied spectral navigation—is the next experimental programme. It should reuse the same frozen MaleCNS and the same discipline of matched controls rather than becoming an unrelated architecture.

The next clean implementation should expose a common `MaleCNSClosedLoop` interface in which the environment supplies:

- sensory/semantic channels;
- deterministic external-memory retrieval;
- reward/cycle signals;
- an action space (initially spectral embedding transformations).

The connectome remains frozen; adapters around it implement the policy boundary.

---

## 11. Central claim boundary

The strongest claim this programme can eventually support is:

> A fixed recurrent connectome can provide a useful context-dependent state for controlling directed plasticity, external-memory access, and iterative actions over semantic representations.

A stronger biological claim requires topology controls:

> The specific MaleCNS wiring provides a better control state than appropriately matched artificial recurrent graphs for deciding how to learn, what to retrieve, and how to act on representation geometry.

Until those controls win, the first claim and the second claim must remain separate.

The memory claim must also remain precise. We are **not** claiming that the connectome stores the external corpus internally. The external memory is an ordinary deterministic database. The hypothesis is that the connectome can provide a useful recurrent state for **indexing, interpreting, revisiting, and acting on that memory**.

---

## 12. The reason this direction is promising

The architecture gives the connectome jobs that are unusually well matched to what recurrence naturally provides.

We do not ask 165,122 frozen neurons to become a modern language model or to memorize millions of embedding pairs. We ask them to maintain a rich dynamical summary of what the surrounding system is experiencing and to use that summary to modulate:

- who should teach whom;
- how much to trust each channel;
- what external memory should be retrieved;
- whether the retrieved neighbourhood is coherent;
- whether a translation survives a return trip;
- what geometric action should be taken next;
- when the system should stop moving.

That turns MaleCNS from a strange fixed layer inserted between embeddings and a decoder into something more coherent:

**a recurrent context engine for plasticity, memory access, and action.**

The external database supplies scalable durable memory. The recurrent state supplies context. The descending interface supplies action. Cycle consistency supplies self-checking. Supervised targets, when available, supply a stronger reward but are no longer the only possible source of correction.

If successful, that role is reusable. The semantic channels can later be replaced by embedding translators, NER heads, audio adapters, visual receptors or motor controllers without changing the core principle.

That is why the progression

`semantic flavour → coupled flavour → reliability → directed reliability → state-conditioned feedback → state-conditioned external memory → bidirectional cycle consistency → embodied spectral navigation`

is more interesting than any one of its stages in isolation: it is the shortest path we currently have from "use a fly connectome as a reservoir" to a general closed-loop architecture in which the connectome participates in deciding **how learning unfolds, what is remembered, and how the represented world should be changed next**.