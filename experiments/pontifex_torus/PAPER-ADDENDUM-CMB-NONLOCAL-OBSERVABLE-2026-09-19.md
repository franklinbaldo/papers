---
type: Experiment Report
title: "Pontifex CMB: a genuinely nonlocal synthetic response axis"
date: 2026-09-19
status: experimental
---

# Pontifex CMB: a genuinely nonlocal synthetic response axis

## Question

The preceding component-attribution experiment showed that the nominal three-term CMB response score is effectively one-dimensional in the current synthetic harness: `boundary_shift` is structurally zero, while `sqrt(global_energy)` is a positive theta-dependent rescaling of `core_rmse`. Consequently, identical matched-null calibration for those terms did not establish a multichannel response.

This experiment asks the narrow next question: **does a measurement that genuinely observes outside the mutated core produce information that cannot be reduced to the old core-amplitude channel?**

The existing baseline score is left unchanged.

## Discriminating intervention/observation contract

`cmb_nonlocal_observable_ablation.py` keeps the existing intervention exactly where it was: only the `core` is modified. It then applies a fixed Gaussian observation beam to the resulting delta field and measures the blurred response in the unchanged outer boundary ring.

Three quantities are persisted separately:

- `core_rmse`, the old effective response axis;
- `beam_boundary_rmse`, the new nonlocal observation;
- `beam_leakage_ratio = beam_boundary_rmse / core_rmse`, a scale-normalized diagnostic.

The Gaussian beam has sigma 2 pixels. It is deliberately a simple synthetic observation operator, not an instrument model.

The experiment uses **8 independently generated synthetic skies**, with a fixed balanced panel of five occlusion families x three geometries x four replicates: **60 theta per sky, 480 theta rows**. Each theta is calibrated against **64 matched null maps**. The rank resolution is therefore `1/65 = 0.01538`.

## Result: the nonlocal observable does not collapse to the core-amplitude channel

The result rejects the simple degeneracy that affected the previous score components.

Across the eight independent skies, the observed Pearson correlation between `core_rmse` and `beam_boundary_rmse` is high but clearly imperfect:

- mean: **0.9075**;
- median: **0.9209**;
- range: **0.8308 to 0.9404**.

More importantly, the scale-normalized leakage ratio varies substantially within every sky. Its coefficient of variation has:

- mean: **0.4664**;
- median: **0.4673**;
- range: **0.4365 to 0.4919**.

This rules out the specific explanation that the new observable is merely a fixed positive rescaling of `core_rmse` within a sky.

The matched-null calibration changes as well. Among **472 rows for which core, nonlocal, and leakage-ratio calibration are all finite**:

- the exact-rank p-value for `beam_boundary_rmse` differs from the core rank p-value in **95.13%** of rows;
- median absolute difference in exact-rank p is **0.1462**;
- mean absolute difference is **0.1885**;
- core and nonlocal exact-rank p-values correlate only **0.6118**;
- the two axes disagree on the `p <= 0.05` rank decision in **4.87%** of paired rows.

The predictive-Student-t calibration also differs: median absolute p difference **0.1368**, mean **0.1823**.

For the leakage ratio itself, the median absolute exact-rank p difference versus core is larger again, **0.2923**. Eight leakage-ratio rows have zero matched-null variance; these are retained as an explicit negative/degenerate corner rather than silently coerced into finite p-values.

## What the result supports

This is positive evidence for a **second synthetic response coordinate** in the present harness. The new boundary statistic is not algebraically the old core amplitude under a per-theta positive rescaling, and it changes the ordering of observed versus matched-null responses for most theta rows.

That is enough to justify carrying the nonlocal observable forward as a separate diagnostic channel. It is **not** enough to replace the baseline scalar score or to claim that a particular multichannel combination is scientifically optimal.

## What the result does not support

The Gaussian beam was introduced as a discriminating observation operator. It is not a model of Planck, ACT, beam transfer functions, mapmaking, radiative propagation, or any other real CMB measurement process. Therefore this result is **not evidence** for:

- a real CMB anomaly;
- a physically nonlocal cosmological effect;
- Pontifex/Torus causality;
- the physical adequacy of the Gaussian-beam observable;
- a benefit to Assembly or student learning.

The experiment establishes a property of the synthetic measurement geometry only: once the observation contract is allowed to couple the modified core to an exterior ring, the response no longer collapses to one scalar amplitude axis.

## Dependence and data boundary

The independent replication unit is the synthetic sky. Theta rows within a sky share the field and matched-null bank and must not be read as independent population tests.

No Assembly, student, validation, or test data enter this experiment. The strict partition boundary remains untouched:

`D_assembly ⟂ D_student ⟂ D_val ⟂ D_test`.

No model selection, threshold choice, or feature construction here uses any of those partitions.

## Consequence for the paper

The previous statement that the current CMB score is effectively one-dimensional remains true for the **baseline score**. This experiment does not rewrite that history. Instead it shows constructively that the degeneracy is a property of the old measurement contract, not an unavoidable property of the intervention family.

Accordingly, future experiments should report the original score for continuity and report a nonlocal channel separately until a physically justified observation model earns the right to combine them.

## Next discriminant

The next useful test is a **beam-width ladder** with sigma approaching zero and increasing through several spatial scales, while preserving exactly the same skies, theta panel, and null bank. A real nonlocal effect of the observation contract should disappear continuously as sigma approaches zero and should exhibit a reproducible scale curve. If the apparent second axis does not obey that control, the present result should be treated as an implementation artifact rather than meaningful geometry.
