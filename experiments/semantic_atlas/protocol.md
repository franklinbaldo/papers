---
type: "Protocol"
title: "Semantic Atlas Experiment A — SRF and Observational Atlas"
description: "Pre-registered toy protocol for testing artificial quasars, calibration, semantic trajectories, and a graph atlas before any generation steering experiment."
tags: [semantic-atlas, preregistration, embeddings, quasars]
timestamp: 2026-08-09T00:17:00Z
---

# Semantic Atlas Experiment A — SRF and Observational Atlas

## Status

Pre-registration. No result in this document should be filled from memory or selected after seeing the outcome.

## Question

Can a mathematically fixed reference frame preserve enough local semantic geometry to support stable trajectory measurements and a reusable graph atlas?

## Models

Primary observer: `Qwen/Qwen3-Embedding-0.6B`.

Primary generator for the frozen trajectory corpus: `Qwen/Qwen3-0.6B`.

The implementation must record exact revisions when model downloads are first executed.

## SRF v0

1. Embed the calibration split.
2. Center and whiten to 64 dimensions.
3. Fix orientation deterministically.
4. Construct a regular simplex of 65 unit quasars.
5. Express states as canonical vectors and/or their 65 quasar projections.

No semantic label is assigned to a quasar.

## Dataset split

Create a small frozen corpus containing multiple domains and several continuations per origin prompt. Split by prompt family, not by individual continuation, so near-duplicates cannot cross calibration/test boundaries.

The first committed dataset manifest must be treated as frozen for the primary run. Corrections require a new manifest version and explanation.

## Primary tests

### T1 — synthetic rotation invariance

Apply random orthogonal rotations to calibration/test embeddings before calibration. After fitting the SRF independently, compare pairwise distances and trajectory metrics. The test succeeds if differences remain within a declared numerical tolerance.

### T2 — local neighborhood preservation

Compare k-nearest-neighbor sets before and after dimensional reduction/SRF projection for multiple `k`. Report recall, not only examples.

### T3 — trajectory stability

Measure path length, displacement, straightness, and turning angle under chunk/window choices fixed before the primary run.

### T4 — atlas repeatability

Build cell centers on the calibration split, observe test trajectories, and report transition stability across seeds. Visualization is diagnostic only.

## Negative controls

- random orthonormal basis with equal dimension;
- random projection with equal dimension;
- no whitening;
- native embeddings without SRF.

## Metrics

- pairwise-distance correlation;
- kNN recall;
- mean absolute difference in trajectory metrics;
- transition overlap/Jaccard;
- atlas coverage and unassigned/low-confidence rate;
- wall-clock and serialized atlas size.

## Failure criteria

The SRF hypothesis is weakened if it materially degrades local geometry versus dimensionality-matched controls or if trajectory measurements are unstable to modest representational choices.

The atlas hypothesis is weakened if transition structure does not repeat on held-out prompt families or if useful resolution requires nearly one cell per observed state.

## Reproduction

From `experiments/semantic_atlas`:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev,models]'
pytest
```

Model-backed collection scripts are added in the next PR so this layer remains cheap to unit-test without downloading model weights.

## Claim boundary

Success here demonstrates only that a toy navigational representation can be constructed. It does not demonstrate steering, reasoning improvement, token savings, FLOP savings, or cross-family universality.
