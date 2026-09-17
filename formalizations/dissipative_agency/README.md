---
type: "Companion Note"
title: "Lean 4 Companion — Scale-Invariant Recursive Agency"
description: "Machine-checkable companion for sparse_intelligence_dissipative_universe.md, separating matter, organization, lifecycle viability, counterfactual agency, recursive promotion, and full Ship-of-Theseus persistence."
tags: [lean4, dissipative-agency, recursive-agency, causal-pruning, malecns]
timestamp: 2026-09-17T08:50:00-04:00
---

# Lean 4 Companion — Scale-Invariant Recursive Agency

This directory contains the formal core for `sparse_intelligence_dissipative_universe.md`.

## What the formalization separates

The ontology is deliberately layered:

1. **Matter** — `Level P k` is the substrate available at scale `k`.
2. **Organization** — `Assembly α` is a nonempty collection plus a controller, but is not automatically an agent.
3. **Lifecycle viability** — `Entity P α` carries a proof that the assembly is above the death threshold and has positive controller energy.
4. **Agency** — `HasContrafactualAgency` is stronger than viability: with the same initial matter and the same exogenous noise `ξ`, the controlled branch must strictly contract the accessible future volume relative to the free branch.
5. **Recursive promotion** — `Level P (k + 1)` is definitionally `Entity P (Level P k)`. What survives at one scale becomes the matter of the next.
6. **Causal identity under turnover** — `FullTheseusPersistence` requires complete constituent replacement, controller-instance replacement, and preservation of an intervention-defined causal signature within tolerance.

Coherence therefore remains useful as a physical lifecycle observable, but it is **not** the definition of agency. A passive crystal may be coherent. It does not receive an agency certificate unless active intervention prunes the paired counterfactual future bundle.

## Trusted boundary

The file intentionally has no Mathlib dependency. It abstracts the numerical and physical layer through explicit axioms/interfaces:

- scalar quantities and order;
- primitive substrate and noise;
- coarse-graining `phi`;
- physical step dynamics;
- reachable-future volume;
- causal signatures and distances;
- material disjointness.

Lean checks the type-level ontology and theorems relative to these interfaces. It does **not** prove that a concrete CUDA/Python simulator computes a physically correct reachable volume, that MaleCNS is intelligent, or that recursive agency emerges empirically. Those remain experimental claims governed by `experiments/dissipative_agency/run_spec_v1.json`.

## Load-bearing definitions

The central definitions are:

```text
Alive
Entity
Level
HasContrafactualAgency
CanSpawn
FullTheseusPersistence
```

The intended recursive identity is:

```text
Level P 0       = Primitive
Level P (k + 1) = Entity P (Level P k)
```

and the strong agency criterion is a paired intervention:

```text
same members
same exogenous noise ξ
controlled branch future volume < free branch future volume
```

## CI

The companion is checked with the same pinned Lean toolchain style already used elsewhere in the repository:

```bash
lean formalizations/dissipative_agency/DissipativeAgency.lean
```

The corresponding workflow is `.github/workflows/dissipative-agency-lean.yml`.
