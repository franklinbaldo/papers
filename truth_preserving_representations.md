---
type: "Technical Paper"
title: "When 37 Can Be i: Truth-Preserving Representations and Structural Identifiability"
description: "Position paper separating classical transport of structure from the nontrivial problem of identifying latent algebraic structure from sparse truths under arbitrary representations."
tags: [structural-identifiability, universal-algebra, representation-learning, invariance, machine-teaching]
timestamp: 2026-08-24T01:30:00Z
---

# When 37 Can Be $i$: Truth-Preserving Representations and Structural Identifiability

**Franklin Baldo**  
Independent Researcher  
franklinbaldo@gmail.com

---

> **Position paper and experimental programme.** The classical mathematics of transport of structure, homomorphisms, quotient algebras, algebraic theories, categoricity, and teaching dimension is prior art. This paper does **not** claim that assigning arbitrary codes to mathematical objects, transporting operations through a bijection, or identifying models up to isomorphism is new. Its narrower proposal is to make **structural ambiguity under sparse truth constraints** an explicit experimental object: given an arbitrary representation and only part of the relations that are true in a target structure, measure the remaining version space of non-isomorphic structures, distinguish predictive success from structural identification, and test which evidence collapses that ambiguity.

## Abstract

A symbol need not resemble the mathematical object it denotes. The real number `37` can be used as the code for the imaginary unit $i$ without contradiction if the relevant operations are transported with the code. In the fully specified bijective case this observation is mathematically unremarkable: it is an isomorphic copy of the original structure. The interesting problem begins when the representation is arbitrary but the available truths are **partial**.

This paper asks: given a class of candidate algebraic structures, an observation language, and a finite set of truths expressed through an arbitrary code, when is the latent structure determined up to isomorphism? We define a structural version space as the set of candidate models satisfying the observations, quotiented by isomorphism. Structural identification occurs when only one isomorphism class remains. The size of this quotient version space measures residual structural ambiguity. A minimal identifying truth set is then a teaching-set-like object relative to a fixed hypothesis class and observation language; we do not claim this measure as a new invariant.

The framing separates three regimes that are often conflated. **Full transport** is representational relabeling and preserves all structure by construction. **Sparse truth preservation** generally underdetermines the ambient structure. **Restricted structural identification** becomes possible only relative to a sufficiently constrained hypothesis class, signature, logic, and observation budget. A toy finite-group apparatus makes the distinction concrete. The local existence of an element with the multiplicative behavior of $i$ is compatible with $C_4$, $C_8$, and $D_4$; adding commutativity still leaves $C_4$ and $C_8$; constraining the carrier to four elements leaves only $C_4$. A second toy construction shows that a non-injective decoder can preserve every decoded multiplication while admitting many inequivalent latent multiplication tables.

The proposed benchmark exposes randomly relabeled finite algebraic structures through progressively revealed truths. Systems are evaluated not only on held-out operation prediction but on recovery of the target isomorphism class, calibration to the exact structural version space, robustness to relabeling, and the rate at which selected evidence collapses ambiguity. This creates a clean empirical separation between **using relations well enough to answer** and **having enough information to identify the relational world that generated them**.

**Keywords:** structural identifiability, invariance, universal algebra, model theory, arbitrary representation, teaching dimension, in-context algebra, latent structure

---

## 1. The question behind “what if 37 were $i$?”

The ordinary imaginary unit satisfies

$$
i^2=-1.
$$

If `37` is interpreted as the ordinary real number thirty-seven while ordinary real multiplication is retained, declaring $37=i$ is inconsistent with that equation. But this is only one possible reading of the proposal. A different reading treats `37` as a **representative** or **code** for an object and asks that calculations be interpreted through a map.

Let $A$ be a mathematical structure containing $i$. Let $X$ be a set of arbitrary codes, and let

$$
f:X\to A
$$

interpret a code as an element of the target structure. We may choose some $x_i\in X$ with

$$
f(x_i)=i.
$$

Nothing requires $x_i$ to resemble $i$. It could be the token `37`, a vector, a byte string, or an otherwise meaningless identifier.

This observation motivates two very different questions:

1. **Representation question.** Can arbitrary objects serve as representatives of a mathematical structure while preserving its truths?
2. **Identification question.** If only some truths are observed through those arbitrary representatives, what structure is forced by them?

The first question is classical and easy under a bijection. The second is where uncertainty enters.

The position of this paper is therefore deliberately deflationary:

> The arbitrary value assigned to a symbol is not the research object. The research object is the residual family of non-isomorphic structures compatible with the truths that survive the representation.

---

## 2. Full transport is not a new mathematics

### 2.1 Transporting the operations

Let

$$
\mathcal A=(A,(\sigma^{\mathcal A})_{\sigma\in\Sigma})
$$

be a $\Sigma$-algebra, where each operation symbol $\sigma$ has arity $n_\sigma$. Let $X$ be any set with $|X|=|A|$, and let

$$
f:X\overset{\sim}{\longrightarrow}A
$$

be a bijection.

Define each operation on $X$ by transport:

$$
\sigma^{\mathcal X}(x_1,\ldots,x_n)
=
f^{-1}\!\left(
\sigma^{\mathcal A}(f(x_1),\ldots,f(x_n))
\right).
$$

Then

$$
f:\mathcal X\to\mathcal A
$$

is an isomorphism by construction.

For multiplication, this is simply

$$
x\otimes_X y
=
f^{-1}(f(x)\cdot_A f(y)).
$$

If $x_i=37$ and $f(37)=i$, then

$$
f(37\otimes_X37)=i^2=-1.
$$

The operation $\otimes_X$ need not resemble ordinary multiplication of the labels. `37` is not being asserted to be the real number $37$ *inside the target algebra*. It is a name in an isomorphic presentation.

### Proposition 1 — truth is preserved under full transport

For every first-order formula $\varphi$ in the signature $\Sigma$ and every assignment $s$ into $X$,

$$
\mathcal X\models\varphi[s]
\quad\Longleftrightarrow\quad
\mathcal A\models\varphi[f\circ s].
$$

This is the ordinary invariance of first-order truth under isomorphism. It is the correct formal answer to the unrestricted version of “make the operations adjust so the old truths remain true.”

### 2.2 Why the fully transported case is scientifically empty

If every operation is obtained by the equation above and $f$ is bijective, then no empirical or mathematical distinction has been created. We changed coordinates or names, not structure.

This is a useful negative result for the present programme. It blocks a tempting but false novelty claim:

$$
\boxed{\text{arbitrary labels + exact transported operations} \neq \text{new algebraic structure}.}
$$

The classical foundations include universal algebra, free and quotient algebras, equational classes, algebraic theories, homomorphisms, and functorial semantics [1,2]. Philosophically, the same distinction between the internal identity of representatives and their structural role is central to structuralist discussions following Benacerraf [3].

---

## 3. Partial truths change the problem

Suppose now that the observer does **not** receive the whole algebra. It sees only a finite set of facts.

Let:

- $\Sigma$ be a signature;
- $\mathcal H$ be a declared hypothesis class of $\Sigma$-structures;
- $\mathcal O$ be the admissible observation language;
- $\mathcal A\in\mathcal H$ be the latent target;
- $E\subseteq\mathcal O$ be a finite evidence set such that $\mathcal A\models E$.

Define the **version space**

$$
V_{\mathcal H}(E)
=
\{\mathcal B\in\mathcal H:\mathcal B\models E\}.
$$

If object names are arbitrary, labeled models should not be counted as distinct merely because their carrier elements were permuted. We therefore quotient by isomorphism:

$$
\overline V_{\mathcal H}(E)
=
V_{\mathcal H}(E)/\cong.
$$

### Definition 1 — structural identifiability from evidence

The target $\mathcal A$ is **structurally identifiable from $E$ relative to $(\mathcal H,\mathcal O)$** when

$$
\overline V_{\mathcal H}(E)=\{[\mathcal A]\}.
$$

The qualification is load-bearing. There is no context-free notion of “the truths identify the structure.” The answer depends on what models were allowed, which predicates or equations could be observed, the background axioms, and sometimes the allowed cardinalities.

### Definition 2 — structural ambiguity

For finite $\overline V_{\mathcal H}(E)$, define

$$
A_{\mathrm{struct}}(E;\mathcal H)
=
\log |\overline V_{\mathcal H}(E)|.
$$

The logarithm is optional; the important object is the quotient version-space cardinality. For weighted hypothesis classes one may instead use entropy over isomorphism classes.

### Definition 3 — minimal identifying truth set

For a finite admissible observation family,

$$
\tau(\mathcal A;\mathcal H,\mathcal O)
=
\min_{E\subseteq\mathcal O(\mathcal A)}
\left\{|E|:
\overline V_{\mathcal H}(E)=\{[\mathcal A]\}
\right\}.
$$

This is deliberately presented as a **teaching-set-like** quantity. Teaching dimension already studies the number of instances a helpful teacher must reveal to uniquely identify a target from a concept class [4]. The proposal here is not to rename that literature, but to use its perspective in an isomorphism-aware algebraic benchmark where prediction and model-class collapse can be scored separately.

---

## 4. The $i$ example: local behavior does not identify the ambient world

The multiplicative orbit

$$
1,\ i,\ -1,\ -i
$$

forms a cyclic group of order four. If all we know is that a latent structure has an identity $e$ and contains an element $x$ satisfying

$$
x^4=e,
\qquad
x^2\neq e,
$$

then we know that $x$ has order four. We have **not** thereby identified the ambient structure.

Consider the finite hypothesis class

$$
\mathcal H=\{C_4,V_4,C_8,D_4\},
$$

where $D_4$ denotes the dihedral group of order eight.

The evidence “there exists an element of order four” leaves

$$
\overline V(E)=\{C_4,C_8,D_4\}.
$$

Adding commutativity removes $D_4$ but leaves

$$
\{C_4,C_8\}.
$$

Adding the background fact that the carrier has four elements leaves only

$$
\{C_4\}.
$$

The same local truth changes from underdetermining to identifying when the hypothesis class changes.

### 4.1 Why $x^2+1=0$ can nevertheless characterize the complex extension

There is no contradiction with the familiar construction

$$
\mathbb C\cong\mathbb R[x]/(x^2+1).
$$

Here the background specification is much stronger. We are not asking which arbitrary mathematical universe contains some square root of $-1$. We fix $\mathbb R$, work in a particular algebraic category, adjoin a generator, and quotient by the relation $x^2+1=0$. The construction is governed by a universal property.

Thus the amount of explicit evidence can be tiny precisely because the **background theory has already supplied most of the structure**.

This gives a useful bookkeeping principle:

$$
\text{identifying power}
=
\text{observed truths}
+
\text{background restrictions}.
$$

Counting only the observed equations can therefore badly misstate how much information was needed.

---

## 5. Non-injective representations expose a second ambiguity

A bijection permits exact transport. A many-to-one interpretation map creates a different problem.

Let

$$
f:X\twoheadrightarrow A
$$

be surjective but not injective. Suppose we demand only that an internal binary operation $\star$ be semantically compatible:

$$
f(x\star y)=f(x)\cdot_A f(y).
$$

The right-hand side identifies the **fiber** in which $x\star y$ must land, but may not identify a unique representative in that fiber. Therefore many latent operations can induce the same decoded operation.

### Toy example

Let the decoded algebra be $C_2=\{0,1\}$ under addition mod 2. Let

$$
X=\{a,b,c\},
$$

with

$$
f(a)=f(b)=0,
\qquad
f(c)=1.
$$

Enumerating every binary table on $X$ that satisfies

$$
f(x\star y)=f(x)+f(y)\pmod 2
$$

produces:

- 32 labeled compatible multiplication tables;
- 16 isomorphism classes of magmas;
- after requiring associativity, 4 labeled tables and 2 semigroup isomorphism classes;
- after additionally requiring a two-sided identity, 2 labeled tables forming 1 monoid isomorphism class.

The decoded truths alone therefore fail to determine the latent mechanism. Extra axioms progressively collapse the fiber-level ambiguity.

This phenomenon matters outside pure algebra. A decoder can make two internal implementations behaviorally indistinguishable on the observed interface even when their latent transition structures differ substantially.

---

## 6. What is already known

The proposal sits at the intersection of mature literatures and must keep their boundaries explicit.

### 6.1 Universal algebra and algebraic specification

Birkhoff's work on abstract algebras and equational classes established the classical setting in which structures are characterized by operations and identities [1]. Lawvere's functorial semantics of algebraic theories supplied a categorical formulation that unifies free constructions and semantics [2]. Generators, relations, free objects, quotient constructions, and homomorphisms already formalize much of the motivating intuition.

**Boundary:** the paper does not claim that a structure can be defined through relations, that arbitrary representatives can instantiate it, or that transported operations preserve equations.

### 6.2 Model theory and categoricity

A theory is categorical when its models are unique up to isomorphism. First-order model theory also imposes a strong warning on unrestricted identification: an infinite first-order theory with an infinite model cannot be categorical in all infinite cardinalities because of Löwenheim–Skolem phenomena [5].

**Boundary:** any infinite-structure extension of this programme must state the logic, cardinality regime, background category, or other restrictions under which identification is being claimed.

### 6.3 Mathematical structuralism

Benacerraf's classic argument emphasized that familiar mathematical structure can have multiple set-theoretic realizations without any one realization obviously constituting the intrinsic identity of the numbers [3]. Structuralist responses make invariance under structure-preserving maps central.

**Boundary:** “relations matter more than the arbitrary identity of the representatives” is philosophical prior art, not a new thesis here.

### 6.4 Teaching dimension

Goldman and Kearns formalized teaching dimension as the number of instances a helpful teacher must provide to identify a target concept from a concept class [4]. Many later variants refine this idea.

**Boundary:** $\tau$ above should be read as an isomorphism-aware specialization or benchmark device, not as a claim to have invented minimal identifying evidence.

### 6.5 Identifiability in learned representations

Roeder, Metz, and Kingma showed that learned representations can be identifiable only up to a linear indeterminacy under suitable conditions [6]. Nelson et al. distinguish statistical identifiability from structural identifiability and explicitly study near-identifiability of learned representations relative to latent ground truth [7].

**Boundary:** the present object is not parameter identifiability or latent-coordinate recovery per se. It is the quotient space of **candidate relational structures** that remain compatible with finite truth evidence.

### 6.6 In-context algebra with arbitrary symbol meanings

Todd et al.'s *In-Context Algebra* is the closest empirical collision [8]. Their task randomly changes the one-to-one assignment between tokens and group elements across sequences, forcing transformers to use relational facts rather than fixed token semantics. Models achieve strong operation prediction and the paper studies mechanisms such as identity recognition, copying, and closure-based cancellation.

This establishes that **arbitrary symbol-to-element assignment plus group-relation inference is already an active benchmark**.

The proposed distinction is narrower. A system can predict a held-out product correctly while several non-isomorphic structures remain compatible with the observed facts. Therefore held-out operation accuracy and structural identification are not the same endpoint. The proposed benchmark makes the latter explicit by computing an exact version space whenever feasible.

### 6.7 Orbit recovery from invariants

Invariant theory studies when invariant observations separate group orbits. Edidin and Katz, for example, show generic orbit recovery from low-degree invariants in finite-group representations under specified conditions [9].

**Boundary:** this is a neighboring mathematical formulation of recovery up to symmetry. The current programme is broader in the kind of finite relational evidence allowed, but should use orbit-recovery results as a warning against broad novelty claims about “recovering hidden objects from invariants.”

---

## 7. Proposed benchmark: Sparse Truth Structural Identification

The first empirical programme should use finite structures so the ground-truth version space can be computed exactly.

### 7.1 Data generation

For each target structure $\mathcal A$:

1. sample $\mathcal A$ from a frozen finite hypothesis class $\mathcal H$;
2. draw a fresh random bijection from its carrier to opaque tokens;
3. generate a pool $\mathcal O(\mathcal A)$ of admissible truths, initially multiplication facts of the form
   $$a\star b=c;$$
4. reveal a prefix or selected subset $E_k$ of $k$ facts;
5. reserve unseen operation facts for ordinary predictive evaluation;
6. compute the exact structural version space $\overline V_{\mathcal H}(E_k)$.

The primary finite-group track should include multiple non-isomorphic groups of the same order wherever possible so cardinality alone cannot solve the task.

### 7.2 Three tasks, not one

**Task P — operation prediction.** Predict held-out products under the current arbitrary labeling.

**Task S — structural identification.** Predict the target isomorphism class or a calibrated distribution over the surviving isomorphism classes.

**Task R — reconstruction.** Produce a complete operation table whose structure is isomorphic to the target, with evaluation invariant to carrier relabeling.

A central empirical question is whether Task P can saturate while Task S remains genuinely ambiguous.

### 7.3 Evidence policies

Compare at least:

- uniformly random revealed facts;
- entropy-greedy facts chosen to maximally reduce the exact version space;
- a helpful teacher approximating a minimum identifying set;
- adversarially redundant facts that maximize prediction signal while minimizing structural discrimination.

The comparison links the benchmark to teaching-dimension intuitions without presuming that minimum teaching sets are computationally easy.

### 7.4 Baselines

The benchmark should include:

1. an exact enumerative/model-finding solver over the frozen finite class;
2. a constraint or graph-isomorphism-aware solver;
3. an *In-Context Algebra*-style transformer trained only for held-out product prediction;
4. the same model with an auxiliary structural-class objective;
5. a label-memorization control that should fail under per-episode random relabeling.

The exact solver is not merely a ceiling. It defines the **Bayes-relevant ambiguity supplied by the data**: a learned system must not be penalized for failing to select one structure when the evidence has not selected one.

---

## 8. Metrics

### 8.1 Held-out product accuracy

Standard accuracy on unseen operation facts. This measures competence at using the available relations but does not imply identification.

### 8.2 Structural exact recovery

Success if the predicted complete structure is isomorphic to the target.

### 8.3 Version-space size

For each evidence budget $k$:

$$
N_k=|\overline V_{\mathcal H}(E_k)|.
$$

Plotting $N_k$ or $\log N_k$ gives an ambiguity-collapse curve.

### 8.4 Calibration to structural ambiguity

If a model emits probabilities over candidate classes, compare them with the exact posterior induced by a declared prior and the constraint set. A model that becomes certain before the evidence identifies a class is structurally overconfident even if its product predictions are accurate.

### 8.5 Relabeling robustness

Evaluate every target under multiple fresh carrier permutations. A structural score should be invariant to these renamings.

### 8.6 Evidence efficiency

Measure the number of revealed truths required to reach

$$
N_k=1.
$$

Compare random, greedy, learned-teacher, and adversarial evidence policies.

---

## 9. Hypotheses and falsification

### H1 — relabeling invariance

A learner that has acquired the relevant relational structure should retain structural performance under unseen random renamings of every carrier element.

**Failure:** performance follows stable token identities or collapses to chance under fresh bijections.

### H2 — prediction and identification separate

There exist evidence regimes in which held-out product accuracy is high while

$$
|\overline V_{\mathcal H}(E)|>1.
$$

**Failure:** after controlling task design and hypothesis class, product prediction and structural version-space collapse are empirically indistinguishable at all useful budgets. In that case the extra structural endpoint adds little.

### H3 — evidence selection can collapse structure faster than random facts

A teacher or information-greedy selector should reduce

$$
\log|\overline V|
$$

with fewer observations than a matched random policy.

**Failure:** after exact optimization on small instances and matched budgets, selected evidence provides no reliable advantage.

### H4 — semantic equivalence can hide latent structural multiplicity

Under a non-injective decoder, multiple non-isomorphic latent operations can produce the same decoded operation truths.

This is already true in the toy construction. The empirical extension asks whether learned systems develop distinguishable latent implementations that remain behaviorally equivalent under a restricted observation interface.

### H5 — explicit structural supervision changes representations beyond predictive supervision

A model trained jointly for operation prediction and structural identification should encode more readily decodable isomorphism-class information than a prediction-only model at matched predictive accuracy.

**Failure:** the auxiliary structural objective changes neither structural recovery nor representation diagnostics once prediction is matched.

---

## 10. Toy results already completed

A dependency-free finite-group apparatus accompanies this paper in `experiments/truth_preserving_representations/`.

The current toy tests establish only mathematical bookkeeping, not a machine-learning result:

1. arbitrary bijective relabeling of $C_4$ preserves its complete multiplication table through transported operations;
2. the local “$i$-like” fact leaves $C_4$, $C_8$, and $D_4$ in the finite version space;
3. adding commutativity leaves $C_4$ and $C_8$;
4. adding carrier cardinality four identifies $C_4$ within the toy class;
5. a fixed non-injective decoder to $C_2$ admits 32 compatible labeled binary operations, corresponding to 16 magma isomorphism classes; associativity reduces these to 2 semigroup isomorphism classes.

These tests are intentionally small enough to enumerate exactly. They validate the definitions and expose false-positive routes before model-backed experiments are attempted.

---

## 11. Connection to the surrounding research programme

### 11.1 Structured Irregularity

`pedagogical_signal_extraction.md` argues that arbitrary identifiers can be legitimate parts of a learned language when their roles become inferable through interaction, and that two learners may use different registries while being functionally equivalent at the observable interface. The present paper sharpens one part of that claim: equivalence at an interface need not imply that the underlying structure is identified, and the missing information can be represented explicitly as a version space over non-isomorphic hypotheses.

### 11.2 Semantic Atlas

`semantic_atlas.md` already distinguishes model-specific coordinates from semantic correspondence and requires paired calibration before claiming a shared reference frame. The current proposal does **not** make that calibration unnecessary. Route planning may require shared coordinates or another explicit correspondence.

It instead suggests a complementary diagnostic: after quotienting away admissible coordinate transformations, which relational or transition structures are actually fixed by the observations? Two observers can disagree pointwise yet implement isomorphic transition structure; conversely, they can agree on a restricted decoded interface while hiding different latent structures. Coordinate alignment and structural identification answer different questions.

### 11.3 Machine teaching

A future bridge to `generative_machine_teaching.md` is natural but should be tested rather than asserted. A teacher that knows the hypothesis class can choose demonstrations for **structural discrimination**, not merely local predictive gain. The exact finite benchmark supplies a setting in which that distinction can be measured without semantic judgment.

---

## 12. Non-claims and limitations

This paper does not claim:

- that transport of structure is new;
- that mathematical objects are “nothing but relations” as an original philosophical thesis;
- that version spaces, categoricity, teaching sets, or identifiability are new concepts;
- that arbitrary encoding creates new mathematical content;
- that a finite benchmark settles identifiability in continuous neural representations;
- that an isomorphism class is always the correct equivalence class for every scientific task;
- that a learner must explicitly represent the exact version space to reason correctly;
- that structural recovery is always more useful than predictive competence;
- that first-order truths can uniquely characterize arbitrary infinite structures without cardinality or logic qualifications;
- or that the proposed benchmark is novel until a broader implementation- and citation-level audit excludes equivalent prior benchmarks under different terminology.

The strongest present contribution is therefore **problem separation and experimental instrumentation**. The project becomes scientifically useful if structural ambiguity predicts something that ordinary held-out operation accuracy does not.

---

## 13. Conclusion

The provocative statement “37 can be $i$” contains one trivial truth and one nontrivial question.

The trivial truth is that labels are arbitrary. Given a bijection, every operation can be transported so that `37` plays exactly the structural role of $i$. This is an isomorphic presentation.

The nontrivial question appears only after information is removed. If an observer sees a finite collection of truths through arbitrary symbols, what family of relational worlds remains possible? Which new truth eliminates which worlds? When does the evidence identify the target only up to a symmetry, and when does it fail even at that level?

The proposed programme makes those questions explicit through

$$
\boxed{
\text{sparse truths}
\longrightarrow
\text{version space}
\longrightarrow
\text{quotient by isomorphism}
\longrightarrow
\text{structural ambiguity}
}.
$$

That framing does not replace universal algebra, model theory, teaching dimension, or representation identifiability. It creates a common experimental object on which their distinctions can be tested against modern relational learners.

---

## References

[1] G. Birkhoff. “On the Structure of Abstract Algebras.” *Proceedings of the Cambridge Philosophical Society* 31(4):433–454, 1935. doi:10.1017/S0305004100013463.

[2] F. W. Lawvere. “Functorial Semantics of Algebraic Theories.” *Proceedings of the National Academy of Sciences* 50(5):869–872, 1963.

[3] P. Benacerraf. “What Numbers Could Not Be.” *The Philosophical Review* 74(1):47–73, 1965. doi:10.2307/2183530.

[4] S. A. Goldman and M. J. Kearns. “On the Complexity of Teaching.” *Journal of Computer and System Sciences* 50(1):20–31, 1995. doi:10.1006/jcss.1995.1003.

[5] W. Hodges. “First-order Model Theory.” *Stanford Encyclopedia of Philosophy*. Sections on categoricity and the Löwenheim–Skolem theorems; archived and revised editions.

[6] G. Roeder, L. Metz, and D. P. Kingma. “On Linear Identifiability of Learned Representations.” *Proceedings of ICML 2021*, PMLR 139:9030–9039, 2021. arXiv:2007.00810.

[7] W. Nelson, M. Fumero, T. Karaletsos, and F. Locatello. “Statistical and Structural Identifiability in Representation Learning.” *ICLR 2026*, 2026. arXiv:2603.11970.

[8] E. Todd, J. Brinkmann, R. Gandikota, and D. Bau. “In-Context Algebra.” 2025/2026. arXiv:2512.16902.

[9] D. Edidin and J. Katz. “Orbit Recovery from Invariants of Low Degree in Representations of Finite Groups.” 2025. arXiv:2503.00009.
