---
type: "Protocol"
title: "Pontifex NFCorpus local shared-warp replication K=256"
description: "Preregistered independent-dataset replication of the SciFact shared-warp coherence result using NFCorpus and local residual-norm-matched derangement banks."
tags: [pontifex, red-1, nfcorpus, beir, replication, shared-warp, null, preregistration]
timestamp: 2026-09-19T16:11:00-04:00
---

# Pontifex NFCorpus local shared-warp replication K=256

## Status

**Prospective independent-dataset replication.** This protocol is frozen on a dedicated preregistration commit before the first NFCorpus `D_test` relevance-grade read. It is motivated by the completed SciFact shared-warp result, but NFCorpus test outcomes were not inspected when the hypothesis, split roles, nuisance family, locality threshold, seeds, or decision rule below were chosen.

The replication changes the dataset/domain while holding the encoder pair fixed:

- A: `sentence-transformers/all-MiniLM-L6-v2@1110a243fdf4706b3f48f1d95db1a4f5529b4d41`
- B: `sentence-transformers/all-mpnet-base-v2@e8c3b32edf5434bc2275fc9bab85f82640a19130`
- dataset: canonical BEIR NFCorpus archive, MD5 `a89dba18a62ef92f7d323ec890a0d38d`.

This design is therefore an independent **dataset** replication, not an independent representation-pair replication.

## Question

Does the narrow SciFact mechanism result replicate on NFCorpus: after exact residual identity is destroyed, does applying the **same** local residual permutation to query and document maps preserve more held-out retrieval utility than applying independently frozen local permutations to the two sides?

The primary contrast is:

`mean(LOCAL_COUPLED) - mean(LOCAL_INDEPENDENT)` per-query nDCG@10.

The stronger exact-identity question (`TRUE - LOCAL_COUPLED`) is secondary here and is not the preregistered replication target.

## Information boundary

Four roles remain non-interchangeable.

- `D_assembly`: canonical NFCorpus archive; corpus/query text; train/test split membership; frozen encoder identities and revisions. Relevance grades are not used for map fitting, hyperparameter selection, stratum construction, nuisance-bank construction, or locality calibration.
- `D_student`: deterministic 80% of NFCorpus train-query texts after excluding exact text matches with test queries. A/B coordinates from this pool define the K=256 anchors, Procrustes fit, residual vectors, residual-norm strata, and both local nuisance banks.
- `D_val`: deterministic remaining 20% of the filtered train queries. A/B coordinates are used only to select `tau` and `lambda` by coordinate reconstruction loss.
- `D_test`: official NFCorpus test relevance grades. Grades are loaded only after the map, selected hyperparameters, residual strata, nuisance banks, locality calibration, membership manifests, A-test coordinates, A-corpus coordinates, and map ingredients are frozen.

Additional guards:

- B coordinates for NFCorpus test queries are never encoded.
- B coordinates for NFCorpus corpus documents are never encoded.
- task labels/qrel grades used for fit or selection: zero.
- exact train/test query-text overlaps are removed before the student/validation split.
- the train/student/validation/test/corpus ID manifests and both nuisance-bank hashes are emitted in the result.

## Frozen constants

- seed: `20260919`
- K: `256`
- residual-norm strata: `8` equal-count strata
- local nulls per bank: `31`
- paired-query bootstrap resamples: `5000`
- minimum accepted locality capture: `0.50`
- noisy-assignment jitter ladder: `[0.01, 0.02, 0.05, 0.10, 0.20, 0.40]`
- maximum candidates per jitter level: `400`
- metric: nDCG@10
- primary decision: paired-query bootstrap 95% percentile CI for `LOCAL_COUPLED - LOCAL_INDEPENDENT` must lie strictly above zero.

No finite-bank p-value is required for the primary replication decision. The 31-member banks are used to average over frozen local nuisance assignments; inference is across held-out test queries via the preregistered paired bootstrap.

## Local nuisance construction

The null must destroy exact residual identity while remaining substantially more local in normalized source-space A geometry than random within the same residual-magnitude stratum.

1. Fit the K=256 Pontifex map from `D_student`; use `D_val` only to freeze `tau` and `lambda`.
2. Sort the 256 residual vectors by L2 norm into eight equal-count strata of 32 anchors.
3. Within each stratum, compute normalized A-space cosine donor distances.
4. Compute the deterministic minimum-cost perfect derangement. This is the attainable locality reference under the frozen strata.
5. Compute the expected random non-self donor distance within the same strata.
6. Define locality capture as:

   `(random_distance - candidate_distance) / (random_distance - minimum_cost_distance)`.

7. Generate candidate perfect derangements by solving independent noisy assignment problems within each stratum. The diagonal is forbidden.
8. Accept a candidate only if its **unperturbed** mean donor distance has locality capture at least `0.50`.
9. Freeze 31 unique query-bank permutations and 31 unique document-bank permutations from separate RNG streams.
10. Require the two banks to be disjoint. If the frozen ladder/attempt budget cannot produce the required banks, the experiment fails closed **before `D_test` grades are opened**.

The run must report the minimum-cost distance, random-within-stratum expectation, bank mean/max distance, mean/min locality capture, jitter values that generated accepted assignments, and hashes of both banks.

This makes the nuisance family stronger than a purely global or magnitude-only shuffle: every accepted assignment is both residual-norm matched and explicitly constrained toward A-space locality.

## Conditions

- `TRUE`: ordinary K=256 Pontifex local-residual map.
- `LOCAL_COUPLED_j`: destroy exact identity with query-bank permutation `j`, and apply that same permutation to both query and document sides.
- `LOCAL_INDEPENDENT_j`: apply query-bank permutation `j` to queries and the separately frozen document-bank permutation `j` to documents.

All three conditions use the same K anchors, Procrustes map, residual vectors, `tau`, and `lambda`. Only residual identity/coupling differs.

## Primary decision rule

For each held-out NFCorpus test query, average nDCG@10 across the 31 coupled nulls and across the 31 independent nulls. Form the paired per-query difference:

`delta_shared(q) = mean_j LOCAL_COUPLED_j(q) - mean_j LOCAL_INDEPENDENT_j(q)`.

Bootstrap the held-out queries with replacement 5,000 times using seed `20260919 + 3_000_000`.

- **Replicated:** 95% percentile CI is strictly above zero.
- **Not replicated:** interval touches or crosses zero.
- A negative result is retained and reported symmetrically; it is not a CI failure.

## Secondary exact-identity contrast

Also report:

`delta_identity(q) = TRUE(q) - mean_j LOCAL_COUPLED_j(q)`,

with a 5,000-resample paired-query bootstrap using seed `20260919 + 4_000_000`.

This is secondary. A positive or negative result does not alter the preregistered status of the primary shared-warp replication.

## Interpretation boundary

A positive primary result would support only the narrow statement that, on a second BEIR dataset with the same frozen encoder pair, a **shared two-sided local residual deformation** preserves more held-out retrieval structure than independently deformed sides.

A negative primary result would be real falsification pressure on the apparent cross-dataset robustness of the SciFact shared-warp result.

Neither outcome demonstrates:

- an intrinsic or physical torus;
- causal semantic locality;
- universal transport superiority;
- native-B superiority;
- exact residual identity necessity;
- low-budget dominance;
- broad cross-representation generalization;
- Assembly-to-student generalization.

## Reproducibility rule

The preregistration commit, experimental script, workflow run, resolved manifests, and final findings must all be linked from `pontifex_red1_empirical.md`. The experimental PR remains unmerged.
