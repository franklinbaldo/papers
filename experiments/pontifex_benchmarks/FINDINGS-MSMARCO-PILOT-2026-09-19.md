---
type: "Findings Record"
title: "Pontifex MS MARCO Passage transport pilot findings"
description: "A frozen 256-query MS MARCO Passage reranking pilot finds that independently fitted query-side and document-side A→B transports collapse retrieval despite improving coordinate fit with K; this negative result motivates a prospective shared-gauge control without changing the benchmark target."
timestamp: 2026-09-19T13:54:00-04:00
tags: [pontifex, msmarco, retrieval, reranking, transport, negative-result, leakage-audit, pilot]
---

# Pontifex MS MARCO Passage transport pilot findings

## Status

**Completed external benchmark pilot; negative result preserved.** Protocol: `PROTOCOL-MSMARCO-PILOT-2026-09-19.md`.

Run: <https://github.com/franklinbaldo/papers/actions/runs/35457214292>

Artifact: <https://github.com/franklinbaldo/papers/actions/runs/35457214292/artifacts/10589256951>

Classification: `pilot`, not a full-dev or leaderboard-comparable native retrieval result.

Primary metric: **MRR@10** on a deterministic 256-query subset of `msmarco-passage-dev-subset`, with every dense/transport method reranking the same frozen BM25 top-100 candidate IDs.

## Leakage audit

**PASS.** The candidate manifest was frozen from dev query text plus BM25 only. Dev qrels were not used for candidate generation, fitting, hyperparameter selection, early stopping, or method choice; they were opened only after every ranking had been frozen. Transport fitting used zero task labels.

The run records:

- query IDs: `1ee39d7850762f834d6b4c851534814f2354c21952027df2a85b10eab0af0520`;
- query text: `8af7446981d56c0198f8e48450ce2f151c6aa39508ae69d615ad43a802df10b7`;
- candidate rows: `a129eadf935f495914f69f9f74266f4421751b091e0925802a7ad0b2c086d1f1`;
- candidate PID sequence: `9dffbf983ce7ff345b8d11d445e80b0a9bf128213c4ae026f458534b22b22856`;
- query student IDs: `33e2bd14fa96a66cf0cde3a4ed356dff599c2618a5d5dbfe0672fa4f94d5e93e`;
- query validation IDs: `97ed80e0e81e2cf33418bf6d3c14f9595e7ee2979beda68c5a8bf111e2ce56fa`;
- document student IDs: `25777d29b95b34dd971f71b1dc2e6f0b47e5cabe83648eaef4dd548afc9994dc`;
- document validation IDs: `9c54e600347b114a7624d19b841c1bf5daf1edbaec460d9682ef58e45113b011`.

Candidate PIDs were excluded from document-side transport fit. True B dev coordinates were used only for the B oracle and post-freeze evaluation. A↔B pretraining overlap is `pretraining_overlap_possible`; overlap with the benchmark is `known` at the MS MARCO-family training level because both retrieval models are MS MARCO models. This is recorded as pre-existing knowledge, not evaluation leakage.

## Spaces and candidate pool

- A: ANCE, query encoder `castorini/ance-msmarco-passage`, public index `msmarco-v1-passage.ance`;
- B: TCT-ColBERT-v2 HN+, query encoder `castorini/tct_colbert-v2-hnp-msmarco`, public index `msmarco-v1-passage.tct_colbert-v2-hnp`;
- 256 pilot queries;
- 25,600 candidate rows;
- 24,858 unique candidate PIDs;
- 1,024 unlabeled train queries available for query-side A↔B fitting;
- 1,024 deterministic non-candidate corpus PIDs available for document-side A↔B fitting.

## Reference scores

| System | MRR@10 |
|---|---:|
| BM25 frozen candidate order | 0.205872 |
| A-only ANCE | **0.346215** |
| B-oracle TCT-ColBERT-v2 HN+ | **0.373555** |

The A→B oracle gap is `+0.027341` MRR@10. The predeclared 50% and 90% gap targets are `0.359885` and `0.370821`.

## Budget-matched transport result

Each K uses K query correspondences and K document correspondences, so every transport family receives the same `2K` paired observations across the two retrieval sides.

| K per side | Procrustes | Ridge | Pontifex residual | shuffled Pontifex | fraction of B utility recovered by Pontifex |
|---:|---:|---:|---:|---:|---:|
| 16 | 0.027488 | 0.011186 | 0.029506 | 0.021467 | -11.584 |
| 32 | 0.008873 | 0.006735 | 0.008760 | 0.014267 | -12.343 |
| 64 | 0.042112 | 0.015572 | 0.041178 | 0.014143 | -11.157 |
| 128 | 0.081416 | 0.015972 | 0.078547 | 0.020528 | -9.790 |
| 256 | 0.139156 | 0.046965 | 0.138714 | 0.018462 | -7.589 |
| 512 | **0.222836** | 0.094517 | **0.222483** | 0.013194 | -4.526 |

The negative fractions are not efficiency wins: every tested transport is materially worse than unchanged A-only ANCE. No method reaches either frozen quality target.

## Compute / supervision context

At K=512 the run used `3,145,728` float32 paired-representation bytes for query supervision and the same amount for document supervision (`6,291,456` bytes total). Pontifex fit+validation selection took about `0.394 s`; Ridge about `1.276 s` on the runner. Query encoding took about `66.5 s` for ANCE and `99.7 s` for TCT for the train+pilot batches. The public 8.84M-passage index vectors were not re-encoded; only the frozen PID subset was reconstructed into compact feature stores.

## Evidence against the present formulation

This pilot is strong evidence against **independently fitting a query-side and document-side transport and then assuming the two fitted outputs inhabit a retrieval-compatible common gauge**. Increasing K improves the transported MRR substantially, but even K=512 remains below BM25 and far below A-only. Pontifex is essentially tied with Procrustes at high K, so the local residual does not rescue this formulation.

This is also direct evidence against claiming low-budget dominance for ANCE→TCT transport in the tested formulation.

## Prospective mechanism follow-up

The result exposes a retrieval-specific confound that was not isolated in the original pilot: query and document maps were fitted independently. With underdetermined or regularized A→B alignment, independently fitted maps can choose different target-space gauges; dot-product retrieval then compares vectors expressed through different learned coordinate frames even when each side has acceptable B-coordinate validation loss.

A **shared-gauge** follow-up is therefore justified as a mechanism/fairness diagnostic, not as a replacement benchmark and not as post-hoc erasure of this negative result. The follow-up must:

1. preserve this pilot unchanged;
2. use the same candidate manifest, qrels boundary, K values, and total `2K` correspondence budget;
3. tie the linear/orthogonal orientation across query and document sides for every comparable baseline;
4. allow only side-specific centering/intercepts/residual neighborhoods needed to respect the asymmetric query/document distributions;
5. select all hyperparameters only from train/validation coordinate loss;
6. evaluate dev MRR@10 only after every shared-gauge ranking is frozen.

If tied-gauge Procrustes/Ridge alone recover the loss, the original collapse is primarily an interface/gauge failure rather than evidence for Pontifex. Pontifex has a method-specific advantage only if, under the same tied-gauge information budget, its residual transport improves the external task frontier beyond the simple tied baselines.
