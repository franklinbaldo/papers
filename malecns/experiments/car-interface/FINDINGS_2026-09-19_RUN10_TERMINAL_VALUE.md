---
type: "Findings Record"
title: "MaleCNS Car Interface Run 10: Delayed terminal-value specialist recruitment"
description: "A sequential allocator is trained against final allocation loss after the remaining specialist budget is spent, improving over one-step marginal reward but still failing to beat the best simple matched-budget baselines."
tags: [malecns, driving, sensor-colony, dynamic-recruitment, terminal-value, delayed-reward, negative-result, experiment]
timestamp: 2026-09-19T02:52:00-04:00
---

# Run 10 — delayed terminal-value specialist recruitment

## Question

Run 9 showed that immediate `error_before - error_after` is a poor objective for deciding where to put the next fly. Does delayed **terminal value** work better if each recruitment action is credited by final loss only after the rest of the 12-specialist budget has been spent?

## Implementation advance

`colony_terminal_value_ablation.py` keeps the same reality-bounded 13-value decision state from Run 9: current sensor-health features plus active camera/IMU specialist counts and total budget usage.

Training differs in one important way. A random reachable allocation state is sampled, one recruitment action (`camera` or `imu`) is taken, and the remaining slots are spent by a fixed randomized continuation policy that cannot inspect hidden truth. Only after the complete allocation is formed is the action assigned reward:

`terminal reward = - final prediction error`

Synthetic truth is therefore delayed supervision only. It is not present in the decision vector, the action choice, or the continuation policy.

The learned terminal-value policy is then used sequentially to spend the full eight-slot extra budget. This is compared against:

- fixed 4-camera / 8-IMU allocation;
- stateless disagreement × freshness allocation;
- Run-9 one-step marginal learner;
- an evaluation-only clairvoyant final-allocation oracle.

## Executed validation

Configuration:

- terminal-value training samples: 120,000;
- Run-9 marginal training samples: 60,000;
- evaluation samples: 30,000 per age profile;
- profiles: uniform, fresh-skewed and stale-skewed camera age;
- initial specialists: 2 camera + 2 IMU;
- extra specialist slots: 8;
- final budget: 12 specialists for all deployable policies;
- per-modality maximum: 8;
- seed: `20260919`;
- external dependencies: none in the experiment logic.

Observed mean absolute error:

| age profile | fixed 4/8 | stateless dynamic | one-step marginal | terminal value | clairvoyant final-allocation oracle |
|---|---:|---:|---:|---:|---:|
| uniform | **0.097228** | 0.097232 | 0.098077 | 0.097438 | 0.074186 |
| fresh-skewed | **0.089178** | 0.089553 | 0.090444 | 0.089377 | 0.068267 |
| stale-skewed | 0.093787 | **0.093544** | 0.094931 | 0.093943 | 0.070104 |

Average final camera-specialist counts:

| age profile | one-step marginal | terminal value |
|---|---:|---:|
| uniform | 5.864 | 4.042 |
| fresh-skewed | 6.210 | 4.041 |
| stale-skewed | 5.493 | 4.033 |

Relative to the Run-9 one-step learner, terminal-value training reduced MAE by approximately:

- 0.65% on uniform camera age;
- 1.18% on fresh-skewed camera age;
- 1.04% on stale-skewed camera age.

However, it still missed the best simple baseline by approximately 0.22%, 0.22% and 0.43% respectively.

These are deterministic single-seed comparisons. They establish the executed result for seed `20260919`, but the ~0.65–1.18% terminal-over-one-step improvement should not be generalized as a robust effect until replicated across independent seeds or accompanied by paired uncertainty estimates.

## Result

The delayed objective is **better than the myopic objective, but not yet good enough**.

This rejects a simple explanation that Run 9 failed only because its reward horizon was too short. Moving supervision to terminal loss consistently recovers much of the one-step learner's deficit, but the learned sequential policy collapses toward roughly four camera specialists and eight IMU specialists across all three regimes. In other words, with this linear state/action model and randomized continuation target, terminal training mostly rediscovers the strong fixed IMU-heavy prior rather than learning useful per-episode adaptation.

There remains a large gap to the evaluation-only final-allocation oracle, but that oracle sees realized outputs of specialists not yet recruited. The gap is therefore best interpreted as a **value-of-clairvoyance / perfect-information upper bound**, not as a direct estimate of actionable value of information. A lawful coordinator must pay to reveal a report before deciding whether to use it. The oracle gap motivates a probe/value-of-information experiment, but does not by itself show that paid probing can recover the gap.

## Design implication

Do not jump directly from Run 9 to a more complicated recurrent coordinator while keeping recruitment and trust conflated.

The next clean experiment should separate two operations:

1. **probe / activate** — spend compute to obtain a specialist report;
2. **trust / use** — decide whether that report is allowed to affect the fused control estimate.

A probe can be informative even if its value should not be trusted directly. This permits a coordinator to learn from disagreement, freshness, confidence calibration and cross-modal consistency without forcing every paid-for specialist into the actuator path.

A second useful comparison is terminal training under a stronger but still lawful continuation policy, because the randomized continuation used here adds variance to the target. That must be compared against probe-then-trust rather than silently replacing this negative result.

## Prior-art and falsification boundary

A claim-level adversarial audit is recorded in [`audits/prior-art/malecns-terminal-value-recruitment-2026-09-19.md`](../../audits/prior-art/malecns-terminal-value-recruitment-2026-09-19.md).

The audit materially narrows what this run should be taken to establish:

- rollout and approximate dynamic-programming literature long predates the pattern of evaluating a current action through a downstream/base continuation policy; consequently, the randomized continuation is a load-bearing part of the RUN10 target rather than an implementation detail;
- active feature-acquisition and sensor-scheduling literature long predates the generic idea of paying to reveal information under a prediction/control budget;
- acquisition/resource scheduling followed by separate measurement validation also predates the generic `probe / activate` versus `trust / use` distinction;
- sparse terminal rewards have known credit-assignment difficulties, while reward shaping and stronger nongreedy acquisition methods are established alternatives;
- under adaptive-submodular/diminishing-return conditions, a strong greedy policy can already be competitive, so a more complex long-horizon coordinator should not be assumed to help without a stronger greedy control.

RUN10's defensible contribution is therefore the **executed MaleCNS-specific negative/control result**: within this lawful state, policy class, randomized continuation, matched 12-specialist budget, and seed, extending the reward horizon recovers part of RUN9's deficit but still does not beat the best simple baseline.

The next test should include at least: independent-seed uncertainty, a stronger lawful continuation policy, a stronger expected-marginal/greedy acquisition baseline, and a paid probe-then-trust comparison. The free clairvoyant oracle should remain an upper bound, not a deployable baseline.

## Reality-bound status

All action-time inputs are existing specialist reports, their age/confidence/disagreement-derived summaries, and compute-budget state. The randomized continuation policy never reads latent truth. Synthetic truth appears only after a completed allocation as delayed training/evaluation supervision.

For a real car, terminal supervision must be replaced by declared delayed physical/task signals: later IMU/OBD/GNSS consistency, route progress, intervention/collision outcomes, or other reproducible feedback. No simulator-only geometry or perfect object state is required by the policy contract.

## Cache / dependency status

No dataset, model weight, CARLA artifact, or new package was downloaded for this run. There was no heavyweight cache miss.

## Next experiment

Implement **probe-then-trust** under the same 12-specialist compute budget. Measure separately:

- which specialist was activated;
- whether its report was admitted into fusion;
- prediction/control error;
- calibration/disagreement information gained from the probe;
- latency/compute cost.

Compare always-trust, robust fixed trust gate, learned trust gate, and later a MaleCNS coordinator. This is the next experiment most directly motivated by Runs 9 and 10.
