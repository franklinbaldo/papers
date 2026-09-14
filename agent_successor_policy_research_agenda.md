---
okf_version: "0.2"
title: "Agent Successor Policy — Research Agenda and Falsifiable Questions"
description: "Open architectural questions and experiments for trajectory-conditioned semantic policies."
doc_type: "alignment-paper-note"
status: "draft"
---

# Agent Successor Policy — Research Agenda and Falsifiable Questions

Franklin Baldo  
Draft: 2026-08-16

This note makes explicit a set of unresolved questions that are not implementation trivia but part of the empirical content of Agent Successor Policy (ASP). The current O Vigia implementation is useful precisely because it can turn these questions into measurable comparisons rather than settling them by intuition.

## 1. What should be the canonical behavior embedding space?

In the trajectory-conditioned form of ASP, the learned policy does not need to output a categorical prompt identifier. It may instead output a desired point in a semantic behavior space:

```text
z* = pi(tau_t)
```

The executable prompt is then retrieved from an OKF prompt catalog by nearest-neighbor search. This makes the choice of embedding model structurally important: it defines the geometry in which policies, prompt similarity, catalog gaps, fusion and interpolation are expressed.

The first question is therefore not merely which embedding model has the best benchmark score, but which representation produces a geometry that is useful for behavior selection. A good ASP embedding space should make prompts with operationally similar consequences close even when their wording differs, while separating prompts that are textually similar but behaviorally distinct.

This suggests several experiments:

- compare multiple fixed embedding models while holding the trajectory learner constant;
- evaluate whether nearest semantic prompts also produce similar successor states;
- measure policy regret under each embedding space;
- test whether the geometry remains stable when new prompts are added to the catalog;
- test whether checkpoints trained in one embedding space can be mapped into another without substantial loss.

A possible falsifier of the current semantic-retrieval hypothesis is that ordinary language embeddings may cluster prompts primarily by wording or topic rather than by downstream behavioral effect. If so, ASP may need a learned behavior-specific projection on top of a frozen general embedding model.

## 2. How much does trajectory history matter beyond current state?

ASP proposes that the relevant policy is trajectory-conditioned:

```text
pi(tau_t)
```

rather than merely state-conditioned:

```text
pi(s_t)
```

This claim should be tested directly. Two agents can reach apparently similar repository states through very different sequences of implementation, falsification, verification and documentation. If those histories contain information about saturation, repeated failure, momentum or unresolved uncertainty, a trajectory-aware policy should outperform a state-only policy.

The clean experiment is an ablation:

```text
Model A: current state only
Model B: current state + previous cycle
Model C: recent N-cycle window
Model D: full trajectory representation
```

All models should use the same prompt catalog, reward definitions and evaluation windows. Performance should be compared separately at hour, day, week, month and longer horizons.

This experiment can falsify an attractive but unnecessary complexity. If `pi(s_t)` performs as well as `pi(tau_t)`, the recurrent/trajectory machinery may not justify its cost. Conversely, a systematic advantage for longer context would establish that agent history is itself part of the decision state.

## 3. Does the policy learn destinations or directions?

There are at least two qualitatively different things a semantic policy might learn.

The first is a **destination model**: in a given trajectory, the next useful behavior lies near a stable semantic region such as verification, falsification or exploitation.

The second is a **vector-field model**: what matters is not an absolute region but a displacement relative to recent behavior. After several implementation-heavy cycles, the useful move may be away from implementation toward verification; after repeated falsification with no new evidence, the useful move may be back toward exploitation.

These hypotheses can be written as:

```text
absolute policy:  z* = f(tau_t)
relative policy:  delta_z* = g(tau_t, z_recent)
                  z* = z_recent + delta_z*
```

A relative policy would be particularly interesting because it would mean the agent has learned something like strategic dynamics rather than a static taxonomy of good prompts.

The experiment should compare absolute target prediction against displacement prediction, especially in trajectories exhibiting repeated prompts from the same semantic neighborhood. A strong signal would be whether the relative model better predicts moments when the agent should switch modes.

## 4. Which temporal rewards are actually informative?

ASP currently preserves separate judgments for hour, day, week, month and year horizons. This is deliberately richer than a single scalar reward, but it raises several questions.

Do the horizons contain genuinely different information, or are some redundant? Does an hour critic predict later success or merely activity? Does a simulated year critic provide useful regularization before genuine year-scale outcomes exist? How should later observed outcomes revise earlier simulated evaluations?

The architecture should therefore distinguish at least:

```text
forecast reward
next-cycle retrospective reward
observed delayed outcome
```

and measure the predictive relationship among them. A central calibration question is whether simulated long-horizon evaluators eventually correlate with real long-horizon consequences such as rework, reversions, merge durability, publication success, maintenance burden or reuse.

A possible result is that some horizons should be downweighted, combined or learned as latent timescales rather than fixed labels.

## 5. How should sparse hourly data be learned from?

A new cycle approximately once per hour is a low-data regime. ASP should therefore distinguish between immediate online adaptation and heavier representation training.

A plausible schedule is:

```text
each cycle: append OKF experience + lightweight online update
daily: replay/retrain small policy components
weekly: offline evaluation and checkpoint promotion
less frequently: representation/architecture changes
```

The empirical question is how much model complexity the accumulating corpus can support. Early nonparametric or Bayesian models may outperform neural sequence models simply because uncertainty is better represented and overfitting is lower.

An important benchmark is therefore not "does the Transformer fit the corpus?" but "at what corpus size does a learned trajectory encoder begin to outperform the sparse-data kernel/bandit baseline on held-out or subsequent trajectories?"

## 6. How should the prompt catalog evolve?

The OKF prompt catalog converts a continuous semantic policy into executable discrete behavior. This makes catalog quality part of the control system.

If the predicted point repeatedly falls far from every existing prompt, that distance may indicate not policy failure but a missing action in the catalog. A generator can then propose a new `agent-prompt` concept near the underserved region.

This creates a second learning loop:

```text
policy demand
→ semantic catalog gap
→ prompt generation
→ catalog expansion
→ execution
→ reward
```

Questions include whether catalog growth improves policy performance, whether generated prompts collapse into redundant paraphrases, and whether pruning poorly performing or duplicate prompts improves exploration. Catalog mutation should therefore be evaluated as an experimental variable rather than treated as free expansion.

## 7. Can the policy generalize beyond O Vigia?

O Vigia is the first environment, not necessarily the final abstraction boundary. A critical question is what part of ASP is project-specific.

The prompt catalog may contain generic behavioral modes, project-specific operations, or both. State representations may contain universal concepts such as blockers and evidence alongside domain-specific concepts such as article publication. The learned policy could therefore transfer at several levels:

- unchanged policy and unchanged catalog;
- shared policy with project-specific catalog;
- shared trajectory encoder with project-specific policy head;
- shared behavior space plus project adapters;
- no useful transfer at all.

The right time to extract ASP into a reusable library is an empirical question. Premature extraction can freeze assumptions before they are tested; never extracting makes transfer impossible to measure. A reasonable trigger is evidence that the same trajectory/prompt contracts work in at least two materially different repository-bound missions.

## 8. Where should training and checkpoint promotion run?

Training location is operationally important because ASP distinguishes canonical evidence from derived model artifacts. The durable source of truth should remain the append-only OKF cycle reports and prompt catalog. Training corpora, embedding indexes and checkpoints are derived.

This allows several execution environments:

- repository-local deterministic training;
- GitHub Actions when governance and billing permit;
- an external trusted runner;
- periodic manual training during the experimental phase.

The scientific requirement is not a particular runner but reproducibility. Each checkpoint should identify the exact corpus, embedding model, catalog, learner version, random seed or sampling policy, parent checkpoint and evaluation result from which it was produced.

Checkpoint promotion should be treated separately from checkpoint production. A newly trained model should not automatically become the active selector merely because it is newer. It should beat the previous policy and simple baselines under a declared evaluation rule.

## 9. How much of the agent is the model, and how much is the catalog?

ASP decomposes behavior into at least three learned or evolving objects:

```text
trajectory representation
continuous policy
prompt catalog
```

Performance gains may come from any of them. A stronger embedding model may appear to improve the policy when the real improvement comes from better prompt retrieval. A richer catalog may improve outcomes without any change to policy weights. A better trajectory model may only matter when the catalog contains sufficiently diverse actions.

Experiments should therefore vary these pieces independently. This decomposition also matters for agent fusion: two agents can differ in policy weights, trajectory memories, prompt catalogs, or all three.

## 10. Can multiple agents be combined in behavior space instead of parameter space?

Parallel ASP agents may produce desired behavior vectors:

```text
z_A = pi_A(tau)
z_B = pi_B(tau)
```

A combined agent can potentially fuse those intentions before retrieval:

```text
z_AB = alpha(tau) z_A + (1 - alpha(tau)) z_B
```

This avoids some representation-alignment problems of neural weight averaging, provided both agents share the same embedding coordinate system. The mixture coefficient may itself depend on context or temporal horizon.

The open question is whether semantic intention fusion preserves complementary strengths better than posterior fusion, mixture-of-experts at the discrete policy level, or distillation. This can be tested directly with agents trained on parallel trajectories.

## 11. What would falsify the broader ASP hypothesis?

ASP should not become unfalsifiable by absorbing every failure into another component. Several outcomes would count against its central claims:

1. trajectory-conditioned policies fail to beat state-only baselines after sufficient data;
2. prompt embedding distance fails to predict behavioral similarity or successor-state similarity;
3. continuous target prediction plus retrieval performs no better than direct categorical prompt selection;
4. multi-horizon rewards add noise without improving delayed outcomes;
5. simulated temporal critics remain poorly calibrated against observed future outcomes;
6. catalog expansion does not improve policy coverage or merely creates paraphrase redundancy;
7. learned policies fail to beat simple schedules, round-robin selection or strong hand-written heuristics;
8. parallel-agent fusion consistently underperforms selecting the best single parent.

These are desirable failure conditions to state in advance. The goal is not to preserve ASP as a story but to discover which parts of the architecture earn their complexity.

## 12. Experimental program

The O Vigia corpus can support a staged program as data accumulates:

```text
Stage 1
state-only baseline vs trajectory-kernel baseline

Stage 2
multiple embedding spaces + fixed prompt catalog

Stage 3
absolute target vs semantic displacement/vector-field policy

Stage 4
catalog growth/pruning experiments

Stage 5
learned trajectory encoder vs sparse-data baseline

Stage 6
parallel-agent fusion / distillation

Stage 7
cross-project transfer
```

The key methodological advantage of the current design is that these experiments need not change the underlying evidence format. The same append-only OKF cycle reports can be replayed into different corpus projections and learners. Architectural hypotheses can therefore compete over a shared history rather than rewriting the history to fit the latest model.
