---
type: "Protocol"
title: "Preregistration amendment — byte logits to Few-NERD token/entity decoding"
description: "Freezes the multiclass positional decoder and exact byte-logit to official-token/entity conversion before the first trained Few-NERD MaleCNS run."
tags: [malecns, few-nerd, ner, decoder, bytes, preregistration]
timestamp: 2026-09-15T19:10:00Z
---

# Preregistration amendment — byte logits to Few-NERD token/entity decoding

Date: 2026-09-15

Recorded before the first trained MaleCNS Few-NERD smoke.

## Decoder

The recurrent MaleCNS state is decoded at every UTF-8 byte position into **67 logits**: label 0 is `O` and labels 1–66 are Few-NERD's official fine-grained entity types (`fine_ner_tags`). The benchmark uses Few-NERD's published IO scheme; no artificial B/I labels are introduced.

## Byte → official-token boundary

For official token `i` with frozen UTF-8 byte interval `[a_i, b_i)`, aggregate the model's real-valued byte logits before classification:

`token_logits_i = mean(byte_logits[a_i:b_i], axis=byte)`

`token_class_i = argmax(token_logits_i)`

Separator-space bytes are excluded from this aggregation. We do **not** majority-vote hard byte labels in the scientific runner; hard-label majority remains only a byte-axis round-trip smoke utility.

## Token classes → entities

Predicted entities are maximal contiguous runs of the same non-zero fine label. `O` terminates an entity and a change from one non-zero label to another starts a new entity, matching Few-NERD's IO representation.

Primary scoring is exact token-span + fine-type micro precision/recall/F1.

## Training loss

Training supervision is applied at the official-token boundary after mean aggregation of byte logits, using multiclass cross-entropy over the 67 classes. This avoids overweighting long UTF-8 spellings while preserving byte-level recurrent dynamics inside the MaleCNS.

Class imbalance handling, if used beyond ordinary cross-entropy, must be fixed from the training split only and preregistered before a benchmark-evidence run. The first smoke uses unweighted cross-entropy.

## Semantic channels and adapters

The first trained smoke uses eight distinct frozen semantic channels: MiniLM and E5 × token-window scales 1, 2, 4 and 8. Each channel has its own trainable residual rank-16 adapter; adapters are not shared across encoder or scale. The adapter form is the established v3 form:

`A(x) = unit(x + 0.1 * up(tanh(down(unit(x)))))`

with zero-initialised `up`, so the initial adapted field equals the frozen semantic field up to normalisation.

No benchmark labels enter MiniLM/E5 or the semantic cache. Supervision updates adapters and the 67-way decoder through the MaleCNS recurrent path.

## Whole-brain path

The smoke reuses the established full-graph path: row-normalised signed MaleCNS graph, registered sensory population for input, recurrent state over all neurons, `gain=4.0`, `leak=0.4`, target input RMS `0.05`, and a fixed sparse projection from the whole recurrent state to the trainable decoder.

## Smoke guardrail

The first trained smoke uses train examples for optimisation and dev examples for evaluation only. Test is not loaded. Smoke scores are infrastructure evidence, not the official benchmark result.
