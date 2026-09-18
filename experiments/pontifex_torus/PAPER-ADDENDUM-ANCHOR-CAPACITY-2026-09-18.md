---
type: "Interpretability Paper"
title: "Pontifex Torus Addendum: Anchor Capacity at Scale"
description: "A fixed-2,000-text capacity sweep tests whether the scale degradation of regional Torus backprojection is explained by too few semantic anchors."
tags: [pontifex, torus, capacity, scaling, anchors, latent-space]
timestamp: 2026-09-18T03:20:00-04:00
---

# Pontifex Torus Addendum: Anchor Capacity at Scale

**Franklin Baldo**  
Independent Researcher

## Question

The first corpus-size ladder showed that the regional Torus backprojection lost
neighbor preservation as the synthetic corpus grew while the decoder remained fixed
at 16 B-side anchors. That left an important ambiguity: was the adverse scaling
mostly a trivial capacity bottleneck in the regional decoder, or did it expose a
more structural limitation of the current representation?

This addendum tests the narrow hypothesis:

> **If fixed regional capacity is the principal cause of scale degradation, then
> increasing the number of B-side anchors at fixed corpus size should substantially
> restore held-out neighborhood preservation.**

The experiment is deliberately restricted to the existing synthetic cartography
corpus. It does not use, tune on, or reveal any future `D_assembly`, `D_student`,
`D_val`, or `D_test` partition intended for the multi-teacher downstream benchmark.

## Protocol

The corpus is fixed at 2,000 synthetic texts. For every condition:

- the same one-lens (`size=1`) response field is reused;
- the same ten seeds are used;
- train/test splitting remains 70/30;
- inference receives exactly `K=8` held-out A-side real probes;
- virtual integration is fixed at `M=128`;
- the Fourier source representation uses 8 harmonics and a 512-point dense training grid;
- only the number of B-side regional anchors changes.

The anchor sweep is

\[
A\in\{8,16,32,64,128,256\}.
\]

The matched direct Fourier Ridge baseline sees the same reconstructed source
features and is unaffected by anchor count. It remains the control for whether the
regional factorization itself is useful.

## Result: anchor count is a bottleneck, but not the whole bottleneck

| B-side anchors | cosine to B | normalized RMSE | retrieval top-1 | neighbor overlap |
|---:|---:|---:|---:|---:|
| 8 | 0.77666 | 0.03411 | 0.00283 | 0.11411 |
| 16 | 0.79111 | 0.03298 | 0.00217 | 0.13148 |
| 32 | 0.79616 | 0.03258 | 0.00217 | 0.13703 |
| 64 | 0.79863 | 0.03239 | 0.00183 | 0.13561 |
| 128 | 0.79903 | 0.03235 | 0.00200 | 0.13689 |
| 256 | **0.80145** | **0.03216** | 0.00267 | **0.13879** |
| matched direct Fourier Ridge | **0.84743** | **0.02819** | **0.06983** | **0.15392** |

The first conclusion is positive but limited. Increasing regional capacity clearly
helps: neighbor overlap rises by about 21.6% from 8 to 256 anchors, and coordinate
fidelity improves steadily. The 16-anchor setting used in the earlier scale ladder
was therefore genuinely capacity constrained.

The stronger hypothesis, however, is not supported. Most of the relational gain is
already obtained by approximately 32 anchors. From 32 through 256 anchors,
neighbor overlap fluctuates in a narrow band and ends at only `0.13879`, still below
the matched direct Ridge control at `0.15392`. Exact retrieval remains near chance
for the regional decoder while the direct baseline reaches `0.06983` top-1.

Thus simply adding more anchors does **not** recover the small-corpus relational
result or close the coordinate gap. Fixed anchor count is a contributing bottleneck,
not a sufficient explanation of scale degradation.

## Chance-corrected neighborhood preservation

Raw neighbor-overlap scores shrink mechanically when the held-out candidate set
grows. To avoid mistaking this candidate-set effect for semantic degradation, we
also compute the expected Jaccard overlap of two independent random `k=5`
neighborhoods.

For a held-out set of size `n`, let the intersection size be

\[
I\sim\operatorname{Hypergeom}(N=n-1,K=5,n=5).
\]

The random baseline is

\[
J_{chance}
=
\mathbb E\left[\frac{I}{10-I}\right],
\]

and a chance-adjusted score is

\[
J_{adj}
=
\frac{J-J_{chance}}{1-J_{chance}}.
\]

At 2,000 total texts the held-out set has 600 texts and
`J_chance = 0.004653`. The capacity sweep becomes:

| anchors | raw overlap | chance-adjusted overlap |
|---:|---:|---:|
| 8 | 0.11411 | 0.10997 |
| 16 | 0.13148 | 0.12742 |
| 32 | 0.13703 | 0.13300 |
| 64 | 0.13561 | 0.13157 |
| 128 | 0.13689 | 0.13285 |
| 256 | **0.13879** | **0.13476** |
| direct Ridge | **0.15392** | **0.14997** |

The plateau therefore survives chance correction.

The same correction also shows that the earlier corpus-size decline was not merely a
larger-candidate artifact. With 16 anchors:

| total texts | held-out texts | Torus raw overlap | Torus adjusted | direct Ridge adjusted |
|---:|---:|---:|---:|---:|
| 120 | 36 | 0.3539 | 0.2945 | 0.3038 |
| 500 | 150 | 0.1855 | 0.1698 | 0.1871 |
| 1,000 | 300 | 0.1558 | 0.1478 | 0.1686 |
| 2,000 | 600 | 0.1315 | 0.1274 | 0.1500 |

Even after accounting for the expected random overlap, the current regional
backprojection loses relational quality as corpus diversity grows.

## Interpretation

This discriminates between two explanations that were previously confounded.

1. **Supported:** a fixed small anchor set limits the decoder. Moving from 8 to 32+
   anchors improves both cosine fidelity and semantic-neighborhood preservation.
2. **Rejected as sufficient:** anchor count alone does not explain the scaling
   failure. Beyond about 32 anchors, returns are small and the direct Fourier Ridge
   control remains better.

The next target should therefore be the **regional decoding rule**, not another blind
increase in anchor count. Plausible controls include hierarchical or multiresolution
regions, sparse/top-k mixtures, learned prototype geometry, calibrated mixture
temperature, or a decoder that preserves pairwise neighborhood constraints directly.
Any such choice must be selected only on cartography/validation data and frozen
before the future external benchmark.

This result also strengthens the motivation for the proposed multi-teacher Assembly:
if an Assembly is built, its representational capacity cannot be equated with a
small fixed set of barycentric anchors. Capacity must be allowed to grow or become
hierarchical with semantic diversity.

## Evidence boundary

This experiment establishes only a capacity property of the current synthetic,
pairwise MiniLM-to-BGE regional backprojection.

It does **not** establish:

- that a scalable multi-teacher Torus Assembly exists;
- that teacher order becomes irrelevant;
- that a held-out teacher can be predicted;
- that a sparse student can enter a frozen Assembly;
- tokenizer-free byte-level inference;
- long-context retrieval at fixed probe budget;
- superiority on an external downstream benchmark.

Those remain hypotheses for separate, disjoint-data experiments.

## Reproducibility

Workflow:

`https://github.com/franklinbaldo/papers/actions/runs/35318379408`

Implementation uses the existing
`experiments/pontifex_torus/virtual_resolution.py` with a dedicated matrix workflow:

`.github/workflows/pontifex-anchor-capacity.yml`
