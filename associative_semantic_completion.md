---
type: "Paper"
title: "Associative Completion of Sparse Semantic Pyramids"
description: "Draft empirical systems paper: use cheap observed semantic channels as associative keys for historically observed expensive channels, with confidence-gated real-embedding fallback."
tags: [embeddings, retrieval, associative-memory, semantic-pyramid, tagging]
timestamp: 2026-09-14T21:20:00-04:00
status: "pre-registered design; no confirmatory results yet"
---

# Associative Completion of Sparse Semantic Pyramids

## Abstract

Dense multiresolution semantic representations are attractive for precise span tagging but expensive if every scale must be re-embedded at every position. We study a complementary architecture in which the live representation is sparse in measurement and approximately dense through associative memory. A cheap local or seen-prefix embedding acts as a retrieval key; previously observed expensive coarse channels attached to semantically similar keys are reused as provisional values. Low-confidence retrieval triggers the real expensive encoder, turning semantic memory into a cost-saving hypothesis mechanism rather than a source of fabricated certainty.

The central question is not whether nearest-neighbour retrieval can approximate embeddings in the abstract. It is whether a leakage-safe associative completion layer can retain most of the tagging value of a fully observed semantic pyramid while avoiding a substantial fraction of expensive encoder calls. We additionally test a domain-level mechanism prediction: structurally repetitive corpora should expose denser cross-document semantic memory and therefore permit more aggressive skipping of expensive observations at the same quality floor.

## Core idea

At text position `t`, suppose only fine channels have been physically observed:

```text
4 / 8 / 16 / 32 tokens     real, cheap
64 / 128 / 256 tokens       missing or expensive
512 / 1024 tokens            missing or expensive
```

A query built only from text already observed at or before `t` searches a prior memory:

```text
cheap current state q_t
    -> cosine top-k over historical cheap keys
    -> associated historical coarse value(s)
    -> provisional missing channel
```

The key and value may be produced by different encoders and may have different dimensions. This is a key-value association, not cross-space arithmetic.

A confidence gate decides whether to trust the remembered value or pay for the real observation:

```text
query
  -> high-confidence memory match -> reuse remembered channel
  -> low-confidence match         -> compute real expensive channel
                                    -> optionally add new association to memory
```

If this works, the cost of maintaining a rich semantic field should fall as the memory becomes more representative of the domain.

## Why this is not ordinary embedding cache

A content-addressed cache answers: "have I embedded this exact text before?"

Associative completion answers: "have I seen a cheap semantic state like this before, and what did the expensive sense look like then?"

The first is exact reuse. The second is prediction from experience. They have different correctness and leakage rules and are measured separately.

## Why formulaic corpora are the target, not a caveat

Many high-volume text domains are deliberately repetitive: judicial decisions, contracts, medical records, insurance claims, filings and procurement documents use recurring semantic states and recurring larger structures. That is exactly the regime in which repeated expensive observation is most plausibly avoidable.

The paper therefore makes an applicability prediction rather than apologizing for a favourable corpus:

> **At a fixed quality floor, the fraction of expensive encoder calls that associative completion can avoid should increase with the corpus's structural/semantic repetitiveness.**

We preregister two descriptive statistics. `F_sem` is label-free cross-document semantic neighbourability: for each cheap query key, find its closest admissible key from another document and summarize the cosine distribution (mean, median, lower-tail quantile and coverage over a frozen confidence grid). `F_struct`, where annotations exist, measures how concentrated recurring structural tags are in relative document position using normalized entropy.

A single TJRO corpus cannot prove the cross-domain relationship. Its role is to report the local point `(formulaicity, savings, quality retention)`. The stronger mechanism claim is reserved for a future multi-genre study: if corpora with higher `F_sem`/`F_struct` do not systematically support more skipped expensive observations at the same quality floor, then the proposed explanation for when associative completion pays is wrong even if the method remains useful locally.

## Experimental decomposition

The governing protocol compares:

- a full real pyramid;
- the physically observed sparse pyramid alone;
- trivial mean and shuffled-value imputations;
- a small parametric cheap-to-coarse predictor;
- top-1 associative retrieval;
- top-k value barycenters;
- confidence-gated associative completion with real fallback.

The primary result is joint: held-out tagging quality and measured embedding cost. A method that preserves quality but saves no expensive calls is not a systems win; a method that saves calls by degrading tagging is not a semantic win.

## Confidence is a selected policy, not an oracle

The fallback threshold `tau` determines how much real observation is purchased and is therefore a hyperparameter, not a descriptive statistic. It is selected strictly inside each outer training fold together with the other frozen retrieval choices such as `k` and top-k temperature.

Selection is lexicographic. Inner-validation candidates must first satisfy the paper's quality floor relative to the real pyramid (at least 90% of its macroAP and within 0.03 absolute macroAP). Among those, the policy that avoids the most expensive calls wins; ties prefer higher macroAP and then more conservative fallback. If no candidate reaches the quality floor, selection falls back to the highest inner-validation macroAP and the failure to enter the economic regime is reported.

Thus the held-out document never participates in deciding how much uncertainty is acceptable, and the final output reports `selected_by_fold` rather than a globally tuned confidence threshold.

## Causality and leakage

For a held-out document, associative memory contains no item derived from that document. Query features use only text seen up to the current point. Historical memory may of course contain large contexts from training documents; that is the memory being tested.

A separate within-document-prefix memory can be studied later, but it is not part of the confirmatory result.

## Relationship to the semantic retina

The semantic-pyramid programme asks whether multiple scales and sensor types form a useful field. Associative completion asks whether every sense needs to be physically measured at every moment.

The resulting architecture is:

```text
real cheap channels
+ exact cached channels
+ confidence-marked remembered channels
+ real expensive fallback when needed
    -> local flavourization
    -> tagger and/or recurrent substrate
```

Retrieved channels are not treated as truth. They are remembered hypotheses about missing senses whose confidence determines when the system must look again.

## Claim boundary

A positive result would support a narrow claim: on this corpus and frozen key/value schemas, associative semantic memory recovers enough missing multiscale information to preserve tagging quality while reducing measured expensive embedding work.

A broader applicability claim requires independent corpora: the preregistered prediction is that formulaicity statistics predict the savings/quality frontier across genres. That prediction is separately falsifiable from whether TJRO itself yields a systems win.

The result would not establish that coarse embeddings are generally predictable from short text, that retrieval replaces long-context encoders, or that memory can safely use future context from the document being evaluated.
