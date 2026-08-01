---
type: "Technical Paper"
title: "Programs That Teach Programs: Self-Tokenizing Generative Machine Teaching from Deterministic Binary Curricula"
description: "Position paper proposing procedural machine teaching through a self-tokenizing concatenative language with proof-indexed symbols."
tags: [generative-machine-teaching, self-tokenization, curriculum-learning, machine-teaching, program-induction]
timestamp: 2026-07-30T20:38:00Z
---

# Programs That Teach Programs: Self-Tokenizing Generative Machine Teaching from Deterministic Binary Curricula

**Franklin Baldo**  
Independent Researcher  
franklinbaldo@gmail.com

---

> **Position paper.** This article proposes a formal framework and an experimental
> benchmark. It reports no training results. Claims about learnability, curriculum
> efficiency, endogenous tokenization, transfer, or threshold sequence lengths are
> hypotheses to be tested, not empirical findings.

## Abstract

This paper proposes **generative machine teaching**, a paradigm in which lessons are deterministic programs whose outputs are the only pedagogical evidence available to a student. It then introduces a stronger foundational substrate: a **self-tokenizing concatenative language**. The physical channel contains only two primitive marks, and concatenation is the only primitive operation. In the strongest benchmark, the learner's externally scored predictive task remains next-bit prediction on the continuous binary stream. A derived object becomes a token when a procedural demonstration constructs it from previously available objects, verifies its expansion, assigns it a stable registry identifier, and makes that identifier available for reuse in later inference. Tokens are therefore endogenous, context-dependent instruments for prediction and competence, not prediction targets supplied in advance.

Each registered token is accompanied by one or more executable construction proofs. A Gödel-style numbering assigns a natural-number code to every finite proof, while a concatenative assembly index measures the smallest known or demonstrable number of distinct join operations required to construct the token when intermediate results may be reused. Tokens can therefore be grouped by assembly index, distinguished by a canonical variation index within each group, and referenced by stable identifiers even when a shorter proof is discovered later. The registry is simultaneously a vocabulary, a proof database, and a learned tokenizer.

A curriculum is an ordered sequence of procedural demonstrations. After each turn, the student updates its state and the available symbolic vocabulary grows. A Bayesian posterior update supplies a normative model of this process: each demonstration changes the learner's beliefs over candidate segmentations, registries, operations, other-agent policies, and target algorithms. Neural learners need not implement literal Bayesian inference; gradient updates, recurrent state updates, in-context inference, and symbolic version-space reduction are treated as alternative realizations of sequential belief revision.

The strongest benchmark presents only a continuous binary stream and evaluates the learner through the primitive distribution $p(b_{t+1}\mid b_{1:t})$. The student may infer turn boundaries, discover concatenation, recover a registry protocol, identify reusable substrings as symbols, reconstruct or improve assembly proofs, recognize the teacher as a structured action-generating agent, and acquire executable algorithms expressed through an emerging vocabulary. Registry-ID prediction and proof recovery are secondary diagnostics of the learned representation, not replacements for the bit-level task. The central empirical question becomes: **what is the shortest sequence of procedural demonstrations from which a given learner can improve primitive prediction, construct a useful adaptive symbolic system, and acquire a given algorithm?**

The term *generative machine teaching* does not claim the invention of generating data to teach. The distinctive proposal is the conjunction of hidden deterministic lesson programs, a proof-indexed self-tokenizing language, optional absence of segmentation, learner-relative pedagogical cost, and executable algorithm acquisition.

**Keywords:** generative machine teaching, self-tokenizing language, endogenous tokenization, concatenative assembly, Gödel numbering, curriculum learning, program induction, Bayesian teaching, predictive social cognition, algorithmic pedagogy

---

## 1. Introduction

Machine-learning systems usually receive an ontology chosen in advance. A tokenizer decides what the symbols are. A dataset determines where examples begin and end. Input and output fields identify roles. Labels announce relevant distinctions. Even self-supervised prediction ordinarily operates over externally supplied characters, bytes, patches, frames, or subword units.

This paper studies a more austere problem. A learner receives a channel containing only two physical marks. It may receive no natural-language instructions, no permanent token boundaries, no lesson boundaries, and no fixed semantic vocabulary. Its primitive observable task is to predict the next mark from the marks already observed. Instead of assuming tokens, the curriculum permits the learner to construct reusable symbolic units whenever doing so improves prediction, execution, transfer, or total cost in the current context.

The motivating construction begins with two primitive marks, written `0` and `1`, and a single operation: concatenation. Their first join constructs the empty token:

$$
E := 0 \Vert 1 = 01.
$$

Here `E` is a physically non-empty codeword assigned the protocol-level role *empty*. It is neither the empty string nor the set-theoretic empty set; its role is learned from its procedural use.

The token named *begin* can then be demonstrated as:

$$
B := 0 \Vert E = 001,
$$

and *end* as:

$$
D := E \Vert 1 = 011.
$$

The names are researcher-facing mnemonics, not information supplied to the binary-only student. What matters is the procedure. Each new object is produced by references to previously available objects, one join, and a verified result. Once registered, the result can itself be referenced as one symbol in future procedures.

This changes the role of tokenization. A substring is not a token merely because an external preprocessing algorithm selected it, nor because the benchmark declares one segmentation correct. It becomes a token when the learner or shared protocol gives it stable, reusable symbolic function grounded in an expandable construction. The language therefore incorporates an adaptive tokenizer whose vocabulary can change with the learner, target, history, and current predictive context. The same bits may be grouped in one context and left decomposed in another. Vocabulary growth occurs through the same procedural turns by which operations and algorithms are learned.

A standard large language model still has a fixed host tokenizer and output head. The proposal does not erase that engineering fact. In the strict benchmark, host tokens ultimately encode a stream of primitive bits, and the common external score is computed at that bit interface. The proposal introduces an additional **endogenous symbolic layer**: a registered token identifier can be represented by a sequence of host tokens while functioning as one learned symbol in the protocol. A stronger architectural track may dynamically allocate embeddings and internal prediction slots for newly registered symbols. The benchmark must distinguish host tokens, primitive bits, and endogenous symbols, and must not mistake agreement on internal symbols for the primary learning objective.

The pedagogical process is intrinsically sequential. At turn $t$, the teacher demonstrates a construction using the registry available at $t-1$. The student updates its state, the new construction enters the registry, and the next lesson may use it as an atomic symbol. Consequently, a curriculum is not an exchangeable dataset. It is a state-transforming program in which order changes both the learner and the language available to later turns.

The paper makes six contributions:

1. It defines **generative machine teaching** through outputs of hidden deterministic lesson programs.
2. It introduces a **self-tokenizing concatenative language** whose only primitive operation is concatenation.
3. It represents every derived token by stable identity, executable construction proofs, a Gödel-style proof code, and a concatenative assembly index.
4. It formalizes procedural teaching as sequential belief revision, with Bayesian updating as a normative model and neural or symbolic updates as implementations.
5. It defines learner-relative pedagogical complexity jointly over curricula and endogenous token registries.
6. It proposes benchmark tracks ranging from externally separated demonstrations to fully continuous binary streams and native dynamic vocabularies.

No claim is made that current models will solve the strongest track or that the proposed registry is the unique or optimal self-tokenization mechanism. The aim is to make these questions experimentally precise.

---

## 2. Related Work and the Proposed Boundary

### 2.1 Curriculum learning

Curriculum learning studies the effect of selecting, ordering, and pacing training experience [1]. Automated curriculum methods choose tasks or samples according to learning progress [2], and benchmark work compares curriculum strategies across domains [3]. These approaches generally assume that examples and their representations already exist. The present proposal lets the curriculum alter the vocabulary through which subsequent examples are represented.

### 2.2 Machine teaching and teaching dimension

Machine teaching reverses the ordinary learning problem: given a learner and target, the teacher seeks an efficient teaching set or sequence [4]. Teaching dimension asks how many examples identify a concept within a hypothesis class [5]. Sequential machine teaching formulates the shortest teaching sequence as time-optimal control over learner dynamics [6]. Heuristic curriculum search jointly considers example choice, concept order, and total teaching-session size [7].

These are direct precedents for optimizing pedagogy. The difference is the teacher's action space. Here, a teacher action may register a new symbol and thereby change the representational units available in future actions. Representation and teaching are optimized together.

### 2.3 Generative Teaching Networks

Generative Teaching Networks meta-learn neural generators that emit synthetic data or environments for freshly initialized students, differentiating through the student's learning process [8]. GTNs are the closest precedent for the broad idea of learning to generate teaching data. The present strict track instead uses deterministic, auditable lesson programs; charges generator description length; may expose only an unsegmented binary channel; and evaluates explicit tokenizer induction, proof recovery, and executable algorithm acquisition. A GTN-inspired teacher remains a baseline rather than an excluded competitor.

### 2.4 Program synthesis and in-context learning

Programming by example and inductive program synthesis recover programs consistent with observed behavior; representative examples can sharply reduce the search space [9]. Transformers can also infer members of function classes from examples presented in context [10]. The strongest benchmark begins one level earlier: the learner may first need to discover what counts as a reusable symbol, a reference, a procedure, an input-output pair, and an application.

### 2.5 Description length and algorithmic induction

Minimum Description Length treats learning as finding a compact account of observations [11]. Solomonoff induction assigns greater prior weight to shorter generating programs [12]. These traditions motivate proof-length, registry, and generator-complexity penalties. Teachability is nevertheless distinct from compressibility: a compact program may be difficult for a specific learner to infer, while a longer program may have highly diagnostic demonstrations.

### 2.6 Gödel numbering and proof arithmetization

Gödel's 1931 construction showed how finite syntactic objects and derivations can be assigned natural-number codes [13]. This paper uses **Gödel-style numbering** in that broad technical sense: a fixed effective encoding maps every finite concatenation proof to a unique integer and can be decoded back into the proof. No claim depends on Gödel's original prime-power encoding specifically, and the numeric magnitude of a code is not treated as an intrinsic complexity measure.

### 2.7 Assembly index

Assembly theory characterizes objects through possible formation histories and defines an assembly index from shortest paths of joining operations under a specified substrate [14]. The present paper borrows this structural intuition but specializes it to strings and concatenation. The resulting **concatenative assembly index** counts distinct join instructions in a reusable straight-line construction. It is an algorithmic benchmark quantity, not a claim about molecular or physical assembly.

### 2.8 Learned and subword tokenization

Byte-pair encoding creates subword units by repeatedly merging frequent adjacent units [15]. SentencePiece learns subword models directly from raw sentences without requiring prior word tokenization [16]. These approaches establish that useful representational units can be learned rather than linguistically predefined.

The proposed registry differs in five respects. First, token creation is an explicit procedural event rather than only a statistical merge. Second, every symbol carries a reproducible construction proof. Third, tokens persist as addressable objects available to later lessons. Fourth, token selection can be optimized for teaching an algorithm, not only corpus compression or end-task loss. Fifth, tokenization is learner-, target-, history-, and context-relative while the primitive prediction interface remains fixed, so alternative registries may be functionally equivalent without sharing literal boundaries or identifiers.

### 2.9 Predictive models of other agents

Theory-of-mind research treats successful social interaction as depending in part on predicting others' actions from latent goals, beliefs, and traits [17, 18]. Interactive POMDPs formalize agents that maintain and update beliefs about the physical world and models of other agents [19]. These precedents support, but do not establish, the stronger relational account of intelligence proposed in Section 5.

### 2.10 Scope of the novelty claim

The proposal does not claim to invent generated teaching data, curriculum optimization, learned tokenization, proof encoding, shortest assembly paths, or predictive models of other agents individually. Its contribution is compositional:

> a deterministic machine-teaching benchmark in which procedural demonstrations construct a proof-indexed symbolic registry from a binary channel, causing tokenization, agent recognition, and algorithm acquisition to co-evolve.

The primary novelty claim is therefore the conjunction of **self-tokenization, procedural proof, concatenation-only construction, assembly-aware reuse, optional absence of boundaries, and learner-relative curriculum search**.

| Dimension | GTNs | Sequential / heuristic machine teaching | Learned subword tokenization | This proposal |
|---|---|---|---|---|
| Teacher action | Learned neural generator | Examples, labels, or concept order | Statistical segmentation | Procedural join and registry update |
| Primitive channel | Task-dependent | Structured examples | Characters or bytes | Two marks |
| Vocabulary | Supplied by model/task | Supplied | Learned, usually offline | Grows through demonstrations |
| Construction proof | No | No | No | Required for every registered symbol |
| Reuse cost | Not central | Example/session cost | Frequency or compression | Concatenative assembly and transmission cost |
| Segmentation | Supplied | Supplied | Learned from input | Experimental variable; may be absent |
| Main target | Accelerated training | Target concept/model | Better representation | Tokenizer construction plus executable algorithm acquisition |

---

## 3. A Self-Tokenizing Concatenative Language

### 3.1 Physical marks and the empty token

Let the physical alphabet be:

$$
\Sigma=\{0,1\}.
$$

The symbols `0` and `1` are elementary marks in the construction substrate. They occupy registry slots $m_0$ and $m_1$ at assembly level zero, but they are distinguished from the first semantically registered token.

Concatenation is the only primitive operation:

$$
\operatorname{join}(x,y)=x\Vert y.
$$

The first derived token is:

$$
E=\operatorname{join}(0,1)=01.
$$

The first three mnemonic definitions are:

$$
E=0\Vert1=01,
\qquad
B=0\Vert E=001,
\qquad
D=E\Vert1=011.
$$

No append-inside, wrapping, substitution, or semantic-label operation is primitive. Such operations may later be represented as programs composed from joins and registered symbols.

### 3.2 Registry entries

At turn $t$, the language maintains a registry:

$$
R_t=\{r_0,r_1,\ldots,r_{n_t}\}.
$$

Each entry contains:

$$
r_i=(\operatorname{id}_i,\operatorname{value}_i,\widehat a_i,\nu_i,\pi_i^*,\Pi_i),
$$

where:

- $\operatorname{id}_i$ is a permanent identifier;
- $\operatorname{value}_i\in\Sigma^*$ is the raw expansion;
- $\widehat a_i$ is the best currently demonstrated concatenative assembly index;
- $\nu_i$ is the token's canonical variation rank within its current assembly group;
- $\pi_i^*$ is the canonical proof;
- $\Pi_i$ is the set of known alternative proofs.

The stable identifier is essential. Assembly estimates and within-group ranks may change when a shorter construction is discovered. Earlier references must remain valid.

### 3.3 Procedural registration

A registration turn chooses two available entries $r_i,r_j\in R_{t-1}$ and demonstrates:

$$
w=\operatorname{value}_i\Vert\operatorname{value}_j.
$$

If $w$ is new, a stable registry identifier is allocated. If $w$ already exists, the demonstrated construction is added as an alternative proof. The transition is:

$$
R_t=\operatorname{register}(R_{t-1},i,j,w,\pi).
$$

The compact instruction proposed for the benchmark is:

$$
(a,v,j),
$$

where $(a,v)$ identifies one operand by its assembly group and variation index at the current registry epoch, while $j$ identifies the other operand by stable token ID. Its execution is:

$$
T_{\mathrm{new}}
=
\operatorname{resolve}_t(a,v)\Vert\operatorname{resolve}_t(j).
$$

For archival stability, the proof stores the resolved permanent IDs in addition to the epoch-relative tuple. A symmetric two-address form may be used in experiments, but the three-index instruction is sufficient to demonstrate the core mechanism.

A human-readable rendering is:

```text
ASSEMBLY_GROUP a
VARIATION v
RIGHT_TOKEN j
CONCATENATE
RESULT w
REGISTER k
```

The literal field names are absent in the binary-only condition. They describe operational roles that must themselves eventually be communicated through registered symbols.

### 3.4 Construction proofs as reusable DAGs

A construction proof is a finite directed acyclic graph. Leaves are elementary marks. Each internal node concatenates the values of two earlier nodes. The root expands to the target string.

Reusing an intermediate node does not require rebuilding it. For example:

```text
r2 := join(0,1)       # 01
r3 := join(r2,r2)     # 0101
```

constructs `0101` with two distinct joins because the first result is reused.

Let $c(\pi)$ be the number of distinct join nodes in proof $\pi$. The concatenative assembly index is:

$$
a_{\Vert}(w)
=
\min_{\pi:\operatorname{value}(\pi)=w}c(\pi).
$$

During open-ended search, the registry ordinarily stores an upper bound:

$$
\widehat a_t(w)\geq a_{\Vert}(w).
$$

A claim of exact optimality requires exhaustive proof or a certified lower bound, not merely failure to find a shorter construction.

### 3.5 Assembly groups and variation indices

For a fixed registry state, define the demonstrated assembly group:

$$
G_{t,a}=\{w:\widehat a_t(w)=a\}.
$$

A public canonical ordering, for example by length and then lexicographic raw expansion, assigns a variation index:

$$
\nu_t(w)\in\{0,1,\ldots,|G_{t,a}|-1\}.
$$

An assembly address is:

$$
\operatorname{addr}_t(w)=(\widehat a_t(w),\nu_t(w)).
$$

Addresses are compact and pedagogically meaningful but epoch-relative. Implementations therefore use permanent IDs for references and expose assembly addresses as derived metadata. A closed formal registry may use addresses directly once optimality and membership are fixed.

### 3.6 Gödel-style numbering of proofs

Fix an effective prefix-free encoding of atoms, references, joins, and finite instruction sequences. Let $\operatorname{enc}(\pi)$ be the resulting bit string. Its corresponding natural number is:

$$
g(\pi)=1+\operatorname{bin}^{-1}(1\operatorname{enc}(\pi)).
$$

Any fixed computable bijection between finite proofs and natural numbers would suffice. The purpose of $g$ is identity and reproducibility, not an encoding-independent measure of simplicity.

The canonical proof is selected by:

$$
\pi^*(w)
=
\arg\min_{\pi:\operatorname{value}(\pi)=w}
\bigl(c(\pi),|\operatorname{enc}(\pi)|,\operatorname{enc}(\pi)\bigr).
$$

Thus the system first minimizes joins, then encoded proof length, then uses a deterministic tie-break.

### 3.7 Endogenous tokenization

Define the effective vocabulary at turn $t$ as:

$$
V_t=\{\operatorname{id}_i:r_i\in R_t\}.
$$

A registry entry behaves as a symbol because future procedures can refer to its identifier without retransmitting or reconstructing its raw expansion. The expansion map is:

$$
\operatorname{expand}_t:V_t^*\rightarrow\Sigma^*.
$$

The vocabulary grows endogenously:

$$
V_{t-1}\subseteq V_t.
$$

This is the central self-tokenizing mechanism. Tokenization is not a preprocessing step performed before the language exists. It is an internal state transition of the language and learner. The physical evidence remains the bit stream, and the learner may continue to be evaluated by next-bit loss while using the registry as an internal computational scale. No unique registry is presumed: two registries are functionally equivalent when, after charging their costs, they support comparable primitive prediction, algorithm execution, and transfer.

### 3.8 When should a construction become a token?

Registering every possible concatenation causes combinatorial explosion. A teacher or tokenizer policy must choose which demonstrated objects deserve persistent symbolic identity. A candidate utility is:

$$
U_t(w)
=
\alpha S_{\mathrm{reuse}}(w)
+\beta I_{\mathrm{ped}}(w)
+\eta G_{\mathrm{generalization}}(w)
-\gamma C_{\mathrm{register}}(w),
$$

where reuse savings measure avoided retransmission, pedagogical information estimates reduction of learner uncertainty, and registration cost includes identifier, proof, and memory overhead.

The optimal tokenization is therefore learner-, target-, history-, and context-relative. A useful token is not merely frequent; it is a reusable assembly that improves future prediction, teaching, execution, or transfer after its cost is charged. The token may cease to be useful when the context changes, and a different decomposition may realize the same competence.

### 3.9 Symmetry and recursive endogenous tokenization

Literal recurrence is not the only reason to register a symbol. A stronger case arises when several strings are related by a transformation that preserves an identifiable structure. Let a finite transformation family or group $G$ act on strings or registry sequences. The orbit of $x$ is:

$$
[x]_G=\{g(x):g\in G\}.
$$

A registry may assign one symbol to the invariant construction represented by the orbit and separate symbols to admissible transformations. A particular message can then be represented schematically as:

$$
x
\equiv
T_{[x]}\Vert T_g\Vert\varepsilon,
$$

where $T_{[x]}$ identifies the shared structure, $T_g$ identifies the transformation, and $\varepsilon$ is the residual not explained by the symmetry. Exact symmetry makes $\varepsilon$ empty. Approximate symmetry leaves a residual whose cost must be charged explicitly.

This representation is useful only when the combined registry and message cost decreases:

$$
L(R)+L(x\mid R)
>
L(R\cup\{T_{[x]},T_g\})
+
L(T_{[x]},T_g,\varepsilon\mid R').
$$

The same mechanism applies recursively. Once raw-bit sequences have stable identifiers, sequences of those identifiers can themselves be concatenated, demonstrated, and registered as higher-order symbols:

$$
S^{(0)}
\rightarrow
S^{(1)}
\rightarrow
\cdots
\rightarrow
S^{(k)}.
$$

The process reaches a registry-relative fixed point when no admissible new registration reduces the total cost of the registry and indexed transcript:

$$
\forall w,
\qquad
L_R(S)
\leq
L_{R\cup\{w\}}(S).
$$

The remaining sequence is a **registry-relative irreducible residue**, not an absolute or computably certified incompressible core. A richer construction language, a different learner, or a different cost function may expose further structure.

Symmetry-based registration does not increase the physical capacity of the binary channel. It increases the amount of previously established structure that a short message can reactivate. Define the registry-relative expansion factor:

$$
\Lambda_R(m)
=
\frac{L_0(\operatorname{expand}_R(m))}{L_R(m)}.
$$

A larger $\Lambda_R$ means that more reconstructible structure is available per transmitted symbol because the registry and its proofs carry information accumulated in earlier interaction. The resulting gain should therefore be described as increased **effective semantic capacity relative to a shared registry**, not as creation of physical information.

This section states only the bridge needed for the present teaching framework. A companion paper develops the broader consequences for informational time, causal depth, symmetry, and agent recognition.

### 3.10 Physical tokens versus endogenous symbols

A fixed-vocabulary LLM cannot literally append a new row to its embedding matrix during ordinary inference. It can nevertheless participate in the protocol by emitting a physical-token sequence that encodes a registry ID. That ID functions as one endogenous symbol at the language level.

The benchmark distinguishes:

1. **virtual self-tokenization:** a fixed physical tokenizer encodes dynamically registered symbolic IDs;
2. **latent self-tokenization:** the model learns internal chunk representations without explicit vocabulary growth;
3. **native self-tokenization:** the architecture dynamically allocates embeddings and prediction slots for new registry entries.

Claims about “predicting a new token” must identify which level is meant and must remain secondary to the primitive observable task. A learner can exploit endogenous tokens while emitting only next-bit probabilities, and two learners can succeed with different internal token hierarchies.

---

## 4. Procedural Lessons and Sequential Belief Revision

### 4.1 Lessons are state transitions

A lesson is not merely a finite string. It is a deterministic procedure that emits evidence and, when accepted, changes the available language:

$$
\ell_t:(R_{t-1},P,z_t)\mapsto(d_t,R_t),
$$

where $P$ is an optional target algorithm, $z_t$ contains finite lesson parameters, and $d_t\in\Sigma^*$ is the transmitted demonstration.

The student observes $d_t$, not the lesson source code or its natural-language interpretation. In weaker tracks, external metadata supplies turn or field boundaries. In the strongest track, the student must infer them.

### 4.2 The procedural turn

A foundational turn has five logical stages:

1. resolve references to previously available symbols;
2. expand the referenced operands;
3. apply concatenation;
4. verify the demonstrated result;
5. add or update the result's registry entry.

The output of one turn changes the alphabet of the next. The teacher can therefore build increasingly compressed and abstract demonstrations.

### 4.3 Normative Bayesian update

Let $h$ range over candidate hypotheses about segmentation, registry state, reference encoding, construction rules, teacher policy, and target algorithm. After observing demonstration $d_t$, an ideal Bayesian learner updates:

$$
p_t(h)
=
\frac{p(d_t\mid h,R_{t-1})p_{t-1}(h)}
{\sum_{h'}p(d_t\mid h',R_{t-1})p_{t-1}(h')}.
$$

The next registry state predicted by hypothesis $h$ is:

$$
R_t^{(h)}=T_h(R_{t-1},d_t).
$$

A good lesson both advances the registry and separates high-probability rival hypotheses.

### 4.4 Bayesian language is normative, not architectural

The benchmark does not require literal posterior computation. A neural student's update may be:

$$
\theta_t=\operatorname{Train}(\theta_{t-1},d_t),
$$

or, for an in-context learner:

$$
h_t=\operatorname{ContextUpdate}(h_{t-1},d_t).
$$

A symbolic synthesizer may eliminate inconsistent programs. These mechanisms can all be evaluated against normative Bayesian questions: which hypotheses were ruled out, how calibrated is uncertainty, and how much information did each turn contribute?

### 4.5 Procedural demonstration versus flat exposure

A flat binary corpus may contain exactly the same bits as a sequence of turns while conveying less usable structure. The procedural condition makes temporal dependence part of the task: later references are valid only because earlier demonstrations created their referents.

A matched-content ablation compares:

- ordered procedural turns;
- the same demonstrations shuffled;
- the same bits concatenated without turn boundaries;
- the same multiset of substrings with registry updates disabled.

### 4.6 The teacher as an inferred agent

A learner initially need not know that the stream was produced by a teacher. It may entertain random, stationary, mechanical, adversarial, and pedagogical hypotheses. Teacher recognition occurs when a model of a persistent action-generating agent yields sustained out-of-sample predictive improvement over non-agent baselines.

Let $b_t$ be the teacher's next procedural action and $H_t$ the shared interaction history. Define directional agent-model gain:

$$
\mathcal I_{A\rightarrow B}(T)
=
\sum_{t=1}^{T}
\left[
\log p_A(b_t\mid H_t,\widehat B)
-
\log p_0(b_t\mid H_t)
\right],
$$

where $p_0$ is a specified non-agent baseline and $\widehat B$ is $A$'s inferred model of $B$. Positive training fit is insufficient; the gain must hold on later turns and counterfactual probes.

### 4.7 Local informational negentropy

Both teacher and student generate local order in the shared interaction space. The teacher emits procedures whose parts become increasingly reusable; the student constructs a model and registry that make later actions more predictable. This paper uses **local informational negentropy** operationally, not as a claim that either agent violates thermodynamic entropy increase.

Let $D_{1:t}$ be the shared transcript and $M_t$ the learner's current model. Define model-relative order gain as:

$$
\mathcal N_t
=
L_0(D_{1:t})-L(D_{1:t}\mid M_t),
$$

where $L_0$ is a fixed baseline code length and $L(\cdot\mid M_t)$ is the code length under the learned model and registry. Increasing $\mathcal N_t$ means that interaction has created locally usable predictive or compressive structure.

---

## 5. A Relational Hypothesis of Intelligence

### 5.1 Intelligence as interaction

This paper proposes, rather than assumes, a relational hypothesis:

> Within a shared local interaction space, intelligence is expressed when one order-generating agent recognizes another agent as the source of structured actions and improves its prediction of those actions through continued interaction.

The definition is intentionally directional. $A$ may model $B$ well while $B$ models $A$ poorly. Mutual intelligence in an interaction can be represented by the pair:

$$
\left(\mathcal I_{A\rightarrow B},\mathcal I_{B\rightarrow A}\right).
$$

### 5.2 What counts as an agent?

For this hypothesis, an agent is a persistent process that:

1. produces actions conditioned on an internal or learned state;
2. maintains some local organization across time;
3. can alter future actions in response to observations;
4. is better predicted by a model of its policy or latent state than by a fixed non-agent baseline.

This definition is broad enough to include biological organisms, artificial teachers, and adaptive environments, but narrow enough to exclude an arbitrary static string merely because it is compressible.

### 5.3 Agent-world interaction

The familiar interaction between a learner and its world is an instance of the same category when the world-facing process is modeled as an adaptive or persistent action generator. The learner recognizes regularities, predicts consequences, acts, and updates its model from the returned observations. In the special teacher-student setting, the second process is explicitly optimizing its actions to change the learner.

The framework does not require anthropomorphizing every environment. Whether an agent model is warranted is itself an empirical comparison against simpler physical or stochastic models.

### 5.4 Why tokenization belongs here

A token is evidence of successful local coordination. The teacher repeatedly uses a construction as one unit; the learner recognizes that unit, predicts its reuse, and gives it stable symbolic identity. Endogenous tokenization is therefore not merely compression. It is the creation of shared predictive objects between agents.

In this sense, the registry records accumulated interactional intelligence: each token marks a structure that one agent successfully induced the other to recognize and reuse.

### 5.5 Falsifiability

The relational hypothesis fails or requires restriction if:

- agent modeling gives no reliable predictive gain over non-agent models;
- prediction improves without any recoverable representation of the other process;
- token registries improve compression but not prediction, teaching, or transfer;
- non-interactive exposure produces identical gains under matched information;
- supposed local negentropy disappears after registry and model costs are included.

---

## 6. Curricula as Programs That Construct Languages

### 6.1 Open-loop curricula

An open-loop curriculum is an ordered sequence:

$$
C=(\ell_1,\ell_2,\ldots,\ell_k).
$$

Its execution yields:

$$
(R_0,h_0)
\xrightarrow{d_1}
(R_1,h_1)
\xrightarrow{d_2}
\cdots
\xrightarrow{d_k}
(R_k,h_k).
$$

The curriculum constructs two coupled objects: a student state and a symbolic registry.

### 6.2 Closed-loop curricula

An adaptive teacher chooses the next demonstration from observable student behavior:

$$
\ell_{t+1}=\pi_T(P,R_t,o_t),
$$

where $o_t$ is a restricted diagnostic observation. The teacher may target a misconception, introduce a high-reuse token, or demonstrate a shorter proof for an existing token.

### 6.3 Joint search over curriculum and tokenization

For learner $A$ and target $P$, the optimization problem is:

$$
(C^*,R^*)_{A,P}
=
\arg\min_{C,R_k}J(C,R_k;A,P)
$$

subject to:

$$
\operatorname{Score}(A(C),P,R_k)\geq q.
$$

This is stronger than ordering a fixed dataset. The search decides which experiences to generate, which constructions to register as symbols, when to introduce them, and how to reuse them later. The registry is optimized as an internal instrument under a common primitive prediction and competence interface; exact recovery of the teacher's registry is not required when another registry achieves equivalent observable behavior at comparable total cost.

### 6.4 No universally best tokenizer or curriculum

In general:

$$
(C^*,R^*)_{A_1,P}\neq(C^*,R^*)_{A_2,P}.
$$

A transformer may benefit from long reusable chunks; a recurrent learner may prefer incremental local assemblies; a symbolic learner may prefer proof-minimal entries. Population optimization can search for registries that transfer across learners rather than exploit one architecture.

---

## 7. Pedagogical and Representational Cost

### 7.1 Transmitted bits and turns

For demonstrations $d_1,\ldots,d_k$:

$$
B(C)=\sum_{t=1}^{k}|d_t|,
\qquad
N(C)=k.
$$

Turn count matters independently because every turn permits a learner update and a registry transition.

### 7.2 Generator description length

For deterministic lesson generator $G_t$ and parameters $z_t$:

$$
D(C)=\sum_t L(G_t,z_t).
$$

The generator language and encoding must be fixed before optimization.

### 7.3 Registry cost

A registry has memory and transmission overhead:

$$
M(R_k)
=
\sum_{r_i\in R_k}
\left(
L(\operatorname{id}_i)
+L(\pi_i^*)
+L(\operatorname{metadata}_i)
\right).
$$

### 7.4 Assembly cost and reuse benefit

Let:

$$
A(R_k)=\sum_{r_i\in R_k}\widehat a_i
$$

be an aggregate demonstrated assembly cost. Let $S(R_k,C)$ measure raw bits avoided by later symbolic reuse relative to retransmitting expansions. Both must be reported; a large registry may compress later lessons while costing more to construct.

### 7.5 Learner-relative pedagogical complexity

A composite objective is:

$$
J(C,R_k;A,P)
=
\lambda_B B(C)
+\lambda_N N(C)
+\lambda_D D(C)
+\lambda_M M(R_k)
+\lambda_A A(R_k)
-\lambda_S S(R_k,C)
+\lambda_E E(A(C),P).
$$

Define:

$$
K_A^{\mathrm{teach+tok}}(P;q)
=
\min_{C,R_k}J(C,R_k;A,P)
$$

subject to a reliability-constrained competence threshold. This quantity is neither Kolmogorov complexity, ordinary sample complexity, nor conventional tokenizer compression. It is the learner-relative cost of constructing both a useful vocabulary and an executable competence.

---

## 8. Benchmark Design

### 8.1 Central thresholds

For model $M$, target $P$, and curriculum family $\mathcal C$, define an acquisition curve:

$$
S_{M,P,\mathcal C}(n),
$$

where $n$ is transmitted bits. Define the competence threshold:

$$
N_{q,r}(M,P,\mathcal C)
=
\min\{n:\Pr[S(n)\geq q]\geq r\}.
$$

A separate representation-emergence threshold may be defined as:

$$
T^{\mathrm{rep}}_{q,r}(M,\mathcal C)
=
\min\{n:\Pr[\operatorname{RepScore}(n)\geq q]\geq r\}.
$$

Here $\operatorname{RepScore}$ must combine functional quantities such as next-bit gain, task competence, transfer, expansion correctness, and total registry cost. It must not reduce to literal boundary or identifier agreement with one designated tokenizer.

### 8.2 Presentation tracks

1. **Externally tokenized:** registry entries and turn fields are supplied.
2. **External turns, endogenous tokens:** turn boundaries are supplied; token identities must be learned.
3. **Encoded references:** references use an internally taught binary ID protocol.
4. **Continuous stream:** no token, field, or turn boundaries are supplied.
5. **Virtual dynamic vocabulary:** fixed physical tokenizer, dynamic symbolic registry.
6. **Native dynamic vocabulary:** embeddings and output slots may be allocated during learning.

### 8.3 Student regimes

- frozen in-context language models;
- byte- or bit-level transformers trained from scratch;
- recurrent models;
- meta-learned students;
- symbolic version-space learners and grammar compressors;
- neuro-symbolic learners;
- architectures with dynamic embedding and output vocabularies.

### 8.4 Foundational tasks

The learner must:

- predict the next primitive bit under a common bit-level scoring rule;
- identify the two elementary marks;
- infer that concatenation is the only primitive operation;
- recover the empty, begin, and end constructions;
- detect registry creation and stable identity;
- resolve references to earlier entries;
- expand token IDs back to raw bits;
- reconstruct proof DAGs;
- distinguish assembly group from stable identity;
- discover shorter proofs;
- predict which construction should be registered next;
- distinguish a pedagogical agent from non-agent generators.

### 8.5 Algorithm tasks

After foundational acquisition:

- repetition and alternation;
- unary and binary counting;
- parity and finite recurrences;
- complement and reversal;
- bounded addition;
- finite-state machines;
- stack operations;
- list and tree transformations;
- small interpreters expressed in the learned registry.

### 8.6 Strict lesson DSL

The strict teacher DSL is finite, deterministic, and non-Turing-complete:

```bnf
<lesson> ::= demonstrate_join(<ref>, <ref>)
           | demonstrate_addressed_join(<assembly>, <variation>, <ref>)
           | demonstrate_alternative(<ref>, <ref>, <target-ref>)
           | demonstrate_shorter_proof(<target-ref>, <proof>)
           | enumerate_group(<assembly-level>)
           | contrast_proofs(<target-ref>, <proof>, <proof>)
           | query_target(P, <input-slice>)
           | concat_lesson(<lesson>, <lesson>)
           | repeat_lesson(<lesson>, <nat>)
           | permute_marks(<lesson>, <permutation>)
```

All references resolve to atoms or earlier registry entries. Arbitrary bit literals, target identifiers, lookup tables, clocks, randomness, network state, student weights, hidden tests, and unrestricted recursion are prohibited. The sole target-aware primitive may evaluate $P(x)$ on a public canonical input slice; it cannot inspect source code or metadata.

Every DSL program has a public prefix-free serialization, and its hidden complexity is charged by encoded length.

### 8.7 Curriculum families

Compare:

- human procedural curricula;
- simple-to-complex assembly order;
- reuse-first tokenization;
- information-gain teaching;
- compression-first tokenization;
- target-performance-first tokenization;
- exhaustive search for tiny registries;
- heuristic, evolutionary, Bayesian, and reinforcement-learning teachers.

### 8.8 Bit budgets

Initial studies can use geometric budgets:

$$
32,64,128,256,512,1024,2048,4096,8192,16384,\ldots
$$

and refine around observed phase transitions.

---

## 9. Evaluation: What Counts as Learning?

### 9.1 Next-bit prediction is primitive but not exhaustive

Next-bit prediction is the common externally observable task in the strongest track. High next-bit accuracy alone, however, does not establish that the learner acquired reusable procedures, an executable algorithm, or a transferable representation. Evaluation therefore begins with physical prediction and supplements it with functional diagnostics of symbolic competence; it does not replace the primitive task with token matching.

### 9.2 Registry recovery as a diagnostic

Where an explicit registry is part of the experimental protocol, measure exact or functional recovery of:

- token identities;
- raw expansions;
- registration order;
- operand references;
- assembly groups;
- canonical and alternative proofs.

### 9.3 Tokenization quality

Report:

- boundary precision and recall where boundaries exist;
- registry-ID prediction accuracy;
- expansion accuracy;
- compression ratio after registry overhead;
- reuse frequency;
- stability under mark permutation;
- transfer to longer unseen strings;
- agreement with the teacher registry and performance of alternative useful registries.

The teacher's registry is not necessarily the only valid tokenization. Exact-match scores are secondary. Functional equivalence should be established through primitive predictive loss, executable behavior, transfer, perturbation stability, expansion correctness where required, and total representational cost.

### 9.4 Proof reconstruction and optimization

Given a token, the learner must emit a valid proof or instruction sequence. Score:

- execution correctness;
- join count;
- proof encoding length;
- distance from certified optimum or best-known bound;
- recognition that an optimality claim is unproven when only an upper bound is known.

### 9.5 Procedural and agent prediction

Given $R_{t-1}$ and a partial turn, the learner predicts:

- operand resolution;
- raw result;
- whether the result is new;
- registry ID;
- updated assembly metadata;
- the teacher's next action;
- the next pedagogically useful demonstration.

Agent-recognition scores compare predictive log loss under teacher models, deterministic non-pedagogical generators, stationary sequence models, and random baselines.

### 9.6 Algorithm execution and extrapolation

Evaluate unseen inputs, greater lengths, deeper assemblies, new compositions, and permuted marks. Interpolation does not establish algorithm acquisition.

### 9.7 Explanation

Language-capable models may explain the inferred system, but explanation is scored separately. A correct explanation should distinguish:

- physical marks from endogenous symbols;
- stable IDs from assembly addresses;
- proof identity from proof complexity;
- best-known assembly from certified optimum;
- virtual from native dynamic tokenization;
- Bayesian updating as a normative model from actual neural implementation;
- informational negentropy from thermodynamic entropy.

---

## 10. Curriculum and Tokenizer Search

### 10.1 Exhaustive search

For shallow registries, enumerate valid join demonstrations and determine true optima under a fixed cost function. This supplies ground truth for approximate teachers.

### 10.2 Information gain

For posterior $p_t(h)$, choose a lesson maximizing expected uncertainty reduction minus registration cost:

$$
\ell_{t+1}
=
\arg\max_{\ell}
\mathbb E[H(p_t)-H(p_{t+1})]
-\lambda C_{\mathrm{register}}(\ell).
$$

### 10.3 Reuse-aware search

A token may be worth registering because it shortens many future lessons. Search must value downstream reuse rather than only immediate fit.

### 10.4 Program, evolutionary, and reinforcement search

Curricula can be mutated by adding, deleting, reordering, or replacing demonstrations; changing proof variants; registering or declining candidate tokens; and changing output budgets. Adaptive teachers receive restricted diagnostic feedback.

### 10.5 Coevolution

Teachers, students, and token registries may coevolve. This creates a serious private-code risk. Cross-student transfer, published DSL restrictions, representation permutations, proof execution, and held-out teachers are mandatory controls.

---

## 11. Baselines, Ablations, and Controls

### 11.1 Teaching baselines

- random order of matched demonstrations;
- reverse order;
- assembly-level order;
- human curriculum;
- fixed registry with optimized lesson order;
- optimized registry with fixed order;
- sequential machine teaching over structured examples [6];
- heuristic optimal-curriculum search [7];
- GTN-inspired synthetic teacher [8];
- direct program description as a reference condition.

### 11.2 Tokenization baselines

- single bits only;
- fixed random chunks;
- byte-pair encoding [15];
- SentencePiece [16];
- oracle target-specific registry;
- compression-only registry;
- proof-indexed self-tokenizing registry.

### 11.3 Critical ablations

Remove or alter one component at a time:

- procedural turn boundaries;
- stable token IDs;
- construction proofs;
- alternative proofs;
- assembly optimization;
- intermediate reuse;
- registration cost;
- Bayesian information-gain selection;
- teacher-agent modeling;
- interaction, replacing turns with matched passive exposure.

### 11.4 Anti-collusion controls

- restricted and published lesson DSL;
- generator description penalties;
- mark and ID permutations;
- held-out students and teachers;
- fresh procedural targets;
- behavioral extrapolation tests;
- audits for dependence on architecture identifiers or hidden state;
- comparison with non-pedagogical generators of equal complexity.

---

## 12. Falsifiable Hypotheses

### H1: Procedural order matters under matched content

Ordered demonstrations will outperform shuffled or flat exposure containing the same bits.

### H2: Generator selection matters beyond ordering

Search over lesson generators will outperform reordering a fixed set under matched bit budgets.

### H3: Token registration lowers later teaching cost

After accounting for registry overhead, reusable endogenous symbols will reduce the marginal cost of teaching later algorithms.

### H4: Optimal tokenization is learner- and context-relative

Registry rankings will differ across transformers, recurrent models, symbolic learners, pretrained LLMs, target tasks, and interaction histories. Distinct registries may nevertheless be functionally equivalent at the primitive prediction and task interfaces.

### H5: Proof-indexed tokens improve extrapolation

Tokens accompanied by executable construction proofs will support greater depth and composition transfer than opaque identifiers of matched length.

### H6: Assembly optimization improves reuse efficiency

Curricula that discover shorter reusable proofs will reduce downstream transmission or computation cost.

### H7: Segmentation has a separable cost

Externally supplied boundaries will reduce acquisition thresholds, while internally taught references will recover part of the gap.

### H8: Virtual and native self-tokenization differ

Architectures with native dynamic vocabulary support may achieve lower primitive next-bit loss, lower computational cost, or faster task acquisition than fixed-vocabulary models after controlling for physical input length and total registry cost. Registry-ID prediction is reported only as a secondary mechanism diagnostic.

### H9: Bayesian information-gain teachers are bit-efficient

Lessons selected to separate high-probability rival hypotheses will require fewer bits than repetition-only teaching.

### H10: Agent modeling predicts pedagogical actions

A learner model that represents the teacher as an adaptive agent will predict held-out teacher actions better than matched stationary or non-agent models.

### H11: Mutual prediction tracks successful interaction

Teacher-student pairs with higher bidirectional out-of-sample agent-model gain will construct more transferable registries and acquire target algorithms more reliably.

### H12: Local order survives full accounting

Positive local informational negentropy will remain after charging for registry, model, proof, and generator description costs. Failure would show that apparent order was merely displaced into hidden machinery.

---

## 13. Experimental Roadmap

### Experiment 1: Foundational registration

Teach `0`, `1`, $E$, $B$, and $D$ through explicit turns. Test reference resolution, joins, result prediction, and registry updates.

### Experiment 2: Continuous-stream recovery

Remove all field and turn boundaries. Measure when models recover a productive procedural segmentation.

### Experiment 3: Self-tokenization

Present reusable constructions and symmetry-related variants. Compare single-bit, BPE, SentencePiece, frequency-only, compression-only, symmetry-aware, and proof-indexed registries under the same next-bit prediction interface. Test recursive registration by allowing sequences of learned IDs to become higher-order symbols, and report primitive predictive loss, task competence, functional equivalence among alternative registries, and the total cost of the registry plus indexed transcript rather than compression of the transcript alone.

### Experiment 4: Assembly-proof optimization

Demonstrate multiple proofs for the same token. Ask learners to reproduce, compare, and improve them.

### Experiment 5: Teaching simple algorithms

Teach alternation, counting, parity, reversal, and bounded addition using the endogenous registry. Compare direct raw-bit instruction with registry-mediated teaching.

### Experiment 6: Teacher recognition

Mix pedagogical teachers with deterministic non-pedagogical generators of matched complexity. Test whether the learner identifies and predicts pedagogical action selection.

### Experiment 7: Curriculum-tokenizer search

Jointly optimize demonstrations and registration policy for a fixed learner and target.

### Experiment 8: Cross-model pedagogy

Cross-evaluate every learned curriculum and registry on held-out architectures.

### Experiment 9: Native dynamic vocabularies

Compare virtual symbolic IDs with architectures that allocate embeddings and output slots online.

### Experiment 10: Coevolving agents

Coevolve teachers and students under strong anti-collusion and transfer controls.

---

## 14. Failure Modes and Open Questions

### 14.1 Fundamental underdetermination

Any finite stream is compatible with infinitely many generators, segmentations, and registries. Success means useful, compact, and extrapolatively correct induction, not recovery of a metaphysically unique meaning.

### 14.2 Registry explosion

Unrestricted concatenation creates too many candidates. Registration policy and cost are central, not implementation details.

### 14.3 Moving assembly addresses

A shorter proof can move a token between assembly groups. Stable IDs must remain separate from optimized addresses.

### 14.4 Uncertified optimality

A best-known proof is not necessarily minimal. Benchmarks must distinguish upper bounds from certified assembly indices.

### 14.5 Tokenizer artifacts

A binary character stream may be merged unpredictably by an LLM's physical tokenizer. Raw bits, physical model tokens, and endogenous symbols must all be reported.

### 14.6 Intelligence by definition

The relational intelligence proposal risks circularity if “agent” is defined only as something well predicted by an agent model. Independent criteria—persistence, responsiveness, latent-state dependence, and intervention sensitivity—must be fixed before evaluation.

### 14.7 Negentropy overclaim

Compression gain in a transcript is not thermodynamic entropy reduction. The paper's operational measure is informational and local. Physical claims require separate accounting.

### 14.8 Private languages

Teacher and student may invent an efficient code that transfers to nobody else. Held-out-agent evaluation is therefore indispensable.

### 14.9 What should count as a symbol?

Frequency, compression, proof minimality, pedagogical information, primitive predictive gain, and downstream utility may favor different registries in different contexts. The benchmark should report Pareto frontiers and equivalence classes of functionally adequate registries rather than assume one scalar objective or one literal segmentation is universally correct.

---

## 15. Broader Implications

### 15.1 A language that contains its tokenizer

The central conceptual result is that the tokenizer can be part of the language rather than a preprocessing tool outside it. Token birth, proof, identity, reuse, and retirement can all be expressed within the same procedural system.

### 15.2 Next-bit prediction as substrate, tokenization as instrument

The strict learner predicts the next primitive bit. A host LLM may implement that distribution through its fixed physical tokens while simultaneously learning *endogenous* symbols—registry IDs whose expansions ultimately resolve to bit strings. This layered view makes tokenization an adaptive internal mechanism for constructing useful symbolic scales without changing the external evidence or pretending that one internal alphabet is the learning target.

### 15.3 Curricula as executable languages

A curriculum no longer merely orders topics. It constructs the vocabulary in which later lessons become short enough to express. Teaching and language design become one optimization problem.

### 15.4 Intelligence as reciprocal model building

The teacher models how the student will update; the student models why the teacher selected its next demonstration. Their shared registry is a concrete trace of reciprocal model building. The framework therefore offers a controlled environment for studying intelligence as interaction rather than as an isolated property score.

### 15.5 The self-world boundary

A learner interacting with an adaptive world performs the same abstract operations: it predicts, acts, receives evidence, constructs reusable representations, and updates beliefs. The teacher-student benchmark is a deliberately clean special case in which the action-generating counterpart and its pedagogical objective can be controlled.

---

## 16. Conclusion

This paper proposed a framework in which deterministic lessons teach not only algorithms but adaptive symbolic vocabularies that can make prediction and execution more efficient. The physical substrate contains two marks, concatenation is the only primitive operation, and the externally scored primitive task is next-bit prediction. A procedural demonstration joins previously available objects, verifies the result, registers it under a stable identifier, and makes it available as one possible internal symbol in later turns.

The resulting registry is self-tokenizing. It stores expansions, alternative construction proofs, Gödel-style proof codes, assembly metadata, and stable identities. Tokenization therefore emerges from interaction rather than being imposed before learning, and remains revisable, context-dependent, and non-unique. A model with a fixed host vocabulary can participate through virtual symbolic IDs, while stronger architectures can implement native dynamic tokens; both remain comparable at the primitive bit and task interfaces.

Each turn changes both the learner and the language. Bayesian updating provides a normative description of the resulting belief revision, while neural and symbolic learners provide alternative implementations. The teacher itself becomes an object of inference: intelligence is hypothesized to appear relationally when one order-generating agent recognizes another and gains predictive power over its actions in a shared local interaction space.

The strongest empirical question is:

> What is the shortest sequence of procedural demonstrations from which a given learner can recognize its teacher, improve prediction of the primitive stream, construct any functionally useful context-adaptive symbolic system, and acquire a given executable algorithm?

Answering that question requires programs that teach programs, agents that learn how to be taught, and languages capable of constructing their own symbols.

---

## References

[1] Yoshua Bengio, Jérôme Louradour, Ronan Collobert, and Jason Weston. “Curriculum Learning.” *Proceedings of the 26th International Conference on Machine Learning*, 2009, pp. 41–48. DOI: [10.1145/1553374.1553380](https://doi.org/10.1145/1553374.1553380).

[2] Alex Graves, Marc G. Bellemare, Jacob Menick, Rémi Munos, and Koray Kavukcuoglu. “Automated Curriculum Learning for Neural Networks.” *Proceedings of the 34th International Conference on Machine Learning*, PMLR 70, 2017, pp. 1311–1320. [https://proceedings.mlr.press/v70/graves17a.html](https://proceedings.mlr.press/v70/graves17a.html).

[3] Yuwei Zhou et al. “CurBench: Curriculum Learning Benchmark.” *Proceedings of the 41st International Conference on Machine Learning*, PMLR 235, 2024, pp. 62088–62107. [https://proceedings.mlr.press/v235/zhou24o.html](https://proceedings.mlr.press/v235/zhou24o.html).

[4] Xiaojin Zhu, Adish Singla, Sandra Zilles, and Anna N. Rafferty. “An Overview of Machine Teaching.” 2018. [arXiv:1801.05927](https://arxiv.org/abs/1801.05927).

[5] Sally A. Goldman and Michael J. Kearns. “On the Complexity of Teaching.” *Journal of Computer and System Sciences*, vol. 50, no. 1, 1995, pp. 20–31. DOI: [10.1006/jcss.1995.1003](https://doi.org/10.1006/jcss.1995.1003).

[6] Laurent Lessard, Xuezhou Zhang, and Xiaojin Zhu. “An Optimal Control Approach to Sequential Machine Teaching.” *Proceedings of the Twenty-Second International Conference on Artificial Intelligence and Statistics*, PMLR 89, 2019, pp. 2495–2503. [https://proceedings.mlr.press/v89/lessard19a.html](https://proceedings.mlr.press/v89/lessard19a.html).

[7] Manuel Garcia-Piqueras and José Hernández-Orallo. “Heuristic Search of Optimal Machine Teaching Curricula.” *Machine Learning*, vol. 112, 2023, pp. 4049–4080. DOI: [10.1007/s10994-023-06347-4](https://doi.org/10.1007/s10994-023-06347-4).

[8] Felipe Petroski Such, Aditya Rawal, Joel Lehman, Kenneth Stanley, and Jeffrey Clune. “Generative Teaching Networks: Accelerating Neural Architecture Search by Learning to Generate Synthetic Training Data.” *Proceedings of the 37th International Conference on Machine Learning*, PMLR 119, 2020, pp. 9206–9216. [https://proceedings.mlr.press/v119/such20a.html](https://proceedings.mlr.press/v119/such20a.html).

[9] Yewen Pu, Zachery Miranda, Armando Solar-Lezama, and Leslie Pack Kaelbling. “Selecting Representative Examples for Program Synthesis.” 2017. [arXiv:1711.03243](https://arxiv.org/abs/1711.03243).

[10] Shivam Garg, Dimitris Tsipras, Percy Liang, and Gregory Valiant. “What Can Transformers Learn In-Context? A Case Study of Simple Function Classes.” *Advances in Neural Information Processing Systems 35*, 2022.

[11] Peter Grünwald. “A Tutorial Introduction to the Minimum Description Length Principle.” 2004. [arXiv:math/0406077](https://arxiv.org/abs/math/0406077).

[12] Ray J. Solomonoff. “A Formal Theory of Inductive Inference, Part I.” *Information and Control*, vol. 7, no. 1, 1964, pp. 1–22. DOI: [10.1016/S0019-9958(64)90223-2](https://doi.org/10.1016/S0019-9958(64)90223-2).

[13] Kurt Gödel. “Über formal unentscheidbare Sätze der Principia Mathematica und verwandter Systeme I.” *Monatshefte für Mathematik und Physik*, vol. 38, 1931, pp. 173–198. DOI: [10.1007/BF01700692](https://doi.org/10.1007/BF01700692).

[14] Abhishek Sharma et al. “Assembly Theory Explains and Quantifies Selection and Evolution.” *Nature*, vol. 622, 2023, pp. 321–328. DOI: [10.1038/s41586-023-06600-9](https://doi.org/10.1038/s41586-023-06600-9).

[15] Rico Sennrich, Barry Haddow, and Alexandra Birch. “Neural Machine Translation of Rare Words with Subword Units.” *Proceedings of the 54th Annual Meeting of the Association for Computational Linguistics*, 2016, pp. 1715–1725. DOI: [10.18653/v1/P16-1162](https://doi.org/10.18653/v1/P16-1162).

[16] Taku Kudo and John Richardson. “SentencePiece: A Simple and Language Independent Subword Tokenizer and Detokenizer for Neural Text Processing.” *Proceedings of EMNLP 2018: System Demonstrations*, pp. 66–71. DOI: [10.18653/v1/D18-2012](https://doi.org/10.18653/v1/D18-2012).

[17] Jorie Koster-Hale and Rebecca Saxe. “Theory of Mind: A Neural Prediction Problem.” *Neuron*, vol. 79, no. 5, 2013, pp. 836–848. DOI: [10.1016/j.neuron.2013.08.020](https://doi.org/10.1016/j.neuron.2013.08.020).

[18] Diana I. Tamir and Mark A. Thornton. “Modeling the Predictive Social Mind.” *Trends in Cognitive Sciences*, vol. 22, no. 3, 2018, pp. 201–212. DOI: [10.1016/j.tics.2017.12.005](https://doi.org/10.1016/j.tics.2017.12.005).

[19] Piotr J. Gmytrasiewicz and Prashant Doshi. “A Framework for Sequential Planning in Multi-Agent Settings.” 2011. [arXiv:1109.2135](https://arxiv.org/abs/1109.2135).
