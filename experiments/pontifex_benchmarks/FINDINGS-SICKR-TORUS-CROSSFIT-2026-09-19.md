---
type: "Findings Record"
title: "Pontifex SICK-R strict cross-fit: B-specific geometry improves without a primary task gain"
description: "Prospective cross-benchmark SICK-R result after correcting the residual selector to strict within-student cross-fitting: the local residual improves B-specific geometry at several K, but does not establish downstream Pearson competitiveness and is non-monotonic across budgets."
timestamp: 2026-09-19T09:36:00-04:00
tags: [pontifex, torus, benchmark, sick-r, transport, residual, cross-fitting, negative-result, leakage-audit]
---

# Pontifex SICK-R strict cross-fit: B-specific geometry improves without a primary task gain

## Status

**Completed prospective cross-benchmark run with a pre-outcome selector correction.** The A/B model pair came from the preceding STS-B work, but SICK-R is a fresh external task. The strict cross-fit correction described below was made from a static code audit before any successful SICK result existed.

Run: https://github.com/franklinbaldo/papers/actions/runs/35445822476  
Artifact: https://github.com/franklinbaldo/papers/actions/runs/35445822476/artifacts/10584829075  
Protocol: `experiments/pontifex_benchmarks/PROTOCOL-SICKR-TORUS-RESIDUAL-2026-09-19.md`  
Executable: `experiments/pontifex_benchmarks/sickr_torus_residual.py`  
Workflow: `.github/workflows/pontifex-sickr-torus-residual.yml`

## Two corrections before interpreting the benchmark

### 1. The original selector was not truly leave-one-out

The first implementation excluded the held anchor from the residual-kernel weights, but the Procrustes coarse map and its centroids had already been fitted with all K anchors. Consequently the held anchor's B coordinate still influenced the coarse prediction being scored. This did not cross the `D_student`/`D_val`/`D_test` boundary, but it made the anchor reconstruction criterion optimistic.

Before a successful SICK execution, the selector was changed to deterministic four-fold outer cross-fitting. For each held fold, both Procrustes and the residual basis are fitted only on the other folds; `(tau, lambda)` is chosen from the aggregate held-fold B-coordinate cosine loss and only then is the deployment map refitted on all K student anchors.

The correction materially changes the selected residual in four of six budgets: legacy pseudo-LOO selected `(tau, lambda)=(0.8,0.25)` at K=8/16, `(0.2,0.25)` at K=128 and `(0.1,0.25)` at K=256, whereas strict cross-fit selected `(0.2,1.5)`, `(0.05,1.5)`, `(0.05,0.5)` and `(0.05,0.5)`, respectively. At K=32/64 both selectors choose `(0.8,0.25)`.

### 2. The first workflow failure was infrastructure, not scientific evidence

Run `35444648938` failed before producing a benchmark JSON because the then-unbounded `datasets>=3.0` dependency resolved to a version that no longer executes the script-backed `RobZamp/sick` loader. The executable was pinned to `datasets>=3.0,<4.0` and now explicitly opts into that predeclared dataset script with `trust_remote_code=True`. No model, K budget, seed, split rule, hyperparameter grid or endpoint was changed. The failed run therefore carries **no positive or negative evidence about Pontifex**.

## Information boundary

The successful artifact reports `leakage_audit: PASS`.

- `D_assembly`: not used here; A and B are frozen external encoders.
- `D_student`: only exact-text-filtered SICK train sentences may supply the K unlabeled A↔B correspondences and all transport selection.
- `D_val`: diagnostic reporting only; no fit or hyperparameter selection.
- `D_test`: final scoring only; B-test coordinates are evaluation oracle only.

SICK contains substantial exact sentence reuse across its public splits. Of 4,789 unique train sentence candidates, 3,931 also occurred in validation or test and were removed before the seeded anchor permutation, leaving 858 eligible student sentences. Zero task labels are used for transport fitting or selection.

## Test result

Test oracle context is narrow: A-only Pearson is `0.836248` and B-oracle Pearson is `0.838836`; their difference is only `0.002588`. Consequently downstream Pearson has little dynamic range here and is kept separate from the B-specific transport endpoints.

| K | strict `(tau, lambda)` | Δ B-coordinate cosine | Δ B pair-RMSE | Δ B pair-geometry Spearman | Δ SICK Pearson |
|---:|:---:|---:|---:|---:|---:|
| 8 | `(0.20, 1.50)` | `+0.000022` | `-0.003044` | `+0.004646` | `-0.000039` |
| 16 | `(0.05, 1.50)` | `+0.000442` | `-0.008432` | `+0.011928` | `+0.001105` |
| 32 | `(0.80, 0.25)` | `-0.000045` | `-0.000115` | `+0.000101` | `-0.000023` |
| 64 | `(0.80, 0.25)` | `-0.000067` | `-0.000161` | `+0.000140` | `-0.000018` |
| 128 | `(0.05, 0.50)` | `+0.002686` | `-0.008457` | `+0.008792` | `-0.000388` |
| 256 | `(0.05, 0.50)` | `+0.009450` | `-0.010843` | `+0.011216` | `-0.000485` |

Deltas are `Pontifex Torus residual - same paired Procrustes coarse map`; therefore positive coordinate/Spearman and negative RMSE are improvements.

The capacity control matters. At K=16, Torus beats the shuffled-residual control by `+0.002188` in B-coordinate cosine and `-0.010860` in pair-RMSE. At K=128 those contrasts are `+0.005547` and `-0.008720`; at K=256 they grow to `+0.015632` and `-0.010996`. Thus the larger-K B-specific gains are not reproduced merely by adding a same-sized residual field whose anchor identities are destroyed.

The pattern is nevertheless **non-monotonic**. K=32 and K=64 fail the protocol's direct-coordinate sign criterion and the residual is almost inert. K=8 technically has the required positive direct-coordinate sign, but the magnitude (`2.2e-5`) is too small to carry a strong mechanistic claim by itself. The clearest point estimates are K=16, K=128 and K=256.

At K=256, for example, paired Procrustes has B-coordinate cosine `0.618052`, pair-RMSE `0.114533` and B-pair Spearman `0.915436`; Torus moves these to `0.627502`, `0.103690` and `0.926652`. The shuffled-residual control remains at `0.611870`, `0.114687` and `0.915149`.

Ridge is an instructive counterexample to collapsing the endpoints: at K=256 it obtains higher sentencewise B-coordinate cosine (`0.686039`) than Torus, but much worse pair-RMSE (`0.155624`) and lower task Pearson (`0.805787`). B-coordinate alignment alone is therefore not sufficient evidence for useful geometry transport.

## Evidence

The successful run supports the following narrow statements.

1. Under the same K unlabeled SICK-train correspondence budget, a residual selected entirely inside `D_student` can improve B-specific pair geometry over the same paired Procrustes coarse map, with clear point-estimate gains at K=16, 128 and 256.
2. At K=128 and K=256, the correctly paired residual also beats a shuffled-residual capacity control on direct B-coordinate alignment and pair-RMSE; anchor identity therefore carries useful B-specific information beyond merely adding residual capacity.
3. The effect is not monotonic in K: K=32 and K=64 are essentially null and slightly negative on direct coordinate cosine.
4. The official primary SICK Pearson endpoint does **not** show a reliable advantage. The largest Torus-vs-Procrustes Pearson gain is `+0.001105` at K=16; at K=128 and K=256 Pearson is slightly worse. This result is mechanistic evidence about B-specific geometry, not evidence of downstream task superiority.
5. This is one benchmark, one model pair and one predeclared anchor seed. No inferential p-value or model-pair-general claim follows from these deterministic point estimates.

## Hypothesis — not established by this run

A plausible interpretation is that the coarse Procrustes map captures the approximately shared/isometric part of A↔B structure while the local residual can recover some non-isometric, B-specific deformation once anchor support is informative enough. The recovery at K=128/256 is consistent with that picture, but the null K=32/64 regime means the run does not establish a smooth sample-complexity law, a toroidal mechanism, or a generally superior transport architecture.

It is also only a hypothesis that the K=32/64 trough reflects neighborhood support or the selector entering a low-amplitude `(0.8,0.25)` regime. Because those test outcomes are now known, changing the grid or selector to rescue them would be post-hoc. Any such variant must be a separately predeclared follow-up, preferably on a fresh benchmark or model pair.

## Bottom line

The stricter experiment survives its most important anti-leakage correction and yields a useful mixed result: **B-specific geometry transfer is detectable and beats the shuffled residual at larger K, while primary downstream Pearson does not improve and the budget curve is not monotonic.** That is enough to keep the coarse-map-plus-residual hypothesis alive, but not enough to claim task superiority or a general Pontifex law.
