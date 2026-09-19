---
type: Experiment Report
title: "Pontifex CMB: held-out test of radius/correlation-length scale modulation"
date: 2026-09-19
status: experimental
---

# Pontifex CMB: held-out test of radius/correlation-length scale modulation

## Question

The metric-spectrum control left two simultaneous observations inside the synthetic harness:

1. a fixed beam width near `0.5 × lesion radius` remained a reproducible sky-level optimum across substantially different metric-isotropic field spectra;
2. within skies, the row-level preferred width covaried with `lesion radius / field correlation length`.

The second pattern was descriptive. It had not yet shown that using the field correlation length actually improves prediction on unseen skies.

The discriminating question here is therefore stricter: **can a scale-modulation rule learned only on development skies beat the already-frozen fixed width `0.5` on disjoint held-out skies?**

## Frozen protocol

The theta panel is fixed before any sky generation. Three metric-isotropic field conditions are predeclared (`k0 = 4, 8, 16` cycles per metric unit), and conditions generated from the same white-noise realization are treated as repeated measurements nested inside one base sky.

Development uses 8 independent base skies. Held-out evaluation uses 16 disjoint base skies that are not generated until the rule is frozen.

The predictor is

`log(lesion radius / measured field-correlation-length geomean)`.

Development values are split into three quantile bins. Within each bin, the selected beam width maximizes the median across development base skies of the within-sky median leakage. Candidate widths remain exactly `{0.125, 0.25, 0.5, 1.0}`. Ties favor the already-established `0.5` baseline rather than additional complexity.

The frozen development rule was:

| development bin | log(radius/correlation-length) region | selected width |
|---|---|---:|
| low | `< -1.2433` | `0.5` |
| middle | `[-1.2433, -0.2941)` | `0.5` |
| high | `>= -0.2941` | `0.25` |

Thus development did recover the previously observed qualitative modulation: only the largest lesion-to-field-scale regime moved away from `0.5`, choosing `0.25`.

## Held-out result

On the 16 held-out base skies, the adaptive rule selected width `0.25` for 485 theta/field rows and width `0.5` for 955 rows.

The confirmatory unit is the independent base sky. For each held-out sky, all nested spectral conditions and theta rows are summarized to one median adaptive leakage and one median fixed-`0.5` leakage.

The adaptive-minus-fixed contrast was:

- mean: `+0.001260`;
- median: `+0.000243`;
- range: `[-0.002326, +0.005862]`;
- positive in 9 of 14 non-zero paired sky differences;
- 2 skies were exact ties at the sky-median level;
- exact two-sided sign-test `p = 0.42395`.

This is a **negative confirmatory result**. The pre-frozen modulation rule did not reliably beat the fixed `0.5` baseline on unseen base skies.

The descriptive per-spectrum medians were positive (`+0.00189` at `k0=4`, `+0.00328` at `k0=8`, `+0.00215` at `k0=16`), but these conditions share each base sky realization and are not independent inferential replicates. They therefore do not override the base-sky-level negative result.

## Oracle ceiling

For diagnosis only, the experiment also records the best candidate width separately for every held-out row. This per-row oracle never participates in binning, fitting, selection, or inference.

Relative to that ceiling, the frozen three-bin rule recovered a median of only `2.72%` of the available oracle improvement over fixed `0.5`; the distribution was highly unstable, including negative values when adaptation hurt. This argues against rescuing the result by treating the present three-bin rule as an approximately optimal controller.

## What changed scientifically

The earlier Spearman relationship remains real as a **descriptive covariance inside the synthetic generator**, but it is not promoted to a predictive control law by this experiment.

That distinction matters. The evidence now favors a simpler account:

- the aggregate intermediate optimum near `0.5 × lesion radius` is robust at the base-sky level;
- local field-scale variation exists;
- the particular one-dimensional summary `radius / correlation length`, used through a simple frozen three-bin controller, does not add reliable held-out value beyond the fixed width.

## Evidence / hypothesis boundary

**Evidence:** the development-only controller, with fixed model class and frozen bin edges/widths, failed to improve held-out base-sky leakage consistently over the pre-existing `0.5` baseline.

**Still hypothesis:** local optimal width may depend on a richer field descriptor than one scalar correlation length, for example anisotropic or scale-dependent spectral structure, local rather than sky-global correlation length, geometry/occlusion interaction, or a continuous multiscale response model.

**Not evidence:** this result says nothing about a real CMB anomaly, Planck or ACT beam physics, physical nonlocality, topology, or Torus causality. All fields here are synthetic and the observation operator remains an experimental instrument.

The data boundary remains strict: `D_assembly`, `D_student`, `D_val`, and `D_test` are disjoint and untouched. None enters this experiment.

## Practical consequence

Do **not** replace the fixed `w=0.5` synthetic baseline with the current radius/correlation-length controller. Keep `0.5` as the default synthetic reference until a richer adaptive model earns held-out improvement at the independent-sky level.

The next useful discriminant is not to increase controller flexibility immediately. First test whether a **local spectral descriptor** measured around each lesion predicts the row-level optimum on development skies and then freeze that descriptor-to-width mapping before held-out evaluation. That separates failure of the scalar global correlation length from failure of adaptation itself.

## Reproduction

- workflow run: https://github.com/franklinbaldo/papers/actions/runs/35420754004
- artifact: https://github.com/franklinbaldo/papers/actions/runs/35420754004/artifacts/10576977939
- script: `experiments/pontifex_torus/cmb_scale_modulation_holdout.py`
