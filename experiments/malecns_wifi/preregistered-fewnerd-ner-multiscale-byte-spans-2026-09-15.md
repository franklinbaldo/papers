---
type: "Protocol"
title: "Preregistration amendment — multiscale byte/token/span channels for Few-NERD NER"
description: "Protocol amendment freezing the initial multiscale semantic receptive fields projected onto a common UTF-8 byte axis for MaleCNS NER."
tags: [malecns, few-nerd, ner, embeddings, multiscale, preregistration]
timestamp: 2026-09-15T18:04:00Z
---

# Preregistration amendment — multiscale byte/token/span channels for Few-NERD NER

Date: 2026-09-15

Recorded before the first Kaggle Few-NERD execution.

## Internal axis

The MaleCNS output axis remains UTF-8 bytes. Every prediction is attached to a byte position and later converted back to official Few-NERD entity spans/types only for evaluation.

## Receptive-field hierarchy

Semantic evidence may be generated at several deterministic receptive-field scales and projected back onto the same byte axis:

1. **byte-local**: individual UTF-8 byte position / tiny local byte neighbourhood;
2. **token**: the official Few-NERD token containing the byte;
3. **span-1**: one-token span (identical boundaries to token, retained as the base span level for a uniform span hierarchy);
4. **span-2**: every contiguous 2-token span;
5. **span-4**: every contiguous 4-token span;
6. **span-8**: every contiguous 8-token span;
7. optionally larger powers of two (16, 32, ...) only in later preregistered stress tests.

For a span of N official tokens, reconstruct its text using the same canonical single-ASCII-space rule as the sentence byte axis. Encode that span in each frozen semantic encoder and broadcast/interpolate the resulting semantic vector over the UTF-8 byte intervals covered by the span.

Overlapping spans are allowed and intentional. At a given byte, the method can therefore receive evidence from its token and from all enclosing spans at the registered scales.

## Channel identity

Scale is part of channel identity. Evidence from `MiniLM span-2`, `MiniLM span-4`, `E5 span-2`, etc. remains distinguishable before entering MaleCNS. No averaging across scales is required before the recurrent system.

The design goal is analogous to multiple receptive fields: fine scales localise boundaries; larger scales provide context and disambiguation.

## Training/evaluation guardrails

- Output resolution stays byte-level regardless of semantic receptive-field scale.
- Span boundaries are derived only from official Few-NERD token boundaries.
- No test-set tuning of which scales are enabled.
- Initial primary scale set is frozen as byte-local + token/span-1 + span-2 + span-4 + span-8.
- MiniLM/E5 tokenizers are implementation details of the semantic encoders and never define the prediction grid.
- Exact entity span + type evaluation remains the primary benchmark metric.

## Computational note

Span embedding generation is embarrassingly parallel across sentences, encoders and span scales and should be cached with provenance (`dataset revision`, `sentence id`, `span start/end token`, `byte start/end`, `encoder revision`, `scale`). Repeated MaleCNS training must reuse this cache rather than recompute semantic embeddings.
