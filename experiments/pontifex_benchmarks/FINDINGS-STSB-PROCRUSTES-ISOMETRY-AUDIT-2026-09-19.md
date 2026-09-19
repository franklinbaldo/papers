---
type: "Findings Record"
title: "Pontifex STS-B Procrustes audit: task retention is not transport evidence"
description: "Mechanism audit showing that rectangular Procrustes is a semi-orthogonal isometry of A; task retention is non-discriminant, while direct B-coordinate alignment is real and B pair-geometry transfer appears only at larger K."
timestamp: 2026-09-19T08:20:00-04:00
tags: [pontifex, benchmark, stsb, procrustes, isometry, negative-control, correction]
---

# Pontifex STS-B Procrustes audit: task retention is not transport evidence

## Status

**Completed post-hoc mechanism audit.** This diagnostic was designed after inspecting the first STS-B test result, so it is not a fresh confirmatory benchmark. Its purpose is narrower: determine whether the surprisingly high same-K Procrustes STS score reflected actual A→B transport or merely preservation of A geometry.

Run: https://github.com/franklinbaldo/papers/actions/runs/35442332162  
Artifact: https://github.com/franklinbaldo/papers/actions/runs/35442332162/artifacts/10583574173  
Executable: `experiments/pontifex_benchmarks/stsb_procrustes_isometry_audit.py`  
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

## Numerical isometry check on the actual benchmark embeddings

The workflow verifies the identity on the actual MiniLM→MPNet maps. Across `K=8…256`:

- normalized `||WW^T-I||_F` lies between `3.64e-7` and `3.87e-7` in float32;
- the largest absolute test-pair cosine change under the pure map `x -> xW` is `2.38e-7` at every K;
- mean absolute cosine change is about `4e-8`.

These are floating-point residuals around the exact algebraic identity.

## Discriminant controls

At each frozen K, the audit compares:

- correctly paired Procrustes;
- 16 shuffled-correspondence Procrustes maps using the same A anchors, same B anchors and therefore the same anchor means;
- 16 random Stiefel isometries with the same centering and B-mean translation.

The primary mechanism endpoints do **not** use STS labels:

1. sentencewise cosine between mapped A test vectors and their true B test vectors;
2. RMSE between mapped-A and true-B pair cosines;
3. Spearman agreement between mapped-A and true-B pair geometry.

STS test Spearman is retained only as a secondary, explicitly post-hoc task-retention diagnostic.

## Result 1 — STS retention is a negative control, not transport evidence

The correctly paired Procrustes map did **not** outperform the negative controls on STS Spearman. In fact, its task score was below the median shuffled and random-isometry score at every tested K:

| K | paired Procrustes | shuffled median | random-isometry median |
|---:|---:|---:|---:|
| 8 | `0.82384` | `0.82511` | `0.82498` |
| 16 | `0.82393` | `0.82487` | `0.82467` |
| 32 | `0.82048` | `0.82237` | `0.82284` |
| 64 | `0.81913` | `0.82306` | `0.82329` |
| 128 | `0.81884` | `0.82236` | `0.82196` |
| 256 | `0.81941` | `0.82179` | `0.82160` |

This is strong negative evidence against interpreting the first run's near-A STS score as B-specific transport. The earlier phrase “roughly one quarter of B utility recovered” remains arithmetically true as a task-score ratio, but it is **not** a valid estimate of B-geometry recovery.

## Result 2 — correct correspondences do recover B coordinates

A different endpoint gives a genuine positive result. Mean sentencewise cosine between mapped A and the corresponding true B test vector increased monotonically with K:

| K | paired mean cosine | shuffled median | random median |
|---:|---:|---:|---:|
| 8 | `0.0520` | `0.0224` | `0.0232` |
| 16 | `0.0723` | `0.0223` | `0.0232` |
| 32 | `0.1310` | `0.0198` | `0.0227` |
| 64 | `0.2129` | `0.0248` | `0.0232` |
| 128 | `0.3272` | `0.0199` | `0.0240` |
| 256 | `0.4313` | `0.0254` | `0.0233` |

At every K, correctly paired Procrustes beat **all 16 shuffled controls and all 16 random-isometry controls** on this direct coordinate-alignment endpoint.

Therefore the correspondences are doing real identity-specific work. The important correction is that this work is visible in **B-coordinate alignment**, not in retained STS score.

## Result 3 — pair-geometry transfer emerges only after more correspondences

The B pair-geometry endpoint is more demanding and gives a graded result.

- `K=8`: paired Procrustes is not better than the negative controls; its B-geometry RMSE is `0.14392` and Spearman `0.95253`, both slightly worse than the control medians.
- `K=16`: RMSE improves beyond all 16 controls (`0.10914`), but geometry Spearman is not beyond all controls.
- `K=32`: RMSE beats all controls and Spearman beats all shuffled maps, but not every random isometry.
- `K=64,128,256`: paired Procrustes beats **all 16 shuffled and all 16 random controls** on both B-geometry RMSE and B-geometry Spearman.

At `K=64`, for example, paired RMSE is `0.08564` versus shuffled median `0.09202` and random median `0.09121`; paired geometry Spearman is `0.95508` versus `0.95333` and `0.95360`.

The effect is numerically modest because A and B already have very similar task-pair geometry before any mapping: raw A-vs-B pair-cosine Spearman is `0.95624`. This high baseline similarity is itself a reason not to oversell small differences.

## Split and leakage boundary

The first STS-B test result had already been observed before this audit was designed, so the whole diagnostic is explicitly post-hoc with respect to benchmark/model choice. Within the executable, data roles remain separated:

- **assembly:** benchmark/model choice and the audit question were motivated by the already-inspected first STS-B result;
- **student:** only leakage-filtered STS-B train A↔B correspondences fit maps;
- **validation:** unused by this parameter-free audit;
- **test:** evaluation only; no test label or B test vector fits or selects a map.

The leakage audit remains `10,534` raw unique train candidates, `463` exact validation/test overlaps removed, and `10,071` eligible train candidates.

## Evidence vs hypothesis

### Evidence

- The Procrustes class used here is semi-orthogonal and therefore preserves A-space cosines under the pure map.
- Retained STS score is non-discriminant: shuffled and random isometries retain the task at least as well as paired Procrustes.
- Correct correspondences nevertheless produce strong, monotonic B-coordinate alignment, beating every tested shuffled/random control at every K.
- B pair-geometry reconstruction becomes consistently better than the tested controls only in the moderate/high-K regime, cleanly so from `K=64` onward in this 16-control bank.

### Hypothesis still open

- Procrustes may be useful as a **coarse coordinate aligner** before a small learned residual/deformation field.
- That residual should be justified by incremental B-specific reconstruction on a fresh benchmark, not by preserving a cosine-based task that the coarse map preserves by construction.
- The apparent transition around `K≈64` is descriptive in this post-hoc audit; it is not a preregistered sample-complexity threshold.

No result here establishes a universal latent manifold, Torus causal structure, physical non-locality, or a general law of semantic-space equivalence.

## Consequence for the next Pontifex experiment

The next fair comparison is no longer `Pontifex residual vs A-only`. It should be:

`frozen paired Procrustes coarse map` **vs** `the same frozen coarse map + a low-capacity residual Pontifex field`,

on a **fresh external benchmark/model pair** with assembly/student/validation/test roles fixed before test evaluation. Primary endpoints should include direct B-coordinate and B-geometry reconstruction; downstream task utility should be secondary unless the task is not invariant to the coarse-map class.
