---
type: "Interpretability Paper"
title: "Pontifex Torus — Addendum: c4 Interaction Gain Survives a Disjoint B Atlas"
description: "A strict-separation control rebuilds the B-side anchor atlas from an auxiliary pool disjoint from both transport training and outer test. The tiny c4 cross-interaction gain remains positive in 8/10 outer splits and is not reduced relative to a matched shared-atlas control, weakening the concern that atlas/train overlap creates the signal."
tags: [pontifex, torus, transport, quadratic, interactions, atlas, leakage-control, separation, c4, ablation, cartography]
timestamp: 2026-09-18T15:16:00-04:00
---

# Pontifex Torus — Addendum: c4 Interaction Gain Survives a Disjoint B Atlas

## Question

The c4 interaction experiments so far built the B-side anchor dictionary only from outer-training B embeddings, so there was no outer-test leakage. But one weaker form of coupling remained: some of the same paired families could both define the output coordinate system and train the A→B transport.

That leaves a concrete alternative explanation for the tiny interaction gain:

> perhaps cross terms look useful only because the B coordinate system is adapted to the same families used to fit the transport.

This ablation tests that possibility directly.

## Protocol

The experiment uses the same synthetic c4 field store with 800 whole families. For each of ten outer seeds, families are partitioned into three mutually disjoint pools:

- 120 outer-test families;
- 120 auxiliary **B-only atlas** families;
- 560 paired A→B transport-training families.

The A-side representation is identical between conditions and is fitted only from the 560 transport-training families: 512-point dense response, eight Fourier harmonics, standardized linear features, and standardized pairwise cross terms.

Two B coordinate systems are then compared while holding transport train/test, atlas candidate count, anchor count, penalty grids, and inner-selection seed fixed:

1. **shared atlas** — 120 atlas candidates are taken from the transport-training B embeddings;
2. **disjoint atlas** — 120 atlas candidates come from the auxiliary B-only pool and are disjoint from both transport train and outer test.

Each condition selects 64 farthest-point anchors from its 120 candidates. Linear and cross penalties are selected only on an inner split of the 560 transport-training families, with an explicit `cross=off` candidate. Outer test is scored only after that selection.

Because the two atlas conditions define different B coordinates, their absolute RMSE values are not treated as directly comparable. The primary quantity is the **within-condition held-out gain over that condition's own linear baseline**, followed by the paired difference of those gains across outer seeds.

The disjoint condition also consumes 120 additional B-only observations. It is therefore a strict-separation robustness control, not a total-data-efficiency comparison.

## Result

| quantity | shared atlas | disjoint atlas |
|---|---:|---:|
| mean linear test RMSE | 0.03763108 | 0.03736919 |
| mean selected test RMSE | 0.03761071 | 0.03734121 |
| mean interaction gain vs linear | **+0.00002038** | **+0.00002798** |
| median interaction gain vs linear | +0.00002549 | +0.00003795 |
| positive gain | 8/10 splits | 8/10 splits |
| `cross=off` selected | 1/10 | 0/10 |

The paired `disjoint - shared` interaction-gain difference is:

- mean: `+7.60×10^-6` RMSE;
- median: `+1.11×10^-5` RMSE;
- disjoint larger in 6/10 outer splits;
- shared larger in 4/10.

The important result is not that the disjoint atlas is "better". Its coordinate system is different and it uses additional B-only observations, so that stronger claim is not identified by this design.

The useful result is narrower: **removing all atlas/transport-family overlap does not erase the interaction gain**. The sign and rough scale of the weak c4 interaction effect survive a stricter separation boundary.

## Scientific update

The atlas-overlap concern is weakened.

Earlier evidence supported a very small c4 cross-mode signal under an outer-train-only atlas. This control shows that the signal is not contingent on reusing transport-training families to construct the B anchor dictionary. Under a disjoint auxiliary atlas, the selected interaction model still improves over its own linear baseline in 8/10 outer splits and does not show a lower mean gain.

The strongest defensible statement is therefore:

> within this synthetic c4 regime, the weak interaction signal survives when atlas construction, paired transport fitting, and outer testing use mutually disjoint family pools.

That is a robustness result for the **existence of a tiny aligned interaction component**, not evidence that the component is practically important.

## Evidence boundary

**Supported here:** with 560 paired transport families, a 120-family auxiliary B-only atlas pool, a 120-family untouched outer test, 64 B anchors, the current Fourier A representation, and inner-only penalty selection, cross interactions retain a small positive held-out gain when atlas construction is fully disjoint from transport fitting.

**Not established:** that a disjoint atlas is superior to a shared atlas; total-data efficiency; population significance; monotonic scaling beyond 560 paired examples; practical relevance of a gain on the order of `10^-5`; Torus causality; transfer to natural long-form text; robustness to other encoders/generators; or usefulness for multi-teacher Assembly/student transfer.

This control also changes the atlas from the earlier 256-anchor experiments to 64 anchors so that both atlas conditions can use equal-size 120-family candidate pools. The numerical gain should therefore not be treated as an exact replication of the preceding 256-anchor effect size.

The experiment does not instantiate, tune on, or read the reserved future partitions

\[
D_{assembly}\perp D_{student}\perp D_{val}\perp D_{test}.
\]

They remain untouched.

## Updated working hypothesis

The current evidence is now consistent with a c4 interaction component that is:

1. extremely small relative to the linear transport error;
2. increasingly detectable as paired sample size grows;
3. better than a sample-exchangeability null under the previous 256-anchor protocol;
4. still detectable when the B atlas is constructed from a family pool disjoint from transport training and outer test.

The remaining uncertainty is less about simple train/atlas overlap and more about **stability across atlas realizations and larger paired n**.

## Next discriminant

The clean next experiment is a two-axis replication:

- multiple independently sampled disjoint atlases for the same fixed transport train/test split;
- paired-training budgets above 560 on a larger c4 field store while atlas size and anchor dictionary are held fixed.

If the gain remains positive across atlas realizations and grows with paired n, the sample-limited weak-signal interpretation becomes substantially stronger. If it varies mostly with atlas realization or plateaus near `2–3×10^-5`, c4 should be treated as operationally linear despite a detectable residual interaction.

## Reproducibility

- experiment: `experiments/pontifex_torus/c4_atlas_independence_ablation.py`
- workflow: `.github/workflows/pontifex-c4-atlas-independence.yml`
- decisive run: `https://github.com/franklinbaldo/papers/actions/runs/35384678296`
- artifact: `https://github.com/franklinbaldo/papers/actions/runs/35384678296/artifacts/10562359747`
