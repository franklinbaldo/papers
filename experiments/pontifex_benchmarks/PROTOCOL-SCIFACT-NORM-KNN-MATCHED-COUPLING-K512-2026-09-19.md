---
type: "Protocol"
title: "Pontifex SciFact residual-norm plus A-KNN matched coupling K=512"
description: "Frozen feasibility-ladder protocol for the residual-norm and A-KNN matched coupled-versus-independent null on SciFact."
tags: [pontifex, scifact, red-1, null, knn, locality, protocol]
timestamp: 2026-09-19T14:00:00-04:00
---

# Protocol: SciFact residual-norm + A-KNN matched coupling specificity, K=512

Status: **prospective/adaptive follow-up, frozen before the new D_test read**.

## Motivation

The completed balanced-group norm+local-A run (GitHub Actions `35457676312`) did not validate the intended nuisance control as strongly as its name implied. Its query-side donor cosine-distance diagnostic was mean `0.78787` with p95 `0.99686` (document side mean `0.78952`, p95 `0.99686`). Therefore that run is evidence for a **coarse balanced-group** null, not a tight local-A null.

The first hard-locality attempt (`35460716096`) froze donor rank `<=16`. It failed **before any D_test relevance grades were read** because at least one residual-norm stratum's directed 16-nearest-neighbor bipartite graph admitted no perfect derangement. This is a protocol-feasibility result, not a retrieval result and not evidence for or against Pontifex.

The correction below is determined entirely from `D_student` geometry: use a predeclared rank ladder and choose the smallest graph that is combinatorially feasible. No `D_test` grade can influence that choice.

## Frozen information boundary

- `D_assembly`: canonical SciFact text/split membership and encoder identities only; no relevance grades.
- `D_student`: deterministic 80% of overlap-filtered train queries. It alone defines the K=512 paired coordinates, residual-norm strata, A-space donor graph, and graph-feasibility choice.
- `D_val`: deterministic remaining 20%; used only for coordinate-space `tau` / `lambda` selection.
- `D_test`: official SciFact test qrels; grades are not read until the map, strata, selected KNN graph, feasibility record, and both null banks are frozen and hashed.
- B/MPNet coordinates for test queries and corpus documents are not encoded.
- Task labels/qrels used for fit or selection: zero.

Expected frozen manifests remain identical to the prior K=512 family for student, validation, test, corpus, and anchor identities.

## Stronger null and feasibility ladder

Residuals remain restricted to the same 8 equal-count residual-L2 strata (64 anchors each). Rank 1 means the nearest non-self anchor in normalized A-space inside the same residual-norm stratum.

The donor-rank caps are frozen as the ordered ladder:

`R = [16, 20, 24, 32, 48, 63]`.

For each `R`, using only `D_student` coordinates, construct the directed bipartite graph in which anchor `i` may receive a residual only from one of its `R` nearest non-self A-space anchors in the same residual-norm stratum. Test whether every stratum admits a perfect derangement. Select the **smallest feasible R**. The failed `R=16` attempt is retained in the feasibility record rather than discarded.

After `R*` is selected, freeze and hash the exact candidate graph. Each null permutation is then obtained as a random-cost minimum-cost perfect matching over that fixed graph. The diagonal is forbidden, so every accepted permutation is a derangement. Sixty-three unique query-bank permutations and sixty-three unique document-bank permutations are frozen using distinct deterministic RNG streams.

The run must report the full feasibility ladder, selected `R*`, mean/median/p95/max cosine donor distance, and mean/p95/max donor rank. It fails rather than silently moving beyond the frozen ladder. Selection of `R*` is a **combinatorial nuisance-design choice based only on D_student**, not performance tuning.

## Contrasts and decision rule

Primary semantic-specificity contrast:

`TRUE - mean(NORM_KNN_MATCHED_COUPLED)` nDCG@10.

The exact-identity claim is supported only if **both** are true:

1. finite-bank upper-tail `p <= 0.05`; and
2. paired-query bootstrap 95% percentile interval is strictly above zero.

Shared-warp coherence is assessed as:

`mean(NORM_KNN_MATCHED_COUPLED) - mean(NORM_KNN_MATCHED_INDEPENDENT)`.

It is supported if the paired-query bootstrap 95% interval is strictly above zero.

## Interpretation boundary

A positive semantic-specificity result would support the narrow claim that exact residual identity contributes held-out SciFact retrieval utility beyond residual magnitude plus the **tightest feasible donor-rank constraint in the frozen ladder**. A negative result would further weaken that exact-identity claim.

The infeasibility of rank 16 is itself only a property of the frozen `D_student` graph; it is not evidence about held-out retrieval.

Neither outcome establishes causal semantic locality, torus topology, physical geometry, universal superiority of Pontifex transport, native-B superiority, low-budget superiority, cross-dataset generalization, or `D_assembly -> D_student` generalization.
