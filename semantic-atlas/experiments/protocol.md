---
type: "Protocol"
title: "Semantic Atlas Experiment A — SRF and Observational Atlas"
description: "Pre-registered toy protocol for testing artificial quasars, paired cross-model calibration, semantic trajectories, and a graph atlas before steering."
tags: [semantic-atlas, preregistration, embeddings, quasars]
timestamp: 2026-08-09T00:17:00Z
---

# Semantic Atlas Experiment A — SRF and Observational Atlas

## Status

Pre-registration. No result in this document should be filled from memory or selected after seeing the outcome.

## Question

Can a fixed artificial quasar geometry, together with an empirically anchored cross-model calibration, preserve enough semantic coordinates to support stable trajectory measurements and a reusable graph atlas?

## Models

Reference observer: `Qwen/Qwen3-Embedding-0.6B`.

Transfer observer: a second frozen open embedding model selected and revision-pinned before the primary model-backed run. Its role is not to be another Qwen checkpoint: the primary SRF test requires a genuinely independent native coordinate system.

Primary generator for the frozen trajectory corpus: `Qwen/Qwen3-0.6B`.

The implementation must record exact revisions when model downloads are first executed.

## SRF v0

The regular simplex fixes **geometry only**. It does not assign semantic meaning to its axes and cannot resolve the rotational gauge between independently trained embedding spaces by itself.

1. Freeze a shared calibration set of texts and preserve row-wise correspondence across observers.
2. Embed those same calibration items with the designated reference observer.
3. Center/whiten the reference embeddings to 64 dimensions and freeze the resulting calibration coordinates as the canonical target cloud.
4. Construct a regular simplex of 65 artificial unit quasars in that canonical space.
5. For every other observer, independently center/whiten its embeddings of the same calibration items.
6. Fit an orthogonal Procrustes map from those whitened, row-paired points to the **same frozen canonical targets**.
7. Evaluate only on held-out items that were not used to fit either transform.

No semantic label is assigned to a quasar. The quasars remain artificial landmarks; the empirical semantic anchoring is carried by the paired calibration transform.

## Dataset split

Create a small frozen corpus containing multiple domains and several continuations per origin prompt. Split by prompt family, not by individual continuation, so near-duplicates cannot cross calibration/test boundaries.

The cross-model calibration set, held-out SRF test set, and trajectory corpus must be distinct manifests. The first committed manifest for each is frozen for the primary run. Corrections require a new manifest version and explanation.

## Primary tests

### T1 — held-out cross-model coordinate agreement

Fit the reference frame and transfer-model Procrustes map **only** on paired calibration examples. On held-out texts, compare canonical vectors and all 65 quasar coordinates produced independently by both observers.

Report coordinate RMSE, cosine agreement, nearest-quasar agreement, and local-neighborhood agreement. This is the principal identifiability test: pairwise distances alone are insufficient because they are invariant under the very rotations the SRF is supposed to resolve.

### T2 — synthetic gauge recovery

Apply an unknown invertible linear transform (including arbitrary rotation/reflection and anisotropic scaling) to a latent synthetic semantic cloud, then fit each view to the same paired canonical targets. The test succeeds only if **held-out canonical coordinates**, not merely distances or path lengths, agree within the declared numerical tolerance.

As a negative control, shuffle calibration correspondences before Procrustes. Held-out coordinate agreement must collapse materially. If it does not, the test is not measuring semantic anchoring.

### T3 — local neighborhood and trajectory preservation

Compare k-nearest-neighbor sets before and after dimensional reduction/SRF projection for multiple `k`, then measure path length, displacement, straightness, and turning angle under chunk/window choices fixed before the primary run.

### T4 — atlas repeatability

Build cell centers on the calibration split, observe held-out trajectories, and report transition stability across seeds. Visualization is diagnostic only.

## Negative controls

- shuffled calibration correspondences;
- independent arbitrary orthonormal gauges without paired Procrustes;
- random projection with equal dimension;
- no whitening;
- native embeddings without cross-model alignment.

## Metrics

- held-out canonical-coordinate RMSE and cosine agreement;
- nearest-quasar agreement;
- pairwise-distance correlation;
- kNN recall;
- mean absolute difference in trajectory metrics;
- transition overlap/Jaccard;
- atlas coverage and unassigned/low-confidence rate;
- wall-clock and serialized atlas size.

## Failure criteria

The **cross-model SRF** hypothesis is weakened if paired calibration does not produce materially better held-out coordinate agreement than shuffled-correspondence and unaligned controls. Preserving distances while disagreeing on coordinates is a failure of the cross-model claim, not a success.

The single-model geometry hypothesis is weakened if SRF projection materially degrades local geometry versus dimensionality-matched controls or if trajectory measurements are unstable to modest representational choices.

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

Success here would show that a toy shared frame can be **empirically calibrated** across the tested observers. It would not make the simplex intrinsically semantic, establish a universal coordinate system, demonstrate steering, reasoning improvement, token savings, or FLOP savings.
