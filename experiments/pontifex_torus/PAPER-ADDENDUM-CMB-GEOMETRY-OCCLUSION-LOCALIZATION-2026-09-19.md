---
type: Experiment Report
title: "Pontifex CMB: geometry x occlusion localization"
date: 2026-09-19
status: experimental
---

# Pontifex CMB: geometry x occlusion localization

## Question

The previous fixed-theta family analysis found that the residual predictive-Student-t versus exact-rank mismatch at the 1% tail did **not** concentrate in one occlusion family. The next discriminant is narrower: **does the mismatch recur in a particular geometry x occlusion interaction?**

This matters because a stable cell-specific effect would motivate a mechanistic follow-up, whereas sparse one-sky discrepancies would argue against a reproducible intervention-family explanation.

## Design

The analysis reuses the already-run artifact from the fixed balanced panel rather than generating new theta values. That artifact contains **12 independently generated synthetic skies**, five occlusion families, three geometries, and four fixed theta replicates per geometry x occlusion cell: **720 rows total**, 48 per cell.

For each row the stored 128 matched-null scores are recalibrated using both:

- predictive Student-t;
- symmetric leave-one-out exact-rank calibration.

The target is the 1% tail, where `m=128` gives exact-rank resolution `1/129 ~= 0.00775`. The independent replication unit remains the sky; theta rows within a sky share the field and null-map bank.

## Result

Globally, the reanalysis reproduces the preceding run:

- predictive Student-t rejection at 1%: **1.5278%**;
- exact-rank rejection at 1%: **0.9722%**;
- decision disagreement: **0.8333%**.

The geometry x occlusion decomposition is mostly null. Of the **15 balanced cells**, only **6** show any signed predictive-minus-rank difference at all, and in every affected cell that difference occurs in only **1 of the 12 independent skies**. The other 11 skies in each affected cell have zero difference.

The nonzero cells are:

| geometry x occlusion | predictive <=1% | rank <=1% | signed gap | skies with positive / zero / negative gap |
|---|---:|---:|---:|---:|
| annulus x adjacency_phase | 4.17% | 2.08% | +2.08 pp | 1 / 11 / 0 |
| annulus x residual_permute | 2.08% | 0% | +2.08 pp | 1 / 11 / 0 |
| disc x apodized | 2.08% | 0% | +2.08 pp | 1 / 11 / 0 |
| disc x hard | 0% | 2.08% | -2.08 pp | 0 / 11 / 1 |
| disc x residual_permute | 2.08% | 0% | +2.08 pp | 1 / 11 / 0 |
| ellipse x apodized | 2.08% | 0% | +2.08 pp | 1 / 11 / 0 |

The remaining **9/15 cells have exactly zero predictive-minus-rank tail difference across all 12 skies**.

The sign reversal in `disc x hard` is useful negative evidence: the residual is not merely a universal one-sided permissiveness of predictive Student-t inside every cell.

## Evidence

This decomposition provides evidence **against a stable geometry x occlusion mechanism** for the residual 1% mismatch in the current synthetic harness. The discrepancies are sparse across cells and, more importantly, fail to recur across independently generated skies within any affected cell.

That result narrows the live explanation. A persistent mismatch, if real, is more plausibly associated with the scalar score functional, the matched-null construction, or higher-order interactions not captured by the coarse geometry x occlusion labels than with one fixed intervention cell.

## Hypothesis, not evidence

The component-level hypothesis remains open: `core_rmse`, `boundary_shift`, or `sqrt(global_energy)` may have different null shapes whose weighted combination produces the residual scalar-score mismatch. A dedicated component-attribution experiment has therefore been added, but its result must be treated separately from this completed geometry x occlusion analysis.

No claim is made here that any component is causal before that experiment is observed.

## Scope boundary

This is a synthetic calibration result only. It is **not** evidence of:

- a real CMB anomaly;
- physical topology;
- Torus causality;
- validity of phase-scrambled nulls for Planck/ACT production inference;
- downstream Assembly or student benefit.

The strict data separation remains unchanged:

`D_assembly ⟂ D_student ⟂ D_val ⟂ D_test`.

No Assembly, student, validation, or test data are used in this experiment.

## Reproducibility

The second-stage analysis is implemented in `cmb_null_geometry_occlusion_localization.py` and is now chained directly after `cmb_null_family_localization.py` in the same workflow, so future family-localization runs produce the interaction decomposition from exactly the same persisted score vectors.

The completed source artifact for this analysis came from GitHub Actions run `35401032175` (`pontifex-cmb-null-family-localization`).

## Next discriminant

Decompose the same fixed balanced panel by the actual score components (`core_rmse`, `boundary_shift`, and `sqrt_global_energy`) while preserving the 128 individual matched-null values. If one component shows a recurrent sky-blocked tail gap while the others do not, that would localize the calibration mismatch mechanistically. If all components remain sparse across skies, the residual should be treated as a small finite-sample calibration effect rather than evidence for a stable score-law pathology.
