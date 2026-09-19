---
type: "Findings Record"
title: "MaleCNS Car Interface Run 12: Learned trust from delayed physical corroboration"
description: "A tiny generic trust gate trained only from delayed independent sensor corroboration modestly beats the fixed probe-trust heuristic at 20–30% specialist fault rates and under correlated camera faults, but is slightly worse when specialist faults are absent."
tags: [malecns, driving, sensor-colony, learned-trust, delayed-supervision, sensor-fusion, robustness, experiment]
timestamp: 2026-09-19T04:53:00-04:00
---

# Run 12 — learned trust from delayed physical corroboration

## Question

Run 11 showed that a fixed reality-bounded probe-then-trust gate can protect the actuator-facing fusion path when paid specialists are confidently wrong. Can a tiny learned gate improve on that hand-written rule **without receiving simulator truth as either a decision-time input or a training label**?

## Implementation advance

`delayed_trust.py` adds a modality-generic 11-feature trust vector and a tiny online logistic baseline. No feature encodes a specific sensor name, so the same gate contract can be reused for camera/YOLO, IMU, OBD-II, GPS, ultrasonic, low-cost LiDAR, RF/Wi-Fi or a local semantic transducer when two modalities expose a compatible scalar/vector component.

Decision-time features are derived only from reports already acquired:

- candidate confidence;
- candidate freshness / timestamp age;
- residual to the already-trusted same-modality summary;
- residual to an independent modality summary;
- residual to the current fused estimate;
- within-modality disagreement;
- disagreement between the two trusted modality summaries;
- confidence × freshness;
- freshness × cross-modal agreement.

There is no hidden failure flag, perfect pose, simulator geometry, object truth or realized future error in the feature vector.

The training teacher is deliberately different from the evaluation truth. After the decision-time feature vector is frozen, the harness generates a later independent corroborating measurement with Gaussian noise σ=0.10. The binary training label is whether the candidate lies within 0.30 of that corroborating measurement. This stands for a deployable physical teacher such as camera ego-motion later checked against IMU yaw, or visual speed checked against OBD/GNSS speed. The model receives the sampled corroboration-derived label only; it never receives the latent synthetic truth.

A later prior-art/falsification audit makes an important boundary explicit: **the current corroborator itself is generated from the same latent synthetic truth plus independent Gaussian noise**. The learner is not handed truth, but the harness still gives the teacher-generation process privileged access to truth. RUN12 therefore tests the learning interface under an idealized independent proxy teacher; it does not yet establish that a real physical corroborator is unbiased, independent, correctly time-aligned, or sufficient.

`colony_delayed_trust_ablation.py` retains the Run-11 matched budget: two trusted camera specialists + two trusted IMU specialists, then four paid camera probes + four paid IMU probes. Every policy therefore pays for the same 12-specialist compute budget.

## Training and lawful threshold calibration

Training:

- 80,000 uniform-age synthetic episodes;
- 8 delayed-supervision updates per episode;
- 640,000 online logistic updates;
- 20% independent high-confidence specialist fault probability;
- learning rate 0.03, L2=0.001;
- training seed `2026091912`.

The learned weights after the executed run were:

`[-0.556652302, 0.015637646, 0.417766738, 0.853379985, -1.091529353, -0.536889066, -6.645120574, 0.368008312, -0.216254525, 0.706676814, 3.858181588]`

The admission threshold was **not** tuned against hidden-truth MAE. A disjoint 12,000-episode calibration stream evaluated thresholds 0.10–0.50 in steps of 0.02 using only final error against another delayed independent corroborating measurement. The selected threshold was **0.20**, with calibration delayed-sensor loss `0.130570`.

The same qualification applies to calibration: that second corroborating measurement is also an idealized synthetic proxy generated from the latent episode truth. This avoids direct target leakage into the learner, but does not emulate the error structure of a real sensor pair.

## Primary executed validation

Each profile below averages five independent seeds × 10,000 episodes = 50,000 episodes per profile. The injected specialist-fault probability is 20%.

| camera-age profile | always trust MAE | fixed Run-11 gate MAE | learned delayed gate MAE | fixed admission | learned admission |
|---|---:|---:|---:|---:|---:|
| uniform | 0.108721 ± 0.001040 | 0.106985 ± 0.000880 | **0.106140 ± 0.000778** | 0.5249 | 0.6133 |
| fresh-skewed | 0.098666 ± 0.000596 | 0.096526 ± 0.000810 | **0.095914 ± 0.000705** | 0.6248 | 0.6844 |
| stale-skewed | 0.106009 ± 0.000687 | 0.103866 ± 0.000638 | **0.102880 ± 0.000619** | 0.4426 | 0.5435 |

Relative to the fixed Run-11 gate, the learned gate reduced MAE by approximately:

- **0.79%** on uniform camera age;
- **0.63%** on fresh-skewed camera age;
- **0.95%** on stale-skewed camera age.

Relative to automatically trusting every paid probe, the reductions were approximately 2.37%, 2.79% and 2.95%, respectively.

The learned policy actually admits more reports than the fixed heuristic. Its improvement therefore does not come from simply becoming stricter; it appears to reject a more selective subset while preserving more useful reports.

The nominal learned-vs-fixed effect is small enough that the next confirmatory run should report **paired seed-level deltas and confidence/bootstrap intervals for the difference**, not only separate across-seed standard deviations. A predeclared practical-equivalence margin should determine whether a sub-1% gap is scientifically meaningful.

## Fault-rate distribution shift

The gate was trained once at 20% independent specialist faults, then frozen. The same learned threshold 0.20 was evaluated under other fault rates on uniform camera age. Each row is five seeds × 5,000 episodes.

| specialist fault probability | fixed gate MAE | learned gate MAE | learned vs fixed |
|---:|---:|---:|---:|
| 0% | **0.100704** | 0.101169 | **−0.46%** |
| 10% | 0.104183 | **0.104152** | +0.03% |
| 20% | 0.107221 | **0.106397** | +0.77% |
| 30% | 0.111617 | **0.109833** | +1.60% |

This is an important negative boundary. The learned gate is **not universally superior**: when specialist faults are absent, it is about 0.46% worse than the fixed gate. At 10% the difference is effectively negligible at this scale. Its advantage grows as confidently wrong specialists become common.

## Correlated camera-failure stress test

Run 11 injected specialist faults independently. This run also tested an organ-level failure mode: on a configurable fraction of episodes, all four extra camera probes share the same signed high-confidence bias. Independent probe faults remain at 10% for the other probes. The learned gate was not retrained for this failure mode.

Each row is five seeds × 5,000 episodes.

| episodes with shared camera bias | always trust MAE | fixed gate MAE | learned gate MAE | learned vs fixed |
|---:|---:|---:|---:|---:|
| 10% | 0.114812 | 0.103943 | **0.103274** | +0.64% |
| 30% | 0.133849 | 0.103052 | **0.101281** | +1.72% |
| 50% | 0.155603 | 0.104418 | **0.101272** | +3.01% |

The result is encouraging but narrow: a gate trained only on independent faults transfers modestly to this synthetic common-mode camera failure. It does not prove robustness to real camera blindness, synchronized frame stalls, calibration drift or adversarial perception errors. Those require distinct stressors.

A stronger common-cause test must also corrupt the **trusted reference and/or delayed corroborator**. In the executed stressor, the extra camera probes share a bias but the synthetic teacher remains an independent `truth + Gaussian noise` source. Source-dependence literature shows that agreement is not independent evidence when sources share a failure or copy the same wrong value.

## Prior-art and falsification boundary

The dedicated audit is [`audits/prior-art/malecns-delayed-trust-2026-09-19.md`](../../audits/prior-art/malecns-delayed-trust-2026-09-19.md).

Its main boundary is narrower than the original interpretation:

- local physical corroboration of peer reports predates RUN12 (e.g. radar verification of announced VANET positions in 2007/2008);
- post-message behavior as later evidence predates RUN12 (Ruj et al., 2011);
- source trust/reliability inferred without an external oracle is established truth-discovery machinery (TruthFinder and heterogeneous truth discovery);
- context-aware learned vehicle trust predates RUN12 (TROVE, 2020);
- source dependence/correlated error is a known failure mode of naive corroboration;
- realistic proxy-label error is commonly instance-dependent rather than independent Gaussian noise.

No pre-cutoff work was located with the full RUN12 MaleCNS/budget/feature/training/calibration/ablation conjunction. That is a bounded negative search result, not a claim of being first.

## Interpretation

The useful advance is not merely that a logistic model beats a scalar rule by less than one percent in the nominal 20% condition. The defensible result is narrower: **within this synthetic harness, a trust-admission model can be trained from an idealized delayed corroboration channel without giving the learner the latent truth or fault flag directly**.

That supplies a candidate deployment pattern to test on real sensors:

`pay to observe → decide provisionally → wait for an independently measured consequence/corroboration → update trust`

For a real car, examples include:

- camera yaw / lane-motion estimate → later IMU yaw-rate corroboration;
- visual or GPS speed estimate → OBD wheel-speed corroboration;
- low-cost LiDAR range change → ultrasonic echo-time trend;
- on-device YOLO obstacle-motion estimate → later optical-flow / IMU / vehicle-response consistency;
- Wi-Fi/RF peer token claiming a hazard → later local sensor confirmation before increasing that peer's trust.

The last pattern is useful for this programme but is not a generic novelty claim: VANET work already validates communicated claims against local physical sensing and, separately, uses later observed behavior and learned/context-aware trust. RUN12's remaining question is whether this particular reality-bounded specialist interface and delayed-learning loop adds measurable robustness beyond stronger conventional reliability estimators.

## Reality-bound status

At decision time the learned gate receives only values reproducible on a real ordinary car plus phone/declared sensors. Synthetic truth is used to generate the simulated world and research evaluation MAE; it is not a decision-time feature or direct training label.

However, the current **training and calibration corroborators are generated from that latent truth plus independent Gaussian noise**. The episodes also reuse the same latent scalar rather than evolving a physical state over the delay. Thus RUN12 establishes an interface separation, not yet a real-world supervision guarantee.

Before any real-car claim, the teacher must be replaced by an explicitly timestamped channel pair with units, calibration, latency and dependence documented. The gate should never be trained on CARLA-only actor state, perfect lane coordinates, collision flags unavailable in a real car, or hidden object identities. It must also be tested when teacher and candidate share calibration, clock, environment, or upstream-model failures.

## Validation and cache status

The experiment and trust model use only Python standard library plus repository-local modules. Primary validation used 150,000 evaluation episodes across three age profiles, plus 100,000 fault-rate-shift episodes and 75,000 correlated-camera-failure episodes. The model-training and threshold-calibration streams are disjoint from evaluation seeds.

No dataset, model weight, CARLA artifact, simulator asset or Python package was downloaded. There was no heavyweight cache miss in this run. The repository already contains today's dedicated MaleCNS prior-art record and autonomous-driving dataset/benchmark/safety research, so this run focused on the next falsifiable implementation step rather than duplicating those searches.

## Next experiment

The next clean step is to replace the idealized synthetic corroborator with a small cached real-world aligned slice containing at least two independently measured versions of the same driving quantity — preferably phone IMU yaw + camera-derived ego-motion, or OBD wheel speed + phone GNSS speed.

Before or alongside that real slice, freeze the current gate and sweep a teacher-quality ladder: unbiased Gaussian proxy; biased proxy; heteroscedastic/feature-dependent noise; candidate+teacher common bias; trusted-reference+candidate common bias; shared clock drift; state evolution across the delay; and missing/late corroboration. Compare against the RUN11 fixed gate, an adaptive hard threshold, a soft robust/reliability-weighted baseline and a simple online source-reliability updater under identical information and compute. Report paired effect intervals, admission confusion where synthetic fault labels exist, trust calibration and time-to-recovery after shifts.