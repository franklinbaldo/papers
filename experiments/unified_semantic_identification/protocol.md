---
type: "Protocol"
title: "Unified Semantic Identification Benchmark"
description: "Prospective cross-program benchmark comparing static geometry, interventional responses, inverse semantic queries, their combinations, and optional Torus model classes under one frozen held-out-observer evaluation contract."
tags: [semantic-identification, semantic-atlas, pontifex, perquire, torus, semantic-observers, benchmark]
timestamp: 2026-09-19T16:00:00-04:00
---

# Unified Semantic Identification Benchmark

## Status

Prospective protocol. No result is implied by this document.

The benchmark exists to answer one programme-level question:

> Do Semantic Atlas, Pontifex and Perquire expose genuinely complementary information about a representation system, or do they mostly recover the same structure through different interfaces?

Torus is evaluated only as an **optional model class** over Pontifex-derived observations. It is not assumed by the benchmark.

## 1. Unit of evaluation

Choose a panel of frozen representation observers

[
O_1,ldots,O_m
]

that can process the same declared stimulus set. One observer is held out from construction in each confirmatory fold.

The primary endpoint is prediction of the held-out observer's **relational structure** on untouched test stimuli, not raw coordinate equality.

Primary relational endpoints:

- pairwise cosine/distance reconstruction after observer-local normalization;
- k-nearest-neighbor overlap / calibrated mKNN;
- rank correlation of pairwise relations;
- held-out intervention-response prediction when the observer supports the Pontifex probe family.

Downstream task utility is secondary and must not substitute for the structural endpoint.

## 2. Frozen data boundary

Use four disjoint partitions:

[
D_{mathrm{assembly}}
perp
D_{mathrm{student}}
perp
D_{mathrm{val}}
perp
D_{mathrm{test}}.
]

The names are programme-wide contracts:

- **assembly:** construct static Atlas objects, intervention registries, anchor sets, or any cross-observer common structure;
- **student:** fit trainable predictors/transports/search policies that consume the already frozen construction;
- **val:** choose hyperparameters/model class only;
- **test:** final confirmatory endpoint; never used for construction, adaptation, model selection, query design, or threshold choice.

For Perquire-style arms, adaptive search occurs only on (D_{mathrm{student}}) or on a separately declared adaptation partition nested inside it. Correct-target similarity from (D_{mathrm{test}}) must never select prompts, questions, budgets, or stopping rules.

For held-out-observer folds, the held-out observer contributes no assembly data and no validation labels used to select the cross-observer model. Its test responses are opened only for final scoring.

## 3. Arms

All arms receive the same stimulus manifests and declared resource accounting.

### A. Static Atlas

Inputs may include:

- observer-local embeddings;
- relative/anchor coordinates;
- calibrated neighborhood graphs;
- spectral or manifold features frozen from assembly data.

No intervention responses and no target-conditioned Perquire feedback are allowed.

### B. Pontifex intervention only

Inputs are within-observer responses to a predeclared shared/proxy intervention family.

No raw cross-observer coordinate mapping is required at the primitive layer. If the predictor later fits an explicit transport, that transport is reported as a separate sub-arm.

### C. Perquire inverse-query only

The system receives an unknown target representation and a frozen query/generation mechanism with scalar feedback under the Perquire causal-feedback contract.

The evaluator is distinct from the optimization signal.

### D. Atlas + Pontifex

Static relational features and intervention-response features are combined under the shared Synergy Geometry evaluation contract.

### E. Atlas + Pontifex + Perquire

All three observation channels are available. The Perquire search policy is frozen before test.

### F. Optional Torus model class

The same Pontifex observations as arm B or D are passed through the frozen Torus periodic/multiscale model class.

This arm tests **model class**, not access to additional observations. It must receive the same intervention budget as its non-Torus comparator.

### G. Simple alignment baselines

At minimum:

- orthogonal/rectangular Procrustes where dimension permits;
- affine/ridge transport;
- anchor-relative representation;
- best single observer / nearest static baseline.

## 4. Resource matching

Report separately:

- number of observer forward passes;
- number of intervention evaluations;
- number of target-similarity evaluations;
- LLM generation calls for Perquire arms;
- trainable parameter count;
- wall-clock and compute;
- stored state / bytes when relevant.

A combined arm is not allowed to claim scientific superiority solely by spending an unreported larger observation budget.

## 5. Shared multi-observer controls

Reuse `experiments/synergy_geometry/protocol.md`.

For every combined arm report:

- best single channel;
- best static weighted combination;
- interaction-capable combination;
- shuffled-coupling null;
- channel ablation/corruption;
- correspondence-specific interaction where applicable.

Use "synergy" only when the corresponding statistical/information-theoretic criterion is actually estimated. Otherwise use "complementarity" or "interaction gain".

## 6. Primary discriminants

### 6.1 Unique Pontifex information

Does

[
	ext{Atlas+Pontifex} > 	ext{Atlas}
]

on held-out-observer structural prediction under matched capacity and observation budget?

A null result means Pontifex may be rediscovering static relational structure for this benchmark.

### 6.2 Unique Perquire information

Does

[
	ext{Atlas+Pontifex+Perquire}
>
	ext{Atlas+Pontifex}
]

under a held-out evaluator distinct from Perquire's optimization score?

### 6.3 Torus-specific value

Does a Torus model class outperform a matched non-periodic/non-Torus model using **the same Pontifex observations**?

If not, the result cannot be interpreted as evidence for the Torus even if Pontifex itself works.

### 6.4 Static/interventional quadrant

Classify observer pairs by static relational similarity and intervention-response similarity. Test whether each quadrant predicts different held-out transfer behavior.

## 7. Confirmatory rule

No initiative "wins" the programme from one endpoint.

A channel is called **incrementally informative** only if:

1. it improves the frozen primary held-out-observer endpoint over the nested arm without that channel;
2. the confidence interval for the paired improvement excludes zero under the preregistered analysis;
3. a matched shuffled/decoy control does not reproduce the gain;
4. the result is not explained solely by a larger observation or compute budget.

Negative results are retained as first-class findings.

## 8. Evidence boundaries

The benchmark can establish only incremental predictive information under the declared observers, stimuli, probe families, and model classes.

It cannot by itself establish:

- an observer-independent semantic universe;
- metaphysical semantic atoms;
- intrinsic toroidal topology;
- biological equivalence between MaleCNS and artificial models;
- human semantic truth;
- causal identity across proxy interventions.

## 9. First implementation target

The first executable version should use only artificial text embedding observers so that all arms can share exactly the same stimuli and the intervention family is unambiguous.

MaleCNS or other heterogeneous substrates are escalation tests only after the artificial-observer benchmark is frozen and understood.

## 10. Reuse contract

Implementations should import or reuse existing project machinery where possible:

- Semantic Atlas relational metrics and frozen static baselines;
- Pontifex response-field builders;
- Perquire's frozen causal-feedback/search contract, without importing target outcomes into test;
- Synergy Geometry multi-observer baselines;
- Structural Identification vocabulary for equivalence/gauge;
- Torus as an optional model class only.

Any new metric or aligner must document why the existing component is insufficient.
