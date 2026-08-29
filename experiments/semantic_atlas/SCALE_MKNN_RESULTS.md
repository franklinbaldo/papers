---
type: "Findings Record"
title: "Semantic Atlas — Large-Scale Relational Geometry v1 Results"
description: "Terminal application of the preregistered 100k arXiv gallery gate."
tags: [semantic-atlas, observation, embeddings, mknn, arxiv, exact-knn, scale]
timestamp: 2026-08-29T07:47:08.221318+00:00
---

# Semantic Atlas — Large-Scale Relational Geometry v1 Results

## Terminal disposition

- scale gate: **`scale_stable`**;
- observer-specific gate: **`observer_specific_gap_survives`**;
- static paper released: **`true`**.

The preregistered static paper gate is released.

## Decision statistics

| Statistic | Value |
|---|---:|
| S(1,000) | 0.406546 |
| S(100,000) | 0.319519 |
| Retention R | 0.785935 |
| Cross-model C(100,000) | 0.319519 |
| Conservative ceiling U(100,000) | 0.928384 |
| Ceiling ratio Q | 0.344167 |

## Primary k=5 curve

| Gallery N | Calibrated mKNN median | 95% gallery interval | Qwen ceiling | MiniLM ceiling |
|---:|---:|---:|---:|---:|
| 1,000 | 0.4065 | [0.3934, 0.4176] | 0.9314 | 0.9339 |
| 2,500 | 0.3815 | [0.3692, 0.3915] | 0.9273 | 0.9280 |
| 5,000 | 0.3637 | [0.3558, 0.3691] | 0.9273 | 0.9284 |
| 10,000 | 0.3504 | [0.3464, 0.3557] | 0.9301 | 0.9299 |
| 25,000 | 0.3348 | [0.3326, 0.3366] | 0.9295 | 0.9288 |
| 50,000 | 0.3260 | [0.3245, 0.3280] | 0.9290 | 0.9290 |
| 100,000 | 0.3195 | [0.3190, 0.3202] | 0.9284 | 0.9289 |

## Frozen unit and controls

The unit is the full normalized arXiv abstract. Every included abstract has at most 256 WordPieces under the pinned MiniLM tokenizer and runtime truncation was forbidden, so both primary observers received the same semantic content. All neighbor sets are exact cosine kNN. The curve uses 32 preregistered stratified random galleries per N; chronological prefixes are descriptive only.

The prior Qwen 1024→384 dimensionality diagnostic remains secondary and post-hoc. It cannot change either terminal gate.
