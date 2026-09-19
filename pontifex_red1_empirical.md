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

## 3. Current evidence / hypothesis boundary

Supported: under the frozen SciFact K=512 setup, shared query/document warp coherence is robust to global, residual-magnitude-matched, and coarse balanced-group nulls; and the tested Pontifex map substantially outperforms CCA, PLS and RFF+ridge coordinate mappings at the same K=512 correspondence budget.

Not supported: the stronger claim that exact residual-to-anchor identity is necessary. It has now failed the same predeclared two-part criterion under three completed null families. Also not supported: robustness to **tight** source-space locality, because the completed balanced-group run's own donor-distance diagnostics show that its groups were not genuinely local.

Still hypotheses or outside this diagnostic: causal semantic locality, an intrinsic or physical torus, universal transport superiority, native-B superiority, low-budget superiority, cross-dataset generalization, and Assembly-to-student generalization.

## 4. Prospective stronger discrimination: residual norm + hard A-KNN donor constraint

The next frozen protocol replaces the weak balanced-group notion of locality with a direct rank constraint. Inside each of the eight 64-anchor residual-norm strata, every anchor may receive a residual only from one of its **16 nearest non-self neighbors in normalized `D_student` A-space**. Each of the 63 coupled and 63 independent nulls is a unique perfect-matching derangement on that fixed bipartite candidate graph. The graph and both banks are hashed before the first `D_test` grade read.

The run must report donor cosine-distance and donor-rank diagnostics, and it fails rather than silently widening the neighborhood if any accepted donor exceeds rank 16. The semantic-specificity decision rule remains unchanged: paired-query 95% interval strictly above zero **and** finite-bank `p<=0.05`.

This is adaptive/prospective, not an independent replication. A positive result would strengthen only the narrow claim that exact residual identity adds utility beyond residual magnitude and a hard source-space locality constraint. A negative result would further weaken exact-identity claims. Either outcome leaves broader torus, causality, and physical-topology hypotheses unproven.

## Reproducibility

- PR: `https://github.com/franklinbaldo/papers/pull/485`
- completed global K=512: `https://github.com/franklinbaldo/papers/actions/runs/35451426518`
- completed norm-matched K=512: `https://github.com/franklinbaldo/papers/actions/runs/35455793661`
- completed balanced-group norm+local K=512: `https://github.com/franklinbaldo/papers/actions/runs/35457676312`
- completed classical baselines: `https://github.com/franklinbaldo/papers/actions/runs/35455793508`
- hard-locality prospective protocol: `experiments/pontifex_benchmarks/PROTOCOL-SCIFACT-NORM-KNN-MATCHED-COUPLING-K512-2026-09-19.md`
