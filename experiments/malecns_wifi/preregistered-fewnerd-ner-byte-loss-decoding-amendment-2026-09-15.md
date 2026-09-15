---
type: "Protocol"
title: "Preregistration amendment — byte loss and token/entity decoding for Few-NERD NER"
description: "Freezes equal-token-weight byte supervision and deterministic byte-logit aggregation back to official Few-NERD token/entity predictions before the first trained NER smoke."
tags: [malecns, few-nerd, ner, bytes, loss, decoding, preregistration]
timestamp: 2026-09-15T22:45:00Z
---

# Preregistration amendment — byte loss and token/entity decoding for Few-NERD NER

Date: 2026-09-15

Recorded before the first trained MaleCNS Few-NERD NER smoke.

## Output space

The trainable NER head emits one logit vector per UTF-8 byte position for the complete Few-NERD fine ontology: outside (`O`) plus 66 fine entity types.

Semantic fields and the recurrent MaleCNS state remain positional. Official token boundaries are used only to define supervision weights and the benchmark-boundary decoder.

## Training loss

Every byte inside an official token inherits that token's `fine_ner_tags` class. ASCII separator bytes inserted by canonical reconstruction are excluded from supervised loss.

To avoid giving longer UTF-8 spellings more weight merely because they contain more bytes, each official token receives total weight 1. Within a token of `n` bytes, each byte-level cross-entropy term therefore receives weight `1/n`. The sentence loss is the mean of these per-token losses.

This preserves byte-level supervision while making the learning objective invariant to UTF-8 byte length of an official token.

## Benchmark-boundary decoding

For each official token, average the model's **pre-softmax byte logits** over that token's exact UTF-8 byte interval. The token prediction is `argmax` of the resulting 67-class mean-logit vector.

Do not majority-vote hard byte labels for the benchmark result: averaging logits preserves confidence information and is deterministic.

Convert the predicted token labels to Few-NERD IO entities using maximal contiguous runs of the same non-zero fine label. A label change terminates the current entity even without an intervening `O`.

## Primary score

Entity-level micro precision, recall and F1 with exact token span + fine entity type match.

## Guardrails

- Separator bytes never contribute to supervised loss or entity scoring.
- Test labels do not influence thresholds, pooling, decoding, class weights, training budget or stopping.
- Validation may be used for training-budget selection; the first frozen full-test evaluation is the primary result.
- Byte logits remain inspectable so boundary behaviour can be analysed independently of the official token-level scorer.
