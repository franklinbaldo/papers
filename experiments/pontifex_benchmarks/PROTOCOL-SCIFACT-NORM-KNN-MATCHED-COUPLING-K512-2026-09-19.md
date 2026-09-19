# Protocol: SciFact residual-norm + A-KNN matched coupling specificity, K=512

Status: **prospective/adaptive follow-up, frozen before the new D_test read**.

## Motivation

The completed balanced-group norm+local-A run (GitHub Actions `35457676312`) did not validate the intended nuisance control as strongly as its name implied. Its query-side donor cosine-distance diagnostic was mean `0.78787` with p95 `0.99686` (document side mean `0.78952`, p95 `0.99686`). Therefore that run is evidence for a **coarse balanced-group** null, not a tight local-A null. This protocol strengthens locality explicitly rather than relabeling the earlier result.

## Frozen information boundary

- `D_assembly`: canonical SciFact text/split membership and encoder identities only; no relevance grades.
- `D_student`: deterministic 80% of overlap-filtered train queries. It alone defines the K=512 paired coordinates, residual-norm strata, and A-space donor graph.
- `D_val`: deterministic remaining 20%; used only for coordinate-space `tau` / `lambda` selection.
- `D_test`: official SciFact test qrels; grades are not read until the map, strata, KNN graph, and both null banks are frozen and hashed.
- B/MPNet coordinates for test queries and corpus documents are not encoded.
- Task labels/qrels used for fit or selection: zero.

Expected frozen manifests remain identical to the prior K=512 family for student, validation, test, corpus, and anchor identities.

## Stronger null

Residuals remain restricted to the same 8 equal-count residual-L2 strata (64 anchors each). For every anchor, eligible donors are restricted to its **16 nearest non-self anchors in normalized A-space within the same residual-norm stratum**. Rank 1 means the nearest eligible A-space anchor.

Each null permutation is obtained as a random-cost minimum-cost perfect matching over this fixed bipartite candidate graph. The diagonal is forbidden, so every accepted permutation is a derangement. Sixty-three unique query-bank permutations and sixty-three unique document-bank permutations are frozen using distinct deterministic RNG streams.

This construction guarantees every moved residual donor has source-space neighbor rank `<=16` within its norm stratum. The run must report mean/median/p95/max cosine donor distance and mean/p95/max donor rank. If any donor rank exceeds 16, or the graph has no perfect derangement, the experiment fails as an infrastructure/protocol failure rather than silently relaxing locality.

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

A positive semantic-specificity result would support the narrow claim that exact residual identity contributes held-out SciFact retrieval utility beyond residual magnitude plus a hard local A-space donor-rank nuisance control. A negative result would further weaken that exact-identity claim.

Neither outcome establishes causal semantic locality, torus topology, physical geometry, universal superiority of Pontifex transport, native-B superiority, low-budget superiority, cross-dataset generalization, or `D_assembly -> D_student` generalization.
