---
type: "Technical Paper"
title: "Semantic Computation Reuse: Amortized Reasoning by Composing Reusable Textual States"
description: "Position paper proposing that concrete textual checkpoints from heterogeneous past LLM computations can be openly recombined so that retrieval causally displaces part of fresh inference on novel tasks."
tags: [semantic-computation-reuse, reasoning-memory, retrieval, test-time-compute, amortized-reasoning]
timestamp: 2026-08-21T19:53:00-04:00
---

# Semantic Computation Reuse: Amortized Reasoning by Composing Reusable Textual States

**Franklin Baldo**  
Independent Researcher  
franklinbaldo@gmail.com

---

> **Position paper.** This article proposes a narrow hypothesis and staged experimental programme. It reports no new empirical results. It does not claim novelty for semantic navigation, trajectory stitching, successor representations, experience graphs, reasoning memory, semantic caching, or the general proposition that past inference can be amortized. The open claim is narrower: whether concrete textual states from heterogeneous prior computations can be recombined into a previously unseen path that causally substitutes for fresh LLM inference on a novel task.

## Abstract

Large language models repeatedly pay autoregressive inference cost for computations that may overlap with work performed in earlier trajectories. Recent systems already reuse documents, strategies, procedures, episodic memories, trajectory segments, compiled reasoning programs, and internal key-value caches. These results make a broad claim that "memory can replace reasoning" too weak to be novel.

We isolate a stricter hypothesis, **semantic computation reuse (SCR)**. A corpus of prior LLM computations is segmented into concrete textual checkpoints. Each checkpoint is stored with a semantic address and provenance, and may retain observed predecessor/successor relations and downstream outcomes. On a new task whose terminal solution is not known and whose complete solution trajectory is absent from memory, a system composes checkpoints drawn from heterogeneous historical trajectories into a new ordered textual path. The path is supplied to a black-box language model, which receives a deliberately small remaining generation budget.

The central claim is causal and cost-sensitive: if the ordered retrieved path permits the model to preserve task performance while using less fresh generation than matched baselines, then some effect of earlier computation has been amortized through text. Retrieval must do more than provide useful facts or procedural hints. Same-fragment shuffles, edge-destroyed paths, semantic top-k retrieval, procedural summaries, and ordinary reasoning are therefore necessary controls.

The paper separates three questions that should not be solved at once. **Existence:** do substitutive textual paths exist even with an oracle path selector? **Navigation:** can such paths be found without knowing the destination cheaply enough to matter? **Scaling:** does a denser memory reduce the fresh inference required at fixed performance after all retrieval, prefill, storage, and build costs are counted? Failure at the first stage should stop the programme before sophisticated semantic planning is built.

**Keywords:** reasoning memory, test-time compute, amortized inference, trajectory reuse, compositional retrieval, external memory, black-box language models

---

## 1. The narrow claim

A useful reasoning-memory literature now exists. It is no longer enough to propose that prior experience can guide later reasoning, that trajectories can be recombined, or that expensive inference can be cached.

This paper claims only the following empirical possibility:

> **SCR hypothesis.** Concrete textual checkpoints from heterogeneous prior LLM computations can serve as behaviorally substitutable computation states, such that a novel ordered sequence of those checkpoints can be assembled at inference time and causally displace fresh reasoning on a held-out task.

The claim has four load-bearing parts.

1. **Concrete textual checkpoints.** The reusable object is an observed textual state from an earlier computation, not only a distilled skill, template, rule, or hidden activation.
2. **Heterogeneous provenance.** Useful states may come from different tasks and trajectories; the complete path need not have existed before.
3. **Novel composition.** The sequence used on the test task was not itself a stored solution trajectory.
4. **Computation substitution.** The retrieved path reduces new inference required at matched task performance; it does not merely improve performance while the model reasons again at roughly the same cost.

The claim is deliberately weaker than saying that text reproduces a model hidden state. A stored string is a black-box intervention. Its value is behavioral: what useful continuations become accessible after the model reads it?

## 2. What is already prior art

Several broad versions of the idea are already occupied.

### 2.1 Memory and retrieval can improve language modeling and reasoning

kNN-LM, Memorizing Transformers, RETRO, MassiveDS, and large memory layers establish that sparse non-parametric memory can improve prediction and can trade storage/retrieval against dense model capacity or compute. SCR does not claim this principle.

### 2.2 Reasoning experience can be retrieved as procedure or strategy

Agent Workflow Memory, ReasoningBank, ProcMEM, MemRL, ExpGraph, and especially *Procedural Knowledge at Scale Improves Reasoning* show that prior trajectories can be converted into reusable experience. The latter constructs roughly 32 million subquestion-subroutine entries and uses retrieved procedures as priors for fresh reasoning. ExpGraph combines graph-structured experience, utility-aware ranking, and frozen/replaceable executors. MemRL similarly separates semantic candidate recall from learned downstream utility.

These works make "semantic memory plus utility learning" prior art rather than the novelty of SCR.

### 2.3 Trajectories can be stitched or recombined

Trajectory stitching has a substantial offline-RL lineage. Work on offline RL under partial observability also connects successful stitching to representations that preserve action-relevant future behavior, including bisimulation-style conditions. In LLM agents, SE-Agent explicitly uses revision, recombination, and refinement across reasoning trajectories.

SCR therefore does not claim that cross-trajectory recombination itself is new.

### 2.4 Reasoning can be compiled and amortized

CACHE-ED2 has an LLM reason once over a document format, compile the logic into a reusable DSL program, and execute later matches without LLM inference. ReaComp compiles small sets of reasoning traces into reusable symbolic solvers that can execute with zero test-time LLM calls on supported tasks. These are strong demonstrations of amortized reasoning.

SCR differs by asking whether useful reuse is possible **without first compiling a complete reusable solver or procedure for the new task family**.

### 2.5 Internal computation can be cached and composed

KV-cache reuse already attacks redundant inference directly. C²KV goes further by learning compressed, position-agnostic KV representations that can be independently stored and concatenated. This is an important precedent for composable computation representations.

SCR asks whether ordinary text can act as a weaker but portable black-box interface for an analogous kind of composition.

## 3. Guidance is not computation substitution

The critical distinction is operational.

```text
retrieval as guidance
past computation
    ↓ distill/retrieve
strategy, fact, procedure
    ↓
NEW REASONING
    ↓
answer
```

SCR requires something stronger:

```text
past computation
    ↓ retain concrete checkpoints
x_a   x_b   x_c
 \     |    /
  \-- compose --/
       ↓
reused textual path
       ↓
small fresh-compute frontier
       ↓
answer
```

A memory system can be highly useful while failing the SCR claim. If retrieved material improves accuracy but the downstream model performs roughly the same amount of new reasoning, the mechanism is guidance.

The cleanest evidence for substitution is therefore obtained by **strangling the remaining generation budget**. If a retrieved path allows a model to succeed with a short answer-only continuation where no-memory, RAG, and procedural-hint controls require substantially more generated computation, the path has evidence of carrying reusable computational work.

## 4. Text as a portable state intervention

Let a historical reasoning trajectory contain textual checkpoints

\[
T_i=(x_{i,0},x_{i,1},\ldots,x_{i,n_i}).
\]

A frozen external encoder gives each checkpoint an address

\[
z_{i,j}=E(x_{i,j}).
\]

A memory record may retain

\[
m_{i,j}=(z_{i,j},x_{i,j},\mathrm{prev},\mathrm{next},o_{i,j},c_{i,j},p_{i,j}),
\]

where `o` records outcomes, `c` costs, and `p` provenance.

The embedding is not identified with the LLM's internal computational state. It is only an address for a real text. The text is then inserted into the model context and functions as an intervention on future generation.

This architecture matters for closed models. Exact hidden states and KV caches may be unavailable, but text remains a common interface across model families and providers.

## 5. Behavioral substitutability and continuation equivalence

Semantic proximity is not sufficient for substitutability. Two almost identical statements can imply opposite next actions. Conversely, text that is distant under a generic embedding may induce similar future behavior for a particular task.

For task distribution \(\mathcal D\), model \(M\), remaining budget \(b\), and utility \(U\), define a practical behavioral relation

\[
x \simeq_{c} y
\]

when replacing \(x\) with \(y\) preserves downstream utility under the matched continuation budget to within a declared tolerance.

This is called **continuation equivalence** here, but the underlying idea is not presented as conceptually novel. It is closely related to predictive-state equivalence and to bisimulation-style abstractions in reinforcement learning: states are grouped by the futures and decisions they preserve, not by surface identity.

The experimental implication is important:

> semantic similarity should be used for candidate recall; behavioral substitutability must be earned by downstream intervention.

## 6. The mountain as a later navigation problem

A useful terminal state may be difficult to discover from the current state under a limited generation budget. Another state may be valuable because it opens a much larger or more useful set of futures. The intuitive "mountain" is such a waypoint.

This idea has strong conceptual neighbors in successor representations, options, landmarks, reachability, and the repository's own Semantic Atlas and Agent Successor Policy work. It is therefore **not** the novelty claim of SCR.

It belongs to Stage 2: once Stage 1 establishes that substitutive textual paths exist, a navigation policy can ask which remembered waypoint is prospectively valuable when the final destination is not yet known.

A future successor-like quantity might estimate

\[
\Psi(x;b)=\text{useful future occupancy reachable from }x\text{ within budget }b.
\]

The navigation system may then combine frozen semantic candidate recall with learned functional ranking, observed transition structure, incoming trajectory, and successor value. None of this complexity is justified before the existence test passes.

## 7. Open composition

Memory may contain historical fragments

\[
A\rightarrow B\rightarrow C,
\]

\[
D\rightarrow E\rightarrow F,
\]

and

\[
G\rightarrow H\rightarrow I.
\]

SCR asks whether a new task can benefit from an unseen composition such as

\[
Q\rightarrow B\rightarrow E\rightarrow H\rightarrow Y,
\]

where the stored textual payloads for \(B,E,H\) came from distinct trajectories and were never previously concatenated.

The sequence need not be good prose. The stronger hypothesis is precisely that **textual coherence and computational usefulness can come apart**. If the same fragments work equally well after permutation, however, the correct explanation is likely a bag of semantic hints rather than a reusable trajectory.

This creates a direct causal test of order.

## 8. Three-stage programme

The research programme should proceed in increasing order of complexity.

### Stage 1 — Existence

Question:

> Do ordered combinations of concrete historical textual states ever substitute for fresh reasoning?

Use an oracle or deliberately expensive path-discovery procedure if necessary. This stage estimates an upper bound on whether the phenomenon exists at all. It does **not** claim a deployable retrieval algorithm.

The decisive outcome is task performance under sharply restricted fresh generation, compared with same-information controls.

If Stage 1 fails, stop. There is no reason to build a sophisticated semantic navigator for paths that do not have a measurable substitutive effect.

### Stage 2 — Navigation

Only after an existence result, ask:

> Can useful paths be found without knowing the terminal destination and at a cost below the inference they replace?

This stage can draw on Semantic Atlas reachability, inverse-atlas textual realization, reward-conditioned retrieval, successor representations, learned functional keys, graph search, or other planners.

### Stage 3 — Scaling

Finally ask whether memory density creates a stable memory-compute frontier:

\[
|\mathcal M|\uparrow
\quad\Rightarrow\quad
C_{\mathrm{fresh}}(U\ge U_0)\downarrow.
\]

This must include build cost, index/storage cost, lookup, path-construction compute, prompt-prefill cost, fresh decoding cost, latency, and amortization horizon.

A positive Stage 3 result would be stronger than ordinary retrieval scaling: more memory would increase the fraction of **previous computation that can be reused in novel compositions**.

## 9. Stage 1 controls that distinguish rival explanations

The companion preregistration `semantic_computation_reuse_experiment1.md` specifies the first test in detail. Its minimum arms are:

1. **fresh reasoning** — no memory;
2. **semantic top-k** — same retrieval-token budget, no trajectory structure;
3. **procedural abstraction** — a concise procedure/summary derived from comparable retrieved evidence;
4. **ordered composed path** — concrete checkpoints from heterogeneous trajectories;
5. **same-fragment shuffle** — identical fragments and token budget, order randomized;
6. **edge-destroyed composition** — same memory nodes but transition structure randomized before selection.

The primary mechanism question is not whether arm 4 has the highest unrestricted accuracy. It is whether arm 4 preserves more success than its controls when the model has little fresh generation left.

The strongest simple falsifiers are:

- ordered path = shuffled path → order carries no detectable computational work;
- ordered path = semantic top-k → navigation/topology adds nothing beyond relevant content;
- ordered path = procedural abstraction → a compact reusable procedure explains the effect;
- all retrieval arms still require the same fresh reasoning budget → memory is guidance, not substitution.

## 10. Cost accounting: amortization, not erased history

Past computation was paid once. Retrieval does not make that causal work disappear.

For memory-build cost \(C_{build}\), storage/index cost \(C_{store}\), lookup/path cost \(C_{lookup}\), input-prefill cost \(C_{prefill}\), and remaining generation cost \(C_{fresh}\), a practical claim requires a horizon \(N\) for which

\[
C_{build}+C_{store}+\sum_{n=1}^{N}(C_{lookup}+C_{prefill}+C_{fresh})
<
\sum_{n=1}^{N}C_{recompute}
\]

at matched task performance.

Stage 1 need only establish a substitutive mechanism. Stage 3 must establish the economic crossover.

This distinction also prevents a trivial token-count claim. A long retrieved path may reduce output tokens while increasing prefill FLOPs or latency. Such a result is mechanistically interesting but not yet an efficiency win.

## 11. Negative evidence is informative

Current memory systems already show that retrieval and composition can be difficult. RECON, for example, reports low performance for non-oracle systems on compositional long-context tasks involving multi-hop chains, invalidation propagation, conflicts, counterfactuals, and temporal constraints. This makes it unsafe to assume that locally useful memory fragments compose reliably.

SCR could fail for several principled reasons:

- textual interventions may be too lossy to stand in for computational states;
- continuation equivalence may be strongly model- and task-specific;
- useful substitution may not be transitive across multiple hops;
- ordering effects may wash out after the model reinterprets the whole prompt;
- the model may need to regenerate hidden dependencies even when the surface path is present;
- prefill cost may erase any decode savings;
- state density may scale too slowly to yield useful coverage.

Any of these results would narrow the role of external memory back toward procedural guidance, compiled solvers, or internal-state caches.

## 12. Relation to the existing research programme

This paper is intentionally narrower than several related manuscripts in this repository.

- **Semantic Atlas** owns the broad claim that reasoning can be studied as controlled movement through a semantic/dynamical map.
- **Inverse Atlas** explores textual realization of locally desired semantic movement from historical inference records.
- **RL Relay Transducers** already separates semantic candidate recall from reward-conditioned functional ranking.
- **Agent Successor Policy** supplies a trajectory-conditioned and successor-style account of which future behavioral regions are valuable.
- **Informational Time** supplies the distinction between historical causal work and its later compressed/indexed representation.
- **Structured Irregularity** supplies the warning that local textual incoherence can still participate in a globally useful ordered process, and that order must be tested rather than assumed.

SCR's job is not to restate those mechanisms. It asks one bridging question:

> **Can their shared object — a semantically addressable textual state — carry enough previously paid computational work that recombining such states measurably reduces new inference?**

The internal lineage is documented separately in `semantic_computation_reuse_internal_lineage.md`.

## 13. The role of semantic inversion

Embedding inversion is not required when a memory key already has a stored textual value. The text is simply retrieved.

Inversion becomes relevant only when a later navigator proposes a useful off-datastore vector waypoint for which no textual realization is stored. In that regime an inversion system, including experiments developed in Perquire, could serve as a bridge technology.

Semantic inversion is therefore downstream and optional. It is not evidence for the SCR hypothesis itself.

## 14. Claim boundary after the 2026 frontier scan

The following statements should not be presented as SCR novelty:

- memory can improve reasoning;
- vector retrieval can be cheaper than dense inference;
- experience can be ranked by downstream utility;
- trajectories can be stitched or recombined;
- future reachability can define useful state similarity;
- reasoning can be compiled and amortized;
- internal inference representations can be cached and composed.

The surviving research question is narrower:

> **Can cross-trajectory composition of concrete textual checkpoints itself perform part of a novel computation, as demonstrated by causal displacement of fresh LLM inference under matched information and cost controls?**

That statement is the working novelty boundary. The companion frontier note records the literature scan that motivated it and should be revised if closer prior art appears.

## 15. Conclusion

The interesting question is no longer whether language-model agents can remember, retrieve experience, recombine trajectories, or cache computation. They can.

The unresolved question is whether **language itself can serve as a portable cache format for partially computed reasoning**. If concrete textual states can be behaviorally substituted and openly recombined, past inference may become a non-parametric computational substrate rather than only a source of facts or advice. If ordered-state paths fail to beat same-information controls under a restricted continuation budget, the stronger interpretation should be abandoned.

The next step is therefore not a larger semantic map. It is a small, adversarial existence test designed to give the hypothesis a clean chance to die.

---

## References

Bhoi, S., Tripathi, A., Raza, A., & Jauhari, M. (2026). *CACHE-ED2: Compiling LLM Reasoning into Reusable Extraction Programs for Document Extraction at Scale*. ICML 2026 SCALE Workshop. https://www.amazon.science/publications/cache-ed2-compiling-llm-reasoning-into-reusable-extraction-programs-for-document-extraction-at-scale

Borgeaud, S., et al. (2022). *Improving Language Models by Retrieving from Trillions of Tokens*. ICML 2022. https://proceedings.mlr.press/v162/borgeaud22a.html

Dayan, P. (1993). *Improving Generalization for Temporal Difference Learning: The Successor Representation*. Neural Computation, 5(4), 613–624. https://doi.org/10.1162/neco.1993.5.4.613

Du, C., Chen, J., Tang, H., et al. (2026). *C²KV: Compressed and Composable KV Cache Reuse for Efficient LLM Inference*. https://arxiv.org/abs/2607.17715

Feng, T., Ye, C., Luo, T., et al. (2026). *ExpGraph: Model-Agnostic Experience Learning with Graph-Structured Memory for LLM Agents*. https://arxiv.org/abs/2605.30712

Guo, Y., Lin, J., Wang, H., et al. (2025). *SE-Agent: Self-Evolution Trajectory Optimization in Multi-Step Reasoning with LLM-Based Agents*. NeurIPS 2025. https://papers.nips.cc/paper_files/paper/2025/hash/a911e543a95493ae5004fdc01909043e-Abstract-Conference.html

Hong, J., Dragan, A., & Levine, S. (2024). *Offline RL with Observation Histories: Analyzing and Improving Sample Complexity*. ICLR 2024. https://proceedings.iclr.cc/paper_files/paper/2024/file/1c3d419b754cb4de0a67a453cb28d959-Abstract-Conference.html

Khandelwal, U., Levy, O., Jurafsky, D., Zettlemoyer, L., & Lewis, M. (2020). *Generalization through Memorization: Nearest Neighbor Language Models*. ICLR 2020. https://arxiv.org/abs/1911.00172

Mi, Q., Ma, Z., Yang, M., et al. (2026). *ProcMEM: Learning Reusable Procedural Memory from Experience via Non-Parametric PPO for LLM Agents*. https://arxiv.org/abs/2602.01869

Naik, A., Mathur, Y., Prakam, Rose, C., & Mortensen, D. (2026). *ReaComp: Compiling LLM Reasoning into Symbolic Solvers for Efficient Program Synthesis*. https://arxiv.org/abs/2605.05485

Ouyang, S., et al. (2026). *ReasoningBank: Scaling Agent Self-Evolving with Reasoning Memory*. ICLR 2026. https://arxiv.org/abs/2509.25140

Shriniwas Arya, M. (2026). *RECON: Benchmarking Agent Memory for Compositional Reasoning over Long Contexts*. https://arxiv.org/abs/2607.16716

Wang, Z. Z., Mao, J., Fried, D., & Neubig, G. (2025). *Agent Workflow Memory*. ICML 2025. https://proceedings.mlr.press/v267/wang25bx.html

Wu, D., Sachan, D. S., Yih, W.-t., & Chen, M. (2026). *Procedural Knowledge at Scale Improves Reasoning*. https://arxiv.org/abs/2604.01348

Wu, Y., Rabe, M. N., Hutchins, D., & Szegedy, C. (2022). *Memorizing Transformers*. ICLR 2022. https://arxiv.org/abs/2203.08913

Zhang, S., Wang, J., Zhou, R., et al. (2026). *MemRL: Self-Evolving Agents via Runtime Reinforcement Learning on Episodic Memory*. https://arxiv.org/abs/2601.03192
