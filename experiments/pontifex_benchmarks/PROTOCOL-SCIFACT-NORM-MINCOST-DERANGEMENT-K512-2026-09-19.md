---
type: "Protocol"
title: "Pontifex SciFact K=512 residual-norm minimum-cost derangement"
tags: [pontifex, scifact, red-1, null, locality, preregistration]
timestamp: 2026-09-19T15:18:00-04:00
---

# Pontifex SciFact K=512 residual-norm minimum-cost derangement

## Status

Adaptive/prospective follow-up motivated by completed runs `35461028519` and `35463689486`. This protocol is frozen before the new held-out `D_test` relevance-grade read. It is not an independent replication.

## Question

Does exact residual-to-anchor identity add held-out SciFact retrieval utility beyond a nuisance control that destroys identity while making the replacement residuals as close as possible in normalized source-space A geometry, subject to the already-frozen eight residual-L2 strata?

## Information boundary

- `D_assembly`: canonical SciFact text/split membership and frozen encoder identities; no relevance grades.
- `D_student`: deterministic 80% of exact-test-text-overlap-filtered train queries. The K=512 anchors, Procrustes fit, residual vectors, eight residual-norm strata, and minimum-cost derangement are defined here.
- `D_val`: deterministic remaining 20%; coordinate-space `tau`/`lambda` selection only.
- `D_test`: official test qrels. Relevance grades must not be read until the map, strata, optimal derangement, manifests, query/document mapped coordinates, and decision rule below are frozen.
- No B/MPNet coordinates for test queries or corpus documents are encoded.
- Zero task labels/qrels may be used for fitting, hyperparameter selection, stratum construction, or derangement construction.

Expected frozen membership hashes are inherited from the completed K=512 mechanism series:

- anchors: `5a581b24b09b874bd65e759dfeabbe721eb66f947994470ceb3cee8768f4e80a`
- `D_student`: `bd5775940da2cb20d0ec5ee5ec4c9e35d871f82f12c0ff87e1955e38bd69ccf5`
- `D_val`: `7a699f93186bd3b8c6042c8941b045ed8197438fceb396b0d7178af34e9c349c`
- `D_test` membership: `c307ee1faa37715704375e5c59a071b0c579b3114bedcbf263d43111a2f15ebf`

## Null construction

Within each of the eight residual-L2 strata, form the normalized A-space cosine-distance cost matrix among the K=512 `D_student` anchors. Set self-donor edges to forbidden cost and solve the linear assignment problem that minimizes total **unperturbed** A-cosine distance. Concatenate the eight assignments into one perfect derangement `P*`.

`P*` must contain no fixed point and must be hashed before `D_test` relevance grades are opened. This is deliberately a single deterministic nuisance control: it is the most source-local perfect derangement available under the frozen strata, rather than a random permutation bank.

## Conditions

- `TRUE`: ordinary K=512 Pontifex residual map.
- `MINCOST_COUPLED`: apply `P*` to the residual identity on both query and document maps.

The primary paired effect is per-query nDCG@10(`TRUE`) minus nDCG@10(`MINCOST_COUPLED`).

## Frozen inference rule

Because a single deterministic optimum is not a permutation reference distribution, **no finite-bank permutation p-value will be reported or retrofitted**. The inferential summary is the paired-query bootstrap with 5,000 resamples using seed `20260919 + 1_800_000`.

For this adaptive test only:

- support for exact-identity utility beyond the distance-optimal nuisance requires the paired-query bootstrap 95% percentile interval to be strictly above zero;
- an interval crossing zero fails to support that claim;
- either outcome applies only to this frozen SciFact K=512 setup.

## Required locality calibration

Report, from `D_student` only:

1. individual nearest-nonself mean A-cosine distance;
2. minimum-cost perfect-derangement mean A-cosine distance;
3. random-within-stratum expected mean A-cosine distance.

The completed calibration run `35463689486` provides reference values `0.51386`, `0.53900`, and `0.87712`, respectively. The new run must reproduce them within numerical tolerance before any interpretation of `D_test` performance.

## Interpretation boundary

A positive result would support only the narrow statement that exact residual identity adds held-out retrieval utility beyond residual magnitude plus the strongest deterministic A-local perfect-derangement nuisance tested here. A negative result would further weaken exact-identity necessity.

Neither outcome establishes causal semantic locality, intrinsic/physical torus topology, universal transport superiority, native-B superiority, low-budget superiority, cross-dataset generalization, or `D_assembly -> D_student` generalization.
