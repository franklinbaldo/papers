---
type: "Audit Report"
title: "Pontifex Torus Assembly multi-teacher prior-art audit — 2026-09-18"
description: "Claim-specific audit of the multi-teacher Torus Assembly added on PR #485, separating established common-space, multi-teacher, adaptive-reliability, geometry-fusion, and held-out-system antecedents from the narrower intervention-conditioned combination."
tags: [pontifex, torus, prior-art, multi-teacher, knowledge-distillation, representation-alignment, shared-latent-space, reliability, geometry]
timestamp: 2026-09-18T15:02:35-04:00
---

# Pontifex Torus Assembly multi-teacher prior-art audit — 2026-09-18

> **Status:** claim-specific supplement to the Pontifex Torus audits already in this repository. This record audits the later **Torus Assembly** proposal on PR #485, not the earlier occlusion-cartography claim. It narrows novelty boundaries; it does not establish patent novelty, exhaustive literature coverage, or causal dependence between projects.

## 1. Claim and public cutoff

The relevant claim is not as old as Pontifex or even the first Torus/cartography pivot. GitHub history on the still-public PR #485 shows that the multi-teacher Assembly was introduced in:

- [`311f20e2c076d2f6b077a43c4751e78e5dfb63fe`](https://github.com/franklinbaldo/papers/commit/311f20e2c076d2f6b077a43c4751e78e5dfb63fe), `paper: consolidate Torus Assembly long-context and tokenizer-free architecture`, authored/committed **2026-09-18 03:02:31 UTC**.

The parent [`115a3d8a5bb9e6982478af3e24244bc78a6a4861`](https://github.com/franklinbaldo/papers/commit/115a3d8a5bb9e6982478af3e24244bc78a6a4861) still has `## 14. Immediate evaluation ladder` and does not contain the Assembly section. Therefore the relevant cutoff for the claims audited below is:

> **Our cutoff: 2026-09-18 03:02:31 UTC.**

This is a claim-specific cutoff. It is not the PR creation time, paper creation time, current file timestamp, or repository creation date.

At that cutoff the public claim already included the following combination:

1. several independently trained teacher embedding spaces `E_1...E_n` feed one `Z_assembly`;
2. teachers may differ in coordinates, dimensionality, tokenizer, context length, and objective;
3. teachers are related by the **same intervention family** and by transport learned from their response fields rather than by direct parameter alignment;
4. teachers may have **region-dependent reliability** `rho_i(r)`, so local authority can differ across the semantic terrain;
5. the Assembly is updated sequentially while trying to preserve previously acquired geometry, with teacher-order/repeated-cycle controls;
6. a held-out teacher is excluded from Assembly construction and used to test whether the resulting geometry predicts its response geometry or downstream neighborhoods;
7. after Assembly construction, the space is frozen and a cheap student is distilled into it using a disjoint student corpus, with separate validation and final test corpora.

The broad claim is therefore stronger than ordinary pairwise latent alignment, but several of its ingredients and larger subcombinations have substantial antecedents.

## 2. Search protocol

This round searched both the exact vocabulary and older terminology that could encode the same mechanism. Representative queries included:

- `multiple heterogeneous teacher networks common feature space student distillation`
- `multi teacher knowledge distillation adaptive teacher weight per sample reliability`
- `heterogeneous pretrained models shared latent space universal representation`
- `cross model concept alignment universal latent space multiple pretrained models`
- `hub and spoke shared latent space heterogeneous models anchor texts`
- `same inputs shared response model multiple subjects common latent space`
- `shared response model held out subject common space decoder`
- `relative representations anchors unaligned latent spaces`
- `Gromov Wasserstein barycenter heterogeneous metric spaces Frechet mean`
- `shared interventions response field representation alignment multiple models`
- `perturbation response shared latent space multiple encoders`
- `intervention conditioned transport teacher reliability semantic region`
- recent searches restricted around the cutoff for `shared latent space`, `multiple pretrained models`, `multi-teacher common space`, and `cross-model shared latent`.

Primary-source verification used arXiv, NeurIPS, PMLR/ICML, IJCAI, KDD/AAAI pages and DOI/proceedings metadata. Secondary indexes were used only for discovery when useful. Searches were decomposed into common-space construction, heterogeneous-teacher amalgamation, adaptive teacher weighting, geometry-aware aggregation, cross-model communication, and held-out-source validation because an exact terminology match is not required for anticipation.

## 3. Candidate-by-candidate findings

### 3.1 Shared Response Model — heterogeneous source spaces mapped into one shared response space

**Po-Hsuan Chen, Janice Chen, Yaara Yeshurun, Uri Hasson, James Haxby, Peter J. Ramadge. _A Reduced-Dimension fMRI Shared Response Model._ NIPS 2015.**

- Primary source: <https://papers.neurips.cc/paper_files/paper/2015/hash/b3967a0e938dc2a6340e258630febd5a-Abstract.html>
- Earliest public point verified this round: **public by 2015-12-07**, the start of NIPS 2015; no earlier preprint date was established in this round.
- Compared claim: multiple heterogeneous spaces -> common latent/shared response space under common stimuli.
- **Classification: `partial_prior_art`.**

The Shared Response Model aggregates multi-subject response data while accounting for subject-specific functional topographies. It is a strong antecedent to the broad idea that several differently organized source spaces can be mapped into a shared latent representation because the sources are observed under corresponding stimuli.

It does not anticipate Torus Assembly's model-to-model setting, externally indexed perturbation family, response-field transport, region-dependent teacher reliability, or student distillation. The source domain is neuroscience rather than pretrained embedding models, but the common-space primitive is clearly older.

### 3.2 Gromov-Wasserstein barycenters — geometry-aware aggregation without pointwise correspondence

**Gabriel Peyré, Marco Cuturi, Justin Solomon. _Gromov-Wasserstein Averaging of Kernel and Distance Matrices._ ICML 2016.**

- Primary source: <https://proceedings.mlr.press/v48/peyre16.html>
- PMLR publication metadata date: **2016-06-11**; ICML 2016 ran 20–22 June for this volume.
- Compared claim: a geometry-preserving fusion operator over heterogeneous relational spaces.
- **Classification: `adjacent_prior_work` for the current weighted Torus rule; `prior_art` for any future claim that barycentric/Fréchet aggregation of heterogeneous relational geometries is itself new.**

Peyré et al. compute a barycenter of distance/kernel matrices that need not have the same size or row correspondence. The barycenter is explicitly a Fréchet mean under a Gromov-Wasserstein-style discrepancy. Torus Assembly's current public proposal does **not** instantiate this exact method; its conceptual rule is a reliability-weighted fusion after transport. The relevance is epistemic: geometry-aware aggregation of heterogeneous relational structures is an established mathematical primitive, so novelty cannot rest on replacing arithmetic averaging with a manifold/barycentric fusion operator later.

### 3.3 Heterogeneous Knowledge Amalgamation — multiple heterogeneous teachers -> common feature space -> one student

**Sihui Luo, Xinchao Wang, Gongfan Fang, Yao Hu, Dapeng Tao, Mingli Song. _Knowledge Amalgamation from Heterogeneous Networks by Common Feature Learning._ IJCAI 2019.**

- Primary preprint: <https://arxiv.org/abs/1906.10546>
- IJCAI proceedings: <https://www.ijcai.org/Proceedings/2019/428>
- arXiv v1: **2019-06-24 12:33:24 UTC**.
- Compared claim: heterogeneous teachers -> common representation -> lightweight student.
- **Classification: `prior_art` for that broad subclaim; `partial_prior_art` for Torus Assembly as a whole.**

This is the strongest older antecedent for the broad Assembly description. Luo et al. take pretrained teachers with heterogeneous architectures and tasks, transform their features into a **common space**, and train a lightweight student to imitate the integrated knowledge. Therefore neither "heterogeneous teachers can be fused into a common feature space" nor "a student can be distilled from that common space" is independently novel in Torus Assembly.

What remains different is how correspondence is created and fused: Torus proposes the same external interventions, within-model response fields, learned transport geometry, and locally varying reliability over semantic terrain rather than direct teacher-feature transformation.

### 3.4 Adaptive Knowledge Amalgamation — teacher authority can vary per input

**Chengchao Shen, Mengqi Xue, Xinchao Wang, Jie Song, Li Sun, Mingli Song. _Customizing Student Networks From Heterogeneous Teachers via Adaptive Knowledge Amalgamation._ ICCV 2019.**

- Primary preprint: <https://arxiv.org/abs/1908.07121>
- arXiv v1: **2019-08-20 01:13:26 UTC**.
- Compared claim: heterogeneous teachers with locally/input-conditionally different authority.
- **Classification: `partial_prior_art`.**

Shen et al. use heterogeneous pretrained teachers and, for each unlabeled sample, adaptively select the teacher with the least prediction ambiguity. This does not create a spatial reliability field `rho_i(r)` over a response-derived semantic terrain, but it materially anticipates the underlying principle that **the best teacher is not globally fixed and teacher authority should depend on the current input/region**.

This boundary is reinforced by later multi-teacher distillation work. For example, Confidence-Aware Multi-Teacher Knowledge Distillation (arXiv v1 **2021-12-30 11:00:49 UTC**, <https://arxiv.org/abs/2201.00007>) assigns sample-wise reliability to teacher predictions. Consequently, local/adaptive teacher weighting is established prior work even though the Torus reliability signal and geometry are different.

### 3.5 Universal Representations — several task/domain networks aligned and distilled into one universal network

**Wei-Hong Li, Xialei Liu, Hakan Bilen. _Universal Representations: A Unified Look at Multiple Task and Domain Learning._**

- Primary preprint: <https://arxiv.org/abs/2204.02744>
- arXiv v1: **2022-04-06 11:40:01 UTC**.
- Compared claim: multiple specialized representations -> aligned universal representation / universal student.
- **Classification: `prior_art` for the broad universal-representation/distillation subclaim; `partial_prior_art` for the full Torus combination.**

Li et al. distill multiple task/domain-specific networks into a single network after aligning their representations through small adapters. This independently closes another broad novelty route: a common/universal representation distilled from multiple specialized pretrained networks is not new as a standalone architecture.

Torus remains structurally different because it proposes correspondence through controlled intervention-response fields rather than task/domain adapters and makes local transport reliability part of the assembled terrain.

### 3.6 Relative Representations — common relational coordinates for otherwise incompatible spaces

**Luca Moschella et al. _Relative representations enable zero-shot latent space communication._**

- Primary source: <https://arxiv.org/abs/2209.15430>
- arXiv v1: **2022-09-30 12:37:03 UTC**.
- Compared claim: cross-space communication without requiring absolute coordinates to agree.
- **Classification: `partial_prior_art`.**

This source was already relevant to the earlier Pontifex Torus audit and remains relevant here. It uses similarities to shared anchors to make incompatible latent spaces communicate without requiring direct agreement of their absolute coordinates. Torus's intervention-response coordinates are different from static anchor-relative coordinates, but the broader claim that shared external references can mediate communication among unaligned representation spaces is prior work.

### 3.7 Universal Sparse Autoencoders — one universal concept space across multiple pretrained models

**Harrish Thasarathan, Julian Forsyth, Thomas Fel, Matthew Kowal, Konstantinos G. Derpanis. _Universal Sparse Autoencoders: Interpretable Cross-Model Concept Alignment._**

- Primary source: <https://arxiv.org/abs/2502.03714>
- arXiv v1: **2025-02-06 02:06:16 UTC**.
- Compared claim: multiple independently pretrained models -> one shared/universal representational space.
- **Classification: `prior_art` for that broad subclaim; `partial_prior_art` for Torus Assembly as a whole.**

USAEs jointly learn a universal concept space that can reconstruct and interpret activations of multiple pretrained models, across different tasks, architectures, and datasets. That is a close modern antecedent to the high-level phrase "assemble several pretrained representation spaces into one universal/shared space."

The mechanism is substantially different: a shared sparse autoencoder rather than intervention-indexed response transport, no Torus local reliability field, and no equivalent sequential teacher-order/repeated-cycle protocol.

### 3.8 Vision Wormhole — heterogeneous model families -> hub-and-spoke common reference space

**Xiaoze Liu et al. _The Vision Wormhole: Latent-Space Communication in Heterogeneous Multi-Agent Systems._**

- Primary source: <https://arxiv.org/abs/2602.15382>
- arXiv v1: **2026-02-17 06:31:53 UTC**.
- Compared claim: scalable common reference space for heterogeneous model families plus teacher-student alignment.
- **Classification: `partial_prior_art`.**

Vision Wormhole is especially relevant because it targets heterogeneous model families with disjoint manifolds, maps their reasoning traces into a shared continuous reference space, uses a hub-and-spoke architecture to avoid pairwise `O(N^2)` translators, and trains the communication channel with teacher-student distillation. Its alignment uses per-agent mappings and shared anchor texts rather than Torus intervention-response cartography.

This means the scalable architectural idea "many heterogeneous models communicate through one reference latent hub" also predates the Torus Assembly cutoff. The remaining distinction is again the intervention-derived transport/reliability mechanism and the specific Assembly validation protocol.

### 3.9 Held-out-system validation in a shared space

**Ji-Hoon Heo, Aleksandra Joanna Wisniewska, Seo-Hyun Lee, Seong-Whan Lee. _Cross-Subject Semantic Decoding with Shared-Space Alignment for Generalized Neural Representation Learning._**

- Primary source: <https://arxiv.org/abs/2607.19394>
- arXiv v1: **2026-07-03 03:59:16 UTC**.
- Compared claim: exclude one source from shared-space learning and test transfer/generalization to that source.
- **Classification: `partial_prior_art`.**

Heo et al. estimate a shared latent space across subjects, train a semantic decoder on aligned representations, and evaluate a held-out subject by projecting it into the predefined shared space and applying the pretrained decoder without retraining the decoder. This is not the Torus held-out-teacher test: the held-out subject still receives a subject-specific projection, and the domain is neural recording rather than teacher encoders. But it is a direct methodological antecedent for treating **held-out source/system generalization as a key test that a shared space captures structure beyond the fitted sources**.

Thus the held-out-teacher idea should not be presented as a novel validation principle by itself.

## 4. Revised novelty boundary

Before the Torus Assembly cutoff, the literature already contains all of the following components or large subcombinations:

1. **multiple heterogeneous spaces mapped into one common/shared representation** (Shared Response Model and related hyperalignment literature);
2. **multiple heterogeneous teacher networks transformed into a common feature space and distilled into one student** (Luo et al. 2019);
3. **teacher authority selected or weighted adaptively per input/sample** (Shen et al. 2019 and later multi-teacher distillation);
4. **multiple task/domain representations aligned and distilled into a universal representation** (Li et al. 2022);
5. **one universal concept space jointly spanning several pretrained models** (Universal Sparse Autoencoders 2025);
6. **a hub-and-spoke shared latent reference for heterogeneous model families** (Vision Wormhole 2026);
7. **held-out-source validation of a learned shared space** (Heo et al. 2026);
8. **geometry-aware barycenters/Fréchet means over non-corresponding relational spaces** as an older mathematical primitive (Peyré et al. 2016).

Accordingly, Torus Assembly should **not** claim novelty merely from:

- combining several teachers;
- constructing a common/universal latent space;
- distilling a student from multiple heterogeneous teachers;
- assigning different weights/reliabilities to teachers depending on an input;
- using a hub-and-spoke common reference instead of pairwise translators;
- using a barycentric/Fréchet-style fusion if that is adopted later; or
- validating a shared space with a held-out source.

The narrower unresolved combination is:

> Given several frozen heterogeneous embedding models and the same externally indexed family of local interventions, measure each model through its own intervention-response field; learn transports among those response geometries without direct coordinate alignment; assign teacher authority as a region-dependent reliability over that intervention-derived terrain; sequentially fuse the transported evidence while testing teacher-order stability; freeze the resulting Assembly; distill a cheap student into it on disjoint data; and test whether the Assembly predicts the response geometry/neighborhood structure of a teacher excluded from construction.

After the searches documented in this audit, **no source public before 2026-09-18 03:02:31 UTC was located that materially anticipates that entire combination**. This is a reproducible negative-search result, not a claim that no such source exists or that Torus Assembly is first.

The main scientific novelty question has therefore moved from "can heterogeneous teachers be unified?" to the much narrower question of whether **shared controlled interventions can supply the correspondence and local reliability field from which a useful multi-teacher common geometry is assembled**.

## 5. Temporal classification after our cutoff

Recent/same-day searches around the cutoff did not locate a post-**2026-09-18 03:02:31 UTC** publication close enough to the full Assembly combination to classify as `later_independent`, `later_overlap`, `later_non_citing`, `later_citing`, or `later_derivative` in this round.

Because the cutoff is only hours old, this negative result has very low evidentiary weight. No inference about causal independence or dependence is made.

## 6. Change relative to the prior Pontifex Torus audit

`audits/prior-art/pontifex-torus-occlusion-cartography-2026-09-17.md` correctly audits the earlier cartography pivot: shared perturbations, within-space response fields, cross-field prediction, geometry, and active traversal. It cannot cover Torus Assembly because the multi-teacher Assembly claim was added later, on 18 September.

This supplement materially narrows the newer proposal in three ways:

- **Luo et al. 2019** and **Li et al. 2022** mean heterogeneous multi-teacher -> common/universal representation -> student is established prior work.
- **Shen et al. 2019** and later adaptive multi-teacher methods mean locally/input-conditionally varying teacher authority is also established at the primitive level.
- **Universal Sparse Autoencoders 2025** and **Vision Wormhole 2026** make the recent cross-model shared-space landscape substantially closer to the high-level Assembly story than a generic knowledge-distillation bibliography would suggest.

The defensible research frontier is the specific **intervention-response mechanism for correspondence, transport, and regional reliability**, plus whether that mechanism yields teacher-order-stable geometry and meaningful held-out-teacher prediction.

## 7. Search frontier / negative evidence

High-value searches did not locate an exact pre-cutoff match under combinations of `shared intervention`, `response field`, `heterogeneous teachers`, `common latent`, `transport geometry`, `regional reliability`, `held-out teacher`, `perturbation alignment`, and `multi-teacher assembly`.

The next useful search frontier is outside ordinary knowledge distillation: multi-view manifold fusion, sensor-fusion system identification under common excitation, functional-data registration, multi-subject hyperalignment variants with reliability fields, mixture-of-experts gating over latent geometry, representation stitching/model soups, and patents/theses using response-surface or transfer-operator vocabulary. Those areas may contain closer formulations even when they never use the words `teacher`, `embedding`, or `Assembly`.
