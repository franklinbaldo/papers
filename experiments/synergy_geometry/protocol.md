---
type: "Protocol"
title: "Synergy–Geometry Coupling — Adversarial Experimental Protocol"
description: "Pre-registered kill-first experiment testing whether purified interaction geometry is relation-specific, generalizes compositionally, is causally efficacious, and transfers across independently trained language models."
tags: [semantic-atlas, synergy, interaction-geometry, causality, representation-geometry, preregistration]
timestamp: 2026-08-24T00:48:00Z
---

# Synergy–Geometry Coupling — Adversarial Experimental Protocol

## Status

Pre-registration. This protocol is intentionally separate from `semantic_atlas.md` and from the existing `experiments/semantic_atlas` harness.

The broad claim that combining two semantic inputs creates a genuinely new semantic space is **not** under test. That claim is already too close to established work on compositional semantics, conceptual blending, binding, feature interactions, tensor fusion, and information synergy to support a novelty claim by itself.

The experiment asks whether a much narrower conjunction of properties exists in language-model activations:

\[
\text{statistical synergy}
\;\stackrel{?}{\longleftrightarrow}\;
\text{interaction geometry}
\;\stackrel{?}{\longleftrightarrow}\;
\text{causal computation}.
\]

The default outcome is negative. Passing a gate permits the next gate; it does not retroactively validate the broad conceptual framing.

## Research question

After marginal effects are removed under an explicitly fixed representation gauge, do language models contain interaction components that are simultaneously:

1. **relation-specific** rather than generic nonlinearity;
2. **compositionally generalizable** to unseen factor combinations;
3. **causally efficacious** for the relation-dependent output; and
4. **cross-model stable** after alignment learned without the confirmatory joint interactions?

A secondary question is whether information-theoretic synergy about an externally defined target covaries with the geometric structure and causal efficacy of those interaction components.

## Claim boundary

Success would **not** show that:

- semantic spaces literally grow when concepts are combined;
- a joint activation contains metaphysically new information;
- non-additivity itself is novel;
- PID synergy is a new construct;
- conceptual blending has been rediscovered mechanistically;
- the Semantic Atlas should already be extended with composition operators;
- a cross-model relation geometry is universal across architectures, scales, languages, or training regimes.

At most, success would support a narrow empirical claim: some relation-dependent computations may be carried by an identifiable interaction geometry that survives held-out composition, causal intervention, and independently calibrated cross-model comparison.

## Formal objects

Let \(A\) and \(B\) be finite sets of experimentally controlled factors, not assumed to be vector spaces. For model \(M\), layer \(l\), and fixed scaffold/context \(c\), record the activation

\[
H_l^M(a,b;c)\in Z_l^M\subseteq\mathbb{R}^{d_l}.
\]

The model-induced map is

\[
F_l^M:A\times B\times C\rightarrow Z_l^M.
\]

A joint realization

\[
h_{ab}^{(l)}=F_l^M(a,b;c)
\]

is a state in the model's existing activation space. It is **not** called a new space.

### Marginal and interaction terms

For a balanced factorial design, estimate a functional-ANOVA-style decomposition

\[
H_l(a,b)=H_{0,l}+H_{A,l}(a)+H_{B,l}(b)+J_l(a,b),
\]

with centering constraints over the frozen experimental distribution so that the interaction term is identified relative to that design.

As a model-free contrast, also compute mixed finite differences

\[
D_l(a_1,a_2;b_1,b_2)=
H_l(a_1,b_1)-H_l(a_1,b_2)-H_l(a_2,b_1)+H_l(a_2,b_2).
\]

For an additive representation \(H_l(a,b)=p_l(a)+q_l(b)\), \(D_l=0\). Under an invertible linear map \(T\),

\[
D_{T\circ H}=T D_H,
\]

so the zero/non-zero interaction property is preserved within the declared linear gauge class.

Neither \(J_l\neq 0\) nor \(D_l\neq 0\) is itself evidence for semantic emergence.

## Gauge discipline

The confirmatory experiment permits only affine/linear representation changes whose parameters are fitted on declared calibration data.

No nonlinear transformation may be selected after inspecting confirmatory interaction results. A nonlinear reparameterization can turn multiplicative structure into additive structure and vice versa; therefore claims about interaction geometry are always relative to the frozen gauge class.

For cross-model tests, alignment must be learned from **independent calibration material** containing no confirmatory \(J_l(a,b)\) pairs. Alignment on the interaction vectors later used for evaluation is circular and invalidates the cross-model claim.

## Models

Primary model: a small frozen open causal language model with accessible hidden states.

Transfer model: a small independently trained open causal language model from a different family.

Candidate families may include Qwen and SmolLM, but exact model IDs, revisions, tokenizer revisions, dtype, layer-selection convention, and inference library versions must be frozen in the implementation manifest **before the first confirmatory model-backed run**.

A same-family checkpoint comparison may be added as a diagnostic but cannot substitute for the independently trained transfer model.

## Experimental task families

The first run should use controlled tasks with objective targets and exact factorial splits. Natural-language metaphor, open-ended analogy, and discovery tasks are explicitly deferred.

Use at least two task families so a positive result is not synonymous with one synthetic rule.

### Family R1 — pairwise relational comparison

Construct two independently varied source statements \(a\) and \(b\) and ask for a relation \(Y=R(a,b)\) that cannot be determined from either source alone. Suitable domains include spatial comparison, equality/difference of attributes, or ordered comparison.

The lexical scaffold is fixed and factor identities are substituted into matched positions.

### Family R2 — controlled entity–relation composition

Construct entity/relation combinations in which the correct output depends on binding the two controlled factors rather than recognizing either marginal factor alone. Freeze the grammar and label map before collection.

### Synthetic controls

- XOR-style construction: positive control for statistical synergy, not evidence for the semantic hypothesis.
- Strictly additive synthetic representation: negative control for the interaction extractor.
- Random labels: negative control for relation decoding.

## Data splits

Splits are by **factor identity and composition**, never random rows alone.

Freeze four disjoint manifests:

1. `calibration`: gauge/alignment material only;
2. `train`: fits interaction estimators and decoders;
3. `composition_test`: contains factor combinations absent from train;
4. `relation_holdout`: where feasible, contains a relation/template family absent from estimator fitting and is treated as a stronger exploratory transfer test.

At least one primary split must withhold complete pairings so neither \((a,b)\) nor a trivial paraphrase appears in training.

## Baselines

Every claimed interaction effect is compared against all applicable baselines:

1. additive reconstruction from marginal activations;
2. ridge/linear regression from concatenated marginals;
3. bilinear interaction model;
4. capacity-matched MLP from marginal activations;
5. decoder trained directly on marginal activations without constructing \(J_l\);
6. shuffled \((a,b)\) pairing with the same marginals;
7. shuffled target labels;
8. random low-rank subspace matched to the dimensionality of any learned interaction subspace;
9. raw joint activation \(H_l(a,b)\) as an upper-reference representation, not as proof of interaction.

A nonlinear baseline predicting the joint activation from marginals does **not** falsify interaction merely by succeeding. It tests how much of the joint state is predictably reconstructible from the marginals. The scientific burden remains relation specificity, held-out generalization, causal specificity, and cross-model stability.

## H1 — purified interaction geometry

For at least one nontrivial task family and a reproducible layer range, the purified interaction component \(J_l(a,b)\) contains relation-specific geometric structure that generalizes to unseen compositions after controlling for marginal information and matched nonlinear baselines.

### Primary H1 metric

Train a fixed-complexity relation decoder on \(J_l\) using only the train split and evaluate on `composition_test`.

H1 passes only if all of the following hold:

- interaction decoding exceeds the best marginal-only baseline by at least **5 absolute percentage points** on the primary balanced metric;
- the paired bootstrap 95% confidence interval for that improvement excludes zero;
- shuffled-pair and shuffled-label controls collapse toward their expected null level;
- the effect is not confined to a single cherry-picked layer: the layer-selection rule is frozen before confirmatory scoring, or the full predeclared layer profile is reported.

### H1 null

Any apparent \(J_l\) structure is generic nonlinearity, lexical/scaffold leakage, or a re-expression of marginal information and does not improve held-out relation information over matched controls.

## H2 — compositional generalization

The relation-specific structure in \(J_l\) survives factor combinations not observed while fitting the interaction estimator or decoder.

H2 passes only if the H1 effect remains on `composition_test` and performance does not fall to within **2 points** of the best marginal-only baseline.

A random row split is not admissible evidence for H2.

### H2 null

The interaction representation memorizes observed pairings or local lexical templates and does not transfer compositionally.

## H3 — causal efficacy

An intervention on a relation-associated interaction component changes the model's relation-dependent behavior while preserving marginal identity better than dimensionality-matched control interventions.

### Intervention design

Where the architecture permits activation patching or subspace intervention:

1. identify a relation-associated interaction direction/subspace using training data only;
2. intervene at a frozen layer/site in a source example;
3. transplant or move the interaction component toward a target relation;
4. compare with random-subspace, marginal-component, norm-matched, and sham interventions.

### H3 primary outcomes

Report:

- target-relation switch rate;
- original factor/entity retention;
- non-target output degradation;
- intervention norm;
- effect relative to random and marginal controls.

H3 passes only if target-relation switching exceeds the strongest norm-matched control by at least **15 absolute percentage points**, with a bootstrap 95% confidence interval excluding zero, while factor/entity retention falls by no more than **5 points** relative to sham.

If intervention merely destroys the representation or changes all outputs indiscriminately, H3 fails.

### H3 null

The decoded interaction geometry is epiphenomenal: it is correlated with the relation but is not selectively used by the model to produce the relation-dependent output.

## H4 — independently calibrated cross-model stability

A relation-associated interaction geometry learned in one model has above-null correspondence with the independently trained transfer model after alignment calibrated without confirmatory joint interactions.

### Cross-model procedure

1. fit each model's allowed centering/whitening transform on calibration data;
2. fit the declared linear/orthogonal cross-model map using independent calibration states;
3. freeze the map;
4. transform held-out \(J_l\) or declared interaction summaries;
5. compare relation geometry without refitting on confirmatory interaction pairs.

Metrics may include:

- held-out Procrustes error under the frozen map;
- CKA/RSA;
- relation-neighborhood agreement;
- principal-angle agreement between relation subspaces;
- cross-model transfer of a relation decoder when dimensions permit.

H4 passes only if the primary predeclared correspondence metric improves by at least **20% relative** to both unaligned and shuffled-calibration controls, with a bootstrap 95% confidence interval excluding the control difference.

### H4 null

Any relation geometry is model-specific, or apparent cross-model agreement is produced by the alignment procedure rather than by independently corresponding interaction structure.

## H5 — synergy–geometry coupling

This gate is evaluated only if H1 and H2 pass.

Let \(Y\) be the externally defined relation target. Estimate an explicitly chosen PID/synergy quantity for the two controlled sources with respect to \(Y\). The estimator and PID definition must be frozen before confirmatory analysis; alternative PID definitions may be reported as sensitivity analyses, not substituted post hoc.

For each task condition or controlled difficulty bin, define three independently measured quantities:

\[
S=\text{information-theoretic synergy about }Y,
\]

\[
G=\text{predeclared interaction-geometry strength/structure},
\]

\[
C=\text{causal efficacy of the interaction intervention}.
\]

Test the predeclared associations \(S\leftrightarrow G\), \(G\leftrightarrow C\), and \(S\leftrightarrow C\).

A positive H5 requires the primary association to survive held-out conditions and declared multiple-comparison correction. Synergy by itself is not a positive result for this programme.

## Gate sequence and kill criteria

### Gate 0 — apparatus sanity

The extractor must recover the synthetic additive null and the XOR-style positive control in the expected directions. Failure means the apparatus is invalid; do not interpret model results.

### Gate 1 — interaction

Run H1.

**Kill:** if H1 fails in both predeclared task families, stop. Record the broad idea as framing only; do not proceed to causal or cross-model fishing.

### Gate 2 — generalization

Run H2.

**Kill:** if H2 fails, stop the strong claim. A train-set interaction signature is insufficient.

### Gate 3 — causality

Run H3.

If H1–H2 pass but H3 fails, the result may support a representational regularity but not a mechanism. Do not call the interaction component functionally constitutive.

### Gate 4 — cross-model stability

Run H4 only after a same-model causal signal exists.

If H1–H3 pass but H4 fails, classify the phenomenon as model/architecture-specific unless later evidence changes that conclusion.

### Gate 5 — synergy coupling

Run H5 after H1–H2. Its purpose is to connect the information-theoretic and representational objects, not to rescue failed geometry or causality gates.

## Anti-leakage rules

- No confirmatory pair may enter cross-model calibration.
- No relation label may be inferred from filenames or manifest ordering.
- Hyperparameters chosen after viewing `composition_test` results create a new protocol version and invalidate that split as confirmatory evidence.
- Layer/site selection must be nested inside training/validation or frozen from a pilot split that is never reused for confirmation.
- Any probe must be compared against a marginal-only probe of matched training budget.
- Any causal intervention must be norm-matched against control interventions.
- Prompt templates and answer-token positions must be balanced so lexical position alone cannot solve the task.

## Required artifacts for the first implementation PR

The implementation must add, without changing this protocol after seeing model outcomes:

- frozen model manifest with revisions;
- frozen dataset manifests and generation seed;
- task generator and leakage tests;
- interaction extractor with additive and XOR sanity tests;
- baseline suite;
- layer/site capture code;
- result schema that records every gate, including failures;
- one command for cheap synthetic tests that downloads no model weights;
- a separate explicit command for model-backed collection.

Model-backed artifacts should record package versions, seeds, hardware-relevant dtype/device settings, model revision, tokenizer revision, exact manifests, and wall-clock.

## Relationship to Semantic Atlas

No change to `semantic_atlas.md` is justified by this preregistration.

The current Semantic Atlas maps states, trajectories, reachability, transition dynamics, control costs, and semantic bridges. A bridge is a route such as

\[
A\rightarrow G_1\rightarrow G_2\rightarrow B.
\]

The object tested here is different: an interaction operator or interaction summary associated with coupling two controlled factors,

\[
(q_a,q_b)\mapsto J(q_a,q_b).
\]

Only if the experiment passes the relevant gates should the Atlas programme consider whether such operators deserve representation as additional atlas structure. Even then, the correct interpretation would be an atlas of state-dependent composition operators, **not** evidence that a transformer literally creates a new vector space whenever two semantic regions interact.

## Decision table

| Outcome | Interpretation | Action |
| --- | --- | --- |
| Gate 0 fails | invalid apparatus | fix apparatus; no scientific inference |
| H1 fails | no useful purified interaction geometry | stop; retain only conceptual framing |
| H1 passes, H2 fails | pairing/template regularity | stop strong claim |
| H1–H2 pass, H3 fails | generalizable representation, not causal mechanism | report narrowly if effect is robust |
| H1–H3 pass, H4 fails | causal model-specific interaction geometry | candidate standalone result, no universality claim |
| H1–H4 pass | causal, generalizable, cross-model interaction geometry | candidate hypothesis-level contribution |
| H5 also passes | evidence for synergy–geometry coupling | strongest result; literature re-audit before paper claim |

## Publication criterion

This programme starts at verdict **B — useful reframing**.

It may be promoted to **C — testable new hypothesis with positive evidence** only after H1, H2, and H3 pass. A cross-model claim additionally requires H4. A claim specifically linking synergy to geometry additionally requires H5.

A negative result is a successful outcome of the protocol if it cleanly eliminates the proposed stronger interpretation.