---
type: "Interpretability Paper"
title: "Pontifex Torus — Addendum: SciFact Separates Shared-Warp Coherence from Semantic-Specific Transport"
description: "Held-out SciFact ablations show a reproducible two-sided shared-warp effect but do not yet show that the correct residual-to-anchor correspondence reliably improves retrieval over a matched coupled scrambled warp."
tags: [pontifex, torus, scifact, retrieval, transport, coupling, null, mechanism, evidence-boundary]
timestamp: 2026-09-19T11:25:00-04:00
---

# Pontifex Torus — Addendum: SciFact Separates Shared-Warp Coherence from Semantic-Specific Transport

## Why this addendum matters

The external BEIR/SciFact transport benchmark produced an attractive K=512 point estimate: the full Pontifex residual map reached nDCG@10 `0.649954` versus `0.646066` for the same Procrustes coarse map. Read alone, that could be mistaken for evidence that the learned local residuals had captured a semantically specific A→B transport law.

The held-out mechanism ablations make the boundary substantially sharper. They separate three claims that should not be conflated:

1. applying a local residual to both retrieval sides can create a non-additive interaction;
2. applying the **same** nonlinear warp to both sides can preserve retrieval geometry better than applying different warps;
3. the **correct A↔B residual-to-anchor assignment** contributes utility beyond generic shared-warp coherence.

The current evidence supports (1) and (2) more clearly than (3).

## Frozen SciFact information boundary

All reported mechanism tests preserve the parent split contract:

- `D_assembly`: SciFact text/split membership and frozen encoder identities; no relevance grades;
- `D_student`: deterministic filtered train-query A/B representation pairs;
- `D_val`: disjoint filtered train queries used only for coordinate-level transport selection;
- `D_test`: official test qrels opened only after maps, selected hyperparameters, and null assignments are frozen.

The mechanism runs do **not** encode target-space MPNet coordinates for SciFact test queries or corpus documents. No SciFact task label is used for fit or selection.

## Result 1 — two-sided residual interaction exists, but downstream superiority is not established

At the predeclared K=256 mechanism point:

| contrast | mean paired-query delta | 95% bootstrap interval |
|---|---:|---:|
| query-side residual only, `RC-CC` | -0.005274 | [-0.015654, +0.005355] |
| document-side residual only, `CR-CC` | -0.012846 | [-0.025648, +0.000035] |
| full residual, `RR-CC` | -0.001108 | [-0.013902, +0.011501] |
| two-sided interaction, `RR-RC-CR+CC` | **+0.017012** | **[+0.002184, +0.032110]** |

Thus neither side alone explains a gain, and the full residual map does not reliably beat Procrustes. The positive result is narrower: the effect of applying the residual to both sides is non-additive.

At K=512 the same pattern is stronger:

- `RR-CC = +0.003888`, but 95% interval `[-0.014190, +0.021739]`;
- `RC-CC = -0.008264`;
- `CR-CC = -0.032575`, interval `[-0.055922, -0.010691]`;
- `RR-RC-CR+CC = +0.044726`, interval **[+0.017208, +0.073570]**.

The K=512 point estimate remains interesting but is not a reliable downstream win by itself.

## Result 2 — K=256 coupling-specificity null

A prospective follow-up kept K, `tau`, `lambda`, the residual-vector marginal distribution, and two-sided application fixed while changing only residual-to-anchor identity.

| condition | nDCG@10 |
|---|---:|
| TRUE correspondence | 0.645311 |
| COUPLED-NULL median | 0.642651 |
| COUPLED-NULL mean | 0.643434 |
| INDEPENDENT-NULL median | 0.634310 |
| INDEPENDENT-NULL mean | 0.633493 |

### Correct semantic assignment versus a shared scrambled warp

The correct correspondence did **not** reliably beat a coupled scrambled warp:

- `TRUE - COUPLED` paired-query mean = `+0.001878`;
- 95% interval = `[-0.007845, +0.011360]`;
- finite-bank upper-tail p = `0.3125`.

This is negative evidence against a strong semantic-specificity interpretation of the K=256 residual map.

### Shared warp versus independent warps

The coherence effect is clearer:

- `COUPLED - INDEPENDENT` paired-query mean = **`+0.009941`**;
- 95% interval = **`[+0.001884, +0.018939]`**;
- bootstrap probability mean > 0 = `0.993`.

Therefore a substantial part of the two-sided interaction can be produced by applying the same nonlinear deformation coherently to queries and documents even when the learned anchor identities are deliberately scrambled.

## Evidence boundary

**Supported now:** on this held-out SciFact benchmark, two-sided transformation coherence matters. The full residual interaction is non-additive, and a shared scrambled warp outperforms independently scrambled query/document warps at K=256.

**Not supported now:** a reliable K=256 downstream benefit uniquely attributable to the correct semantic A↔B residual assignment; a reliable full-map nDCG improvement over Procrustes; low-budget dominance; causal semantic locality; intrinsic toroidal topology; or universal transport superiority.

This distinction is scientifically important because it converts what looked like a mechanism win into a more precise hypothesis: **semantic-specific correspondence may emerge only at higher information budgets, while shared-warp coherence is already detectable at K=256.**

## Frozen next discriminant: K=512

The larger-budget residual-side result motivates — but does not confirm — one follow-up: repeat the coupling-specificity null at K=512 with a 63-permutation null bank.

The protocol is frozen in `experiments/pontifex_benchmarks/PROTOCOL-SCIFACT-COUPLING-SPECIFICITY-K512-2026-09-19.md`.

The K=512 run counts as evidence for semantic specificity only if both conditions hold prospectively:

1. paired-query 95% bootstrap interval for `TRUE - mean(COUPLED-NULL)` is strictly above zero;
2. finite-bank upper-tail p <= 0.05.

If that test fails while `COUPLED > INDEPENDENT` remains positive, the present evidence should be read primarily as **shared retrieval-geometry coherence under a common warp**, not as demonstrated semantic-local transport.

## Reproducibility

Completed evidence:

- SciFact residual-side ablation: <https://github.com/franklinbaldo/papers/actions/runs/35449038241>
- SciFact coupling-specificity K=256: <https://github.com/franklinbaldo/papers/actions/runs/35449589119>
- SciFact parent transport: <https://github.com/franklinbaldo/papers/actions/runs/35449589115>

The K=512 scaling diagnostic is implemented separately so that the completed K=256 protocol and executable remain historically frozen.
