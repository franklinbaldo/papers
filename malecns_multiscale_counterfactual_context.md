---
type: "Scientific Position Paper"
title: "Buying Reality Across Timescales: Active Counterfactual Context Inference with a Frozen Drosophila Male CNS Connectome"
description: "Proposes a falsifiable multiscale context architecture in which a MaleCNS-derived frozen recurrent controller may reinstall remembered context embeddings as counterfactual hypotheses and selectively pay to verify context against the external world at horizon-dependent cost."
tags: [malecns, drosophila, connectome, active-sensing, context, memory, embeddings, counterfactuals, world-models, reservoir-computing]
timestamp: 2026-09-16T21:34:00-04:00
---

# Buying Reality Across Timescales

## Active Counterfactual Context Inference with a Frozen Drosophila Male CNS Connectome

**Franklin Baldo**  
Independent Researcher

> **Scientific position paper / research agenda — 16 September 2026.** No benchmark result is claimed here. This paper specifies a falsifiable architecture, places it against neighboring prior art, and defines the first synthetic experiment needed to determine whether the mechanism is useful. The MaleCNS connectome is treated as a fixed recurrent substrate, not as a physiological simulation of a living fly.

## Abstract

Intelligent agents rarely need perfect knowledge of their entire past. They need enough context, at the appropriate temporal scale, to infer what kind of situation they currently inhabit. Yet most artificial agents either receive context passively, store history in a homogeneous memory, or imagine future trajectories from a single latent state.

We introduce **Multiscale Counterfactual Context Inference (MCCI)**, a framework in which an agent maintains explicit context channels corresponding to progressively longer temporal horizons. Each channel contains an embedding summarizing the world over its associated horizon. Crucially, these channels are not immutable memory states. The agent may temporarily replace any context level with an embedding previously observed at that same scale, thereby installing a remembered context as a hypothesis about the present. It may perform such internal counterfactual substitutions freely or cheaply, whereas obtaining the true current context from the external world requires an explicit **CHECK** operation whose energy cost increases with temporal horizon.

The agent must therefore decide not merely what to predict, but **which reality is worth purchasing**.

We propose to instantiate the controller with a frozen recurrent substrate derived from the complete male *Drosophila melanogaster* central nervous system connectome (MaleCNS), training only compact input and output interfaces. The initial benchmark asks an agent to infer a hidden context level while selectively observing other levels under an energy budget. We describe synthetic hierarchical worlds, counterfactual context operations, controls against randomized recurrent substrates and conventional learned recurrent networks, and falsifiable hypotheses concerning active information acquisition.

The resulting framework tests whether a large fixed biological recurrent graph can learn not merely to retain context, but to navigate among possible contexts and strategically decide when imagination should be replaced by observation.

## 1. Motivation

A current observation does not uniquely determine its context.

The same sensory state may occur during the beginning or end of an episode, inside different tasks, under different long-term goals, or as part of different environmental regimes. The meaning of the present therefore depends on events unfolding at multiple temporal scales.

Artificial agents commonly address this problem by preserving a history window, recurrent hidden state, external memory, hierarchical state, or latent world state. Hierarchical recurrent architectures explicitly represent multiple temporal scales. Predictive-coding theories similarly motivate progressively slower and more contextual representations. Multiscale successor representations provide another formal route to maintaining predictions over different horizons.

These approaches usually answer a question of the form:

> What representation of history should an agent maintain?

We study a different question:

> Given multiple possible histories, which history should the agent temporarily believe, and which part of reality is worth checking?

This distinction turns context from passive state into an **actionable variable**.

Consider an agent maintaining several context channels. Level 0 summarizes the immediate present, level 1 a short episode, level 2 a longer scene, and so forth. The true context at every scale exists in the environment, but the agent does not receive all levels continuously.

Instead, the agent may perform three operations:

- **KEEP** — retain the current hypothesis at a level;
- **IMAGINE** — replace a context level with another embedding previously observed at that same level;
- **CHECK** — query the environment for the actual current context embedding at that level.

Internal imagination need not access the external world. CHECK does, and therefore incurs an explicit cost.

Longer temporal horizons receive larger observation costs. Under a fixed budget, the agent cannot continually request perfect context at every scale. It must exploit relationships among scales, test hypotheses internally, and selectively ground those hypotheses in reality.

The proposed cognition loop is therefore:

\[
\text{remember}
\rightarrow
\text{imagine}
\rightarrow
\text{discriminate}
\rightarrow
\text{check}
\rightarrow
\text{revise}.
\]

## 2. Prior art and claim boundary

The individual ingredients of MCCI are not new. The claim must therefore be deliberately narrow.

### 2.1 Hierarchical and multiscale temporal representations

Hierarchical Multiscale Recurrent Neural Networks introduced mechanisms by which different parts of a recurrent network update at different effective timescales. Predictive-coding models likewise produce increasingly slow or abstract representations across hierarchical levels. Multiscale successor representations encode expected future occupancy under different discount horizons.

MCCI inherits the motivation for multiscale state representation but makes the levels explicitly and independently manipulable by the agent.

### 2.2 Costly observation and active sensing

Controlled-observation POMDPs and active-sensing methods already formulate sensing as a decision with nonzero cost. A controller may choose whether, when, or which variable to observe according to expected value of information.

MCCI does not claim costly observation as new. Its distinction is that the queried variables are explicit **temporal-context levels**, coupled to an internal mechanism that can first install counterfactual remembered contexts and then use their consequences to decide what should be checked.

### 2.3 Latent imagination and world models

World-model systems such as *World Models* and Dreamer allow agents to simulate trajectories in latent space rather than repeatedly interacting with the external environment.

The principal counterfactual axis in MCCI is different. The agent need not only ask what future follows from the current latent state. It may ask:

> What would the present imply if my context at horizon \(H_k\) were the same as a particular context I encountered before?

The manipulated variable is therefore an explanatory context over the recent past, not only a prospective future trajectory.

### 2.4 Context reinstatement and episodic retrieval

Temporal Context Model and retrieved-context models formalize the reinstatement of contextual states associated with earlier experience. Empirical work on episodic memory likewise studies neural reinstatement during retrieval.

MCCI adopts context reinstatement as an explicit **action** over a multiscale state hierarchy rather than treating reinstatement only as a consequence of recall.

### 2.5 Replay and prioritized memory access

Replay can be prioritized according to expected utility for learning or planning. Mattar and Daw's normative account is particularly relevant because it treats access to memory as a resource-allocation problem.

MCCI differs in what is done with the retrieved episode: a remembered context can overwrite one level of the agent's current context hypothesis while the rest of the context stack remains unchanged.

### 2.6 Resource-rational cognition

Resource-rational models frame cognition as optimization under limited computational or informational budgets. This motivates the explicit observation-energy term in MCCI.

The cost schedule in the first experiment is synthetic and should not be interpreted as literal biological metabolism. It is an experimental mechanism for forcing the agent to decide which uncertainty deserves external resolution.

### 2.7 Narrow novelty claim

The proposed contribution is **not** any of the following in isolation:

- memory at multiple timescales;
- active sensing;
- context retrieval;
- replay;
- latent imagination;
- resource-rational inference;
- biological recurrent reservoirs.

The proposed unit is their operational composition:

1. the agent maintains an explicit stack of context embeddings indexed by temporal horizon;
2. each level is a manipulable internal variable;
3. previously observed embeddings from the same level can be installed as counterfactual hypotheses;
4. the recurrent controller may evolve under these counterfactual context assignments;
5. the agent then chooses which context levels to verify externally;
6. verification has horizon-dependent cost;
7. reward depends jointly on inference quality and purchased information.

A literature search snapshot on 16 September 2026 found close ancestors for each component but did not identify a work combining all seven into the same intervention space. This is a provisional novelty statement, not proof of priority.

## 3. Multiscale Counterfactual Context Inference

### 3.1 Context hierarchy

Let the environment produce an observation sequence

\[
x_1,x_2,\ldots,x_t.
\]

Define \(K\) context levels. Each level \(k\) has horizon

\[
H_k = H_0 b^k,
\]

for \(b>1\).

A context encoder \(E_k\) maps the corresponding history onto an embedding:

\[
c_t^{(k)} = E_k(x_{t-H_k+1:t}) \in \mathbb{R}^{d}.
\]

The complete external context is

\[
C_t = \{c_t^{(0)},c_t^{(1)},\ldots,c_t^{(K-1)}\}.
\]

The agent, however, maintains an internal hypothesis stack

\[
\tilde C_t = \{\tilde c_t^{(0)},\ldots,\tilde c_t^{(K-1)}\},
\]

which need not equal \(C_t\).

This disagreement is intentional. It is the space in which counterfactual reasoning occurs.

### 3.2 Example horizons

A first benchmark can use geometric horizons:

| Level | Horizon | Interpretation | CHECK cost |
|---|---:|---|---:|
| 0 | 1 | immediate state | 1 |
| 1 | 4 | micro-context | 2 |
| 2 | 16 | local episode | 4 |
| 3 | 64 | scene | 8 |
| 4 | 256 | episode | 16 |
| 5 | 1024 | regime | 32 |
| 6 | 4096 | long-range regime | 64 |

The particular numbers are not theoretically privileged. What matters is that context levels correspond to distinct horizons and that CHECK cost increases monotonically with horizon.

### 3.3 Episodic context memory

For each scale \(k\), the agent maintains a memory

\[
\mathcal{M}_k = \{c_{\tau_1}^{(k)},c_{\tau_2}^{(k)},\ldots\}
\]

containing context embeddings encountered previously at that same temporal scale.

A retrieval mechanism supplies candidate memories

\[
R_t^{(k)} \subset \mathcal{M}_k.
\]

The first implementation should expose only a small candidate set, for example 8–16 memories per level, selected by a fixed nearest-neighbor retriever. This keeps the action space tractable while separating retrieval quality from recurrent-control quality.

A later experiment may allow the controller itself to learn retrieval.

### 3.4 Context actions

At every internal reasoning step, the controller selects an operation.

#### KEEP

\[
\tilde c_t^{(k)} \leftarrow \tilde c_t^{(k)}.
\]

No external information is obtained.

#### IMAGINE

For candidate \(m_j^{(k)}\in R_t^{(k)}\),

\[
\tilde c_t^{(k)} \leftarrow m_j^{(k)}.
\]

The agent therefore behaves temporarily as though the present belonged to the remembered context.

This operation does not assert that the memory is correct. It installs a hypothesis.

#### CHECK

\[
\tilde c_t^{(k)} \leftarrow c_t^{(k)}.
\]

CHECK obtains ground truth from the environment and incurs energy

\[
e_k = e_0 f(H_k),
\]

where \(f\) is monotonically increasing. A simple first schedule is

\[
e_k=e_0 2^k.
\]

### 3.5 Action representation

A complete action can be represented as

\[
a_s = (k, o, j),
\]

where

- \(k\) is the context level;
- \(o\in\{\text{KEEP},\text{IMAGINE},\text{CHECK}\}\);
- \(j\) identifies a candidate memory when \(o=\text{IMAGINE}\).

The controller may take several internal actions before making its final target estimate.

## 4. MaleCNS as a fixed recurrent controller

The complete male *Drosophila melanogaster* central nervous system connectome provides a large recurrent graph spanning the brain and ventral nerve cord. The public resource exposes neuron annotations, synaptic connectivity, and associated representations suitable for programmatic analysis.

The experiment does **not** assume that a simple artificial recurrence over the connectome reproduces living fly physiology. The connectome supplies a structured recurrent operator. Neural dynamics, normalization, sensory injection, leak, gain, activation function, and readout are engineered.

Let

\[
W_{\mathrm{fly}}
\]

denote a normalized recurrent operator derived from the connectome. Its recurrent weights remain frozen.

A generic state update is

\[
h_{s+1}
= \phi\bigl(
(1-\lambda)h_s
+ \lambda(gW_{\mathrm{fly}}h_s + B_\theta u_s + b_\theta)
\bigr),
\]

where:

- \(h_s\) is recurrent state;
- \(u_s\) contains the current hypothesized context stack, observation budget, target identifier, and candidate-memory features;
- \(g\) controls recurrent gain;
- \(B_\theta\) is a trainable input adapter;
- \(\phi\) is the engineered activation function.

A trainable output adapter produces both the context-action policy and final estimate:

\[
(\pi_\theta,\hat c^{(q)}) = G_\theta(h_s).
\]

The first experiment should keep the recurrent connectome operator fixed and train only the surrounding interfaces.

This isolates the question of whether useful context-control dynamics can be induced **through** the fixed topology.

## 5. The context deduction task

Each episode specifies a target level \(q\).

Its true context

\[
c_t^{(q)}
\]

is hidden.

In the strongest version of the benchmark, CHECK on the target itself is forbidden. The agent must infer the target from relationships among the remaining levels.

For example, if level 4 is the target, the agent may inspect or imagine levels 0–3 and 5–6 but must ultimately produce

\[
\hat c_t^{(4)}.
\]

A simple terminal prediction reward is

\[
R_{\mathrm{pred}}
= \cos(\hat c_t^{(q)},c_t^{(q)}).
\]

Total reward includes information cost:

\[
R
=
R_{\mathrm{pred}}
-
\lambda_E\sum_s e_{k_s}
\mathbf{1}[a_s=\mathrm{CHECK}(k_s)].
\]

No explicit penalty for internal IMAGINE operations is needed in the first experiment. The primary question concerns acquisition of external information.

A later benchmark can add internal-compute cost.

## 6. Synthetic hierarchical world

The first benchmark should deliberately avoid natural-language, visual, or embodied complexity.

We require a world whose causal hierarchy is known.

Let the highest latent level \(z^{(K-1)}\) evolve slowly. Every lower level changes more rapidly while being conditioned on its parent:

\[
p(z_t^{(k)})
=
p(z_t^{(k)}\mid z_{t-1}^{(k)},z_t^{(k+1)}).
\]

Finally,

\[
x_t\sim p(x_t\mid z_t^{(0)}).
\]

One intuitive interpretation is

\[
\text{era}
\rightarrow
\text{environment}
\rightarrow
\text{episode}
\rightarrow
\text{scene}
\rightarrow
\text{event}
\rightarrow
\text{frame}.
\]

Each scale therefore carries information about neighboring scales while remaining imperfectly predictable from them.

The hierarchy must contain deliberate ambiguity. Multiple long-term contexts should sometimes produce nearly identical short-term observations. Without such ambiguity, active context acquisition is unnecessary.

### 6.1 Required properties of the synthetic generator

The first generator should satisfy five properties:

1. **Known ground truth.** Every latent level and true context embedding is recorded.
2. **Cross-scale dependence.** Neighboring levels are informative but not deterministic copies.
3. **Aliasing.** Different high-level regimes can generate similar low-level states.
4. **Reusable motifs.** Contexts recur often enough that episodic reinstatement has something meaningful to retrieve.
5. **Controlled difficulty.** The ambiguity and transition entropy can be swept systematically.

## 7. Why counterfactual context substitution matters

Suppose the current long-range context is unknown.

The agent retrieves a previously observed context \(m_A^{(5)}\) and installs it:

\[
\tilde c^{(5)} \leftarrow m_A^{(5)}.
\]

The recurrent system evolves.

Its resulting internal activity may imply that the observed short-range contexts are plausible under hypothesis \(A\).

The agent can then install another hypothesis:

\[
\tilde c^{(5)} \leftarrow m_B^{(5)}.
\]

If hypothesis \(B\) creates a different recurrent state, the controller may decide that a cheap CHECK at level 2 is sufficient to discriminate between \(A\) and \(B\).

Thus imagination does not replace sensing.

It chooses **which sensing operation becomes informative**.

This is the central mechanism of MCCI.

### 7.1 Memory as hypothesis rather than record

An episodic context has at least three computational roles:

\[
\text{record}
\rightarrow
\text{hypothesis}
\rightarrow
\text{probe}.
\]

It begins as a record of something previously encountered.

It can later become a candidate explanation for the present.

The consequences of temporarily adopting that explanation can then determine what the agent chooses to inspect in reality.

## 8. Evaluation

Performance must not be represented by raw task accuracy alone.

A successful agent should reconstruct context while minimizing expensive contact with the world.

We therefore measure prediction similarity

\[
S = \cos(\hat c^{(q)},c^{(q)}),
\]

total purchased information

\[
E = \sum_s e_{k_s},
\]

and the Pareto frontier

\[
\text{prediction quality}
\quad\text{vs.}\quad
\text{observation energy}.
\]

Additional measurements should include:

- number of CHECK operations by level;
- prediction quality under fixed energy budgets;
- regret relative to an oracle observation policy;
- frequency and duration of IMAGINE operations;
- frequency of hypothesis switches;
- probability that an imagined context survives subsequent evidence;
- improvement from IMAGINE before the first CHECK;
- robustness to highly similar distractor memories;
- calibration of target uncertainty before and after CHECK;
- mutual information between selected CHECK level and latent ambiguity state.

A useful derived metric is **reality efficiency**:

\[
\eta_R
=
\frac{S-S_{\mathrm{no\ observation}}}{E+\epsilon}.
\]

This measures how much additional correct inference is extracted per unit of purchased reality.

The primary result should still be reported as a quality-cost curve rather than compressed into a single scalar whenever possible.

## 9. Baselines

The primary scientific comparison is not merely MaleCNS versus one arbitrary neural network.

The benchmark should distinguish at least three explanations:

1. the task formulation itself is sufficient;
2. any large recurrent substrate is sufficient;
3. specific structure in MaleCNS contributes.

Required controls include the following.

### 9.1 Full-observation oracle

Receives every non-target context level for free.

This establishes the information ceiling of the task.

### 9.2 Zero-observation model

Must infer the target without CHECK.

This measures how much can be obtained from initial context and memory alone.

### 9.3 Fixed sensing schedules

Policies such as cheapest-first, nearest-level-first, and longest-horizon-first establish simple nonadaptive controls.

### 9.4 Greedy information policy

A model estimates immediate expected information gain per unit CHECK cost and selects the best current ratio without multistep planning.

### 9.5 GRU/LSTM controller

Receives the same context stack, candidate memories, action space, and budget.

### 9.6 Small Transformer controller

Receives exactly the same interface and observation contract.

### 9.7 Random recurrent reservoir

Replaces MaleCNS with a matched random recurrent operator.

### 9.8 Degree-preserving rewiring

Preserves node count, directed in/out-degree structure and relevant weight statistics while destroying higher-order connectome topology.

### 9.9 Weight or sign perturbation

Where the chosen MaleCNS representation supports it, preserve topology while perturbing edge attributes.

### 9.10 Same-topology open-loop control

Allow the recurrent substrate to process current context but forbid IMAGINE actions. This separates recurrence from explicit counterfactual intervention.

## 10. Ablations

The framework permits unusually clean ablations.

### 10.1 No imagination

Remove IMAGINE while retaining CHECK.

If performance is unchanged at matched energy, counterfactual context substitution is unnecessary.

### 10.2 No active sensing

Provide a fixed CHECK schedule.

If performance is unchanged, learned information acquisition is unnecessary.

### 10.3 Flat context

Collapse all temporal scales into one embedding.

If performance is unchanged, the context hierarchy is unnecessary.

### 10.4 Equal observation cost

Set

\[
e_0=e_1=\dots=e_{K-1}.
\]

This tests whether behavior genuinely exploits the scale-cost structure.

### 10.5 Random memories

Replace retrieved historical contexts with unrelated vectors.

This determines whether episodic structure matters beyond generic perturbation.

### 10.6 Same-scale shuffled memories

Preserve the empirical embedding distribution at each level while destroying correspondence to real past contexts.

### 10.7 No recurrence

Feed the same context-action sequence into a feed-forward controller with similar trainable parameter count.

### 10.8 Rewired MaleCNS

Destroy higher-order biological topology while preserving selected low-order graph statistics.

This is the critical control for any MaleCNS-specific claim.

## 11. Falsifiable hypotheses

The work should begin with hypotheses, not conclusions.

### H1 — Selective grounding

When CHECK operations have nonzero cost, trained agents will learn a nonuniform observation policy rather than uniformly querying all levels.

### H2 — Horizon-dependent acquisition

Long-horizon contexts will usually be checked less frequently than short-horizon contexts, except when their expected informational value outweighs their higher cost.

### H3 — Counterfactual efficiency

Allowing IMAGINE operations will improve prediction quality at matched external observation cost.

### H4 — Adaptive scale selection

The level queried will depend on the current ambiguity state rather than only on the identity of the target level.

### H5 — Episodic specificity

Replacing meaningful remembered contexts with random or same-scale shuffled vectors will reduce the value of imagination.

### H6 — Counterfactual-to-sensing coupling

The distribution of subsequent CHECK actions will depend on which memories were previously installed through IMAGINE.

This distinguishes meaningful hypothesis testing from decorative replay.

### H7 — Connectome contribution

The frozen MaleCNS recurrent substrate will differ reproducibly from topology-destroying controls on prediction-energy efficiency, learning dynamics, or both.

H7 is deliberately neutral about direction. Failure of MaleCNS to outperform matched graph controls is a valid result.

## 12. First preregistered experiment

The first experiment should be small enough to run many seeds and simple enough that every source of advantage is inspectable.

### 12.1 Environment

Use a six- or seven-level hierarchical latent generator with geometric timescales and controlled cross-level aliasing.

### 12.2 Embeddings

The first version should avoid powerful pretrained encoders. Each true latent state can map through a fixed random projection plus controlled noise to produce \(d\)-dimensional normalized context embeddings.

This prevents a pretrained semantic model from becoming an uncontrolled source of structure.

### 12.3 Memory

Populate a per-level episodic store from previous training episodes. At each reasoning step expose a fixed number of candidate past embeddings returned by a deterministic nearest-neighbor index.

### 12.4 Training

Train only the input adapter, action/readout heads, and any explicitly declared small controller parameters around the frozen recurrent substrate.

The MaleCNS recurrent operator itself remains fixed.

### 12.5 Primary comparison

The primary curve is

\[
\text{target cosine similarity}
\quad\text{versus}\quad
\text{mean CHECK energy}.
\]

The key mechanistic comparison is MCCI with IMAGINE versus the same controller without IMAGINE at matched observation cost.

The key biological-topology comparison is MaleCNS versus a degree-preserving topology null under the same interface and training budget.

### 12.6 Seeds

Use paired seeds across all controller arms so that environment generation, initial adapters, candidate memories, and task instances are shared wherever technically possible.

### 12.7 Promotion criterion

Do not promote the architecture to language, video, Doom, or other complex domains unless at least one of the following survives multiple seeds:

1. IMAGINE improves the quality-cost frontier over the no-imagination ablation; or
2. learned sensing improves the quality-cost frontier over fixed sensing schedules; or
3. analysis demonstrates a clear state-dependent policy in which imagined hypotheses predict which level is checked next.

MaleCNS-specific superiority is **not** required to promote MCCI as an architecture. It is a separate empirical question.

## 13. Interpretation

The proposed agent does not attempt to remember everything continuously.

Instead, it maintains a collection of possible explanations of the present distributed across temporal horizons.

Past contexts become reusable hypotheses.

The resulting system can ask something resembling:

> If the long-range situation were like episode 37, what should the shorter-range world look like now?

It can then compare that induced internal state against another hypothesis and purchase only the piece of reality expected to distinguish between them.

This yields a different conception of memory from passive long-context processing.

The history is not simply supplied to the model. The agent actively negotiates how much historical truth it requires.

## 14. Relation to biological cognition

The framework should not be interpreted as claiming that *Drosophila* literally implements the proposed context hierarchy or CHECK operation.

MaleCNS is used as a computational substrate whose topology came from a biological nervous system rather than gradient descent on this task.

Nevertheless, the framework is conceptually adjacent to biological observations concerning multiple predictive timescales, episodic context reinstatement, active sensing, and replay. Those analogies motivate experiments; they do not establish mechanistic identity.

The appropriate scientific claim, if any, must come from matched topology controls rather than from biological storytelling.

## 15. Limitations

Several limitations should be explicit from the beginning.

First, a connectome specifies anatomical connectivity, not complete neural dynamics. Neurotransmitter effects, neuromodulation, membrane properties, timing, plasticity, gap junctions, and many other physiological variables are absent or only partially represented in a simple recurrent operator.

Second, context levels are engineered variables. Their usefulness would not demonstrate that biological organisms encode context in the same format.

Third, the imposed energy schedule is synthetic. It studies resource allocation rather than literal metabolic expenditure.

Fourth, the external encoder defines what information is available at each level. A poor encoder could artificially create or erase cross-scale structure.

Fifth, success of MCCI would not imply success of MaleCNS specifically. The architecture and the recurrent substrate are separable hypotheses.

Sixth, a positive MaleCNS result would require strong random, degree-preserving, weight-perturbed and conventional learned-controller baselines before any claim about biological topology.

Finally, the first synthetic hierarchy is intentionally simpler than language, vision, or embodied behavior. That simplicity is an advantage for causal interpretation but limits immediate ecological claims.

## 16. Extensions

Once the mechanism is established in a synthetic world, the same interface can be transferred to richer domains.

### 16.1 Text

Levels might summarize byte span, sentence, paragraph, document, conversation segment, and long session. The target task could ask the agent to reconstruct or classify a hidden level while paying to retrieve selected longer-range context.

### 16.2 Video

Levels might represent frame, local motion, action, scene, episode, and narrative regime.

### 16.3 Embedding translation

A context hierarchy can be defined directly across semantic embedding streams. The controller could reason over alternate remembered semantic states before deciding which external encoder or scale to recompute.

### 16.4 Embodied worlds

Levels could encode immediate sensor state, maneuver, local behavioral episode, room, environment, and mission.

### 16.5 Doom-like environments

A short level might describe current geometry while longer levels represent room, region, mission state, navigation history, or behavioral phase. Expensive CHECK actions could correspond to reconstructing larger maps or querying longer-range memory traces.

The defining constraint remains unchanged:

> the agent may cheaply entertain alternative contexts but must pay to establish which context is actually true.

## 17. What would count as failure?

A useful research proposal must admit clear failure.

MCCI would lose much of its motivation if:

- IMAGINE does not improve the quality-cost frontier relative to no-imagination controls;
- sensing policies collapse to a fixed schedule independent of internal state;
- random remembered embeddings work as well as true episodic contexts;
- the optimal policy simply buys the most informative level immediately, making internal counterfactual reasoning irrelevant;
- the hierarchy provides no advantage over one flat latent state;
- performance gains disappear under a fair accounting of additional action steps or trainable parameters.

A MaleCNS-specific hypothesis would fail if topology-destroying or conventional recurrent controls match it under paired conditions.

These failures should be published rather than hidden, because they identify which component of the composite idea actually carries information.

## 18. Conclusion

We propose Multiscale Counterfactual Context Inference, an agent architecture in which temporal context is divided into explicit horizons and treated as a controllable internal variable.

Rather than merely retrieving memories, the agent may install a past context as a hypothesis.

Rather than continuously observing all context, it may selectively purchase external evidence.

Rather than treating imagination and perception as competing strategies, the architecture uses imagination to decide what perception is worth acquiring.

The first experiment asks a frozen MaleCNS-derived recurrent network to infer hidden context under an observation budget and compares it against conventional recurrent controllers, non-imagining variants, and randomized graph controls.

The core question is:

> **Can an agent learn to distinguish when it should trust an imagined context from when it should spend energy to ask reality?**

If so, memory becomes more than storage.

It becomes a space in which alternative worlds can be temporarily inhabited, cheaply tested, and selectively grounded.

## References

1. Berg, S. et al. **Sexual dimorphism in the complete Drosophila male central nervous system connectome.** *Cell* (2026). DOI: https://doi.org/10.1016/j.cell.2026.08.015
2. Chung, J., Ahn, S., & Bengio, Y. **Hierarchical Multiscale Recurrent Neural Networks.** arXiv:1609.01704 (2016). https://arxiv.org/abs/1609.01704
3. Ha, D. & Schmidhuber, J. **World Models.** arXiv:1803.10122 (2018). https://arxiv.org/abs/1803.10122
4. Hafner, D. et al. **Dream to Control: Learning Behaviors by Latent Imagination.** ICLR (2020). https://arxiv.org/abs/1912.01603
5. Howard, M. W. & Kahana, M. J. **A Distributed Representation of Temporal Context.** *Journal of Mathematical Psychology* 46(3), 2002.
6. Mattar, M. G. & Daw, N. D. **Prioritized memory access explains planning and hippocampal replay.** *Nature Neuroscience* 21, 1609–1617 (2018). https://doi.org/10.1038/s41593-018-0232-z
7. Ólafsdóttir, H. F., Bush, D., & Barry, C. **The Role of Hippocampal Replay in Memory and Planning.** *Current Biology* 28(1), R37–R50 (2018). https://doi.org/10.1016/j.cub.2017.10.073
8. Yoon, J., Jordon, J., & van der Schaar, M. **ASAC: Active Sensing using Actor-Critic models.** MLHC / PMLR 106 (2019). https://proceedings.mlr.press/v106/yoon19a.html
9. Zhou, H. et al. **Timing as an Action: Learning When to Observe and Act.** AISTATS / PMLR 238 (2024). https://proceedings.mlr.press/v238/zhou24c.html
10. Wu, W. & Arapostathis, A. **Optimal Sensor Querying: General Markovian and LQG Models With Controlled Observations.** *IEEE Transactions on Automatic Control* (2008).
11. Lieder, F. & Griffiths, T. L. **Resource-rational analysis: Understanding human cognition as the optimal use of limited computational resources.** *Behavioral and Brain Sciences* 43, e1 (2020).
12. Dutta, S., Ramachandran, S. N., & Sra, S. **Active Inference as Context Acquisition for AI Agents.** arXiv:2608.19202 (2026). https://arxiv.org/abs/2608.19202
