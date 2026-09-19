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

The claim-specific prior-art/falsification boundary for this protocol is recorded in `../../audits/prior-art/malecns-whole-cns-closed-loop-2026-09-19.md`. Whole-adult-Drosophila connectome control, fixed connectome processing units, connectome reservoirs and degree-preserving topology controls all predate this protocol. The local question is therefore the narrower conjunction tested here, not whether connectomes can be used as controllers in general.

## Primary question

Under the same lawful sensors, actuators, reward channels, trainable interface capacity, optimizer, curriculum, evaluation budget and seeds, does a frozen whole-MaleCNS connectome core produce better closed-loop control than matched null brains and a conventional controller?

The primary scientific comparison is topology/dynamics-specific. Adapter success by itself is not evidence for MaleCNS.

### Interpretation boundary

The v1 frozen-core experiment tests whether MaleCNS is useful as a **connectome-constrained dynamical substrate under external learning**. It does not test a complete biological theory of how Drosophila learns from reinforcement. Known fly learning mechanisms include dopamine-gated synaptic plasticity and persistent neural traces; those mechanisms are not created merely by freezing a connectome graph and routing reward into biologically named populations.

This distinction is deliberate. The first priority is to put the whole MaleCNS in a minimal closed control loop and observe what it can and cannot do. A biologically motivated local-plasticity model is a later discriminator if reward/credit assignment emerges as an observed failure mode, not a prerequisite for the first drive.

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

The appetitive/aversive/omission partition is an engineering abstraction with biological motivation, not a claim that fly reinforcement is a context-free signed scalar. Compartment, timing, movement and internal state can alter dopaminergic meaning; v1 records the simplification rather than pretending to model all of it.

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

Do **not** pre-solve delayed reward before the first C1 run. Begin with the simplest causal immediate/proximal reward and the same minimal external training rule in true and null brains. Once the loop learns anything at all, measure temporal-credit tolerance with a preregistered reward-delay sweep rather than adding machinery speculatively.

If delay becomes a measured failure mode, compare at least: (a) the same frozen core with an explicit external eligibility/credit mechanism, and (b) a separately declared biologically motivated local-plasticity/trace arm. Any such plasticity arm changes the scientific question and must be matched in the null brains. Success of the frozen v1 core must not be described as evidence that Drosophila's endogenous delayed-reward mechanism has been reproduced.

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
2. degree-preserving rewired connectome controls;
3. weight/sign-matched random/null connectome appropriate to the implementation;
4. adapter-only/no-connectome control receiving the same lawful inputs;
5. conventional controller or RL baseline appropriate to the stage.

Where feasible, also include a monolithic MaleCNS and the sensor-colony variant under matched total trainable parameters and compute.

Null brains receive the same sensory populations by role, action adapter size, reward transduction contract, optimizer, curriculum schedule and stopping rule. Differences in convergence caused only by extra optimization or capacity are not topology evidence.

For an exploratory C1 smoke test, one deterministic degree-preserving rewiring is sufficient to get the car moving and expose gross failures. **Confirmatory topology inference requires multiple independently generated degree-preserving rewired graphs**, shared/matched from-scratch initialization, and reporting between-rewiring variance; one lucky null graph is not a sufficient causal control.

To test whether biological addressing itself matters, the confirmatory control set must also include a capacity-matched random/anatomically implausible assignment of the same lawful sensory/reward/action channels. If biological and random assignments are equivalent, the result supports generic graph geometry rather than biological pathway semantics.

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

1. paired improvement over the distribution of degree-preserving rewired controls, not merely one convenient rewiring;
2. paired improvement over the adapter-only/conventional baseline selected for the stage;
3. the preregistered uncertainty interval for the primary contrast excludes zero and exceeds the declared minimum practical effect;
4. the gain survives matched resource, initialization and dynamical-scale accounting;
5. no privileged-state or interface-capacity asymmetry explains the result.

If the true connectome does not clear the matched null and conventional baselines, record the result as a failure of the tested formulation. Do not rescue the claim by increasing reservoir size, changing reward semantics or opening another test set after observing the result.

## Run manifest requirements

Each run must preserve:

- MaleCNS source/provenance and graph hash;
- exact biological-interface population map;
- null-generation method, graph realization IDs and seeds;
- initialization policy shared/matched across arms;
- lawful sensor manifest and rates/latencies;
- actuator manifest;
- reward/value terms and biological/engineered classification;
- trainable parameter counts per arm;
- optimizer and temporal-credit settings;
- recurrent/activity/spectral normalization or other dynamical-scale choices;
- curriculum stage and promotion criterion;
- train/validation/test manifests;
- code commit, environment version and random seeds;
- raw episode outputs and aggregate statistics.

## First execution target

Execute C1 before any full-driving claim: one actuator, one signal, true whole-MaleCNS versus a degree-preserving rewiring, adapter-only and a simple conventional controller. This is a fast exploratory loop whose job is to discover whether the closed biological core contributes anything before sensor fusion and multi-actuator complexity are introduced.

Do not delay C1 to implement every confirmatory control or a complete fly-learning model. If the exploratory result is interesting enough to support a topology claim, rerun the frozen task with the full rewired ensemble, matched initialization/dynamical accounting and biological-address randomization before treating the effect as confirmatory.

A C1 failure is scientifically useful and blocks escalation only long enough to identify the concrete failure mode. It should not trigger speculative addition of sensor-fusion, clock, trust or delayed-credit machinery unrelated to that observed failure. A C1 success permits C2 but does not imply driving competence.

## Claim boundary

This protocol tests a whole-system closed-loop MaleCNS formulation as a frozen connectome-constrained substrate under external learning. It does not assert that the connectome is a general reinforcement learner, that the frozen graph reproduces dopamine-gated Drosophila synaptic learning, that Drosophila reward biology is completely captured by the chosen proxy populations, or that success in simulation transfers to a road vehicle. Those stronger claims require separate evidence.