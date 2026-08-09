---
type: "Protocol"
title: "Semantic Atlas Experiment D — Compiling a Static Atlas from Weights"
description: "Pre-registered experiment testing whether low-rank weight-space structure predicts useful parts of an empirical Semantic Atlas before exhaustive autoregressive exploration."
tags: [semantic-atlas, preregistration, svd, weights, reduced-order-model]
timestamp: 2026-08-09T00:20:00Z
---

# Semantic Atlas Experiment D — Compiling a Static Atlas from Weights

## Question

How much navigationally useful structure can be extracted from a frozen LLM's weights before observing large numbers of autoregressive trajectories?

The experiment distinguishes **lexical compression** from **dynamic atlas compilation**. Preserving logits with a low-rank output head does not by itself show that semantic transitions are predictable.

## Part 1 — output-head compression

Read `model.get_output_embeddings().weight` from the frozen Qwen generator. Compute truncated SVD at ranks fixed in advance, initially:

`r = {8, 16, 32, 64, 128, 256}`.

For a frozen hidden-state test set, compare full and approximate logits.

### Metrics

- top-1 agreement;
- top-10/top-50 overlap;
- KL after softmax with numerically stable normalization;
- rank vs serialized size;
- rank vs matrix-multiplication cost estimate.

### Controls

- random orthonormal projector at the same rank;
- shuffled singular directions;
- PCA of hidden states without using output-head weights.

## Part 2 — SRF alignment

Project hidden states through the low-rank lexical map and fit the same SRF calibration used in Experiment A. Test whether lexical neighborhoods and empirical trajectory direction are preserved.

Do not infer semantic universality merely because singular vectors are interpretable or because high-frequency tokens cluster.

## Part 3 — local reduced dynamics

Partition the empirical atlas using the frozen cells from Experiment A. For cells with enough held-out transitions, fit

`q_(t+1) ~= A_c q_t + b_c`.

Evaluate one-step and multi-step prediction without teacher forcing. Compare with:

- cell mean next state;
- global linear dynamics;
- nearest-neighbor transition;
- random matrices matched for spectral norm.

## Part 4 — sparse dynamic calibration

Measure whether adding a small fraction of empirical transitions/Jacobians materially improves a weight-derived static map. Report the full calibration curve rather than one chosen sample size.

## Falsification

The weight-compilation hypothesis is weakened if:

- low-rank output-head structure does not outperform dimensionality-matched random controls;
- weight-derived geometry fails to correlate with empirical route structure;
- local operators lose predictive value immediately outside one-step teacher-forced evaluation;
- the amount of dynamic calibration required approaches the cost of building the empirical atlas directly.

## Claim boundary

A compressed lexical map is useful even if dynamic compilation fails, but it must be reported as lexical compression rather than a compiled Semantic Atlas.
