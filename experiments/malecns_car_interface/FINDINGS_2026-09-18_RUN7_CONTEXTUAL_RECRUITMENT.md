---
type: "Findings Record"
title: "MaleCNS Car Interface Run 7: Contextual learned recruitment policy"
description: "A tiny reality-bounded bandit learns when to use a fixed IMU-heavy allocation versus the prior stateless dynamic allocator, using only specialist freshness at decision time."
tags: [malecns, driving, sensor-colony, dynamic-recruitment, bandit, experiment]
timestamp: 2026-09-18T23:53:00-04:00
---

# Run 7 — contextual learned recruitment policy

## Question

Run 6 showed that instantaneous disagreement × freshness moves compute away from a stale camera, but it did not consistently beat a strong fixed IMU-heavy allocation. The next question is whether a coordinator can learn **when each allocator is useful**, rather than committing to one rule globally.

## Implementation advance

Added `recruitment_bandit.py` with a tiny epsilon-greedy `ContextualPolicyBandit` and a lawful `freshness_context()` helper. The selector chooses between two already-defined matched-budget policies:

- `fixed_imu_heavy`: 4 camera specialists + 8 IMU specialists;
- `stateless_dynamic`: 2 pilot specialists per modality plus 8 slots allocated by the existing disagreement × freshness rule.

The decision-time context is only the median age of the two camera pilot reports, bucketed at 150 ms as `fresh` or `stale`. No hidden fault flag, latent truth, realized error, or simulator geometry is given to the selector.

The synthetic harness does use latent truth **after the action** to provide a delayed training/evaluation loss. That is explicitly harness supervision, not an agent input. A physical deployment must update the learner from a reproducible delayed target or task signal (for example later IMU/OBD/GNSS agreement or registered bodily/task feedback), not hidden simulator truth.

## Executed experiment

Deterministic standard-library simulation, same camera/IMU noise model as Run 6:

- train: 20,000 samples at 50% camera-stall prevalence;
- exploration: epsilon = 0.10;
- evaluate: 30,000 fresh samples at each of 20%, 50%, and 80% stall prevalence;
- total compute budget unchanged at 12 specialists;
- seed: `20260918`.

The learned mapping was stable and interpretable:

- `fresh` camera -> `fixed_imu_heavy`;
- `stale` camera -> `stateless_dynamic`.

Observed mean absolute error:

| camera stall prevalence | fixed 4/8 | stateless dynamic | contextual learned selector |
|---:|---:|---:|---:|
| 20% | 0.057979 | 0.058588 | **0.057869** |
| 50% | 0.069491 | 0.069795 | **0.069276** |
| 80% | 0.080469 | 0.080333 | **0.080094** |

Evaluation context counts were 23,995 fresh / 6,005 stale at 20%; 15,063 / 14,937 at 50%; and 6,082 / 23,918 at 80%.

During training, the learned mean losses also separated in the expected direction: on fresh-camera contexts, fixed 4/8 was better than stateless dynamic; on stale-camera contexts, stateless dynamic was better than fixed 4/8.

## Interpretation

This is a **small but consistent positive result**, not a large performance jump. The learned selector beat the better of the two global baselines at all three evaluation prevalences, including prevalence shifts away from the 50% training mixture. The gain is roughly 0.2–0.3% versus the best baseline in the easier/middle regimes and about 0.3% at 80% stalls; it is larger versus the wrong global policy.

The important result is architectural: Run 6's heuristic need not be discarded. A higher-level coordinator can learn **which recruitment rule to invoke under which lawful sensor-health context**. This is a closer analogue of the proposed MaleCNS coordinator than a single hard-coded formula.

The bandit is deliberately a cheap conventional baseline. A future MaleCNS coordinator must beat it under the same inputs, feedback contract, compute budget, and prevalence shifts.

## Reality-bound status

Decision-time policy selection consumes only `SpecialistReport.age_ms`, which is reproducible from real acquisition/inference timestamps. The experiment does not expose a simulator fault label or truth value to the selector.

## Cache / dependency status

No dataset, model weights, CARLA assets, or external package were downloaded. This run used only deterministic Python standard-library simulation; therefore there was no heavyweight cache miss.

## Next experiment

Replace the binary `fresh/stale` context with continuous lawful coordinator inputs — freshness, disagreement, confidence, age spread, novelty, and recent delayed reward — and compare:

1. fixed allocation;
2. stateless heuristic;
3. contextual bandit;
4. a small learned adapter;
5. a MaleCNS coordinator.

The key target is not merely lower average error but **marginal value of one additional fly per modality**, under matched compute and changing sensor reliability.
