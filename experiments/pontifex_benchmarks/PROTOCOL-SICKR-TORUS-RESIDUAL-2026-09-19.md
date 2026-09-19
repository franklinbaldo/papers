---
type: "Experiment Protocol"
title: "Pontifex Torus SICK-R residual transport benchmark"
description: "Prospective cross-benchmark test of a low-capacity local residual field on top of the same Procrustes coarse A→B alignment, with the official SICK relatedness metric and strict same-K information budget."
timestamp: 2026-09-19T08:58:00-04:00
tags: [pontifex, torus, benchmark, sick-r, transport, residual, anti-leakage]
---

# Question

Given two frozen semantic spaces A and B and only K unlabeled shared sentence correspondences from the SICK training split, does the Pontifex Torus local deformation/residual stage improve on the same frozen Procrustes coarse alignment in B-specific reconstruction and in the external SICK semantic-relatedness task?

This is the direct test that follows the STS-B isometry audit. Procrustes is not treated as a new alternative architecture: it is the cheap global/coarse alignment stage. The discriminant comparison is the same coarse map **with versus without** the low-capacity local residual field.

# External task and frozen spaces

- Benchmark: SICK / SemEval-2014 Task 1 semantic relatedness, loaded from `RobZamp/sick`.
- Official primary task metric: Pearson correlation between predicted pair similarity and `relatedness_score`.
- Secondary task metric: Spearman correlation.
- A: `sentence-transformers/all-MiniLM-L6-v2`.
- B: `sentence-transformers/all-mpnet-base-v2`.
- Shared-correspondence budgets K: `8, 16, 32, 64, 128, 256`.
- Seed: `20260919`.

The A/B model pair was selected before this SICK-R run from the earlier STS-B work, so this is a fresh **cross-benchmark replication**, not a claim of model-pair-independent confirmation.

# Same-K information contract

For every K, all fitted transport methods may consume exactly the same K unlabeled A↔B sentence correspondences drawn from the SICK train split. No SICK relatedness label is used to fit or tune the transport. Hyperparameters for the Torus residual are selected only by leave-one-out reconstruction within those same K correspondence pairs. The validation split is used only for pre-test diagnostics; it does not add A↔B correspondences to the fitting budget. Test is final evaluation only.

Train sentences that occur verbatim in validation or test are excluded before the anchor permutation. The script records dataset fingerprints, candidate/overlap counts, anchor hashes, split hashes and the seed.

Pretraining overlap between A and B is classified as `possible`; overlap between either encoder's unknown pretraining corpus and SICK is `unknown`. Such pretraining overlap is not adapter leakage. Test labels, test B coordinates, or target-derived test information entering fit/selection would be leakage and are prohibited.

# Methods

## A-only and B-oracle

A-only is the frozen A-space cosine baseline. B-oracle is the frozen B-space cosine ceiling/reference; B test embeddings are never available to fitted A→B methods.

## Coarse map: rectangular Procrustes

Fit the same centered rectangular Procrustes map on the K anchors:

`z(x) = (x - mean(A_K)) W + mean(B_K)`.

Because the rectangular map is semi-orthogonal, retained A-space cosine utility alone is not evidence of transport. B-specific reconstruction diagnostics are mandatory.

## Pontifex Torus residual

Compute anchor residuals after the coarse map:

`r_i = B_i - z(A_i)`.

For an unseen A vector x, estimate a local residual field from neighboring anchors in A geometry:

`r_hat(x) = Σ_i softmax(cos(x,A_i)/tau)_i r_i`

and output

`T(x) = z(x) + lambda * r_hat(x)`.

Frozen hyperparameter grid:

- `tau ∈ {0.02, 0.05, 0.10, 0.20, 0.40, 0.80}`
- `lambda ∈ {0.25, 0.50, 1.00, 1.50}`

Select `(tau, lambda)` using only the K anchors, by leave-one-out residual reconstruction: each anchor's residual prediction excludes that anchor from the kernel weights, and the selected pair minimizes mean `1 - cosine(predicted_B_i, true_B_i)`. No task labels participate.

# Controls / baselines

At each K report:

1. A-only.
2. B-oracle.
3. paired Procrustes coarse map.
4. paired Procrustes + Torus residual.
5. same paired Procrustes + **shuffled residual field** (residual vectors permuted across anchors; same capacity and K).
6. fully shuffled A↔B correspondence Procrustes + residual control.
7. Ridge A→B baseline if it can be tuned using only the same K pairs without consuming extra validation correspondences; otherwise record it as deferred rather than giving it privileged information.

# Primary decision rules

The Torus residual counts as positive incremental evidence only if, on untouched SICK test data:

1. it improves direct B-coordinate alignment over the paired Procrustes coarse map;
2. it improves B pair-geometry reconstruction over the paired Procrustes coarse map;
3. the correctly paired residual beats the shuffled-residual capacity control on those B-specific endpoints; and
4. any downstream Pearson/Spearman improvement is reported separately rather than used to substitute for B-specific transport evidence.

A downstream task gain without B-specific gains is task adaptation, not evidence for the proposed latent-space transport mechanism. A B-specific gain without downstream gain is mechanistic evidence but not task competitiveness.

# Geometry diagnostics

On validation and test, using B only as evaluation oracle, report:

- sentencewise cosine(`predicted_B`, `true_B`), mean;
- pair-cosine RMSE against true B pair cosines;
- Spearman between predicted and true B pair cosines;
- downstream Pearson and Spearman against SICK relatedness labels.

# Budget and cost accounting

Record K, number of task labels used for fitting (`0`), stored anchor floats, coarse-map size, residual storage, selected scalars, fit/selection time and test inference time. The key fair comparison is paired Procrustes versus the same paired Procrustes plus residual at identical K and access to the same correspondence information.

# Leakage audit status before run

`PASS / protocol-frozen`: no test result has been inspected for this SICK-R experiment at protocol freeze. Dataset and model pair are known from public sources/prior STS-B work, but SICK test outcomes for this implementation have not been used to choose the above K values, hyperparameter grids or decision rules.
