---
type: Experiment Report
title: "Pontifex CMB: half-radius beam survives metric-spectrum control"
date: 2026-09-19
status: experimental
---

# Pontifex CMB: half-radius beam survives metric-spectrum control

## Why this control was necessary

The previous metric-aware beam experiment corrected the observation kernel so that a nominal beam width means the same distance in the metric used by the synthetic lesion. A second geometric confound remained in the synthetic sky generator itself.

`synthetic_map` builds its spectrum with `np.fft.fftfreq(n)` in cycles per pixel. On the `64 x 128` grid, however, the mask metric gives the effective x and y axes the same unit length. Consequently the legacy spectral filter is anisotropic in the metric in which the lesion and beam are defined. A scale preference near `0.5 x lesion radius` could therefore have been a beam-field artifact rather than a property of the lesion-relative observation geometry.

This addendum tests that alternative directly rather than assuming the legacy synthetic field is isotropic.

## Frozen discriminant

The beam ladder is not re-tuned. The candidate widths remain `0.125, 0.25, 0.5, 1.0` times lesion radius, and `0.5` remains the frozen reference selected before this experiment.

For each of 12 independent base sky seeds, the experiment draws one white-noise realization and constructs four paired fields from it:

- the exact legacy cycles-per-pixel spectrum;
- a metric-isotropic spectrum with cutoff `k0=4` cycles per metric unit;
- metric-isotropic `k0=8`;
- metric-isotropic `k0=16`.

The same fixed balanced theta panel is applied to every field: 30 interventions per sky, with two replicates for every `3 geometries x 5 occlusion families` cell. The independent base sky is the replication unit. Theta rows inside a sky are not treated as independent samples.

The experiment measures the 1/e autocorrelation length independently along x and y, the sky-level median leakage curve over beam width, and the row-level relation between `lesion radius / measured field correlation length` and the preferred beam width.

No matched-null p-value is used here: this discriminant is about the geometry of the synthetic response curve and the spectrum of the field, not anomaly detection.

## The legacy generator really was anisotropic

The audit confirms the confound rather than merely positing it. In the legacy field, the median 1/e autocorrelation lengths were approximately:

- x: `0.03669` metric units;
- y: `0.07268` metric units;
- x/y ratio: `0.5012`.

The metric-isotropic fields remove that factor-of-two distortion while spanning substantially different correlation scales:

| field | median corr. length x | median corr. length y | median x/y |
|---|---:|---:|---:|
| legacy pixel spectrum | 0.03669 | 0.07268 | 0.5012 |
| metric `k0=4` | 0.11535 | 0.11738 | 1.0203 |
| metric `k0=8` | 0.06229 | 0.06286 | 0.9610 |
| metric `k0=16` | 0.03229 | 0.03286 | 0.9886 |

Thus the control changes both the metric anisotropy and, across `k0`, the characteristic field scale.

## Main result: the sky-level half-radius peak survives

Despite that intervention, `0.5 x lesion radius` remains the width with the largest **sky-level median leakage in 12/12 independent skies in every one of the four field conditions**.

The frozen width also beats every unchanged alternative in all 12 paired skies for every field condition. Because there are 12 predeclared condition-by-alternative contrasts, the exact two-sided sign-test value `p=0.00048828125` becomes `p_Holm=0.005859375` under one global Holm correction.

Median sky-level leakage advantages of width `0.5` over the alternatives were:

| field | vs 0.125 | vs 0.25 | vs 1.0 |
|---|---:|---:|---:|
| legacy | +0.11886 | +0.03427 | +0.04769 |
| metric `k0=4` | +0.13264 | +0.04526 | +0.05158 |
| metric `k0=8` | +0.12371 | +0.03426 | +0.05033 |
| metric `k0=16` | +0.10904 | +0.02961 | +0.04757 |

This is a positive result for the narrow synthetic claim: the aggregate half-radius preference is not removed by correcting the field to the lesion metric, and it persists while the metric-isotropic field correlation length changes by more than a factor of three.

## Important negative/mixed result: local peak width is not field-independent

The stronger hypothesis — that the preferred scale is purely lesion-relative and insensitive to field structure — is **not** supported.

Within individual skies, the row-level preferred beam width remains negatively associated with `log(lesion radius / field correlation length)`. The median within-sky Spearman correlations are:

- legacy: `-0.451`;
- metric `k0=4`: `-0.357`;
- metric `k0=8`: `-0.451`;
- metric `k0=16`: `-0.520`.

So the result has two levels that must not be conflated:

1. **aggregate sky-level geometry:** the frozen half-radius peak is exceptionally stable across field metrics and spectral cutoffs;
2. **per-intervention geometry:** which beam width maximizes leakage still covaries with lesion size relative to the field correlation length.

A plausible hypothesis is therefore a two-scale interaction: lesion-relative geometry determines the broad aggregate optimum, while field correlation structure modulates the optimum locally. This is a hypothesis generated by the control, not an established mechanism.

## Evidence boundary

What the experiment supports:

- the legacy synthetic field had a real metric anisotropy;
- correcting that anisotropy does not abolish the aggregate `w=0.5` preference;
- the aggregate preference survives metric-isotropic fields with markedly different correlation lengths;
- local preferred widths still carry measurable dependence on lesion size relative to field correlation length.

What it does **not** support:

- that `0.5 x lesion radius` is a physical CMB scale;
- that a Gaussian beam is an adequate Planck or ACT observation model;
- that the synthetic correlation structure matches the real sky;
- a CMB anomaly, physical nonlocality, topology, or Torus causality;
- any downstream Assembly/student performance claim.

The experiment uses synthetic instrumentation only. The future-data boundary remains explicit and unchanged:

`D_assembly ⟂ D_student ⟂ D_val ⟂ D_test`.

None of those four datasets enters this experiment.

## Next discriminant

The next useful test is no longer another global width sweep. The aggregate peak is already robust to this field-spectrum control. The sharper question is whether the **row-level** scale modulation is predictable out of sample.

A discriminating follow-up should fit, on development skies only, a rule mapping `lesion radius / measured field correlation length` (plus geometry/occlusion family if needed) to a predicted beam width, freeze that rule, and evaluate it on disjoint held-out skies against the fixed `w=0.5` baseline. If the adaptive rule fails held out, the present row-level correlation should be treated as descriptive. If it improves held-out leakage reproducibly, the field-coupling component becomes a real predictive result rather than a post-hoc pattern.
