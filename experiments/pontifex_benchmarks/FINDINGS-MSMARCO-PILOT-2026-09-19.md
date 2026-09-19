---
type: "Experiment Report"
title: "Pontifex MS MARCO transport pilot findings"
description: "Completed frozen 256-query ANCE→TCT-ColBERT-v2 HN+ pilot: leakage audit passed, but Pontifex transport did not recover the native A-space retrieval baseline."
timestamp: 2026-09-19T14:27:00-04:00
tags: [pontifex, msmarco, retrieval, transport, negative-result, leakage-audit]
---

# Pontifex MS MARCO transport pilot findings

Run: `35457043627`  
Protocol: `PROTOCOL-MSMARCO-PILOT-2026-09-19.md`

## Completed result

The frozen 256-query pilot completed successfully with the leakage audit marked `PASS`. Dev qrels were not used for candidate generation, fitting, or hyperparameter selection; candidate PIDs were excluded from document transport fitting; and dev qrels were loaded only after rankings were frozen.

Reference MRR@10 on the common frozen BM25 candidate pool:

| condition | MRR@10 |
| --- | ---: |
| BM25 candidate order | 0.205872 |
| A-only ANCE | 0.346215 |
| B-oracle TCT-ColBERT-v2 HN+ | 0.373555 |

The native B-space oracle therefore improves over A-only by `+0.027341` MRR@10 on this pilot.

At the largest paired budget, `K=512`:

| mapping | MRR@10 |
| --- | ---: |
| Pontifex | 0.222483 |
| Procrustes | 0.222836 |
| Ridge | 0.094517 |
| shuffled Pontifex | 0.013194 |

Pontifex improves strongly over its shuffled-correspondence control, so the paired correspondence contains usable structure. But it remains `-0.123732` below the native A-only ANCE reranker and essentially tied with plain Procrustes (`-0.000353`). It therefore recovers **none of the positive A→B oracle retrieval gap** in this pilot; the reported fraction-of-B-utility-recovered is negative.

The same qualitative failure holds across the frozen K ladder. Pontifex MRR@10 is `0.029506, 0.008760, 0.041178, 0.078547, 0.138714, 0.222483` for `K={16,32,64,128,256,512}`. Larger K helps substantially, but the K=512 score is still far below A-only.

## Evidence / hypothesis boundary

**Evidence:** the end-to-end external-task plumbing works under the frozen 256-query protocol; the leakage audit passes; true A↔B correspondence is much better than shuffled correspondence; and the current Pontifex residual-transport formulation does **not** preserve enough retrieval geometry to match the native A-space baseline on this ANCE→TCT pilot.

**Not evidence:** this does not show that cross-space transport is impossible, that Pontifex fails on all representation pairs, or that the full MS MARCO dev benchmark would have the same numerical scores. Both representation families are MS-MARCO-trained, the evaluation uses a 256-query pilot and a frozen BM25 candidate pool, and the full baseline matrix has not yet been run.

The result is direct falsification pressure against any claim of universal or plug-and-play transport superiority. It also suggests that future work should diagnose what retrieval-relevant geometry is lost between coordinate reconstruction and ranking before scaling this exact formulation to the full 6,980-query dev set.

## Reproducibility

- run: `https://github.com/franklinbaldo/papers/actions/runs/35457043627`
- PR: `https://github.com/franklinbaldo/papers/pull/485`
