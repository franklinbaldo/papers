---
type: "Experimental Programme"
title: "State-Conditioned Multi-Memory Control for MaleCNS"
description: "Falsifiable experiments for testing whether a frozen MaleCNS can learn to control, combine, revisit, and act through multiple deterministic external memories."
tags: [malecns, external-memory, vector-search, state-conditioned, memory-routing, cycle-consistency, spectral-action, closed-loop]
timestamp: 2026-09-16T19:52:00-04:00
status: draft
---

# State-Conditioned Multi-Memory Control for MaleCNS

## 1. Question

The central hypothesis is stronger than ordinary retrieval augmentation.

We do not ask whether a deterministic vector database improves an embedding translator. We ask whether the recurrent state of a frozen MaleCNS can become a **control state for several external memories at once**: deciding which memory to query, how to query it, how much to trust it, whether to combine it with another memory, when to revisit it, and how the retrieved evidence should influence the next spectral action.

The durable facts remain outside the connectome. The connectome is not required to memorize the corpus. Its proposed role is to organize access to memory.

The architecture is:

```text
current semantic state z_t
        ↓
     MaleCNS x_t
        ↓
 memory-routing policy
   ↙      ↓       ↘
 M_sem   M_act   M_err   ...
   ↘      ↓       ↙
 retrieved sensory packet m_t
        ↓
     MaleCNS x'_t
        ↓
 descending spectral action a_t
        ↓
 new semantic state z_{t+1}
        ↓
 reward / cycle / retrieval outcome
        └──────────────→ next state
```

No experiment below may claim a MaleCNS-specific advantage unless topology-matched recurrent controls are also run.

---

## 2. Deterministic memory types

The first implementation should keep every memory ordinary and auditable. A memory is a table plus a deterministic retrieval rule, not a learned neural module.

### M1 — paired semantic memory

Records:

`(A_i, B_i, item_id)`

Purpose: retrieve the local correspondence between embedding spaces A and B.

Query: cosine/top-k in the current source space.

Return packet: weighted barycenter, similarities, variance, neighbour IDs, entropy/stability.

### M2 — action memory

Records:

`(local_state_signature, spectral_action, observed_delta_target, observed_delta_cycle)`

Purpose: remember which spectral moves previously helped in regions resembling the current one.

This memory stores experience, not a policy. Retrieval remains deterministic.

### M3 — error memory

Records:

`(state_signature, cycle_error_signature, retrieval_signature, corrective_action/outcome)`

Purpose: retrieve previous situations in which translation looked plausible in one direction but failed the reverse cycle.

### M4 — spectral-region memory

Records:

`(spectral_signature, successful_delta_theta, outcome)`

Purpose: capture whether particular Fourier bands/phases/mixing operations were useful in particular regions of the representation geometry.

### M5 — trajectory memory

Records:

`(initial_signature, step_sequence, final_quality, stopping_step)`

Purpose: expose previously successful short paths through embedding space. The system may retrieve a trajectory as advice, but still decides online whether to follow, modify, or abandon it.

### M6 — failure / taboo memory

Records:

`(state_signature, action_or_route, regression_measure)`

Purpose: explicitly remember moves or routes that damaged protected A↔B correspondences. This gives the controller an external record of regressions without requiring those failures to be stored in MaleCNS weights.

---

## 3. Experiment I — Does more than one memory help at all?

### Question

Before testing intelligent routing, determine whether lateral memories contain complementary information.

### Fixed task

Embedding translation A→B with exact test pairs removed from every memory. Use the same frozen paired corpus, same train/test split, same source/target embedding models, and same spectral action family across all arms.

### Arms

1. `semantic_only`: M1 only.
2. `semantic+action`: M1 + M2.
3. `semantic+error`: M1 + M3.
4. `semantic+spectral`: M1 + M4.
5. `semantic+trajectory`: M1 + M5.
6. `all_memories`: M1–M6 available simultaneously.
7. `all_memories_shuffled`: same storage and bandwidth, but lateral-memory item associations are shuffled within split.

In this experiment all retrieval schedules are fixed. MaleCNS does not yet choose which memory is queried. Every arm receives the same retrieval budget.

### Metrics

- held-out cosine to true B;
- downstream neighbourhood preservation in B;
- A→B→A cycle error;
- protected-memory regression;
- number of spectral steps;
- action energy;
- gain over the deterministic M1 barycenter.

### Support criterion

A lateral memory is useful only if adding it improves held-out translation or cycle consistency relative to `semantic_only` without increasing protected-memory regression beyond the frozen tolerance.

If `all_memories_shuffled` matches `all_memories`, the gain is likely bandwidth/context rather than meaningful memory structure.

---

## 4. Experiment J — Can MaleCNS route among lateral memories?

### Question

Given memories that have individually shown useful information, can recurrent MaleCNS state decide **which memory should be consulted now** better than a fixed schedule?

### Available actions

At each step the controller may choose:

- which memory bank(s) to query;
- query temperature;
- top-k;
- whether to query one or multiple banks;
- how much of each returned packet is admitted to the next sensory input;
- whether to skip retrieval and act immediately.

The controller may not modify database contents in this experiment.

### Arms

1. `fixed_round_robin`: deterministic M1→M2→M3→… schedule.
2. `query_all`: every bank queried at every step; fixed averaging.
3. `confidence_heuristic`: deterministic hand-written routing from retrieval entropy/cycle error.
4. `learned_router_no_recurrence`: same trainable routing capacity, but no recurrent state.
5. `random_ESN_router`: matched random recurrent reservoir.
6. `MaleCNS_router`: frozen MaleCNS state controls routing.
7. `MaleCNS_router_state_shuffled`: same MaleCNS outputs, but states are permuted across examples before routing decisions.

### Metrics

All Experiment I metrics plus:

- retrieval calls per solved item;
- bytes/vectors retrieved;
- memory-bank selection distribution;
- conditional value of each bank given state;
- route entropy;
- repeated-query rate;
- improvement per retrieval call.

### Support criterion

The state-conditioned routing hypothesis is supported if `MaleCNS_router` improves quality-per-retrieval over fixed/query-all baselines and beats its state-shuffled control. A MaleCNS-specific claim additionally requires improvement over `random_ESN_router`.

---

## 5. Experiment K — Is retrieval itself an action?

### Question

Can the system learn that changing the query changes what can be remembered, rather than treating memory as a passive lookup table?

### Mechanism

Let the raw current embedding be `z_t`. The controller emits a bounded query action `u_t`, producing:

`q_t = Q(z_t, x_t, u_t)`

The simplest implementation constrains `Q` to a small spectral/query deformation. Retrieval is then performed with `q_t`, while the semantic state itself remains unchanged until a separate motor action is accepted.

### Arms

1. raw cosine query only;
2. deterministic local query expansion;
3. gradient-optimized query against retrieval consistency;
4. learned feed-forward query adapter;
5. random ESN query controller;
6. MaleCNS query controller;
7. MaleCNS with repeated retrieve→state→requery cycles before any spectral motor move.

### Key measurement

Measure whether a state-conditioned requery discovers neighbour sets whose B-space barycenter is closer to the unseen true B than the raw-query neighbour set.

This is the cleanest test of **remembering by movement**.

### Failure condition

If repeated state-conditioned requery does not improve neighbour quality relative to deterministic query expansion, the memory-control claim should be narrowed: MaleCNS may still interpret memory usefully without providing superior indexing.

---

## 6. Experiment L — Lateral memory arbitration under disagreement

### Question

The interesting case is not when all memories agree. Does the recurrent state help when different memory systems recommend incompatible actions?

### Constructed disagreement regimes

Create held-out cases in which:

- M1 semantic barycenter points toward one B region;
- M2 action memory recommends an action learned elsewhere;
- M3 error memory flags that action as cycle-risky;
- M4 spectral memory recommends a different frequency-band adjustment;
- M5 trajectory memory proposes a multi-step route.

The conflicts should be constructed from real stored records, not synthetic arbitrary vectors.

### Arms

1. equal vote over memory recommendations;
2. globally learned scalar weight per memory;
3. hand-written priority ordering;
4. current-observation-only arbitration;
5. random recurrent arbitration;
6. MaleCNS state-conditioned arbitration.

### Readouts

- final held-out B correspondence;
- cycle error;
- probability of choosing the retrospectively best memory/action;
- regret relative to an oracle that knows the true B only for scoring;
- stability across repeated nearby examples.

### Hypothesis

If MaleCNS state is useful as a contextual controller, its advantage should be largest precisely when memory recommendations conflict, not when all memories already agree.

---

## 7. Experiment M — Memory + embodied spectral navigation

### Question

Does memory routing become more valuable when retrieval and action are interleaved rather than performed once?

### Loop

```text
z_t
 → retrieve selected lateral memories
 → MaleCNS state
 → choose spectral action
 → z_{t+1}
 → recompute cycle/plausibility
 → choose memories again
 → ...
```

### Arms

1. one-shot M1 barycenter, no action;
2. one-shot all-memory context + one spectral action;
3. fixed iterative retrieval/action schedule;
4. state-conditioned memory routing with fixed spectral optimizer;
5. fixed memory retrieval with MaleCNS spectral policy;
6. random ESN controlling both retrieval and action;
7. MaleCNS controlling both retrieval and action.

### Primary result

The strongest architectural evidence would be an interaction: controlling retrieval and action together should outperform the sum of their isolated gains.

Formally compare whether:

`gain(joint) > gain(memory_control_only) + gain(action_control_only)`

within uncertainty bounds fixed before reading the result.

This would indicate that memory access and geometric action form a coupled closed loop rather than two separable modules.

---

## 8. Experiment N — Bidirectional multi-memory consistency

### Question

Can separate lateral memories for A→B and B→A improve each other without allowing one direction to destroy the other?

### Memory sets

Maintain mirrored but independently indexed banks for both directions:

- semantic A→B / B→A;
- action histories;
- error histories;
- spectral corrections;
- trajectory histories;
- taboo/regression memories.

### Protocol

For every proposed policy/adapter update:

1. score A→B on the current minibatch;
2. score B→A on the paired reverse minibatch;
3. score cycle consistency;
4. score a frozen protected-memory set in both directions;
5. accept/weight the update only under a preregistered conservative rule.

### Controls

- optimize A→B only;
- optimize B→A only;
- alternate directions without protection;
- joint objective without protected memory;
- joint objective + protected memory;
- MaleCNS-state-conditioned update gate;
- random-reservoir update gate.

### Success criterion

The system should improve one direction while holding the other within the frozen non-regression tolerance, and eventually improve the bidirectional Pareto frontier rather than oscillating between directions.

---

## 9. Experiment O — Memory growth without retraining

### Question

A core claim of external memory is that factual capacity can grow independently of learned weights. Test it directly.

### Protocol

Freeze the complete trained controller/adapters. Do not perform further gradient updates.

Evaluate the same held-out set while expanding the deterministic memory through nested sizes, for example:

`1k → 10k → 100k → 1M pairs`

where every larger memory strictly contains the smaller one and no exact test pair is inserted.

### Compare

- fixed top-k system;
- learned nonrecurrent query adapter;
- random ESN controller;
- MaleCNS memory controller.

### Hypothesis

A successful memory-control policy should exploit additional useful memories without retraining. Performance should improve or remain stable as memory grows, while retrieval cost and neighbourhood ambiguity are measured explicitly.

A collapse at large memory sizes would show that the controller learned a small-database regime rather than a scalable memory-access policy.

---

## 10. Experiment P — Lesion the memory interface, not the connectome

### Question

What exactly has the system learned about memory use?

### Lesions

At inference, without retraining:

- remove one lateral memory at a time;
- swap M2 and M3 return channels;
- preserve returned vectors but remove metadata such as confidence/variance;
- preserve metadata but replace retrieved vectors with matched random neighbours;
- freeze routing to the mean training policy;
- reset MaleCNS recurrent state between retrieval steps;
- preserve MaleCNS state but shuffle memory-bank identity labels.

### Interpretation

These lesions distinguish several possibilities:

- the system merely consumes more vectors;
- it learned bank identity;
- it uses uncertainty metadata;
- it depends on temporal retrieval history;
- it genuinely integrates memory type with recurrent context.

The prediction of the full hypothesis is selective degradation: destroying state↔memory correspondence should hurt more than removing an equivalent amount of raw retrieval bandwidth.

---

## 11. Common controls and preregistration rules

Every experiment should preserve the following discipline:

1. **Exact-pair exclusion.** The test pair itself must never be present in the external memory used to translate it.
2. **Document/entity split.** Near duplicates must be grouped before train/memory/test partitioning.
3. **Frozen memory snapshots.** Every run records memory item IDs and index fingerprint.
4. **Matched retrieval budget.** Baselines receive the same maximum retrieval calls/vectors when the question concerns routing quality.
5. **Matched action budget.** Controllers receive the same maximum spectral steps and action range.
6. **Matched trainable capacity.** Feed-forward, random-reservoir, and MaleCNS controllers use comparable adapter/readout capacity around the frozen recurrent core.
7. **Topology controls.** Biological-topology claims require random and rewired recurrent controls.
8. **Protected correspondence set.** Bidirectional updates are checked against a frozen set that cannot be selected after seeing outcomes.
9. **No validation-controlled memory weights.** Reliability/routing rules may use training state and deterministic memory metadata, never validation outcomes.
10. **Log the entire trajectory.** Queries, neighbour IDs, similarities, selected banks, MaleCNS state summaries, actions, rewards, cycle errors, and stop decisions must be reproducible.

---

## 12. Minimal execution order

Do not build the complete system first. The shortest falsifiable path is:

1. **Experiment I** — prove that lateral memories contain complementary information under fixed retrieval.
2. **Experiment J** — test whether state-conditioned routing beats fixed/query-all access.
3. **Experiment K** — test whether changing the query improves what can be recalled.
4. **Experiment L** — force memory disagreement and test contextual arbitration.
5. **Experiment M** — close the retrieval↔spectral-action loop.
6. **Experiment N** — enforce bidirectional non-regression.
7. **Experiment O** — scale memory without retraining.
8. **Experiment P** — lesion the interface to identify what the controller actually uses.

The architecture earns each additional mechanism only if the previous experiment shows a measurable need for it.

The strongest eventual claim is not that MaleCNS contains a superior internal memory. It is narrower and more testable:

> A frozen recurrent connectome can provide a useful state for controlling access to multiple deterministic external memories, integrating their disagreements over time, and coupling retrieval to actions over representation geometry.
