---
type: companion-note
title: "Event-Sourced Agent Experience: OKF Cycle Reports as the Training Source for Agent Successor Policy"
description: "Companion note replacing a mutable reward ledger with immutable start/end cycle concepts and a parser-derived RL corpus."
status: draft
sources:
  - id: asp
    resource: "agent_successor_policy.md"
    title: "Agent Successor Policy"
---

# Event-Sourced Agent Experience: OKF Cycle Reports as the Training Source for Agent Successor Policy

## Motivation

The initial ASP formulation describes a temporal reward ledger. A stronger implementation is to avoid treating a mutable ledger as the primary memory at all. Each work cycle can instead be represented by two immutable, typed knowledge events: a start report and an end report. The training dataset then becomes a deterministic projection of those reports.

This matters because delayed rewards do not require rewriting the original cycle. The next cycle can express its retrospective judgment of the previous cycle in its own start event. The resulting chain preserves what the agent knew and predicted at each moment.

## Two-event cycle representation

For cycle `t`, define:

```text
S_t = agent-cycle-start
E_t = agent-cycle-end
```

The start report contains the state observed before action and the policy decision:

```text
S_t = {
  cycle_id,
  previous_cycle_id,
  state_before,
  previous_cycle_evaluation,
  forecast_calibration,
  selected_strategy,
  selected_prompt
}
```

The end report contains the transition outcome and forecast:

```text
E_t = {
  cycle_id,
  state_after,
  action,
  evidence,
  next_gate,
  future_evaluator_forecast
}
```

`E_t` references `S_t`. The delayed evaluation of cycle `t` is written in `S_{t+1}` through `previous_cycle_id = t` and `previous_cycle_evaluation`.

Thus the reward history is append-only:

```text
S_t → E_t → S_t+1 → E_t+1 → ...
```

No later evaluator edits `E_t` merely because more information became available.

## Forecast and delayed label

At close, cycle `t` predicts future judgments:

```text
F_t[h] = (importance, quality, rationale)
```

At the beginning of cycle `t+1`, the temporally situated evaluators reassess `t`:

```text
G_t+1[h] = (importance', quality', rationale')
```

The pair `(F_t, G_t+1)` yields a calibration signal while preserving both historical viewpoints. Longer-delay observed outcomes can be represented by later typed evaluation events if needed, without modifying the original cycle reports.

## Parser-derived corpus

The reports are ordinary typed OKF Markdown concepts. An OKF parser can discover them, project their frontmatter into relational records, and construct training transitions by joining:

```text
agent-cycle-start.cycle_id = agent-cycle-end.cycle_id
```

and delayed labels by joining:

```text
agent-cycle-start.previous_cycle_id = prior_cycle.cycle_id
```

The training row is therefore derived rather than authored:

```text
(state_before,
 prompt,
 strategy,
 action,
 state_after,
 evidence,
 forecast,
 retrospective,
 calibration,
 multi_horizon_value)
```

This separation has three benefits.

First, the raw experience is human-readable and versioned with the project. Second, model-specific datasets can be regenerated as learning methods change. Third, policy checkpoints remain disposable artifacts rather than acquiring accidental authority over the history from which they were trained.

## Artifact hierarchy

The persistence hierarchy becomes:

```text
immutable OKF cycle reports        authoritative experience
            ↓ parser
training corpus                    derived dataset
            ↓ trainer
policy weights / model checkpoint  derived model
            ↓ runner
artifact storage                   distribution/cache
```

This makes GitHub artifacts a natural location for model weights without using them as the canonical history. If an artifact expires, the reports can regenerate the corpus and retrain the model.

## Implication for successor policies

For successor-style learning, this event-sourced representation is especially useful because it preserves both the pre-action state and the post-action state, as well as temporally delayed judgments. An encoder can learn from the sequence of immutable cycle events rather than from a single repeatedly edited record.

The conceptual ASP object is therefore better understood not as a mutable reward ledger but as an **append-only trajectory of typed agent experience**, from which reward tensors, calibration signals, embeddings, successor representations, and policy weights are projected.
