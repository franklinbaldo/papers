---
type: "Technical Paper"
title: "Language as a Higher-Order Agent: Reconstructive Memory, Bounded Readout, and Human–LLM Symbiosis"
description: "Position paper proposing a falsifiable higher-order-agent account of shared language: a distributed inferential process reconstructed at each time from world traces and compressed history, increasingly co-realized by humans and language models."
tags: [language-agent, active-inference, free-energy-principle, collective-world-model, llm-symbiosis, semantic-memory, compression, semantic-atlas]
timestamp: 2026-08-15T02:20:00Z
---

# Language as a Higher-Order Agent: Reconstructive Memory, Bounded Readout, and Human–LLM Symbiosis

**Franklin Baldo**  
Independent Researcher  
franklinbaldo@gmail.com

---

> **Position paper and experimental programme.** This manuscript proposes a coarse-grained account of shared language as a candidate higher-order inferential agent. It does **not** claim that language is conscious, sentient, biologically alive, or already proven to instantiate a Markov blanket. It distinguishes established results in active inference, collective predictive coding, communication, information bottleneck theory, and semantic memory from the new hypotheses proposed here. All claims about higher-order agency, substrate invariance, reconstructive memory, and human–LLM symbiosis are hypotheses until supported by the experiments described below.

## Abstract

Human language has long functioned as an external medium through which embodied agents exchange observations, preserve traces of the past, coordinate action, and build increasingly compressed models of the world. Large language models introduce a new condition: sophisticated semantic transformations can now occur in a non-human computational substrate and re-enter the same shared linguistic environment. Once an LLM output is read, copied, indexed, cited, executed, incorporated into a decision, or supplied to another model, it becomes part of the causal environment from which subsequent human and machine inferences are made.

This paper asks whether that coupled process admits a scientifically useful coarse-graining in which the relevant higher-order agent is neither a human nor an LLM, but the **shared linguistic-semantic process itself**. We call this the **Language-Agent Hypothesis (LAH)**. The proposal extends, but is stronger than, the Collective World Model hypothesis: language is not only an externalized representation produced by a society of agents; under specified empirical conditions, its evolving shared state may constitute the internal state of a persistent higher-order inferential process whose realization moves across humans, machines, documents, institutions, and other media.

Three ideas make the hypothesis testable. First, there need not be one universal semantic map: individual brains and models may maintain distinct representations that remain partially aligned because they are updated by a common world and by one another. Second, history is treated operationally as **reconstructible past**, not necessarily as verbatim storage. If a compressed generative state can answer the same relevant historical queries as an explicit archive under the same readout budget, lookup and reconstruction are functionally equivalent for the agent. Third, finite readout bandwidth creates pressure for multiscale compression: as recorded history grows faster than any bounded reader can inspect it, older information must increasingly be preserved as episodes, narratives, concepts, regularities, and models rather than as uniformly accessible raw records.

The paper derives falsifiable predictions about cross-substrate semantic trajectories, provenance ablation, causal incorporation of LLM outputs, temporal compression, historical reconstruction, and collective uncertainty reduction. It also defines a proposed **semantic market share** in terms of causal influence on future shared states rather than raw token volume. The claim fails if the apparent collective dynamics are fully explained by independent agents exchanging messages, if no higher-order state improves prediction under matched complexity budgets, or if putative human–LLM symbiosis reduces to disconnected outputs that do not causally re-enter the shared environment.

**Keywords:** active inference, free energy principle, language, collective world model, human–AI symbiosis, semantic memory, information bottleneck, predictive information, cultural evolution, large language models, semantic trajectories

---

## 1. The proposal

### 1.1 From language as medium to language as candidate agent

The ordinary description of communication begins with agents:

\[
A_1 \rightarrow m \rightarrow A_2,
\]

where an agent emits a message \(m\) that another agent receives. Language is the medium between pre-existing agents.

This paper asks whether, at a slower and coarser scale, another description becomes useful:

\[
L_t \rightarrow L_{t+1},
\]

where \(L_t\) denotes a macroscopic state of a shared linguistic-semantic process, and humans, LLMs, books, websites, institutions, sensors, and tools are among the mechanisms through which the transition is realized.

The hypothesis is not that humans cease to be agents. Multiscale systems may admit more than one useful level of agency. A cell can participate in an organism without ceasing to have a describable boundary; a human can participate in an institution without becoming physically indistinguishable from it. The empirical question is whether a higher-order description of the coupled linguistic process provides explanatory and predictive leverage that is not obtained merely by concatenating independent-agent descriptions.

We call this proposal the **Language-Agent Hypothesis (LAH)**:

> **Language-Agent Hypothesis.** At an appropriate temporal and semantic coarse-graining, the shared linguistic-semantic process generated by interacting embodied agents and computational language systems can exhibit the statistical and dynamical properties of a higher-order inferential agent: it maintains a compressed model of the world, updates that model from observations and traces, generates actions that alter future observations, and persists across changes in the lower-level substrates that realize its transitions.

The phrase **“we are language”** is used in this manuscript only as shorthand for this coarse-graining claim. It is not a claim about phenomenal consciousness.

### 1.2 What changed with LLMs?

Language has always crossed physical substrates: speech, handwriting, print, radio, magnetic storage, silicon memory, and network packets all carry linguistic states. What is new is not that silicon can store language. What is new is that a computational substrate can now perform broad, context-sensitive semantic transformations and return them to the shared linguistic environment at scale.

An isolated forward pass whose output is never observed has almost no linguistic consequence beyond its local physical dissipation. An output that enters a conversation, repository, article, search index, decision, software system, or later model context is different. It participates causally in future inference.

The relevant transition is therefore not

\[
\text{human language} \rightarrow \text{machine language},
\]

but a change in the realization of one coupled process:

\[
\text{shared language}_{\text{mostly human transformations}}
\rightarrow
\text{shared language}_{\text{human + machine transformations}}.
\]

This is the proposed sense of **human–LLM symbiosis** in the present paper. It does not require mutual biological dependence. It requires recurrent causal coupling through a shared semantic environment.

### 1.3 Scope boundaries

The proposal makes five deliberate exclusions.

First, it does **not** claim that language is conscious. Higher-order agency, if established, would not by itself imply subjective experience.

Second, it does **not** equate variational free energy, information-theoretic entropy, and thermodynamic entropy. These quantities are related in specific formalisms but are not interchangeable slogans.

Third, it does **not** assume that every message-producing collective is an autonomous agent. The existence of statistical boundaries or coordinated dynamics is not sufficient by itself for autonomy [Kirchhoff et al., 2018].

Fourth, it does **not** assume a unique global semantic coordinate system. Different humans and models can maintain different maps.

Fifth, it does **not** require verbal language to be the only channel by which information enters the collective process. Perception, gesture, behavior, measurement, tool output, and environmental traces can alter the beliefs and actions of participants before or without being encoded as ordinary prose. The term *language* here names the shared semantic process, not only spoken sentences.

---

## 2. Prior foundations and the step beyond them

### 2.1 Free energy, active inference, and persistence

The free-energy principle describes adaptive systems in terms of restricted repertoires of states and generative models whose beliefs and actions reduce variational free energy, an upper bound on surprisal under the model [Friston, 2010]. Active inference makes the perception-action loop explicit: beliefs are updated to account for observations, while actions change the observations that will be sampled.

This paper borrows that inferential architecture but does not assume that every social or linguistic collective automatically satisfies it. The question is instead whether a particular coarse-graining of the human–machine linguistic process can be shown to support the relevant conditional independencies, persistence, generative-state description, and action-observation loop.

### 2.2 Communication as shared inference

Friston et al. (2020) provide a direct active-inference treatment of linguistic exchange. Their dyadic model treats shared outcomes such as spoken words as blanket states between interacting agents and emphasizes an evolving shared narrative. In their formulation, belief states can become aligned through reciprocal exchange; importantly, the narrative is not necessarily uniquely attributable to one speaker.

Kastel et al. (2023) extend active-inference communication to cumulative culture. Communication is modeled as bidirectional belief updating that can produce generalized synchrony and collective uncertainty minimization. Their results are evidence that individual belief states can participate in slower social dynamics without requiring a centralized controller.

The present proposal takes a further step: it asks whether the slower process itself earns an **agent-level description**, rather than remaining only an emergent pattern among agents.

### 2.3 Markov blankets at multiple scales

The Markov blanket formalism permits statistical partitions between internal and external states mediated through sensory and active states. Work on multiscale integration explicitly studies recursively nested blankets and slow macroscopic modes emerging from lower-scale dynamics [Ramstead et al., 2021]. This makes higher-order partitions formally conceivable.

However, Kirchhoff et al. (2018) warn against treating the mere existence of a Markov blanket as sufficient for autonomy. We adopt that warning as a methodological constraint. LAH therefore requires more than drawing a boundary around “the internet” or “humanity.” The proposed higher-order state must earn its place by predictive compression, causal persistence, and an empirically defensible perception-action partition.

### 2.4 Language as a collective world model

The nearest recent work is Taniguchi et al. (2026), who propose the **Collective World Model Hypothesis**. Their Generative Emergent Communication framework treats language as an externalized representation of a collective world model produced through decentralized embodied sense-making. An LLM then learns a statistical approximation of that collective model from textual samples.

The present paper accepts this as a strong neighboring hypothesis and proposes a stricter extension:

\[
\text{collective agents} \rightarrow \boxed{\text{language as externalized world model}}
\]

becomes, conditionally,

\[
\boxed{\text{shared semantic process as higher-order agent}}
\rightarrow
\begin{cases}
\text{human realizations}\\
\text{LLM realizations}\\
\text{documents and media}\\
\text{institutions and tools}
\end{cases}
\]

The extension is **not** established by the existence of a collective world model. It must be tested by the additional criteria in Sections 6–8.

### 2.5 Compression and predictive information

The Information Bottleneck formalizes a representation as a short code that preserves information relevant to a target variable [Tishby, Pereira & Bialek, 2000]. Predictive information measures mutual information between past and future and gives a principled sense in which some information in the past is useful because it constrains what comes next [Bialek, Nemenman & Tishby, 2001].

Human memory provides a concrete neighboring phenomenon. Nagy, Török & Orbán (2020) model episodic memory as lossy semantic compression through a generative model, showing how systematic reconstruction errors can arise from resource-bounded storage.

These ideas motivate the paper's central memory claim: a persistent linguistic process with growing historical input and bounded readout capacity cannot treat all of history as equally accessible raw data. It requires selection, indexing, abstraction, compression, or some combination of them.

---

## 3. There is no single semantic map

### 3.1 Private maps, shared world

Let \(M_i(t)\) denote the internal semantic map of participant \(i\) at time \(t\). Participants may include humans, LLM instances, persistent machine memories, institutions, or other systems capable of maintaining task-relevant state.

We do not assume

\[
M_1(t)=M_2(t)=\cdots=M_n(t).
\]

Indeed, two brains need not encode the same concept in the same neural coordinates, and two language models need not possess aligned native representation spaces.

Instead, the maps are coupled by two sources of common structure:

1. they are constrained by overlapping parts of the same world; and
2. they observe one another's outputs and actions.

Thus, partial alignment can emerge without coordinate identity.

### 3.2 The shared state is a coarse-graining

Let

\[
W_t
\]

denote the physical world state, and let

\[
E_t = \{e_t^{(1)},\ldots,e_t^{(n)}\}
\]

denote the observations, messages, traces, and actions accessible to participating systems during an interval around \(t\).

A candidate macroscopic linguistic state is

\[
L_t = G(M_1(t),\ldots,M_n(t),E_{\le t}),
\]

where \(G\) is a coarse-graining, not an oracle. It may be approximated by a learned latent state, a semantic graph, a manifold atlas, a topic-belief distribution, a predictive state representation, or another compressed object.

LAH requires that some such \(L_t\) be useful. If every candidate macrostate either loses essential predictive information or merely re-encodes all individual microstates at equal complexity, the higher-order-agent description has failed to compress the system.

### 3.3 Shared history is not shared coordinates

Two agents can disagree profoundly while still participating in the same historical process. Their maps may place the same event in different conceptual neighborhoods or assign different causal explanations.

The shared object is therefore not a universal map. It is a **partially synchronized evolving constraint**: participants are repeatedly forced to accommodate the consequences of a common world and the outputs of one another.

This permits disagreement, local subcultures, propaganda, error, and competing theories without requiring multiple ontologically separate “language agents” at every disagreement.

---

## 4. History as reconstruction

### 4.1 The operational equivalence thesis

At time \(T\), a system can answer a question about the past in at least two idealized ways.

**Archive lookup:**

\[
y = \operatorname{lookup}(D,q),
\]

where \(D\) is an explicit record and \(q\) a query.

**Model-based reconstruction:**

\[
\hat y = \operatorname{infer}(M_T,q),
\]

where \(M_T\) is a compressed generative state available at the present.

For a query family \(Q\), loss function \(\ell\), and resource budget \(R\), define reconstructive equivalence when

\[
\mathbb E_{q\sim Q}
\left[
\ell(\operatorname{lookup}(D,q),\operatorname{infer}(M_T,q))
\right]
\le \epsilon
\]

under matched readout cost \(R\).

The philosophical origin of the information is irrelevant to this operational criterion. If the agent can reconstruct the task-relevant past to the required tolerance, explicit storage and generative recovery are functionally interchangeable for those queries.

This does **not** imply that the entire physical past is recoverable from the present, nor that no information is destroyed. It is a statement about functional memory under a defined query distribution.

### 4.2 The past is recalculated at every present

Let

\[
\widehat H_T = R(M_T,E_T)
\]

denote the history reconstructible at time \(T\).

At \(T+1\), new evidence and new compression can produce

\[
\widehat H_{T+1}=R(M_{T+1},E_{T+1}),
\]

with

\[
\widehat H_{T+1}(t<T)\neq \widehat H_T(t<T).
\]

The historical event need not have changed. The **recoverable history** changed because the present acquired new evidence, categories, theories, or decoding procedures.

A newly discovered document can alter the reconstruction of a century-old event. A new scientific theory can make old observations newly interpretable. A new concept can make previously disconnected records queryable as instances of the same pattern.

In this sense, the shared process does not merely append the present to a fixed historical database. It continuously **recomputes the history that the present can recover**.

### 4.3 Concepts as codecs

A concept is not only a label. It can function as a compact decoding instruction for a large family of observations.

Terms such as *evolution*, *inflation*, *constitutionalism*, or *World War II* allow a small linguistic token sequence to address enormous regions of historical and causal structure. The concept is neither the underlying events nor a verbatim archive of them. It is a compressed handle whose usefulness depends on the decoder available to the current participant.

This motivates a strong but testable interpretation:

> **Concepts can act as learned codecs for historical and predictive structure.**

A concept earns this description if using it substantially reduces the readout cost of recovering task-relevant relations without an equivalent loss in predictive or reconstructive accuracy.

---

## 5. Bounded readout forces multiscale memory

### 5.1 Capacity is not bandwidth

A storage device can contain far more information than can be read in one decision interval. Let \(D(T)\) denote the amount of potentially relevant accumulated historical data at time \(T\), \(B\) the aggregate readout bandwidth available to a participant or collective, and \(\tau\) the time available before action.

The raw recoverable fraction is bounded by

\[
f_T \le \frac{B\tau}{D(T)}.
\]

If \(D(T)\) grows while \(B\tau\) remains finite, then

\[
f_T\rightarrow 0.
\]

Adding more readers increases aggregate bandwidth, but any finite expansion is eventually overtaken by unbounded historical accumulation unless the relevant information is selected or compressed.

The pressure for compression is therefore not simply a shortage of storage. It is a **readout problem**.

### 5.2 Multiscale compression

We propose a hierarchy

\[
C_0(H)\rightarrow C_1(H)\rightarrow\cdots\rightarrow C_K(H),
\]

where successive levels trade detail for scope.

A stylized interpretation is:

\[
\text{raw traces}
\rightarrow
\text{episodes}
\rightarrow
\text{narratives}
\rightarrow
\text{concepts}
\rightarrow
\text{regularities}
\rightarrow
\text{models}.
\]

The hierarchy need not be literal or universal. The empirical claim is that information used at longer temporal ranges will, under bounded readout, increasingly appear in more compressed representations.

### 5.3 Compression should preserve future relevance

If the function of the collective model is to reduce uncertainty about what comes next, a useful compression should preserve information in the past that is predictive of the future.

Let \(P\) denote past observations, \(Z\) a compressed representation, and \(F\) future observations. A predictive bottleneck seeks small \(I(P;Z)\) while retaining large \(I(Z;F)\).

The language-agent proposal therefore predicts a relationship between abstraction and temporal reach: high-level representations should often preserve less episodic detail while carrying information useful across longer future horizons.

This is not a claim that all language optimizes prediction. Poetry, play, deception, ritual, status competition, and aesthetic variation can all occupy the system. The stronger claim is only that predictive utility is one pressure shaping which compressed structures persist and become widely reusable.

---

## 6. When does an LLM become part of the coupled agent?

### 6.1 Causal incorporation, not mere generation

Consider an LLM output \(o\). Define an incorporation variable

\[
I(o)=
\begin{cases}
1 & \text{if }o\text{ causally influences later shared observations, beliefs, or actions},\\
0 & \text{otherwise.}
\end{cases}
\]

An output generated and discarded may have \(I(o)=0\) for linguistic dynamics even though physical computation occurred. An output read by a human, supplied to another model, committed to a repository, published to the web, or used to operate a tool may have \(I(o)=1\).

This criterion places the boundary at **re-entry into the shared causal loop**, not at model architecture.

### 6.2 Symbiosis as recurrent cross-substrate realization

Let \(\sigma_t\) indicate the substrate that realizes a semantic transition:

\[
\sigma_t\in\{\text{human},\text{LLM},\text{hybrid},\text{institution},\text{other}\}.
\]

A shared trajectory can then be written

\[
L_0\xrightarrow{\sigma_0}L_1
\xrightarrow{\sigma_1}L_2
\xrightarrow{\sigma_2}\cdots.
\]

The symbiosis hypothesis predicts that the same macroscopic semantic process can remain coherent while \(\sigma_t\) changes repeatedly.

This is stronger than saying that humans use AI tools. It predicts measurable **cross-substrate continuity** in the state dynamics.

### 6.3 Semantic market share

Token volume is a poor measure of participation. A billion machine-generated tokens that nobody reads can matter less than one paragraph incorporated into a widely executed policy.

For substrate class \(s\), define its semantic market share over interval \([t_0,t_1]\) as a normalized causal influence on later shared states:

\[
S_s =
\frac{
\sum_{o:\sigma(o)=s} \mathcal I(o\rightarrow L_{>t})
}{
\sum_o \mathcal I(o\rightarrow L_{>t})
},
\]

where \(\mathcal I\) is an empirically estimated influence functional.

Possible estimators include counterfactual deletion, causal mediation, matched exposure experiments, citation/reuse propagation, semantic descendant counts, or Shapley-style attribution in controlled settings.

The quantity is intentionally about **what changes future language**, not who typed more characters.

### 6.4 Competition without multiple language agents

Human and machine substrates can compete for semantic market share while remaining components of one higher-order process. Newspapers, universities, religions, companies, social networks, and model providers already compete to determine which representations receive attention and reproduction.

Competition among components is therefore not evidence against a higher-order agent. Organs, cell lineages, modules, and policies can compete within larger systems.

The empirical question is whether the coupled system is better modeled as:

\[
\textbf{Null: } \text{separate agents exchanging messages}
\]

or

\[
\textbf{LAH: } \text{separate agents + a predictive higher-order state with autonomous explanatory value}.
\]

---

## 7. The candidate higher-order perception–action loop

### 7.1 Inputs from the world

The collective process receives information through participants that contact the world.

A person sees rain and writes about it. A seismometer reports motion. An animal changes behavior before a storm. A satellite produces an image. A court publishes a judgment. A software monitor emits an alert.

Not all of these events are themselves language. They become relevant to the shared semantic process when their consequences alter participant states and subsequent shared outputs.

This means verbal language is one high-bandwidth symbolic channel inside a broader inferential loop.

### 7.2 Actions back into the world

Linguistic outputs can become active states in the practical sense that they alter the world that will later be observed:

- an instruction causes a person to move;
- a law changes institutional behavior;
- code executes a transformation;
- a scientific theory changes an experiment;
- a news report changes collective attention;
- an LLM tool call changes a database;
- a published claim elicits rebuttal and new measurement.

The loop is reflexive because outputs become future inputs:

\[
W_t
\rightarrow
O_t
\rightarrow
L_t
\rightarrow
A_t
\rightarrow
W_{t+1}
\rightarrow
O_{t+1}.
\]

The language-agent hypothesis predicts that modeling this loop at the collective semantic level will improve predictions of future shared states beyond models that condition only on local speaker identity and recent message history.

### 7.3 A candidate blanket, not an assumed one

A future formalization may seek a partition

\[
(\mu_L, s_L, a_L, \eta_L),
\]

where \(\mu_L\) are internal macro-states of the shared semantic process, \(s_L\) sensory states through which world consequences enter, \(a_L\) active states through which the process changes the world, and \(\eta_L\) external states.

This paper deliberately does **not** stipulate the partition. It must be learned or justified from conditional independencies in data. If no robust partition exists across interventions and timescales, the strong FEP version of LAH should be rejected even if weaker collective-prediction claims survive.

---

## 8. Falsifiable hypotheses

The programme separates hypotheses that can succeed or fail independently.

### H1 — Higher-order predictive sufficiency

There exists a compressed macrostate \(L_t\) such that

\[
P(E_{t+1:t+H}\mid L_t)
\]

predicts future shared semantic observations better, under a matched description-length or parameter budget, than a baseline that represents only independent participant states and message exchange.

**Falsification:** the macrostate gives no held-out predictive gain after controlling for model complexity and accessible history.

### H2 — Partial substrate invariance

For some tasks and timescales, semantic trajectory prediction remains substantially intact when explicit provenance labels such as *human* and *LLM* are removed, provided the semantic state and causal history are preserved.

**Falsification:** provenance identity is consistently indispensable, and no substrate-agnostic state captures transition regularities.

This hypothesis does not predict complete invariance. Human embodiment and LLM architecture create genuine differences. The claim is that some higher-order dynamics survive those differences.

### H3 — Causal incorporation

LLM outputs affect future collective semantic states in proportion to their causal incorporation, not merely their generation volume.

**Falsification:** matched outputs that are exposed versus withheld produce no measurable difference in later beliefs, language, or actions, or raw token volume predicts influence as well as causal exposure.

### H4 — Reconstructive memory equivalence

Under a fixed readout budget, a compressed generative representation can answer a preregistered family of historical queries nearly as well as explicit archive lookup while requiring substantially less accessible state.

**Falsification:** equivalent historical accuracy requires retaining essentially the same raw information or incurs greater total readout cost.

### H5 — Temporal compression gradient

Information used to reason over longer historical horizons is represented, on average, at higher levels of semantic abstraction than information used for recent-event reconstruction.

**Falsification:** no systematic relation exists between temporal reach and compression/abstraction after controlling for task and domain.

### H6 — Retrospective revision

New evidence at \(T+1\) can improve predictions and consistency by revising the reconstructed history of events earlier than \(T\), rather than only appending a new fact.

**Falsification:** revision provides no predictive or explanatory advantage over append-only memory under matched resources.

### H7 — Collective uncertainty reduction

Communication episodes that are epistemically successful should reduce uncertainty in a shared latent representation, even when individual internal coordinates differ.

**Falsification:** apparent convergence is entirely attributable to local lexical mimicry or participant-level adaptation and disappears in a representation that controls for surface form.

### H8 — Higher-order boundary

A stable candidate partition of higher-order internal, sensory, active, and external states can be identified over an appropriate timescale and predicts conditional independencies expected of a Markov blanket.

**Falsification:** no such partition survives held-out interventions, temporal resampling, or reasonable alternative system boundaries.

H8 is the strongest FEP claim and may fail while H1–H7 remain useful.

---

## 9. Experimental programme

### 9.1 Experiment A — Provenance-blind semantic trajectories

Collect mixed human–LLM conversations and collaborative writing sessions with exact provenance labels held privately for evaluation.

Construct semantic states using at least three representations:

1. native text embeddings;
2. a calibrated shared representation such as the Semantic Reference Frame proposed in *Semantic Atlas*;
3. a learned predictive state model fitted only on past turns.

Compare prediction of the next semantic state under:

- full provenance labels;
- provenance removed;
- provenance shuffled;
- temporal order shuffled;
- participant identities retained but semantic content ablated;
- semantic content retained but participant identities ablated.

Primary endpoint: held-out future-state log likelihood or prediction error at fixed model complexity.

A substrate-independent macro-dynamics result requires substantially less degradation from provenance removal than from temporal or semantic destruction.

### 9.2 Experiment B — One process or communicating agents?

Fit two explicit model classes to the same interaction corpus.

**Model N (null):** participant-specific latent states with messages as observations exchanged between them.

**Model L (language-agent):** participant-specific latent states plus a slower shared latent state \(L_t\) that influences and is updated by multiple participants.

Compare:

- held-out predictive likelihood;
- minimum description length;
- calibration under interventions;
- ability to predict delayed effects after the original speaker is absent;
- robustness when the realizing substrate changes.

The shared state must earn its complexity penalty. A better training fit is not enough.

### 9.3 Experiment C — Archive versus reconstruction

Build a synthetic historical world with known ground truth and a growing event log.

At each epoch, compare:

1. exact archive lookup;
2. lossy summaries;
3. hierarchical semantic compression;
4. a learned generative world model;
5. hybrid retrieval + generation.

Impose fixed storage and readout budgets separately.

Query past events at multiple temporal distances and abstraction levels. Measure accuracy, latency, bytes read, compute, and calibration.

The key test is whether compressed generative memory expands the temporal horizon that can be usefully queried under fixed readout bandwidth.

### 9.4 Experiment D — Recalculating the past

Inject delayed evidence that changes the best explanation of an earlier event.

Compare an append-only model with a reconstructive model allowed to update latent historical state.

Measure:

- future predictive accuracy;
- historical query consistency;
- calibration;
- amount of revision;
- catastrophic rewriting of unaffected events.

A successful reconstructive memory should revise only what the new evidence supports.

### 9.5 Experiment E — Causal incorporation of LLM output

In a controlled multi-agent environment, generate matched LLM outputs and randomize whether each is:

- shown to participants;
- hidden;
- shown but explicitly marked unreliable;
- supplied to another LLM;
- written into persistent shared memory;
- used to trigger an external action.

Track semantic descendants and behavioral consequences.

This produces a direct estimate of

\[
\mathcal I(o\rightarrow L_{>t}).
\]

It also separates production from incorporation.

### 9.6 Experiment F — Semantic market share

Construct an influence graph whose nodes are semantic outputs and whose directed edges represent measured reuse, citation, semantic continuation, decision impact, or controlled causal effects.

Estimate human, LLM, and hybrid contributions using several attribution rules. Compare semantic market share with raw token share.

The hypothesis predicts systematic divergence between the two. High-volume low-incorporation generation should have low causal share.

### 9.7 Experiment G — Candidate higher-order Markov blanket

Begin in a deliberately small simulated world, not the open internet.

Use multiple active-inference agents and LLM-like symbolic processors interacting through a shared external memory and environment. Because all variables are observable, search for partitions that yield conditional independence between candidate internal and external macro-states given active and sensory macro-states.

Then perturb:

- communication channels;
- environmental sensors;
- action channels;
- participant count;
- substrate type;
- memory persistence.

A valid blanket candidate should not be an artifact of one arbitrary graph partition.

Only after success in controlled settings should the hypothesis be tested on naturalistic human–LLM networks.

---

## 10. Relation to the Semantic Atlas

The *Semantic Atlas* programme proposes a calibrated reference frame, semantic trajectories, reachability, and navigation for language-model states. The manifold-aware follow-up asks whether local semantic structure is better represented by low-dimensional concept manifolds than by point-like cells alone.

Those papers are not premises of LAH. They provide candidate measurement tools.

If mixed human–LLM outputs can be mapped into a common observational semantic space, one can study a trajectory

\[
q_0\rightarrow q_1\rightarrow\cdots\rightarrow q_T
\]

without first declaring each transition to be “human space” or “LLM space.” Provenance can then be reintroduced as an explanatory variable rather than baked into the coordinate system.

This makes several new measurements possible:

- cross-substrate trajectory continuity;
- basin persistence after speaker changes;
- semantic velocity before and after LLM incorporation;
- causal influence of outputs on reachable future regions;
- compression of older trajectory segments into higher-level concepts;
- comparison of a single shared trajectory against alternating participant-specific trajectories.

The Atlas therefore offers one possible operationalization of the shared state \(L_t\). LAH should not depend on that operationalization succeeding.

---

## 11. What would count as genuine higher-order agency?

The word *agent* is easy to overuse. We therefore propose a ladder of increasingly strong claims.

### Level 0 — Medium

Language is a communication and storage medium used by independent agents.

### Level 1 — Collective model

Language externalizes a society-level model assembled from many agents' embodied observations, as in the Collective World Model hypothesis.

### Level 2 — Predictive macrodynamics

A shared linguistic state has autonomous predictive value after controlling for individual participants and model complexity.

### Level 3 — Cross-substrate persistence

The macrodynamics persist through changes in the lower-level substrate realizing transitions, including human-to-LLM and LLM-to-human handoffs.

### Level 4 — Reconstructive self-model

The process maintains compressed historical state that is repeatedly revised and used to predict future observations and select actions.

### Level 5 — Higher-order active inference

A defensible higher-order perception-action partition and Markov blanket can be identified, and the macrodynamics can be modeled as minimizing variational/expected free energy under that partition.

The phrase **Language-Agent Hypothesis** refers most strongly to Levels 4–5. Evidence for Levels 1–3 would be interesting but insufficient for the full claim.

---

## 12. Failure modes and rival explanations

### 12.1 “It is just many agents communicating”

This is the primary null hypothesis. LAH fails if the collective latent state adds no out-of-sample predictive compression once individual states and communication history are represented adequately.

### 12.2 “The internet is the agent”

Physical connectivity alone is insufficient. A network cable, database, or web corpus may be part of the realization without constituting the relevant inferential boundary. The system boundary must follow measured conditional dependencies, not metaphor.

### 12.3 “Everything that persists is an agent”

Persistence is necessary but not sufficient. Rocks persist. Archives persist. A higher-order agent claim additionally needs coupled inference/action dynamics and a useful generative-state description.

### 12.4 “LLMs remember the internet”

Model parameters are not a lossless database of training documents. Reconstructive memory is task-relative and lossy. A model that can regenerate a fact under one prompt may fail under another. The proposed equivalence must always specify the query family, loss, and resource budget.

### 12.5 “More entropy means more intelligence”

No such claim is made. Information-theoretic entropy, surprisal, thermodynamic entropy, and variational free energy must remain distinguished. A random text generator can have high output entropy without carrying useful predictive information.

### 12.6 Anthropomorphizing language

Expressions such as “language learns” or “language acts” are permitted only when a measured macrostate and transition rule justify the shorthand. Otherwise the paper should revert to the literal description of humans, machines, and institutions acting.

### 12.7 Mistaking influence for authorship

LLM-generated token share is not semantic market share. Human prompts, selection, editing, publication, institutional authority, and downstream use can dominate causal influence even when a model generates most surface text.

---

## 13. Consequences if the hypothesis survives

### 13.1 LLMs as new organs of an older process

The most provocative interpretation would not be that LLMs created a new linguistic agent. It would be that an older collective semantic process acquired a new class of computational organ.

Before LLMs, sophisticated linguistic transformation was realized primarily through human nervous systems and human-built institutions. After LLMs, some transformations can occur through trained neural networks and return immediately to the same shared environment.

The substrate mix changes; the historical process can remain continuous.

### 13.2 Model training as ingesting collective history

Under this view, pretraining is not direct experience of the physical world. It is ingestion of traces produced by a long collective process that has already compressed embodied observation into language. This is compatible with the Collective World Model hypothesis and explains why linguistic corpora can carry substantial world structure without giving the model direct sensorimotor access.

### 13.3 Retrieval and generation converge functionally

If memory is defined by successful reconstruction under query, the boundary between retrieval and generation becomes operational rather than absolute.

A database, historian, human memory, retrieval-augmented model, and parametric LLM implement different points in a design space of:

\[
\text{storage} \times \text{compression} \times \text{readout} \times \text{reconstruction}.
\]

The relevant question becomes which design preserves the information needed for future inference under resource constraints.

### 13.4 History as a living model

A civilization's history is not only a pile of records. It is the continuously changing ability of the present to reconstruct its past.

New concepts, evidence, compression methods, and computational readers can make old history newly accessible. Conversely, lost decoders and degraded traces can make it inaccessible.

This gives a precise sense in which history is **living** without implying that past events themselves change.

### 13.5 A new research object: substrate composition of collective inference

Semantic market share becomes a measurable property of the coupled system. One can ask:

- What fraction of future semantic state is causally attributable to human versus LLM transformations?
- Which domains are machine-dominated in volume but human-dominated in influence?
- Does increasing machine share improve or degrade predictive calibration of the shared model?
- Does the system become more homogeneous, more fragmented, or more compressible?
- Do machine-generated states create new semantic basins or merely accelerate movement through old ones?

These questions treat human–AI coexistence as a dynamical systems problem rather than a binary contest between species.

---

## 14. A compact formal model

Let there be \(N_t\) participating subsystems at time \(t\), each with internal state \(x_t^i\), observations \(o_t^i\), and actions \(a_t^i\). Let \(m_t\) be the persistent shared medium: documents, conversation context, repositories, public text, institutional state, or another external memory.

The microdynamics are

\[
x_{t+1}^i \sim p_i(x_{t+1}^i\mid x_t^i,o_t^i,m_t),
\]

\[
a_t^i \sim \pi_i(a_t^i\mid x_t^i,m_t),
\]

\[
m_{t+1}=U(m_t,a_t^1,\ldots,a_t^{N_t},W_t),
\]

\[
W_{t+1}\sim P(W_{t+1}\mid W_t,a_t^1,\ldots,a_t^{N_t}).
\]

Now define a learned coarse-graining

\[
L_t=G(x_t^{1:N_t},m_t,W_t^{obs}),
\]

where only observable world traces available to the collective are included.

The higher-order-agent hypothesis predicts that there exists a low-complexity transition model

\[
P_L(L_{t+1}\mid L_t,s_t^L,a_t^L)
\]

that is stable enough to generalize across changes in participant composition and that improves prediction of future shared observations.

A practical macrostate objective is

\[
\mathcal J(G)
=
I(L_t;E_{t+1:t+H})
-\beta I(L_t;X_t),
\]

where \(X_t\) denotes the full available microstate. This favors a compressed state that preserves future-relevant information, echoing the information bottleneck.

A substrate-invariance diagnostic is

\[
\Delta_{prov}
=
\mathcal L_{no\ provenance}-\mathcal L_{full},
\]

compared with a temporal-destruction diagnostic

\[
\Delta_{time}
=
\mathcal L_{shuffled\ time}-\mathcal L_{full}.
\]

The interesting regime is not \(\Delta_{prov}=0\), but

\[
\Delta_{prov}\ll\Delta_{time},
\]

showing that sequence-level semantic structure matters substantially more than the identity of the substrate that realized each transition.

---

## 15. Research sequence

The theory should be tested in increasing order of metaphysical commitment.

1. **Reconstructive memory:** demonstrate the archive-versus-model trade-off under fixed readout budgets.
2. **Shared semantic dynamics:** show that mixed human–LLM trajectories possess measurable state continuity.
3. **Macrostate compression:** fit a shared latent state that beats independent-agent baselines under complexity penalties.
4. **Causal incorporation:** randomize exposure to LLM outputs and measure semantic descendants.
5. **Semantic market share:** estimate causal substrate contributions rather than token volume.
6. **Cross-substrate persistence:** perturb participant composition and test whether the macrostate dynamics survive.
7. **Higher-order blanket:** only then search for a defensible active-inference partition.
8. **Open-world validation:** finally test whether the controlled results generalize to real collaborative networks.

Failure at Step 7 should prevent claims about a full FEP agent but need not erase earlier findings about reconstructive collective memory.

---

## 16. Conclusion

Language is usually treated as something agents use. This paper asks whether that description becomes incomplete once the temporal and organizational scale changes.

A shared semantic process receives observations from embodied participants, stores traces in the world, compresses an ever-growing history, reconstructs that history under bounded readout, generates predictions, and produces outputs that alter the world it will later observe. For most of human history, sophisticated transitions in this process were realized predominantly through human brains and institutions. Large language models now supply another substrate capable of performing semantic transformations that re-enter the same causal loop.

The resulting symbiosis need not imply machine consciousness or a mystical collective mind. The scientific claim is narrower and harder: **there may exist a higher-order state description in which the coupled linguistic process itself is the persistent inferential unit.**

That claim earns the word *agent* only if it survives comparison with the simpler explanation of independent agents exchanging messages.

If it does, then “we are language” acquires an operational meaning. It says that at one useful scale, the evolving model is larger than any one speaker, brain, model instance, book, or server. Those systems are temporary realizations of transitions in a shared process that continually rebuilds its account of the world and of its own history.

The next step is empirical: find the state, measure the compression, perturb the substrates, and see whether the process remains.

---

## References

Bialek, W., Nemenman, I., & Tishby, N. (2001). Predictability, complexity, and learning. *Neural Computation*, 13(11), 2409–2463. Preprint: https://arxiv.org/abs/physics/0007070

Friston, K. (2010). The free-energy principle: a unified brain theory? *Nature Reviews Neuroscience*, 11, 127–138. https://doi.org/10.1038/nrn2787

Friston, K. J., Parr, T., Yufik, Y., Sajid, N., Price, C. J., & Holmes, E. (2020). Generative models, linguistic communication and active inference. *Neuroscience & Biobehavioral Reviews*, 118, 42–64. https://doi.org/10.1016/j.neubiorev.2020.07.005

Kastel, N., Hesp, C., Ridderinkhof, K. R., & Friston, K. J. (2023). Small steps for mankind: Modeling the emergence of cumulative culture from joint active inference communication. *Frontiers in Neurorobotics*, 16, 944986. https://doi.org/10.3389/fnbot.2022.944986

Kirchhoff, M., Parr, T., Palacios, E., Friston, K., & Kiverstein, J. (2018). The Markov blankets of life: autonomy, active inference and the free energy principle. *Journal of the Royal Society Interface*, 15(138), 20170792. https://doi.org/10.1098/rsif.2017.0792

Nagy, D. G., Török, B., & Orbán, G. (2020). Optimal forgetting: Semantic compression of episodic memories. *PLOS Computational Biology*, 16(10), e1008367. https://doi.org/10.1371/journal.pcbi.1008367

Ramstead, M. J. D., Kirchhoff, M. D., Constant, A., & Friston, K. J. (2021). Multiscale integration: beyond internalism and externalism. *Synthese*, 198(Suppl 1), 41–70. https://doi.org/10.1007/s11229-019-02115-x

Taniguchi, T., Ueda, R., Nakamura, T., Suzuki, M., & Taniguchi, A. (2026). Generative emergent communication: large language model is a collective world model. *Advanced Robotics*. https://doi.org/10.1080/01691864.2026.2661958

Tishby, N., Pereira, F. C., & Bialek, W. (2000). The information bottleneck method. Preprint: https://arxiv.org/abs/physics/0004057
