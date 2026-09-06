---
type: "Technical Paper"
title: "Semantic Atlas: Scale-Robust Partial Local Alignment and Observer-Specific Neighborhood Geometry"
description: "Empirical paper on cross-model local-neighborhood agreement across exact cosine galleries from 1k to 100k arXiv abstracts, showing above-chance scale-robust overlap that remains far below same-observer stability ceilings."
tags: [semantic-atlas, embeddings, representation-alignment, observer-specific-geometry, mknn, exact-knn, arxiv]
timestamp: 2026-08-29T08:10:00Z
---

# Semantic Atlas: Scale-Robust Partial Local Alignment and Observer-Specific Neighborhood Geometry

**Franklin Baldo**  
Independent Researcher  
franklinbaldo@gmail.com

---

> **Empirical scope.** This paper reports the static result selected by the preregistered large-gallery gate in `experiments/semantic_atlas/protocol_scale_mknn.md`. It does not claim observer-independent semantic geometry, causal mechanism, temporal dynamics, Blackwell ordering, or reconstructability of one embedding space from another. Dynamic susceptibility remains a separate downstream programme.

## Abstract

Representation alignment can make embeddings from independently trained models comparable in a common coordinate frame, but coordinate comparability does not imply that the models induce the same discrete relational structure. We test that distinction at scale with two frozen text-embedding observers, Qwen3-Embedding and all-MiniLM-L6-v2, on a frozen corpus of 120,000 arXiv abstracts. The primary analysis uses exact cosine k-nearest-neighbor sets on 32 preregistered stratified random galleries at each gallery size from 1,000 to 100,000 documents. Agreement is measured with permutation-calibrated mutual k-nearest-neighbor overlap, with k=5 primary, and compared against same-observer stability ceilings.

The primary curve declines smoothly with gallery size but does not collapse. Calibrated cross-observer agreement is 0.4065 at N=1,000 and 0.3195 at N=100,000, retaining 78.6% of the small-gallery signal. The preregistered scale gate required both retention R >= 0.75 and S(100k) >= 0.20; both pass. At N=100,000, however, cross-observer agreement remains far below the conservative same-observer stability ceiling U=0.9284, yielding Q=C/U=0.3442 and passing the preregistered observer-specific gate Q <= 0.80.

The result supports a narrow but useful conclusion: independently trained embedding models can exhibit **partial local relational alignment that remains above chance and reasonably stable with scale while preserving strongly observer-specific discrete neighborhood structure**. A shared operational coordinate frame is therefore compatible with substantial disagreement about which nearby items constitute the local semantic neighborhood. The Semantic Atlas is best treated not as one universal map but as a comparison framework in which observer-specific relational structure can be measured explicitly.

**Keywords:** representation alignment, embedding geometry, nearest neighbors, semantic similarity, observer dependence, scale robustness, mKNN

---

## 1. Question

Suppose two embedding models can be compared on the same collection of texts. Even if their coordinates can be aligned, two different questions remain:

1. do the models place semantically related items near one another often enough to produce above-chance local agreement; and
2. do they actually induce the same local relational graph?

These questions are not equivalent. Coordinate alignment can preserve broad correspondence while nearest-neighbor identities remain observer-specific. Conversely, small-gallery neighborhood disagreement can be a finite-gallery artifact: as the gallery grows, calibrated agreement might collapse toward chance or converge toward a common structure.

The experiment therefore asks whether cross-observer local agreement survives a large-gallery test, and whether surviving agreement approaches the stability one obtains when the observer is held fixed.

The preregistered decision rule was deliberately asymmetric. The static paper would be released only if cross-observer agreement remained both nontrivial and scale-stable, while also remaining materially below a same-observer stability ceiling. A collapse would demote the pilot result to a small-gallery artifact. Near-equivalence to the same-observer ceiling would weaken the case that discrete relational structure is meaningfully observer-specific.

## 2. Frozen design

### 2.1 Corpus and semantic unit

The frozen corpus contains 120,000 arXiv abstracts selected from first submissions dated 2025-07-01 through 2026-06-30. Selection is deterministic by ascending SHA-256 of base arXiv id. The semantic unit is the full normalized abstract.

Every included abstract fits within 256 WordPieces under the pinned MiniLM tokenizer, and runtime truncation is forbidden. This matters because the two observers must receive the same semantic content. A comparison in which one model sees a longer text window would confound observer identity with input scope.

### 2.2 Observers

The primary observer pair is frozen before the terminal run:

- Qwen3-Embedding, with its registered revision and inference settings;
- all-MiniLM-L6-v2, likewise pinned.

The experiment does not treat either observer as ground truth. Each induces a neighborhood relation over the same corpus.

### 2.3 Galleries

For each gallery size

\[
N \in \{1{,}000, 2{,}500, 5{,}000, 10{,}000, 25{,}000, 50{,}000, 100{,}000\},
\]

32 preregistered stratified random galleries are evaluated. Chronological prefixes are retained only as descriptive sensitivity analyses and do not determine the primary result.

All neighborhood sets use exact cosine k-nearest-neighbor search. The primary neighborhood size is k=5, with k=10 and k=20 reserved as sensitivities.

### 2.4 Calibrated local agreement

Raw neighborhood overlap rises mechanically with k/N. The decision-bearing quantity is therefore permutation-calibrated mutual k-nearest-neighbor agreement, denoted here by S(N,k). Correspondence permutations provide the null expected under broken cross-observer identity while preserving the gallery-level structure needed for calibration.

For the primary k=5 curve, define

\[
R = \frac{S(100{,}000,5)}{S(1{,}000,5)}.
\]

The preregistered scale-stability gate is

\[
R \ge 0.75
\quad\text{and}\quad
S(100{,}000,5) \ge 0.20.
\]

### 2.5 Same-observer stability ceiling

Exact same-model/same-gallery nearest-neighbor agreement is trivially one and is therefore not an informative ceiling. The protocol instead defines a preregistered same-observer stability operator and reports its gallery-jackknife ceiling by N.

Let U(N) be the conservative same-observer ceiling and C(N) the calibrated cross-observer agreement. The observer-specific gap is summarized as

\[
Q(N) = \frac{C(N)}{U(N)}.
\]

The preregistered observer-specific gate at N=100,000 is

\[
Q(100{,}000) \le 0.80.
\]

## 3. Results

### 3.1 Primary k=5 curve

| Gallery N | Calibrated mKNN median | 95% gallery interval | Qwen ceiling | MiniLM ceiling |
|---:|---:|---:|---:|---:|
| 1,000 | 0.4065 | [0.3934, 0.4176] | 0.9314 | 0.9339 |
| 2,500 | 0.3815 | [0.3692, 0.3915] | 0.9273 | 0.9280 |
| 5,000 | 0.3637 | [0.3558, 0.3691] | 0.9273 | 0.9284 |
| 10,000 | 0.3504 | [0.3464, 0.3557] | 0.9301 | 0.9299 |
| 25,000 | 0.3348 | [0.3326, 0.3366] | 0.9295 | 0.9288 |
| 50,000 | 0.3260 | [0.3245, 0.3280] | 0.9290 | 0.9290 |
| 100,000 | 0.3195 | [0.3190, 0.3202] | 0.9284 | 0.9289 |

The curve declines monotonically but smoothly. It does not show the rapid collapse expected if the pilot overlap were mainly a small-gallery coincidence.

At the two preregistered endpoints,

\[
S(1{,}000)=0.406546,
\qquad
S(100{,}000)=0.319519.
\]

Thus

\[
R=0.785935.
\]

Both scale thresholds pass:

\[
0.785935 \ge 0.75,
\qquad
0.319519 \ge 0.20.
\]

The terminal classification is therefore `scale_stable` under the frozen rule.

### 3.2 Observer-specific gap

At N=100,000, the conservative same-observer ceiling is

\[
U(100{,}000)=0.928384.
\]

The cross-observer value is

\[
C(100{,}000)=0.319519,
\]

so

\[
Q=\frac{0.319519}{0.928384}=0.344167.
\]

This is well below the preregistered upper bound of 0.80. The terminal classification is therefore `observer_specific_gap_survives`.

The result is stronger than saying that two models are imperfectly correlated. The same texts, same gallery, same metric family, exact neighbor search, and stable within-observer neighborhoods still produce substantially different discrete local neighborhoods across observers.

### 3.3 What the gate does and does not establish

The experiment establishes the conjunction that motivated the static paper:

- cross-observer local agreement is above the calibrated chance baseline;
- the agreement retains most of its N=1,000 magnitude at N=100,000;
- cross-observer agreement remains far below within-observer stability.

It does not establish that one observer is more correct, that the two geometries are ordered by refinement, or that the disagreement arises from a single latent mechanism.

## 4. Interpretation: shared-ish locality, different neighborhoods

A useful way to read the result is to distinguish three levels.

First, there is **correspondence**: both observers process the same text identities and produce enough common local structure for calibrated overlap to remain materially above chance.

Second, there is **scale robustness**: enlarging the candidate gallery by two orders of magnitude reduces but does not erase that local agreement.

Third, there is **observer specificity**: the cross-observer neighborhood relation remains much less stable than the relation obtained when the observer itself is held fixed.

This combination rules out two simplistic pictures.

The first is a universal-neighborhood picture in which alignment should make the models converge on essentially the same local graph. The observed Q≈0.344 is difficult to reconcile with that strong version.

The second is a total-incommensurability picture in which cross-observer local relations should dissolve at scale. They do not: S(100k)≈0.320 and R≈0.786 under the frozen calibration.

The more defensible middle position is that semantic observers share some local relational regularities while imposing substantial model-specific structure on which candidates count as nearest neighbors.

## 5. Implication for the Semantic Atlas

The original Semantic Atlas idea can be made more precise by separating a **comparison frame** from an **observer-specific map**.

A common frame is useful because it lets us ask correspondence questions across models. But the atlas itself should not be identified with that frame. The empirical object is the family of relations induced by each observer:

\[
\mathfrak A = (\mathcal Q, \{G_M\}_{M\in\mathcal M}),
\]

where \(\mathcal Q\) is an operational comparison frame and \(G_M\) is the local relational graph induced by observer M.

The large-gallery result says that the graphs are neither independent nor interchangeable. They overlap substantially more than chance while remaining far apart relative to same-observer stability.

This formulation is intentionally static. It is already sufficient to motivate several downstream questions without presuming answers:

- which document regions show the largest observer disagreement;
- whether disagreement is explained by density, hubness, anisotropy, lexical specialization, or task-domain structure;
- whether the cross-observer gap persists across a broader encoder panel;
- whether dimensionality-matched or architecture-matched controls narrow the gap;
- whether observer-specific local geometry predicts later differences in retrieval, ranking, or generative behavior.

These are consequences of the static result, not evidence already contained in it.

## 6. Relation to dynamic hypotheses

Earlier Semantic Atlas drafts placed model-specific transition dynamics, reachability, navigation, and control near the center of the claim. Those remain legitimate research targets, but the present experiment does not validate them.

Pilot analyses found large differences in first-churn survival and suggested order-invariant local susceptibility, while chronology-specific excess was not detected under a severely underpowered design. Those observations are useful for designing the next experiment, not for upgrading the static gate into a temporal or causal result.

The evidential order is therefore:

1. **static result established here:** partial local alignment survives scale while a large observer-specific gap remains;
2. **next explanatory layer:** test which registered geometric variables predict observer disagreement or susceptibility;
3. **only then:** test dynamic transfer, reachability, planning, or control under separately frozen protocols.

This ordering prevents a common failure mode in exploratory representation research: allowing an interesting downstream mechanism to become the explanation of an upstream effect before the mechanism itself has survived a confirmatory test.

## 7. Limitations

### 7.1 Two observers

The primary result is based on one frozen pair of encoders. A broader panel is necessary before claiming that the observed gap is characteristic of embedding models in general.

### 7.2 One corpus family

The corpus consists of arXiv abstracts from a registered one-year period. Scientific abstracts are diverse but structurally specialized. Legal text, dialogue, web prose, code, multilingual corpora, and long-form documents may produce different cross-observer relations.

### 7.3 Metric and neighborhood choice

The primary analysis uses exact cosine kNN and k=5. Sensitivities at other k values are informative but do not remove the dependence on a local-neighborhood operationalization.

### 7.4 Ceiling semantics

The same-observer ceiling is a registered stability reference, not a metaphysical maximum. Its role is to prevent exact self-agreement (=1) from becoming a trivial comparator and to quantify how much relational stability is available when observer identity is not changed.

### 7.5 Mechanism remains open

The experiment does not identify why the observers disagree. Dimensionality, architecture, training corpus, objective, normalization, anisotropy, and semantic specialization are plausible contributors. A preserved post-hoc Qwen 1024→384 dimensionality diagnostic makes raw output dimension alone an implausible complete explanation of the earlier pilot gap, but it cannot alter the terminal gate and is not a causal decomposition.

## 8. Falsifiable next tests

The static result earns follow-up only if the follow-up is capable of weakening it.

A useful next panel should therefore freeze additional encoders and ask whether the pairwise pattern generalizes. The key outcomes are not merely more significant p-values but changes in the geometry of the claim:

- **generalization:** multiple observer pairs show S(N) above calibrated chance with retention comparable to the primary pair while Q remains materially below one;
- **architecture-specific boundary:** the effect clusters by model family or training objective;
- **dimensionality boundary:** matched-dimensionality controls substantially close the gap;
- **corpus boundary:** the effect weakens or disappears outside scientific abstracts;
- **collapse:** larger or differently structured galleries drive calibrated overlap toward the null.

For the dynamic programme, the next confirmatory target should be observer-specific local susceptibility averaged over randomized arrival orders, with density, boundary gap, hubness, and basal churn preregistered as candidate predictors or covariates. Chronology-specific flow should not be promoted unless a separately powered design detects it.

## 9. Conclusion

The large-gallery Semantic Atlas gate produced a clean middle result. Two frozen embedding observers do not converge to the same discrete local semantic graph, but neither do their local relations dissolve into chance as the gallery grows.

Across exact cosine galleries from 1,000 to 100,000 arXiv abstracts, calibrated cross-observer mKNN@5 declines from 0.4065 to 0.3195 and retains 78.6% of its small-gallery signal. At N=100,000 the same-observer stability ceiling remains about 0.928, leaving cross-observer agreement at only 34.4% of that ceiling. Both preregistered gates pass.

The narrow conclusion is therefore the useful one: **local semantic structure is partially shared, scale-robust over the tested regime, and still strongly observer-specific at the level of discrete nearest-neighbor relations.**

That is enough to justify an Atlas as a comparative object. The map should not be assumed to be universal. The empirical task is to measure what different observers share, where they disagree, and which downstream behaviors those disagreements actually predict.

---

## Reproducibility and provenance

The terminal findings record is `experiments/semantic_atlas/SCALE_MKNN_RESULTS.md` on the scale-gate branch and records the preregistered disposition `scale_stable`, `observer_specific_gap_survives`, `static paper released=true`.

The frozen protocol, corpus manifest, exact-draw code, aggregate results, embeddings manifests, and terminal figure are preserved under `experiments/semantic_atlas/` and in the durable prerelease `semantic-atlas-scale-v1-data`. The primary corpus hash is `3333172fb665cd6de92117f6a825de7bb250c4b18a248d74acbec810405f89c8`.

No threshold, corpus rule, model revision, gallery schedule, or terminal classification rule was changed after observing the N=100k outcome.
