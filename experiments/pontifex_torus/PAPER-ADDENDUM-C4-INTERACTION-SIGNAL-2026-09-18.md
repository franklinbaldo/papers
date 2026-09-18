---
type: "Interpretability Paper"
title: "Pontifex Torus — Addendum: c4 Cross-Interaction Signal Is Weak, Sample-Limited, and Nearly Negligible"
description: "A nested paired-example learning curve with an explicit cross=off model and a fixed B-side atlas finds that c4 interaction terms are not robustly useful at 140 paired families, are effectively neutral at 280, and become weakly positive at 560. The effect is real enough to reject a simple zero-signal story, but far too small to claim material c4 benefit."
tags: [pontifex, torus, transport, quadratic, interactions, regularization, learning-curve, sample-efficiency, c4, ablation, cartography]
timestamp: 2026-09-18T13:20:00-04:00
---

# Pontifex Torus — Addendum: c4 Cross-Interaction Signal Is Weak, Sample-Limited, and Nearly Negligible

## Question

The blockwise-regularization ablation removed the apparent c4 failure by allowing the interaction block to shrink almost to zero, but it left an important ambiguity:

> is the best c4 transport genuinely linear, or is there a weak cross-interaction signal that current sample size can only estimate unreliably?

The previous experiment could not answer that cleanly because a very large finite penalty is only an approximation to removing the interaction block. This follow-up therefore adds an explicit `cross=off` nested model and measures a paired-example learning curve.

## Protocol

The experiment uses only the synthetic paired c4 cartography field store with 800 whole families. For each of ten outer seeds:

- 240 families are fixed as outer held-out test;
- the remaining 560 families form the outer-training pool;
- nested paired A→B training budgets are 140, 280, and 560 families, using deterministic prefixes of that same outer-training pool;
- the B-side coordinate system is held fixed across budgets: 256 farthest-point anchors are constructed once from the full 560-family **outer-training** B pool and never from outer-test B embeddings;
- A-side features use the same 512-point dense response, eight Fourier harmonics, and standardized pairwise cross terms as the preceding transport ablations;
- linear and cross penalties are selected only on an inner split of the current paired-training budget;
- the linear grid is `3, 10, 30, 100, 300, 1000`;
- the cross grid is `10^3, 3×10^3, 10^4, 3×10^4, …, 10^8`, plus an explicit `cross=off` candidate.

The saved penalty risk curves contain **inner-validation RMSE only**. Outer-test families are not scanned to choose a penalty. For each seed and budget, the outer test is evaluated only after model selection.

Holding the B atlas fixed is deliberate. It isolates the sample efficiency of paired A→B transport from the separate question of how many B examples are required to construct the output atlas. Therefore the estimand here is **paired transport sample efficiency conditional on an already constructed, outer-train-only B atlas**, not end-to-end data efficiency.

## Result

Mean held-out B-anchor affinity RMSE across ten outer splits:

| paired train families | linear RMSE | selected model RMSE | mean gain vs linear | wins vs linear | cross=off selected | finite cross selected | mean cross contribution RMS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 140 | 0.038313 | 0.038335 | **-0.0000228** | 3/10 | 5/10 | 5/10 | 0.000924 |
| 280 | 0.037940 | 0.037940 | **-0.0000004** | 7/10 | 1/10 | 9/10 | 0.001227 |
| 560 | 0.037714 | **0.037692** | **+0.0000225** | 8/10 | 1/10 | 9/10 | 0.001655 |

The learning curve is informative precisely because the effect is tiny.

At 140 paired families, the selector chooses `cross=off` in half the outer splits and the cross-enabled selector is slightly worse on average. There is no evidence at this budget that estimating the interaction block is worthwhile.

At 280 families, finite cross terms are selected in 9/10 splits and beat linear in 7/10, but the mean gain is effectively zero (`-4.4×10^-7` RMSE). This is a transition regime: the interaction contribution is being used, but it does not yet improve average held-out risk.

At 560 families, finite cross terms are again selected in 9/10 splits, win 8/10 outer tests, and improve mean RMSE by `2.25×10^-5`. The mean RMS contribution of the cross block also grows monotonically across the three budgets (`0.000924 → 0.001227 → 0.001655`).

That final gain is only about **0.06% of the linear RMSE**. It is therefore scientifically useful as a sign diagnostic, but not a practically meaningful performance improvement.

## What changed scientifically

The strongest defensible update is narrower than either extreme interpretation from the previous round.

The data no longer support the simple statement **"c4 has no interaction signal"**. If that were literally true under this generator and representation, increasing the number of paired examples should not systematically move model selection from frequent `cross=off` toward finite interaction penalties while also shifting held-out wins and mean risk in the favorable direction. The observed trajectory is instead consistent with a **weak, sample-limited cross-interaction signal**.

But the data also do not support the stronger statement **"cross interactions materially improve c4 transport"**. Even at the largest available paired budget, the mean held-out gain is only `2.25×10^-5` RMSE. The operationally important fact remains that c4 is overwhelmingly explained by the linear component under this protocol.

This also sharpens the earlier blockwise result: its very large c4 cross penalties were not merely hiding a strictly useless block. They were appropriately shrinking a block whose signal-to-variance ratio is extremely poor at n≈560 and worse below that.

## Evidence boundary

**Supported here:** in this synthetic c4 paired cartography regime, with a fixed B atlas built exclusively from outer-training B embeddings, explicit `cross=off` competition, nested paired-training budgets, train-only hyperparameter selection, and ten whole-family outer splits, the interaction block moves from unreliable/slightly harmful at n=140 to approximately neutral at n=280 and weakly positive at n=560. This pattern is consistent with a small sample-limited interaction signal.

**Not established:** that the same learning curve continues at larger n; that the interaction effect is practically important; that clause count is causal; that a Torus topology causes the interaction signal; that the result transfers to natural long-form text; that an atlas learned from only the current paired subset would behave the same way; or that this pairwise synthetic A→B task predicts multi-teacher Assembly/student transfer.

The experiment does not instantiate, tune on, or read the reserved future partitions

\[
D_{assembly}\perp D_{student}\perp D_{val}\perp D_{test}.
\]

Those remain untouched.

## Updated working hypothesis

A better working hypothesis is now:

> c4 contains a real but very low-SNR interaction component. With few paired examples, variance dominates and the correct decision is often to turn the block off; with more paired examples, the same block becomes estimable, but its marginal contribution remains tiny relative to the linear transport.

This is a hypothesis about the current synthetic generator, not a claim about semantic composition in general.

## Next discriminant

The next high-information test is a **larger-n c4 learning curve with the B atlas still held fixed per outer split**, extending paired budgets beyond 560 while keeping the explicit `cross=off` competitor. If the gain grows and cross-off selections disappear, the sample-limited interpretation strengthens. If the curve plateaus near `2×10^-5`, c4 should be treated as effectively linear for practical purposes.

A second, orthogonal control should repeat the curve with an atlas learned only from each current paired subset. That would measure end-to-end data efficiency separately from the conditional transport estimand tested here.

## Reproducibility

- experiment: `experiments/pontifex_torus/c4_interaction_signal_curve.py`
- workflow: `.github/workflows/pontifex-c4-interaction-signal.yml`
- decisive run: `https://github.com/franklinbaldo/papers/actions/runs/35373126840`
- decisive artifact: `https://github.com/franklinbaldo/papers/actions/runs/35373126840/artifacts/10559161871`
