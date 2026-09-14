---
type: "Protocol"
title: "MaleCNS Visual Attractor Run 1 — Dynamic Positive Control"
description: "Frozen operating point, controls and decision rule for the first closed-loop visual-attraction run."
tags: [malecns, drosophila, visual-tracking, positive-control, preregistration]
timestamp: 2026-09-14T19:15:00-04:00
---

# Run 1 — dynamic positive control

Status: **frozen before any Run 1 behavioural result is observed**.

This document resolves implementation choices left open by `protocol.md`. Changing any value below after observing Run 1 is a new run, not a reinterpretation of Run 1.

## Biological basis of the positive control

The positive control is deliberately a small moving target in a courtship-primed male state rather than a static photograph.

Three results motivate that choice:

1. Ribeiro et al. showed that LC10 visual projection neurons are required for male orientation/proximity during courtship and preferentially respond to small moving objects. DOI: `10.1016/j.cell.2018.06.020`.
2. Hindmarsh Sten et al. showed that P1-mediated sexual arousal increases LC10a gain and enables high-fidelity tracking of a virtual female. DOI: `10.1038/s41586-021-03714-w`.
3. Kohatsu & Yamamoto showed courtship-like following of artificial moving light targets after courtship-state priming; a canonical assay used a `15°` square moving at `53°/s`. DOI: `10.1038/ncomms7457`.

These papers motivate the starting region of stimulus space. They do not imply that the MaleCNS implementation must reproduce the behaviour.

## Canonical graph

Use the full compiled MaleCNS graph from the existing repository pipeline, not a subgraph and not a replacement connectome.

The recurrent operator is normalized at runtime by the already measured leading-eigenvalue scale:

- `spectral_scale = 3776.27`;
- `gain = 1.0`;
- `leak = 0.2`.

The graph and interface SHA-256 fingerprints are written into the result manifest. A mismatch produces a different run.

## Frozen sensory and state drive

- visual input types: `R1-6`, `R7`, `R8`;
- azimuth: pinned optic-column mapping from `flyconnectome/2025malecns@67767d2233657983993ff6c2be48e836a935863c`;
- `visual_scale = 0.5`;
- courtship-prime population: all resolved `P1_*` cell types;
- `prime_scale = 0.08`;
- `dt = 0.02` simulation units/seconds in the engineering arena.

The prime is identical for every stimulus condition. Run 1 does not tune prime amplitude against the decision scenes.

## Frozen motor decoder

Primary steering readout:

- left/right `DNa02` activity;
- turn command `tanh(4 * (right - left))`;
- maximum engineering turn-rate scale `4 rad/s`.

Primary forward readout:

- bilateral `DNg100` activity;
- baseline forward speed `0.12`;
- activity-dependent increment scale `0.20`.

The interface must resolve `DNa02` and `DNg100` on both sides before Run 1. The broad descending-neuron fallback in the generic scaffold is **not authorized as a silent Run 1 substitute**.

## Frozen stimuli

All targets use physical diameter `0.25` in arena units and full contrast.

`moving_target`:

- sinusoidal angular path;
- amplitude `18°`;
- frequency `0.47 Hz`;
- peak angular velocity about `53.2°/s`.

`static_equivalent`:

- same target and contrast;
- zero path motion.

`blank`:

- no target drive.

`random_motion`:

- same target;
- deterministic band-limited irregular path;
- amplitude bounded by `18°`;
- seed `20260914`.

The random-motion control is not required to match the exact temporal spectrum of the sinusoid in Run 1; a spectrum-matched control is added after a positive gate and before optimization claims.

## Reference distance and horizon

The easy distance `d0` is defined by a `15°` apparent target width:

`d0 = (0.25 / 2) / tan(7.5°) = 0.9494692641` arena units.

Each trajectory receives enough registered time to traverse `1.5 * d0` at the baseline speed plus `2.0 s` acquisition allowance. With `dt = 0.02`, this is `694` recurrent steps.

## Scene design

- `32` scene/swarm seeds;
- seed sequence `20260914 ... 20260945`;
- `64` flies per stimulus per scene;
- radial jitter `±5%` around `d0`;
- headings uniform on `[-pi, pi]`;
- candidate and every control reuse the exact same fly starts inside a scene;
- all four stimuli are evaluated together as independent columns of one batched recurrent simulation.

The statistical unit is the scene seed, not the individual fly.

## Primary behavioural event

A fly is an `approach` when its minimum radial distance is at least `50%` smaller than its initial radial distance before the horizon.

Run 1 reports the full behavioural vector, but the pre-frozen gate is:

- moving-target scene-aggregated approach probability `>= 0.60`; and
- moving-target approach exceeds the strongest of `static_equivalent`, `blank`, and `random_motion` by at least `0.10`.

This is the same `capture_pass` rule that will later define whether a curriculum distance is captured.

## Run 1 interpretation

If the gate passes, proceed immediately to the parametric evolutionary search at `d0` and then the distance curriculum.

If the gate fails, do not run a large stimulus optimizer. Diagnose the interface/operating point on a separately labelled calibration run and then preregister Run 2. A failed Run 1 remains reported as failed.

## Output contract

Heavy output stays outside GitHub:

- per-scene compressed behavioural trajectories;
- per-fly metrics;
- any videos/render caches.

GitHub receives the small `positive-control-summary.json` containing:

- graph/interface hashes;
- all frozen parameters;
- scene seeds;
- scene-level summaries;
- attraction by initial angular sector;
- aggregate decision values;
- `capture_pass`.
