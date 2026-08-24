---
type: "Companion Note"
title: "Lean 4 Companion — Structural Identification from Restricted Truths"
description: "Machine-checked companion for the structural-identification theory note, listing the formal definitions, theorem surface, trusted boundary, and compile command."
tags: [lean4, structural-identification, formal-verification]
timestamp: 2026-08-24T03:41:00Z
---

# Lean 4 Companion — Structural Identification from Restricted Truths

This directory contains the machine-checked core for `structural_identification_from_restricted_truths.md`.

## Scope

`StructuralIdentification.lean` formalizes the generic layer only:

- structural version spaces;
- identification relative to a relation, hypothesis class, and evidence family;
- monotonicity under evidence and hypothesis refinement;
- hitting-set characterization;
- the observational-equivalence impossibility theorem;
- invariance under structural equivalence;
- finite-conjunction collapse;
- a finite four-group discrimination example.

The formalization deliberately does **not** formalize first-order syntax, group axioms, Scott sentences, teaching dimension, or computational complexity. Those are literature connections and downstream instantiations, not dependencies of the generic proofs.

The motivating `C4 / V4 / C8 / D4` example treats those names as already-classified isomorphism types. Lean checks the discrimination argument, not the underlying group-theory classification.

## Trusted boundary

The file imports no Mathlib module and introduces no axioms. It ends with `#print axioms` commands for the load-bearing theorems so CI logs expose any nonconstructive dependencies used by the proof terms. One theorem (`identifies_iff_hits_competitors`) invokes classical reasoning for the converse-from-no-witness step; the remaining theorem statements do not assume model-theoretic axioms.

## CI

The repository workflow `.github/workflows/structural-identification-lean.yml` installs the pinned Lean toolchain and checks:

```bash
lean formalizations/structural_identification/StructuralIdentification.lean
```

The proof file must compile before the mathematical claims are treated as verified.
