---
type: "Findings Record"
title: "MaleCNS colony dynamic specialist recruitment under fixed compute"
description: "Deterministic ablation of a lawful freshness-and-disagreement allocator that recruits specialist flies under a fixed 12-instance budget."
tags: [malecns, driving, sensor-fusion, multi-agent, dynamic-recruitment, compute-budget, robustness, ablation]
timestamp: 2026-09-18T22:57:00-04:00
---

# Run 6 — dynamic specialist recruitment under fixed compute

## Status

**Executed.** This is a deterministic synthetic architecture experiment, not a trained-MaleCNS or autonomous-driving result.

The colony contract tests passed **15/15** assertions after adding the recruitment contract. The ablation used only Python standard-library code. No dataset, CARLA asset, model weight, or external dependency was downloaded in this run, so there was no repeated heavyweight download or cache miss.

## Question

RUN5 established that extra flies on a commonly stale physical sensor cannot recreate missing information. The next question is operational:

> If the car has a fixed compute budget, can the colony decide at runtime where another specialist fly is worth spending?

The allocator must obey the same reality boundary as the agent. It may not observe simulator truth, realized prediction error, or a hidden `sensor_failed` flag.

## Implementation advance

`colony.py` now provides two small baselines for curriculum stage C5.

`recruitment_score()` combines:

- within-modality specialist disagreement, as a proxy for uncertainty that another independently trained specialist might reduce;
- median report age, converted to exponential freshness, so a common-mode stale stream is not rewarded merely because its specialists disagree;
- a small uncertainty floor so perfectly agreeing fresh pilots are not assigned a mathematically zero opportunity value.

`allocate_recruitment_slots()` apportions a fixed number of extra specialist slots across modalities using largest-remainder allocation. All candidate modalities must estimate the same normalized semantic channel. The allocator receives only lawful specialist reports.

The intended distinction is important:

- **specialist/inference uncertainty** can justify more flies on the same fresh modality;
- **physical sensor staleness** should push compute toward an independent fresh modality instead.

This is a deterministic baseline for a future learned MaleCNS recruiter, not a claim that this hand-written score is optimal.

## Synthetic experiment

`colony_dynamic_recruitment_ablation.py` models a fast-changing scalar jointly estimated by camera-derived perception and IMU.

Every policy gets exactly **12 fly instances**. Dynamic recruitment always starts with two camera pilots and two IMU pilots, then allocates the remaining eight slots from those pilot reports. Three matched-compute static splits are controls:

- camera-heavy: 8 camera / 4 IMU;
- balanced: 6 / 6;
- IMU-heavy: 4 / 8;
- dynamic: 4 pilots + 8 lawfully recruited specialists.

Per trial:

- true scalar uniform in `[-1, 1]`;
- scalar velocity uniform in `[-3, 3]` units/s;
- healthy camera age 20–60 ms;
- common-mode stalled camera age 450–900 ms;
- IMU age 5–30 ms;
- camera specialist noise burst probability 0.15 (`sigma=0.20`, confidence 0.65) versus normal `sigma=0.055`, confidence 0.90;
- IMU specialist noise burst probability 0.35 (`sigma=0.28`, confidence 0.62) versus normal `sigma=0.11`, confidence 0.86;
- 10,000 deterministic trials per camera-stall condition.

Camera acquisition age is common to its specialists while inference noise is independent. This lets the allocator face both kinds of failure without being told which one occurred.

## Observed results

Mean absolute error; lower is better. The last two columns show how the eight extra slots were allocated on average.

| Camera stall probability | Camera-heavy 8/4 | Balanced 6/6 | IMU-heavy 4/8 | Dynamic | Extra camera | Extra IMU |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.0 | 0.054558 | 0.051145 | **0.050317** | 0.051358 | 2.7892 | 5.2108 |
| 0.2 | 0.063760 | 0.059462 | **0.057909** | 0.058729 | 2.2906 | 5.7094 |
| 0.4 | 0.073440 | 0.068562 | **0.065889** | 0.066309 | 1.8120 | 6.1880 |
| 0.6 | 0.082171 | 0.076143 | **0.072869** | 0.073216 | 1.3330 | 6.6670 |
| 0.8 | 0.091750 | 0.084480 | 0.080925 | **0.080786** | 0.7856 | 7.2144 |
| 1.0 | 0.100634 | 0.093255 | 0.089087 | **0.088553** | 0.3321 | 7.6679 |

The allocator clearly reacts in the intended direction without seeing the fault flag: mean extra camera allocation falls from `2.7892` slots when the camera never stalls to `0.3321` when it is always stalled. The freed compute moves to IMU.

The more important result is **negative**: the hand-written dynamic heuristic does **not** dominate a tuned static allocation. From 0–60% camera-stall probability, the fixed IMU-heavy split remains 0.48–2.07% better than dynamic. Dynamic becomes slightly better only at the two most severe conditions: about 0.17% lower MAE at 80% stall and 0.60% lower at 100% stall.

Across the six equally weighted conditions, mean MAE is:

- camera-heavy: `0.077719`;
- balanced: `0.072174`;
- IMU-heavy: `0.069499`;
- dynamic: `0.069825`.

So the first C5 heuristic is about **0.47% worse** than the best fixed split averaged across this synthetic sweep. That is small, but it is a real failure to beat the static oracle-like choice and should not be hidden.

## Interpretation

The run establishes two different points.

First, lawful online allocation is feasible: freshness plus disagreement can make compute migrate away from a stale common-mode sensor without privileged state.

Second, **routing in the right direction is not enough**. A static allocation tuned to the known noise regime can still win. The pilot disagreement estimate is noisy, and the current hand-written score does not know the expected marginal error reduction from one additional specialist.

This is useful for the MaleCNS design. A learned coordinator/recruiter should not merely implement `more disagreement -> more flies`. It should learn the counterfactual value of another specialist under a compute/latency cost. The fixed heuristic becomes a concrete baseline it must beat.

The experiment also reinforces a useful decomposition for coordinator inputs:

- freshness / age: is the physical stream current enough to invest in?;
- disagreement: are the specialists epistemically unsettled?;
- confidence and novelty: what do individual specialists say about their own state?;
- marginal-value history: did recruiting another specialist actually improve downstream prediction/control recently?

Only the last item is not yet represented in the current contract.

## Prior-art boundary

Dynamic expert routing, mixtures of experts, conditional computation, uncertainty-aware sensor fusion, and adaptive resource allocation are established ideas. This run does **not** claim invention of dynamic routing.

Its contribution is narrower: an executed MaleCNS-specific architecture diagnostic inside the repository's reality-bounded sensor-colony program, with matched total specialist count, explicit separation between stale physical streams and independent specialist noise, and a falsifiable baseline for a future learned MaleCNS recruiter.

## Real-data bridge and cache plan

The next real-data candidate remains `commaai/comma2k19`. Its public example segment exposes CAN speed / steering / wheel speed together with IMU gyroscope/accelerometer and GNSS streams, which is enough to build overlapping reality-bounded motion channels without using global-pose truth as an agent input.

A small public demo shard was also identified for a future cached acquisition. The intended policy is:

1. download a single pinned shard once into a persistent cache;
2. key the cache by source URL + content checksum/version;
3. derive a compact local aligned slice once and reuse it across specialist experiments;
4. never redownload the full dataset just to repeat an ablation.

Binary dataset acquisition was not available in this execution environment, so this run did **not** claim a comma2k19 experiment and did not substitute global-pose or other privileged truth.

## Next experiment

Move from allocation by instantaneous disagreement to **measured marginal value of recruitment**. On a cached real-data slice, train several actual MaleCNS specialists per modality, then let the coordinator observe whether adding one specialist changed held-out prediction/control loss under a fixed latency/compute price.

Compare, at equal total compute:

- best fixed split selected on training data;
- current freshness + disagreement heuristic;
- a small learned non-connectome recruiter;
- a MaleCNS recruiter;
- random/rewired-connectome recruiter controls.

The key success criterion is not that dynamic allocation changes. It is that it improves unseen-regime performance enough to pay for its own routing complexity.
