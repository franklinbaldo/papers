# Pontifex RED-1 — learned convergence vs trivial aggregation

This is the earliest cheap falsification test for the distinctive Pontifex claim.
It does **not** ask whether occlusion works. It asks whether learning convergence
across several independent embedding spaces adds useful signal beyond a single
encoder or an unweighted average.

## Claim under test

> Combining bilateral scalar signals from multiple unaligned frozen encoders with
> a learned convergence head should localize a causally constructed span better
> than either the best single encoder or a simple mean of encoder saliencies.

### Preregistered H1

On held-out template families, condition **C** must improve macro AUPRC by at
least **0.05 absolute** over `max(A, B)`.

The aggregate result is considered to survive RED-1 only when:

1. the median `C - max(A,B)` margin is at least +0.05;
2. at least half of the preregistered seeds meet +0.05; and
3. no seed has a negative margin.

Failure is a scientific result, not a CI failure.

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

`run.py` creates 240 short synthetic sentences by default (the registered range
is 100–300). Each sentence has exactly one span whose experimental variable is
known by construction. Examples include animal identity, sentiment, direction,
truth value, urgency, safety, quantity, permission, intent, spatial relation,
and indicator colour.

Candidate spans are ordinary word spans. The causal span is labelled positive;
all other spans in the same sentence are negatives.

The train/test split is by **template family**, not by sentence, so near-duplicate
phrasing from the same family cannot cross the boundary.

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

Primary: macro AUPRC computed **per sentence** and then averaged. With one known
causal span per sentence, this is directly sensitive to the rank of that span.

Secondary:

- precision@1;
- normalized saliency mass on the causal span.

## Run

The file is a PEP 723 script, so the intended command is:

```bash
uv run experiments/pontifex_red1/run.py \
  --examples 240 \
  --seeds 0 1 2 \
  --output pontifex-red1-result.json
```

It writes JSON plus a compact Markdown table next to it.

## Interpretation

- `C > B >= A` with the preregistered +5 pp margin: the learned multi-space
  convergence claim survives this first cheap RED gate.
- `C ≈ B`: the convergence head has not justified its complexity; Phase 2 should
  stop or be redesigned before multimodality.
- `C < A`: the multi-space combination is actively harmful on this test.
- `D ≈ C` despite a destroyed third channel: either the head successfully ignores
  the bad channel or encoder 3 contributed little; inspect the test-only
  corruption diagnostic and learned behaviour before claiming robustness.
- test-only corruption improves C: treat that as an artifact/leakage warning.

This experiment is intentionally narrower than the full Pontifex paper. It is a
kill-switch for the most distinctive Phase-2 claim, not a validation of the whole
architecture.
