---
type: "Findings Record"
title: "Pontifex RED-1 — learned convergence vs trivial aggregation"
description: "Synthetic held-out ablation harness for testing whether learned multi-space convergence adds signal beyond a single encoder or simple mean."
tags: [pontifex, experiment, interpretability]
timestamp: 2026-09-17T13:05:00-04:00
---

# Pontifex RED-1 — learned convergence vs trivial aggregation

This is the earliest cheap falsification test for the distinctive Pontifex claim.
It does **not** ask whether occlusion works. It asks whether learning convergence
across several independent embedding spaces adds useful signal beyond a single
encoder or an unweighted average.

## Claim under test

> Combining bilateral scalar signals from multiple unaligned frozen encoders with
> a learned convergence head should localize a causally constructed span better
> than either the best single encoder or a simple mean of encoder saliencies.

## Primary quantity

The experiment tracks

`delta = AUPRC(Pontifex) - max(AUPRC(best single encoder), AUPRC(mean encoder saliency))`.

There is **no fixed positive-effect cutoff**. A positive delta is interesting when
it reproduces and persists as scale and diversity increase. The scientific target
is therefore the trajectory and stability of delta, not whether one toy run
crosses an arbitrary threshold.

## Conditions

| Condition | Signals |
|---|---|
| A | Best individual encoder, chosen using training families only |
| B | Mean occlusion saliency of all 3 encoders |
| C | Pontifex convergence head over 9 scalar bilateral signals (3 × 3) |
| D | Same head class, but encoder 3 is semantically destroyed by permutation in train and held-out data |

A fifth diagnostic corrupts encoder 3 **only at test time** for the clean C head.
It is meant to expose heads that appear to gain while actually exploiting a
fragile dataset/channel artifact.

## Dataset

`run.py` creates 240 short synthetic sentences by default. Each sentence has
exactly one span whose experimental variable is known by construction. Examples
include animal identity, sentiment, direction, truth value, urgency, safety,
quantity, permission, intent, spatial relation, and indicator colour.

Candidate spans are ordinary word spans. The causal span is labelled positive;
all other spans in the same sentence are negatives.

The train/test split is by **template family**, not by sentence, so phrasing from
the same semantic family cannot cross the boundary.

`scale.py` extends the same test to up to 6,144 unique surface variants and is
used to study how delta behaves as the number of examples, seeds, and corrupted
channels increase. This is a sample-scale study; semantic-family, language, and
encoder-bank diversity are separate follow-up axes.

## Features

Three frozen encoders are used:

- `sentence-transformers/all-MiniLM-L6-v2`
- `sentence-transformers/paraphrase-MiniLM-L3-v2`
- `BAAI/bge-small-en-v1.5`

For each candidate span and each encoder, the harness computes only within-space
cosine similarities:

1. original vs span-masked sentence;
2. left context vs original;
3. right context vs original.

No embedding from one encoder is aligned to or directly compared with another
encoder. The learned head only receives the resulting nine scalar signals.

## Endpoints

Primary: macro AUPRC computed **per sentence** and then averaged.

Secondary:

- precision@1;
- normalized saliency mass on the causal span;
- delta under partial or complete corruption of encoder channel 3.

## Run

```bash
uv run experiments/pontifex_red1/run.py \
  --examples 240 \
  --seeds 0 1 2 \
  --output pontifex-red1-result.json
```

Scaling study:

```bash
uv run experiments/pontifex_red1/scale.py \
  --sizes 100 300 1000 3000 \
  --seeds 0 1 2 3 4 5 6 7 8 9 \
  --corruption 0 0.25 0.5 1 \
  --output pontifex-scale.json
```

## Interpretation

The first 240-example run produced median held-out delta of approximately
**+0.030 AUPRC** across three seeds, with high variance. That is a positive signal
worth scaling, not a pass/fail verdict.

Evidence against the distinctive claim would be a pattern in which delta tends
toward zero or negative values as data, semantic diversity, and statistical power
increase. Evidence for the claim would be persistent positive delta, especially if
uncertainty shrinks or the effect grows as the representation bank becomes more
diverse.

See `INTERPRETATION.md` for the explicit interpretation rule.
