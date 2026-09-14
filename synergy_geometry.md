---
type: "Technical Paper"
title: "Gauge-Controlled Interaction Geometry: Testing Whether Semantic Composition Produces Transferable Synergistic Structure in Language Models"
description: "Position paper and staged experimental programme asking whether purified interaction components in language-model activations are relation-specific, compositionally generalizable, causally efficacious, and stable across independently trained models."
tags: [interaction-geometry, synergy, compositionality, mechanistic-interpretability, representation-geometry, semantic-atlas]
timestamp: 2026-08-24T01:14:00Z
---

# Gauge-Controlled Interaction Geometry: Testing Whether Semantic Composition Produces Transferable Synergistic Structure in Language Models

**Franklin Baldo**  
Independent Researcher  
franklinbaldo@gmail.com

---

> **Position paper and experimental programme.** This manuscript does not claim that semantic composition, interaction effects, binding, information synergy, or emergent structure are new phenomena. It reports no model-backed positive result. Its narrow research question is whether language models contain an identifiable interaction geometry that survives marginal controls, held-out composition, causal intervention, and independently calibrated cross-model comparison. The confirmatory gate sequence is preregistered separately in `experiments/synergy_geometry/protocol.md` and `protocol-amendment-001.md`. Failure at the early gates is intended to terminate the strong claim rather than trigger rescue tuning.

## Abstract

When two semantic factors are processed jointly, the resulting neural state will generally differ from states induced by either factor alone. That observation is not new. Compositional semantics studies how meanings combine; tensor-product and vector-symbolic architectures provide explicit binding operators; functional ANOVA formalizes interaction terms; conceptual blending describes emergent structure in integrated conceptual spaces; multimodal fusion creates cross-source representations; and partial information decomposition (PID) defines information about a target that is available only from sources jointly. Recent mechanistic work also identifies causal, low-dimensional representations of relational binding in language models and localizes semantic composition across transformer depth.

This paper asks a narrower question. For controlled semantic factors $a\in A$ and $b\in B$, let $H_l(a,b)$ be a model activation at layer $l$. After fixing an experimental distribution and an admissible representation gauge, we decompose

$$
H_l(a,b)=H_{0,l}+H_{A,l}(a)+H_{B,l}(b)+J_l(a,b),
$$

where $J_l$ is an identified interaction term relative to that design. The claim under test is not that $J_l\neq0$. Generic nonlinearity already makes that unsurprising. The stronger hypothesis is that, for some relation-dependent computations, $J_l$ has structure that is simultaneously (i) informative beyond matched marginal and nonlinear baselines, (ii) generalizable to unseen factor combinations, (iii) selectively causal for the relation-dependent output, and (iv) partially stable across independently trained model families after alignment learned without the confirmatory joint interactions. A secondary hypothesis asks whether this geometry covaries with target-relative information synergy measured independently by PID.

The proposal therefore separates five objects often conflated under words such as *emergence*: representational non-additivity, statistical synergy, semantic relevance, causal efficacy, and cross-model geometric stability. We define failure conditions for each and argue that only their conjunction would justify treating interaction geometry as a useful scientific primitive. If the conjunction fails, the appropriate conclusion is not that composition is absent, but that established concepts such as binding, nonlinear contextualization, or target-level synergy are sufficient without positing a transferable interaction geometry. If it succeeds, the result may motivate a later extension of the Semantic Atlas from a map of states and transitions to a map that also represents multi-input semantic operators or hyperedges.

**Keywords:** compositionality, interaction effects, partial information decomposition, synergy, relational binding, mechanistic interpretability, representation geometry, causal intervention, Semantic Atlas

---

## 1. The claim we are not making

A tempting informal statement is:

> Combining two semantic regions can create information or meaning that was absent from either region separately.

As a novelty claim, this is untenable.

The principle of compositionality and its distributional descendants study mappings from component meanings to composite meanings. Tensor Product Representations explicitly bind fillers to roles through higher-order products [1]. Holographic Reduced Representations and later Vector Symbolic Architectures provide fixed-dimensional binding and superposition operators [2]. Conceptual blending treats multiple input spaces as sources for a blended space in which completion and elaboration can support emergent structure and inference [3]. Functional ANOVA gives an explicit decomposition into lower-order and interaction effects and emphasizes that those effects are not identifiable without constraints and a data distribution [4]. PID was introduced precisely to distinguish redundant, unique, and synergistic information about a target [5,6]. Modern multimodal work now applies PID directly to model decisions and layerwise interaction analyses [7].

Recent language-model research closes the gap further. Additive compositionality can be quantified across layers and tested on unseen attribute combinations [8]. Semantic composition has been causally probed across transformer depth rather than assumed to occur at one privileged layer [9,10]. Relational binding has been localized to low-dimensional, causally functional geometry that transfers across contexts and appears in more than one model family [11].

Accordingly, none of the following is treated as a contribution here:

- the existence of a composition function $F(a,b)$;
- the fact that $F(a,b)$ may be nonlinear;
- a nonzero residual after subtracting two marginal vectors;
- the existence of information available only from two sources jointly;
- the existence of relation-specific activations;
- the possibility of binding entities, attributes, or roles;
- the possibility that composition is distributed over several layers.

The paper survives only if it identifies a narrower conjunction not supplied by any one of those observations.

## 2. Formal object and the gauge problem

Let $A$ and $B$ be finite sets of experimentally controlled semantic factors. They need not be vector spaces. For a frozen model $M$, layer $l$, and controlled context/scaffold $c$, define

$$
H_l^M(a,b;c)\in Z_l^M\subseteq\mathbb R^{d_l}.
$$

A joint state is therefore a point in the model's existing activation space. No new ambient space is implied by composition.

For a balanced factorial design, define the empirical decomposition

$$
H_l(a,b)=H_{0,l}+H_{A,l}(a)+H_{B,l}(b)+J_l(a,b),
$$

with centering constraints

$$
\mathbb E_A H_{A,l}=0,\qquad
\mathbb E_B H_{B,l}=0,
$$

and

$$
\mathbb E_A J_l(a,b)=0,\qquad
\mathbb E_B J_l(a,b)=0.
$$

Under the frozen empirical distribution, $J_l$ is the pure pairwise interaction term in the functional-ANOVA sense. It is not an observer-independent metaphysical residue.

A complementary diagnostic is the mixed finite difference

$$
D_l(a_1,a_2;b_1,b_2)=
H_l(a_1,b_1)-H_l(a_1,b_2)-H_l(a_2,b_1)+H_l(a_2,b_2).
$$

If

$$
H_l(a,b)=p_l(a)+q_l(b),
$$

then $D_l=0$. For any invertible linear map $T$,

$$
D_{T\circ H}=T D_H,
$$

so the zero/non-zero property survives that declared gauge class.

This restriction matters. Under unrestricted nonlinear reparameterization, apparent interactions are not invariant. For positive variables, for example, a multiplicative relation $F(a,b)=ab$ becomes additive after the invertible transform $g(x)=\log x$. Therefore an interaction residual can only be interpreted relative to an explicit class of admissible transformations. Learned representations have analogous identifiability limits: representational coordinates are often identified only up to a transformation class, and similarity claims are meaningful only after the relevant invariances are declared [12].

The present programme therefore uses affine/linear gauge discipline for confirmatory geometric claims. A nonlinear transform chosen after seeing confirmatory results creates a new analysis, not a valid rescue of the original claim.

## 3. Five different notions hidden inside "new information"

The phrase *new information* is too ambiguous to carry the research claim. At least five notions must be separated.

### 3.1 Representational non-additivity

A joint activation differs from the best additive prediction of the marginal factors:

$$
H_l(a,b)\neq \widehat H_{A,l}(a)+\widehat H_{B,l}(b).
$$

This is weak evidence. Generic neural nonlinearity can generate it.

### 3.2 Statistical synergy

For an externally defined target $Y$, two sources contain information that is available only jointly. PID writes, schematically,

$$
I(A,B;Y)=R+U_A+U_B+S,
$$

where $R$ is redundant information, $U_A$ and $U_B$ are unique contributions, and $S$ is synergy. Different PID definitions need not assign the same numerical decomposition, so the estimator and definition must be fixed prospectively [5-7].

### 3.3 Semantic relevance

An interaction representation is semantically relevant when it predicts an externally grounded relation or property under controls that prevent trivial lexical, positional, or factor-identity decoding. Semantic interpretation is therefore task-relative and earned by behavioral evidence.

### 3.4 Causal efficacy

A representation may decode a relation without being used by the model. Causal efficacy requires intervention: perturbing, ablating, patching, or transplanting the interaction component should selectively alter relation-dependent behavior while preserving marginal identity better than matched control interventions.

### 3.5 Cross-model stability

A causal interaction mechanism in one model may still be architecture-specific. A stronger claim requires correspondence between independently trained models after an alignment calibrated without the confirmatory interaction pairs. The alignment itself must not manufacture the correspondence.

These distinctions produce the central hierarchy:

$$
\text{non-additivity}
\not\Rightarrow
\text{synergy}
\not\Rightarrow
\text{semantic mechanism}
\not\Rightarrow
\text{cross-model geometry}.
$$

The arrows are empirical questions, not definitions.

## 4. The surviving hypothesis

The programme tests the following narrow conjecture.

> **Gauge-Controlled Interaction Geometry hypothesis.** For some relation-dependent computations, a purified interaction component $J_l(a,b)$ forms a reproducible geometric object that carries relation information beyond matched marginal baselines, generalizes to unseen combinations, is selectively used by the model, and exhibits above-null correspondence across independently trained model families after independently calibrated alignment.

This is intentionally conjunctive. A positive result on only one clause is classified more weakly.

- Decodability without generalization: **interaction correlate**.
- Generalization without causal evidence: **interaction representation**.
- Causal evidence in one model only: **model-specific interaction mechanism**.
- Causal, cross-model correspondence: **transferable interaction geometry**.
- Additional stable relation to PID synergy: **synergy–geometry coupling**.

Only the last two outcomes would materially exceed the prior-art boundary established above.

## 5. Why nonlinear prediction is a necessary but not decisive control

Suppose a capacity-matched MLP predicts the joint state from marginal states:

$$
\widehat H_l(a,b)=g_l(H_l(a,\varnothing),H_l(\varnothing,b)).
$$

If this prediction is excellent, that does not show there is no interaction. It shows that the joint state is computable from its inputs, which any deterministic model already implies in a broad sense. The important questions are instead whether the identified interaction is relation-specific, whether it generalizes outside fitted pairings, and whether the model behavior depends selectively on it.

Conversely, merely beating a linear baseline is nearly uninformative. The confirmatory comparisons therefore include additive, ridge, bilinear, and nonlinear marginal predictors; direct marginal probes; shuffled pairings and labels; random subspaces; and raw joint activations as an upper-reference representation.

The intended burden is not to prove that the transformer is nonlinear. It is to show that a particular interaction decomposition exposes a stable functional variable that simpler explanations do not exhaust.

## 6. Experimental programme

The preregistered protocol defines five sequential gates. The implementation already includes the cheap interaction extractor, mixed finite differences, split validation, deterministic ridge decoding, paired bootstrap comparison, and synthetic additive/XOR controls. No model-backed success is inferred from that apparatus.

### Gate 0 — instrument sanity

Synthetic additive representations must produce no interaction signal under the extractor. A synthetic XOR-style construction must produce the expected positive interaction/synergy signature. Failure stops the programme because the measurement apparatus is invalid.

### Gate 1 — relation-specific interaction

Use controlled task families in which two factors jointly determine an objective relation. Train interaction estimators and fixed-capacity decoders on `train`; evaluate only once on a distinct `interaction_test` split containing held-out examples but not yet requiring unseen pair combinations.

The primary test asks whether $J_l$ predicts the relation better than the strongest marginal-only baseline by the preregistered margin, with paired uncertainty excluding zero. Shuffled pair and label controls must collapse.

### Gate 2 — compositional generalization

Without refitting, evaluate the frozen estimator and decoder on `composition_test`, whose factor combinations were absent during fitting. This gate is deliberately separate from Gate 1. A model can contain a relation-specific interaction signature that merely memorizes familiar pairings; such an outcome should be visible rather than collapsed into a generic failure.

### Gate 3 — causal efficacy

Identify the relation-associated interaction subspace using training data only. At a frozen site, perform activation patching or another norm-matched intervention designed to move the interaction representation toward a target relation. Compare against random-subspace, sham, and marginal-component interventions.

The strong result requires selective relation switching with preservation of factor/entity identity. Broad output degradation is a failure, not causal evidence.

### Gate 4 — cross-model stability

Repeat the phenomenon in an independently trained model family. Cross-model centering, whitening, and linear/orthogonal alignment are learned only from independent calibration material. Confirmatory interaction vectors are never used to fit the alignment.

The primary cross-model metric must beat both unaligned and shuffled-calibration controls. A result confined to one architecture remains scientifically interesting but does not establish transferable interaction geometry.

### Gate 5 — synergy–geometry coupling

Only after interaction structure has survived the earlier gates, estimate a preregistered PID quantity for the externally defined target $Y$. Compare independent measurements of:

$$
S=\text{target-relative synergy},
$$

$$
G=\text{interaction-geometry strength or structure},
$$

and

$$
C=\text{causal efficacy}.
$$

A positive result requires held-out association among these quantities under the declared correction procedure. High synergy alone cannot rescue failed geometry; strong geometry alone cannot be relabeled synergy.

## 7. Task design

The first confirmatory models should be small, frozen, open-weight causal language models with accessible hidden states. The primary and transfer models should come from independently trained families. Exact model and tokenizer revisions, dtype, layer-selection rule, prompt templates, answer positions, and library versions must be frozen before confirmatory model-backed collection.

The first task families should be deliberately unromantic.

### 7.1 Pairwise relational comparison

Two independently varied facts determine a relation such as equality, ordering, or spatial comparison. Neither factor alone determines the target. Lexical scaffolds and answer positions remain balanced.

### 7.2 Controlled entity–relation binding

Entity and relation factors determine the correct bound attribute or output. This family directly confronts the strongest mechanistic predecessor: recent cell-based relational-binding results [11]. The new experiment must show that its purified-interaction formulation adds evidence beyond simply rediscovering a binding subspace.

### 7.3 Why metaphor and discovery are deferred

Metaphor, analogy, synthesis, and scientific discovery motivated the original intuition, but they are poor first tests. Ground truth is less precise, marginal insufficiency is hard to guarantee, and post-hoc semantic interpretation is easy. A positive result in controlled relation tasks can later justify broader probes. A negative result should prevent escalation to settings in which almost any pattern can be narrated as emergence.

## 8. Direct collisions with recent literature

### 8.1 Additive compositionality

Guo et al. [8] explicitly test whether embeddings of unseen attribute combinations can be reconstructed compositionally and show that compositionality varies across layers and training stages. Their work means that additive reconstruction and its failures are already an empirical object. The present programme differs only if the residual interaction supports a separate functional claim rather than merely marking where additivity fails.

### 8.2 Distributed semantic composition

Aljaafari et al. [9] intervene on constituent representations across eight models and find that semantic composition is distributed across depth rather than localized to one layer. Their result blocks any claim that finding a layerwise integration profile is itself novel. Their later causal-tracing work connects compositional functions to semantically interpretable roles [10], further raising the bar.

### 8.3 Causal relational binding

Dai et al. [11] provide the closest mechanistic collision. They identify a low-dimensional grid-like Cell-based Binding Representation across domains and two model families, find transferable context relations, and use activation patching to establish causal relevance. A positive interaction-geometry result that merely recovers their phenomenon under different notation would be a redescription, not a contribution.

The surviving distinction is therefore demanding: the interaction component must be purified against marginal effects under a frozen factorial design, tested on unseen compositions, compared with matched nonlinear marginal baselines, aligned across models without using confirmatory joint interactions, and related independently to target-level synergy.

### 8.4 PID in modern multimodal models

Fang et al. [7] already use PID to separate unique, redundant, and synergistic contributions in multimodal language models, including layerwise analysis and modality-shuffling interventions. Consequently, measuring synergy in a transformer is not novel. The open question here is the coupling of such target-level information with an independently identified geometric and causal interaction object.

## 9. Falsification matrix

| Outcome | Interpretation | Strong programme |
| --- | --- | --- |
| Gate 0 fails | instrument invalid | stop |
| Gate 1 fails in both task families | no evidence that purified interaction adds relation information beyond controls | stop; retain only framing |
| Gate 1 passes, Gate 2 fails | relation-specific interaction without compositional generalization | stop strong claim |
| Gates 1–2 pass, Gate 3 fails | stable decodable geometry may be epiphenomenal | do not claim mechanism |
| Gates 1–3 pass, Gate 4 fails | model-specific causal interaction mechanism | no cross-model claim |
| Gates 1–4 pass, Gate 5 fails | transferable interaction geometry without demonstrated PID coupling | publishable narrower result if robust |
| Gates 1–5 pass prospectively | evidence for synergy–geometry coupling | strongest supported claim |

This matrix is intentionally asymmetric. A later gate cannot rescue an earlier failure by changing definitions, splits, layers, or gauges after inspection.

## 10. Relation to the Semantic Atlas

The Semantic Atlas currently models semantic states, trajectories, transition dynamics, reachability, and intervention cost in a calibrated frame. Its existing notion of a semantic bridge is sequential: a difficult transition may become reachable through intermediate states.

Interaction geometry would introduce a different primitive. Instead of an ordinary transition

$$
q_a\rightarrow q_b,
$$

one could represent a multi-input operation schematically as

$$
\{q_a,q_b\}\longrightarrow q_{ab}.
$$

The natural data structure would be closer to a directed hyperedge than an ordinary edge. Such an extension could matter if the interaction term improves held-out prediction of transition, reachability, or control cost beyond the state-only Atlas.

Nothing in the current hypothesis requires that conclusion. The state $q_{ab}$ may simply be an ordinary, previously unsampled point in the same fixed-dimensional space. The fact that it was produced jointly does not imply that the ambient semantic space grew. At most, successful experiments could show expansion of observed support, of the catalogue of reachable states, or of the atlas's operator vocabulary.

For that reason `semantic_atlas.md` should remain unchanged until the interaction programme earns integration empirically. If Gates 1–3 fail, the interaction idea remains a useful explanatory lens but adds no required Atlas primitive.

## 11. What a positive result would mean

A fully positive result would support a statement substantially narrower than the original intuition:

> Across at least two independently trained language-model families, some controlled relation-dependent computations are represented by purified interaction components whose geometry generalizes compositionally, whose intervention selectively changes relation behavior, and whose strength covaries with independently estimated target-level synergy.

That would not show that reasoning in general is composition, that metaphor is generated by the same mechanism, that neural models discover new semantic dimensions, or that the geometry is universal.

It would, however, identify a reusable experimental object connecting three literatures that are often studied separately:

$$
\text{functional interaction decomposition}
\quad+\quad
\text{information synergy}
\quad+\quad
\text{causal representation geometry}.
$$

That conjunction is the entire research bet.

## 12. What a negative result would mean

A clean negative result is scientifically valuable.

If matched marginal and nonlinear baselines explain relation-dependent behavior, then there is no need to posit a privileged interaction geometry. If interaction structure exists only in-sample, it is not a compositional representation. If it decodes but cannot be manipulated selectively, it is not established as a mechanism. If each model implements the relation with unrelated geometry, the phenomenon is model-specific. If PID synergy varies independently of the geometric object, then information-theoretic and representational interaction should remain separate concepts.

In each case the broad fact of semantic composition remains intact. What fails is only the stronger claim that composition exposes a transferable geometric primitive useful to a Semantic Atlas.

## 13. Conclusion

The scientifically interesting question is not whether combining two semantic inputs creates a different activation. It inevitably does in a contextual nonlinear system. Nor is the question whether jointly observed sources can contain synergistic information about a target; information theory already supplies that object.

The narrower question is whether a model constructs a relation-specific interaction representation that remains visible after the obvious explanations are removed, survives novel compositions, participates causally in the computation, and recurs across independently trained models under non-circular alignment.

That claim is hard enough to fail. It should be.

The accompanying protocol therefore treats failure as a stopping rule rather than an inconvenience. Until the causal and cross-model gates are passed, **Gauge-Controlled Interaction Geometry** is a candidate experimental object, not a new theory of semantics.

---

## References

1. Smolensky, P. (1990). Tensor Product Variable Binding and the Representation of Symbolic Structures in Connectionist Systems. *Artificial Intelligence*, 46(1–2), 159–216.
2. Plate, T. A. (1995). Holographic Reduced Representations. *IEEE Transactions on Neural Networks*, 6(3), 623–641.
3. Fauconnier, G., & Turner, M. (2002). *The Way We Think: Conceptual Blending and the Mind's Hidden Complexities*. Basic Books.
4. Lengerich, B., Tan, S., Chang, C.-H., Hooker, G., & Caruana, R. (2020). Purifying Interaction Effects with the Functional ANOVA: An Efficient Algorithm for Recovering Identifiable Additive Models. *AISTATS 2020*. https://proceedings.mlr.press/v108/lengerich20a.html
5. Williams, P. L., & Beer, R. D. (2010). Nonnegative Decomposition of Multivariate Information. arXiv:1004.2515. https://arxiv.org/abs/1004.2515
6. Bertschinger, N., Rauh, J., Olbrich, E., Jost, J., & Ay, N. (2014). Quantifying Unique Information. *Entropy*, 16(4), 2161–2183.
7. Fang, W., Zhang, T., Tao, W., & Chan, A. (2026). Towards Understanding Modality Interaction in Multimodal Language Models via Partial Information Decomposition. arXiv:2606.00959. https://arxiv.org/abs/2606.00959
8. Guo, Z., Xue, C., Xu, Z., Bo, H., Ye, Y., Pierrehumbert, J. B., & Lewis, M. (2025). Quantifying Compositionality of Classic and State-of-the-Art Embeddings. *Findings of EMNLP 2025*. https://aclanthology.org/2025.findings-emnlp.1206/
9. Aljaafari, N., Carvalho, D., & Freitas, A. (2026). Where Do LLMs Compose Meaning? A Layerwise Analysis of Compositional Robustness. *EACL 2026*. https://aclanthology.org/2026.eacl-long.214/
10. Aljaafari, N., Carvalho, D., & Freitas, A. (2026). Bridging Linguistic Structure and Mechanistic Interpretability for Conceptual Interpretation in Language Models. *CoNLL 2026*. https://aclanthology.org/2026.conll-main.44/
11. Dai, Q., Heinzerling, B., & Inui, K. (2026). Cell-Based Representation of Relational Binding in Language Models. *ACL 2026*. https://aclanthology.org/2026.acl-long.2194/
12. Roeder, G., Metz, L., & Kingma, D. P. (2021). On Linear Identifiability of Learned Representations. *ICML 2021*.
