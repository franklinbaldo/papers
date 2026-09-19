# Pontifex CMB addendum — radius-conditioned roughness holdout

**Date:** 2026-09-19  
**Status:** experimental addendum; synthetic evidence only  
**Branch:** `experiment/pontifex-red-1`  
**PR:** [#485](https://github.com/franklinbaldo/papers/pull/485)

## Question

The preceding locality/cohort controls exposed a serious confound: apparent gains from a roughness-conditioned observation width changed when the geometry gate changed the lesion-radius distribution. A radius-matched follow-up then removed the cohort contrast and caused the roughness controller to collapse.

This addendum asks the narrower discriminating question:

> After lesion scale is given its own development-fitted policy, does pre-intervention context roughness add any held-out predictive value?

This is deliberately not a test of CMB physics. It is a test of what the current synthetic harness has actually earned.

## Predeclared design

A fresh balanced panel was frozen before generating skies:

- 120 theta rows (`8` per geometry × occlusion cell);
- geometries: `disc`, `ellipse`, `annulus`;
- occlusions: `hard`, `apodized`, `local_mean`, `residual_permute`, `adjacency_phase`;
- metric-isotropic field conditions: `k0 = {4, 8, 16}`;
- candidate observation widths: `{0.125, 0.25, 0.5, 1.0}` lesion radii;
- 12 development base skies;
- 24 disjoint held-out base skies;
- the independent inferential unit is the base-sky seed; theta and spectral rows are nested repeated measurements.

Three radius bands were fixed from the theta radii alone, before any sky outcome existed. Their interior edges were:

- `r = 0.0218706651`;
- `r = 0.0741399080`.

Two policies were then fit on **development only**:

1. **RADIUS** — one width per radius band.
2. **RADIUS+ROUGHNESS** — inside each radius band, split an outcome-free context-frequency proxy into two development quantile bins, then select one width per cell.

The conditional predictor removes the explicit radius multiplier from the earlier descriptor:

\[
\text{context-frequency}
= \frac{\text{local-spectral-roughness}}{r}
= \frac{\operatorname{RMS}(|\nabla f|)}{\operatorname{SD}(f)}.
\]

It is computed only from the unaltered context ring. The altered map, leakage response, matched-null scores and held-out outcomes never enter predictor construction or policy fitting.

A caveat remains explicit: the context-ring support itself depends on theta geometry and radius. This is coarse conditioning on scale, not an exact causal residualization.

## Development result: roughness adds no decision

The radius-only policy selected:

| Radius band | Selected width |
|---|---:|
| small | `0.5` |
| medium | `0.5` |
| large | `0.25` |

The extra roughness split selected exactly the same width on both sides of every within-radius roughness threshold:

| Radius band | low context-frequency | high context-frequency |
|---|---:|---:|
| small | `0.5` | `0.5` |
| medium | `0.5` | `0.5` |
| large | `0.25` | `0.25` |

So before opening held-out skies, the nominally more flexible policy had already collapsed to the radius-only policy. No post-hoc extra bins or richer model were introduced.

## Held-out result

### Primary contrast: RADIUS+ROUGHNESS vs RADIUS

The policies were identical on every held-out row. Consequently, across the 24 independent held-out base skies:

- mean difference: `0.000000`;
- median difference: `0.000000`;
- range: `[0.000000, 0.000000]`;
- positives / negatives / ties: `0 / 0 / 24`;
- exact two-sided sign-test `p = 1.0`;
- Holm-adjusted `p = 1.0`.

This is a clean negative result for incremental roughness complexity under the present predeclared design.

### Secondary contrast: RADIUS vs inherited fixed `w = 0.5`

The scale-only policy did replicate strongly on held-out skies:

- mean gain in median leakage: `+0.00358996`;
- median gain: `+0.00350098`;
- range: `[+0.00085849, +0.00739649]`;
- wins / losses / ties: `24 / 0 / 0`;
- exact two-sided sign-test `p = 1.1920929e-7`;
- Holm-adjusted `p = 3.5762787e-7` across the three planned tests.

The RADIUS+ROUGHNESS policy has exactly the same held-out numbers because it collapsed to RADIUS during development.

## Evidence

Within this synthetic harness, the new held-out evidence supports a **scale-conditional observation policy**: small and medium lesions favor `w = 0.5`, while the largest radius stratum favors `w = 0.25`. That frozen radius-only rule beat the inherited fixed `0.5` baseline on all 24 held-out skies.

The same experiment provides **no evidence that the tested pre-intervention context-frequency proxy adds predictive information once coarse lesion radius is already represented**. The added roughness degree of freedom never changed a development decision and therefore could not improve held-out performance.

This result sharpens the interpretation of the earlier roughness-controller gains: lesion scale is now a demonstrated competing explanation, whereas roughness has not earned an incremental control role under radius conditioning.

## Hypothesis boundary

Several possibilities remain hypotheses rather than evidence:

- a continuous radius law may outperform the three-band rule;
- field texture may interact with radius only in narrower regimes than these predeclared bins;
- a descriptor that is independent of theta-dependent ring support may recover texture information;
- different synthetic spectra or lesion families may shift the scale law.

None may be claimed from this run. Testing them requires a new development/freeze/held-out protocol; changing radius edges, adding roughness bins or fitting a richer controller to rescue the present negative would be post-hoc.

Most importantly, this experiment is **not evidence** for a physical CMB scale, Planck/ACT beam law, anomaly, physical nonlocality, topology, or Torus causality. It establishes only a reproducible relationship inside the current synthetic generator and observation contract.

## Data boundary

`D_assembly`, `D_student`, `D_val`, and `D_test` remain disjoint and untouched. None enters this synthetic experiment. Development and held-out synthetic base-sky seeds are disjoint, and held-out fields are generated only after the policy is frozen.

## Reproduction

Experiment:

- [`cmb_radius_conditioned_roughness_holdout.py`](./cmb_radius_conditioned_roughness_holdout.py)

Workflow:

- [`.github/workflows/pontifex-cmb-radius-conditioned-roughness.yml`](../../.github/workflows/pontifex-cmb-radius-conditioned-roughness.yml)

Confirmatory run used to write this addendum:

- [GitHub Actions run 35436716015](https://github.com/franklinbaldo/papers/actions/runs/35436716015)
- [artifact 10582336334](https://github.com/franklinbaldo/papers/actions/runs/35436716015/artifacts/10582336334)

The artifact persists both the JSON summary and all development/held-out rows. Scientific outcomes do not fail CI merely because a hypothesis is unsupported; infrastructure failures still do.
