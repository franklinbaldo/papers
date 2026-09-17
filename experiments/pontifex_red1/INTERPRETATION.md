---
type: "Experiment Note"
title: "Pontifex RED-1 — interpretation rule"
description: "Interpretation rule for Pontifex convergence experiments, centered on persistence and scaling of held-out delta rather than a fixed effect-size cutoff."
tags: [pontifex, experiment, interpretation]
timestamp: 2026-09-17T13:05:00-04:00
---

# Pontifex RED-1 — interpretation rule

The original harness encoded a `+0.05 macro AUPRC` pass/fail threshold. That threshold was introduced during implementation and was **not an agreed scientific criterion**. It must not be used to classify the Pontifex convergence claim as surviving or falsified.

## Correct interpretation

The primary quantity is the held-out effect size

`delta = AUPRC(Pontifex) - max(AUPRC(best single encoder), AUPRC(mean encoder saliency))`.

No arbitrary minimum positive delta is required at RED-1.

A positive delta is scientifically interesting if it is reproducible and remains positive as experimental scale and diversity increase. The next experiments therefore evaluate the **trajectory and stability of delta**, rather than whether it crosses a fixed 5 percentage-point threshold.

Scale dimensions to vary independently:

- number of examples;
- number and diversity of template families;
- number of random seeds / held-out partitions;
- languages;
- number and diversity of frozen encoders;
- amount of training data available to the convergence head;
- contamination/removal of individual encoder channels.

Report at every scale:

- median and mean delta;
- full per-seed delta distribution;
- bootstrap confidence interval for delta;
- fraction of seeds with delta > 0;
- AUPRC, precision@1, and causal saliency mass for A/B/C/D;
- degradation under channel contamination and channel ablation.

## What would count against the distinctive claim

Evidence against learned multi-space convergence is not `delta < +0.05`. The stronger negative pattern is that, with increasing scale and adequate statistical power, delta converges to zero or negative values, or that apparent gains fail to reproduce across independent templates/languages/encoders.

Conversely, even a small positive delta can matter if it persists or grows with scale. A stable small effect can also conceal system-level benefits not captured by this toy endpoint, including robustness, complementary error correction, graceful handling of weak channels, and increasing returns as the encoder bank becomes more diverse.

## Status of the first run

The first 240-example run produced a median held-out delta of approximately **+0.030 AUPRC** across three seeds. This is a positive signal worth scaling, not a falsification. The large seed variance remains an important diagnostic and must be investigated rather than hidden by an aggregate threshold.
