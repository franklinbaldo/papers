---
type: "Audit Report"
title: "Semantic Atlas — static neighborhood geometry and scale robustness prior-art audit — 2026-09-18"
description: "Claim-specific temporal audit of nearest-neighbor overlap, permutation-calibrated mKNN, gallery-scale robustness, and observer-specific neighborhood geometry in semantic_atlas_static_geometry.md."
tags: [semantic-atlas, prior-art, embeddings, mknn, nearest-neighbor-overlap, representation-similarity, scale-robustness, observer-specific-geometry]
timestamp: 2026-09-18T16:01:00-04:00
---

# Semantic Atlas — static neighborhood geometry and scale robustness prior-art audit — 2026-09-18

> **Status:** claim-specific temporal audit of [`semantic_atlas_static_geometry.md`](../../semantic_atlas_static_geometry.md). This record narrows the originality boundary of the static Semantic Atlas result. It does not establish exhaustive novelty, legal patent novelty, causal dependence, copying, or priority beyond the public record and searches described here. An older Semantic Atlas frontier scan remains useful historical evidence, but it did not reconstruct the cutoff of this later terminal static claim and did not include the closest 2026 scale-analysis papers identified below.

## 1. Claims audited

The static paper contains a narrow empirical conjunction. To avoid treating a result as one indivisible novelty claim, this audit decomposes it into five claims:

- **C1 — neighborhood-overlap comparison:** two text/sentence embedding observers can be compared by the overlap of the nearest-neighbor sets they induce over the same inputs;
- **C2 — null-calibrated local alignment:** local-neighborhood agreement should be evaluated against a broken-correspondence/permutation null rather than interpreted from raw overlap alone;
- **C3 — gallery-scale robustness:** local-neighborhood alignment should be re-evaluated as the candidate gallery grows substantially, because sparse galleries may make two representations look more similar than they are at finer resolution;
- **C4 — observer-specific gap:** surviving cross-observer overlap can coexist with much higher within-observer stability, so the correct conclusion may be partial shared locality plus strongly observer-specific discrete neighborhoods rather than either universal geometry or total incommensurability;
- **C5 — full registered conjunction:** on the same frozen corpus of 120,000 arXiv abstracts, Qwen3-Embedding and all-MiniLM-L6-v2 are compared using exact cosine neighborhoods over 32 preregistered stratified galleries at each size from 1,000 to 100,000, permutation-calibrated mKNN@5 remains above the registered scale gate (`R=0.785935`, `S(100k)=0.319519`), and the 100k cross-observer score remains far below a preregistered same-observer stability ceiling (`U=0.928384`, `Q=C/U=0.344167`).

The audit distinguishes novelty of the **components and generic phenomenon** from novelty of this particular preregistered experiment and result.

## 2. Temporal reconstruction of our claim

### 2.1 Relevant cutoff: 2026-08-29 07:47:11 UTC

The timestamp at the top of the current paper is not used as the priority date, and neither is the creation date of the repository.

The large-gallery experiment lived publicly in PR #389 before the result existed:

- PR #389, `experiment: run Semantic Atlas gate at 100k`, was opened on **2026-08-27 03:40:42 UTC**;
- its initial commits preregistered and executed the scale test but did not yet establish the terminal empirical claim;
- commit [`06063aecceeb3ba3cd71e6c4757aebfe2ea18a11`](https://github.com/franklinbaldo/papers/commit/06063aecceeb3ba3cd71e6c4757aebfe2ea18a11), **2026-08-29 07:47:11 UTC**, added `experiments/semantic_atlas/SCALE_MKNN_RESULTS.md` with the terminal classifications `scale_stable`, `observer_specific_gap_survives`, and `static paper released: true`, together with the decision statistics later reported by the paper;
- PR #399 was opened later to turn that frozen evidence into `semantic_atlas_static_geometry.md`; its own description states that #389 owns the protocol, terminal Findings Record, and durable data assets.

Accordingly, the earliest public GitHub date located for **the terminal static empirical claim C5** is **2026-08-29 07:47:11 UTC**, and that is the cutoff used in this audit.

The broader methodological ideas C1–C4 existed in earlier Semantic Atlas drafts and preregistrations, but using an earlier date would only make a priority claim easier to satisfy. This audit conservatively uses the later terminal-result cutoff when asking whether published work already occupied the method/phenomenon around C5.

## 3. Search protocol

The search was claim-led rather than title-led. Sources included arXiv version histories and full text, ICML/PMLR material, ACL Anthology, ACM survey material, publisher/project pages, and targeted web discovery. Primary arXiv/venue records were preferred for dates and substantive classification.

Representative searches included:

- `nearest neighbor overlap sentence embedders`
- `nearest neighbor overlap embedding models same inputs`
- `mutual kNN representation alignment`
- `local neighborhood representation similarity neural networks`
- `permutation calibrated representation similarity mKNN`
- `permutation null nearest neighbor overlap representations`
- `gallery size mutual kNN representation alignment scale`
- `dense gallery representation alignment nearest neighbors`
- `language language model mutual kNN gallery scale`
- `within modality alignment language models gallery size`
- `embedding models neighborhood overlap MTEB`
- `shared local geometry language model embeddings`
- exact-title searches for `Scale-Robust Partial Local Alignment and Observer-Specific Neighborhood Geometry`;
- exact-author/title searches combining `Franklin Baldo`, `Franklin Silveira Baldo`, `Semantic Atlas`, and the terminal statistic `0.319519`.

Negative searches are evidence only about these bounded searches. “Not located” does not mean “does not exist.”

## 4. Pre-cutoff findings

### 4.1 Lin & Smith (2019): nearest-neighbor overlap between sentence embedders is direct prior art

**Work:** Lucy H. Lin and Noah A. Smith, **“Situating Sentence Embedders with Nearest Neighbor Overlap.”** arXiv:1909.10724.

- first public arXiv version: **2019-09-24 06:03:35 UTC**;
- <https://arxiv.org/abs/1909.10724>;
- status: arXiv preprint.

The paper proposes **Nearest Neighbor Overlap (N2O)** as a task-agnostic way to compare embedders: for the same inputs, two embedders are more similar when the induced nearest-neighbor sets overlap. It explicitly focuses on sentence embedders while noting that the method applies to texts of other sizes.

**Compared claim:** C1.

**Classification:** `prior_art`.

**Consequence:** Semantic Atlas cannot claim originality for comparing sentence/text embedding models via nearest-neighbor-set overlap. That component was explicit by 2019.

### 4.2 Huh et al. (2024): mutual-kNN as a representation-alignment metric is prior art

**Work:** Minyoung Huh, Brian Cheung, Tongzhou Wang, Phillip Isola, **“The Platonic Representation Hypothesis.”** arXiv:2405.07987; ICML 2024.

- arXiv v1: **2024-05-13 17:58:30 UTC**;
- <https://arxiv.org/abs/2405.07987>;
- status: ICML 2024 / arXiv.

The paper defines representational alignment through induced similarity structures and uses a mutual nearest-neighbor metric equal to the mean overlap of two models’ k-nearest-neighbor sets, normalized by `k`. It applies this metric across networks and modalities.

**Compared claims:** C1, methodological component of C2/C3.

**Classification:** `prior_art` for mKNN-style local-neighborhood representation alignment; `adjacent_prior_work` for the later scale/calibration questions.

**Consequence:** mKNN itself, and interpreting it as local representational alignment, are not Semantic Atlas contributions.

### 4.3 Lee et al. (2025): shared local geometry across language-model embeddings

**Work:** Andrew Lee, Melanie Weber, Fernanda Viégas, Martin Wattenberg, **“Shared Global and Local Geometry of Language Model Embeddings.”** arXiv:2503.21073.

- arXiv v1: **2025-03-27 01:17:06 UTC**;
- <https://arxiv.org/abs/2503.21073>;
- later conference publication: COLM 2025.

The paper reports common local geometric structure across token embeddings of language models, using local linear structure and intrinsic-dimensionality analyses rather than the exact Semantic Atlas mKNN protocol.

**Compared claims:** C4 and the broad interpretation surrounding C5.

**Classification:** `adjacent_prior_work`.

**Consequence:** the broad proposition that independently trained language models can share nontrivial local geometry predates the static Atlas result, but this work does not anticipate the registered mKNN scale/ceiling conjunction.

### 4.4 Naber, Frassinelli & Schulte im Walde (2025): semantic-neighborhood overlap varies by observer/modality

**Work:** Sven Naber, Diego Frassinelli, Sabine Schulte im Walde, **“Evaluating Textual and Visual Semantic Neighborhoods of Abstract and Concrete Concepts.”** *SEM 2025.

- public proceedings: **2025-11**;
- <https://aclanthology.org/2025.starsem-1.11/>;
- DOI: 10.18653/v1/2025.starsem-1.11.

The paper systematically compares nearest-neighbor neighborhoods across textual and visual semantic spaces. Same-modality models exhibit stronger neighborhood alignment than cross-modal models, and the measured alignment changes with neighborhood size.

**Compared claims:** C1, C4.

**Classification:** `partial_prior_art`.

**Consequence:** observer/modality dependence of semantic-neighborhood overlap was already an explicit empirical object. It does not, however, perform the Atlas gallery-scale experiment or use the same-observer stability ceiling.

### 4.5 Gröger, Wen & Brbić (2026): permutation null-calibration plus surviving local-neighborhood agreement is direct prior art

**Work:** Fabian Gröger, Shuo Wen, Maria Brbić, **“Revisiting the Platonic Representation Hypothesis: An Aristotelian View.”** arXiv:2602.14486; ICML 2026.

- arXiv v1: **2026-02-16 06:01:23 UTC**;
- <https://arxiv.org/abs/2602.14486>;
- status: ICML 2026 / arXiv.

The paper shows that representation-similarity metrics can have scale-dependent null behavior and introduces a **permutation-based null-calibration framework**. When applied to representation alignment, global spectral convergence is substantially weakened while local neighborhood similarity, including mKNN, retains significant agreement. Its null explicitly breaks sample correspondence by permutation while retaining marginal representation structure.

**Compared claims:** C2, parts of C4/C5.

**Classification:** `prior_art` for permutation-calibrated representation similarity and for the broad claim that local-neighborhood agreement can survive such calibration; `partial_prior_art` for C5.

**Consequence:** neither “use permutation nulls for representation similarity” nor “calibrated local alignment survives” can carry originality for Semantic Atlas. The residual claim must be tied to the particular text-embedding, large-gallery and stability-ceiling experiment.

### 4.6 Koepke et al. (2026): gallery-scale mKNN testing and stable language-language alignment are especially close prior art

**Work:** A. Sophia Koepke, Daniil Zverev, Shiry Ginosar, Alexei A. Efros, **“Back into Plato’s Cave: Examining Cross-modal Representational Convergence at Scale.”** arXiv:2604.18572.

- arXiv v1: **2026-04-20 17:56:02 UTC**;
- <https://arxiv.org/abs/2604.18572>;
- status: arXiv preprint.

This is the closest pre-cutoff work located in this run for C3. It argues that mKNN measured on ~1k samples can be misleading because the gallery is sparse, and explicitly increases gallery density up to millions of samples. For cross-modal vision-language pairs, fixed-small-`k` alignment falls sharply as the gallery grows.

Crucially for the static Atlas claim, the supplementary control asks whether mKNN necessarily collapses with gallery size even **within a modality**. It compares OpenLlama-3b with OpenLlama-13b and reports that language-language mKNN@1 remains between approximately **0.59 and 0.62 across gallery scales**; a DINOv2 vision-model pair is also comparatively stable. The paper therefore already demonstrates, before our cutoff, both the importance of gallery-scale testing and the empirical possibility that two language-model representation spaces retain stable local-neighborhood overlap under densification.

The work also reports exact nearest-neighbor computation with normalized features and discusses null calibration following Gröger et al. in supplementary scale analyses.

**Compared claims:** C3, C4, C5.

**Classification:** `prior_art` for the broad C3 method/phenomenon (“test mKNN under gallery densification; same-modality language-model overlap can remain relatively stable at scale”); `partial_prior_art` for C4/C5.

**Consequence:** the static Atlas paper must not frame generic **scale-robust cross-model local-neighborhood agreement** as an unoccupied phenomenon. What remains distinct is the precise same-content text-embedding experiment, its preregistered scale gate, permutation calibration, and its comparison with a separately constructed same-observer stability ceiling.

### 4.7 Myntti et al. (2026): nearest-neighbor overlap is already a diagnostic across modern text embedding models

**Work:** Amanda Myntti, Jenna Kanerva, Veronika Laippala, Filip Ginter, **“Structure Retention in Embedding Spaces as a Predictor of Benchmark Performance.”** arXiv:2605.22202.

- arXiv v1: **2026-05-21 09:05:55 UTC**;
- <https://arxiv.org/abs/2605.22202>;
- status: arXiv preprint.

The paper evaluates 25 contemporary embedding models across multiple MTEB tasks and uses nearest-neighbor overlap as a measure of retained local information, finding strong correlations with benchmark performance.

**Compared claims:** C1 and the text-embedding scope of C5.

**Classification:** `partial_prior_art`.

**Consequence:** by mid-2026, nearest-neighbor overlap was not merely a sentence-embedder comparison idea from 2019; it was actively used as a structural diagnostic over broad modern embedding-model panels.

### 4.8 Caffagni et al. (2026): mKNN local topology is an explicit training/alignment object

**Work:** Davide Caffagni et al., **“Mind the Heads: Topological Representation Alignment for Multimodal LLMs.”** arXiv:2606.23885.

- arXiv v1: **2026-06-22 19:30:30 UTC**;
- <https://arxiv.org/abs/2606.23885>;
- status: arXiv preprint.

The paper explicitly describes local neighborhood relationships as the topological structure of representations, measures them with mKNN, and trains a differentiable proxy to align such local structures at attention-head level.

**Compared claims:** C1/C2 interpretation.

**Classification:** `adjacent_prior_work`.

**Consequence:** this reinforces that “local topology measured by mKNN” was already a recognized representation-alignment object before the Atlas result, though the optimization setting differs materially.

### 4.9 Shimizu et al. (2026-08-28): very close temporal neighbor, but not an anticipation of C5

**Work:** Yuria Shimizu, Soh Takahashi, Takato Horii, Masafumi Oizumi, **“Relational Knowledge Distillation Brings DNN Representations Close Enough to Humans to Be Aligned Without Supervision.”** arXiv:2608.27877.

- arXiv v1: **2026-08-28 03:32:39 UTC**, approximately 28 hours before the Atlas terminal-result cutoff;
- <https://arxiv.org/abs/2608.27877>;
- status: arXiv preprint.

This vision/human-representation study distinguishes global structural alignment from **local nearest-neighbor overlap**, finding that relational distillation improves the global alignment responsible for unsupervised matching while local human-DNN nearest-neighbor overlap remains largely unchanged.

**Compared claim:** broad C4 distinction between global/common structure and local-neighborhood identity.

**Classification:** `adjacent_prior_work`.

**Consequence:** it is temporally important because it appeared immediately before our cutoff, but it does not anticipate the Atlas scale experiment or its text-embedding result.

## 5. Classification after this audit

| Claim | Classification | Reason |
|---|---|---|
| C1 — compare text/sentence embedders by nearest-neighbor overlap | `prior_art` | Lin & Smith 2019 directly state this method; later embedding work broadens it. |
| C2 — permutation-calibrated local-neighborhood alignment | `prior_art` | Gröger et al. 2026 introduce a general permutation calibration and show local-neighborhood similarity survives it. |
| C3 — evaluate mKNN as gallery density grows; local agreement can be stable for language-language model pairs | `prior_art` | Koepke et al. 2026 explicitly test scale and report stable OpenLlama-vs-OpenLlama mKNN across gallery sizes. |
| C4 — partial shared locality together with a large observer-specific/local-identity gap | `partial_prior_art` | Naber et al., Gröger et al., and Koepke et al. collectively occupy substantial pieces; the exact registered same-observer ceiling ratio used here was not located. |
| C5 — full frozen Atlas experiment and terminal conjunction | `partial_prior_art` | Every major methodological ingredient has material pre-cutoff precedent, but no pre-cutoff source located in this search combines the same two text embedding observers, same-content 120k arXiv corpus, 32 stratified galleries over 1k→100k, permutation-calibrated mKNN, registered retention gate, and a separately constructed same-observer stability ceiling yielding the reported conjunction. |

The material change from a weak novelty reading is therefore substantial: **the broad method and broad scale-robustness phenomenon are occupied by prior art**. The defensible contribution is much narrower: a preregistered empirical measurement and boundary result in a specific text-embedding setting, with a particular stability reference and reproducible terminal evidence.

This does not make the result scientifically uninteresting. It changes what kind of contribution it is. The work is better positioned as a controlled same-modality/text-embedding extension and quantified boundary test of an already active representation-geometry literature, rather than as invention of neighborhood-overlap comparison, calibrated local alignment, or gallery-scale robustness testing.

## 6. Later work and citation/dependency check

Targeted post-cutoff searches used the exact paper title, `Semantic Atlas`, both `Franklin Baldo` and `Franklin Silveira Baldo`, combinations with `mKNN`, `observer-specific geometry`, and the distinctive terminal value `0.319519`.

No post-**2026-08-29 07:47:11 UTC** work was located in this run that was both materially similar enough and sufficiently evidenced to classify as `later_overlap`, `later_non_citing`, `later_citing`, or `later_derivative`.

That is a bounded negative result, not evidence that no such work exists. In particular, this run makes **no claim of copying, derivation, priority violation, or failure to credit** by any later author.

## 7. Novelty boundary to carry forward

A defensible formulation after this audit is:

> Prior work already established nearest-neighbor overlap for sentence/text embedder comparison, mutual-kNN representation alignment, permutation-null calibration, and the need to test mKNN under gallery densification; pre-cutoff work also showed that language-language model neighborhood overlap can remain comparatively stable as galleries grow. After targeted searches across those literatures, no material pre-cutoff antecedent was located for the **full registered conjunction** reported here: same-content Qwen3-Embedding versus MiniLM over 32 stratified arXiv galleries from 1k to 100k, permutation-calibrated exact-cosine mKNN satisfying a frozen retention gate while remaining far below a preregistered same-observer stability ceiling. This is a bounded search result, not a claim of firstness.

Any future abstract, README, submission metadata, or related-work section should preserve that narrower boundary.

## 8. Audit trail and future search targets

The strongest remaining uncertainty is not whether nearest-neighbor overlap or gallery-scale testing existed — they did — but whether an earlier paper in NLP/IR, model-similarity, manifold comparison, or neuroscience independently combined **cross-observer neighborhood overlap with an empirically estimated within-observer stability ceiling** in a large same-content gallery experiment.

High-value next searches therefore include:

- reliability-normalized neighborhood overlap across repeated embeddings/models;
- noise-ceiling or split-half-ceiling normalization of kNN graph similarity;
- representational similarity analysis using local-neighborhood scores divided by within-subject/model reliability;
- large-corpus text-embedding geometry comparisons before August 2026 that may use terms such as `neighborhood preservation`, `trustworthiness`, `continuity`, `graph agreement`, or `topological similarity` rather than `mKNN`;
- citation-forward searches from Lin & Smith (2019), Huh et al. (2024), Gröger et al. (2026), and Koepke et al. (2026).

A later audit should revise this record, rather than silently replacing it, if any of those searches reveal a closer antecedent or a post-cutoff overlapping work.
