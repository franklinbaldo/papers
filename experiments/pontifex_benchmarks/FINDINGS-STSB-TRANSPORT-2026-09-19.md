---
type: "Findings Record"
title: "Pontifex STS-B transport: first external latent-space benchmark"
description: "Real STS-B benchmark of low-budget A→B latent transport with an explicit leakage audit and same-K Procrustes, Ridge and shuffled-correspondence controls."
timestamp: 2026-09-19T08:12:00-04:00
tags: [pontifex, benchmark, stsb, latent-transport, negative-result, leakage-audit]
---

# Pontifex STS-B transport: first external latent-space benchmark

## Status

**Real external benchmark result.** The first explicit Pontifex anchor-transport rule is **not supported** on STS-B. The result is retained as negative evidence rather than reinterpreted as a win.

Workflow: https://github.com/franklinbaldo/papers/actions/runs/35441878327  
Artifact: https://github.com/franklinbaldo/papers/actions/runs/35441878327/artifacts/10584425080

## Task and spaces

External task: **Semantic Textual Similarity Benchmark (STS-B)**. Primary endpoint is test Spearman correlation between embedding cosine similarity and human similarity score; Pearson is secondary.

- A: `sentence-transformers/all-MiniLM-L6-v2`
- B: `sentence-transformers/all-mpnet-base-v2`
- train / validation / test rows: `5749 / 1500 / 1379`
- shared unlabeled A↔B correspondence budgets: `K = 8, 16, 32, 64, 128, 256`

Possible shared pretraining knowledge between A and B is allowed by the scientific premise. The adapter itself may not consume evaluation information.

## Leakage audit — PASS

The executable run reports:

- adapter fitting uses only unlabeled STS-B train sentences;
- `10,534` unique train candidates existed before overlap filtering;
- `463` train sentences appearing verbatim in validation or test were excluded;
- `10,071` leakage-filtered train candidates remained;
- validation labels are used only for temperature / Ridge-alpha selection;
- test labels are used only for final scoring;
- B test embeddings are used only for the `B-oracle` ceiling and diagnostics;
- anchor order is deterministic (`seed = 20260919`) and K budgets are nested prefixes;
- shuffled A↔B correspondence is included as a mandatory negative control.

Provenance:

- train fingerprint: `971f0f2b71347f79`
- validation fingerprint: `46e79bc35c295868`
- test fingerprint: `6da4977136e89ab3`
- anchor-pool SHA-256: `21d1bacef0016e59dac5fd8c1b951b739fd08bb44b39b09fd1bf25b909aa9360`
- validation-pairs SHA-256: `187027f5e5f7d76204e9a940774edc2dbd41029cb05502c72b31fc128258da89`
- test-pairs SHA-256: `a345206e191466e24cd594f3b967f633f0d934b1900d7fd4e59d0fc406bcd5f1`

## Oracle context

On untouched test:

| condition | Spearman | Pearson |
|---|---:|---:|
| A-only / MiniLM | 0.82030 | 0.82740 |
| B-oracle / MPNet | 0.83422 | 0.84041 |

B exceeds A by only `+0.01392` Spearman. Therefore `fraction_of_B_utility_recovered` is numerically ill-conditioned in this particular A/B/task combination: small absolute losses below A create very large negative recovery ratios. The raw task scores remain the primary evidence.

## Test result by shared-correspondence budget

| K | Pontifex anchor transport | Procrustes | Ridge | shuffled correspondence |
|---:|---:|---:|---:|---:|
| 8 | 0.64528 | **0.82377** | 0.65981 | 0.64877 |
| 16 | 0.69891 | **0.82379** | 0.71205 | 0.70826 |
| 32 | 0.73693 | **0.82053** | 0.74089 | 0.75289 |
| 64 | 0.74706 | **0.81924** | 0.77273 | 0.77809 |
| 128 | 0.74505 | **0.81886** | 0.80697 | 0.78098 |
| 256 | 0.74116 | **0.81941** | 0.81416 | 0.79553 |

All values are test Spearman. `A-only = 0.82030`; `B-oracle = 0.83422`.

## Interpretation

### 1. The first Pontifex anchor-transport rule fails the task

The proposed one-scalar barycentric transport does not beat A-only at any K. More importantly, the **shuffled-correspondence control beats the correctly paired Pontifex condition at every tested K**. This is direct evidence that the current rule is not extracting useful identity-specific A↔B transport from the shared correspondences.

The likely behavior is generic semantic smoothing/kernelization rather than reconstruction of B-specific geometry. That distinction matters: this run does **not** support claiming that correct cross-space pairing is doing useful work under this transport rule.

### 2. Very small-K Procrustes is unexpectedly strong

With only `K=8` or `16` unlabeled A↔B correspondences, rectangular Procrustes reaches about `0.8238` Spearman, slightly above A-only and roughly one quarter of the narrow A→B oracle improvement:

- K=8 fraction of B utility recovered: `0.249`
- K=16 fraction of B utility recovered: `0.250`

Its map has `294,912` coefficients and takes about `0.059 s` to fit in this runner, so it is substantially less parameter-efficient than the one-scalar anchor rule. But on task quality it decisively wins the same-K transport competition in this run.

### 3. Ridge needs more correspondences and still does not reach A-only

Ridge improves monotonically in the high-K regime, reaching `0.81416` at K=256, but remains below A-only. It therefore does not establish useful B recovery here.

### 4. The efficiency frontier is not favorable to the tested Pontifex rule

The Pontifex anchor rule is extremely cheap — one selected scalar, K stored A/B anchors, and test-pair transport measured at roughly milliseconds — but its quality loss is too large to qualify as a useful low-compute trade-off on STS-B. Cheap compute alone is not a win when the external task score drops from `0.8203` to the `0.645–0.747` range.

## What this says about the method

This is evidence **against this particular direct barycentric realization**, not against the broader hypothesis that shared latent geometry can be reused cheaply. The strongest clue in the same run is that a geometry-preserving global map learned from as few as eight unlabeled pairs retains essentially all of A's STS performance and slightly exceeds it.

The next Pontifex variant should therefore be treated explicitly as a **follow-up after inspecting this test result**. A high-value hypothesis is to use a simple global alignment such as Procrustes as the coarse shared geometry and spend Pontifex's small additional budget only on a local residual/deformation field. That follow-up must compete directly against frozen Procrustes under the same K and must not reuse this test set for model selection.

A second high-value replication is to choose a different external task/model pair where `B-oracle - A-only` is materially larger, because the current `+0.01392` Spearman denominator makes oracle-recovery fractions unstable even though the raw benchmark comparison remains valid.

## Reproducibility

Executable: `experiments/pontifex_benchmarks/stsb_transport.py`  
Protocol: `experiments/pontifex_benchmarks/PROTOCOL-STSB-TRANSPORT-2026-09-19.md`  
Workflow: `.github/workflows/pontifex-stsb-transport.yml`

The run completed successfully and uploaded the JSON artifact. No benchmark result in this record is inferred from a pending workflow.
