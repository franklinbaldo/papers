---
okf_version: "0.2"
title: "Agent Successor Policy v2 — First Executable Semantic Policy"
description: "Implementation note connecting the ASP research architecture to the first trajectory-conditioned, reward-reranked, Jina-backed executable baseline in O Vigia."
doc_type: "alignment-paper-note"
status: "draft"
---

# Agent Successor Policy v2 — First Executable Semantic Policy

Franklin Baldo  
Draft: 2026-08-16

> **Implementation note, not an empirical result.** This note records the first executable realization of several hypotheses developed in the ASP paper and companion notes. The implementation lives in `franklinbaldo/ovigia-redacao#32`. At the time of this note, the new code is still marked **UNVALIDATED** in that repository: the canonical local integration gate has not been run on the new head, no real Jina embedding artifact has yet been observed, and no claim is made that the v2 policy outperforms its baselines.

## 1. Why a second implementation baseline was needed

The earliest ASP baseline represented a trajectory by a reward-weighted semantic summary and predicted an absolute point in the same embedding space as the prompt catalog. That implementation was intentionally small enough for a handful of hourly experiences. Cross-paper comparison subsequently exposed four missing distinctions:

1. semantic proximity is not the same as downstream functional usefulness;
2. a semantic position is not a complete dynamical state without information about the route by which it was reached;
3. "use the entire trajectory" cannot require unbounded rereading of raw history;
4. simulated temporal evaluations must not be silently relabeled as observed reward.

The v2 implementation makes those distinctions explicit while keeping the same external abstraction:

```text
trajectory
    → continuous behavioral intention
    → governed prompt catalog
    → selected prompt
    → successor state
```

## 2. Frozen semantic recall and learned functional ranking

Let the admitted prompt catalog be

\[
\mathcal P=\{p_1,\ldots,p_n\},
\]

and let a frozen embedding backend assign each prompt a semantic key

\[
e_j=E(p_j).
\]

The policy predicts a desired behavior vector \(z_t^*\). Semantic similarity is used only to construct a high-recall candidate set:

\[
\mathcal C_t=\operatorname{TopK}_{p_j\in\mathcal P}
\cos(z_t^*,e_j).
\]

Each prompt also has a learned functional key \(k_j\), utility estimate \(u_j\), and exposure count \(n_j\). The first implementation reranks semantic candidates by a mixture of semantic affinity, functional affinity, historical utility, and an exploration bonus:

\[
S_t(j)=
\alpha\,\widetilde{\cos}(z_t^*,e_j)
+\beta\,\widetilde{\cos}(z_t^*,k_j)
+\gamma u_j
+\kappa b(n_j),
\]

where cosine terms are rescaled for combination and \(b(n_j)\) is UCB-like.

The important learning rule is qualitative rather than the particular coefficients:

> **Exposure is not reward. Selection alone never moves a prompt's functional key.**

For attributed downstream reward \(R_t\) and a baseline \(\bar R\), define provisional advantage

\[
A_t=R_t-\bar R.
\]

The functional key update is directionally equivalent to

\[
k_j\leftarrow
\operatorname{norm}(k_j+\eta A_t h_t),
\]

where \(h_t\) is the trajectory context. Positive advantage pulls the prompt toward similar future contexts; negative advantage pushes it away. This is the direct ASP adaptation of reward-conditioned retrieval from the relay-transducer programme.

## 3. Trajectory state as position plus incoming motion

The v2 context is explicitly dynamical. If \(q_t\) is the embedding of the reconstructed current project state, an incoming semantic velocity is approximated by

\[
v_t=\operatorname{norm}(q_t-q_{t-1}).
\]

This quantity is deliberately crude in the sparse-data baseline. Its purpose is to make a falsifiable distinction available: can the same apparent current state require different prompts depending on the direction from which the trajectory arrived?

The policy learns two targets:

\[
z_t^{\mathrm{abs}}
\]

for an absolute desired prompt-space destination, and

\[
\Delta z_t^*
\]

for a desired displacement relative to the previously executed prompt.

The executable baseline combines them:

\[
z_t^*=
\operatorname{norm}
\left(
(1-\lambda)z_t^{\mathrm{abs}}
+\lambda(E(p_{t-1})+\Delta z_t^*)
\right).
\]

The mixing coefficient is part of the checkpoint, so `absolute target` versus `relative delta` can later be tested as a genuine ablation rather than treated as metaphor.

## 4. Bounded readout of a complete history

A recurrent project can eventually contain thousands of cycles. ASP therefore distinguishes **canonical history** from **readout representation**.

All cycle reports remain append-only OKF evidence. For one policy inference, however, v2 separates:

```text
recent cycles       → explicit recency-weighted summary
older cycles        → compressed long-term summary
current state       → explicit
incoming velocity   → explicit
```

If the recent window contains \(m\) cycles, all earlier cycles contribute to a derived long-term summary with a slower decay. Thus old evidence is not deleted, but the policy's immediate read cost does not scale by replaying every old vector at full resolution.

This is a first engineering approximation to the bounded-readout/reconstructive-memory hypothesis. It is not evidence that exponential summaries are optimal. They must be compared against recent-only, full-history, prototype, recurrent-state, attention, and reconstructive-memory alternatives.

## 5. Epistemic provenance and two notions of reward

The corpus now distinguishes at least four epistemic statuses:

```text
observed
simulated
inferred
pending
```

In particular:

- end-of-cycle future critics are `simulated`;
- next-cycle retrospective critics are also `simulated`;
- a scalar computed from those critics and calibration is an `inferred` bootstrap reward;
- an `observed_reward` is admitted only when an independently declared objective event or measurement supplies it;
- absence of a matured label remains `pending`.

This creates two materially different training/evaluation scopes:

\[
R_t^{\mathrm{sim}}
\quad\text{and}\quad
R_t^{\mathrm{obs}}.
\]

The implementation may use the simulated scalar while objective labels are sparse, but downstream evaluation must report which reward provenance supported a result. A model that only predicts its own critics has not yet demonstrated external project value.

## 6. Causal depth versus wall-clock time

Each derived corpus row can now retain both:

\[
\Delta t_{\mathrm{wall}}
\]

and a predecessor-chain depth

\[
d_{\mathrm{causal}}.
\]

The latter counts relevant ASP cycle transitions rather than hours on a clock. This makes the Informational Time connection experimentally accessible: fixed hour/day/week/month/year observers remain useful observation schedules, but the learner can separately test whether causal-cycle depth better explains delayed outcomes.

## 7. Jina AI as the first concrete embedding provider

The ASP theory does not depend on one commercial or open embedding provider. The O Vigia implementation nevertheless needs a concrete space before `continuous behavioral policy` becomes executable.

The first configured provider is Jina AI with an explicitly versioned artifact contract. The initial configuration uses:

```text
model: jina-embeddings-v3
task: text-matching
dimensions: 256
normalized vectors: true
```

Prompts, `state_before`, and `state_after` are projected through the same declared configuration. The derived artifact stores an `embedding_model_id` containing provider, model, task, and dimension. A checkpoint must reject a mismatched embedding artifact.

The choice is an implementation hypothesis, not a theoretical commitment. The research agenda still requires comparison with another single space, an aligned Semantic Reference Frame, and multi-space convergence.

## 8. Secret boundary and pre-cycle selection request

A practical complication sharpens the event-sourced architecture. `agent-cycle-start` must contain the chosen prompt **before the action**, but the current `state_before` must first be sent to an embedding service whose API key must never enter the knowledge corpus.

The implementation adds an earlier immutable concept:

```text
agent-selection-request
```

containing only:

```text
cycle_id
state_before
public embedding configuration
generation metadata
```

The sequence becomes:

```text
reconstruct factual state
        ↓
persist agent-selection-request
        ↓
derived workflow crosses secret boundary
        ↓
embedding index + checkpoint + selection artifact
        ↓
persist agent-cycle-start with chosen prompt
        ↓
action
        ↓
agent-cycle-end
```

This preserves two properties simultaneously:

1. the prompt is still an ex-ante commitment;
2. the API secret never becomes part of canonical experience memory.

The GitHub workflow used for this purpose is an artifact derivation mechanism, not a software-quality gate. The O Vigia repository continues to require its separate canonical local validation before integration.

## 9. Catalog gaps remain proposals, not authority

If the predicted vector lies far from every admitted prompt, the implementation emits explicit `catalog_gap` telemetry:

```text
best semantic similarity
threshold
nearest admitted prompt
```

This does **not** authorize a generated prompt. It only supplies evidence that the finite action vocabulary may under-cover a region frequently requested by the learned policy.

A future prompt generator may propose a candidate, but executable authority requires a separate catalog-admission event. This preserves the Affordance Restriction distinction:

\[
\text{learned preference}\neq\text{authority to enlarge action space}.
\]

## 10. Propensity-aware comparison with null policies

The first implementation also adds an offline evaluation layer. A selected prompt records a behavior propensity whenever the learned policy actually made the choice. Human overrides and fallback choices remain excluded from off-policy evaluation.

For behavior policy \(\mu\), candidate target policy \(\pi\), chosen action \(a_t\), and reward \(R_t\), the initial evaluator uses self-normalized importance sampling:

\[
\hat V_{\mathrm{SNIPS}}(\pi)=
\frac{\sum_t w_tR_t}{\sum_t w_t},
\qquad
w_t=\frac{\pi(a_t\mid s_t)}{\mu(a_t\mid s_t)}.
\]

It reports overlap diagnostics including effective sample size rather than treating a number with vanishing support as evidence.

The first null policies are:

- uniform choice over the admitted catalog;
- repeat the last prompt;
- state-only semantic retrieval;
- trajectory-conditioned v2.

Observed reward and simulated bootstrap reward are evaluated separately. With insufficient overlap, the correct output is **no estimate**, not zero and not a win for ASP.

These baselines operationalize the stronger epistemic requirement inherited from the agent-recognition work: structure in a learned trajectory representation is interesting only if it predicts or controls outcomes better than simpler structured alternatives.

## 11. What this implementation does not yet establish

The existence of code for the architecture establishes none of its empirical claims. In particular, it does not yet establish that:

- Jina embeddings provide the best or even a good behavioral geometry;
- trajectory conditioning beats current-state conditioning;
- velocity is causally useful;
- relative delta prediction beats absolute target prediction;
- compressed long-term memory preserves all policy-relevant history;
- functional reranking beats cosine-only retrieval;
- the five initial prompts cover an adequate behavioral action space;
- temporal self-critics predict observed future outcomes;
- ASP beats a scheduler or simple hand-written policy;
- a latent trajectory representation deserves an agent-level interpretation.

These remain falsifiable comparisons, not conclusions.

## 12. Immediate experimental ladder

The implementation suggests a staged evaluation that avoids waiting for a large neural policy before testing the mechanism:

1. **Provider smoke test.** Produce a real embedding artifact for the existing OKF catalog and historical states; verify determinism/identity contracts and no secret leakage.
2. **First semantic selection.** Run one real pre-cycle selection, persist its propensity and execute the admitted prompt.
3. **Semantic recall test.** Compare cosine-only against reward-conditioned reranking among deliberately similar prompt siblings.
4. **Trajectory ablation.** Compare state-only, recent-history, and recent + compressed-history policies.
5. **Dynamics ablation.** Compare absolute target, delta-only, and mixed prediction.
6. **Temporal ablation.** Compare wall-clock and causal-depth outcome models.
7. **Objective maturation.** Accumulate independently observed outcomes rather than relying on simulated critics.
8. **OPE threshold.** Refuse policy-comparison claims until logged overlap and effective sample size cross preregistered minima.
9. **Cross-environment test.** Transfer the representation/policy machinery from O Vigia to the papers synthesis routine without assuming the same reward structure.

## 13. Relation to the main ASP claim

The v2 baseline changes the implementation question from:

> Which prompt ID should be selected now?

to:

> Given the trajectory by which this agent-project system arrived here, what behavioral displacement is desirable, which admitted prompts lie near that intention, and which of those semantically plausible prompts has historically produced useful successors under comparable conditions?

That is the first executable form of ASP's stronger proposal: **trajectory-conditioned continuous behavioral control with governed semantic discretization and delayed outcome learning**.
