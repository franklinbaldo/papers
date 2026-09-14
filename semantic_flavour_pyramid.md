---
type: "Empirical Paper"
title: "Semantic Flavour Pyramids: Reusable Multiresolution Embeddings for Precise Span Tagging"
description: "Pre-registered empirical design for cached multiresolution semantic tiles and scale-local flavourizers; confirmatory results not yet collected."
tags: [semantic-embeddings, tagging, multiscale, flavourizer, caching, malecns]
timestamp: 2026-09-14T20:45:00-04:00
---

# Semantic Flavour Pyramids: Reusable Multiresolution Embeddings for Precise Span Tagging

**Franklin Baldo**  
Independent Researcher

> **Pre-registered design; no confirmatory results yet.** Existing MaleCNS tagging pilots motivate the design but are not reported here as results of this experiment. The governing protocol is `experiments/malecns_wifi/semantic-flavour-pyramid.md`.

## Abstract

Dense text embeddings are normally computed at one or a few chunk sizes and then consumed as disposable model inputs. We propose a different representation: a **semantic flavour pyramid**, in which a document is decomposed into overlapping, content-addressed semantic tiles at progressively smaller scales, each tile can be expressed through relations to larger containing tiles, and lightweight trainable flavourizers modulate selected scales for downstream span tagging. The design has two linked hypotheses. First, fine channels should provide spatial precision for tag boundaries while coarse channels preserve contextual identity. Second, short-span embeddings can be precomputed cheaply in batches, cached by content and encoder revision, and reused across many flavourizer or downstream-model training runs. A biological connectome such as MaleCNS may optionally be used as a temporary training scaffold, but it is not part of the required inference architecture. We preregister a four-arm scale-localization test (`none`, `high_only`, `low_only`, `all_scales`), a matched compute/cache ledger, and controls separating benefits of the semantic pyramid from benefits of MaleCNS-assisted training. No confirmatory result is claimed in this draft.

## 1. Introduction

Span tagging combines two requirements that are easy to conflate. A system must know **what semantic role** a region plays, and it must know **where that role begins and ends**. Large semantic chunks are well suited to the first problem but coarse for the second. Very small text units provide precise position but weak context when treated alone.

The proposed semantic flavour pyramid treats these as different frequency bands of the same text. A document is embedded at many overlapping scales. High levels represent broad semantic context; progressively lower levels represent increasingly local semantic, lexical and formal detail. Instead of repeatedly re-encoding the corpus while experimenting with a downstream tagger, tile embeddings are stored in a content-addressed cache. Downstream trainable transformations operate on those cached values.

The name **flavourizer** denotes a small residual transformation applied to one or more channels. A flavourizer does not receive the gold tag at inference. During supervised training it is optimized so that the representation becomes more useful for predicting the tag at the correct location. The architecture therefore permits the model to concentrate tag-discriminative changes in low-level channels while retaining broader context from high-level channels.

MaleCNS motivated this formulation because a recurrent substrate can be driven by many simultaneous channels and can provide an auxiliary training signal. But the core proposal is not a claim that a fly brain is necessary. A final successful system may discard the connectome entirely.

## 2. Representation

### 2.1 Semantic tiles

For a tokenized document `x`, define overlapping tiles at scales

`S = {1024, 512, 256, 128, 64, 32, 16, 8, 4}`.

At scale `s`, tiles have width `s` and confirmatory stride `s/2`. The overlap reduces dependence on an arbitrary chunk boundary and allows a span boundary to appear near the center of at least one fine tile.

Each tile is identified by the exact text sent to the encoder plus the encoder identity, immutable revision and normalization version. The embedding cache key is therefore content-addressed rather than document-addressed. Identical text under the same encoder policy has one embedding regardless of how many documents or experiments reuse it.

### 2.2 Relational channels

A fine tile may be related to one or more containing ancestors. For one encoder space, a child `c` and parent `p` can be represented by a geometric relation such as alignment plus residual:

`a = <c_hat, p_hat>`

`r = c_hat - a p_hat`.

The channel is `R(c|p) = [a, r]`. Multiple relations may coexist, e.g. `R(64|128)` and `R(64|256)`.

The paper does **not** assume that relation-only features are universally superior to absolute embeddings. Existing pilot results motivate testing a much denser hierarchy than the earlier sparse relation design. Absolute channels and relational channels remain separable ablations.

### 2.3 Heterogeneous encoders

Different scales may use different embedding models. Cross-encoder vector arithmetic is forbidden: every relation is computed between child and parent embeddings produced by the same encoder and revision. The resulting relation channels may then coexist downstream.

This permits expensive high-quality encoders at coarse scales and cheaper encoders at fine scales. Whether this actually reduces total cost is measured, not assumed.

## 3. Low-Level Flavourization

For channel `C_s` at scale `s`, a low-rank flavourizer applies

`C'_s = C_s + U_s tanh(V_s C_s)`.

The residual form makes the size of the learned intervention measurable. Flavourizers operate strictly downstream of cached embeddings, so retraining them never requires recomputing the encoder output.

The primary scale-localization experiment compares:

1. `none`: no flavourizer;
2. `high_only`: flavourizers on child scales >=128;
3. `low_only`: flavourizers on child scales <=32;
4. `all_scales`: flavourizers on all eligible scales.

The central prediction is not merely that more parameters improve tagging. `high_only` and `low_only` therefore use matched trainable parameter budgets. `all_scales` is reported as a capacity-expanded arm and requires a matched-budget follow-up before a scale-specific causal claim can rest on it.

## 4. Cache and Reuse as Part of the Model Design

The embedding stage is treated as reusable infrastructure rather than as part of every training epoch.

For each scale the experiment records total tile occurrences, unique cache entries, exact repeats, cache storage, encoding wall time, input token volume and avoided encoder calls. Embeddings are created in batches so per-call model overhead is included in the real measured cost.

The practical hypothesis is that fine tiles are cheap enough to precompute densely and become especially attractive when the same corpus supports many downstream experiments. The stronger reuse claim is tested by requiring later flavourizer epochs to run with zero encoder calls after cache construction.

This distinction is important: computational reuse is an engineering contribution independent of whether any particular recurrent substrate improves semantic quality.

## 5. Optional MaleCNS Training Scaffold

A second stage may temporarily add a frozen MaleCNS path during training:

`flavourized pyramid -> MaleCNS -> disposable taste head -> supervised food/flavour target`.

The main tagger path remains direct. The auxiliary MaleCNS loss is annealed to zero before training finishes, and the connectome branch is removed for held-out inference.

The scientific question is therefore whether exposure to the substrate changes the learned flavourizers in a way that improves the final standalone tagger. It is **not** whether MaleCNS must remain deployed.

Controls use the same final architecture and compare tag-only training, MaleCNS assistance, degree-preserving-null assistance and random-ESN assistance. A topology-specific teaching claim requires the real connectome to beat all alternatives.

## 6. Evaluation

The confirmatory corpus uses the same held-out-document span annotations as the governing MaleCNS semantic-tagging experiment unless a larger corpus is frozen before execution.

The primary metric is macro per-tag AUPRC. Secondary metrics are any-tag AUPRC, tag identity accuracy on true spans, fine-resolution boundary AUPRC, sample efficiency, per-document paired deltas and residual magnitude by scale.

The pre-registered gates are defined in `experiments/malecns_wifi/semantic-flavour-pyramid.md`. In summary, low-level flavourization must beat no flavourization and matched-budget high-level flavourization; the dense pyramid must beat the earlier sparse relation design; and the cache must demonstrate real encoder-call reuse rather than theoretical reuse.

## 7. Expected Analyses, Not Results

If `low_only > high_only`, the first interpretation will be that fine channels are especially useful for precise tag localization under the tested representation. It will not establish that low-level semantics are universally superior.

If `all_scales` wins while matched-budget `low_only` and `high_only` do not separate, the result will be attributed first to additional capacity, not to a special multiscale mechanism.

If MaleCNS-assisted training improves the final standalone tagger but matched recurrent nulls do equally well, the result supports recurrent auxiliary teaching rather than biological topology.

If the dense pyramid fails the preregistered gates, the experiment stops rather than adding ever smaller channels after seeing the result. Token/byte channels require a separately frozen follow-up.

## 8. Relationship to Existing Work in This Repository

This paper is deliberately separate from the MaleCNS reservoir paper. The earlier experiment asks whether a frozen biological connectome itself provides a better representation for semantic tagging. The fly-assisted experiment asks whether the substrate can help during training even when removed at inference. This paper asks a more general representation-and-systems question: whether dense reusable semantic tiles and local flavourizers form an effective and economical substrate for precise tagging.

It is also distinct from `semantic_tokenization_transformers.md`. Semantic Tokenization Transformers proposes replacing subword sequences with high-level semantic codes for language-model pretraining. The present work keeps a simultaneous **pyramid** of resolutions and targets local supervised span tagging rather than autoregressive semantic-code prediction.

## 9. Limitations

The planned first corpus is small and domain-specific. Fine-scale embeddings may be cheap per token but inefficient if batching and model-launch overhead dominate. Exact tile reuse may be limited when text varies lexically even if it is semantically repetitive. Low-level flavourizers may simply become ordinary local classifiers. The experiment therefore reports both task quality and a complete compute/cache ledger, and it uses matched-budget controls before attributing improvements to scale.

## 10. Conclusion

The proposal separates expensive semantic perception from cheap repeated adaptation. A text corpus is embedded once into a reusable multiresolution tile pyramid; lightweight flavourizers then learn where and at what scale tag-discriminative changes should occur. If successful, the result would provide a representation that is simultaneously semantically contextual, spatially precise and reusable across downstream training runs. MaleCNS is one possible teacher for shaping that representation, not a required component of the final system.

## Pre-registration

Governing protocol: `experiments/malecns_wifi/semantic-flavour-pyramid.md` on the frozen experiment branch. Confirmatory result language must not be added to this paper until the corresponding run is complete and recorded.
