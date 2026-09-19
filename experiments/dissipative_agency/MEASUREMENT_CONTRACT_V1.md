---
type: "Companion Note"
title: "Dissipative Agency v1 — Frozen Measurement Contract"
description: "Human-readable companion to run_spec_v1.json freezing the primary counterfactual agency estimator, power/precision gate, controller-budget accounting, Theseus stress calibration, and discrete-scale claim boundary."
tags: [dissipative-agency, preregistration, causal-inference, theseus, malecns]
timestamp: 2026-09-17T10:48:00-04:00
---

# Dissipative Agency v1 — Frozen Measurement Contract

This note is a human-readable rendering of the load-bearing gates in `run_spec_v1.json`. The JSON is authoritative for execution. Changes to any primary estimator, threshold, dimension, rollout count, intervention, budget rule, or success condition require a new run-spec version before confirmatory outcomes are inspected.

## 1. Primary agency certificate

Agency is not identified with coherence. Coherence is a lifecycle observable. The primary agency certificate is paired counterfactual contraction of reachable futures in the fixed-dimensional macrostate exposed by the candidate entity.

For an eligible snapshot, controlled and free branches start from the identical global state and receive the same exogenous stochastic stream. For each rollout `m` and horizon `h`, record the resulting entity macrostate

\[
q_A^{(b,m)}(t+h)\in\mathbb R^d.
\]

The v1 macrostate dimension is bounded by

\[
d\le16.
\]

The exact coordinate set, its dimension, and coordinate normalization must be frozen from calibration runs before the confirmatory run. No outcome-dependent addition of richer macrostate coordinates is permitted.

The primary future-volume proxy is

\[
V_{b,h}=\frac12\log\det(\Sigma_{b,h}+\epsilon I),
\]

with `epsilon = 1e-4` after calibration-only coordinate normalization.

The primary causal effect is

\[
\Delta V_h=V_{\mathrm{free},h}-V_{\mathrm{controlled},h}.
\]

The primary horizon is 100 base ticks. Horizons 25 and 500 are supporting measurements and cannot replace a failed primary horizon.

Each branch uses 256 matched rollouts. The uncertainty interval is computed by 2,000 paired bootstrap resamples of the matched rollout indices, recomputing both covariance log-determinants on each resample.

The primary certificate is GREEN only if the lower bound of the preregistered 95% interval at the primary horizon exceeds

\[
\delta_{\min}=0.10\ \text{nat}.
\]

A raw floating-point inequality `V_controlled < V_free` is not evidence of agency.

Alternative kNN entropy, covering-radius, or trace-covariance measurements are sensitivity analyses only. They cannot substitute for the primary estimator after outcomes are observed.

## 2. Precision and power gate

The reachable-volume estimator must itself be measurable with adequate precision. Before any confirmatory emergence result is inspected, calibration-only runs must demonstrate:

- at least 16 rollouts per active macrostate dimension;
- a 95% interval half-width no larger than 0.05 nat for the primary `DeltaV` estimator under the frozen measurement pipeline.

The registered v1 design uses at most 16 dimensions and 256 rollouts per branch, exactly the minimum 16:1 rollout-to-dimension ratio at the maximum allowed dimension.

If the precision gate fails, v1 remains RED. Increasing rollout count, changing `d`, changing `epsilon`, changing the estimator, or changing the minimum effect is prohibited inside v1; the remedy is a new `run_spec_v2` frozen before confirmatory outcomes are examined.

## 3. Causal control is not viability

A passive structure or a controller that freezes a region may reduce future dispersion. Therefore future-volume contraction certifies causal control only.

A persistent agent must additionally satisfy independent lifecycle and energetic gates: positive controller energy, nontrivial resource throughput, action cost, and survival under the registered environment. This prevents a static crystal or frozen-world controller from satisfying the full entity criterion merely by occupying a narrow state-space basin.

## 4. H1 and H2 are independent hypotheses

### H1 — recursive-control hypothesis

H1 asks whether recursive control changes preregistered persistence and hierarchy outcomes relative to passive, detection-only, and shallow-control universes. H1 does not require MaleCNS to be special.

### H2 — connectome-topology hypothesis

H2 asks whether MaleCNS topology differs from topology-destroying and matched synthetic controllers under identical interfaces and charged budgets.

H1 may succeed while H2 fails. Such an outcome is explicitly not evidence for a MaleCNS-specific advantage.

For H2, implementation efficiency cannot become a hidden metabolic advantage. Every matched controller pays the same preregistered **reserved compute charge per invocation** and shares the same action-energy ceiling. Actual normalized operation count and wall-clock cost are recorded per controller instance as secondary efficiency measurements but do not change the primary H2 metabolic charge.

Every controller instance maintains its own energy ledger in addition to the global ledger.

## 5. Energy-accounting gate

The full stochastic driven system is not expected to conserve ordinary energy or momentum because it contains bath forcing, damping, resource transfer, and active control.

Numerical validation therefore has two distinct regimes.

First, in the appropriate closed passive limit (`controller=off`, stochastic/resource forcing removed as required by the selected force law), conservation and symmetry properties implied by that passive model must hold within frozen numerical tolerances.

Second, the driven simulation must close the explicit ledger

\[
\Delta E=W_{\mathrm{controller}}+W_{\mathrm{bath}}-D+\epsilon_{\mathrm{numerical}}.
\]

The numerical residual tolerance is calibrated and frozen before confirmatory runs. Ledgers are recorded both globally and per controller instance.

## 6. Theseus signature and boundary stress

A causal identity test is meaningless if perturbations are always gentle. The confirmatory intervention strength is therefore selected only on calibration seeds from the frozen candidate impulse grid

\[
\{0.25,0.5,1.0,2.0,4.0\}.
\]

Using the severed branch as reference, choose the smallest impulse whose calibration death fraction lies between 20% and 40%. That magnitude is then frozen for confirmatory tests.

If no candidate reaches the target mortality band, v1 remains RED. The grid may be changed only in v2.

The frozen causal-signature intervention battery contains:

- momentum impulses in `+x`, `-x`, `+y`, and `-y` at the calibrated boundary-stress magnitude;
- a phase reset applied to 10% of immediate constituents;
- random dropout of 5% of immediate constituents.

Responses are sampled at base ticks

`[0, 10, 25, 50, 100, 250, 500]`.

`K_A` is the concatenated, calibration-normalized `q_A` response matrix over this fixed battery. Its distance is normalized Frobenius distance.

The Theseus tolerance `epsilon_Theseus` is the 95th percentile of within-entity repeated-intervention distances measured on calibration seeds only, then frozen before confirmatory turnover runs.

Full Theseus persistence requires all three conditions:

1. initial and current constituent sets are disjoint;
2. the controller instance has been replaced;
3. the causal-signature distance is below the frozen calibration tolerance.

## 7. Scale claim boundary

Version 1 is **recursively scale-consistent across simulator-defined discrete levels**.

It does not establish:

- continuous scale invariance;
- scale-free agency;
- automatic discovery of privileged physical coarse-grainings.

A later experiment may search over continuous or overlapping coarse-grainings and use the agency certificate itself to discover candidate causal boundaries. That stronger experiment is explicitly outside the claims of v1.

## 8. Independent ways for v1 to fail

The design permits at least five scientifically distinct negative outcomes:

1. no statistically resolved counterfactual future-volume pruning;
2. no metabolic advantage (`G_k` fails);
3. no recursive advantage over shallow control;
4. no causal-signature continuity after full constituent and controller turnover;
5. no MaleCNS-specific topology effect.

A positive result on one gate does not rescue a failure on another. In particular, H1 success does not imply H2 success, and causal control does not imply dissipative viability.
