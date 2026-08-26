---
type: "Technical Paper"
title: "Semantic Observers: Multiscale Observability, Resolution, and Parallax in Learned Representation Spaces"
description: "Position paper proposing that embedding models be treated as partially informative observers of a latent semantic relational structure, with local multiscale resolution profiles, observer-specific parallax, partial informativeness orders, and multi-observer reconstruction as falsifiable objects of study."
tags: [semantic-observers, embeddings, representation-alignment, semantic-geometry, multi-view-learning, information-theory, topology, interpretability]
timestamp: 2026-08-25T23:30:00Z
---

# Semantic Observers: Multiscale Observability, Resolution, and Parallax in Learned Representation Spaces

**Franklin Baldo**  
Independent Researcher  
franklinbaldo@gmail.com

---

> **Position paper and experimental programme.** This manuscript proposes a way to organize and test a family of hypotheses about learned representations. It does **not** claim that an observer-independent semantic universe has been established, that larger models are uniformly better semantic observers, or that agreement among models is equivalent to truth. The language of "universe," "observer," "resolution," and "parallax" is operational: each term is tied below to measurable quantities and explicit failure conditions. Unless a section is marked as reporting prior published evidence, the claims are hypotheses and proposed experiments rather than empirical results.

## Abstract

Recent work has produced striking evidence that independently trained neural networks can share substantial representational structure. The Platonic Representation Hypothesis proposes convergence toward a common statistical model of reality; `vec2vec` demonstrates unpaired translation between text embedding spaces through a learned universal latent representation; shared representations can be recovered from largely unpaired multimodal data; and multi-way alignment can place several models in one common reference. At the same time, recent null-calibrated analyses substantially weaken the strongest global-convergence story: global spectral similarity can be confounded by model scale, while shared **local neighborhood relations** survive more robustly. These results suggest a different question. Instead of asking whether each embedding space *is* the semantic world, what if each model is treated as an **observer** that measures some partially shared semantic structure with its own resolution, distortion, noise, domain sensitivity, and blind spots?

We formalize this perspective without assuming that the latent structure is globally Euclidean. A semantic substrate \(\mathcal U\) is an unknown relational object; an observer \(O_m\) maps states of that substrate into a model-specific representation \(\mathcal Z_m\). The primary scientific object is not a scalar ranking of models but a **multiscale observer-resolution profile** describing which registered structural predicates—neighborhoods, boundaries, local tangent structure, paths, connected components, or other features—are recoverable at a location and scale. We define semantic resolution, approximate observer dominance using Blackwell-style informativeness, observer-specific residuals called **semantic parallax**, and multi-observer reconstruction. The framework predicts that apparent semantic topology can differ across observers: a weak observer may merge distinct regions, split a continuous region, or erase a narrow bridge without the underlying relation itself changing.

The proposal is intentionally narrower than a new universal-representation claim. Multi-view learning, nonlinear-ICA identifiability, representational similarity analysis, alignment, model stitching, manifold alignment, and topological analysis are extensive prior art. The proposed contribution is to combine these ingredients into a falsification-driven theory of **observer-dependent semantic observability** and to test a specific progression: which structural properties become reliably visible, where, and at what scale as observer informativeness changes? We specify null-calibrated experiments that separate local agreement from global geometry, capability from model size, consensus from ground truth, and representation similarity from recoverability of structure. If resolution profiles are unstable, if stronger task performance does not predict any systematic increase in registered observability, or if multi-observer fusion fails to recover structure better than matched single observers, the stronger observer interpretation should be rejected.

**Keywords:** representation geometry, semantic embeddings, representational alignment, Platonic Representation Hypothesis, multi-view learning, semantic resolution, observer models, Blackwell order, manifolds, topology, interpretability

---

## 1. The question after universal alignment

A growing literature asks whether independently trained models converge toward common representations. This question has moved quickly from qualitative similarity to constructive interoperability.

Huh et al. (2024) formulated the **Platonic Representation Hypothesis (PRH)**: sufficiently capable models, even across modalities, appear to converge toward a shared statistical structure of the world. Subsequent work has shown substantial alignment between independently trained vision and language encoders, with alignment quality related to properties such as clustering quality and language-understanding performance. Relative representations showed earlier that similarities to anchors can enable communication across incoherent latent coordinate systems. Procrustes-style mappings, model stitching, manifold alignment, and other techniques likewise demonstrate that raw coordinates need not match for representations to be functionally or geometrically related.

The strongest recent constructive result for text embeddings is Jha et al. (2025/2026), **Harnessing the Universal Geometry of Embeddings**. Their `vec2vec` method learns to translate embeddings between independently trained text encoders without paired samples, access to the source encoders, or predefined matches, using a learned universal latent representation. Yacobi et al. (2025) independently showed that shared multimodal representations can be learned almost entirely from unpaired data using spectral structure. Achara et al. (2026) then addressed the \(M\geq3\) case, constructing a shared multi-model universe with Generalized Procrustes Analysis and Geometry-Corrected Procrustes Alignment.

If these results are taken at face value, a natural temptation is to say that the semantic universe has been found and that each model merely uses different coordinates. That conclusion is too strong.

Gröger, Wen, and Brbić (2026) revisited PRH with permutation-based null calibration and showed that network width and depth can inflate common representational-similarity statistics. After calibration, much of the apparent **global** convergence disappears, while **local neighborhood agreement** remains robust. Their resulting Aristotelian Representation Hypothesis is deliberately local: models converge on "who is near whom" more reliably than on one globally shared metric geometry. Hosseini et al. (2026) further show that cross-model convergence is stimulus dependent: stimuli on which vision models agree internally also align more strongly across vision and language.

These findings suggest a reformulation:

> An embedding model need not be identified with semantic space. It can instead be treated as an **observation channel** of a partially shared semantic structure.

The central questions then become:

1. Which properties of semantic structure are invariant across observers?
2. Which properties are visible only to some observers?
3. Does observability improve systematically with task-relevant capability, and at what locations and scales?
4. Can disagreements among observers reveal structure that consensus alone hides?
5. Can several imperfect observers jointly reconstruct a better approximation of the latent structure than any one observer alone?

The proposal in this paper is to make those questions measurable.

---

## 2. Do not assume a Euclidean semantic universe

Let \(\mathcal X\) denote a set of semantic stimuli: texts, images, code fragments, multimodal records, or controlled latent states. We posit an unknown semantic substrate

\[
\mathcal U=(\mathcal X,\mathcal R),
\]

where \(\mathcal R\) is a family of relations or structural observables over \(\mathcal X\). Examples include neighborhood relations, partial orderings, equivalence classes, transition relations, boundaries, local dimensionality, or other task-relevant structure.

The notation \(\mathcal U\) is intentionally weaker than "a true vector space." Nothing here requires a single global Euclidean metric, a unique manifold, or even one topology at all semantic scales. The empirical evidence may support only local relational invariants. The substrate is therefore best understood initially as a **latent relational structure**.

An embedding model \(m\) is an observer

\[
O_m:\mathcal X\rightarrow\mathcal Z_m,
\qquad
\mathcal Z_m\subseteq\mathbb R^{d_m},
\]

or, more generally, a stochastic channel

\[
O_m(z\mid x).
\]

The observed embedding \(z_m=O_m(x)\) is a measurement produced by one observer. Different observers can have different dimensions, metrics, training data, objectives, architectures, modalities, and inductive biases.

This distinction is load-bearing:

\[
\text{semantic substrate}\neq\text{one model's coordinate system}.
\]

Alignment methods attempt to infer correspondences among the \(\mathcal Z_m\). The present proposal instead asks what those correspondences tell us about the **observability of structure in \(\mathcal U\)**.

### 2.1 The observer metaphor must earn its keep

Calling a model an observer is useful only if it yields predictions beyond "representations differ." In this paper an observer has four operational properties:

- **resolution:** which registered structures it can recover at which scales;
- **distortion:** which relations it systematically warps, merges, or splits;
- **uncertainty:** how stable those observations are under sampling, paraphrase, corpus, and alignment perturbations;
- **parallax:** the structured residual that remains when observers are placed into a common comparison frame.

If these quantities cannot be measured reproducibly, the metaphor should be discarded.

---

## 3. From model quality to observer resolution

The phrase "a better model sees the space more clearly" is intuitive and scientifically dangerous. Model size, benchmark score, embedding dimension, and representational similarity are not interchangeable. In particular, Gröger et al. show that width and depth themselves can confound similarity metrics.

We therefore replace a total ranking of observers with a local, multiscale profile.

### 3.1 Registered structural predicates

Let

\[
P_\alpha(u,s)\in\{0,1\}
\]

be a registered structural predicate about semantic location or stimulus \(u\), evaluated at scale \(s\). Examples include:

- whether two items are mutual neighbors at scale \(k\);
- whether a point lies on opposite sides of a known semantic boundary;
- whether a local support is approximately one-dimensional or two-dimensional;
- whether two tangent directions belong to the same local manifold;
- whether a narrow bridge connects two regions;
- whether a loop or connected component persists across a filtration interval;
- whether an ordered semantic path preserves a known monotonic relation.

The predicate must be defined **before** examining the observer under test. Otherwise "resolution" collapses into post-hoc storytelling.

For observer \(m\), let \(\widehat P_{m,\alpha}(u,s)\) be the corresponding estimate obtained from its representation using a frozen estimator and matched data budget.

### 3.2 Resolution profile

Define the observer's resolution for predicate \(\alpha\) as

\[
R_m(u,s,\alpha)
=
\Pr\left[
\widehat P_{m,\alpha}(u,s)=P_\alpha(u,s)
\right],
\]

where the probability is estimated over held-out stimuli, bootstrap resamples, paraphrase families, random seeds, or other preregistered perturbations appropriate to the experiment.

For continuous observables, replace exact equality by a calibrated loss:

\[
R_m(u,s,\alpha)
=
1-\widetilde L_\alpha\!\left(
\widehat P_{m,\alpha}(u,s),
P_\alpha(u,s)
\right),
\]

with \(\widetilde L\) normalized against a permutation or matched null.

A model's **observer fingerprint** is the collection

\[
\mathbf R_m
=
\{R_m(u,s,\alpha)\}_{u,s,\alpha}.
\]

This is not expected to collapse to one number.

### 3.3 Resolution threshold

For a target reliability \(\tau\), define the smallest scale at which a feature becomes reliably visible:

\[
s_m^*(u,\alpha;\tau)
=
\inf\{s:R_m(u,s,\alpha)\geq\tau\}.
\]

When smaller \(s\) corresponds to finer structure, lower \(s_m^*\) means finer semantic resolution for that predicate and location.

The telescope analogy becomes precise only here: an observer with finer resolution can reliably distinguish structure at a smaller scale. It does **not** follow that the same observer dominates everywhere.

### 3.4 Resolution is local and task dependent

For two observers \(A\) and \(B\), it may be true that

\[
R_A(u_{law},s,\alpha)>R_B(u_{law},s,\alpha)
\]

while

\[
R_A(u_{chem},s,\alpha)<R_B(u_{chem},s,\alpha).
\]

Likewise, one observer may preserve macro-neighborhoods while another better preserves local curvature. This makes a **partial order** more plausible than one universal leaderboard.

---

## 4. Apparent topology and semantic coarse-graining

The observer view predicts something stronger than varying noise levels: observers can induce qualitatively different **apparent structure**.

Suppose \(A\) and \(B\) are two semantic regions connected by a narrow bridge. An observer with insufficient local resolution may map the bridge below its discriminability threshold, making the regions appear disconnected. Conversely, heavy smoothing may merge two genuinely distinct regions. A distorted observer can also introduce an apparent boundary into a continuous latent relation.

Thus:

\[
\text{latent relational structure}
\longrightarrow
\text{observer-dependent apparent geometry/topology}.
\]

This is not a claim that topology is subjective. It is a claim about **measurement**: finite, noisy, learned representation channels need not preserve every structural invariant of the source.

### 4.1 A hierarchy of structural observables

A useful first experimental hierarchy is:

1. **point discriminability** — can distinct states be separated at all?
2. **local neighborhood** — does the observer preserve who is near whom?
3. **boundaries and bridges** — are discontinuities or weak connections recoverable?
4. **local tangent and curvature** — does the observer preserve the shape of continuous variation?
5. **manifold organization** — can coherent low-dimensional concept structure be recovered?
6. **topological features** — are connected components, loops, or other persistent structures stable?
7. **dynamics** — if trajectories are available, are transitions and reachability relations preserved?

The ordering is a research convenience, not a theorem. A model may preserve a higher-order property while failing a lower-order estimator, and different metrics may disagree. The value of the hierarchy is that it converts phrases such as "edges, curves, and objects become clearer" into registered measurements.

### 4.2 Relation to concept manifolds

Recent work makes the manifold level particularly plausible. Block-Sparse Featurizers recover low-dimensional multidimensional visual concept structures rather than isolated directions, and recent language-model work studies trajectories and control on concept manifolds. These findings do not prove an observer-independent manifold. They show that **manifold-valued observables are scientifically legitimate candidates** for the resolution profile.

### 4.3 Topology requires severe caution

Persistent homology and related topological methods can quantify multiscale structure in neural representations, and 2026 work has begun tracking language-model representation dynamics with persistent and zigzag homology. But topology is highly sensitive to sampling, metric choice, observer layer, graph construction, and filtration. A topological feature observed in one embedding is not evidence of a universal semantic object unless it survives independent observers, null calibration, and resampling.

The present framework therefore treats topological agreement as one of the **hardest**, not easiest, observer-invariance tests.

---

## 5. Observer informativeness and the Blackwell connection

A more principled version of "observer A is better than observer B" comes from the theory of statistical experiments.

For two channels with a common underlying state, Blackwell's informativeness order says, informally, that channel \(A\) dominates channel \(B\) if \(B\) can be obtained by **garbling** the output of \(A\). Such an \(A\) is at least as useful as \(B\) for every decision problem over the common state. Blackwell dominance is a partial order; many channels are incomparable.

This is almost exactly the discipline needed here.

### 5.1 Approximate semantic observer dominance

For a finite registered semantic benchmark \(\mathcal B\), define

\[
O_A\succeq_{\mathcal B,\varepsilon}O_B
\]

when there exists a stochastic map \(G\) such that

\[
D\!\left(
O_B(\cdot\mid x),
G\circ O_A(\cdot\mid x)
\right)
\leq\varepsilon
\qquad
\forall x\in\mathcal B,
\]

for a preregistered divergence \(D\), and when this simulated observer preserves the registered downstream decisions within tolerance.

For deterministic embedding APIs, stochasticity can be induced through paraphrase families, augmentation, dropout-enabled runs where available, neighborhood sampling, or empirical distributions over matched semantic realizations.

This definition gives a strong interpretation:

> If a weaker observer is approximately a garbling of a stronger observer, the stronger representation contains enough information to reproduce the weaker view plus additional usable distinctions.

### 5.2 The Observer Refinement Hypothesis

We can now state a strong and falsifiable hypothesis.

> **Observer Refinement Hypothesis (ORH).** Within controlled model families and matched semantic domains, increases in independently measured capability are associated with finer observer-resolution profiles, and some lower-capability observers are approximately recoverable as garblings or coarse-grainings of higher-capability observers over registered semantic probes.

The hypothesis deliberately says **some**, not all. Architecture, objective, domain specialization, and modality can make observers Blackwell-incomparable.

A failure to find approximate garbling relations is informative. It would favor a picture in which model improvement changes *which* features are represented rather than successively refining one common observation.

### 5.3 Relation to information bottleneck and successive refinement

The information-bottleneck literature formalizes representations that retain task-relevant information while discarding other detail. Work on successive refinement asks whether a coarse representation can be upgraded to a finer one without losing optimality. These results provide a natural mathematical neighboring framework for semantic observers: a family of embedding models may behave like different-rate descriptions of a latent source, but this must be tested rather than assumed.

The observer paper therefore does **not** claim to invent information ordering or coarse-graining. Its proposal is to operationalize those ideas on modern embedding-model families and connect them to local geometric and topological visibility.

---

## 6. Semantic parallax: disagreement after alignment

If several observers can be aligned into a common frame, the obvious move is to average them. That can destroy useful information.

Let \(T_m\) map observer \(m\)'s representation into a common comparison space, using a frozen alignment procedure such as paired Procrustes, GPA/GCPA, a relative representation, `vec2vec`, SUE, or another baseline. For stimulus \(x\), define the consensus representation

\[
\bar z(x)=\operatorname{Agg}_{m=1}^{M}T_m(O_m(x)).
\]

Define the observer residual

\[
\delta_m(x)=T_m(O_m(x))-\bar z(x).
\]

We call structured, reproducible components of \(\delta_m\) **semantic parallax**.

The term is not meant to imply literal projective geometry. Its operational content is simply:

> After removing the component on which observers can be brought into agreement, does the residual systematically predict observer identity, domain competence, sensitivity to particular semantic distinctions, or downstream behavior?

If the residual is only noise, parallax has no scientific value.

### 6.1 Universal component plus observer-specific residual

The decomposition

\[
T_m(O_m(x))
=
\bar z(x)+\delta_m(x)
\]

suggests two complementary objects:

- **consensus structure**, which is a candidate observer-invariant component;
- **observer-specific structure**, which may encode specialization, blind spots, or distortions.

This is particularly relevant to interpretability. A universal aligned representation can tell us what several models agree a stimulus means. The residual can tell us **where an observer departs from that consensus**.

### 6.2 Parallax must beat nuisance explanations

A parallax claim must survive controls for:

- embedding dimension;
- sequence or image length;
- norm and anisotropy;
- tokenizer artifacts;
- domain/source metadata;
- alignment model capacity;
- training-data overlap where known;
- paraphrase or augmentation family;
- random observer labels.

A residual that merely identifies the model family is not automatically semantically meaningful.

---

## 7. Multi-observer semantic tomography

Multi-view learning has long exploited the fact that several measurements can contain complementary information about a shared latent variable. Multi-view nonlinear ICA goes further: under explicit assumptions, multiple sufficiently different noisy views can make latent-source recovery identifiable even when individual nonlinear views are not. Multimodal contrastive-learning theory likewise establishes latent-factor identifiability under particular generative conditions.

Therefore the claim "several views can recover a latent source" is emphatically **not new**.

The narrower proposal here is to treat a collection of independently trained embedding models as a population of semantic observation channels and ask whether their **measured resolution and residual structure** can be used to reconstruct relational features more faithfully than any single observer.

Let each observer induce a local graph

\[
G_m=(V,E_m,W_m).
\]

A reliability-weighted consensus graph may be estimated as

\[
\widehat W_{ij}
=
\frac{\sum_m w_m(i,j,s)W^{(m)}_{ij}}
{\sum_m w_m(i,j,s)},
\]

where \(w_m\) is determined only from training/calibration data and can depend on location and scale.

Call the resulting procedure **semantic tomography** only if it satisfies a hard criterion:

\[
\operatorname{Err}(\widehat{\mathcal U}_{1:M})
<
\min_m\operatorname{Err}(\widehat{\mathcal U}_m)
\]

on held-out structure with an external ground truth or independent behavioral reference.

Consensus by itself is not truth. Correlated models can share the same systematic error. The tomography claim therefore requires external validation.

---

## 8. Prior art and the novelty boundary

This proposal sits at the intersection of mature literatures. A credible version must say explicitly what is already known.

### 8.1 Representational similarity is established prior art

Representational Similarity Analysis (RSA) compares relational structure rather than raw units and was explicitly designed to bridge different measurement modalities and subjects. SVCCA and CKA provide transformation-invariant or partially invariant comparisons of neural representations. A large literature now compares neural networks using representational and functional similarity measures.

**Not claimed here:** inventing representation comparison, coordinate invariance, local-neighborhood similarity, or a new scalar similarity score.

### 8.2 Alignment and interoperability are established prior art

Relative representations, Procrustes mappings, model stitching, Gromov-Wasserstein alignment, Joint MDS, and learned latent translators all align or compare heterogeneous spaces. `vec2vec` makes the strongest challenge to any novelty claim based merely on a universal text-embedding space: it demonstrates unsupervised translation through a learned universal latent. Multi-Way Representation Alignment supplies a common reference for several models and explicitly separates geometry-preserving from agreement-maximizing objectives.

**Not claimed here:** discovering that embeddings can be aligned, constructing the first common reference, or showing that raw coordinates are arbitrary.

### 8.3 Shared or universal representations are established prior art

The PRH explicitly proposes convergence toward a shared statistical model of reality. SUE learns shared representations from mostly unpaired multimodal data. Multi-view representation learning, CCA-family methods, multimodal autoencoders, and related methods are much older.

**Not claimed here:** the first shared-latent-space hypothesis or the first multi-view fusion method.

### 8.4 Local convergence is now especially close prior art

The Aristotelian Representation Hypothesis is the closest conceptual neighbor. Its core empirical conclusion is that calibrated local neighborhood relations survive cross-model and cross-modal comparison more robustly than global geometry. Hosseini et al. further introduce single-stimulus dispersion across aligned model populations and show that intra-modal agreement modulates cross-modal convergence.

These works occupy a substantial portion of the intuitive territory behind "models observe the same thing differently."

**Proposed distinction:** the present framework moves from *how much models agree* to a registered **observability profile over structural type, location, and scale**, adds an approximate informativeness order, explicitly models topology-changing coarse-graining, and asks whether disagreement residuals and observer fusion predict externally validated structure.

### 8.5 Multi-view latent recovery is established prior art

Gresele et al.'s Incomplete Rosetta Stone results show that multiple sufficiently different noisy nonlinear views can permit recovery of shared latent sources under assumptions that fail in the single-view case. Later multimodal contrastive-learning identifiability results extend this general theme.

**Not claimed here:** proving generic identifiability from multiple views.

### 8.6 Manifold and topology analysis are established prior art

Neural manifolds, intrinsic dimension, manifold capacity, TDA, persistent homology, spectral geometry, and concept-manifold featurization are active research areas. Recent work uses persistent and zigzag homology directly on language-model representations, while Block-Sparse Featurizers provide evidence that some learned concepts are better modeled as low-dimensional multidimensional structures than as single directions.

**Not claimed here:** the first manifold or topological analysis of neural representations.

### 8.7 Informativeness and coarse-graining are established prior art

Blackwell's theory orders statistical experiments by informativeness; information-bottleneck and successive-refinement work studies compressed representations and changing granularity.

**Not claimed here:** a new general information order.

### 8.8 What is left to contribute?

The candidate contribution is therefore deliberately specific:

1. **Semantic observer formalization:** treat pretrained embedding systems as measurement channels of a latent *relational* semantic substrate without assuming one global Euclidean space.
2. **Multiscale resolution profile:** measure recoverability of registered structural predicates as a function of semantic location, scale, and observer.
3. **Approximate observer dominance:** test whether capability improvements correspond to Blackwell-like refinement or instead produce incomparable observation channels.
4. **Apparent-topology hypothesis:** test whether missing resolution causes reproducible merges, splits, and bridge loss across observers.
5. **Semantic parallax:** test whether aligned observer residuals contain reproducible, behaviorally useful semantic information rather than nuisance variation.
6. **Observer-aware tomography:** test whether reliability-weighted combinations of heterogeneous observers recover externally defined structure better than the best single observer.

The combination may be novel; each ingredient separately has substantial precedent. The paper should be rejected as an originality claim if existing work is found that already operationalizes this same combination on learned semantic representations.

---

## 9. Experimental programme

The experiments are staged so that a failure at an early stage prevents promotion of stronger claims.

### 9.1 Stage 0 — Synthetic instrument validation

Construct latent spaces with known structure:

- separated clusters;
- clusters joined by bridges of controlled width;
- circles and tori with known persistent homology;
- curved one- and two-dimensional manifolds;
- hierarchical trees embedded with known neighborhoods;
- continuous manifolds containing controlled semantic-like boundaries.

Generate synthetic observers with known transformations:

\[
O_m(x)=f_m(x)+\epsilon_m,
\]

where \(f_m\) includes rotations, anisotropic scalings, nonlinear warps, dimensional projections, local blur, region-specific masking, and stochastic noise.

The instrument passes only if the proposed resolution metrics recover the known ordering under true coarse-graining **and** identify deliberately incomparable observers.

This stage is essential because a metric that always ranks higher-dimensional observers as "better" would merely reproduce the scale confound already documented in representational-similarity work.

### 9.2 Stage 1 — Controlled semantic micro-worlds

Create semantic worlds with known relational ground truth independent of any tested embedding model. Candidates include programmatically generated scene graphs, small knowledge graphs, compositional attribute spaces, taxonomies, and rule-generated textual descriptions.

For example, define objects by attributes

\[
x=(shape,color,size,material,relation),
\]

then generate multiple paraphrases that realize the same latent state. The ground-truth neighborhood and factor structure are known before embedding.

Test model families spanning:

- parameter scales within the same architecture/training family;
- different embedding objectives;
- domain-specialized versus generic encoders;
- multilingual encoders;
- text and, where paired ground truth exists, vision encoders.

No model is ranked by parameter count. Capability is measured independently on held-out tasks relevant to the tested semantic domain.

### 9.3 Stage 2 — Resolution curves

For each registered structure \(\alpha\), estimate

\[
R_m(s,\alpha)
=
\mathbb E_u[R_m(u,s,\alpha)]
\]

and local profiles \(R_m(u,s,\alpha)\).

Primary hypothesis:

> Better independently measured domain capability predicts finer resolution for at least some preregistered structural families after null calibration.

Strong version:

> The resolution curves are approximately nested within controlled model families.

The strong version is expected to fail often and should not be rescued by post-hoc domain selection.

### 9.4 Stage 3 — Approximate Blackwell refinement

Train a constrained garbling map from higher-capability to lower-capability observer outputs using only the training split. Compare:

- high \(\rightarrow\) low simulation;
- low \(\rightarrow\) high simulation;
- matched-capability cross-family simulation;
- random and shuffled controls.

A refinement relation requires not only low representation loss but preservation of a preregistered family of downstream semantic decisions.

If both directions are equally easy, the result may reflect generic alignment rather than informativeness dominance. If neither direction works while each observer has distinct strengths, the correct interpretation is incomparability.

### 9.5 Stage 4 — Apparent topology

Using datasets with known latent topology or graph connectivity, measure whether observers lose or invent structural features.

Required estimators include at least:

- mutual-kNN neighborhood agreement;
- boundary/bridge recovery;
- local intrinsic-dimension estimates;
- tangent-space principal-angle agreement;
- geodesic rank correlation where a ground-truth path metric exists;
- persistent-homology summaries under preregistered filtrations.

Topological claims require stability across bootstrap samples, neighborhood scales, and at least two independent estimators where feasible.

### 9.6 Stage 5 — Semantic parallax

Fit a common frame using only training items. On held-out data compute residuals \(\delta_m(x)\).

Test whether residual structure predicts:

- observer-specific downstream errors;
- domain specialization;
- sensitivity to compositional distinctions;
- robustness to paraphrase;
- known modality-specific information.

Compare against nuisance-only predictors. A parallax effect counts only if it transfers to new stimuli and remains after controlling for model identity and basic embedding statistics.

### 9.7 Stage 6 — Multi-observer tomography

Construct consensus or latent reconstructions using multiple observers. Baselines must include:

- best single observer selected on training data;
- equal-weight averaging after alignment;
- GPA/GCPA consensus;
- `vec2vec` common latent where applicable;
- SUE or another shared-representation baseline where modality/data permit;
- reliability-weighted fusion using the proposed resolution profiles.

Primary test:

\[
\Delta_{fusion}
=
\operatorname{Err}(best\ single)
-
\operatorname{Err}(fusion).
\]

The tomography claim passes only if \(\Delta_{fusion}>0\) on an untouched test set with confidence intervals excluding zero under the preregistered analysis.

---

## 10. Metrics and calibration

### 10.1 Local relations first

Given the 2026 evidence against uncalibrated global convergence, the primary cross-observer statistic should be local neighborhood agreement, not global CKA.

For a paired stimulus set, define mutual-kNN overlap for item \(i\) as

\[
J_k^{A,B}(i)
=
\frac{|N_k^A(i)\cap N_k^B(i)|}
{|N_k^A(i)\cup N_k^B(i)|}.
\]

Aggregate only after applying a width/depth-aware permutation calibration comparable in spirit to Gröger et al. Raw similarity is insufficient.

### 10.2 Global metrics remain diagnostics

RSA, CKA, SVCCA, Procrustes error, and spectral similarity remain useful, but they are secondary. Agreement among them is itself an empirical result, not an assumption.

### 10.3 Geometry-preserving versus agreement-maximizing alignment

Achara et al. show that isometric alignment and retrieval agreement optimize different desiderata. Every observer experiment should therefore report at least one geometry-preserving alignment and one agreement-maximizing baseline where possible.

Otherwise a flexible alignment may erase exactly the observer-specific distortion we want to measure.

### 10.4 Negative controls

At minimum:

- shuffled stimulus correspondences;
- feature-marginal-preserving scrambling;
- random orthogonal transforms;
- dimension-matched Gaussian or synthetic embeddings;
- label permutation for supervised structural probes;
- corpus/source and length controls;
- alignment-capacity controls.

The test statistic—not an upstream intermediate—must be calibrated against its own null when model width, depth, layer search, or hyperparameter selection can inflate it.

---

## 11. Core hypotheses and falsification criteria

### H1 — Local observer invariance

**Hypothesis.** Independently trained competent observers preserve non-trivial local semantic neighborhood relations above calibrated nulls.

**Falsified if.** Calibrated neighborhood agreement is indistinguishable from matched nulls across preregistered datasets or disappears on independent corpora.

This is close to the Aristotelian hypothesis and is not presented as a new claim; it is the foundation the rest of the programme requires.

### H2 — Resolution differentiation

**Hypothesis.** Observer-resolution profiles differ systematically across models and predict independent domain/task capability better than parameter count or embedding dimension alone.

**Falsified if.** Profiles are unstable across resamples or add no predictive information beyond simple nuisance/model-size variables.

### H3 — Successive semantic refinement

**Hypothesis.** Within at least some controlled model families, higher-capability observers resolve finer preregistered structure and can approximately simulate lower-capability observers through garbling more readily than the reverse.

**Falsified if.** Directional simulation is absent, symmetric, or unrelated to capability after matched-capacity controls.

### H4 — Apparent-topology error

**Hypothesis.** Known fine-scale semantic structures disappear or merge in predictable ways as observer resolution degrades.

**Falsified if.** Topological/bridge errors show no relationship to independently estimated resolution or are dominated by estimator choice.

### H5 — Semantic parallax

**Hypothesis.** Cross-observer residuals after common alignment contain reproducible semantic information that predicts model-specific behavior on held-out stimuli.

**Falsified if.** Residuals reduce to model identity, length, norm, source, or alignment artifacts and fail cross-corpus transfer.

### H6 — Multi-observer reconstruction

**Hypothesis.** Combining observers with complementary resolution profiles can recover externally specified semantic structure more accurately than the best single observer under a matched data budget.

**Falsified if.** Fusion does not outperform the best preregistered single-observer baseline or gains vanish under independent test sets.

---

## 12. What would the strongest positive result mean?

Suppose the programme found that:

1. calibrated local neighborhoods are shared across model families;
2. observer resolution varies systematically by domain and scale;
3. some weaker observers are approximate garblings of stronger ones;
4. fine structural features emerge monotonically along controlled capability series;
5. residual parallax predicts domain-specific behavior;
6. multi-observer fusion reconstructs known latent structure better than any single observer.

That would support a careful conclusion:

> Learned representation systems behave as partially informative, differently resolved observations of a shared semantic relational substrate on the tested domains and scales.

It still would **not** establish a metaphysically real semantic universe, a globally unique metric, or observer-independent coordinates.

The strongest result would be epistemic and operational: different learned systems would be shown to provide complementary measurements of reproducible structure.

---

## 13. What would a negative result mean?

Several negative outcomes are scientifically useful.

### 13.1 Alignment without refinement

Models may align well while no Blackwell-like capability order exists. Then shared geometry is better understood as interoperability than as progressively clearer observation.

### 13.2 Shared neighborhoods without shared curvature

This would support the Aristotelian picture: local order relations may be the invariant while metric/manifold detail remains observer-specific.

### 13.3 Consensus without truth

Several models may agree strongly yet fail external semantic ground truth. This would demonstrate correlated bias, directly falsifying the naive tomography story.

### 13.4 Better task performance without finer semantic resolution

A stronger encoder could improve because it represents **different** task-relevant features, not because it refines a common scene. This would reject the telescope analogy as a general model.

### 13.5 Parallax as noise

If aligned residuals fail to predict anything beyond nuisance variables, the universal/residual decomposition is descriptively sufficient and no special parallax construct is needed.

---

## 14. Relation to the Semantic Atlas, Pontifex, and semantic navigation

This paper is intended to isolate a foundational question that otherwise gets mixed into downstream proposals.

The **Semantic Atlas** asks whether language-model behavior can be mapped as trajectories, reachability, control cost, and navigable semantic dynamics. The observer framework supplies a stricter interpretation of the Atlas's coordinate layer: an atlas should record not only estimated structure, but **which observers resolve that structure and with what uncertainty**. A shared location does not imply shared dynamics.

**Pontifex** asks whether perturbation saliency can be made tokenizer-free and compared across several independent representation spaces. The observer framework suggests a stronger decomposition for that project: universal or consensus response plus observer-specific parallax. The interesting signal may be precisely what alignment does not remove.

For **semantic search and navigation systems**, the practical implication is observer selection. If \(R_m(u,s,\alpha)\) is known approximately, a system need not use one embedding model everywhere. A cheap coarse observer could navigate broad semantic structure; a higher-resolution or domain-specialized observer could be invoked only near ambiguous boundaries or narrow semantic bridges. This is an engineering implication, not part of the core scientific claim.

---

## 15. Limitations

### 15.1 The latent substrate may be non-identifiable

Many different latent structures can generate the same family of observations. The paper therefore avoids claiming unique recovery of \(\mathcal U\) without explicit identifiability assumptions.

### 15.2 "Semantic" ground truth is difficult

Controlled micro-worlds provide ground truth but can be artificial. Natural-language benchmarks are realistic but often encode annotation conventions rather than semantic reality. Both are necessary.

### 15.3 Model populations are not independent observers

Modern encoders share architectures, datasets, distillation sources, and training conventions. Agreement can reflect common ancestry rather than independent discovery.

### 15.4 Capability is multidimensional

No single benchmark defines observer quality. Resolution profiles should therefore be predicted from domain-specific capability vectors, not one global score.

### 15.5 Alignment can manufacture agreement

A high-capacity nonlinear alignment can make unrelated spaces look compatible. Geometry-preserving baselines, held-out correspondences, and shuffled controls are mandatory.

### 15.6 Structural estimators can create artifacts

kNN graphs, manifold estimators, curvature estimates, and persistent homology all depend on scale and sampling. Registered sensitivity analyses are part of the claim, not optional robustness decorations.

### 15.7 Human semantics is not automatically the latent truth

Human similarity judgments are useful external references but are themselves observer-dependent measurements. When used, they should be described as behavioral reference channels, not ontological ground truth.

---

## 16. Conclusion

The rapid progress of representation alignment changes the interesting question. It is increasingly difficult to claim novelty merely from the observation that independently trained models share geometry or can be translated into one another. The frontier is now to characterize **what is actually invariant, what remains observer specific, and how that difference depends on scale and capability**.

This paper proposes an observer-based framework for doing so. Embedding models are treated as measurement channels of an unknown semantic relational substrate. Their quality is described not by one scalar but by local multiscale resolution profiles. Blackwell-style informativeness provides a hard test for the intuition of successive refinement. Apparent topology makes loss of resolution geometrically falsifiable. Semantic parallax asks whether structured disagreement contains useful information. Multi-observer tomography asks whether complementary views can reconstruct externally validated structure better than any one view.

The central hypothesis can be stated without metaphysics:

\[
\boxed{\text{Different learned models may be differently resolved measurements of partially shared semantic structure.}}
\]

The corresponding research question is sharper:

\[
\boxed{\text{Which semantic relations are observer-invariant, and what becomes visible as observer resolution changes?}}
\]

That question remains meaningful whether the strongest Platonic hypothesis is true, whether only local Aristotelian neighborhoods are universal, or whether semantic structure ultimately proves to be a patchwork of observer-dependent but partially interoperable relations.

---

## References

Achara, A., Gaintseva, T., Mahaut, M., Chakraborty, P., Stenby Johansson, V., Barsbey, M., Rodolà, E., & Crisostomi, D. (2026). **Multi-Way Representation Alignment.** ICML 2026. arXiv:2602.06205. https://arxiv.org/abs/2602.06205

Aghajanyan, A., Zettlemoyer, L., & Gupta, S. (2020). **Intrinsic Dimensionality Explains the Effectiveness of Language Model Fine-Tuning.** arXiv:2012.13255. https://arxiv.org/abs/2012.13255

Ballester, R., Casacuberta, C., & Escalera, S. (2023). **Topological Data Analysis for Neural Network Analysis: A Comprehensive Survey.** arXiv:2312.05840. https://arxiv.org/abs/2312.05840

Bansal, Y., Nakkiran, P., & Barak, B. (2021). **Revisiting Model Stitching to Compare Neural Representations.** NeurIPS 2021. https://papers.nips.cc/paper/2021/hash/01ded4259d101feb739b06c399e9cd9c-Abstract.html

Chen, D., Fan, B., Oliver, C., & Borgwardt, K. (2022). **Unsupervised Manifold Alignment with Joint Multidimensional Scaling.** arXiv:2207.02968. https://arxiv.org/abs/2207.02968

Daunhawer, I., Bizeul, A., Palumbo, E., Marx, A., & Vogt, J. E. (2023). **Identifiability Results for Multimodal Contrastive Learning.** ICLR 2023. https://openreview.net/forum?id=U_2kuqoTcB

Davies, T., Wan, Z., & Sanchez-Garcia, R. J. (2023). **The Persistent Laplacian for Data Science: Evaluating Higher-Order Persistent Spectral Representations of Data.** ICML 2023. https://proceedings.mlr.press/v202/davies23c.html

Federici, M., Dutta, A., Forré, P., Kushman, N., & Akata, Z. (2020). **Learning Robust Representations via Multi-View Information Bottleneck.** arXiv:2002.07017. https://arxiv.org/abs/2002.07017

Fel, T., Kowal, M., Jacobs, M., et al. (2026). **Structuring Sparsity: Block-Sparse Featurizers Capture Visual Concept Manifolds.** arXiv:2606.25234. https://arxiv.org/abs/2606.25234

Gresele, L., Rubenstein, P. K., Mehrjou, A., Locatello, F., & Schölkopf, B. (2020). **The Incomplete Rosetta Stone Problem: Identifiability Results for Multi-View Nonlinear ICA.** UAI / PMLR 115:217–227. https://proceedings.mlr.press/v115/gresele20a.html

Gröger, F., Wen, S., & Brbić, M. (2026). **Revisiting the Platonic Representation Hypothesis: An Aristotelian View.** ICML 2026. arXiv:2602.14486. https://arxiv.org/abs/2602.14486

Gröger, F., Wen, S., Le, H., & Brbić, M. (2025). **With Limited Data for Multimodal Alignment, Let the STRUCTURE Guide You.** NeurIPS 2025. arXiv:2506.16895. https://arxiv.org/abs/2506.16895

Hernandez, A., Dangovski, R., Lu, P. Y., & Soljačić, M. (2023). **Model Stitching: Looking for Functional Similarity Between Representations.** arXiv:2303.11277. https://arxiv.org/abs/2303.11277

Hosseini, E. A., Cheung, B., Fedorenko, E., & Williams, A. H. (2026). **Modulating Cross-Modal Convergence with Single-Stimulus, Intra-Modal Dispersion.** arXiv:2604.21836. https://arxiv.org/abs/2604.21836

Huh, M., Cheung, B., Wang, T., & Isola, P. (2024). **Position: The Platonic Representation Hypothesis.** ICML 2024, PMLR 235:20617–20642. https://proceedings.mlr.press/v235/huh24a.html

Jha, R., Zhang, C., Shmatikov, V., & Morris, J. X. (2025). **Harnessing the Universal Geometry of Embeddings.** NeurIPS 2025. arXiv:2505.12540. https://arxiv.org/abs/2505.12540

Kawakita, G., Zeleznikow-Johnston, A., Tsuchiya, N., & Oizumi, M. (2024). **Gromov-Wasserstein Unsupervised Alignment Reveals Structural Correspondences Between the Color Similarity Structures of Humans and Large Language Models.** Scientific Reports. arXiv:2308.04381. https://arxiv.org/abs/2308.04381

Klabunde, M., et al. (2025). **Similarity of Neural Network Models: A Survey of Functional and Representational Measures.** ACM Computing Surveys 57(9), Article 242. https://doi.org/10.1145/3728458

Kriegeskorte, N., Mur, M., & Bandettini, P. (2008). **Representational Similarity Analysis—Connecting the Branches of Systems Neuroscience.** Frontiers in Systems Neuroscience 2:4. https://doi.org/10.3389/neuro.06.004.2008

Li, Y., Yang, M., & Zhang, Z. (2019). **A Survey of Multi-View Representation Learning.** IEEE Transactions on Knowledge and Data Engineering 31(10):1863–1883. https://doi.org/10.1109/TKDE.2018.2872063

Liu, J., Zhang, W., & Poor, H. V. (2021). **A Rate-Distortion Framework for Characterizing Semantic Information.** arXiv:2105.04278. https://arxiv.org/abs/2105.04278

Malhotra, N., Ambadkar, J., Gupta, A., et al. (2026). **Tracking Representation Dynamics in Large Language Models with Persistent Homology.** TAG-DS 2026, PMLR 334:211–245. https://proceedings.mlr.press/v334/malhotra26a.html

Moschella, L., Maiorca, V., Fumero, M., Norelli, A., Locatello, F., & Rodolà, E. (2022). **Relative Representations Enable Zero-Shot Latent Space Communication.** arXiv:2209.15430. https://arxiv.org/abs/2209.15430

Raghu, M., Gilmer, J., Yosinski, J., & Sohl-Dickstein, J. (2017). **SVCCA: Singular Vector Canonical Correlation Analysis for Deep Learning Dynamics and Interpretability.** NeurIPS 2017. https://papers.nips.cc/paper/2017/hash/dc6a7e655d7e5840e66733e9ee67cc69-Abstract.html

Wang, Z., & Goldfeld, Z. (2023). **Neural Entropic Gromov-Wasserstein Alignment.** arXiv:2312.07397. https://arxiv.org/abs/2312.07397

Yacobi, A., Ben-Ari, N., Talmon, R., & Shaham, U. (2025). **Learning Shared Representations from Unpaired Data.** NeurIPS 2025. arXiv:2505.21524. https://arxiv.org/abs/2505.21524

Zhang, L., Yang, Q., & Agrawal, A. (2025). **Assessing and Learning Alignment of Unimodal Vision and Language Models.** CVPR 2025, pp. 14604–14614. https://openaccess.thecvf.com/content/CVPR2025/html/Zhang_Assessing_and_Learning_Alignment_of_Unimodal_Vision_and_Language_Models_CVPR_2025_paper.html

Zhu, T., Han, T., Guibas, L., Pătrăucean, V., & Ovsjanikov, M. (2026). **Dynamic Reflections: Probing Video Representations with Text Alignment.** ICLR 2026. arXiv:2511.02767. https://arxiv.org/abs/2511.02767
