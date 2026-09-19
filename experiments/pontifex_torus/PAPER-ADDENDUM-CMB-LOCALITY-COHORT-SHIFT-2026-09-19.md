---
type: Experiment Report
title: "Pontifex CMB: matched cohort-shift ablation"
date: 2026-09-19
status: experimental
---

# Pontifex CMB: matched cohort-shift ablation

## Question

The multi-remote locality control failed to reproduce the adaptive roughness gain seen in the preceding single-remote experiment. That negative result changed more than one thing at once: it imposed a stricter geometry gate and then fitted controllers on the resulting theta cohort.

This experiment asks a narrower question: **does the stricter, outcome-free multi-remote geometry gate materially change the held-out value of the same `+0.5` remote roughness controller?**

The comparison is deliberately matched. One balanced raw theta panel, one set of development skies, one set of held-out skies, one field generator, one candidate-width set, and one controller class are shared by two nested cohorts:

- `SINGLE`: the `+0.5` remote context must be disjoint from local lesion support;
- `MULTI`: the `+0.25`, `+0.5`, and `+0.75` remote contexts must additionally be disjoint from local support and from one another.

The `MULTI` theta set is required in code to be a strict subset of `SINGLE`. Gates depend only on geometry. No sky outcome is inspected when deciding membership.

Within each development cohort, the same three-bin controller class is fitted and then frozen before held-out skies are generated. The predeclared primary contrast is, at the independent base-sky level,

`(MULTI remote+0.5 - MULTI fixed) - (SINGLE remote+0.5 - SINGLE fixed)`.

A negative value means that the stricter cohort makes the otherwise identical remote-controller protocol less useful relative to the frozen `w=0.5` baseline.

## Design

The run used:

- 60 raw balanced theta samples;
- 12 independent development base skies;
- 24 independent held-out base skies;
- metric spectra `k0 = {4, 8, 16}` nested within each base sky;
- candidate widths `{0.125, 0.25, 0.5, 1.0}`;
- fixed baseline `w = 0.5 × lesion radius`;
- independent base-sky seed as the inferential unit;
- four predeclared two-sided exact sign tests with Holm correction.

The `SINGLE` gate accepted **55/60** theta samples. The stricter `MULTI` gate accepted **45/60**, removing 10 samples that had passed `SINGLE`.

The removed samples are not a random-looking slice of the panel. Their median lesion radius was **0.10096**, versus **0.03001** in the retained `MULTI` cohort. Their mean radius was **0.10344**, versus **0.03445** retained. Six of the ten removed samples were discs, and five used the apodized occlusion family. This geometry imbalance is descriptive evidence about what the gate selected; it was not used to tune the controller.

## Development rules

On the broader `SINGLE` cohort, development selected:

- LOCAL: `[0.5, 0.5, 0.25]`;
- REMOTE `+0.5`: `[0.5, 0.5, 0.25]`.

On the stricter `MULTI` cohort, development selected:

- LOCAL: `[0.5, 0.5, 0.5]`;
- REMOTE `+0.5`: `[0.5, 0.5, 0.25]`;
- REMOTE-ENSEMBLE: `[0.5, 0.5, 0.25]`.

Thus the local controller again collapses to the fixed baseline after the stricter geometry restriction, while the `+0.5` remote controller retains the same nominal width pattern. The held-out result below therefore cannot be explained merely by a different vector of selected remote widths.

## Held-out result

### Primary cohort-shift discriminant

The primary paired contrast was negative in **24/24 held-out base skies**:

- mean shift: **-0.0058244**;
- median shift: **-0.0058229**;
- range: **[-0.0161769, -0.0001761]**;
- exact two-sided sign test: **p = 1.1921e-7**;
- Holm-adjusted: **p = 4.7684e-7**.

This is strong evidence that the stricter outcome-free geometry cohort materially changes the apparent usefulness of the learned `+0.5` remote roughness protocol under matched skies and a matched raw theta panel.

The broader `SINGLE` cohort reproduces a positive remote-controller advantage over fixed `w=0.5`:

- mean: **+0.0031383**;
- median: **+0.0035228**;
- 20 positive, 3 negative, 1 tie;
- exact sign test: **p = 0.0004883**;
- Holm-adjusted: **p = 0.0014648**.

The stricter `MULTI` cohort reverses that descriptive direction:

- mean: **-0.0026861**;
- median: **-0.0016339**;
- 6 positive, 17 negative, 1 tie;
- exact sign test: **p = 0.03469**;
- Holm-adjusted: **p = 0.06938**.

The remote ensemble remains unconvincing relative to fixed:

- mean: **-0.0010995**;
- median: **-0.0000033**;
- 10 positive, 12 negative, 2 ties;
- exact sign test: **p = 0.83181**;
- Holm-adjusted: **p = 0.83181**.

The primary result is therefore not merely another failed replication. It identifies the **geometry-defined theta cohort as a major sensitivity axis** of the roughness-to-width result.

## Spectrum-stratified diagnostic

The aggregate gate effect is not equally large at every spectrum:

- `k0=4`: median gate shift `-0.0000272`;
- `k0=8`: median gate shift `-0.0033355`;
- `k0=16`: median gate shift `-0.0046490`.

These strata are descriptive diagnostics, not additional confirmatory tests. They suggest that the cohort effect interacts with field scale, but this run does not establish the mechanism of that interaction.

## Evidence and hypothesis boundary

### Evidence from this run

1. With raw theta candidates and skies held fixed, the stricter multi-remote geometry gate changes the learned protocol's held-out behavior strongly and consistently.
2. The broad `SINGLE` cohort supports a positive remote-controller gain, while the nested `MULTI` cohort does not retain that gain after multiplicity correction.
3. The stricter gate preferentially removes large lesions in this realized panel; the median radius of removed theta samples is more than three times that of the retained cohort.
4. The fixed `w=0.5` baseline remains the safer default across the stricter cohort.

### Hypotheses not established

The most economical mechanistic hypothesis is now that lesion scale / geometry composition changes the roughness-to-useful-width relationship, with stronger sensitivity at shorter field correlation length. **That mechanism is not established here.** The gate changes both the development distribution on which the controller is fitted and the held-out theta mixture on which it is scored. This run therefore identifies full-protocol cohort sensitivity, not yet whether the causal contribution enters through controller fitting, evaluation composition, or both.

A clean next discriminant is a crossed analysis: fit the `SINGLE` and `MULTI` controllers separately in development, then evaluate both frozen rules on the common `MULTI` held-out rows. That isolates the training-cohort contribution; applying one frozen `SINGLE` rule to both held-out cohorts isolates the evaluation-cohort contribution.

Nothing in this experiment establishes a physical CMB scale, a Planck/ACT beam law, a real-sky anomaly, physical non-locality, or Pontifex/Torus causality.

## Data boundary

This is an internal synthetic calibration experiment. Its development and held-out sky seeds are disjoint, and all geometry gates, predictors, bins, candidate widths, and inferential contrasts are fixed without held-out outcomes.

The downstream partition remains strict and untouched:

`D_assembly ⟂ D_student ⟂ D_val ⟂ D_test`.

No assembly, student-training, validation, or test data enter this experiment.

## Reproducibility

Workflow run: https://github.com/franklinbaldo/papers/actions/runs/35431610022

Artifact: https://github.com/franklinbaldo/papers/actions/runs/35431610022/artifacts/10581043093

Script: `experiments/pontifex_torus/cmb_locality_cohort_shift_ablation.py`

Workflow: `.github/workflows/pontifex-cmb-locality-cohort-shift.yml`
