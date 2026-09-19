---
type: "Protocol"
title: "Pontifex SciFact norm-matched coupling specificity at K=512"
description: "Prospective mechanism null preserving residual-magnitude strata while destroying exact residual-to-anchor identity, after the global-permutation K=512 result."
timestamp: 2026-09-19T12:24:00-04:00
tags: [pontifex, scifact, retrieval, transport, coupling, null, mechanism, matched-null, leakage-audit]
---

# Pontifex SciFact norm-matched coupling specificity at K=512

## Status

**Prospective follow-up protocol frozen after the completed K=512 global-permutation coupling test was known.** It is therefore not an independent replication of that result. It asks a narrower nuisance-control question that was not answered by the global shuffle.

## Motivation

At K=512, the correct residual-to-anchor assignment beat the mean globally shuffled coupled warp by `+0.008940` nDCG@10, but the frozen semantic-specificity rule failed (`p=0.078125`; paired-query 95% interval crosses zero). The coupled shared warp still beat independent query/document warps robustly.

A global permutation destroys exact semantic identity, but it also moves large residual vectors onto anchor positions whose true residuals may have very different magnitude. Therefore part of the TRUE-versus-null contrast could be caused by this low-level magnitude mismatch rather than semantic identity itself.

This follow-up makes the null harder: preserve coarse residual-magnitude structure while destroying exact correspondence.

## Frozen benchmark state

Reuse the K=512 SciFact mechanism benchmark exactly:

- A: `sentence-transformers/all-MiniLM-L6-v2`;
- B: `sentence-transformers/all-mpnet-base-v2`;
- seed `20260919`;
- K=`512` first frozen `D_student` correspondences;
- identical `D_student`, `D_val`, `D_test`, corpus and anchor manifests;
- `tau` and `lambda` selected only by B-coordinate loss on `D_val`;
- no task label/qrel used for fitting or selection;
- no B test-query or B corpus coordinates encoded by this diagnostic.

The runner must reproduce the exact parent manifests or fail.

## Split contract

The information boundary remains explicit:

- `D_assembly`: canonical SciFact text/split membership and frozen encoder identities; no relevance grades;
- `D_student`: deterministic 80% of exact-test-overlap-filtered train queries, used for A/B paired coordinates and for defining residual-magnitude strata;
- `D_val`: remaining 20%, used only for coordinate-space selection of `tau`/`lambda`;
- `D_test`: official test relevance grades, not opened until the map, strata and every null permutation are frozen.

This experiment does not train a separate sparse student; it therefore makes no claim about Assembly-to-student generalization.

## Norm-matched null construction

After fitting the K=512 coarse map and residual bank on `D_student`:

1. compute the L2 norm of each of the 512 true residual vectors;
2. stable-sort the 512 anchor positions by residual norm;
3. split them into **8 equal-count strata of 64 anchors**;
4. for each null draw, independently derange residual assignments **within each stratum** so no anchor retains its own residual;
5. create 63 unique query null permutations and 63 unique document null permutations from deterministic seed offsets;
6. hash the strata and both complete permutation banks before opening `D_test` relevance grades.

The null therefore preserves the residual bank exactly and preserves coarse residual-magnitude quantiles at each destination anchor, while breaking exact residual identity.

## Conditions

### TRUE
Correct K=512 residual-to-anchor assignment on query and corpus sides.

### NORM-MATCHED COUPLED
One within-stratum derangement is applied to both query and corpus residual banks. This preserves a coherent two-sided deformation and residual-magnitude stratum while destroying exact semantic correspondence.

### NORM-MATCHED INDEPENDENT
A query-side within-stratum derangement is paired with a different document-side within-stratum derangement. This destroys query/document warp coherence while preserving the same nuisance constraints.

## Predeclared primary contrasts

### 1. Semantic identity beyond residual magnitude

`TRUE - mean(NORM_MATCHED_COUPLED)` on official SciFact nDCG@10.

Supported only if **both**:

- paired-query bootstrap 95% interval is strictly above zero; and
- finite-bank upper-tail `p <= 0.05` against the 63 matched coupled null scores.

Failure is evidence that exact residual identity has not been separated from a magnitude-matched coherent deformation at K=512.

### 2. Shared-warp coherence under nuisance matching

`mean(NORM_MATCHED_COUPLED) - mean(NORM_MATCHED_INDEPENDENT)`.

Supported if the paired-query bootstrap 95% interval is strictly above zero.

This asks whether two-sided coherence survives even when the null is constrained to preserve residual-magnitude strata.

## Leakage / adaptivity rule

The global K=512 result motivated this experiment, so this is a **prospective follow-up, not confirmation**. After this protocol is committed, do not change K, number of strata, null-bank size, seed, decision thresholds, or contrast definitions in response to the result.

Scientific null/negative outcomes are successful experimental outcomes and must be recorded as such.

## Interpretation boundary

A positive semantic-specificity result would show only that exact K=512 residual identity carries held-out SciFact retrieval information beyond a coarse residual-magnitude-matched coherent warp. It would not establish causal semantic locality, intrinsic toroidal topology, low-budget transport, universal superiority, or native-B superiority.

A negative semantic-specificity result would materially weaken the strong local-correspondence mechanism claim while leaving open the narrower empirical fact that a coherent learned deformation can preserve retrieval structure.
