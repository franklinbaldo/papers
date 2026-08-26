---
type: "Findings Record"
title: "Semantic Atlas — Gallery-Scale Gate v1 Results"
description: "Terminal result of the preregistered static gallery-size gate on 382 documents."
tags: [semantic-atlas, observation, embeddings, mknn, gallery-size]
timestamp: 2026-08-26T16:17:22-04:00
---

# Semantic Atlas — Gallery-Scale Gate v1 Results

## Terminal decision

**`static_shared_but_observer_specific_structure`**

The frozen static gate cleared. This result authorizes the narrow static Atlas paper; it does not authorize causal, chronological, dynamical, routing, steering, density, gap, hubness, or susceptibility claims.

## Frozen run

- source commit: `7674788808165019772d05631775c0dedde3c96a`;
- corpus: all 382 Markdown documents at that commit, exact first 1,200 characters;
- observers: `Qwen/Qwen3-Embedding-0.6B@97b0c61` and `sentence-transformers/all-MiniLM-L6-v2@1110a24`;
- gallery sizes: `32, 48, 72, 116, 176, 256, 382`;
- primary neighborhood: `k=5`;
- eight deterministic subsets below N=382 and one full-corpus replicate;
- 1,024 correspondence permutations per subset;
- same-observer reference: frozen Markdown-versus-format-elided operator.

The machine-readable protocol and result are `gallery_scale_v1.json` and `artifacts/gallery_scale_v1.json`. Raw and normalized embedding caches plus the decision figure are preserved under `artifacts/`.

## Primary curve

Values below are replicate medians; N=382 is the single full-corpus value.

| Gallery N | Cross-model raw mKNN@5 | Cross-model calibrated | Qwen format stability | MiniLM format stability |
| ---: | ---: | ---: | ---: | ---: |
| 32 | 0.5313 | 0.4024 | 0.7013 | 0.6999 |
| 48 | 0.4938 | 0.4073 | 0.6854 | 0.6936 |
| 72 | 0.4750 | 0.4202 | 0.7005 | 0.6723 |
| 116 | 0.4578 | 0.4235 | 0.6923 | 0.6658 |
| 176 | 0.4614 | 0.4394 | 0.7101 | 0.6527 |
| 256 | 0.4586 | 0.4434 | 0.7250 | 0.6487 |
| 382 | 0.4628 | 0.4528 | 0.7236 | 0.6437 |

Every cross-model permutation test attained the minimum possible plus-one p-value, `1/1025 = 0.0009756`.

## Gate accounting

| Registered condition | Threshold | Observed | Result |
| --- | ---: | ---: | :---: |
| Material full-gallery alignment | calibrated mKNN@5 >= 0.20 | 0.4528 | pass |
| Retention from N=116 to N=382 | >= 0.75 | 1.0693 | pass |
| Conservative stability control, N=176 | >= 0.50 | 0.6527 | pass |
| Conservative stability control, N=256 | >= 0.50 | 0.6487 | pass |
| Conservative stability control, N=382 | >= 0.50 | 0.6437 | pass |
| Gap below stability reference, N=176 | >= 0.10 | 0.2133 | pass |
| Gap below stability reference, N=256 | >= 0.10 | 0.2054 | pass |
| Gap below stability reference, N=382 | >= 0.10 | 0.1909 | pass |

The calibrated score increased from 0.4235 at the preregistered N=116 anchor to 0.4528 on the full gallery. The small-gallery-artifact kill condition did not fire. The same-observer control remained valid and the cross-model curve remained separated from both observer-specific format-stability curves at every registered tail point.

## Sensitivity at full gallery

| k | Raw mKNN | Calibrated mKNN | Null 95th percentile | Plus-one p |
| ---: | ---: | ---: | ---: | ---: |
| 3 | 0.4398 | 0.4324 | 0.0131 | 0.0009756 |
| 5 | 0.4628 | 0.4528 | 0.0183 | 0.0009756 |
| 10 | 0.4631 | 0.4458 | 0.0312 | 0.0009756 |

The qualitative result is unchanged across the two registered sensitivity neighborhoods.

## Claim boundary

The supported claim is:

> Across these two frozen embedding observers and this 382-document corpus, local semantic neighborhoods show substantial permutation-calibrated agreement that is stable over gallery size and remains materially below same-observer robustness to the frozen formatting perturbation.

The result does not establish a universal semantic geometry, identify a causal mechanism, validate chronology, or show that the observer-specific remainder forms discrete ontologies. Those are separate claims and require separately frozen experiments.
