---
type: "Findings Record"
title: "MaleCNS colony dynamic specialist recruitment under fixed compute"
description: "Deterministic ablation of lawful freshness-and-disagreement recruitment under a fixed 12-instance budget."
tags: [malecns, driving, sensor-fusion, dynamic-recruitment, compute-budget, ablation]
timestamp: 2026-09-18T22:57:00-04:00
---

# Run 6 — dynamic specialist recruitment under fixed compute

## Status

**Executed.** This is a deterministic synthetic architecture diagnostic, not a trained-MaleCNS or autonomous-driving result. Colony tests passed **15/15** after adding the recruitment contract. The run used only Python standard library; no dataset, CARLA asset, model weight, or external dependency was downloaded.

## Question and implementation

RUN5 showed that more flies cannot recover a commonly stale physical stream. RUN6 asks whether a fixed compute budget can be moved online toward the modality where another specialist is more useful.

`colony.py` now adds:

- `recruitment_score()`: within-modality disagreement multiplied by exponential freshness, with a small uncertainty floor;
- `allocate_recruitment_slots()`: largest-remainder allocation of a fixed extra-specialist budget.

The allocator sees only lawful specialist reports. It never sees truth, realized error, or a hidden sensor-fault flag. All candidate modalities must estimate the same normalized semantic channel.

## Experiment

Every policy gets 12 fly instances. Dynamic recruitment starts with two camera pilots and two IMU pilots, then allocates eight extra slots. Controls are fixed matched-compute splits: camera-heavy 8/4, balanced 6/6, and IMU-heavy 4/8.

Camera age is 20–60 ms when healthy and 450–900 ms during common-mode stall. IMU age is 5–30 ms. Specialist inference noise is independent and includes stochastic bursts. Each condition uses 10,000 deterministic trials.

## Observed results

Mean absolute error; lower is better.

| Camera stall | Camera 8/4 | Balanced 6/6 | IMU 4/8 | Dynamic | Extra camera | Extra IMU |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.0 | 0.054558 | 0.051145 | **0.050317** | 0.051358 | 2.7892 | 5.2108 |
| 0.2 | 0.063760 | 0.059462 | **0.057909** | 0.058729 | 2.2906 | 5.7094 |
| 0.4 | 0.073440 | 0.068562 | **0.065889** | 0.066309 | 1.8120 | 6.1880 |
| 0.6 | 0.082171 | 0.076143 | **0.072869** | 0.073216 | 1.3330 | 6.6670 |
| 0.8 | 0.091750 | 0.084480 | 0.080925 | **0.080786** | 0.7856 | 7.2144 |
| 1.0 | 0.100634 | 0.093255 | 0.089087 | **0.088553** | 0.3321 | 7.6679 |

The allocator reacts correctly to physical staleness without being told that the camera failed: mean extra camera allocation falls from `2.7892` slots at 0% stall to `0.3321` at 100% stall.

The important result is negative: this hand-written dynamic heuristic does **not** dominate a tuned fixed allocation. The IMU-heavy split is 0.48–2.07% better through 0–60% stall. Dynamic becomes only slightly better at 80% and 100% stall. Across the six equally weighted conditions, MAE is `0.069499` for IMU-heavy versus `0.069825` for dynamic, so dynamic is about **0.47% worse** on average.

## Interpretation

Routing in the right direction is not enough. Freshness tells the colony where **not** to spend compute, while disagreement indicates specialist-level uncertainty, but the current heuristic does not estimate the *marginal value* of one more fly. A learned coordinator should therefore receive feedback about whether recruiting another specialist actually improved downstream prediction/control, under an explicit compute/latency price.

Dynamic expert routing and adaptive resource allocation are established prior art; this run claims no invention of those ideas. Its role is a MaleCNS-specific, reality-bounded, matched-compute baseline that a learned MaleCNS recruiter must beat.

## Real-data bridge and cache plan

`commaai/comma2k19` remains the next data source: its public example contains CAN speed/steering/wheel-speed, IMU gyro/accelerometer, and GNSS streams, sufficient for overlapping lawful motion channels without exposing global-pose truth to the agent. A future run should pin one small shard by URL + checksum in a persistent cache, derive one aligned local slice, and reuse it for all specialist ablations.

Binary dataset acquisition was unavailable in this execution environment, so no real-data result is claimed here and no repeated download occurred.

## Next experiment

On a cached real-data slice, compare at equal total compute:

- best fixed split selected on training data;
- current freshness + disagreement heuristic;
- a small learned non-connectome recruiter;
- a MaleCNS recruiter;
- random/rewired-connectome recruiter controls.

Success requires improved unseen-regime performance large enough to pay for routing complexity, not merely a changing allocation.
