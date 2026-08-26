---
type: "Companion Note"
title: "Lean 4 Companion — Semantic Observers"
description: "Machine-checked core for deterministic garbling, restricted observer orders, cross-task reversal, and probe-relative reparameterization invariance."
tags: [lean4, semantic-observers, decision-theory, formal-verification]
timestamp: 2026-08-26T01:35:00Z
---

# Lean 4 Companion — Semantic Observers

This directory contains the machine-checked core for `semantic_observers.md`.

## Why this formalization comes first

The adversarial review exposed a point worth proving rather than narrating: with a deterministic encoder and `theta = input`, unrestricted exact garbling does **not** generally have deficiency one. Instead, exact deterministic simulation from `A` to `B` exists precisely when every fiber/collision of `A` is also a fiber/collision of `B`.

Consequently, if `A` is injective on a finite registered benchmark, an unrestricted simulator can reproduce **any** deterministic `B` by memorizing the map from `A(x)` to `B(x)`. If both encoders are injective on the benchmark, exact garblings exist in both directions. This is the real reason `theta = input` is often scientifically uninformative for comparing modern deterministic embeddings: unrestricted comparison can collapse to equivalence by memorization.

## Formalized claims

`SemanticObservers.lean` proves:

1. `deterministicGarbling_iff_fiberRefines`
   - exact deterministic garbling `A -> B` is equivalent to
     `A(x) = A(y) -> B(x) = B(y)`;
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

These claims formalize the paper's main methodological distinction:

- **unrestricted information equivalence** is invariant to invertible coordinate changes;
- **accessible/extractable information** is relative to the allowed decision/probe class;
- **dominance on one decision family** does not imply an observer-level order that transfers to another family.

## What is intentionally not formalized yet

The first companion does **not** formalize probability measures, total variation, Markov kernels, Bayes integrals, or Le Cam deficiency. Those require a substantially larger measure-theoretic dependency surface and are not needed to establish the paper's first logical constraints.

The current Lean core therefore treats:

- deterministic exact garbling directly as existence of a simulator function;
- empirical restricted dominance through an abstract risk functional;
- reparameterization through equivalences of observation types and transported decision rules.

A later Mathlib-backed companion can formalize the stochastic generalization once the experimental protocol is frozen.

## Trusted boundary

The file imports no Mathlib module and introduces no axioms. It uses classical choice only in the converse direction of `deterministicGarbling_iff_fiberRefines`, to define a simulator outside and across fibers of the source observation. The load-bearing theorems end with `#print axioms` commands so CI logs expose their dependencies.

## CI

The repository workflow `.github/workflows/semantic-observers-lean.yml` installs Lean 4.22.0 and checks:

```bash
lean formalizations/semantic_observers/SemanticObservers.lean
```
