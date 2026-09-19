---
type: "Protocol"
title: "Pontifex SciFact norm+local-A matched coupling specificity at K=512"
description: "Prospective harder mechanism null preserving residual magnitude and local A-space anchor neighborhoods while destroying exact residual identity."
timestamp: 2026-09-19T13:20:00-04:00
tags: [pontifex, scifact, retrieval, transport, coupling, null, mechanism, matched-null, locality, leakage-audit]
---

# Pontifex SciFact norm+local-A matched coupling specificity at K=512

## Status

**Prospective follow-up frozen after the global-permutation and residual-norm-matched K=512 outcomes were known.** It is not an independent replication. It asks a narrower mechanism question that those completed tests leave open.

## Motivation from completed evidence

The completed norm-matched run (`35455793661`) preserved eight residual-L2 strata while destroying exact residual identity. On official SciFact nDCG@10 it observed `TRUE=0.649954`, matched-coupled mean `0.640712`, and matched-independent mean `0.619617`. The global TRUE-minus-coupled contrast was `+0.009241` with finite-bank `p=0.015625`, but the paired-query bootstrap 95% interval `[-0.003507, +0.021617]` crossed zero. Under the predeclared two-part rule, exact residual identity therefore remained **unsupported**, while shared-warp coherence remained supported (`+0.021095`, 95% CI `[+0.008416,+0.034615]`).

That null controls coarse residual magnitude but can still reassign a residual to a distant anchor in source A-space. A positive TRUE-minus-null contrast could therefore reflect preservation of local A-space geometry rather than exact residual identity. The present null explicitly controls that nuisance too.

## Frozen benchmark state and split contract

Reuse the exact K=512 SciFact mechanism benchmark:

- A: `sentence-transformers/all-MiniLM-L6-v2`;
- B: `sentence-transformers/all-mpnet-base-v2`;
- seed `20260919`;
- K=`512` first frozen `D_student` correspondences;
- same frozen `D_student`, `D_val`, `D_test`, corpus and anchor manifests;
- `tau` and `lambda` selected only by B-coordinate loss on `D_val`;
- no qrel/task label used for fitting or selection;
- no B test-query or B corpus coordinates encoded by this diagnostic.

Information roles remain separate:

- `D_assembly`: SciFact text/split membership and frozen encoder identities; no relevance grades;
- `D_student`: deterministic 80% of exact-test-overlap-filtered train queries; paired A/B coordinates fit the map; residual norms and local groups are defined here;
- `D_val`: remaining 20%; coordinate-only selection of `tau`/`lambda`;
- `D_test`: official test relevance grades; not opened until map, residual-norm strata, A-local groups and both null banks are frozen.

This diagnostic does not train a separate sparse student and therefore does not support an `D_assembly -> D_student` generalization claim.

## Stronger matched-null construction

1. Compute the L2 norm of each of the K=512 `D_student` residuals and stable-sort into the same **8 equal-count norm strata of 64 anchors** used by the completed norm-matched test.
2. Normalize the corresponding 512 A-space anchor vectors.
3. Inside each 64-anchor norm stratum, deterministically choose **8 farthest-first centers** in A-space, starting from the lowest anchor index.
4. Assign each remaining anchor to the most similar center with remaining capacity, yielding **8 balanced local groups of 8** per norm stratum, hence 64 local groups total.
5. Generate 63 unique query null permutations and 63 unique document null permutations by deranging residual assignments **only within each 8-anchor local group**. No anchor may retain its own residual.
6. Freeze and hash the norm strata, A-local partition, and both complete permutation banks before opening `D_test` grades.

This null preserves two nuisance structures simultaneously: coarse residual magnitude and a coarse local neighborhood in source A-space. It deliberately does **not** preserve exact semantic identity.

## Conditions and predeclared contrasts

### TRUE
Correct K=512 residual-to-anchor assignment on query and corpus sides.

### NORM+LOCAL-A MATCHED COUPLED
The same within-local-group derangement is applied to query and corpus residual banks.

### NORM+LOCAL-A MATCHED INDEPENDENT
A query-side local derangement is paired with a different document-side local derangement.

Primary contrast 1, **identity beyond magnitude + source locality**:
`TRUE - mean(NORM_LOCAL_MATCHED_COUPLED)` on official nDCG@10. Support requires both (a) paired-query bootstrap 95% interval strictly above zero and (b) finite-bank upper-tail `p <= 0.05` against the 63 coupled null scores.

Primary contrast 2, **shared-warp coherence under stronger matching**:
`mean(NORM_LOCAL_MATCHED_COUPLED) - mean(NORM_LOCAL_MATCHED_INDEPENDENT)`. Support requires the paired-query bootstrap 95% interval strictly above zero.

The runner also records residual-norm mismatch and donor-anchor A-space cosine-distance diagnostics so that the strength of the nuisance match is auditable.

## Adaptivity and interpretation boundary

This design was chosen after seeing both earlier K=512 results. Group size, grouping algorithm, null-bank size, seeds, contrasts and thresholds are therefore frozen **now**, and must not be changed in response to the outcome.

A positive identity result would show only that exact residual identity carries held-out SciFact utility beyond a coherent deformation already matched on coarse residual magnitude and local source-space geometry. It would still not establish causal semantic locality, intrinsic toroidal topology, universal transport superiority, native-B superiority, low-budget superiority, cross-dataset generalization, or Assembly-to-student generalization.

A negative result would further weaken the exact-identity mechanism claim while leaving the already observed shared-warp phenomenon intact unless that contrast also fails.
