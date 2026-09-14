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

The central question is not whether nearest-neighbour retrieval can approximate embeddings in the abstract. It is whether a leakage-safe associative completion layer can retain most of the tagging value of a fully observed semantic pyramid while avoiding a substantial fraction of expensive encoder calls.

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

## Why it may work

Many domains, especially structured legal text, revisit similar local semantic states inside recurring larger contexts. A short fragment such as a procedural transition, citation pattern, report formula or dispositive marker may strongly constrain the kind of section surrounding it even when the exact larger text is new.

This does not imply every local state determines its context. Semantic collisions and genuinely novel states are expected. The architecture gains value only if confidence separates recoverable cases from cases that need a real observation.

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

It would not establish that coarse embeddings are generally predictable from short text, that retrieval replaces long-context encoders, or that memory can safely use future context from the document being evaluated.
