---
type: "Findings Record"
title: "MaleCNS colony freshness weighting under asynchronous sensor latency"
description: "Deterministic ablation testing whether report-age metadata protects a sensor colony from stale-but-confident specialist outputs."
tags: [malecns, driving, sensor-fusion, multi-agent, latency, robustness, ablation]
timestamp: 2026-09-18T20:54:00-04:00
---

# Run 4 — freshness as a first-class coordinator signal

## Status

**Executed.** This is a deterministic synthetic architecture experiment, not a trained-MaleCNS result.

Ten unit tests passed for the colony contract and fusion baselines. The ablation used only Python standard-library code. No dataset, CARLA asset, model weight, or external dependency was downloaded, so this run had no cache misses.

## Motivation

The previous run addressed specialists that are confidently wrong because their interpretation is bad. A different failure exists in a real retrofit car: a specialist may be internally correct, mutually consistent, and highly confident while describing sensor state that is simply too old.

Phone camera, IMU, GNSS, OBD/CAN, RF, ranging, and learned transducers are asynchronous and have different acquisition, transport, batching, and inference latencies. Cross-specialist consensus alone cannot reliably detect stale data, especially when several specialists share the same delayed modality.

The new hypothesis is modest and testable: **report age should be exposed as a lawful scalar to the coordinator, and fixed freshness-aware fusion should be a baseline that any learned MaleCNS coordinator must beat.**

## Implementation

`SpecialistReport` now contains `age_ms`, validated as non-negative. This value is real-world reproducible from acquisition and processing timestamps and therefore does not violate the reality boundary.

`colony.py` adds:

- `freshness_weighted_value()`: confidence weighting with exponential age decay;
- `age_spread_ms()`: oldest-minus-newest report age as another tiny coordinator signal.

The default freshness half-life is 150 ms. This is not claimed as an optimal vehicle-control constant; it is a fixed baseline parameter for the synthetic ablation.

## Synthetic experiment

`colony_freshness_ablation.py` models five specialists observing a changing scalar that could stand for yaw rate, speed error, visual TTC, or another real driving quantity.

Per trial:

- true scalar: uniform in `[-1, 1]`;
- scalar velocity: uniform in `[-3, 3]` units/s;
- fresh reports: age 10–60 ms;
- stale reports: age 450–900 ms;
- measurement noise: sigma `0.03`;
- every specialist self-reports confidence `0.9`, including stale ones;
- 10,000 deterministic trials per condition.

Five fusion policies are compared: one specialist, median, raw confidence weighting, robust consensus weighting, and freshness weighting with a 150 ms half-life.

## Observed results

| Stale probability | Single MAE | Median MAE | Confidence MAE | Consensus MAE | Freshness MAE |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.0 | 0.058314 | 0.054695 | 0.054358 | 0.054457 | 0.053227 |
| 0.2 | 0.251986 | 0.114252 | 0.246976 | 0.100470 | 0.069899 |
| 0.4 | 0.447688 | 0.331620 | 0.441725 | 0.305154 | 0.107660 |
| 0.6 | 0.632815 | 0.644444 | 0.633511 | 0.619921 | 0.197160 |
| 0.8 | 0.820629 | 0.903874 | 0.828281 | 0.902141 | 0.432450 |

At 40% stale specialists, freshness weighting reduces MAE from `0.441725` for raw confidence weighting to `0.107660`, about **75.6% lower error** in this synthetic regime. At 60% stale specialists the reduction is about **68.9%**.

Importantly, freshness weighting is also slightly best in the zero-staleness condition here, but the difference is tiny (`0.053227` versus `0.054358` for confidence weighting) and should not be overinterpreted.

## Interpretation

The useful result is not that exponential age decay is the final fusion rule. It is that **time itself belongs in the sensor-colony state**.

Consensus and confidence answer different questions:

- confidence: does this specialist trust its own interpretation?
- consensus: do other specialists agree?
- freshness: is this report still temporally relevant to the current vehicle state?

A learned coordinator should therefore receive at least compact timing signals alongside value/confidence/novelty/agreement, for example:

- report age;
- age spread within a modality;
- fraction of reports older than a task-specific threshold;
- acquisition-to-inference latency;
- inter-arrival jitter;
- missing-sample duration.

All are available on a real phone/vehicle computer and can be emitted as scalar channels without simulator privilege.

## Prior-art boundary

A claim-level audit performed immediately after RUN4 materially narrows what this experiment can support as novelty. See [`audits/prior-art/malecns-freshness-fusion-2026-09-19.md`](../../audits/prior-art/malecns-freshness-fusion-2026-09-19.md).

The following ingredients have clear public antecedents before RUN4's conservative public cutoff (`2026-09-19T00:57:33Z`):

- explicit age/freshness variables for rejecting stale information in distributed estimation (Age-of-Information literature);
- timestamp-offset features for robust autonomous-driving sensor fusion under staleness (Zoox, 2025);
- age-aware decay plus learned attention/gating based on temporal freshness (AoI-FusionNet, 2026);
- Age-of-Sensing as an active learned trust gate in asynchronous sensor fusion (TA-Fusion, 2026);
- quality/confidence × freshness × reliability fusion, including continuous **exponential** freshness decay from sensor latency, in the public Ananta Meridian implementation (April 2026).

In particular, RUN4's `confidence * 2 ** (-age / half_life)` rule is not a new class of sensor-fusion algorithm: it is an exponential age-decay weighting rule, mathematically equivalent up to parameterization to `exp(-age / tau)` freshness factors already used publicly in multisensor fusion.

Accordingly, RUN4 should be read as an **executed MaleCNS-specific benchmark and failure-mode diagnostic**. Its project-specific content is the reality-bounded `SpecialistReport` timing contract, the exact deterministic stale-specialist ablation and numerical result, and the planned matched comparison against a learned MaleCNS coordinator. No pre-cutoff source was located in the recorded searches that combines that entire MaleCNS-specific conjunction; this is a bounded search result, not a claim of universal priority.

## Limits

This experiment uses a deliberately simple linear-in-time latent scalar. It does not model realistic vehicle dynamics, correlated bus delays, camera batching, sensor clock drift, or trained MaleCNS specialists. The observed MAE improvements are therefore architecture diagnostics, not autonomous-driving performance claims.

## Next experiment

The next cheap step should introduce **clock skew and correlated modality stalls**. In particular, test cases where an entire group of specialists receives the same delayed camera or OBD frame: their values will agree with each other, so consensus can be high while all are stale. Then compare fixed freshness weighting against a learned coordinator that receives age, age spread, confidence, consensus, and novelty.

After that, replay the same timing contract over one small cached real-driving shard before moving to CARLA.
