---
type: "Research Map"
title: "Semantic Systems Research Map"
description: "Canonical map of the Pontifex, Torus, Semantic Atlas, Semantic Observers, Perquire, MaleCNS, structural-identification, machine-interaction, and adjacent research initiatives."
tags: [research-map, pontifex, torus, semantic-atlas, semantic-observers, perquire, malecns]
timestamp: 2026-09-19T15:00:00-04:00
---

# Semantic Systems Research Map

> **Canonical programme map.** This document is the source of truth for how the research initiatives in and around this repository relate to one another. It records programme structure and current evidence state; it does not replace the underlying papers, protocols, findings records, experiment artifacts, or prior-art audits.

## 1. Why this map exists

Several initiatives that began independently now attack different projections of one broad problem:

> **How can we identify, compare, reconstruct, align, control, or communicate through semantic and representational systems when their native coordinates, substrates, tokenizations, modalities, or internal mechanisms differ?**

The main maintenance rule is simple:

- **dynamic cross-project status lives here**;
- each paper owns its own claims, definitions, evidence, and limitations;
- papers should point here rather than duplicating a programme-wide state summary.

A negative result in one branch must not be silently propagated as a negative result for a sibling branch. In particular, the Torus is an optional geometric hypothesis inside the larger Pontifex programme; falsifying the Torus would not falsify Pontifex.

## 2. Status vocabulary

| status | meaning |
|---|---|
| `concept` | vocabulary or mathematical object proposed, not yet empirically established |
| `protocol` | prospective experimental design frozen or under implementation |
| `running` | experiment/infrastructure actively producing evidence |
| `evidence-positive` | at least one discriminating result supports the narrow claim stated |
| `evidence-negative` | at least one discriminating result weighs against the narrow claim stated |
| `mixed` | positive and adverse evidence materially coexist |
| `infrastructure` | enabling system rather than a scientific claim |
| `adjacent` | scientifically related but not a Pontifex subproject |

These labels summarize the public record; the underlying artifact remains authoritative.

## 3. Top-level programme

~~~text
SEMANTIC / REPRESENTATIONAL SYSTEMS
│
├── Observation theory
│   └── Semantic Observers
│
├── Static geometry
│   ├── Semantic Atlas
│   │   ├── static geometry
│   │   ├── manifolds
│   │   ├── spectral bottleneck
│   │   ├── relational dynamics
│   │   ├── alignment tournament
│   │   └── dynamic gauge compression
│   └── Dynamic Quasar Reference Frames
│
├── Inverse semantics
│   └── Perquire  [external repository]
│
├── Interventional identification
│   ├── Pontifex
│   │   ├── byte/tokenizer-free intervention
│   │   ├── bilateral response signatures
│   │   ├── multi-space convergence / synergy
│   │   ├── cross-lingual / cross-modal probing
│   │   ├── active experimental design
│   │   ├── system identification
│   │   └── held-out observer prediction
│   │
│   ├── Interventional Latent Graph
│   ├── Narrative Proxy Interventions
│   └── Torus [optional geometric/model class]
│       ├── periodic / seam / gauge geometry
│       ├── multiscale occlusion cartography
│       ├── directed traversal / cycles / hysteresis
│       ├── transport and embedding reconstruction
│       ├── active cartography / virtual traversal
│       ├── Torus Assembly
│       ├── semantic tomography
│       ├── Noether-style structural hypotheses
│       └── domain stress tests (text, retrieval, CMB, sensors)
│
├── Multi-observer information
│   └── Synergy Geometry
│
├── Alternative substrates
│   └── MaleCNS
│       ├── connectome reservoir / adapters
│       ├── proxy-intervention alignment
│       └── controller / closed-loop roles
│
├── Semantic computation
│   └── Semantic Tokenization Transformers
│
├── Structural identification / formal methods
│   └── Structural Identification from Restricted Truths
│
└── Machine interaction / agency [adjacent programme]
    ├── Machine Interaction Program
    ├── Interstitial Agent
    ├── Forbidden Relay
    ├── RL relay transducers
    ├── informational time
    └── machine discovery
~~~

## 4. Four complementary access modes

The core initiatives differ most cleanly by **what is observed**:

| initiative | primitive question | observation mode |
|---|---|---|
| **Perquire** | What might this unknown vector mean? | interrogate one point through candidate generation + scalar similarity feedback |
| **Semantic Atlas** | What is the structure of this representation? | observe static relational/geometric structure across many points |
| **Pontifex** | How does this system react to controlled change? | intervene and measure within-system response signatures |
| **Semantic Observers** | What can each system observe, and at what resolution? | compare observability, parallax, blind spots, and informativeness across systems |

These are complementary, not competing definitions of the same method.

A long-term unification target is therefore:

[
\ext{static observations}
+
\ext{interventional responses}
+
\ext{inverse queries}
\ightarrow
\ext{better system identification}.
]

## 5. Pontifex — core programme independent of Torus

**Canonical paper:** `pontifex.md`  
**Current status:** `mixed`

Pontifex compares systems using shared or semantically matched interventions and measures responses **inside each system**, avoiding the assumption that raw coordinates are directly comparable.

Stable non-Torus fronts include:

1. byte-level / tokenizer-free occlusion;
2. bilateral response signatures;
3. multi-space convergence versus single-space / mean / learned-weight baselines;
4. encoder-diversity scaling and semantic-family scaling;
5. channel corruption / weak-observer robustness;
6. causal-span localization;
7. static-alignment versus intervention-response alignment;
8. active probe selection;
9. cross-lingual and cross-modal intervention tests;
10. held-out observer prediction;
11. interventional fingerprints / system identification;
12. observational equivalence classes under an intervention family;
13. intervention algebra and compositional interventions;
14. proxy interventions when substrates cannot receive the same physical perturbation.

The early RED-1 nonlinear convergence head is **not** the programme definition. Its instability under scale/diversity is evidence against that particular implementation and motivated more structured alternatives.

## 6. Torus — optional Pontifex geometry/model class

**Canonical paper:** `pontifex_torus.md` on the active experimental branch until consolidated.  
**Current status:** `mixed`

The Torus organizes intervention-indexed response fields in a periodic multiscale substrate. It is explicitly **not** a claim that embedding spaces are intrinsically topological tori.

Current fronts:

- periodic Fourier coordinates;
- seam rotation and coordinate-gauge invariance;
- occlusion size and context horizon as lenses;
- directed/bidirectional traversal and repeated passes;
- response-field transport;
- sparse acquisition / active cartography;
- embedding reconstruction;
- Procrustes coarse alignment + low-capacity residual deformation;
- regional decoder and anchor-capacity ablations;
- nonlinear/cross-term transport models;
- Torus Assembly / multi-teacher response geometry;
- narrative phase;
- semantic tomography;
- structural Noether-style phase/conservation hypotheses;
- domain stress tests including CMB and terrain/sensor-style fields.

### Evidence boundary

Evidence for a periodic coordinate system or useful Fourier features is not evidence that semantic space is intrinsically toroidal. Likewise, positive reconstruction does not by itself establish downstream utility or causal mechanism.

## 7. Interventional Latent Graph

**Canonical paper:** `interventional_latent_graph.md`  
**Current status:** `concept` + formal structural results

Minimal rule:

[
\oxed{\ext{one shared intervention}=\ext{one edge}}
]

Vertices are representational systems/spaces; edges are shared experimental contrasts. Edge existence does not assert similarity, response agreement, common ontology, or causal equivalence.

The ILG deliberately sits **before geometry**. Cycles, communities, coverings, manifolds, or toroidal realizations are downstream empirical hypotheses.

## 8. Narrative Proxy Interventions

**Canonical paper:** `pontifex_malecns_narrative_proxy_interventions.md`  
**Current status:** `protocol`

For heterogeneous substrates, the same physical intervention may be impossible. The shared object becomes an intervention concept (c) with substrate-native realizations:

[
c\ightarrow R_A(c),
qquad
c\ightarrow R_B(c).
]

For sequential systems, the atomic experimental object is better written as:

[
i=(c,\au,h),
]

where (\au) is narrative position and (h) is relevant history.

This front is broader than MaleCNS and broader than Torus.

## 9. Semantic Observers

**Canonical paper:** `semantic_observers.md`  
**Current status:** `concept` / experimental programme

Observer model:

[
O_m:mathcal U\ightarrow mathcal Z_m
]

with (mathcal U) treated initially as a latent **relational** structure rather than a globally Euclidean universe.

Main fronts:

- multiscale semantic resolution;
- blind spots and distortion;
- semantic parallax;
- approximate observer dominance / informativeness;
- local versus global observability;
- multi-observer reconstruction;
- topology visible only at certain observer capabilities/scales.

Semantic Observers supplies vocabulary that can organize both static Atlas measurements and interventional Pontifex measurements.

## 10. Semantic Atlas

**Canonical papers:**  
- `semantic_atlas.md`  
- `semantic_atlas_static_geometry.md`  
- `semantic_atlas_manifolds.md`

**Experiments:** `experiments/semantic_atlas/`  
**Current status:** `running` / `mixed`

Semantic Atlas studies representation structure **without requiring interventions**.

Major fronts already represented in the repository:

- static geometry;
- multiscale neighborhoods / mKNN;
- model-backed atlas construction;
- gallery scaling;
- relational dynamics and relational stability;
- manifold-aware charts and tangent structure;
- spectral structure;
- spectral bottleneck;
- cross-model replication;
- alignment tournament;
- dynamic gauge compression;
- planning/control and inverse-route memory;
- static versus dynamic reference frames.

### Interface with Pontifex

A central comparative question is:

[
\ext{Does intervention-response structure add predictive information beyond static Atlas geometry?}
]

That comparison should be preferred over assuming that every cross-model effect is uniquely interventional.

## 11. Perquire — semantic inversion by iterative questioning

**Repository:** <https://github.com/franklinbaldo/perquire>  
**Canonical local docs:** `README.md`, `docs/research_contract.md`  
**Current status:** `running` / active v2 protocol

Perquire receives a target embedding (v) and searches for natural-language semantic preimages using candidate generation and scalar similarity feedback.

The v1 adaptive-scaling study failed its operational validity gate and remains historical evidence. The active scientific question is the causal-feedback v2 experiment:

- `true_feedback`;
- `decoy_feedback`;
- `null_feedback`;

with proposer mechanism and resource opportunities held fixed.

A positive v2 result would support the usefulness of target-relevant feedback for search. It would **not** by itself establish semantic recovery; that requires a separately frozen held-out evaluator.

### Interface with this repository

- Perquire owns executable inversion experiments and results.
- `papers` owns broader representational theory and may cite Perquire evidence.
- Perquire should not inherit claims from Semantic Atlas or Pontifex automatically.

## 12. Synergy Geometry

**Canonical protocol:** `experiments/synergy_geometry/protocol.md`  
**Current status:** `protocol`

Question:

> Do several observers jointly reveal information not reducible to the best observer or a redundant combination?

This is the general information-theoretic version of the early Pontifex convergence question and should not be tied to a specific convergence head.

It provides a natural bridge among:

- Pontifex multi-space responses;
- Semantic Observers complementarity;
- Semantic Atlas multi-model fusion;
- Torus Assembly reliability fields.

## 13. Dynamic Quasar Reference Frames

**Canonical paper:** `dynamic_quasar_reference_frames.md`  
**Current status:** `adjacent` / geometric-reference programme

This initiative studies dynamic reference frames and canonical vector fields for trajectory, reachability, flow, and control.

Its strongest adjacency is to:

- Semantic Atlas dynamic gauge compression;
- Torus seam/gauge invariance;
- representation alignment under moving references.

It should remain independent because the reference-frame problem is broader than semantic intervention.

## 14. Structural Identification from Restricted Truths

**Canonical paper:** `structural_identification_from_restricted_truths.md`  
**Current status:** `adjacent` / formal foundation

General question:

> Given a restricted family of observations/truths and a hypothesis class, what structure is identifiable, up to which equivalences, and at what cost?

This is a mathematical foundation for:

- Pontifex intervention identifiability;
- Semantic Atlas gauge freedom;
- observer equivalence;
- minimal probe sets;
- held-out-system prediction;
- formal separation between identifiable structure and coordinate convention.

## 15. MaleCNS

**Canonical related papers include:**  
- `malecns_connectome_reservoir_tagging.md`  
- `pontifex_malecns_narrative_proxy_interventions.md`

**Current status:** `running` across several experiment families

MaleCNS is not one hypothesis. It can play at least three roles:

1. **observer/substrate** — compare a biological connectome-derived dynamical system with artificial representations;
2. **operator** — frozen connectome dynamics between trainable adapters;
3. **controller** — select probes/actions or close an external feedback loop.

Its relevance to Pontifex is strongest as a radical heterogeneous substrate that forces proxy-intervention and coordinate-free comparison to be explicit.

## 16. Semantic Tokenization Transformers

**Canonical paper:** `semantic_tokenization_transformers.md`  
**Current status:** `concept` / position paper

STT asks whether semantic representations can become the **computational unit** of sequence modeling:

[
\ext{text}\ightarrow\ext{semantic chunks}\ightarrow
\ext{embedding}\ightarrow\ext{RVQ codes}\ightarrow\ext{sequence model}.
]

It is adjacent because:

- Semantic Atlas can characterize candidate semantic-code geometry;
- Perquire can help interpret centroids/codes;
- Pontifex can test whether code/chunk boundaries are causally meaningful;
- Semantic Observers can compare code observability across models.

STT remains an application of semantic representation, not evidence for Pontifex or Atlas.

## 17. Machine Interaction Program

**Canonical map:** `machine_interaction_program.md`  
**Current status:** `adjacent`

This is a separate but intersecting programme about repeated interaction among machine systems:

- generative machine teaching;
- pedagogical signal extraction;
- informational time;
- interstitial agency;
- RL relay transducers;
- Forbidden Relay;
- machine discovery.

Its common interface with the semantic-systems programme is **interaction as an information-bearing experimental object**.

## 18. Interstitial Agent

**Canonical paper:** `interstitial_agent.md`  
**Current status:** `adjacent`

Question:

> Can agency or persistent informational state reside in the coupling among components rather than in any individual model?

This is relevant to Pontifex cycles, MaleCNS closed loops, and multi-system response dynamics, but it is an agency claim rather than a representation-geometry claim.

## 19. Forbidden Relay / relay transducers

**Canonical papers:** `forbidden_relay.md`, `rl_relay_transducers.md`  
**Current status:** `protocol` / adjacent

These ask how information survives transformation chains:

[
z\ightarrow M_0\ightarrow M_1\ightarrowcdots\ightarrow M_N\ightarrowhat z.
]

This is approximately dual to Pontifex:

- Pontifex: what does a controlled perturbation reveal about a system?
- Relay: what information survives passage through a system?

Shared methods may include intervention design, independent decodability, depth controls, and information-preservation metrics.

## 20. Active Experimental Design — cross-cutting methodological initiative

Several projects independently need to choose the **next query/intervention** under budget:

- Perquire: next semantic question/candidate;
- Pontifex: next probe;
- Torus: next cartographic sample;
- Machine Interaction: next relay/action;
- Semantic Atlas: next informative anchor/chart.

This should be treated as shared methodology rather than independently reinvented in each repository.

Candidate methods include:

- contextual bandits;
- information gain;
- uncertainty reduction;
- expected model discrimination;
- active learning;
- k-center / coverage methods.

## 21. Adjacent control/action-space research

### Affordance Restriction

**Paper:** `affordance_restriction.md`

Controls what an agent is allowed to do rather than discovering latent geometry.

Useful conceptual duality:

- Pontifex studies the **response space** under interventions.
- Affordance Restriction constrains the **action space** from which interventions can be selected.

### Machine interaction / auditability

This family should remain adjacent, because its main claims concern agency, safety, audit, communication, and discovery rather than representation identification.

## 22. Shared experimental opportunities

### 22.1 Unified Semantic Identification Benchmark

A common benchmark should compare, on the **same models, data, and held-out endpoints**:

1. static Semantic Atlas only;
2. Perquire-style queries only;
3. Pontifex interventions only;
4. Atlas + Pontifex;
5. Atlas + Pontifex + Perquire;
6. optional Torus model class;
7. simple coordinate-alignment baselines.

Primary question:

> Which observation channel contains which uniquely predictive information about a held-out representation or observer?

### 22.2 Static × interventional quadrant

For two observers (A,B):

| static similarity | intervention similarity | interpretation |
|---|---|---|
| high | high | strong relational equivalence |
| high | low | similar static geometry, different dynamics |
| low | high | different coordinates/geometries, similar causal response |
| low | low | strongly distinct observers |

### 22.3 Held-out observer

A high-value common endpoint is to learn structure from (O_1,ldots,O_{n-1}) and predict a frozen (O_n) never used in construction.

### 22.4 Alternative-substrate escalation

After artificial-model benchmarks, the same frozen protocols can be escalated to heterogeneous endpoints such as MaleCNS. Proxy interventions must be specified prospectively; renderer tuning after observing cross-space agreement is prohibited.

## 23. Dependency and non-dependency rules

The following rules prevent programme-wide overclaiming:

1. **Pontifex does not require Torus.**
2. **Semantic Atlas does not require Pontifex.**
3. **Perquire does not establish a universal semantic geometry.**
4. **Semantic Observers is a modelling language, not evidence that a unique observer-independent semantic universe exists.**
5. **MaleCNS success does not validate Torus unless the Torus-specific comparator is discriminated.**
6. **Torus transport success does not establish downstream task benefit.**
7. **Static alignment success does not establish interventional equivalence.**
8. **Interventional equivalence on a finite probe family does not establish global equivalence.**
9. **A shared intervention concept across heterogeneous substrates does not guarantee identical causal realization.**
10. **Adjacent machine-interaction results do not automatically support representation-geometry claims.**

## 24. Maintenance rule for papers

Every paper in this ecosystem should contain a short section titled **Research programme position** with exactly four items:

- **Initiative:** which node in this map owns the paper;
- **Scope:** what this paper claims/tests;
- **Not claimed here:** nearest adjacent claims owned elsewhere;
- **Canonical map:** link to this file.

Do **not** duplicate this map's dynamic status tables inside individual papers.

When programme structure changes, update this file first. Update a paper only when its own claim, evidence, protocol, or boundary changes.

## 25. Immediate programme-level next step

The most useful shared experiment is not another domain-specific demonstration. It is a **Unified Semantic Identification Benchmark** with common data splits and held-out endpoints, allowing static, interventional, inverse-query, and combined methods to compete under one evaluation contract.

That benchmark would tell us whether these initiatives are genuinely complementary or merely rediscovering the same signal through different interfaces.


## 26. Cross-line consistency register

This register tracks places where two research lines can be individually reasonable but jointly inconsistent, ambiguous, or vulnerable to claim leakage. A row stays open until the linked issue's acceptance criterion is met.

| priority | inconsistency | affected initiatives | risk | issue |
|---|---|---|---|---|
| **P0** | Pontifex core says it avoids explicit alignment, while current transport branches use Procrustes / explicit maps | Pontifex, Torus transport, benchmarks | foundational-method ambiguity: readers may think the programme reversed its primitive rather than added an optional downstream stage | [#670](https://github.com/franklinbaldo/papers/issues/670) |
| **P0** | STT can read as if a single teacher's embedding defines observer-independent semantic units | STT, Semantic Observers, Semantic Atlas | ontology leakage: teacher-relative codes can be mistaken for universal semantic atoms | [#671](https://github.com/franklinbaldo/papers/issues/671) |
| **P0** | Semantic Atlas global/shared-geometry language can outrun the local/observer-relative evidence boundary | Semantic Atlas, Semantic Observers, Structural Identification | overclaiming global geometry from local relational agreement | [#672](https://github.com/franklinbaldo/papers/issues/672) |
| **P1** | MaleCNS appears as observer, operator, controller, and optional Torus component; evidence can leak across roles | MaleCNS, Pontifex, Torus | role conflation and invalid cross-paper inference | [#676](https://github.com/franklinbaldo/papers/issues/676) |
| **P1** | Gauge / equivalence / identifiability terminology is independently redefined in several lines | Structural Identification, Semantic Atlas, Pontifex, ILG, Torus | duplicated formal work and incompatible theorem statements | [#675](https://github.com/franklinbaldo/papers/issues/675) |

### Consistency interpretation rules

1. An inconsistency is not automatically a contradiction in the underlying science. It may be a **scope or ontology mismatch** that needs explicit wording.
2. Historical papers/results are preserved. Corrections should narrow interpretation or add stage distinctions rather than rewrite the empirical record.
3. A cross-line issue is closed only when every affected canonical paper either:
   - adopts the common definition/boundary; or
   - explicitly states why its usage is intentionally different.
4. Evidence does not propagate across initiative boundaries unless an experiment was designed to discriminate that bridge claim.

## 27. Synergy register

This register tracks reusable work that should flow from one initiative into another rather than being reimplemented.

| priority | source capability | potential consumer | reuse / new discriminant | issue |
|---|---|---|---|---|
| **P0** | Synergy Geometry vocabulary and controls for redundancy / unique information / interaction | RED-1, Semantic Observers, Semantic Atlas multi-model fusion, Torus Assembly | make multi-observer gain use one baseline ladder and one interaction vocabulary | [#673](https://github.com/franklinbaldo/papers/issues/673) |
| **P0** | Static Atlas + Pontifex interventions + Perquire inverse queries | all semantic-identification lines | Unified Semantic Identification Benchmark under common splits and held-out observer | [#674](https://github.com/franklinbaldo/papers/issues/674) |
| **P1** | Structural Identification equivalence/gauge formalism | Atlas gauge compression, Torus seam/gauge, Pontifex equivalence, ILG paths | shared glossary + reusable Lean definitions instead of parallel formalizations | [#675](https://github.com/franklinbaldo/papers/issues/675) |
| **P1** | Semantic Observers resolution/parallax metrics | STT, Perquire, Pontifex, MaleCNS | use a frozen held-out observer to test whether "semantic" structure generalizes beyond the constructing observer | [#671](https://github.com/franklinbaldo/papers/issues/671) |
| **P1** | Pontifex response fields | Semantic Atlas | compare static geometry against differential/interventional geometry on the same stimuli | [#674](https://github.com/franklinbaldo/papers/issues/674) |
| **P1** | Perquire target-relevant feedback experiment | Pontifex active probing / Atlas active anchor selection | share active-experimental-design methods while keeping scientific endpoints separate | [#674](https://github.com/franklinbaldo/papers/issues/674) |
| **P2** | MaleCNS proxy-intervention protocol | cross-modal Pontifex / alternative-substrate tests | stress-test whether correspondence survives radically heterogeneous native realizations | [#676](https://github.com/franklinbaldo/papers/issues/676) |
| **P2** | Dynamic Quasar / dynamic gauge machinery | Semantic Atlas + Torus | compare moving-reference explanations against periodic-coordinate explanations before introducing new geometry | [#675](https://github.com/franklinbaldo/papers/issues/675) |

### Reuse rule

Before adding a new metric, aligner, active sampler, notion of equivalence, or multi-observer baseline to a paper, check this register. If an equivalent component already exists elsewhere in the programme, prefer:

1. reuse unchanged;
2. adapt behind a clearly named interface;
3. only create a new version when the existing one fails a documented requirement.

The consumer paper should cite the source initiative and state whether the reused component is evidence, methodology, or infrastructure.

## 28. Issue escalation policy

The map itself is the first place to record a cross-line concern. Escalate to a repository issue when at least one of the following is true:

- a canonical paper's claim boundary must change;
- an experiment must be rerun or a new discriminant is required;
- two papers use materially incompatible definitions;
- evidence is being cited across initiatives without a valid bridge experiment;
- a shared component would eliminate duplicated experimental or formal work;
- the inconsistency could change the interpretation of a published/preprint-ready claim.

Minor wording drift stays in this map until the next normal paper edit.

Each escalated issue should state:

- affected papers/initiatives;
- exact inconsistency or unrealized synergy;
- why it matters scientifically;
- required change or discriminating experiment;
- acceptance criterion.

## 29. Priority queue

### P0 — correct before expanding the programme

1. **Pontifex core vs explicit transport** — [#670](https://github.com/franklinbaldo/papers/issues/670). Clarify that coordinate-free intervention comparison is the core primitive and explicit transport is an optional later stage.
2. **Observer-relative semantics in STT** — [#671](https://github.com/franklinbaldo/papers/issues/671). Prevent one teacher embedding from silently becoming the semantic ontology.
3. **Semantic Atlas global-geometry boundary** — [#672](https://github.com/franklinbaldo/papers/issues/672). Make local relational evidence the default and label stronger universal geometry as hypothesis.
4. **Shared multi-observer evaluator** — [#673](https://github.com/franklinbaldo/papers/issues/673). Consolidate RED-1 / Assembly / observer-fusion metrics into Synergy Geometry.
5. **Unified Semantic Identification Benchmark** — [#674](https://github.com/franklinbaldo/papers/issues/674). This is the main anti-duplication experiment: determine whether Atlas, Pontifex and Perquire contain complementary information under one frozen evaluation contract.

### P1 — unify language and prevent future divergence

6. **Shared identifiability / gauge vocabulary and formal primitives** — [#675](https://github.com/franklinbaldo/papers/issues/675).
7. **MaleCNS role separation** — [#676](https://github.com/franklinbaldo/papers/issues/676): observer vs operator vs controller vs Torus component.

### P2 — exploit validated bridges after P0/P1

8. Reuse active-design machinery across Perquire, Pontifex and Atlas.
9. Use held-out-observer metrics from Semantic Observers as a cross-project validity layer.
10. Compare Dynamic Quasar moving-reference explanations directly against Torus periodic-coordinate explanations where both can fit the same phenomenon.

## 30. Cross-paper change-control loop

For every substantial new result:

1. update the originating findings record / paper;
2. ask whether it changes any row in the consistency or synergy register;
3. update this map;
4. if a P0/P1 boundary or reusable component changed, update the linked issue;
5. only edit sibling papers if their **own claim boundary or evidence** changed;
6. never propagate a conclusion to a sibling solely because the projects are adjacent.

This loop is intended to make the map an active scientific control surface rather than a static taxonomy.
