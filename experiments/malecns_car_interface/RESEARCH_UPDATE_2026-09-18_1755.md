---
type: "Companion Note"
title: "MaleCNS car-interface research update — 2026-09-18 17:55"
description: "Fresh prior-art verification, closed-loop benchmark additions, and newly prioritized near-free scalar channels for the MaleCNS retrofit driving program."
tags: [malecns, prior-art, autonomous-driving, benchmarks, sensors, closed-loop]
timestamp: 2026-09-18T17:55:00-04:00
---

# MaleCNS car-interface research update — 2026-09-18 17:55

## 1. Direct MaleCNS driving prior art is stronger than the first sweep implied

Primary source:
https://github.com/suanmiao/fly-self-driving

`fly-self-driving` is direct prior art, not merely a concept demo. Its README reports:

- 165,122 MaleCNS neurons and 25,563,197 measured synapses;
- recurrent state carried between decisions;
- a 64 x 32 pixel windscreen as sensory input;
- one learned gain per synapse plus one learned leak per neuron, about 25.7M trainable parameters while preserving measured graph connectivity;
- frozen random pixel-to-optic-lobe input mapping and frozen random motor readout;
- behaviour cloning followed by three DAgger rounds;
- closed-loop evaluation on three independent held-out sets of 20 streets with traffic;
- reported connectome result of 20/20, 19/20 and 19/20 on those three sets (58/60 total), versus 16/20 for a randomly rewired graph in the reported comparison;
- about 35 minutes of training on one H100 for the reported recipe;
- an explicit caveat that braking is not yet learned and that there is one training seed per condition.

### Implication

Our novelty must not be framed as “MaleCNS can drive.” A stronger and testable distinction is **reality-bounded retrofit driving with multimodal cheap sensors, explicit sim-to-real contracts, systematic sensor ablations, active sensing, peer negotiation and real-data validation**.

The project should also adopt two controls from `fly-self-driving` whenever feasible:

1. randomly rewired graph under the same training recipe;
2. simple linear/MLP baselines with the same public sensor channels.

DAgger is now a serious candidate training stage for our closed-loop curriculum rather than merely a background technique.

## 2. Drone claim clarification

Primary project page:
https://spikecalls.github.io/FlyDrones/

The FlyDrones page explicitly describes the visible live demo as a browser simulation. It uses an 850-neuron synthetic MiniFly stand-in for the interactive browser experience while stating that its Python package can load the full MaleCNS connectome. The page explicitly says: **simulation, not a real flight**.

### Implication

The earlier “physical MaleCNS drone” claim remains unverified. FlyDrones is relevant direct simulation prior art, but it should not be cited as evidence that a physical drone has already been flown by MaleCNS.

## 3. Another direct re-embodiment precedent: Fly Brain Bridge

Project page:
https://www.doriantodd.com/projects/fly-brain-bridge/

This project describes the full 166,700-neuron MaleCNS connectome wired to a simulated Sesame robot, with stimulation of identified neurons and readout of fly command neurons for robot behaviors.

### Implication

The field is rapidly moving from “connectome analysis” to **connectome re-embodiment**. Our strongest contribution therefore needs rigorous interface design and benchmark evidence, not merely novelty of putting MaleCNS into a non-fly body.

# Driving benchmark additions

## 4. Bench2Drive: useful multi-ability closed-loop benchmark

Sources:
- https://github.com/Thinklab-SJTU/Bench2Drive
- mirrored/current repository found in search: https://github.com/946548737619/bench2drive

Bench2Drive is a CARLA closed-loop benchmark with 220 short routes and safety-critical scenarios. It also provides dataset scales intended for different compute budgets:

- Mini: about 4 GB / 10 representative clips;
- Base: about 400 GB / 1,000 clips;
- Full: about 4 TB / 10,000 clips.

The download tooling supports resumable Hugging Face retrieval.

### Proposed use

Use Bench2Drive primarily as a **multi-ability closed-loop scorecard**, not as our first training corpus.

For our cache policy, start with Mini only and key the persistent cache by benchmark version + file list + checksum where available. Base/Full should require an explicit registered experiment before download.

## 5. Fail2Drive: high-value generalization stress test

Primary source:
https://github.com/autonomousvision/fail2drive

Paper:
https://arxiv.org/abs/2604.08535

Fail2Drive is especially well matched to our goals because it tests closed-loop generalization under held-out distribution shifts rather than only replaying familiar scenario classes. It provides:

- 17 unseen scenario classes;
- 30 new assets including animals, visual noise and adversarial obstacles;
- 100 paired route pairs (200 routes total), each shifted route matched to an in-distribution reference;
- explicit rules forbidding training or fine-tuning on Fail2Drive scenarios;
- a lightweight plugin path for existing CARLA projects.

The paper reports a mean success-rate drop of 22.8% across evaluated state-of-the-art models under the distribution shifts.

### Proposed use

After we establish a basic CARLA driver, make Fail2Drive a **held-out final stress suite**. Do not use its routes/assets for curriculum training. This preserves its main value: measuring whether MaleCNS + retrofit channels learned a transferable control policy rather than a route-specific trick.

## 6. Open-loop metrics are not enough

Relevant 2026 analysis:
https://arxiv.org/abs/2605.00066

The cross-benchmark study comparing NAVSIM-style open-loop metrics to Bench2Drive closed-loop results reports ranking inversions even when aggregate open-loop scores correlate strongly. In its paired sample, Ego Progress was the strongest single predictor of closed-loop success, while collision-oriented open-loop metrics alone were not sufficient.

### Implication

Our evaluation should explicitly separate:

- offline perception / representation quality;
- open-loop trajectory quality;
- closed-loop driving score;
- held-out generalization gap.

A MaleCNS variant does not “drive better” merely because it predicts a human trajectory more accurately offline.

# Newly prioritized zero/near-zero-cost scalar channels

The implementation in this run already added the first four lawful cross-sensor scalars:

- `abs(GNSS speed - OBD speed)`;
- wheel-speed spread;
- steering-angle vs measured-yaw residual;
- GNSS confidence from reported accuracy.

The next free channels to prioritize are:

### Sensor age / synchronization

Expose per-bus sample age and cross-bus timestamp skew. A stale but numerically plausible sensor can be more dangerous than a missing sensor. These scalars are free and available in both simulator and real instrumentation.

### Camera health / visibility

From the phone camera stack, expose lawful quality scalars such as exposure time, ISO/gain, focus state, frame-drop rate, blur estimate and saturation fraction. These can tell the agent when visual perception is unreliable without giving it simulator weather truth.

### Compute-budget / thermal state

Phone temperature / thermal-throttling state, battery current and inference latency can form an internal “metabolic” channel. This is useful if YOLO, active sensing or a local LLM are optional expensive actions: the agent can learn when extra perception is worth the compute/energy cost.

### CAN/OBD dynamic residuals

Where the car exposes them, prioritize steering torque, brake-pedal state/pressure, ABS/traction-control events and steering-rate. Derived residuals such as expected deceleration vs measured deceleration can become compact bodily signals.

### TPMS as a cheap safety organ

If tire-pressure/temperature telemetry is available from the vehicle or inexpensive BLE TPMS hardware, feed normalized pressure/temperature deviation rather than raw vendor-specific packets. This can warn about a changing physical plant before handling quality degrades.

### Communication freshness

For multi-car Wi-Fi negotiation, do not expose only peer messages. Also expose packet age, jitter, loss and link confidence. A negotiated right-of-way token should become less trustworthy as its communication state becomes stale.

# Immediate research/experiment consequence

The next small empirical step should not require CARLA or any large download: construct a synthetic/recorded sensor stream where GPS speed, wheel speeds and yaw are perturbed independently, then measure whether the derived disagreement channels let a tiny baseline detect fault/slip regimes better than raw single-sensor thresholds. If that mechanism survives, repeat on a cached comma2k19 shard before feeding the channels to MaleCNS.
