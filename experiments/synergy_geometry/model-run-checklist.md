---
type: "Checklist"
title: "Synergy–Geometry Model-Backed Run Checklist"
description: "Pre-run checklist that must be satisfied before opening the first confirmatory hidden-state results for the Synergy–Geometry programme."
tags: [interaction-geometry, preregistration, checklist, experiment]
timestamp: 2026-08-24T01:24:00Z
---

# Synergy–Geometry model-backed run checklist

This checklist operationalizes the freeze boundary in the preregistered protocol. It must be completed before the first confirmatory model-backed result is inspected.

- [ ] Primary open-weight causal LM ID is frozen.
- [ ] Primary model revision is frozen.
- [ ] Transfer model comes from an independently trained family.
- [ ] Transfer model revision is frozen.
- [ ] Tokenizer revisions are frozen.
- [ ] Torch/Transformers versions and dtype are frozen.
- [ ] Activation site and token-position convention are frozen.
- [ ] Layer-selection rule is frozen without using `interaction_test` or `composition_test` outcomes.
- [ ] R1 task generator and lexical templates are frozen.
- [ ] R2 task generator and lexical templates are frozen.
- [ ] Label maps and answer positions are balanced and frozen.
- [ ] `calibration` manifest is frozen and hashed.
- [ ] `train` manifest is frozen and hashed.
- [ ] `interaction_test` manifest is frozen and hashed.
- [ ] `composition_test` manifest is frozen and hashed.
- [ ] `relation_holdout` manifest is frozen and hashed, or explicitly marked exploratory/unavailable.
- [ ] Split-disjointness tests pass.
- [ ] Unseen-combination tests for `composition_test` pass.
- [ ] No confirmatory interaction pair appears in calibration.
- [ ] Additive, ridge, bilinear, MLP, marginal-probe, shuffled-pair, shuffled-label and random-subspace baselines are specified.
- [ ] Probe capacities and hyperparameters are frozen or selected entirely inside `train` by nested resampling.
- [ ] MLP capacity and training budget are frozen.
- [ ] Bootstrap seed/count and primary metric are frozen.
- [ ] Gate thresholds match the preregistered protocol/amendment.
- [ ] Result schema records failed as well as passed gates.
- [ ] Raw model outputs/activations are stored with immutable manifest IDs.
- [ ] Gate 0 synthetic controls pass before model evidence is interpreted.
- [ ] A new protocol version will be created rather than editing thresholds after results are viewed.

Opening `composition_test` is permitted only after Gate 1 has been scored once and the implementation has been frozen. Gate 3–5 work is not authorized as a rescue path after a Gate 1 or Gate 2 kill result.
