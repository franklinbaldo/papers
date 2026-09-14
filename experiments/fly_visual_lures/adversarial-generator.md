---
type: "Protocol"
title: "Adversarial Neural Generator Arm for Fly Visual Lures"
description: "Registered optimizer arm in which a neural generator proposes printable patterns and a learned critic predicts population-level fly attraction while the simulator remains the ground-truth evaluator."
tags: [drosophila, gan, adversarial-learning, visual-lure, simulation]
timestamp: 2026-09-14T17:50:00-04:00
---

# Adversarial neural generator arm

This is an optimizer arm inside the independent `fly_visual_lures` experiment. It does not replace the evolutionary baseline.

## Roles

- `G(z)`: neural generator mapping latent `z` to a printable `32 x 32` pattern.
- `C(p, s)`: learned critic/surrogate predicting the attraction score of pattern `p` under a compact scene/swarm summary `s`.
- `FlyArena(p, swarm, scene)`: authoritative evaluator. Its measured fly behaviour is the only ground-truth reward.

The loop is:

```text
z -> G -> pattern
        -> FlyArena -> real population attraction R
        -> replay buffer (pattern, scene, R)
        -> C learns R
C-gradient -> G proposes better patterns
```

This is adversarial/generative in optimization structure, but unlike an ordinary image GAN the critic does not define realism. It approximates the expensive behavioural objective.

## Anti-collusion rule

The generator is never credited for fooling `C`. Every candidate entering validation or the final table is rescored by `FlyArena`. A fixed fraction of each generation is also evaluated by `FlyArena` and added to the replay buffer, so drift between critic and simulator is measured continuously.

Report:

- critic prediction error on unseen simulator evaluations;
- rank correlation between critic score and simulator score;
- fraction of generated candidates directly evaluated;
- best simulator-confirmed attraction found per simulator call.

If `C` becomes inaccurate in the region explored by `G`, optimization pauses for new simulator labels rather than accepting critic-only wins.

## Printable constraint

Gate 1 remains binary black/white. `G` may emit logits during training, but simulator/decision evaluation uses the same deterministic binarization rule frozen before search. No subpixel or imperceptible perturbation is allowed to count as the printable candidate.

An optional second adversary may penalize patterns whose attraction disappears under print/render transformations. It may regularize `G` but cannot substitute for real domain-randomized simulator evaluation.

## Multi-fly critic target

The critic predicts a robust **population** target, not one fly's trajectory. Training labels come from a shared pattern evaluated on a deterministic swarm:

`target = [mean attraction, lower-tail attraction, approach rate, dwell/landing]`.

The primary scalar may be a frozen weighted aggregate of these outputs, but the vector is retained so the generator cannot improve one pathological component while degrading the others unnoticed.

## Comparison against evolutionary search

Both optimizers receive the same simulator-call budget and the same train/validation/test scene distributions.

Decision outputs:

- best held-out attraction at fixed simulator budget;
- simulator calls required to reach fixed attraction thresholds;
- robustness across held-out swarm sectors/distances;
- diversity of high-performing printable patterns;
- final sim-to-real candidate quality if Gate 4 is eventually authorized.

A GAN win means only that learned proposal generation found better simulator-confirmed patterns more efficiently. It is not evidence that a GAN is necessary for visual attraction.
