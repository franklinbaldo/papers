---
type: "Findings Record"
title: "Semantic Atlas — Gallery-Scale Pilot Extension Results"
description: "Preserved result of the N=382 same-repository pilot extension; not the preregistered large-scale gate."
tags: [semantic-atlas, observation, embeddings, mknn, gallery-size]
timestamp: 2026-08-26T16:17:22-04:00
---

# Semantic Atlas — Gallery-Scale Pilot Extension Results

## Corrected disposition

**`pilot_extension_direction_preserved`**

The N=382 run did not execute the preregistered large-scale gate, which requires a post-release arXiv corpus and galleries reaching N=50,000–100,000. It therefore does not authorize the narrow static Atlas paper. PR #379 remains blocked.

The machine result originally emitted `static_shared_but_observer_specific_structure` under the N=382 manifest. That value remains preserved in the immutable JSON artifact as the literal output of that runner, but it is not the program-level gate decision. Its valid scope is: the N=116 pilot direction persisted through a same-repository extension to N=382.

## Input-unit limitation

Both observers received the same first 1,200 Unicode characters. The run did **not** enforce a common no-truncation token window, however. MiniLM can truncate an excerpt that Qwen reads in full. The resulting content-window confound applies to the cross-model estimates and to the gaps against the same-observer formatting controls.

The large-scale protocol removes this confound: its unit is the full normalized arXiv abstract, eligible only when the pinned MiniLM tokenizer reports at most 256 tokens including special tokens, and runtime truncation is forbidden for both observers.

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

## Within-run manifest accounting

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

The calibrated score increased from 0.4235 at the N=116 anchor to 0.4528 on the N=382 gallery. The within-run thresholds passed. This is evidence about the pilot extension only; a collapse between 10,000 and 100,000 remains compatible with these observations.

## Sensitivity at full gallery

| k | Raw mKNN | Calibrated mKNN | Null 95th percentile | Plus-one p |
| ---: | ---: | ---: | ---: | ---: |
| 3 | 0.4398 | 0.4324 | 0.0131 | 0.0009756 |
| 5 | 0.4628 | 0.4528 | 0.0183 | 0.0009756 |
| 10 | 0.4631 | 0.4458 | 0.0312 | 0.0009756 |

The qualitative result is unchanged across the two registered sensitivity neighborhoods.

## Claim boundary

The supported claim is:

> Across these two frozen embedding observers and this 382-document same-repository corpus, local semantic neighborhoods show substantial permutation-calibrated agreement from N=116 through N=382 and remain below same-observer robustness to the frozen formatting perturbation.

The result does not establish scale robustness, release a static paper, establish a universal semantic geometry, identify a causal mechanism, validate chronology, or show that the observer-specific remainder forms discrete ontologies. Those are separate claims and require the frozen large-corpus experiment.
