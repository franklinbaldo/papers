---
type: "Findings Record"
title: "MaleCNS Car Interface Run 9: Greedy marginal specialist recruitment"
description: "A sequential allocator learns the one-step value of recruiting another camera or IMU specialist from lawful sensor-health and budget-state features; the executed ablation shows that this myopic objective underperforms simpler matched-budget baselines."
tags: [malecns, driving, sensor-colony, dynamic-recruitment, marginal-value, negative-result, experiment]
timestamp: 2026-09-19T01:54:00-04:00
---

# Run 9 — greedy marginal specialist recruitment

## Question

Run 8 left a clear target: instead of choosing between two complete allocation policies, can a coordinator predict the marginal value of **one more fly** and allocate the eight extra specialist slots sequentially?

This run implements that literal version and tests it before making the architecture more complicated.

## Implementation advance

`marginal_recruitment.py` adds a reusable 13-value decision contract. The first ten values are the continuous reality-bounded sensor-health context from Run 8. Three additional features encode only the current compute state:

- primary-modality specialist count / per-modality limit;
- secondary-modality specialist count / per-modality limit;
- total active specialists / total budget.

`colony_marginal_recruitment_ablation.py` starts with two camera specialists and two IMU specialists, then allocates eight additional slots one at a time. At each step it can choose only `camera` or `imu`. The learner sees reports that have already been activated plus the budget state. It never sees a hidden fault flag, latent truth, simulator geometry, or future specialist reports before deciding.

Training uses randomized reachable allocation states. After a random action, synthetic truth is used only to compute delayed one-step reward:

`reward = error_before - error_after`

Positive reward therefore means that recruiting that one specialist reduced prediction error.

## Executed validation

Configuration:

- marginal learner: per-action linear ridge model already used by Run 8;
- training samples: 60,000;
- diagnostic randomized states: 40,000;
- evaluation samples: 10,000 per age profile;
- profiles: uniform, fresh-skewed, stale-skewed camera age;
- initial specialists: 2 camera + 2 IMU;
- extra slots: 8;
- total final budget: 12 specialists for every compared policy;
- seed: `20260919`;
- external dependencies: none; Python standard library only in the repository implementation.

Observed one-step diagnostic over reachable randomized states:

| modality recruited | fraction where the extra specialist worsened current error | mean one-step error improvement |
|---|---:|---:|
| camera | 0.513822 | -0.000285 |
| IMU | 0.454923 | +0.005819 |

The camera specialist is slightly harmful on average in this synthetic regime, while another IMU specialist has positive expected one-step value. More importantly, either action can worsen the current estimate very often because modality summaries use finite noisy ensembles and medians are non-monotonic under one-sample additions.

Final mean absolute error:

| age profile | fixed 4 camera / 8 IMU | stateless dynamic | learned marginal | clairvoyant final-allocation oracle |
|---|---:|---:|---:|---:|
| uniform | 0.097974 | **0.097970** | 0.099319 | 0.075340 |
| fresh-skewed | **0.090837** | 0.091298 | 0.092025 | 0.069874 |
| stale-skewed | 0.092937 | **0.092870** | 0.094213 | 0.069321 |

Average final camera-specialist counts chosen by the marginal learner were 5.861, 6.192 and 5.499 respectively. The evaluation-only oracle averaged about 5.93 camera specialists in all three profiles.

## Result

This is a **negative result for the naive marginal-value formulation**.

The learned sequential allocator was worse than the best simple matched-budget baseline in all three evaluation profiles. Relative to the best baseline in each profile, MAE increased by roughly 1.38%, 1.31% and 1.45%.

The failure is useful because it rejects the most literal interpretation of “value of the next fly.” The allocator's average camera/IMU balance is not wildly wrong; indeed its average camera count is close to the oracle's. The problem is **per-sample choice**. Immediate one-step error reduction is a noisy, non-additive target and does not reliably identify the allocation that minimizes final error after all eight slots have been spent.

The large gap to the clairvoyant final-allocation oracle must also be interpreted carefully. That oracle inspects the realized outputs of specialists that the lawful policy has not recruited yet. It is therefore a lower bound for analysis, not a deployable policy. Part of the apparent gap is irreducible future-specialist noise rather than decision-time information that a better coordinator can necessarily recover.

## Design implication

Do not train the MaleCNS coordinator on one-step `error_before - error_after` as its primary recruitment objective.

The next allocator should target **terminal value under delayed feedback** or **value of information** instead. Two concrete variants are now better motivated:

1. train action value against final task loss after a continuation policy spends the remaining budget;
2. separate `activate/probe` from `trust/use`, so a newly activated specialist can be observed and rejected without forcing its report into the fused estimate.

The second variant is particularly compatible with a colony: compute allocation and epistemic trust do not have to be the same decision.

## Reality-bound status

All decision-time features are derived from already available `SpecialistReport` values, confidence, age, disagreement/spread, and active specialist counts. Synthetic truth appears only after a training action to compute delayed reward and in the explicitly clairvoyant evaluation lower bound. A real-car version must replace training reward with declared delayed supervision such as later OBD/IMU/GNSS consistency, route/body feedback, or other reproducible task outcomes.

## Cache / dependency status

No dataset, CARLA asset, model weight, Python package, or other heavyweight artifact was downloaded. There was no cache miss in this run.

## Next experiment

Keep the same 12-specialist budget and the same reality-bounded context, but compare:

- one-step marginal reward (this run);
- terminal-value recruitment with a fixed continuation policy;
- probe-then-trust recruitment;
- the Run-8 whole-policy selector;
- a MaleCNS coordinator trained on the same delayed terminal signal.

The decisive later validation remains a cached real CAN/IMU/GNSS/camera slice rather than this synthetic dynamics model.
