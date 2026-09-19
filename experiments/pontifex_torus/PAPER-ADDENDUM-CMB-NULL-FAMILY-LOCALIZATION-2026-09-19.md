---
type: Experiment Report
title: "Pontifex CMB: matched-null family localization"
date: 2026-09-19
status: experimental
---

# Pontifex CMB: matched-null family localization

## Question

The previous empirical matched-null ladder found a small residual mismatch between predictive Student-t and exact exchangeable-rank calibration in the synthetic CMB harness, especially in the 1% tail. That experiment sampled a different theta panel for each sky, so sky-to-sky variation and intervention-family composition were partially confounded.

This addendum asks a discriminating question: **does the residual tail mismatch concentrate in one occlusion family when the theta panel is fixed and balanced across independent skies?**

## Design

`cmb_null_family_localization.py` fixes one theta panel and reuses it across **12 independently generated synthetic skies**. The panel is balanced over five occlusion families (`hard`, `apodized`, `local_mean`, `residual_permute`, `adjacency_phase`) and three geometries (`disc`, `ellipse`, `annulus`), with four theta replicates per geometry x occlusion cell: **60 theta per sky**.

For every theta on every sky, the experiment evaluates nested matched-null ensembles at `m=64` and `m=128`, persists every individual null score, and compares predictive Student-t with the symmetric leave-one-out exact-rank calibration. The principal replication unit for interpretation is the **independently generated sky**, not the individual theta row, because rows within one sky share the same field and null-map bank.

The run produced 720 finite rows at each null budget and no zero-variance exclusions.

## Global result

At `m=128` and nominal 5%:

- predictive Student-t rejection fraction: **6.11%**;
- exact-rank rejection fraction: **5.00%**;
- pooled difference: **+1.11 percentage points**;
- decision disagreement: **1.67%**;
- across skies, the predictive-minus-rank difference was positive in 6/12 skies and zero in 6/12.

At `m=128` and nominal 1%:

- predictive Student-t rejection fraction: **1.53%**;
- exact-rank rejection fraction: **0.97%**;
- pooled difference: **+0.56 percentage points**;
- decision disagreement: **0.83%**;
- across skies, the difference was positive in 5/12, zero in 6/12, and negative in 1/12.

The null-score law remains visibly non-Gaussian in low-order moments: at `m=128`, median skew is **0.708** and median excess kurtosis is **0.384**.

## Family localization at the 1% tail

At `m=128`, the mean predictive-minus-rank rejection-rate difference across independent skies was:

| occlusion family | mean difference |
|---|---:|
| hard | **-0.69 pp** |
| apodized | **+1.39 pp** |
| local_mean | **0.00 pp** |
| residual_permute | **+1.39 pp** |
| adjacency_phase | **+0.69 pp** |

The pooled family-level rates tell the same qualitative story: `local_mean` had exact agreement at 1% (1.39% versus 1.39%); `hard` went in the opposite direction (1.39% predictive versus 2.08% rank); `apodized` and `residual_permute` each showed +1.39 pp predictive excess; `adjacency_phase` showed +0.69 pp.

## Evidence

The fixed-panel result is evidence **against the simple hypothesis that one occlusion family is responsible for the residual Student-t tail mismatch**. The discrepancy is small, diffuse across several families, absent in `local_mean`, and even reverses sign for `hard`.

It also strengthens the narrower positive conclusion from the previous ladder: with `m=128`, predictive Student-t and exact rank remain close at the decision level in this synthetic harness. The remaining difference is measurable but small: 0.83% of rows disagree at the 1% threshold and 1.67% at the 5% threshold.

## Hypothesis boundary

The data do **not** identify the mechanism behind the remaining mismatch. A diffuse family pattern is compatible with at least three possibilities that remain hypotheses:

1. non-Gaussianity introduced by the common score functional;
2. structure induced by the phase-scrambled matched-null construction;
3. finer geometry x occlusion interactions that are hidden by marginalizing over geometry.

The descriptive tie between `apodized` and `residual_permute` is not evidence that either is a causal source, and the 12-sky sample is not a basis for ranking intervention families by scientific importance.

## Scope and data separation

This is a **synthetic calibration/falsification experiment**. It does not establish a real CMB anomaly, physical topology, Torus causality, or downstream learning benefit. Phase-scrambled synthetic nulls are not being presented as the final real-sky null model.

No Assembly, student, validation, or test data are used. The strict boundary remains unchanged:

`D_assembly ⟂ D_student ⟂ D_val ⟂ D_test`.

## Consequence

The practical rule should remain conservative: persist the individual matched-null scores; use predictive Student-t as a compact diagnostic, but report exact-rank calibration for scientifically important tail candidates when the null budget permits it.

The next discriminant should keep the same fixed sky/theta design and decompose by **geometry x occlusion** or by the constituent score terms (`core_rmse`, `boundary_shift`, `global_energy`). That can distinguish a genuinely local interaction mechanism from non-Gaussianity introduced by the shared scalar score itself.
