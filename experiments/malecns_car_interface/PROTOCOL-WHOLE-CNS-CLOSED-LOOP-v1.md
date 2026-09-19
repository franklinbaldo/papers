---
type: "Protocol"
title: "MaleCNS Whole-CNS Closed-Loop Control v1"
description: "Frozen prospective protocol for testing a whole-connectome MaleCNS core in a biologically addressed perception-state-action-reinforcement loop with matched null brains and a staged reality-bounded driving curriculum."
tags: [malecns, closed-loop, reinforcement-learning, driving, connectome, preregistration]
timestamp: 2026-09-19T13:27:46-04:00
---

# MaleCNS Whole-CNS Closed-Loop Control v1

## Status

Prospective protocol. No result is implied by this document.

This protocol converts the methodological requirements recorded in `malecns_connectome_reservoir_tagging.md` and the reality-bounded ladder in `experiments/malecns_car_interface/README.md` into one executable confirmatory contract. The historical 512-neuron open-loop tagging run remains a diagnostic of that reduced formulation and is not evidence for or against the hypothesis tested here.

## Primary question

Under the same lawful sensors, actuators, reward channels, trainable interface capacity, optimizer, curriculum, evaluation budget and seeds, does a frozen whole-MaleCNS connectome core produce better closed-loop control than matched null brains and a conventional controller?

The primary scientific comparison is topology/dynamics-specific. Adapter success by itself is not evidence for MaleCNS.

## Frozen substrate boundary

Use the complete released MaleCNS graph supported by the repository runtime, or the maximal technically faithful whole-system representation if an exact full graph cannot be executed. Any omission, aggregation or numerical approximation must be declared before confirmatory scoring and applied identically to the matched null brains.

The biological core is frozen during a run. Trainable components are restricted to declared input adapters, output adapters and, where a protocol stage requires it, a small policy/value interface around the core. No trainable parameter may silently alter the connectome adjacency or biological sign structure in the true-brain arm.

## Reality boundary

Only signals reproducible on an ordinary car plus a modern dashboard-mounted Android phone may cross into the agent. The simulator may generate those sensor measurements, but exact simulator state may not cross the boundary.

Allowed families are the existing registered buses:

- phone: RGB camera, GNSS/GPS, accelerometer, gyroscope, magnetometer/orientation and explicitly registered common phone sensors;
- vehicle: declared OBD-II/ECU signals;
- intent/body: route intent plus registered appetitive/aversive bodily feedback;
- optional organs only when explicitly registered and ablated: ultrasonic/echolocation, low-cost LiDAR, RF/Wi-Fi context, on-device detector output or local semantic transducer.

Forbidden inputs include exact lane-center coordinates, perfect object geometry, hidden traffic state, ground-truth semantic segmentation, perfect world pose or any simulator-only collision prediction.

## Biological interface map

Every external scalar/vector must be assigned to a declared biological role before training. The exact neuron IDs/populations are an implementation artifact of this protocol and must be version-pinned in the run manifest.

### Sensory entry

Map each lawful modality to a declared sensory population or biologically motivated proxy population. Different modalities must not share an arbitrary undifferentiated broadcast solely for implementation convenience. If one modality is represented through several specialist MaleCNS instances, each specialist receives the same lawful source signal but an independently initialized external adapter.

### Appetitive reinforcement

Positive task progress enters through a declared appetitive/reward pathway. The mathematical reward and the neural transduction are recorded separately. The external scalar may scale the adapter drive, but reward is not broadcast indiscriminately to every neuron.

### Aversive reinforcement

Collisions, wrong-way travel, route violation and other predeclared failures enter through a distinct aversive pathway. Aversive magnitude is not implemented merely as a negative appetitive scalar unless an ablation explicitly tests that simplification.

### Omission and relief

Expected reward omitted after a predictive state and relief after cessation of an aversive condition are separate event types in the run log. Their transduction may share or differ from appetitive/aversive pathways, but the choice must be frozen before test scoring.

### Internal state

If motivational state, fatigue, novelty or uncertainty is supplied as an internal channel, it must be generated from past lawful observations/actions/rewards only. No hidden simulator variable may be relabeled as internal state.

### Action readout

Actions originate from declared descending/motor/VNC or proxy output populations and pass through a thin trainable actuator adapter. The adapter may map biological state to steering, throttle and brake, but may not receive raw sensor input through a bypass path.

## Reward/value contract

The reward objective is task-level and causal. For each stage, report every shaping term separately.

Primary components:

- progress toward the registered task objective: appetitive;
- collision or safety-boundary violation: strong aversive;
- wrong-way or route-corridor violation: aversive;
- stable sustained target attainment: appetitive terminal or milestone event;
- omission/relief events: explicitly logged when applicable.

Engineered shaping is permitted only when declared before training and separately ablated. Every term is tagged `biological-motivation` or `engineered-scaffold` in the run manifest.

Reward near the target must retain pressure for precision rather than flatten prematurely. When continuous target error is available lawfully, use a monotone late-precision term that increases the marginal value of further improvement near the goal. The exact bounded transform and scale are frozen per stage; no post-test tuning is allowed.

Temporal credit assignment is part of the trainable external interface unless a biologically motivated local mechanism is explicitly implemented. Delayed/terminal rewards must use the same credit-assignment algorithm in true and null brains.

## Curriculum

Use the existing experimental ladder and do not begin with full driving complexity.

### C0 — interface integrity

Verify that a recorded observation/action/reward trajectory can be reconstructed exclusively from the declared buses and biological-interface manifest. Any privileged-state leak fails the run before learning is evaluated.

### C1 — one actuator, one signal

One controllable degree of freedom and one task-relevant sensory/feedback channel. Default first task: fixed steering, learn throttle to hold target speed from lawful speed feedback. Add no second actuator until sustained stability is reached under the preregistered criterion.

### C2 — longitudinal control

Throttle + brake; maintain speed and stop at a marked objective.

### C3 — visual lateral control

Add steering and camera-grounded lane/corridor following. The environment may compute deviation only to generate the registered bodily aversive feedback; exact lane-center truth is not an observation.

### C4 — route following

Add navigation intent and lawful position/orientation signals.

### C5 — traffic and obstacle interaction

Add vehicles/pedestrians without exposing their ground-truth geometry.

### C6 — robustness and sim-to-real stress

Apply frozen perturbation suites for sensor noise, delay, dropout, GNSS drift, missing OBD PIDs, camera changes and mounting perturbations.

Promotion between stages is based on validation episodes only. Test episodes are never used to decide whether to add a sensor, actuator, shaping term or curriculum stage.

## Arms and matched controls

Every confirmatory stage must include, with identical external budgets:

1. true whole-MaleCNS core;
2. degree-preserving rewired connectome;
3. weight/sign-matched random/null connectome appropriate to the implementation;
4. adapter-only/no-connectome control receiving the same lawful inputs;
5. conventional controller or RL baseline appropriate to the stage.

Where feasible, also include a monolithic MaleCNS and the sensor-colony variant under matched total trainable parameters and compute.

Null brains receive the same sensory populations by role, action adapter size, reward transduction contract, optimizer, curriculum schedule and stopping rule. Differences in convergence caused only by extra optimization or capacity are not topology evidence.

## Data split and selection firewall

Use disjoint `train`, `validation` and `test` episode manifests. Seeds, environment routes/scenarios and perturbation families are frozen before final test opening.

- training may adapt interfaces/policies;
- validation may choose checkpoints and curriculum promotion;
- test may only score the already selected candidate;
- no test outcome may change reward scale, interface mapping, topology preprocessing, stopping rule or model selection.

## Primary endpoints

For the first completed stage, declare one primary endpoint before the test set is opened. Candidate task-level endpoints are:

- sustained target-control error;
- route completion;
- collision rate;
- off-route time;
- recovery time after perturbation.

Secondary endpoints may include smoothness, intervention count, sample efficiency, energy/compute and robustness to dropout/noise.

Internal state diagnostics are explanatory only and cannot substitute for task performance.

## Confirmatory decision rule

A MaleCNS-specific advantage requires all of the following on the frozen primary endpoint:

1. paired improvement over the degree-preserving rewired control;
2. paired improvement over the adapter-only/conventional baseline selected for the stage;
3. the preregistered uncertainty interval for the primary contrast excludes zero and exceeds the declared minimum practical effect;
4. the gain survives matched resource accounting;
5. no privileged-state or interface-capacity asymmetry explains the result.

If the true connectome does not clear the matched null and conventional baselines, record the result as a failure of the tested formulation. Do not rescue the claim by increasing reservoir size, changing reward semantics or opening another test set after observing the result.

## Run manifest requirements

Each run must preserve:

- MaleCNS source/provenance and graph hash;
- exact biological-interface population map;
- null-generation method and seed;
- lawful sensor manifest and rates/latencies;
- actuator manifest;
- reward/value terms and biological/engineered classification;
- trainable parameter counts per arm;
- optimizer and temporal-credit settings;
- curriculum stage and promotion criterion;
- train/validation/test manifests;
- code commit, environment version and random seeds;
- raw episode outputs and aggregate statistics.

## First execution target

Execute C1 before any full-driving claim: one actuator, one signal, true whole-MaleCNS versus degree-preserving rewiring, adapter-only and a simple conventional controller. This isolates whether the closed biological core contributes anything before sensor fusion and multi-actuator complexity are introduced.

A C1 failure is scientifically useful and blocks escalation until the failure mode is understood. A C1 success permits C2 but does not imply driving competence.

## Claim boundary

This protocol tests a whole-system closed-loop MaleCNS formulation. It does not assert that the connectome is a general reinforcement learner, that Drosophila reward biology is completely captured by the chosen proxy populations, or that success in simulation transfers to a road vehicle. Those stronger claims require separate evidence.
