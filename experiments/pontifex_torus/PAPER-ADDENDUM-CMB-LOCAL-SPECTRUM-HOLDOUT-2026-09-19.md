---
type: Experiment Report
title: "Pontifex CMB: local-spectrum controller on held-out skies"
date: 2026-09-19
status: experimental
---

# Pontifex CMB: local-spectrum controller on held-out skies

## Question

The preceding scale-modulation experiment tested a controller based on the global quantity

`log(lesion radius / field correlation length)`

and obtained a useful negative result: the development rule `[0.5, 0.5, 0.25]` did not reliably beat the already-frozen `w=0.5` beam on disjoint held-out skies. Across 16 held-out base skies its median adaptive-minus-fixed gain was only about `+0.00024`, the exact two-sided sign-test p-value was `0.424`, and the controller recovered only about `2.7%` of the descriptive row-oracle gain.

The next discriminant was therefore predeclared more narrowly: **does an outcome-free local spectral descriptor around the lesion contain predictive scale information that one global field correlation length discards?**

## Descriptor

For each theta, before applying any occlusion, the experiment measures the immediate context ring outside the modified core and computes

`local_roughness = radius * RMS(|metric gradient of field|) / SD(field)`.

The x and y derivatives are expressed in the same unit metric used by the lesion and metric-aware beam. Multiplying by lesion radius makes the statistic dimensionless: larger values mean more local spatial variation per lesion radius.

The descriptor uses only the **unaltered input field** and theta geometry. It never sees the altered field, leakage outcome, matched-null scores, chosen width, or held-out outcomes.

## Confirmatory protocol

This experiment intentionally uses a new theta panel and new skies rather than recycling outcomes inspected in the previous controller experiment.

- candidate widths: `0.125, 0.25, 0.5, 1.0` lesion radii;
- fixed baseline: `w=0.5`;
- field conditions: metric-isotropic `k0 = 4, 8, 16` cycles per unit;
- balanced theta panel: 2 theta per `geometry × occlusion` cell = 30 theta per field condition;
- development: 12 independent base skies;
- held-out: 24 independent base skies;
- spectral conditions within a base sky are paired repeated measurements, not independent replicates;
- inferential replication unit: independent base-sky seed.

On development skies only, `log(local_roughness)` is divided into three quantile bins. One width is selected per bin by maximizing the median across development skies of within-sky median leakage. Ties favor the pre-existing `w=0.5` baseline, then the smaller width. Bin edges and width choices are frozen **before any held-out sky is generated**.

## Development result

The development quantile edges were:

- `0.38387`;
- `0.97418`.

The frozen width rule was again:

`[0.5, 0.5, 0.25]`.

But the separation between bins was much sharper than in the failed global-correlation controller. Development median leakage scores were:

| local-roughness bin | w=.125 | w=.25 | w=.5 | w=1.0 | frozen |
|---|---:|---:|---:|---:|---:|
| low | 0.00859 | 0.10808 | **0.15527** | 0.10830 | 0.5 |
| middle | 0.07309 | 0.13343 | **0.15072** | 0.09717 | 0.5 |
| high | 0.10796 | **0.12119** | 0.09876 | 0.05573 | 0.25 |

The descriptor distribution itself transferred cleanly: median local roughness was `1.9645` on development rows and `1.9833` on held-out rows. There were 1,080 development rows and 2,160 held-out rows; the smallest accepted context ring contained four pixels. No held-out outcome was used to define the descriptor or rule.

## Held-out result

The local controller **did beat** fixed `w=0.5` on the new held-out skies.

Across 24 independent base skies:

- adaptive-minus-fixed mean: **`+0.00670`**;
- median: **`+0.00665`**;
- range: `[-0.00172, +0.01849]`;
- adaptive wins: **22/24** skies;
- nonzero paired differences: 24/24;
- exact two-sided sign-test p: **`3.5882e-05`**.

The selected-width counts across all held-out rows were:

- `w=0.5`: 1,411 rows;
- `w=0.25`: 749 rows;
- `w=0.125` and `w=1.0`: zero rows.

The positive contrast was not confined to one field cutoff. Descriptively, median adaptive-minus-fixed leakage was:

- `k0=4`: `+0.00184`;
- `k0=8`: `+0.00904`;
- `k0=16`: `+0.00762`.

Relative to the per-row oracle ceiling, the local controller recovered a median **`40.15%`** of the available sky-level gain. That number is descriptive only; the oracle never enters fitting, selection, binning, or inference.

The prior global-correlation controller recovered only about `2.7%` and was not significant. The magnitude contrast is scientifically suggestive, but it is **not a paired head-to-head test** because this experiment deliberately used a new theta panel and new sky seeds.

## What this supports

Within the current synthetic harness, **pre-intervention local field roughness contains held-out predictive information about the useful observation width that is not captured adequately by a single global field correlation length**.

This is stronger than the earlier row-level covariance result because the descriptor, quantile edges, and width rule were learned only on development skies and then frozen before 24 new base skies were generated.

It also narrows the synthetic mechanism: the reproducible `w≈0.5` aggregate optimum is not the whole story. A high-local-roughness regime reproducibly benefits from a narrower `w=0.25` observation scale.

## What this does not support

This experiment does **not** establish:

- that the chosen roughness statistic is the unique or causal field variable;
- that the effect is purely spectral rather than partly encoded by the geometry of the context ring;
- a physical CMB length scale;
- a Planck or ACT beam law;
- a real-sky anomaly;
- physical nonlocality;
- Torus topology or Torus causality.

The descriptor's context ring is theta-dependent, so it can carry geometry/scale information in addition to local field texture. That is now the main confound to attack rather than something to hide.

## Evidence / hypothesis boundary

**Evidence:** one predeclared, outcome-free local descriptor produced a frozen development rule that improved median leakage over the existing `w=0.5` baseline on 22/24 new independent base skies.

**Hypothesis:** the useful variable is genuinely *local spectral structure* near the lesion, rather than geometry encoded by the sampling ring or another correlated local statistic.

The latter has not yet been established.

The strict downstream data boundary remains unchanged:

`D_assembly ⟂ D_student ⟂ D_val ⟂ D_test`.

None of those datasets enters this experiment.

## Next discriminant

Use the same local-roughness formula on a **matched remote control ring**: same theta shape, radius, and field realization, but translated away from the lesion before any intervention. Learn local-ring and remote-ring controllers under identical development/held-out protocols.

If only the lesion-local descriptor transfers, locality earns additional evidence. If the remote descriptor performs similarly, the present gain is more likely explained by global/geometry-correlated information than by genuinely lesion-local spectral structure.
