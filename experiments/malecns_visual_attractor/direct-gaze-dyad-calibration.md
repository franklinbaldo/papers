---
type: "Protocol"
title: "MaleCNS Direct-Gaze Dyad Calibration"
description: "Reciprocal full-visual MaleCNS calibration after Run 1 failed to separate moving and control conditions."
tags: [malecns, drosophila, visual, dyad, direct-gaze, calibration, kaggle]
timestamp: 2026-09-14T20:45:00-04:00
---

# Direct-gaze dyad calibration

Status: **engineering calibration after the frozen Run 1 failed**. This is not Run 2 and cannot rescue or reinterpret Run 1.

## Why this calibration exists

Run 1 completed all 32 registered scenes and produced identical approach rates for `moving_target`, `static_equivalent`, `random_motion`, and `blank` within every scene. The aggregate moving and strongest-control approach probability were both `0.1787109375`, so the preregistered capture gate failed.

The next task is therefore not stimulus optimization. It is to establish a live causal visual channel from rendered stimulus through the mapped visual receptors and frozen MaleCNS dynamics into motor readout.

## Simplifications

The first calibration deliberately removes target acquisition and courtship assumptions:

- the receiving fly is in **direct-gaze mode**: the partner image is centered on the visual field;
- all currently mapped visual receptors are used, not a reduced proxy population;
- no pC1/P1 courtship prime is applied (`prime_scale = 0`);
- no claim about female appearance, color preference, mating state, or natural social signalling is tested here;
- the two MaleCNS graphs remain frozen.

## Reciprocal loop

Two independent MaleCNS states, A and B, run simultaneously.

A rendered partner pattern is delivered through the receiver's complete mapped visual interface. Apparent size depends on current A-B distance. A simple body-plus-side-lobes silhouette is centered on the retina, and side-lobe asymmetry follows the emitter's previous turn command. Thus the loop is causal:

`A state -> A motor -> image seen by B -> B state -> B motor -> image seen by A -> ...`

The renderer is an engineering coupling used to test whether reciprocal visual dynamics can exist. It is not asserted to be a biologically natural fly communication code.

## Conditions

All conditions reuse the exact same pair starts inside a scene:

1. `reciprocal` — A sees B and B sees A with dynamic distance/turn feedback;
2. `one_way` — B sees A while A receives no partner image;
3. `static_pair` — both receive a fixed centered partner pattern whose size is frozen at the initial distance;
4. `blank_pair` — neither receives visual input.

## Starting regime

The partner physical size is `0.25` arena units and initial apparent width is `30°`, intentionally easier than Run 1's `15°` target. The direct-gaze condition keeps the partner centered; distance/offset curriculum comes only after this channel is demonstrated.

Calibration sweep:

- visual scales: `0.5`, `2.0`, `8.0`;
- scenes: `6`;
- pairs per condition per scene: `32`;
- steps: `300`;
- `dt = 0.02`;
- seeds: `20260950 ... 20260955`;
- `spectral_scale = 3776.27`;
- `gain = 1.0`;
- `leak = 0.2`;
- `prime_scale = 0.0`.

## Causal ladder

For every condition the calibration records:

- external visual RMS on the full mapped receptor population;
- visual-receptor state RMS after recurrent update;
- forward and turn motor commands;
- pair distance through time;
- minimum/final pair distance and normalized reduction;
- pair capture event (`>=50%` minimum-distance reduction).

The diagnostic compares `reciprocal` and `one_way` against their matched `blank_pair` trajectories. A scale is marked `channel_live` only as an engineering indication that nonzero visual drive reaches receptor state and produces a nonzero matched motor difference. It is not a behavioural success criterion.

The smallest scale with a live channel may inform a later preregistered Run 2 operating point. Run 2 must be frozen separately before its behavioural result is inspected.

## Observability

The Kaggle execution should be public. The kernel log prints one JSON progress record after every scene with condition summaries, causal diagnostics, scene time, elapsed time, and ETA. Small public outputs include:

- `direct-gaze-dyad-summary.json`;
- `progress.jsonl`;
- graph/interface provenance;
- the visual-interface manifest.

Trajectories remain available as Kaggle output but are not required for GitHub success-path retrieval.
