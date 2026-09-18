---
type: "Interpretability Paper"
title: "Pontifex Torus — Addendum: Degree-2 Transport Does Not Survive the Long Multi-Clause Regime"
description: "A short-vs-long full-response transport contrast, followed by a sample-size-matched control, shows that the strong quadratic/cross-term advantage on one-clause synthetic texts reverses on four-clause texts. Matching both corpora at 800 texts preserves the reversal, ruling out sample count as the simple explanation."
tags: [pontifex, torus, transport, quadratic, interactions, regime, sample-size, ablation, cartography]
timestamp: 2026-09-18T10:47:00-04:00
---

# Pontifex Torus — Addendum: Degree-2 Transport Does Not Survive the Long Multi-Clause Regime

## Question

The interaction-topology ablation found a weak Fourier-local advantage only when the complete A response was available on the original one-clause synthetic corpus. The acquisition-budget × topology follow-up then failed to reproduce that local advantage on a longer four-clause corpus, including at full response.

That leaves a more informative discriminant than another graph search:

> Did only the proposed **local interaction topology** fail on longer texts, while generic nonlinear transport still works, or does the broader **degree-2 transport advantage itself reverse** in the longer multi-clause regime?

A first full-response contrast answered that question but had an important confound: the original short field contains 2,000 texts whereas the long field contains 800. A second control therefore fixes **both corpora at 800 texts before the outer split**. This addendum reports both steps and treats the matched-sample result as the decisive one.

## Protocol

The experiment uses only synthetic pairwise-cartography fields and removes sparse acquisition from the comparison by giving every model the complete available A response. The A response is represented with the existing eight-harmonic Fourier basis, producing 17 standardized coefficients.

For each corpus and each outer seed (`0, 1, 2`), the protocol uses a whole-text 70/30 train/test split. All learned quantities are training-only: source normalization, `StandardScaler`, B-side anchors, the diagnostic affinity-to-B decoder, and Ridge alpha selection. Random interaction graphs are chosen independently of labels.

Five transport classes are compared:

1. **linear** — 17 Fourier coefficients;
2. **local-frequency** — linear plus the fixed 36-edge same/adjacent-harmonic graph;
3. **random-harmonic** — linear plus 36 random harmonic-harmonic edges, 12 repetitions per outer seed;
4. **all-cross** — linear plus all 136 distinct `x_i x_j` cross terms;
5. **full-degree-2** — linear plus all 17 squares and all 136 cross terms.

The first run compares all 2,000 one-clause texts with all 800 four-clause texts. Because that changes both input regime and training-sample count, the decisive control chooses a fixed, label-independent 800-text subset of the one-clause corpus (`subset_seed=20260918`) and compares it against all 800 four-clause texts. Both corpora then have 560 training and 240 held-out test texts per outer seed.

The one-clause subset has a mean of `10.21` observed A positions per text; the four-clause field has exactly `32.0` sampled positions per text. Absolute RMSE values therefore should not be compared across corpora. The discriminant is the **within-corpus gain or loss relative to the linear baseline**.

## Result

### Initial contrast: 2,000 short texts vs 800 long texts

The first run already showed a qualitative reversal.

| corpus | model | affinity RMSE ↓ | B top-1 ↑ | neighbor overlap ↑ |
|---|---|---:|---:|---:|
| one-clause, n=2000 | linear | 0.05793 | 0.1661 | 0.1788 |
| one-clause, n=2000 | local-frequency | 0.05235 | 0.2844 | 0.1984 |
| one-clause, n=2000 | all-cross | **0.04708** | 0.4578 | **0.2054** |
| one-clause, n=2000 | full-degree-2 | 0.04695 | **0.4628** | 0.1960 |
| four-clause, n=800 | **linear** | **0.02869** | 0.1014 | 0.1604 |
| four-clause, n=800 | local-frequency | 0.02897 | 0.1125 | 0.1639 |
| four-clause, n=800 | all-cross | 0.02936 | 0.1181 | 0.1623 |
| four-clause, n=800 | full-degree-2 | 0.02969 | 0.1194 | 0.1628 |

On the short corpus, all-cross reduces affinity RMSE by `0.01085` relative to linear; on the long corpus it **increases** RMSE by `0.00067`. Full degree-2 behaves similarly. This was suggestive but not sufficient because the short model had substantially more training texts.

### Decisive control: both corpora fixed at n=800

Matching the sample count does **not** remove the reversal.

| corpus, n=800 | model | affinity RMSE ↓ | B top-1 ↑ | neighbor overlap ↑ |
|---|---|---:|---:|---:|
| one-clause | linear | 0.05798 | 0.2486 | 0.2166 |
| one-clause | local-frequency | 0.05410 | 0.3417 | 0.2366 |
| one-clause | random-harmonic mean | 0.05399 | 0.3441 | 0.2344 |
| one-clause | **all-cross** | 0.05039 | **0.4708** | **0.2439** |
| one-clause | full-degree-2 | **0.05032** | **0.4708** | 0.2427 |
| four-clause | **linear** | **0.03761** | 0.0333 | 0.02184 |
| four-clause | local-frequency | 0.03915 | 0.0236 | 0.02130 |
| four-clause | random-harmonic mean | 0.03876 | **0.0353** | **0.02453** |
| four-clause | all-cross | 0.04339 | 0.0319 | 0.02323 |
| four-clause | full-degree-2 | 0.04425 | 0.0250 | 0.02330 |

For the matched one-clause corpus, all-cross improves affinity RMSE over linear by `0.00759` (**13.1%**) and full degree-2 by `0.00767` (**13.2%**). The improvement is positive in every outer seed. Top-1 rises from `0.2486` to `0.4708`, and all-cross neighbor overlap rises from `0.2166` to `0.2439`.

For the matched four-clause corpus, the direction reverses in every outer seed. All-cross worsens affinity RMSE by `0.00578` (**15.4%**) and full degree-2 by `0.00664` (**17.7%**) relative to linear. Local-frequency also worsens RMSE by `0.00155` (**4.1%**). The local graph beats **0/36** capacity-matched random harmonic graphs on affinity RMSE across the three seeds, and only `3/36` on downstream neighbor overlap.

The sample-size control also weakens the earlier claim of a privileged full-response Fourier-local topology on the short field. At n=800 the local graph is slightly **worse** than the random-graph mean on affinity RMSE (`0.05410` vs `0.05399`), although it retains a small neighbor-overlap advantage (`0.2366` vs `0.2344`). The stronger and more reproducible fact is therefore not local topology but the **short-corpus benefit of distributed cross interactions**.

## Interpretation

The discriminant rejects the simple explanation that the long-corpus reversal was caused only by having fewer training texts.

> With equal sample count and the sparse-acquisition stage removed, degree-2 transport remains strongly useful on one-clause texts and becomes actively harmful on four-clause texts.

This is negative evidence against promoting the current quadratic transport class — and especially the fixed Fourier-local graph — to a general Pontifex architectural prior. The earlier short-corpus success is **regime-dependent**.

What changes between the matched corpora is not just token count. The four-clause generator introduces longer inputs, more compositional structure, more independently sampled clause content, and a denser A-response sampling grid. This experiment does not identify which of those changes causes the reversal. It therefore supports a **regime interaction**, not a specific causal story about length or composition.

One plausible hypothesis is that low-order cross terms approximate the short one-clause A→B map well but become a misspecified, high-variance expansion once the perturbation field contains several compositional substructures. Another is that the richer long response is already sufficiently informative for the linear map and that the extra degree-2 basis mainly fits training-specific covariance. These are hypotheses for the next experiment, not conclusions from this one.

## Evidence boundary

**Supported here:** on these two synthetic fields, with identical sample count, identical outer split sizes, full A response, train-only preprocessing/selection, and the same transport/decoder protocol, distributed degree-2 interactions improve held-out affinity prediction strongly on the one-clause corpus and worsen it strongly on the four-clause corpus. The current 36-edge Fourier-local graph is not robustly privileged over capacity-matched random harmonic graphs.

**Not established:** that text length itself causes the reversal; that clause count itself causes it; that degree-2 transport fails on natural text; that a different regularizer or interaction basis would fail; that the Torus is or is not the correct semantic topology; or that any result here predicts multi-teacher Assembly/student transfer.

The diagnostic never instantiates, tunes on, or reads the reserved future benchmark partitions

\[
D_{assembly}\perp D_{student}\perp D_{val}\perp D_{test}.
\]

Those partitions remain untouched. This is evidence about synthetic pairwise cartography only.

## Next discriminant

The highest-information follow-up is a **matched-n clause-complexity ladder**: generate `1, 2, 3, 4` clause corpora with the same number of texts, the same fixed position budget, and otherwise identical generators, then compare linear, all-cross, and full-degree-2 transport with the same outer splits. A monotonic decay of the quadratic advantage with clause count would support a compositional-complexity interaction. A sharp or non-monotonic transition would point elsewhere.

A complementary control should match token length while varying compositional structure, so that "longer" and "more multi-clause" stop moving together. Until that is done, the paper should use **regime-dependent** rather than **length-dependent** language.

## Reproducibility

Initial short-vs-long contrast:

- implementation: `experiments/pontifex_torus/transport_regime_contrast.py`
- workflow: `.github/workflows/pontifex-transport-regime-contrast.yml`
- run: `https://github.com/franklinbaldo/papers/actions/runs/35357685367`
- artifact: `https://github.com/franklinbaldo/papers/actions/runs/35357685367/artifacts/10553635083`

Sample-size-matched control:

- implementation: `experiments/pontifex_torus/transport_regime_n_control.py`
- workflow: `.github/workflows/pontifex-transport-regime-n-control.yml`
- run: `https://github.com/franklinbaldo/papers/actions/runs/35358086828`
- artifact: `https://github.com/franklinbaldo/papers/actions/runs/35358086828/artifacts/10553051923`

The PR remains experimental; this addendum does not authorize merging it.