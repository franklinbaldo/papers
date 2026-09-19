---
type: Experiment Report
title: "Pontifex CMB: radius assignment frequency-matched permutation holdout"
date: 2026-09-19
status: experimental
---

# Pontifex CMB: radius assignment frequency-matched permutation holdout

## Question

The preceding radius-conditioned experiment established a reproducible held-out gain for a development-fitted radius-only beam policy: small and medium lesions used `w=0.5 × radius`, while large lesions used `w=0.25 × radius`. That result still admitted a simpler explanation: perhaps the gain came merely from using a useful **mixture** of widths, rather than from assigning those widths to lesions according to radius.

This experiment tests that ambiguity directly. The discriminant is:

> Does the frozen radius-to-width assignment outperform controllers with the **same width frequencies**, but with those widths reassigned to theta rows independently of radius?

A positive result supports predictive specificity of radius within the current synthetic harness. It does not establish a physical CMB scale or a Torus mechanism.

## Predeclared design and freeze order

The experiment uses a fresh balanced theta panel (`seed=20260926`) with 8 theta rows in every `geometry × occlusion` cell, for 120 theta rows total. Candidate beam widths remain `{0.125, 0.25, 0.5, 1.0} × radius`; the pre-existing fixed baseline remains `w=0.5`; metric-field conditions remain `k0 ∈ {4, 8, 16}`.

The order is strict:

1. generate the theta panel and freeze three radius bands, before any sky outcome;
2. generate 12 **development** base skies and fit one width per radius band;
3. freeze the resulting true radius-linked assignment;
4. freeze 255 unique non-identity placebo assignments **before any held-out sky is generated**;
5. only then generate 24 disjoint **held-out** base skies and score the frozen assignments.

Every placebo is formed by shuffling the true width labels **within each `geometry × occlusion` cell**. Therefore it preserves the exact width count in every such cell, not merely the global width histogram. What it destroys is the lesion-radius-to-width correspondence.

The independent inferential unit is the base-sky seed. `k0` conditions and theta rows are nested repeated measurements, not independent replicates.

## Development freeze

The pre-outcome radius cut points were:

- band 0 / small: `radius ≤ 0.0240612`;
- band 1 / medium: `0.0240612 < radius ≤ 0.0677110`;
- band 2 / large: `radius > 0.0677110`.

Development again selected:

| Radius band | Frozen width |
|---|---:|
| small | `0.5 × radius` |
| medium | `0.5 × radius` |
| large | `0.25 × radius` |

Thus the new panel independently recovered the same qualitative controller as the preceding experiment.

## Permutation integrity

All 255 requested placebo assignments were unique and non-identical to the true assignment. Each preserved the exact per-cell width counts. Relative to the true controller, a placebo changed a median **36.67%** of theta assignments (range **26.67–48.33%**).

The true assignment had Pearson correlation `radius ↔ selected_width = -0.8795`. Across the frequency-matched placebo assignments, that correlation had median `-0.1272`, range `[-0.3678, +0.1196]`. The null therefore breaks most of the radius-width coupling while retaining geometry, occlusion and width-frequency structure.

## Held-out result

The primary randomization statistic was the mean, across the 24 independent held-out base skies, of each sky's median leakage ratio.

| Controller / null | Held-out statistic |
|---|---:|
| true radius-linked assignment | **0.132454** |
| placebo randomization distribution, median | `0.123077` |
| placebo randomization distribution, maximum | `0.129967` |

None of the 255 pre-frozen frequency-matched placebo assignments reached the true statistic. With the standard +1 Monte Carlo correction, the one-sided randomization p-value is therefore **`1 / 256 = 0.00390625`**. This is also the resolution limit of the predeclared 255-placebo bank; no smaller p-value is claimed.

The planned base-sky sign contrasts tell the same story:

| Held-out contrast | Median difference | Wins / losses / ties | exact sign p | Holm p |
|---|---:|---:|---:|---:|
| true radius-linked − per-sky placebo-ensemble median | **+0.009154** | **24 / 0 / 0** | `1.19e-7` | `3.58e-7` |
| true radius-linked − fixed `w=0.5` | **+0.004408** | **24 / 0 / 0** | `1.19e-7` | `3.58e-7` |
| placebo-ensemble median − fixed `w=0.5` | **−0.004748** | **0 / 24 / 0** | `1.19e-7` | `3.58e-7` |

The last contrast is especially discriminating: merely preserving the same marginal mixture of `0.5` and `0.25` widths is not sufficient. When those widths are detached from radius, the median placebo controller is worse than the fixed `w=0.5` baseline on every held-out sky.

## Evidence boundary

### Supported by this experiment

Within the current synthetic CMB lesion harness, the held-out advantage of the radius policy depends on **which lesion radii receive which beam widths**, not merely on the marginal frequency of those widths. The result survives a null that exactly preserves the width mixture separately inside each geometry × occlusion cell.

This upgrades the previous result from “radius predicts a useful policy” to a narrower but stronger statement: **radius-to-width coupling has held-out predictive specificity in this synthetic measurement problem**.

### Still hypothesis

A natural mechanistic hypothesis is scale matching: the useful observation kernel may need to contract for sufficiently large lesions because boundary contamination and field structure change with lesion scale. This experiment does **not** identify that mechanism. Other radius-correlated geometric properties, the discrete candidate-width grid, the synthetic field family, or the leakage objective could generate the same controller.

A clean next discriminant would hold physical lesion size fixed while changing grid resolution / sampling density, or construct counterfactual theta pairs that match all available geometry descriptors except radius, then freeze the test before evaluating new skies.

### Not supported

Nothing here is evidence for a physical CMB scale, Planck/ACT behavior, cosmological anomaly, physical non-locality, or Torus causality. Those remain outside the evidential reach of this synthetic experiment.

## Data-separation contract

The production/research partitions remain strictly separate:

`D_assembly ⟂ D_student ⟂ D_val ⟂ D_test`.

No row from any of those partitions enters this experiment. The present study has its own synthetic split, with disjoint base-sky seeds:

`S_development ∩ S_heldout = ∅`.

The radius bands are frozen before sky outcomes; the radius policy is learned only from `S_development`; all 255 placebo assignments are frozen before generation of `S_heldout`; no held-out outcome chooses a band edge, candidate width, controller or permutation.

## Reproduction

```bash
uv run experiments/pontifex_torus/cmb_radius_assignment_permutation_holdout.py \
  --dev-skies 12 \
  --heldout-skies 24 \
  --theta-per-cell 8 \
  --radius-bands 3 \
  --permutations 255 \
  --beam-width-ratios 0.125 0.25 0.5 1.0 \
  --baseline-width 0.5 \
  --metric-k0 4 8 16 \
  --ny 64 --nx 128 \
  --seed 20260926
```

Confirmatory GitHub Actions run: https://github.com/franklinbaldo/papers/actions/runs/35439687865

Artifact (summary JSON + complete development/held-out row table): https://github.com/franklinbaldo/papers/actions/runs/35439687865/artifacts/10583347795
