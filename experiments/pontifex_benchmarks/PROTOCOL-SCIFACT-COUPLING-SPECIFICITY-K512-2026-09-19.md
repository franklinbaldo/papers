---
type: "Protocol"
title: "Pontifex SciFact coupling-specificity scaling diagnostic at K=512"
description: "Prospective follow-up testing whether correct residual-to-anchor correspondence becomes distinguishable from a shared scrambled warp at the larger K=512 budget where the two-sided interaction was strongest."
timestamp: 2026-09-19T11:25:00-04:00
tags: [pontifex, scifact, retrieval, coupling, null, transport, mechanism, scaling, leakage-audit]
---

# Pontifex SciFact coupling-specificity scaling diagnostic at K=512

## Status

**Prospective mechanism follow-up, not an independent confirmation.** The K=256 coupling-specificity result and the K=512 residual-side ablation are already known. This protocol is frozen after those observations and therefore asks only whether the mechanism separation changes at the larger supervision budget.

## Motivation

At K=256, the correct residual-to-anchor correspondence was not reliably better than a two-sided coupled scrambled warp, while coupled scrambling was reliably better than independent scrambling. At K=512, the separate residual-side ablation showed a larger positive two-sided interaction (`RR-RC-CR+CC = +0.044726`, paired-query 95% bootstrap interval `[+0.017208, +0.073570]`) but the full residual map still did not reliably beat Procrustes (`RR-CC = +0.003888`, interval `[-0.014190, +0.021739]`).

The discriminating question is therefore:

> Does increasing the unlabeled correspondence budget to K=512 make the **correct semantic residual assignment** distinguishable from a generic shared nonlinear warp, or does shared-warp coherence remain the dominant explanation?

## Frozen information boundary

Reuse the exact SciFact contract and manifests from the completed benchmark:

- `D_assembly`: dataset text/split membership plus frozen encoder identities; no relevance grades;
- `D_student`: deterministic 80% subset of exact-test-overlap-filtered SciFact train queries, using only unlabeled A/B representation pairs;
- `D_val`: remaining 20% of filtered train queries; B coordinates may be used only to select `tau`/`lambda`;
- `D_test`: official SciFact test qrels, unsealed only after the map and the complete null banks are frozen.

The script must reproduce the frozen student/validation/test/corpus manifests. Any mismatch is a protocol failure.

No B/MPNet coordinates may be encoded for SciFact test queries or corpus documents. Task-label budget for fitting and selection is zero.

## Fixed point and null bank

- K = `512` exactly;
- null bank = `63` coupled permutations and `63` independent document-side permutations;
- seed = `20260919`;
- `tau` and `lambda` are selected only by D_val coordinate loss using the same selector as the parent benchmark;
- every permutation is generated and hashed before D_test qrels are loaded.

Using 63 null draws gives a finite-bank upper-tail resolution of `1/64 = 0.015625` while keeping the run practical.

## Conditions

1. `TRUE`: correct residual-to-anchor assignment on both query and document sides;
2. `COUPLED-NULL`: one incorrect residual permutation applied identically to query and document sides;
3. `INDEPENDENT-NULL`: one incorrect permutation on the query side and a different incorrect permutation on the document side.

## Predeclared contrasts

### Semantic specificity

`TRUE - mean(COUPLED-NULL)` at the per-query level, with:

- global nDCG@10 difference;
- finite-bank upper-tail p-value against the 63 coupled-null global scores;
- paired-query bootstrap interval.

The K=512 run supports semantic specificity only if the paired-query 95% interval is strictly above zero **and** the finite-bank upper-tail p-value is <= 0.05.

### Shared-warp coherence

`mean(COUPLED-NULL) - mean(INDEPENDENT-NULL)` at the per-query level, with a paired-query bootstrap interval.

A positive interval supports shared-warp coherence even when the correct semantic assignment is destroyed.

## Interpretation rule

- If semantic specificity passes: record evidence that correct train-side A↔B residual correspondence contributes downstream SciFact utility at K=512 beyond a generic shared warp. This is a high-budget mechanism result, not evidence for low-budget transport or a physical torus.
- If semantic specificity fails while shared-warp coherence passes: strengthen the negative boundary around the current semantic-locality interpretation; the two-sided effect remains explainable largely by coherent deformation.
- If both fail: treat the earlier K=256 coherence result as non-robust across correspondence budget.

No result from this follow-up establishes universal transport superiority, native-B superiority, causal semantic locality, intrinsic toroidal topology, or a low-budget advantage.
