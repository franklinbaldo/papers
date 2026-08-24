---
type: "Protocol"
title: "Synergy–Geometry Protocol Amendment 001 — Separate interaction detection from compositional generalization"
description: "Prospective amendment separating Gate 1 interaction evidence from Gate 2 compositional generalization before any model-backed confirmatory run."
tags: [semantic-atlas, synergy, interaction-geometry, preregistration, protocol-amendment]
timestamp: 2026-08-24T00:57:00Z
---

# Synergy–Geometry Protocol Amendment 001

## Status

Prospective amendment to `experiments/synergy_geometry/protocol.md`.

This amendment was written immediately after the initial preregistration landed in `main` and before any model-backed confirmatory result was committed to the repository. Its purpose is to remove an internal identification error in the gate sequence, not to accommodate observed outcomes.

Where this amendment conflicts with the original protocol, this amendment governs the first implementation/run. A later protocol revision may fold the change back into the main file, but must preserve this audit trail.

## Problem found

The original protocol intends Gate 1 and Gate 2 to answer different questions:

1. **Gate 1 / H1:** is there relation-specific interaction structure beyond marginal information and matched controls?
2. **Gate 2 / H2:** does that structure generalize compositionally to factor combinations not seen during fitting?

But H1 was defined and scored directly on `composition_test`, and H2 then required the H1 effect to remain on that same `composition_test` split. That makes the two gates depend on the same confirmatory observations and collapses interaction detection and compositional generalization into one test.

A protocol that kills at Gate 1 on the compositional holdout cannot later claim that Gate 2 independently established compositional generalization.

## Amendment

Freeze **five** disjoint data roles before the first model-backed confirmatory run:

1. `calibration` — gauge/alignment material only;
2. `train` — fits interaction estimators and decoders;
3. `interaction_test` — held-out examples from factor identities/compositions represented in the training design, used only to test relation-specific interaction structure without requiring novel composition;
4. `composition_test` — complete factor combinations absent from estimator/decoder fitting, used only for compositional generalization;
5. `relation_holdout` — where feasible, a relation/template family absent from estimator fitting; exploratory stronger transfer test unless separately powered and preregistered.

No example may appear in more than one split, and no trivial paraphrase of a confirmatory example may leak into `train` or `calibration`.

### Revised H1 / Gate 1

H1 asks only whether purified interaction structure exists and is relation-specific beyond marginal information and matched nonlinear controls.

Train the frozen-complexity relation decoder on `train` and evaluate H1 on `interaction_test`.

H1 passes only if all original H1 criteria hold **on `interaction_test`**:

- interaction decoding exceeds the best marginal-only baseline by at least 5 absolute percentage points on the primary balanced metric;
- the paired bootstrap 95% confidence interval for that improvement excludes zero;
- shuffled-pair and shuffled-label controls collapse toward their expected null level;
- the frozen layer-selection rule is respected.

H1 does **not** establish compositional generalization.

### Revised H2 / Gate 2

Only after H1 passes, evaluate the already-frozen estimator/decoder on `composition_test` without refitting, layer reselection, threshold changes, or hyperparameter updates.

H2 passes only if:

- the H1 direction of effect survives on `composition_test`;
- interaction decoding remains more than 2 absolute percentage points above the best marginal-only baseline;
- the paired bootstrap 95% confidence interval for the interaction-minus-best-marginal difference excludes zero;
- no confirmatory choice is revised after inspecting `composition_test`.

If H1 passes but H2 fails, classify the result as relation-specific interaction structure without demonstrated compositional generalization. Stop the strong programme at Gate 2 as originally intended.

## Layer and hyperparameter discipline

`interaction_test` must not become a hidden tuning set.

Any hyperparameter, probe capacity, layer/site rule, interaction-subspace dimension, centering choice, or preprocessing choice that is not fixed from theory/synthetic pilots must be selected inside `train` by nested resampling or on a separate pilot dataset that is never reused for H1/H2 confirmation.

After H1 is scored once on `interaction_test`, the implementation is frozen before `composition_test` is opened.

## Required implementation changes

The first implementation PR must therefore add:

- a frozen `interaction_test` manifest in addition to the original manifests;
- tests proving pair/example disjointness across all five roles;
- tests proving that `composition_test` contains genuinely unseen factor combinations;
- a result schema that records Gate 1 and Gate 2 metrics from distinct splits;
- a guard preventing `composition_test` from being used for training, layer selection, threshold selection, or hyperparameter tuning.

## What this amendment does not change

- Gate 0 synthetic sanity checks;
- the affine/linear gauge discipline;
- H3 causal intervention thresholds;
- H4 independent cross-model calibration boundary;
- H5 being conditional and unable to rescue failed geometry/causality gates;
- the claim boundary against "new semantic spaces";
- the rule that `semantic_atlas.md` remains unchanged until empirical gates earn integration.

## Falsifiable consequence

After this amendment, the programme can produce the scientifically meaningful outcome:

> H1 passes on ordinary held-out interaction examples, but H2 fails on unseen compositions.

That outcome was not cleanly identifiable under the original split usage because H1 already consumed the compositional holdout. Preserving this distinction is necessary for the kill-first gate sequence to mean what it says.
