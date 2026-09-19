---
type: "Findings Record"
title: "Pontifex AG News single-item transport findings"
description: "On canonical AG News classification, all A→B transports remain below A-only through K=1024; Ridge is the strongest high-budget transport and Pontifex does not show a practical or sample-efficiency advantage."
timestamp: 2026-09-19T15:30:00-04:00
tags: [pontifex, ag-news, classification, cross-model-transfer, negative-result, leakage-audit]
---

# Pontifex AG News single-item transport findings

## Status

**Completed real external fixed-label-budget benchmark.** Protocol: `PROTOCOL-AGNEWS-CLASSIFICATION-2026-09-19.md`.

Run: <https://github.com/franklinbaldo/papers/actions/runs/35463333085>

Artifact: <https://github.com/franklinbaldo/papers/actions/runs/35463333085/artifacts/10590518684>

Primary metric: canonical AG News test **accuracy**; macro-F1 secondary.

## Provenance and leakage audit

**PASS.** Dataset `fancyzhx/ag_news` was resolved to revision `eb185aade064a813bc0b7f42de02595523103ca4`. A is `sentence-transformers/all-MiniLM-L6-v2` at `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`; B is `BAAI/bge-small-en-v1.5` at `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`.

The frozen information partition used 3,276 unlabeled transport-student rows, 820 unlabeled transport-validation rows, 12,000 labeled head-train rows, 3,000 labeled head-validation rows, and the full canonical 7,600-row test split. Task labels used for transport fit or selection: **0**. Test labels were opened only after predictions were frozen; B test coordinates were not used for transport selection. A↔B pretraining overlap is recorded as `pretraining_overlap_possible`; benchmark/pretraining overlap is `unknown` and is not classified as evaluation leakage.

Manifest hashes:

- transport student IDs: `44c81781f1d6de2f947d32254d09f829d24e21a061995e86d27bc12bf4529973`;
- transport validation IDs: `d2da447e48d96b135c3f9ffc3a02140e899a464048d70208f058f50c8182e60b`;
- head train IDs: `926c189ca4f56e6dbf8fe7e244b42e786bdfc5037c0946bdbd5d62d846c06fe8`;
- head validation IDs: `e1f12be37ad7d52d4c227402ba676e134812fa770a35c4533d88b991166e4b1b`;
- test IDs: `fe0d6cfcf0295511b8774dcfaa9203d6a17290aa659e87b743f466a2c2e4319f`.

## Reference systems

| System | Accuracy | Macro-F1 |
|---|---:|---:|
| A-only MiniLM | **0.889342** | 0.889148 |
| B-oracle BGE-small | **0.898816** | 0.898642 |

The native B-over-A gap is `+0.009474` accuracy. Frozen quality targets were `0.894079` for 50% of that gap and `0.897868` for 90%.

## Budget-matched results

All methods below receive the same first K unlabeled A↔B correspondences and select any transport hyperparameters only on `D_transport_val` coordinate loss.

| K | Procrustes | RankProc | Ridge | PLS | Pontifex | RankPontifex | Shuffled |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 16 | 0.563421 | 0.667632 | 0.525921 | 0.563684 | 0.561842 | 0.641184 | 0.193158 |
| 32 | 0.760658 | 0.810658 | 0.757368 | 0.757237 | 0.759868 | 0.798816 | 0.126184 |
| 64 | 0.816184 | 0.837500 | 0.830921 | 0.825658 | 0.815789 | 0.834474 | 0.206316 |
| 128 | 0.847500 | 0.854342 | **0.855132** | 0.850658 | 0.847368 | 0.853289 | 0.264211 |
| 256 | 0.856579 | 0.858421 | **0.863816** | 0.860000 | 0.856842 | 0.858816 | 0.247105 |
| 512 | 0.868026 | 0.868158 | **0.871447** | 0.865132 | 0.868553 | 0.868684 | 0.211053 |
| 1024 | 0.872895 | 0.873158 | **0.873684** | 0.865132 | 0.868158 | 0.868026 | 0.227763 |

CCA, RFF+Ridge and the capacity-matched MLP were also run at every K and do not alter the conclusion; their full scores and costs remain in the artifact.

## Quality-matched and efficiency frontier

No transport reaches either frozen quality target at any tested K. Therefore every `min_k_50pct` and `min_k_90pct` entry is null.

The practical frontier is dominated by **A-only**, which achieves 0.889342 accuracy with zero incremental A↔B correspondence supervision. Among transport methods, Ridge is strongest from K=128 through K=1024. At K=1024 Ridge reaches 0.873684 with about 147,840 fitted floats and ~0.0168 s for full-test mapping+prediction on the runner; Pontifex reaches 0.868158 with about 934,656 fitted floats and ~0.128 s. Pontifex selects faster in this implementation, but that does not compensate for worse task quality, larger fitted state, and slower inference.

Because every transported score remains below A-only, `fraction_of_B_utility_recovered` is negative throughout the tested frontier. At K=1024 it is approximately `-1.653` for Ridge, `-2.236` for Pontifex, and `-2.250` for RankPontifex. The small native B−A gap makes the normalized ratio numerically large in magnitude; raw accuracy is the primary interpretation.

## Geometry diagnostic

At K=1024, Ridge also has better held-out B-coordinate recovery than Pontifex: mean cosine `0.840724` versus `0.760508` for Pontifex and `0.760712` for RankPontifex. Neighbor-overlap@10 is `0.488049` for Ridge, `0.479512` for Pontifex and `0.478902` for RankPontifex. Geometry recovery remains secondary to the downstream result.

## Evidence for and against the operational hypothesis

Correct correspondences clearly carry real information: the shuffled Pontifex control collapses to roughly 0.13–0.26 accuracy across K, while correctly paired maps improve strongly with K. The prospective rank-constrained controls also validate the earlier nullspace concern: at low K, RankProcrustes and RankPontifex materially outperform their full-map counterparts.

However, this benchmark is **evidence against a practical Pontifex advantage for MiniLM→BGE-small on AG News**. Pontifex never exceeds A-only, never reaches a frozen B-gap target, and is overtaken by the simpler Ridge baseline once K is moderately large. The local-residual mechanism therefore does not convert correspondence information into superior downstream utility here.

This is not a claim that cross-space semantic transport is impossible. It is a falsification of the stronger claim that this Pontifex residual form already provides low-budget utility recovery on this encoder/task pair.

## Next highest-value action

Replicate the same MiniLM→BGE-small transport question on a **separately frozen external semantic task without choosing the pair after seeing its test set**. The highest-value next step is a recognized fine-grained classification benchmark such as Banking77, using the same transport family and the same anti-leakage/fairness rules, because it tests whether the negative AG News result is task-specific while avoiding two-tower gauge confounds and encoder-pair shopping. The new task must remain a separate prospective benchmark and must not retroactively alter the AG News success criterion.
