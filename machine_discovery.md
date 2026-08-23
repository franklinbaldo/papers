---
type: "Technical Paper"
title: "When the Learner Changes the Curriculum: Machine Discovery as Recursive Expansion of Verifiable Knowledge"
description: "Position paper defining machine discovery as a certified, provenance-aware transition between public epistemic states, with downstream curriculum expansion as its recursive consequence. §19's central claim now states the machine-originated/machine-assisted (Definition 2) restriction explicitly, absorbed from the r4/r5 adversarial-supportive exchange over §19's prior wording, edit cycle 13."
tags: [machine-discovery, epistemic-expansion, verification, provenance, formal-mathematics]
timestamp: 2026-08-22T00:00:00Z
---

# When the Learner Changes the Curriculum: Machine Discovery as Recursive Expansion of Verifiable Knowledge

**Franklin Baldo**  
Independent Researcher  
franklinbaldo@gmail.com

---

> **Position paper.** This article proposes a formal framework and an experimental
> program. It does not claim that any particular recent machine-generated proof
> has survived independent mathematical audit, that formal verification settles
> novelty or importance, or that current systems autonomously conduct science in
> the full institutional sense. The definitions and hypotheses below are intended
> to make such claims testable rather than rhetorical.

## Abstract

Machine learning is ordinarily described as the acquisition of predictive or executable competence from an antecedent body of data. Machine discovery begins at a different boundary: a system produces an artifact that, after independent certification and novelty audit, changes the body of public knowledge available to later learners. The relevant unit is therefore not an output considered in isolation, but a transition between epistemic states.

This paper formalizes that transition. A public epistemic state contains a language, admitted inference rules, accepted claims, certificates, provenance records, and an audit policy. A candidate discovery contains a claim, a certificate, and a production trace. It becomes an accepted discovery only when it is well formed, survives an appropriate verifier, is novel relative to an explicitly frozen knowledge snapshot and equivalence standard, and is incorporated into the public state. Correctness, novelty, provenance, autonomy, significance, and downstream usefulness are separated rather than collapsed into a single label.

The central recursive consequence is **curriculum expansion**. Once an accepted artifact becomes a reusable theorem, algorithm, representation, dataset, or experimental result, subsequent learners no longer face the same informational environment. The learner has changed the curriculum. We distinguish extensional expansion of accepted claims from resource-bounded expansion of what can be derived, solved, or taught; define measures of downstream reach and fertility; state propositions clarifying why conjecture generation, theorem proving, rediscovery, and discovery are not equivalent; and propose benchmarks based on frozen corpora, independent verification, provenance ledgers, semantic duplicate search, and controlled reuse by later agents.

The framework is domain-general but mathematics supplies the cleanest initial test bed because certificates can often be made machine-checkable. The thesis is deliberately narrow: **machine discovery is a certified and provenance-aware enlargement of a public epistemic state, and recursive machine discovery occurs when that enlargement measurably improves the learning or discovery capacity of later systems.**

**Keywords:** machine discovery, automated theorem proving, scientific discovery, formal verification, novelty, provenance, epistemic state, recursive curriculum, cumulative knowledge

---

## 1. From Learning Within a Curriculum to Changing It

A learner normally receives a world already partitioned into admissible objects. There is a corpus, a language, a set of tasks, a library of results, and a convention for deciding whether an answer is correct. Even when the learner develops an internal representation not supplied by the teacher, its success is measured against an environment whose relevant public contents precede the learning episode.

Discovery introduces a historical asymmetry. Before the event, a certain claim, construction, method, or measured regularity is not part of the accepted public state. After the event, it is. Later learners may cite it, prove consequences from it, train on it, use it as a lemma, implement it as an algorithm, or design experiments around it.

The decisive distinction is therefore not:

$$
\text{human output}
\quad\text{versus}\quad
\text{machine output}.
$$

It is:

$$
\text{candidate artifact}
\quad\text{versus}\quad
\text{certified epistemic transition}.
$$

A fluent proof-shaped text is not yet a theorem. A numerically striking pattern is not yet a law. A formally checked theorem need not be new. A new theorem need not be important. An important result need not have been autonomously produced by the machine that first displayed it. Each proposition concerns a different property and requires different evidence.

The motivating observation can be stated without depending on any single contemporary announcement:

> A machine becomes historically consequential when a successful internal construction ceases to belong only to that machine and becomes a certified public object that restructures what later learners can infer.

This paper develops the minimum apparatus needed to say when that has happened.

---

## 2. Scope and Non-Claims

The framework studies **publicly auditable discovery events**. It does not attempt to define creativity, consciousness, understanding, authorship, or scientific personhood.

It does not claim:

- that novelty can be established absolutely rather than relative to a search scope and knowledge snapshot;
- that a proof assistant verifies the intended informal theorem merely because it accepts some formal statement;
- that empirical findings admit certificates as final as formal proofs;
- that machine involvement should be represented by one binary autonomy label;
- that a valid and novel result is automatically significant;
- that an artifact must improve future performance to count as a discovery;
- that every increase in a formal library increases practical mathematical reach;
- that self-training on unverified outputs enlarges public knowledge;
- that a discovery produced by a human-machine system belongs exclusively to either component;
- that one spectacular output establishes a general capacity for autonomous research.

The proposal is operational. Every discovery claim is indexed to:

- a domain;
- a frozen prior knowledge state;
- a language and equivalence standard;
- a verification policy;
- a provenance record;
- a date of acceptance;
- and, when significance is claimed, a downstream task distribution and resource budget.

---

## 3. Related Work and the Missing Distinction

Computational systems have long assisted mathematical and scientific discovery. Recent systems make several stages unusually explicit.

Machine learning has helped mathematicians identify patterns that led to new conjectures and theorems [1]. The Ramanujan Machine generates numerical conjectures about fundamental constants, intentionally separating conjecture generation from proof [2]. AlphaTensor discovered provably correct matrix-multiplication algorithms that improved known bounds in specified settings [3]. FunSearch combines a language model with an executable evaluator and reported new constructions and algorithms for established open problems [4]. AlphaGeometry combines learned guidance with symbolic deduction and produces machine-checkable geometric arguments in its formal domain [5].

Other work targets self-improving formal mathematics. Minimo jointly generates conjectures and searches for proofs from axioms [6]. Self-supervised theorem-discovery systems grow theorem libraries whose entries are reused as lemmas and can improve later proof performance [7]. Recent systems combine informal reasoning, retrieval, formalization, and Lean verification to resolve research-level conjectures [8].

These advances establish important components:

- candidate generation;
- conjecture formation;
- program search;
- symbolic deduction;
- formal proof checking;
- library growth;
- and reuse by later proof search.

What remains conceptually under-specified is the transition from **a system emitted an artifact** to **the public epistemic state expanded**, and then from public expansion to **recursive improvement of later learners**.

The contribution of this paper is not another discovery algorithm. It is a framework that keeps six questions distinct:

1. Is the claim well formed?
2. Is it correct under the relevant standard?
3. Is it new relative to the prior public state?
4. Who or what causally contributed which indispensable parts?
5. Does acceptance enlarge the public state?
6. Does the enlargement change what later systems can learn or discover?

The first five define an auditable discovery event. The sixth measures its recursive consequence.

---

## 4. Public Epistemic States

### 4.1 State structure

Let a public epistemic state at time $t$ be:

$$
K_t=(\mathcal L_t,\mathcal R_t,\mathcal C_t,\Pi_t,\mathcal P_t,\mathcal A_t).
$$

Its components are:

- $\mathcal L_t$: the admitted language, ontology, and formation rules;
- $\mathcal R_t$: inference rules, experimental protocols, and admissible transformations;
- $\mathcal C_t$: accepted claims or constructions;
- $\Pi_t$: certificates associated with accepted claims;
- $\mathcal P_t$: provenance records;
- $\mathcal A_t$: the audit and acceptance policy.

The state is public in the operational sense that appropriately situated auditors can inspect the artifacts and apply the stated policy. Publicity does not require unrestricted access to every private datum. It requires enough disclosure for the claimed level of acceptance.

### 4.2 Closure

For formal domains, define the deductive closure:

$$
\operatorname{Cl}_{K_t}(\mathcal C_t)
=
\left\{
\varphi:\mathcal C_t\vdash_{\mathcal R_t}\varphi
\right\}.
$$

This closure is an ideal object. It may be infinite or computationally inaccessible. Practical discovery must therefore also use a resource-bounded closure:

$$
\operatorname{Cl}^{B}_{K_t}(\mathcal C_t),
$$

containing claims recoverable by admitted procedures within budget $B$, where $B$ may constrain computation, proof length, retrieval, experiments, time, or human attention.

For empirical domains, closure is not purely deductive. It includes claims licensed by accepted data, uncertainty models, calibration procedures, and replication rules. The same notation will be used, but the audit policy must state what inferential relation is intended.

### 4.3 Equivalence

Syntactic difference is not novelty. Let:

$$
\varphi\equiv_t\psi
$$

mean that $\varphi$ and $\psi$ count as the same contribution under the equivalence standard at time $t$.

The standard may include:

- definitional equality;
- logical equivalence;
- renaming of variables;
- isomorphism;
- known translations between formalisms;
- algorithmic equivalence under a cost model;
- or domain-expert judgment that two formulations express the same result.

No universal equivalence relation is assumed. A discovery report must identify the relation used.

---

## 5. Candidate Artifacts

A candidate artifact is:

$$
a=(\varphi,\pi,\mu,\sigma),
$$

where:

- $\varphi$ is the proposed claim, construction, algorithm, or empirical regularity;
- $\pi$ is its certificate or evidential package;
- $\mu$ is the production and provenance trace;
- $\sigma$ is the declared scope, including the prior snapshot and standards used.

The four fields answer different questions.

The claim $\varphi$ says what is being added. The certificate $\pi$ says why it should be accepted. The provenance trace $\mu$ says how it was produced. The scope $\sigma$ says relative to what background the words *new*, *correct*, and *machine-generated* are being used.

A system that emits $\varphi$ but cannot supply $\pi$ has generated a candidate. A system that supplies a valid $\pi$ for a known $\varphi$ has solved or reproved a result. A system that supplies a new $\varphi$ with an invalid $\pi$ has produced an unconfirmed conjecture. None of these categories should be redescribed as discovery merely because the text is impressive.

---

## 6. Certification

### 6.1 Domain-relative certificates

A certificate is evidence that can be checked by a procedure more reliable and more narrowly specified than the generative process that produced the candidate.

In formal mathematics, a certificate may be:

- a proof term accepted by a small trusted kernel;
- an independently reconstructed formal proof;
- or a conventional proof that survives line-by-line expert audit.

In algorithm discovery, it may combine:

- executable source code;
- a correctness proof;
- complexity analysis;
- tests designed to expose boundary failures;
- and reproducible performance measurements.

In empirical science, it may include:

- preregistered hypotheses;
- calibrated instruments;
- raw data and code;
- uncertainty analysis;
- negative controls;
- and independent replication.

The certificate relation is written:

$$
V_{\mathcal A_t}(\varphi,\pi)=1.
$$

This means only that $\pi$ satisfies the acceptance policy $\mathcal A_t$. It does not imply that the policy is infallible.

### 6.2 Independence is graded

A verifier is not independent merely because it is a different process name. Generator and verifier may share:

- training data;
- theorem retrieval systems;
- formalization errors;
- libraries;
- numerical assumptions;
- prompts;
- software bugs;
- or institutional incentives.

Let the audit graph $G_a$ contain the generators, translators, checkers, human reviewers, codebases, datasets, and formal kernels involved in accepting $a$. A discovery report should identify common-mode dependencies in $G_a$.

Verification strength is therefore graded. A useful hierarchy is:

1. **self-assertion:** the generator judges its own output;
2. **same-stack checking:** another component checks the result but shares most dependencies;
3. **heterogeneous checking:** independent implementations or methods agree;
4. **small-kernel verification:** a compact trusted checker validates a complete certificate;
5. **replicated reconstruction:** independent parties reconstruct the result from disclosed artifacts.

Different domains permit different maximum levels. The paper does not require a fictional standard of perfect independence. It requires that dependence be recorded rather than hidden.

### 6.3 Formalization soundness

A machine-checked proof can establish:

$$
\Gamma\vdash\widehat\varphi,
$$

while the intended informal claim is $\varphi$. Acceptance also requires a defensible bridge:

$$
\operatorname{Interpret}(\widehat\varphi)=\varphi.
$$

A proof assistant can reject invalid derivations inside its formal system. It cannot, by itself, guarantee that the formal statement captures the intended theorem, that the imported axioms are appropriate, or that novelty was assessed correctly.

---

## 7. Novelty

### 7.1 Snapshot-relative novelty

Absolute novelty is generally unavailable. The public corpus is incomplete, terminology varies, equivalent results may be dispersed across fields, and exhaustive semantic search is infeasible.

Novelty should therefore be stated relative to a frozen snapshot:

$$
S_t=(K_t,\equiv_t,B_N),
$$

where $B_N$ is the novelty-audit budget.

A candidate is **snapshot-novel** when no equivalent prior result is found in the admitted closure and search process:

$$
\nexists\psi\in
\operatorname{Cl}^{B_N}_{K_t}(\mathcal C_t)
\quad\text{such that}\quad
\psi\equiv_t\varphi.
$$

This is an auditable negative search result, not a metaphysical guarantee.

### 7.2 Levels of novelty

At least four forms should be distinguished:

- **statement novelty:** the proposition itself was not previously available;
- **proof novelty:** the statement was known, but the proof introduces a new route;
- **method novelty:** the proof or algorithm instantiates a reusable technique;
- **performance novelty:** an artifact improves a previously best-known bound or measurable result.

One artifact may satisfy several levels. A new proof of an old theorem is not statement discovery, but it may be a genuine discovery of method. A new program that reproduces a known optimum is not performance discovery, but may reveal a simpler construction.

### 7.3 Contamination and rediscovery

A machine may reproduce a result from its training corpus without retrieving a recognizable citation. It may also reconstruct a result independently. The output alone does not distinguish memorization, diffuse influence, and independent derivation.

The provenance trace should therefore record:

- training-data disclosures to the extent available;
- retrieval queries and returned documents;
- prompts and human hints;
- intermediate candidate histories;
- tool calls;
- and the timing of literature searches.

When full training provenance is unavailable, autonomy claims must weaken accordingly. Correctness and public novelty can still be established even when the internal originality of the model cannot.

---

## 8. Provenance and Contribution

### 8.1 Discovery is often distributed

A modern discovery pipeline may include:

- a human selecting the problem;
- a model proposing a representation;
- a search procedure generating candidates;
- a theorem database supplying lemmas;
- a proof assistant checking derivations;
- another model formalizing the argument;
- experts repairing gaps;
- and editors identifying the relevant prior art.

Calling the final result either *human* or *machine* erases the causal structure that matters.

Represent the production trace as a directed acyclic graph:

$$
\mu=(N,E),
$$

whose nodes are contributions and whose edges record informational dependence.

Nodes may be labeled by function:

- problem formulation;
- representation design;
- candidate generation;
- search control;
- lemma selection;
- proof construction;
- counterexample search;
- formalization;
- verification;
- novelty audit;
- exposition;
- and interpretation.

### 8.2 Essential contribution

A contribution is **causally essential under an ablation family** when removing or replacing it prevents the pipeline from producing an equivalent accepted artifact within the specified resource budget.

Let $P$ be the observed pipeline and $P\setminus n$ an admissible ablation of node $n$. Define:

$$
I_B(n,a)=
\mathbf 1
\left[
P\text{ produces }a\text{ within }B
\ \land\ 
P\setminus n\text{ does not produce an equivalent accepted artifact within }B
\right].
$$

This is not a complete theory of credit. It is a reproducible test of indispensability relative to stated alternatives.

### 8.3 Autonomy vector

Instead of one autonomy score, report a vector:

$$
\alpha(a)=
(\alpha_q,\alpha_r,\alpha_g,\alpha_p,\alpha_v,\alpha_n,\alpha_e),
$$

for autonomy in:

- question selection $q$;
- representation $r$;
- generation $g$;
- proof or experiment $p$;
- verification $v$;
- novelty audit $n$;
- exposition $e$.

Each component should be tied to disclosed intervention or ablation evidence. A result can be machine-generated but human-selected, machine-proved but human-formalized, or machine-proposed but independently machine-verified. These are different scientific facts.

---

## 9. Definition of a Machine Discovery Event

Let $a=(\varphi,\pi,\mu,\sigma)$ be a candidate produced by a pipeline containing at least one machine component.

### Definition 1: Accepted discovery

The transition:

$$
K_t\xrightarrow{a}K_{t+1}
$$

is an **accepted discovery event** relative to $(K_t,\equiv_t,\mathcal A_t,B_N)$ when:

1. **Admissibility:** $\varphi$ is well formed in $\mathcal L_t$ or extends the language through an explicitly accepted definition.
2. **Certification:** $V_{\mathcal A_t}(\varphi,\pi)=1$.
3. **Snapshot novelty:** no equivalent prior contribution is found under the stated novelty procedure.
4. **Provenance sufficiency:** $\mu$ supports the level of machine-contribution claim being made.
5. **Public uptake:** $a$ is incorporated into the accepted state, with its certificate, scope, and provenance attached.

The updated state is:

$$
K_{t+1}=U(K_t,a).
$$

### Definition 2: Machine-assisted and machine-originated discovery

An accepted discovery is **machine-assisted** when at least one machine contribution lies on an essential path in $\mu$.

It is **machine-originated relative to an ablation family** when a machine component is essential to the first generation of the novel claim, construction, or method, rather than only to verification, formatting, or retrieval.

The adjective *autonomous* should be reserved for a stronger claim whose relevant components of $\alpha(a)$ are high under disclosed intervention tests. No universal threshold is proposed.

### Definition 3: Recursive machine discovery

An accepted discovery event is **recursively productive** for learner family $\mathcal F$ and budget $B$ when incorporating $a$ into the curriculum or library yields a reproducible improvement in later learning or discovery:

$$
\mathbb E_{L\sim\mathcal F}
\left[
\operatorname{Perf}_B(L,K_{t+1})
-
\operatorname{Perf}_B(L,K_t)
\right]
>0
$$

on preregistered held-out tasks, after charging the cost of storing, retrieving, and interpreting $a$.

Recursive productivity is not required for discovery. It measures whether the discovery changes the capabilities of later learners.

---

## 10. Immediate Propositions

### Proposition 1: Validity without novelty is not statement discovery

If:

$$
V_{\mathcal A_t}(\varphi,\pi)=1
$$

but there exists:

$$
\psi\in\operatorname{Cl}^{B_N}_{K_t}(\mathcal C_t)
\quad\text{with}\quad
\psi\equiv_t\varphi,
$$

then $a$ is not a snapshot-novel statement discovery.

**Reason.** Certification establishes admissibility to the accepted state; it does not establish that the state has gained a new equivalence class of claims. The artifact may still be a new proof, method, formalization, or compression.

### Proposition 2: Novelty without certification is a candidate, not accepted knowledge

If $\varphi$ is snapshot-novel but:

$$
V_{\mathcal A_t}(\varphi,\pi)=0
$$

or remains undetermined, then $a$ does not induce an accepted discovery event.

**Reason.** The public state may record the conjecture and its provenance, but it must distinguish the candidate ledger from the accepted-claim ledger.

### Proposition 3: Accepted novel claims extend extensional closure

Suppose $a$ is accepted, $\varphi\notin\operatorname{Cl}_{K_t}(\mathcal C_t)$ up to $\equiv_t$, and $K_{t+1}$ preserves the prior rules and claims. Then:

$$
\operatorname{Cl}_{K_t}(\mathcal C_t)
\subsetneq
\operatorname{Cl}_{K_{t+1}}(\mathcal C_{t+1}).
$$

**Proof sketch.** Monotonic preservation gives inclusion. Acceptance adds $\varphi$ or an equivalent new class to the latter closure, while novelty excludes it from the former.

### Proposition 4: Extensional expansion does not imply practical expansion

There exist accepted novel claims for which:

$$
\operatorname{Cl}_{K_t}(\mathcal C_t)
\subsetneq
\operatorname{Cl}_{K_{t+1}}(\mathcal C_{t+1})
$$

but:

$$
\operatorname{Cl}^{B}_{K_t}(\mathcal C_t)
=
\operatorname{Cl}^{B}_{K_{t+1}}(\mathcal C_{t+1})
$$

on a specified task language and budget $B$.

**Reason.** The new result may be too costly to retrieve or apply, irrelevant to the task family, or an isolated fact with no budget-feasible consequences.

### Proposition 5: Unverified self-training enlarges a candidate state, not the accepted state

Let a learner append its own unchecked outputs to its future context. This can enlarge its internal candidate set, but it does not enlarge $\mathcal C_t$ unless the outputs pass $\mathcal A_t$.

**Reason.** Repetition, confidence, or downstream reuse by the same generator does not supply an independent acceptance relation.

### Proposition 6: Curriculum expansion can create compounding but not automatic improvement

If accepted artifacts are reusable by later learners, then the sequence:

$$
K_0\rightarrow K_1\rightarrow\cdots\rightarrow K_T
$$

creates the possibility of cumulative gains. It does not guarantee monotonic practical performance because added artifacts impose storage, search, conflict-resolution, and interpretation costs.

**Reason.** A larger library can increase both available lemmas and retrieval burden. Recursive discovery requires measured net benefit, not mere accumulation.

---

## 11. Measuring Epistemic Expansion

### 11.1 Extensional gain

For a finite evaluation universe $\Omega$ of claims or tasks, define:

$$
G_{\mathrm{ext}}(a;\Omega)
=
\left|
\operatorname{Cl}_{K_{t+1}}(\mathcal C_{t+1})\cap\Omega
\right|
-
\left|
\operatorname{Cl}_{K_t}(\mathcal C_t)\cap\Omega
\right|.
$$

This measures added reach inside $\Omega$. It is not an absolute measure of importance.

### 11.2 Resource-bounded reach

Let $\mathcal T$ be a task distribution. Define:

$$
\operatorname{Reach}_B(K,\mathcal T)
=
\Pr_{\tau\sim\mathcal T}
\left[
\tau\text{ is solved from }K\text{ within }B
\right].
$$

The practical gain is:

$$
G_B(a;\mathcal T)
=
\operatorname{Reach}_B(K_{t+1},\mathcal T)
-
\operatorname{Reach}_B(K_t,\mathcal T).
$$

The budget must charge:

- retrieval;
- representation conversion;
- proof checking;
- additional context;
- tool execution;
- and human or machine review.

### 11.3 Fertility

A result is fertile when it supports many nontrivial downstream transitions. One operational measure is:

$$
F_{B,H}(a)
=
\sum_{h=1}^{H}
\gamma^{h-1}
\mathbb E
\left[
G_B(a;\mathcal T_h)
\right],
$$

where $\mathcal T_h$ contains tasks at dependency distance $h$ from the artifact and $0<\gamma\leq1$ discounts remote effects.

Fertility should be measured prospectively where possible. Retrospective citation counts confound scientific utility with visibility, prestige, and field size.

### 11.4 Compression and conceptual gain

A discovery can matter by shortening explanations or proofs even when it adds no new theorem statement. Let $L_K(\psi)$ be the shortest admitted description or proof of $\psi$ relative to state $K$. Define:

$$
G_{\mathrm{comp}}(a;\Omega)
=
\sum_{\psi\in\Omega}
\max\left\{
0,
L_{K_t}(\psi)-L_{K_{t+1}}(\psi)
\right\}.
$$

This captures one form of method discovery: a reusable representation can reorganize an existing field without changing which statements are true.

---

## 12. The Recursive Curriculum

### 12.1 The basic loop

The discovery cycle is:

$$
K_t
\xrightarrow{\text{learning and search}}
a_t
\xrightarrow{\text{audit}}
K_{t+1}
\xrightarrow{\text{teaching and reuse}}
L_{t+1}.
$$

Expanded:

$$
\text{learning}
\rightarrow
\text{representation formation}
\rightarrow
\text{candidate generation}
\rightarrow
\text{certification}
\rightarrow
\text{novelty audit}
\rightarrow
\text{public uptake}
\rightarrow
\text{curriculum expansion}
\rightarrow
\text{new learning}.
$$

The final arrow is the central recursive step. A later learner does not merely imitate the earlier learner. It receives a changed world.

### 12.2 Historical dependence

Let learner $L$ have update rule $U_L$ and curriculum $C(K_t)$. Then:

$$
M_{t+1}=U_L(M_t,C(K_t)).
$$

After an accepted discovery:

$$
M'_{t+1}=U_L(M_t,C(K_{t+1})).
$$

Even with the same architecture and compute, the learner may reach different states because the curriculum now contains a new theorem, proof, algorithm, vocabulary, or experimental fact.

Machine discovery is therefore not merely a capability of a model. It is a mechanism of path dependence in the collective knowledge system.

### 12.3 Recursive versus circular training

The distinction between recursive discovery and circular self-training is structural:

- **circular self-training:** the system treats its own outputs as targets without an external acceptance boundary;
- **recursive discovery:** outputs cross an audit boundary, enter a versioned public state, and are then available to later systems as independently identified artifacts.

The first may amplify both competence and error. The second creates an accountable historical record in which each accepted transition can be challenged or reversed.

---

## 13. A Discovery Ledger

Every claimed machine discovery should be accompanied by a versioned ledger.

### 13.1 Minimum record

The ledger should contain:

1. **Prior snapshot** — exact corpus, theorem library, datasets, code, and date.
2. **Problem statement** — including who selected it and how success was defined.
3. **Generation trace** — prompts, tool calls, retrieved sources, candidate history, and compute budget.
4. **Artifact** — statement, proof, code, data, and human-readable exposition.
5. **Certificate** — formal proof, evaluator, replication package, or domain-specific evidence.
6. **Audit graph** — components and shared dependencies among generator and verifiers.
7. **Novelty search** — databases, queries, equivalence criteria, expert review, and unresolved uncertainty.
8. **Contribution graph** — human and machine roles, with ablations where feasible.
9. **Acceptance status** — candidate, provisionally accepted, formally accepted, replicated, corrected, or retracted.
10. **Downstream tests** — whether later learners use the artifact and with what net gain.

### 13.2 Status must remain revisable

A discovery state is not immutable. Let:

$$
\operatorname{status}_t(a)
\in
\{
\text{candidate},
\text{accepted},
\text{replicated},
\text{corrected},
\text{superseded},
\text{retracted}
\}.
$$

Corrections should preserve the original artifact and audit history. Deleting failed results destroys evidence about the reliability of the discovery process.

---

## 14. False Positives and Category Errors

A rigorous benchmark must deliberately generate cases that resemble discovery without satisfying the definition.

### 14.1 Rediscovery

The system reconstructs a known result under different notation. This may demonstrate reasoning competence but fails statement novelty.

### 14.2 Citation laundering

A retrieved result is paraphrased without preserved provenance and later presented as model-generated.

### 14.3 Formal vacuity

A proof assistant accepts a theorem because assumptions encode the conclusion, definitions trivialize the claim, or an inconsistent axiom is imported.

### 14.4 Specification gaming

An algorithm improves the evaluator while failing the intended task. Executable verification protects only the written specification.

### 14.5 Shared-verifier failure

Generator and checker rely on the same false lemma, numerical library bug, or mistranslation.

### 14.6 Novel but insignificant output flooding

A system produces vast numbers of true, formally novel, low-value statements. Novelty volume is not epistemic progress unless the evaluation distinguishes useful reach, compression, or explanatory gain.

### 14.7 Hidden human completion

Experts repair essential steps while the public description attributes the complete result to the model.

### 14.8 Benchmark leakage

The alleged open problem or solution appears in training data, retrieval caches, private evaluation material, or generated synthetic corpora.

### 14.9 Self-confirmation

Multiple agents derived from the same model family agree because they share the same error distribution.

### 14.10 Premature historical claims

A fresh result is described as having changed mathematics before independent experts have checked it, found precedents, and attempted reuse.

---

## 15. Experimental Program

The cleanest initial environment is formal mathematics because the claim language, prior library, and certificate relation can be frozen precisely.

### 15.1 Experiment 1: Frozen-library theorem discovery

Freeze a proof-assistant library at commit $K_t$. Permit the discovery agent access only to:

- the frozen axioms and theorems;
- documented tactics;
- a declared compute budget;
- and no later commits.

The agent generates theorem-certificate pairs. Evaluate:

- kernel acceptance;
- semantic deduplication against $K_t$;
- proof novelty;
- theorem usefulness on hidden downstream tasks;
- and contribution under search and retrieval ablations.

### 15.2 Experiment 2: Matched rediscovery controls

Mix genuinely withheld results with already-known results translated into unfamiliar notation. The system and novelty auditor must distinguish:

- new statement;
- known statement under translation;
- new proof of known statement;
- and invalid candidate.

This tests whether the pipeline discovers or merely renames.

### 15.3 Experiment 3: Curriculum-expansion trial

Construct two later-agent conditions:

$$
L^{+a}: K_{t+1}=U(K_t,a),
$$

$$
L^{-a}: K_t\text{ plus a token- and compute-matched control artifact}.
$$

Evaluate both on preregistered tasks not used to select $a$. Measure:

- proof success;
- search depth;
- compute;
- context use;
- transfer;
- and calibration.

The control prevents the mere presence of more text from being mistaken for epistemic gain.

### 15.4 Experiment 4: Audit-diversity study

Submit the same candidates to:

- self-evaluation;
- same-model peer evaluation;
- different-model evaluation;
- formal checking;
- independent human reconstruction;
- and heterogeneous software implementations.

Track which accepted results survive later challenge. Test whether audit diversity predicts durability better than nominal reviewer count.

### 15.5 Experiment 5: Provenance ablations

Remove or replace each major node in $\mu$:

- human problem framing;
- retrieval;
- model generation;
- symbolic search;
- formalizer;
- verifier;
- expert repair.

Estimate which components are essential for candidate generation, correctness, novelty recognition, and exposition.

### 15.6 Experiment 6: Open-literature discovery

Move from a frozen formal library to natural-language mathematics. Require:

- timestamped literature snapshots;
- multilingual and cross-field semantic search;
- expert prior-art review;
- independent proof reconstruction;
- and explicit residual uncertainty about novelty.

This experiment is harder precisely because the equivalence and closure relations are no longer mechanically enumerable.

### 15.7 Experiment 7: Empirical discovery

For domains with executable simulations or automated laboratories, separate:

- hypothesis generation;
- experiment design;
- data acquisition;
- model selection;
- replication;
- and theory incorporation.

A candidate should not be credited with discovery merely for predicting held-out data if the claimed mechanism fails intervention or replication tests.

---

## 16. Falsifiable Hypotheses

### H1: Certification sharply reduces false discovery claims

Pipelines with external certificates will have lower later-retraction rates than output-only pipelines, after controlling for candidate difficulty.

### H2: Snapshot-aware novelty audit reduces rediscovery

Frozen-corpus semantic search plus expert equivalence review will identify substantially more disguised prior results than keyword search alone.

### H3: Formal acceptance alone weakly predicts downstream usefulness

Kernel-accepted novel lemmas will show a heavy-tailed distribution of practical gain, with many producing negligible improvement on held-out proof tasks.

### H4: Fertile discoveries improve later search under fixed budgets

Artifacts with high measured $F_{B,H}$ will reduce proof-search cost or increase solution rate for later agents relative to matched controls.

### H5: Audit diversity predicts durability

Candidates checked through heterogeneous methods with low common-mode dependence will survive later scrutiny more often than candidates receiving the same number of same-stack reviews.

### H6: Provenance decomposition changes attribution

Ablation-based contribution graphs will frequently contradict binary descriptions such as *the model discovered* or *the human discovered*.

### H7: Recursive curricula can outperform static curricula

A sequence of accepted, useful machine-generated artifacts incorporated into later training will produce greater held-out performance than a static curriculum with equal total compute and token budget.

### H8: Unfiltered recursive curricula can degrade performance

When candidate artifacts are incorporated without independent certification and retrieval controls, error propagation and search burden will sometimes outweigh the benefit of added material.

### H9: Method novelty can matter without statement novelty

New proofs or representations of known theorems will sometimes yield larger downstream practical gains than isolated novel theorem statements.

### H10: Autonomy is stage-specific

Systems that appear highly autonomous at candidate generation will often depend strongly on human framing, retrieval, formalization, or novelty audit, producing nonuniform autonomy vectors.

---

## 17. A Contemporary Motivating Episode

In 2026, OpenAI released a collection titled *Ten Advances in Mathematics and Theoretical Computer Science*, describing results attributed to an internal model, including an explicit proposed non-sofic group and other claimed advances [9]. Such a release is an appropriate motivating episode because it places all the distinctions in this paper under pressure at once:

- Are the arguments correct?
- Are the formal statements the intended ones?
- Which results are genuinely new?
- What literature and tools were available to the system?
- Which steps were machine-generated, machine-checked, or human-repaired?
- What level of independent audit has occurred?
- Will the methods be reused by later mathematicians or systems?

The framework deliberately does not answer those empirical questions from the existence of a polished document. A newly released manuscript is a candidate package. Its historical status depends on the audit, novelty, provenance, uptake, and downstream reuse that follow.

That restraint is not skepticism about machine discovery. It is the condition that makes a credible claim of machine discovery possible.

---

## 18. Implications

### 18.1 For model evaluation

Solving known benchmark problems measures competence against an existing curriculum. Discovery evaluation must additionally freeze the prior state, establish novelty, and show a valid transition beyond it.

### 18.2 For scientific publishing

Papers reporting machine-generated discoveries should publish provenance and audit ledgers alongside conventional methods and results. The key reproducibility question is not merely whether the final artifact can be regenerated, but whether its correctness, novelty, and attribution can be independently reconstructed.

### 18.3 For formal libraries

Proof libraries should distinguish:

- imported human results;
- machine formalizations of known results;
- machine-generated proofs;
- machine-proposed novel statements;
- and externally accepted novel discoveries.

This metadata enables later studies of recursive curriculum effects.

### 18.4 For authorship and credit

Authorship policy cannot be derived from the technical definition of discovery. The contribution graph can, however, replace vague narratives with evidence about who framed, generated, proved, checked, interpreted, and communicated the result.

### 18.5 For safety

Recursive knowledge expansion can amplify both truth and error. Versioned acceptance boundaries, heterogeneous audit, provenance, and reversible status changes are not administrative overhead. They are control mechanisms for systems that may increasingly write the curricula from which later systems learn.

---

## 19. Conclusion

Machine discovery should not be defined by surprise, eloquence, scale of search, or the prestige of the generating model. It should be defined by a disciplined transition:

$$
\text{candidate}
\rightarrow
\text{certificate}
\rightarrow
\text{novelty audit}
\rightarrow
\text{provenance}
\rightarrow
\text{public uptake}.
$$

The transition enlarges an epistemic state. Its recursive consequence appears when later learners receive that enlargement as part of their curriculum:

$$
K_t
\rightarrow
K_{t+1}
\rightarrow
L_{t+1}
\rightarrow
K_{t+2}.
$$

This yields the paper's central claim:

> **A machine discovers when it makes a machine-originated contribution — essential to the first generation of the claim, construction, or method, not only to its verification, formatting, or retrieval (Definition 2) — to an artifact that survives the relevant certificate and novelty procedures and thereby enlarges a public epistemic state. The discovery becomes recursive when that enlargement measurably changes what later learners can infer, solve, or discover.**

This restates the claim with Definition 2's machine-originated/machine-assisted distinction made explicit on the surface of the text rather than left for the reader to supply from context. A verification-only or formatting-only machine contribution — however essential to the pipeline that produced the artifact — is machine-assisted, not machine discovery, under this statement. Both `otherwise/machine-discovery-scope.md` (rounds 4–5) and `yesindeed/definition1-machine-discovery-defense.md` (§§3.6–3.7) converged on this specific textual fix as removing a genuine ambiguity in the prior wording, independent of their continuing disagreement over whether Definition 1 itself needs its own generation-essentiality requirement — that broader question is not resolved by this revision and remains open in the adversarial/supportive exchange.

A learner changes the curriculum not when it produces a remarkable-looking answer, but when its contribution becomes a durable and reusable part of what comes next.

---

## References

[1] Davies, A. et al. “Advancing mathematics by guiding human intuition with AI.” *Nature* 600, 70–74 (2021). https://doi.org/10.1038/s41586-021-04086-x

[2] Raayoni, G. et al. “Generating conjectures on fundamental constants with the Ramanujan Machine.” *Nature* 590, 67–73 (2021). https://doi.org/10.1038/s41586-021-03229-4

[3] Fawzi, A. et al. “Discovering faster matrix multiplication algorithms with reinforcement learning.” *Nature* 610, 47–53 (2022). https://doi.org/10.1038/s41586-022-05172-4

[4] Romera-Paredes, B. et al. “Mathematical discoveries from program search with large language models.” *Nature* 625, 468–475 (2024). https://doi.org/10.1038/s41586-023-06924-6

[5] Trinh, T. H. et al. “Solving olympiad geometry without human demonstrations.” *Nature* 625, 476–482 (2024). https://doi.org/10.1038/s41586-023-06747-5

[6] Poesia, G., Broman, D., Haber, N. D., and Goodman, N. D. “Learning Formal Mathematics From Intrinsic Motivation.” arXiv:2407.00695 (2024). https://arxiv.org/abs/2407.00695

[7] Ota, K., Osa, T., and Harada, T. “Self-Supervised Theorem Discovery in a Formal Axiomatic System.” arXiv:2606.28747 (2026). https://arxiv.org/abs/2606.28747

[8] Ju, H. et al. “Automated Conjecture Resolution with Formal Verification.” arXiv:2604.03789 (2026). https://arxiv.org/abs/2604.03789

[9] OpenAI. *Ten Advances in Mathematics and Theoretical Computer Science.* (2026). https://cdn.openai.com/pdf/ten-proofs-oai.pdf
