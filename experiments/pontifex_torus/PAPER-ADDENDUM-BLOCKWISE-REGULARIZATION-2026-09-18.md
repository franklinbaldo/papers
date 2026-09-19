---
type: "Interpretability Paper"
title: "Pontifex Torus — Addendum: The c3/c4 Sign Flip Is Mostly a Shared-Penalty Artifact"
description: "A ten-split blockwise Ridge ablation shows that independently shrinking linear and cross-interaction transport coefficients removes the c3/c4 held-out harm seen under a single shared penalty. c3 becomes consistently positive; c4 becomes effectively neutral."
tags: [pontifex, torus, transport, quadratic, regularization, blockwise-ridge, generalization, clause-complexity, ablation, cartography]
timestamp: 2026-09-18T12:23:00-04:00
---

# Pontifex Torus — Addendum: The c3/c4 Sign Flip Is Mostly a Shared-Penalty Artifact

## Question

The preceding generalization-gap addendum showed that widening a single Ridge penalty removed most of the apparent c2-c4 failure of degree-2 A→B transport, but c3 remained approximately neutral and c4 weakly negative. The richer models were also selecting very strong regularization, leaving open a more specific estimator question:

> are linear Fourier terms and cross-interaction terms being forced to share a penalty even though their useful signal-to-variance ratios differ sharply?

This experiment tests that possibility directly. It is not a new topology test and it does not use the future multi-teacher benchmark.

## Protocol

The experiment reuses the paired c1/c2/c3/c4/repeat4 field stores: 800 families per regime, eight deterministic size-1 probes per text, eight Fourier harmonics, 256 B anchors, whole-family 70/30 outer train/test splits, and no access to held-out families during model selection.

Ten outer splits (`seed=0..9`) are evaluated. Inside each outer-training set, hyperparameters are selected on a deterministic inner split. Four transport estimators are compared:

1. `linear` — standardized Fourier features only;
2. `legacy_shared` — linear + raw pairwise cross terms under one shared Ridge penalty;
3. `scaled_shared` — the cross block is standardized independently, but still shares one penalty with the linear block;
4. `blockwise` — linear and independently standardized cross blocks receive separately selected L2 penalties.

The blockwise model is implemented as generalized Ridge by dividing each block by the square root of its selected penalty and fitting `Ridge(alpha=1)`. The search grid for each penalty is

`0.1, 1, 10, 100, 1000, 10000, 100000, 1000000`.

All preprocessing scalers are fit on outer-training data only. Outer-test families are scored only after the inner selection is complete.

## Result

Mean held-out affinity RMSE across ten outer splits:

| regime | linear | legacy shared | scaled shared | blockwise | blockwise gain vs linear | blockwise wins |
|---|---:|---:|---:|---:|---:|---:|
| `c1` | 0.058826 | 0.052409 | 0.052415 | **0.052383** | **+0.006443** | 10/10 |
| `c2` | 0.061830 | 0.061249 | 0.061104 | **0.060579** | **+0.001250** | 10/10 |
| `c3` | 0.049993 | 0.050156 | 0.050134 | **0.049749** | **+0.000243** | 10/10 |
| `c4` | 0.037764 | 0.038214 | 0.038190 | **0.037748** | **+0.000016** | 9/10 |
| `repeat4` | 0.041027 | 0.040507 | 0.040471 | **0.039741** | **+0.001287** | 10/10 |

Two observations matter.

First, **independent standardization is not the rescue**. `scaled_shared` remains negative versus linear at c3 (`-0.000141`) and c4 (`-0.000426`). The sign changes only when the interaction block is allowed to shrink separately.

Second, the selected penalties become increasingly anisotropic with compositional complexity. At c2 the cross block is usually assigned penalty `1000` while the linear block remains between `1` and `100`. At c3 the cross penalty is `1000` or `10000`, while the linear block stays between `1` and `100`. At c4 the cross penalty rises to `10000`-`1000000`, while the linear block is `100` in nine of ten splits. Three c4 splits hit the maximum cross penalty of `1000000`.

That pattern is exactly what a shared scalar penalty cannot express: preserving useful low-order linear structure while aggressively shrinking the much higher-variance interaction block.

## What changed scientifically

The earlier negative c3/c4 result should no longer be described as evidence that degree-2 transport structurally breaks under multi-clause composition.

Under ten fresh outer splits, the legacy shared-penalty model is still negative at c3 (`-0.000163` mean gain versus linear, only 2/10 wins) and c4 (`-0.000450`, 0/10 wins). The blockwise model changes c3 to a small but consistent positive effect (`+0.000243`, 10/10 wins) and reduces c4 to practical neutrality (`+0.000016`, 9/10 wins).

The c4 result deserves restraint. Because the selected cross penalty reaches `10^6` in three splits and the mean benefit is only `1.6e-5` RMSE, this is **not evidence that cross interactions remain useful at c4**. It is evidence that the previous c4 harm can be removed by allowing the estimator to nearly turn those interactions off without simultaneously over-shrinking the linear block.

The stronger positive result is c3: the same blockwise estimator gives a held-out improvement over linear in all ten outer splits while the shared-penalty variants remain negative on average.

## Evidence boundary

**Supported here:** on this synthetic paired cartography generator, with whole-family train/test isolation and train-only hyperparameter selection, the c3/c4 negative sign under ordinary shared-penalty Ridge is largely an estimator-regularization artifact. Separate shrinkage restores a reproducible small c3 advantage and eliminates practically all c4 harm.

**Not established:** that c4 benefits materially from interaction terms; that the selected penalty ratios reflect a biological or semantic law; that clause count itself is causal; that the Torus is the correct topology; that the same anisotropic regularization transfers to natural long-form text; or that this pairwise A→B cartography predicts multi-teacher Assembly/student transfer.

The experiment does not instantiate, tune on, or read the reserved future partitions

\[
D_{assembly}\perp D_{student}\perp D_{val}\perp D_{test}.
\]

Those remain untouched.

## Updated working hypothesis

A better current hypothesis is not "composition breaks quadratic transport." It is:

> as compositional complexity rises, useful interaction signal becomes weak relative to interaction-block variance, so transport needs strongly anisotropic shrinkage; low-order linear structure remains much less regularized.

That hypothesis is compatible with c2/c3 and with the near-linear c4 optimum, but it remains a hypothesis about this generator.

## Next discriminant

The highest-information next step is to determine whether c4 is genuinely best at zero interaction contribution. A continuous or finer logarithmic cross-penalty sweep around `10^4..10^8`, with the linear penalty selected independently, should estimate the c4 risk curve and compare its optimum against the explicit `cross=off` nested model. Repeating that test at larger `n` would then distinguish "interaction signal vanishes" from "interaction signal exists but current sample size cannot estimate it."

## Reproducibility

- experiment: `experiments/pontifex_torus/blockwise_regularization_ablation.py`
- workflow: `.github/workflows/pontifex-blockwise-regularization.yml`
- initial 3-split run: `https://github.com/franklinbaldo/papers/actions/runs/35367428360`
- initial artifact: `https://github.com/franklinbaldo/papers/actions/runs/35367428360/artifacts/10557026524`
- decisive 10-split run: `https://github.com/franklinbaldo/papers/actions/runs/35367673458`
- decisive artifact: `https://github.com/franklinbaldo/papers/actions/runs/35367673458/artifacts/10556843205`
