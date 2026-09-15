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
  (mark the first byte of a run `B-`, the rest `I-`) is bookkeeping for the metric
  library, not a change to any label or prediction; see "Metric" below.

## Architecture (positional, byte-synchronised)

This programme already has an established convention for feeding text to
MaleCNS positionally: `text_axis_channels.py`, used by the flavour/food/wifi
experiments. The first draft of this protocol proposed per-token hidden
states from a HF tokenizer instead -- a different, ad hoc representation with
no place in the rest of the programme -- and was corrected before any
benchmark-evidence run. The channel construction below is that established
convention, not a new one:

```
sentence text (word-joined) -> UTF-8 byte axis
   -> for each scale in the power-of-two ladder {1, 2, 4, 8, ..., 2048} chars:
      overlapping windows, pooled by a frozen encoder, interpolated to every
      byte position (text_axis_channels.window_spans / interpolate_to_bytes)
   -> unit-normalised per (model, scale), concatenated -> fused byte channel
   -> fixed Gaussian sensory projection (RMS-normalised per byte)
   -> row-normalised MaleCNS recurrent step (gain, leak, tanh) -- one step per BYTE
   -> fixed sparse whole-brain readout emitted at EVERY byte position
   -> 256-d embedding per byte
```

No pooling of the sequence into a single document vector at any point, and no
tokenizer subword alignment anywhere. The connectome
(`malecns_wifi.token_reservoir.PositionalReservoir`), its frozen sensory-input
weights, and its frozen sparse readout projection are **identical in
construction** to the MultiEURLEX document encoder (`document_reservoir.py`):
row-normalised operator, same gain/leak/target-RMS defaults, same seeded fixed
projections. Only the *time axis* changes -- one step per UTF-8 byte instead
of up to four sampled text windows -- and the readout is taken after every
step instead of only the last.

Scale ladder decided 2026-09-15: `2**i` for `i` in `0..11` (1, 2, 4, 8, 16, 32,
64, 128, 256, 512, 1024, 2048 characters) -- a full geometric sweep from
single-character to whole-sentence context, rather than the 3-point ladder
(`{8, 32, 128}`) other experiments in this programme use. Scales at or above a
sentence's byte length collapse to one whole-sentence window
(`window_spans`'s `n <= scale` branch), so the ladder saturates gracefully
instead of erroring; per-scale channel count is fixed regardless of sentence
length.

Frozen encoders: the same pair as MultiEURLEX --
`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` and
`intfloat/multilingual-e5-small` -- for continuity across the research
programme, even though Few-NERD is English-only and a monolingual encoder
would also be a legitimate choice. E5's `"query: "`/`"passage: "` prefix
convention applies exactly as it does for the flavour/food channels: every
pooled window is a "passage", so the `"passage: "` prefix is used, same as
`multieurlex_cache.model_prefix`.

**Preregistered deviation from the document pipeline**: Few-NERD supplies
pre-tokenized words, not raw text, so the sentence is reconstructed as
`" ".join(words)`. Word-level fine/coarse labels are broadcast onto each
word's own byte span (via the same `utf8_byte_axis` used for the channels);
the single-space bytes between words carry label `O`. This is a documented
approximation of the original text and its labels' resolution, not a change to
any label's value.

## What is frozen vs. what is fit

- Frozen, never sees labels: both semantic encoders, the sensory projection,
  the connectome operator, the sparse whole-brain readout.
- The **only** supervised component is a linear probe (multinomial logistic
  regression) from the 256-d per-byte readout to the 66-way fine label,
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
- Secondary: entity-level macro-F1, per-entity-type P/R/F1, raw byte-level
  label accuracy (context only -- byte accuracy on a 66-way, heavily `O`-skewed
  label space is not comparable to span F1 and must not be reported as if it
  were the headline number).
- Validation accuracy of the probe is recorded for provenance, not compared
  across variants as a benchmark result.

## Comparable controls (same byte channels, same encoders, no MaleCNS)

Mirroring the MultiEURLEX label-free controls, sharing the exact fused
per-byte channel inputs:

- `sensory-only`: the same reservoir with the recurrent operator switched off
  (`gain = 0`) -- sensory projection + leaky tanh + readout, no topology.
- `fused-mean-proj` / raw fused vector: the per-byte fused MiniLM/E5 channel
  (optionally projected to 256-d by the same fixed seeded projection) fed
  straight to the identical probe, with no reservoir step at all.

These isolate what the recurrent connectome adds on top of (a) the frozen
encoders alone and (b) the projection scaffolding without the topology --
exactly the question the whole-brain reservoir experiments have been asking
for MultiEURLEX, now on a task the architecture was actually built for.

## Cache storage, corrected 2026-09-15

Persisting the byte-interpolated channel field directly does not scale: on
the full supervised corpus (~25M bytes) it measured at ~860 GB before
compression and OOM'd during construction (74.4M window occurrences held in
memory before any encoding). Measured on the real corpus, window text is
enormously redundant at small scales (scale=1: 17,342x duplicate ratio;
scale=2: 2,356x; scale=4: 50x; scale=8: 2.9x); across all 12 scales combined,
only 7.32M of 74.4M window occurrences are textually unique. The cache
therefore stores each **unique window text once** (16-byte BLAKE2b digest,
model-independent), cutting storage to ~20 GB and encoder calls by ~10x;
stage B recomputes window spans deterministically and looks embeddings up by
hash, assembling the byte-resolution field transiently per sentence batch --
it is never written to disk. This cache is a local intermediate and is not
published to the Hub.

## Engineering metrics to record

bytes/s, sentences/s, MiniLM/E5 seconds, reservoir forward seconds, SpMM call
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
