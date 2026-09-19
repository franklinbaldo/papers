---
type: Experiment Report
title: "Pontifex CMB: outcome-free radius-matched locality control"
date: 2026-09-19
status: experimental
---

# Pontifex CMB: outcome-free radius-matched locality control

## Question

The preceding nested-cohort ablation found a large change in held-out controller gain when the theta panel was restricted from the `SINGLE` geometry gate to the stricter `MULTI` gate. The same run also showed that the stricter gate preferentially removed large lesions.

A direct radius-matched reanalysis of that 60-theta panel is not identifiable: the saved artifact shows **zero lesion-radius common support** between the 10 `SINGLE`-only rows and the 45 `MULTI`-retained rows. The largest retained lesion had radius `0.07587`, while the smallest `SINGLE`-only lesion had radius `0.07911`. In that panel, every row removed only by the multi-remote gate was larger than every retained row.

This follow-up therefore changes the design before generating outcomes. It asks: **when common support is created with a denser pre-outcome theta panel, and `SINGLE`-only lesions are matched to `MULTI`-retained lesions on geometry, occlusion, radius and aspect, does the gate-associated controller-gain difference persist on new held-out skies?**

## Pre-outcome design

The experiment generated a new balanced panel of **600 theta samples** (`40` per geometry × occlusion cell), then applied the same outcome-free geometry rules:

- `SINGLE`: the `+0.5` remote context must be disjoint from local lesion support;
- `MULTI`: the `+0.25`, `+0.5`, and `+0.75` remote contexts must additionally be disjoint from local support and from one another.

`SINGLE` accepted **534/600** samples. `MULTI` accepted **395/600**, leaving **139 `SINGLE`-only** candidates. Unlike the sparse earlier panel, the dense panel has radius overlap: `SINGLE`-only radii span `0.05984–0.19959`, while `MULTI`-retained radii span `0.00800–0.11734`.

Before any sky outcome was generated, one-to-one matching without replacement was performed by Hungarian assignment. Matching was exact within `geometry × occlusion`; the predeclared cost was

`|Δ log(radius)| + 0.25 |Δ log(aspect)|`,

with calipers `|Δ log(radius)| ≤ 0.10` and `|Δ log(aspect)| ≤ 0.70`.

This produced **17 matched pairs / 34 theta samples**. Radius balance was tight by construction: median absolute log-radius difference `0.05021`, maximum `0.09534`; the median ratio `radius_SINGLE-only / radius_MULTI-retained` was `1.0441`. The matched set contained 13 ellipse, 3 annulus and 1 disc pairs. That composition is an important limitation: this experiment identifies the effect only on the geometry/scale region where outcome-free overlap and matching were possible.

## Development / held-out separation

Only after matching was frozen were **12 development base skies** generated. One shared three-bin `+0.5` remote-roughness controller was fitted on the union of both matched groups, so controller fitting itself cannot differ between `SINGLE`-only and `MULTI`-retained rows.

The learned bin edges were `0.80670` and `1.31583` in log roughness. More importantly, development selected the same width in every bin:

`[0.25, 0.25, 0.25]`.

Thus, inside the matched common-support region, remote roughness did **not** induce an adaptive width rule at all. It collapsed to the fixed width `w=0.25`. This fact was fixed before held-out skies were generated.

Only then were **24 disjoint held-out base skies** generated. Spectral conditions `k0={4,8,16}` are nested repeated measurements inside each sky; the independent inferential unit remains the base-sky seed.

The predeclared primary statistic is the sky-level median paired difference

`gain_SINGLE-only - gain_MULTI-retained`,

where `gain = leakage(controller width) - leakage(fixed w=0.5)`. Three exact two-sided sign tests were Holm-adjusted: the matched primary contrast and each matched group versus the frozen `w=0.5` baseline.

## Held-out result

The dramatic cohort penalty from the previous experiment **did not survive radius/shape matching with a shared controller**.

For the primary matched contrast:

- median `SINGLE-only - MULTI-retained`: **-0.001967**;
- mean: **-0.001205**;
- range: **[-0.009990, +0.009854]**;
- 11 positive, 13 negative, 0 ties across 24 held-out skies;
- exact two-sided sign test: **p = 0.83882**;
- Holm-adjusted: **p = 1.0**.

Neither matched group showed a reliable advantage of the development-selected `w=0.25` over the pre-existing `w=0.5` baseline:

- `SINGLE`-only vs fixed: median **-0.000373**, 11/24 positive, `p=0.83882`, Holm `p=1.0`;
- `MULTI`-retained vs fixed: median **+0.002380**, 15/24 positive, `p=0.30746`, Holm `p=0.92237`.

Descriptively, the matched difference remained small and negative in all three spectral conditions (`k0=4`: median `-0.001395`; `k0=8`: `-0.002163`; `k0=16`: `-0.000264`), but those row-level spectrum summaries are diagnostics, not independent confirmatory tests.

## What changed scientifically

The previous 24/24 negative gate-shift result is real for its realized nested cohorts, but the new experiment shows that it should **not** be interpreted as evidence that `MULTI` gate membership itself carries a stable residual response law. On the earlier sparse panel, gate membership and lesion radius were effectively separated with no common support. Once a denser panel supplies overlap and the two groups are matched on lesion scale/shape within exact geometry and occlusion strata, the large held-out difference disappears.

The second negative result matters just as much: the remote-roughness controller itself collapses to `[0.25,0.25,0.25]` in the matched region. Therefore the earlier roughness-to-width adaptivity is also not demonstrated to be invariant to the lesion-scale cohort. The safer interpretation is that **cohort geometry/scale is a major source of the earlier apparent controller effect**.

## Evidence and hypothesis boundary

### Evidence from this run

1. The original 60-theta cohort-shift panel had no lesion-radius common support between `SINGLE`-only and `MULTI`-retained rows, so a clean radius-matched causal reading of that comparison was impossible.
2. A new denser, outcome-free panel yielded 17 exact-stratum radius/aspect-matched pairs before any sky outcomes existed.
3. With one shared development-fitted controller and 24 new held-out skies, the prior large gate-associated gain difference was not reproduced (`Holm p=1.0`).
4. Within the matched support, development selected `w=0.25` in all roughness bins; the predictor did not generate an adaptive control law.
5. Neither matched group reliably beat the frozen `w=0.5` baseline after multiplicity correction.

### Hypotheses not established

A parsimonious hypothesis is that the previous gate penalty was largely a lesion-scale / cohort-composition phenomenon produced by the geometry of the multi-remote exclusion rule, rather than a distinct remote-field mechanism. This run **supports that interpretation by falsification pressure**, but does not prove it: matching is limited to 17 pairs, is concentrated in ellipses, and does not match every latent geometric coordinate such as center or phase.

It is also possible that a genuine roughness interaction exists only outside the matched common-support region. That would be a different, explicitly scale-conditional hypothesis and would require a separately predeclared experiment rather than rescuing the current controller post hoc.

Nothing here establishes a physical CMB scale, a Planck/ACT beam law, a real-sky anomaly, lesion-local information, physical non-locality, or Pontifex/Torus causality.

## Data boundary

Matching uses theta geometry only and is frozen before sky generation. Development and held-out base-sky seeds are disjoint. Held-out outcomes choose neither pairs, bin edges nor widths.

The downstream partition remains strict and untouched:

`D_assembly ⟂ D_student ⟂ D_val ⟂ D_test`.

No assembly, student-training, validation, or test data enter this synthetic experiment.

## Reproducibility

Workflow run: https://github.com/franklinbaldo/papers/actions/runs/35434197777

Artifact: https://github.com/franklinbaldo/papers/actions/runs/35434197777/artifacts/10582052502

Script: `experiments/pontifex_torus/cmb_locality_radius_matched.py`

Workflow: `.github/workflows/pontifex-cmb-locality-radius-matched.yml`
