---
type: "Interpretability Paper"
title: "Pontifex Torus — Addendum: c4 Interaction Gain Survives an Exchangeability Null, but Remains Tiny"
description: "A matched exchangeability-null calibration tests whether the very small c4 cross-interaction gain at 560 paired families can be reproduced by an equally large but sample-misaligned interaction block. The real aligned cross block beats the seed-matched null mean in 9/10 outer splits and every null replica in 7/10, strengthening the weak-signal interpretation without making the effect practically important."
tags: [pontifex, torus, transport, quadratic, interactions, null-model, exchangeability, calibration, c4, ablation, cartography]
timestamp: 2026-09-18T14:25:00-04:00
---

# Pontifex Torus — Addendum: c4 Interaction Gain Survives an Exchangeability Null, but Remains Tiny

## Question

The preceding c4 learning curve found a mean held-out gain of only `+2.25×10^-5` RMSE from the selected cross-interaction block at 560 paired families. That pattern was consistent with a weak, sample-limited interaction signal, but the effect was small enough that a more adversarial explanation remained plausible:

> could an equally large but irrelevant interaction block obtain a similar apparent gain simply because the inner model-selection procedure occasionally finds a favorable penalty?

This follow-up keeps the real protocol fixed and calibrates that tiny gain against a sample-exchangeability null.

## Protocol

The experiment reuses the same synthetic c4 field store and the same operational regime as the n=560 point of the previous learning curve:

- 800 whole text families;
- ten outer splits;
- 240 whole families in outer held-out test and 560 in outer train;
- a fixed 256-anchor B atlas built exclusively from the **outer-training** B embeddings;
- 512-point dense A responses with eight Fourier harmonics;
- standardized pairwise cross terms;
- the same linear penalty grid and cross penalty grid, including an explicit `cross=off` model;
- linear and cross penalties selected **only on an inner split of outer train**.

For the real model, each row of the cross-feature matrix remains paired with its own A-response family and B-affinity target.

For each outer split, eight null replicas are then generated. In each replica, the rows of the standardized cross-feature block are independently permuted in train and test. The linear features and B targets are left untouched. This preserves the marginal distribution and dimensionality of the cross block while destroying the sample-specific alignment that could carry a genuine interaction signal.

Each null replica is subjected to the same inner-only penalty selection as the real model. The real model is never tuned using a null result or an outer-test score.

There is one important epistemic distinction: outer held-out data are scored repeatedly for the **null calibration**. Therefore the 80 null scores are not a fresh one-shot benchmark and are not treated as 80 independent population samples or as a formal p-value. They answer the narrower predeclared question of whether the observed real gain is unusual under this specific exchangeability-null construction.

## Result

The real aligned interaction model exactly reproduces the previous n=560 result:

| quantity | real aligned cross block | exchangeability null |
|---|---:|---:|
| mean gain vs linear RMSE | **+0.00002251** | -0.00000888 |
| median gain vs linear RMSE | **+0.00002537** | 0.00000000 |
| positive gain | 8/10 outer splits | 15/80 replicas (18.75%) |
| gain standard deviation | — | 0.00003332 |

The paired calibration is more informative than the pooled means:

- real gain exceeds the **seed-matched null mean** in **9/10** outer splits;
- mean `(real gain - seed null mean)` is **+0.00003139** RMSE;
- median `(real gain - seed null mean)` is **+0.00002996** RMSE;
- only **14/80 = 17.5%** of null replicas reach or exceed the real gain of their corresponding outer split;
- in **7/10** outer splits, the real aligned gain is larger than **all eight** null replicas for that split.

The null is not merely centered near the real result. On average, irrelevant sample-misaligned cross features are slightly harmful, and the selector often neutralizes them. The real aligned cross block behaves differently enough that the earlier weak-signal interpretation becomes harder to dismiss as generic high-dimensional model-selection luck.

## Scientific update

The strongest defensible update is:

> at n=560, the tiny c4 cross-interaction gain contains sample-specific structure that is not reproduced by an equally large exchangeability-null cross block under the same inner-selection procedure.

This strengthens the statement that c4 has a **real but very low-SNR interaction component** under the current synthetic generator and representation.

It does **not** strengthen the practical claim. The absolute real gain remains only about `2.25×10^-5` RMSE, roughly 0.06% of the linear RMSE. A statistically interesting sign diagnostic can still be operationally negligible.

The result also does not rescue any stronger Torus claim. The experiment establishes that the aligned cross features carry more useful information than their sample-misaligned counterparts; it does not establish why that information exists, whether a toroidal topology causes it, or whether the same interaction geometry appears outside this synthetic construction.

## Evidence boundary

**Supported here:** conditional on this synthetic c4 generator, A/B encoders, fixed outer-train-only B atlas, Fourier representation, penalty grids, and n=560 paired families, the aligned cross-interaction block produces a small held-out improvement that is systematically better than a row-exchangeability null calibrated with the same model-selection procedure.

**Not established:** a population-level significance test; independence of the 80 null scores; practical relevance of the effect; monotonic growth beyond n=560; Torus causality; transfer to natural long-form text; robustness to other encoders or generators; end-to-end atlas sample efficiency; or predictive value for multi-teacher Assembly/student transfer.

The experiment does not instantiate, tune on, or read the reserved future partitions

\[
D_{assembly}\perp D_{student}\perp D_{val}\perp D_{test}.
\]

Those remain untouched.

## Updated working hypothesis

The c4 interaction component now has two independent pieces of supporting evidence within the synthetic regime:

1. increasing paired sample size moves the selected model from frequently `cross=off` toward a weak positive aligned-cross gain;
2. at n=560, the aligned cross block outperforms an equally large sample-misaligned exchangeability null in most outer splits.

The working hypothesis is therefore that the c4 generator induces a genuine but extremely small cross-mode dependency that is difficult to estimate and contributes little beyond the linear transport.

That remains a hypothesis about this synthetic regime, not a claim about semantic composition in general.

## Next discriminant

The next higher-information experiment should extend c4 beyond 560 paired examples **while separating the B-atlas construction pool from the paired transport-training pool**. A three-way design — atlas-only families, paired transport families, and untouched outer test — would avoid letting larger paired budgets simultaneously alter how much of the outer-training distribution is represented in the fixed atlas.

If the aligned-minus-null gap grows with paired n while the atlas is independently fixed, the sample-limited interaction interpretation strengthens. If the real gain remains near `2×10^-5` and the aligned-minus-null gap plateaus, c4 should be treated as effectively linear for practical purposes even though a tiny interaction signal is detectable.

## Reproducibility

- experiment: `experiments/pontifex_torus/c4_interaction_null_calibration.py`
- workflow: `.github/workflows/pontifex-c4-interaction-null.yml`
- decisive run: `https://github.com/franklinbaldo/papers/actions/runs/35379180635`
- artifact: `https://github.com/franklinbaldo/papers/actions/runs/35379180635/artifacts/10560898574`
