---
type: "Protocol"
title: "Withdrawn amendment — byte-weighted loss for Few-NERD NER"
description: "Records and withdraws, before any trained run, a proposed byte-level cross-entropy objective in favor of the already preregistered token-boundary loss after byte-logit aggregation."
tags: [malecns, few-nerd, ner, bytes, loss, preregistration, withdrawn]
timestamp: 2026-09-15T22:45:00Z
---

# Withdrawn amendment — byte-weighted loss for Few-NERD NER

Date: 2026-09-15

**Status: withdrawn before the first trained MaleCNS Few-NERD execution.**

This file originally proposed applying cross-entropy independently to every UTF-8 byte, with inverse-token-byte-length weights. Review before execution showed that this would add an artificial auxiliary task: every byte would be required to classify the entity independently even though the public benchmark is defined on official Few-NERD tokens/entities.

The controlling protocol is therefore `preregistered-fewnerd-ner-decoder-amendment-2026-09-15.md`, recorded earlier and retained unchanged:

1. MaleCNS dynamics still advance at every UTF-8 byte position;
2. the decoder emits 67 real-valued logits at every byte;
3. logits are averaged across the exact bytes of each official token;
4. ordinary 67-way cross-entropy is applied once per official token;
5. separator bytes are excluded from the token aggregation and supervision;
6. token predictions are converted to Few-NERD IO entities and scored by exact span + fine type.

This gives every official token equal supervision weight regardless of UTF-8 length while preserving byte-level recurrent dynamics and positional evidence. No trained smoke or benchmark result was observed before this decision.
