---
type: "Findings Record"
title: "MaleCNS colony robust-consensus fusion under overconfident faults"
description: "Deterministic ablation testing whether cross-specialist consensus protects sensor colonies when faulty specialists are confidently wrong."
tags: [malecns, driving, sensor-fusion, multi-agent, robustness, ablation]
timestamp: 2026-09-18T19:57:00-04:00
---

# Run 3 — robust consensus against confidently wrong specialists

## Status

**Executed.** This is a deterministic synthetic architecture experiment, not a trained-MaleCNS result.

Six unit tests passed. The experiment used only Python standard-library code. No dataset, CARLA asset, model weight, or external dependency was downloaded, so there were no cache misses.

## Motivation

Run 2 showed that confidence-weighted fusion is excellent when specialist confidence is calibrated, but collapses when a faulty specialist is confidently wrong. A real sensor colony therefore needs a cheap baseline that does not trust confidence before checking whether a specialist agrees with its peers.

## Implementation

`colony.py` now includes `consensus_weighted_value()`.

The rule is deliberately small and reality-bounded:

1. find the median specialist value;
2. estimate median absolute deviation (MAD);
3. keep reports inside `max(min_radius, mad_scale * MAD)` around the median;
4. confidence-weight only the inlier reports.

The fusion rule sees only specialist reports. It receives no simulator truth, object state, lane geometry, or other privileged information.

`colony_consensus_ablation.py` compares five policies over 10,000 deterministic trials per condition with five specialists: one specialist, arithmetic mean, median, raw confidence-weighted mean, and consensus-gated confidence weighting.

Healthy specialists use sigma `0.05` and confidence `0.9`. Faulty specialists use bias `+0.8`, sigma `0.08`, and are tested in two regimes: calibrated low confidence (`0.15`) and adversarial/miscalibrated high confidence (`0.95`).

## Observed results — calibrated faulty confidence 0.15

| Fault probability | Single MAE | Mean MAE | Median MAE | Confidence MAE | Consensus MAE |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.0 | 0.040075 | 0.017748 | 0.021236 | 0.017748 | 0.018128 |
| 0.1 | 0.114442 | 0.090424 | 0.031166 | 0.029173 | 0.024997 |
| 0.2 | 0.192122 | 0.166000 | 0.069250 | 0.046721 | 0.060391 |
| 0.3 | 0.267613 | 0.243237 | 0.147587 | 0.071970 | 0.136327 |
| 0.4 | 0.343821 | 0.320124 | 0.259624 | 0.106385 | 0.249504 |

When confidence is genuinely calibrated, plain confidence weighting remains the strongest rule at moderate/high fault rates. The consensus gate is slightly better at 10% faults but should not replace calibrated confidence wholesale.

## Observed results — overconfident faulty specialists 0.95

| Fault probability | Single MAE | Mean MAE | Median MAE | Confidence MAE | Consensus MAE |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.0 | 0.040075 | 0.017748 | 0.021236 | 0.017748 | 0.018128 |
| 0.1 | 0.114442 | 0.090424 | 0.031166 | 0.093565 | 0.025544 |
| 0.2 | 0.192122 | 0.166000 | 0.069250 | 0.171619 | 0.062747 |
| 0.3 | 0.267613 | 0.243237 | 0.147587 | 0.250581 | 0.142617 |
| 0.4 | 0.343821 | 0.320124 | 0.259624 | 0.328458 | 0.259605 |

At 20% overconfident faults, raw confidence fusion reaches MAE `0.171619`, while consensus-gated fusion reaches `0.062747` — about **63.4% lower error**. It also slightly beats the plain median (`0.069250`).

## Interpretation

The useful conclusion is not that the new fixed rule is the final coordinator. It is that a MaleCNS coordinator should receive enough information to infer **both self-confidence and social/ensemble agreement**.

A specialist saying “I am certain” is not sufficient. The coordinator should be able to sense whether that report is compatible with independent specialists observing the same physical channel.

This suggests a richer but still tiny per-channel state for the coordinator:

- fused scalar candidate;
- median / robust center;
- disagreement or MAD;
- fraction of specialists inside consensus;
- aggregate self-reported confidence;
- novelty/surprise.

These are all derivable from lawful specialist outputs and can become scalar input channels to the next-layer MaleCNS.

## Next experiment

Move from synthetic scalar reports to one real low-bandwidth channel. A good first target is vehicle speed/yaw/IMU because it can be reproduced from OBD/phone sensors and later replayed from a small cached driving shard. Train several independent sensor-specialist adapters + frozen MaleCNS instances, then compare:

- one specialist;
- median;
- confidence weighting;
- consensus-gated confidence;
- learned MaleCNS coordinator.

The learned coordinator must beat these fixed baselines under normal noise, dropout, confidently wrong specialists, and sensor drift.
