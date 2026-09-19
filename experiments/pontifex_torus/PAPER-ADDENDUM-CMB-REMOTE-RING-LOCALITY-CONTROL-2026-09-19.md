---
type: Experiment Report
title: "Pontifex CMB: matched remote-ring locality control"
date: 2026-09-19
status: experimental
---

# Pontifex CMB: matched remote-ring locality control

## Question

The preceding held-out experiment showed that a pre-intervention roughness descriptor measured in the immediate unaltered ring around a synthetic lesion can choose an observation width that beats the frozen `w=0.5` baseline on new skies.

That result left one major confound unresolved: the lesion-adjacent ring is theta-dependent and therefore can carry information about global field state, lesion scale, or geometry even if **spatial locality to the lesion itself is irrelevant**.

The discriminating question here is therefore:

> does the lesion-adjacent descriptor outperform an otherwise matched descriptor measured far away in the same field realization?

## Matched remote control

For each theta, a remote control theta is produced by translating the center by exactly half a period in the periodic x coordinate:

`center_a_remote = (center_a + 0.5) mod 1`.

Radius, geometry, aspect, phase, y coordinate, field realization, and descriptor formula are unchanged.

Both descriptors use

`roughness = radius * RMS(|metric gradient|) / SD(field)`

on an unaltered context ring.

The remote control therefore differs only in **where** the ring samples the field.

A geometric exclusion is applied before any sky outcome is generated: a theta is retained only if the complete remote context ring has zero overlap with the local lesion support. Tiny rings with fewer than four context pixels are also excluded. Of 45 pre-generated balanced theta rows, 39 survived this geometry-only filter.

## Confirmatory protocol

The experiment uses a new seed relative to the preceding local-controller test.

- balanced theta source: 3 theta per `geometry × occlusion` cell before geometry-only exclusions;
- accepted theta: 39/45;
- field conditions: metric-isotropic `k0 = 4, 8, 16` cycles per unit;
- candidate observation widths: `0.125, 0.25, 0.5, 1.0` lesion radii;
- pre-existing fixed baseline: `w=0.5`;
- development: 12 independent base skies;
- held-out: 24 independent base skies;
- inferential unit: base-sky seed; spectral conditions are nested repeated measurements.

Two controllers receive exactly the same flexibility: three development quantile bins and one selected width per bin.

- **LOCAL controller:** predictor = `log(local roughness)`;
- **REMOTE controller:** predictor = `log(remote roughness)`.

Both sets of bin edges and widths are frozen before any held-out sky is generated.

The primary planned contrast is LOCAL minus REMOTE. Two secondary planned contrasts compare each adaptive controller with fixed `w=0.5`. Exact two-sided sign tests are Holm-adjusted across all three planned contrasts.

## Development result

The frozen LOCAL rule was:

`[0.5, 0.25, 0.25]`.

The frozen REMOTE rule was:

`[0.5, 0.5, 0.25]`.

Thus the two development fits were not forced to coincide. The middle roughness regime is the main place where the learned policies differ.

Development contained 1,404 rows.

## Held-out result

Held-out evaluation contained 2,808 rows across 24 independent base skies.

The local and remote descriptors were strongly correlated (`Pearson r = 0.9391`), already warning that much of the predictive scale information is shared across distant positions in the same synthetic field.

### Primary locality contrast

LOCAL did **not** beat REMOTE.

Across 24 held-out base skies, LOCAL minus REMOTE had:

- mean: `+0.000289`;
- median: `0.000000`;
- range: `[-0.003566, +0.006676]`;
- LOCAL wins: 8;
- REMOTE wins: 11;
- ties: 5;
- nonzero paired differences: 19;
- exact two-sided sign-test p: `0.647606`;
- Holm-adjusted p: `0.647606`.

This is a clear negative result for the lesion-specific locality interpretation.

### Both adaptive controllers versus the fixed baseline

The negative locality result does **not** erase the earlier scale-adaptation signal.

LOCAL minus fixed `w=0.5`:

- mean: `+0.005948`;
- median: `+0.004794`;
- wins: 22/24 skies;
- exact sign-test p: `3.5882e-05`;
- Holm-adjusted p: `7.1764e-05`.

REMOTE minus fixed `w=0.5`:

- mean: `+0.005659`;
- median: `+0.004497`;
- wins: **24/24 skies**;
- exact sign-test p: `1.1921e-07`;
- Holm-adjusted p: `3.5763e-07`.

The matched remote controller therefore reproduces essentially the same held-out advantage as the lesion-adjacent controller, and in this panel its sky-level win count against the fixed baseline is even cleaner.

Descriptively, neither one spectral condition explains the whole result. The local-minus-remote medians are approximately zero at `k0=4` and `k0=8`, and `+0.00046` at `k0=16`; these condition-level summaries are repeated measurements and are not treated as independent confirmatory tests.

## What this supports

The experiment supports a narrower statement than the previous local-controller result:

**pre-intervention field state contains held-out information about useful observation width, but the present evidence does not localize that information specifically to the lesion neighborhood.**

The adaptive-scale effect survives a strong spatial control because a ring translated half a period away can learn a controller that also beats the fixed baseline on held-out skies.

This shifts the synthetic mechanism away from a simple claim of lesion-local texture and toward information shared over larger spatial scales, global spectral state, theta-linked scale information, or some combination of these.

## Negative result and falsified interpretation

The predeclared positive-locality criterion required LOCAL minus REMOTE to be consistently positive on held-out skies and survive the three-contrast Holm correction.

It did not.

Accordingly, the hypothesis

> "the held-out gain of the roughness controller is specifically caused by spectral structure local to the lesion"

is **not supported by this experiment** and should not be stated as an empirical conclusion from the current synthetic harness.

The strong correlation between local and remote descriptors (`r = 0.9391`) is consistent with the alternative that the controller is exploiting information that is spatially broad rather than lesion-specific.

## Evidence / hypothesis boundary

**Evidence:** two equally flexible, outcome-free controllers were learned only on development skies and frozen before held-out generation. A matched remote controller performed similarly to the local controller and significantly beat fixed `w=0.5`.

**Evidence against a stronger claim:** LOCAL did not outperform REMOTE (`Holm p = 0.648`).

**Hypothesis:** the useful variable may be a larger-scale or field-wide spectral state, or a geometry-conditioned statistic correlated across positions. This experiment does not identify which of those alternatives is responsible.

The experiment does **not** establish:

- a physical CMB scale;
- a Planck or ACT beam law;
- a real-sky anomaly;
- physical nonlocality;
- Torus topology or Torus causality.

The remote result is about information in a synthetic field, not evidence for physical action at a distance.

## Downstream data boundary

The strict downstream separation remains unchanged:

`D_assembly ⟂ D_student ⟂ D_val ⟂ D_test`.

None of those datasets enters descriptor construction, development selection, held-out evaluation, or inference in this experiment.

## Next discriminant

The next useful test should remove the remaining single-remote-location arbitrariness. For each theta and sky, sample several predeclared non-overlapping remote rings at different translations, estimate the distribution of remote roughness/controller decisions, and compare the lesion-adjacent descriptor against that within-sky remote ensemble.

If the lesion-local ring is not exceptional relative to several matched remote rings, the locality interpretation should be retired. If it becomes exceptional only after controlling for the field-wide remote distribution, that would provide a cleaner route to testing genuinely local residual information.
