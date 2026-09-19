---
type: "Scientific Position Paper"
title: "Narrative Proxy Interventions: Aligning Language Embeddings and the Drosophila MaleCNS Through Shared Causal Stories in the Pontifex Torus"
description: "A falsifiable protocol for testing predictive structural correspondence between a language-embedding trajectory and a Drosophila MaleCNS trajectory through substrate-native realizations of the same ordered causal story."
tags: [pontifex, torus, malecns, drosophila, embeddings, causal-interventions, narrative-time, representation-alignment, connectome]
timestamp: 2026-09-19T09:41:00-04:00
authors:
  - ref: /authors/franklin-silveira-baldo.md
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

# Narrative Proxy Interventions

## Aligning Language Embeddings and the Drosophila MaleCNS Through Shared Causal Stories in the Pontifex Torus

**Franklin Silveira Baldo**  
Independent Researcher  
franklinbaldo@gmail.com

> **Scientific position paper / protocol.** This manuscript proposes a formal object, an experimental protocol, controls, and falsifiable predictions. It reports no new empirical measurements. The proposed text↔MaleCNS correspondences are experimental proxies, not claims that a structural connectome reproduces complete *Drosophila* physiology. A positive alignment would establish, at most, predictive structural correspondence under the declared interventions unless separate evidence supports a stronger mechanistic claim.

## Abstract

Cross-model representation alignment is often posed as coordinate matching, paired-sample translation, or construction of a common latent space. Those formulations become awkward when the two systems differ in substrate and modality, as with a text embedding model and a recurrent computation constrained by the complete male *Drosophila* central nervous system connectome. We propose a different experimental primitive: an **ordered causal story** whose events are expressed through **substrate-native proxy interventions**.

A canonical story is parameterized by narrative time τ∈[0,1] with explicit initial and terminal conditions. Each intervention concept is realized independently in a text branch and a MaleCNS branch. The text branch changes a natural-language account and measures the response in a frozen embedding model. The connectome branch changes an anatomically declared sensory or, where defensible, modulatory input and measures the resulting recurrent trajectory. The two branches need not share coordinates or physical stimuli. They must instead preserve a prespecified experimental distinction and causal order.

Pontifex then compares **within-substrate response geometries** rather than directly subtracting latent vectors across systems. A monotone temporal transport may absorb different local rates while preserving order. Internal concept identities can be hidden from the aligner, and the strongest test holds out interventions or story families and asks whether language-side responses predict MaleCNS response neighborhoods beyond conventional relational/temporal alignment baselines and matched null systems.

The generic ingredients are not new. Canonical/Generalized Time Warping, Gromov Dynamic Time Warping, Gromov–Wasserstein structural alignment, causal-abstraction intervention mappings, and narrative-boundary effects all predate this proposal. A bounded pre-cutoff audit did not locate the full conjunction proposed here; that negative search is not a claim of firstness. The candidate contribution is the specific experimental composition: ordered causal stories, substrate-native interventions, hidden correspondence, held-out response-field prediction, explicit proxy-validity controls, alignment-capacity controls, and MaleCNS topology nulls.

The protocol is deliberately falsifiable. If time-only, CTW/GTW, GDTW/GWOT, direct translators, arbitrary proxy locations, shuffled responses, untrained observers, or matched rewired/random recurrent systems explain the effect, the interpretation must narrow accordingly. Even a successful result would support predictive structural correspondence, not by itself shared mechanism, ontology, or computation.

**Keywords:** Pontifex, MaleCNS, Drosophila connectome, narrative time, causal interventions, proxy intervention, representation alignment, Gromov alignment, embeddings, monotone alignment, response geometry

---

## 1. Scientific question

Suppose two systems are probed about the same causal distinction but do not accept the same physical input. A text encoder accepts language. A connectome-derived dynamical system accepts neuronal input. Requiring both endpoints to receive the same vector would pre-impose a coordinate system whose recovery is supposedly under test; requiring the same physical stimulus would be equally artificial.

Pontifex therefore asks whether controlled interventions can serve as bridges between otherwise unaligned representational spaces. For sequential systems, the intervention must also be placed in a history. Hunger followed by sugar contact is not equivalent to sugar contact followed by hunger; a textual event inserted before a goal is established need not have the same effect as the same event inserted afterward.

The primary question is:

> Can two radically different substrates exhibit **predictively corresponding relational response structure** to independently defensible realizations of the same ordered causal story, beyond what is explained by time, labels, lexical overlap, generic relational alignment, flexible warping, renderer choices, generic recurrence, or a directly learned translator?

The intended endpoint is operational and predictive. It is not an inference of shared internal ontology or identical computation.

## 2. Relation to Pontifex and causal abstraction

### 2.1 Intervention concepts and native realizations

Let C be a registry of experimental intervention concepts and let each substrate S have a realization function

\[
R_S : C \times X_S \rightarrow X_S.
\]

For a concept c, generally

\[
R_Q(c) \neq R_F(c),
\]

where Q denotes the language branch and F the fly-connectome branch. The experiment requires a defensible equality of **intended experimental distinction**, not equality of objects.

This idea is adjacent to established causal-abstraction work: mappings between low-level and high-level interventions are part of the abstraction contract rather than an automatic consequence of shared labels. The proxy registry here is therefore an experimental hypothesis to be stress-tested, not a semantic oracle.

### 2.2 Intervention-in-history

For sequential data, define an intervention instance

\[
i_k=(c_k,\tau_k,h_k),
\]

where c_k is the concept, τ_k∈[0,1] its narrative position, and h_k the relevant preceding history. The same nominal intervention may have different consequences at different points in a trajectory.

### 2.3 Boundaries as a testable constraint

A canonical story declares an initial condition b and terminal condition e. The hypothesis is not that every narrative has a metaphysically privileged beginning or end. It is narrower: explicitly observed boundary conditions may reduce ambiguity about trajectories.

Narrative and event boundaries already have an established cognitive/neural literature. The proposal here is only that boundary information may add **incremental cross-substrate alignment information** after matched-content and matched-anchor controls.

## 3. Formal object

A canonical story is

\[
H=(V,\prec,b,e,\lambda),
\]

with event states V, an acyclic precedence relation ≺, initial state b, terminal state e, and labels/annotations λ used by the experimenter. The first experiment restricts H to a total order and assigns

\[
0=\tau_0 < \tau_1 < \cdots < \tau_n=1.
\]

Each substrate has a renderer ρ_S(H) and frozen observer O_S, yielding

\[
\gamma_S(\tau)=O_S(\rho_S(H)(\tau)).
\]

For an intervention i with a baseline story H and counterfactual H^(i), define an in-substrate response signature

\[
r_S(i)=\Psi_S\left(\gamma_S^{(i)}[\tau_i,1],\gamma_S[\tau_i,1]\right).
\]

The two response vectors are never directly subtracted. Instead define a within-substrate relation

\[
K_S(i,j)=k_S(r_S(i),r_S(j)),
\]

and ask whether a learned or inferred correspondence preserves enough of this relational structure to predict held-out responses.

## 4. Narrative transport

Physical time, textual length, and narrative progress need not coincide. Let

\[
\phi:[0,1]\rightarrow[0,1]
\]

be monotone, with φ(0)=0 and φ(1)=1. An objective may combine relational distortion, monotonicity, endpoint constraints, and explicit capacity regularization.

Monotone multimodal alignment is established prior art. Canonical Time Warping and Generalized Time Warping already align sequences across heterogeneous modalities, while Gromov Dynamic Time Warping aligns time series in incomparable spaces by comparing intra-relational geometry. Accordingly, **monotone cross-space temporal alignment is a baseline, not the novelty claim**.

Any confirmatory run must preregister the admissible warp/map family and its capacity. A sufficiently flexible map can manufacture apparently strong correspondence even in systems without the intended computation; therefore capacity is itself a controlled experimental variable.

## 5. Experimental design

### 5.1 Stage A: clamped causal stories

The initial experiment uses externally scheduled event sequences. This avoids confounding representation alignment with policy learning and environment dynamics. The connectome evolves recurrently, but the event ledger is fixed by the protocol.

A later stage may close the perception→state→action→environment→reinforcement loop; such a stage is a separate experiment, not evidence silently imported into v0.1.

### 5.2 Example story family

A feeding-oriented family provides interpretable sensory and motivational variables. A canonical ledger might include:

| τ | event concept | role |
|---:|---|---|
| 0.00 | food-deprived initial state | initial boundary |
| 0.15 | appetitive odor appears | distal cue |
| 0.30 | odor intensity increases | approach proxy |
| 0.45 | sugar contact | gustatory event |
| 0.60 | nutrient availability | consumption proxy |
| 0.75 | satiety-related transition | internal-state proxy |
| 0.90 | food-seeking drive decreases | consequence proxy |
| 1.00 | stable post-feeding state | terminal boundary |

Variants should manipulate deprivation, sugar concentration, odor timing, omission, aversive taste, interruption, inter-event timing, and textual paraphrase while preserving a prespecified train/validation/test split.

This ledger is a task schema, not a claim that MaleCNS connectivity alone implements metabolism or neuromodulator chemistry.

### 5.3 Language branch

Use a frozen embedding observer. A practical initial candidate is Qwen3-Embedding-0.6B, but the framework is model-agnostic.

At event k, the primary representation is the cumulative prefix

\[
P_k=[s_0,\ldots,s_k],
\]

with isolated-event and fixed-window representations retained as controls. Each conceptual story should have multiple controlled paraphrases.

### 5.4 MaleCNS branch

Use the complete available MaleCNS graph when technically feasible; a reduced graph may be used only as an explicitly labeled pilot. Every task concept maps to an anatomically declared input or modulation proxy. The registry must record:

- biological evidence;
- target population/pathway;
- sign and timing;
- magnitude convention;
- confidence and alternatives;
- whether the realization is sensory, motivational, reinforcement-related, or explicitly engineered.

A structural connectome does not by itself specify dopamine, octopamine, serotonin, receptor expression, metabolic state, or other chemical dynamics. Neuromodulatory concepts therefore require an explicit dynamical model and should not be implemented as arbitrary global scalar broadcasts.

### 5.5 Proxy registry and construct validity

The registry is known to the experimenter but not necessarily to the aligner. It is fixed before confirmatory response data are inspected.

To reduce hidden experimenter-induced correspondence, confirmatory work should use:

1. independently specified proxy mappings where feasible;
2. multiple biologically plausible renderers for the same concept;
3. negative proxy pairs that are plausible in superficial form but intentionally mismatch the causal distinction;
4. size/magnitude-matched arbitrary neural targets;
5. blinded or independent judgments of whether text and fly realizations instantiate the intended distinction.

A result that exists only for one hand-tuned registry is evidence about that registry, not about a general cross-substrate correspondence.

### 5.6 Information regimes

Three regimes separate experimental ground truth from aligner information:

- **boundary-only:** only start/end anchors and trajectories are exposed;
- **sparse-anchor:** a prespecified fraction of internal correspondences is exposed;
- **full concept oracle:** all identities are exposed as an upper-bound diagnostic.

The primary scientific evidence should come from boundary-only or sparse-anchor conditions.

## 6. Response-field alignment and held-out prediction

For each story, construct baseline and counterfactual trajectories. Summarize each intervention by downstream magnitude, direction where meaningful, persistence, recovery time, local derivatives, and pairwise relations.

The primary held-out task fits the cross-space cartography on training concepts/stories and then, from a language-side held-out response, predicts:

1. the corresponding MaleCNS narrative region;
2. nearest MaleCNS response neighbors;
3. relative effect-magnitude rank;
4. where applicable, paired-intervention interaction relations.

Only after prediction is fixed is the held-out MaleCNS response revealed for scoring.

## 7. Evaluation and baseline ladder

No single score defines success. Report temporal retrieval, relational-matrix agreement, neighborhood overlap, held-out response prediction, warp complexity, and paraphrase stability.

The conventional baseline ladder must include, under the same information budget:

1. normalized-time / time-only monotone matching;
2. CTW/GTW-style multimodal temporal alignment where applicable;
3. GDTW on the same trajectory representations;
4. static or temporally stratified Gromov–Wasserstein matching on response dissimilarity matrices;
5. a direct paired cross-space translator with matched supervision/capacity;
6. the Pontifex interventional response-field method.

GDTW and Gromov–Wasserstein baselines are particularly important because generic intra-relational alignment across incomparable spaces and unlabeled structural matching are established before this proposal. Pontifex cannot claim explanatory advantage merely by rediscovering that generic structure.

## 8. Required controls and ablations

### 8.1 Temporal and label controls

- time-only matching;
- concept-label oracle;
- concept-label permutation;
- random event-order permutation;
- local adjacent swaps and complete reversal;
- missing-event tests.

### 8.2 Boundary-content versus endpoint-anchor control

The boundary hypothesis must separate two effects: information in the beginning/end content and privileged status of points declared as anchors.

Compare at least:

- real boundaries with real anchor status;
- real boundary content without privileged anchor status;
- matched interior content assigned endpoint-anchor status;
- removal of beginning/end versus equal-size interior removal;
- random fragments matched for retained length/information budget.

If arbitrary endpoint anchors reproduce the effect, evidence for a special role of narrative boundary content weakens.

### 8.3 History controls

Compare cumulative prefixes against:

- isolated event descriptions;
- fixed-width context;
- prefix-length-matched paraphrases;
- lexical-overlap-matched variants;
- participant/entity-overlap-matched variants;
- shuffled-order prefixes preserving much of the same token content;
- incremental response vectors, e.g. E(P_k)-E(P_{k-1}), to test whether apparent history effects are just nested-prefix smoothness.

### 8.4 Proxy controls

- biologically motivated versus arbitrary size/magnitude-matched neural targets;
- multiple independent/plausible renderers;
- negative proxy pairs;
- proxy mappings specified before cross-space results are inspected.

### 8.5 Alignment-capacity and observer nulls

Preregister map/warp capacity and regularization. Include:

- random or untrained text observers where technically meaningful;
- response-structure shuffles preserving marginal statistics;
- capacity-matched random mapping/null models;
- disjoint story families or vocabulary at test time where feasible.

These controls are required because high-capacity alignment can produce impressive scores without the intended shared computation.

### 8.6 MaleCNS topology controls

Use directed degree-preserving rewires and matched random recurrent networks with comparable node count, edge count, edge-weight distribution where practical, interface capacity, initialization, dynamics budget, and evaluation protocol. MaleCNS-specific evidence requires beating these matched nulls.

## 9. Preregistered predictions

**P1 — complete-history advantage.** Full stories outperform matched fragments after content controls.

**P2 — boundary-content advantage.** Real beginning/end content adds predictive value beyond arbitrary endpoint-anchor status.

**P3 — order dependence.** Temporal permutation/reversal materially reduces held-out correspondence.

**P4 — history advantage beyond nesting.** Cumulative history outperforms isolated/fixed-window/shuffled-prefix and incremental-vector controls after lexical/participant overlap is matched.

**P5 — proxy-validity advantage.** Biologically justified proxies outperform arbitrary matched targets and remain reasonably stable across independently specified plausible renderers.

**P6 — added value beyond generic alignment.** Pontifex adds held-out predictive value beyond time-only, CTW/GTW, GDTW/GWOT, and direct-translation baselines under matched information and capacity.

**P7 — held-out intervention generalization.** Hidden intervention neighborhoods are recovered above permutation and capacity-matched nulls.

**P8 — paraphrase invariance.** Correspondence is more stable across paraphrases of the same concept than across different intervention concepts.

**P9 — composition consistency.** Paired-intervention interaction relations are better preserved in the two real systems than in shuffled concept pairs.

**P10 — topology specificity is conditional.** Biological MaleCNS topology outperforms rewired/random recurrent controls only if topology contributes relevant structure; otherwise the topology claim fails.

## 10. What would count as failure or narrowing?

The strong version of the proposal is unsupported or must narrow if reproducibly:

1. generic time-only, CTW/GTW, GDTW/GWOT, or direct-translation baselines match the claimed held-out advantage;
2. temporal permutation does not materially reduce correspondence;
3. concept-label permutation or other leakage explains performance;
4. history effects vanish under lexical/participant/length and incremental-vector controls;
5. arbitrary endpoint anchors explain the boundary result;
6. arbitrary neural input locations or negative proxy pairs perform as well as justified proxies;
7. results are unstable across independently defensible renderers;
8. held-out interventions cannot be recovered above permutation/capacity-matched nulls;
9. random/untrained observers or shuffled response fields produce comparable alignment;
10. the admissible warp/map family is so flexible that unrelated trajectories are easily aligned;
11. paraphrase controls destroy the effect;
12. matched random or rewired recurrent systems reproduce the MaleCNS result.

A failure of topology specificity does not automatically invalidate response-field alignment as an engineering method; it invalidates the stronger claim that MaleCNS organization contributes unique structure in that experiment.

## 11. Prior art and bounded contribution

Several components are established and are treated here as antecedents rather than discoveries.

- **Dynamic time warping:** monotone sequence alignment is classical.
- **Canonical / Generalized Time Warping:** multimodal temporal alignment across heterogeneous feature spaces predates this proposal.
- **Gromov Dynamic Time Warping:** Cohen et al. align time series in incomparable spaces using intra-relational geometry, directly occupying the generic relational+temporal-alignment component.
- **Gromov–Wasserstein structural matching:** Kawakita et al. align human and LLM color-similarity structures without predefined cross-system labels, occupying a close unlabeled heterogeneous-structure component.
- **Causal abstraction:** intervention mappings between levels/models are established parts of abstraction contracts.
- **Narrative/event boundaries:** cognitive/neural effects of event segmentation and boundaries are established.
- **Shared/relative representation methods:** common probes, anchors, shared-response models, representational similarity, response-based model comparison, and intervention-based representation analysis are established lineages.

A dated claim-specific audit fixed the conservative public cutoff for this manuscript at **2026-09-19T13:52:51Z**. In the bounded searches documented in `audits/prior-art/narrative-proxy-interventions-2026-09-19.md`, no pre-cutoff work was located containing the full conjunction of text-native and MaleCNS-native proxy interventions embedded in an ordered story, hidden internal correspondences, held-out intervention-response prediction, proxy-location controls, alignment-capacity nulls, and MaleCNS topology nulls.

That is a bounded negative-search result, **not a claim of being first**. The candidate contribution is the experimental composition and falsification ladder, not its individual alignment, intervention-mapping, or narrative-boundary ingredients.

## 12. Interpretation of a positive result

A successful result should be reported first as:

> **predictive structural correspondence under the declared interventions and controls.**

It would mean that one substrate's intervention-response relations predict held-out relations in the other better than the declared conventional and null models.

It would **not**, by itself, establish:

- shared mechanism;
- identical or isomorphic latent ontology;
- the same computation;
- biological equivalence of the proxy renderers;
- complete *Drosophila* neurophysiology in the MaleCNS dynamical model.

Sutter et al. show why flexible maps can make causal correspondence vacuous under broad conditions, including strong intervention-alignment scores in systems lacking the target capability. Bertram et al. show why decoding/representational alignment need not imply aligned encoding organization or computation. Stronger mechanistic claims therefore require evidence beyond the alignment itself.

## 13. Practical first experiment

A minimal confirmatory study can use approximately 200–500 prespecified story variants, multiple textual paraphrases, frozen train/validation/test assignment, a frozen embedding observer, and a declared MaleCNS dynamical implementation.

Store for every run:

- story and paraphrase IDs;
- concept registry version;
- connectome version and file hashes;
- input populations and transfer functions;
- all dynamical parameters;
- aligner/warp family and capacity;
- random seeds;
- observer versions;
- null-model construction;
- exact code/data commit.

Run the baseline ladder and controls before touching the held-out set. The experiment should be considered confirmatory only if registry, metrics, capacity, exclusions, and primary comparisons are frozen beforehand.

## 14. Limitations

### 14.1 Structural connectome versus physiology

MaleCNS is an anatomical connectivity resource. A dynamical model built from it is not automatically a faithful simulation of neurotransmitter chemistry, receptor state, metabolism, hormonal modulation, plasticity, or the living animal. The experiment must say exactly which biological facts are represented and which are engineered approximations.

### 14.2 Proxy construct validity

The central bridge is an experimenter-defined mapping from a concept to two native realizations. This is a construct-validity problem. A registry can unintentionally encode the desired answer. Multiple renderers, negative proxy pairs, independent specification, and precommitment reduce but do not eliminate this risk.

### 14.3 Narrative time and boundaries are hypotheses

Narrative time is an experimental coordinate, not a biological clock or universal semantic time. Boundary effects can be confounded by endpoint anchors, extra content, lexical structure, or sampling density. Those factors require separate controls.

### 14.4 Alignment flexibility can manufacture correspondence

High-capacity transformations can overfit relational structure. Map/warp capacity, regularization, training information, and null models must be preregistered. An alignment score without capacity-matched controls has weak mechanistic meaning.

### 14.5 Correspondence is not mechanism

Representational or decoding alignment does not entail shared encoding organization, computation, or ontology. The strongest interpretation licensed by the proposed protocol alone is predictive structural correspondence under declared interventions.

### 14.6 Prior-art search is bounded

The claim-specific search records a fixed cutoff and explicit search protocol, but it is not exhaustive. Failure to locate the full conjunction is not proof of novelty or priority.

### 14.7 No empirical result in v0.1

This archival version is a scientific position paper and preregistrable protocol. It reports **no new MaleCNS↔language alignment result** and makes no empirical success claim. Any later result must be versioned prospectively and tied to the exact frozen protocol or clearly documented amendments.

## 15. Conclusion

Narrative Proxy Interventions proposes a controlled way to compare heterogeneous sequential systems without assuming common coordinates or identical physical stimuli. The shared experimental object is an intervention concept embedded in an ordered history; each substrate receives a native realization; the comparison is made through within-substrate response relations and held-out prediction.

The framework is scientifically useful only if it survives stronger alternatives than a time-only matcher. CTW/GTW, GDTW/Gromov–Wasserstein alignment, direct translators, endpoint-anchor controls, lexical/history controls, renderer perturbations, random/untrained observers, shuffled responses, and matched recurrent nulls are part of the protocol rather than after-the-fact defenses.

If the method survives those tests, the warranted result is deliberately narrow: **the two selected systems exhibit predictive structural correspondence in the ordered consequences of the declared interventions**. Whether that correspondence reflects shared mechanism or computation is a separate question requiring additional evidence.

---

## References

Ahuja, K., Mahajan, D., Wang, Y., & Bengio, Y. (2023). Interventional causal representation learning. *Proceedings of the 40th International Conference on Machine Learning (PMLR 202)*.

Baldo, F. S. (2026a). *Pontifex: Byte-Level Occlusion with Multi-Space Convergence for Tokenizer-Free, Cross-Modal Interpretability*. Research manuscript, `pontifex.md`.

Baldo, F. S. (2026b). *Interventional Latent Graphs: Binary Distinctions as Minimal Operational Edges Between Representation Spaces*. Research manuscript, `interventional_latent_graph.md`.

Beckers, S., & Halpern, J. Y. (2019). Abstracting causal models. *Proceedings of the AAAI Conference on Artificial Intelligence, 33*(01). https://doi.org/10.1609/aaai.v33i01.33012678

Berg, S., Beckett, I. R., Costa, M., et al. (2026). Sexual dimorphism in the complete *Drosophila* male central nervous system connectome. MaleCNS v1.0 released 8 June 2026; publication 3 September 2026. Janelia FlyEM Male CNS Connectome Project.

Bertram, J., Dyballa, L., Keller, T. A., Kinger, S., & Zucker, S. W. (2026). Decoding Alignment without Encoding Alignment: A critique of similarity analysis in neuroscience. arXiv:2605.05907.

Chen, P.-H., Chen, J., Yeshurun, Y., Hasson, U., Haxby, J., & Ramadge, P. J. (2015). A reduced-dimension fMRI shared response model. *Advances in Neural Information Processing Systems*.

Cohen, S., Luise, G., Terenin, A., Amos, B., & Deisenroth, M. P. (2021). Aligning time series on incomparable spaces. *Proceedings of AISTATS 2021, PMLR 130*. arXiv:2006.12648.

Cohen, J. P., Blankemeier, L., & Chaudhari, A. (2023). Identifying spurious correlations using counterfactual alignment. arXiv:2312.02186.

Gat, I., Lorberbom, G., Schwartz, I., & Hazan, T. (2022). Latent space explanation by intervention. *Proceedings of the AAAI Conference on Artificial Intelligence*.

Inagaki, H. K., Ben-Tabou de-Leon, S., Wong, A. M., Jagadish, S., Ishimoto, H., Barnea, G., Kitamoto, T., Axel, R., & Anderson, D. J. (2012). Visualizing neuromodulation in vivo: TANGO-mapping of dopamine signaling reveals appetite control of sugar sensing. *Cell, 148*(3), 583–595. https://doi.org/10.1016/j.cell.2011.12.022

Kawakita, G., Zeleznikow-Johnston, A., Tsuchiya, N., & Oizumi, M. (2024). Gromov–Wasserstein unsupervised alignment reveals structural correspondences between the color similarity structures of humans and large language models. *Scientific Reports, 14*, 15917. https://doi.org/10.1038/s41598-024-65604-1

Kriegeskorte, N., Mur, M., & Bandettini, P. A. (2008). Representational similarity analysis — connecting the branches of systems neuroscience. *Frontiers in Systems Neuroscience, 2*, 4.

Li, Y., Zhang, Z., Liu, B., Yang, Z., & Liu, Y. (2021). ModelDiff: Testing-based DNN similarity comparison for model reuse detection. *ISSTA 2021*. arXiv:2106.08890.

Moschella, L., Maiorca, V., Fumero, M., Norelli, A., Locatello, F., & Rodolà, E. (2022). Relative representations enable zero-shot latent space communication. arXiv:2209.15430.

Sakoe, H., & Chiba, S. (1978). Dynamic programming algorithm optimization for spoken word recognition. *IEEE Transactions on Acoustics, Speech, and Signal Processing, 26*(1), 43–49.

Speer, N. K., Zacks, J. M., & Reynolds, J. R. (2007). Human brain activity time-locked to narrative event boundaries. *Psychological Science, 18*(5). https://doi.org/10.1111/j.1467-9280.2007.01920.x

Sutter, D., Minder, J., Hofmann, T., & Pimentel, T. (2025). The Non-Linear Representation Dilemma: Is Causal Abstraction Enough for Mechanistic Interpretability? *NeurIPS 2025*. arXiv:2507.08802.

Wurgaft, D., et al. (2026). Manifold Steering Reveals the Shared Geometry of Neural Network Representation and Behavior. arXiv:2605.05115.

Zacks, J. M., & Swallow, K. M. (2007). Event Segmentation. *Current Directions in Psychological Science, 16*(2). https://doi.org/10.1111/j.1467-8721.2007.00480.x

Zhang, Y., Li, M., Long, D., Zhang, X., Lin, H., Yang, B., Xie, P., Yang, A., Liu, D., Lin, J., Huang, F., & Zhou, J. (2025). Qwen3 Embedding: Advancing Text Embedding and Reranking Through Foundation Models. arXiv:2506.05176.

Zhou, F., & De la Torre, F. (2009). Canonical Time Warping for Alignment of Human Behavior. *Advances in Neural Information Processing Systems*.

Zhou, F., & De la Torre, F. (2012). Generalized Time Warping for Multi-Modal Alignment of Human Motion. *Proceedings of CVPR 2012*. https://doi.org/10.1109/CVPR.2012.6247812
