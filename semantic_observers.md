---
type: "Technical Paper"
title: "Semantic Observers: Decision-Theoretic Informativeness, Multiscale Measurement, and Parallax in Learned Representation Spaces"
description: "Revised position paper treating embedding models as task-relative observation channels, grounding observer comparison in Blackwell-Le Cam decision theory, and defining multiscale observability, apparent-topology errors, and alignment-capacity parallax as falsifiable measurement protocols."
tags: [semantic-observers, embeddings, representation-alignment, semantic-geometry, decision-theory, le-cam-deficiency, probing, topology, interpretability]
timestamp: 2026-08-26T01:10:00Z
---

# Semantic Observers: Decision-Theoretic Informativeness, Multiscale Measurement, and Parallax in Learned Representation Spaces

**Franklin Baldo**  
Independent Researcher  
franklinbaldo@gmail.com

---

> **Position paper and experimental programme, revised after adversarial review.** This manuscript proposes a measurement framework for comparing learned representations as observation channels. It does **not** claim that an observer-independent semantic universe has been established, that larger models uniformly see semantic structure more clearly, or that representational reconstructability is equivalent to informativeness. The central comparison is decision-theoretic: an observer is more informative only relative to a registered family of decision problems, and approximate bilateral comparison is grounded in Blackwell's comparison of experiments and Le Cam deficiency. The terms "observer," "resolution," "parallax," and "tomography" are operational metaphors whose value depends on surviving the falsification tests below.

## Abstract

Independently trained neural representations often share substantial structure. The Platonic Representation Hypothesis proposes convergence toward a common statistical model of reality; `vec2vec` demonstrates unpaired translation among text embedding spaces through a learned common latent representation; multi-view and multi-way methods recover shared coordinates across models and modalities. Recent null-calibrated work, however, weakens the strongest global-convergence reading: model width and depth can inflate common similarity statistics, while calibrated local neighborhood relations remain more robust than global geometry. This suggests a narrower question. Rather than identifying an embedding space with semantic reality, can embedding models be treated as **observation channels** whose usefulness, distortions, and blind spots can be measured locally, at multiple scales, and relative to explicit decision problems?

We revise the observer proposal around three constraints. First, **informativeness is not reconstruction error**. Mapping one embedding space into another can be easier in one direction merely because the target is lower-dimensional, smoother, or more anisotropic. We therefore ground observer comparison in Blackwell's decision order and Le Cam deficiency: observer \(A\) is at least as informative as observer \(B\), relative to a registered task family, when optimal risk under \(A\) is no worse across that family; bilateral deficiency measures approximate loss when one experiment is substituted for another. This comparison is invariant to invertible reparameterizations of the observed coordinates. Second, **resolution is a measurement suite, not a new latent quantity by fiat**. We define registered multiscale probes over neighborhoods, boundaries, bridges, manifolds, and topology, but require density-, dimension-, and estimator-matched nulls and explicitly connect the construction to the probing literature. Third, **observer disagreement is not automatically semantic parallax**. Residuals after alignment count only when their per-item content predicts within-observer behavior beyond model identity, item difficulty, and marginal covariates, and only when the effect survives a curve over alignment-model capacity.

The framework also separates three mechanisms that the telescope metaphor otherwise conflates: limited resolution, missing exposure, and objective-induced quotienting. A model may fail to distinguish two semantic states because its observations are noisy, because relevant distinctions were absent from training, or because its objective rewarded invariance to that distinction. These mechanisms are observationally confounded without interventions and must not be collapsed into a single notion of "seeing less." For topology, persistent-homology claims require bootstrap uncertainty and density-matched nulls because bridge loss and spurious components are default finite-sample phenomena in high dimensions.

The proposed contribution is therefore methodological rather than ontological: a preregistered protocol for asking which semantic distinctions are recoverable by which learned observers, at which scales, for which decision families, and whether multiple observers provide complementary information beyond the best single observer. The programme is rejected if the decision-theoretic ordering fails coordinate-invariance controls, if resolution profiles disappear under matched nulls, if parallax vanishes under richer non-destructive alignment, or if multi-observer fusion cannot beat strong single-observer baselines on externally specified held-out structure.

**Keywords:** representation geometry, semantic embeddings, Blackwell order, Le Cam deficiency, statistical experiments, probing, multiscale observability, representation alignment, semantic parallax, persistent homology, interpretability

---

## 1. From universal representation to comparison of observers

A growing literature asks whether independently trained models converge toward common representations. Huh et al. (2024) formulate the **Platonic Representation Hypothesis (PRH)**: sufficiently capable models, even across modalities, appear to converge toward a shared statistical structure of the world. Relative representations, Procrustes-style alignment, model stitching, representational similarity analysis, Gromov-Wasserstein methods, and related approaches had already shown that raw coordinate systems need not agree for learned representations to be meaningfully comparable.

The recent alignment literature raises the stakes. Jha et al. (2025/2026), in **Harnessing the Universal Geometry of Embeddings**, introduce `vec2vec`, which translates between independently trained text embedding spaces without paired samples or access to the source encoders by learning a shared latent representation. Yacobi et al. (2025) show that shared representations can be learned from largely unpaired data. Achara et al. (2026) address multi-way alignment, explicitly separating geometry-preserving and agreement-maximizing objectives.

These results make it increasingly difficult to claim novelty merely from the existence of common representational structure. But they do not establish that every model instantiates one globally identical semantic metric space.

Gröger, Wen, and Brbić (2026), **Revisiting the Platonic Representation Hypothesis: An Aristotelian View**, provide an important correction. Their ICML 2026 camera-ready paper shows that model width and depth can inflate common representational-similarity measures. They introduce permutation-based null calibration and report that the apparent scaling trend of global spectral similarity largely flattens after calibration, whereas **local neighborhood similarity, but not local distances, retains significant cross-modal agreement**. Their proposed Aristotelian Representation Hypothesis is correspondingly local: representations converge more robustly on neighborhood relationships than on one global statistical geometry.

This paper starts from that narrower empirical footing. It proposes that a learned representation be treated not as "the semantic universe" but as an **experiment** or **observation channel** over a set of task-relevant semantic states. The scientific questions are then:

1. Which registered decisions can be made from each observer's output, and at what risk?
2. Are two observers decision-theoretically equivalent, ordered, or incomparable?
3. Which structural predicates are recoverable locally and at multiple scales after matched null calibration?
4. When observers disagree, does the residual disagreement contain item-specific behavioral information, or merely model identity and alignment error?
5. Do multiple observers contain complementary information that improves held-out reconstruction or decision risk beyond the best single observer?

The observer metaphor earns its keep only if these questions produce reproducible asymmetries that cannot be reduced to coordinate choice, probe capacity, sample density, training exposure, or model identity.

---

## 2. Semantic states, stimuli, and observation channels

Let \(\Theta\) denote a finite or measurable set of **registered semantic states** relevant to an experiment. A state need not be an ontological atom of meaning. In controlled experiments it may be a scene graph, a compositional attribute tuple, a legal relation, a taxonomic position, a logical entailment state, or another externally specified variable.

A state \(\theta\in\Theta\) gives rise to stimuli

\[
x\sim P_X(\cdot\mid\theta),
\]

where different realizations may be paraphrases, images, code, or other surface forms that instantiate the same registered state.

An embedding model \(m\) maps the stimulus to an observed representation

\[
z_m=O_m(x)\in\mathcal Z_m.
\]

Marginalizing over realization variability induces a statistical experiment

\[
\mathcal E_m
=
\{P_m(\cdot\mid\theta):\theta\in\Theta\},
\]

where

\[
P_m(A\mid\theta)
=
\Pr[O_m(X)\in A\mid\theta].
\]

This construction is deliberately weaker than positing one true vector space. The common object is the **registered parameter/state family** and its decision problems, not a privileged coordinate system.

### 2.1 Deterministic embedding APIs are still statistical experiments

Many embedding APIs are deterministic conditional on a string. Stochasticity can nevertheless arise from the stimulus-generating distribution: paraphrases, controlled renderings, equivalent programs, image viewpoints, lexical realizations, or repeated contexts sampled from the same latent state. The experiment is over the distribution of observed embeddings induced by these realizations.

Where no meaningful realization distribution exists, the analysis must be stated as a finite deterministic benchmark rather than invoking full statistical-experiment semantics.

### 2.2 Observer quality is task-relative

The phrase "observer \(A\) is better than observer \(B\)" is incomplete until a decision family is specified. An encoder optimized for retrieval may intentionally collapse distinctions useful for syntax; a legal-domain model may preserve distinctions irrelevant to a generic semantic-similarity objective. There is no reason to expect a universal total order.

The natural object is therefore a family of comparisons indexed by registered decision problems and structural measurements.

---

## 3. Observer informativeness: Blackwell first, representation reconstruction second

### 3.1 Decision problems

A decision problem is a tuple

\[
d=(\mathcal A,\ell,\pi),
\]

where \(\mathcal A\) is an action space, \(\ell(\theta,a)\) is a loss, and \(\pi\) is a prior over semantic states when a Bayesian formulation is used.

Given experiment \(\mathcal E_m\), a decision rule \(q(a\mid z)\) maps the observed embedding to an action. Its Bayes risk is

\[
\mathcal R(\mathcal E_m,d)
=
\inf_q
\mathbb E_{\theta\sim\pi,\,z\sim P_m(\cdot\mid\theta),\,a\sim q(\cdot\mid z)}
[\ell(\theta,a)].
\]

For a preregistered family \(\mathcal D\) of semantic decisions, define **restricted decision dominance**

\[
\mathcal E_A\succeq_{\mathcal D}\mathcal E_B
\]

when

\[
\mathcal R(\mathcal E_A,d)
\le
\mathcal R(\mathcal E_B,d)
\qquad\forall d\in\mathcal D.
\]

If the inequalities cross across tasks, the observers are incomparable relative to \(\mathcal D\). This is a feature, not a defect: "sees more" and "sees something different" should not be forced into one scalar ranking.

### 3.2 Blackwell order

Blackwell's comparison of experiments gives the unrestricted ideal. Under the classical conditions, experiment \(A\) is at least as informative as experiment \(B\) for every decision problem if and only if \(B\) can be obtained by a stochastic **garbling** of \(A\).

Thus the semantic claim

> "A contains everything B reveals, plus possibly more"

should be grounded in decision risk or an equivalent comparison-of-experiments criterion, not in the difficulty of regressing one embedding vector onto another.

### 3.3 Le Cam deficiency

Exact Blackwell dominance is often too strong. Le Cam introduced a quantitative approximate comparison.

For experiments

\[
\mathcal E_A=\{P_A^\theta\}_{\theta\in\Theta},
\qquad
\mathcal E_B=\{P_B^\theta\}_{\theta\in\Theta},
\]

define the deficiency of \(A\) relative to \(B\) schematically as

\[
\delta(\mathcal E_A,\mathcal E_B)
=
\inf_K\sup_{\theta\in\Theta}
\left\|
K P_A^\theta-P_B^\theta
\right\|_{TV},
\]

where \(K\) ranges over Markov kernels from observations of \(A\) to simulated observations of \(B\). A small value means that \(A\) can simulate \(B\) with little loss. The bilateral pair

\[
\left(
\delta(\mathcal E_A,\mathcal E_B),
\delta(\mathcal E_B,\mathcal E_A)
\right)
\]

separates approximate dominance, approximate equivalence, and incomparability. The associated symmetric Le Cam distance uses the larger of the two deficiencies.

In finite empirical settings, directly estimating the full deficiency may be difficult. The paper therefore distinguishes two levels:

1. **decision-suite comparison**, estimated through held-out risks over a preregistered family \(\mathcal D\);
2. **channel deficiency**, estimated only when the induced experiments are sufficiently controlled for a defensible estimator.

The first must not be mislabeled as the second.

### 3.4 Why reconstruction asymmetry is not informativeness

A map

\[
g:\mathcal Z_A\to\mathcal Z_B
\]

can have lower prediction error than a reverse map

\[
h:\mathcal Z_B\to\mathcal Z_A
\]

for reasons unrelated to information: target dimension, entropy, anisotropy, smoothness, estimator class, regularization, or sample size. Reconstruction asymmetry is therefore only a diagnostic of representational compatibility.

It is **not** the primary observer-informativeness test.

### 3.5 Coordinate-invariance falsifier

The first required synthetic falsifier is an invertible reparameterization.

Let \(A\) be an experiment and define

\[
B'=\phi(A),
\]

where \(\phi\) is a known invertible nonlinear transformation chosen to alter geometry, anisotropy, marginal entropy, or regression difficulty while preserving all information.

Then \(A\) and \(B'\) are decision-theoretically equivalent. A valid observer-informativeness instrument must report no directional advantage except estimation error:

\[
\mathcal R(A,d)=\mathcal R(B',d)
\quad\forall d\in\mathcal D,
\]

and, in the controlled channel setting,

\[
\delta(A,B')\approx\delta(B',A)\approx0.
\]

If the instrument reports \(A\succ B'\) merely because one coordinate system is easier to regress into, the instrument has failed.

---

## 4. Resolution profiles are a measurement suite, not a new information theory

The observer programme also needs local and multiscale measurements. But the relevant prior art is substantial: supervised probing, control tasks, information-theoretic probing, Bayesian probing, and minimum-description-length probing all study what properties can be extracted from learned representations and how probe capacity or sample efficiency confounds interpretation.

Accordingly, the **resolution profile is best presented as a registered measurement protocol**, not as a fundamentally new theoretical object.

### 4.1 Registered structural tasks

Let \(\alpha\) index a preregistered structural predicate or loss, such as:

- local neighborhood membership;
- side of a known boundary;
- bridge membership or connectivity;
- compositional factor identity;
- monotonic position on a generated semantic path;
- local intrinsic dimension in a synthetic manifold;
- tangent orientation;
- persistence of a known topological feature;
- transition or reachability relation when dynamic data exist.

For each observer \(m\), a frozen estimator \(Q_{m,\alpha,s}\) is trained with the same data budget and protocol. Its held-out performance is calibrated against matched controls.

The resulting quantity

\[
R_m(u,s,\alpha)
\]

is therefore shorthand for **calibrated local recoverability** of structural task \(\alpha\) near location \(u\) at scale \(s\). It should not be interpreted as a directly observed physical resolution parameter.

### 4.2 Probe controls are mandatory

A structural probe can learn the task rather than reveal accessible structure in the representation. The protocol therefore inherits the discipline of Hewitt and Liang's control tasks, Pimentel et al.'s information-theoretic probing, and Voita and Titov's MDL probing.

At minimum, report:

- task accuracy or calibrated loss;
- a control task or label-permutation baseline;
- probe class and capacity;
- learning curves as a function of sample size;
- MDL or another sample-efficiency/extractability statistic when appropriate;
- matched random or synthetic representations;
- uncertainty across seeds and stimulus families.

A "resolution" gain that disappears when probe capacity or sample size is equalized is not evidence of observer resolution.

---

## 5. What is scale?

The symbol \(s\) is dangerous because embedding spaces do not share a canonical metric radius. Raw Euclidean radius is incomparable across models with different norm, anisotropy, density, and intrinsic dimension. A fixed \(k\) in k-nearest-neighbor graphs also renormalizes local density and can erase the very sparsity or crowding differences under study.

There is therefore **no single universal scale variable** in the framework. Scale must be operationalized per structural experiment.

### 5.1 Admissible scale parameterizations

Examples include:

1. **latent intervention scale** in controlled synthetic worlds: known perturbation magnitude in the generative state \(\Theta\);
2. **probability-mass scale**: neighborhoods containing a fixed estimated mass fraction rather than a raw metric radius;
3. **density-quantile scale**: observer-specific radii chosen by matched quantiles of local density;
4. **geodesic rank scale** when a ground-truth path metric exists;
5. **filtration quantile** for persistent-homology experiments, defined relative to a matched distance distribution rather than absolute radius;
6. **semantic granularity level** in generated taxonomies or hierarchical state spaces.

The paper should report exactly what \(s\) means for each predicate rather than pretending these scales are interchangeable.

### 5.2 Null-calibrated scale profiles

For every observed profile, construct null observers matched on properties that can mechanically affect the statistic:

- sample size;
- ambient dimension;
- estimated intrinsic dimension;
- marginal norm distribution;
- anisotropy spectrum;
- local density or graph degree distribution;
- model-layer search multiplicity where applicable.

The null is applied to the **final reported statistic**, following the logic of Gröger et al.'s calibration rather than only calibrating intermediate representations.

If scale-dependent observer differences disappear after dimension- and density-matched calibration, the resolution claim fails.

---

## 6. Resolution, exposure, and objective-induced quotienting are different mechanisms

The telescope metaphor is incomplete because learned representations are not passive sensors. They are produced by training objectives and data.

Suppose observer \(A\) distinguishes semantic states \(\theta_1\) and \(\theta_2\), while observer \(B\) collapses them. At least three mechanisms can explain the collapse:

1. **limited measurement resolution:** relevant variation reaches the model but is represented unreliably;
2. **missing exposure:** the training process did not contain enough information about the distinction;
3. **objective-induced quotienting:** the training objective rewarded invariance to the distinction, deliberately mapping both states into the same equivalence class.

These mechanisms are observationally confounded if only the final embedding API is available.

### 6.1 No causal attribution without interventions

From a frozen black-box embedding alone, one may report only the operational fact:

> the distinction is not recoverable under the registered measurement protocol.

One may **not** infer that the model "could not see" the distinction rather than never receiving it or intentionally discarding it.

### 6.2 Controlled exposure experiments

To separate exposure from representational capacity, train or obtain matched model families where corpus exposure is experimentally manipulated while architecture and objective are held fixed. Synthetic semantic micro-worlds are particularly useful because the relevant distinction can be inserted, withheld, or varied at known frequency.

If adding exposure restores the distinction without changing architecture or objective, the original failure is better described as coverage/exposure than resolution.

### 6.3 Controlled objective experiments

To test objective-induced quotienting, hold training data and architecture fixed while changing which distinctions the objective rewards. If a contrast disappears specifically under an invariance-inducing objective while decision performance on the intended task improves, the collapse is not a generic loss of quality. It is a task-relative sufficient-statistic or quotient effect.

This point limits the observer metaphor in a productive way:

> a learned observer is not merely a noisy telescope; it is an instrument whose optics were optimized for a task family.

Decision-theoretic comparison is therefore essential. An observer can be sufficient for one family of decisions while deliberately discarding information needed by another.

---

## 7. Apparent geometry and topology require statistical inference

A finite learned representation can make connected structures appear disconnected, merge distinct regions, or introduce apparent holes. But in high-dimensional sampled data, such effects are common even when the underlying topology is unchanged.

Therefore "bridge disappearance" is not interesting until compared with a strong null.

### 7.1 Bridge and connectivity tests

For generated data with known connectivity, register a bridge-recovery statistic before inspection. Compare the observer against null point clouds matched for:

- sample count;
- intrinsic dimension;
- local density profile;
- anisotropy;
- graph degree distribution;
- cluster imbalance.

A bridge-loss claim requires excess failure beyond these matched finite-sample effects.

### 7.2 Persistent homology

Persistent homology provides multiscale summaries, but persistence diagrams are random objects under finite sampling. Prior statistical work derives confidence sets for persistence diagrams and bootstrap confidence bands for persistence landscapes.

Accordingly, topological claims require:

- a preregistered filtration and distance normalization;
- bootstrap confidence sets or bands;
- matched synthetic nulls with the same sample size and density structure;
- sensitivity analysis across admissible filtration scales;
- replication on new stimulus sets;
- no post-hoc selection of the most favorable homology dimension or layer.

A feature that does not clear its uncertainty band is topological noise, not observer-specific semantic structure.

---

## 8. Semantic parallax as conditional, item-level residual information

Alignment produces another tempting overclaim. Let \(T_m\) map observer \(m\)'s representation into a common comparison space. Define a consensus representation

\[
\bar z(x)=\operatorname{Agg}_m T_m(O_m(x))
\]

and residual

\[
\delta_m(x)=T_m(O_m(x))-\bar z(x).
\]

A nonzero residual is guaranteed whenever alignment is imperfect. It is **not** by itself semantic parallax.

### 8.1 The hard parallax criterion

Let \(Y_{mi}\) denote an item-level behavioral outcome for observer \(m\) on held-out item \(i\): correctness, calibrated loss, retrieval success, ranking error, sensitivity to a controlled contrast, or another preregistered quantity.

Let \(B_{mi}\) be a baseline nuisance model containing at least:

- observer identity;
- item identity or independently estimated item difficulty;
- observer-level capability summaries;
- norm, anisotropy, sequence length, and other marginal embedding statistics;
- domain/source metadata;
- tokenizer or modality indicators where relevant.

A residual counts as semantic parallax only if item-specific features of \(\delta_m(x_i)\) improve prediction of \(Y_{mi}\) beyond \(B_{mi}\) on untouched data:

\[
\operatorname{Risk}(B+\delta)
<
\operatorname{Risk}(B),
\]

with uncertainty excluding zero improvement under the preregistered analysis.

This is a **within-observer, per-item** claim. Predicting model identity is insufficient.

### 8.2 Alignment-capacity curve

Parallax is a function of the alignment class. A rigid orthogonal map leaves larger residuals than a flexible nonlinear map. Therefore report a capacity curve

\[
\mathcal P(c)
=
\text{incremental held-out value of residuals after alignment class }\mathcal T_c,
\]

for a registered sequence such as:

\[
\text{orthogonal}
\rightarrow
\text{linear}
\rightarrow
\text{shallow MLP}
\rightarrow
\text{more flexible nonlinear map}.
\]

The scientific claim is the component that survives increasing **non-destructive** alignment capacity. If residual predictive value smoothly vanishes as alignment improves, the parsimonious interpretation is alignment error, not parallax.

### 8.3 Alignment must not erase the target by construction

A highly flexible aligner trained directly on the behavioral target can trivially remove useful residuals. Alignment is therefore fitted only on representation correspondence objectives and frozen before behavioral evaluation. The capacity curve measures robustness to coordinate matching, not supervised deletion of the phenomenon under test.

---

## 9. Multi-observer reconstruction: complementarity, not consensus

Multi-view learning and nonlinear-ICA theory already establish that multiple noisy views can, under assumptions, identify latent factors unavailable from a single view. Thus "several observers can reconstruct a latent source" is not a novelty claim.

The narrower test here is whether **independently trained embedding observers** provide complementary decision-relevant information after strong baselines.

For a task family \(\mathcal D\), compare:

- the best single observer chosen only on training/validation data;
- a parameter-matched ensemble of same-family observers;
- equal-weight aligned averaging;
- GPA/GCPA or another multi-way common frame;
- `vec2vec` or another shared-latent baseline where applicable;
- observer-aware fusion using only training-estimated reliability and parallax features.

The multi-observer claim passes only if fusion improves held-out decision risk or recovery of externally specified structure beyond the best single observer, with confidence intervals excluding zero.

Consensus is never treated as ground truth. Correlated observers can share the same error.

---

## 10. Prior art and novelty boundary

### 10.1 Representation convergence and alignment

The PRH, representational similarity analysis, CKA/SVCCA, relative representations, Procrustes alignment, model stitching, Gromov-Wasserstein alignment, `vec2vec`, shared unpaired representations, and multi-way alignment already occupy the terrain of cross-model correspondence.

**Not claimed:** discovering common structure, inventing coordinate alignment, or proving a universal semantic vector space.

### 10.2 Local calibrated convergence

Gröger, Wen, and Brbić (2026) are particularly close prior art. Their primary-source abstract and project materials explicitly report width/depth confounds in representational similarity, permutation-based null calibration, flattening of global spectral convergence after calibration, and persistence of local neighborhood agreement.

**Not claimed:** discovering that local neighborhoods can be more stable than global geometry.

### 10.3 Probing and extractability

Hewitt and Liang (2019) show why probe accuracy must be contextualized by control tasks and selectivity. Pimentel et al. (2020) frame probing information-theoretically, while Voita and Titov (2020) use minimum description length to measure how efficiently labels can be extracted from representations. Later Bayesian probing work emphasizes finite-data agents and extractability.

**Not claimed:** inventing local probing accuracy, extractability, or sample-efficiency measurement.

The proposed **resolution profile** is a protocol that sweeps preregistered structural tasks over controlled scales with matched null calibration. Its contribution, if any, is methodological synthesis and experimental discipline.

### 10.4 Blackwell and Le Cam

Blackwell's 1951 and 1953 comparison-of-experiments results formalize when one information structure is at least as useful as another across decision problems. Le Cam's theory of deficiency quantifies approximate loss between statistical experiments; Torgersen's monograph develops the relationship among risks, deficiency, sufficiency, randomization, and comparison.

**Not claimed:** a new information order or new concept of approximate dominance.

The observer programme applies this established machinery to learned semantic representations and makes the decision family explicit.

### 10.5 Multi-view latent recovery

Multi-view learning and nonlinear-ICA identifiability, including the Incomplete Rosetta Stone line of work, already show how multiple views can help identify latent structure.

**Not claimed:** generic latent identifiability from multiple views.

### 10.6 Topological inference

Persistent homology, confidence sets for persistence diagrams, bootstrap inference for persistence landscapes, and topological analysis of neural representations are established literatures.

**Not claimed:** inventing topological analysis of embeddings.

### 10.7 Candidate contribution after these concessions

The remaining contribution is deliberately narrow:

1. cast embedding models as **task-relative statistical experiments** rather than as candidate copies of one semantic coordinate space;
2. compare informativeness through **registered decision risk and, where estimable, bilateral Le Cam deficiency**, not representation reconstruction error;
3. operationalize "semantic resolution" as a **multiscale, null-calibrated probing suite** over registered structural predicates;
4. explicitly separate **resolution, exposure, and objective-induced quotienting**;
5. require topology claims to survive bootstrap uncertainty and density/dimension-matched nulls;
6. define parallax through **incremental per-item behavioral prediction** and an **alignment-capacity curve**;
7. test multi-observer complementarity against the best single observer and modern shared-space baselines.

The paper should be rejected as an originality claim if prior work is found that already combines this same decision-theoretic comparison, multiscale registered measurement, causal mechanism separation, and residual-capacity analysis for learned semantic observers.

---

## 11. Experimental programme

The experiments are staged so that stronger claims cannot survive failed prerequisites.

### Stage 0A — Reparameterization invariance

Construct a known experiment \(A\) and an invertibly transformed version \(B'=\phi(A)\) with deliberately different dimension-conditioned smoothness, anisotropy, or regression difficulty.

Required result:

- decision risks indistinguishable within uncertainty;
- bilateral deficiency approximately symmetric and near zero when directly estimable;
- any representation-reconstruction asymmetry explicitly ignored as evidence of informativeness.

**Failure interpretation:** the instrument measures coordinate convenience rather than information.

### Stage 0B — Dimension- and density-matched nulls

Construct observer pairs with no planted semantic resolution difference but matched or manipulated:

- ambient dimension;
- intrinsic dimension;
- anisotropy;
- density;
- sample size;
- graph degree distribution.

Run the complete multiscale profile pipeline.

**Required result:** calibrated resolution differences remain at nominal false-positive rates.

**Failure interpretation:** the profile is a geometric nuisance detector.

### Stage 0C — Known coarse-graining and incomparability

Construct three synthetic experiments:

1. \(B\) is a known stochastic garbling of \(A\);
2. \(A\) and \(C\) preserve complementary independent factors;
3. \(D\) is invertibly equivalent to \(A\).

The decision suite must recover:

\[
A\succeq B,
\]

incomparability of \(A\) and \(C\) for a task family spanning both factors, and equivalence of \(A\) and \(D\).

### Stage 1 — Controlled semantic micro-worlds

Generate latent semantic states with known factors and relations, then multiple surface realizations per state. Candidate worlds include:

- scene graphs;
- compositional attribute tuples;
- taxonomies;
- small logical worlds;
- programmatically generated legal-rule scenarios;
- code semantics with controlled refactorings.

Freeze train/validation/test splits before embedding.

### Stage 2 — Exposure versus objective interventions

Where training is feasible, construct matched encoder families:

- same architecture/objective, controlled inclusion or exclusion of a semantic distinction;
- same architecture/data, objectives that either preserve or encourage invariance to the distinction.

Measure whether non-recoverability follows exposure or objective manipulation.

**Failure interpretation:** if mechanisms cannot be separated, later claims remain operational only and must not receive optical causal language.

### Stage 3 — Multiscale registered measurement

For each structural family \(\alpha\), register the meaning of scale \(s\), probe class, sample budget, and matched null. Estimate

\[
R_m(u,s,\alpha)
\]

with uncertainty.

Primary question:

> Do observer differences survive probe-capacity, density, intrinsic-dimension, and scale calibration?

### Stage 4 — Decision comparison and deficiency

Register a task suite \(\mathcal D\) that spans the semantic distinctions of interest. Estimate held-out Bayes-risk proxies with probe families sufficiently expressive to approximate the relevant decisions, alongside sample-efficiency diagnostics.

Report the matrix

\[
\Delta R_{A,B}(d)
=
\mathcal R(A,d)-\mathcal R(B,d)
\]

for every registered task rather than collapsing immediately to one score.

Where controlled distributions make it feasible, estimate bilateral deficiency or validated bounds on it.

### Stage 5 — Apparent topology

Use only datasets with externally known or independently justified topology/connectivity for confirmatory claims. Apply:

- matched density/dimension nulls;
- preregistered filtrations;
- bootstrap confidence sets/bands;
- independent stimulus replication.

Bridge or component loss counts only when it exceeds finite-sample null behavior.

### Stage 6 — Alignment-capacity parallax

Fit common frames under a frozen ladder of alignment capacities. For each capacity, compute held-out residuals and test incremental item-level prediction of observer behavior beyond nuisance baselines.

The output is a curve

\[
\mathcal P(c),
\]

not one favored residual statistic.

### Stage 7 — Multi-observer complementarity

Fuse observers using only training-estimated quantities. Evaluate against best-single and shared-space baselines on untouched test data.

The claim survives only if complementary observers reduce decision risk or structural error beyond all preregistered baselines.

---

## 12. Revised hypotheses

### H1 — Calibrated local commonality

**Hypothesis.** Competent independently trained observers share non-trivial local neighborhood relations above width-, depth-, density-, and dimension-matched nulls.

**Status.** Close prior art; foundation rather than claimed novelty.

**Falsified if.** Agreement disappears under final-statistic calibration or independent-corpus replication.

### H2 — Multiscale recoverability differentiation

**Hypothesis.** Registered structural-task profiles differ reproducibly among observers after controlling probe capacity, sample size, intrinsic dimension, density, anisotropy, and model-size confounds.

**Falsified if.** Profiles collapse under matched nulls or are unstable across resamples and corpora.

### H3 — Decision-theoretic refinement

**Hypothesis.** For at least some controlled observer families and task suites, higher-capability observers weakly dominate lower-capability observers in registered decision risk and show lower deficiency in the high-to-low direction than the reverse.

**Falsified if.** The ordering is driven by coordinate parameterization, disappears on the invertible-transform control, or risk curves cross systematically rather than show refinement.

A crossed risk profile is interpreted as **incomparability**, not a failed attempt to force a ranking.

### H4 — Mechanism-sensitive non-recoverability

**Hypothesis.** Controlled exposure and objective interventions can distinguish at least some cases of missing semantic information from objective-induced invariance.

**Falsified if.** The proposed interventions do not change recoverability in the predicted directions or cannot separate mechanisms.

### H5 — Statistically non-trivial apparent topology

**Hypothesis.** Some observer-specific bridge, connectivity, or persistence errors exceed density/dimension-matched finite-sample nulls and covary with independently measured recoverability.

**Falsified if.** Effects lie inside bootstrap uncertainty or are reproduced by matched null point clouds.

### H6 — Alignment-robust semantic parallax

**Hypothesis.** Observer residuals contain item-specific information that predicts within-observer behavior beyond identity and nuisance covariates, and a non-zero component survives increasing non-destructive alignment capacity.

**Falsified if.** Prediction is explained by observer identity, marginal statistics, or item difficulty, or if the effect vanishes under a richer correspondence-preserving aligner.

### H7 — Multi-observer complementarity

**Hypothesis.** Heterogeneous observers contain complementary decision-relevant information such that preregistered fusion outperforms the best single observer and modern shared-space baselines on untouched data.

**Falsified if.** Gains vanish against the best-single baseline, same-family ensemble controls, or independent test sets.

---

## 13. Implications for related programmes

### 13.1 Semantic Atlas

A Semantic Atlas need not assume one embedding observer supplies the map. The revised observer framework suggests attaching **task-relative measurement uncertainty** to atlas regions and distinguishing common neighborhood structure from observer-specific dynamics.

The decision-theoretic correction is important: an observer that preserves a region's geometry is not necessarily more useful for navigation unless the relevant route decisions can be made with lower risk.

### 13.2 Pontifex

Pontifex's multi-space comparison can be reframed around consensus and residual information without assuming alignment is impossible. The observer framework suggests a stricter test: does residual response to an occlusion predict **which items a given observer changes behavior on**, beyond observer identity, and does that effect survive increasing alignment capacity?

This turns "multi-space disagreement" into a falsifiable item-level question.

### 13.3 Perquire and adaptive observer selection

A search or navigation system could eventually choose observers by task-relative decision value rather than by a global model leaderboard. A cheap observer may suffice for coarse decisions while a specialized observer is invoked near a registered ambiguity.

This is an engineering implication, not evidence for the scientific framework.

---

## 14. Limitations

### 14.1 The latent semantic state is experimenter-defined

The framework avoids positing one true vector space, but it still requires registered semantic states and decision problems. In synthetic worlds these are explicit; in natural language they are contestable. Conclusions therefore inherit the validity of the benchmark ontology.

### 14.2 Restricted decision families give restricted orders

Empirical experiments cannot quantify performance over every conceivable decision problem. A result

\[
A\succeq_{\mathcal D}B
\]

means dominance only for the registered family \(\mathcal D\), not universal Blackwell dominance.

### 14.3 Deficiency estimation can be difficult

Full Le Cam deficiency is a theoretical object over experiments, not a free empirical statistic. In high-dimensional continuous embeddings, estimation may be impractical without controlled generative models. When only downstream risks are measured, the paper must say so explicitly.

### 14.4 Training histories are usually unavailable

For proprietary or pretrained black-box embeddings, exposure and objective effects cannot be causally separated. The optical metaphor must remain operational in those settings.

### 14.5 Alignment capacity has no unique endpoint

A sufficiently flexible aligner can memorize finite correspondences. The parallax curve therefore needs held-out correspondence tests and complexity control; there is no magic "perfect alignment" class.

### 14.6 Topology is sample hungry

High-dimensional topological inference is fragile. Negative results may reflect insufficient power; positive results require severe correction for sampling and model selection.

---

## 15. Conclusion

The most defensible version of the semantic-observer idea is not that larger embedding models are telescopes of increasing aperture pointed at one already-given semantic universe. Learned representations are task-shaped experiments. They can be noisy, underexposed, intentionally invariant, or genuinely complementary.

The comparison should therefore begin with decisions:

\[
\boxed{
\text{Which observer permits which decisions, at what risk?}
}
\]

Blackwell's order and Le Cam deficiency supply the right conceptual language for refinement and approximate equivalence. Multiscale structural probes then describe **where and how** the relevant information is accessible, provided they survive probe-capacity, density, intrinsic-dimension, and null calibration. Apparent topology requires statistical inference. Residual disagreement becomes semantic parallax only when it predicts item-level behavior beyond identity and survives increasing alignment capacity.

Under this revised framework, "better observer" is not a synonym for larger model, lower reconstruction error, or prettier geometry. It is a task-relative statement about decision-relevant information.

That narrower claim is also more testable. An invertible coordinate change must not alter informativeness. Missing exposure must not be mislabeled as poor resolution. Objective-induced invariance must be allowed to count as useful compression rather than blindness. Parallax must survive strong nuisance and alignment controls. Multi-observer fusion must beat the best single observer.

If those tests fail, the observer metaphor should be retired. If they survive, learned representation spaces can be studied as a population of partially ordered, partially complementary semantic experiments rather than as competing claims to one privileged coordinate system.

---

## References

Achara, N., et al. (2026). **Multi-Way Representation Alignment.** arXiv:2602.06205.

Blackwell, D. (1951). **Comparison of Experiments.** *Proceedings of the Second Berkeley Symposium on Mathematical Statistics and Probability*, 93–102.

Blackwell, D. (1953). **Equivalent Comparisons of Experiments.** *The Annals of Mathematical Statistics*, 24(2), 265–272. https://doi.org/10.1214/aoms/1177729032

Chazal, F., Fasy, B. T., Lecci, F., Rinaldo, A., Singh, A., & Wasserman, L. (2014). **On the Bootstrap for Persistence Diagrams and Landscapes.** arXiv:1311.0376.

Fasy, B. T., Lecci, F., Rinaldo, A., Wasserman, L., Balakrishnan, S., & Singh, A. (2014). **Confidence Sets for Persistence Diagrams.** *The Annals of Statistics*, 42(6), 2301–2339. https://doi.org/10.1214/14-AOS1252

Gresele, L., et al. (2020). **The Incomplete Rosetta Stone Problem: Identifiability Results for Multi-View Nonlinear ICA.** *UAI 2020 / PMLR 115*.

Gröger, F., Wen, S., & Brbić, M. (2026). **Revisiting the Platonic Representation Hypothesis: An Aristotelian View.** ICML 2026; arXiv:2602.14486.

Hewitt, J., & Liang, P. (2019). **Designing and Interpreting Probes with Control Tasks.** *EMNLP-IJCNLP 2019*, 2733–2743. https://doi.org/10.18653/v1/D19-1275

Huh, M., Cheung, B., Wang, T., & Isola, P. (2024). **The Platonic Representation Hypothesis.** *ICML 2024 / PMLR 235*.

Jha, A., Zhang, Y., Shmatikov, V., & Morris, J. X. (2025/2026). **Harnessing the Universal Geometry of Embeddings.** arXiv:2505.12540; NeurIPS 2025.

Le Cam, L. (1964). **Sufficiency and Approximate Sufficiency.** *The Annals of Mathematical Statistics*, 35(4), 1419–1455.

Le Cam, L. (1986). **Asymptotic Methods in Statistical Decision Theory.** Springer.

Pimentel, T., Valvoda, J., Maudslay, R. H., Zmigrod, R., Williams, A., & Cotterell, R. (2020). **Information-Theoretic Probing for Linguistic Structure.** arXiv:2004.03061.

Pimentel, T., & Cotterell, R. (2021). **A Bayesian Framework for Information-Theoretic Probing.** *EMNLP 2021*.

Raginsky, M. (2011). **Shannon Meets Blackwell and Le Cam: Channels, Codes, and Statistical Experiments.** *IEEE ISIT 2011*, 1220–1224. https://doi.org/10.1109/ISIT.2011.6033729

Torgersen, E. (1991). **Comparison of Statistical Experiments.** Cambridge University Press.

Voita, E., & Titov, I. (2020). **Information-Theoretic Probing with Minimum Description Length.** arXiv:2003.12298.

Yacobi, et al. (2025). **Learning Shared Representations from Unpaired Data.** arXiv:2505.21524; NeurIPS 2025.
