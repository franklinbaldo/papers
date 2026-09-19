---
type: Experiment Report
title: "Pontifex CMB: empirical matched-null score law"
date: 2026-09-18
status: experimental
---

# Pontifex CMB: empirical matched-null score law

## Question

The previous robustness ladder established a clean statistical boundary:

- predictive Student-t is exact for exchangeable Gaussian score laws;
- it is not distribution-free;
- an exact leave-one-out rank calibration is finite-sample valid under exchangeability but needs enough null maps to resolve the desired tail.

The unresolved empirical question was whether the **actual score distribution emitted by the Pontifex CMB synthetic harness** is close enough to Gaussian for predictive Student-t to be useful, or whether the adversarial non-Gaussian examples were materially relevant to the harness.

## Discriminating experiment

cmb_empirical_null_ladder.py uses the production synthetic score path rather than stylized draws.

For each of **6 independently generated synthetic skies**:

1. sample 48 intervention parameters theta;
2. generate a nested bank of 128 phase-scrambled matched null maps;
3. persist the observed score and all 128 individual matched-null scores;
4. evaluate the same score vector at **m = 32, 64, 128**;
5. compare predictive Student-t with the symmetric leave-one-out exact-rank calibration.

Map resolution is 64 x 128 for this CI-scale discriminant. The nested design ensures that changes across m are changes in null budget, not changes in theta.

Four of 288 theta rows had effectively zero null-score variance and were excluded by the predeclared finite-variance rule, leaving **284 finite rows** at every m.

## Results

| null maps m | predictive-t p<=.05 | exact-rank p<=.05 | disagreement @ .05 | predictive-t p<=.01 | exact-rank p<=.01 | median abs(p_t-p_rank) |
|---:|---:|---:|---:|---:|---:|---:|
| 32 | 0.04930 | 0.03873 | 0.01056 | 0.01408 | 0.00000 | 0.03787 |
| 64 | 0.05634 | 0.05634 | 0.00704 | 0.02113 | 0.00000 | 0.02401 |
| 128 | 0.05282 | 0.05282 | 0.01408 | 0.02113 | 0.01056 | 0.02185 |

The zero 1% rank rate at m=32 and m=64 is partly mechanical: the rank resolution is respectively 1/33 ~= 0.0303 and 1/65 ~= 0.0154, so those ensembles **cannot resolve p <= .01**. At m=128 the rank resolution becomes 1/129 ~= 0.00775 and the 1% comparison becomes meaningful.

The actual matched-null score law is not Gaussian in its low-order moments. Median null-score skew rises from **0.532 (m=32)** to **0.640 (m=64)** and **0.697 (m=128)**. Median excess kurtosis is **0.029**, **0.177**, and **0.372**, respectively.

## What this supports

At the **5% diagnostic level**, predictive Student-t is surprisingly robust for this synthetic harness once m reaches 64: its rejection fraction is identical to the exact-rank fraction at m=64 and m=128, and decision disagreement stays around 0.7--1.4%.

That is useful positive evidence that predictive Student-t can remain a practical smoke diagnostic here despite measurable skew.

## Negative result / remaining warning

The agreement does **not** extend cleanly into the 1% tail. At m=128, predictive Student-t marks **2.11%** of finite rows while exact rank marks **1.06%**. The score law also retains substantial positive skew.

Therefore the experiment does **not** justify calling predictive-t distribution-free, and it argues against using predictive-t alone for strong tail claims. For a candidate that matters scientifically, the individual scores should be retained and an empirical/rank calibration should be reported alongside any parametric statistic.

## Evidence boundary

This experiment establishes only properties of the **synthetic calibration mechanics** of the current Pontifex CMB harness.

It does **not** establish:

- a CMB anomaly;
- that the real Planck/ACT score law has the same shape;
- that phase-scrambled nulls are the final scientifically adequate real-sky null model;
- that the Torus causes the observed score geometry;
- any benefit for Assembly or student training.

Rows within a sky share the same field and null-map bank, so the pooled rejection fractions are diagnostic summaries over interventions, **not 284 independent population hypothesis tests**.

The strict future-data boundary remains untouched:

D_assembly is disjoint from D_student, D_val, and D_test.

No Assembly, student, validation, or test data are used here.

## Practical consequence

The harness now persists every individual matched-null score per theta. Future CMB runs should preserve those vectors as first-class artifacts rather than retaining only mean and standard deviation.

A reasonable escalation rule is:

1. use predictive Student-t as a cheap diagnostic;
2. require at least m=128 when interrogating ~1% tails;
3. report exact-rank calibration beside predictive-t for surviving candidates;
4. before real-sky claims, replace the synthetic phase-scramble placeholder with scientifically appropriate C_l-matched / a_lm null skies and repeat across independent real experiments.

## Next discriminant

Repeat the same empirical ladder with more independent skies while holding the theta distribution fixed, then stratify calibration by occlusion family. If the 1% predictive-t excess concentrates in one intervention family, the non-Gaussianity is mechanistically localizable; if it persists across families, the score functional itself is the more likely source.
