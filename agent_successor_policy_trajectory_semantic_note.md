---
okf_version: "0.2"
title: "Agent Successor Policy — Trajectory-Conditioned Continuous Behavior and OKF Prompt Retrieval"
description: "Companion note formalizing ASP as a trajectory-conditioned policy whose output is a point in semantic prompt space and whose discrete actions are retrieved from an evolving OKF prompt catalog."
doc_type: "research-note"
status: "draft"
---

# Agent Successor Policy — Trajectory-Conditioned Continuous Behavior and OKF Prompt Retrieval

Franklin Baldo  
Draft: 2026-08-16

## 1. From state-conditioned prompt choice to trajectory-conditioned behavior

A recurring autonomous agent should not choose its next behavioral prompt from the current project state alone. Two agents can occupy superficially similar states while having arrived there through very different sequences of prior prompts, interventions, successes, failures, and delayed rewards. Those histories change what should happen next.

Let one completed cycle be represented as:

```text
x_t = (s_t, p_t, a_t, s_{t+1}, R_t, C_t)
```

where `s_t` is the reconstructed state, `p_t` the behavioral prompt, `a_t` the concrete work performed, `s_{t+1}` the successor state, `R_t` the multi-horizon evaluation tensor, and `C_t` calibration or uncertainty metadata. The policy input is the trajectory prefix:

```text
tau_t = (x_0, x_1, ..., x_{t-1}, s_t)
```

The central refinement is therefore:

```text
policy = pi(tau_t)
```

rather than:

```text
policy = pi(s_t)
```

The policy is **trajectory-conditioned, not merely state-conditioned**.

This matters because sequences themselves carry information. Repeated implementation prompts followed by diminishing weekly value may signal that the agent should move toward verification or falsification. A similar current state reached after successful falsification and correction may justify continued exploitation. The sequence of behaviors and their outcomes is therefore part of the learned internal state of the agent.

## 2. The policy predicts a point, not a prompt ID

ASP should not require the RL model to classify directly among a fixed set of prompt identifiers. Instead, prompts are embedded by a semantic model into a continuous behavioral space:

```text
E_p(p) -> z_p in R^d
```

The trajectory encoder produces a latent representation:

```text
h_t = T(tau_t)
```

and the policy head predicts a desired behavioral point:

```text
z_hat_t = pi_theta(h_t)
```

The discrete prompt actually executed is obtained by semantic retrieval from a catalog `P`:

```text
p*_t = argmax_{p in P} sim(z_hat_t, E_p(p))
```

or equivalently by minimizing a distance metric in embedding space.

This changes the nature of the action space. ASP becomes a **continuous behavioral policy with discrete semantic retrieval**. The neural or statistical model learns where in behavior space the next action should lie; the catalog determines which currently available instruction best realizes that intention.

## 3. The prompt catalog as an OKF bundle

The prompt catalog itself should be an Open Knowledge Format bundle. Each prompt is a typed concept, for example:

```yaml
---
type: agent-prompt
prompt_id: falsify-live-boundary-v3
generator: mutation
intent: "Probe the cheapest live falsifier before adding implementation."
prompt: >
  Attempt the least expensive live test that could falsify the current plan...
tags:
  - falsification
  - live-boundary
---
```

The catalog is versioned knowledge; its embedding index is a derived projection. This distinction permits auditability and evolution. The authoritative prompt is Markdown/OKF. The vector is reproducible metadata bound to an `embedding_model_id`, model revision, dimension, and bundle digest.

Adding a new prompt does not require retraining a classifier head with a new output dimension. The new prompt is simply embedded and inserted into the retrieval index. If its vector lies closer to the behavioral point predicted by the policy than existing prompts, it can immediately become selectable.

This is one of the principal advantages of continuous behavioral prediction over categorical prompt selection.

## 4. Sparse regions become prompt-generation signals

A policy prediction may consistently land far from every existing prompt:

```text
min_p distance(z_hat_t, z_p) > delta
```

This should not necessarily be interpreted as policy failure. It can indicate that the catalog lacks a behavioral instruction corresponding to a useful region of the learned space.

The distance to the nearest catalog item can therefore become a signal to prompt generators. A mutation, composition, LLM generator, or human process may propose new prompt concepts intended to occupy that region. The candidate enters the OKF bundle, receives an embedding, competes with existing prompts, and accumulates trajectory evidence.

The prompt catalog consequently becomes evolutionary:

```text
trajectory policy predicts desired region
        ↓
nearest catalog prompt sufficiently close?
   yes ───────────────→ execute
   no
    ↓
prompt generator proposes candidate
    ↓
new OKF prompt concept
    ↓
embedding + evaluation
    ↓
future retrieval competition
```

Prompt generation and prompt selection are therefore coupled without being conflated.

## 5. Encoding the whole prompt/result chain

The trajectory encoder must represent not only prior prompts but what those prompts produced. A cycle token can contain at least:

```text
E_state(s_t)
E_prompt(p_t)
E_state(s_{t+1})
R_t[hour, day, week, month, year]
forecast calibration
selection propensity
retrieval distance
validation/outcome features
```

A causal sequence model may then compute:

```text
h_t = TrajectoryEncoder(token_0, ..., token_{t-1}, E_state(s_t))
```

Early implementations need not train a large Transformer. With only approximately one new datapoint per hour, a data-efficient baseline can aggregate the entire chain with recency weights or retrieve semantically similar historical trajectory prefixes. The important architectural invariant is that the model's input remains the trajectory, so the statistical learner can later be replaced without changing the event schema.

Long trajectories can eventually use hierarchical memory:

```text
recent cycles → high-resolution causal attention
older cycles  → compressed prototypes / episodic retrieval / sufficient statistics
```

The distinction is analogous to episodic, semantic, and policy memory:

- **episodic memory**: concrete cycle sequences;
- **semantic memory**: recurring state and trajectory prototypes;
- **policy memory**: which behavioral regions performed well under which histories.

## 6. Training targets in prompt space

For a historical trajectory prefix `tau_t`, the executed prompt supplies a known prompt embedding `z_{p_t}` and later evaluations supply value evidence. Training can therefore treat good outcomes as attraction toward the executed prompt region and poor outcomes as weak or negative evidence.

A simple positive objective is:

```text
L_pos = w(R_t) * d(pi_theta(tau_t), E_p(p_t))
```

where `w(R_t)` is derived from the preserved multi-horizon value vector rather than necessarily from a single scalar.

Contrastive learning can distinguish prompts that led to better futures in comparable trajectories:

```text
L_contrastive = max(
  0,
  margin + sim(z_hat, z_negative) - sim(z_hat, z_positive)
)
```

The key target is a **region of semantic behavior space**, not the name of a prompt class.

A successor-style model can go further. It can first predict desirable future-state features and then infer the behavioral region expected to produce them:

```text
tau_t
  ↓
expected successor representation
  ↓
desired behavior vector z_hat_t
  ↓
semantic retrieval
```

This preserves the original ASP interpretation: choose the kind of behavior associated with better futures.

## 7. Propensity and retrieval telemetry

Because retrieval converts a continuous prediction into a discrete action, the start-of-cycle report should preserve the decision boundary, not only the winning prompt. A useful machine-readable record contains:

```yaml
selection:
  policy_version: ...
  model_type: ...
  embedding_model_id: ...
  history_cycles: 127
  predicted_prompt_vector: [...]
  prompt_id: verify-live-boundary
  probability: 0.23
  candidate_policy:
    verify-live-boundary: 0.23
    falsify-current-plan: 0.21
    exploit-next-gate: 0.19
  retrieval:
    - prompt_id: verify-live-boundary
      cosine_similarity: 0.91
    - prompt_id: falsify-current-plan
      cosine_similarity: 0.88
```

This information supports off-policy evaluation, calibration, catalog-gap analysis, and debugging of whether failures arose from trajectory representation, vector prediction, or discretization.

Human overrides should be explicitly marked and excluded from claims about the stochastic policy that did not actually make the choice.

## 8. Combining parallel agents in semantic behavior space

The continuous prompt representation adds another fusion mechanism to the population architecture described in the main ASP paper. Suppose agents `A` and `B` observe the same trajectory but predict different desired behavior vectors:

```text
z_A = pi_A(tau)
z_B = pi_B(tau)
```

A contextual gate can combine intentions directly:

```text
z_AB = alpha(tau) z_A + (1 - alpha(tau)) z_B
```

Retrieval then finds the catalog prompt nearest to `z_AB`.

This can be preferable to merging neural parameters. It permits agents with different internal models to contribute compatible behavioral intentions as long as they share the same semantic prompt space. Horizon-specific gates may also generate a combined vector from agents specializing in short- and long-term futures.

Thus ASP supports fusion at multiple levels:

```text
posterior/parameter fusion
policy distribution fusion
successor-value fusion
semantic intention-vector fusion
teacher distillation
```

The empirical question is which level best preserves complementary strengths.

## 9. O Vigia baseline implementation

The first O Vigia implementation deliberately uses a sparse-data kernel baseline rather than pretending that a deep trajectory model can be trained from a handful of hourly cycles.

Its contract is:

```text
OKF agent-cycle reports
→ okf-parser trajectory corpus
→ common embedding model for prompts/states/successor states
→ trajectory-prefix kernel memory
→ reward-weighted desired prompt vector
→ nearest prompt from OKF bundle
```

Each historical cycle token combines the prior prompt embedding, successor-state embedding, and the best currently available value signal. All previous cycles contribute with temporal decay. Historical trajectory prefixes become exemplars mapping trajectory context to the prompt-space point that was chosen next and the value later associated with that choice.

This model is intentionally replaceable. Once enough trajectories accumulate, the same corpus can train a causal Transformer, recurrent state-space model, successor-feature network, or offline RL policy without changing the OKF event model or prompt catalog contract.

## 10. Research hypotheses

This refinement creates several testable hypotheses:

1. trajectory-conditioned policies outperform state-only policies when superficially similar project states arise from different behavioral histories;
2. predicting a continuous behavior vector transfers to newly added prompts better than categorical prompt classification;
3. nearest-prompt distance identifies useful catalog gaps and can guide prompt generation;
4. preserving retrieval telemetry improves off-policy evaluation and selector calibration;
5. semantic intention-vector fusion can combine independently trained agents even when their internal parameterizations are incompatible;
6. successor-state prediction plus semantic prompt retrieval outperforms direct reward-maximizing prompt selection as trajectory length grows.

## 11. Core claim

The central object learned by ASP is not a favorite prompt and not merely a value attached to the current state. It is a representation of **where the agent should move in behavioral space given the path by which it arrived at the present**.

The resulting control loop is:

```text
history of prompts + results + current state
        ↓
trajectory representation
        ↓
expected/desirable future representation
        ↓
desired point in semantic behavior space
        ↓
nearest available prompt in an evolving OKF catalog
        ↓
agent action
        ↓
new successor state and delayed evaluations
        ↺
```

This makes the prompt a replaceable executable surface of a deeper learned policy: a trajectory-conditioned representation of which behaviors tend to produce better futures.
