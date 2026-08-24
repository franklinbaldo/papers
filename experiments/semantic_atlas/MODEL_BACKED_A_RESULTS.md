---
type: "Findings Record"
title: "Semantic Atlas Experiment A — model-backed results (v1 and API replication)"
description: "Execution record for both frozen model-backed Experiment A manifests on the same corpus derivation: Qwen3-Embedding×MiniLM on GitHub Actions and a Gemini×Jina API replication, with the shuffled-correspondence gate passing in both pairings and moderate absolute held-out coordinate agreement."
tags: [semantic-atlas, findings, preregistration, embeddings, srf, replication]
timestamp: 2026-08-24T22:19:14Z
---

# Semantic Atlas Experiment A — model-backed results (v1 and API replication)

Both pre-registered manifests were executed end-to-end on 2026-08-24 against the
same frozen corpus derivation (`source_commit ff68b0653063e11e9cc3da887003bc0d46b14d26`,
`sha256(path)` ordering, 80 calibration / 24 held-out / 12 trajectory, SRF dim 64,
generator `Qwen/Qwen3-0.6B@c1899de`, seeds [11, 23]).

## Provenance

| | v1 (`model_backed_a_v1`) | v2 API (`model_backed_a_v2_api`) |
|---|---|---|
| Reference observer | `Qwen/Qwen3-Embedding-0.6B@97b0c61` (local weights) | `gemini-embedding-001` via Gemini API |
| Transfer observer | `all-MiniLM-L6-v2@1110a24` (local weights) | `jina-embeddings-v3` via Jina API |
| Generator | local `Qwen/Qwen3-0.6B@c1899de` | identical |
| Execution | GitHub Actions run [`32781573139`](https://github.com/franklinbaldo/papers/actions/runs/32781573139) on `07c1578` | local collection at 2026-08-24T22:19:14Z on `3258b2b` |
| Manifest sha256 | `49affa98…82b7f7b1` | `b9c1c219…f2b0fa1af425` |
| Artifact | `artifacts/model_backed_a_v1.json` | `artifacts/model_backed_a_v2_api.json` |
| API usage | — | 31 Gemini requests, 4 Jina requests |

## Metrics

| Metric | v1 (Qwen×MiniLM) | v2 (Gemini×Jina) | Chance baseline |
|---|---|---|---|
| heldout_coordinate_rmse | **0.1251** | 0.1320 | — |
| heldout_canonical_cosine | **0.4995** | 0.4425 | — |
| nearest_quasar_agreement | **0.1667** (4/24) | 0.125 (3/24) | 1/65 ≈ 0.0154 |
| shuffled_coordinate_rmse | 0.1773 | 0.1814 | — |
| **shuffled_worse_than_paired** | **True** ✅ | **True** ✅ | required by gate |
| atlas_coverage | 0.4375 | 0.3438 | — |
| transition_count | 21 | 13 | — |

## Reading against the pre-registered failure criteria

1. **Cross-model SRF (T1/negative control).** Paired calibration beats the
   shuffled-correspondence control in both observer pairings, and the control
   collapses in the predicted direction. The apparatus is measuring semantic
   anchoring, not noise. However, absolute held-out agreement is moderate:
   cosine ≈ 0.44–0.50 and nearest-quasar agreement ≈ 8–11× chance but far from
   stable. This is a partial positive, not full identifiability.
2. **Atlas hypothesis (T4).** Coverage 34–44% of cells with non-trivial
   transition counts indicates usable resolution without degenerating to one
   cell per state. Transition stability across seeds was observed but not yet
   summarized as overlap/Jaccard in these artifacts.
3. **Replication across independent vendor pairs.** The effect survives a complete
   change of observer pair (two open-weight checkpoints → two commercial APIs),
   which strengthens the claim that paired-Procrustes anchoring generalizes.

## Consequence for Experiment B (#267, MPC navigation)

Per `protocol_mpc.md`, Experiment B requires a usable frozen SRF + atlas and may
always run diagnostically. Both gates passed, so #267 may proceed on this
substrate. Given the moderate absolute T1 numbers, treat MPC results as
diagnostic unless route-completion gains appear alongside materially better
coordinate agreement than recorded here.

## Claim boundary

These artifacts test Experiment A only. They cannot support steering claims, and
a green execution is not by itself a positive scientific result beyond what the
metrics above support.