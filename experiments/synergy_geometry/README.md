---
type: "Companion Note"
title: "Synergy–Geometry Experimental Programme"
description: "Map of the preregistered kill-first gates, current apparatus, and evidence boundary for Gauge-Controlled Interaction Geometry."
tags: [interaction-geometry, synergy, preregistration, experiment, semantic-atlas]
timestamp: 2026-08-24T01:18:00Z
---

# Synergy–Geometry experimental programme

This directory implements the experimental programme for `../../synergy_geometry.md`.

## Scientific status

The broad idea that semantic composition can produce interaction-specific structure is **not** treated as novel. The programme tests only whether a purified interaction representation survives a sequence of increasingly strong gates:

1. **Gate 0 — apparatus sanity:** recover a known additive null and a synthetic interaction positive control;
2. **Gate 1 — interaction:** relation-specific signal beyond matched marginal controls on `interaction_test`;
3. **Gate 2 — composition:** the frozen effect survives unseen factor combinations on `composition_test`;
4. **Gate 3 — causality:** norm-matched intervention selectively changes relation-dependent behavior;
5. **Gate 4 — cross-model stability:** independently calibrated models show above-null interaction correspondence;
6. **Gate 5 — synergy coupling:** target-level PID synergy covaries prospectively with geometry/causal efficacy.

A later gate does not rescue an earlier failure.

## Protocols

- `protocol.md` — original adversarial preregistration;
- `protocol-amendment-001.md` — prospective correction separating Gate 1 interaction detection from Gate 2 compositional generalization before any model-backed confirmatory run.

The amendment governs where it conflicts with the original protocol. It is preserved separately so the preregistration history remains auditable.

## Implemented apparatus

The cheap package currently provides:

- balanced factorial interaction decomposition;
- mixed finite differences;
- held-out main-effects interaction estimation;
- deterministic ridge relation decoding;
- paired bootstrap accuracy differences;
- split-manifest validation and hashing;
- additive and XOR-style synthetic controls;
- unit tests and a dedicated GitHub Actions workflow.

These components validate measurement plumbing only. They are **not** model-backed evidence for the hypothesis.

## Next admissible step

Before the first confirmatory model-backed result is inspected, freeze and commit:

- exact primary and transfer model IDs and revisions;
- tokenizer revisions, dtype and inference-library versions;
- task generators and lexical templates;
- the five disjoint split manifests (`calibration`, `train`, `interaction_test`, `composition_test`, `relation_holdout`);
- layer/site selection rule;
- probe and nonlinear-baseline capacities;
- result schema and gate thresholds;
- leakage tests proving that held-out combinations cannot enter fitting or calibration.

Only then should hidden-state collection begin.

## Evidence boundary

A green CI run means that the apparatus executed and its invariants passed. It does not mean that any scientific gate passed.

`semantic_atlas.md` remains unchanged unless the interaction programme earns integration empirically. A negative result at Gate 1 or Gate 2 is an intended terminal outcome for the strong claim.
