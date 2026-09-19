---
type: "Interpretability Paper"
title: "Pontifex RED-1: Empirical Mechanism Boundary on SciFact"
description: "Living empirical companion to Pontifex, separating completed SciFact transport evidence from mechanism hypotheses and prospective stronger null tests."
tags: [pontifex, red-1, scifact, transport, matched-null, empirical]
timestamp: 2026-09-19T13:20:00-04:00
---

# Pontifex RED-1: Empirical Mechanism Boundary on SciFact

**Franklin Baldo**  
Independent Researcher

> **Living empirical companion paper.** This document records completed RED-1 evidence and explicitly separates it from follow-up hypotheses. A result enters the evidence column only after its frozen run completes. Follow-ups motivated by earlier results are labeled adaptive/prospective rather than independent confirmations.

## 1. Information boundary

The current SciFact mechanism programme uses four non-interchangeable roles. `D_assembly` contains canonical text/split membership and frozen encoder identities, without relevance grades. `D_student` is a deterministic 80% of exact-test-overlap-filtered train queries and supplies unlabeled paired representation coordinates. `D_val` is the remaining 20% and is used only for coordinate-space hyperparameter selection. `D_test` contains official SciFact test relevance grades and is opened only after the tested map and every null object are frozen.

For K=512 mechanism diagnostics, no B/MPNet coordinates for test queries or corpus documents are encoded, and zero task labels/qrels are used for fitting or selection. These experiments test a transport mechanism; they do **not** demonstrate `D_assembly -> D_student` generalization.

## 2. Completed evidence

### 2.1 Global-permutation K=512

Run `35451426518` gave TRUE `0.649954`, coupled global-null mean `0.641013`, and independent global-null mean `0.620021` nDCG@10. Exact residual identity did not meet the predeclared rule: TRUE-minus-coupled was `+0.008940`, finite-bank `p=0.078125`, paired-query 95% CI `[-0.003652,+0.021549]`. Shared-warp coherence did: coupled-minus-independent was `+0.020992`, 95% CI `[+0.009079,+0.033756]`.

Evidence: a common two-sided deformation preserves more held-out retrieval structure than independently scrambled query/document deformations under this frozen benchmark. Not evidence: necessity of exact residual identity.

### 2.2 Residual-norm-matched K=512

The stronger completed run `35455793661` constrained every null permutation to remain within eight equal-count residual-L2 strata. It observed:

| condition | nDCG@10 |
| --- | ---: |
| TRUE | 0.649954 |
| norm-matched coupled mean | 0.640712 |
| norm-matched independent mean | 0.619617 |

TRUE-minus-coupled was `+0.009241`. The finite-bank upper-tail test was positive (`p=0.015625`), but the paired-query bootstrap 95% interval remained `[-0.003507,+0.021617]`, so the **predeclared two-part semantic-specificity criterion still fails**. The two statistical views are therefore reported together rather than selecting the favorable one after the fact.

Shared-warp coherence replicated under the stronger nuisance match: coupled-minus-independent was `+0.021095`, with paired-query 95% CI `[+0.008416,+0.034615]`. This remains the cleanest positive mechanism result currently supported.

### 2.3 Residual-norm + balanced-group A-space null

Run `35457676312` completed the next adaptive follow-up. TRUE remained `0.649954`; the balanced-group coupled mean was `0.640717` and the independent mean `0.620341`. TRUE-minus-coupled was `+0.009236`, with finite-bank `p=0.03125` but paired-query 95% CI `[-0.003390,+0.022029]`. The predeclared exact-identity criterion therefore **failed again**. Shared-warp coherence remained positive at `+0.020376`, with paired-query 95% CI `[+0.009422,+0.032373]`.

The run also falsified a methodological assumption in its own design: the deterministic balanced groups were not tightly local in normalized A-space. Query-side donor cosine distance averaged `0.78787` with p95 `0.99686`; document-side distance averaged `0.78952` with the same p95. Accordingly, this run is evidence for robustness to a **coarse balanced-group nuisance control**, not evidence that the result survives a genuinely local-A null. The locality diagnostic is treated as a negative result that motivates, but does not itself validate, the next experiment.

### 2.4 Classical coordinate-mapping baselines

Run `35455793508` completed a label-free, frozen-manifest comparison against CCA, PLS and RFF+ridge. A-only MiniLM scored `0.645082` and the B/MPNet oracle `0.655697` nDCG@10. At K=512, the best of the three classical maps was RFF+ridge at `0.496555`; PLS scored `0.307058` and CCA `0.000000`. The Pontifex TRUE K=512 map (`0.649954`) therefore exceeded the best tested classical mapping by `+0.153399` nDCG@10, sat `+0.004872` above A-only, and remained `-0.005743` below the B oracle.

Across K={16,32,64,128,256,512}, none of those three classical families reached the precomputed A-to-B midpoint (`0.650389`) or the 90%-to-B target (`0.654635`). This is useful comparative evidence **only for these frozen methods, budgets and SciFact setup**. It does not establish universal transport superiority.

### 2.5 MS MARCO pilot: negative transfer result

Run `35457043627` completed the separately frozen 256-query ANCE→TCT-ColBERT-v2 HN+ MS MARCO pilot with leakage audit `PASS`: dev qrels were excluded from candidate generation, fitting and hyperparameter selection, candidate documents were excluded from document-side transport fitting, and qrels were loaded only after rankings were frozen.

On the common BM25 candidate pool, A-only ANCE scored `0.346215` MRR@10 and B-oracle TCT scored `0.373555`. At K=512, Pontifex scored only `0.222483`, essentially tied with Procrustes (`0.222836`) and far below A-only, while shuffled-correspondence Pontifex scored `0.013194`. Thus the paired correspondence carries real structure relative to shuffle, but the present transport formulation does **not** preserve enough retrieval geometry to recover even the native A-space baseline on this pilot.

This is a genuine negative result against plug-and-play or universal transport claims, not evidence that transport is impossible. Both encoders are MS-MARCO-family models, the evaluation is a 256-query pilot over a frozen candidate pool, and it is not an official full-dev leaderboard result. Detailed record: `experiments/pontifex_benchmarks/FINDINGS-MSMARCO-PILOT-2026-09-19.md`.

### 2.6 Feasibility-frozen residual-norm + A-KNN null

The hard-locality protocol first attempted donor rank `<=16` and failed before opening any `D_test` relevance grades (`35460716096`) because at least one residual-norm stratum admitted no perfect derangement. The frozen feasibility ladder `[16,20,24,32,48,63]` therefore selected the smallest combinatorially feasible cap from `D_student` geometry only. Runs at 16, 20 and 24 were infeasible; rank 32 was the first feasible cap. Only after the graph and both 63-permutation null banks were frozen and hashed were the official `D_test` qrels read.

Run `35461028519` then observed TRUE `0.649954`, norm+KNN coupled mean `0.640060`, and independent mean `0.616211` nDCG@10. TRUE-minus-coupled was `+0.009894`, but exact residual identity again failed the predeclared two-part criterion: finite-bank `p=0.09375` and paired-query 95% CI `[-0.002436,+0.022668]`. Shared-warp coherence remained positive: coupled-minus-independent was `+0.023849`, with paired-query 95% CI `[+0.011687,+0.036146]`.

This is therefore a fourth completed failure of the exact-identity claim under the frozen decision rule, alongside another positive replication of two-sided shared-warp coherence. However, the same run reported mean donor A-cosine distance `0.80004` (p95 `0.93161`) despite the rank-32 cap, so donor rank alone still does not establish tight geometric locality.

### 2.7 D_student-only locality calibration of the KNN null

To quantify that concern without reopening or reusing `D_test` grades, run `35463689486` calibrated the frozen rank-32 bank entirely on `D_student` geometry. Within the same residual-norm strata, the expected random-donor mean A-cosine distance is `0.87712`; the theoretical minimum-cost perfect derangement reaches `0.53900`, while the unconstrained per-anchor nearest-neighbour floor is `0.51386`. The actual frozen KNN bank averages `0.80004` (median `0.81079`, p95 `0.93161`).

Define a descriptive locality-capture scale with 0 equal to random-within-stratum mean locality and 1 equal to the minimum-cost feasible derangement. The frozen KNN bank scores only `0.22797`. Thus the rank-32 bank is measurably more local than random, but captures only about 23% of the available random-to-optimal locality improvement. This is a **methodological negative result** about the strength of the nuisance control, not a held-out retrieval result and not evidence for semantic specificity.

## 3. Current evidence / hypothesis boundary

Supported: under the frozen SciFact K=512 setup, shared query/document warp coherence is robust to global, residual-magnitude-matched, coarse balanced-group, and feasibility-frozen KNN nulls; and the tested Pontifex map substantially outperforms CCA, PLS and RFF+ridge coordinate mappings at the same K=512 correspondence budget.

Not supported: the stronger claim that exact residual-to-anchor identity is necessary. It has now failed the same predeclared two-part criterion under **four** completed null families. Also not supported: robustness to genuinely tight source-space locality. The completed KNN test used the tightest *rank cap* that admitted perfect derangements, but the D_student-only calibration shows that its actual donor distances remain much closer to random-within-stratum than to the minimum-cost feasible derangement.

The MS MARCO pilot adds a separate negative boundary: current Pontifex transport does not generalize as a plug-and-play retrieval upgrade across the tested ANCE→TCT representation pair. That failure coexists with the positive SciFact shared-warp result; neither should be generalized beyond its frozen design.

Still hypotheses or outside these diagnostics: causal semantic locality, an intrinsic or physical torus, universal transport superiority, native-B superiority, low-budget superiority, broad cross-dataset generalization, and Assembly-to-student generalization.

## 4. Prospective stronger discrimination: distance-optimal local null

The locality calibration identifies a sharper next discriminant. Within each residual-norm stratum, the minimum-cost perfect derangement reaches mean A-cosine distance `0.53900`, compared with `0.80004` for the current KNN bank and `0.87712` for random donors. A future frozen test should therefore destroy exact residual identity while directly minimizing source-space donor distance, rather than using neighbour rank as a proxy.

This follow-up must be treated as adaptive/prospective. Its assignment object must be constructed from `D_student` only, with `D_val` restricted to coordinate-space selection as before, and frozen before any `D_test` relevance-grade read. Because a single deterministic optimum does not provide a valid 63-member permutation reference distribution by itself, a future inferential protocol must predeclare either a near-optimal assignment bank with an explicit locality tolerance or a paired-query-only decision rule before opening `D_test`. No result from that future test is claimed here.

A positive result would strengthen only the narrow claim that exact residual identity adds utility beyond residual magnitude and a genuinely distance-local source-space nuisance control. A negative result would further weaken exact-identity claims. Either outcome leaves broader torus, causality, and physical-topology hypotheses unproven.

## Reproducibility

- PR: `https://github.com/franklinbaldo/papers/pull/485`
- completed global K=512: `https://github.com/franklinbaldo/papers/actions/runs/35451426518`
- completed norm-matched K=512: `https://github.com/franklinbaldo/papers/actions/runs/35455793661`
- completed balanced-group norm+local K=512: `https://github.com/franklinbaldo/papers/actions/runs/35457676312`
- completed classical baselines: `https://github.com/franklinbaldo/papers/actions/runs/35455793508`
- completed MS MARCO pilot: `https://github.com/franklinbaldo/papers/actions/runs/35457043627`
- infeasible hard rank-16 locality attempt: `https://github.com/franklinbaldo/papers/actions/runs/35460716096`
- completed KNN feasibility-ladder test: `https://github.com/franklinbaldo/papers/actions/runs/35461028519`
- completed D_student-only locality calibration: `https://github.com/franklinbaldo/papers/actions/runs/35463689486`
- locality calibration script: `experiments/pontifex_benchmarks/scifact_knn_null_locality_calibration_k512.py`
- hard-locality protocol: `experiments/pontifex_benchmarks/PROTOCOL-SCIFACT-NORM-KNN-MATCHED-COUPLING-K512-2026-09-19.md`
