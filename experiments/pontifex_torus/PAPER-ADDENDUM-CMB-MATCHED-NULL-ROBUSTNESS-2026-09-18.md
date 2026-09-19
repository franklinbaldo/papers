---
type: "Interpretability Paper"
title: "Pontifex Torus — Addendum: Predictive-t Calibration Is Conditional, Exact Rank Needs More Nulls"
description: "A null-count and score-shape robustness ladder shows that the finite-null predictive Student-t correction is calibrated under Gaussian exchangeable scores but is not distribution-free. Exact leave-one-out rank calibration remains valid under skew and heavy tails, at the cost of coarse resolution: at least 19 matched nulls are needed to attain p<=0.05 and 99 for p<=0.01."
tags: [pontifex, torus, cmb, occlusion, null-model, calibration, student-t, permutation, rank-test, falsification, statistics, monte-carlo]
timestamp: 2026-09-18T17:24:00-04:00
---

# Pontifex Torus — Addendum: Predictive-t Calibration Is Conditional, Exact Rank Needs More Nulls

## Question

The previous calibration audit corrected a real statistical error: with only `m=4` matched null maps, the quantity

\[
z_{like}=\frac{s_{obs}-\bar s_{null}}{\operatorname{sd}(s_{null})}
\]

must not be read against `N(0,1)`. Under an exchangeable Gaussian score null,

\[
t_{pred}=\frac{z_{like}}{\sqrt{1+1/m}}
\]

has a Student-t reference with `m-1` degrees of freedom. On the 600-row synthetic smoke this changed the apparent two-sided `p<0.05` rate from 19.83% to 4.33%.

That result left an important assumption implicit: **predictive Student-t is exact because of Gaussian score structure, not merely because the candidate and matched null maps are exchangeable**.

The discriminating question in this addendum is therefore:

> Does the predictive-t repair remain calibrated when the matched-null score law is skewed or heavy-tailed, and what finite-null statement is available without assuming a parametric score shape?

## Protocol

`cmb_matched_null_robustness_ladder.py` simulates `m+1` exchangeable scores per trial. Item zero is treated as the candidate and the remaining `m` values as its matched null ensemble. The ladder uses

`m = 4, 8, 16, 32, 64, 128`

and four standardized score laws:

1. Gaussian;
2. Student-t with 5 degrees of freedom;
3. centered/scaled lognormal;
4. 95/5 contaminated Gaussian, with the contaminating component inflated by 5x.

Each cell uses 100,000 independent Monte Carlo trials in the full local run. Three calibrations are computed from the same trial:

1. **naive normal** — the known-bad `N(0,1)` interpretation of `z_like`;
2. **predictive Student-t** — `t_pred` compared with `t_{m-1}`;
3. **exact leave-one-out rank** — every one of the `m+1` exchangeable values is, in turn, treated as the held-out candidate; its predictive studentized residual is computed against the other `m`, and the actual candidate is ranked among these `m+1` symmetrically computed absolute residuals.

The third method is a finite-sample randomization test under exchangeability. It does **not** require Gaussian scores, but its p-value resolution is exactly `1/(m+1)`.

This experiment is about calibration mechanics only. It does not touch any Assembly/student/validation/test split.

## Results

### 1. The Student-t correction is genuinely correct in its intended model

Across the Gaussian cells, the predictive-t two-sided 5% false-positive rate stayed within **0.00148 absolute** of 0.05 over the entire `m=4..128` ladder.

Selected Gaussian results:

| m | naive normal FPR @ 5% | predictive-t FPR @ 5% | exact-rank FPR @ 5% | rank resolution |
|---:|---:|---:|---:|---:|
| 4 | 17.680% | **4.925%** | 0% | 0.2000 |
| 32 | 6.171% | **4.994%** | 3.065% | 0.0303 |
| 128 | 5.285% | **4.978%** | 4.673% | 0.00775 |

This reproduces the earlier diagnosis: treating a small-null studentized statistic as Gaussian is badly anti-conservative, while predictive Student-t fixes that failure when the score law is Gaussian.

### 2. Predictive Student-t is not distribution-free

The adversarial score families produce a negative result for the stronger interpretation of the previous audit.

At `m=4`:

| score law | predictive-t FPR @ 5% | predictive-t FPR @ 1% |
|---|---:|---:|
| Gaussian | 4.925% | 0.978% |
| Student-t5 | 5.991% | 1.412% |
| lognormal | **9.436%** | **4.716%** |
| contaminated Gaussian | 6.531% | 2.033% |

Across all non-Gaussian cells, the worst observed predictive-t inflation was **1.8872x at the 5% level** and **5.254x at the 1% level**.

Increasing `m` does not automatically cure tail-shape mismatch. At `m=128`, for example, the lognormal score law gives predictive-t FPR **2.970% at nominal 1%**, and Student-t5 gives **2.140%**. The finite-variance estimate has stabilized, but the reference distribution is still wrong in the tail.

This is the central negative result: **the Student-t repair is a parametric calibration, not an exchangeability-only calibration**.

### 3. Exact rank survives score-shape changes, but small `m` cannot support fine tail claims

Because the exact leave-one-out statistic is ranked symmetrically among all `m+1` exchangeable members, its null rank is distribution-free for the continuous families tested here. Its cost is discreteness.

The minimum attainable p-value is

\[
p_{min}=\frac{1}{m+1}.
\]

Consequently:

- `m=4`: `p_min=0.20`;
- `m=8`: `p_min=0.1111`;
- `m=16`: `p_min=0.0588`;
- `m=32`: `p_min=0.0303`;
- `m=64`: `p_min=0.0154`;
- `m=128`: `p_min=0.00775`.

A calibration-free claim at `p<=0.05` therefore needs **at least 19 matched nulls**. A claim at `p<=0.01` needs **at least 99**. With four matched nulls, an exact distribution-free 5% tail claim is mathematically unavailable, regardless of how extreme `z_like` appears.

At `m=128`, the exact-rank 5% rejection rates were 4.673% (Gaussian), 4.557% (Student-t5), 4.596% (lognormal), and 4.696% (contaminated Gaussian). At the 1% level they were 0.797%, 0.770%, 0.781%, and 0.783%, respectively, consistent with the expected conservative discretization.

## Scientific update

The previous conclusion should be narrowed, not discarded.

**Still supported:** the naive Gaussian reading of `z_matched_null` is wrong for small null ensembles, and predictive Student-t is the correct finite-null reference under the Gaussian score model. The earlier 600-row synthetic smoke was broadly compatible with that parametric calibration.

**Newly falsified:** exchangeability by itself does not justify the predictive-t p-value. A skewed or heavy-tailed matched-null score law can leave substantial tail inflation even when `m` is large.

**New operational rule:** a real-map Pontifex CMB result must choose one of two paths before looking at a claimed tail:

1. justify a parametric score law and use its calibrated predictive distribution; or
2. use an exact exchangeability/rank test with enough matched null maps to resolve the predeclared alpha (`m>=19` for 5%, `m>=99` for 1%).

The second path is more expensive, but it removes an assumption that the current CMB harness has not yet earned.

## Evidence boundary

**Supported here:** under controlled exchangeable simulations, predictive Student-t is well calibrated for Gaussian matched-null scores; it can be materially anti-conservative for skew/heavy-tailed scores; exact leave-one-out ranking is robust to those score-shape perturbations and exposes the hard p-value resolution imposed by a finite null ensemble.

**Not established:** that the actual `score` distribution produced by the Pontifex CMB occlusion harness is Gaussian, Student-t5, lognormal, contaminated Gaussian, or any mixture of these; that Planck/ACT null maps are exchangeable with the observed sky; that the lightweight synthetic null generator is adequate for cosmology; any CMB anomaly; any Torus causal mechanism; or any downstream Assembly/student benefit.

The non-Gaussian families are intentionally adversarial **stylized score laws**. They demonstrate an assumption sensitivity of the calibration method; they do not estimate the real CMB score law.

The reserved learning partitions remain untouched:

\[
D_{assembly}\perp D_{student}\perp D_{val}\perp D_{test}.
\]

## Next discriminant

The next experiment should move from stylized score laws back into the CMB harness itself:

1. persist the individual matched-null scores, not only their mean/SD;
2. run `m=32,64,128` over multiple independent synthetic skies with fixed theta streams;
3. compare predictive-t and exact leave-one-out rank p-values on those real harness score ensembles;
4. quantify score skewness/tail behavior by intervention family before choosing a production calibration rule.

That experiment can tell whether the score-law robustness failure demonstrated here is merely adversarial possibility or an active property of the Pontifex occlusion statistic.

## Reproducibility

- robustness script: `experiments/pontifex_torus/cmb_matched_null_robustness_ladder.py`
- workflow: `.github/workflows/pontifex-cmb-matched-null-robustness.yml`
- implementation commit: `e71d24f749e9fd8b2d0c82225cee33b33f7a5701`
- workflow commit: `113b2187966b37ebfaac01c59f7d61eec2ff6c07`
- full local command: `uv run experiments/pontifex_torus/cmb_matched_null_robustness_ladder.py --trials 100000`
- PR CI uses 50,000 trials per family/null-count cell for a faster reproducibility smoke.
