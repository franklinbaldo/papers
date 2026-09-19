---
type: "Companion Note"
title: "MaleCNS Sensor Colony Architecture"
description: "Hierarchical multi-MaleCNS architecture in which multiple specialist fly-brain instances learn individual sensor channels and one or more coordinator flies combine their reports for driving."
tags: [malecns, driving, multi-agent, sensor-fusion, embodied-agent, experiment]
timestamp: 2026-09-19T00:00:00Z
---

# MaleCNS Sensor Colony Architecture

## Core idea

A single MaleCNS instance does not need to learn the entire vehicle sensorium.

Instead, the car can host a **colony of specialist MaleCNS instances**. Each specialist receives one sensor, one small family of related signals, or one derived discrepancy channel and is trained to become useful at interpreting that modality.

Examples:

- camera specialist;
- YOLO/detection specialist;
- IMU specialist;
- GNSS/GPS specialist;
- OBD dynamics specialist;
- ultrasonic/echolocation specialist;
- LiDAR specialist;
- RF/Wi-Fi specialist;
- map/navigation specialist;
- cross-sensor disagreement specialist;
- peer-communication / negotiation specialist.

Several specialists MAY observe the same channel. Redundant specialists create an ensemble rather than a single point of failure.

## Hierarchy

A first-layer specialist should not directly need to know the entire driving task. It can learn a narrow contract such as:

- "how unusual is this IMU state?";
- "is longitudinal motion stable?";
- "is the visual scene becoming more dangerous?";
- "is this echo pattern consistent with free space?";
- "is GNSS currently trustworthy?";
- "does steering produce the expected yaw?";
- "is a peer message worth trusting?".

The output of each specialist is a small report that can contain:

- one or more bounded scalar signals;
- confidence;
- novelty / surprise;
- local appetitive or aversive state;
- a compact learned embedding or state reference.

A second layer receives only these lawful specialist outputs and learns coordination. This coordinator can itself be another MaleCNS instance.

The hierarchy can recurse:

```text
raw lawful sensors
   ↓
MaleCNS sensor specialists
   ↓
MaleCNS modality coordinators
   ↓
MaleCNS driving coordinator
   ↓
thin actuator adapter
   ↓
steering / throttle / brake
```

Nothing in this hierarchy permits simulator-only truth. Every specialist input must satisfy the same reality boundary as the single-agent architecture.

## Why this matters experimentally

The hypothesis is not merely that "more flies are better." The architecture makes several falsifiable claims possible:

1. **specialization** — a MaleCNS trained on one narrow modality may learn faster or more robustly than a monolithic instance;
2. **redundancy** — multiple independent specialists for one sensor may improve robustness to noise or individual training failures;
3. **modularity** — new sensors can be added without retraining every existing specialist;
4. **graceful degradation** — losing one sensor or one specialist should not collapse the whole policy;
5. **hierarchical credit assignment** — local specialists can receive local feedback while the coordinator receives driving-level feedback;
6. **population diversity** — independently initialized or differently trained MaleCNS instances may discover complementary interpretations of the same channel.

## Training curriculum

Start extremely small.

### C0 — one sensor, one fly

One MaleCNS receives one scalar and learns one narrow target.

### C1 — one sensor, several flies

Train N independent specialists on the same signal. Compare individual, mean/median ensemble, confidence-weighted ensemble and learned coordinator.

### C2 — several sensors, one specialist each

Introduce separate specialists for speed, yaw, IMU, GPS confidence, visual danger and range.

### C3 — specialist colony + coordinator fly

Freeze or slow specialist learning and train a MaleCNS coordinator on their outputs.

### C4 — recursive hierarchy

Group specialists by modality (vision, vehicle dynamics, ranging, navigation, social/RF) and let modality coordinators feed a final driving coordinator.

### C5 — dynamic recruitment

Allow a coordinator to allocate attention or compute to specialists based on uncertainty, novelty or expected value.

## Required ablations

Every colony result should compare at least:

- monolithic MaleCNS with the same total raw inputs;
- one specialist per channel;
- multiple specialists per channel;
- fixed averaging;
- confidence-weighted fusion;
- learned MaleCNS coordinator;
- random/rewired connectome specialists where feasible;
- equal versus matched parameter/compute budgets.

This last control matters: a colony must not be declared superior merely because it contains more total trainable capacity.

## Failure tests

The colony should be stressed with:

- one specialist silenced;
- one sensor frozen;
- delayed specialist output;
- noisy specialist output;
- confidently wrong specialist;
- contradictory specialists;
- sensor dropout;
- adversarial/deceptive peer communication.

The coordinator should learn when to distrust or ignore a specialist.

## Interface contract

Specialists communicate through small lawful reports rather than raw simulator state. A report should expose bounded semantic quantities such as value, confidence, novelty and optional compact state references.

The accompanying `colony.py` defines the first executable report contract and deterministic baselines for aggregation. Learned MaleCNS coordination comes later and must be compared against these cheap baselines.

## Prior-art boundary — 2026-09-19 audit

A claim-level temporal audit materially narrows what this architecture can treat as distinctive. Hierarchical mixtures of experts, modality-specific experts, learned routing, confidence-weighted sensor fusion, median-based robust fusion, missing-sensor robustness, and even multiple independent copies of one MaleCNS connectome all have public antecedents before this note's cutoff.

The research question is therefore **not** whether expert hierarchies or redundant sensor fusion are new. The remaining combination-level hypothesis is whether a population of measured MaleCNS connectome instances, assigned narrow reality-bounded sensor-specialist roles and fused by higher-level MaleCNS coordinators, yields useful behavior beyond those established baselines under matched-capacity and connectome controls.

See the full dated audit: [`audits/prior-art/malecns-sensor-colony-2026-09-19.md`](../../audits/prior-art/malecns-sensor-colony-2026-09-19.md).
