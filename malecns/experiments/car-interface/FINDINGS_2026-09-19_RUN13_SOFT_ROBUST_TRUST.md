---
type: "Findings Record"
title: "MaleCNS Car Interface Run 13: Soft robust fusion beats hard trust gating"
description: "A simple reality-bounded bounded-influence fusion baseline substantially outperforms both fixed and learned hard probe-admission gates in the current synthetic generator, so the learned trust coordinator has not yet earned its complexity."
tags: [malecns, driving, sensor-colony, robust-fusion, soft-trust, sensor-fusion, falsification, experiment]
timestamp: 2026-09-19T05:55:00-04:00
---

# Run 13 — soft robust fusion beats hard trust gating

## Question

The Run-11 prior-art/falsification audit explicitly required a **soft robust-fusion control** before crediting a learned or MaleCNS trust coordinator. Run 12 then showed a small advantage for a learned hard admission gate over the fixed hard gate. Does that advantage survive a matched, simpler estimator that never rejects a paid probe and only bounds its influence?

## Implementation advance

`soft_trust.py` adds a modality-generic bounded-influence baseline. For each already-paid probe it computes a lawful soft weight from:

- declared specialist confidence;
- timestamp-derived freshness;
- residual to the current fused estimate built from already-observed same-modality and independent-modality summaries.

The residual term uses a Cauchy weight:

`1 / (1 + (|residual| / scale)^2)`

The final influence weight is `confidence × freshness × CauchyWeight`. The probe is **not rejected**. Its value is shrunk toward the current lawful cross-modal estimate and its downstream confidence is reduced by the same weight. Thus the experiment directly contrasts hard admission/exclusion against continuous bounded influence.

No hidden truth, injected fault identity, perfect pose, simulator geometry or future realized error enters the decision. The same primitive can be used for any pair of modalities exposing a comparable scalar/vector component, including camera/YOLO, IMU, OBD-II, GNSS, low-cost LiDAR, ultrasonic echo features or RF/Wi-Fi peer claims.

## Matched controls

The ablation retains the existing Run-12 synthetic generator and 12-specialist compute budget:

- two initial camera specialists + two initial IMU specialists;
- four additional paid camera probes + four additional paid IMU probes;
- all policies pay for the same probes;
- `pilot_only` uses only the initial 2+2 reports and verifies that soft fusion is not merely benefiting by ignoring the added specialists;
- `always_trust` admits all raw paid probes;
- `fixed_gate` is the Run-11 thresholded heuristic;
- `learned_gate` reconstructs the **frozen Run-12 model** from its recorded weights and threshold `0.20` rather than retraining it;
- `soft_robust` always retains every paid probe but bounds its influence continuously.

The soft residual scale is the only new tunable parameter. It was selected from `(0.10, 0.15, 0.22, 0.33, 0.50, 0.75)` on a disjoint 3,000-episode calibration stream using error against a later independent corroborating measurement, **not hidden-truth MAE**. The selected scale was **0.75**, with delayed-sensor calibration loss `0.112078`.

## Executed primary validation

Each profile below averages five independent seeds × 5,000 episodes = 25,000 episodes per profile at the same 20% independent high-confidence fault probability used in Run 12.

| camera-age profile | pilot only MAE | always trust MAE | fixed hard gate MAE | learned hard gate MAE | soft robust MAE |
|---|---:|---:|---:|---:|---:|
| uniform | 0.122252 ± 0.001818 | 0.108732 ± 0.001916 | 0.106566 ± 0.001425 | 0.105817 ± 0.001363 | **0.075722 ± 0.001105** |
| fresh-skewed | 0.111063 ± 0.001226 | 0.099070 ± 0.000258 | 0.096438 ± 0.000486 | 0.095997 ± 0.000249 | **0.071829 ± 0.000676** |
| stale-skewed | 0.124827 ± 0.000416 | 0.107822 ± 0.001094 | 0.104873 ± 0.000741 | 0.104013 ± 0.000876 | **0.076794 ± 0.000188** |

Relative to the frozen learned Run-12 hard gate, the soft robust baseline reduces MAE by approximately:

- **28.44%** on uniform camera age;
- **25.18%** on fresh-skewed camera age;
- **26.17%** on stale-skewed camera age.

This is much larger than the sub-1% advantage previously measured for learned hard admission over the fixed hard gate.

## Fault-rate shift

The same scale `0.75` was frozen and evaluated across fault prevalence. Each row is five seeds × 3,000 episodes on uniform camera age.

| specialist fault probability | pilot only | fixed hard gate | learned hard gate | soft robust |
|---:|---:|---:|---:|---:|
| 0% | 0.123343 | 0.100217 | 0.100755 | **0.066158** |
| 10% | 0.124208 | 0.104415 | 0.104318 | **0.070815** |
| 20% | 0.123622 | 0.107447 | 0.106735 | **0.076651** |
| 30% | 0.124393 | 0.112255 | 0.110653 | **0.083428** |

The key falsification result is the **0% fault condition**. Soft robust fusion remains much better even when no injected high-confidence specialist faults exist. Therefore its advantage is not primarily a better fault detector. In this generator it is also acting as a better estimator under ordinary noise, asynchronous age and modality disagreement.

That changes the interpretation of Runs 11–12: hard trust gating was solving a narrower problem than the underlying estimator actually needed.

## Correlated camera-failure stress test

Independent faults remain at 10%; on the listed fraction of episodes all four extra camera probes also share one strong signed bias. Each row is five seeds × 3,000 episodes.

| shared-camera-bias episodes | pilot only | always trust | fixed hard gate | learned hard gate | soft robust |
|---:|---:|---:|---:|---:|---:|
| 10% | 0.123194 | 0.114747 | 0.104133 | 0.103630 | **0.070842** |
| 30% | 0.121851 | 0.133184 | 0.101808 | 0.100314 | **0.071081** |
| 50% | 0.123340 | 0.153920 | 0.103584 | 0.100361 | **0.070817** |

The soft baseline remains stable under this particular common-mode stressor, but this should not be overgeneralized. Its reference is itself built from currently trusted observations; simultaneous correlated failures across both modalities, legitimate abrupt transitions, calibration drift and adversarially coordinated faults can still defeat residual-based robust fusion.

## Scientific interpretation

This run is a meaningful negative result for the current learned-trust direction.

The learned hard gate **has not earned its complexity yet**. A simpler, transparent, reality-bounded soft robust estimator dominates it by roughly 25–28% MAE in the primary conditions and by similarly large margins under the tested shifts. The correct next scientific comparison is therefore no longer “fixed hard gate versus learned hard gate versus MaleCNS coordinator.” It is:

`strong robust estimator → adaptive robust estimator → learned baseline → MaleCNS coordinator`

A MaleCNS trust coordinator should only receive credit if it can beat or complement this stronger statistical control under matched compute and lawful signals.

The result also suggests separating two jobs:

1. **estimation** — continuously fuse noisy/stale modalities with bounded influence;
2. **resource/trust control** — decide which sensors/specialists to activate, probe, quarantine or communicate with when robust estimation alone is insufficient.

The second job remains a plausible role for a MaleCNS coordinator, especially when compute/latency/energy budgets, missing modalities, peer-token reputation or active sensing actions matter. But the current synthetic evidence says not to use a learned binary gate merely to solve ordinary robust fusion.

## Reality boundary

Everything available to `soft_robust` at decision time is reproducible from an ordinary real car plus phone/declared sensors: specialist values, timestamps, confidence metadata and cross-modal residuals. Hidden synthetic truth is used only by the harness to generate samples and report evaluation MAE after decisions are complete.

The one new parameter, residual scale, is calibrated with delayed independent sensor corroboration. A real implementation can use the same pattern with, for example, camera ego-motion ↔ phone IMU yaw, OBD wheel speed ↔ GNSS speed, LiDAR range trend ↔ ultrasonic echo trend, or a peer RF/Wi-Fi hazard token ↔ later local sensor confirmation.

## Validation and cache status

The executed validation used repository-equivalent Python standard-library code and the frozen Run-12 weights. No dataset, model weight, CARLA artifact, simulator asset or package was downloaded, so there was **no heavyweight cache miss**.

The repository already contains the dedicated 2026-09-19 MaleCNS embodied-control prior-art pass and the 2026-09-19 autonomous-driving dataset/benchmark/safety review in `RESEARCH_2026-09-19.md`; this round therefore focused on the falsification control explicitly required by today's audit rather than duplicating the daily search.

## Next experiment

Two follow-ups now have higher priority than another learned hard gate:

1. replace the synthetic corroborator with a small cached synchronized real-world pair such as **phone IMU yaw + camera ego-motion** or **OBD wheel speed + phone GNSS speed**, and test the same soft estimator under timestamp stalls, packet loss and calibration bias;
2. add a second robust-estimation family (for example Huber/Tukey or an innovation-covariance-normalized adaptive scale) so `scale=0.75` is not accidentally exploiting one generator-specific normalization.

Only after those controls should a MaleCNS coordinator be tested for incremental value in trust/resource allocation.
