---
type: "Companion Note"
title: "Synergy–Geometry Next Executable Step"
description: "Defines the next admissible implementation slice after the paper and toy apparatus: freeze one small model-backed Gate 0/1 run without opening composition or causal gates."
tags: [interaction-geometry, next-step, experiment, preregistration]
timestamp: 2026-08-24T01:30:00Z
---

# Synergy–Geometry next executable step

The next implementation slice should **not** attempt all gates at once.

Its sole objective is to make Gate 1 executable without contaminating Gate 2.

## Deliverables

1. Freeze a primary small open causal LM and revision.
2. Freeze one independently trained transfer model and revision, but do not run the cross-model gate yet.
3. Implement R1 and R2 task generators with balanced lexical scaffolds.
4. Materialize and hash the five protocol roles.
5. Add activation capture at a predeclared set of layers/sites.
6. Add the full Gate 1 baseline suite: additive, ridge, bilinear, MLP, direct marginal probe, shuffled pair, shuffled label, random subspace and raw-joint upper reference.
7. Produce one result artifact for Gate 0 and, only if Gate 0 passes, one result artifact for Gate 1.
8. Do **not** inspect `composition_test` during this slice.

## Stop condition

If Gate 1 fails in both preregistered task families, record the kill result and stop the strong programme. Do not open Gate 2, causal interventions, cross-model geometry, PID coupling, metaphor, analogy, or Semantic Atlas hyperedges as rescue analyses.

If Gate 1 passes, freeze the implementation SHA before `composition_test` is opened in a separate run/PR.
