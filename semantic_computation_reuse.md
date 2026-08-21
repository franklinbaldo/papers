---
type: "Technical Paper"
title: "Semantic Computation Reuse: Reasoning as Navigation over a Memory of Reusable States"
description: "Position paper proposing that past language-model computation can be stored as semantically addressable states and recombined into novel retrieval paths that substitute for part of future inference."
tags: [semantic-computation-reuse, reasoning-memory, retrieval, test-time-compute]
timestamp: 2026-08-21T00:00:00+00:00
---

# Semantic Computation Reuse: Reasoning as Navigation over a Memory of Reusable States

**Franklin Baldo**  
Independent Researcher  
franklinbaldo@gmail.com

---

> **Position paper.** This article proposes a hypothesis and experimental program. It reports no new empirical results. Claims about computation savings, state reuse, navigation, and scaling are falsifiable predictions rather than measurements.

## Abstract

Large language models repeatedly spend inference compute producing reasoning that overlaps with computation performed before. Retrieval-augmented generation reduces some redundancy by retrieving knowledge, semantic caches reuse answers to similar requests, and recent reasoning-memory systems retrieve workflows, strategies, or procedural subroutines from prior trajectories. We propose a stronger use of external memory: **semantic computation reuse**. Past textual states are embedded and stored as key-value entries, optionally together with observed transitions and outcomes. At inference time, a new computation may navigate through these stored states and concatenate their associated texts, constructing a path that need not have appeared in any previous trajectory. The retrieved path is then supplied to a language model, which resumes generation only near the frontier where new computation is required.

The central hypothesis is not that embedding proximity reproduces a language model's hidden state. Rather, some texts may be **continuation-equivalent**: conditioning on them places a model in states with sufficiently similar useful futures. A valuable retrieved state can therefore function as a computational waypoint even when it is not a solution, is not a known skill for the current problem, and is not an obvious semantic intermediate between the initial problem and the eventual answer. We call states with unusually high prospective reachability **landmark states**. A path through landmark states may be textually incoherent yet computationally useful.

This view distinguishes retrieval as **guidance** from retrieval as **computation substitution**. It predicts a measurable trade-off between memory coverage and new inference: as a datastore becomes denser and its transition structure becomes more informative, the amount of fresh generation required to reach useful terminal states may fall. We formulate falsifiers and a minimal experiment comparing ordinary reasoning, nearest-neighbor RAG, procedural-memory retrieval, novel path composition, shuffled paths, and edge-destroyed controls under compute-matched evaluation.

**Keywords:** reasoning memory, semantic retrieval, test-time compute, associative memory, trajectory reuse, compositional retrieval, non-parametric memory, language-model inference

---

## 1. The problem: computation is usually discarded

A language model solving a difficult problem may generate a long sequence of intermediate text before reaching a useful answer. Another model, or the same model later, may encounter a different problem that requires traversing part of the same conceptual region. Today, that computation is usually performed again.

This is not inevitable. Approximate nearest-neighbor lookup over a large vector store can be much cheaper than autoregressive generation. If useful intermediate computations can be made externally addressable, a system may be able to replace some fresh reasoning with retrieval.

Existing approaches already exploit weaker forms of this idea. Semantic caches reuse whole answers when a new request is sufficiently similar to an old one. Retrieval-augmented generation retrieves facts or documents. Agent memories retrieve successful workflows or distilled strategies. Procedural reasoning memories retrieve subroutines relevant to the current subproblem. These systems show that external memory can improve performance and reduce redundant work.

We ask a different question:

> **Can previously generated computation itself become a reusable substrate from which new reasoning trajectories are assembled?**

The distinction matters most on genuinely new problems. A skill is useful when a problem can be mapped to a known procedure. A cached answer is useful when the new request is sufficiently close to an old request. But a new problem may have no matching answer, workflow, or skill. It may nevertheless benefit from states that were produced in unrelated historical computations and have never before appeared together.

The proposed system therefore does not merely retrieve a previous solution. It attempts to compose a **new path through old computation**.

## 2. From reasoning traces to an external state memory

Consider a textual reasoning trajectory

\[
T = (x_0, x_1, \ldots, x_n),
\]

where each \(x_i\) is a textual checkpoint: a problem statement, partial analysis, intermediate conclusion, reformulation, hypothesis, plan, or other state-bearing text.

Let an external encoder \(E\) map each checkpoint to a vector

\[
z_i = E(x_i).
\]

A memory entry can then store at least

\[
(z_i, x_i),
\]

and may additionally store observed successors, predecessor relations, task metadata, costs, and outcomes:

\[
(z_i, x_i, \mathcal{N}^+_i, \mathcal{N}^-_i, o_i).
\]

The embedding is an **address**, not the computational state itself. This distinction is essential. A sentence embedding is not assumed to equal, reconstruct, or expose the hidden state of the language model. The stored text is instead a black-box control surface: by placing that text in context, we induce some internal state in the downstream model.

At inference time, a current textual state \(q\) is embedded and used to retrieve candidate memory entries. A conventional retrieval system would return the nearest entries and expose them as information. Semantic computation reuse instead asks whether retrieved states can be **ordered and composed as a trajectory**, after which the language model continues from the resulting context.

A new path might therefore be

\[
q \rightarrow x_a \rightarrow x_b \rightarrow x_c \rightarrow \text{fresh generation},
\]

where \(x_a\), \(x_b\), and \(x_c\) originated in three different historical reasoning traces and have never previously been concatenated.

The possibility of such a path is the core speculative claim.

## 3. Retrieval as guidance versus retrieval as computation substitution

Most reasoning-memory systems use retrieved content as **guidance**. A retrieved item says, in effect, "a similar problem was solved with this strategy; use it while reasoning." The model still performs substantial fresh inference.

Semantic computation reuse aims at a stronger operational criterion. A retrieved state is valuable when using it allows the model to **avoid recomputing a segment that would otherwise have to be generated**.

This yields a simple distinction:

- **Knowledge reuse:** retrieve information needed by the computation.
- **Procedure reuse:** retrieve a method that guides the computation.
- **Computation reuse:** retrieve a state or path that substitutes for part of the computation.

The categories can overlap, but they make different empirical claims. A procedural hint may improve accuracy while increasing prompt length and leaving generated reasoning unchanged. Computation reuse requires a cost-sensitive demonstration that retrieval actually displaces new inference while preserving useful outcomes.

The primary quantity of interest is therefore not retrieval accuracy alone. It is a frontier such as

\[
\text{memory coverage} \;\longleftrightarrow\; \text{fresh inference cost} \;\longleftrightarrow\; \text{task performance}.
\]

## 4. Continuation equivalence

Semantic similarity is not sufficient for safe state substitution. Two texts may have high cosine similarity while implying different next steps. Conversely, two lexically and semantically different texts may induce similar useful continuations.

We therefore define the central behavioral notion informally.

Two textual states \(x\) and \(y\) are **continuation-equivalent with respect to task distribution \(\mathcal{D}\), model \(M\), and utility \(U\)** when replacing one with the other preserves the distribution of useful downstream continuations closely enough for the intended application.

A strong version could compare continuation distributions directly. A practical version can be task-level and counterfactual:

\[
x \simeq_c y
\]

when conditioning on \(x\) versus \(y\), under matched remaining inference budget, yields statistically indistinguishable downstream utility.

This definition deliberately avoids claiming that the two texts have identical meanings or induce identical hidden activations. The relevant equivalence is **prospective**: what useful futures remain reachable after the substitution?

This also suggests that ordinary embedding distance should be treated as a candidate-generation heuristic, not as the ground truth metric for state reuse.

## 5. The mountain: landmark states and prospective reachability

Suppose reasoning begins in state \(A\) and a useful terminal region \(Z\) exists, but from \(A\) the model rarely discovers \(Z\) within the available inference budget. There may exist another state \(M\) that is neither the answer nor an obvious semantic midpoint between \(A\) and \(Z\), but from which \(Z\) becomes much easier to reach.

State \(M\) is analogous to a mountain: reaching it changes what can be reached next.

We call such a state a **landmark state**. Its value is not primarily retrospective similarity to the current query. Its value is **prospective reachability**: conditioning on it expands or improves the set of useful futures accessible under a bounded generation budget.

A crude prospective-value functional might be written

\[
V(M; b) = \mathbb{E}[U(Y) \mid M, \text{fresh generation budget}=b],
\]

or, when diversity of reachable useful regions matters,

\[
R(M; b) = \mu\left(\{y : y \text{ is usefully reachable from } M \text{ within } b\}\right),
\]

for an appropriate measure \(\mu\).

A landmark need not be nearest to the starting state. It may even initially move the context away from the apparent target. This is why pure greedy nearest-neighbor traversal is not the complete proposal.

Historical reasoning traces can provide more than points: they provide observed **transitions**. With enough traces, the datastore induces a directed graph whose nodes are semantically addressable textual states and whose edges represent observed or inferred reachability. The memory then becomes not only a collection of facts but an empirical map of how computation has moved through state space.

## 6. Novelty by recombination

The strongest version of the hypothesis concerns **open composition**.

Suppose memory contains trajectories

\[
A \rightarrow B \rightarrow C,
\]

\[
D \rightarrow E \rightarrow F,
\]

and

\[
G \rightarrow H \rightarrow I.
\]

A new problem need not replay any of these paths. It might construct

\[
Q \rightarrow B \rightarrow E \rightarrow H \rightarrow Y,
\]

where the sequence \(B,E,H\) never occurred historically.

The concatenated text may be poor discourse. Its fragments may come from different domains, use different terminology, or lack an obvious human narrative. The hypothesis is that discourse coherence is not the relevant criterion. The sequence may still alter the model's internal computation in a way that makes a useful terminal state easier to generate.

This yields the paper's strongest claim:

> **A sufficiently rich memory of prior computational states may create new capability through recombination, rather than merely reproduce previously solved tasks.**

If true, memory would not be only a cache. It would be a non-parametric substrate for constructing new computations.

## 7. Why this is not ordinary RAG, semantic caching, or a skill library

### 7.1 Not semantic caching

Semantic caching asks whether a new request is similar enough to an old request that the old answer can be reused. It is strongest when the desired terminal output has already been computed.

Semantic computation reuse targets cases where the terminal output is unknown and may never have existed.

### 7.2 Not ordinary RAG

RAG retrieves content relevant to the current query. If a proposed path works only because its fragments form a bag of relevant facts or concepts, ordinary RAG is a sufficient explanation and the stronger hypothesis fails.

For this reason, top-k semantic retrieval is an indispensable baseline.

### 7.3 Not a skill library

A skill encodes a reusable transformation for a recognized class of problems. Skills can efficiently move many agents into similar useful configurations, but they presuppose that the relevant procedure has already been abstracted.

Open state composition does not require a stored procedure for the new problem. Its claimed advantage is precisely that states from unrelated historical trajectories may be recombined into a useful path that no skill author or previous execution specified.

### 7.4 Not KV-cache reuse

KV-cache reuse literally reuses internal inference computation and can provide large serving speedups. It generally requires model-level access and strong compatibility conditions. Semantic computation reuse is intended to work, at least in its textual form, with black-box language-model APIs. It trades exact internal-state reuse for a weaker but portable interface: retrieved text.

The two approaches are complementary. If textual state reuse proves real, open-weight models could later test whether the same navigation principle works more efficiently with hidden-state or KV representations.

## 8. Relation to prior work

The proposal sits at the intersection of several established lines.

**Product-key and memory layers.** Lample et al. [2019] showed that very large key-value memories can add capacity with small computational overhead. More recently, Berges et al. [2025] scaled trainable memory layers to 128B memory parameters and showed that sparse lookup can outperform substantially more compute-intensive dense alternatives. These works establish that associative lookup can be a computationally efficient model component, but their memories are trained inside the model rather than assembled from external reasoning traces.

**Nearest-neighbor and retrieval language models.** kNN-LM [Khandelwal et al., 2020], Memorizing Transformers [Wu et al., 2022], RETRO [Borgeaud et al., 2022], and MassiveDS retrieval scaling [Shao et al., 2024] demonstrate that non-parametric datastores can improve language modeling and that increasing datastore scale can substitute for some parametric capacity. These systems primarily retrieve tokens, internal representations, or documents to improve prediction; they do not test novel composition of reasoning-state paths as a substitute for generated reasoning.

**Agent and procedural memory.** Agent Workflow Memory [Wang et al., 2025] induces reusable workflows from previous agent trajectories and reduces the number of steps needed on later tasks. ReasoningBank [Ouyang et al., 2026] retrieves strategies distilled from successful and failed experiences and explicitly frames memory as a dimension of test-time scaling. ProcMEM [Mi et al., 2026] learns reusable procedural skills from experience to avoid repeatedly deriving solutions in recurring scenarios. These systems provide strong evidence for experience reuse, but they primarily reuse abstractions known to be useful.

**Reasoning Memory at scale.** Wu et al. [2026] provide the closest direct precedent. They decompose reasoning trajectories into approximately 32 million subquestion-subroutine pairs, retrieve procedural knowledge inside the reasoning stream, and outperform compute-matched test-time scaling baselines. This is strong evidence that large procedural datastores can improve reasoning. The remaining distinction is that retrieved subroutines serve as procedural priors under which the model performs new reasoning. The present proposal asks whether stored states can instead be composed into **novel paths that directly displace portions of that reasoning**.

**Semantic and KV caching.** Semantic response caches reuse outputs for similar requests. CacheBlend [Yao et al., 2025] and SemShareKV [Zhao & Mastorakis, 2025] show increasingly flexible reuse of precomputed KV representations, including reuse across semantically similar but lexically different prompts. These systems directly attack redundant inference, but at the serving/state-representation level rather than through open-ended graph navigation over reasoning experiences.

The novelty claim of this position paper is therefore deliberately narrow. It is **not** that memory helps reasoning, that vector lookup is cheaper than dense inference, or that reasoning trajectories contain reusable procedures. Those claims already have substantial prior art. The open hypothesis is that **semantically addressable states from heterogeneous prior computations can be recombined into previously unseen paths whose causal effect is to reduce the fresh inference required on genuinely novel tasks**.

## 9. A minimal falsifiable experiment

A first experiment should test the recombination claim without requiring a new model architecture.

### 9.1 Datastore

Start from a public corpus of verified reasoning trajectories in at least one domain with objective outcomes, such as mathematics or code.

Segment each trajectory into checkpoints. For every checkpoint store:

1. the checkpoint text;
2. its embedding;
3. trajectory and step identifiers;
4. observed predecessor and successor edges;
5. final trajectory outcome;
6. generation-token and, where possible, latency/cost metadata.

The evaluation problems must be held out at the problem-family level as far as practical, so that simple answer or trajectory memorization is not the intended solution.

### 9.2 Arms

Use a fixed downstream language model and compare at least:

**A. No-memory reasoning.** The model solves the problem with a fixed inference budget.

**B. Top-k semantic RAG.** Retrieve the same number of fragments by direct similarity to the current problem and provide them without path structure.

**C. Procedural-memory baseline.** Retrieve a known subroutine/workflow or the closest available implementation of Reasoning Memory.

**D. Composed state path.** Construct a path through stored states using the proposed semantic/transition graph, concatenate the textual payloads, and let the model continue from the path endpoint.

**E. Same-fragment shuffle.** Use exactly the fragments from D but randomly permute their order.

**F. Edge-destroyed path.** Preserve node content and approximate similarity statistics while randomizing historical transition edges before path construction.

The last two controls are crucial. If D does not outperform E, ordering contributes little and the mechanism may reduce to bag-of-hints retrieval. If D does not outperform F, the historical topology of computation contributes little and semantic retrieval alone may explain the effect.

### 9.3 Outcomes

The primary result should be a Pareto frontier rather than accuracy alone:

- task success or exact correctness;
- fresh generated reasoning tokens;
- retrieved input tokens;
- embedding/retrieval cost;
- total inference latency and monetary/compute proxy;
- fraction of the baseline reasoning trajectory displaced by retrieval.

A useful system should improve the amount of task utility obtained per unit of **new** inference.

### 9.4 Memory scaling

Repeat the experiment with increasing datastore sizes. The key predicted curve is

\[
|M| \uparrow \quad \Rightarrow \quad C_{\text{fresh}}(U \geq U_0) \downarrow,
\]

where \(|M|\) is usable memory size and \(C_{\text{fresh}}\) is the fresh inference required to maintain a fixed utility threshold \(U_0\).

The strong version predicts more than ordinary retrieval scaling: larger memory should increase the probability of finding useful **compositional paths**, not merely better single neighbors.

## 10. Falsifiers

The proposal should be abandoned or substantially weakened if any of the following hold under well-powered, compute-matched tests.

1. **Top-k RAG matches composed paths.** Then path navigation adds no evidence beyond retrieving relevant material.

2. **Shuffling path order does not hurt.** Then the trajectory carries no detectable sequential information; the fragments function as an unordered hint set.

3. **Destroying transition edges does not hurt.** Then historical reachability is not contributing useful structure.

4. **Memory scaling improves accuracy but does not reduce fresh inference at fixed accuracy.** Then memory is useful guidance but not computation substitution.

5. **Composed paths help only on problem families already represented in memory.** Then the mechanism is closer to skill or case reuse than open recombination.

6. **Semantic proximity fails to predict continuation equivalence and no learnable retrieval criterion repairs it.** Then textual embeddings may be inadequate addresses for reusable computational states.

7. **The cost of constructing, retrieving, and ingesting paths exceeds the generation they replace.** Then the hypothesis may be scientifically true but economically uninteresting in the tested regime.

## 11. The role of semantic inversion

Embedding inversion is not required when every memory key has an associated textual value. Nearest-neighbor retrieval already returns a text that approximately addresses the desired region.

Inversion becomes relevant only in harder regimes: when a navigation algorithm identifies a useful vector-space waypoint with no stored textual realization, when interpolation or extrapolation creates an off-datastore target, or when one wants to test whether scalar feedback can synthesize a text that realizes a desired region.

Semantic inversion should therefore be treated as a possible **bridge technology** for semantic computation reuse, not as the central scientific claim.

## 12. Open problems

Several questions determine whether the proposal becomes useful or collapses into ordinary retrieval.

### 12.1 What is a state?

A sentence, a paragraph, a summarized reasoning prefix, a subproblem, and a hidden activation are different objects. The optimal granularity may depend on the downstream model and task.

### 12.2 How are landmarks found without knowing the destination?

The terminal answer to a new problem is unknown. Landmark selection therefore cannot depend on distance to a known target. Candidate criteria include historical reachability, successor diversity, outcome-conditioned centrality, learned value functions, and cheap exploration over the transition graph. This is closely related to landmark and waypoint planning in reinforcement learning.

### 12.3 Does textual incoherence matter?

A composed path may be locally addressable in embedding space yet globally nonsensical as prose. This is a feature of the hypothesis, not an implementation detail: if incoherent-but-ordered paths work, the result would separate discourse coherence from computational usefulness. If only coherent paths work, the system may reduce to a sophisticated retrieval-and-summarization pipeline.

### 12.4 Is the useful geometry semantic or dynamical?

Cosine similarity measures a static relation between representations. The relevant geometry may instead be defined by transition and reachability probabilities. A learned graph metric could outperform the original embedding space even if embeddings remain useful for candidate generation.

### 12.5 Where is the economic crossover?

Retrieval is not free. Embedding queries, ANN search, input-token prefill, storage, graph traversal, and validation all consume resources. The practical question is not whether memory can replace generation in principle, but where the total cost curve crosses that of fresh inference.

## 13. Prediction

The conservative prediction is that semantic computation reuse will work first in domains with repeated latent structure and objective verification, such as mathematics, code, tool use, and formal procedures. In these domains, historical trajectories provide dense evidence about useful transitions and failures can be detected cheaply.

The stronger prediction is a scaling effect: once memory is sufficiently dense, useful landmark states and cross-trajectory connections become common enough that the cost of reaching a productive reasoning region falls nonlinearly. Under this view, past inference becomes infrastructure. Reasoning traces are not merely logs to be summarized or discarded; they are observations of a reusable computational topology.

If this prediction is wrong, procedural memory remains the more parsimonious model: retrieve a useful skill and reason again. If it is right, a large semantic memory may do something stronger. It may allow future systems to **navigate computation that has already happened and recombine it into computation that has never happened before**.

---

## References

Berges, V.-P., Oğuz, B., Haziza, D., Yih, W.-t., Zettlemoyer, L., & Ghosh, G. (2025). *Memory Layers at Scale*. ICML 2025. https://proceedings.mlr.press/v267/berges25a.html

Borgeaud, S., et al. (2022). *Improving language models by retrieving from trillions of tokens*. ICML 2022. https://proceedings.mlr.press/v162/borgeaud22a.html

Khandelwal, U., Levy, O., Jurafsky, D., Zettlemoyer, L., & Lewis, M. (2020). *Generalization through Memorization: Nearest Neighbor Language Models*. ICLR 2020. https://arxiv.org/abs/1911.00172

Lample, G., Sablayrolles, A., Ranzato, M. A., Denoyer, L., & Jégou, H. (2019). *Large Memory Layers with Product Keys*. NeurIPS 2019. https://arxiv.org/abs/1907.05242

Mi, Q., Ma, Z., Yang, M., Li, H., Wang, Y., Zhang, H., & Wang, J. (2026). *ProcMEM: Learning Reusable Procedural Memory from Experience via Non-Parametric PPO for LLM Agents*. https://arxiv.org/abs/2602.01869

Ouyang, S., et al. (2026). *ReasoningBank: Scaling Agent Self-Evolving with Reasoning Memory*. ICLR 2026. https://arxiv.org/abs/2509.25140

Shao, R., He, J., Asai, A., Shi, W., Dettmers, T., Min, S., Zettlemoyer, L., & Koh, P. W. (2024). *Scaling Retrieval-Based Language Models with a Trillion-Token Datastore*. NeurIPS 2024. https://arxiv.org/abs/2407.12854

Wang, Z. Z., Mao, J., Fried, D., & Neubig, G. (2025). *Agent Workflow Memory*. ICML 2025. https://proceedings.mlr.press/v267/wang25bx.html

Wu, D., Sachan, D. S., Yih, W.-t., & Chen, M. (2026). *Procedural Knowledge at Scale Improves Reasoning*. https://arxiv.org/abs/2604.01348

Wu, Y., Rabe, M. N., Hutchins, D., & Szegedy, C. (2022). *Memorizing Transformers*. ICLR 2022. https://arxiv.org/abs/2203.08913

Yao, J., et al. (2025). *CacheBlend: Fast Large Language Model Serving for RAG with Cached Knowledge Fusion*. EuroSys 2025. https://arxiv.org/abs/2405.16444

Zhao, X., & Mastorakis, S. (2025). *SemShareKV: Efficient KVCache Sharing for Semantically Similar Prompts via Token-Level LSH Matching*. Findings of IJCNLP-AACL 2025. https://aclanthology.org/2025.findings-ijcnlp.25/
