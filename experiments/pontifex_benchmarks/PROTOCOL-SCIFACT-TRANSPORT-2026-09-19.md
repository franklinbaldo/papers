---
type: "Protocol"
title: "Pontifex BEIR/SciFact transport: low-budget A→B retrieval"
description: "Prospective external retrieval benchmark of low-budget latent transport from MiniLM to MPNet on untouched BEIR/SciFact test retrieval, with explicit train-only correspondence fitting and leakage audit."
timestamp: 2026-09-19T09:57:00-04:00
tags: [pontifex, benchmark, beir, scifact, retrieval, transport, leakage-audit]
---

# Pontifex BEIR/SciFact transport

## Status

**Prospective protocol.** This protocol is frozen before the first successful SciFact transport result from this executable. The earlier `pontifex_red1/scifact_real_toy.py` is not treated as this benchmark: that toy split BEIR test queries internally and used test qrels for learned fusion, so it remains an exploratory real-data control rather than evidence under the present anti-leakage contract.

## Operational hypothesis

Two frozen semantic spaces share useful structure. With only `K` unlabeled corresponding observations from BEIR/SciFact **train queries**, a small Pontifex residual on top of a coarse global alignment may recover useful MPNet (`B`) geometry from MiniLM (`A`) and improve untouched SciFact **test** retrieval more efficiently than same-information baselines.

The primary scientific object is transport, not fusion. Pontifex never receives qrels, labels, test-specific targets, or B test embeddings during fitting or model selection.

## Benchmark and official target

- benchmark: **BEIR/SciFact**;
- canonical archive: `https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/scifact.zip`;
- published archive MD5: `5f7d1de60b170fc8027bb7898e2efca1`;
- official test set: BEIR SciFact `test` qrels, 300 queries, shared corpus of about 5k documents;
- primary metric: **nDCG@10**;
- secondary: MRR@10, Recall@100, MAP@100.

The executable records the exact corpus/query counts and hashes observed at runtime.

## Spaces

- `A`: `sentence-transformers/all-MiniLM-L6-v2`;
- `B`: `sentence-transformers/all-mpnet-base-v2`;
- exact Hugging Face revision SHAs are resolved and recorded by the runner.

Pretraining overlap between A and B is classified as `pretraining_overlap_possible`. Benchmark overlap with either encoder is `unknown` unless stronger provenance is established. This is **not automatically leakage**: the hypothesis explicitly asks whether existing semantic structure can be reused cheaply.

## Split and information boundary

The canonical BEIR train/test query split is preserved.

1. Exact train-query texts that duplicate any test-query text are removed before anchor selection.
2. Remaining train queries are deterministically permuted with seed `20260919`.
3. First 80% form `D_student`; last 20% form `D_val`.
4. `D_student` supplies only paired A/B embeddings for nested `K = 16,32,64,128,256,512` budgets.
5. `D_val` supplies only A/B embedding pairs for transport hyperparameter selection. **Its qrels are unused.**
6. `D_test` is the canonical BEIR SciFact test qrels. It is opened only for final official retrieval scoring.
7. True B embeddings of test queries and corpus documents are evaluation oracle/diagnostics only; they cannot fit or select a transport.

The runner emits SHA-256 manifests for student IDs, validation IDs, test IDs, corpus IDs, and every K-prefix anchor set.

## Methods and same-information baselines

Every transport method receives the same K A↔B train-query correspondences.

- `A-only`: MiniLM direct retrieval; no transport.
- `B-oracle`: MPNet direct retrieval; ceiling/context only.
- `Procrustes`: rectangular paired global alignment.
- `Pontifex_residual`: same paired Procrustes coarse map plus a local residual kernel; only `tau` and `lambda` are selected on `D_val` B-coordinate cosine.
- `Ridge`: linear A→B map; alpha selected on `D_val` B-coordinate cosine.
- `MLP_64`: capacity-controlled nonlinear A→B map trained on the same K correspondences with internal early stopping.
- `shuffled_correspondence`: same Pontifex capacity with B-anchor identity deterministically destroyed; its hyperparameters still receive the same `D_val` coordinate-selection opportunity, making this a deliberately strong negative control.

CCA/PLS/RFF and a reproduced lexical reference are not silently omitted from the research programme; they are follow-up baselines if this first retrieval run executes cleanly. No claim of a complete baseline sweep is allowed before they are added.

## Fairness regimes

### Budget-matched

At each K, all learned transport methods receive exactly the same K paired unlabeled train-query representations. Task-label budget for transport is zero.

The artifact records:

- K;
- UTF-8 bytes of shared anchor text;
- float32 bytes of paired A/B embedding supervision;
- fitted/stored parameter counts;
- fit/selection time;
- mapping and retrieval time.

### Quality-matched

If B-oracle nDCG@10 exceeds A-only, the runner reports the minimum K at which each method reaches 50% and 90% of the A→B nDCG gap. If B does not beat A, B-recovery quality targets are marked not applicable rather than forced into a misleading frontier.

## Primary and diagnostic endpoints

Primary: untouched test **nDCG@10**.

For every method and K:

`fraction_of_B_utility_recovered = (nDCG@10(method) - nDCG@10(A)) / (nDCG@10(B) - nDCG@10(A))`

when the denominator is nonzero.

Secondary mechanism diagnostics use true B coordinates only after fitting:

- mean cosine of transported test-query coordinates to B;
- mean cosine of transported corpus-document coordinates to B;
- incremental Pontifex-vs-same-Procrustes deltas.

These diagnostics never replace the official retrieval metric.

## Leakage audit acceptance

`PASS` requires all of the following at runtime:

- canonical dataset checksum matches;
- train/test IDs and exact-text overlap filtering are recorded;
- test qrels never enter fit or selection;
- train qrels never enter transport fit or selection;
- no task labels enter transport fit or selection;
- B test/corpus coordinates are oracle/evaluation-only;
- all transport hyperparameters use only train-derived representation pairs;
- deterministic seeds and SHA manifests are emitted.

A violation is `FAIL`, not a caveat. Unknown pretraining-corpus overlap is recorded separately and does not itself change the leakage status.

## Interpretation rule

A Pontifex win requires more than better B-coordinate reconstruction. At the same K it must improve official retrieval utility relative to the same paired Procrustes coarse map and survive the shuffled-correspondence control, or establish a legitimate quality/cost frontier against the stronger baselines. Negative and non-monotonic results are retained.
