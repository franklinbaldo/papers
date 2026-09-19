---
type: "Findings Record"
title: "Pontifex SciFact coupling-specificity findings at K=512"
description: "At K=512 the correct semantic correspondence has a larger positive point estimate over a coupled shuffled warp, but still fails the frozen significance rule; shared two-sided warp coherence remains the robust mechanism result."
timestamp: 2026-09-19T12:15:00-04:00
tags: [pontifex, scifact, retrieval, transport, coupling, null, mechanism, scaling, leakage-audit]
---

# Pontifex SciFact coupling-specificity findings at K=512

## Status

**Completed prospective external-benchmark mechanism follow-up.** Protocol: `PROTOCOL-SCIFACT-COUPLING-SPECIFICITY-K512-2026-09-19.md`.

Run: <https://github.com/franklinbaldo/papers/actions/runs/35451426518>

Artifact: <https://github.com/franklinbaldo/papers/actions/runs/35451426518/artifacts/10587352014>

This run was frozen after the K=256 coupling-specificity result and the K=512 residual-side ablation were already known. It therefore tests one narrow scaling question and is not an independent confirmation of the original Pontifex hypothesis.

## Leakage audit

**PASS.** The run reproduced the frozen SciFact split contract and manifests. K was fixed at `512`, the null bank contained 63 coupled and 63 independent permutations, and seed `20260919` generated the null banks before test relevance grades were loaded.

- `D_student`: 80% deterministic filtered train-query A/B representation pairs; first 512 are anchors;
- `D_val`: remaining filtered train-query pairs; used only to select `tau`/`lambda` by coordinate loss;
- `D_test`: official SciFact test qrels, opened only after transport and null assignments froze;
- task labels used for fit or selection: `0`;
- B test-query coordinates encoded: `false`;
- B corpus coordinates encoded: `false`.

Frozen manifests:

- student IDs: `bd5775940da2cb20d0ec5ee5ec4c9e35d871f82f12c0ff87e1955e38bd69ccf5`;
- validation IDs: `7a699f93186bd3b8c6042c8941b045ed8197438fceb396b0d7178af34e9c349c`;
- test IDs: `c307ee1faa37715704375e5c59a071b0c579b3114bedcbf263d43111a2f15ebf`;
- corpus IDs: `bcb266241b6c749fe993de0353d1ce95cc3b9fbd47b86d356ba54acab09ccfd4`;
- anchor IDs: `5a581b24b09b874bd65e759dfeabbe721eb66f947994470ceb3cee8768f4e80a`.

Selected only on `D_val`: `tau=0.05`, `lambda=1.0`, coordinate loss `0.261930`.

## Official task result

Primary metric: SciFact nDCG@10.

| Condition | nDCG@10 |
|---|---:|
| TRUE correspondence | **0.649954** |
| COUPLED-NULL mean | 0.641013 |
| COUPLED-NULL median | 0.640823 |
| COUPLED-NULL range | 0.631203–0.654367 |
| INDEPENDENT-NULL mean | 0.620021 |
| INDEPENDENT-NULL median | 0.620296 |
| INDEPENDENT-NULL range | 0.604729–0.637619 |

The TRUE score is the same K=512 Pontifex residual point from the frozen parent benchmark. The diagnostic changes only how that point is compared against matched null deformations.

## Predeclared contrast 1 — semantic specificity

Question: does the **correct residual-to-anchor correspondence** beat a generic shared scrambled warp?

- `TRUE - mean(COUPLED-NULL) = +0.008940` nDCG@10;
- finite-bank upper-tail p = `0.078125`;
- paired-query bootstrap mean delta = `+0.008940`;
- 95% percentile interval = `[-0.003652, +0.021549]`;
- bootstrap probability mean > 0 = `0.9164`.

**Decision: NOT SUPPORTED under the frozen rule.** The protocol required both a strictly positive paired-query 95% interval and finite-bank `p <= 0.05`. Neither condition is satisfied.

The point estimate is materially larger than the corresponding K=256 semantic-specificity point estimate, so increasing correspondence budget may strengthen a semantic-specific component. But the current external-benchmark evidence is not strong enough to claim it.

## Predeclared contrast 2 — shared-warp coherence

Question: does using the same two-sided warp preserve retrieval utility better than independently scrambled query/document warps?

- `mean(COUPLED-NULL) - mean(INDEPENDENT-NULL) = +0.020992` nDCG@10;
- paired-query bootstrap mean delta = `+0.020992`;
- 95% percentile interval = **`[+0.009079, +0.033756]`**;
- bootstrap probability mean > 0 = `0.9998`.

**Decision: SUPPORTED.** The shared-warp coherence effect not only survives at K=512 but is larger than at K=256.

## Relation to the parent utility benchmark

The parent SciFact transport benchmark reported:

- A-only MiniLM: `0.645082` nDCG@10;
- B-oracle MPNet: `0.655697`;
- K=512 Procrustes: `0.646066`;
- K=512 Pontifex residual: `0.649954`;
- fraction of B utility recovered by K=512 Pontifex: about `0.459`.

Thus the attractive K=512 downstream point remains real, but this null test changes its interpretation. We cannot yet attribute that gain uniquely to correct semantic A↔B local correspondence, because a substantial part of retrieval preservation comes from applying one coherent nonlinear deformation to both sides.

## Evidence boundary

### Evidence for Pontifex

- Correct correspondence has a positive and larger point estimate over the coupled null at K=512 than at K=256.
- The full transported system remains above its matched Procrustes point estimate at K=512.
- All transport fitting remains label-free with respect to the SciFact task.

### Evidence against / limiting the strong thesis

- The frozen semantic-specificity criterion still fails at K=512.
- K=512 uses 512 of 645 eligible student correspondences, so this is not low-budget evidence.
- Shared-warp coherence is much more robust than semantic-specific correspondence under the current protocol.
- Therefore the result does not establish causal semantic locality, intrinsic toroidal topology, universal transport superiority, or a handful-of-probes advantage.

## Next discriminant

The highest-value immediate comparison is no longer another local-warp variant. It is the already-frozen **information-matched CCA/PLS/RFF baseline sweep** on the same SciFact split and K budgets. If a classical baseline reaches or exceeds the K=512 Pontifex point with the same information budget, the practical distinctiveness of the current residual transport weakens. If it does not, the external utility case becomes cleaner even though the mechanism interpretation remains bounded by this null result.
