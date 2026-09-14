---
type: "Companion Note"
title: "Lean 4 Companion — Semantic Observers Negative Ledger"
description: "Machine-checked ledger showing why deterministic point-indexed garbling, restricted observer orders, and fixed-probe reparameterization do not yield an intrinsic semantic-observer hierarchy."
tags: [lean4, semantic-observers, decision-theory, formal-verification, negative-results]
timestamp: 2026-08-26T03:00:00Z
---

# Lean 4 Companion — Semantic Observers Negative Ledger

This directory contains the machine-checked negative core that motivated the current `semantic_observers.md` experimental paper.

The formalization is intentionally modest. Its purpose is **not** to use Lean as a badge of mathematical depth. The theorems are elementary. Their value is methodological: several natural formalizations of “observer A sees more than observer B” are either vacuous on finite deterministic embedding benchmarks or relative to choices of task/probe class. Encoding those facts in Lean prevents later versions of the paper from silently reintroducing the discarded definitions.

## Formalized claims

`SemanticObservers.lean` proves:

1. `deterministicGarbling_iff_fiberRefines`
   - exact deterministic garbling `A -> B` is equivalent to `A(x) = A(y) -> B(x) = B(y)`;
2. `injective_source_simulates_any`
   - an injective source encoder can exactly simulate any target encoder under unrestricted deterministic garbling;
3. `injective_encoders_are_bilaterally_garbling`
   - two injective deterministic encoders are exactly simulable in both directions on the registered index set;
4. `resolved_collision_blocks_garbling`
   - if `A` merges two indexed states that `B` distinguishes, exact garbling from `A` to `B` is impossible;
5. `restrictedDominance_descends`
   - dominance on a larger decision family implies dominance on every subfamily;
6. `disjoint_decision_families_can_reverse_order`
   - a finite Boolean counterexample where the observer order reverses between two disjoint decision families;
7. `optimal_values_invariant_under_corresponding_probe_classes`
   - an invertible reparameterization preserves attained restricted optimum values only when the admissible probe classes correspond under pullback/pushforward;
8. `invertible_reparameterization_need_not_preserve_fixed_probe_score`
   - a finite counterexample showing that an invertible coordinate change can change fixed-probe extractability when the probe class is not equivariant.

## Scientific consequence

For high-dimensional floating-point embeddings on a finite benchmark, exact collisions are atypical. Consequently, if the parameter/state index is simply the input identity, unrestricted deterministic comparison generically becomes uninformative: an injective encoder can serve as a lookup key and exactly simulate any other deterministic observer on that finite set.

Likewise, a restricted task order does not define an intrinsic observer order, and fixed-probe extractability is not invariant under arbitrary invertible coordinate changes.

The current paper therefore abandons the original “semantic resolution hierarchy” as its primary thesis. It asks a different empirical question in dense retrieval: whether **cross-model aligned residual geometry adds predictive value about a behaviorally unseen retriever beyond modern target-local Query Performance Prediction signals**.

The Lean file does not prove that such residual geometry exists or is useful. It records only the negative constraints that a viable positive experiment must respect.

## What is intentionally not formalized

The companion does **not** formalize probability measures, total variation, Markov kernels, Bayes integrals, Le Cam deficiency, Query Performance Prediction, retrieval metrics, or the proposed leave-one-retriever-out experiment.

A larger Mathlib-backed stochastic formalization would be justified only if a later empirical result creates a theorem surface worth preserving. Formalizing the current experimental machinery in advance would add verification surface without resolving the substantive empirical question.

## Trusted boundary

The file imports no Mathlib module and introduces no axioms. It uses classical choice only in the converse direction of `deterministicGarbling_iff_fiberRefines`, to define a simulator across source-observation fibers. The load-bearing theorems end with `#print axioms` commands so CI logs expose their dependencies.

## CI

The repository workflow `.github/workflows/semantic-observers-lean.yml` installs Lean 4.22.0 and checks:

```bash
lean formalizations/semantic_observers/SemanticObservers.lean
```
