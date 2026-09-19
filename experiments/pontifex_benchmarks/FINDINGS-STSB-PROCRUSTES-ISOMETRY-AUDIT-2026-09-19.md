---
type: "Findings Record"
title: "Pontifex STS-B Procrustes audit: task retention is not transport evidence"
description: "Mechanism audit showing that the rectangular Procrustes baseline is a semi-orthogonal isometry of A, so retained cosine-based STS utility is non-discriminant for cross-space transport; adds B-specific negative controls."
timestamp: 2026-09-19T08:20:00-04:00
tags: [pontifex, benchmark, stsb, procrustes, isometry, negative-control, correction]
---

# Pontifex STS-B Procrustes audit: task retention is not transport evidence

## Status

**Interpretive correction plus discriminant experiment.** This note was written after inspecting the first STS-B test result, so it is a post-hoc mechanism audit rather than a fresh confirmatory benchmark.

The correction itself is algebraic and does not depend on another dataset run: the rectangular Procrustes map used in the first benchmark is semi-orthogonal. Therefore its apparently strong STS-B score cannot, by itself, be counted as evidence that B-specific geometry was recovered.

Executable discriminant: `experiments/pontifex_benchmarks/stsb_procrustes_isometry_audit.py`  
Workflow: `.github/workflows/pontifex-stsb-procrustes-isometry-audit.yml`

## Why the previous interpretation was too strong

The first STS-B record observed that Procrustes reached about `0.8238` Spearman at `K=8/16`, close to the A-only score of `0.8203`, and described this as evidence that a geometry-preserving global map might already recover useful shared geometry.

That reading conflated **retention of A geometry** with **reconstruction of B geometry**.

Let the fitted rectangular Procrustes map be `W ∈ R^(d_A × d_B)` with `d_A <= d_B`. The implementation computes

`W = U V^T`

from the thin SVD of the anchor cross-covariance. Because `U` is square orthogonal and the rows of `V^T` are orthonormal,

`W W^T = I_(d_A)`.

For any row vectors `x,y ∈ R^(d_A)`, before centering/translation,

`(xW)(yW)^T = x W W^T y^T = x y^T`

and

`||xW|| = ||x||`.

Hence

`cos(xW, yW) = cos(x, y)`.

STS-B is scored from cosine similarity. A high score after the pure semi-orthogonal map is therefore expected even if the orientation of `W` carries **zero useful information about B**.

## Reproducible numerical self-check

Using the exact dimensions of the benchmark (`d_A=384`, `d_B=768`) and the same Procrustes construction on random anchors, a local numerical sanity check gave the following normalized `||WW^T-I||_F` and maximum absolute cosine change under `x -> xW`:

| K | relative Frobenius error | max |Δ cosine| |
|---:|---:|---:|
| 8 | `2.16e-15` | `3.12e-16` |
| 16 | `2.19e-15` | `3.12e-16` |
| 32 | `2.23e-15` | `3.05e-16` |
| 64 | `2.64e-15` | `4.86e-16` |
| 128 | `3.09e-15` | `4.79e-16` |
| 256 | `3.58e-15` | `5.10e-16` |

These are floating-point residuals around the exact algebraic identity, not empirical evidence about STS-B.

## What remains empirically discriminant

The actual benchmark applies a centered map and adds the B-anchor mean, so its final cosine is not mathematically identical to A-only. But the decisive question is no longer “does Procrustes retain STS score?” It is:

> Does the **correct A↔B pairing** improve B-specific reconstruction beyond maps that have the same isometric capacity but no identity-specific correspondence?

The new executable therefore compares, at each frozen `K`:

- correctly paired Procrustes;
- shuffled-correspondence Procrustes using the same A anchors, same B anchors and therefore the same anchor means;
- random Stiefel isometries with the same centering and B-mean translation.

The primary mechanism endpoints do **not** use STS labels:

1. sentencewise cosine between mapped A test vectors and their true B test vectors;
2. RMSE between mapped-A and true-B pair cosines;
3. Spearman agreement between mapped-A and true-B pair geometry.

STS test Spearman is retained only as a secondary, explicitly post-hoc task-retention diagnostic.

## Split and leakage boundary

The first STS-B test result has already been observed, so this diagnostic is not presented as fresh confirmation. The data roles remain explicit:

- **assembly:** dataset/model choice and this diagnostic were motivated by the already-inspected first STS-B run;
- **student:** only leakage-filtered STS-B train A↔B correspondences fit maps;
- **validation:** unused by this parameter-free audit;
- **test:** evaluation only; no test label or B test vector fits or selects a map.

This preserves the operational separation of student/evaluation data while also recording the unavoidable fact that the benchmark family itself is now post-hoc with respect to STS-B.

## Evidence vs hypothesis

### Evidence

- The Procrustes map class used here is semi-orthogonal and preserves all A-space inner products and cosines before the benchmark's centering/translation step.
- Therefore near-A STS performance after Procrustes is **not sufficient evidence of cross-space transport**.
- The earlier phrase “roughly one quarter of B utility recovered” is numerically true as a task-score ratio but should not be interpreted as one quarter of B geometry recovered.

### Hypothesis still open

- Correct paired Procrustes may still recover B-specific coordinates or pair geometry beyond shuffled/random isometries.
- If that happens, Procrustes can remain a useful coarse map for a residual Pontifex field.
- If it does not, the appropriate baseline is not “Procrustes transport” but simply an isometric preservation control, and the proposed Procrustes+residual follow-up must be reconsidered.

No result in this note supports claims about a universal latent manifold, Torus causal structure, or physical non-locality.

## Decision rule for the running discriminant

The B-specific interpretation is strengthened only if correctly paired Procrustes is consistently better than both shuffled-pair and random-isometry controls on direct B point alignment **and** B pair-geometry reconstruction. Task Spearman alone cannot pass this gate.

The external workflow result is intentionally not inferred here while it is pending; once complete, its positive or negative outcome should be appended without changing this algebraic correction.
