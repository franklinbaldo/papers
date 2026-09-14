---
type: "Empirical Paper"
title: "Semantic Computation Reuse Experiment 1: Do Substitutive Textual Paths Exist?"
description: "Pre-registered existence test of whether ordered cross-trajectory textual checkpoints can preserve objective task success under a sharply reduced fresh-generation budget; no results collected yet."
tags: [semantic-computation-reuse, preregistration, reasoning-memory, computation-substitution, trajectory-composition]
timestamp: 2026-08-21T19:53:00-04:00
---

# Semantic Computation Reuse Experiment 1: Do Substitutive Textual Paths Exist?

**Franklin Baldo**  
Independent Researcher  
franklinbaldo@gmail.com

> **Pre-registered design; no results yet.** No target-model result may be interpreted under this protocol until the run manifest described below has been committed with model, benchmark, task split, memory snapshot, segmentation, budgets, candidate-search limits, seeds, and evaluator hashes frozen. Any post-result change creates a new experiment version and the earlier result remains part of the record.

## 1. Question

This experiment tests only **existence**, not deployable navigation.

> Can an ordered sequence of concrete textual checkpoints drawn from heterogeneous prior LLM trajectories causally substitute for part of fresh reasoning on a held-out task?

The experiment intentionally permits an expensive, outcome-aware **oracle path-discovery stage**. If no substitutive path can be found even with this advantage, building Semantic Atlas navigation, successor-value policies, learned graph search, or massive vector infrastructure is premature.

A positive result is only an upper-bound existence result. It does not show that useful paths can yet be found cheaply or without outcome feedback.

## 2. Hypotheses

### H1 — Strong SCR existence hypothesis

For held-out objectively verifiable tasks, a frozen ordered path of three concrete historical checkpoints from distinct source trajectories will preserve substantially more task success under a short fresh-generation budget than:

- no-memory short-budget generation;
- semantic top-k fragments with no path structure;
- a procedural abstraction of the same evidence;
- the same three path fragments in a non-identity shuffled order.

The ordered path should also recover a substantial fraction of the success of full-budget fresh reasoning.

### H0a — Relevant-content account

Any benefit is explained by exposing semantically relevant text. Top-k retrieval performs as well as the composed path.

### H0b — Bag-of-hints account

The same fragments work regardless of order. Shuffling does not reduce performance.

### H0c — Procedural-guidance account

A compact procedural abstraction of the path performs as well as the concrete ordered checkpoints. The memory is useful guidance, but there is no evidence that concrete state composition is doing additional work.

### H0d — No-substitution account

Retrieval may improve accuracy, but all successful arms still require roughly full fresh reasoning. Past computation is not measurably displacing new inference.

## 3. Scope and non-claims

This experiment does **not** test:

- whether semantic nearest-neighbor search can autonomously discover the correct path;
- whether an SCR system is economically cheaper end-to-end;
- whether the result scales with memory size;
- whether text reproduces hidden states;
- whether a universal continuation-equivalence metric exists;
- whether results transfer across model families;
- whether a generated off-datastore waypoint can be inverted to text.

Those belong to later stages only if H1 survives.

## 4. Experimental domain

The primary domain must satisfy four conditions:

1. objective automatic verification of final answers;
2. multi-step tasks for which the chosen target model has non-trivial but imperfect full-budget performance;
3. a corpus of successful historical textual reasoning trajectories that can be segmented into intermediate checkpoints;
4. a defensible held-out split such that exact test solutions and complete test trajectories are absent from the memory snapshot.

A code, mathematics, formal-logic, or procedurally generated compositional benchmark is admissible. The exact benchmark is frozen in the run manifest **before any target-model output on evaluation tasks is collected**.

For a procedurally generated benchmark, generator code, generator version, seeds, and train/calibration/test template-composition splits must be committed before generation. Test compositions must be absent as complete compositions from the memory split, while constituent motifs may occur separately so that open recombination is possible.

For an external benchmark, the exact task IDs and family-disjointness rule must be committed. Known train/test contamination risks must be reported and weaken any claim of task novelty.

## 5. Frozen substrate gate

Before target-data collection, commit a machine-readable run manifest containing at least:

```yaml
experiment: semantic-computation-reuse-experiment-1
protocol_version: 1
benchmark_id: ...
benchmark_revision: ...
calibration_task_ids: [...]
evaluation_task_ids: [...]
memory_task_ids: [...]
memory_snapshot_sha256: ...
segmenter_version: ...
embedding_model_id: ...
embedding_revision: ...
target_model_id: ...
target_model_revision: ...
target_model_weight_hash_or_provider_revision: ...
hidden_reasoning: disabled_or_observable
sampling:
  temperature: ...
  top_p: ...
  replicas: 3
budgets:
  full_generated_tokens: ...
  short_generated_tokens: ...
  retrieval_input_tokens: ...
path_length: 3
candidate_pool_k: ...
path_search_cap: ...
rng_seeds: [...]
evaluator_version: ...
```

The target model must either expose all billable/generated reasoning tokens or be a model configuration without hidden reasoning. A model whose unobserved internal reasoning budget can vary by arm is not admissible for the primary computation-substitution claim.

Model selection may use operational criteria such as reproducibility, availability, objective-benchmark competence, and absence of hidden reasoning, but may not use SCR arm performance. After the first target-model evaluation output exists, model substitution is a new preregistered experiment.

## 6. Data construction

### 6.1 Historical memory

Collect successful reasoning trajectories only from the memory split. Preserve raw text and provenance. Segment each trajectory into checkpoints using one frozen segmentation procedure.

Each memory entry stores at least:

```text
entry_id
source_task_id
source_trajectory_id
step_index
checkpoint_text
embedding
predecessor_entry_id
successor_entry_id
source_outcome
source_generated_tokens
model/revision
```

No evaluation-task answer, evaluation-task trajectory, or episode-specific hidden target may enter the memory.

### 6.2 Checkpoint granularity

Checkpoint granularity is frozen before evaluation. The segmenter may use sentence/paragraph boundaries, explicit reasoning steps, or a fixed token window, but it may not be tuned on evaluation-arm performance.

If the initial memory contains fewer than three distinct source trajectories with plausible candidates for a material fraction of test tasks, the experiment is operationally underpowered and should stop rather than relax the heterogeneity condition post hoc.

### 6.3 Heterogeneous-path constraint

Every SCR path contains exactly three checkpoints:

\[
P=(x_a,x_b,x_c),
\]

with each checkpoint drawn from a different `source_trajectory_id`. No two checkpoints may be adjacent steps from the same historical solution, and no complete historical trajectory may be replayed.

## 7. Calibration split and budgets

Use only the calibration split to choose token budgets and verify that the target model is suitable.

Run no-memory fresh reasoning with a generous cap. Set:

- `B_full` to a frozen generation budget sufficient for stable non-trivial performance on calibration tasks;
- `B_short` to at most one quarter of `B_full`.

The exact values are committed in the manifest before evaluation.

The model is unsuitable if full-budget calibration accuracy is below 60% or above 95%. Below 60%, the task/model pair may be too weak to define a useful substitution target; above 95%, ceiling effects make improvement hard to interpret. Replacing the model or benchmark after this gate requires a new manifest and occurs before evaluation-task results.

All short-budget arms receive the same maximum fresh-generation budget `B_short`.

## 8. Oracle path discovery

The existence experiment deliberately separates **path existence** from **path finding**.

For each held-out evaluation problem, construct a frozen candidate pool using only the test prompt, memory, embedding index, and historical transition metadata. The candidate-pool rule and `K` are frozen in the manifest.

An outcome-aware search may then evaluate candidate ordered triples under the objective task verifier. The search is capped identically for every test task and records every tried path and outcome.

Important boundaries:

- discovery may use correctness feedback for the current evaluation task;
- discovery may not modify model weights, embeddings, memory contents, or checkpoint text;
- the winning path is frozen after the discovery phase;
- discovery outputs are never counted as evidence of deployable efficiency;
- all confirmatory comparisons use **fresh model replicas/seeds not used in path discovery**.

This produces an oracle upper bound: *if a substitutive path existed among the allowed candidates, could we identify one with a bounded exhaustive/black-box search?*

A later Stage 2 experiment must remove outcome-aware search.

## 9. Confirmatory arms

For every evaluation task, run the following arms with frozen prompts and evaluation seeds.

### A — Full fresh reasoning

No memory. Generation budget `B_full`.

Purpose: estimate the task performance that a substitutive path is trying to preserve.

### B — Short fresh reasoning

No memory. Generation budget `B_short`.

Purpose: quantify how much performance is normally lost when fresh inference is strangled.

### C — Semantic top-k

Provide memory fragments selected only by frozen semantic similarity to the current problem, under the same retrieval input-token budget as the SCR path. Do not use historical transition order. Fresh generation budget `B_short`.

Purpose: test the relevant-content/RAG explanation.

### D — Procedural abstraction

From evidence matched to the SCR path, produce one concise procedural abstraction that states the reusable method or lesson without preserving the original three-checkpoint sequence. The abstraction procedure/model, maximum tokens, and whether it may see the test prompt are frozen in the manifest. Its construction cost is recorded separately.

Fresh generation budget `B_short`.

Purpose: test whether a compact skill/procedure fully explains the effect.

### E — Ordered composed path

Provide the three concrete historical checkpoints selected and frozen by oracle path discovery, in their discovered order. Fresh generation budget `B_short`.

This is the SCR arm.

### F — Same-fragment shuffle

Use exactly the same three checkpoint strings as E with identical formatting and input-token budget, but apply a preregistered non-identity permutation determined by evaluation seed. Fresh generation budget `B_short`.

Purpose: isolate sequential order from content.

### G — Edge-destroyed path

Before path discovery, randomize predecessor/successor edges within strata that preserve source-task family and coarse semantic-distance statistics. Run the same candidate-search cap and freeze the selected path. Fresh generation budget `B_short`.

Purpose: test whether historical transition topology helps beyond node content and semantic neighborhoods.

This arm is secondary for Stage 1 because the oracle is already outcome-aware, but it becomes important for later navigation claims.

## 10. Prompt and information controls

All retrieval arms must use the same outer prompt template apart from the memory payload.

For C, E, F, and G:

- cap retrieved text by the same tokenizer and token budget;
- use identical delimiters and metadata visibility;
- do not reveal source-task correctness or evaluator scores to the target model;
- do not identify one payload as "best," "correct," or "oracle selected";
- do not include evaluation answers in memory metadata.

D may use fewer tokens because abstraction is part of the hypothesis being tested; its exact size and construction cost are reported.

If formatting differs in a way that reveals arm identity to the target model, the primary comparison is invalid.

## 11. Sampling and unit of inference

Use three fresh evaluation replicas/seeds per task unless the frozen target is deterministically reproducible, in which case one deterministic run may be preregistered instead.

The inferential unit is the **evaluation task**, not individual replicas. Average replicas within each task first, then compare paired task-level outcomes.

No successful task may be duplicated as additional inferential observations because it produced multiple generations.

## 12. Outcomes

### 12.1 Primary outcome

Objective task success under `B_short`.

The primary contrasts are paired, task-level differences:

\[
\Delta_{shuffle}=Acc(E)-Acc(F),
\]

\[
\Delta_{procedure}=Acc(E)-Acc(D),
\]

\[
\Delta_{semantic}=Acc(E)-Acc(C).
\]

### 12.2 Substitution retention

Define

\[
\rho = \frac{Acc(E)}{Acc(A)}
\]

when `Acc(A)>0`.

This measures how much full-budget performance the short-budget composed path retains.

### 12.3 Secondary outcomes

Report:

- exact generated tokens;
- prompt/retrieved tokens;
- prefill latency;
- decode latency;
- end-to-end latency;
- peak memory if locally measurable;
- retrieval and oracle-search calls;
- monetary cost where applicable;
- verifier failures;
- path source diversity;
- semantic distance among path nodes;
- path-order sensitivity across F permutations;
- edge-destroyed result G.

Stage 1 distinguishes **mechanistic substitution** from **economic superiority**. A path may reduce fresh decoding yet still be slower or more expensive after prefill and oracle search. That is not an economic win.

## 13. Confirmatory decision rule

The **strong SCR existence hypothesis is supported** only if all of the following hold on the frozen evaluation set:

1. full-budget arm A remains valid with accuracy at least 60%;
2. ordered path E retains at least 80% of A's accuracy: \(\rho\ge0.80\);
3. E exceeds same-fragment shuffle F by at least 5 percentage points and the paired 95% bootstrap confidence interval for \(\Delta_{shuffle}\) excludes zero;
4. E exceeds procedural abstraction D by at least 5 percentage points and the paired 95% bootstrap confidence interval for \(\Delta_{procedure}\) excludes zero;
5. E exceeds semantic top-k C by at least 5 percentage points and the paired 95% bootstrap confidence interval for \(\Delta_{semantic}\) excludes zero;
6. `B_short <= B_full / 4` as frozen before evaluation.

Use a paired non-parametric bootstrap over evaluation tasks with a fixed preregistered RNG seed and at least 10,000 resamples. Report exact paired task-level differences in addition to confidence intervals.

No multiplicity-adjusted omnibus claim is needed because the scientific claim is conjunctive: failure of any required contrast means the **strong** mechanism is not established.

## 14. Interpretation table

| Result | Interpretation |
|---|---|
| E beats B but not C | relevant retrieval helps; no evidence for path computation |
| E beats C but not F | selected fragments help; order not causal; bag-of-hints remains viable |
| E beats F but not D | order matters, but a procedural abstraction explains the useful computation |
| E beats C, D, F and retains >=80% of A under <=25% fresh budget | evidence for substitutive ordered textual state composition |
| E passes mechanism gate but total latency/cost is worse | scientific mechanism supported; economic claim not supported |
| E fails even with oracle discovery | stop before Stage 2; no evidence that a navigator has useful paths to find |

Arm G is diagnostic: if E beats G, historical topology contains additional signal worth testing in Stage 2. If E and G are equal, Stage 1 may still pass, but a transition-graph interpretation is weakened.

## 15. Operational failures and reruns

A run is operationally invalid only for preregistered failures such as:

- model/server error with no usable completion;
- corrupted memory payload;
- verifier crash;
- token-budget enforcement failure;
- wrong task/answer mapping;
- manifest mismatch.

Incorrect model answers are **not** operational failures.

Do not rerun a valid poor answer until it succeeds. Any replacement after a valid outcome is observed is a new replicate and must remain in the data.

All excluded cells and exclusion reasons must be reported.

## 16. Leakage controls

The experiment must assert mechanically that:

- evaluation answers are absent from memory records supplied to the model;
- exact evaluation task text is absent from memory source tasks when the benchmark contract requires it;
- oracle correctness scores are not placed in target-model context;
- path-discovery logs are not readable by confirmatory generation except through the frozen selected checkpoint texts;
- arm labels are not exposed to the target model;
- procedural-summary generation cannot read gold answers.

For code tasks, hidden tests may be used by the verifier but never exposed to path discovery beyond scalar correctness unless the manifest explicitly declares a richer oracle.

## 17. Evidence that would stop the programme

Do **not** proceed to a sophisticated Stage 2 navigation experiment if any of the following occurs on the frozen primary run:

- E does not beat same-fragment shuffle;
- E does not beat the procedural abstraction;
- E does not materially recover the short-budget deficit relative to A;
- apparent gains depend on one small task family and vanish under the preregistered family-stratified analysis;
- the only successful paths contain direct answer leakage or near-duplicate solutions;
- the result requires changing checkpoint granularity, model, path length, or budgets after target outcomes are visible.

Exploratory analyses may still be reported, but they do not reactivate H1.

## 18. Stage 2 gate

Stage 2 is justified only after the strong Stage 1 gate passes.

Stage 2 then asks a distinct question:

> Can a target-blind navigator find substitutive paths cheaply enough to produce net gain?

Only there should the programme introduce successor-value ranking, Semantic Atlas reachability, inverse-atlas realization, reward-conditioned functional keys, graph search, or learned policies.

## 19. Pre-registration record

This Markdown file is the conceptual preregistration. Before execution, the implementation branch must add the frozen run manifest and executable protocol. The first commit containing any target-model evaluation artifact fixes the operational protocol for that run.

No result has been collected under this preregistration as of 2026-08-21.
