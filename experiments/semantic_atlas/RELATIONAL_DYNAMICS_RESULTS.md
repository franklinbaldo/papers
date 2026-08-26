---
type: "Findings Record"
title: "Semantic Atlas relational dynamics v1 — outcome and robustness correction"
description: "Outcome record for the preregistered frozen-encoder corpus-flow pilot, corrected by a post-hoc 10,000-permutation power and representational-similarity analysis: chronology is non-exchangeable; chronology-specific excess divergence is unresolved because v1 was underpowered; cross-model local neighborhood structure differs materially while remaining strongly above chance."
tags: [semantic-atlas, findings, dynamics, embeddings, mknn, power, preregistration]
timestamp: 2026-08-26T05:58:00Z
---

# Semantic Atlas relational dynamics v1 — outcome and robustness correction

## Scope

This record has two deliberately separate layers.

1. **Frozen v1 result.** The protocol, statistic, 128-permutation null and decision
   rule were fixed before execution in PR #380. Those facts are preserved.
2. **Post-hoc robustness correction.** After inspecting the v1 result, we expanded
   the null to 10,000 permutations, estimated minimum detectable effect and power,
   added a same-observer estimator-stability reference, calibrated the observed
   neighborhood overlap against the representational-similarity permutation null,
   and replaced naive resolution medians with Kaplan–Meier summaries.

The second layer may narrow or qualify the interpretation of v1. It may **not**
retroactively turn a preregistered negative/non-significant test into confirmation.
The complete post-hoc output is versioned at
`artifacts/relational_dynamics_v1_reanalysis.json` and reproduced by
`scripts/run_relational_dynamics_reanalysis.py`.

The encoders remain frozen throughout. Individual document vectors do not move.
The replayed object is corpus-induced relational structure as the same final
116-document repository sample is exposed in first-Git-touch order.

## Frozen v1 classification

Under the preregistered 128-permutation decision rule, the experiment classified
as:

**`dynamic-transfer-not-rejected`**.

That label is retained as provenance, but its scientific interpretation is
narrower than the original Findings Record stated.

The order-null test does **not** ask whether the two observers possess different
relational dynamics in an absolute sense. The null keeps both final geometries
fixed and applies the same arbitrary insertion order to both observers. It asks:

> Does repository chronology create **excess cross-observer churn divergence**
> beyond the divergence already produced by arbitrary insertion orders on these
> two fixed geometries?

That is the claim evaluated below.

## 10,000-permutation refinement

The original 128 permutations put the semantic-drift statistic at the resolution
floor. Re-running the already-frozen geometries with 10,000 shared permutations
changes no corpus, embedding or statistic and gives finer measurement.

### Repository-order non-exchangeability

- chronological semantic-drift score: **0.149835**;
- 10k null mean: **0.111801**;
- 10k null 95th percentile: **0.119808**;
- largest of 10,000 null draws: **0.132509**;
- plus-one `p_upper = 0.000100`.

The repository first-touch order is therefore detectably non-exchangeable in
semantic content. This remains a statement about the growth history of this
small research repository, not about generic or natural corpus growth.

### Chronology-specific excess divergence

For the preregistered primary `k=5`:

- observed `D`: **0.357006**;
- 10k order-null mean: **0.333845**;
- excess over null mean: **0.023162**, or **6.94%**;
- null 95th percentile: **0.423977**;
- `p_upper = 0.323568`.

Sensitivity checks remain non-significant:

| k | observed D | 10k null mean | p_upper |
|---:|---:|---:|---:|
| 3 | 0.262649 | 0.371680 | 0.971503 |
| 5 | 0.357006 | 0.333845 | 0.323568 |
| 10 | 0.328090 | 0.291259 | 0.205379 |

Therefore there is still no evidence that **this repository chronology amplifies
cross-observer churn divergence above the arbitrary-order baseline**.

## Power correction: the v1 negative is weak

Non-significance is not enough to call the effect absent. Using the 10,000-draw
`k=5` null as the fixed-geometry sampling distribution, we evaluated an explicit
additive location-shift alternative.

At `alpha=0.05`, the 80%-power minimum detectable excess is:

- absolute MDE in `D`: **0.135793**;
- MDE relative to the null mean: **40.68%**.

The observed excess is only **0.023162 / 6.94%**. Under that location-shift model,
the estimated power for an effect of the observed size is only **10.54%**.

This changes the scientific wording materially. The correct conclusion is **not**
"model-specific corpus-flow dynamics were falsified." It is:

> **Chronology-specific excess cross-observer divergence was not detected, and
> v1 was severely underpowered to detect an excess of the observed magnitude.**

A larger corpus is required before a tight negative conclusion is available.

## Same-observer estimator-stability reference

The cached embedding models are deterministic, so a literal "different encoder
seed" null would be degenerate: same model + same documents + same inference
procedure gives the same vectors and neighborhood graph. We therefore do not
invent stochastic encoder variability.

Instead, the post-hoc reference uses independent Poisson(1) bootstrap weights on
document **anchors**. Candidate geometry, candidate availability and insertion
order stay unchanged; only which currently present anchors estimate the mean
hazard is perturbed. This measures finite-anchor estimator instability, not model
seed variability.

Under the real chronology (`k=5`, 10,000 bootstrap pairs):

| observer | same-observer D mean | q95 | q99 | fraction >= cross-model D=0.357006 |
|---|---:|---:|---:|---:|
| Qwen | 0.194990 | 0.266379 | 0.307939 | 0.0012 |
| MiniLM | 0.209228 | 0.281400 | 0.319780 | 0.0013 |

Under arbitrary orders, the same-observer bootstrap means are approximately
**0.232** (Qwen) and **0.229** (MiniLM), while the cross-model arbitrary-order
baseline is **0.333845**.

This does not create a formal encoder-seed test. It does answer the narrower
question that motivated the check: the large `~0.33` arbitrary-order
cross-observer divergence is not well explained by finite-anchor averaging noise
alone. A material component belongs to the difference between the two frozen
relational geometries.

## Positive static result: mutual kNN alignment is partial, not absent

The previously reported `kNN@5` set overlap is the standard **mutual k-nearest
neighbor / mutual kNN (mKNN)** representational-similarity statistic used in the
recent representational-convergence literature. For shared sample identities,

`mKNN_k = mean_i |N_k^A(i) ∩ N_k^B(i)| / k`.

The final native Qwen/MiniLM gallery gives:

- paired canonical cosine after the existing atlas alignment: **0.756507**;
- native **mKNN@5 = 0.467241**.

The full 116-document gallery curve is:

| k | mKNN |
|---:|---:|
| 1 | 0.456897 |
| 2 | 0.478448 |
| 3 | 0.488506 |
| 5 | 0.467241 |
| 8 | 0.468750 |
| 10 | 0.487069 |
| 15 | 0.526437 |
| 20 | 0.562931 |
| 30 | 0.615230 |
| 40 | 0.642672 |
| 50 | 0.684483 |

Following the permutation-calibration framework used by Gröger, Wen and Brbić,
we break sample correspondence while preserving each representation's internal
geometry. At `k=5`, with 10,000 permutations:

- observed mKNN: **0.467241**;
- permutation-null mean: **0.043611** (close to the analytic `k/(n-1)` null);
- 95% critical value `tau`: **0.060345**;
- plus-one `p = 0.000100`;
- max-preserving calibrated mKNN: **0.433028**.

Thus the two observers share substantially more local neighborhood structure than
chance, while still disagreeing on more than half of the five-neighbor identities
on average. That is the cleanest positive fact in v1.

It should be described as **partial local alignment with substantial discrete
relational disagreement**, not as weak representations and not yet as a universal
counterexample to local-convergence results.

## Gallery-size limitation

The local-alignment literature now makes the gallery-size dependence impossible
to ignore. Huh et al. (2024) popularized mutual kNN as evidence for
representational convergence. Gröger, Wen and Brbić (2026) report that after
permutation calibration local-neighborhood agreement survives more reliably than
global spectral convergence on their evaluated model panel. Koepke et al. (2026),
however, show that mutual-kNN agreement can change substantially as the gallery
is scaled from small evaluation sets to millions of examples.

This v1 gallery has only **116 documents**, smaller even than the ~1k small-gallery
regime criticized in that work. Therefore `0.467241` is a pilot point, not a
scale-stable quantity.

The next empirical stage must report **mKNN as a joint function of gallery size N
and neighborhood size k** on a much larger timestamped corpus. No claim that
Qwen/MiniLM violate an emerging local-convergence hypothesis is allowed unless the
cross-model disagreement survives that curve.

## Resolution with censoring handled correctly

The original report compared raw time-to-first-churn medians despite asymmetric
censoring. The post-hoc correction uses Kaplan–Meier survival over the 24 initial
anchors.

For Qwen:

- 14 events, 10 censored (**41.67%**);
- KM survival: `S(4)=0.75`, `S(12)=0.542`, `S(24)=0.50`, `S(72)=0.417`;
- KM median time to first churn: **24 added documents**.

For MiniLM:

- 24 events, no censoring;
- `S(4)=0.25`, `S(8)=0.167`, `S(12)=0.0417`, `S(16)=0`;
- KM median: **4 added documents**.

This supports a real descriptive difference in local relational stability between
the observers, but the 24-anchor sample is too small for a general law.

## What v1 now supports

The evidence layer after the robustness correction is:

1. **Repository-order non-exchangeability: strong.** First-touch chronology is
   semantically non-exchangeable relative to arbitrary insertion.
2. **Partial cross-model local alignment: strong relative to chance.** mKNN is
   far above a correspondence-permutation null for every reported `k`.
3. **Substantial discrete relational disagreement: observed.** At `k=5`, only
   46.7% of neighbor identities overlap despite reasonably aligned canonical
   coordinates.
4. **Different local stability profiles: observed.** Kaplan–Meier churn survival
   differs sharply between Qwen and MiniLM in this pilot.
5. **Chronology-specific amplification: unresolved.** It is not significant, but
   v1 had only ~10.5% estimated power for an excess as small as the observed one.

The compact headline is therefore:

> **shared-ish aligned coordinates, partial-but-significant local neighborhood
> agreement, substantial observer-specific discrete structure; no detected
> chronology-specific excess flow in an underpowered 116-document pilot.**

## Consequence for the roadmap

1. Preserve PR #380 as the frozen pilot; do not rewrite its protocol after seeing
   the outcome.
2. Treat this robustness record as a correction to the interpretation, not a
   second confirmatory experiment.
3. Reframe PR #379 around the positive relational observation first, while making
   the `N=116` gallery-size limitation explicit.
4. Before fitting `arrival × gap`, move to a large timestamped corpus. Explore the
   mechanism there, then freeze it and confirm on held-out time/corpus data.
5. The large-corpus run must include `mKNN(N,k)` and a matched same-observer
   stability baseline. The present `0.467` must become a point on a curve.
6. For any future `arrival × gap` model, use a null that scrambles arrival
   direction while preserving local density; simple order permutation is not
   sufficient because exposure and gap are functions of the same local geometry.
7. Pre-specify basal churn / ceiling behavior as a covariate or stratification
   variable before testing gap susceptibility.

## Related measurement literature

- Huh, M.; Cheung, B.; Wang, T.; Isola, P. **Position: The Platonic
  Representation Hypothesis.** ICML 2024, PMLR 235:20617–20642.
- Gröger, F.; Wen, S.; Brbić, M. **Revisiting the Platonic Representation
  Hypothesis: An Aristotelian View.** ICML 2026; arXiv:2602.14486.
- Koepke, A. S.; Zverev, D.; Ginosar, S.; Efros, A. A. **Back into Plato's Cave:
  Examining Cross-modal Representational Convergence at Scale.**
  arXiv:2604.18572v2, 2026.
- Klabunde, M.; Schumacher, T.; Strohmaier, M.; Lemmerich, F. **Similarity of
  Neural Network Models: A Survey of Functional and Representational Measures.**
  arXiv:2305.06329; ACM Computing Surveys 57(9).

## Provenance

- frozen protocol/result implementation: PR #380;
- #380 merge: `dad7f2a7c5ff9356d8156ad91e94674ea0336f3c`;
- parent artifact: `artifacts/relational_dynamics_v1.json`;
- parent artifact hash: `8791af54…`;
- post-hoc reanalysis: `artifacts/relational_dynamics_v1_reanalysis.json`;
- reanalysis runner: `scripts/run_relational_dynamics_reanalysis.py`;
- source corpus commit: `ff68b0653063e11e9cc3da887003bc0d46b14d26`;
- reference observer: `Qwen/Qwen3-Embedding-0.6B@97b0c61`;
- transfer observer: `sentence-transformers/all-MiniLM-L6-v2@1110a24`.
