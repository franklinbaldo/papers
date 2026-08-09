---
type: "Protocol"
title: "Semantic Atlas Experiment D — Compiling Lexical and Dynamic Structure from Weights"
description: "Pre-registered experiment testing whether low-rank lexical structure and local semantic Jacobians can be compiled from frozen LLM weights before large-scale trajectory observation."
tags: [semantic-atlas, preregistration, svd, weights, jacobian, reduced-order-model]
timestamp: 2026-08-09T00:20:00Z
---

# Semantic Atlas Experiment D — Compiling Lexical and Dynamic Structure from Weights

## Question

How much navigationally useful **static and dynamic** structure can be extracted from a frozen LLM's weights before observing large numbers of autoregressive trajectories?

The experiment distinguishes three objects:

1. **lexical weight structure** — truncated SVD of the output head;
2. **weight-derived local dynamics** — a Jacobian of a differentiable frozen-transformer semantic transition;
3. **empirical reduced dynamics** — `q_(t+1) ~= A_c q_t + b_c` fitted from observed transitions.

Only (1) and (2) count as compilation from weights. Object (3) is a baseline and later calibration target, not evidence for weight-derived dynamics.

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

## Part 2 — SRF bridge

Use a frozen linear projection from generator hidden state into the calibrated SRF. This projection is fitted only on the registered calibration split; all dynamic evaluation uses held-out prefixes/transitions.

Do not infer semantic universality merely because singular vectors are interpretable or because high-frequency tokens cluster.

## Part 3 — weight-derived local semantic dynamics

For each frozen evaluation prefix, build a differentiable one-step transition from the **frozen Qwen weights**:

1. obtain the prefix input embeddings;
2. treat only the final input embedding as the local variable and keep earlier context fixed;
3. run the transformer and obtain next-token logits;
4. form a differentiable soft expected next-token embedding from those logits;
5. append that soft token and run one additional frozen transformer step;
6. project the resulting final hidden state into the SRF;
7. use autograd to compile the local Jacobian of this map at the prefix anchor.

The resulting `WeightJacobianOperator` is therefore compiled from model parameters plus the frozen SRF projection. It **does not accept empirical `(state, next_state)` pairs during construction**.

The soft-token step is a relaxation of discrete generation, not a fact about how the model samples. Its value is empirical: test whether its local directions predict the subsequently observed discrete SRF transition better than matched random Jacobians and static lexical baselines.

### Metrics

- cosine agreement between predicted and observed transition direction;
- endpoint error for small registered perturbations;
- singular-spectrum concentration of the semantic Jacobian;
- JVP agreement under held-out intervention directions;
- performance versus random Jacobians matched for Frobenius/spectral norm;
- performance versus output-head-only linearization.

If this part fails, the PR may still support lexical weight-space compression, but **not dynamic atlas compilation**.

## Part 4 — empirical reduced-dynamics baseline

Partition the empirical atlas using the frozen cells from Experiment A. For cells with enough training transitions, fit the explicitly empirical baseline

`q_(t+1) ~= A_c q_t + b_c`.

Evaluate one-step and multi-step prediction without teacher forcing. Compare with:

- weight-derived `WeightJacobianOperator`;
- cell mean next state;
- global empirical linear dynamics;
- nearest-neighbor transition;
- random matrices matched for spectral norm.

The paper must label this model **empirical reduced dynamics**, never "compiled from weights."

## Part 5 — sparse dynamic calibration

Starting from the weight-derived Jacobian operator, allow increasing registered fractions of empirical transitions to calibrate a residual correction. Report the full curve from zero empirical transitions through the empirical-atlas baseline.

This is the direct test of whether weights provide useful dynamic structure **before** walking the territory. If the zero-data operator has no predictive advantage, a later empirically fitted `A_c` cannot retroactively make the weight-compilation claim true.

## Falsification

The weight-compilation hypothesis is weakened if:

- low-rank output-head structure does not outperform dimensionality-matched random controls;
- the zero-trajectory weight-derived semantic Jacobian does not predict held-out discrete transition directions better than matched random/static controls;
- any advantage disappears outside an infinitesimal local neighborhood;
- useful prediction appears only after enough empirical calibration to approach the cost of building the empirical atlas directly.

## Claim boundary

A compressed lexical map can be useful even if dynamic compilation fails. An empirical `LocalLinearDynamics.fit(states, next_states)` can also be useful. Neither is, by itself, evidence that transformer dynamics were compiled from weights. The dynamic compilation claim belongs specifically to the frozen-weight semantic Jacobian and whatever held-out predictive advantage it demonstrates.
