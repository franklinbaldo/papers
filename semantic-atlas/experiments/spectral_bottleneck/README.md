---
type: "Protocol"
title: "Semantic Atlas Spectral Bottleneck Smoke"
description: "Synthetic implementation check for the graph-Laplacian and Fiedler bottleneck pipeline proposed by the manifold-aware Semantic Atlas."
tags: [semantic-atlas, spectral-geometry, fiedler, conductance, smoke-test]
timestamp: 2026-08-17T02:10:00Z
---

# Semantic Atlas Spectral Bottleneck Smoke

This experiment is an **implementation/protocol check**, not evidence that language-model semantic states contain spectral bottlenecks.

It compares a planted two-lobe geometry connected by a moderate bridge against a continuous matched control. Graph construction and cut discovery are label-blind: a symmetric weighted kNN graph is built, the normalized graph Laplacian is diagonalized, and a balanced Fiedler sweep selects the candidate cut. Planted labels are revealed only afterward to score recovery.

The independent dynamic check is random-walk expected hitting time from the far-left quartile to the opposite half-space. The workflow repeats the comparison over five seeds and `k in {8, 12, 16}` and fails unless the bottleneck has lower conductance, smaller `lambda2`, high planted-cut recovery, higher crossing cost, and robustness across at least 80% of paired settings.

The GitHub Actions workflow is `.github/workflows/semantic-spectral-bottleneck.yml`. Results are emitted as `summary.json` and `summary.md` and uploaded as a workflow artifact.

The first repository run passed all five gates. The aggregate result was:

- median bottleneck/control conductance ratio: `0.0737`;
- median bottleneck/control `lambda2` ratio: `0.2170`;
- median planted-partition recovery: `0.9976`;
- median crossing hitting-time ratio: `6.8119`;
- robust paired fraction: `0.8667`.

These numbers validate the synthetic instrument only. The scientific M4 claim still requires frozen LLM-state data, preregistered graph construction, held-out navigation/control outcomes, and the density/randomization controls specified in `semantic_atlas_manifolds.md`.
