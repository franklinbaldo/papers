---
type: "Findings Record"
title: "Pontifex BEIR/SciFact low-budget transport findings"
description: "Untouched BEIR/SciFact retrieval shows partial B-utility recovery only at larger correspondence budgets, with no quality-target win yet and no low-budget dominance over A-only."
timestamp: 2026-09-19T11:08:00-04:00
tags: [pontifex, scifact, beir, retrieval, transport, benchmark, leakage-audit]
---

# Pontifex BEIR/SciFact low-budget transport findings

## Status

**Completed real external benchmark result.** Protocol: `PROTOCOL-SCIFACT-TRANSPORT-2026-09-19.md`.

Run: <https://github.com/franklinbaldo/papers/actions/runs/35449589115>

Artifact: <https://github.com/franklinbaldo/papers/actions/runs/35449589115/artifacts/10586334884>

The run used the canonical BEIR/SciFact test qrels for final scoring only. Transport fitting and hyperparameter selection used unlabeled A/B representation pairs from filtered SciFact train queries.

## Leakage audit

**PASS.** The canonical archive MD5 matched. Two train queries with exact text overlap against test queries were excluded before splitting. The resulting pools were 645 student queries, 162 validation queries, and 300 official test queries. Neither train nor test qrels entered transport fit or selection; task-label budget was zero. A/B pretraining overlap remains `pretraining_overlap_possible`; overlap of either encoder's pretraining corpus with SciFact remains `unknown` and is not treated as evaluation leakage.

Resolved spaces:

- A: `sentence-transformers/all-MiniLM-L6-v2` @ `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`;
- B: `sentence-transformers/all-mpnet-base-v2` @ `e8c3b32edf5434bc2275fc9bab85f82640a19130`.

## Oracle context

| System | nDCG@10 | MRR@10 | Recall@100 | MAP@100 |
|---|---:|---:|---:|---:|
| A-only MiniLM | 0.645082 | 0.604725 | 0.925000 | 0.603074 |
| B-oracle MPNet | 0.655697 | 0.617737 | 0.941667 | 0.615954 |

The available B-over-A gap is only `+0.010615` nDCG@10, so fraction-of-B-utility values are sensitive to small absolute changes and must be read together with raw task score.

## Budget-matched result

Every learned transport received the same K paired unlabeled train-query representations.

| K | Procrustes | Pontifex residual | shuffled | Ridge | MLP-64 | Pontifex fraction of B utility recovered |
|---:|---:|---:|---:|---:|---:|---:|
| 16 | 0.642405 | 0.639385 | 0.621971 | 0.237239 | 0.341572 | -0.537 |
| 32 | 0.637463 | 0.635255 | 0.638409 | 0.389451 | 0.326547 | -0.926 |
| 64 | 0.643195 | 0.644136 | 0.632450 | 0.422115 | 0.440632 | -0.089 |
| 128 | 0.644168 | 0.645327 | 0.630072 | 0.492381 | 0.400965 | +0.023 |
| 256 | **0.646420** | 0.645311 | 0.635865 | 0.547407 | 0.450015 | +0.022 |
| 512 | 0.646066 | **0.649954** | 0.631458 | 0.572826 | 0.447325 | **+0.459** |

There is no legitimate low-budget dominance claim. At K=16 and K=32 the residual transport is worse than both A-only and the corresponding Procrustes map. At K=64 and K=128 its incremental gain over Procrustes is small. K=256 favors Procrustes. The clearest positive point estimate appears only at K=512, where Pontifex beats the same Procrustes map by `+0.003888` nDCG@10 and recovers about **45.9%** of the B-over-A nDCG gap.

K=512 is not a tiny fraction of the available student pool: it uses 512 of 645 eligible student correspondences. It is therefore evidence for partial transport at a larger supervision budget, not evidence that a handful of correspondences suffices.

## Geometry versus utility

At K=512, Pontifex improves B-coordinate reconstruction over the same Procrustes map:

- test-query mean cosine to B: `0.663928 -> 0.717361`, delta `+0.053433`;
- corpus-document mean cosine to B: `0.591645 -> 0.604102`, delta `+0.012456`.

The downstream nDCG improvement is much smaller. This reinforces the rule that geometry recovery is diagnostic only and cannot substitute for official retrieval utility.

## Efficiency accounting at K=512

- shared query-text bytes: `45,742`;
- paired float32 A/B supervision bytes: `2,359,296`;
- Procrustes fitted floats: `296,064`;
- Pontifex residual increment: `393,216` stored residual floats plus two selected scalars;
- Procrustes fit: about `0.062 s`; map test queries + corpus: `0.022 s`;
- Pontifex coarse + selection fit: about `0.085 s`; map test queries + corpus: `0.080 s`;
- Ridge fit + validation selection: about `0.543 s`;
- MLP-64 fit: about `2.401 s`.

These timings are runner-local measurements, not hardware-normalized FLOP claims.

## Quality-matched frontier

The predeclared 50%-of-gap target was `0.650389` nDCG@10 and the 90%-of-gap target was `0.654635`. No tested transport method reached either target for `K <= 512`.

Pontifex at K=512 reaches `0.649954`, approximately `0.000436` below the 50%-gap target. The correct quality-matched conclusion is therefore **no winner within the tested budget range**, not an interpolated success.

## Evidence for and against the hypothesis

### For

- Correct A/B correspondence clearly matters relative to the shuffled control at moderate and large K.
- At K=512, the local residual improves both held-out B-coordinate recovery and official nDCG@10 over the same Procrustes coarse map.
- It achieves that without task labels in transport fitting or selection.

### Against / limiting

- The effect is not present as a stable monotone low-K frontier.
- A-only remains stronger than transported systems through much of the curve.
- No method reaches the predeclared 50% or 90% B-utility targets.
- The strongest point uses most of the available student correspondences, weakening the present evidence for the central small-K thesis.
- Ridge can reconstruct B coordinates increasingly well while remaining poor at retrieval, demonstrating that coordinate closeness alone is not enough.

## Next highest-value discriminants

1. Add CCA/PLS/RFF under the identical frozen split and information budget; the prospective protocol explicitly reserved these baselines.
2. Add a reproducible lexical/reference retrieval system separately; do not use it as a transport baseline because it receives different information.
3. Replicate transport on a retrieval pair where B has a materially larger ceiling over A. The current `+0.0106` B-over-A gap makes utility-recovery ratios fragile and limits the room for a practically important win.
4. Preserve the current SciFact test result as frozen evidence; new model classes or encoder pairs constitute new prospective comparisons rather than retroactive tuning of this run.
