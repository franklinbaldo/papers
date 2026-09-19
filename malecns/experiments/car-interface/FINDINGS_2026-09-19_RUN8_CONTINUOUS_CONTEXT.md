---
type: "Findings Record"
title: "MaleCNS Car Interface Run 8: Continuous lawful context for recruitment"
description: "A small ridge-regression selector replaces the binary fresh/stale bucket with continuous sensor-health signals and learns which matched-budget recruitment policy to invoke."
tags: [malecns, driving, sensor-colony, dynamic-recruitment, continuous-context, experiment]
timestamp: 2026-09-19T00:54:00-04:00
---

# Run 8 — continuous lawful context for specialist recruitment

## Question

Run 7 showed that a binary `fresh` / `stale` context can learn when to switch between a strong fixed IMU-heavy allocation and the stateless disagreement × freshness allocator. The next question is whether the coordinator benefits from retaining continuous sensor-health information instead of throwing it away at one hand-chosen threshold.

## Implementation advance

`recruitment_bandit.py` now includes `LinearContextualPolicy`, a tiny per-action ridge-regression reward model that stores only sufficient statistics. The policy receives a 10-value context built by `continuous_context_features()` from two pilot specialists per modality:

- intercept;
- primary-modality median age;
- squared median age;
- exponential freshness;
- within-primary disagreement;
- primary median confidence;
- primary age spread;
- secondary disagreement;
- secondary median confidence;
- secondary median age.

All ten values are reproducible from real specialist reports. There is no hidden fault flag, simulator geometry, realized error, or latent truth in the decision-time context.

The two actions remain matched-budget policies from Run 7:

- `fixed_imu_heavy`: 4 camera specialists + 8 IMU specialists;
- `stateless_dynamic`: 2 pilot specialists per modality plus 8 extra specialists allocated by disagreement × freshness.

## Executed experiment

A new deterministic standard-library harness, `colony_continuous_context_ablation.py`, replaces the binary camera stall with a continuous camera age from 20 to 900 ms. Training uses randomized action assignment, so each observed reward corresponds to the action actually selected for that training sample; the learner does not inspect the counterfactual action's loss.

Configuration:

- training: 200,000 samples, camera age uniform over 20–900 ms;
- ridge: 0.1;
- evaluation: 30,000 fresh samples per age profile;
- age profiles: uniform, fresh-skewed, stale-skewed;
- total specialist budget: 12 for every compared policy;
- seed: `20260919`;
- local wall time for training plus all evaluations: approximately 12.5 s;
- dependencies: Python standard library only.

Observed mean absolute error:

| age profile | fixed 4/8 | stateless dynamic | discrete 150 ms | continuous linear | oracle per-sample |
|---|---:|---:|---:|---:|---:|
| uniform | 0.098547 | 0.098481 | 0.098380 | **0.098198** | 0.095961 |
| fresh-skewed | 0.089707 | 0.090010 | 0.089642 | **0.089472** | 0.086361 |
| stale-skewed | 0.094146 | 0.093860 | 0.093865 | **0.093726** | 0.092299 |

The learned selector chose `fixed_imu_heavy` / `stateless_dynamic` respectively:

- uniform: 16,205 / 13,795;
- fresh-skewed: 20,448 / 9,552;
- stale-skewed: 12,330 / 17,670.

Relative to the best single global policy in each evaluation profile, the continuous selector reduced MAE by about 0.29%, 0.26%, and 0.14%. Relative to the Run-7-style discrete 150 ms rule, it improved by about 0.18%, 0.19%, and 0.15%.

## Interpretation

This is another **small positive result**, not a dramatic jump. The main result is that the continuous coordinator preserved a modest advantage across three different age distributions without changing total compute. The learned action counts also move in the expected direction: more fixed IMU-heavy choices when the camera distribution is fresher, more stateless-dynamic choices when it is older.

The oracle gap remains much larger than the gain from the linear model. That is useful: a great deal of per-sample allocation value is still left on the table. The next coordinator should therefore learn **marginal value of another specialist**, not only select between two coarse whole-budget policies.

The linear policy is a conventional baseline, not evidence that MaleCNS is required. A future MaleCNS coordinator must beat this baseline under identical lawful inputs, delayed-feedback contract, specialist budget and distribution shifts.

## Reality-bound status

Decision-time features are derived only from `SpecialistReport.age_ms`, `confidence`, interpreted `value`, and their within-modality disagreement/spread. The synthetic harness uses latent truth only after action selection to score prediction error. A physical experiment must replace that scoring source with delayed reproducible supervision such as later cross-sensor agreement, route/task feedback, or other declared bodily signals.

## Cache / dependency status

No dataset, model weights, CARLA assets, or external package were downloaded. There was no heavyweight cache miss.

## Next experiment

Move from choosing one of two whole-budget policies to predicting the **marginal reward of one additional specialist per modality**. Allocate the eight extra slots sequentially under an explicit compute/latency cost, then compare:

1. fixed allocation;
2. stateless disagreement × freshness allocation;
3. binary contextual selector;
4. continuous policy selector;
5. learned marginal-value allocator;
6. MaleCNS coordinator using the same report vector and delayed reward.

The decisive test remains real cached CAN/IMU/GNSS/camera data rather than synthetic sensor dynamics.
