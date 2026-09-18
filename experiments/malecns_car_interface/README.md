---
type: "Companion Note"
title: "MaleCNS Car Interface: Reality-Bounded Driving Experiments"
description: "Experimental program for coupling MaleCNS to an ordinary-car-equivalent interface: virtual OBD-II plus a dashboard-mounted modern Android sensor suite, without privileged simulator state."
tags: [malecns, driving, carla, obd-ii, android, embodied-agent, sim-to-real, experiment]
timestamp: 2026-09-18T16:25:00-04:00
---

# MaleCNS Car Interface: Reality-Bounded Driving Experiments

This directory starts a driving experiment line whose central constraint is simple:

> The agent may receive only signals that could plausibly be available later from an ordinary road car plus a modern dashboard-mounted Android phone.

The simulator is a replaceable world backend. It must not become a source of privileged cognition.

## Intended physical deployment analogue

The virtual setup mirrors a future real setup:

```text
ordinary car
  ├─ OBD-II adapter ───────────────┐
  │                                │
  └─ Android phone on dashboard ───┼─> thin input adapters -> MaleCNS
                                   │
route / navigation intent ─────────┘

MaleCNS -> thin output adapter -> steering / throttle / brake
```

The target phone profile is not a specific flagship model. It is a generic reasonably modern Android roughly in the Galaxy S23/S24 class: camera, GNSS/GPS, accelerometer, gyroscope, magnetometer and derived orientation/motion signals where available.

## Optional cheap external sensor organs

The physical analogue may add inexpensive external sensors, provided each one is explicitly declared and independently ablatable. These are treated as optional organs, not as simulator privileges.

### Active echolocation / ultrasonic ranging

A small ultrasonic transmitter/receiver array can emit pulses and return time-of-flight / echo features. The agent should receive measured echoes or a compact physically plausible transduction of them, not exact simulator object coordinates.

This channel is attractive because it is cheap, low-bandwidth and genuinely active: the agent can decide when or where to ping, paying an energy / attention cost if an experiment needs that pressure.

### Low-cost LiDAR

A small single-point or narrow-field ToF LiDAR can provide real distance measurements through a physical sensor contract. Low-cost modules in the Benewake TFmini-S class are currently available in the tens-of-dollars range, making this a realistic optional channel rather than a simulator-only luxury.

The simulator may use its geometry to synthesize the sensor measurement, but only the virtual LiDAR output crosses the reality boundary.

### Ambient RF / city Wi-Fi

The phone or an auxiliary radio can expose passive features of the surrounding RF environment: visible access-point identifiers after privacy-preserving hashing, RSSI, channel, scan timing and aggregate spectral occupancy.

The default goal is not to decode private traffic. It is to test whether ambient radio structure can become a cheap contextual / localization modality, analogous to landmarks in another sensory domain.

Wi-Fi can also become an explicit inter-agent communication channel. Multiple cars, each controlled by a separate MaleCNS instance, may exchange low-bandwidth messages or learned tokens with nearby peers.

This creates a multi-agent research track:

- cooperative signaling: warn peers about congestion, hazards or intended maneuvers;
- negotiation: resolve merges, bottlenecks and right-of-way conflicts;
- transferable credits/tokens: one agent may compensate another for yielding, allowing experiments in endogenous traffic conventions and local markets;
- reputation / reciprocity: agents may learn which peers honor commitments;
- coalition and anti-collusion tests: measure whether communication improves global flow or merely enables selfish coordination.

The initial token system should be an internal simulation credit, not a real cryptocurrency. Its semantics, supply and transfer rules should be explicit and auditable. A simple first experiment is a one-lane bottleneck where two cars approach simultaneously and may bid, yield, or exchange credits for priority.

The simulator must also retain non-communication baselines and adversarial controls: message dropout, deceptive peers, identity reset/Sybil-like behavior, unequal initial credit allocation and communication latency.

### On-device YOLO perception channel

The dashboard phone may run a compact object detector locally and expose its detections as a separate derived sensory channel while preserving the raw camera feed.

This channel should contain only outputs that a real phone could compute from its own camera, for example:

- class id / semantic label;
- confidence;
- bounding box coordinates normalized to the image;
- optional object track id when produced by a real tracking stage;
- optional coarse velocity estimated from frame-to-frame motion.

The agent must still receive the raw camera independently. YOLO is therefore an optional perceptual transducer, not a replacement for vision and not simulator ground truth.

The important experiment is the ablation:

- raw camera only;
- YOLO channel only;
- raw camera + YOLO;
- raw camera + YOLO + other cheap sensors.

This distinguishes whether MaleCNS benefits from pre-digested symbolic perception or learns more useful structure directly from the visual stream.

Mobile deployment should target a small model exported for an on-device runtime such as LiteRT/TFLite or NCNN. The exact detector version and device profile must be pinned per experiment.

### Optional local language-model transducer

A local LLM is a qualitatively different component: it is not a sensor but an expensive semantic transducer. It may convert approved raw or structured inputs into a low-bandwidth semantic channel for MaleCNS.

This must remain optional and separately measured because it changes the compute and hardware envelope. The clean comparison is:

- MaleCNS + cheap physical sensors only;
- MaleCNS + each new sensor organ separately;
- MaleCNS + all cheap sensor organs;
- MaleCNS + local LLM transducer.

The local LLM must never receive privileged simulator fields either. Its input must be a subset or lawful transformation of the same reality-bounded buses available in a real car.

## Reality boundary

The agent MUST NOT receive simulator-only fields such as exact object distance, lane-center coordinates, perfect world pose, ground-truth semantic segmentation, collision prediction, hidden traffic state or perfect map-relative localization.

Objects, vehicles, pedestrians, road edges and free space should normally be inferred from the dashboard camera.

Allowed inputs are split into three buses.

### Phone bus

- forward-facing RGB camera;
- GNSS/GPS-like position fixes;
- accelerometer;
- gyroscope;
- magnetometer / compass;
- orientation / rotation-vector style derived signals;
- optional barometer and other common phone sensors when an experiment explicitly registers them.

Sensor rate, noise, latency and dropout should eventually approximate a real phone.

### OBD bus

The first profile should stay conservative and use signals commonly exposed through OBD-II / ECU telemetry, for example:

- vehicle speed;
- engine RPM;
- throttle position;
- engine load;
- coolant temperature;
- selected diagnostic/status values.

The exact available PID set must be a profile, not an assumption baked into MaleCNS.

### Intent / bodily-feedback bus

Navigation intent is legitimate external information. The agent does not need to rediscover that a destination exists.

The route interface may expose quantities analogous to what a navigation system could provide, such as next-turn direction, route progress or distance to the next waypoint. This is different from exposing perfect lane geometry from the simulator.

Training feedback should preferentially be represented as localized bodily signals rather than one global scalar reward. Examples:

- drifting away from the permitted route corridor -> localized aversive signal;
- wrong-way travel -> a distinct aversive channel;
- collision -> strong aversive signal;
- progress toward the route objective -> appetitive signal.

Obstacle proximity is deliberately NOT a privileged feedback channel in the default experiment: the camera should be sufficient to learn that relation.

## Experimental ladder

### E0 — Interface integrity

Goal: prove that the adapter layer structurally prevents privileged simulator state from reaching MaleCNS.

No driving competence is required.

Pass condition: a recorded observation can be generated entirely from the declared phone, OBD and intent/body buses.

### E1 — One actuator, one signal

Curriculum starts with one controllable degree of freedom and one task-relevant sensory/feedback signal. Add complexity only after stable control.

Candidate: fixed steering and learn throttle to hold a target speed using OBD speed plus bodily error.

### E2 — Longitudinal driving

Throttle + brake; maintain speed and stop at a marked objective.

Ablations: OBD-only versus phone IMU + vision versus combined.

### E3 — Lane / corridor following from vision

Steering enters. Do not expose lane-center truth to MaleCNS.

The environment may compute deviation internally only to generate the registered bodily aversive signal.

### E4 — Route following

Add navigation intent from the virtual phone/GPS. The agent must follow a route while perception remains camera-grounded.

### E5 — Traffic and obstacle interaction

Vehicles and pedestrians appear. Their geometry remains hidden from MaleCNS; perception is visual.

### E6 — Sensor degradation and sim-to-real stress

Introduce realistic noise, rate limits, delay, GPS drift/dropout, missing OBD PIDs, camera exposure changes and phone mounting perturbations.

A policy that works only with perfect synthetic sensors fails this stage.

## Required comparisons

Each competence experiment should retain at least:

1. full interface;
2. no OBD;
3. no IMU;
4. no GPS/navigation intent when task permits;
5. vision removed when task permits;
6. no active echolocation;
7. no LiDAR;
8. no ambient RF / Wi-Fi context;
9. no on-device YOLO channel;
10. YOLO-only versus raw-camera-only versus combined perception;
11. no local-LLM transducer;
12. shuffled or delayed bodily feedback;
13. a simple controller / conventional RL baseline appropriate to that stage.

The aim is not merely to make the car move. It is to identify what the frozen MaleCNS contributes and which thin adapters or sensor buses are actually necessary.

## Metrics

Prefer task-level observable metrics:

- route completion;
- collisions;
- off-route time;
- control smoothness;
- time to recover after perturbation;
- intervention count;
- generalization to unseen routes;
- degradation under sensor noise/dropout.

Also log adapter activity and MaleCNS state summaries needed for later mechanistic analysis.

## Backend plan

CARLA is the first intended world backend because it exposes programmable vehicles, sensors and traffic while allowing the experiment to control what crosses the reality boundary.

The Android side should initially be a phone-interface emulator, not necessarily a full Android OS emulator. A later experiment can replace it with an actual Android emulator or physical phone while preserving the same sensor contract.

## Immediate next implementation

The accompanying `interface.py` defines the first executable contract and rejects undeclared simulator fields. The next PR should add a CARLA adapter that populates only those fields and records synchronized episodes.
