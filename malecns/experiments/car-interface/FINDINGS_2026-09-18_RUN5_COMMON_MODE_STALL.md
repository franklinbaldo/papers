---
type: "Findings Record"
title: "MaleCNS colony common-mode sensor stall and cross-modal rescue"
description: "Deterministic ablation showing that redundant flies on one stalled sensor cannot recover missing information, while a fresh independent modality plus hierarchical freshness fusion can."
tags: [malecns, driving, sensor-fusion, multi-agent, common-mode-failure, latency, robustness, ablation]
timestamp: 2026-09-18T21:54:00-04:00
---

# Run 5 — common-mode sensor stall and cross-modal rescue

## Status

**Executed.** This is a deterministic synthetic architecture experiment, not a trained-MaleCNS result.

The colony contract validation passed 12/12 assertions, including the new modality-summary invariants. The ablation used only Python standard-library code. No dataset, CARLA asset, model weight, or external dependency was downloaded, so this run had no cache miss.

## Question

Previous runs showed that several specialist flies can help against independent specialist errors and that report age is a useful signal. A harder failure exists when multiple flies share the same physical sensor.

If the camera pipeline stalls, every camera specialist can receive the same old frame. Five camera flies may then agree with each other, report high confidence, and still all describe the past. Adding more flies on that sensor cannot recreate information that never arrived.

The testable question is therefore:

> Does sensor-colony robustness require *modality diversity* in addition to specialist redundancy?

## Implementation advance

`SpecialistReport` now has an optional declared `modality`, such as `camera` or `imu`.

`colony.py` adds `summarize_modality()`, which collapses redundant specialists estimating the same semantic scalar from one declared modality into a modality-level report using robust medians for:

- value;
- self-reported confidence;
- novelty;
- report age.

The function refuses mixed modalities or mixed semantic channels. It uses only specialist outputs and acquisition-age metadata that are reproducible in a real car. No simulator truth crosses the reality boundary.

This creates an explicit hierarchy:

```text
physical sensor
  -> several MaleCNS specialists
  -> robust modality summary
  -> higher-level coordinator
  -> actuator adapter
```

## Synthetic experiment

`colony_common_mode_stall_ablation.py` models one fast-changing scalar that both camera-derived perception and IMU could estimate, for example yaw rate or a normalized motion-error signal.

Per trial:

- true scalar: uniform in `[-1, 1]`;
- scalar velocity: uniform in `[-3, 3]` units/s;
- five camera specialists;
- three IMU specialists;
- camera specialists share a common sensor age, with only +/-5 ms jitter;
- healthy camera age: 20–60 ms;
- stalled camera age: 450–900 ms;
- camera noise sigma: 0.025;
- IMU age: 5–30 ms;
- IMU noise sigma: 0.04;
- camera self-confidence: 0.90;
- IMU self-confidence: 0.85;
- 10,000 deterministic trials per condition.

The camera stall is a **common-mode fault**: when it occurs, all five camera flies observe the same temporally displaced physical stream.

Five policies are compared:

1. one camera specialist;
2. median of five camera specialists;
3. freshness weighting among five camera specialists;
4. median of camera-summary + IMU-summary;
5. freshness weighting across camera-summary + IMU-summary.

## Observed results

Mean absolute error:

| Camera stall probability | 1 camera | 5 camera median | 5 camera freshness | Hierarchy median | Hierarchy freshness |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.0 | 0.063644 | 0.061214 | 0.060952 | 0.044645 | 0.044011 |
| 0.2 | 0.250483 | 0.248707 | 0.248592 | 0.137982 | 0.050035 |
| 0.4 | 0.439423 | 0.438321 | 0.438205 | 0.232601 | 0.056966 |
| 0.6 | 0.621473 | 0.620713 | 0.620642 | 0.323751 | 0.063432 |
| 0.8 | 0.823548 | 0.823080 | 0.822973 | 0.424803 | 0.071077 |
| 1.0 | 1.016457 | 1.015925 | 1.015861 | 0.521046 | 0.077651 |

The important negative result is immediate: **five camera specialists do almost nothing against a camera-level stall**. At 60% stall probability, one camera gives MAE `0.621473`, while five-camera median gives `0.620713` and five-camera freshness gives `0.620642`. Redundant cognition cannot replace missing physical information.

The independent fresh modality changes the picture. At 60% camera stall probability, hierarchical freshness fusion reaches MAE `0.063432`, about **89.8% lower error than the five-camera median** and about **80.4% lower than hierarchy without freshness weighting**.

Even with the camera stalled on every trial, hierarchical freshness produces MAE `0.077651` versus `1.015925` for five-camera median, about **92.4% lower error** in this synthetic regime.

## Interpretation

This run separates two kinds of redundancy that should not be conflated:

- **specialist redundancy**: several MaleCNS instances interpret the same physical stream; useful against individual training/inference failures;
- **modality redundancy**: independent physical streams estimate overlapping useful quantities; necessary against common-mode sensor failure.

The architecture should therefore avoid allocating all additional compute to more flies on the same sensor. A better colony has both population redundancy *and* physical diversity.

For the coordinator, `modality`, modality-summary age, confidence, novelty, and cross-modality disagreement are legitimate low-bandwidth signals. A learned MaleCNS coordinator should eventually beat the fixed hierarchical freshness baseline.

## Prior-art boundary

The generic reliability conclusions above are **not** new. Common-cause/common-mode failure defeating identical redundancy is established reliability engineering; sensor diversity and independent sensing principles are established mitigations. In autonomous-driving literature, modality-specific processing, quality/reliability-aware routing, and graceful degradation under missing/corrupted modalities also predate RUN5.

The claim-level audit at [`audits/prior-art/malecns-common-mode-stall-2026-09-19.md`](../../audits/prior-art/malecns-common-mode-stall-2026-09-19.md) documents the temporal boundary and sources. In particular, NIST (1993) already describes a common sensor defeating redundant processors; NASA/IEEE work on common-cause failures formalizes the redundancy limit and role of diversity; and a 2026 autonomous-vehicle systematic review states that redundancy should be judged by independence of evidence rather than sensor count.

What RUN5 contributes is narrower: an **executed MaleCNS-specific architecture diagnostic** that instantiates that established principle inside the repository's specialist-colony contract, quantifies same-camera redundancy versus cross-modal rescue in a deterministic synthetic regime, preserves reality-bounded modality/age metadata, and defines a concrete benchmark for a future learned MaleCNS coordinator. The numerical RUN5 results remain results of this experiment; they do not establish invention of common-mode-resilient or modality-diverse sensor fusion.

No exact pre-cutoff source was located that combines measured-connectome MaleCNS reservoirs, several specialists per physical modality, the repository's robust modality-summary contract, the exact camera-stall/IMU-rescue ablation, and the planned matched-compute learned MaleCNS coordinator. That is a bounded negative search result, not an assertion of exhaustive novelty.

## Next experiment

Replace the synthetic paired modalities with a cacheable real-data slice where overlapping signals exist, preferably vehicle yaw/speed derived independently from IMU and CAN/GNSS. Then train several actual MaleCNS specialists per modality and inject correlated sensor stalls after acquisition. The key comparison should preserve matched total compute:

- more flies on one modality;
- fewer flies spread across independent modalities;
- fixed hierarchical fusion;
- learned MaleCNS coordinator.

That experiment would directly test whether the common-mode result survives contact with real sensor dynamics.
