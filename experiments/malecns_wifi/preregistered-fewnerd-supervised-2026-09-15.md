---
type: "Protocol"
title: "Preregistered benchmark — MaleCNS on Few-NERD supervised (fine-grained NER)"
description: "Preregistered protocol for a frozen, positional MaleCNS recurrent reservoir on Few-NERD's supervised fine-grained named-entity-recognition split: token-level semantic channels, per-position readout, a linear probe fit on train/validation only, and span-level F1 on the untouched test split."
tags: [malecns, few-nerd, ner, reservoir-computing, token-classification, drosophila, connectome]
timestamp: 2026-09-15T19:30:00+00:00
---

# Preregistered benchmark — MaleCNS on Few-NERD supervised (fine-grained NER)

## Why this benchmark, and why now

`multieurlex21-throughput.md` optimised the frozen-MaleCNS pipeline for
document-level classification: a handful of pooled text chunks per document,
one reservoir pass, one embedding. That protocol never tests the hypothesis
this research programme actually cares about -- can the connectome learn
concepts/"flavours" from local context and *locate* new occurrences of them in
running text? A document-level vector cannot answer that; a token-level task
with positional readout can.

Order decided 2026-09-15: **Few-NERD supervised first** (this document), then
Few-NERD `intra`/`inter` (few-shot generalisation to entity types with little
supervision), then MultiCoNER II English as a harder stress test, with
CoNLL-2003 kept only as a historical sanity check, not a headline result.

## Task

- Dataset: `DFKI-SLT/few-nerd`, revision `205f3e9c9f3577ea2561d43f2f62dc249ab92d5b`.
- Config: `supervised` (the `intra`/`inter` few-shot configs are a later,
  separate preregistration -- do not mix their splits into this one).
- Splits used exactly as published (`train`: 131,767 sentences, `validation`:
  18,824, `test`: 37,648). No reshuffling, no relabelling.
- Labels: `fine_ner_tags`, 66 values (65 fine-grained entity types + `O`).
  `ner_tags` (8 coarse types + `O`) is recorded as context only, never as the
  scored label space.
- Tag scheme as published: **IO**, not BIO/BIOES -- a run of identical
  non-`O` fine labels is one entity. Converting that run to BIO for scoring
  (mark the first token `B-`, the rest `I-`) is bookkeeping for the metric
  library, not a change to any label or prediction; see "Metric" below.

## Architecture (positional, token-first)

```
tokens -> per-token frozen MiniLM/E5 hidden states (word-pooled over subwords)
       -> fused semantic vector (unit-per-model, concatenated)
       -> fixed Gaussian sensory projection (RMS-normalised per token)
       -> row-normalised MaleCNS recurrent step (gain, leak, tanh) -- one step per token
       -> fixed sparse whole-brain readout emitted at EVERY position
       -> 256-d embedding per token
```

No pooling of the sequence into a single document vector at any point. The
connectome (`malecns_wifi.token_reservoir.PositionalReservoir`), its frozen
sensory-input weights, and its frozen sparse readout projection are
**identical in construction** to the MultiEURLEX document encoder
(`document_reservoir.py`): row-normalised operator, same gain/leak/target-RMS
defaults, same seeded fixed projections. Only the *time axis* changes -- token
positions instead of up to four sampled text windows -- and the readout is
taken after every step instead of only the last.

Frozen encoders: the same pair as MultiEURLEX --
`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` and
`intfloat/multilingual-e5-small` -- for continuity across the research
programme, even though Few-NERD is English-only and a monolingual encoder
would also be a legitimate choice.

**Preregistered deviation from the document pipeline**: E5's
`"query: "`/`"passage: "` prefix convention has no defined per-token alignment
(it is a pooled-sentence-embedding instruction), so it is **not** applied when
extracting per-token hidden states. This changes what the frozen encoder is
asked to compute, not any label, split, or downstream decision.

## What is frozen vs. what is fit

- Frozen, never sees labels: both semantic encoders, the sensory projection,
  the connectome operator, the sparse whole-brain readout.
- The **only** supervised component is a linear probe (multinomial logistic
  regression) from the 256-d per-token readout to the 66-way fine label,
  fit on `train`. This is the token-classification analogue of the k-NN
  classifier the MTEB evaluator fits on top of a frozen sentence encoder for
  document classification -- not a claim that the encoder itself is
  supervised.
- Regularisation strength (`C`) is selected by accuracy on `validation` only.
  `test` labels never influence probe fitting, model selection, the
  connectome, or any hyperparameter (gain/leak/target-RMS/readout width).

## Metrics

- Primary: entity-level micro-F1 (seqeval, IO->BIO converted as above),
  following Few-NERD's own evaluation convention.
- Secondary: entity-level macro-F1, per-entity-type P/R/F1, raw token
  accuracy (context only -- token accuracy on a 66-way, heavily `O`-skewed
  label space is not comparable to span F1 and must not be reported as if it
  were the headline number).
- Validation accuracy of the probe is recorded for provenance, not compared
  across variants as a benchmark result.

## Comparable controls (same tokens, same encoders, no MaleCNS)

Mirroring the MultiEURLEX label-free controls, sharing the exact fused
per-token inputs:

- `sensory-only`: the same reservoir with the recurrent operator switched off
  (`gain = 0`) -- sensory projection + leaky tanh + readout, no topology.
- `fused-mean-proj` / raw fused vector: the per-token fused MiniLM/E5 vector
  (optionally projected to 256-d by the same fixed seeded projection) fed
  straight to the identical probe, with no reservoir step at all.

These isolate what the recurrent connectome adds on top of (a) the frozen
encoders alone and (b) the projection scaffolding without the topology --
exactly the question the whole-brain reservoir experiments have been asking
for MultiEURLEX, now on a task the architecture was actually built for.

## Engineering metrics to record

tokens/s, sentences/s, MiniLM/E5 seconds, reservoir forward seconds, SpMM call
count, peak RAM/VRAM, cache size, probe fit seconds -- same discipline as
`multieurlex21-throughput.md`. Stage A/B/C split so the semantic cache is
computed once and reused by the probe, the controls, and any later ablation
(random graph, shuffled weights, binary topology) without repaying MiniLM/E5.

## First execution

A smoke run may use a deterministic prefix of the official splits solely to
validate I/O, shapes, and metric code; smoke numbers are not benchmark
evidence and must be labelled `claim_status: pipeline smoke only`. The first
benchmark-evidence run uses the full official splits.

## Scientific hygiene

- No tuning against test labels, ever.
- No changes to labels, tag scheme, or split membership.
- Store predictions, probe hyperparameters, metrics, timing, dataset revision,
  code commit, and executor provenance for every run.
- `intra`/`inter` few-shot configs and MultiCoNER II require their own
  preregistration before any accelerator time is spent on them.
