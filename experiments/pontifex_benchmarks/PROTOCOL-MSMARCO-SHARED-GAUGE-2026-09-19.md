---
type: "Protocol"
title: "Pontifex MS MARCO Passage shared-gauge transport follow-up"
description: "Prospective mechanism and fairness follow-up to the negative MS MARCO pilot, testing whether independent query/document gauges caused retrieval collapse while preserving the same external task, candidate set, information budget, and leakage boundary."
timestamp: 2026-09-19T13:56:00-04:00
tags: [pontifex, msmarco, retrieval, reranking, transport, shared-gauge, leakage-audit, pilot]
---

# Pontifex MS MARCO Passage shared-gauge transport follow-up

## Status and motivation

**Prospective post-result mechanism follow-up.** Parent pilot: `PROTOCOL-MSMARCO-PILOT-2026-09-19.md`; preserved negative findings: `FINDINGS-MSMARCO-PILOT-2026-09-19.md`.

The original pilot fitted A→B transports independently for query and document representations. All transported methods collapsed far below A-only. The post-result hypothesis tested here is deliberately narrow: independently estimated maps may choose incompatible target-space gauges, which is fatal to a dot-product retrieval task even when each side approximates B coordinates individually.

This is not a new benchmark target and cannot overwrite the original result. The external task, candidate set, MRR@10 metric, train/validation/test boundary and total information budget remain fixed.

## Frozen external task

- benchmark: MS MARCO Passage Ranking V1;
- evaluation source: deterministic 256-query subset of Pyserini `msmarco-passage-dev-subset`;
- primary metric: **MRR@10**;
- frozen candidate generator: BM25 over `msmarco-v1-passage`;
- candidate depth: 100/query;
- frozen candidate-row hash: `a129eadf935f495914f69f9f74266f4421751b091e0925802a7ad0b2c086d1f1`;
- all systems rerank exactly the same candidate PIDs.

This remains a `pilot`, not a full-dev or native full-corpus leaderboard result.

## Spaces

A:
- query encoder `castorini/ance-msmarco-passage`;
- document vectors from `msmarco-v1-passage.ance`.

B:
- query encoder `castorini/tct_colbert-v2-hnp-msmarco`;
- document vectors from `msmarco-v1-passage.tct_colbert-v2-hnp`.

Pretraining overlap A↔B: `pretraining_overlap_possible`. Benchmark training overlap: `known` at the broad MS MARCO-family level. Neither is evaluation leakage.

## Information boundary

Reuse the deterministic selection algorithm and manifests from the parent pilot:

- unlabeled MS MARCO train queries provide query-side A↔B pairs;
- deterministic corpus PIDs excluded from every evaluation candidate provide document-side A↔B pairs;
- student/validation splits are frozen before any dev qrel is loaded;
- no label, qrel, relevant PID, dev score or target-specific statistic selects a map or hyperparameter;
- true B pilot vectors are allowed only for B-oracle scoring and post-freeze diagnostics;
- dev qrels are opened once, only after every ranking is frozen.

The runner must fail if the reconstructed candidate-row hash differs from the frozen parent hash.

## Budget fairness

For every K in `16, 32, 64, 128, 256, 512`:

- query side contributes exactly K paired A↔B observations;
- document side contributes exactly K paired A↔B observations;
- total supervision budget is therefore exactly `2K` paired observations for both separate-gauge and tied-gauge methods;
- no method receives additional labels or task feedback;
- report float32 supervision bytes, fitted-state floats and fit/selection time.

This is a **budget-matched** comparison. The quality-matched frontier uses the same parent targets: 50% and 90% of the frozen A→B oracle MRR@10 gap.

## Compared systems

References:
- BM25 frozen candidate order;
- A-only ANCE;
- B-oracle TCT-ColBERT-v2 HN+.

Original-regime controls, reconstructed in the same runner:
- separate query/document Orthogonal Procrustes;
- separate query/document Ridge;
- separate query/document Pontifex residual transport.

Shared-gauge systems:
- **Tied Procrustes:** one orthogonal orientation W estimated from the sum of query and document cross-covariances, with side-specific A/B centering so query/document marginals are not artificially forced to share a mean;
- **Tied Ridge:** one centered linear W shared across sides, with side-specific means/intercepts; alpha selected by equal-weight query/document B-coordinate validation loss;
- **Tied Pontifex:** Tied Procrustes as the coarse map, then side-specific local residual neighborhoods expressed in the same target gauge; a single `(tau, lambda)` pair is selected from equal-weight query/document validation coordinate loss;
- **Tied shuffled Pontifex:** identical architecture and K budget, but true A↔B identity is destroyed independently within query and document anchor strata before the one shared gauge is fitted.

The shared-gauge restriction is applied to the simple baselines as well as Pontifex. A gain caused merely by fixing coordinate compatibility must therefore accrue to Procrustes/Ridge too, not be attributed to Pontifex.

## Selection contract

Hyperparameters are selected before dev qrels are opened:

- Procrustes: no task hyperparameter;
- Ridge alpha: choose from the same frozen grid by mean normalized B-coordinate loss over query and document validation sets;
- Pontifex tau/lambda: choose from the same frozen grids by mean normalized B-coordinate loss over both validation sides;
- shuffled control receives the identical validation procedure.

No MRR@10, qrel or pilot relevance grade participates in selection.

## Predeclared interpretation

Primary comparisons are, at each K:

1. `Tied Procrustes` vs `Separate Procrustes` — isolates the shared-gauge effect with no Pontifex residual;
2. `Tied Ridge` vs `Separate Ridge` — checks whether the effect generalizes beyond orthogonal alignment;
3. `Tied Pontifex` vs `Separate Pontifex` — asks whether Pontifex specifically benefits from a retrieval-compatible common gauge;
4. `Tied Pontifex` vs `Tied Procrustes`, `Tied Ridge`, and `Tied shuffled Pontifex` — tests method-specific utility under matched information.

Interpretation is frozen as follows:

- if tied simple baselines recover most of A-only while Pontifex adds nothing, diagnose the original failure primarily as independent-gauge mismatch, not a Pontifex advantage;
- if tied Pontifex exceeds tied Procrustes/Ridge/shuffled at the same K and improves the A→B utility frontier, that is positive evidence for local residual transport under a valid retrieval interface;
- if all tied methods remain materially below A-only, treat ANCE→TCT low-budget transport as negative evidence for the practical hypothesis in this encoder pair;
- no result from this 256-query pilot may be described as full MS MARCO competitiveness.

No thresholds or method choices may be altered after dev MRR@10 is opened.
