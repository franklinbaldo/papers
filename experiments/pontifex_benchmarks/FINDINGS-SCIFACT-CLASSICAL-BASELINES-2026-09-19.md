---
type: "Findings Record"
title: "Pontifex SciFact classical transport baseline findings"
description: "CCA, PLS and RFF+Ridge fail to preserve SciFact retrieval utility under the same unlabeled A↔B correspondence budgets; Pontifex remains the strongest tested A→B transport at K=512 but still does not beat A-only or reach the frozen 50%-of-B-gap target."
timestamp: 2026-09-19T12:57:00-04:00
tags: [pontifex, scifact, beir, retrieval, baselines, cca, pls, rff, leakage-audit]
---

# Pontifex SciFact classical transport baseline findings

## Status

**Completed real external benchmark baseline follow-up.** Protocol: `PROTOCOL-SCIFACT-CLASSICAL-BASELINES-2026-09-19.md`.

Run: <https://github.com/franklinbaldo/papers/actions/runs/35455793508>

Artifact: <https://github.com/franklinbaldo/papers/actions/runs/35455793508/artifacts/10588397204>

Primary metric: official BEIR/SciFact **nDCG@10**.

## Leakage audit

**PASS.** The runner reproduced the frozen SciFact manifests from the parent benchmark:

- `D_student`: `bd5775940da2cb20d0ec5ee5ec4c9e35d871f82f12c0ff87e1955e38bd69ccf5`;
- `D_val`: `7a699f93186bd3b8c6042c8941b045ed8197438fceb396b0d7178af34e9c349c`;
- test: `c307ee1faa37715704375e5c59a071b0c579b3114bedcbf263d43111a2f15ebf`;
- corpus: `bcb266241b6c749fe993de0353d1ce95cc3b9fbd47b86d356ba54acab09ccfd4`.

No qrel or task label was used for transport fitting or hyperparameter selection. CCA component count, PLS component count, and RFF gamma/width/Ridge alpha were selected only by B-coordinate loss on `D_val`; all models were frozen before test scoring. Pretraining overlap A↔B remains `pretraining_overlap_possible`; benchmark overlap remains `unknown`, neither of which is treated as evaluation leakage.

Spaces are unchanged:

- A: `sentence-transformers/all-MiniLM-L6-v2` @ `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`;
- B: `sentence-transformers/all-mpnet-base-v2` @ `e8c3b32edf5434bc2275fc9bab85f82640a19130`.

## Oracle context

| System | nDCG@10 | MRR@10 | Recall@100 | MAP@100 |
|---|---:|---:|---:|---:|
| A-only MiniLM | 0.645082 | 0.604725 | 0.925000 | 0.603074 |
| B-oracle MPNet | 0.655697 | 0.617737 | 0.941667 | 0.615954 |

The frozen 50%-of-B-gap target is `0.650389` nDCG@10; the 90% target is `0.654635`.

## Budget-matched result

All methods below receive exactly the same first K unlabeled A↔B train correspondences used by the parent transport experiment.

| K | CCA | PLS | RFF+Ridge | frozen Pontifex residual | A-only |
|---:|---:|---:|---:|---:|---:|
| 16 | 0.080943 | 0.119456 | 0.174091 | 0.639385 | 0.645082 |
| 32 | 0.208512 | 0.246836 | 0.312167 | 0.635255 | 0.645082 |
| 64 | 0.201664 | 0.225340 | 0.416064 | 0.644136 | 0.645082 |
| 128 | 0.092774 | 0.240472 | 0.405175 | 0.645327 | 0.645082 |
| 256 | 0.046659 | 0.294226 | 0.436630 | 0.645311 | 0.645082 |
| 512 | 0.000000 | 0.307058 | **0.496555** | **0.649954** | 0.645082 |

The strongest classical family is RFF+Ridge, but even at K=512 it remains `-0.148527` nDCG@10 below A-only and `-0.153399` below Pontifex. CCA and PLS are substantially worse. Their negative `fraction_of_B_utility_recovered` values are therefore not a useful efficiency claim; raw task scores are the meaningful quantity here.

## Quality-matched frontier

No CCA, PLS, or RFF+Ridge configuration reaches either frozen quality target at any tested K. Pontifex also remains just below the 50%-gap target at K=512 (`0.649954` versus `0.650389`). Therefore:

- **same budget:** Pontifex is decisively stronger than these three classical transport families across the useful part of the frontier;
- **same target quality:** none of the tested transports reaches the predeclared 50% or 90% B-utility target within K≤512;
- **low-budget dominance:** still **not demonstrated**, because A-only remains the stronger practical system at small K;
- **B utility recovered:** the best frozen Pontifex point remains about **45.9%** at K=512.

## Compute / capacity context

At K=512:

- CCA and PLS store about `295,680` fitted floats each;
- RFF+Ridge stores `98,560` random-feature floats plus `197,376` fitted Ridge floats;
- RFF+Ridge fit+validation selection took about `1.33 s`, mapping test queries+corpus about `0.028 s` and retrieval about `0.018 s` on the runner;
- CCA selection took about `10.30 s`; PLS about `0.32 s`.

These methods are therefore not losing merely because Pontifex received a larger information budget. They received the same K paired observations and comparable or cheaper fitted-state budgets, but their transformed spaces fail to retain downstream retrieval geometry.

## Evidence for Pontifex

This follow-up eliminates an important easy explanation: the K=512 Pontifex point is **not** reproduced by standard CCA, PLS, or an RBF random-feature map with Ridge when all are selected without task labels under the same correspondence budget. Pontifex's local residual structure is therefore doing something more retrieval-preserving than these generic coordinate-regression families in this frozen encoder pair.

## Evidence against / boundary

The stronger conclusion remains limited:

- Pontifex still does not beat the unchanged A-only system on SciFact by a practically large margin; its K=512 gain over A-only is only `+0.004872` nDCG@10;
- K=512 consumes most of the 645 eligible student correspondences, so the central *small correspondence* thesis is still weak on this benchmark;
- B-over-A headroom is only `+0.010615`, making fraction-of-B-utility ratios fragile;
- mechanism controls show that shared-warp coherence explains a substantial part of the effect, so classical-baseline failure does not by itself prove semantically specific transport.

## Next highest-value action

Move to the already frozen MS MARCO Passage plan (#686), where ANCE and TCT-ColBERT-v2 HN+ provide a larger recognized retrieval setting and a more meaningful native quality gap. First validate an explicit shared PID/candidate manifest and dual-index feature extraction without dev-label access; then run a clearly marked pilot before unsealing the full official `msmarco-passage-dev-subset` result.
