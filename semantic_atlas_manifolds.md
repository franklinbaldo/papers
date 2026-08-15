---
type: "Technical Paper"
title: "From Semantic Points to Concept Manifolds: A Manifold-Aware Extension of the Semantic Atlas"
description: "Follow-up position paper proposing a two-scale Semantic Atlas in which a global calibrated reference frame locates concept manifolds while local manifold coordinates support geometry-aware navigation, steering, and visualization."
tags: [semantic-atlas, manifolds, block-sparse-featurizers, embeddings, steering, interpretability, navigation]
timestamp: 2026-08-15T01:25:00Z
---

# From Semantic Points to Concept Manifolds: A Manifold-Aware Extension of the Semantic Atlas

**Franklin Baldo**  
Independent Researcher  
franklinbaldo@gmail.com

---

> **Follow-up position paper and experimental extension.** This manuscript does not modify or supersede *Semantic Atlas: Quasar Reference Frames, Reachability, and Closed-Loop Navigation for Language Models*. It asks what changes if the local objects being navigated are not adequately represented as points or preferred directions, but as low-dimensional concept manifolds embedded in a much larger activation space. Unless explicitly marked otherwise, the claims below are hypotheses and proposed experiments rather than measured results.

## Abstract

The Semantic Atlas programme treats language-model behavior as navigation through a structured semantic state space. Recent work on neural geometry sharpens a possible weakness in the simplest version of that picture: a concept may not be well represented by a single direction, centroid, or globally reduced coordinate. Block-Sparse Featurizers (BSFs) recover visual concepts as low-dimensional multidimensional subspaces whose internal coordinates vary continuously, while separate work in language models finds concept manifolds, trajectories over those manifolds, and improved control when steering follows their geometry rather than cutting across it.

This paper proposes a **manifold-aware Semantic Atlas** as a follow-up hypothesis. The original Semantic Reference Frame (SRF) and semantic quasars remain a macroscopic coordinate system. Local semantic structure is instead represented by a sparse collection of active charts, each with its own intrinsic coordinates, activation strength, geometry, and transition dynamics. Navigation therefore decomposes into two coupled problems: **inter-manifold routing**, which determines which conceptual region should be entered next, and **intra-manifold motion**, which determines where and how to move within a concept while preserving its natural geometry.

This produces a testable alternative to a global-PCA picture of semantic space. Global dimensionality reduction remains useful for visualization, but is no longer assumed to be the scientific state representation. We define experiments comparing global linear projections, direction-based features, post-hoc manifold recovery, and block-sparse featurization on language-model activations. We further propose tangent-aware control, cross-model chart alignment, and a three-dimensional "semantic spacecraft" interface in which the visual world is explicitly treated as a rendering of measured geometry rather than evidence by itself. The central falsifiable claim is that a hierarchical atlas of globally located but locally curved concept manifolds predicts and controls language-model trajectories better than matched point-space baselines at comparable complexity.

**Keywords:** semantic atlas, concept manifolds, block sparsity, neural geometry, semantic trajectories, activation steering, local charts, representation geometry, semantic navigation

---

## 1. Scope: a follow-up, not a revision

The original [Semantic Atlas](semantic_atlas.md) proposes a multiscale map of language-model dynamics expressed in a calibrated Semantic Reference Frame (SRF), with semantic quasars fixing an external reference geometry, an atlas estimating local transition and reachability structure, and a Semantic Servo providing closed-loop control.

Nothing in the present paper requires that proposal to be rewritten. The original programme already distinguishes global reference geometry from model-specific dynamics and already treats semantic trajectories as richer objects than isolated embeddings. The narrower question here is:

> **What is the correct local geometric primitive of the atlas?**

The simplest implementation partitions a semantic space into points, neighborhoods, cells, or graph nodes. That is a sensible first experiment. But if concepts themselves occupy curved or multidimensional low-dimensional structures, then a point cloud may be only the sampling of a more structured object. A useful follow-up is therefore to replace neither the SRF nor the atlas, but to refine the local state representation.

The resulting architecture becomes:

```text
language model activations
          ↓
concept-manifold featurizer
          ↓
local manifold coordinates + active concept blocks
          ↓
Semantic Reference Frame / quasars
          ↓
manifold-aware Semantic Atlas
          ↓
inter-manifold route + intra-manifold path
          ↓
geometry-aware Semantic Servo
          ↓
lexical generation
```

The original point-space Atlas is retained as a baseline throughout. If manifold structure does not improve prediction, compression, routing, or control, the extension should be rejected while the broader Semantic Atlas programme remains intact.

## 2. Why points may be an incomplete primitive

### 2.1 One concept can contain structured internal variation

A single concept often varies along several semantically meaningful degrees of freedom. A tree can vary in species, scale, orientation, age, foliage, season, and viewpoint while remaining recognizably a tree. Treating the concept as one direction collapses those internal relations. Treating every instance as an unrelated point preserves the observations but discards the hypothesis that they belong to one coherent geometric object.

Recent evidence makes this more than a philosophical concern. Fel et al. (2026) introduce **Block-Sparse Featurizers**, which enforce sparsity over multidimensional blocks instead of individual one-dimensional features. In DINOv3 and SDXL, the recovered blocks contain interpretable internal geometry, and their effective stable rank is typically about two to four dimensions. The same paper shows that movement within such a block can produce smooth, interpretable changes in generated images. This result is currently strongest in vision and image generation; it is not evidence that every language concept has the same dimensionality or that the same featurizer is optimal for language.

Language-model work nevertheless supplies related evidence. Bhalla et al. (2026) show that sparse autoencoders can fragment continuous concept manifolds across multiple directions and demonstrate post-hoc recovery of manifold structure in Llama 3.1 8B. Wurgaft et al. (2026) find that steering along fitted representation manifolds yields more natural behavioral trajectories than straight-line steering in several structured language tasks. Bigelow et al. (2026) model in-context belief updates as trajectories on low-dimensional conceptual manifolds and show that those trajectories are reflected in both representations and behavior.

These results motivate, but do not establish, the hypothesis that the Semantic Atlas should be charted as a collection of locally low-dimensional objects rather than only a globally reduced cloud.

### 2.2 Global PCA is a rendering candidate, not yet a theory of semantic geometry

Suppose hidden states or embeddings are collected into a matrix

\[
X\in\mathbb R^{n\times D}.
\]

A global projection

\[
P:\mathbb R^D\rightarrow\mathbb R^3
\]

obtained from the first three principal components is attractive because it immediately produces a navigable world. It may also preserve important large-scale variance. But a global linear projection makes a strong assumption: the dimensions that explain variance across the entire corpus are also the dimensions needed to preserve every local conceptual geometry.

That need not hold. Two distant concepts may each have low-dimensional internal structure living in different local tangent spaces. A single three-dimensional projection can superimpose, flatten, or distort them even if each is individually easy to represent in two or three dimensions.

The follow-up hypothesis is therefore not "PCA is wrong." It is:

> **PCA should be evaluated as one observation/rendering layer, while the scientific state may require multiple local charts.**

A visually convincing 3D map is not evidence that the projection preserved causal or navigational structure. Conversely, a high-dimensional atlas can be scientifically useful even if its rendered 3D projection is imperfect.

## 3. A manifold-aware semantic state

Let \(h_t\in\mathbb R^D\) denote a model activation or other high-dimensional semantic observation at step \(t\). A manifold featurizer maps it to a collection of block coordinates

\[
F(h_t)=\{z_{t,g}\}_{g=1}^G,
\qquad z_{t,g}\in\mathbb R^{d_g},
\]

with sparsity encouraged at the block level. For a BSF-like model, only a small active set

\[
\mathcal G_t=\{g:\|z_{t,g}\|_2>\tau\}
\]

should contribute materially to a given activation.

For each active block define

\[
\alpha_{t,g}=\|z_{t,g}\|_2
\]

as a block activation magnitude and

\[
u_{t,g}=z_{t,g}
\]

or a normalized/chart-specific transformation of it as the **intra-concept coordinate**.

This separates two questions that a single scalar feature conflates:

1. **How much is this concept present?** — approximately \(\alpha_{t,g}\).
2. **Where are we inside the concept?** — approximately \(u_{t,g}\).

A manifold-aware semantic state can then be written schematically as

\[
s_t=\left(q_t,\mathcal G_t,\{\alpha_{t,g},u_{t,g}\}_{g\in\mathcal G_t},v_t,\Omega_t\right),
\]

where \(q_t\) is the global SRF position, \(v_t\) is semantic velocity or another dynamic summary, and \(\Omega_t\) records uncertainty.

The precise parameterization is empirical. A BSF block is a candidate chart, not automatically the true intrinsic manifold. Curvature may require nonlinear coordinates inside a block, multiple overlapping charts, or a different featurizer entirely.

## 4. Global quasars, local charts

### 4.1 Keep the SRF macroscopic

The Semantic Atlas introduced artificial quasars to define an external reference geometry while using paired calibration data to establish cross-model orientation. That distinction should remain.

The manifold extension does **not** assign intrinsic semantic meaning to a quasar. Nor does it assume that the basis vectors inside a learned concept block are stable across independently trained models. A local block basis can rotate without changing the represented manifold.

Instead, the SRF can locate local charts macroscopically. For a concept block \(g\), define a representative global location such as

\[
c_g=\mathbb E[T_M(h)\mid g\text{ active}],
\]

where \(T_M\) is the model-specific map into the calibrated SRF. More detailed summaries can include covariance, support, boundary samples, or multiple landmarks rather than a single centroid.

The atlas therefore acquires a two-scale structure:

```text
GLOBAL
SRF + semantic quasars
    └── concept region g
         ├── chart coordinate u1
         ├── chart coordinate u2
         └── ...

DYNAMIC
concept/chart g_t
    → location within chart u_t
    → transition to chart g_{t+1}
```

The global frame answers "where is this conceptual region relative to the rest of the atlas?" The local chart answers "what variations are available inside it?"

### 4.2 The gauge problem appears again locally

Local manifold coordinates are not automatically comparable across models. If one model represents a concept in coordinates \(u\) and another in \(Ru\) for an orthogonal matrix \(R\), their geometries can be equivalent while their coordinate labels differ.

Cross-model manifold alignment must therefore be tested using paired examples or invariant quantities. Candidate tests include:

- Procrustes alignment of matched local coordinates;
- geodesic-distance correlation;
- neighborhood preservation within a chart;
- correspondence of boundary or extremal states;
- preservation of transition ordering along known structured concepts;
- shuffled-pair negative controls.

A successful global SRF does not imply successful local chart alignment. These are separate claims.

## 5. Navigation becomes two coupled problems

### 5.1 Inter-manifold routing

At a coarse scale, the planner chooses a sequence of conceptual regions

\[
g_0\rightarrow g_1\rightarrow\cdots\rightarrow g_k.
\]

Edges can be weighted by observed transition probability, intervention cost, reachability, uncertainty, or task-specific utility. This is close to the graph/cell view of the original Atlas.

### 5.2 Intra-manifold motion

Within a selected concept region, the desired path should respect local support. Let \(\mathcal M_g\) denote the manifold associated with chart \(g\). Instead of taking a Euclidean straight line between two activation-space points,

\[
h(\lambda)=(1-\lambda)h_a+\lambda h_b,
\]

we seek a path

\[
\gamma:[0,1]\rightarrow\mathcal M_g
\]

that remains close to the natural representation manifold and minimizes an appropriate local cost.

The practical implementation may use:

- tangent directions estimated from neighbors;
- a fitted nonlinear manifold;
- geodesics under a learned metric;
- BSF coordinates followed by decode/re-embed verification;
- model-predictive control constrained by atlas support.

The key comparison is not whether curved paths look nicer. It is whether they produce better measured behavior: higher task success, greater likelihood under the base model, lower off-support distance, smaller intervention norm, or more predictable semantic displacement.

### 5.3 Transitions can depend on where one is inside a concept

A graph with one node per concept loses an important dependency if transition probabilities vary across the concept manifold. We should therefore model

\[
P(g_{t+1},u_{t+1}\mid g_t,u_t,v_t,\text{context})
\]

rather than only

\[
P(g_{t+1}\mid g_t).
\]

For example, movement from a broad "tree" manifold toward "autumn" may be easier from the region encoding leaf color than from the region encoding trunk geometry. If such conditional transition structure is measurable, the local coordinates are not merely interpretability decorations; they are part of the dynamics.

## 6. Semantic gravity under the manifold view

The original Atlas defines semantic gravity operationally through escape or intervention cost. The manifold extension makes that quantity potentially more local.

For a manifold region \(B\subset\mathcal M_g\), define an escape cost

\[
E_{escape}(B,u)=\min_{\Gamma:(g,u)\rightarrow\neg B} C(\Gamma).
\]

Gravity can therefore vary within a concept. Some parts of a manifold may be dynamically sticky while others lie near bridges to neighboring concepts.

This suggests three distinct observables that should not be collapsed into one visual parameter:

- **occupancy/density:** how often the model visits a region;
- **geometric extent:** how much local variation is represented;
- **dynamic gravity:** how costly it is to leave or redirect the region.

A visualization may encode them as brightness, radius, or attraction, but those mappings must remain declared render choices rather than physical claims.

## 7. A semantic spacecraft as an experimental interface

A three-dimensional navigable interface can be scientifically useful if it is built as an instrument rather than a proof-by-visualization.

### 7.1 World construction

Each discovered concept manifold becomes a rendered object or local system. Its macroscopic location is derived from its SRF representation. Internal manifold coordinates are reduced to two or three visual dimensions **within that local chart** using PCA, another faithful local projection, or a learned chart map.

A possible rendering contract is:

| Visual element | Measured quantity |
|---|---|
| system position | SRF location / chart landmark |
| local surface coordinates | reduced intra-manifold coordinate |
| luminosity | activation or visitation frequency |
| apparent size | measured support/extent, with declared transform |
| attraction | empirical escape/control cost |
| route line | observed or planned transition path |
| fog/uncertainty | atlas uncertainty or sparse support |

The rendering must expose its transforms so that a visually dramatic property cannot silently masquerade as a scientific result.

### 7.2 Text as propulsion

The player's text is embedded or passed through the observed model, producing a new semantic state. Movement is then the measured transition

\[
s_t\rightarrow s_{t+1},
\]

not an arbitrary game-engine velocity vector.

A typed phrase can therefore:

1. change which concept blocks are active;
2. move the state inside one or more active blocks;
3. shift the global SRF position;
4. alter semantic velocity and reachable next regions.

The game becomes a front end for observing and probing the atlas. A user may discover that two visually nearby systems are dynamically hard to traverse between, or that a seemingly distant region has a low-cost semantic bridge.

### 7.3 Empty space is itself a hypothesis

The earlier intuition that a navigable semantic universe should contain empty space becomes testable. Empty regions should correspond to low support under the measured representation distribution or to regions that are not reachable under the chosen budget.

A meaningful "void" must be stable under:

- resampling the corpus;
- changing random seeds;
- reasonable changes in projection;
- held-out prompts;
- local neighborhood metrics.

If voids appear and disappear under arbitrary rotations or rendering choices, they are visualization artifacts, not atlas structure.

## 8. Experimental programme

The experiments below are deliberately staged. A visually impressive demo is not allowed to substitute for the earlier quantitative gates.

### 8.1 Experiment M0: reproduce the geometric premise

Before extending the Atlas, reproduce a small public BSF result on an available vision model or synthetic manifold dataset using the authors' public implementation or an equivalent implementation.

Purpose:

- verify that the pipeline and metrics are understood;
- establish reconstruction and block-sparsity baselines;
- validate the distinction between block activation strength and intra-block coordinates;
- avoid debugging the Semantic Atlas and a new featurizer simultaneously.

This experiment supports no language-model claim.

### 8.2 Experiment M1: discover local concept geometry in language activations

Using a frozen open language model such as Qwen3-0.6B or Llama 3.1 8B, collect activations from registered layers and token positions over a frozen corpus containing both natural text and structured concept families.

Compare:

1. global PCA;
2. a standard sparse autoencoder or other direction-based featurizer;
3. post-hoc grouping of direction features into candidate manifolds;
4. a BSF-like block-sparse featurizer;
5. simple local PCA/kNN manifold baselines.

Primary measurements:

- held-out reconstruction error;
- minimum-description-length or matched compression measure;
- stable/effective rank of recovered blocks;
- neighborhood preservation;
- split-to-split stability of recovered geometry;
- semantic coherence under blinded labels or automated probes;
- sensitivity to block size and sparsity budget.

**Support condition:** a manifold-aware method captures reproducible low-dimensional internal structure at comparable or lower description cost than matched direction-based baselines.

**Falsifier:** blocks are effectively one-dimensional, unstable across splits, semantically incoherent, or no more parsimonious than simple baselines.

### 8.3 Experiment M2: trajectories on charts

Construct prompts with known evolving latent structure, including at least one replication-style task inspired by emotional story trajectories and one non-emotional structured domain.

For each sequence, compare prediction of the next semantic state using:

- global SRF position only;
- SRF position plus velocity;
- active chart identity only;
- chart identity plus intra-chart coordinate;
- full manifold-aware state.

Primary endpoint:

\[
\text{held-out next-state prediction error}
\]

under matched model complexity.

A manifold coordinate earns its place in the Atlas only if it predicts future semantic motion or behavior beyond simpler global summaries.

### 8.4 Experiment M3: geometry-aware steering

For concept families with validated local geometry, compare:

1. base generation;
2. straight-line activation steering;
3. global SRF MPC;
4. local manifold steering;
5. hierarchical control: global SRF route plus local manifold steering.

Measure:

- target/task success;
- base-model log probability or KL divergence;
- off-manifold distance;
- intervention norm;
- semantic route error;
- failure/recovery under perturbations;
- total compute.

The manifold hypothesis predicts that geometry-aware interventions will reach matched semantic targets with less off-support motion or less behavioral degradation than straight-line controls.

### 8.5 Experiment M4: cross-model chart portability

Repeat a subset of M1-M3 for two observers or generators. Use the original SRF calibration procedure for global alignment, then separately test whether matched local manifolds can be aligned from paired examples.

Required controls:

- held-out paired items;
- shuffled correspondences;
- random orthogonal chart rotations;
- unmatched concept controls;
- native-space baselines.

Possible outcomes should remain distinct:

- global SRF alignment succeeds, local chart alignment fails;
- both succeed for selected concepts;
- local geometry aligns only up to invariant structure;
- neither generalizes.

No outcome from two models establishes a universal semantic manifold catalogue.

### 8.6 Experiment M5: the navigable universe

Only after M1 establishes reproducible chart structure should the 3D semantic spacecraft be treated as an experiment rather than a sketch.

Freeze the mapping from measurements to visual properties before inspecting target examples. Then test whether human navigation in the rendered atlas reveals information that agrees with held-out quantitative structure.

Useful evaluation questions include:

- Do rendered neighborhoods correspond to held-out semantic neighborhoods?
- Do visible bridges predict lower measured transition/control cost?
- Do visible voids correspond to low support or low reachability?
- Can a user reach target semantic states by text more efficiently than with an unstructured interface?
- Does the interface expose false intuitions created by the projection?

The last question matters as much as the first four. A scientific visualization is valuable partly because it can show where the metaphor breaks.

## 9. Strong falsification criteria

The manifold extension should be considered unnecessary or false in its strong form if any of the following survive reasonable attempts at replication:

1. **No intrinsic gain:** global linear methods preserve the relevant neighborhoods, trajectories, and control behavior as well as manifold-aware methods at matched complexity.
2. **No stable charts:** recovered manifolds change qualitatively across samples, seeds, or small hyperparameter changes.
3. **No dynamic relevance:** intra-manifold coordinates do not improve transition or behavior prediction beyond chart identity and global position.
4. **No control advantage:** manifold-aware steering offers no improvement in target success, naturalness, off-support distance, or intervention cost.
5. **No useful hierarchy:** separating inter-manifold and intra-manifold navigation adds complexity without predictive or computational benefit.
6. **Projection dependence:** the purported large-scale structures, bridges, or voids exist only under one convenient visualization.
7. **Excessive entanglement:** useful states require so many simultaneously active, overlapping charts that the representation ceases to compress or clarify the original activation space.

These failures would still leave open weaker conclusions: concepts may have local geometry without that geometry being useful for navigation; BSFs may work in vision but not language; or the Semantic Atlas may remain useful at the coarser graph/cell level proposed originally.

## 10. Relationship to the original Semantic Atlas claims

The follow-up changes the proposed implementation of the local atlas, not the logical status of the original claims.

| Original Atlas claim | Manifold follow-up |
|---|---|
| semantic trajectories are geometrically informative | asks whether trajectories lie on structured local manifolds |
| a calibrated SRF can support comparison/navigation | keeps SRF as global frame; does not replace it |
| atlas fields approximate model dynamics | enriches local state with chart identity and coordinates |
| semantic routes can control generation | tests geometry-aware local routes against point-space routes |
| control may reduce token/compute cost | makes no new efficiency claim until control is validated |
| atlas structure may be compiled from weights | leaves this open; BSF/manifold discovery may itself become a compilation primitive |

This modularity is important. The new evidence from neural geometry should update the research programme without retroactively rewriting what the original paper claimed before those hypotheses were tested.

## 11. Expected contribution if supported

If the experiments succeed, the conceptual shift is small to state but substantial in consequence:

> A semantic atlas is not merely a cloud of points with routes drawn through it. It is an **atlas in the differential-geometric sense**: a collection of local coordinate charts, connected by transitions, embedded in a larger calibrated reference frame.

That interpretation gives distinct roles to the components:

- **semantic quasars** provide external macroscopic reference geometry;
- **concept manifolds** provide local semantic degrees of freedom;
- **chart transitions** provide the grammar of conceptual movement;
- **semantic gravity** measures dynamic resistance rather than visual distance;
- **the Servo** follows geometry rather than assuming straight-line control;
- **the spacecraft interface** renders this structure for exploration without confusing the rendering with the underlying object.

The most interesting possibility is that the model's enormous activation space contains a sparse collection of small, navigable local worlds connected by structured transitions. The least interesting—but equally useful—result would be that this picture fails under controlled comparison with simple global baselines. Both outcomes sharpen the Semantic Atlas programme.

## 12. References

- Baldo, F. (2026). *Semantic Atlas: Quasar Reference Frames, Reachability, and Closed-Loop Navigation for Language Models*. `semantic_atlas.md` in this repository.
- Bhalla, U., Fel, T., Rager, C., Feucht, S., Haklay, T., Wurgaft, D., et al. (2026). *Do Sparse Autoencoders Capture Concept Manifolds?* arXiv:2604.28119.
- Bigelow, E., Sarfati, R., Wurgaft, D., Lewis, O., McGrath, T., Merullo, J., Geiger, A., & Lubana, E. S. (2026). *Stories in Space: In-Context Learning Trajectories in Conceptual Belief Space*. arXiv:2605.12412.
- Fel, T., Kowal, M., Jacobs, M., Hazra, D., Bhalla, U., Sharkey, L., et al. (2026). *Structuring Sparsity: Block-Sparse Featurizers Capture Visual Concept Manifolds*. arXiv:2606.25234.
- Gärdenfors, P. (2000). *Conceptual Spaces: The Geometry of Thought*. MIT Press.
- Wurgaft, D., Rager, C., Kowal, M., Shyam, V., Feucht, S., Bhalla, U., et al. (2026). *Manifold Steering Reveals the Shared Geometry of Neural Network Representation and Behavior*. arXiv:2605.05115.

---

## Claim boundary

This paper proposes an extension and a sequence of falsifiable experiments. It does **not** claim that BSFs are the correct featurizer for language, that language concepts are typically two- to four-dimensional, that independently trained models share the same local manifold coordinates, that semantic "gravity" is a physical force, or that a three-dimensional visualization faithfully represents the full high-dimensional geometry without distortion. Those are exactly the questions the proposed programme is meant to test.
