---
type: "Companion Note"
title: "Lean 4 Companion — Scale-Consistent Recursive Agency"
description: "Machine-checkable companion for sparse_intelligence_dissipative_universe.md, separating matter, organization, lifecycle viability, ideal counterfactual agency, versioned measurement contracts, empirical agency certificates, recursive promotion, and full Ship-of-Theseus persistence."
tags: [lean4, dissipative-agency, recursive-agency, causal-pruning, malecns]
timestamp: 2026-09-17T08:50:00-04:00
---

# Lean 4 Companion — Scale-Consistent Recursive Agency

This directory contains the formal core for `sparse_intelligence_dissipative_universe.md`.

The formalization is intentionally **scale-consistent across simulator-defined discrete levels**, not a proof of continuous scale invariance or scale-free agency.

## What the formalization separates

The ontology remains deliberately layered:

1. **Matter** — `Level P k` is the substrate available at level `k`.
2. **Organization** — `Assembly α` is a nonempty collection plus a controller, but is not automatically viable or agentic.
3. **Lifecycle viability** — `Entity P α` carries a proof that the assembly is above the death threshold and has positive controller energy.
4. **Ideal agency** — `HasIdealContrafactualAgency` states the semantic target: holding initial matter and exogenous noise fixed, active control strictly prunes the accessible future volume relative to the free branch.
5. **Measurement contract** — `FutureVolumeContract` freezes a version, estimator identity, rollout count, primary/supporting horizons, regularizer, minimum meaningful effect, confidence level, and an explicit macrostate-dimension ceiling.
6. **Empirical agency certificate** — `EmpiricalAgencyCertificate` may exist only when its estimate is tied to the registered contract version/estimator/budget/horizon and the lower confidence bound clears the preregistered minimum effect.
7. **Recursive promotion** — `Level P (k + 1)` is definitionally `Entity P (Level P k)`. What survives at one level becomes the matter of the next.
8. **Causal identity under turnover** — `FullTheseusPersistence` requires complete constituent replacement, controller-instance replacement, and preservation of an intervention-defined causal signature under the same versioned `CausalIdentityContract`.

Coherence therefore remains useful as a physical lifecycle observable, but it is **not** the definition of agency. A passive crystal may be coherent. It may even resist perturbation. It does not receive an empirical agency certificate merely from coherence or a favorable point estimate.

## Ideal meaning vs finite evidence

The formal core deliberately does not collapse the scientific meaning into the estimator.

### 1. Ideal meaning

`HasIdealContrafactualAgency` expresses the counterfactual statement we mean:

```text
same initial matter
same exogenous noise
controlled accessible-future volume < free accessible-future volume
```

`PairedCounterfactual` stores the common initial matter, common noise, and proposed control in one object. The two branches are then derived from that object, making the intended pairing explicit in the type structure.

### 2. Allowed measurement

Finite experiments observe rollouts only through the fixed-dimensional `MacroState`. `FutureVolumeContract` is the logical surface to which a concrete preregistration binds its numerical estimator.

The current run specification freezes a Gaussian regularized log-det estimator, but Lean intentionally leaves `EstimatedFutureVolume` abstract. This is important: the theorem layer should not turn one numerical proxy into the definition of agency. A concrete estimator must instead be identified by the versioned contract used to issue a certificate.

### 3. Evidence threshold

`PassesAgencyGate` requires more than a favorable point estimate. The estimate must match the registered:

- contract version;
- estimator identity;
- rollout count;
- primary horizon;

and its lower confidence bound must exceed the contract's minimum meaningful effect.

Thus the formal layer distinguishes:

```text
meaning
→ allowed measurement contract
→ evidence threshold
```

rather than treating an observed floating-point inequality as a scientific conclusion.

## Theseus identity is also contract-bound

`CausalIdentityContract` freezes the identity-test surface:

- contract version;
- signature identity;
- tolerance `epsilon`;
- perturbation count;
- response horizon.

`FullTheseusPersistence` then requires, under that same contract:

```text
initial/current constituent sets are disjoint
controller instances differ
causal-signature distance < frozen epsilon
```

The numerical calibration of `epsilon`, the concrete intervention battery, and the response representation remain empirical and are governed by the preregistered run specification.

## Trusted boundary

The file intentionally has no Mathlib dependency. It abstracts the numerical and physical layer through explicit axioms/interfaces:

- scalar quantities and order;
- primitive substrate and noise;
- coarse-graining `phi`;
- physical step dynamics;
- ideal reachable-future volume;
- finite macrostate rollouts;
- finite future-volume estimation;
- confidence-bound results supplied as `AgencyEstimate`;
- causal signatures and distances;
- material disjointness.

Lean checks the type-level ontology and contract-binding theorems relative to these interfaces. It does **not** prove:

- that the Gaussian log-det estimator is statistically adequate for a particular `d` and rollout count;
- that bootstrap confidence intervals have their nominal coverage;
- that the CUDA/Python simulator is physically correct;
- that MaleCNS is intelligent or superior to controls;
- that recursive agency emerges;
- that the preregistration was historically frozen before data were inspected.

Those are empirical/provenance claims governed by Git history, CI artifacts, calibration runs, and `experiments/dissipative_agency/run_spec_v1.json`.

## Load-bearing definitions

```text
Alive
Entity
Level
PairedCounterfactual
HasIdealContrafactualAgency
FutureVolumeContract
PassesAgencyGate
EmpiricalAgencyCertificate
CanSpawn
CausalIdentityContract
FullTheseusPersistence
```

The recursive identity remains:

```text
Level P 0       = Primitive
Level P (k + 1) = Entity P (Level P k)
```

No theorem in this companion promotes lifecycle viability into agency automatically.

## CI

The companion is checked with the same pinned Lean toolchain style already used elsewhere in the repository:

```bash
lean formalizations/dissipative_agency/DissipativeAgency.lean
```

The corresponding workflow is `.github/workflows/dissipative-agency-lean.yml`.
