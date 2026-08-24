---
type: "Technical Paper"
title: "Structural Identification from Restricted Truths: Version Spaces, Invariance, and the Cost of Isolating a Structure"
description: "A mathematical theory note formalizing identification of a structure up to equivalence from a restricted family of invariant truths, with machine-checked Lean 4 proofs of the core results."
tags: [structural-identification, model-theory, teaching-dimension, version-spaces, lean4, formal-verification]
timestamp: 2026-08-24T03:40:00Z
---

# Structural Identification from Restricted Truths: Version Spaces, Invariance, and the Cost of Isolating a Structure

**Franklin Baldo**  
Independent Researcher  
franklinbaldo@gmail.com

---

> **Mathematical theory note with machine-checked core.** This paper does not claim that categoricity, Scott sentences, teaching dimension, distinguishing formulas, or version spaces are new. Its purpose is narrower: to place structural equivalence, admissible truth families, hypothesis classes, and explicit query cost in one formal object; prove the resulting identification laws; expose a triviality in naive formula-count definitions; and provide a Lean 4 formalization of the core propositions. The finite optimization problem is shown to be exactly a weighted hitting/set-cover problem over non-equivalent competitors.

## Abstract

Suppose an unknown mathematical object is known only through truths that it satisfies. When do those truths determine the object up to isomorphism, and how much information is required? A naive answer counts the number of true sentences needed to isolate the target. That quantity is usually ill-posed: if the admissible language is closed under finite conjunction and each sentence costs one unit, every finite identifying set collapses to one sentence. Meaningful identification complexity must therefore be relative to a restricted family of admissible tests, a hypothesis class, an intended structural equivalence, and a cost model.

We formalize a **structural identification instance** by a universe of candidate models, an equivalence relation (typically isomorphism), a hypothesis class, a family of admissible invariant truth-valued queries, and optionally a query cost. Evidence induces a structural version space. A target is identified when every surviving candidate is equivalent to it. We prove monotonicity under evidence and hypothesis refinement; an observational-equivalence impossibility theorem; invariance of version spaces under representation changes; an exact hitting-set characterization of finite identification; and a **conjunction-collapse theorem** showing why raw sentence count is degenerate whenever conjunction is free. In finite instances, minimum-cost structural identification is weighted set cover on the non-equivalent competitors and therefore contains Set Cover as a special case.

The framework is deliberately positioned between model theory and teaching complexity rather than against them. Scott sentences show that sufficiently expressive infinitary languages can characterize countable structures by a single sentence, while teaching dimension already studies minimum specifying sets in a version space. The present framework makes the bridge explicit: after quotienting by structural equivalence and restricting to invariant tests, structural identification is a teaching/specification problem on the induced truth signatures. The mathematical value is therefore not a new replacement for those theories, but a compact abstraction that makes representational invariance and query cost load-bearing. The central results are formalized and checked in Lean 4.

**Keywords:** structural identification, version space, isomorphism, categoricity, Scott sentence, teaching dimension, specifying set, hitting set, set cover, Lean 4

---

## 1. The problem

Let \(\mathcal A\) be a mathematical structure. We observe that it satisfies some collection of statements:

\[
\varphi_1(\mathcal A),\ldots,\varphi_k(\mathcal A).
\]

The basic question is not whether those statements are true. It is:

\[
\boxed{\text{Which other structures could satisfy exactly the evidence we have chosen to reveal?}}
\]

If all surviving alternatives are isomorphic to \(\mathcal A\), the evidence identifies its structure. If a non-isomorphic alternative survives, it does not.

This question is classical in several neighboring forms. Model theory studies theories, elementary equivalence, categoricity, Scott sentences, and logical resources needed to characterize structures. Computational learning theory studies version spaces, teaching sets, specifying sets, and teaching dimension. Finite model theory studies formulas that distinguish structures, including their quantifier complexity. The present note starts from those connections rather than claiming a new foundational problem.

The motivating distinction is instead methodological:

\[
\text{truth of the observations}
\quad\neq\quad
\text{identification of the generating structure}.
\]

A collection of true statements may leave many non-isomorphic models compatible. Conversely, a sufficiently discriminating statement may isolate one isomorphism type immediately. The relevant complexity is therefore not a property of the target alone. It depends on what competitors are admitted, what tests are allowed, what counts as the same structure, and what each test costs.

---

## 2. Why the naive minimum-number-of-truths definition collapses

A tempting definition is

\[
\tau(\mathcal A)
=
\min\{|E|:E\subseteq \operatorname{Th}(\mathcal A),\ E\text{ identifies }\mathcal A\}.
\]

Without restrictions on the language, this is usually useless.

Suppose

\[
E=\{\varphi_1,\ldots,\varphi_n\}
\]

is finite and identifying. If the language permits finite conjunction, define

\[
\psi
=
\varphi_1\land\cdots\land\varphi_n.
\]

Then for every candidate \(\mathcal B\),

\[
\mathcal B\models\psi
\iff
\forall i\;\mathcal B\models\varphi_i.
\]

Hence \(\{\psi\}\) has exactly the same version space as \(E\).

### Theorem 1 — Conjunction Collapse

If the admissible query family is closed under finite conjunction and query cost is the constant unit cost, every finite identifying certificate can be replaced by an identifying certificate of size one.

Therefore the unqualified cardinality invariant degenerates to essentially three values:

\[
0,\quad 1,\quad \infty,
\]

where \(0\) occurs when the hypothesis class already contains only the target isomorphism type, \(1\) occurs whenever a nontrivial finite certificate exists, and \(\infty\) occurs when no finite certificate exists.

This is not merely a technical nuisance. Scott's isomorphism theorem makes the same point from the opposite direction. Every countable structure in a countable language has a single \(L_{\omega_1\omega}\) Scott sentence characterizing its countable isomorphism type. The interesting object is therefore not raw sentence count but the **logical or descriptive complexity of the sentence**. Scott rank and Scott complexity are built precisely around that distinction [1,2].

The lesson is load-bearing:

> A nontrivial theory of structural identification must restrict the admissible query family, charge for query complexity, or both.

The Lean theorem `one_query_if_closed_under_conjunction` machine-checks this collapse directly.

---

## 3. Structural identification instances

### 3.1 Candidate universe and equivalence

Let \(\mathcal M\) be a universe of candidate mathematical objects. Let

\[
\sim\;\subseteq\mathcal M\times\mathcal M
\]

be the intended structural equivalence. In the principal application,

\[
\mathcal A\sim\mathcal B
\quad\Longleftrightarrow\quad
\mathcal A\cong\mathcal B.
\]

The abstract development does not require the proofs below to inspect the internal definition of isomorphism. It only needs a relation specifying when two candidates count as the same answer.

Let

\[
\mathcal H\subseteq\mathcal M
\]

be a **hypothesis class**. Identification is always relative to \(\mathcal H\). A cyclic group of order four is trivial to identify inside \(\{C_4\}\), less trivial inside the finite abelian groups, and different again inside all finite groups.

### 3.2 Queries

A truth-valued query is a predicate

\[
q:\mathcal M\to\{\text{true},\text{false}\}.
\]

Let \(\mathcal Q\) denote the admissible query family.

For genuinely structural identification, queries should be invariant under \(\sim\):

\[
\mathcal A\sim\mathcal B
\Longrightarrow
\big(q(\mathcal A)\leftrightarrow q(\mathcal B)\big).
\]

Otherwise a query may distinguish two presentations of the same structure and the problem is no longer identification *up to structure*.

In model-theoretic applications, a query can be satisfaction of a sentence in a fixed logical fragment. In a finite-algebra application it can be a property such as commutativity, cardinality, exponent, existence of an element of a specified order, or satisfaction of a bounded equation schema.

### 3.3 Evidence and version spaces

Evidence is a family

\[
E\subseteq\mathcal Q
\]

of admissible truths observed to hold at the target \(\mathcal A\):

\[
\forall q\in E,\quad q(\mathcal A)=\text{true}.
\]

This positive-truth presentation loses no expressive power when the logical fragment is closed under negation: an observed false answer to \(q\) can be represented by the true statement \(\neg q\). For fragments not closed under negation, positive-only and labeled-query identification must be distinguished; that extension is discussed in Section 11.

Define the **version space**

\[
V_{\mathcal H}(E)
=
\left\{
\mathcal B\in\mathcal H:
\forall q\in E,\;q(\mathcal B)
\right\}.
\]

The target is **structurally identified** by \(E\) when

\[
\mathcal A\in\mathcal H,
\qquad
E\subseteq\operatorname{Th}(\mathcal A),
\]

and

\[
\forall \mathcal B\in V_{\mathcal H}(E),
\qquad
\mathcal B\sim\mathcal A.
\]

Equivalently, the quotient version space has one equivalence class:

\[
V_{\mathcal H}(E)/{\sim}
=
\{[\mathcal A]\}.
\]

---

## 4. Elementary laws of structural version spaces

The first results are simple but establish the direction of every later comparison.

### Proposition 2 — Evidence antitonicity

If

\[
E\subseteq F,
\]

then

\[
V_{\mathcal H}(F)
\subseteq
V_{\mathcal H}(E).
\]

Adding truths can only eliminate candidates.

Lean: `version_antitone_evidence`.

### Proposition 3 — Hypothesis-class monotonicity

If

\[
\mathcal H\subseteq\mathcal K,
\]

then

\[
V_{\mathcal H}(E)
\subseteq
V_{\mathcal K}(E).
\]

Consequently, if \(E\) identifies \(\mathcal A\) in the larger class \(\mathcal K\), it identifies \(\mathcal A\) in every subclass \(\mathcal H\subseteq\mathcal K\) that still contains \(\mathcal A\).

Lean: `version_monotone_hypotheses` and `identification_descends_to_subclass`.

### Proposition 4 — Persistence under additional sound evidence

If \(E\) identifies \(\mathcal A\) and

\[
E\subseteq F\subseteq \operatorname{Th}(\mathcal A),
\]

then \(F\) also identifies \(\mathcal A\).

Lean: `identification_persists_with_more_sound_evidence`.

### Proposition 5 — Relaxing the equivalence criterion cannot make identification harder

Suppose

\[
x\sim_1y\Longrightarrow x\sim_2y.
\]

Thus \(\sim_1\) is the finer notion of identity. Any certificate that identifies \(\mathcal A\) up to \(\sim_1\) also identifies it up to \(\sim_2\).

Lean: `identification_relaxes_equivalence`.

These elementary facts already show why an identification number without its parameters is underspecified. Enlarging \(\mathcal H\), shrinking \(\mathcal Q\), strengthening the equivalence criterion, or increasing query cost can all change the answer.

---

## 5. The observational-equivalence barrier

Define two models to be \(\mathcal Q\)-observationally equivalent when

\[
\mathcal A\equiv_{\mathcal Q}\mathcal B
\quad\Longleftrightarrow\quad
\forall q\in\mathcal Q,
\;
q(\mathcal A)\leftrightarrow q(\mathcal B).
\]

This is equivalence with respect to the available observational language, not necessarily structural equivalence.

### Theorem 6 — Observational Indistinguishability Barrier

Let \(\mathcal A,\mathcal B\in\mathcal H\). If

\[
\mathcal A\not\sim\mathcal B
\]

but

\[
\mathcal A\equiv_{\mathcal Q}\mathcal B,
\]

then no evidence

\[
E\subseteq\mathcal Q
\]

can identify \(\mathcal A\) up to \(\sim\).

### Proof

Every query available to the evidence has the same truth value on \(\mathcal A\) and \(\mathcal B\). Since every element of \(E\) is true at \(\mathcal A\), every element of \(E\) is true at \(\mathcal B\). Thus

\[
\mathcal B\in V_{\mathcal H}(E).
\]

But \(\mathcal B\not\sim\mathcal A\), contradicting identification. \(\square\)

Lean: `observational_equivalence_blocks_identification`.

This theorem is the basic identifiability limit. No choice of evidence, optimization algorithm, or learner can recover a distinction absent from the admissible query family.

A useful corollary is obtained by taking the full target theory available inside \(\mathcal Q\):

\[
E^*_{\mathcal Q}(\mathcal A)
=
\{q\in\mathcal Q:q(\mathcal A)\}.
\]

Then \(E^*_{\mathcal Q}(\mathcal A)\) identifies \(\mathcal A\) exactly when every non-equivalent competitor is separated from \(\mathcal A\) by at least one query in \(\mathcal Q\).

Lean: `full_evidence_identifies_iff_separates`.

---

## 6. Structural invariance and presentation independence

The original motivation for this programme came from arbitrary representations: the symbol or code used for an object may be changed while its relations are preserved. A structural identification theory must therefore prevent presentation-specific tests from masquerading as structural evidence.

Assume the hypothesis class is saturated under \(\sim\):

\[
\mathcal A\sim\mathcal B
\Longrightarrow
\big(\mathcal A\in\mathcal H
\leftrightarrow
\mathcal B\in\mathcal H\big),
\]

and every query in \(E\) is invariant under \(\sim\).

### Theorem 7 — Version-space invariance

If

\[
\mathcal A\sim\mathcal B,
\]

then

\[
\mathcal A\in V_{\mathcal H}(E)
\quad\Longleftrightarrow\quad
\mathcal B\in V_{\mathcal H}(E).
\]

Thus a structurally admissible version space is a union of complete equivalence classes. It cannot select one encoding, coordinate system, naming convention, or presentation of an object while rejecting an equivalent one.

Lean: `version_space_is_invariant`.

This is the formal point at which the claim “37 can play the role of \(i\)” ceases to be mysterious. If two presentations are isomorphic and all admissible truths are invariant under that isomorphism, structural evidence cannot distinguish the presentations. The mathematical content lies in the preserved structure, not in the external name assigned to one of its elements.

---

## 7. Identification as hitting set

The most useful finite characterization follows by turning every non-equivalent candidate into an obligation to be excluded.

Fix target \(\mathcal A\). Define the competitor set

\[
C_{\mathcal A}
=
\{\mathcal B\in\mathcal H:\mathcal B\not\sim\mathcal A\}.
\]

For a truth \(q\in\mathcal Q\) with \(q(\mathcal A)\), define its **exclusion set**

\[
X_q
=
\{\mathcal B\in C_{\mathcal A}:\neg q(\mathcal B)\}.
\]

If queries are structural invariants, \(X_q\) is well-defined on equivalence classes.

### Theorem 8 — Hitting-set characterization

Let \(E\subseteq\mathcal Q\) be sound at \(\mathcal A\). Then \(E\) identifies \(\mathcal A\) if and only if

\[
\forall\mathcal B\in C_{\mathcal A},
\quad
\exists q\in E:\mathcal B\in X_q.
\]

Equivalently,

\[
C_{\mathcal A}
\subseteq
\bigcup_{q\in E}X_q.
\]

### Proof

If \(E\) identifies \(\mathcal A\), no non-equivalent competitor can satisfy all truths in \(E\); hence each competitor falsifies at least one \(q\in E\). Conversely, if each non-equivalent competitor falsifies at least one \(q\in E\), every model satisfying all of \(E\) is equivalent to \(\mathcal A\). \(\square\)

Lean: `identifies_iff_hits_competitors`.

This theorem converts structural identification into a standard combinatorial optimization problem.

### Corollary 8.1 — Weighted set cover

Assign each admissible truth a nonnegative cost

\[
c:\mathcal Q\to\mathbb R_{\ge0}.
\]

For finite \(\mathcal H/{\sim}\), define

\[
\operatorname{SIC}_{\mathcal H,\mathcal Q,c}(\mathcal A)
=
\min_E
\sum_{q\in E}c(q),
\]

where the minimum ranges over finite sound identifying sets \(E\subseteq\mathcal Q\).

By Theorem 8 this is exactly weighted set cover on universe \(C_{\mathcal A}/{\sim}\) with available cover sets \(X_q\).

### Corollary 8.2 — NP-hardness in the finite truth-table model

Under the natural finite representation in which \(\mathcal H\) and the truth table of every admissible query are explicit, minimum-cost structural identification contains Set Cover as a special case.

Given a Set Cover instance with universe \(U\) and subsets \(S_1,\ldots,S_k\), construct a target \(a\), one competitor \(b_u\) for each \(u\in U\), and one query \(q_i\) for each \(S_i\), with

\[
q_i(a)=\text{true}
\]

and

\[
q_i(b_u)=\text{false}
\quad\Longleftrightarrow\quad
u\in S_i.
\]

Take structural equivalence to be equality. A selected query family identifies \(a\) exactly when the corresponding \(S_i\) cover \(U\). Therefore the optimization problem is NP-hard.

This is not proposed as a surprising new complexity result; it is an immediate but useful consequence of making the competitor-exclusion geometry explicit.

---

## 8. Cost is part of the mathematics

The conjunction-collapse theorem shows that there is no representation-independent notion of “number of truths required” without specifying what counts as one admissible truth.

A **structural identification instance** should therefore be written as

\[
\mathfrak I
=
(\mathcal M,\sim,\mathcal H,\mathcal Q,c),
\]

where \(c\) is a cost functional.

Possible choices include:

- unit cost on a **fixed primitive query vocabulary**;
- formula length;
- quantifier rank;
- alternation depth;
- circuit size;
- proof length required to establish the queried truth;
- computational cost of evaluating the query;
- weighted domain-specific tests.

The same structure can be easy under one \((\mathcal Q,c)\) and hard under another.

If \(c\) is formula size, replacing \(\varphi_1,\ldots,\varphi_n\) by their conjunction is not free. If \(\mathcal Q\) is a fixed finite primitive vocabulary, the conjunction may not itself belong to \(\mathcal Q\). Both choices block the collapse.

This is exactly analogous to the role of description complexity in Scott-sentence research and quantifier rank in finite-model distinguishability. A single formula is not a single unit of information unless its internal complexity is ignored.

---

## 9. Relation to model theory

### 9.1 Categoricity as full-fragment identification

Let \(\mathcal Q\) consist of the sentences of a logical fragment \(L\), interpreted on a class \(\mathcal H\) of \(L\)-structures. Then

\[
\mathcal A\equiv_{\mathcal Q}\mathcal B
\]

is simply equivalence with respect to that fragment.

The full \(L\)-theory of \(\mathcal A\) identifies \(\mathcal A\) inside \(\mathcal H\) exactly when no non-isomorphic member of \(\mathcal H\) is \(L\)-equivalent to \(\mathcal A\). In the appropriate model-theoretic setting this is a relative categoricity statement.

The observational-equivalence barrier is therefore not a competitor to categoricity. It is its query-family formulation.

### 9.2 Scott sentences

Scott's isomorphism theorem states that every countable structure in a countable language has an \(L_{\omega_1\omega}\) sentence whose countable models are exactly its isomorphic copies [1]. Modern work studies the least logical complexity at which such descriptions are possible [1,2]. A 2026 result by Knight, Lange, and McCoy continues this line for computable \(\Pi_2\) Scott sentences [2].

For the present framework, Scott sentences are an important boundary condition:

- with a sufficiently expressive query language, one query may identify the target;
- therefore query *count* alone is not meaningful;
- logical complexity, admissible fragments, and evaluation cost are the substantive parameters.

### 9.3 Distinguishing formulas

Rocha, Martins, and Ferreira study first-order sentences of minimal quantifier rank that distinguish sets of relational structures, using Ehrenfeucht–Fraïssé methods for specific classes [3]. This is close prior art to any claim that “minimum logical information distinguishing structures” is new.

The present note is more abstract and correspondingly more modest: it does not solve minimum-rank problems for a new structure class. Instead it isolates the generic version-space and set-cover layer that appears before one chooses a specific logical fragment and structure family.

---

## 10. Relation to teaching dimension and specifying sets

Goldman and Kearns define teaching dimension through the minimum number of examples a helpful teacher must reveal to uniquely identify a target concept within a concept class [4]. Later work develops recursive teaching dimension, preference-based teaching, specifying sets, and algebraic characterizations of teaching complexity [5,6].

The structural framework reduces directly to this setting.

Assume every \(q\in\mathcal Q\) is invariant under \(\sim\). Associate to each structural equivalence class \([\mathcal A]\) its truth signature

\[
s_{[\mathcal A]}:\mathcal Q\to\{0,1\},
\qquad
s_{[\mathcal A]}(q)=1
\iff
q(\mathcal A).
\]

Invariance makes this well-defined. Let

\[
\mathcal C_{\mathcal H,\mathcal Q}
=
\{s_{[\mathcal B]}:\mathcal B\in\mathcal H\}
\]

be the induced concept class.

Then selecting admissible tests whose observed values isolate \([\mathcal A]\) is exactly selecting a specifying/teaching set for the concept \(s_{[\mathcal A]}\). With the positive-truth convention used in the Lean core, one obtains the positive-evidence specialization; with labeled query outcomes one recovers the standard teaching-set formulation.

Thus the proposed structural identification cost is not presented as an unrelated new combinatorial dimension. It is a **structural quotient specialization of teaching/specification complexity**, with two explicit additions that matter for the motivating problem:

1. candidate presentations are quotient by an independently declared structural equivalence, usually isomorphism;
2. admissible queries must respect that equivalence, or the test is presentation-sensitive rather than structural.

This bridge is useful because it imports a mature body of lower bounds, teaching-plan concepts, and complexity results while preserving the mathematical distinction between a structure and one encoding of it.

---

## 11. Extensions

The core formalization is intentionally minimal. Several extensions are mathematically natural.

### 11.1 Labeled query outcomes

Instead of truth-only evidence, let

\[
q:\mathcal M\to Y
\]

for an arbitrary outcome set \(Y\), and observe pairs

\[
(q,q(\mathcal A)).
\]

Then

\[
V_{\mathcal H}(E)
=
\{\mathcal B\in\mathcal H:
q(\mathcal B)=q(\mathcal A)\text{ for every observed }q\}.
\]

This is the cleanest bridge to exact query learning and ordinary teaching dimension.

### 11.2 Adaptive identification

A protocol may choose the next query as a function of previous answers. The observational-equivalence barrier survives unchanged: two candidates that agree on every query in \(\mathcal Q\) produce the same transcript under any deterministic adaptive protocol using only \(\mathcal Q\). The interesting complexity measure then becomes decision-tree depth or expected query cost rather than static certificate size.

### 11.3 Approximate identification

For noisy observations or empirical models, exact satisfaction can be replaced by a discrepancy or likelihood. A structural version space becomes a confidence region over equivalence classes. The exact theory developed here should be viewed as the zero-noise boundary case.

### 11.4 Infinite hypothesis classes

For infinite \(\mathcal H/{\sim}\), raw cardinality of the version space may be uninformative. Candidate replacements include logical rank, measure/posterior mass, descriptive-set complexity, or resource-bounded distinguishability. The present results about monotonicity, invariance, and observational indistinguishability do not depend on finiteness.

---

## 12. Worked finite example: how much does “\(i\)-like” behavior identify?

Consider the hypothesis class

\[
\mathcal H=\{C_4,V_4,C_8,D_4\},
\]

where \(C_n\) denotes the cyclic group of order \(n\), \(V_4\) the Klein four-group, and \(D_4\) the dihedral group of order eight.

Take equality of these named isomorphism types as the structural relation in the finite classification table. Consider three admissible truths:

\[
q_1(G):\text{ “}G\text{ has an element of order }4\text{”},
\]

\[
q_2(G):\text{ “}G\text{ is commutative”},
\]

and

\[
q_3(G):\text{ “}|G|=4\text{”}.
\]

For target \(C_4\):

\[
V_{\mathcal H}(\{q_1\})
=
\{C_4,C_8,D_4\}.
\]

So one highly characteristic fact about a generator does not identify the ambient group.

Adding commutativity yields

\[
V_{\mathcal H}(\{q_1,q_2\})
=
\{C_4,C_8\}.
\]

Adding carrier size yields

\[
V_{\mathcal H}(\{q_1,q_2,q_3\})
=
\{C_4\}.
\]

The point is not that these group facts are deep. It is that the example separates three questions that are often conflated:

1. is a statement true of the target? — yes;
2. does it exclude some alternatives? — perhaps;
3. does the available evidence isolate the structure? — only relative to \(\mathcal H\) and \(\mathcal Q\).

The Lean file proves the corresponding finite claims and the final theorem `three_truths_identify_c4`.

---

## 13. Lean 4 formalization

The machine-checked core lives at:

```text
formalizations/structural_identification/StructuralIdentification.lean
```

The file deliberately uses no algebra or model-theory library. The abstract theorems require only predicates, functions, propositions, and lists, which keeps the trusted surface small. The concrete four-group example treats the groups as already-classified isomorphism types; it verifies the discrimination logic rather than reproving group theory.

The central definitions correspond directly to the mathematics:

```lean
def VersionSpace
    (H : Family Model) (E : Family (Query Model)) : Family Model :=
  fun m => H m ∧ ∀ q, E q → q m

def Identifies
    (r : Model → Model → Prop)
    (H : Family Model)
    (a : Model)
    (E : Family (Query Model)) : Prop :=
  H a ∧ SoundAt a E ∧ ∀ m, VersionSpace H E m → r m a
```

The checked theorem surface includes:

| Mathematical result | Lean theorem |
|---|---|
| evidence antitonicity | `version_antitone_evidence` |
| hypothesis monotonicity | `version_monotone_hypotheses` |
| descent to a smaller hypothesis class | `identification_descends_to_subclass` |
| persistence under more sound evidence | `identification_persists_with_more_sound_evidence` |
| relaxation of equivalence | `identification_relaxes_equivalence` |
| hitting-set characterization | `identifies_iff_hits_competitors` |
| full-query separation criterion | `full_evidence_identifies_iff_separates` |
| observational-equivalence barrier | `observational_equivalence_blocks_identification` |
| structural invariance of version spaces | `version_space_is_invariant` |
| conjunction collapse | `conjunction_collapse` |
| one-query collapse under conjunction closure | `one_query_if_closed_under_conjunction` |
| finite \(C_4\) example | `three_truths_identify_c4` |

The file ends with `#print axioms` for the load-bearing theorems. The CI workflow compiles the file with Lean 4 and therefore treats proof checking, rather than prose, as the gate for the formal claims.

---

## 14. What this framework does and does not contribute

### 14.1 What is not claimed

This paper does **not** claim novelty for:

- the idea that structures are identified up to isomorphism;
- categoricity;
- Scott sentences or Scott complexity;
- first-order distinguishability and quantifier-rank minimization;
- version spaces;
- teaching sets, specifying sets, or teaching dimension;
- hitting set or set cover;
- the fact that conjunction combines finitely many formulas.

Any paper making those broad claims would collide immediately with established mathematics.

### 14.2 The narrower contribution

The proposed contribution is the joint parameterization

\[
(\mathcal M,\sim,\mathcal H,\mathcal Q,c)
\]

and the resulting separation of four questions:

1. **truth** — does \(q\) hold at the target?
2. **discrimination** — which non-equivalent competitors does \(q\) exclude?
3. **identifiability** — does \(\mathcal Q\) separate the target from every competitor?
4. **cost** — what is the cheapest admissible separating family under \(c\)?

The framework's main conceptual correction is negative: one cannot define a useful “minimum number of truths needed to identify a structure” without controlling the grammar or cost of those truths. The conjunction-collapse theorem makes that failure explicit, while Scott complexity and teaching dimension show the two mature traditions into which a corrected definition naturally fits.

The Lean formalization serves two purposes. First, it prevents hidden changes of quantifier direction or monotonicity from entering the prose. Second, it makes the paper's modest claim auditable: the generic structural laws are exactly the theorems that compile, no more.

---

## 15. Open mathematical directions

A stronger follow-up should move from the generic framework to nontrivial bounds for concrete classes. Promising targets include:

1. **Finite groups under restricted query vocabularies.** For a frozen family of invariant group properties or bounded first-order formulas, determine upper and lower bounds on structural identification cost.

2. **Quantifier-rank/cost tradeoffs.** Characterize when many low-rank queries are cheaper than one high-rank characteristic sentence.

3. **Automorphism-sensitive query design.** Relate the cheapest structural query families to orbit structure and definability.

4. **Adaptive versus nonadaptive identification.** Bound the gap between minimum certificate cost and optimal decision-tree cost.

5. **Robust structural identification.** Replace exact truth tables by noisy oracle answers and characterize when an isomorphism type remains identifiable.

6. **Formal bridge to Mathlib model theory.** Instantiate the abstract Lean interface with actual first-order structures and isomorphisms, then connect the general theorems to existing formalized model-theoretic notions rather than representing isomorphism as an abstract relation.

These are the points at which the programme can produce mathematics that is not merely a re-expression of teaching dimension or Scott complexity.

---

## 16. Conclusion

The statement “a set of truths identifies a mathematical object” is incomplete until four choices are fixed: the competing structures, the equivalence relation, the admissible language, and the cost of asking or expressing a truth.

Once those choices are explicit, the theory is simple:

\[
\text{evidence}
\longrightarrow
\text{version space}
\longrightarrow
\text{equivalence classes that survive}.
\]

Identification occurs when one structural class remains. A query family that cannot distinguish a non-isomorphic competitor cannot identify the target. Invariant queries preserve presentation independence. In finite settings, choosing a minimum-cost identifying family is exactly a set-cover problem over structural competitors. And if conjunction is free, naive sentence count collapses to one, showing why logical complexity rather than formula count must carry the burden.

The framework therefore turns the informal question

> How many truths do we need before we know what mathematical structure we are looking at?

into the parameterized question

\[
\boxed{
\text{What is the cheapest invariant evidence that isolates }[\mathcal A]
\text{ inside }\mathcal H
\text{ using queries from }\mathcal Q?
}
\]

That formulation is not a replacement for model theory or teaching complexity. It is a common structural interface between them, with its core claims machine-checked in Lean 4.

---

## References

[1] Matthew Harrison-Trainor. “An Introduction to the Scott Complexity of Countable Structures and a Survey of Recent Results.” *Bulletin of Symbolic Logic* 28(1), 71–103, 2022. DOI: 10.1017/bsl.2021.62.

[2] Julia Knight, Karen Lange, and Charles McCoy. “Computable Π₂ Scott Sentences.” *Journal of Symbolic Logic*, published online 6 February 2026. The paper develops current results in the Scott-sentence programme and recalls Scott's theorem that every countable structure in a countable language has an \(L_{\omega_1\omega}\) sentence characterizing its countable isomorphism type.

[3] Thiago Alves Rocha, Ana Teresa C. Martins, and Francicleber Martins Ferreira. “On Distinguishing Sets of Structures by First-Order Sentences of Minimal Quantifier Rank.” *Electronic Notes in Theoretical Computer Science* 344, 189–208, 2019. DOI: 10.1016/j.entcs.2019.07.012.

[4] Sally A. Goldman and Michael J. Kearns. “On the Complexity of Teaching.” *Journal of Computer and System Sciences* 50(1), 20–31, 1995. DOI: 10.1006/jcss.1995.1003.

[5] Rahim Samei, Pavel Semukhin, Boting Yang, and Sandra Zilles. “Algebraic Methods Proving Sauer's Bound for Teaching Complexity.” *Theoretical Computer Science* 558, 35–50, 2014. DOI: 10.1016/j.tcs.2014.09.024.

[6] Ziyuan Gao, Christoph Ries, Hans U. Simon, and Sandra Zilles. “Preference-Based Teaching.” *Journal of Machine Learning Research* 18, 1–32, 2017.
