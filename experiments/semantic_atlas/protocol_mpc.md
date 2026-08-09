---
type: "Protocol"
title: "Semantic Atlas Experiment B — Model Predictive Navigation"
description: "Pre-registered experiment testing whether short-horizon rollout selection can follow explicit semantic routes while preserving natural language generation."
tags: [semantic-atlas, preregistration, mpc, steering]
timestamp: 2026-08-09T00:18:00Z
---

# Semantic Atlas Experiment B — Model Predictive Navigation

## Dependency

Requires Experiment A to produce a frozen SRF calibration and atlas. If Experiment A fails its geometry criteria, this experiment may still be run as a diagnostic but cannot support the full atlas claim.

## Hypothesis

Short-horizon semantic MPC increases semantic route completion at a fixed visible-token budget relative to base generation and simple similarity reranking, without requiring an abrupt degradation in language-model likelihood or path naturalness.

This experiment is a **control experiment, not an efficiency experiment**. All discarded rollouts count toward compute cost.

## Conditions

1. `base`: ordinary Qwen generation;
2. `goal-prompt`: destination stated explicitly in natural language;
3. `similarity`: choose candidates only by endpoint distance to the current waypoint;
4. `semantic-mpc`: waypoint progress + curvature + measured off-manifold cost + model log probability;
5. `mpc-no-curvature`: identical controller with curvature weight exactly zero;
6. `mpc-no-manifold`: identical candidates and measured manifold diagnostics, but off-manifold weight exactly zero.

Conditions 4 and 6 are invalid if their candidate manifold penalties are all implicitly zero. The harness must compute the same explicit estimator in both conditions and ablate only its contribution to the score.

## Tasks

Create a frozen list of origin/route pairs covering at least:

- explanation -> formalization;
- concrete example -> general principle;
- one technical domain -> a neighboring technical domain with a plausible bridge;
- multi-waypoint routes with an explicit precedence constraint;
- at least one deliberately hard transition expected to expose a barrier.

Each task stores an ordered `Route` of SRF waypoints, not only a terminal goal. Goals and waypoints are evaluated through held-out semantic descriptions and should not be copied verbatim into generated continuations for non-prompt conditions.

## Off-manifold estimator

The primary v0 estimator is distance to observed atlas support: for each point on a candidate path, compute the mean distance to its `k` nearest frozen atlas reference points, normalize by a calibration scale, and average over the path. Freeze `k`, the reference set, and scale before the primary run.

A density-based estimator can be a later robustness check, not a post-hoc replacement for bad results.

## Controller

At each decision point:

1. select the first route waypoint not yet reached within the frozen tolerance;
2. sample `N` short continuations;
3. trace every full candidate in the SRF;
4. compute waypoint progress, curvature, off-manifold cost, path length, and base-model log probability;
5. choose one candidate;
6. commit only the first `commit_tokens` **model tokens**, not the whole winning rollout;
7. trace the committed prefix again, update waypoint state from the committed endpoint, and replan.

The Qwen adapter must use the model tokenizer for step 6. Whitespace prefixing exists only for deterministic unit tests.

Primary `N`, rollout horizon, `commit_tokens`, waypoint tolerance, manifold-estimator parameters, and random seeds must be frozen in the result manifest before inspecting aggregate outcomes.

## Metrics

- route completion and success@visible-token-budget;
- waypoint completion rate and order violations;
- final goal distance;
- semantic path length;
- straightness and turning angle;
- measured off-manifold cost;
- revisit/loop count;
- base-model log probability;
- total generated tokens including discarded rollouts;
- committed/generated token ratio;
- wall-clock time;
- independent fluency/coherence score on a blinded sample.

## Primary falsification

The navigation claim is weakened if `semantic-mpc` does not beat both `base` and `similarity` on route completion at matched visible-token budget, if intermediate waypoints add no value over terminal-goal reranking, or if gains require a material loss of coherence.

The natural-route claim is weakened if `mpc-no-manifold` is indistinguishable from `semantic-mpc` while the registered estimator has adequate dynamic range, or if the manifold penalty merely forces longer paths without improving held-out naturalness/coherence.

The efficiency claim is **not tested** by a positive MPC result. A controller that generates 20 discarded paths for each committed path may be useful evidence of navigability while remaining computationally inefficient.

## Reporting

Report every frozen task and seed, including failures, waypoint skips, and routes that become less natural under curvature or manifold penalties. Do not select only visually attractive trajectories.
