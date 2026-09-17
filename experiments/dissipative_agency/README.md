---
type: "Companion Note"
title: "Dissipative Agency Experiment — Preregistered Harness"
description: "Execution contract for the sparse-intelligence dissipative-universe paper: numerical validation, lambda_0 hysteresis sweep, recursive-controller ablations, and split-world causal intervention."
tags: [dissipative-agency, experiment, preregistration, malecns, causal-intervention]
timestamp: 2026-09-17T08:35:00-04:00
---

# Dissipative Agency Experiment

This directory contains the preregistered experiment contract for `sparse_intelligence_dissipative_universe.md`.

## Status

Not run. The files here freeze the first scientific gates before inspecting emergence outcomes. In particular, `10^5+` entities is a scaling target, not a demonstrated throughput result.

## Scientific separation

The harness must keep three structures distinct:

1. **short-range physical neighborhood** — exact spatial-grid interactions used for contact, capture, ejection, local lifecycle measurements, and self-force exclusion;
2. **long-range numerical approximation** — Barnes-Hut multipoles used for distant fields and coarse contextual observations;
3. **causal hierarchy** — empirically persistent entities that can become constituents of a higher level.

Barnes-Hut nodes must never become entities merely because they exist in the numerical tree.

## Agency criterion

Coherence is a lifecycle observable, not the definition of agency. A candidate counts as exhibiting agency only under a paired counterfactual test in which the same initial matter and same exogenous disturbance are evaluated with and without the controller action.

The core inequality is:

\[
V_{\mathrm{future}}(X,c,\xi)
<
V_{\mathrm{future}}(X,\varnothing,\xi).
\]

A passive crystal or oscillator may remain coherent but does not receive an agency certificate unless its active intervention strictly prunes the reachable future bundle relative to the matched free branch.

## Frozen run spec

`run_spec_v1.json` fixes:

- the initial substrate and noise parameters;
- lifecycle hysteresis thresholds;
- the upward/downward `lambda_0` sweep;
- universes A–D;
- controller ablations;
- the split-world intervention;
- the Theseus criteria;
- numerical-validation gates;
- Figure 1 observables.

Any scientifically material change to a threshold, branch, metric, intervention, or controller comparison requires a new run-spec version.

## RED / success discipline

The run is RED until all of the following are true:

- exact small-`N` dynamics and Barnes-Hut approximations agree within a preregistered tolerance;
- key trajectory-level observables remain stable under a stricter Barnes-Hut acceptance setting;
- local interactions exclude self-force exactly;
- upward and downward `lambda_0` sweeps finish for every registered seed and universe;
- all raw measurements needed for Figure 1 are persisted;
- split-world branches share the same pre-branch state and matched exogenous noise stream;
- no positive agency claim is inferred solely from coherence, clustering, or visual complexity.

The run becoming GREEN means only that the measurement contract completed. It does not imply the hypothesis succeeded.

## Primary causal intervention

Once an entity at level `k >= 2` has `S0 < 0.01` and `Theta_k >= 10`, clone the full simulator state into:

- `intact` — actual controller output;
- `severed` — zero controller output;
- `matched_noise` — matched stochastic output;
- `temporally_shuffled` — historical controller output at the wrong time.

Inject the same standardized shock and evaluate the four branches for 500 base ticks. The same exogenous stochastic stream must be reused across branches where implementation permits.

## Required outputs

At minimum, each run persists:

- `D_max(t)` and `N_k(t)`;
- `G_k`;
- `S0(t)` and `Theta_k(t)`;
- controller energy balances;
- upward/downward `lambda_0` traces;
- `lambda_ignite` and `lambda_extinguish` estimates;
- reachable-future-volume measurements;
- causal signatures under standardized perturbations;
- split-world branch trajectories;
- wall-clock, memory, backend, and Barnes-Hut error diagnostics.

## Figure 1 contract

The paper's central figure is generated only from registered outputs:

- Panel A: `D_max(lambda_0)` with upward/downward branches;
- Panel B: `G_k` with the neutral line `G=1`;
- Panel C: `Theta_k` and material retention `S0`;
- Panel D: split-world causal intervention after a mature Theseus regime is reached.

If the eligibility condition for Panel D is never reached, that absence is itself the registered result; the threshold must not be relaxed post hoc inside v1.
