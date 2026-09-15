---
type: "Protocol"
title: "Preregistration — MaleCNS × Few-NERD NER"
description: "Preregistered protocol for evaluating the complete MaleCNS method on fine-grained token/span-level Few-NERD named-entity recognition."
tags: [malecns, few-nerd, ner, preregistration]
timestamp: 2026-09-15T18:00:00Z
---

# Preregistration — MaleCNS × Few-NERD NER

Date: 2026-09-15

## Question

Can the MaleCNS method perform token/span-level named-entity recognition on a consolidated public benchmark, preserving the original positional/localisation objective rather than document-level classification?

## Benchmark

Primary dataset: Few-NERD.

Primary stage: supervised Few-NERD benchmark using the official train/dev/test split and the published fine-grained entity labels. Follow-up stages may use Few-NERD INTRA/INTER few-shot splits, but those are separate experiments and must not be used to tune the primary test result.

## Task

Input: text/tokens.
Output: token/span-level entity prediction with entity type.

The implementation must preserve positional predictions. It must not collapse the whole document/sentence to one global label.

## Method under test

The method is evaluated as a whole system:

text/tokens -> frozen semantic channels (MiniLM/E5, potentially multiscale) -> positional MaleCNS dynamics -> positional readout/decoder -> entity spans/types.

MiniLM/E5 are part of the method, not contaminants to subtract from the headline result.

The MaleCNS connectome is not being evaluated in isolation. Mechanistic ablations (binary/shuffled/quantised/random graph, channel removals, etc.) are secondary analyses.

## Primary metrics

- entity-level micro-F1 using exact span + type match
- entity-level precision
- entity-level recall

If the official Few-NERD evaluation exposes additional macro/fine-grained metrics, record them unchanged.

## Scientific constraints

- Preserve official data splits and label ontology.
- Do not tune on the test split.
- Hyperparameter/budget selection must use train/dev only.
- Record hardware, wall time, peak RAM/VRAM, embedding time, MaleCNS time, and decoder/evaluation time separately.
- Cache semantic embeddings with provenance so repeated MaleCNS runs do not repay encoder cost.
- Embedding generation may be parallelised because documents/sentences/chunks are independent before MaleCNS consumption.
- Report both cold-run cost (including embeddings) and warm-run cost (cached embeddings).

## First milestone

Pipeline smoke on a small train/dev slice that proves:

1. dataset loading and official label mapping;
2. exact token/span alignment;
3. semantic channel cache;
4. MaleCNS positional forward pass;
5. decoding back to entity spans/types;
6. official-style entity F1 computation.

Smoke numbers are not benchmark evidence.

## Evidence run

After the smoke passes, run the full official supervised split with the protocol frozen. The first full test evaluation is the primary benchmark result.

## Later stress tests

After the primary result, training-budget saturation may be explored on train/dev using increasing budgets (for example 1x, 2x, 4x, 8x, 16x) and only then frozen for a fresh test evaluation.

## Interpretation

Primary claim: performance/efficiency of the complete MaleCNS NER method.

Secondary claims: contribution of connectome topology/weights, semantic channels, state-conditioned plasticity, and other components via preregistered ablations.
