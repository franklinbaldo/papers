---
type: Experiment Report
title: "Pontifex CMB: beam scale survives held-out skies"
date: 2026-09-19
status: experimental
---

# Pontifex CMB: beam scale survives held-out skies

## Why this experiment was necessary

The metric-aware beam ladder produced a striking scale-response curve: the nonlocal leakage ratio rose from the local limit, peaked near a beam width of one half lesion radius, and then fell. But that peak was discovered and inspected on the same six synthetic skies. It was therefore evidence for a candidate scale, not yet evidence that the scale preference generalizes.

This addendum closes that adaptivity loop with a development/held-out design.

## Frozen protocol

The theta panel is fixed first: 45 interventions per sky, balanced across the five occlusion families and three geometries. Candidate beam widths are fixed at `0.125, 0.25, 0.5, 1.0` times the lesion radius.

Six **development** skies are used for one decision only: choose the width that maximizes

`median across development skies(per-sky median leakage ratio)`.

Ties are resolved toward the smaller width. No matched-null result enters this selection.

Only after the width is frozen are twelve disjoint **held-out** sky seeds generated. The held-out stage then compares the frozen width with every alternative at the **sky level**, using paired leakage differences. Exact two-sided sign tests are Holm-adjusted across the three planned contrasts.

Matched-null calibration on held-out data is computed only for the already-frozen width. It cannot change the selected width.

## Development result

The development selection scores were:

| width / lesion radius | development score |
|---:|---:|
| 0.125 | 0.03909 |
| 0.25 | 0.10150 |
| **0.5** | **0.12806** |
| 1.0 | 0.07914 |

The frozen width was therefore **0.5 lesion radius**.

## Held-out result

The result replicated cleanly.

The frozen width `0.5` produced the largest per-sky median leakage in **12/12 held-out skies**. No held-out sky preferred `0.125`, `0.25`, or `1.0`.

Paired sky-level differences were all positive against every planned alternative:

| contrast | median leakage advantage of width 0.5 | skies with 0.5 greater | exact sign p | Holm-adjusted p |
|---|---:|---:|---:|---:|
| 0.5 vs 0.125 | +0.09202 | 12/12 | 0.000488 | 0.001465 |
| 0.5 vs 0.25 | +0.02516 | 12/12 | 0.000488 | 0.001465 |
| 0.5 vs 1.0 | +0.03788 | 12/12 | 0.000488 | 0.001465 |

This is stronger evidence than the original ladder that the synthetic nonlocal observation operator has a reproducible **intermediate scale optimum** rather than a monotonic blur effect or an accident of six inspected skies.

## Does the held-out channel remain distinct from the core?

Yes, but not independent.

At the frozen width, raw core-vs-boundary Pearson correlation across theta had a held-out sky median of **0.8047**. The matched-null rank-p correlation had median **0.6774**. Median absolute rank-p gap across skies was **0.0909**, and the median 5% decision disagreement was **2.22%**.

Thus the nonlocal response remains strongly coupled to core amplitude while retaining calibration information that is not a simple positive rescaling of the core channel.

There were **zero zero-variance calibration rows** in the held-out stage.

## Important statistical boundary

The primary scale-replication result does not depend on the 32-null rank resolution: scale selection and held-out confirmation use the observed leakage ratio summarized at the independent-sky level.

The matched-null rank summaries are secondary diagnostics. With 32 nulls, rank resolution is `1/33 ~= 0.0303`, so they are suitable for the 5% smoke comparison used here but not for strong tail claims.

The twelve held-out skies are the replication units. The 45 theta rows inside each sky are dependent because they share the field; they are never treated as 540 independent population replicates.

## Evidence versus hypothesis

### Evidence from this experiment

Under the current synthetic map generator, intervention family panel, metric-aware Gaussian observation operator, and fixed candidate width grid:

- development selects width `0.5`;
- that frozen width is the leakage maximum in 12/12 unseen synthetic skies;
- its sky-level leakage advantage is positive against every alternative in all twelve paired comparisons;
- the nonlocal channel remains measurably different from core calibration while still strongly correlated with it.

### Hypotheses still open

A reproducible synthetic intermediate scale may justify a multiscale observation model and motivates asking what mechanism determines that scale. Candidate explanations include the geometry of the core/boundary construction, the Gaussian observation kernel, and the spectrum of the synthetic field.

Those are hypotheses, not conclusions of this run.

### Not established

This experiment does **not** establish:

- that `0.5 radius` is a physical scale in the CMB;
- that the Gaussian beam represents Planck or ACT instrumentation;
- a CMB anomaly;
- physical nonlocality;
- topology or Torus causality;
- any gain in Assembly/student learning.

The strict data boundary remains unchanged:

`D_assembly ⟂ D_student ⟂ D_val ⟂ D_test`.

None of those datasets enters this experiment.

## Next discriminant

The strongest next test is to ask whether the `0.5` optimum is controlled by **field correlation length** rather than by the lesion geometry itself. Keep the development-selected width frozen, vary only the synthetic field spectrum/correlation length on new skies, and express the observed optimum simultaneously in units of lesion radius and field correlation length. If the optimum tracks the field spectrum, the effect belongs primarily to the observation-field interaction; if it stays near a fixed fraction of lesion radius, the geometric interpretation becomes substantially stronger.
