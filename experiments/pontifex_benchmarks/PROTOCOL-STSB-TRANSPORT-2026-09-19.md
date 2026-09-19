---
type: "Experiment Protocol"
title: "Pontifex STS-B latent-space transport benchmark"
timestamp: 2026-09-19T08:06:00-04:00
tags: [pontifex, benchmark, stsb, latent-transport, leakage-audit]
---

# Pontifex STS-B latent-space transport benchmark

## Question

Can a tiny transport mechanism reuse semantic structure already present in one frozen latent space to recover useful downstream behavior from another frozen latent space with very few shared, unlabeled correspondences?

The downstream task is the external **Semantic Textual Similarity Benchmark (STS-B)**. The primary endpoint is test-set Spearman correlation between cosine similarity and the human similarity score; Pearson is secondary.

## Frozen spaces

- A: `sentence-transformers/all-MiniLM-L6-v2`
- B: `sentence-transformers/all-mpnet-base-v2`

Possible overlap in the pretraining/fine-tuning knowledge of A and B is allowed and is part of the premise being tested. It is not counted as adapter leakage. Exposure of either public encoder to STS-B itself is classified as `unknown` unless documented otherwise.

## Information boundary and leakage audit

- A↔B transport may fit only on **unlabeled sentences from the STS-B train split**.
- Any train sentence that occurs verbatim in validation or test is removed from the anchor pool before sampling.
- Validation labels may select the Pontifex temperature and Ridge alpha.
- Test labels may only score the final frozen conditions.
- B embeddings for test sentences exist only for the `B-oracle` ceiling and diagnostics. They may not enter transport fitting or hyperparameter selection.
- Anchor order is fixed by seed `20260919`; each K is a nested prefix of that order.
- Every run records dataset fingerprints plus SHA-256 manifests for anchor pool, validation pairs and test pairs.
- A shuffled A↔B correspondence condition is mandatory as a negative control.

A run is `leakage_audit: PASS` only if all of the above are satisfied by the executable output.

## Budgets

`K ∈ {8, 16, 32, 64, 128, 256}` shared unlabeled A↔B sentence correspondences.

## Methods

`A-only`: cosine directly in A.

`B-oracle`: cosine directly in true B; this is a ceiling/context condition, not an allowed transport method.

`Pontifex anchor transport`: locate a held-out A point by cosine to the K A anchors, convert similarities into softmax barycentric weights, and apply the same weights to the corresponding B anchors. Only one scalar temperature is selected on validation.

`Procrustes`: rectangular orthogonal map A→B fitted on the same K correspondences.

`Ridge`: multi-output linear A→B map fitted on the same K correspondences; alpha is selected on validation.

`shuffled correspondence`: Pontifex anchor transport after permuting B-anchor identity at the same K.

## Efficiency accounting

For each K, record official task score, fraction of B utility recovered, stored anchor floats or map parameter count, fit time where applicable, and test-pair inference time.

The primary recovery diagnostic is

`(Spearman(method) - Spearman(A-only)) / (Spearman(B-oracle) - Spearman(A-only))`.

It is interpreted only when the B-oracle/A-only denominator is non-zero. Values above 1 are allowed: they mean the transported representation outperformed the chosen B oracle on this task, not that more than 100% of latent information was literally reconstructed.

## Decision rule

A Pontifex result is interesting if it is competitive on the real STS-B task under the same K and shows a favorable quality/data/compute frontier. Geometry recovery is secondary and cannot substitute for task score. A simple baseline winning is preserved as evidence against the distinctive transport mechanism.

The test result is not to be used to redesign this first protocol after inspection; subsequent variants must be labeled as follow-up experiments.
