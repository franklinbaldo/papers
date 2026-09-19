---
type: "Scientific Position Paper"
title: "Interventional Latent Graphs: Binary Distinctions as Minimal Operational Edges Between Representation Spaces"
description: "A Pontifex extension in which latent spaces are vertices, atomic shared interventions are edges, and binary contrasts provide the minimal non-trivial operational intervention without being claimed as a minimum physical quantum."
tags: [pontifex, interventional-graph, latent-space, information-theory, causal-representation, lean4]
timestamp: 2026-09-19T03:10:00Z
authors:
  - ref: /about/authors/franklin-silveira-baldo.md
    byline: "Franklin Silveira Baldo"
    affiliations:
      - "Independent Researcher"
    corresponding: true
publication:
  status: ready
  targets: [zenodo]
  zenodo:
    publication_type: preprint
    access_right: open
    license: cc-by-nc-4.0
    version: "0.1"
---

# Interventional Latent Graphs: Binary Distinctions as Minimal Operational Edges Between Representation Spaces

**Franklin Silveira Baldo**  
Independent Researcher  
franklinbaldo@gmail.com

> **Scientific position paper.** This paper proposes a mathematical object and a falsifiable research programme. It reports no new empirical measurements. In particular, the claim that a binary contrast is a minimal operational intervention is an information-theoretic statement about discrete distinguishability, not a claim that one bit is a smallest physical object, a smallest quantum of energy, or a lower bound on all possible physical interventions.

## Abstract

Pontifex began as a method for comparing how different representation spaces respond to matched perturbations. This paper isolates a more primitive structure: before asking whether two latent spaces are equivalent, aligned, or semantically similar, one may ask only whether the same intervention can be posed to both. We define an **Interventional Latent Graph** (ILG) as a multigraph whose vertices are latent spaces and whose edges are atomic shared interventions. The definition is deliberately minimal: **one intervention is one edge**. An edge does not assert similarity, agreement, causal equivalence, metric alignment, or shared ontology. It asserts only that a single controlled contrast is realizable at both endpoints and therefore creates an opportunity for comparison.

For the discrete operational layer, we propose a binary contrast as the minimal non-trivial intervention alphabet. A one-element alphabet cannot distinguish alternatives; a two-element alphabet can. In base two this is one bit. This does not identify a bit with a photon, a quantum, or an energetic lower bound. A photon may physically realize a binary intervention, as may a voltage transition, a neural spike, a prompt edit, or a policy toggle. The bit belongs to the intervention's **logical resolution**, not necessarily to its physical substrate.

The resulting object is naturally a multigraph because distinct interventions may connect the same pair of latent spaces. Response functions live in a separate layer above the graph, allowing two spaces to be adjacent even when their responses disagree maximally. Paths become finite sequences of interventions; cycles become experimentally meaningful closure tests; and global topological hypotheses, including toroidal structure, become downstream hypotheses rather than assumptions built into the graph. We provide a Lean 4 companion formalization that machine-checks the minimality of binary contrast, the identity between intervention tokens and graph edges, parallel-edge construction, path composition and length additivity, and the fact that edge existence does not force response agreement.

## 1. Motivation

Representation-learning systems routinely produce internal spaces whose coordinates are not directly comparable. A language model, a vision model, a biological nervous system, a physical sensor network, and a human conceptual scheme may all encode related structure while assigning that structure to different coordinates, dimensions, geometries, or substrates.

A common response is to align representations. One learns a map from one space into another, assumes a joint embedding, or compares observations after projecting both spaces into a shared coordinate system. Pontifex takes a different route: intervene on both systems and compare what changes.

That shift suggests a prior question.

Before asking whether two spaces respond similarly to an intervention, what structure exists merely because the intervention can be posed to both?

The answer proposed here is intentionally austere:

\[
\boxed{\text{one shared intervention} = \text{one edge}}
\]

The graph is therefore not a graph of causal variables inside a system. Its vertices are entire representational spaces. Nor is an edge a claim that two spaces are equivalent. It is simply the existence of a common experimental question.

This minimality is useful for three reasons.

First, it prevents semantic conclusions from being smuggled into the ontology. The graph can be built before Pontifex succeeds or fails on any edge.

Second, it lets multiple interventions between the same spaces remain distinct. Two spaces may share thousands of possible experiments, and that multiplicity is itself observable structure.

Third, it makes global geometry an empirical question. Cycles, bottlenecks, communities, coverings, and possible manifold-like or toroidal realizations are properties to be inferred from the accumulated intervention structure, not assumed at definition time.

## 2. Relation to existing ideas

### 2.1 Shannon: one bit as the smallest non-trivial discrete contrast

Shannon's theory measures information through distinguishable alternatives. For an alphabet with \(N\) equiprobable alternatives, the information associated with selecting one alternative is \(\log_2 N\) bits. The smallest non-trivial finite alphabet has \(N=2\), yielding one bit.

The use of the bit here is therefore operational. If an intervention has only one possible setting, there is no contrast and hence no experiment. With two distinguishable settings, a counterfactual comparison becomes possible.

This is weaker than claiming that all interventions are intrinsically binary. Multi-valued and continuous interventions are allowed, but they can be studied at a chosen binary resolution by selecting two alternatives. Whether that decomposition is lossless is a separate question.

### 2.2 Landauer: information is physically instantiated, but the bit is not a universal physical quantum

Landauer connected logical irreversibility to thermodynamic cost. That result is essential background because it blocks a naive separation between information and physical realization. Nevertheless, Landauer's principle does **not** establish that one bit is the smallest possible physical intervention, nor that every binary operation dissipates the same energy, nor that intervention energy is quantized in bits.

The present framework therefore keeps two levels separate:

1. **logical intervention resolution** — the number of distinguishable alternatives;
2. **physical implementation** — the substrate and energetic dynamics that realize those alternatives.

A single photon can realize a binary distinction, for example presence/absence or one of two controlled polarizations, but so can many other physical systems. The graph definition is substrate-independent.

### 2.3 Pearl and interventionist causality

Modern causal inference distinguishes observation from intervention. Pearl's \(do(\cdot)\) formalism gives interventions a precise mathematical role inside causal models. The ILG borrows the interventionist stance but changes the level of description.

Pearlian graphs ordinarily place variables as vertices and causal dependencies as edges. In an ILG:

- a vertex denotes a representation space;
- an edge denotes a shared intervention token;
- causal or semantic agreement is evaluated after the edge exists.

Thus the ILG should not be read as a replacement for a structural causal model. It is an experimental incidence structure over representational systems.

### 2.4 Causal representation learning

Causal representation learning studies how high-level causal variables may be recovered from low-level observations and how interventions can make representations identifiable. Work on latent interventions, atomic interventions, and binary interactions is particularly close in spirit.

BISCUIT, for example, shows that binary interaction variables can support identification of causal variables in interactive environments. Other work uses interventional environments to identify latent causal structures or representation classes.

The ILG differs in its primary object. It does not initially seek the causal variables *within* one latent system. It constructs a graph *whose vertices are the latent systems themselves*, with shared interventions as the primitive edges. The responses observed at the endpoints can later support structural-identification claims.

### 2.5 Cross-model intervention correspondence is established prior art

The generic idea that interventions must be related across models or abstraction levels is not new. Rubenstein et al. formalize exact transformations between structural causal models and make intervention specification part of cross-level consistency. Beckers and Halpern likewise treat allowed interventions and their mappings as part of causal abstraction, while Otsuka and Saigo study equivalence between causal models through translations that preserve intervention calculus. Geiger et al. broaden this lineage for mechanistic interpretability by formalizing causal abstraction with a richer intervention algebra.

This literature imposes a direct constraint on the ILG ontology: an intervention token cannot be admitted merely because two endpoint-specific manipulations share a name. The scientific contract must say what factor or mechanism is manipulated, how each endpoint implements that manipulation, and why those implementations count as the same operational contrast independently of the response agreement later measured by Pontifex. If that identity can only be established after learning the same alignment the graph is intended to test, the slogan that “the graph exists before the map” becomes circular and must be narrowed.

### 2.6 Heterogeneous domains, identifiability, and closure controls

Transportability theory already shows that corresponding interventions across heterogeneous domains need not induce identical effects. This supports the ILG separation between edge admission and response agreement, but it also reinforces the burden of specifying intervention identity independently of the effect being compared.

Binary contrast is similarly only a minimal *question*, not a generic identification guarantee. Modern interventional causal-representation results show that identifiability depends on intervention type, transformation class, causal assumptions, and the number of interventional environments. The present paper therefore makes no claim that one binary contrast suffices to reconstruct a latent system.

Finally, learned transport and closure are potentially non-discriminating when the alignment family is too expressive. Sutter et al. show that sufficiently flexible nonlinear alignments can make arbitrary model/algorithm pairs appear causally aligned, including a randomly initialized language-model control in their setting. Any future ILG evidence from learned transports or cycle closure must therefore constrain or complexity-penalize the transport family, evaluate held-out interventions, and compare against capacity-matched shuffled or random endpoint/null-cycle controls. Closure that also occurs in those nulls is not evidence for a Torus or manifold.

### 2.7 Contribution boundary after the claim-specific audit

A dated claim-specific audit in this repository finds pre-cutoff antecedents for the component ideas of cross-model intervention correspondence, intervention mappings, multiple interventional contexts/entities, atomic interventions, binary contrast as the smallest non-trivial finite alphabet, heterogeneous response to corresponding interventions, and generic multigraph/path/cycle/closure machinery. None of those components is claimed here as an isolated novelty.

The narrower conjunction for which that audit did **not** locate a material pre-cutoff antecedent is the following: whole representation systems are vertices; each admitted shared intervention token is definitionally one multigraph edge; primitive edge existence is deliberately independent of response agreement; response comparison is layered above the edge; paths are intervention histories; learned transports and closure are downstream measurements; and manifold/Torus structure is an explicitly falsifiable downstream hypothesis rather than part of the graph definition.

That finding is a bounded negative-search result, not a claim of priority or exhaustive novelty. The empirical programme remains capable of falsifying the central premise if shared-intervention identity cannot be operationalized independently of the alignment being measured.

## 3. Definition of the Interventional Latent Graph

Let \(\mathcal{L}\) be a collection of latent spaces and \(\mathcal{I}\) a collection of atomic intervention tokens.

Define the Interventional Latent Graph

\[
G_I = (\mathcal{L}, \mathcal{I}, \partial)
\]

with endpoint map

\[
\partial : \mathcal{I} \rightarrow \mathcal{L}\times\mathcal{L}.
\]

The crucial convention is:

\[
\boxed{E(G_I) \equiv \mathcal{I}}
\]

That is, the edge set is not merely labeled by interventions. **The interventions are the edges.**

For an intervention \(i\in\mathcal{I}\),

\[
\partial(i) = (L_a,L_b)
\]

means that \(i\) is a shared intervention between \(L_a\) and \(L_b\).

Nothing else follows from the edge definition.

In particular,

\[
i : L_a \leftrightarrow L_b
\]

does not imply

\[
L_a \simeq L_b,
\]

does not imply that their responses are equal, and does not imply the existence of an invertible map between their coordinates.

### 3.1 Multigraph structure

Distinct interventions may have identical endpoints:

\[
i_1 \neq i_2,\qquad
\partial(i_1)=\partial(i_2)=(L_a,L_b).
\]

Therefore the natural object is a multigraph.

This is desirable. If two spaces permit a large repertoire of matched interventions, collapsing all of them into a single weighted edge would destroy experimentally meaningful identity. Counts, families, and compositions of interventions can be derived later without weakening the primitive ontology.

### 3.2 Direction

The base graph can be treated as undirected when the intervention is merely shared. If an intervention has an intrinsically directional role, direction can be represented in a derived structure.

The minimal theory therefore stores an ordered endpoint pair for implementation convenience but defines connectivity symmetrically:

\[
\operatorname{Connects}(i,L_a,L_b)
\]

iff

\[
\partial(i)=(L_a,L_b)
\quad\text{or}\quad
\partial(i)=(L_b,L_a).
\]

No causal direction is inferred from endpoint order alone.

## 4. The atomic intervention as a binary contrast

Let the arm set be

\[
\mathbb{B}=\{0,1\}.
\]

An elementary discrete intervention exposes two alternatives:

\[
i(0),\quad i(1).
\]

The minimality claim is modest but exact.

A singleton alphabet cannot contain two distinct alternatives. Therefore it cannot define a non-trivial contrast. A two-element alphabet can. Consequently, among finite discrete alphabets, the first size that supports an intervention contrast is two.

With base-two coding,

\[
\log_2 2 = 1\text{ bit}.
\]

This motivates the phrase **one-bit intervention**.

It should be interpreted as:

> one controlled binary distinction at the chosen operational resolution.

It should not be interpreted as:

> the physically smallest perturbation possible in nature.

Those statements are different, and only the first is asserted here.

### 4.1 Binary refinement of larger interventions

Suppose an intervention parameter admits values in a set \(A\) with \(|A|>2\). For any two distinguishable values \(a,b\in A\), one may define a binary contrast

\[
i_{a,b} = \{a,b\}.
\]

Continuous controls can similarly be probed through finite binary contrasts such as \(x\) versus \(x+\delta\).

Whether all relevant structure can be reconstructed from such contrasts is an empirical and mathematical question. The ILG requires only that a binary comparison can be posed, not that binary decomposition is universally sufficient.

## 5. Response semantics are a separate layer

After the graph exists, each endpoint may return an observation.

Let

\[
R : \mathcal{L}\times\mathcal{I}\times\mathbb{B}\rightarrow\mathcal{O}
\]

be a response function into an observation space \(\mathcal{O}\).

For an edge \(i\) connecting \(L_a\) and \(L_b\), the raw response signature is

\[
S_i(L)
=
\bigl(
R(L,i,0),
R(L,i,1)
\bigr).
\]

Pontifex then acts on the pair

\[
\bigl(S_i(L_a),S_i(L_b)\bigr).
\]

Different applications may compare these signatures by equality, a learned map, a metric, an invariant statistic, causal effect structure, or another criterion.

The separation is fundamental:

\[
\boxed{
\text{edge existence}
\not\Rightarrow
\text{response agreement}
}
\]

A valid shared intervention can produce opposite responses at its endpoints. The Lean companion includes an explicit model witnessing this possibility.

This avoids a circular definition. If adjacency required Pontifex similarity, then the graph could only be built after the phenomenon it is meant to measure had already been established.

## 6. Paths, histories, and intervention length

A walk through the graph is a sequence of interventions

\[
h=(i_1,i_2,\ldots,i_k)
\]

whose consecutive edges share endpoints in the usual graph-theoretic sense.

Its intervention length is

\[
\ell_I(h)=k.
\]

This quantity is always meaningful.

It is tempting to call \(\ell_I(h)\) the number of bits in the history, but that stronger interpretation requires additional assumptions. Edge count equals a number of binary intervention *steps*; it equals Shannon information only when the relevant coding distribution and dependence assumptions justify that reading.

The conservative terminology is therefore **intervention length**.

For composable histories \(h_1\) and \(h_2\),

\[
\ell_I(h_1\cdot h_2)
=
\ell_I(h_1)+\ell_I(h_2).
\]

This is machine-checked in the companion Lean development.

### 6.1 Reverberation as a downstream quantity

The graph permits a more rigorous version of the idea that a history can reverberate beyond its original representational region.

Let a history induce an intervention-response signature \(\sigma_h\). One may define a recoverability criterion

\[
\operatorname{Rec}(\sigma_h,L)\ge \tau
\]

and ask how far from the origin that signature remains identifiable.

Possible derived quantities include:

- graph radius of recoverability;
- number of distinct latent spaces reached;
- shortest intervention path carrying a recoverable signature;
- attenuation or deformation of the signature along paths;
- invariance under alternative paths to the same destination.

These are proposed measurements, not part of the primitive graph definition.

## 7. Cycles and closure tests

If

\[
L_A
\xleftrightarrow{i_1}
L_B
\xleftrightarrow{i_2}
L_C
\xleftrightarrow{i_3}
L_A,
\]

the graph contains a closed walk.

A closed walk is not yet evidence of a torus. Even very small ordinary graphs contain cycles.

The scientific value of cycles emerges after response transformations are attached to the edges. If each edge supports a learned transport

\[
P_i,
\]

then a cycle permits a closure test such as

\[
P_{i_3}\circ P_{i_2}\circ P_{i_1}
\approx I.
\]

Failure to close can itself be informative, for example as path dependence or a holonomy-like residual.

The important methodological rule is:

\[
\boxed{\text{cycle} \neq \text{torus}}
\]

A toroidal or manifold interpretation requires additional global evidence.

## 8. The Torus as a downstream hypothesis

The term "Torus" has been useful as an intuition for a globally connected space of latent representations. The ILG turns that intuition into something testable.

The construction procedure is:

1. collect latent spaces;
2. enumerate or discover shared interventions;
3. instantiate one edge per intervention;
4. measure endpoint responses;
5. apply Pontifex-style structural comparison;
6. study global graph properties;
7. only then test candidate continuous or topological realizations.

Evidence relevant to a toroidal hypothesis might include stable independent cycle families, consistent local charts, path-independent neighborhoods up to measurable holonomy, or successful low-distortion embeddings into a toroidal manifold compared with alternatives.

Conversely, tree-like structure, unstable cycles, strong bottlenecks, or better fit by another topology would count against the hypothesis.

Thus the ILG does not encode the Torus. It provides a substrate on which the Torus can fail.

## 9. Experimental programme

### 9.1 Synthetic latent spaces

Construct several latent systems whose relationship is known:

- isomorphic spaces under coordinate changes;
- partially shared factor spaces;
- spaces with one common causal mechanism and unrelated nuisance dimensions;
- deliberately non-equivalent controls.

Define a library of atomic binary interventions and build the ILG without using the ground-truth correspondence.

Questions:

- Does graph connectivity recover where comparison is possible?
- Do Pontifex response signatures distinguish isomorphic from merely adjacent spaces?
- Do composed edge transports close on cycles when they should?

### 9.2 Heterogeneous machine representations

Candidate vertices include:

- hidden layers from different language models;
- image encoders;
- audio encoders;
- multimodal encoders;
- symbolic or program-state representations.

Candidate shared interventions include controlled edits whose semantics can be instantiated in each system.

The key discipline is that an intervention is admitted as an edge because it is realizable at both endpoints, not because the observed responses already agree.

### 9.3 Physical and biological systems

The same abstraction can in principle be applied to physical or biological systems, provided that "latent space" and "shared intervention" are operationally specified.

At this level the binary intervention may be physically instantiated by a photon, a voltage level, a receptor stimulus, or another controlled perturbation. No substrate is privileged by the formalism.

Claims about physical minimality require separate physics and are outside the present result.

## 10. Falsifiers and failure modes

The proposal should be weakened or rejected if any of the following occur.

### 10.1 Shared-intervention identity cannot be defined independently of semantic agreement

If in realistic systems researchers cannot decide that an intervention is "the same intervention" across spaces without already assuming the alignment Pontifex is supposed to discover, then the edge ontology is circular.

This is the most important conceptual risk.

### 10.2 Binary refinement destroys essential structure

If relevant interventions are intrinsically multi-valued or quantum in a way that cannot be faithfully studied through controlled binary contrasts, the one-bit primitive is an inadequate operational basis.

The ILG itself can survive with a richer intervention alphabet, but the binary-minimality programme would be limited.

### 10.3 Graph structure is too coarse

A graph may discard higher-order relations in which one intervention is simultaneously meaningful across many spaces. In such cases a hypergraph, simplicial complex, or category-like structure may ultimately be more faithful.

The multigraph should therefore be treated as the minimal starting object, not a guaranteed final ontology.

### 10.4 Path length is mistaken for information

Counting atomic interventions is not automatically an information measure. Dependencies, redundancy, unequal priors, and coding choices matter.

Any claim that \(k\) edges equal \(k\) bits of Shannon information must state the additional assumptions that make the equality valid.

### 10.5 Topological over-interpretation

Cycles and graph embeddings can be visually suggestive while carrying little topological meaning. The Torus hypothesis must be compared against alternative global models and explicit nulls.

## 11. Formalization strategy

The companion Lean 4 development deliberately formalizes only the minimal mathematical spine.

It defines:

- a two-arm intervention alphabet;
- non-trivial contrast;
- impossibility of non-trivial contrast for a subsingleton alphabet;
- an interventional graph whose edge type is definitionally the intervention type;
- symmetric connectivity;
- walks and intervention length;
- walk composition and additive length;
- a parallel-edge example;
- an explicit valid edge whose endpoints disagree in their responses;
- a three-edge closed walk.

It deliberately does **not** formalize:

- Shannon entropy;
- thermodynamics or Landauer bounds;
- physical photons;
- causal do-calculus;
- neural embeddings;
- metric alignment;
- manifold reconstruction;
- toroidal topology.

Those are either literature-level dependencies, empirical layers, or future extensions. Keeping them outside the trusted core prevents a position paper from presenting philosophical interpretation as a machine-checked theorem.

## 12. Consequences for Pontifex

The ILG suggests a cleaner decomposition of the Pontifex programme:

\[
\text{shared intervention}
\rightarrow
\text{edge}
\rightarrow
\text{endpoint responses}
\rightarrow
\text{Pontifex comparison}
\rightarrow
\text{derived structure}.
\]

This corrects a common conceptual compression in which an edge was implicitly made to carry confidence, alignment error, response similarity, and structural equivalence at once.

Those are not primitive properties of an edge. They are measurements over an edge.

The distinction matters because negative results become first-class data. If a shared intervention produces incompatible responses, that edge remains in the graph and records exactly where a structural equivalence failed.

The graph therefore contains both bridges and disagreements.

## 13. Conclusion

The Interventional Latent Graph is defined by a deliberately small commitment:

\[
\boxed{\text{one intervention} = \text{one edge}}
\]

Latent spaces are vertices. Distinct shared interventions remain distinct parallel edges. An edge creates an opportunity to compare responses but asserts no agreement.

At the discrete operational level, the minimal non-trivial intervention is a binary contrast: a singleton cannot distinguish alternatives, while a two-element alphabet can. In base two that contrast carries one bit of logical resolution. This is not a claim that the universe has a one-bit minimum physical perturbation.

The resulting separation of graph structure from response semantics gives Pontifex a cleaner foundation. Paths can represent intervention histories; cycles can support closure tests; and hypotheses about the global geometry of representation space, including the Torus, become falsifiable downstream constructions rather than assumptions.

The most important next empirical question is also the simplest:

> Across genuinely different representation systems, can we define shared atomic interventions independently of the alignment we hope to discover?

If the answer is yes, the graph exists before the map.

## References

- Shannon, C. E. (1948). *A Mathematical Theory of Communication*. Bell System Technical Journal, 27, 379-423 and 623-656.
- Landauer, R. (1961). *Irreversibility and Heat Generation in the Computing Process*. IBM Journal of Research and Development, 5(3), 183-191. https://doi.org/10.1147/rd.53.0183
- Pearl, J. (2009). *Causality: Models, Reasoning, and Inference*, 2nd ed. Cambridge University Press.
- Rubenstein, P. K., Weichwald, S., Bongers, S., Mooij, J. M., Janzing, D., Grosse-Wentrup, M., & Schölkopf, B. (2017). *Causal Consistency of Structural Equation Models*. UAI 2017. https://arxiv.org/abs/1707.00819
- Beckers, S., & Halpern, J. Y. (2019). *Abstracting Causal Models*. Proceedings of the AAAI Conference on Artificial Intelligence, 33(01), 2678-2685. https://doi.org/10.1609/aaai.v33i01.33012678
- Bareinboim, E., & Pearl, J. (2013). *Meta-Transportability of Causal Effects: A Formal Approach*. Proceedings of AISTATS 2013, PMLR 31, 135-143. https://proceedings.mlr.press/v31/bareinboim13a.html
- Otsuka, J., & Saigo, H. (2022). *On the Equivalence of Causal Models: A Category-Theoretic Approach*. CLeaR 2022, PMLR 177. https://arxiv.org/abs/2201.06981
- Geiger, A., et al. (2023). *Causal Abstraction: A Theoretical Foundation for Mechanistic Interpretability*. https://arxiv.org/abs/2301.04709
- Schölkopf, B., Locatello, F., Bauer, S., Ke, N. R., Kalchbrenner, N., Goyal, A., & Bengio, Y. (2021). *Towards Causal Representation Learning*. Proceedings of the IEEE, 109(5), 612-634. https://arxiv.org/abs/2102.11107
- Kocaoglu, M., Jaber, A., Shanmugam, K., & Bareinboim, E. (2019). *Characterization and Learning of Causal Graphs with Latent Variables from Soft Interventions*. NeurIPS 32.
- Lippe, P., Magliacane, S., Löwe, S., Asano, Y. M., Cohen, T., & Gavves, E. (2023). *BISCUIT: Causal Representation Learning from Binary Interactions*. UAI 2023.
- Varıcı, B., Acartürk, E., Shanmugam, K., Tajer, A., & Tchetgen Tchetgen, E. J. (2025). *Score-based Causal Representation Learning: Linear and General Transformations*. Journal of Machine Learning Research, 26(112), 1-90. https://arxiv.org/abs/2402.00849
- Sutter, D., Minder, J., Hofmann, T., & Pimentel, T. (2025). *The Non-Linear Representation Dilemma: Is Causal Abstraction Enough for Mechanistic Interpretability?* https://arxiv.org/abs/2507.08802

## Companion formalization

The machine-checked core is in:

`pontifex/formalizations/interventional-latent-graph/InterventionalLatentGraph.lean`

with scope and trusted-boundary notes in:

`pontifex/formalizations/interventional-latent-graph/README.md`
