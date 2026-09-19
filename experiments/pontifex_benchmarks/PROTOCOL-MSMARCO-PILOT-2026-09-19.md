---
type: "Protocol"
title: "Pontifex MS MARCO Passage transport pilot"
description: "Prospective plumbing-and-signal pilot for ANCE→TCT-ColBERT-v2 HN+ transport on a frozen BM25 candidate pool, with MS MARCO train-only adapter fitting and a held-out dev-query subset used only after maps are frozen."
timestamp: 2026-09-19T12:59:00-04:00
tags: [pontifex, msmarco, retrieval, reranking, ance, tct-colbert, transport, leakage-audit, pilot]
---

# Pontifex MS MARCO Passage transport pilot

## Status

**Prospective pilot.** Parent planning issue: #686.

This is deliberately not the final full-dev benchmark. Its purpose is to validate the end-to-end external task plumbing, candidate-manifest invariants, dual-index feature extraction, query-side transport, document-side transport, official MRR@10 scoring, and leakage accounting before the full `msmarco-passage-dev-subset` result is unsealed.

## External task

- collection: MS MARCO Passage Ranking V1;
- evaluation query source: Pyserini `msmarco-passage-dev-subset`;
- primary metric: **MRR@10**;
- pilot query count: `256`, selected deterministically from the dev-subset IDs by SHA-256 order with seed string `pontifex-msmarco-pilot-v1`;
- candidate generator: BM25 over the canonical Pyserini `msmarco-v1-passage` sparse index;
- candidate depth: `100` per pilot query;
- every compared dense/transport method reranks the **same frozen candidate IDs**.

The pilot score must be labelled `pilot`, never an official full-dev competitive result.

## Spaces

A:

- representation family: ANCE;
- Pyserini passage index: `msmarco-v1-passage.ance`;
- query encoder: `castorini/ance-msmarco-passage`.

B:

- representation family: TCT-ColBERT-v2 HN+;
- Pyserini passage index: `msmarco-v1-passage.tct_colbert-v2-hnp`;
- query encoder: `castorini/tct_colbert-v2-hnp-msmarco`.

Pretraining overlap A↔B: `pretraining_overlap_possible`. Benchmark overlap with either model's training data is `known` at the broad MS MARCO-family level because these are MS MARCO retrieval models; this is **not evaluation leakage**. The scientific question is whether a low-cost adapter can exploit already learned semantic structure. Evaluation leakage is prevented at the adapter-fit boundary below.

## Candidate-set contract

Candidate generation may use dev **query text** because the system must rank documents for those queries, but may not use dev qrels, labels, known relevant PIDs, B scores, Pontifex scores, or any dev-derived target to decide candidate membership.

The BM25 manifest is generated once before any transport is fitted. It records:

- ordered pilot qids and query-text hash;
- ordered candidate PIDs per qid;
- BM25 scores/ranks;
- union candidate PID hash;
- explicit dense-feature PID manifest hash.

Every method sees the same candidate pool.

## Adapter-fit information boundary

### Query-side correspondence

Use unlabeled query texts from `ir_datasets` MS MARCO Passage **train** only. Select train query IDs deterministically and split into `D_student_query` / `D_val_query` before any dev score is opened.

### Document-side correspondence

Use deterministic corpus PIDs from the existing full-cycle MS MARCO PID walk, excluding every pilot candidate PID before selecting `D_student_doc` / `D_val_doc`. These passage pairs are independent of dev qrels.

### Final pilot evaluation

Only after all K-specific maps and hyperparameters are frozen may dev qrels be loaded to compute pilot MRR@10.

## Budgets

Pilot K values: `16, 32, 64, 128, 256, 512` where available.

For each K, query-side and document-side adapters receive the same number K of A↔B paired observations from their respective frozen student pools. Record text/query bytes when available, float32 paired-representation bytes, fitted floats, fit time, mapping time, rerank time, and encoder/index provenance.

## Methods

Required in the pilot:

- BM25 frozen-candidate ordering reference;
- A-only ANCE candidate rerank;
- B-oracle TCT-ColBERT-v2 HN+ candidate rerank;
- paired Orthogonal Procrustes, separately fit for query and document sides;
- Ridge linear A→B map, same K and train/validation boundary;
- Pontifex residual transport: Procrustes coarse map + local residual interpolation, separately fit for query/document sides;
- shuffled-correspondence Pontifex negative control using the same K.

CCA/PLS/RFF/capacity-matched MLP remain mandatory for the full benchmark, but may wait until the pilot proves that query encoding, explicit PID extraction, candidate scoring, and qrel isolation are correct.

## Hyperparameter selection

No dev MRR/qrel may select anything.

- Procrustes has no task-tuned hyperparameter;
- Ridge alpha is selected by B-coordinate loss on train validation coordinates;
- Pontifex `tau` and residual scale are selected by B-coordinate loss on train validation coordinates;
- shuffled control receives the same validation procedure.

All choices are frozen before dev qrels are loaded.

## Leakage audit PASS criteria

- no dev qrel/label enters candidate generation, adapter fitting, hyperparameter selection, early stopping, or method choice;
- pilot dev qids and candidate manifests are hashed before fitting;
- train-query IDs, train/validation membership, corpus PID student/validation sets, every K prefix, and random seeds are hashed;
- candidate PIDs are excluded from document transport fit/validation;
- true B dev query vectors and true B candidate document vectors are used only for B-oracle scoring and post-freeze geometry diagnostics;
- pretraining overlap is recorded separately from evaluation leakage;
- shuffled correspondence is evaluated under the same information budget.

## Success / failure boundary

The pilot succeeds operationally if it produces reproducible MRR@10 for all required methods on the frozen candidate pool with a PASS leakage audit. Scientific evidence is provisional.

A promising signal is Pontifex beating Procrustes/Ridge/shuffled at the same K while closing a material fraction of the A→B oracle gap. A negative or null signal is equally valid and must be preserved. The full 6,980-query dev result is not run until this plumbing audit is clean and the full baseline matrix is frozen.
