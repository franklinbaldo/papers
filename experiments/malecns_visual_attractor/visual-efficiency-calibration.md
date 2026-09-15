---
type: "Protocol"
title: "MaleCNS visual-efficiency calibration"
description: "Energy-matched structure-vs-brightness curriculum for the stationary-screen reward loop."
tags: [malecns, drosophila, visual, calibration, kaggle]
timestamp: 2026-09-14T21:45:00-04:00
---

# Visual-efficiency calibration

This calibration follows the successful stationary-screen engineering run. It is not a behavioural Run 2 and it does not reinterpret the failed preregistered Run 1.

## Question

Can the reward-coupled frozen MaleCNS generator produce a structured screen pattern that excites and guides another frozen MaleCNS more than simpler controls **when visual energy is matched**, and does any advantage survive as that visual-energy budget is reduced?

## Anti-brightness constraints

- Visual budgets are fixed before execution: mean resolved-receptor intensity `0.12 -> 0.06 -> 0.03`.
- Every non-blank condition is normalized per frame to the same budget.
- The transducer bias is frozen at exactly zero; ES may change only the `6 x 6` body-latent-to-screen weight matrix.
- The generator body latent is amplified by one declared engineering gain (`20,000`) before the zero-bias transducer because the preceding calibration measured natural readouts near `1e-5`.
- Only the 2,627 optic-column-resolved visual receptors participate in screen-energy accounting and screen drive. The 1,395 unresolved receptors remain present in the MaleCNS state but receive zero screen input here, preventing optimization against fallback coordinates.

## Matched conditions

All conditions reuse the same receiver starts and begin 45 degrees off the display bearing:

1. `learned` — live reward-coupled MaleCNS generator and structured three-lobe screen pattern;
2. `uniform_tv` — softly edged 16:9 illuminated display patch at the same per-frame visual-energy budget;
3. `spatial_shuffle` — the generated receptor intensities deterministically permuted only among resolved optic columns, preserving their framewise value distribution and energy;
4. `blank` — zero visual drive.

The generator receives reward only from the `learned` receiver state. Controls do not feed the generator.

## Selection

For each candidate:

`advantage = integrated_excitation(learned) - max(integrated_excitation(uniform_tv), integrated_excitation(spatial_shuffle), integrated_excitation(blank))`

The highest advantage advances the ES center. The center is carried from each energy budget into the next lower budget.

Behavioural quantities — approach fraction, final distance and final orientation error — are secondary diagnostics. A later behavioural experiment will require a separate frozen success gate and stronger spatial-acquisition conditions.

## Execution

GPU execution remains GitHub Actions -> public Kaggle. The planned first calibration uses 8 matched receivers, population 7, 2 generations per budget and 300 recurrent steps per candidate/control block. Receptor raster telemetry is emitted every 100 steps.
