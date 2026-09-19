---
type: "Scientific Position Paper"
title: "Narrative Proxy Interventions: Aligning Language Embeddings and the Drosophila MaleCNS Through Shared Causal Stories in the Pontifex Torus"
description: "A falsifiable protocol for aligning a language-embedding trajectory and a Drosophila MaleCNS trajectory through native proxy realizations of the same ordered causal story, using monotone narrative time rather than direct latent-coordinate alignment."
tags: [pontifex, torus, malecns, drosophila, embeddings, causal-interventions, narrative-time, representation-alignment, connectome]
timestamp: 2026-09-19T09:41:00-04:00
authors:
  - ref: /authors/franklin-silveira-baldo.md
    byline: "Franklin Silveira Baldo"
    affiliations:
      - "Independent Researcher"
    corresponding: true
publication:
  status: draft
  targets: [zenodo]
  zenodo:
    publication_type: preprint
    access_right: open
    license: cc-by-nc-4.0
    version: "0.1"
---

# Narrative Proxy Interventions

## Aligning Language Embeddings and the Drosophila MaleCNS Through Shared Causal Stories in the Pontifex Torus

**Franklin Silveira Baldo**  
Independent Researcher  
franklinbaldo@gmail.com

> **Scientific position paper.** This manuscript proposes a formal object, an experimental protocol, controls, and falsifiable predictions. It reports no new empirical measurements. The proposed correspondences between textual descriptions and Drosophila interventions are experimental proxies, not claims that a structural connectome fully simulates Drosophila neurophysiology. In particular, neuromodulatory manipulations must not be represented as if synaptic connectivity alone encoded their chemical dynamics.

## Abstract

Cross-model representation alignment is usually posed as a problem of mapping coordinates, matching samples, or constructing a shared latent space. Those formulations become awkward when the two systems differ not only in coordinates but in substrate and modality: for example, a text embedding model and a recurrent computation constrained by the complete male *Drosophila* central nervous system connectome. We propose a different experimental primitive. The shared object is neither an input token nor a physical stimulus. It is an **ordered causal story** whose events are expressed through **native proxy realizations** appropriate to each system.

A canonical story is parameterized by narrative time \\(\\tau\\in[0,1]\\), with explicit initial and terminal conditions. Each event is a conceptual intervention \\(c_i\\) located at narrative position \\(\\tau_i\\). A text branch realizes the intervention by changing a natural-language account of the story and measures the resulting trajectory in a frozen embedding model. A connectome branch realizes the same intervention through an anatomically declared sensory, motivational, or reinforcement proxy and measures the resulting recurrent MaleCNS trajectory. The two realizations need not be physically or representationally identical. They are required only to be independently defensible realizations of the same intervention concept and to preserve causal order.

The Pontifex Torus is then asked to align the **response geometries** of the two ordered trajectories without directly aligning their latent coordinates. A monotone time-warp permits different local rates while forbidding causal inversion. The protocol distinguishes experimental ground truth from information supplied to the aligner: concept identities may be used to generate both branches, but can be hidden from Pontifex so that successful matching cannot be obtained merely by reading shared labels. The strongest test holds out internal events or entire story variants, fits the cross-space cartography on the remainder, and asks whether the language-side response predicts the location and relational neighborhood of the corresponding MaleCNS response.

The framework yields several falsifiable predictions. Complete stories should align better than equally informative fragments lacking boundary conditions; removal of beginnings or endings should degrade matching more than removal of comparable interior material if boundaries constrain the trajectory; cumulative-prefix embeddings should outperform sentence-isolated embeddings if history matters; temporally permuted stories should collapse alignment; and biological MaleCNS topology should outperform matched rewired or random recurrent controls only if its organization contributes structure beyond generic recurrence. The proposal therefore converts the qualitative claim that two heterogeneous systems may share causal structure into a controlled test of whether they preserve the same **ordered algebra of intervention consequences**.

**Keywords:** Pontifex, MaleCNS, Drosophila connectome, narrative time, causal interventions, proxy intervention, representation alignment, embeddings, monotone alignment, response geometry

---

## 1. Introduction

Suppose two systems are asked about the same phenomenon but do not accept the same kind of input. A language embedding model operates naturally on text. A Drosophila connectome-derived dynamical system operates naturally on activity injected into biologically interpretable neuronal populations. Requiring the exact same physical perturbation at both endpoints would make the comparison artificial: text is not sucrose, and a connectome does not read English. Requiring the same vector would be worse, because it would pre-impose a coordinate system whose recovery is supposedly the object of study.

The Pontifex programme instead treats controlled interventions as bridges between otherwise unaligned representational spaces. Earlier Pontifex formulations used common occlusions and within-space response changes as externally shared probes. The Interventional Latent Graph formulation sharpened the primitive further: one shared intervention creates one operational edge between spaces, without asserting that the spaces are already equivalent.

This paper adds a missing constraint. For sequential systems, an intervention does not occur in a vacuum. Its consequence depends on what happened before it. Hunger followed by sugar contact is not the same event as sugar contact followed by hunger. A word inserted at the beginning of a story does not have the same representational consequence when inserted after the narrative has established different characters, goals, or causal conditions. If Pontifex is to compare sequential substrates, the shared object must therefore contain not only **what intervention occurred**, but **where it occurred in a history**.

We propose that the experimental bridge should be an **ordered causal story** with explicit boundaries. The story supplies a canonical one-dimensional coordinate \\(\\tau\\) running from an initial condition to a terminal condition. Each substrate realizes that story in its native medium:

\\[
H
\\xrightarrow{R_Q}
\\gamma_Q(\\tau),
\\qquad
H
\\xrightarrow{R_F}
\\gamma_F(\\tau),
\\]

where \\(R_Q\\) produces a textual realization observed through a frozen language embedding model and \\(R_F\\) produces a connectome-native realization observed through a MaleCNS dynamical model.

The proposal makes three separations that are essential to avoid a tautological alignment.

First, the **intervention concept** is distinct from its **realization**. "Increase hunger" may be represented textually by changing the described deprivation interval and neurally by changing a declared hunger-related modulatory channel. The two implementations are proxies of the same concept; neither is a translation of the other.

Second, **experimental ground truth** is distinct from **aligner input**. The protocol may know that two manipulations instantiate the same concept so that the experiment can be constructed and scored. Pontifex need not be told that identity. In the strongest setting it receives only ordered trajectories, boundary anchors, and response measurements.

Third, **narrative time** is distinct from physical time and token position. The text may devote several sentences to a transition that takes milliseconds in a neural simulation. Alignment therefore preserves order but allows a monotone deformation of local rate.

The primary scientific question is:

> Can two radically different substrates be aligned by the relational geometry of their responses to native realizations of the same ordered causal story, beyond what is explained by shared time, shared labels, generic recurrence, or a directly learned coordinate translator?

The paper develops a precise protocol for answering that question.

---

## 2. Relation to Pontifex and the Interventional Latent Graph

### 2.1 From shared object to shared concept

The earliest Pontifex formulation compared spaces through common perturbations. For text encoders, this could mean applying the same byte-level occlusion to the same source text and measuring the response independently in each latent space.

That symmetry is unavailable when one endpoint is a language encoder and the other a connectome. The exact perturbation cannot be shared. What can be shared is the **intervention concept**.

Let \\(C\\) be a registry of experimental intervention concepts. For each substrate \\(S\\), define a realization function

\\[
R_S : C \\times X_S \\rightarrow X_S,
\\]

where \\(X_S\\) is the substrate-specific state or input domain.

For a concept \\(c\\in C\\),

\\[
R_Q(c) \\neq R_F(c)
\\]

in general. The equality demanded by the experiment is not equality of objects. It is equality of intended experimental semantics.

The resulting structure is a fork:

\\[
R_Q(c) \\leftarrow c \\rightarrow R_F(c).
\\]

No text-to-fly or fly-to-text translator is required to define the intervention.

### 2.2 Refining one intervention = one edge

The Interventional Latent Graph proposal uses the deliberately minimal rule:

> one intervention = one edge.

For sequential data, we refine an intervention instance to

\\[
i_k=(c_k,\\tau_k,h_k),
\\]

where:

- \\(c_k\\) is the intervention concept;
- \\(\\tau_k\\in[0,1]\\) is its canonical narrative position;
- \\(h_k\\) denotes the relevant preceding history.

The concept alone is insufficient because

\\[
\\operatorname{Effect}(c,\\tau,h)
\\neq
\\operatorname{Effect}(c,\\tau',h')
\\]

in general.

The atomic edge therefore remains an intervention, but an **intervention-in-history**.

### 2.3 Why explicit beginnings and endings matter

A story fragment beginning in the middle still contains local ordering and may remain alignable. The proposal does not require a "natural" beginning in a metaphysical sense. It predicts only that explicit boundary conditions reduce ambiguity.

If \\(H_{0:1}\\) is the complete observed story and \\(H_{a:b}\\) a fragment,

\\[
\\mathcal{I}(H_{0:1}) \\geq \\mathcal{I}(H_{a:b})
\\]

is the empirical prediction, where \\(\\mathcal{I}\\) is an alignment-identifiability measure defined operationally by held-out matching performance.

The loss of a beginning removes information about the state entering the fragment. The loss of an ending removes information about which trajectories converge to the same terminal outcome. Thus boundaries can act as constraints rather than as arbitrary formatting.

---

## 3. Formal framework

### 3.1 Canonical causal story

A canonical story is

\\[
H=(V,\\prec,b,e,\\lambda),
\\]

where:

- \\(V=\\{v_0,\\dots,v_n\\}\\) is a set of event states;
- \\(\\prec\\) is an acyclic precedence relation;
- \\(b\\in V\\) is the declared initial condition;
- \\(e\\in V\\) is the declared terminal condition;
- \\(\\lambda(v)\\) contains intervention concepts and state annotations.

For the first experiments we restrict the story to a total order,

\\[
v_0 \\prec v_1 \\prec \\cdots \\prec v_n,
\\]

and assign canonical narrative coordinates

\\[
0=\\tau_0 < \\tau_1 < \\cdots < \\tau_n=1.
\\]

This one-dimensional restriction is intentional. Branching stories are a later extension. The initial question is whether the Torus can exploit a clean ordered history before introducing partial orders or alternative futures.

### 3.2 Native realization

Each substrate has a renderer

\\[
\\rho_S(H) = x_S(\\tau).
\\]

For the language branch, \\(x_Q(\\tau)\\) is a textual prefix or textual state. For the MaleCNS branch, \\(x_F(\\tau)\\) is a time-indexed pattern of sensory/modulatory input to declared neuronal populations.

The renderer is not itself learned from the cross-space outputs in the confirmatory experiment. It is specified before response data are inspected.

This constraint blocks a serious failure mode: if a renderer is repeatedly adjusted until the two spaces agree, the experiment merely learns its own desired correspondence.

### 3.3 Observer trajectory

Each branch has an observer

\\[
O_S : X_S \\rightarrow Z_S
\\]

that produces a state in its own representation space.

The trajectory is

\\[
\\gamma_S(\\tau)=O_S(\\rho_S(H)(\\tau)).
\\]

The spaces \\(Z_Q\\) and \\(Z_F\\) may differ in dimensionality, metric, topology, and physical interpretation. Pontifex does not require direct coordinate comparability.

### 3.4 Counterfactual intervention response

For an intervention concept \\(c\\) applied at \\(\\tau_i\\), define a baseline history \\(H\\) and a counterfactual history \\(H^{(i,c)}\\). The substrate-specific response is measured within that substrate:

\\[
\\Delta_S(i,c;t)
=
d_S\\left(
\\gamma_S^{(i,c)}(t),
\\gamma_S(t)
\\right),
\\qquad t\\geq\\tau_i,
\\]

where \\(d_S\\) is a within-space discrepancy.

A richer response signature may retain the direction of change rather than only its magnitude:

\\[
r_S(i,c)
=
\\Psi_S\\left(
\\gamma_S^{(i,c)}[\\tau_i,1],
\\gamma_S[\\tau_i,1]
\\right).
\\]

Crucially, \\(r_Q\\) and \\(r_F\\) are never subtracted from one another. Comparability is built from their relational structure.

### 3.5 Response geometry

For intervention instances \\(i,j\\), define a substrate-internal relation

\\[
K_S(i,j)
=
k_S(r_S(i),r_S(j)),
\\]

where \\(k_S\\) may be a distance, similarity, kernel value, trajectory distance, or a vector of relational statistics.

The alignment target is preservation of the response geometry:

\\[
K_Q(i,j)
\\approx
K_F(\\pi(i),\\pi(j)),
\\]

for an order-preserving correspondence \\(\\pi\\).

This is deliberately weaker than

\\[
\\gamma_Q(\\tau) \\approx \\gamma_F(\\tau)
\\]

and does not require an isomorphism between latent coordinates.

### 3.6 Monotone narrative transport

Physical time and textual extent need not coincide. Let

\\[
\\phi:[0,1]\\rightarrow[0,1]
\\]

be a monotone temporal transport satisfying

\\[
\\phi(0)=0,\\qquad
\\phi(1)=1,\\qquad
\\phi'(\\tau)\\geq0
\\]

where differentiability is not required in implementation.

The alignment may stretch or compress local regions but must not reverse order.

An empirical objective can combine relational distortion and temporal regularization:

\\[
\\mathcal{L}
=
\\mathcal{L}_{rel}
+
\\alpha\\mathcal{L}_{mono}
+
\\beta\\mathcal{L}_{boundary}
+
\\eta\\mathcal{L}_{complexity}.
\\]

The monotonicity term forbids causal inversion. The boundary term anchors declared beginnings and endings. The complexity term prevents an arbitrarily flexible warping function from memorizing every training story.

Dynamic time warping is a natural baseline for this component, but the Pontifex claim cannot rest on monotone sequence alignment itself, which is established prior art. The research claim concerns whether intervention-response geometry supplies useful cross-substrate correspondence beyond time-only alignment.

---

## 4. Experimental design

### 4.1 Stage A: clamped narrative playback

The first experiment should not begin with an embodied fly agent whose own actions change the world. That would confound representational alignment with policy learning, credit assignment, and environment dynamics.

Stage A therefore uses a **clamped causal story**: both branches receive externally scheduled realizations of the same event sequence. The connectome still evolves recurrently, so its current state depends on history, but the external event order is controlled.

Only after Stage A succeeds should the experiment move to a closed perception-action loop.

### 4.2 A canonical feeding story

A suitable initial story is a feeding episode because it supports interpretable sensory and motivational variables and because hunger is known to modulate sugar sensing in *Drosophila*.

A canonical event sequence might be:

| \\(\\tau\\) | event concept | story role |
|---:|---|---|
| 0.00 | food-deprived initial state | boundary / initial condition |
| 0.15 | appetitive odor appears | distal cue |
| 0.30 | odor intensity increases | approach proxy |
| 0.45 | sugar contact | gustatory event |
| 0.60 | feeding / nutrient availability | consumption |
| 0.75 | satiety increases | internal-state transition |
| 0.90 | food-seeking drive decreases | behavioral consequence |
| 1.00 | stable post-feeding state | boundary / terminal condition |

This table is not a claim that MaleCNS alone simulates all listed physiology. It is a story schema whose individual realizations must be restricted to channels the chosen MaleCNS model can defend.

### 4.3 Story family rather than one script

The actual dataset should contain a controlled family of variants:

- stronger versus weaker initial deprivation;
- low versus high sugar concentration;
- appetitive odor absent, present, early, or delayed;
- sugar contact omitted after an odor cue;
- bitter/aversive input inserted before feeding;
- feeding interrupted;
- satiety transition early or delayed;
- identical event concepts with altered inter-event intervals;
- matched paraphrases of the textual realization.

This creates a grid of stories sharing structure without being identical.

### 4.4 Language branch

A practical first observer is Qwen3-Embedding-0.6B, an Apache-2.0 text embedding model small enough to run locally in many research environments. The framework is model-agnostic; the embedding model should be frozen throughout the confirmatory run.

The key design choice is to represent **history cumulatively**.

At narrative position \\(\\tau_k\\), the text branch should embed the story prefix

\\[
P_k = [s_0,s_1,\\ldots,s_k]
\\]

rather than only the isolated sentence \\(s_k\\).

Thus

\\[
\\gamma_Q(\\tau_k)=E(P_k).
\\]

This creates a closer structural analogue to a recurrent neural state: both observers contain information accumulated from the beginning of the episode.

A sentence-isolated trajectory,

\\[
E(s_k),
\\]

is retained as an ablation. If story history is genuinely important, cumulative-prefix embeddings should provide a stronger cross-substrate correspondence than isolated event descriptions.

#### Counterfactual textual interventions

A conceptual intervention should change the story in a semantically natural manner.

Example:

Baseline:

> The fly has been deprived of food for 4 hours. It encounters a weak sucrose source.

Counterfactual:

> The fly has been deprived of food for 24 hours. It encounters a weak sucrose source.

The intervention concept is \\(c=\\texttt{increase_hunger}\\). The textual change is only its language-native realization.

Another example:

Baseline:

> The fly contacts a 1% sucrose solution.

Counterfactual:

> The fly contacts a 10% sucrose solution.

Here \\(c=\\texttt{increase_sugar}\\).

To reduce wording artifacts, each conceptual story should have multiple controlled paraphrases. A successful response geometry should be stable across paraphrase groups substantially beyond a lexical baseline.

### 4.5 MaleCNS branch

MaleCNS v1.0 covers the male fruit fly brain and ventral nerve cord and exposes connectivity, annotations, synapses, skeletons, and related resources. The initial MaleCNS implementation should treat the connectome as a structured recurrent substrate with a separately declared interface contract.

The renderer maps each story concept to an anatomically declared input or modulation proxy:

\\[
c
\\mapsto
\\rho_F(c).
\\]

Examples include:

- olfactory-like concepts mapped to olfactory sensory/projection pathways;
- gustatory sugar concepts mapped to sugar-sensitive gustatory pathways;
- aversive taste concepts mapped to appropriate gustatory/aversive pathways;
- action measurements decoded from descending or motor-related populations;
- motivational variables represented only through declared modulatory channels if the model implements them.

The proxy registry must record evidence, anatomical targets, sign, timing, magnitude convention, and confidence.

#### Important limitation: structure is not chemistry

A structural connectome does not by itself specify the complete dynamics of dopamine, octopamine, serotonin, internal metabolic state, receptor expression, or neuromodulatory gain. Experimental evidence shows, for example, that starvation-dependent dopamine release can enhance sugar sensitivity in primary gustatory neurons. That is precisely why a naive rule such as "increase dopamine concentration everywhere" is not a defensible MaleCNS realization.

The first experiment should therefore prioritize concepts whose proxies can be represented through identifiable sensory pathways. Neuromodulatory concepts should be added only when the model explicitly implements a plausible modulatory mechanism and should be labeled as engineered approximations.

### 4.6 Proxy registry

The experimental ground truth is a registry of conceptual interventions and native realizations.

A conceptual record can be represented in OKF without boilerplate, for example:

- concept: \`increase_sugar_concentration\`
- textual realization: change described sucrose concentration while preserving surrounding story
- MaleCNS realization: increase declared sugar-sensitive gustatory input according to a prespecified transfer function
- validity notes: sensory proxy; not a pharmacological simulation
- evidence: anatomical/physiological sources
- allowed magnitudes: fixed before confirmatory runs

The renderer may use this registry. Pontifex does **not** automatically receive the concept name.

This distinction is central:

\\[
\\text{registry known to experiment}
\\not\\Rightarrow
\\text{registry labels known to aligner}.
\\]

### 4.7 What Pontifex is allowed to see

We propose three information regimes.

**Regime 1 — boundary-only.** Pontifex receives the two ordered trajectories and knows which points are the story start and story end. Internal concept identities are hidden.

**Regime 2 — sparse anchors.** In addition to the boundaries, a small predefined fraction of internal event correspondences is revealed. Performance is measured on hidden events.

**Regime 3 — full concept oracle.** All event identities are supplied. This is an upper-bound diagnostic, not evidence of discovered alignment.

The strongest scientific result would come from Regime 1 or Regime 2.

---

## 5. Pontifex Torus alignment

### 5.1 Why time alone is not enough

If both branches are explicitly indexed by the same \\(\\tau\\), an algorithm could appear successful by returning \\(\\phi(\\tau)=\\tau\\) without reading either representation.

Therefore **time-only matching is a mandatory baseline**.

Pontifex must outperform a model that knows the ordered positions but has no access to response geometry.

The problem becomes meaningful when:

1. the two branches have different sampling densities;
2. local durations vary across story variants;
3. some events are omitted;
4. textual paraphrase changes representation without changing the concept;
5. only boundaries or sparse internal anchors are supplied;
6. held-out interventions must be located by relational response structure.

### 5.2 Response-field construction

For each story variant \\(H_m\\), each branch produces a baseline trajectory and a set of counterfactual trajectories.

For intervention \\(i\\), summarize the downstream response as:

\\[
r_S^{(m)}(i)
=
\\left[
d_S(\\tau_i),
d_S(\\tau_i+\\delta),
\\ldots,
d_S(1)
\\right],
\\]

optionally enriched by local derivatives, recovery time, peak response, area under the response curve, and relational distances to other interventions.

Across interventions this yields a response field over the story axis.

### 5.3 Cross-space matching without direct coordinates

Pontifex compares structures such as:

- rank order of intervention effects;
- pairwise response distances;
- neighborhood graphs;
- relative directionality where meaningful within each space;
- response persistence;
- composition effects of intervention pairs;
- boundary-relative position.

A mapping is successful if it predicts the target response neighborhood better than baselines while never requiring \\(Z_Q\\) and \\(Z_F\\) to share coordinates.

### 5.4 Composition

The most informative experiments should include paired interventions.

Let \\(a\\) and \\(b\\) be concepts such as hunger increase and sugar increase.

Compare:

\\[
r_S(a),
\\qquad
r_S(b),
\\qquad
r_S(a\\circ b).
\\]

The interaction residual is

\\[
\\epsilon_S(a,b)
=
r_S(a\\circ b)
-
\\mathcal{C}_S(r_S(a),r_S(b)),
\\]

where \\(\\mathcal{C}_S\\) is a within-space additive or learned null composition rule.

The question is not whether \\(\\epsilon_Q=\\epsilon_F\\) numerically. It is whether interaction relations are preserved:

\\[
\\operatorname{Rel}_Q(a,b)
\\approx
\\operatorname{Rel}_F(a,b).
\\]

This provides a richer test than matching individual events.

### 5.5 Held-out prediction

Partition intervention concepts or story variants into train and test sets.

Fit the Torus cartography using \\(C_{train}\\). Then, for a held-out concept \\(c_*\\), expose only its language-side response and ask the model to predict:

1. its narrative region in the MaleCNS trajectory;
2. its nearest MaleCNS response neighbors;
3. its relative effect magnitude rank;
4. where applicable, its interaction relations with known concepts.

Only after the prediction is fixed is \\(r_F(c_*)\\) revealed for scoring.

A successful result under this protocol is substantially harder to explain as label matching or sample memorization.

---

## 6. Evaluation

### 6.1 Primary metrics

No single score should define success. We propose a battery:

**Temporal retrieval.** Given a language-side held-out response, retrieve the correct MaleCNS narrative bin or event neighborhood.

**Relational geometry preservation.** Compare pairwise response-distance matrices using rank correlation and representational-similarity statistics.

**Neighborhood overlap.** Measure whether nearest-neighbor relations among interventions are preserved across spaces.

**Held-out response prediction.** Predict relational properties of hidden MaleCNS interventions from language-side responses.

**Warp complexity.** Penalize alignments requiring extreme local stretching or collapse.

**Cross-paraphrase stability.** Measure whether textual paraphrases map to the same MaleCNS neighborhood.

### 6.2 Boundary-condition experiment

Construct matched observations with equal or approximately equal information budgets:

1. complete story;
2. beginning removed;
3. ending removed;
4. both beginning and ending removed;
5. an equally sized interior interval removed;
6. random fragment of the same length.

The prediction is not merely "more context is better." It is more specific:

> For equal retained length, removing boundary information should damage cross-substrate alignment disproportionately if beginnings and endings constrain the trajectory.

This is falsified if boundary removal behaves no differently from arbitrary deletion after controlling for retained content.

### 6.3 History experiment

Compare:

- cumulative-prefix embeddings;
- isolated-sentence embeddings;
- fixed-width sliding textual context;
- full-story embedding repeated at every event as a degenerate nonlocal baseline.

If the Torus requires narrative history, cumulative or sufficiently long contextual representations should outperform isolated-event representations.

### 6.4 Temporal-order experiment

Use the same event multiset under:

- correct order;
- random permutation;
- local adjacent swaps;
- complete reversal;
- causally plausible alternative order where available.

If matching survives arbitrary permutations unchanged, the claimed role of narrative time is unsupported.

### 6.5 Missing-event experiment

Remove one event from only one branch and test whether monotone alignment can bridge the omission without globally corrupting the map.

This separates robust temporal transport from brittle index matching.

### 6.6 Cross-story generalization

Train on one story family and evaluate on another that shares some intervention concepts but changes the causal context.

For example, train on feeding episodes and test on food-odor-with-omission episodes.

This probes whether Pontifex learns a reusable causal response geometry rather than one fixed script.

---

## 7. Controls and ablations

The following controls are mandatory because each rules out a different trivial explanation.

### 7.1 Time-only baseline

Use only normalized narrative position \\(\\tau\\) and boundaries. No embeddings and no MaleCNS responses.

If Pontifex does not beat this baseline, response geometry added no evidence.

### 7.2 Concept-label oracle

Give the model the true concept IDs. This measures the ceiling obtainable from the registry and demonstrates how much of the task becomes trivial when labels are leaked.

It must not be reported as the primary result.

### 7.3 Concept-label permutation

Randomly permute concept identities between branches while preserving time.

This tests whether apparent alignment is carried only by chronology.

### 7.4 Temporal permutation

Randomize event order in one branch while retaining the same event set.

This directly tests the order hypothesis.

### 7.5 Noncumulative text representation

Embed each event description independently.

This tests whether accumulated textual history contributes to the match.

### 7.6 Degree-preserving MaleCNS rewire

Use a directed degree-preserving rewired graph with matched node count, edge count, edge-weight multiset where practical, interface capacity, initialization, and simulation budget.

MaleCNS-specific evidence requires outperforming this null, not merely outperforming a feed-forward model.

### 7.7 Random recurrent control

Use a matched recurrent network with similar spectral/dynamical capacity but no biological topology.

This tests whether generic recurrence is sufficient.

### 7.8 Direct translator baseline

Train a conventional cross-space mapper with access to paired examples.

Pontifex need not always outperform it in raw prediction accuracy. The comparison asks whether intervention-response geometry offers better data efficiency, robustness, interpretability, or held-out generalization without requiring direct coordinate alignment.

### 7.9 Proxy-fidelity ablation

Replace biologically motivated MaleCNS target populations with arbitrary populations matched in size and input magnitude.

If performance remains unchanged, the result does not support the claim that conceptually appropriate native realization matters.

### 7.10 Text wording controls

Use paraphrases, lexical substitutions, sentence-order-preserving rewrites, and stylistic changes.

The target correspondence should follow the intervention concept and history more strongly than incidental wording.

---

## 8. Falsifiable predictions

The proposal makes the following preregistrable predictions.

**P1 — complete-history advantage.** Full stories produce better held-out alignment than matched fragments.

**P2 — boundary advantage.** Under matched retained length, removal of the declared beginning or ending reduces alignment more than removal of comparable interior material.

**P3 — order dependence.** Temporal permutation or reversal produces a substantial drop in alignment.

**P4 — accumulated-history advantage.** Cumulative-prefix text embeddings outperform event-isolated embeddings.

**P5 — semantic-proxy advantage.** Anatomically/semantically justified MaleCNS proxies outperform size- and magnitude-matched arbitrary input locations.

**P6 — nontrivial geometry advantage.** Pontifex response-field alignment outperforms a time-only monotone matcher.

**P7 — held-out intervention generalization.** A Torus fitted without a subset of interventions predicts their MaleCNS response neighborhoods better than chance and permutation controls.

**P8 — paraphrase invariance.** The inferred correspondence is more stable across paraphrases of the same conceptual story than across different intervention concepts.

**P9 — composition consistency.** Interaction structure for paired interventions is more conserved across the two real systems than under shuffled concept pairings.

**P10 — topology specificity is conditional.** If MaleCNS topology contributes relevant inductive structure, the biological graph outperforms degree-preserving and random recurrent controls. Failure to do so is a legitimate negative result and should not be reinterpreted post hoc as success of the topology claim.

---

## 9. What would count as failure?

The framework should be considered unsupported in its current form if any of the following occurs reproducibly:

1. time-only matching performs as well as the full response-geometry method;
2. random temporal permutation does not materially reduce alignment;
3. concept-label permutation does not materially reduce alignment when labels are hidden from the aligner;
4. cumulative history provides no advantage over isolated event descriptions despite a claim that history is essential;
5. arbitrary MaleCNS input locations perform as well as biologically motivated proxies;
6. held-out interventions cannot be located above chance;
7. alignment requires a warp so flexible that every trajectory can be matched to every other trajectory;
8. results disappear under paraphrase;
9. the full effect is reproduced by matched random or rewired recurrent networks.

These outcomes would not imply that Pontifex is useless in every domain. They would falsify the stronger claim that ordered conceptual interventions reveal a meaningful shared causal geometry between the chosen language and MaleCNS realizations.

---

## 10. Relation to prior work

Several ingredients of the proposal are established and must not be presented as individually novel.

Common stimuli have long been used to align heterogeneous response spaces, including shared-response models in neuroscience. Relative representations use shared anchors to make otherwise incompatible latent spaces comparable. ModelDiff compares models through patterns of responses to common tests rather than by aligning internal weights. Counterfactual Alignment applies perturbations across models and studies their resulting output relationships. Intervention-based explanation methods treat pre/post-intervention representational change as an object of analysis. Manifold Steering explicitly studies intervention trajectories and intrinsic, including cyclic, representation geometry. Classical dynamic time warping provides monotone alignment of ordered sequences.

The present proposal therefore does **not** claim novelty for shared probes, relative geometry, sequence warping, response-based model comparison, or cyclic geometry as independent ideas.

The narrower research contribution is the proposed composition:

> define an ordered causal story with explicit boundaries; instantiate each intervention concept through substrate-native proxies rather than identical physical inputs; observe cumulative trajectories in a frozen language embedding model and a MaleCNS-derived recurrent system; hide some or all internal concept correspondences from the aligner; preserve only monotone narrative order; and test whether intervention-response geometry learned in one substrate predicts held-out response neighborhoods in the other beyond time-only, label-leakage, proxy-location, paraphrase, and rewired-connectome controls.

A claim-specific prior-art audit should be performed before any priority claim is made for this exact combination.

---

## 11. Practical first experiment

A minimal confirmatory implementation can remain small.

### 11.1 Data

Create approximately 200–500 controlled feeding-story variants from a prespecified generator.

Each variant has:

- one canonical event ledger;
- several textual paraphrases;
- one MaleCNS input schedule;
- zero or more prespecified counterfactual interventions;
- immutable train/validation/test assignment.

### 11.2 Text observer

Use frozen Qwen3-Embedding-0.6B initially.

Store:

- cumulative-prefix embeddings at each event;
- isolated-event embeddings for ablation;
- paraphrase ID;
- story ID;
- event timestamp only in the ground-truth ledger, with controlled exposure to the aligner.

### 11.3 MaleCNS observer

Use the full available MaleCNS graph when computationally feasible, or a preregistered reduced graph only as a pilot.

Store:

- declared input populations;
- state snapshots at fixed physical simulation intervals;
- event-triggered response summaries;
- all engineered dynamics parameters;
- random seed;
- connectome version and file hashes.

### 11.4 Alignment ladder

Run, in order:

1. time-only baseline;
2. boundary-only Pontifex;
3. sparse-anchor Pontifex;
4. full-concept oracle;
5. temporal permutations;
6. concept permutations;
7. paraphrase test;
8. held-out intervention prediction;
9. degree-preserving rewire;
10. random recurrent control.

The held-out test set should remain untouched until the pipeline and metrics are frozen.

---

## 12. Extensions

### 12.1 Closed-loop histories

After clamped playback, allow MaleCNS-derived actions to change an environment. The story is then partly endogenous.

The canonical timeline becomes an observed event ledger rather than a fully scheduled script. Pontifex can ask whether language descriptions of the resulting episode recover the same intervention-response organization.

### 12.2 Partial orders and branching stories

Real narratives contain concurrent and branching events. Replace total order by a causal DAG and define multiple monotone paths through it.

This may eventually connect the Torus more naturally to families of alternative futures rather than a single line.

### 12.3 Multiple embedding observers

Repeat the text branch with several independent embedding models. A genuine story-level geometry should not depend entirely on Qwen coordinates.

### 12.4 Multiple biological observers

The same story registry can be used with rewired MaleCNS, female-fly connectomes where comparable data exist, subcircuits, or future dynamical models incorporating richer physiology.

### 12.5 Learned proxy renderers

Only after fixed proxies are understood should trainable renderers be considered. They require strict capacity controls because a high-capacity renderer can manufacture the desired alignment.

---

## 13. Discussion

The central methodological move is modest but consequential: two systems need not receive the same object to participate in the same intervention. They need native manipulations that instantiate the same prespecified causal distinction.

This permits comparison across substrates while preserving experimental discipline. A text model can receive language. A fly connectome can receive sensory-like or modulatory-like input. The common experimental object is the concept and its location in a history.

The second move is to treat the story itself as part of the intervention definition. An intervention has consequences relative to a state produced by earlier events. This gives the Torus a natural ordered coordinate and turns "context" from a vague linguistic property into an experimentally controlled history.

The third move is to make missing boundaries measurable. A story beginning in the middle is not forbidden. It is a partial observation with weaker constraints. The theory therefore predicts graceful degradation rather than categorical failure.

Finally, the proposal makes it possible to distinguish a compelling demonstration from a circular one. If both branches are generated from the same concept ledger and Pontifex is then handed the ledger, there is little to discover. The important test hides internal correspondences, reveals only the allowed boundary or sparse anchors, and asks whether response geometry recovers what the experimenter knows but the aligner does not.

---

## 14. Conclusion

We propose **Narrative Proxy Interventions** as an experimental bridge between language embeddings and the Drosophila MaleCNS in the Pontifex programme.

The shared unit is not a token, neuron, vector, or physical stimulus. It is a causal intervention concept embedded in an ordered story. Each substrate receives a native proxy realization. The text branch accumulates a narrative through contextual prefixes; the MaleCNS branch accumulates a recurrent neural history. Pontifex compares the structures induced by those interventions while preserving temporal order through a monotone narrative coordinate.

The proposal is useful only if it survives strong controls. Time alone must not explain the match. Shared labels must not leak the answer. Wording must not dominate semantic intervention identity. Arbitrary neural input locations must not substitute for declared biological proxies. Generic recurrence must be separated from MaleCNS topology. Held-out interventions must be predicted rather than retrofitted.

If those tests succeed, the result would support a precise operational statement: two very different representational substrates can share detectable structure not because their coordinates are equal, but because **the ordered consequences of the same causal distinctions stand in corresponding relations**.

That is the object the Pontifex Torus should attempt to recover.

---

## References

Ahuja, K., Mahajan, D., Wang, Y., & Bengio, Y. (2023). Interventional causal representation learning. *Proceedings of the 40th International Conference on Machine Learning (PMLR 202)*.

Baldo, F. S. (2026a). *Pontifex: Byte-Level Occlusion with Multi-Space Convergence for Tokenizer-Free, Cross-Modal Interpretability*. Research manuscript, \`pontifex.md\`.

Baldo, F. S. (2026b). *Interventional Latent Graphs: Binary Distinctions as Minimal Operational Edges Between Representation Spaces*. Research manuscript, \`pontifex/interventional-latent-graph.md\`.

Berg, S., Beckett, I. R., Costa, M., et al. (2026). Sexual dimorphism in the complete *Drosophila* male central nervous system connectome. Official publication 3 September 2026; MaleCNS v1.0 released 8 June 2026. Janelia FlyEM Male CNS Connectome Project.

Chen, P.-H., Chen, J., Yeshurun, Y., Hasson, U., Haxby, J., & Ramadge, P. J. (2015). A reduced-dimension fMRI shared response model. *Advances in Neural Information Processing Systems*.

Cohen, J. P., Blankemeier, L., & Chaudhari, A. (2023). Identifying spurious correlations using counterfactual alignment. arXiv:2312.02186.

Gat, I., Lorberbom, G., Schwartz, I., & Hazan, T. (2022). Latent space explanation by intervention. *Proceedings of the AAAI Conference on Artificial Intelligence*.

Inagaki, H. K., Ben-Tabou de-Leon, S., Wong, A. M., Jagadish, S., Ishimoto, H., Barnea, G., Kitamoto, T., Axel, R., & Anderson, D. J. (2012). Visualizing neuromodulation in vivo: TANGO-mapping of dopamine signaling reveals appetite control of sugar sensing. *Cell, 148*(3), 583–595. https://doi.org/10.1016/j.cell.2011.12.022

Kriegeskorte, N., Mur, M., & Bandettini, P. A. (2008). Representational similarity analysis — connecting the branches of systems neuroscience. *Frontiers in Systems Neuroscience, 2*, 4.

Li, Y., Zhang, Z., Liu, B., Yang, Z., & Liu, Y. (2021). ModelDiff: Testing-based DNN similarity comparison for model reuse detection. *ISSTA 2021*. arXiv:2106.08890.

Moschella, L., Maiorca, V., Fumero, M., Norelli, A., Locatello, F., & Rodolà, E. (2022). Relative representations enable zero-shot latent space communication. arXiv:2209.15430.

Sakoe, H., & Chiba, S. (1978). Dynamic programming algorithm optimization for spoken word recognition. *IEEE Transactions on Acoustics, Speech, and Signal Processing, 26*(1), 43–49.

Wurgaft, D., et al. (2026). Manifold Steering Reveals the Shared Geometry of Neural Network Representation and Behavior. arXiv:2605.05115.

Zhang, Y., Li, M., Long, D., Zhang, X., Lin, H., Yang, B., Xie, P., Yang, A., Liu, D., Lin, J., Huang, F., & Zhou, J. (2025). Qwen3 Embedding: Advancing Text Embedding and Reranking Through Foundation Models. arXiv:2506.05176.
