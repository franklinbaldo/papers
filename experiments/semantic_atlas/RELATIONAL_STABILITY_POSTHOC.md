---
type: "Findings Record"
title: "Semantic Atlas v1 — relational stability and density post-hoc check"
description: "Post-hoc whole-curve survival and local-density confound analysis of the frozen relational-dynamics pilot. The dominant cross-observer churn difference is order-invariant; first-churn survival differs sharply and is not explained by a simple baseline-density split."
tags: [semantic-atlas, findings, embeddings, churn, survival, density, posthoc]
timestamp: 2026-08-26T15:25:00-04:00
---

# Semantic Atlas v1 — relational stability and density post-hoc check

## Status and claim boundary

This is a **post-hoc** analysis performed after the v1 outcome and the power correction in PR #385 were known. It does not alter the frozen protocol in PR #380 and cannot convert any v1 result into preregistered confirmation.

The executable analysis is `scripts/run_relational_stability_posthoc.py`; the machine-readable output is `artifacts/relational_stability_density_posthoc.json`.

## The dynamical signal is mostly order-invariant

At `k=5`, cross-observer churn divergence in repository chronology is `D = 0.357006`. Across 10,000 arbitrary shared insertion orders, the mean is already `0.333845`; chronology adds only `0.023162`, or `6.94%` above that baseline, and PR #385 showed that excess is not significant and was severely underpowered.

The same-observer Poisson-anchor reference under arbitrary orders is much lower: approximately `0.23165` for Qwen and `0.22925` for MiniLM.

The supported interpretation is therefore narrower and more useful than “chronology-specific dynamics”:

> A material cross-observer difference in relational response is present under arbitrary shared arrival orders. The next mechanism should be formulated as **order-invariant local susceptibility**: which static properties of observer `m` around document `i` predict expected neighborhood churn per unit corpus mass, averaged over arrival orders?

This is a motivation for the next large-corpus exploration, not a confirmed mechanism.

## First-churn survival: whole-curve test

The earlier Kaplan–Meier correction gave median added documents to first `k=5` neighborhood churn of `24` for Qwen versus `4` for MiniLM, with 10/24 Qwen anchors censored and no MiniLM censoring. Because those medians are exposed to asymmetric censoring, the relevant comparison is the whole survival curve.

Using the full 92-added-document horizon, restricted mean survival time (RMST) is:

| observer | events | censored | KM median | RMST to 92 |
|---|---:|---:|---:|---:|
| Qwen | 14 | 10 | 24 | 48.8333 |
| MiniLM | 24 | 0 | 4 | 5.8333 |

A paired within-document permutation test swaps observer labels for each of the same 24 anchors and recomputes the RMST difference. With 100,000 permutations:

- observed RMST difference: **43.0 added documents**;
- null 95% interval: approximately `[-23.0, 22.67]`;
- two-sided plus-one `p = 0.000020`;
- one-sided plus-one `p = 0.000010`.

So the survival separation is not an artifact of comparing censored medians alone. It remains a pilot result because only 24 initial anchors are at risk.

## Local-density confound check

All neighborhoods here use L2-normalized vectors and cosine similarity, so vector-norm scale does not enter the kNN calculation. Dimensionality is still inseparable from observer identity with only two models.

As a baseline density proxy, use the cosine similarity to the fifth nearest neighbor **within the 24 documents present before the replay begins**. Higher similarity means a denser local neighborhood.

The baseline distributions are not dramatically separated:

- Qwen mean `0.62599`, median `0.64922`;
- MiniLM mean `0.61548`, median `0.66503`.

Using pooled terciles with cuts `0.62012` and `0.68221`, the first-churn separation persists in every density stratum:

| density stratum | Qwen n / events / censored | Qwen median | Qwen RMST | MiniLM n / events / censored | MiniLM median | MiniLM RMST |
|---|---|---:|---:|---|---:|---:|
| low | 8 / 6 / 2 | 12 | 44.0 | 8 / 8 / 0 | 4 | 6.5 |
| middle | 8 / 3 / 5 | not reached | 61.5 | 8 / 8 / 0 | 4 | 4.0 |
| high | 8 / 5 / 3 | 12 | 41.0 | 8 / 8 / 0 | 4 | 7.0 |

This does **not** prove density independence. It does rule out the simplest reading that the Qwen/MiniLM survival difference is merely “one space is locally sparser” under this baseline cosine-density proxy.

## Gap remains descriptive only

For the same 24-document baseline, the mean cosine gap between the fifth and sixth neighbors is `0.02107` in Qwen and `0.01408` in MiniLM. That direction is compatible with greater local stability in Qwen, but v1 already showed an unstable gap→churn relationship whose sign changed across observers.

Therefore this record makes **no** post-hoc gap mechanism claim. Gap becomes a candidate predictor only in a larger exploratory corpus, where the response is defined order-invariantly and basal churn/ceiling behavior is pre-specified.

## Large-corpus measurement contract

The first large-corpus figure must not be raw mKNN alone. For gallery size `N` on a log x-axis and several fixed `k` values, report at least two aligned panels:

1. raw `mKNN(N,k)`;
2. permutation-calibrated `mKNN(N,k)`.

The calibrated panel is the decision-bearing one because the chance overlap itself scales roughly with `k/N`. A raw fall with `N` can coexist with flat, rising, or falling above-chance local alignment.

A third comparison is required: a **same-observer stability ceiling by N**. Because both encoders are deterministic, exact same-model/same-gallery mKNN is identically 1 and is not a useful “seed-null.” The large-corpus protocol must therefore freeze the actual perturbation/bootstrap operator before execution and label it as a stability ceiling, not seed variability.

The static paper is viable only if calibrated cross-model local alignment is sufficiently scale-stable to interpret and remains materially below that pre-specified same-observer ceiling over the relevant `N × k` regime. If calibrated mKNN collapses with `N`, the `N=116` result is a small-gallery artifact and the static paper stops there.

## Consequence for the mechanism programme

Do not optimize `arrival × gap` on the 116-document repository corpus. The order-specific component is not where the v1 signal lives.

On a large naturally timestamped corpus, the exploratory target becomes:

`expected churn per unit added corpus mass | static local geometry of observer m around i`,

with expectation taken over arrival orders or an equivalent order-averaged construction. Density, boundary gap, hubness, and basal churn/ceiling behavior are candidate predictors; none is promoted before the large-corpus exploration.

Only after that exploration should a functional form be frozen and confirmed on held-out time or a second corpus.

## Provenance

- frozen pilot: PR #380;
- power/mKNN robustness correction: PR #385;
- parent reanalysis artifact: `artifacts/relational_dynamics_v1_reanalysis.json`;
- this analysis: `scripts/run_relational_stability_posthoc.py`;
- this artifact: `artifacts/relational_stability_density_posthoc.json`;
- reference observer: `Qwen/Qwen3-Embedding-0.6B@97b0c61`;
- transfer observer: `sentence-transformers/all-MiniLM-L6-v2@1110a24`.
