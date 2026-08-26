---
type: "Companion Note"
title: "Lean 4 Companion — Semantic Observers"
description: "Machine-checked negative-result ledger for deterministic garbling, restricted observer orders, cross-task reversal, and probe-relative reparameterization invariance."
tags: [lean4, semantic-observers, decision-theory, formal-verification]
timestamp: 2026-08-26T02:15:00Z
---

# Lean 4 Companion — Semantic Observers

This directory contains the machine-checked formal companion for `semantic_observers.md`.

## Why this exists

This file is **not** intended as a badge of mathematical depth. The load-bearing theorems are elementary. Its purpose is more useful: it is a formal ledger of several natural definitions of "observer A sees more than observer B" that turn out to be vacuous, benchmark-relative, or probe-relative.

The adversarial review initially claimed that deterministic encoders with `theta = input` should have maximal bilateral deficiency because their outputs are point masses. That claim was wrong. Formalizing the deterministic core exposed the correct structure immediately.

For deterministic observers `A : Θ → Z_A` and `B : Θ → Z_B`, exact deterministic simulation `A → B` exists precisely when every fiber/collision of `A` is also a fiber/collision of `B`.

Consequently, if `A` is injective on a finite registered benchmark, an unrestricted simulator can reproduce **any** deterministic `B` by memorizing the correspondence from `A(x)` to `B(x)`. If both observers are injective, exact simulations exist in both directions.

For modern floating-point embeddings evaluated on finite item sets, exact collisions are atypical. This makes `theta = individual input item` generically uninformative as a population-level observer comparison: unrestricted comparison tends to collapse to exact equivalence rather than reveal a refinement order.

## Formalized claims

`SemanticObservers.lean` proves:

1. `deterministicGarbling_iff_fiberRefines`
   - exact deterministic garbling `A -> B` is equivalent to
     `A(x) = A(y) -> B(x) = B(y)`;
2. `injective_source_simulates_any`
   - an injective source observer can exactly simulate any target observer under unrestricted deterministic garbling;
3. `injective_encoders_are_bilaterally_garbling`
   - two injective deterministic observers are exactly simulable in both directions on the registered index set;
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

Together these certify three negative constraints on the empirical paper:

- **point-indexed unrestricted comparison can collapse under injectivity**;
- **dominance on one decision family does not imply an observer-level order**;
- **restricted extractability is relative to the allowed probe/rule class**.

The positive hypotheses in the revised paper — realization-invariance profiles and behavioral semantic parallax — are empirical and are not proved by Lean.

## Connection to the revised empirical protocol

The paper indexes empirical claims by

`Π = (Θ, ν, D, H, A)`

with deliberately different roles:

- `Θ` and `ν` define the measurement environment;
- `D` is the axis across which transfer claims are tested;
- `H` and `A` are nuisance/capacity classes that must be swept rather than fixed opportunistically.

The Lean result explains why `ν` is not optional if one wants a nontrivial stochastic experiment from deterministic embedding APIs: setting `Θ` equal to individual benchmark items generically produces injective maps and therefore trivial mutual simulation under unrestricted garblings.

The remaining scientific question is empirical: whether independently generated realization protocols expose reproducible observer-specific invariance profiles, and whether residuals after cross-model alignment predict item-level model behavior across such protocols.

## What is intentionally not formalized

The companion does **not** formalize probability measures, total variation, Markov kernels, Bayes integrals, or Le Cam deficiency. Those require a substantially larger measure-theoretic dependency surface and are not needed for the negative constraints above.

The current Lean core treats:

- deterministic exact garbling directly as existence of a simulator function;
- empirical restricted dominance through an abstract risk functional;
- reparameterization through equivalences of observation types and transported decision rules.

A later Mathlib-backed companion would be justified only if the stochastic realization protocol is frozen and a genuinely load-bearing probabilistic theorem emerges.

## Trusted boundary

The file imports no Mathlib module and introduces no axioms. It uses classical choice in the converse direction of `deterministicGarbling_iff_fiberRefines`, to define a simulator consistently across source fibers and outside the observed image. The load-bearing theorems end with `#print axioms` commands so CI logs expose their dependencies.

## CI

The repository workflow `.github/workflows/semantic-observers-lean.yml` installs Lean 4.22.0 and checks:

```bash
lean formalizations/semantic_observers/SemanticObservers.lean
```
