---
type: "Protocol"
title: "Pontifex SciFact classical transport baseline expansion"
description: "Prospective information-matched CCA, PLS and random-feature transport baselines on the already frozen BEIR/SciFact split, without retuning Pontifex from test results."
timestamp: 2026-09-19T11:12:00-04:00
tags: [pontifex, scifact, beir, retrieval, baselines, cca, pls, rff, leakage-audit]
---

# Pontifex SciFact classical transport baseline expansion

## Status

**Prospective follow-up protocol.** The first untouched-test SciFact transport run has completed. This follow-up was explicitly reserved in `PROTOCOL-SCIFACT-TRANSPORT-2026-09-19.md`, which named CCA/PLS/RFF as missing baseline families. It does not change Pontifex, its K budgets, its frozen test scores, or the interpretation of the completed run.

## Question

Under the **same unlabeled A↔B correspondence budget and the same train/validation information**, can standard classical alignment/nonlinear-feature methods match or beat the frozen Pontifex transport frontier on official SciFact retrieval?

The purpose is adversarial fairness. A positive Pontifex result is not interesting if a standard alignment family obtains the same utility from the same K correspondences more cheaply.

## Frozen benchmark state

Reuse exactly the completed SciFact contract:

- A: `sentence-transformers/all-MiniLM-L6-v2`;
- B: `sentence-transformers/all-mpnet-base-v2`;
- canonical BEIR/SciFact archive and MD5;
- exact train-text overlap filtering against test;
- seed `20260919`;
- deterministic `D_student` / `D_val` split;
- K = `16, 32, 64, 128, 256, 512`;
- task-label budget for all transport fitting/selection = **zero**;
- official primary metric = **nDCG@10**.

The runner must reproduce the student/validation/test/corpus SHA manifests from the original benchmark. A mismatch is a protocol failure.

## Baselines

### CCA

`sklearn.cross_decomposition.CCA`, predicting B from A. Candidate latent component counts are selected **only** by B-coordinate cosine loss on `D_val`. Candidate counts are restricted by the available K/rank and capped at 16 to keep the baseline numerically meaningful under very small samples.

### PLS

`sklearn.cross_decomposition.PLSRegression`, same component-selection rule and information boundary as CCA.

### RFF + Ridge

An RBF random Fourier feature map on A followed by multi-output Ridge A→B. `gamma`, random-feature width, and Ridge alpha are selected only on `D_val` B-coordinate cosine. Random-feature seeds are deterministic and derived from the frozen experiment seed and K.

RFF is intentionally allowed more expressive nonlinearity than Procrustes. Its random-feature storage and fitted Ridge storage are reported separately.

## Not silently claimed

- These methods are **transport baselines**, not lexical retrieval systems.
- Mean/convex A+B fusion is not information-matched for the intended deployment regime because it requires true B representations at test time; it remains a different oracle/fusion setting rather than a fair A→B transport baseline.
- A lexical BM25/reference run remains a separate next step because it answers absolute retrieval competitiveness, not latent-transport efficiency.

## Hyperparameter boundary

For every K, fit candidate baseline models on exactly the first K frozen `D_student` correspondences and select hyperparameters using only `D_val` A/B coordinates. Do not access qrels, labels, downstream nDCG, or test B coordinates for selection.

Only after the full candidate choice for a K is frozen may the selected model be applied to test queries/corpus and scored by the official test qrels.

## Leakage audit

PASS requires:

- same canonical archive checksum;
- exact reproduction of the original ID manifests;
- zero qrels/labels used in candidate fitting or selection;
- test qrels used only for final scoring;
- no test-specific target or score enters hyperparameter choice;
- deterministic seeds and selected hyperparameters recorded;
- true B test/corpus coordinates used only as post-fit diagnostics/oracle context if reported.

Pretraining overlap classifications remain unchanged from the parent protocol and are not evaluation leakage by themselves.

## Fairness outputs

For each K and method record:

- selected hyperparameters;
- official nDCG@10, MRR@10, Recall@100, MAP@100;
- fraction of B utility recovered using the same A/B oracle denominator;
- B-coordinate cosine diagnostic;
- shared text and paired-embedding supervision bytes;
- fitted/stored floats;
- candidate-selection fit time, final map time, retrieval time.

Also report the minimum K, if any, reaching the already frozen 50%- and 90%-of-B-gap nDCG targets from the parent benchmark.

## Interpretation rule

The completed Pontifex test scores are immutable comparators. If a classical baseline beats Pontifex at the same K, record that as evidence against Pontifex's current inductive-bias advantage. If Pontifex remains better, the comparison becomes more credible but still requires replication on another external task/encoder pair before a general claim.
