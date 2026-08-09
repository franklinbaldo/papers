---
type: "Protocol"
title: "Semantic Atlas Experiment B — Model Predictive Navigation"
description: "Pre-registered experiment testing whether short-horizon rollout selection can follow semantic routes while preserving natural language generation."
tags: [semantic-atlas, preregistration, mpc, steering]
timestamp: 2026-08-09T00:18:00Z
---

# Semantic Atlas Experiment B — Model Predictive Navigation

## Dependency

Requires Experiment A to produce a frozen SRF calibration and atlas. If Experiment A fails its geometry criteria, this experiment may still be run as a diagnostic but cannot support the full atlas claim.

## Hypothesis

Short-horizon semantic MPC increases semantic goal attainment at a fixed visible-token budget relative to base generation and simple similarity reranking, without requiring an abrupt degradation in language-model likelihood or path naturalness.

This experiment is a **control experiment, not an efficiency experiment**. All discarded rollouts count toward compute cost.

## Conditions

1. `base`: ordinary Qwen generation;
2. `goal-prompt`: destination stated explicitly in natural language;
3. `similarity`: choose candidates only by endpoint distance to goal;
4. `semantic-mpc`: progress + curvature + off-manifold + model log probability;
5. `mpc-no-curvature`;
6. `mpc-no-manifold`.

## Tasks

Create a frozen list of origin/goal pairs covering at least:

- explanation -> formalization;
- concrete example -> general principle;
- one technical domain -> a neighboring technical domain with a plausible bridge;
- multi-waypoint routes with an explicit precedence constraint;
- at least one deliberately hard transition expected to expose a barrier.

Goals are evaluated through held-out semantic descriptions and should not be copied verbatim into the generated continuation for non-prompt conditions.

## Controller

At each decision point:

1. sample `N` short continuations;
2. trace each candidate in the SRF;
3. compute route score;
4. choose one candidate;
5. commit only a short prefix;
6. recompute the state and repeat.

Primary `N`, horizon, committed-prefix length and random seeds must be frozen in the result manifest before inspecting aggregate outcomes.

## Metrics

- success@visible-token-budget;
- final goal distance;
- semantic path length;
- straightness and turning angle;
- revisit/loop count;
- base-model log probability;
- total generated tokens including discarded rollouts;
- wall-clock time;
- independent fluency/coherence score on a blinded sample.

## Primary falsification

The navigation claim is weakened if `semantic-mpc` does not beat both `base` and `similarity` on goal attainment at matched visible-token budget, or if gains require a material loss of coherence.

The efficiency claim is **not tested** by a positive MPC result. A controller that generates 20 discarded paths for each committed path may be useful evidence of navigability while remaining computationally inefficient.

## Reporting

Report every frozen task and seed, including failures and routes that become less natural under the curvature penalty. Do not select only visually attractive trajectories.
