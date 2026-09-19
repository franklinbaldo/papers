---
type: "Findings Record"
title: "Pontifex MS MARCO Passage shared-gauge findings"
description: "A prospective shared-gauge follow-up shows that the original two-tower transport collapse was largely an interface/gauge failure, but Pontifex does not beat tied Procrustes or shuffled correspondence and every transported system remains below A-only ANCE."
timestamp: 2026-09-19T14:18:00-04:00
tags: [pontifex, msmarco, retrieval, reranking, transport, shared-gauge, negative-result, leakage-audit, pilot]
---

# Pontifex MS MARCO Passage shared-gauge findings

## Status

**Completed external benchmark pilot mechanism/fairness follow-up.** Protocol: `PROTOCOL-MSMARCO-SHARED-GAUGE-2026-09-19.md`.

Run: <https://github.com/franklinbaldo/papers/actions/runs/35460154668>

Artifact: <https://github.com/franklinbaldo/papers/actions/runs/35460154668/artifacts/10589588543>

Artifact SHA-256: `bb562587a6a7c637ee9588f021990e8856fed2579c6a9f33b9e57e9d00ce9193`.

Classification: `pilot; prospective post-result mechanism/fairness follow-up`. This is not a full-dev or leaderboard-comparable native retrieval result.

Primary metric: **MRR@10** on the same frozen 256-query `msmarco-passage-dev-subset` candidate pool used by the parent pilot.

## Leakage audit

**PASS.** The frozen parent manifest was reproduced exactly and the compact public-index feature stores were restored from cache. No dev qrel or task label was used for candidate generation, transport fitting, hyperparameter selection, early stopping, or method choice. Candidate PIDs were excluded from document-side transport fitting. Dev qrels were opened only after every ranking had been frozen. The same shared-gauge restriction was applied to Procrustes, Ridge, Pontifex, and the shuffled correspondence control.

Frozen identities:

- query IDs: `1ee39d7850762f834d6b4c851534814f2354c21952027df2a85b10eab0af0520`;
- query text: `8af7446981d56c0198f8e48450ce2f151c6aa39508ae69d615ad43a802df10b7`;
- candidate rows: `a129eadf935f495914f69f9f74266f4421751b091e0925802a7ad0b2c086d1f1`;
- candidate PID sequence: `9dffbf983ce7ff345b8d11d445e80b0a9bf128213c4ae026f458534b22b22856`;
- query student: `33e2bd14fa96a66cf0cde3a4ed356dff599c2618a5d5dbfe0672fa4f94d5e93e`;
- query validation: `97ed80e0e81e2cf33418bf6d3c14f9595e7ee2979beda68c5a8bf111e2ce56fa`;
- document student: `25777d29b95b34dd971f71b1dc2e6f0b47e5cabe83648eaef4dd548afc9994dc`;
- document validation: `9c54e600347b114a7624d19b841c1bf5daf1edbaec460d9682ef58e45113b011`.

A↔B pretraining overlap remains `pretraining_overlap_possible`. Benchmark training overlap is `known` at the MS MARCO-family level because ANCE and TCT-ColBERT-v2 HN+ are MS MARCO retrieval models; this is pre-existing model knowledge, not evaluation leakage.

## Reference task scores

| System | MRR@10 |
|---|---:|
| BM25 frozen candidate order | 0.205872 |
| A-only ANCE | **0.346215** |
| B-oracle TCT-ColBERT-v2 HN+ | **0.373555** |

The frozen A→B gap is `+0.027341`. The predeclared 50%-gap target is `0.359885`; the 90% target is `0.370821`.

## Budget-matched result

Each K contributes K query A↔B pairs and K document A↔B pairs, for exactly `2K` paired observations per method.

| K/side | Separate Proc. | Separate Pontifex | Tied Proc. | Tied Ridge | Tied Pontifex | Tied shuffled |
|---:|---:|---:|---:|---:|---:|---:|
| 16 | 0.021168 | 0.021804 | 0.262063 | 0.019133 | 0.260423 | **0.284559** |
| 32 | 0.013985 | 0.013725 | 0.260169 | 0.034818 | 0.258578 | **0.260364** |
| 64 | 0.040036 | 0.040081 | **0.290985** | 0.071160 | 0.290892 | 0.262509 |
| 128 | 0.057636 | 0.054760 | 0.278035 | 0.115718 | **0.279005** | 0.276519 |
| 256 | 0.137094 | 0.135837 | 0.277393 | 0.140921 | **0.277756** | 0.274854 |
| 512 | 0.219975 | 0.226082 | 0.282684 | 0.248878 | 0.281917 | **0.284378** |

The shared-gauge intervention repairs a large fraction of the catastrophic failure of independent two-tower alignment. At K=64, for example, Procrustes changes from `0.040036` to `0.290985`; at K=512 it changes from `0.219975` to `0.282684`.

That repair is **not a Pontifex-specific win**. Tied Pontifex is effectively tied with Tied Procrustes throughout the useful range, sometimes slightly above and sometimes below. The shuffled control beats true Tied Pontifex at K=16, K=32, and K=512. No tied method beats unchanged A-only ANCE (`0.346215`).

## Utility recovery and quality frontier

Because every Tied Pontifex score remains below A-only, `fraction_of_B_utility_recovered` is negative at every K. At K=512 it is `-2.3517`; this should not be described as recovery, and raw MRR@10 is the appropriate quantity.

No Tied Procrustes, Tied Ridge, or Tied Pontifex configuration reaches the frozen 50% or 90% A→B quality target. Therefore:

- **same budget:** among true-correspondence transports, Tied Procrustes is as good as or better than Tied Pontifex for practical purposes, with far less fitted state;
- **same target quality:** no tested transport reaches even 50% of the A→B gap;
- **low-budget dominance:** absent; A-only dominates every transported system;
- **B utility recovered:** none in the downstream sense, because transported scores remain below A-only.

## Geometry/task mismatch

Tied Pontifex validation coordinate loss improves monotonically with K (`0.1315 → 0.0827`), while downstream MRR@10 does not. The shuffled control has substantially worse B-coordinate validation loss (`≈0.137–0.145`) yet sometimes matches or exceeds true correspondence downstream.

This is direct evidence for keeping geometry recovery secondary: better coordinate reconstruction of B is not sufficient for better retrieval utility.

## Gauge mechanism

The independently fitted query/document Procrustes rotations have large normalized Frobenius disagreement, decreasing from `1.4140` at K=16 to `1.3443` at K=512. The parent formulation fitted each side from fewer paired observations than the 768-dimensional representation, so the orthogonal completion is underdetermined. A shared map forces query and document vectors through the same orientation and removes this incompatibility.

There is also a structural reason not to interpret the tied-Procrustes repair as recovered B semantics. Ignoring side-specific mean translations, applying the same orthogonal W to query and document vectors preserves their centered dot products exactly. The repair therefore primarily establishes a **retrieval-interface constraint: query and document outputs must remain in a compatible gauge**. It does not establish transfer of B-specific utility.

## Reproducibility note for the parent separate-gauge pilot

The same-run reconstructions of separate Procrustes/Pontifex are not bitwise identical to the parent run even though hashes and data boundaries are unchanged. For example, parent K=512 Procrustes/Pontifex were `0.222836/0.222483`, while this follow-up reconstructed `0.219975/0.226082`. The parent run remains the authoritative record of its own result; tied-versus-separate contrasts in this findings record use the same-run values above.

This variability is consistent with the non-identifiability of independently completed orthogonal maps in the rank-deficient regime and is itself a reason to avoid treating the old separate-gauge transport as a stable scientific baseline without a gauge convention.

## Compute / storage frontier

The compact ANCE/TCT feature-store cache was reused; the two ~27.16 GB public dense indexes were not re-downloaded or re-encoded. At K=512:

- total paired-representation supervision: `6,291,456` float32 bytes;
- Tied Procrustes fitted state: `592,896` floats, fit `0.134 s`, map+rerank `0.200 s`;
- Tied Ridge fitted state: `592,896` floats, fit+selection `0.680 s`, map+rerank `0.248 s`;
- Tied Pontifex fitted state: `2,165,762` floats, fit+selection `0.177 s`, map+rerank `0.471 s`;
- query encoding in this run: ANCE `56.9 s`, TCT `95.5 s`.

Tied Pontifex therefore consumes materially more fitted state and mapping time than Tied Procrustes without improving downstream quality. A-only remains the practical quality frontier because it requires no incremental A→B supervision and scores higher.

## Evidence for / against Pontifex

**Supported:** a common cross-side gauge is crucial for any two-tower transport experiment; independent A→B fits can create an artificial retrieval collapse. This should become a protocol invariant for future retrieval work.

**Not supported:** method-specific utility from the current Pontifex local residual on ANCE→TCT MS MARCO. Under matched information, it does not beat the simple tied orthogonal baseline, shuffled correspondence can equal or exceed it, and every transport remains below A-only. This is evidence against the practical low-budget Pontifex hypothesis for this encoder pair and interface.

## Next highest-value action

Do not tune this pilot against its dev scores and do not unseal the full 6,980-query result: the pilot is already negative for the method-specific claim. The next benchmark should move to a **single-item-type external task** (classification or cross-model transfer) where one A→B map is applied to both train/test representations and the two-tower gauge confound is absent. Freeze the task, model pair, unlabeled correspondence budget, labeled probe budget, baselines, and test split prospectively before evaluation. A recognized intent/topic classification task with accuracy/F1 and explicit few-shot budgets is a natural next portfolio step.
