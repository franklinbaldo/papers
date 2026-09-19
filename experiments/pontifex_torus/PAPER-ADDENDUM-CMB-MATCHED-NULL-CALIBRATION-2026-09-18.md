---
type: "Interpretability Paper"
title: "Pontifex Torus — Addendum: Small Matched-Null Ensembles Require Predictive Student-t Calibration"
description: "A calibration audit of the current synthetic CMB occlusion smoke shows that the matched-null statistic is badly anti-conservative if read as a standard-normal z-score, but is close to nominal after the finite-null predictive Student-t correction. With four null maps and 600 theta samples, naive Gaussian interpretation marks 19.83% of rows at p<0.05, while predictive-t calibration marks 4.33%."
tags: [pontifex, torus, cmb, occlusion, null-model, calibration, student-t, falsification, statistics, monte-carlo]
timestamp: 2026-09-18T16:23:00-04:00
---

# Pontifex Torus — Addendum: Small Matched-Null Ensembles Require Predictive Student-t Calibration

## Question

The current CMB occlusion stress harness improved an important design flaw by comparing every observed intervention parameter vector `theta` against the **same theta** on a small ensemble of null maps. It then reported

\[
z_{like}(\theta)=\frac{s_{obs}(\theta)-\bar s_{null}(\theta)}{\operatorname{sd}(s_{null}(\theta))}.
\]

The latest PR smoke used only four null maps per theta. With such a small null ensemble, the denominator is itself estimated noisily. The quantity above is therefore not distributed as a standard-normal z-score under the null.

That creates a sharp discriminant:

> Are the apparently extreme matched-null values evidence that the synthetic harness is badly miscalibrated, or are they the expected heavy tails of a small-sample predictive statistic that has merely been given the wrong name?

## Protocol

The audit consumes the exact CSV artifact from CMB run `35387349770`:

- synthetic field;
- 600 intervention parameter samples;
- four matched null maps per theta;
- identical `theta` applied to observed and null fields;
- five intervention families (`hard`, `apodized`, `local_mean`, `residual_permute`, `adjacency_phase`);
- no access to any future Assembly/student/validation/test partition.

For each row, the existing `z_matched_null` field is retained as `z_like`. Under an exchangeable Gaussian predictive null with `m` null maps,

\[
t_{pred}=\frac{z_{like}}{\sqrt{1+1/m}}
\]

follows Student-t with `m-1` degrees of freedom. For the PR smoke, `m=4`, so the calibrated reference is `t_3`, not `N(0,1)`.

The audit compares two interpretations of the *same rows*:

1. **naive Gaussian** — treat `z_like` as if it were a standard-normal z-score;
2. **predictive Student-t** — apply the finite-null correction above and evaluate against `t_{m-1}`.

The script also reports a KS uniformity diagnostic over the resulting predictive-t p-values. Because the 600 theta rows reuse one sky and spatial interventions overlap, this KS result and the rejection fractions are **diagnostics, not independent population-level significance tests**.

## Result

The upstream matched-null values looked alarming in raw z-like units:

| quantity | value |
|---|---:|
| mean `z_like` | +0.06595 |
| std `z_like` | 1.77662 |
| 95th percentile `|z_like|` | 3.31718 |
| max `|z_like|` | 10.68281 |

If these values are incorrectly interpreted as standard-normal z-scores:

- **19.83%** of the 600 rows have two-sided `p < 0.05`;
- **10.50%** have `p < 0.01`.

That would look like severe false-positive inflation.

After the predictive Student-t correction (`m=4`, `df=3`):

| calibration diagnostic | result |
|---|---:|
| two-sided `p < 0.05` | **4.33%** |
| two-sided `p < 0.01` | **0.833%** |
| two-sided `p < 0.001` | **0%** |
| median predictive-t p | 0.4662 |
| 5th percentile predictive-t p | 0.0592 |
| KS distance from Uniform(0,1) | 0.0477 |
| KS p-value, diagnostic only | 0.1257 |

The naive normal interpretation therefore creates about **4.58× more `p<0.05` rows** than the predictive-t interpretation on exactly the same smoke artifact.

The family-level `p<0.05` rates after predictive-t calibration are:

- `adjacency_phase`: 6.25%;
- `apodized`: 5.45%;
- `hard`: 5.04%;
- `local_mean`: 3.45%;
- `residual_permute`: 0.93%.

The residual-permutation family is notably conservative in this smoke, while the other families cluster around or modestly around the nominal 5% scale. Because rows are correlated, these family differences are descriptive follow-up targets rather than evidence of different population false-positive rates.

## Scientific update

The calibration audit changes the interpretation of the latest CMB smoke in a useful way.

The extreme values up to `|z_like| ~= 10.7` **do not, by themselves, show that matched-theta calibration is broken**. Most of the apparent inflation is explained by using a four-member null ensemble while reading the resulting studentized statistic as though its denominator were known exactly.

The strongest defensible statement from this synthetic audit is:

> the matched-theta mechanism is broadly compatible with nominal predictive-null calibration when the small-null statistic is treated as Student-t rather than as a Gaussian z-score.

This is positive evidence about the **calibration mechanics**, not about any CMB anomaly.

It also creates a concrete production rule: **do not rank or threshold small-ensemble `z_matched_null` values using standard-normal tails**. Either use the predictive Student-t reference with the explicit finite-null correction, or use a substantially larger empirical null ensemble and empirical tail probabilities.

## Evidence boundary

**Supported here:** on the exact 600-row synthetic smoke artifact with four matched null maps per theta, predictive Student-t calibration reduces the apparent two-sided 5% exceedance rate from 19.83% under the invalid Gaussian-z reading to 4.33%; the resulting p-value distribution does not show a large calibration failure in the simple uniformity smoke.

**Not established:** exact frequentist coverage for dependent theta rows; exchangeability on a real masked CMB sky; validity of the current lightweight HEALPix null placeholder; any cosmological detection; any special Torus causal mechanism; transfer to ACT/Planck data; or downstream value for Assembly/student learning.

The synthetic observed field and phase-scrambled null fields are generated from the same smooth-field construction, which makes this an appropriate **mechanics stress test**. Real-map inference remains blocked on stronger null generation (`C_l`-matched `synfast` or equivalent `a_lm` randomization), masking/systematics controls, independent-map replication, and a predeclared tail-calibration rule.

The experiment does not instantiate, tune on, or read the reserved future partitions

\[
D_{assembly}\perp D_{student}\perp D_{val}\perp D_{test}.
\]

They remain untouched.

## Next discriminant

The next useful calibration experiment is a **null-count ladder** with the same synthetic sky and same theta stream at `m = 4, 8, 16, 32`.

Two predictions now differ cleanly:

- if the Student-t interpretation is correct, predictive-t p-value calibration should remain roughly stable while the raw `z_like` tails approach Gaussian behavior as `m` grows;
- if a structural mismatch remains between observed and null fields, rejection inflation or family-specific distortions should persist even after increasing `m`.

A second control should repeat the ladder across independent synthetic skies so that dependence on one realization is not mistaken for calibration quality.

## Reproducibility

- source smoke experiment: `experiments/pontifex_torus/cmb_occlusion_mc.py`
- new calibration audit: `experiments/pontifex_torus/cmb_matched_null_calibration.py`
- workflow: `.github/workflows/pontifex-cmb-occlusion-mc.yml`
- source run: `https://github.com/franklinbaldo/papers/actions/runs/35387349770`
- source artifact: `https://github.com/franklinbaldo/papers/actions/runs/35387349770/artifacts/10564806641`
- audit implementation commit: `138d6cf0e5cdf40fb886a8b68249fffc05f0692f`
- workflow integration commit: `801d72009be30cefdb78eb98782af5ed8eb376f6`
