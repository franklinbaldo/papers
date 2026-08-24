---
type: "Audit Report"
title: "Synergy–Geometry Prior-Art Boundary — 2026-08-24"
description: "Adversarial literature boundary for Gauge-Controlled Interaction Geometry, recording the claims already occupied and the narrower conjunction left for experiment."
tags: [interaction-geometry, synergy, prior-art, audit, semantic-atlas]
timestamp: 2026-08-24T01:22:00Z
---

# Synergy–Geometry Prior-Art Boundary — 2026-08-24

## Status

This audit freezes the novelty boundary used by `synergy_geometry.md` before any model-backed confirmatory run in `experiments/synergy_geometry`.

It is not a systematic review and does not establish absolute novelty. Its purpose is narrower: prevent the experiment from relabelling established ideas as a contribution if the early gates pass.

Literature cutoff: **2026-08-23**.

## Claims treated as occupied prior art

The following claims are **not** available as contributions of this programme:

1. semantic representations can be composed;
2. composition may be nonlinear or non-additive;
3. roles and fillers can be bound in distributed representations;
4. joint sources may contain target information unavailable from either source individually;
5. interaction terms require identifiability constraints relative to a distribution;
6. additive compositionality can be measured across transformer layers and held-out combinations;
7. semantic composition can be distributed across transformer depth and studied with causal interventions;
8. language models can contain low-dimensional, causally functional relational-binding geometry;
9. PID can diagnose modality synergy in modern multimodal language models, including layerwise and intervention-sensitive effects.

## Strongest direct collisions

### Functional interaction purification

Lengerich et al. (AISTATS 2020), *Purifying Interaction Effects with the Functional ANOVA*, identify the central decomposition problem directly: main and interaction effects are not separately interpretable without constraints because effects can be moved between terms while preserving the represented function. Their functional-ANOVA purification makes interaction explicitly distribution-relative.

Consequence: a raw residual such as `F(a,b) - F(a) - F(b)` is not a scientific contribution. The present programme must use a frozen design and identified interaction term.

Source: https://proceedings.mlr.press/v108/lengerich20a.html

### Target-relative information synergy

Williams & Beer (2010) introduced Partial Information Decomposition to separate redundant, unique, and synergistic information. Fang et al. (2026) apply PID to multimodal language models, including layerwise analysis and modality-shuffling interventions.

Consequence: the proposition that a target may become predictable only from sources jointly is occupied. PID synergy is an independent measurement axis, not the proposed novelty.

Sources:

- https://arxiv.org/abs/1004.2515
- https://arxiv.org/abs/2606.00959

### Additive compositionality in modern embeddings

Guo et al. (Findings of EMNLP 2025), *Quantifying Compositionality of Classic and State-of-the-Art Embeddings*, measure additive compositionality, reconstruct unseen attribute combinations, and track the signal across layers/training stages.

Consequence: failure or success of additive reconstruction is occupied territory. The present experiment matters only if the purified residual exposes function beyond the additive/non-additive diagnosis.

Source: https://aclanthology.org/2025.findings-emnlp.1206/

### Layerwise causal semantic composition

Aljaafari, Carvalho & Freitas (EACL 2026), *Where Do LLMs Compose Meaning?*, intervene on constituent representations across eight models and find composition distributed across depth. Their CoNLL 2026 follow-up uses causal tracing together with semantic-role structure to localize conceptual interpretation.

Consequence: a layerwise integration profile or causal localization of composition is not enough.

Sources:

- https://aclanthology.org/2026.eacl-long.214/
- https://aclanthology.org/2026.conll-main.44/

### Causal relational-binding geometry

Dai, Heinzerling & Inui (ACL 2026), *Cell-Based Representation of Relational Binding in Language Models*, is the closest mechanistic predecessor. It identifies a low-dimensional grid-like binding representation, reports cross-domain and two-model-family evidence, shows translation-based contextual transfer, and establishes causal relevance with activation patching.

Consequence: finding a low-dimensional relation subspace plus causal patching would not distinguish this programme. A positive result must survive the extra identification burden: purified marginal-vs-interaction decomposition, unseen compositions, nonlinear marginal baselines, non-circular cross-model calibration, and independently measured target synergy.

Source: https://aclanthology.org/2026.acl-long.2194/

## Surviving conjunction

The bounded search leaves one experimentally meaningful conjunction:

> **pure interaction geometry + held-out compositional generalization + selective causal efficacy + independently calibrated cross-model stability**, with **PID synergy measured separately rather than assumed**.

No inspected source was found to establish this exact conjunction as one identified object in language-model activations.

This is a bounded negative search result, not proof of novelty. If a semantically equivalent prior result is later found, the paper must narrow or surrender the novelty claim.

## Kill rule for novelty

Even if all experimental gates pass, the programme must be downgraded to replication/reframing if a prior work is found that already establishes the same conjunction under materially equivalent controls.

Scientific success therefore requires two independent conditions:

1. empirical gates pass prospectively;
2. the claim remains distinguishable after a refreshed literature audit at submission time.
