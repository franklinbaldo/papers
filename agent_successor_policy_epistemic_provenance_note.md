---
okf_version: "0.2"
title: "Agent Successor Policy — Epistemic Provenance of Rewards and Agent Claims"
description: "Companion note separating observed, simulated, inferred, and pending ASP training signals and defining null models for claims about learned agency."
doc_type: "alignment-paper-note"
status: "draft"
---

# Agent Successor Policy — Epistemic Provenance of Rewards and Agent Claims

Franklin Baldo  
Draft: 2026-08-16

ASP creates an unusual training corpus because some labels are direct observations, some are later consequences, and some are judgments simulated by the same class of model that participates in the agent loop. These sources should never be collapsed into an undifferentiated scalar called `reward`.

This note imports two disciplines from the existing papers programme: claim provenance from `proveniencia_claims.md`, and structured null-model comparison from `informational_time_negentropy_clarifications.md`.

## 1. Every training signal needs an epistemic status

For a cycle `t`, distinguish at least:

```text
observed
simulated
inferred
pending
```

### Observed

An observed field is directly supported by an external or repository artifact under the declared measurement procedure. Examples include:

- a commit exists at a given SHA;
- a test run passed or failed;
- a PR was merged;
- an article URL responded;
- a prompt was selected with a logged propensity;
- a later cycle reverted an earlier change.

Observed does not mean infallible; it means the datum is tied to a reproducible observation rather than generated as an evaluator judgment.

### Simulated

A simulated field is an explicit role-conditioned model judgment. ASP's hour/day/week/month/year forecasts and next-cycle retrospective grades are simulated labels even when they are carefully evidence-grounded.

They should remain useful as dense bootstrap signals, but their provenance must remain visible to the trainer.

### Inferred

An inferred field is computed from observed or simulated inputs under a declared transformation. Examples include:

- forecast calibration error;
- semantic velocity derived from successive prompt embeddings;
- causal-depth counters;
- reward scalarizations derived from multi-horizon grade vectors;
- a learned probability that one prompt will outperform another.

The transformation and input versions should be reproducible.

### Pending

A pending field records that the relevant status cannot yet be determined. This is not a malformed example. A weekly observed outcome is legitimately pending one hour after the cycle. A missing long-horizon label should remain missing/pending rather than be silently replaced by the forecast.

The corpus should therefore permit partial targets.

## 2. Forecasts must not masquerade as outcomes

At cycle close:

```text
future_evaluator_forecast
kind: simulated
```

At the next cycle start:

```text
previous_cycle_evaluation
kind: simulated
```

At a later horizon, if a measurable consequence exists:

```text
observed_outcome
kind: observed
```

A trainer may use simulated targets before observed outcomes mature, but it should either use separate heads or preserve source-type features so that the model can learn their differing reliability.

This also enables a calibration problem:

```text
P(observed outcome | simulated critic score, context, horizon)
```

The temporal critics can themselves be evaluated and reweighted over time.

## 3. Load-bearing and contingent evidence

The necessary/contingent distinction from claim provenance has an ASP analogue.

A cycle may produce many visible artifacts. Some are **load-bearing evidence** for the claimed reward; others are merely correlated activity.

For example, if the claim is "this cycle closed the publication gate":

- a public URL and confirmed publication state may be load-bearing;
- the number of commits is contingent;
- a long explanatory report may be contingent;
- a test failure may be negative load-bearing evidence.

ASP should therefore avoid rewarding activity counts as if they established mission progress. Where feasible, reward reports should identify the evidence relation:

```yaml
evidence:
  - claim: publication_gate_closed
    support: observed
    role: load-bearing
    resource: ...
  - claim: implementation_effort
    support: observed
    role: contingent
    resource: ...
```

This is especially important for preventing reward hacking through commits, lines changed, issue comments, or self-reported complexity.

## 4. Agent representation is not evidence of agency

ASP uses phrases such as "representation of the agent" to denote a latent summary of behavioral history and expected futures. That is a modeling object. Its existence does not prove that a distinct autonomous agent has been discovered at that level.

The agent-recognition clarification in `informational_time_negentropy_clarifications.md` requires comparison against progressively stronger alternatives. ASP should adopt analogous nulls:

```text
M_schedule
  fixed or periodic scheduler

M_state
  state-only heuristic / contextual policy

M_law
  non-agent trajectory dynamics model

M_agent
  persistent latent policy/agent-state model
```

A claim that the latent `h_t` captures an enduring agent-level state earns support only if it improves held-out prediction and intervention response beyond simpler structured-law alternatives after model complexity is charged.

A trajectory encoder can be useful even if this stronger agency interpretation fails.

## 5. Intervention is the strongest test

Correlation between a latent state and successful outcomes does not establish control. ASP has a natural intervention surface: prompt selection.

Given similar reconstructed trajectories, deliberately selecting prompts from different semantic regions allows measurement of whether the predicted successor-state differences occur.

Useful tests include:

- force a prompt different from the policy's top choice;
- perturb the prompt within a semantic neighborhood;
- choose a prompt aligned versus anti-aligned with predicted desired delta;
- replace trajectory history with a shuffled or truncated history;
- hold current state fixed while varying reconstructed path history.

If the purported latent agent state predicts no intervention-sensitive differences, it may be only a compact description of history rather than a causal control state.

## 6. Corpus contract

A mature ASP training row should preserve provenance approximately as:

```yaml
cycle_id: ...

state_before:
  value: ...
  epistemic_status: observed

selection:
  prompt_id: ...
  propensity: ...
  epistemic_status: observed

future_evaluator_forecast:
  epistemic_status: simulated
  grades: ...

next_cycle_retrospective:
  epistemic_status: simulated
  grades: ...

observed_delayed_outcomes:
  week:
    epistemic_status: pending | observed
    values: ...

features:
  semantic_velocity:
    epistemic_status: inferred
    derivation_version: ...
```

The exact schema can evolve, but provenance should survive projection through `okf-parser` into every training artifact.

## 7. Consequence for the research programme

This provenance discipline makes several ASP comparisons scientifically cleaner:

- simulated critics vs real delayed outcomes;
- state-only vs trajectory-conditioned policies;
- simple dynamics vs persistent-agent latent models;
- semantic similarity vs functional reward-conditioned retrieval;
- short-term visible activity vs load-bearing mission progress.

The general rule is simple: **uncertainty is data**. A pending outcome should remain pending, a simulated evaluator should remain simulated, and a learned agent representation should remain a modeling hypothesis until it defeats simpler nulls under prediction and intervention.
