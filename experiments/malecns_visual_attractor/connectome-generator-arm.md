---
type: "Protocol"
title: "Connectome Generator Arm for Learned Visual Attractors"
description: "Registered arm in which one frozen MaleCNS emits a dynamic visual signal that is evaluated by the closed-loop behaviour of a second frozen MaleCNS."
tags: [malecns, drosophila, connectome-to-connectome, visual-control, closed-loop, evolutionary-strategy]
timestamp: 2026-09-14T19:55:00-04:00
---

# Connectome Generator Arm

Status: **prospective arm; no positive result claimed**.

This arm belongs to `Learned Visual Attractors for Drosophila` and is evaluated only after the ordinary positive-control assay has established that the receiver loop can express measurable visual tracking. It does not replace that gate.

## Question

Can one frozen MaleCNS synthesize a dynamic visual signal that captures and guides another frozen MaleCNS more effectively or robustly than non-connectomic generators under the same behavioural evaluation budget?

The architecture is:

```text
observable state of receiver B
        -> trainable input adapter
        -> photoreceptors of frozen MaleCNS A
        -> recurrent MaleCNS A dynamics
        -> trainable output adapter on descending neurons
        -> visual control vector theta_t
        -> renderer
        -> photoreceptors of frozen MaleCNS B
        -> recurrent MaleCNS B dynamics
        -> locomotor readout
        -> new receiver pose
        -> next emitter context
        -> ...
```

Both recurrent connectomes are frozen. The trainable object is the boundary around emitter A, not its edges.

## What emitter A is allowed to observe

The primary adaptive arm receives only externally observable receiver state:

- normalized distance to lure;
- sine/cosine of target bearing;
- sine/cosine of receiver heading;
- previous radial velocity.

Emitter A does **not** receive receiver B's neural state, future trajectory, reward, target label hidden from the controls, or a privileged direction vector unavailable to an external tracking system.

An open-loop ablation masks receiver-dependent context and leaves only a registered time/noise drive. It asks whether feedback from B is what makes the connectome generator useful.

## Emitter boundary

The first implementation uses:

- emitter input population: identified `R1-6`, `R7`, and `R8` photoreceptors;
- emitter readout population: identified descending neurons;
- input adapter: `context -> emitter photoreceptor drive`;
- output adapter: `emitter descending activity -> four visual controls`.

The four first-stage controls are:

1. angular bearing offset;
2. apparent-size multiplier;
3. contrast multiplier;
4. temporal intensity gate.

This intentionally avoids raw pixel/video generation in the first connectome-generator run. The recurrent emitter invents a time-varying control sequence, and the renderer turns that sequence into the visual stimulus presented to B.

The generated control trace is retained at every timestep. A run is not summarized only by behavioural reward.

## Training rule

The first optimizer for the adapters is black-box evolutionary optimization/CMA-ES against the **true receiver behaviour**. This avoids making the first result depend on differentiating through the simulator.

A later differentiable implementation may backpropagate through adapters and recurrence, but it is a new optimizer comparison, not a reinterpretation of the first run.

At every optimization step:

```text
adapter candidate
  -> emitter A
  -> generated visual sequence
  -> receiver B
  -> true behavioural metrics
  -> selection
```

No surrogate-only or critic-only reward counts as evidence.

## Receiver diversity

Training against one deterministic receiver risks discovering a private simulator exploit. Therefore each adapter candidate is evaluated against a registered population of B conditions sharing the same candidate/control initial states:

- multiple swarm seeds;
- multiple starting sectors/headings;
- the registered receiver gain/drive condition;
- a small preregistered neighbourhood of receiver operating-point perturbations in robustness evaluation.

The decision set remains held out until the emitter candidate is frozen.

## Primary comparisons

All arms receive identical receiver seeds, distance curriculum and true-simulator call budgets.

1. `direct_theta` — ordinary direct parametric/evolutionary visual search;
2. `mlp_generator` — feed-forward context-to-visual controller with trainable parameter count matched as closely as practical;
3. `random_recurrent_generator` — frozen random recurrent substrate with the same adapter locations/dimensions;
4. `degree_null_generator` — degree-preserving MaleCNS emitter null with identical adapters;
5. `malecns_generator` — true frozen MaleCNS emitter with trainable boundary adapters.

Parameter counts, optimizer population size, generations, scene seeds and number of true receiver evaluations are recorded for every arm.

A generic neural video generator remains a later comparison. It is not the privileged generator baseline once this arm exists.

## Primary outcomes

For every generator family report:

- full capture-distance curve;
- `D*` under the governing `p0` and control-margin rule;
- scene-level approach probability;
- orientation fraction;
- normalized distance reduction;
- near-zone time;
- avoidance;
- robustness across receiver seeds/operating points;
- true simulator calls required to reach each performance threshold;
- emitted-control temporal spectrum and distribution.

The connectome generator wins the **engineering generator comparison** only if its frozen selected adapter achieves a larger `D*` or a preregistered equal-`D*` efficiency/robustness advantage over the MLP and direct-parametric generators on held-out receiver scenes.

It earns a **topology-specific emitter claim** only if true MaleCNS A also beats both the degree-preserving emitter null and the matched random recurrent emitter under the same boundary architecture, optimizer and evaluation budget.

## Two-connectome interpretation

A positive result does not establish that flies naturally communicate through this synthetic channel. The valid statement is narrower: a recurrent substrate constrained by the MaleCNS wiring can be used as a frozen generator of visual control dynamics that more effectively controls another MaleCNS-based receiver under the registered comparison.

If A succeeds only against one receiver seed or one narrow operating point, report a receiver-specific exploit rather than a robust visual language.

If A succeeds across receiver variation, the resulting generated traces motivate a separate analysis of whether a compact, reusable visual signalling vocabulary has emerged.

## Distillation after a positive

A successful A-generated sequence enters the same distillation ladder as any other winner:

`adaptive connectome policy -> prerecorded generated trajectory -> simplified trajectory -> low-parameter animation -> static stimulus`.

This separates the value of closed-loop adaptation from the value of the waveform itself. If replaying the frozen waveform preserves attraction, the emitter discovered a reusable signal. If replay fails but adaptive A succeeds, feedback is part of the mechanism.

## Implementation state

`src/connectome_generator.py` implements the first CPU reference loop:

- observable receiver context;
- trainable input/output adapters;
- frozen emitter recurrence;
- bounded visual-control decoding;
- renderer into receiver photoreceptors;
- frozen receiver recurrence and locomotion;
- complete generated-frame and behavioural traces.

`tests/test_connectome_generator.py` pins the boundary and closed-loop invariants. GPU population batching and the optimizer runner are the next implementation layer; they must preserve numerical parity with this reference path before decision-bearing runs.
