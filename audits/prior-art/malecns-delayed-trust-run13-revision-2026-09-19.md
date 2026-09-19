---
type: "Audit Report"
title: "RUN12 delayed trust — RUN13 stronger-baseline revision — 2026-09-19"
description: "Explicit revision to the RUN12 audit recording the post-cutoff RUN13 soft robust baseline, which directly dominates the learned hard trust gate and changes the mechanism-level interpretation."
tags: [malecns, prior-art, falsification, delayed-supervision, learned-trust, robust-fusion, stronger-baseline, revision]
timestamp: 2026-09-19T10:10:00Z
---

# RUN12 delayed trust — RUN13 stronger-baseline revision

This is an explicit addendum to [`malecns-delayed-trust-2026-09-19.md`](./malecns-delayed-trust-2026-09-19.md). It preserves the original audit rather than silently rewriting its evidence ledger.

## Temporal separation

RUN12's conservative public cutoff is **2026-09-19 09:09:03 UTC**, the creation time of PR [#628](https://github.com/franklinbaldo/papers/pull/628).

RUN13 was first publicly exposed by PR [#632](https://github.com/franklinbaldo/papers/pull/632), created at **2026-09-19 10:05:13 UTC** and merged at **10:05:51 UTC**. It is therefore **post-cutoff** evidence and cannot be called prior art against RUN12.

RUN13 explicitly says it implements the soft robust-fusion control required by the earlier falsification audit, freezes/reconstructs the recorded RUN12 model, and compares it directly against a simpler bounded-influence estimator. There is positive, explicit dependence on RUN11/RUN12.

**Temporal/dependency classification:** `later_derivative` for the internal experimental lineage. This says only that RUN13 intentionally builds on RUN12; it carries no adverse implication.

## The stronger test

**Work:** [`FINDINGS_2026-09-19_RUN13_SOFT_ROBUST_TRUST.md`](../../experiments/malecns_car_interface/FINDINGS_2026-09-19_RUN13_SOFT_ROBUST_TRUST.md), *MaleCNS Car Interface Run 13: Soft robust fusion beats hard trust gating*.

RUN13 keeps the same 12-specialist compute budget and the existing RUN12 synthetic generator, freezes the RUN12 learned hard gate, and adds a modality-generic bounded-influence estimator using only declared confidence, freshness and lawful residuals. Every paid probe is retained but smoothly downweighted with a Cauchy residual weight rather than accepted/rejected by a binary trust gate.

At 20% injected high-confidence specialist faults, five seeds × 5,000 episodes per profile produced:

| camera-age profile | fixed hard gate | frozen RUN12 learned hard gate | soft robust | soft vs learned |
|---|---:|---:|---:|---:|
| uniform | 0.106566 | 0.105817 | **0.075722** | **28.44% lower MAE** |
| fresh-skewed | 0.096438 | 0.095997 | **0.071829** | **25.18% lower MAE** |
| stale-skewed | 0.104873 | 0.104013 | **0.076794** | **26.17% lower MAE** |

The more diagnostic result is the **0% injected-fault condition**: fixed hard `0.100217`, learned hard `0.100755`, soft robust **`0.066158`**. The simpler estimator therefore wins strongly even when the synthetic fault-detection problem is absent.

## Truth-status effect on RUN12

### C3 — learned delayed trust improves on the fixed RUN11 gate

The narrow numerical statement survives: in RUN13's rerun the learned hard gate remains modestly better than the fixed hard gate at the nominal 20% fault regime.

But the scientific interpretation changes because the stronger baseline closes far more than the RUN12 learned-vs-fixed gap.

**Classification:** `contrary_evidence` against the mechanism/complexity claim; `boundary_condition` for the narrow C3 result.

**Strength:** `strong` inside the shared synthetic generator because the comparison is matched, direct, uses the frozen RUN12 weights, and the effect is roughly two orders of magnitude larger than the learned-vs-fixed incremental gap on a relative scale.

**Target attacked:** mechanism, baseline adequacy, magnitude/importance of the learned gate — not the recorded RUN12 table.

**Required change:** `revise_mechanism` + `downgrade_confidence`. Do not treat the sub-1% learned-hard-gate gain as evidence that learning trust is the needed solution in this generator.

### C4 — benefit grows with injected fault prevalence

RUN13 shows the soft estimator is already dramatically better at **0%** injected specialist faults. This means a large fraction of the performance problem being attacked by hard trust gating was ordinary noisy/asynchronous estimation, not specialist-fault identification.

**Classification:** `contrary_evidence` against a fault-detection-centric explanation; `boundary_condition` for interpreting RUN12's prevalence curve.

**Strength:** `strong` in-harness.

**Required change:** `revise_mechanism`. Separate robust estimation from resource/trust control.

### C1/C2 — delayed supervision and trust features

RUN13 does not falsify the possibility that delayed lawful corroboration can train useful trust/resource policies. It does show that **the current binary admission objective is not the right place to claim incremental value** before robust estimation is solved.

**Classification:** `boundary_condition`.

**Strength:** `strong` for experimental ordering, not for the eventual value of delayed supervision.

**Required change:** `narrow_claim` + `add_control`. Future learned/MaleCNS controllers should operate above a strong robust estimator or demonstrate incremental value beyond it.

## Revised interpretation

The current evidence hierarchy is now:

1. RUN11: a fixed hard gate can help when confidently wrong reports are common;
2. RUN12: a learned hard gate can modestly improve that fixed hard gate in the same family, but not universally;
3. RUN13: a simpler continuous robust estimator **substantially dominates both hard gates**, including in the no-injected-fault regime.

The most defensible mechanism is therefore not “we need a smarter trust classifier.” It is:

> **robust estimation should absorb ordinary noisy/stale disagreement first; learned or MaleCNS trust/resource control is only justified for residual decisions that robust estimation cannot solve — activation, probing, quarantine, communication, missing modalities, compute/latency/energy allocation, or persistent source reputation.**

This is a material falsification success for the research programme: the stronger baseline removes a tempting but unnecessary layer of complexity.

## Remaining falsifier

RUN13 still calibrates its single robust scale against the same idealized delayed corroborator family. It therefore does **not** resolve the main RUN12 audit boundary around teacher dependence, instance-dependent proxy noise, dynamic temporal aliasing, or shared candidate+teacher failure.

Issue [#634](https://github.com/franklinbaldo/papers/issues/634) remains the discriminating next test. The soft robust estimator should now be treated as the principal baseline in that teacher-quality ladder, not merely a future comparator.
