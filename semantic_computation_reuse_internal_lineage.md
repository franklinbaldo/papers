---
type: "Companion Note"
title: "Semantic Computation Reuse — Internal Research Lineage and Claim Boundary"
description: "Internal synthesis mapping semantic computation reuse onto the existing papers programme before any external literature comparison."
tags: [semantic-computation-reuse, semantic-atlas, rl-relay-transducers, informational-time, successor-policy, research-map]
timestamp: 2026-08-21T18:04:00-04:00
---

# Semantic Computation Reuse — Internal Research Lineage and Claim Boundary

> **Editorial note.** This is an internal lineage and scope-control note for `semantic_computation_reuse.md`. It is based only on research artifacts already present in `franklinbaldo/papers`, including open experimental/paper branches where noted. It is not an external prior-art review and makes no novelty claim against the literature. Its purpose is to identify what this research programme had already proposed before the Semantic Computation Reuse formulation and to isolate the genuinely incremental hypothesis.

## 1. Main finding

Semantic Computation Reuse (SCR) did not arise as an isolated new direction. Most of its conceptual machinery already exists across the repository, but at different abstraction levels.

The strongest internal antecedent is `semantic_atlas.md`. The Atlas already proposes:

- text and reasoning as trajectories through semantic state space rather than isolated embeddings;
- position plus semantic velocity/curvature as a richer dynamic state;
- an empirical map containing transition dynamics, control cost, reachability, corridors, barriers, bridges, and uncertainty;
- directed navigation distance rather than symmetric semantic distance;
- route planning that can replace manually supplied chain-of-thought decomposition;
- the hypothesis that coarse semantic planning can skip semantic distance otherwise explored token by token, invoking full lexical generation only where higher resolution is required.

Therefore SCR should **not** independently claim as its core novelty that reasoning can be modeled as semantic navigation, that trajectories induce a directed map, that bridge states may make an otherwise difficult transition reachable, or that semantic planning may reduce generation cost. Those claims already belong to the Semantic Atlas programme.

SCR's narrower contribution is the proposed mechanism by which an Atlas-like map can become an **amortized store of executable past computation**: stored textual realizations of past states are retrieved and recombined into a path that did not previously exist, with the causal objective of displacing fresh inference on a genuinely new problem.

This suggests the internal relationship:

```text
Semantic Atlas
  defines the map, dynamics, reachability, bridges and planning problem
        ↓
Inverse Atlas / relay memory
  provides textual realizations of semantically addressed states
        ↓
reward-conditioned / successor-aware retrieval
  ranks candidates by future utility rather than cosine alone
        ↓
Semantic Computation Reuse
  recombines past states into novel paths and measures fresh compute displaced
```

## 2. Semantic Atlas: the map was already there

`semantic_atlas.md` is the conceptual parent most directly related to SCR.

Its central architectural move is already to separate lexical generation from lower-resolution semantic navigation. Repeated model trajectories populate an Atlas with state density, transition dynamics, control cost, reachability and uncertainty. A planner operates over that map; a Semantic Servo realizes local semantic movement in text/model space.

The Atlas also already defines directed reachability and low-cost bridges. Its example that a model may fail at a direct `A -> B` transition but succeed through `A -> G1 -> G2 -> B` is the formal ancestor of the later "mountain" intuition.

### What SCR adds to the Atlas

The Atlas primarily asks whether a map of semantic dynamics can guide or control generation. SCR asks a stronger economic/mechanistic question:

> Can nodes and path fragments produced by historical inference be materialized as reusable textual actions so that navigation through the Atlas **substitutes for**, rather than merely guides, part of later inference?

The distinction is:

```text
Atlas navigation as guidance:
planned route -> model realizes route through generation

SCR:
stored route fragments/states -> retrieval realizes part of route directly -> model resumes only at frontier
```

SCR also adds a particularly important regime that should be explicit: **the terminal destination need not be known in advance**. An Atlas controller can be given a desired target/delta. SCR's stronger open-ended problem is to reach states with high prospective value even when the useful final state has not yet been represented as the goal.

## 3. Inverse Atlas: the textual state lookup already exists

Open `papers#277` is even closer at the implementation level. Its `InferenceRecord` memory is keyed by causal semantic state and may store exact context, incoming semantic velocity, observed next state, sampled text/token blocks, and model probabilities. Retrieval can be conditioned both on the direction from which the current trajectory arrived and on a desired outgoing semantic displacement.

This already supplies the key technical insight that a semantic point does not need to be inverted into a unique text. A memory can store **real textual realizations** previously observed near that point and retrieve them conditionally.

The Inverse Atlas models something close to:

```text
P(textual item |
  current semantic position,
  incoming trajectory,
  desired outgoing displacement,
  local lexical evidence)
```

This is a direct internal ancestor of SCR's lookup table:

```text
semantic address -> stored real text -> induce approximate downstream state
```

### What SCR adds to the Inverse Atlas

The Inverse Atlas assumes an independently planned route or desired local direction. SCR asks whether the datastore can also help **discover the route itself**, particularly through recombination of states that originated in unrelated trajectories.

So the important extension is not `embedding -> text`. That machinery already exists. The extension is:

```text
known route / desired delta
    -> route-conditioned lexical realization       [Inverse Atlas]

unknown terminal destination
    -> prospective state selection
    -> cross-trajectory recombination
    -> emergent novel path
    -> reduced fresh inference                     [SCR]
```

## 4. RL Relay Transducers: semantic neighbors are only candidate recall

`rl_relay_transducers.md` already contains the most important correction to naive nearest-neighbor navigation.

Its associative textual memory stores real strings alongside frozen semantic embeddings. The retrieved object inserted into the next prompt is the **stored string**, not the vector. More importantly, it explicitly states that cosine should be treated as a **high-recall candidate generator**, not the final decision rule.

The relay architecture separates:

```text
frozen semantic recall
        ↓
learned functional ranking
        ↓
commit / reject / retrieve action
```

Memory entries can have both a stable semantic key and a trainable functional key. A reranker can use semantic affinity, downstream utility, context, model/channel identity, remaining depth, exploration and cost. Selection alone must not improve future rank; promotion requires attributed downstream advantage.

This is already the correct answer to a central SCR problem: a state close in embedding space may be useless or harmful for the future, while a slightly more distant state may be an excellent computational waypoint.

### Consequence for SCR

SCR should treat semantic similarity as **addressing/recall**, while its real navigation criterion is functional/prospective:

```text
semantic neighborhood
        ↓
which candidate changes the reachable future most usefully?
```

`Continuation equivalence` can therefore be understood as an empirical behavioral criterion for what the relay paper calls functional utility. It should not be sold as a claim that the embedding itself already contains the correct transition metric.

## 5. Reward-conditioned retrieval: Stage 0 already exists

`experiments/reward_conditioned_retrieval/` already isolates the simplest version of the functional-retrieval problem.

Its synthetic environment deliberately makes semantic top-k recall easy while making the functionally useful sibling independent of nearest-cosine rank. The experiment tests whether downstream reward can learn to rank the useful candidate.

Its own interpretation limit is revealing: it explicitly excludes token generation, **multi-hop credit, sequence composition, semantic drift**, and model-specific channel survival.

Those exclusions describe almost exactly the next scientific step SCR now proposes.

Therefore the existing synthetic experiment should be treated as **Stage 0**, not repeated under a new name:

```text
Stage 0 — already defined
semantic recall -> functional ranking of one memory item

Stage 1 — SCR
semantic recall -> functional multi-hop path composition -> black-box LLM -> compute substitution
```

A failed Stage 1 would not invalidate Stage 0. It would show that functional single-step retrieval does not automatically compose into reusable computation.

## 6. Agent Successor Policy: the mountain is a successor-value object

Open `papers#315` supplies a natural formal language for the "mountain" intuition.

ASP argues that state alone is insufficient: the policy should be trajectory-conditioned, `pi(tau)`, and may output an absolute desired semantic point or a desired displacement. Its successor-style formulation asks which behaviors tend to produce desirable future states.

The cross-paper ASP synthesis already imports the Atlas factorization:

```text
current position
+ incoming velocity
+ desired outgoing delta
+ semantic recall
+ functional reranking
```

This suggests a cleaner interpretation of SCR's **landmark state**.

A landmark should not merely be a point with high semantic centrality. It is a state with unusually high **successor value** under a bounded future compute budget: conditioning on it makes valuable future regions easier to reach.

A practical future representation might estimate something like:

```text
Psi(s) ~= discounted / budgeted occupancy of useful future regions from s
```

Then "climbing the mountain" means moving to a stored state whose successor representation exposes a broader or more valuable future than the current state, even if that state is not the nearest semantic neighbor and even if the final destination is not yet known.

This is the strongest internal bridge between ASP and SCR:

- ASP learns **where behavior should move given its trajectory**;
- SCR asks whether previously computed textual states can **realize enough of that movement by lookup rather than generation**.

## 7. Informational Time: reuse does not erase the original computation

`informational_time.md` gives SCR an important accounting discipline.

It distinguishes:

- causal work/depth actually traversed;
- physical message length;
- symbolic representation length;
- a later short registry index that can stand for a long earlier causal history.

The paper explicitly warns that compressing a history into a short index does not make the historical causal path cease to have occurred.

This resolves a possible ambiguity in the phrase "reuse computation". SCR does not claim that retrieval retroactively eliminates the computation that created the stored state. The historical computation was paid once. The hypothesis is **amortization**:

```text
past episode:
pay expensive inference -> materialize state/path in memory

future episodes:
pay cheap lookup + residual fresh inference
```

A useful SCR cost accounting should therefore separate:

- `C_build`: historical compute required to populate the memory;
- `C_store`: storage/index maintenance;
- `C_lookup`: retrieval/navigation cost;
- `C_fresh`: remaining generation cost;
- `N`: number of later tasks over which historical compute is amortized.

For a horizon of future tasks, the relevant advantage is not merely per-query token reduction but whether

```text
C_build + C_store + sum(C_lookup + C_fresh)
    <
sum(C_full_recomputation)
```

under matched task performance.

Informational Time also imports predictive/causal-state equivalence: histories may share a compressed representation when their differences are irrelevant to a specified predictive task. SCR's `continuation equivalence` is a model- and task-specific operationalization of this same predictive principle at the interface of a black-box LLM.

## 8. Generative Machine Teaching: expensive constructions become reusable atoms

`generative_machine_teaching.md` already proposes a registry in which a derived object becomes reusable as one symbolic unit after an explicit construction has produced and registered it. A later curriculum can use the registered object atomically rather than reconstruct it from primitive marks every time.

This is structurally analogous to computation reuse:

```text
expensive historical construction
        ↓
registered reusable object
        ↓
cheap later reference
```

The difference is important.

Generative Machine Teaching uses proof-indexed exact constructions and a registry whose symbols have explicit expansion semantics. SCR instead proposes **approximate semantic addressing** and behavioral reuse: a stored state need not be exactly equal to the desired state, and its legitimacy comes from preserving useful continuations rather than exact expansion identity.

SCR can therefore be read as a softer, black-box, semantic analogue of the registry principle:

> once a useful computation has been paid for, can later systems address a sufficiently equivalent result without replaying its entire construction?

## 9. Structured Irregularity: textual incoherence is not yet failure

`pedagogical_signal_extraction.md` already supplies the conceptual defense against rejecting an SCR path merely because its fragments look incoherent locally.

The paper distinguishes noise from **temporary opacity** and argues that clarity is a property of the complete teacher-learner system, not necessarily of an individual message. Earlier observations may acquire value only after later structure makes them decodable. Ordered curricula can carry information that disappears when the same elements are treated as an exchangeable bag.

This maps directly onto the strongest SCR experiment.

A composed path such as

```text
x_a ; x_b ; x_c ; x_d
```

need not read as good human prose. Its scientific legitimacy depends on downstream counterfactual effect:

- does it improve task performance or reduce required fresh inference?
- does its order matter?
- do the same fragments shuffled lose the effect?
- does edge destruction remove the gain?
- does the gain survive held-out tasks and model/channel perturbations?

If shuffled fragments perform equally well, then the stronger path/topology claim collapses toward a bag-of-hints/RAG explanation. If ordering matters prospectively, Structured Irregularity already provides the programme's vocabulary for why local textual oddness need not imply absence of structure.

## 10. Interstitial Agent: stored text is a black-box control surface

`interstitial_agent.md` already treats an embedding-indexed memory as more than an optimization detail. It says memory can accumulate strings that occupy useful semantic neighborhoods, survive model transformations, induce stable responses and act as canonical representatives of broader regions.

It also separates surface persistence from functional persistence: a representation can change completely at the lexical level while preserving a downstream causal distinction.

For SCR, this supplies a disciplined interpretation of the value stored in the lookup table. The text is not a transparent serialization of a hidden state. It is an **auditable discrete intervention** that has historically induced useful downstream behavior.

That fits SCR's black-box requirement much better than language suggesting that embeddings literally encode or reconstruct transformer hidden states.

## 11. Semantic Tokenization Transformers: real exemplars for semantic coordinates

`semantic_tokenization_transformers.md` contains a narrower but useful implementation analogy. Its decoding design keeps real chunk **medoids** as exemplars for semantic codebook regions and constructs paths through those exemplars before an LLM normalization step.

This supports the practical intuition that a semantic region need not be decoded from scratch. A vector/code can address an already observed textual representative.

The boundary is again important: STT studies semantic tokenization, compression and decoding. SCR studies whether sequences of retrieved representatives can substitute for future reasoning computation. STT should therefore be cited internally as a compatible representation/decoding substrate, not as the source of the navigation claim.

## 12. Language as a Higher-Order Agent: bounded readout supplies the economic pressure

Open `papers#308` argues that an ever-growing history cannot remain uniformly available to a bounded reader. It defines functional equivalence between archive lookup and model-based reconstruction relative to a query family, loss tolerance and matched readout budget.

This provides a broader memory-economics frame for SCR. The relevant question is not whether all historical text can fit into context. It is which mechanism retrieves enough of history's useful state under a bounded readout/computation budget.

SCR can be viewed as one concrete mechanism for that pressure:

```text
large accumulated historical computation
        ↓
semantic addressing + prospective ranking
        ↓
small selected path presented to bounded LLM context
        ↓
residual generation
```

No Language-Agent ontology is required for SCR; only the bounded-readout distinction is imported.

## 13. Machine Discovery: computation reuse changes resource-bounded reach, not truth by itself

`machine_discovery.md` distinguishes ideal closure from **resource-bounded closure**: what claims or constructions are actually reachable within a specified computation, proof, retrieval, time or attention budget.

SCR can enlarge this resource-bounded reach without creating any new fact merely by making existing computational states cheaper to access. That is a capability/efficiency result, not automatically a discovery.

The connection becomes stronger only when a novel composed path produces a new artifact that survives the Machine Discovery paper's independent certification, novelty and provenance requirements. If that artifact is then stored and makes later problems cheaper or newly solvable, the result also becomes an instance of downstream fertility/curriculum expansion.

This boundary prevents a common overclaim:

```text
retrieval saved compute != machine discovery
```

but also identifies the recursive possibility:

```text
novel computation -> certified reusable artifact -> memory -> expanded future reach
```

## 14. The genuinely incremental SCR claim

After this internal comparison, the strongest defensible SCR claim is narrower than the first standalone formulation.

The repository had already proposed:

- semantic trajectories and directed navigation;
- reachability, bridges and control costs;
- stored real texts indexed by embeddings;
- incoming-trajectory- and desired-direction-conditioned retrieval;
- semantic recall separated from learned functional ranking;
- successor-style future value;
- registry-based reuse of expensive prior constructions;
- predictive equivalence as the criterion for valid compression;
- local opacity that can become prospectively useful.

What SCR newly bundles and foregrounds is the conjunction:

> **Past textual computation is materialized as semantically addressable states; a new problem whose terminal solution is not already known can select and recombine states from heterogeneous historical trajectories into a path that never previously existed; if that path preserves downstream performance while reducing fresh generation relative to compute-matched controls, then retrieval has substituted for a portion of reasoning rather than merely guided it.**

Four pieces are load-bearing:

1. **amortization** — historical inference is paid once and reused across later episodes;
2. **open recombination** — the useful sequence need not be a previously observed trajectory or known skill;
3. **unknown destination** — planning can use prospective/successor value rather than only distance to a specified target;
4. **causal compute displacement** — the result must reduce fresh inference at matched performance, not merely improve accuracy after adding more context.

If any one is removed, the claim moves back toward an already existing internal paper:

- remove amortization -> Semantic Atlas steering/navigation;
- remove open recombination -> procedural/skill memory;
- require known destination -> Inverse Atlas route realization;
- remove compute displacement -> retrieval as guidance;
- use cosine as final rule -> contradicted by RL Relay's own functional-retrieval design.

## 15. A unified internal architecture

The most economical architecture after this synthesis is:

```text
historical LLM / agent trajectories
        ↓
textual checkpoints + provenance + outcomes
        ↓
Semantic Atlas state/dynamics representation
(position, incoming trajectory, transitions, cost, uncertainty)
        ↓
frozen semantic index
(high-recall addressing)
        ↓
functional / successor representation
(what futures does this state tend to make reachable?)
        ↓
open-ended path planner
(no terminal state required initially)
        ↓
retrieve stored textual realizations
        ↓
compose path from heterogeneous histories
        ↓
black-box LLM resumes at uncovered frontier
        ↓
outcome + remaining inference cost
        ↓
credit assignment updates functional transition evidence
```

This architecture deliberately reuses existing programme components rather than giving SCR a parallel vocabulary for the same objects.

## 16. Experimental consequence

The next SCR experiment should inherit existing falsifiers instead of starting from scratch.

**Already tested / instrumented conceptually:** semantic recall versus functional choice (`reward_conditioned_retrieval`).

**Next new test:** whether functional choices compose through a real model channel into a multi-hop path that displaces generation.

The minimal comparison should preserve:

1. full fresh reasoning;
2. direct top-k semantic RAG;
3. single best functional retrieval without path composition;
4. existing-route/procedural retrieval;
5. open composed path across unrelated histories;
6. same fragments shuffled;
7. transition edges destroyed while preserving node content and approximate similarity;
8. prospective/successor ranking ablated back to cosine.

Primary outcomes should include both task utility and **fresh inference displaced**. A path that improves accuracy only by adding a large amount of retrieved context is guidance, not yet compute substitution.

For the stronger unknown-destination claim, evaluation tasks should be chosen so that the exact answer, complete solution trajectory, and matching skill are absent from the datastore. The system may reuse states and subpaths, but success must require a new composition.

## 17. Editorial recommendation

`semantic_computation_reuse.md` should remain a separate short position paper because it isolates an experimentally sharp economic claim that the broader Semantic Atlas does not currently make its primary object.

However, it should be presented explicitly as an **extension and synthesis inside the existing programme**, not as a second invention of semantic navigation.

The recommended claim boundary is:

- **Semantic Atlas:** what is the navigable semantic dynamics of model computation?
- **Inverse Atlas:** how can a desired semantic position/direction be realized through stored lexical/textual evidence?
- **RL Relay / reward-conditioned retrieval:** which semantically recalled memory item is functionally useful downstream?
- **Agent Successor Policy:** which states/actions are valuable because of the futures they tend to produce?
- **Semantic Computation Reuse:** can those stored states be recombined, for an unseen problem and without a known terminal destination, so that lookup replaces measurable fresh inference?
- **Machine Discovery:** when does any new terminal artifact become certified public epistemic expansion and alter later curricula?

That division keeps each paper falsifiable and gives the programme a coherent progression instead of a family of overlapping metaphors.
