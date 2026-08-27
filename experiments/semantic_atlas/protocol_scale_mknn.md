---
type: "Protocol"
title: "Semantic Atlas — Large-Scale Relational Geometry v1"
description: "Pre-registered scale test of cross-model local-neighborhood agreement on post-release arXiv abstracts, with exact kNN, gallery-size calibration, same-observer stability ceilings, and a secondary encoder panel."
tags: [semantic-atlas, preregistration, embeddings, mknn, arxiv, exact-knn, scale]
timestamp: 2026-08-26T19:45:00Z
---

# Semantic Atlas — Large-Scale Relational Geometry v1

## Scientific question

Does the pilot observation — aligned coordinates with only partial local-neighborhood agreement between Qwen3-Embedding-0.6B and all-MiniLM-L6-v2 — survive a much larger gallery once chance overlap, gallery size, and same-observer instability are controlled?

This protocol is frozen **before** any large-corpus embeddings are computed.

The primary experiment is static. Chronological growth and dynamic susceptibility are secondary and cannot rescue a failed static gate.

The same-repository N=382 result in #388 is a pilot extension, not this gate. Its emitted machine label is preserved as historical output but has no authority to release the paper; only Sections 6 and 7 below decide #379.

## 1. Corpus

### 1.1 Source and temporal eligibility

Source: arXiv metadata harvested from the official OAI endpoint.

A record is eligible only when its **first submission (`created`) is from 2025-07-01 through 2026-06-30 inclusive**.

This is intentionally stronger than relying on an undocumented training cutoff. Qwen3-Embedding was publicly released in June 2025; papers first submitted after 2025-07-01 could not have been in the released weights.

### 1.2 Unit of analysis: full abstract, never full paper

The semantic unit is the normalized arXiv **abstract only**.

No title, authors, body text, references, comments, or category labels are included in the embedding input.

The exact same Unicode abstract string is supplied to every observer.

### 1.3 Context-window guard

`sentence-transformers/all-MiniLM-L6-v2@1110a24` is the limiting tokenizer.

An abstract is eligible only if its full tokenized length, **including special tokens and with truncation disabled**, is `<= 256` WordPieces under that pinned tokenizer.

The encoder call must run with truncation disabled. Any runtime truncation is a hard failure.

This prevents Qwen from seeing content that MiniLM cannot see.

### 1.4 Deduplication and sample freeze

Records are keyed by base arXiv id. One record per base id.

After eligibility filtering, compute `sha256(arxiv_id)` and select the first **120,000** records by hash order as the frozen master corpus.

If fewer than 120,000 eligible records remain, the run fails and the corpus rule must be revised in a new protocol version before embeddings are computed.

For chronological analyses, the same frozen 120,000 are sorted by first-submission timestamp; chronology never changes corpus membership.

### 1.5 Categories

The first arXiv category listed in OAI metadata is recorded as `primary_category`.

Category is **never** part of the embedding input.

Category is used only for:
- stratified random-gallery sampling;
- external validation via neighborhood category purity;
- secondary stratified analyses.

## 2. Observers

### Primary pair

1. `Qwen/Qwen3-Embedding-0.6B@97b0c61`
   - native dimension 1024;
   - no retrieval/query instruction;
   - L2-normalized output.

2. `sentence-transformers/all-MiniLM-L6-v2@1110a24`
   - dimension 384;
   - no instruction;
   - L2-normalized output.

The primary pair is continuous with v1 and alone determines the main confirmatory claims.

### Within-Qwen dimension control

Because Qwen3-Embedding supports Matryoshka/custom dimensions, report Qwen at:
- 384;
- 768;
- 1024 dimensions.

Dimension-reduced Qwen vectors are formed by the model-supported prefix truncation convention followed by L2 renormalization. This is a control, not a new observer.

Before large-corpus embeddings, the preserved v1 matrices were also subjected to a post-hoc 1024→384 dimensionality diagnostic (`artifacts/qwen_384d_dimension_check.json`; reproducible with `scripts/run_qwen_dimension_check.py`). Qwen's first-384-dimension RMST remained 39.67 versus MiniLM's 5.83; across 2,000 Gaussian projections, median Qwen RMST was 41.83 and 99.8% exceeded MiniLM by at least 20 added documents. This makes raw output dimensionality alone an implausible explanation of the v1 gap. It remains a secondary, post-hoc diagnostic and cannot change the large-scale static gate.

### Secondary encoder panel

Exploratory/secondary only; cannot alter the primary decision:

- `intfloat/e5-small-v2` — 384d;
- `BAAI/bge-base-en-v1.5` — 768d;
- `Alibaba-NLP/gte-base-en-v1.5` — 768d.

Before the first secondary embedding is computed, each model's currently selected revision must be resolved to an immutable Hugging Face commit SHA and written to the run manifest. The panel composition itself is frozen here.

## 3. Exact-neighbor requirement

All reported neighbor sets are **exact k-nearest neighbors under cosine similarity**.

No HNSW, IVF, PQ, approximate FAISS index, ANN service, or recall-corrected approximate search is permitted.

Exact search is performed by blocked matrix multiplication against the full relevant gallery.

An implementation may cache an exact top-L ranking from a larger superset and derive subset kNN by filtering **only if** it verifies that at least `k` retained candidates occur within the exact top-L list for every evaluated query. Any exhausted query must be extended by further exact matrix multiplication; it may not be silently approximated.

## 4. Gallery-size design

Primary neighborhood sizes:

`k ∈ {5, 10, 20}`

Primary gallery sizes:

`N ∈ {1,000, 2,500, 5,000, 10,000, 25,000, 50,000, 100,000}`

### 4.1 Random-gallery scale curve — decision bearing

For each `N`, draw **32** galleries without replacement from the frozen 120k master corpus, stratified to preserve the master primary-category proportions. Seeds are `20260826 + draw_index`.

The same 32 galleries are used for every observer.

This curve answers the gallery-size question and is the only curve used for the static paper gate.

For every `(N,k,draw)` report:

- raw cross-model mKNN;
- correspondence-permutation null;
- permutation-calibrated mKNN;
- category purity for each observer;
- category-purity shuffled-label null.

Permutation calibration uses 10,000 identity permutations for `N <= 10,000`; for larger `N`, use the exact analytic chance expectation plus 1,000 explicit permutations as a verification check unless the analytic and empirical null disagree by more than 1% relative, in which case use 10,000 permutations.

### 4.2 Chronological-prefix curve — descriptive only

Sort the frozen master corpus by first-submission timestamp and report the same raw/calibrated mKNN statistics at the same `N`.

This curve studies composition/history and **cannot** determine the static scale gate.

## 5. Same-observer stability ceiling

Exact same-model/same-gallery mKNN is identically 1 for deterministic encoders and is not an informative seed-null.

The pre-specified empirical ceiling is therefore a **95% gallery-jackknife stability test**.

For every random gallery `G` and observer:

1. choose the anchor set as the hash-smallest 20% of documents in `G`;
2. always retain every anchor;
3. independently retain 95% of non-anchor candidates in pseudo-gallery A and pseudo-gallery B using seeds fixed from the draw id;
4. compute exact kNN for the shared anchors in A and B;
5. compute raw and permutation-calibrated same-observer mKNN between the two pseudo-galleries.

This yields a same-observer stability ceiling under a small, pre-specified perturbation of gallery membership without inventing encoder stochasticity.

For the cross-model-vs-ceiling comparison, use the **lower** calibrated ceiling of Qwen and MiniLM at each `(N,k)`.

## 6. Primary numerical gate

Primary statistic:

`S(N) = median over 32 random galleries of calibrated cross-model mKNN at k=5`.

Define retention:

`R = S(100000) / S(1000)`.

The result is classified before inspection as:

### Scale-stable local alignment

Requires both:

- `R >= 0.75`;
- `S(100000) >= 0.20`.

### Gallery-size collapse

Triggered by either:

- `R <= 0.50`; or
- `S(100000) <= 0.10`.

### Intermediate / unresolved

Anything between those regions.

A static paper claiming scale-robust partial local alignment is permitted only in the **scale-stable** case.

## 7. Observer-specific discrete-structure gate

Let `C(100000)` be the median calibrated cross-model mKNN at `k=5`, and let `U(100000)` be the lower of the Qwen and MiniLM median calibrated same-observer gallery-jackknife ceilings.

Define:

`Q = C(100000) / U(100000)`.

Classification:

- observer-specific gap survives if `Q <= 0.80`;
- cross-model is effectively near the stability ceiling if `Q >= 0.90`;
- `0.80 < Q < 0.90` is unresolved.

The proposed static paper requires **both**:
1. scale-stable local alignment from Section 6;
2. observer-specific gap survives from this section.

If either gate fails, the 116-document result is not promoted as a scale-robust static contribution.

## 8. Secondary checks

These do not change the primary classification.

- `k=10,20` scale-retention curves.
- Qwen 384/768/1024 MRL dimension controls.
- Secondary encoder-panel pairwise calibrated mKNN.
- Regression/descriptive analysis of cross-model mKNN against dimension difference, model family, and category composition. With this small panel, no causal dimension claim is allowed.
- Hubness summaries by `N`.
- Category-purity curves as external validation.
- Chronological-prefix curves.
- Order-invariant local susceptibility may be explored only **after** the static gate is reported and must be labeled exploratory.

## 9. Kill conditions

The static paper is killed if:

- the primary calibrated curve meets the gallery-size-collapse rule; or
- cross-model calibrated mKNN approaches the same-observer ceiling (`Q >= 0.90`).

It remains unresolved if either gate is intermediate.

No change of `k`, model panel, category subset, chronology, alignment method, or calibration rule may rescue a killed primary claim in this dataset.

## 10. Data preservation

Before analysis:
- version the frozen corpus manifest with arXiv id, first-submission timestamp, title hash, abstract SHA256, token count, categories, and selection hash;
- preserve the exact normalized abstract corpus as a compressed content-addressed artifact;
- pin every model revision;
- store raw and normalized embeddings separately with hashes and model/config provenance.

After analysis:
- preserve exact-neighbor cache provenance;
- preserve all random-gallery seeds;
- preserve raw per-draw metrics, not only summaries;
- write a Findings Record containing gate outcomes and kill conditions.
