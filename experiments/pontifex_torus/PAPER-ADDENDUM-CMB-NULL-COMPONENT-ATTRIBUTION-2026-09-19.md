---
type: Experiment Report
title: "Pontifex CMB: matched-null component attribution"
date: 2026-09-19
status: experimental
---

# Pontifex CMB: matched-null component attribution

## Question

After the fixed-theta family and geometry x occlusion analyses failed to localize the residual predictive-Student-t versus exact-rank mismatch to a stable intervention family, the next discriminant asks a more mechanistic question: **which term of the current scalar response score carries the mismatch?**

The current synthetic score is built from `core_rmse`, `boundary_shift`, and `sqrt(global_energy)`. The experiment therefore persists and calibrates each component separately instead of assuming that the scalar score represents several independent response channels.

## Design

`cmb_null_component_attribution.py` uses **12 independently generated synthetic skies** and one fixed balanced theta panel with five occlusion families x three geometries x four replicates: **60 theta per sky, 720 rows**. Each theta is evaluated against **128 matched null maps**. The individual null values are persisted for:

- the full scalar `score`;
- `core_rmse`;
- `boundary_shift`;
- `sqrt_global_energy`, matching the transform that actually enters the score.

Predictive Student-t and symmetric leave-one-out exact-rank calibration are evaluated at 5% and 1%. The independent replication unit remains the sky; theta rows inside a sky are dependent diagnostics.

## Result: the nominal multi-component score collapses to one effective channel

The result is sharper than the original attribution hypothesis.

For `score`, `core_rmse`, and `sqrt_global_energy`, **all calibration summaries are numerically identical**. At the 1% tail, each gives:

- predictive Student-t rejection: **1.5278%**;
- exact-rank rejection: **0.9722%**;
- predictive-minus-rank difference: **+0.5556 percentage points**;
- decision disagreement: **0.8333%**;
- sky-blocked signed difference: positive in 5/12 skies, zero in 6/12, negative in 1/12.

The null-shape diagnostics are likewise identical: median skew **0.70755** and median excess kurtosis **0.38372**.

More strongly, among the **five rows** that are predictive-t-only rejections at 1%, the absolute predictive-t values of `score`, `core_rmse`, and `sqrt_global_energy` are identical row by row (median **2.76860**, range **2.68126--3.10906**).

`boundary_shift` contributes no calibratable variation at all: **all 720 rows have zero matched-null variance** for that component.

## Why this is structural, not merely empirical coincidence

The current intervention operator mutates only pixels inside `core`. The `boundary` pixels are not changed. Yet `boundary_shift` is defined as the difference between the mean altered boundary and the mean original boundary. Under this operator that quantity is therefore structurally zero.

The same support restriction explains the second degeneracy. Because the delta field is zero outside `core`,

`sqrt(global_energy)` is a positive theta-dependent scale multiple of `core_rmse`.

For a fixed theta the core mask is the same across the observed sky and all matched null maps, and the synthetic null construction preserves the map standard deviation. Predictive-t and rank calibration are invariant to that common positive rescaling. Consequently `core_rmse`, `sqrt_global_energy`, and their current weighted scalar combination carry the same calibration information.

So the experiment falsifies a useful implicit assumption: **in this synthetic harness the current response score is not a genuinely multi-channel response measure. It is effectively a one-dimensional core-amplitude statistic.**

## Evidence

The evidence supports these narrow claims:

1. the residual Student-t/rank mismatch is inherited from the core-amplitude response rather than attributable to a distinct boundary or global-energy channel;
2. `boundary_shift` is inert under the current local occlusion operator;
3. `sqrt_global_energy` does not add an independent calibration axis to `core_rmse` in this design;
4. the previous inability to localize the mismatch by occlusion family or geometry x occlusion is therefore consistent with a common one-dimensional response statistic.

This is a negative result for the current score design, but a positive result for identifiability: it removes two apparent explanatory degrees of freedom that were not actually independent.

## Hypothesis, not evidence

It is now reasonable to hypothesize that a genuinely nonlocal response observable could behave differently, but this run does **not** show that it will. A future score should only call a term a boundary/propagation channel if the intervention dynamics can produce a response outside the directly mutated core or if the observable measures a nontrivial relation between the changed core and unchanged context.

Possible next discriminants include a boundary-conditioned reconstruction residual or a nonlocal spectral/gradient response. These are design hypotheses, not results of the present experiment.

## Scope boundary

This is a synthetic calibration and measurement-contract result. It is **not** evidence of:

- a real CMB anomaly;
- physical topology;
- Torus causality;
- validity of phase-scrambled nulls for Planck/ACT production inference;
- any Assembly or student benefit.

The strict data boundary remains unchanged:

`D_assembly ⟂ D_student ⟂ D_val ⟂ D_test`.

No Assembly, student, validation, or test data are used here.

## Reproducibility

GitHub Actions run: `35404878220`.

Artifact: `10572237333` (`pontifex-cmb-null-component-attribution`), containing the aggregate JSON and all persisted per-theta component null values.

The experiment completed successfully; a scientific negative result does not fail CI.

## Next discriminant

Replace the structurally zero boundary term with a **genuinely context-sensitive observable without changing the existing score retroactively**, then compare that new observable against `core_rmse` under the same fixed theta panel and matched-null bank. The critical test is whether the new channel changes calibration/orderings independently of core amplitude. If it does not, the synthetic harness should be treated explicitly as a one-dimensional local-response stress test rather than as a multi-component propagation model.
