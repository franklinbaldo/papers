---
type: "Audit Report"
title: "RUN11 probe-then-trust — soft-gating prior-art revision — 2026-09-19"
description: "Revision to the RUN11 prior-art/falsification audit adding a pre-cutoff hard-vs-soft gating comparison that strengthens the requirement for a soft robust baseline."
tags: [malecns, prior-art, falsification, probe-then-trust, sensor-fusion, soft-gating, robust-kalman, revision]
timestamp: 2026-09-19T09:08:00Z
---

# RUN11 probe-then-trust — soft-gating prior-art revision

This is an explicit revision/addendum to [`malecns-probe-trust-2026-09-19.md`](./malecns-probe-trust-2026-09-19.md). It preserves that audit rather than silently replacing its evidence ledger.

## Newly confirmed candidate

**Work:** *Soft-Gating Mixture Robust Kalman Filter for SINS/DVL Integrated Navigation Under DVL Outlier Interference*.

**Venue/status:** *Journal of Marine Science and Engineering* 14(13), 1165.

**First public date verified:** **2026-06-24**, well before RUN11's conservative cutoff of **2026-09-19 08:01:19 UTC**.

**Primary URL:** https://doi.org/10.3390/jmse14131165

The paper directly compares a conventional **hard innovation-gated Kalman filter** against Huber, Student-t, and a proposed logistic **soft-gating** mixture robust filter. The hard gate rejects a measurement when normalized innovation exceeds a chi-square threshold; the soft gate instead continuously blends nominal and robust branches according to innovation magnitude.

Two observations are directly relevant to RUN11:

1. under nominal/no-outlier conditions, the hard-gated filter can perform worse because transient/model/covariance mismatch causes valid measurements to be classified as outliers and repeatedly rejected;
2. under injected DVL outliers, hard-gate performance is explicitly described as sensitive to the selected threshold and binary accept/reject decision, while the soft robust design achieves a better nominal-accuracy/robustness trade-off in the paper's simulated regime.

## Claim relation

### C3 — fixed hard admission threshold improves robustness

**Priority classification:** `partial_prior_art` for robust admission/gating under outliers.

**Truth-status relation:** `boundary_condition` and `contrary_evidence` against treating binary hard gating as the natural or generally strongest robust-fusion baseline.

**Strength:** `moderate-to-strong` for mechanism/baseline choice; transfer is limited because the paper studies SINS/DVL Kalman navigation, not MaleCNS specialists.

**Target attacked:** mechanism and baseline adequacy, not RUN11's executed synthetic MAE table.

**Required change:** `add_control`. A soft robust/reliability-weighted baseline is mandatory before crediting any advantage to a learned trust coordinator.

### C4 — gating advantage rises with fault prevalence

The paper independently supports the broader boundary that robust filtering must trade nominal accuracy against outlier resistance rather than maximize one with a single rigid rule.

**Truth-status relation:** `boundary_condition`.

**Strength:** `moderate`.

**Required change:** `no_change` to RUN11's observed fault-rate ablation; retain the interpretation that the gate's benefit is regime-dependent.

### C6 — learned/adaptive gate is the next escalation

The result supplies a stronger simpler alternative: smooth innovation-dependent robust fusion can adapt continuously without a learned recurrent coordinator.

**Priority classification:** `partial_prior_art` / `adjacent_prior_work` for adaptive soft admission.

**Truth-status relation:** alternative mechanism.

**Strength:** `strong` for experimental design: a learned or MaleCNS gate should not be evaluated only against `always trust` and one fixed threshold.

**Required change:** `add_control`; if a calibrated soft robust gate matches the learned coordinator under identical information and budget, do not attribute the gain to learned/MaleCNS trust reasoning.

## Epistemic effect on the main audit

This source **does not retract RUN11's empirical result**. The five-seed synthetic comparison remains what it is.

It strengthens one conclusion already present in the main audit: the next ladder should include a soft robust baseline, not just a better hard threshold. It also supplies direct pre-cutoff evidence for the failure mode suggested by RUN11's own 0–10% ablation: hard rejection can sacrifice good observations when the reference model or transient state makes them look anomalous.

The current defensible wording is therefore:

> RUN11 shows that one fixed lawful hard-admission gate can improve mean error in its synthetic high-confident-fault regime. It does not show that binary rejection is the best robust-fusion mechanism, nor that a learned/MaleCNS gate is needed. A soft robust baseline must clear the same matched-information and matched-budget evaluation first.
