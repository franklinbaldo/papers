---
type: "Technical Paper"
title: "Time as Concatenation: Symmetry, Recursive Tokenization, and Informational Causal Depth Between Agents"
description: "Position paper defining informational time as accumulated causal distinction and critical recognition time between interacting agents."
tags: [informational-time, recursive-tokenization, symmetry, causal-depth, agent-recognition]
timestamp: 2026-07-30T21:48:00Z
---

# Time as Concatenation: Symmetry, Recursive Tokenization, and Informational Causal Depth Between Agents

**Franklin Baldo**  
Independent Researcher  
franklinbaldo@gmail.com

---

> **Position paper.** This article proposes an operational framework and an
> experimental program. It does not claim that informational time replaces
> physical time, that information is physically free, or that the proposed
> quantities have already been measured in natural or artificial systems.
> Claims about recursive tokenization, semantic capacity, critical recognition
> time, and relational intelligence are hypotheses to be tested.

## Abstract

This paper proposes a theory of **informational time** for interactions between agents. A demonstration does not instantaneously become an observer update. Information must propagate through a finite causal chain of intermediate states. Under an information-preserving description of the global process, the transported payload may remain unchanged, but every transition counted as a distinct informational event must leave a non-empty recoverable distinction in the causal history. Informational time is the accumulated cost of those distinctions along the realized path.

The framework distinguishes causal time from representational time. A long causal history may be replaced by a short symbolic index without erasing the events that occurred, provided the index retains an executable expansion proof. This motivates **recursive endogenous tokenization**: sequences of primitive marks become tokens; sequences of token indices become higher-order tokens; and the process continues until no admissible registration reduces the combined cost of the registry and the indexed transcript. The endpoint is a registry-relative irreducible residue, not an absolute computable incompressible core.

Symmetry supplies the central mechanism for useful tokenization. Messages related by a transformation can be represented by an invariant token, a transformation token, and an unexplained residual. This does not increase the physical capacity of the communication channel. It increases effective semantic capacity relative to a shared registry by allowing later messages to spend fewer symbols on previously demonstrated structure and more symbols on new distinctions.

The paper defines a directional **critical recognition time** $C_{A\leftarrow B}$: the minimum accumulated informational time required for observer $A$ to model demonstrator $B$ as a structured action-generating agent and obtain both net compression evidence and sustained out-of-sample predictive advantage over the best admissible non-agent null model. We propose benchmark environments that vary causal path length, reversibility, symmetry, registry cost, interaction, and agent adaptivity. The framework links concatenation, time, tokenization, prediction, and agent recognition while keeping physical, algorithmic, and semantic claims explicitly separate.

**Keywords:** informational time, causal depth, recursive tokenization, symmetry, semantic capacity, reversible information, predictive information, agent recognition, local negentropy

---

## 1. Introduction

A message produced by one agent does not become knowledge in another agent merely by being defined. It must be embodied, transmitted, transformed by intermediate states, detected, interpreted, and incorporated into the observer's state. Even in an idealized world in which global information is never destroyed, communication remains a process.

This suggests a definition of time that begins not with an external clock but with causal succession. A demonstration leaves a source, traverses one or more states, and eventually changes an observer. If more intermediate transitions are required, more informational time has elapsed between demonstration and update.

A naive formulation would measure time by the raw length of the message. That is insufficient. The same payload can travel through paths of different causal depth. Conversely, a long history can later be represented by a short index. Compression changes the representation of the past, not necessarily the number or ordering of the events that produced it.

The motivating companion framework, developed in `generative_machine_teaching.md`, introduces a self-tokenizing language in which concatenation is the only primitive operation. A demonstrated construction receives a stable index and an executable proof, allowing later procedures to use the construction as one symbol. The present paper asks what follows when that mechanism is applied recursively to causal histories themselves.

Three observations drive the proposal.

First, **concatenation is ordered**. In general:

$$
x\Vert y\neq y\Vert x.
$$

The operation therefore carries a primitive before-after relation.

Second, **tokens preserve causal structure only when they remain expandable**. Replacing a history by an opaque name may hide or discard its internal order. Replacing it by a proof-indexed token preserves a route back to the demonstrated sequence.

Third, **symmetry separates known structure from new variation**. Once an invariant pattern and a family of transformations have been learned, a message need transmit only a structure index, a transformation index, and any residual not explained by the symmetry.

The resulting thesis is:

> Informational time is the accumulated cost of non-empty causal distinctions through which information propagates before producing an observer update; recursive, proof-preserving tokenization can compress the representation of that history without erasing its causal depth.

This paper makes seven contributions:

1. it defines informational events as non-empty recoverable causal distinctions;
2. it defines path-relative informational time and informational distance;
3. it distinguishes causal depth, causal work, physical message length, and symbolic representation length;
4. it formalizes symmetry-based and recursively self-tokenizing representations;
5. it distinguishes reconstructive expansion from predictive semantic yield;
6. it defines critical recognition time $C_{A\leftarrow B}$ relative to null models and an observer;
7. it proposes falsifiable experiments for agent interaction, reversible propagation, recursive tokenization, and symmetry-aware communication.

---

## 2. Scope and Non-Claims

The proposal is deliberately narrower than a general metaphysics of time.

It does **not** claim:

- that physical time is identical to message length;
- that every physical transition necessarily appends a literal digital bit;
- that global information preservation is established for every physical theory;
- that reversible logical transformations have zero physical duration or cost;
- that compression creates information;
- that any compressible process is an agent;
- that Kolmogorov complexity or absolute incompressibility can be computed;
- that a short token makes the causal history it denotes cease to have occurred.

Instead, the paper defines an operational accounting system for a chosen interaction model. The model specifies:

- what counts as a state;
- which distinctions are recoverable;
- which transitions count as causally separate events;
- the coding language used to measure cost;
- the null models against which order is evaluated;
- the observer whose predictive improvement is being measured.

The central quantities are therefore relative to a model class, registry, observer, and causal path.

---

## 3. Related Foundations

### 3.1 Shannon information and coding

Shannon's theory measures communication relative to probabilistic source and channel models and separates message semantics from channel capacity [1]. The present proposal respects that separation. Its claim of increased semantic capacity is always relative to shared side information in a registry; it is not an increase in the Shannon capacity of the physical channel.

### 3.2 Reversible computation and information preservation

Landauer identified logical irreversibility, particularly information erasure, as the source of a minimum thermodynamic cost under standard assumptions [2]. Bennett showed that computation can be embedded in logically reversible processes that retain sufficient history to reconstruct earlier states [3]. Later work emphasized that communication and measurement need not discard information at every step [4].

These results motivate, but do not prove, the model adopted here: a payload may traverse multiple states while global recoverability is preserved. The paper does not infer that such propagation is physically costless.

### 3.3 Logical depth and causal history

Bennett's logical depth distinguishes random objects from objects whose compact descriptions require substantial computation to unfold [5, 6]. The present proposal likewise separates description length from the depth of a production history. Its informational causal depth is path- and registry-relative rather than a replacement for Bennett's machine-relative logical depth.

### 3.4 Information distance

Information distance measures the shortest effective transformations relating individual objects and has reversible formulations connected to thermodynamic work [7]. Informational distance below is instead defined on permitted causal paths in a concrete interaction model. The analogy is useful, but the quantities should not be conflated.

### 3.5 Predictive information and causal states

Predictive information quantifies how much the observed past tells us about the future [8, 9]. Computational mechanics groups histories into causal states that are equivalent for prediction and identifies minimal predictive representations [10, 11]. These ideas are close to the present use of tokenization: histories should share a symbol when their differences are irrelevant to a specified predictive task.

### 3.6 Information bottleneck

The information bottleneck seeks compressed representations that preserve information relevant to a target variable [12]. This supports the distinction between mere expansion or compression and semantic usefulness. A token is not valuable simply because it abbreviates many bits; it is valuable when it preserves distinctions relevant to future prediction, teaching, or action.

### 3.7 Symmetry as information

Group-theoretic symmetry partitions objects into orbits under transformations. Resource theories of asymmetry show that a state's departures from symmetry can encode information about group transformations [13]. The present framework uses the simpler classical insight that an invariant structure and a transformation label can replace repeated literal descriptions of every transformed occurrence.

---

## 4. Informational States and Events

### 4.1 Global states

Let:

$$
S_0,S_1,\ldots,S_n\in\mathcal S
$$

be a finite sequence of global states connecting a demonstrator action to an observer update.

A state may include:

- the source agent's internal and external configuration;
- the physical or simulated channel;
- intermediate carriers;
- environmental records;
- the observer's current state;
- the shared symbolic registry.

The chosen state description must be rich enough to support the recoverability claims made by the experiment.

### 4.2 Information-preserving transitions

A transition is:

$$
S_{k+1}=F_k(S_k).
$$

For the strict information-preserving track, $F_k$ is injective on the admitted state space, or the environment retains sufficient side information to recover $S_k$ from $S_{k+1}$.

This does not require the visible payload to grow:

$$
M_{k+1}=M_k
$$

may hold. What changes is the total causal state and its recoverable relation to earlier states.

### 4.3 Non-empty causal distinctions

Associate each counted transition with a causal record token:

$$
c_k=\operatorname{record}(S_k\rightarrow S_{k+1}).
$$

The framework adopts the following operational postulate:

> A transition counts as one informationally distinct event only if its causal record has strictly positive cost under the chosen prefix-free code.

Thus:

$$
\ell(c_k)\geq\varepsilon>0.
$$

In a discrete implementation, the minimum may be normalized to one unit:

$$
\varepsilon=1.
$$

A purported transition with zero recoverable distinction is observationally identical, under the model, to no counted event. This is a convention for constructing informational time, not a universal physical theorem.

### 4.4 The concatenated causal history

The history evolves by concatenation:

$$
H_{k+1}=H_k\Vert c_{k+1}.
$$

Therefore:

$$
H_n=H_0\Vert c_1\Vert c_2\Vert\cdots\Vert c_n.
$$

The order of the event tokens records causal succession. Later compression may replace subsequences with indices, but a valid proof-indexed representation must expand to the same ordered history.

---

## 5. Informational Time

### 5.1 Path-relative time

For a realized causal path:

$$
\pi=(S_0,S_1,\ldots,S_n),
$$

define informational time:

$$
\tau_I(\pi)
=
\sum_{k=1}^{n}\ell(c_k).
$$

Under unit event cost:

$$
\tau_I(\pi)=n.
$$

This quantity increases when the message must traverse more informationally distinct intermediate states.

### 5.2 Actual time and informational distance

The realized path may not be the shortest permitted path. Define informational distance:

$$
d_I(S_a,S_b)
=
\inf_{\pi:S_a\leadsto S_b}\tau_I(\pi).
$$

For an actual path $\pi$:

$$
\operatorname{delay}_I(\pi)
=
\tau_I(\pi)-d_I(S_a,S_b).
$$

The delay term captures avoidable mediation, redundancy, detours, or protocol overhead under the specified transition system.

### 5.3 Causal work versus causal depth

A proof or propagation process may contain parallel transitions. Let $W_I$ count total event cost across the causal directed acyclic graph:

$$
W_I(\Pi)=\sum_{v\in\Pi}\ell(c_v).
$$

Let causal depth be the maximum sequential path cost:

$$
D_I(\Pi)
=
\max_{\pi\subseteq\Pi}\tau_I(\pi).
$$

Parallelism can reduce $D_I$ without reducing $W_I$. The distinction is analogous to work and span in parallel computation.

### 5.4 Physical, causal, and symbolic time

The framework distinguishes at least four quantities:

1. **physical message length** $|M|$;
2. **causal time** $\tau_I$, the cost of transitions actually traversed;
3. **causal depth** $D_I$, the longest dependency chain;
4. **symbolic time** $L_R(H)$, the length of the current representation using registry $R$.

A better registry can reduce symbolic time:

$$
L_{R'}(H)<L_R(H),
$$

without changing the causal history:

$$
\operatorname{expand}_{R'}(\operatorname{encode}_{R'}(H))=H.
$$

Compression changes how efficiently the past is described. It does not retroactively shorten the path that occurred.

---

## 6. Symmetry as a Tokenization Mechanism

### 6.1 Orbits and invariants

Let a finite transformation family or group $G$ act on messages. The orbit of $x$ is:

$$
[x]_G=\{g(x):g\in G\}.
$$

Messages in the same orbit share an invariant structure relative to the chosen action.

### 6.2 Structure, transformation, and residual

Represent an occurrence $y$ by:

$$
y
=
\operatorname{decode}
\left(
T_{[x]},T_g,\epsilon
\right),
$$

where:

- $T_{[x]}$ indexes the invariant structure;
- $T_g$ indexes the transformation;
- $\epsilon$ is a residual not explained by the symmetry.

For exact symmetry:

$$
\epsilon=\varnothing.
$$

For approximate symmetry, the residual must be encoded and charged. A system that hides residual cost in the tokenizer has not increased useful capacity; it has merely displaced description length.

### 6.3 Net tokenization gain

Let $R$ be the current registry and $R'$ the registry after adding the relevant structure and transformation tokens. Registration is beneficial for corpus or interaction history $H$ only if:

$$
\Delta_R
=
\left[L(R)+L(H\mid R)\right]
-
\left[L(R')+L(H\mid R')\right]
>0.
$$

The cost $L(R')$ includes:

- identifiers;
- expansion proofs;
- transformation definitions;
- canonicalization rules;
- any residual model parameters;
- memory and synchronization overhead included by the benchmark.

### 6.4 Symmetry and prediction

Compression alone does not establish that a symmetry is meaningful. The stronger test is whether the orbit representation predicts unseen transformed instances or future agent actions.

A symmetry-aware token should support correct inference of:

$$
g'(x)
$$

for transformations or combinations not literally observed during registration.

---

## 7. Recursive Endogenous Tokenization

### 7.1 Tokenization levels

Begin with a physical alphabet:

$$
\Sigma_0=\{0,1\}.
$$

After registering useful strings over $\Sigma_0$, obtain a symbolic alphabet $\Sigma_1$. Sequences over $\Sigma_1$ may themselves be registered, producing $\Sigma_2$, and so on:

$$
\Sigma_0
\rightarrow
\Sigma_1
\rightarrow
\Sigma_2
\rightarrow
\cdots.
$$

Correspondingly, a history may admit representations:

$$
H^{(0)}
\rightarrow
H^{(1)}
\rightarrow
\cdots
\rightarrow
H^{(k)}.
$$

Each higher-order symbol must retain an executable proof that expands through lower levels to the physical history.

### 7.2 A single recursive registry

Separate alphabets are conceptually useful but not implementation requirements. One registry may store a directed acyclic graph in which tokens reference atoms or earlier tokens. A token's level is the maximum reference depth in its canonical proof.

### 7.3 Total description objective

Define total representational cost:

$$
\mathcal L(R,H)
=
L(R)+L(H\mid R).
$$

A candidate token $w$ should be registered only when it produces positive net gain for the specified objective:

$$
\mathcal L(R\cup\{w\},H)
<
\mathcal L(R,H).
$$

If the objective includes future interaction, use an expected cost:

$$
\mathbb E
\left[
\mathcal L(R',H_{1:T+m})
\mid H_{1:T}
\right].
$$

A token may be worthwhile even when it does not compress the past if it substantially reduces expected future teaching, prediction, or action cost.

### 7.4 Registry-relative fixed point

A local fixed point is reached when:

$$
\forall w\in\mathcal A(R),
\qquad
\mathcal L(R,H)
\leq
\mathcal L(R\cup\{w\},H),
$$

where $\mathcal A(R)$ is the admissible candidate set under the construction language and search budget.

The remaining indexed sequence is a:

> **registry-relative irreducible residue**.

It is relative because changing the registry language, candidate set, observer, cost function, or computational budget may reveal additional structure.

### 7.5 Proof preservation

Recursive tokenization preserves the causal history only if:

$$
\operatorname{expand}_R(\operatorname{encode}_R(H))=H.
$$

If the mapping is lossy, the resulting representation may remain useful, but it no longer certifies the complete causal sequence. Lossless and lossy tracks must be reported separately.

---

## 8. Effective Semantic Capacity

### 8.1 Physical capacity does not increase

Let a channel transmit at most $B$ physical bits during an interval. A registry does not make the channel transmit more than $B$ physical bits.

Instead, the observer combines the current message with shared prior structure:

$$
\text{reconstructed content}
=
\operatorname{decode}(m,R).
$$

The registry functions as shared side information accumulated during earlier interaction.

### 8.2 Reconstructive expansion

Define reconstructive expansion:

$$
\Lambda_R(m)
=
\frac{L_0(\operatorname{expand}_R(m))}{L_R(m)}.
$$

A large $\Lambda_R$ means that a short indexed message expands into a long previously structured sequence. It does **not** by itself mean that the message contains proportionally more uncertainty, novelty, or predictive information.

For example, an index for a billion zeros has enormous reconstructive expansion but may communicate little new information once the repetition rule is shared.

### 8.3 Predictive semantic yield

Let $Y$ be the future variable, target action, or task output whose prediction matters. Define predictive semantic yield:

$$
\Psi_R(m;Y)
=
\frac{I(Y;m\mid R)}{L_R(m)}.
$$

This measures task-relevant information per transmitted symbol, conditional on the shared registry.

The distinction is crucial:

- $\Lambda_R$ measures reconstructible structure;
- $\Psi_R$ measures predictive relevance.

A useful communication system may optimize a combination of both.

### 8.4 Symmetry frees channel budget for novelty

Suppose a message contains a large invariant component and a small novel deviation. Without a shared registry, the invariant must be retransmitted. With symmetry tokens, the message can encode:

$$
\text{invariant index}
\Vert
\text{transformation index}
\Vert
\text{residual novelty}.
$$

The physical channel budget is unchanged, but fewer transmitted symbols are spent re-establishing known structure. A greater fraction of the message can therefore specify new distinctions.

This is the intended meaning of increased effective semantic capacity.

---

## 9. Critical Recognition Time

### 9.1 Why improbability is insufficient

Every sufficiently long specific sequence has low probability under a uniform random model. Low probability alone does not demonstrate local negentropy, intelligence, or agency.

Evidence of structure requires comparison with relevant alternatives. A structured hypothesis should encode or predict the interaction better than the best admissible null model after paying for:

- the hypothesis;
- the registry;
- proof descriptions;
- fitted parameters;
- selection or search complexity included by the protocol.

### 9.2 Null and agent model classes

Let $\mathcal M_0$ contain non-agent models such as:

- independent random sources;
- finite-order stationary processes;
- deterministic but non-adaptive generators;
- compression models without persistent latent policy;
- environment dynamics matched in complexity to the agent model.

Let $\mathcal M_1$ contain models of persistent adaptive agents whose actions depend on latent state, observations, and possibly beliefs about the observer.

The classes and their coding penalties must be fixed before evaluation.

### 9.3 Retrospective order evidence

For transcript $D_{1:T}$ and learned registry $R_T$, define net structural evidence:

$$
E_T
=
\min_{M_0\in\mathcal M_0}L(D_{1:T},M_0)
-
\min_{M_1\in\mathcal M_1}
\left[
L(R_T,M_1)+L(D_{1:T}\mid R_T,M_1)
\right].
$$

Positive $E_T$ means that the agent-structured account compresses the observed interaction better after full model and registry accounting.

### 9.4 Prospective predictive gain

Retrospective compression may overfit. Let $b_t$ denote future demonstrator actions. Define held-out predictive gain for horizon $m$:

$$
\Gamma_{T,m}
=
\sum_{t=T+1}^{T+m}
\log
\frac{
 p_A(b_t\mid H_t,\widehat B,R_T)
}{
 p_0(b_t\mid H_t)
}.
$$

The observer recognizes useful agency only when the gain survives held-out and intervention tests.

### 9.5 Definition of $C$

For thresholds $\delta>0$, $\gamma>0$, and horizon $m$, define directional critical recognition time:

$$
C_{A\leftarrow B}(\delta,\gamma,m)
=
\inf_T
\left\{
\tau_I(\pi_{1:T}):
E_T\geq\delta
\ \land\
\Gamma_{T,m}\geq\gamma
\right\}.
$$

Thus $C_{A\leftarrow B}$ is the minimum accumulated informational time required for observer $A$ to obtain both:

1. net evidence that $B$ is a structured adaptive action generator;
2. sustained predictive advantage on actions not used to build the model.

### 9.6 Dependence on path and observer

In general:

$$
C_{A\leftarrow B}
\neq
C_{A'\leftarrow B}.
$$

Different observers possess different priors, registries, computational limits, and sensors.

Likewise, changing the causal channel can change $C$ even when the demonstrator emits the same abstract message. Additional intermediate states increase path cost whenever each counted transition has positive minimum cost.

### 9.7 Failure to reach $C$

For some observer-channel-agent combinations, no finite interaction may satisfy the thresholds:

$$
C_{A\leftarrow B}=\infty.
$$

This can occur when:

- the channel destroys relevant distinctions;
- the observer lacks the representational class needed to model the agent;
- the demonstrator is not distinguishable from the null class;
- the interaction is too short;
- registry overhead exceeds all apparent compression gains;
- future actions are intentionally or intrinsically unpredictable.

---

## 10. Relational Intelligence

### 10.1 Directional recognition

The framework treats intelligence as relational and directional rather than as a scalar substance possessed in isolation.

A minimal operational hypothesis is:

> Agent $A$ exhibits relational intelligence with respect to $B$ when $A$ constructs a representation of $B$ that yields robust predictive or control improvement beyond non-agent alternatives.

The directional quantities may differ:

$$
C_{A\leftarrow B}
\neq
C_{B\leftarrow A}.
$$

### 10.2 Mutual interaction

A mutually modeling pair can be represented by:

$$
\left(
C_{A\leftarrow B},
C_{B\leftarrow A}
\right)
$$

and by the corresponding post-threshold predictive gains.

A teacher may recognize a student's uncertainty and choose actions to reduce it; the student may recognize the teacher's pedagogical policy and predict the next demonstration. Their shared registry then records successful coordination.

### 10.3 Agent-world interaction

The ordinary interaction:

$$
\text{agent}\leftrightarrow\text{world}
$$

belongs to the same formal category when the world-side process is treated as a persistent action generator and this model outperforms simpler alternatives.

The framework does not require calling every environment an agent. Whether agent modeling is warranted is an empirical model comparison.

### 10.4 Tokens as interactional achievements

A shared token is evidence that:

1. a structure recurred or transformed systematically;
2. the demonstrator used it as a unit;
3. the observer identified and registered it;
4. later interaction successfully reused the index.

Tokens therefore mark accumulated predictive coordination, not merely static compression.

---

## 11. Experimental Framework

### 11.1 Synthetic causal channels

Construct channels with controllable numbers of intermediate states:

$$
B
\rightarrow
X_1
\rightarrow
\cdots
\rightarrow
X_n
\rightarrow
A.
$$

Vary:

- $n$;
- per-edge event cost;
- reversibility;
- noise;
- redundant paths;
- parallel paths;
- delays that add states without modifying payload;
- lossy versus proof-preserving compression.

The basic prediction is that informational path time grows with required positive-cost transitions even when payload length is held fixed.

### 11.2 Symmetry families

Generate messages under known transformation families:

- reversal;
- complement;
- cyclic shift;
- reflection;
- permutation;
- repeated block substitution;
- tree relabeling;
- finite group actions;
- approximate symmetries with controlled residuals.

Compare literal, frequency-based, compression-only, and symmetry-aware tokenizers.

### 11.3 Recursive tokenization

Allow tokens at level $k$ to become atoms for candidate tokens at level $k+1$. Measure:

- total registry cost;
- indexed transcript length;
- proof depth;
- causal history recovery;
- compression fixed points;
- predictive yield;
- transfer to larger unseen structures.

### 11.4 Demonstrator classes

Use:

- random sources;
- fixed deterministic generators;
- stationary finite-state sources;
- adaptive but non-pedagogical agents;
- pedagogical agents;
- adversarial agents;
- agents that model the observer;
- real or simulated environments with interventions.

### 11.5 Observer classes

Compare:

- optimal Bayesian learners in finite hypothesis spaces;
- grammar compressors;
- causal-state learners;
- recurrent neural networks;
- byte- or bit-level transformers;
- pretrained language models using virtual registry IDs;
- architectures with native dynamic vocabularies;
- neuro-symbolic proof learners.

### 11.6 Null-model discipline

Every critical-time result must report:

- the null class;
- model coding penalties;
- registry coding penalties;
- search budget;
- held-out horizon;
- intervention design;
- confidence or posterior criteria;
- whether the threshold was selected before observing results.

### 11.7 Matched-information ablations

Compare:

- the same payload through paths of different depth;
- the same causal events in correct and shuffled order;
- opaque tokens versus expandable proof-indexed tokens;
- recursive tokenization enabled and disabled;
- symmetry labels versus literal transformed strings;
- shared registries versus unsynchronized registries;
- passive observation versus interactive probing;
- agent models versus complexity-matched non-agent models.

---

## 12. Falsifiable Hypotheses

### H1: Positive-cost mediation increases informational time

Holding source message and observer fixed, adding required intermediate transitions with cost at least $\varepsilon$ will increase $\tau_I$ and weakly increase $C_{A\leftarrow B}$.

### H2: Recursive tokenization reduces symbolic time, not past causal time

A proof-preserving higher-order token will reduce $L_R(H)$ while leaving the expanded event sequence and its realized causal depth unchanged.

### H3: Symmetry-aware tokens improve net communication efficiency

After registry overhead is included, symmetry-aware registries will require fewer transmitted symbols than literal or frequency-only registries for transformed message families.

### H4: Reconstructive expansion and predictive yield diverge

Some tokens will achieve high $\Lambda_R$ but low $\Psi_R$, demonstrating that expansion ratio alone is not semantic information.

### H5: Recursive fixed points are registry-relative

Changing the construction language, learner, or cost function will alter the irreducible residue and token hierarchy.

### H6: Proof indexing improves causal recovery

Observers receiving expandable proof-indexed tokens will recover event order and dependency depth more accurately than observers receiving opaque identifiers of matched length.

### H7: Agent models cross a predictive threshold

For genuinely adaptive demonstrators, agent models will eventually produce positive held-out predictive gain over complexity-matched stationary and deterministic nulls.

### H8: Some structured processes never warrant agent recognition

Compressible deterministic generators without adaptive latent policy will remain better described by non-agent models despite strong tokenization gain.

### H9: Parallelism separates depth from work

Increasing independent parallel paths will increase total causal work without proportionally increasing causal depth.

### H10: Shared symmetry increases effective semantic yield

When agents share transformation and invariant tokens, a larger fraction of a fixed physical message budget will carry task-relevant residual information.

### H11: Full accounting eliminates spurious negentropy

Apparent gains that disappear after charging registry, proof, model, and search costs will fail the local-order criterion.

### H12: Interaction can reduce critical recognition time

Observers allowed to select informative probes will reach recognition thresholds with lower $C$ than observers receiving matched passive data, for agent classes responsive to those probes.

---

## 13. Failure Modes and Limitations

### 13.1 Event-cost postulate

The requirement $\ell(c_k)>0$ is an operational rule for counted informational events. A critic may choose a coarser state description in which several transitions collapse into one. Results must therefore state the event ontology.

### 13.2 State-description dependence

A transition that appears irreversible in a reduced description may become reversible when environmental records are included. Conversely, an impractically detailed global state may make the framework unusable. State selection is substantive, not neutral.

### 13.3 Compression does not create information

Registry-based reconstruction uses information accumulated previously. Claims of semantic capacity must include the registry as side information and report its construction cost.

### 13.4 Expansion is not novelty

A short token may expand to a huge but trivial repetition. Predictive semantic yield and downstream utility must accompany expansion ratios.

### 13.5 Incomputable optima

Absolute shortest descriptions and unrestricted compression fixed points are generally not computable. Experiments must use bounded languages, certified small instances, or best-known upper and lower bounds.

### 13.6 Circular agency

Defining an agent solely as something predicted by an agent model would be circular. Agent classes should include independently specified persistence, responsiveness, intervention sensitivity, and latent-state dependence.

### 13.7 Null-model dependence

A weak null makes recognition easy; an excessively rich null may absorb all adaptive structure. Results should report multiple nested null families and complexity penalties.

### 13.8 Physical overreach

The framework is informational. Translating $\tau_I$ into seconds, energy, thermodynamic entropy, or relativistic proper time requires additional physical laws and measurements.

### 13.9 Lossy tokenization

Approximate symmetry and learned abstractions may discard causal details. Lossy representations can be useful, but they cannot certify complete event histories.

### 13.10 Private codes

Two co-adapted agents may create a highly efficient code that fails to transfer. Held-out agents, mark permutations, registry audits, and reconstruction tests are necessary.

---

## 14. Research Roadmap

### Experiment 1: Unit-cost causal chains

Transmit an unchanged payload through chains of different lengths. Verify that informational time tracks counted transitions while physical payload length remains fixed.

### Experiment 2: Reversible histories

Use reversible finite-state machines or reversible cellular automata. Compare full global histories with reduced observer-visible histories.

### Experiment 3: Opaque versus proof-indexed compression

Replace causal subsequences with opaque IDs or expandable tokens. Test history reconstruction and depth estimation.

### Experiment 4: Exact symmetries

Teach finite transformation families and measure registry cost, message reduction, and generalization to unseen transformations.

### Experiment 5: Approximate symmetries

Introduce controlled residuals and determine when symmetry-based tokenization ceases to yield net gain.

### Experiment 6: Recursive token hierarchies

Allow sequences of indices to become higher-order indices. Measure fixed points under bounded candidate languages.

### Experiment 7: Expansion versus semantic yield

Construct tokens with matched expansion ratios but different predictive relevance. Test whether learners and tokenizer policies distinguish them.

### Experiment 8: Critical recognition time

Mix adaptive agents with random, stationary, and deterministic non-agent generators. Estimate $C_{A\leftarrow B}$ under preregistered thresholds.

### Experiment 9: Interactive recognition

Allow observers to probe demonstrators. Compare critical times against passive-observation controls with matched communication budgets.

### Experiment 10: Agent-world models

Apply the framework to controlled environments whose dynamics range from static to adaptive. Test when agent models become justified.

### Experiment 11: Cross-observer transfer

Evaluate whether registries and agent models learned by one architecture reduce $C$ for held-out observers.

### Experiment 12: Physical implementation boundary

Only after the informational quantities are stable, study how they correlate with wall-clock time, energy, noise, and irreversible operations in a concrete substrate.

---

## 15. Conclusion

This paper proposed an informational account of time grounded in causal propagation between agents.

A demonstration reaches an observer through a sequence of states. Each transition counted as informationally distinct must leave a non-empty recoverable distinction. The accumulated cost of those distinctions defines path-relative informational time.

Proof-preserving tokenization can replace long histories with short indices without erasing the event order that produced them. Because indices can themselves be concatenated and registered, tokenization becomes recursive. The process continues until the combined registry and transcript reach a relative fixed point under the admitted construction language and cost function.

Symmetry makes this compression productive. An invariant token represents shared structure, a transformation token specifies the variation, and a residual carries what remains unexplained. Physical channel capacity does not increase; effective semantic capacity grows relative to the information already shared in the registry.

Finally, critical recognition time $C_{A\leftarrow B}$ measures how much informational time must accumulate before one agent can model another as a structured adaptive source and obtain both net compression evidence and sustained predictive advantage.

The proposal can be summarized as:

$$
\text{causal transitions}
\rightarrow
\text{ordered history}
\rightarrow
\text{symmetry}
\rightarrow
\text{recursive tokens}
\rightarrow
\text{predictive agent model}.
$$

The central empirical question is not whether a long sequence is improbable. It is whether interaction produces a proof-preserving representation that compresses what has occurred, predicts what comes next, and does so after the full cost of the representation itself is paid.

---

## References

[1] Claude E. Shannon. “A Mathematical Theory of Communication.” *Bell System Technical Journal*, vol. 27, 1948, pp. 379–423 and 623–656. DOI: [10.1002/j.1538-7305.1948.tb01338.x](https://doi.org/10.1002/j.1538-7305.1948.tb01338.x).

[2] Rolf Landauer. “Irreversibility and Heat Generation in the Computing Process.” *IBM Journal of Research and Development*, vol. 5, no. 3, 1961, pp. 183–191. DOI: [10.1147/rd.53.0183](https://doi.org/10.1147/rd.53.0183).

[3] Charles H. Bennett. “Logical Reversibility of Computation.” *IBM Journal of Research and Development*, vol. 17, no. 6, 1973, pp. 525–532. DOI: [10.1147/rd.176.0525](https://doi.org/10.1147/rd.176.0525).

[4] Rolf Landauer. “Dissipation and Noise Immunity in Computation, Measurement, and Communication.” *Journal of Statistical Physics*, vol. 54, 1989, pp. 1509–1517. DOI: [10.1007/BF01044700](https://doi.org/10.1007/BF01044700).

[5] Charles H. Bennett. “On the Nature and Origin of Complexity in Discrete, Homogeneous, Locally-Interacting Systems.” *Foundations of Physics*, vol. 16, 1986, pp. 585–592. [IBM Research publication page](https://research.ibm.com/publications/on-the-nature-and-origin-of-complexity-in-discrete-homogeneous-locally-interacting-systems).

[6] Charles H. Bennett. “Logical Depth and Physical Complexity.” In Rolf Herken, ed., *The Universal Turing Machine: A Half-Century Survey*. Oxford University Press, 1988, pp. 227–257.

[7] Charles H. Bennett, Péter Gács, Ming Li, Paul M. B. Vitányi, and Wojciech H. Zurek. “Information Distance.” *IEEE Transactions on Information Theory*, vol. 44, no. 4, 1998, pp. 1407–1423. DOI: [10.1109/18.681318](https://doi.org/10.1109/18.681318).

[8] William Bialek and Naftali Tishby. “Predictive Information.” 1999. [arXiv:cond-mat/9902341](https://arxiv.org/abs/cond-mat/9902341).

[9] William Bialek, Ilya Nemenman, and Naftali Tishby. “Predictability, Complexity, and Learning.” *Neural Computation*, vol. 13, no. 11, 2001, pp. 2409–2463. DOI: [10.1162/089976601753195969](https://doi.org/10.1162/089976601753195969).

[10] James P. Crutchfield and Karl Young. “Inferring Statistical Complexity.” *Physical Review Letters*, vol. 63, 1989, pp. 105–108. DOI: [10.1103/PhysRevLett.63.105](https://doi.org/10.1103/PhysRevLett.63.105).

[11] Cosma Rohilla Shalizi and James P. Crutchfield. “Computational Mechanics: Pattern and Prediction, Structure and Simplicity.” *Journal of Statistical Physics*, vol. 104, 2001, pp. 817–879. [arXiv:cond-mat/9907176](https://arxiv.org/abs/cond-mat/9907176).

[12] Naftali Tishby, Fernando C. Pereira, and William Bialek. “The Information Bottleneck Method.” 2000. [arXiv:physics/0004057](https://arxiv.org/abs/physics/0004057).

[13] Iman Marvian and Robert W. Spekkens. “Extending Noether’s Theorem by Quantifying the Asymmetry of Quantum States.” *Nature Communications*, vol. 5, 2014, article 3821. DOI: [10.1038/ncomms4821](https://doi.org/10.1038/ncomms4821).
