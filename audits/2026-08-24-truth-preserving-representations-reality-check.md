---
type: "Audit Report"
title: "Truth-Preserving Representations — Adversarial Reality Check"
description: "Prior-art and identifiability audit of the idea that arbitrary representatives can preserve mathematical truths through an interpretation function."
tags: [prior-art, structural-identifiability, universal-algebra, model-theory, in-context-algebra]
timestamp: 2026-08-24T01:32:00Z
---

# Truth-Preserving Representations — Adversarial Reality Check

## Status

External prior-art and formal reality check performed before treating the motivating idea as a research contribution.

Literature cutoff: **2026-08-24**.

This report records both collisions and the narrower formulation that survives them. Negative search evidence is bounded and is not proof of global novelty.

## 1. Starting idea

The motivating thought was:

> choose an arbitrary value or representation for a familiar mathematical object such as $i$, introduce an interpretation function $f$, and require calculations to adjust so that the truths already known about $i$ remain true.

A concrete version is to let the code `37` stand for $i$ and define the code-space operations so that all interpreted equations agree with complex arithmetic.

The audit separates two claims:

- **C0 — full transport:** an arbitrary bijective code can represent a known algebra if every operation is transported through the decoding bijection;
- **C1 — sparse recovery:** from only some preserved truths under arbitrary coding, the latent structure may be recoverable up to isomorphism.

C0 is classical. C1 is meaningful only after the hypothesis class, observation language, equivalence relation, and background axioms are fixed.

## 2. Collision ledger

### A1 — full arbitrary-code transport is ordinary isomorphism

Let $f:X\to A$ be a bijection and define

$$
\sigma_X(x_1,\ldots,x_n)
=f^{-1}(\sigma_A(f(x_1),\ldots,f(x_n))).
$$

Then $f$ is an isomorphism. First-order truth is invariant under this transport.

**Collision:** universal algebra and ordinary structural mathematics already make this exact.

**Consequence:** “37 can be $i$ if the operations adjust” is a pedagogically striking example, not a novel mathematical result.

**Primary boundary sources:** Birkhoff (1935), general abstract algebra and equational structure; Lawvere (1963), functorial semantics of algebraic theories.

### A2 — generators, relations, free objects, and quotients already formalize ‘make a relation true’

The familiar construction

$$
\mathbb C\cong\mathbb R[x]/(x^2+1)
$$

is precisely an example in which a formal generator is subjected to a relation inside a declared algebraic setting. The relation is powerful because the ambient category and base algebra are already fixed.

**Collision:** algebraic specification by equations, free algebras, and quotient constructions are established mathematics.

**Consequence:** the paper must not present “force a relation and close the consequences” as new.

### A3 — uniqueness from truths up to isomorphism is categoricity territory

Model theory calls a theory categorical when its models, under the relevant cardinality qualification, are unique up to isomorphism. First-order infinite structures also expose a hard limit: unrestricted all-cardinality categoricity is blocked by Löwenheim–Skolem phenomena.

**Collision:** “which truths uniquely determine the structure?” is not a new foundational question.

**Consequence:** every identification claim in the paper is explicitly **relative** to a hypothesis class, observation language, and often cardinality.

### A4 — minimum evidence for unique identification is teaching-dimension-like

Goldman and Kearns (1995) define teaching dimension by the number of examples a helpful teacher needs to uniquely identify a target concept in a class.

**Collision:** a proposed quantity such as

$$
\min |E| \quad \text{s.t. only the target remains}
$$

cannot be advertised as a new generic principle.

**Consequence:** the paper calls its minimal truth-set size an **isomorphism-aware teaching-set-like quantity** and uses it as a benchmark diagnostic rather than a novelty claim.

### A5 — arbitrary token meanings plus group-relation inference already has a strong modern benchmark

Todd, Brinkmann, Gandikota, and Bau's *In-Context Algebra* (arXiv:2512.16902; ICLR-era 2026 work) randomizes the one-to-one assignment of tokens to group elements on each sequence. Transformers must infer the token roles from relational/product facts rather than stable token identity, and the work studies learned reasoning mechanisms.

**Collision:** “can a neural model reason about algebra when symbols have arbitrary episode-specific meanings?” is already occupied.

**Consequence:** a model that merely predicts held-out products under random relabeling is not enough to distinguish the proposed programme.

**Surviving distinction:** compute the exact set of **non-isomorphic structures** compatible with the revealed facts and score structural identification separately from held-out product prediction.

### A6 — representation identifiability up to transformations is established research

Roeder, Metz, and Kingma (2021) study learned representations identifiable up to linear indeterminacy. Nelson et al. (2026) distinguish statistical from structural identifiability and formalize near-identifiability relative to latent ground truth.

**Collision:** “representations are only identifiable up to a symmetry/transformation” is established.

**Consequence:** the new benchmark's object must remain the quotient **model/version space of relational structures**, not generic latent-coordinate identifiability.

### A7 — recovery from invariants up to group action has its own theory

Invariant and orbit-recovery work asks when invariant observations separate hidden orbits. Edidin and Katz (2025) give low-degree invariant recovery results for finite-group representations under specified conditions.

**Collision:** broad rhetoric about “recovering a hidden object from invariant truths” would overclaim.

**Consequence:** the proposed finite truth benchmark is positioned as a synthesis/testbed, not as a replacement for invariant theory.

### A8 — the philosophical structuralist intuition is old

Benacerraf's 1965 discussion of multiple set-theoretic realizations of arithmetic is a canonical source for the distinction between the objects serving as representatives and the mathematical structure they instantiate.

**Collision:** “the identities of the representatives do not matter; the relations do” is philosophical prior art.

**Consequence:** the motivating `37 ↦ i` example is retained for intuition only.

## 3. Formal survivor

The clean surviving object is a **structural version space**.

Given a signature $\Sigma$, a declared hypothesis class $\mathcal H$, admissible observations $\mathcal O$, and finite evidence $E$,

$$
V_{\mathcal H}(E)
=\{\mathcal B\in\mathcal H:\mathcal B\models E\}.
$$

Because arbitrary labels should not multiply equivalent hypotheses, use

$$
\overline V_{\mathcal H}(E)=V_{\mathcal H}(E)/\cong.
$$

The target is structurally identified exactly when

$$
\overline V_{\mathcal H}(E)=\{[\mathcal A]\}.
$$

This formulation is not claimed as a new theorem. Its value is experimental: it supplies an exact ambiguity variable against which learned relational reasoning can be evaluated.

## 4. Completed toy checks

A dependency-free finite apparatus was implemented and run locally before manuscript formalization.

### T1 — exact transport under arbitrary codes

A cyclic group $C_4$ was relabeled with the opaque integers

$$
(37,12,83,51).
$$

Transporting the group operation through the bijection preserved every product exactly.

**Verdict:** confirms the trivial/isomorphic regime; no novelty.

### T2 — local $i$-like facts underdetermine the ambient group

Within

$$
\mathcal H=\{C_4,V_4,C_8,D_4\},
$$

the observation “there exists an element of order four” leaves

$$
\{C_4,C_8,D_4\}.
$$

Adding commutativity leaves

$$
\{C_4,C_8\}.
$$

Adding carrier order four leaves only

$$
\{C_4\}.
$$

**Verdict:** demonstrates that structural identification is evidence-plus-background, not a property of one equation alone.

### T3 — non-injective decoding can hide many latent operations

For a three-element code set mapping surjectively to $C_2$ with a duplicate code for the identity fiber, exact enumeration found:

| Constraint | Labeled compatible operations | Isomorphism classes |
| --- | ---: | ---: |
| decoded multiplication only | 32 | 16 magmas |
| + associativity | 4 | 2 semigroups |
| + two-sided identity | 2 | 1 monoid |

**Verdict:** interface-level truth preservation need not identify the latent operation.

### Test status

The local apparatus ran five unit tests:

```text
Ran 5 tests in 0.001s
OK
```

The repository branch adds the same dependency-free apparatus plus CI. This audit does not treat passing toy tests as evidence that a learned model will exhibit the proposed separation.

## 5. What would actually be worth testing

The strongest near-term benchmark is not “teach a transformer that `37` means $i$.” It is:

1. freeze a finite family of non-isomorphic algebraic structures;
2. randomly relabel every carrier on every episode;
3. reveal a controlled subset of operation truths;
4. compute the exact structural version space after each revelation;
5. evaluate held-out operation prediction and structural identification separately;
6. compare random, information-greedy, teaching-oriented, and deliberately redundant evidence policies;
7. test non-injective observation maps as a separate ambiguity regime.

This creates a potentially informative dissociation:

$$
\text{predictive competence}
\not\Rightarrow
\text{structural identification}.
$$

The programme earns its keep only if this dissociation is empirically or theoretically useful.

## 6. Novelty assessment

### Rejected as novelty

- arbitrary labels for mathematical objects;
- transported operations through a bijection;
- preservation of truths by isomorphism;
- algebra from generators and relations;
- identification up to isomorphism;
- minimum evidence as a generic teaching idea;
- arbitrary-symbol group-operation prediction;
- representation identifiability up to transformations.

### Surviving research position

> Treat the exact isomorphism-quotiented version space induced by sparse algebraic truths as an explicit dependent variable in relational-learning experiments, and use it to distinguish **answering correctly under an arbitrary code** from **having received enough information to identify the generating structure**.

This is a narrower and more defensible claim. It may still collide with a benchmark or finite-model-learning literature not found in this pass.

### Confidence

- **Mathematical novelty of the underlying definitions:** low.
- **Novelty of the synthesis/problem framing:** moderate-low.
- **Potential value of the proposed benchmark and prediction-vs-identification separation:** moderate, pending broader benchmark search and model-backed results.
- **Basis for a theorem paper today:** insufficient.
- **Basis for an explicitly scoped position paper + experimental programme:** yes.

## 7. Kill and downgrade criteria

The project should be downgraded or absorbed into a neighboring paper if any of the following occurs:

1. a prior benchmark is found that already computes an isomorphism-quotiented structural version space from sparse arbitrary-label algebra facts and explicitly separates it from operation prediction;
2. exact finite experiments show structural ambiguity is almost perfectly determined by ordinary held-out operation accuracy across all nontrivial evidence regimes;
3. evidence-selection gains reduce entirely to trivial carrier-size or group-order cues;
4. learned-model results disappear under fresh token permutations or equal-order OOD groups;
5. the proposed structural endpoint adds no predictive, calibration, teaching, interpretability, or mechanistic value beyond existing *In-Context Algebra*-style evaluation.

## 8. Relationship to existing papers in this repository

`pedagogical_signal_extraction.md` already states that arbitrary identifiers may become meaningful through interaction and that different internal registries can be functionally equivalent. The current programme supplies an exact finite notion of what can remain unidentified beneath such equivalence.

`semantic_atlas.md` already treats raw coordinates as observer-specific and requires empirical calibration for cross-model correspondence. The current programme suggests a complementary, not substitutive, question: after admissible transformations are quotiented out, which relational or transition structure is actually fixed by the observations?

No change to either existing main paper is justified by this audit alone.

## 9. Sources inspected

- Birkhoff, G. (1935). “On the Structure of Abstract Algebras.” *Proceedings of the Cambridge Philosophical Society* 31(4):433–454. doi:10.1017/S0305004100013463.
- Lawvere, F. W. (1963). “Functorial Semantics of Algebraic Theories.” *PNAS* 50(5):869–872.
- Benacerraf, P. (1965). “What Numbers Could Not Be.” *The Philosophical Review* 74(1):47–73. doi:10.2307/2183530.
- Goldman, S. A. & Kearns, M. J. (1995). “On the Complexity of Teaching.” *JCSS* 50(1):20–31. doi:10.1006/jcss.1995.1003.
- Roeder, G., Metz, L. & Kingma, D. P. (2021). “On Linear Identifiability of Learned Representations.” ICML 2021, PMLR 139:9030–9039. arXiv:2007.00810.
- Todd, E., Brinkmann, J., Gandikota, R. & Bau, D. (2025/2026). “In-Context Algebra.” arXiv:2512.16902.
- Nelson, W., Fumero, M., Karaletsos, T. & Locatello, F. (2026). “Statistical and Structural Identifiability in Representation Learning.” ICLR 2026. arXiv:2603.11970.
- Edidin, D. & Katz, J. (2025). “Orbit Recovery from Invariants of Low Degree in Representations of Finite Groups.” arXiv:2503.00009.
- Stanford Encyclopedia of Philosophy, “First-order Model Theory,” sections on categoricity and Löwenheim–Skolem.

## 10. Next scientific gate

Do not expand the philosophical claim first. The next evidence should come from a finite, exact benchmark in which the true structural version space is enumerable. Only if that benchmark shows a robust gap between prediction and identification should the programme move to larger learned representations or Semantic Atlas dynamics.
