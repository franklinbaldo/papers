---
type: "Protocol"
title: "Pontifex SciFact coupling-specificity null"
description: "Prospective mechanism follow-up separating correct residual correspondence from generic shared-warp coherence on held-out SciFact retrieval."
timestamp: 2026-09-19T10:45:00-04:00
tags: [pontifex, scifact, retrieval, transport, permutation, null, mechanism, holdout]
---

# Pontifex SciFact coupling-specificity null

## Status

**Prospective mechanism follow-up.** This protocol is frozen after observing the completed residual-side ablation but before the first run of this coupling-specificity experiment. It is therefore not an independent confirmation of the original Pontifex claim.

The motivating observation is narrow: at the predeclared `K=256`, the full residual did not reliably outperform Procrustes, but the algebraic two-sided interaction was positive. The larger interaction at `K=512` is noted in the preceding findings but is **not** used to choose the present test point.

## Scientific question

Does the positive two-sided interaction require the **correct local residual correspondence**, or can it be reproduced by any nonlinear warp applied coherently to both query and document coordinates?

A shared nonlinear transformation can create non-additive retrieval effects even when it contains no B-specific local information. The experiment therefore holds the coarse map, local kernel, residual-vector marginal distribution and two-sided application fixed while selectively destroying residual-to-anchor correspondence and/or cross-side coupling.

## Frozen information boundary

- `D_assembly`: canonical SciFact corpus/query text, split membership, frozen MiniLM and MPNet weights. Relevance grades are not part of assembly.
- `D_student`: first 80% of exact-test-text-overlap-filtered train-query IDs after deterministic seed `20260919`. Paired MiniLM/MPNet representations only.
- `D_val`: remaining 20% of filtered train-query IDs. Used only to choose the true residual map's `tau` and `lambda` by B-coordinate reconstruction.
- `D_test`: canonical SciFact test relevance grades, loaded only after the coarse map, residual bank, `tau`, `lambda`, and all null permutations have been frozen.

No MPNet/B coordinate may be encoded for test queries or corpus documents. No test qrel may select K, a permutation, `tau`, `lambda`, model class or endpoint.

## Frozen test point

Only `K=256` is tested here. It remains the primary mechanism point because it was selected prospectively in the preceding residual-side protocol from the earlier SICK-R benchmark, not from SciFact test outcomes. Restricting this follow-up to that already-frozen point also avoids turning the stronger post-hoc `K=512` interaction into a new selection rule.

## Three frozen conditions

Fit the ordinary Procrustes coarse map on the correct `D_student` pairs and compute the true anchor residuals

`r_i = b_i - Procrustes(a_i)`.

Choose `(tau, lambda)` only on `D_val` using the correctly assigned residuals. Then freeze 31 deterministic non-identity permutations before opening `D_test`.

The test evaluates:

1. `TRUE`: correct residual assignment on both query and document sides.
2. `COUPLED-NULL_j`: permutation `p_j` assigns `r_{p_j(i)}` to anchor `a_i`, and **the same** scrambled bank is applied to queries and documents.
3. `INDEPENDENT-NULL_j`: queries use `p_j`, while documents use a separately seeded non-identity permutation `q_j`.

Thus `TRUE` and `COUPLED-NULL` differ in semantic residual-to-anchor assignment while preserving shared two-sided deformation; `COUPLED-NULL` and `INDEPENDENT-NULL` differ primarily in whether query and document sides share the same scrambled warp.

## Frozen inference

The primary retrieval endpoint is mean nDCG@10 over the 300 canonical SciFact test queries.

Report:

- `TRUE - median(COUPLED-NULL_j)` and an exact finite-bank upper-tail randomization p-value `(1 + #{null >= TRUE}) / 32`;
- `median(COUPLED-NULL_j) - median(INDEPENDENT-NULL_j)`;
- paired-query bootstrap intervals for `TRUE - mean(COUPLED-NULL)` and `mean(COUPLED-NULL) - mean(INDEPENDENT-NULL)` using 5000 deterministic resamples.

The 31-null bank gives minimum p-value `1/32 = 0.03125`; no stronger resolution may be claimed. No alternate K is substituted if this point is null or adverse.

## Interpretation boundary

Evidence for `TRUE > COUPLED-NULL` would support the claim that correct local A↔B residual correspondence contributes beyond a generic shared nonlinear warp. Evidence for `COUPLED-NULL > INDEPENDENT-NULL` would support a separate shared-coordinate-coherence contribution. Either, both, or neither may occur.

This experiment cannot establish a physical torus, causal semantic locality, universal transport superiority, or downstream improvement over the best native B model. A positive coupling-specificity result would identify a mechanism inside this frozen SciFact transport setup only.
