---
type: "Companion Note"
title: "Reward-Conditioned Retrieval: Minimal Synthetic Experiment"
description: "CPU-only contextual-bandit experiment comparing cosine-only retrieval, naive selection promotion, and reward-conditioned functional keys for relay memory."
tags: [rl-relay-transducers, retrieval, contextual-bandit, associative-memory, experiment]
timestamp: 2026-08-02T14:00:00-04:00
---

# Reward-Conditioned Retrieval: Minimal Synthetic Experiment

This directory contains the smallest experiment that tests the learned-retrieval claim in `rl_relay_transducers.md` without requiring a language model, GPU, vector database, or reinforcement-learning framework.

## Question

Suppose cosine search already retrieves the correct semantic neighborhood, but that neighborhood contains several nearly synonymous chunks and only one of them is functionally useful. Can downstream reward teach a retrieval layer to rank the useful chunk above its semantic siblings?

The experiment compares three methods:

1. **`cosine_only`** — retrieves the semantic top-k and selects the nearest chunk;
2. **`selection_promotion`** — adds a popularity bonus whenever a chunk is selected, regardless of reward;
3. **`reward_conditioned`** — keeps semantic embeddings frozen, learns functional keys and contextual utility from attributed advantage, and freezes learning during evaluation.

The synthetic environment gives every context a group of semantically close chunks. Exactly one sibling is useful. The identity of the useful sibling is independent of nearest-cosine rank. This makes first-stage candidate recall easy while leaving final ranking as the learned problem.

## Run

Requires Python 3.10+ and NumPy.

```bash
python -m pip install -r requirements.txt
python experiment.py \
  --train-episodes 8000 \
  --eval-episodes 2000 \
  --seeds 8 \
  --top-k 4 \
  --output results
```

The command writes:

- `results/runs.csv` — one row per method and seed;
- `results/summary.json` — aggregate metrics and run configuration.

The `results/` directory is ignored because empirical claims should be regenerated from code rather than committed as if they were fixed findings.

## Tests

```bash
python -m unittest -v test_experiment.py
```

The tests check that:

- semantic top-k candidate recall is high;
- reward-conditioned retrieval beats cosine-only retrieval in a deterministic seeded configuration;
- repeated frozen evaluations are reproducible.

## Metrics

- **evaluation reward** — fraction of contexts in which the useful chunk was selected;
- **regret** — one minus evaluation reward, since the oracle reward is one;
- **candidate recall** — fraction of episodes where the useful chunk was present in semantic top-k;
- **selection Gini** — concentration of selected chunks;
- **maximum selection share** — largest share assigned to one chunk.

Candidate recall and final reward are deliberately separate. High candidate recall with low reward means the cosine layer found the right neighborhood but the ranking policy did not identify the useful member.

## Interpretation limits

This is a mechanism test, not evidence that an ART works through real language-model channels. It excludes token generation, multi-hop credit, sequence composition, semantic drift, model-specific survival, and safety policies. Its purpose is to falsify implementation mistakes cheaply before paying for LLM rollouts.

A successful result supports only the narrow claim that reward-conditioned functional ranking can learn among semantically similar memory chunks. The next experiment should replace the deterministic reward with a frozen text transformation or small frozen language model and score whether retrieved chunks survive that channel.
