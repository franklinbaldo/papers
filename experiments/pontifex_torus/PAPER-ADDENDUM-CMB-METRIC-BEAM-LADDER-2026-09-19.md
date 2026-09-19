---
type: Experiment Report
title: "Pontifex CMB: metric-aware nonlocal beam-width ladder"
date: 2026-09-19
status: experimental
---

# Pontifex CMB: metric-aware nonlocal beam-width ladder

## Why this refinement was necessary

The preceding nonlocal-observable ablation established that a blurred response measured outside the directly mutated core can produce matched-null ranks that are not identical to `core_rmse`.

That result was useful, but its beam used a scalar sigma in pixel coordinates on a `64 x 128` synthetic grid. The radial geometry in `synthetic_masks`, however, uses x with normalized spacing `1/nx` and the effective y coordinate `0.5*y` with normalized spacing `1/ny`. Therefore a scalar two-pixel Gaussian is not isotropic in the same metric that defines the lesion: it is physically twice as wide along the effective y coordinate as along x.

This does not erase the previous existence result, but it weakens any interpretation of the chosen beam width as a meaningful geometric scale.

## Discriminating experiment

`cmb_metric_beam_ladder.py` removes that anisotropy and adds the local-limit control that the previous experiment lacked.

For every theta, Gaussian width is defined as a fraction `w` of that theta's lesion radius:

- `sigma_y = w * radius * ny`
- `sigma_x = w * radius * nx`

Thus the observation kernel is isotropic in the normalized metric used by the synthetic lesion itself. The ladder is:

`w = 0, 0.125, 0.25, 0.5, 1.0`.

Width zero is not approximated by a tiny Gaussian: it is explicitly the unblurred delta field. Because the intervention changes only `core`, a correct implementation must produce exactly zero response in the unchanged boundary at `w=0`.

The same **6 independently generated synthetic skies**, the same balanced theta panel, and the same matched-null bank are reused at every width. Each sky contains five occlusion families x three geometries x three replicates = **45 theta**, for **270 theta rows**, each with **32 matched null maps**. Width is therefore the only changed experimental coordinate.

## Results

The local-limit control behaved exactly as required: at `w=0`, all **270/270** boundary responses were zero and all 270 matched-null calibrations were zero-variance/undefined. That is a positive implementation control, not a scientific detection.

For nonzero widths, all 270 rows were calibratable. Median observed leakage ratio (`beam_boundary_rmse / core_rmse`) followed a reproducible non-monotone scale curve:

| beam width / lesion radius | median leakage ratio | median core-boundary raw correlation across skies | median absolute rank-p difference vs core | rank decision disagreement at 5% |
|---:|---:|---:|---:|---:|
| 0.125 | 0.03791 | 0.83836 | 0.12121 | 0.03333 |
| 0.25 | 0.09953 | 0.88868 | 0.09091 | 0.02593 |
| 0.5 | 0.12652 | 0.85808 | 0.09091 | 0.01111 |
| 1.0 | 0.08311 | 0.73746 | 0.15152 | 0.02963 |

The response therefore does **not** merely increase without bound as the Gaussian gets wider. It emerges from zero, rises, and then weakens again by one full lesion radius.

Using the independent sky as the replication unit, the median leakage curve peaked at **`w=0.5` in all 6/6 skies**. At the individual-theta level, peak widths were distributed as:

- `w=0.125`: 13/270;
- `w=0.25`: 77/270;
- `w=0.5`: 142/270;
- `w=1.0`: 38/270.

The leakage ratio is materially width-sensitive: its coefficient of variation across the four nonzero widths has median **0.56384** across theta rows.

The matched-null ordering also remains distinct from the local core channel. Depending on width, **81.1% to 89.3%** of rows have a boundary rank p-value that is not numerically identical to the core rank p-value. The rank-p correlation with `core_rmse` is approximately `0.626`, `0.684`, `0.703`, and `0.429` as `w` increases from `0.125` to `1.0`.

## What is evidence

Within this synthetic harness, the new result supports three narrow claims:

1. the second response coordinate survives after correcting the pixel-metric anisotropy of the preceding experiment;
2. it vanishes exactly in the local `w=0` limit, as a genuinely nonlocal observation coordinate should under this construction;
3. it has a reproducible scale dependence rather than behaving as an arbitrary positive rescaling of core amplitude. In particular, every independent sky has its median leakage maximum at approximately half a lesion radius in this tested ladder.

These observations make the nonlocal-observation interpretation more credible **inside the synthetic model** than the previous fixed-two-pixel result alone.

## What remains hypothesis

The location of the apparent maximum near `w=0.5` is **not** established as a universal or physically meaningful scale. The ladder is coarse, the observation operator is Gaussian by construction, and the synthetic field/null generator determines much of the geometry being measured.

A denser ladder could move the maximum. Different field spectra, boundary definitions, or instrument operators could change or remove it entirely.

Likewise, the fact that matched-null ranks differ from `core_rmse` does not imply statistical independence: raw correlations remain substantial, and the two coordinates share the same underlying intervention.

## Explicit evidence boundary

This experiment is a synthetic measurement-contract test only. It is **not evidence** for:

- a real CMB anomaly;
- physical nonlocality;
- a toroidal topology of the universe;
- Planck or ACT instrument behavior;
- causal validity of the Pontifex Torus hypothesis;
- improved downstream learning.

The Gaussian kernel here is an intentionally transparent probe, not an astrophysical beam model. Real-sky escalation still requires a physically justified observation operator and scientifically appropriate `C_l`-matched / `a_lm` null skies.

The data boundary is unchanged and strict:

`D_assembly ⟂ D_student ⟂ D_val ⟂ D_test`.

No assembly, student, validation, or test partition enters this experiment.

## Next discriminant

The next useful test is a **dense scale localization with held-out skies**: choose candidate width from a development set of independent synthetic skies, freeze it, and measure the scale-response curve on fresh synthetic skies that played no role in selecting the width. That would distinguish a reproducible characteristic observation scale from a maximum selected on the same six skies used to inspect the curve.
