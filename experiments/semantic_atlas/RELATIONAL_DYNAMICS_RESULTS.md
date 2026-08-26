---
type: "Findings Record"
title: "Semantic Atlas relational dynamics v1 — outcome"
description: "Outcome record for the preregistered frozen-encoder corpus-flow experiment: chronology exhibits semantic drift, but cross-observer relational-dynamics divergence does not exceed the stationary insertion null."
tags: [semantic-atlas, findings, dynamics, embeddings, negative-result, preregistration]
timestamp: 2026-08-26T05:58:00Z
---

# Semantic Atlas relational dynamics v1 — outcome

## Scope

This record interprets the already-versioned artifact
`experiments/semantic_atlas/artifacts/relational_dynamics_v1.json` under the
decision rule frozen before execution in PR #380.

The encoders are frozen. Individual document vectors do not move. The tested
dynamical object is the corpus-induced relational structure obtained while the
same final 116-document corpus is replayed in repository chronology: neighbor
identity/rank, regional churn, and hubness-corrected neighbor structure.

## Primary result

The preregistered classification is:

**`dynamic-transfer-not-rejected`**.

The chronology itself is detectably non-exchangeable in semantic content:

- observed semantic drift: **0.149835**;
- stationary-null mean: **0.111473**;
- z = **7.688**;
- permutation `p_upper = 0.007752`.

So the experiment does not fail because the observed repository chronology is
semantically indistinguishable from random insertion.

However, the primary raw cross-observer dynamic divergence does **not** exceed
the stationary insertion null:

- observed raw global dynamic divergence: **0.357006**;
- null mean: **0.329273**;
- z = **0.519**;
- `p_upper = 0.317829`.

The registered sensitivity checks agree with the negative primary result:

- `k=3`: `p_upper = 0.945736`;
- `k=10`: `p_upper = 0.286822`.

The registered regional statistic also does not support excess divergence
(`p_upper = 0.937984` for raw cosine).

## Hubness controls

Both registered hubness corrections reduced absolute k-occurrence skewness in
both observers and therefore count as effective controls under the frozen rule.
Neither reveals a hidden significant cross-observer dynamic divergence:

| geometry | observed global divergence | null mean | p_upper |
|---|---:|---:|---:|
| raw cosine | 0.357006 | 0.329273 | 0.317829 |
| CSLS | 0.213471 | 0.206949 | 0.418605 |
| Mutual Proximity | 0.233452 | 0.203026 | 0.170543 |

Therefore the result is not “raw divergence explained away by hubness”; the raw
cross-observer divergence was never significant against the stationary null in
the first place.

## What this falsifies

For this frozen corpus, chronology, and Qwen3-Embedding/MiniLM observer pair, the
cheap hypothesis that **corpus growth alone produces model-specific relational
dynamics beyond what stationary insertion already explains** is not supported.

The chronology carries semantic drift, but that drift does not induce an excess
between-observer divergence in normalized neighborhood-churn dynamics.

This is a useful negative result. It rules out one inexpensive surrogate for the
stronger Semantic Atlas dynamics claim and prevents ordinary finite-corpus
neighbor turnover from being mistaken for model-specific dynamics.

## What this does not test

This experiment does **not** test model-generated trajectories, controlled
interventions, transition laws conditioned on semantic history, reachability,
control cost, route planning, MPC, or Semantic Servo. Those objects require
actual model-dependent generation or intervention outcomes.

Accordingly, this result should narrow PR #379 rather than terminate the whole
Atlas programme:

- shared/static coordinates remain infrastructure;
- frozen-corpus relational replay is now a negative control / boundary result;
- any surviving claim of model-specific dynamics must be demonstrated on a
  genuinely model-dependent dynamical process, especially generated semantic
  trajectories;
- no rescue tuning of the corpus-flow experiment is authorized.

## Consequence for the roadmap

1. Do not promote corpus-induced relational churn as evidence for model-specific
   dynamics in `semantic_atlas.md`.
2. Restack/narrow PR #379 so its central empirical claim begins at generated or
   intervention-dependent trajectories, with this negative result recorded as a
   boundary condition.
3. Proceed independently with A.1 using the already-persisted Qwen/MiniLM raw
   embedding caches; A.1 remains a static alignment experiment and is not changed
   by this outcome.
4. Preserve this negative result in future summaries instead of replacing it with
   a stronger post-hoc relational metric.

## Provenance

- protocol/result implementation and execution: PR #380;
- merge: `dad7f2a7c5ff9356d8156ad91e94674ea0336f3c`;
- artifact: `experiments/semantic_atlas/artifacts/relational_dynamics_v1.json`;
- artifact hash recorded by the experiment line: `8791af54…`;
- source corpus commit: `ff68b0653063e11e9cc3da887003bc0d46b14d26`;
- reference observer: `Qwen/Qwen3-Embedding-0.6B@97b0c61`;
- transfer observer: `sentence-transformers/all-MiniLM-L6-v2@1110a24`.
