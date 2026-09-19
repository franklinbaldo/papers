---
type: "Findings Record"
title: "MaleCNS Car Interface Run 14: Age-normalized Huber fusion improves the robust baseline"
description: "A second reality-bounded robust-estimation family, selected only by delayed sensor corroboration, improves on the frozen Run-13 fixed-scale Cauchy baseline across camera-age, fault-rate, and common-mode camera-bias shifts."
tags: [malecns, driving, sensor-colony, robust-fusion, huber, freshness, sensor-fusion, experiment]
timestamp: 2026-09-19T06:56:00-04:00
---

# Run 14 — age-normalized Huber fusion improves the robust baseline

## Question

Run 13 established a much stronger baseline than the hard trust-gating line: fixed-scale Cauchy soft fusion with residual scale `0.75`. The remaining concern was that this one kernel and one scale could be exploiting the normalization of the synthetic generator. The next required control was therefore another robust-estimation family with a scale that can respond to a physically observable property rather than to hidden fault identity.

This run asks whether **Huber bounded influence with a freshness-dependent residual radius** improves on the frozen Run-13 Cauchy estimator without exposing privileged simulator state.

## Concrete implementation advance

`adaptive_soft_trust.py` adds `age_normalized_huber_weight()` and `soften_probe_huber()`.

The decision-time inputs remain exactly reality-bounded:

- specialist scalar/vector component;
- declared confidence;
- timestamp-derived age/freshness;
- same-modality reports already observed;
- an independently sourced modality summary over the same semantic channel.

The effective Huber residual radius is

`effective_scale = max(min_scale, base_scale * freshness ** age_power)`

and the final influence is

`confidence × freshness × HuberWeight(residual / effective_scale)`.

Thus freshness plays two distinct roles. It directly discounts old information, as in Run 13, and it also makes the robust residual test stricter for old information. This is a physical prior: when the world can change during latency, a stale measurement should need closer agreement with a current independent modality before it can move the fused estimate by the same amount.

No truth value, injected-fault flag, perfect pose, simulator geometry, object truth, future error, or CARLA-only state enters the API.

## Calibration discipline

The Huber method has two new hyperparameters, `base_scale` and `age_power`. They were selected on a disjoint 3,000-episode calibration stream against a later independent corroborating measurement, never against hidden-truth MAE.

Grid:

- `base_scale ∈ {0.18, 0.25, 0.35, 0.50, 0.75, 1.00}`;
- `age_power ∈ {0.0, 0.5, 1.0}`.

Selected configuration:

- `base_scale = 0.35`;
- `age_power = 1.0`;
- delayed-sensor calibration loss = **0.110674**.

The fixed-Huber arm uses the same selected base scale with `age_power = 0.0`, isolating the value of the age-normalized radius. The Run-13 control remains frozen at Cauchy scale `0.75`.

## Executed primary validation

Each primary condition is five independent seeds × 5,000 episodes = 25,000 episodes, with the same 20% independent high-confidence specialist-fault process as Run 13.

| camera-age profile | Run-13 fixed Cauchy MAE | fixed Huber MAE | age-normalized Huber MAE | improvement vs Run 13 |
|---|---:|---:|---:|---:|
| uniform | 0.076195 ± 0.001151 | 0.075546 ± 0.001211 | **0.074425 ± 0.001227** | **2.32%** |
| fresh-skewed | 0.073215 ± 0.000496 | 0.072685 ± 0.000474 | **0.071380 ± 0.000504** | **2.51%** |
| stale-skewed | 0.075291 ± 0.001354 | 0.074556 ± 0.001288 | **0.074062 ± 0.001337** | **1.63%** |

The paired seed-level Run-13-minus-Run-14 MAE differences were positive in every seed. Approximate 95% t intervals for the mean paired improvement were:

- uniform: `+0.001770` [`+0.001634`, `+0.001906`];
- fresh-skewed: `+0.001835` [`+0.001732`, `+0.001938`];
- stale-skewed: `+0.001229` [`+0.001155`, `+0.001303`].

The decomposition matters. Fixed Huber is already slightly better than fixed Cauchy, but shrinking the Huber radius with age improves fixed Huber by another approximately **1.48% / 1.80% / 0.66%** across the three profiles. The gain is therefore not only a kernel substitution.

## Fault-rate shift

The selected Huber parameters are frozen. Each row is five seeds × 3,000 episodes with uniform camera age.

| specialist fault probability | Run-13 fixed Cauchy | age-normalized Huber | improvement |
|---:|---:|---:|---:|
| 0% | 0.066793 | **0.064843** | **2.92%** |
| 10% | 0.070600 | **0.068848** | **2.48%** |
| 20% | 0.077100 | **0.075275** | **2.37%** |
| 30% | 0.083475 | **0.081490** | **2.38%** |
| 40% | 0.091522 | **0.089409** | **2.31%** |

The 0% row is important again: the improvement is present even without injected specialist faults. The age-normalized Huber method is not merely a better fault detector; it is a better estimator for the current synthetic mixture of noise, latency, confidence and cross-modal disagreement.

## Common-mode camera-bias shift

Independent specialist faults remain at 10%. On the listed fraction of episodes all four extra camera probes share one strong signed bias. Each row is five seeds × 3,000 episodes.

| shared-camera-bias episodes | Run-13 fixed Cauchy | age-normalized Huber | improvement |
|---:|---:|---:|---:|
| 10% | 0.070829 | **0.068770** | **2.91%** |
| 30% | 0.071370 | **0.069209** | **3.03%** |
| 50% | 0.071748 | **0.069413** | **3.25%** |
| 70% | 0.071792 | **0.068936** | **3.98%** |

The direction strengthens as the camera common-mode stress becomes more frequent. This is plausible because old camera measurements with a large residual receive both the ordinary freshness discount and a tighter Huber radius. It should not be generalized to simultaneous correlated failure of both modalities or to abrupt true state changes that legitimately create cross-modal disagreement.

## Scientific interpretation

Run 14 strengthens the negative result against prematurely assigning ordinary sensor-fusion work to a learned or MaleCNS trust coordinator. A transparent statistical estimator became better again when the robust residual was made explicitly age-aware.

The current evidence ladder is now:

`hard admission gates << fixed soft robust fusion < age-normalized Huber soft fusion`

For this generator, a learned coordinator has not yet earned the right to replace robust estimation. Its more plausible remaining jobs are actions that a static estimator cannot perform, such as:

- decide whether to spend compute on another specialist;
- trigger active ultrasonic/LiDAR/RF measurements;
- quarantine or re-query a modality after persistent inconsistency;
- schedule local-LLM semantic transduction only when expected value exceeds latency/energy cost;
- negotiate/request multi-agent Wi-Fi tokens and learn peer reliability from later local corroboration.

Those are genuine control/resource decisions rather than ordinary robust averaging.

## Reality boundary and transfer to modular channels

The mechanism is modality-generic. It can be applied whenever two declared real-car-compatible channels estimate a comparable quantity:

- camera ego-motion ↔ Android IMU yaw;
- OBD-II wheel speed ↔ Android GNSS speed;
- low-cost LiDAR range trend ↔ active ultrasonic echo range trend;
- YOLO-derived relative-motion scalar ↔ camera optical-flow scalar;
- Wi-Fi/RF peer hazard token confidence ↔ later local camera/LiDAR/ultrasonic confirmation;
- local-LLM semantic scalar ↔ the lower-level sensor evidence from which it was transduced.

The agent never receives simulator-only truth merely because the simulator can provide it.

## Validation and cache status

The numerical validation was executed in the current environment with a repository-equivalent standard-library harness matching the committed sampling, fault-injection, freshness fusion, Run-13 Cauchy rule and new Huber rule. Outbound DNS is unavailable in the execution shell, so the GitHub repository could not be cloned there; repository edits were made through the GitHub connection instead. The experiment intentionally required no dataset, CARLA build, model weights, simulator asset or package download, so there was **no heavyweight cache miss**.

The repository already contains today's dedicated MaleCNS embodied-control prior-art pass and autonomous-driving dataset/benchmark/safety review in `RESEARCH_2026-09-19.md`, including explicit MaleCNS driving/robotics distinctions plus PAVE, Waymo, NHTSA and Tesla evidence. This round therefore did not duplicate that daily research pass.

## Next discriminating experiment

The synthetic line has now extracted enough value from estimator design that the next priority should be a **small persistent real-data cache** rather than another synthetic trust heuristic.

The preferred first pair is `Android/phone IMU yaw ↔ camera ego-motion`, with `OBD-II wheel speed ↔ phone GNSS speed` as the second. Pin the raw slice by source version + checksum, materialize one synchronized scalar stream once, and then reuse it across:

1. fixed Cauchy;
2. fixed Huber;
3. age-normalized Huber;
4. a learned coordinator;
5. eventually a frozen MaleCNS coordinator.

Stress the cached slice with timestamp stalls, packet loss, calibration bias and modality dropout while keeping every agent input reproducible from the physical sensor stream. A MaleCNS-specific advantage should only be claimed if it survives that ladder plus matched random/rewired/connectome controls.