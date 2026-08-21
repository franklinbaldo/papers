---
okf_version: "0.2"
title: "Agent Successor Policy: Multi-Horizon Reward Representations for Prompt-Selected Autonomous Work"
description: "A proposal for agents whose cycle-level prompts are selected by learned representations of the futures their behaviors tend to produce."
doc_type: "alignment-paper"
status: "draft"
---

# Agent Successor Policy: Multi-Horizon Reward Representations for Prompt-Selected Autonomous Work

Franklin Baldo  
Draft: 2026-08-16

## Abstract

Autonomous coding and research agents are often controlled by a fixed system prompt, a schedule, or a short-term instruction. This makes each work cycle depend heavily on the immediate local state while discarding a richer signal: which behavioral modes tend to place the agent in better future states across hours, days, weeks, and months. This paper proposes **Agent Successor Policy** (ASP), a framework in which an agent begins each cycle by selecting a strategy prompt from a set of candidates. Selection is guided by a learned or incrementally updated representation of expected future state features under multiple reward horizons. Instead of asking only which action should be taken now, ASP asks which behavioral mode is likely to move the agent into regions of state space associated with good futures.

The framework combines prompt generators, prompt selectors, a temporal reward ledger, and a successor-style representation of agent trajectories. It is designed for practical repository-bound agents: the agent writes its decisions, evidence, outcomes, and reward updates into versioned project memory, while deterministic runners may materialize models, evaluate artifacts, and upload learned weights as build artifacts. The initial implementation target is O Vigia, a static-first civic-newsroom project whose hourly ChatGPT task must progress toward a first real published article without duplicating operations or losing knowledge between cycles.

## 1. Motivation

A recurring agent faces a problem different from a one-shot assistant. It must not merely answer a prompt; it must maintain a project trajectory. The important question is often not “what is the next action?” but “what kind of agent should act in this state?”

A conservative agent may reliably close local blockers but miss alternative routes. An exploratory agent may find new capabilities but create noise. A falsification-oriented agent may prevent wasted work but sometimes slow momentum. A publication-oriented agent may converge quickly but risk under-building infrastructure. These are not just prompts; they are behavioral policies.

A fixed hourly instruction cannot easily learn which behavioral policy works best in which project state. If every cycle starts from the same mandate, the agent can record progress but cannot systematically improve its own mode of operation. Agent Successor Policy treats the first act of each cycle as a policy decision: select the prompt that will guide the rest of the cycle.

## 2. Core Idea

At cycle `t`, the project has a state `s_t`: open PRs, issues, recent commits, failing gates, current blockers, artifacts, previous reports, and the explicit mission. The agent or deterministic tooling produces a set of candidate strategy prompts:

```text
P_t = {p_1, p_2, ..., p_n}
```

A selector chooses one prompt:

```text
p_t = selector(s_t, P_t, H_t, W_t)
```

where `H_t` is the recorded trajectory history and `W_t` is the current model or policy-weight artifact. The selected prompt guides the agent’s work cycle. After the cycle, the system records:

```text
(s_t, P_t, p_t, action_t, evidence_t, s_{t+1}, rewards_t)
```

The cycle is not complete when a chat message is sent. It matures as later evidence arrives. A change that looks good after one hour may create rework after a week. A conservative handoff may look small immediately but become valuable because later agents resume without rediscovery. ASP therefore uses a **temporal reward ledger**.

## 3. Multi-Horizon Rewards

Let `r_h^k` denote reward component `k` at horizon `h`. Horizons may include:

- immediate or same-cycle reward;
- one-hour reward;
- one-day reward;
- one-week reward;
- one-month reward;
- one-year reward.

Components may include:

- progress toward the mission gate;
- factual correctness;
- reproducibility;
- evidence quality;
- maintainability;
- reduction of downstream uncertainty;
- avoidance of duplicate operations;
- publication or deployment success;
- negative rework caused later.

A cycle can therefore carry a reward tensor rather than a scalar:

```text
R_t[h, k]
```

This avoids premature collapse of value. Different selectors may optimize different scalarizations depending on the phase of the project. A publication sprint may weight short-horizon progress more heavily; a foundational architecture phase may weight weekly maintainability and downstream reuse.

## 4. Successor Representations for Agents

Classical reinforcement learning often learns value functions. ASP is closer to successor representations and successor features. Let `phi(s)` be a feature representation of project state: for example, whether a PR is draft, whether a gate is validated, whether a real artifact exists, whether evidence is persisted, whether a blocker is external, and whether the next action is ambiguous.

For a prompt or behavioral mode `p`, define a horizon-specific successor estimate:

```text
psi_h(s, p) = E[sum_{k >= 0} gamma_h^k phi(s_{t+k}) | s_t = s, prompt = p]
```

Small `gamma_h` values emphasize near-term consequences. Large `gamma_h` values emphasize longer futures. The agent representation is not a static personality label. It is the distribution of futures its prompt-conditioned behavior tends to produce.

The selector may then choose prompts by predicted multi-horizon value:

```text
score(s, p) = aggregate_h,k( w_h,k * f_k(psi_h(s, p)) )
```

This captures the central claim: a useful autonomous agent should learn which behavioral mode produces good future states in the current context, not merely which immediate action appears best.

## 5. Candidate Prompt Generators

ASP separates prompt generation from prompt selection. A system may include several generators:

1. **Schedule generator**: cycles through implementation, verification, review, documentation, and publication modes.
2. **Heuristic generator**: emits prompts based on repository state, such as “validate the draft PR” or “do not write new code until the blocker is reproduced.”
3. **Falsification generator**: asks what would disprove the current plan and forces negative evidence to be recorded.
4. **Exploration generator**: searches for alternative paths, existing code to reuse, or latent capabilities.
5. **Exploitation generator**: focuses on the smallest action that closes the next gate.
6. **Historical retrieval generator**: retrieves prompts that performed well in semantically similar prior states.
7. **Mutation generator**: combines or mutates past successful prompts.

Generators themselves can compete. The system should track not only which selected prompts perform well, but which generators produce candidates that lead to good futures.

## 6. Selection Policies

ASP supports a ladder of sophistication.

The simplest selector is deterministic scheduling. A slightly richer selector is random choice among eligible strategies, useful for exploration. A practical early selector is epsilon-greedy over strategy statistics. More advanced selectors can use UCB, Thompson sampling, embedding-similarity retrieval, contextual bandits, or learned ranking models.

A useful first implementation does not require neural training. It can maintain JSON weights:

```json
{
  "strategies": {
    "exploit-next-gate": {"trials": 12, "mean_reward": 0.64},
    "falsify-plan": {"trials": 5, "mean_reward": 0.51}
  }
}
```

This is enough to select prompts, record outcomes, and create a dataset for later learning. The system can later replace the selector with a model trained from the same ledger.

## 7. Repository-Bound Memory

A recurring agent must avoid losing knowledge in chat history. ASP therefore treats the repository as operational memory. Each cycle should write durable state when it learns something reusable:

- an updated PR body;
- a runbook;
- a cycle ledger entry;
- a model artifact manifest;
- a test, failing or passing;
- an issue comment with evidence;
- a deterministic workflow artifact.

For O Vigia, this means the hourly task should begin by running or consulting a selector. The selector emits the strategy prompt for the next cycle. The ChatGPT task remains the reasoning agent. GitHub Actions, when allowed, only materialize deterministic artifacts such as reward ledgers, model weights, summaries, and reports.

## 8. Weight Artifacts

Learned policy weights are mutable and may be noisy. They should not always be committed directly to `main`. ASP distinguishes:

- **ledger**: durable, inspectable, versioned evidence of cycles and reward updates;
- **weights**: derived artifacts produced from the ledger;
- **policy manifest**: a small versioned pointer describing which artifact was used and how it was produced.

For public or CI-enabled repositories, a workflow can train or update a lightweight policy and upload `agent-policy-weights.json` as a GitHub Actions artifact. In repositories where Actions are disabled or inappropriate, the same deterministic script can be run externally and its artifact referenced in the operational PR until governance permits an upload. This preserves the conceptual contract without pretending that every repository has runners available.

## 9. O Vigia as a Testbed

O Vigia is a good initial environment because it has a clear mission: publish a first real low-sensitivity article from public civic data with provenance. The current task has strict constraints: do not duplicate operations, do not invent publication, respect local validation gates, and persist knowledge in GitHub.

A first ASP integration for O Vigia should:

1. add a deterministic `ovigia select-next-cycle-prompt` command;
2. maintain a small strategy catalog;
3. maintain a reward ledger schema;
4. choose a strategy using schedule or epsilon-greedy weights;
5. output a complete prompt for the next ChatGPT cycle;
6. update the hourly task instruction to obey the selector at the start of each round;
7. provide a deterministic script or workflow contract for writing policy weights as artifacts.

This implementation should not block the First Story. It should guide the routine while the operational PR continues advancing the real `2026-04 → 2026-05` pipeline.

## 10. Safety and Failure Modes

ASP can fail by optimizing proxies. A selector might learn to prefer visible churn over important but quiet work. It might overfit to self-evaluation. It might avoid risky but necessary actions. It might privilege short-horizon progress and accumulate long-term debt.

Mitigations include:

- multi-horizon rewards rather than immediate-only rewards;
- explicit negative rewards for duplicated work and unsupported claims;
- delayed reward updates when rework appears;
- separation between self-evaluation and external evidence;
- mandatory evidence fields for any reward claim;
- keeping the selector advisory rather than absolute while the dataset is small;
- human override and repository governance.

## 11. Research Questions

1. Do prompt strategies have stable performance signatures across similar repository states?
2. Can multi-horizon rewards reduce short-termism in autonomous coding agents?
3. Does successor-style representation improve transfer between projects?
4. Which reward components are most predictive of later successful publication or merge?
5. Can a small ledger plus bandit selector outperform a fixed hourly prompt?
6. How much of the system can remain deterministic while the reasoning stays in ChatGPT?
7. Can populations of independently trained ASP agents be merged or distilled into a policy that preserves complementary temporal and contextual strengths better than simple weight averaging?

## 12. Conclusion

Agent Successor Policy reframes prompt selection as trajectory control. A recurring agent should not merely choose the next action; it should learn which behavioral mode tends to produce good future states across multiple time scales. The practical implementation can begin simply: store candidate prompts, select one by a lightweight policy, record outcomes, and upload derived weights as artifacts. Over time, the repository accumulates a dataset of agent behavior, rewards, and futures. The prompt becomes the executable surface of a learned representation of what kind of agent to be next.

## Appendix A. Temporal Evaluator Ensemble and Forecast Calibration

A practical difficulty in multi-horizon reinforcement signals is that genuinely observed weekly, monthly, or annual rewards arrive slowly. ASP can bootstrap a denser signal by asking the reasoning agent to simulate a small ensemble of temporally situated evaluators while keeping those simulations explicitly separate from external evidence.

At the end of cycle `t`, the agent predicts how five future evaluators — hour, day, week, month, and year — would grade the cycle on two independent dimensions:

```text
F_t[h] = (importance_t,h, quality_t,h, rationale_t,h)
```

At the beginning of cycle `t+1`, before selecting the new strategy prompt, the agent reconstructs cycle `t` from repository evidence and again simulates each temporal evaluator:

```text
G_t+1[h] = (importance'_t,h, quality'_t,h, rationale'_t,h)
```

The first object is a **forecast**, not a reward. The second is a **retrospective simulated evaluation** made with one additional cycle of context. Their disagreement provides a calibration signal:

```text
E_t[h] = |importance_t,h - importance'_t,h|
       + |quality_t,h - quality'_t,h|
```

This creates a useful separation between anticipated value and later self-critique. An agent that systematically exaggerates the future importance or quality of its own work accumulates forecast error even if it produces locally attractive reports. Conversely, an initially modest action that proves more useful to the next cycle can be revised upward.

The evaluator horizons should not be interpreted as literal time travel. The year evaluator is a role-conditioned simulation asking whether the work appears durable under a year-scale objective, not an observed annual outcome. Real delayed outcomes can later supersede or augment these simulated grades. The ledger must therefore label forecasts, next-cycle retrospectives, and external rewards distinctly.

A simple bootstrap scalarization can combine the two grades at each horizon as:

```text
v_t,h = importance_t,h × quality_t,h
```

and then penalize miscalibration:

```text
r_t = mean_h(v'_t,h) - lambda * calibration_error_t
```

while preserving the full vector `G_t+1[h]` in the training data. This scalar is only a temporary interface for a bandit selector. A richer RL model should consume the multi-horizon vector directly and learn representations of which strategies lead to desirable future-state distributions.

This temporal critic loop adds a second learning problem to ASP: the system learns not only which prompt strategies produce good futures, but also how well its current agent can anticipate the future value of its own work. Calibration itself therefore becomes part of the learned representation of agent quality.

## Appendix B. Parallel Agent Training, Fusion, and Policy Lineage

ASP naturally supports training more than one agent in parallel. Two agents may start from the same policy family but receive different sampled prompts, different trajectories, or different subsets of project experience. The objective of fusion is therefore not to average personalities or parameters indiscriminately. It is to combine **evidence about which futures each policy tends to produce** while preserving uncertainty, temporal specialization, and provenance.

### B.1. Bayesian posterior fusion for compatible linear heads

For the initial neural-linear or Bayesian-linear form of ASP, each temporal output head can retain its posterior sufficient statistics instead of storing only a point estimate of the final weights. Let a Gaussian linear head be represented in natural parameters by precision matrix `Lambda` and precision-weighted mean `eta = Lambda mu`.

If two agents `A` and `B` were initialized from the same prior `(Lambda_0, eta_0)` and trained on non-overlapping evidence, their posterior information can be combined without replaying every observation:

```text
Lambda_AB = Lambda_A + Lambda_B - Lambda_0
eta_AB    = eta_A    + eta_B    - eta_0
mu_AB     = inverse(Lambda_AB) eta_AB
```

The subtraction prevents the common prior from being counted twice. The merge is performed independently for every ASP output, for example:

```text
hour.importance
hour.quality
day.importance
day.quality
week.importance
week.quality
month.importance
month.quality
year.importance
year.quality
```

This permits one agent's stronger short-horizon evidence and another agent's stronger long-horizon evidence to contribute according to posterior confidence rather than an arbitrary 50/50 average.

A direct posterior merge is valid only when the checkpoints share a compatible coordinate system. A merge manifest should therefore bind at least:

```text
model_family
architecture_version
encoder_id
encoder_version
feature_schema_hash
prior_id
reward_schema_version
```

If any of these differ materially, direct parameter fusion must be rejected rather than silently producing a meaningless model.

### B.2. Why naive neural weight averaging is insufficient

Once agents learn independent neural representations, parameter coordinates need not remain semantically aligned. One network may encode a feature such as `external blocker` in one hidden unit while another encodes an equivalent feature in a different unit or distributed direction. Elementwise averaging can therefore destroy useful representations even when the two policies behave similarly.

Weight averaging or model soups remain plausible when models are fine-tuned from the same base checkpoint, use the same architecture, remain in a compatible basin, and pass empirical interpolation checks. ASP should nevertheless treat this as an evaluated merge method, not a default assumption.

### B.3. Mixture of experts as contextual fusion

A stronger notion of obtaining the “best of both” is to learn when each agent should be trusted. Let two trained policies produce action distributions `pi_A(a|s)` and `pi_B(a|s)`. A gating model can learn a contextual coefficient `alpha(s)`:

```text
pi_mix(a|s) = alpha(s) pi_A(a|s)
            + (1 - alpha(s)) pi_B(a|s)
```

The gate can itself be multi-horizon. Agent `A` may be more reliable for immediate gate closure while agent `B` produces states that score better at week or year horizons. A horizon-conditioned gate can therefore estimate:

```text
V_h^mix(s, a)
  = alpha_h(s) V_h^A(s, a)
  + (1 - alpha_h(s)) V_h^B(s, a)
```

This turns agent fusion into a policy-selection problem over policies. Instead of constructing an average agent, the system learns **which agent is a useful expert in which state and at which horizon**.

### B.4. Distillation into a single successor agent

An ensemble or mixture may be expensive to serve. Once a gating ensemble demonstrates superior behavior, it can become a teacher for a single student policy. A replay corpus supplies project states and candidate prompts; the teacher produces action probabilities, multi-horizon values, successor-feature targets, and uncertainty estimates. The student then learns to approximate the combined policy:

```text
state + candidate prompts
        ↓
teacher ensemble / mixture
        ↓
policy distribution
multi-horizon value vector
successor representation
        ↓
student ASP agent
```

Distillation should preserve more than the selected action. Matching the teacher's full action distribution and temporal value vector allows the student to retain information about near-ties, uncertainty, and complementary long-horizon strengths.

### B.5. Recursive fusion and populations

Fusion can be recursive. Agents `A` and `B` may form `AB`; agents `C` and `D` may form `CD`; the descendants may later be combined or distilled again. This creates a population-level optimization process:

```text
A ─┐
   ├→ AB ─┐
B ─┘      │
          ├→ ABCD
C ─┐      │
   ├→ CD ─┘
D ─┘
```

The important object is therefore not only a checkpoint but a **policy lineage**. Each checkpoint artifact should record its parents and the transformation that created it:

```yaml
agent_id: agent-AB
parents:
  - agent-A
  - agent-B
fusion:
  method: bayesian-posterior
  compatibility_manifest: sha256:...
```

For mixtures or distilled descendants, the lineage records the gate, teacher ensemble, training corpus manifest, and evaluation set. This makes population experiments reproducible and allows retrospective analysis of which lineages produced better future-state distributions.

### B.6. Preventing double counting

Parallel agents may train on overlapping trajectories. Naively combining their posterior statistics would then count shared evidence multiple times. Every training corpus and checkpoint should therefore identify the experience set from which it was derived, ideally by immutable cycle-report concept IDs or a digest of the selected corpus rows.

A merger can then distinguish:

- disjoint evidence, which permits direct posterior addition under compatible priors;
- partially overlapping evidence, which requires subtracting or replaying the shared subset;
- identical evidence with divergent stochastic training, which is better handled as an ensemble or distillation experiment rather than evidence fusion.

This is especially important in repository-bound ASP because multiple agents can observe the same public Git state while exploring different prompt strategies.

### B.7. Population selection and evolutionary experiments

A population of ASP agents permits a higher-level experimental loop. Agents can be varied by strategy generator, exploration parameter, temporal scalarization, representation architecture, or critic calibration. Evaluation then selects parents using held-out trajectories or online outcomes, and a new generation is produced by posterior fusion, mixture gating, distillation, mutation, or fresh initialization.

The resulting process resembles evolutionary search, but the inheritance mechanism is explicit and auditable. Instead of treating a child as an opaque mutation, ASP can state what was inherited: posterior evidence, prompt-generation behavior, representation weights, or teacher policy outputs.

A particularly useful experiment is to compare three descendants from the same parents:

```text
Bayesian merged child
Mixture-of-experts child
Distilled child
```

against both parents and a fixed-policy baseline. The comparison can be performed separately at hour, day, week, month, and year horizons. This tests whether policy fusion actually preserves complementary strengths or merely raises average short-term reward.

### B.8. Artifact contract for mergeable agents

A mergeable ASP checkpoint should be a structured artifact rather than a bare tensor file. A minimal bundle is:

```text
policy-checkpoint/
  manifest.json
  feature-schema.json
  prior.json
  posterior/
    hour-importance.*
    hour-quality.*
    ...
    year-quality.*
  training-corpus-manifest.json
  evaluation.json
  lineage.json
```

The manifest binds representation coordinates; the corpus manifest prevents accidental evidence duplication; `evaluation.json` records comparative performance; and `lineage.json` makes the agent genealogically inspectable. GitHub artifacts or equivalent immutable artifact stores can hold the large derived files, while the repository preserves the small manifests and OKF trajectory evidence required to reproduce them.

The larger implication is that ASP can learn not only *which prompt should be selected next*, but also *which learned agent should govern the next decision*. Policy selection, agent selection, agent fusion, and agent evolution therefore become different scales of the same successor-oriented optimization problem.
