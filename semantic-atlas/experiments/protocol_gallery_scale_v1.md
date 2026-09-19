---
type: "Protocol"
title: "Semantic Atlas — Gallery-Scale Gate v1"
description: "Frozen scale test for cross-observer local alignment and observer-specific relational structure before the Atlas manuscript is rewritten."
tags: [semantic-atlas, preregistration, embeddings, mknn, gallery-size]
timestamp: 2026-08-26T17:10:00-04:00
---

# Semantic Atlas — Gallery-Scale Gate v1

## Status

This protocol is frozen before collecting embeddings for the 382-document corpus. It is the large-gallery gate required by PRs #385, #386 and the blocked Atlas PR #379. It does not reopen the 116-document relational-dynamics v1, whose protocol and result remain frozen in PR #380.

The machine-readable contract is `gallery_scale_v1.json`. If prose and JSON differ, the JSON controls execution.

## Question

The pilot observed raw `mKNN@5 = 0.467241` and permutation-calibrated `mKNN@5 = 0.433028` on 116 documents. That point may represent scale-stable partial local alignment or a small-gallery artifact.

This run asks:

> As the gallery grows under the same two frozen encoders, does permutation-calibrated mutual-kNN remain material and reasonably stable, while staying below a pre-specified same-observer stability reference?

This is a static relational experiment. It does not test chronology-specific flow, susceptibility, routing, steering or causal dynamics.

## Frozen corpus

- source commit: `7674788808165019772d05631775c0dedde3c96a`;
- all 382 Markdown paths present in that tree;
- deterministic order: `sha256(path)`;
- exact first 1,200 characters after UTF-8 replacement decoding and outer whitespace trimming;
- no path, topic, language or document family is excluded after inspection;
- every excerpt, path and source commit is content-hashed in the embedding-cache sidecar.

The corpus is naturally timestamped in Git, but chronology is not used in this static gate. First-touch timestamps are preserved only as provenance for a later, separately frozen dynamical experiment.

## Frozen observers

- reference: `Qwen/Qwen3-Embedding-0.6B@97b0c61`;
- transfer: `sentence-transformers/all-MiniLM-L6-v2@1110a24`.

Raw outputs and L2-normalized derivatives are persisted separately through the content-addressed cache from PR #371.

## Gallery curve

Evaluate `N in {32, 48, 72, 116, 176, 256, 382}` and `k in {3, 5, 10}`. For every `N < 382`, use eight deterministic hash-selected subsets. `N=382` has one unique full-corpus replicate.

For each subset report:

1. raw mKNN;
2. the correspondence-permutation null mean and 95th percentile from 1,024 shared permutations;
3. plus-one upper-tail p-value;
4. calibrated mKNN, using the same max-preserving calibration as the v1 reanalysis:

`max((mKNN_observed - tau_0.95) / (1 - tau_0.95), 0)`.

The calibrated panel is decision-bearing because chance overlap scales with `k/N`. Replicate medians and 10th/90th percentiles are reported without discarding individual subset rows.

## Same-observer stability control

Exact same-model/same-text mKNN is identically one and is not a seed-null. The frozen perturbation is instead **format-only**:

- view A: the exact frozen Markdown excerpt;
- view B: that already-truncated excerpt after removing Markdown punctuation while preserving lexical headings, link labels, link targets and code content.

For each observer independently, compute the same raw and permutation-calibrated mKNN curve between views A and B. These are labelled format-perturbation stability references, never stochastic encoder variability. The conservative joint reference at each `N,k` is the lower of the two observer-specific calibrated curves.

The operator is deliberately weak. If the conservative calibrated stability reference falls below `0.50` at any of the final three gallery sizes, this does not rescue the cross-model result; the registered outcome is **invalid same-observer stability control** and no static claim is promoted.

## Decision rule

Primary `k=5`; `k=3,10` are sensitivity descriptions.

The static paper proceeds as **shared but observer-specific relational structure** only if all three conditions hold:

1. calibrated cross-model mKNN at `N=382` is at least `0.20`;
2. it retains at least `75%` of the within-run calibrated score at `N=116`;
3. for each of the final three gallery sizes, cross-model calibrated mKNN is at least `0.10` below both observers' same-observer format-stability references.

If condition 1 or 2 fails, the registered result is **small-gallery artifact** and the static Atlas paper stops. No alternate aligner, subset or stability operator may be selected from these outcomes.

If scale survives but condition 3 fails, report **scale-stable alignment not separated from the stability ceiling**. That result does not support observer-specific discrete relational structure.

## Explicit exclusions

- no fitting of density, gap, hubness or susceptibility mechanisms;
- no rewriting of PR #379 before the gate returns;
- no new aligner tournament;
- no dynamic claim from Git chronology;
- no replacement corpus after inspecting the scale curve;
- no interpretation of a failed threshold as motivation for a new post-hoc claim.

## Required artifacts

- machine-readable result JSON with manifest/protocol hashes and every replicate;
- content-addressed raw and normalized embedding caches for both observers and both text views;
- a three-panel decision figure: raw curve, calibrated curve and primary-k stability comparison;
- exact terminal decision from the frozen gate.
