---
type: "Audit Report"
title: "Pontifex Torus occlusion-cartography prior-art audit — 2026-09-17"
description: "Claim-specific audit of the Pontifex Torus intervention-indexed semantic-cartography pivot, with GitHub-derived public cutoffs and explicit separation of component antecedents from the unresolved combination."
tags: [pontifex, torus, prior-art, representation-alignment, perturbation, active-learning, model-similarity, manifold-geometry]
timestamp: 2026-09-17T19:00:00-04:00
---

# Pontifex Torus occlusion-cartography prior-art audit — 2026-09-17

> **Status:** revision/supplement to `audits/prior-art/pontifex-2026-09-17.md`. The earlier audit covers the May 2026 byte-occlusion / bilateral-convergence formulation. This record audits the later Torus pivot now developed on PR #485. It narrows the novelty claim and does not establish patent novelty, exhaustive literature coverage, or causal dependence between projects.

## 1. Claims and claim-specific public cutoffs

The Torus pivot should not inherit the May 2026 cutoff of the older Pontifex formulation. GitHub history on PR #485 gives later, claim-specific cutoffs:

| claim | earliest public GitHub evidence located | cutoff |
|---|---|---|
| **Core intervention-indexed cartography:** apply the same position/scale-indexed occlusions to texts, measure each encoder's response in its own latent space, and learn a local/periodic map from one response field to another without directly aligning latent coordinates | [`abdb9cdef1586f9be1407de31c1a15f819f7847b`](https://github.com/franklinbaldo/papers/commit/abdb9cdef1586f9be1407de31c1a15f819f7847b), `experiment: add Pontifex torus occlusion-lens study` | **2026-09-17 21:18:12 UTC** |
| **Active cartography:** choose a subset of intervention coordinates geometrically (current implementation: k-center) and test whether the cross-space response field can be inferred before exhaustive traversal | [`9419bd0af6085c9da0d0f8a2acc784eb3f9899a0`](https://github.com/franklinbaldo/papers/commit/9419bd0af6085c9da0d0f8a2acc784eb3f9899a0), `experiment: add active torus cartography selection study` | **2026-09-17 21:21:49 UTC** |
| **Directed/tomographic extension:** treat direction/asymmetry of interventions as potentially informative and use repeated directed traversal to refine the map | [`6363e075732cef128d58c98fd65347f4d30b8153`](https://github.com/franklinbaldo/papers/commit/6363e075732cef128d58c98fd65347f4d30b8153), `paper: expand torus into directed tomography and saturation` | **2026-09-17 21:56:47 UTC** |

The living paper itself was added at [`cf38922e6b945027554742f6897386dc94eb6589`](https://github.com/franklinbaldo/papers/commit/cf38922e6b945027554742f6897386dc94eb6589) at 2026-09-17 21:23:22 UTC, but that later file date is **not** used to move earlier claim cutoffs forward.

## 2. Search protocol

This round searched the mechanism under historical and neighboring terminology, not only `Pontifex` or `torus`. Representative queries included:

- `same perturbations compare behavioral responses neural network models`
- `testing based model similarity behavioral pattern pair inputs`
- `shared anchors unaligned latent spaces relative representations`
- `parallel anchors semantic correspondence latent spaces`
- `counterfactual generated for one classifier input into other classifiers response alignment`
- `intervention response geometry neural representations behavior manifold`
- `cyclic geometry neural representations intervention steering`
- `latent space explanation by intervention pre post representation difference`
- `active learning geometry k-center core set`
- `active sampling latent space map k center`
- `occlusion model similarity perturbation response`
- `shared interventions latent spaces alignment neural networks`

Primary-source discovery/verification used arXiv, AAAI proceedings, Zenodo and project/paper pages; secondary surveys/search indexes were used only to find candidates. Searches also covered the recent pre-cutoff 2026 literature because the relevant Torus cutoff is 17 September 2026, not the older May cutoff.

## 3. Candidate-by-candidate findings

### 3.1 ModelDiff — shared test inputs and response-distance signatures

**Yuanchun Li, Ziqi Zhang, Bingyan Liu, Ziyue Yang, Yunxin Liu. _ModelDiff: Testing-Based DNN Similarity Comparison for Model Reuse Detection._ ISSTA 2021.**

- Paper: <https://arxiv.org/abs/2106.08890>
- Associated public artifact: <https://zenodo.org/records/4723301>
- Earliest public date verified in this round: **2021-04-27** for the Zenodo artifact; arXiv v1 is 2021-06-11.
- Compared claim: core intervention-indexed cartography.
- **Classification: `partial_prior_art`.**

ModelDiff does not align model weights or latent coordinates. It exposes models to a common set of inputs and characterizes each model by distances between its reactions to paired inputs (a decision-distance vector), then compares those behavioral patterns. That materially anticipates the general idea that **common probes plus within-model response differences can make otherwise heterogeneous models comparable**.

It does **not** anticipate the Torus combination as currently implemented: the paired inputs are not position/scale-indexed text occlusions, the target is model-reuse similarity rather than learning one semantic response field from another, and there is no active local/periodic cartography objective.

### 3.2 Relative Representations — shared anchors as a common relational coordinate system

**Luca Moschella et al. _Relative representations enable zero-shot latent space communication._** arXiv:2209.15430.

- Primary source: <https://arxiv.org/abs/2209.15430>
- arXiv v1: **2022-09-30**.
- Compared claim: cross-space comparability without direct absolute-coordinate alignment.
- **Classification: `partial_prior_art`.**

Relative Representations encode samples by similarities to a fixed set of shared anchors, making otherwise incompatible latent spaces communicable/comparable without requiring their absolute coordinates to coincide. This is clear antecedent work for the broad relational strategy behind Pontifex: **shared external references can induce comparable coordinates over unaligned spaces**.

Pontifex Torus differs by using **interventions as indexed probes** and responses-to-interventions as the mapped object, rather than similarity-to-static-anchor vectors. Therefore shared relational coordinates are not novel, while the intervention-response construction remains a narrower combination claim.

### 3.3 Bootstrapping / learning anchors and 2026 robust relative representations

**Irene Cannistraci et al. _Bootstrapping Parallel Anchors for Relative Representations._** arXiv:2303.00721, v1 **2023-03-01**. <https://arxiv.org/abs/2303.00721>

**Oscar Thorsted Svendsen et al. _Improving Relative Representations with Learned Anchors and Whitened Inner Products._** arXiv:2605.30596, v1 **2026-05-28**. <https://arxiv.org/abs/2605.30596>

- Compared claim: economical/structured cross-space correspondence through shared reference points.
- **Classification: `adjacent_prior_work` for the Torus response-field claim; `partial_prior_art` for any broad claim that Pontifex is the first to obtain cross-space correspondence from a limited/shared reference set.**

Cannistraci et al. explicitly expand semantic correspondence from a limited seed set of parallel anchors. Svendsen et al. learn robust semantic anchors and use a geometry-aware similarity to improve cross-model communication. These papers make it especially important not to describe Pontifex novelty merely as learning correspondences between unaligned embedding spaces from sparse common references.

### 3.4 Counterfactual Alignment — one intervention, several models, directional response relationships

**Joseph Paul Cohen, Louis Blankemeier, Akshay Chaudhari. _Identifying Spurious Correlations using Counterfactual Alignment._** arXiv:2312.02186.

- Primary source: <https://arxiv.org/abs/2312.02186>
- Project page: <https://latentshift.github.io/>
- arXiv v1: **2023-12-01**.
- Compared claims: shared intervention-response comparison; directional/asymmetric response relation.
- **Classification: `partial_prior_art`.**

Counterfactual Alignment generates a counterfactual with respect to one classifier, feeds the resulting input to other classifiers, and quantifies relationships among the induced output changes. Its project page explicitly discusses **non-symmetric** relationships between classifiers. This is a strong antecedent for two broad ideas in the Torus direction: a perturbation generated/indexed from one reference can be applied across models, and the resulting response relation can carry directional/asymmetric information.

It does not anticipate the current Torus method's text-occlusion grid, explicit position/scale lenses, periodic local map, or active reconstruction of one encoder's intervention-response geography from another.

### 3.5 Latent Space Explanation by Intervention — representation differences under intervention

**Itai Gat, Guy Lorberbom, Idan Schwartz, Tamir Hazan. _Latent Space Explanation by Intervention._ AAAI 2022.**

- Proceedings: <https://ojs.aaai.org/index.php/AAAI/article/view/19948>
- Published **2022-06-28**.
- Compared claim: treating pre/post-intervention representational change as an explanatory signal.
- **Classification: `adjacent_prior_work`.**

This work intervenes on representations and studies differences between original and intervened representations to reveal concepts. It establishes intervention-induced latent change as a meaningful object of analysis, but it is not a cross-encoder cartography method and does not provide the Torus combination.

### 3.6 Manifold Steering — intervention trajectories and non-Euclidean/cyclic representation geometry

**Daniel Wurgaft et al. _Manifold Steering Reveals the Shared Geometry of Neural Network Representation and Behavior._** arXiv:2605.05115.

- Primary source: <https://arxiv.org/abs/2605.05115>
- arXiv v1: **2026-05-06**.
- Compared claims: geometry as the object of intervention analysis; intervention trajectories; cyclic/nonlinear structure.
- **Classification: `partial_prior_art`.**

This is the most important newly located antecedent for the **geometric** framing. Wurgaft et al. fit representation and behavior manifolds, intervene along paths through representation space, and measure the behavioral trajectories induced. They explicitly test cyclic and sequential geometries and argue that intervention/control should respect the intrinsic geometry rather than assume a flat space.

That materially predates the Torus claim that intervention responses should be treated geometrically and that cyclic/periodic structure can matter. It does not, however, construct a common occlusion-indexed response field across two independent text encoders, nor does it learn the target encoder's response geography from the source encoder's response geography. Therefore the broad phrase **"geometry of responses under intervention" is not novel**; the narrower cross-space construction remains unresolved.

### 3.7 k-center / core-set active selection

**Ozan Sener, Silvio Savarese. _Active Learning for Convolutional Neural Networks: A Core-Set Approach._** arXiv:1708.00489.

- Primary source: <https://arxiv.org/abs/1708.00489>
- arXiv v1: **2017-08-01**.
- Compared claim: k-center selection for active cartography.
- **Classification: `prior_art` for the k-center geometric selection principle; `partial_prior_art` for the active-cartography subclaim as a whole.**

Sener & Savarese formulate batch active learning as core-set selection and use the geometry of representation space to choose a covering subset, reducing the problem to k-center-style selection. Thus the current Pontifex use of k-center/farthest-point coverage **cannot itself carry a novelty claim**.

What remains specific to Pontifex is the application target: intervention coordinates are selected to reconstruct a cross-space response field, and success is measured by how well the unsampled semantic geography can be predicted. That combination was not located in this round.

## 4. Revised claim boundaries

The Torus pivot is substantially less novel at the component level than its vocabulary can make it appear. Before the relevant September 2026 cutoffs, the literature already contains:

1. common probes and within-model behavioral-distance signatures for model comparison (`ModelDiff`);
2. shared relational anchors for comparing/communicating across unaligned latent spaces (`Relative Representations` and successors);
3. interventions applied across classifiers with quantified, sometimes asymmetric response relationships (`Counterfactual Alignment`);
4. intervention trajectories analyzed as intrinsic/non-Euclidean, including cyclic geometry (`Manifold Steering`);
5. geometry-based k-center/core-set selection (`Sener & Savarese`).

Accordingly, none of the following should be presented as independently novel: **using shared references across latent spaces; comparing models by their response to common perturbations; treating intervention response geometrically; exploiting direction/asymmetry; using a toroidal/cyclic geometry as such; or using k-center to select informative probes.**

The narrower unresolved combination is:

> Given the same text and an externally indexed family of local occlusions `(position, scale[, direction/context])`, measure each frozen encoder only by its own within-space change; treat those measurements as response fields over the shared intervention coordinates; learn a local/periodic map from one field to another; and test whether a geometrically selected partial traversal reconstructs held-out regions of the target field without first learning a direct alignment between the encoders' latent coordinates.

After the searches documented above, **no pre-2026-09-17 21:18:12 UTC source was located that materially anticipates that entire combination**. This is a negative search result, not a claim of being first.

## 5. Temporal classifications after the cutoff

This round did not locate a post-cutoff work close enough to the full Torus combination to justify `later_independent`, `later_overlap`, `later_non_citing`, `later_citing`, or `later_derivative`. Given that the audited cutoff is only hours old, absence of such a candidate is unsurprising and carries essentially no evidentiary weight.

No causal/dependency inference is made about any source in this audit.

## 6. Change relative to the previous Pontifex audit

The earlier `pontifex-2026-09-17.md` correctly narrowed the May formulation around byte-level occlusion plus multi-space convergence. It did **not** cover the later Torus/cartography pivot because those claims had not yet been published.

This supplement makes two material corrections to how the new pivot should be described:

- **Manifold Steering (2026-05-06)** means the geometric/cyclic intervention framing has significant pre-cutoff antecedent work.
- **ModelDiff (public artifact 2021-04-27) plus Counterfactual Alignment (2023-12-01)** mean common perturbations and cross-model response relations are also established components, not a new primitive introduced by Pontifex.

The defensible novelty question therefore moves from the components to the **specific composition of externally shared occlusion coordinates + within-space response fields + cross-field prediction + partial active traversal**.

## 7. Search frontier / negative evidence

High-value negative searches in this round did not locate an exact pre-cutoff match under combinations of `shared intervention`, `perturbation response map`, `model similarity`, `latent spaces`, `occlusion`, `active sampling`, `k-center`, `counterfactual alignment`, and `manifold geometry`.

The next audit should concentrate on terminology outside ML interpretability that could hide the same construction: system identification by common excitation, response-surface transfer, active manifold mapping, psychophysical system comparison, functional data alignment, and experimental-design literature for reconstructing paired response fields. Patents and theses also remain incompletely covered.
