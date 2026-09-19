---
type: "Findings Record"
title: "Pontifex RED-1 — learned convergence vs trivial aggregation"
description: "Synthetic held-out ablation harness for testing whether learned multi-space convergence adds signal beyond a single encoder, simple mean, or learned weighted mean."
tags: [pontifex, experiment, interpretability]
timestamp: 2026-09-17T13:05:00-04:00
---

# Pontifex RED-1 — learned convergence vs trivial aggregation

This is the earliest cheap falsification test for the distinctive Pontifex claim.
It does **not** ask whether occlusion works. It asks whether learning convergence
across several independent embedding spaces adds useful signal beyond simpler
aggregation rules.

## Claim under test

> Combining bilateral scalar signals from multiple unaligned frozen encoders with
> a learned convergence head should localize a causally constructed span better
> than simpler single-space or static aggregation baselines.

## Primary quantities

The original experiment tracks

`delta = AUPRC(Pontifex) - max(AUPRC(best single encoder), AUPRC(mean encoder saliency))`.

The diversity study adds the stronger quantity

`delta_interaction = AUPRC(Pontifex) - AUPRC(learned convex weighted mean)`.

There is **no fixed positive-effect cutoff**. A positive delta is interesting when
it reproduces and persists as scale and diversity increase. `delta_interaction`
is specifically intended to separate nonlinear learned convergence from the much
simpler explanation that Pontifex merely learns better static encoder weights.

## Conditions and baselines

| Condition | Signals |
|---|---|
| A | Best individual encoder, chosen using training families only |
| B | Unweighted mean of encoder occlusion saliencies |
| W | Learned convex weighted mean: non-negative encoder weights constrained to sum to one, fit on training data only |
| C | Pontifex nonlinear convergence head over all bilateral scalar signals |
| D | Pontifex with an encoder channel semantically destroyed by permutation |

The convex constraint on W matters: it makes W a genuine learned weighted mean,
not another nonlinear classifier. If C consistently exceeds W, the gain cannot be
explained only by static reweighting of encoder saliencies.

## Dataset layers

`run.py` creates the original 240-example RED-1 set with one causal span known by
construction.

`scale.py` extends the same semantic families to up to 6,144 unique surface
variants and studies sample scale, repeated seeds, and channel corruption.

`diversity.py` holds total N approximately fixed while varying two independent
axes:

- semantic-family count: **12 → 24 → 48 → 96**;
- encoder-bank size: **3 → 5 → 8**.

The 96-family bank is built from 12 semantic variables crossed with eight distinct
sentence frames. Family IDs are held out wholesale, so a family used for test is
not seen by the convergence head during training.

## Encoder diversity bank

The diversity study can use, in order:

1. `sentence-transformers/all-MiniLM-L6-v2`
2. `sentence-transformers/paraphrase-MiniLM-L3-v2`
3. `BAAI/bge-small-en-v1.5`
4. `intfloat/e5-small-v2`
5. `sentence-transformers/all-mpnet-base-v2`
6. `sentence-transformers/multi-qa-MiniLM-L6-cos-v1`
7. `intfloat/multilingual-e5-small`
8. `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

The purpose is not merely to increase K, but to test whether the benefit changes
as the representation bank becomes less redundant.

## MS MARCO sampled feature stores

For large prebuilt Pyserini indexes, the project now uses a fixed sampled-PID
workflow instead of trying to materialize an entire 8.8M-passage embedding bank in
RAM.

`sample_manifest.py` defines a deterministic, encoder-independent sample over the
8,841,823 MS MARCO Passage v1 PIDs using a full-cycle modular walk. The sample is
specified by `start`, `step`, corpus size, and a SHA-256 of the ordered PID list.
This guarantees that TCT-ColBERT, BGE, ANCE, and later encoders extract **the same
PID sequence** without relying on internal FAISS ordering or RNG state.

`extract_sample_store.py` then:

1. downloads a Pyserini prebuilt FAISS artifact;
2. scans its companion `docid` file to resolve the real internal position of every sampled PID;
3. opens the full FAISS index read-only via mmap;
4. reconstructs only the sampled vectors;
5. writes a compact `.npz` containing `pids`, `positions`, and `embeddings`, plus JSON provenance metadata.

The intended ladder is:

- **1k PIDs** — automatic smoke/provenance check;
- **10k PIDs** — default research sample;
- **100k PIDs** — first larger stability study after the multi-encoder extraction path is proven.

For a 768-dimensional float32 encoder, 10k raw vectors are only about 30.7 MB
before compression, so even an 8-encoder bank remains easy to manipulate after
one-time extraction from the large source indexes.

The workflow `Pontifex sampled feature store` runs 1k automatically on PR changes
and exposes 10k (or another size) through `workflow_dispatch`. Its default source
is the official `msmarco-v1-passage.tct_colbert-v2-hnp` Pyserini FAISS index.

## Features

For each candidate span and each encoder, the synthetic harness computes only
within-space cosine similarities:

1. original vs span-masked sentence;
2. left context vs original;
3. right context vs original.

No embedding from one encoder is aligned to or directly compared with another.
The convergence head only receives scalar within-space signals.

## Endpoints

Primary: macro AUPRC computed **per sentence** and then averaged.

Secondary:

- precision@1;
- normalized saliency mass on the causal span;
- delta under partial or complete channel corruption;
- `delta_interaction = C - W`;
- fraction of seeds with positive delta and positive interaction delta;
- p10/p90 of the interaction effect across seeds.

## Run

Original RED-1:

```bash
uv run experiments/pontifex_red1/run.py \
  --examples 240 \
  --seeds 0 1 2 \
  --output pontifex-red1-result.json
```

Sample-scale study:

```bash
uv run experiments/pontifex_red1/scale.py \
  --sizes 100 300 1000 3000 \
  --seeds 0 1 2 3 4 5 6 7 8 9 \
  --corruption 0 0.25 0.5 1 \
  --output pontifex-scale.json
```

Full diversity study:

```bash
uv run experiments/pontifex_red1/diversity.py \
  --examples 1920 \
  --families 12 24 48 96 \
  --encoder-counts 3 5 8 \
  --seeds 0 1 2 3 4 5 6 7 8 9 \
  --output pontifex-diversity.json
```

Create a fixed 10k PID manifest:

```bash
uv run experiments/pontifex_red1/sample_manifest.py \
  --size 10000 \
  --output msmarco-sample-10k.json
```

Extract the same 10k PIDs from a prebuilt TCT-ColBERT index:

```bash
uv run experiments/pontifex_red1/extract_sample_store.py \
  --index msmarco-v1-passage.tct_colbert-v2-hnp \
  --size 10000 \
  --output msmarco-tct-sample-10k.npz
```

The GitHub workflow `Pontifex diversity study` runs a small smoke configuration
on PR changes and exposes the complete 12/24/48/96 × 3/5/8 experiment through
`workflow_dispatch` in `full` mode.

## Interpretation

The first 240-example run produced median held-out delta of approximately
**+0.030 AUPRC** across three seeds, with high variance. That is a positive signal
worth scaling, not a pass/fail verdict.

Evidence against the distinctive claim would be a pattern in which delta tends
toward zero or negative values as data, semantic diversity, and statistical power
increase. More specifically, if C and W converge to the same performance as
family and encoder diversity grow, the learned convergence head is probably
acting mainly as a static weighting mechanism.

The stronger positive pattern is persistent `delta_interaction > 0`, especially
if its uncertainty shrinks or its magnitude grows as semantic families and
encoder diversity increase. That would support the more distinctive claim that
Pontifex exploits interactions among unaligned representation spaces rather than
merely averaging them more intelligently.

See `INTERPRETATION.md` for the explicit interpretation rule.