---
type: "Protocol"
title: "Pontifex SciFact residual-side ablation"
description: "Prospective 2x2 query/document-side ablation testing where a local Pontifex residual changes untouched SciFact retrieval after train-only selection."
timestamp: 2026-09-19T10:18:00-04:00
tags: [pontifex, scifact, ablation, retrieval, transport, mechanism, holdout]
---

# Pontifex SciFact residual-side ablation

## Status

**Prospective mechanism protocol.** Frozen before the first successful run of this ablation and before inspecting any SciFact test outcome from it. The parent transport protocol remains `PROTOCOL-SCIFACT-TRANSPORT-2026-09-19.md`.

## Why this discriminant exists

The parent benchmark applies a residual correction learned only from paired train-query representations to both test queries and corpus documents. A retrieval delta from the full map therefore does not by itself tell us whether the useful or harmful contribution comes from the query side, the document side, or their interaction.

This ablation changes no training information and introduces no new fit. It decomposes the already-selected transport into a frozen 2x2 evaluation design.

## Frozen information boundary

- `D_assembly`: canonical SciFact corpus/query text plus split membership and encoder weights. Relevance grades are not part of assembly.
- `D_student`: first 80% of exact-test-text-overlap-filtered train-query IDs after the deterministic seed-20260919 permutation. Only paired MiniLM/MPNet representations are used.
- `D_val`: remaining 20% of filtered train-query IDs. Only B-coordinate reconstruction selects Pontifex `tau` and `lambda`; train qrels are never used.
- `D_test`: canonical SciFact test relevance grades. The ablation script reads only test query IDs before fitting; relevance grades are loaded only after all K-specific transports and hyperparameters are frozen.

True B coordinates for test queries/documents are evaluation diagnostics only. No test endpoint selects K, `tau`, `lambda`, anchors, or model class.

## 2x2 frozen evaluation

For every predeclared K in `16,32,64,128,256,512`, fit the same Procrustes coarse map and select one Pontifex residual on `D_val`. Then score four cells on untouched test qrels:

| Query side | Document side | Cell |
|---|---|---|
| coarse | coarse | `CC` = Procrustes baseline |
| residual | coarse | `RC` = query-only residual |
| coarse | residual | `CR` = document-only residual |
| residual | residual | `RR` = full Pontifex residual |

For per-query nDCG@10 values define:

- `Q = RC - CC`;
- `D = CR - CC`;
- `FULL = RR - CC`;
- `INTERACTION = RR - RC - CR + CC`.

This is an exact algebraic decomposition of the full retrieval change into query-side, document-side, and non-additive interaction terms.

## Primary point and uncertainty

`K=256` is the primary mechanism point because the previously completed SICK-R strict-crossfit benchmark showed the clearest B-coordinate residual reconstruction at that budget. This choice is based on a different benchmark and predates SciFact test inspection. Other K values are a predeclared scaling diagnostic.

For each contrast the script reports the mean paired per-query nDCG@10 difference and a deterministic 95% percentile bootstrap interval over the 300 untouched test queries (`5000` resamples, seed `20260919 + K`). The bootstrap is uncertainty estimation after model freeze; it does not retune anything.

No arbitrary pass/fail effect threshold is introduced. Multiple K values are not treated as six independent confirmatory discoveries.

## Interpretation boundary

Evidence can support statements such as “the retrieval delta is concentrated on the document-side residual” or “the full residual does not outperform the same Procrustes map.” It cannot by itself establish a physical torus, causal semantic locality, or general transport superiority.

A positive coordinate-reconstruction delta without a retrieval delta remains mechanism evidence only. A retrieval delta that disappears in the side decomposition weakens rather than strengthens the claim.
