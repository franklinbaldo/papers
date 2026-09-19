---
type: "Findings"
title: "Pontifex SciFact residual-side ablation findings"
description: "Held-out SciFact retrieval shows a positive non-additive two-sided residual interaction without a reliable full-map improvement over Procrustes."
timestamp: 2026-09-19T10:43:00-04:00
tags: [pontifex, scifact, retrieval, ablation, transport, holdout, mechanism]
---

# Pontifex SciFact residual-side ablation findings

## Status

**Completed held-out external mechanism ablation.** Protocol: `PROTOCOL-SCIFACT-RESIDUAL-SIDE-ABLATION-2026-09-19.md`. Run: <https://github.com/franklinbaldo/papers/actions/runs/35449038241>. Artifact: <https://github.com/franklinbaldo/papers/actions/runs/35449038241/artifacts/10586685329>.

The executable passed while preserving the declared information boundary: no MPNet/B coordinate was generated for SciFact test queries or corpus documents, and test relevance grades were loaded only after every K-specific map and hyperparameter choice was frozen.

## Primary result: K=256

The predeclared primary mechanism point was `K=256`.

| Cell / contrast | nDCG@10 or mean paired delta | 95% paired-query bootstrap interval |
|---|---:|---:|
| `CC` Procrustes | 0.646420 | — |
| `RC` query residual only | 0.641145 | — |
| `CR` document residual only | 0.633574 | — |
| `RR` both sides residual | 0.645311 | — |
| query side `RC-CC` | -0.005274 | [-0.015654, +0.005355] |
| document side `CR-CC` | -0.012846 | [-0.025648, +0.000035] |
| full `RR-CC` | -0.001108 | [-0.013902, +0.011501] |
| interaction `RR-RC-CR+CC` | **+0.017012** | **[+0.002184, +0.032110]** |

The important distinction is that the positive interaction is **not** a positive result for downstream superiority. The full residual map does not reliably beat the same Procrustes map at the primary point; its paired-query interval spans zero. Instead, applying the residual on either side alone is harmful on average, while applying it coherently to both sides recovers most of that harm.

## Scaling diagnostic

The same qualitative pattern strengthens at `K=512`, which was predeclared as a scaling diagnostic rather than a second confirmatory point:

- `CC = 0.646066`;
- `RR = 0.649954`, hence `RR-CC = +0.003888`, but the bootstrap interval remains wide `[-0.014190, +0.021739]`;
- query-only `RC-CC = -0.008264`;
- document-only `CR-CC = -0.032575`, interval `[-0.055922, -0.010691]`;
- interaction `RR-RC-CR+CC = +0.044726`, interval `[+0.017208, +0.073570]`.

Across K, the full downstream delta is small and unstable compared with the much clearer non-additive interaction at larger budgets. This argues against summarizing the run as evidence that Pontifex already improves SciFact retrieval.

## Evidence versus hypothesis

### Evidence from this run

1. At `K=256`, the full residual does **not** show a reliable nDCG@10 improvement over Procrustes.
2. Query-only and document-only application do not explain a positive downstream gain; at the primary point both means are negative.
3. A positive non-additive two-sided interaction is present at `K=256`, and it is larger at `K=512`.
4. The result exists without encoding target-space B coordinates for SciFact test queries or corpus documents.

### Hypotheses not established by this run

A plausible mechanism is that the same local deformation applied to queries and documents preserves or restores a shared retrieval geometry even when applying it to only one side creates coordinate mismatch. The current ablation does **not** establish that this coherence is B-specific. A generic shared nonlinear warp could also produce a positive interaction.

The result therefore does not establish a physical torus, causal semantic locality, or general transport superiority. It also does not turn the `K=512` downstream point into a discovery merely because its point estimate is positive.

## Next discriminant

The next useful test is a **coupling-specificity null** that keeps the Procrustes map, residual-vector marginal distribution, `tau`, `lambda`, K, and two-sided application fixed, but permutes which A anchor receives which residual vector.

Compare:

- `TRUE`: correct residual-to-anchor assignment on both query and document sides;
- `COUPLED-NULL`: the same incorrect residual permutation on both sides;
- `INDEPENDENT-NULL`: different incorrect residual permutations on query and document sides.

If `TRUE > COUPLED-NULL`, the correct local A↔B correspondence carries information beyond merely sharing a warp. If `COUPLED-NULL > INDEPENDENT-NULL`, shared-warp coherence itself contributes even when correspondence is destroyed. The two effects can coexist. This follow-up is motivated by the present held-out result and must therefore be labeled as a prospective mechanism follow-up, not as an independent confirmation of the original hypothesis.
