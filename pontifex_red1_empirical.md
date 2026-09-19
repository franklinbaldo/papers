---
type: "Interpretability Paper"
title: "Pontifex RED-1: Empirical Mechanism Boundary"
description: "Living empirical companion to Pontifex, separating completed transport/mechanism evidence from hypotheses across SciFact, MS MARCO, and the preregistered NFCorpus replication."
tags: [pontifex, red-1, scifact, nfcorpus, transport, matched-null, replication, empirical]
timestamp: 2026-09-19T16:25:00-04:00
---

# Pontifex RED-1: Empirical Mechanism Boundary

**Franklin Baldo**  
Independent Researcher

> **Living empirical companion paper.** This document records completed RED-1 evidence and explicitly separates it from follow-up hypotheses. A result enters the evidence column only after its frozen run completes. Adaptive follow-ups are labeled as such; independent replications require a protocol committed before the new held-out grades are opened.

## 1. Information boundary

The mechanism programme uses four non-interchangeable roles. `D_assembly` contains canonical text/split membership and frozen encoder identities, without relevance grades used for fitting or selection. `D_student` supplies unlabeled paired representation coordinates. `D_val` is used only for coordinate-space hyperparameter selection. `D_test` contains official held-out relevance grades and is opened only after the tested map and null objects are frozen.

For the SciFact K=512 diagnostics and the NFCorpus replication, no B/MPNet coordinates for test queries or corpus documents are encoded, and zero task labels/qrels are used for fitting or selection. These experiments test transport mechanisms; they do **not** demonstrate `D_assembly -> D_student` generalization.

## 2. Completed evidence

### 2.1 SciFact global-permutation K=512

Run `35451426518` gave TRUE `0.649954`, coupled global-null mean `0.641013`, and independent global-null mean `0.620021` nDCG@10. Exact residual identity did not meet the predeclared rule: TRUE-minus-coupled was `+0.008940`, finite-bank `p=0.078125`, paired-query 95% CI `[-0.003652,+0.021549]`. Shared-warp coherence did: coupled-minus-independent was `+0.020992`, 95% CI `[+0.009079,+0.033756]`.

Evidence: a common two-sided deformation preserves more held-out SciFact retrieval structure than independently scrambled query/document deformations under this frozen benchmark. Not evidence: necessity of exact residual identity.

### 2.2 SciFact residual-norm-matched K=512

Run `35455793661` constrained every null permutation to eight equal-count residual-L2 strata. TRUE was `0.649954`, norm-matched coupled mean `0.640712`, and independent mean `0.619617`. TRUE-minus-coupled was `+0.009241`; the finite-bank upper-tail test was positive (`p=0.015625`) but the paired-query 95% CI remained `[-0.003507,+0.021617]`, so the **predeclared two-part semantic-specificity criterion failed**.

Shared-warp coherence remained positive: coupled-minus-independent `+0.021095`, 95% CI `[+0.008416,+0.034615]`.

### 2.3 SciFact residual-norm + balanced-group A-space null

Run `35457676312` gave TRUE `0.649954`, coupled mean `0.640717`, and independent mean `0.620341`. TRUE-minus-coupled was `+0.009236`, finite-bank `p=0.03125`, but paired-query 95% CI `[-0.003390,+0.022029]`; exact identity therefore failed again. Shared-warp coherence was `+0.020376`, 95% CI `[+0.009422,+0.032373]`.

The same run falsified a methodological assumption: its deterministic groups were not tightly local in normalized A-space. Query donor cosine distance averaged `0.78787` with p95 `0.99686`; document distance averaged `0.78952` with the same p95. It is therefore evidence for a **coarse balanced-group nuisance control**, not for a genuinely local null.

### 2.4 SciFact classical coordinate-mapping baselines

Run `35455793508` compared frozen, label-free CCA, PLS and RFF+ridge mappings. A-only MiniLM scored `0.645082`, B-oracle MPNet `0.655697`, and at K=512 RFF+ridge `0.496555`, PLS `0.307058`, CCA `0.000000`, versus Pontifex TRUE `0.649954`. Pontifex exceeded the best of those tested classical mappings by `+0.153399` nDCG@10, sat `+0.004872` above A-only, and remained `-0.005743` below B oracle.

This is comparative evidence only for the frozen methods, budgets and SciFact setup. It is not universal transport superiority.

### 2.5 MS MARCO pilot: negative transfer result

Run `35457043627` completed a separately frozen 256-query ANCE -> TCT-ColBERT-v2 HN+ MS MARCO pilot with leakage audit `PASS`. On the common BM25 candidate pool, A-only scored `0.346215` MRR@10, B-oracle `0.373555`, Pontifex K=512 only `0.222483`, Procrustes `0.222836`, and shuffled-correspondence Pontifex `0.013194`.

The paired correspondence carries structure relative to shuffle, but the current transport formulation does **not** preserve enough retrieval geometry to recover the native A-space baseline. This is a real negative result against plug-and-play or universal transport claims, not evidence that transport is impossible.

### 2.6 SciFact feasibility-frozen residual-norm + A-KNN null

The first hard-locality attempt (`35460716096`) froze donor rank `<=16` and failed before opening `D_test` grades because at least one residual-norm stratum admitted no perfect derangement. A preregistered feasibility ladder `[16,20,24,32,48,63]` then selected rank 32 from `D_student` geometry only.

Run `35461028519` observed TRUE `0.649954`, norm+KNN coupled mean `0.640060`, and independent mean `0.616211`. TRUE-minus-coupled was `+0.009894`, with finite-bank `p=0.09375` and paired-query 95% CI `[-0.002436,+0.022668]`: exact identity failed again. Shared-warp coherence was positive at `+0.023849`, 95% CI `[+0.011687,+0.036146]`.

### 2.7 SciFact D_student-only locality calibration

Run `35463689486`, using `D_student` geometry only, found random-within-stratum expected donor distance `0.87712`, KNN-bank mean `0.80004`, minimum-cost perfect-derangement distance `0.53900`, and individual nearest-nonself floor `0.51386`. On a scale where 0 is random and 1 is the minimum-cost feasible derangement, the KNN bank captured only `0.22797` of available locality improvement.

This is a **methodological negative result** about the strength of that nuisance control, not held-out retrieval evidence.

### 2.8 SciFact residual-norm + minimum-cost A-space derangement

A separately frozen adaptive protocol then replaced donor-rank locality with the deterministic minimum-cost perfect derangement. It was constructed from `D_student` only; `D_val` stayed restricted to `tau`/`lambda`; `D_test` grades were loaded only after map, strata, assignment, manifests and mapped A-side ingredients were fixed. Because one deterministic optimum is not a permutation reference distribution, the protocol explicitly forbade a finite-bank p-value and preregistered a paired-query bootstrap decision rule.

Run `35463942235` observed TRUE `0.649954` versus MINCOST_COUPLED `0.640415`, delta `+0.009538`, with 95% CI `[-0.004726,+0.024025]`. The criterion therefore **failed to support exact residual identity even against the strongest deterministic source-local nuisance tested on SciFact**. This run had no independent-warp comparator and therefore adds no shared-warp evidence by itself.

### 2.9 NFCorpus independent-dataset replication: shared warp does not replicate

After the SciFact sequence, the higher-value test was moved off the reused SciFact held-out set. Commit `aa33ff96f18e363247977604e3491d281f00104d` froze an NFCorpus replication protocol and executable before the first NFCorpus `D_test` relevance-grade read. It retains the same pinned MiniLM -> MPNet encoder pair but changes the BEIR dataset, so this is an independent **dataset** replication, not an independent representation-pair replication.

The K=256 design preserved the four-way split contract. `D_student` created eight residual-norm strata and two separately seeded, disjoint 31-member local derangement banks; `D_val` selected only `tau=0.1` and `lambda=1.5`; official `D_test` grades were opened last. B coordinates for test queries and corpus documents were never encoded and the task-label budget for fit/selection remained zero.

The nuisance banks were considerably more local than required. Minimum-cost A-cosine donor distance was `0.652204` and random-within-stratum expectation `0.855995`. Query-bank mean distance was `0.652270`, document-bank mean `0.652275`, corresponding to mean locality capture `0.999673` and `0.999649`. Thus this test destroys exact identity while keeping replacement residuals extremely close to the strongest feasible regional match.

Run `35466980084` produced TRUE `0.318457`, LOCAL_COUPLED mean `0.314782`, and LOCAL_INDEPENDENT mean `0.314777` nDCG@10. The preregistered primary difference was only `+0.0000053`. Across 323 held-out queries, the 5,000-resample paired bootstrap gave 95% CI `[-0.000329,+0.000356]` and probability of positive mean `0.5056`. The preregistered criterion therefore **fails cleanly: the SciFact shared-warp advantage did not replicate on NFCorpus under this highly local nuisance family**.

The secondary TRUE-minus-LOCAL_COUPLED contrast was `+0.003674`, with 95% CI `[-0.001637,+0.009323]`; it also does not support exact residual identity under an interval-above-zero rule, but it was not the replication target.

This negative replication does not invalidate the four completed SciFact positives; it changes their scope. Shared-warp coherence is now evidence specific to the tested SciFact/null regimes, not a demonstrated cross-dataset property. Detailed record: `experiments/pontifex_benchmarks/FINDINGS-NFCORPUS-LOCAL-SHARED-WARP-REPLICATION-K256-2026-09-19.md`.

## 3. Current evidence / hypothesis boundary

**Supported within SciFact:** at K=512, shared query/document warp coherence survives four global-to-moderately-local null-bank families; the tested Pontifex map also substantially outperforms CCA, PLS and RFF+ridge at the same frozen K=512 correspondence budget.

**Not supported:** exact residual-to-anchor identity is necessary. It failed the predeclared decision rules across four SciFact null banks, the SciFact minimum-cost deterministic local derangement, and the secondary NFCorpus local contrast.

**Not replicated cross-dataset:** the SciFact shared-warp advantage failed the preregistered NFCorpus replication when residual replacements were constrained to near-minimum-cost local A-space derangements. Therefore the current evidence no longer supports describing shared-warp coherence as robust across datasets.

**Additional negative boundary:** the MS MARCO pilot shows current Pontifex transport is not a plug-and-play retrieval upgrade across the tested ANCE -> TCT pair.

Still hypotheses or outside these diagnostics: causal semantic locality, an intrinsic or physical torus, universal transport superiority, native-B superiority, low-budget superiority, broad cross-representation generalization, and `D_assembly -> D_student` generalization.

## 4. Next discriminant: coupling x locality, frozen prospectively

The NFCorpus result creates a sharper mechanistic question than simply trying another dataset. The SciFact positive coupled-versus-independent gaps were obtained with nulls whose replacement residuals were global, magnitude-matched, coarse-group, or only moderately local; the NFCorpus replication used banks with approximately `0.9997` locality capture and observed effectively zero coupled-versus-independent gap.

A plausible generated hypothesis is therefore that the shared-warp contrast is **scale-dependent**: coupling matters when the null displacement is large enough to change the regional field, but becomes irrelevant when both coupled and independent substitutions remain nearly inside the same local field. The current data do not establish that explanation because dataset and locality regime changed together.

The next discriminant should preregister a locality ladder on a fresh held-out dataset/representation setting and test a `coupling × locality` interaction, with the nuisance distances and bank construction frozen from `D_student` before any `D_test` grades are opened. A monotone collapse of the coupled-minus-independent gap as locality tightens would support a regional-field interpretation; absence of such an interaction would weaken it. This is a hypothesis and proposed experiment, not current evidence.

## Reproducibility

- PR: `https://github.com/franklinbaldo/papers/pull/485`
- SciFact global K=512: `https://github.com/franklinbaldo/papers/actions/runs/35451426518`
- SciFact norm-matched K=512: `https://github.com/franklinbaldo/papers/actions/runs/35455793661`
- SciFact balanced-group K=512: `https://github.com/franklinbaldo/papers/actions/runs/35457676312`
- SciFact classical baselines: `https://github.com/franklinbaldo/papers/actions/runs/35455793508`
- MS MARCO pilot: `https://github.com/franklinbaldo/papers/actions/runs/35457043627`
- SciFact KNN feasibility test: `https://github.com/franklinbaldo/papers/actions/runs/35461028519`
- SciFact locality calibration: `https://github.com/franklinbaldo/papers/actions/runs/35463689486`
- SciFact minimum-cost local derangement: `https://github.com/franklinbaldo/papers/actions/runs/35463942235`
- NFCorpus preregistration commit: `https://github.com/franklinbaldo/papers/commit/aa33ff96f18e363247977604e3491d281f00104d`
- NFCorpus preregistered replication: `https://github.com/franklinbaldo/papers/actions/runs/35466980084`
- NFCorpus protocol: `experiments/pontifex_benchmarks/PROTOCOL-NFCORPUS-LOCAL-SHARED-WARP-REPLICATION-K256-2026-09-19.md`
- NFCorpus findings: `experiments/pontifex_benchmarks/FINDINGS-NFCORPUS-LOCAL-SHARED-WARP-REPLICATION-K256-2026-09-19.md`
- NFCorpus executable: `experiments/pontifex_benchmarks/nfcorpus_local_shared_warp_replication_k256.py`
