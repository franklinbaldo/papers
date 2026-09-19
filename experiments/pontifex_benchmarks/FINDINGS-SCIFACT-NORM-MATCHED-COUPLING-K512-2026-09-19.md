---
type: "Findings Record"
title: "Pontifex SciFact norm-matched coupling specificity at K=512"
description: "A stronger residual-norm-matched null preserves the shared-warp effect and narrows the semantic-specificity question; finite-bank evidence favors true correspondence, but the predeclared bootstrap criterion still does not support semantic specificity."
timestamp: 2026-09-19T12:58:00-04:00
tags: [pontifex, scifact, beir, retrieval, mechanism, null-control, leakage-audit]
---

# Pontifex SciFact norm-matched coupling specificity at K=512

## Status

**Completed held-out external mechanism control.** Protocol: `PROTOCOL-SCIFACT-NORM-MATCHED-COUPLING-K512-2026-09-19.md`.

Run: <https://github.com/franklinbaldo/papers/actions/runs/35455793661>

Artifact: <https://github.com/franklinbaldo/papers/actions/runs/35455793661/artifacts/10587763809>

## Leakage audit

**PASS.** The K=512 anchor sequence, student/validation/test/corpus manifests, residual-norm strata, and both permutation banks were frozen before test qrels were used. Task-label budget for fit/selection was zero. True B test/corpus coordinates were not encoded for this control.

## Result

Official SciFact nDCG@10:

- TRUE correspondence: `0.649954`;
- norm-matched coupled null mean: `0.640712` (median `0.641117`, range `0.630035–0.649907`);
- norm-matched independent null mean: `0.619617` (median `0.619678`).

Primary contrasts:

- TRUE − norm-matched coupled mean: `+0.009241`;
- finite-bank upper-tail p: `0.015625`;
- paired-query bootstrap mean: `+0.009241`, 95% percentile CI `[-0.003507,+0.021617]`, `P(mean>0)=0.9238`;
- coupled − independent mean: `+0.021095`, paired-query bootstrap 95% CI `[+0.008416,+0.034615]`, `P(mean>0)=0.9998`.

## Predeclared decision

- semantic-specificity supported: **false**;
- shared-warp coherence supported: **true**.

The stronger null removes the easy explanation that the coupled null was winning merely because it preserved a different residual-magnitude distribution. Exact A↔B identity now beats every mean norm-matched coupled null strongly enough to give a finite-bank p of `1/64`, but the paired-query bootstrap interval still crosses zero. Under the frozen decision rule, that is not enough to promote semantic specificity to a supported mechanism claim.

## Interpretation boundary

The result strengthens a narrower statement: **applying a coherent deformation to both query and document sides matters robustly for held-out retrieval**, and correct correspondence has a promising positive point estimate beyond residual-norm-matched coherent deformations. It does not yet establish that small-K semantic identity is the causal source of the SciFact gain, nor does it rescue the low-budget thesis.

This control should remain secondary to the official downstream benchmark result and to cross-task replication.
