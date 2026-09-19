---
type: "Interpretability Paper"
title: "Pontifex Torus — Addendum: Most of the Clause-Complexity Sign Flip Was Regularization-Sensitive"
description: "A train-vs-held-out diagnostic and wider Ridge sweep show that the apparent c2-c4 failure of degree-2 A→B transport was largely a variance/regularization effect under the earlier alpha grid. c2 becomes positive, c3 becomes approximately neutral, and c4 remains only weakly negative."
tags: [pontifex, torus, transport, quadratic, generalization, regularization, overfitting, clause-complexity, ablation, cartography]
timestamp: 2026-09-18T11:49:00-04:00
---

# Pontifex Torus — Addendum: Most of the Clause-Complexity Sign Flip Was Regularization-Sensitive

## Why this follow-up was necessary

The paired clause-complexity ladder previously showed a sharp held-out sign change for degree-2 A→B affinity transport: all-cross terms helped at one clause, hurt at two through four independent clauses, and became weakly positive again for the long repeated-content control. That result ruled out input length alone, but it did not distinguish **structural misspecification** from a simpler explanation: the richer degree-2 basis may have been overfitting under an insufficient regularization search.

This addendum tests that distinction directly.

## Protocol

A new diagnostic reuses the exact paired field stores from the clause ladder: 800 families per regime, eight deterministic size-1 probes per text, the same family-level 70/30 outer splits for seeds 0/1/2, the same eight-harmonic Fourier source representation, and the same train-only B-anchor construction.

For each outer split it fits:

1. `linear` — 17 source features;
2. `all_cross` — the 17 linear features plus all 136 pairwise cross terms;
3. `full_degree2` — linear + 17 squares + all 136 cross terms.

The script records both final outer-training affinity RMSE and untouched outer-test affinity RMSE. Alpha is selected only inside the outer training families.

The first run retained the earlier grid `0.1, 1, 10`. Because the richer models selected the upper boundary (`10`) essentially everywhere, a second discriminant widened the grid to:

`0.1, 1, 10, 30, 100, 300, 1000`.

This second run is the main result below.

## Result 1 — the narrow-grid reversal had a classic variance signature

Under the original `0.1, 1, 10` grid, all-cross transport improved final training RMSE in every c2-c4 seed while worsening held-out RMSE in every c2-c4 seed. The same pattern held for full degree-2. That is the exact diagnostic signature expected from overfitting under this protocol, not evidence that the richer basis had lost the ability to fit the transport relation.

Mean all-cross train/test gains versus linear were:

| regime | train RMSE gain | held-out RMSE gain | overfit-signature seeds |
|---|---:|---:|---:|
| `c1` | +0.012308 | +0.006357 | 0/3 |
| `c2` | +0.008684 | −0.002830 | **3/3** |
| `c3` | +0.004944 | −0.002487 | **3/3** |
| `c4` | +0.002784 | −0.001640 | **3/3** |
| `repeat4` | +0.004429 | +0.000708 | 0/3 |

So the previous c2-c4 sign flip was compatible with a capacity/variance explanation from the start.

## Result 2 — widening regularization removes most of the reversal

With the wider train-only alpha search, the held-out all-cross gain changes materially:

| regime | old grid gain | wide grid gain | interpretation |
|---|---:|---:|---|
| `c1` | +0.006357 | **+0.006434** | stable positive |
| `c2` | −0.002830 | **+0.000707** | sign reversal disappears |
| `c3` | −0.002487 | **−0.000069** | ~97.2% of the prior harm disappears |
| `c4` | −0.001640 | **−0.000314** | ~80.8% of the prior harm disappears |
| `repeat4` | +0.000708 | **+0.000674** | stable weak positive |

Full degree-2 shows the same qualitative picture: held-out gain is `+0.006516` at c1, `+0.000448` at c2, `−0.000144` at c3, `−0.000345` at c4, and `+0.000639` at repeat4.

The richer models still improve outer-training RMSE at every rung. Under the wide grid, all-cross mean train gains remain `+0.011860`, `+0.004268`, `+0.001619`, `+0.000548`, and `+0.004088` for c1/c2/c3/c4/repeat4 respectively. The residual c3/c4 held-out deficits are therefore small generalization gaps, not failures to fit the training relation.

Regularization selection itself is informative. All-cross selects alpha `300` for all three c2 seeds, and reaches the new upper boundary `1000` in two of three c3 seeds and all three c4 seeds. Full degree-2 behaves similarly. Thus even the widened sweep has not demonstrated that c3/c4 possess an irreducible negative degree-2 effect; the optimum may still lie at stronger shrinkage or require blockwise penalties.

## Updated interpretation

The earlier wording that degree-2 transport "hurts reliably for two through four independent clauses" is too strong as a model-class claim. What was reliable under the earlier protocol was a **held-out reversal under a narrow regularization grid**. Once the regularization search is widened, c2 becomes weakly positive, c3 becomes essentially neutral, and c4 remains only weakly negative.

The strongest current statement is therefore:

> distributed degree-2 interactions remain strongly useful at c1, are regularization-sensitive as compositional complexity increases, and under the present Ridge parameterization provide at most a small held-out advantage or disadvantage from c2 onward.

This weakens a structural "composition breaks quadratic transport" story and strengthens a variance/conditioning account. The repeated-content control remains interesting, but it is no longer evidence for a clean semantic-composition phase transition.

## Evidence boundary

**Supported here:** on this synthetic paired generator, with fixed eight-probe acquisition and family-level train/test isolation, richer degree-2 transport has substantially lower training RMSE than linear transport at every rung; the earlier c2-c4 held-out reversal exhibits an overfitting signature; and a wider train-only Ridge search removes the c2 reversal and nearly eliminates the c3/c4 deficits.

**Not established:** that stronger regularization will fully rescue c3/c4; that clause count or semantic independence is the causal variable; that the Torus is the correct semantic topology; that degree-2 transport generalizes to natural long-form text; or that any of these pairwise-cartography effects predict multi-teacher Assembly/student transfer.

The experiment does not instantiate, tune on, or read the reserved future partitions

\[
D_{assembly}\perp D_{student}\perp D_{val}\perp D_{test}.
\]

Those remain untouched.

## Next discriminant

The highest-information next step is no longer another clause-count ladder. It is a **regularization-structure test** on c3/c4:

- extend scalar Ridge beyond `1000` to verify whether the optimum is still boundary-limited;
- compare one shared penalty against separate penalties for linear and interaction blocks;
- standardize the expanded interaction block independently so alpha does not absorb feature-scale mismatch;
- report nested-validation and held-out curves rather than only the selected point.

If c3/c4 become neutral or positive under well-conditioned/blockwise shrinkage, the apparent regime transition was mostly estimator variance. If a robust negative remains after that control, a structural transport mismatch becomes plausible again.

## Reproducibility

- diagnostic: `experiments/pontifex_torus/clause_complexity_generalization_gap.py`
- workflow: `.github/workflows/pontifex-clause-generalization-gap.yml`
- narrow-grid run: `https://github.com/franklinbaldo/papers/actions/runs/35364179030`
- narrow-grid artifact: `https://github.com/franklinbaldo/papers/actions/runs/35364179030/artifacts/10555760862`
- wide-grid run: `https://github.com/franklinbaldo/papers/actions/runs/35364392562`
- wide-grid artifact: `https://github.com/franklinbaldo/papers/actions/runs/35364392562/artifacts/10554449111`
