---
type: "Companion Note"
title: "Lean 4 Companion — Interventional Latent Graphs"
description: "Machine-checked core for the Interventional Latent Graph paper: binary contrast, intervention-as-edge multigraphs, walks, parallel edges, and response disagreement."
tags: [pontifex, interventional-graph, lean4, formal-verification]
timestamp: 2026-09-19T03:10:00Z
---

# Lean 4 Companion — Interventional Latent Graphs

This directory contains the machine-checked core for `interventional_latent_graph.md`.

## Scope

`InterventionalLatentGraph.lean` formalizes only the minimal layer:

- a binary two-arm intervention alphabet;
- non-trivial contrast;
- impossibility of non-trivial contrast in a subsingleton alphabet;
- an interventional latent graph whose edge type is definitionally the intervention type;
- symmetric endpoint connectivity;
- walks as composable intervention sequences;
- additive intervention length under walk composition;
- distinct parallel interventions with the same endpoints;
- a valid shared-intervention edge whose endpoint responses disagree;
- a closed three-edge walk.

The point of the formalization is to keep the primitive ontology small enough that later Pontifex machinery cannot silently redefine an edge as an equivalence claim.

## What is not formalized

This companion deliberately does not formalize:

- Shannon entropy or coding theorems;
- Landauer thermodynamics;
- photons or quantum mechanics;
- Pearlian structural causal models or do-calculus;
- learned maps between embeddings;
- response metrics or Pontifex alignment scores;
- manifold reconstruction;
- toroidal topology.

Those belong to literature dependencies, empirical layers, or future formal extensions.

## Trusted boundary

The proof file imports no Mathlib module and introduces no axioms. The final `#print axioms` commands expose the dependencies of the load-bearing theorems in CI logs.

The core claim "binary is minimal" is intentionally formalized in the weakest defensible way:

1. a two-arm alphabet contains two distinct alternatives;
2. a subsingleton alphabet cannot contain two distinct alternatives.

The Lean file does not claim that a bit is a minimum physical quantum or minimum-energy perturbation.

## CI

The repository workflow `.github/workflows/interventional-latent-graph-lean.yml` installs Lean 4.22.0 and checks:

```bash
lean formalizations/interventional_latent_graph/InterventionalLatentGraph.lean
```

The formal claims should be treated as verified only when this check compiles.
