---
type: "Findings Record"
title: "MaleCNS sensor-colony synthetic fault ablation"
description: "Deterministic pre-training ablation of aggregation rules for redundant sensor-specialist colonies under independent biased faults."
tags: [malecns, driving, sensor-fusion, multi-agent, robustness, ablation]
timestamp: 2026-09-18T18:58:00-04:00
---

# Run 2 — sensor-colony fault ablation

## Status

**Executed.** This is a synthetic architecture test, not a trained-MaleCNS result.

No CARLA asset, dataset, model weight, or external dependency was downloaded. There were therefore no dataset/model cache misses in this run.

## Question

Before paying the cost of training several MaleCNS instances per sensor, does redundant specialization have a measurable robustness advantage under a simple failure model, and which cheap fusion baselines must a learned coordinator beat?

## Setup

`colony_fault_ablation.py` uses a deterministic random seed (`20260918`) and 10,000 trials per condition. Five specialists observe the same lawful scalar in `[-1, 1]`.

Healthy specialists receive Gaussian noise with sigma `0.05` and report confidence `0.9`. Independently faulty specialists receive a large `+0.8` bias plus Gaussian noise with sigma `0.08` and, in the calibrated condition, report confidence `0.15`.

Four policies are compared by mean absolute error (MAE):

1. one specialist only;
2. arithmetic mean of five specialists;
3. median of five specialists;
4. confidence-weighted mean.

This experiment intentionally does **not** simulate MaleCNS dynamics. It isolates the value and failure modes of the colony/fusion architecture so later learned coordinators have explicit deterministic baselines.

## Observed results

| Fault probability | Observed fault fraction | Single MAE | Mean MAE | Median MAE | Confidence-weighted MAE |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.0 | 0.00000 | 0.040075 | 0.017748 | 0.021236 | 0.017748 |
| 0.1 | 0.09948 | 0.114442 | 0.090424 | 0.031166 | 0.029173 |
| 0.2 | 0.20010 | 0.192122 | 0.166000 | 0.069250 | 0.046721 |
| 0.3 | 0.30010 | 0.267613 | 0.243237 | 0.147587 | 0.071970 |
| 0.4 | 0.39836 | 0.343821 | 0.320124 | 0.259624 | 0.106385 |

At 20% independent specialist faults, the median reduced MAE from `0.192122` for one specialist to `0.069250` (~64% lower), while calibrated confidence weighting reached `0.046721` (~76% lower).

The zero-fault condition is also important: simple averaging of independent noisy specialists already improves the scalar estimate (`0.017748` MAE versus `0.040075` for one specialist). Redundancy can therefore help even before faults appear.

## Adversarial confidence control

The same 20% fault condition was rerun with faulty specialists reporting **high confidence `0.95`** instead of `0.15`.

Observed confidence-weighted MAE rose from `0.046721` to `0.171619`, while the median remained `0.069250` because it does not depend on self-reported confidence.

This is the main result of the run: a colony gains robustness from redundancy, but a learned coordinator must not blindly trust specialist confidence. Confidence calibration itself becomes a trainable/testable property.

## Implication for the MaleCNS experiment

The first real colony experiment should use at least three outputs per sensor specialist:

- task scalar / interpretation;
- confidence;
- novelty or surprise.

The coordinator should be trained and evaluated against both robust fixed fusion (median) and confidence-weighted fusion. Failure tests must include a **confidently wrong specialist**, because otherwise confidence weighting looks artificially strong.

The next step is to replace the synthetic reports with independently trained small adapters + frozen MaleCNS instances on one cached real channel (likely speed/yaw from comma2k19 or a synthetic CAN/IMU stream), while preserving the same aggregation metrics.
