---
type: "Interpretability Paper"
title: "Pontifex Torus Addendum: Where the Regional Decoder Loses Information"
description: "A factorization ablation separates sparse-source transport, anchor-affinity coordinates, and the positive-simplex barycentric readout in the 2,000-text Torus reconstruction pipeline."
tags: [pontifex, torus, decoder, ablation, anchors, scaling, latent-space]
timestamp: 2026-09-18T04:15:00-04:00
---

# Pontifex Torus Addendum: Where the Regional Decoder Loses Information

**Franklin Baldo**  
Independent Researcher

## Question

The 2,000-text anchor-capacity sweep showed that increasing B-side anchors from 8 to
256 improves the current regional Torus decoder, but most of the relational gain
saturates near 32 anchors and the matched direct Fourier Ridge remains better. That
left three different explanations mixed together:

1. the sparse A-side response field may not predict B-side regional affinities well;
2. anchor-affinity coordinates may discard too much B-space information;
3. the current readout may be throwing away information by converting predicted
   affinities into a positive softmax simplex and barycentrically averaging anchors.

This experiment isolates those stages.

It uses only the existing synthetic cartography corpus. It does not use, tune on, or
reveal any future `D_assembly`, `D_student`, `D_val`, or `D_test` partition intended
for the multi-teacher downstream benchmark.

## Protocol

The corpus and observation budget are held fixed:

- 2,000 synthetic texts;
- ten seeds and the same 70/30 train/test protocol;
- one occlusion lens (`size=1`);
- `K=8` actual held-out A-side probes;
- `M=128` virtual integration positions;
- 8 Fourier harmonics on a 512-point dense training grid;
- anchor counts `16, 32, 128, 256`.

For each anchor count, the same anchor-affinity coordinate system is decoded four
ways.

### Predicted affinities, current readout

The deployable Torus path predicts B-anchor affinities from sparse A-side Fourier
features and then applies the current softmax barycentric readout:

\[
A_K(x)
\rightarrow
\widehat a_B(x)
\rightarrow
\operatorname{softmax}(\widehat a_B)
\rightarrow
\sum_j w_j c_j.
\]

### Predicted affinities, learned affine readout

The same predicted affinity vector is instead decoded with a learned signed affine
map:

\[
A_K(x)
\rightarrow
\widehat a_B(x)
\rightarrow
W\widehat a_B+b.
\]

This is a diagnostic control for the positivity/simplex constraint. It is not claimed
as a distinct geometric mechanism: because both stages are linear, their composition
can approach a direct linear regression from source features to B coordinates.

### Oracle affinities

Two oracle controls replace `\widehat a_B(x)` with the **true held-out B-to-anchor
cosine affinities**. One keeps the current softmax barycentric decoder; the other uses
the learned affine decoder. These are not deployable systems. They reveal how much
information is present in the regional affinity coordinates before source-to-region
transport error is introduced.

The matched direct Fourier Ridge sees the exact same sparse A-side source features and
remains the same-input control.

## Results

### 16 anchors

| readout | cosine | nRMSE | top-1 | neighbor overlap |
|---|---:|---:|---:|---:|
| predicted affinities + softmax barycentric | 0.79111 | 0.03298 | 0.0022 | 0.13148 |
| predicted affinities + learned affine | 0.84345 | 0.02855 | 0.0292 | 0.14896 |
| oracle affinities + softmax barycentric | 0.79679 | 0.03253 | 0.0035 | 0.37811 |
| oracle affinities + learned affine | **0.93953** | **0.01774** | **0.8145** | **0.48251** |
| matched direct Fourier Ridge | 0.84743 | 0.02819 | 0.0698 | 0.15392 |

### 32 anchors

| readout | cosine | nRMSE | top-1 | neighbor overlap |
|---|---:|---:|---:|---:|
| predicted affinities + softmax barycentric | 0.79616 | 0.03258 | 0.0022 | 0.13703 |
| predicted affinities + learned affine | **0.84794** | **0.02814** | 0.0483 | 0.15216 |
| oracle affinities + softmax barycentric | 0.80170 | 0.03214 | 0.0030 | 0.43728 |
| oracle affinities + learned affine | **0.97432** | **0.01156** | **0.9670** | **0.59871** |
| matched direct Fourier Ridge | 0.84743 | 0.02819 | **0.0698** | **0.15392** |

### 128 and 256 anchors

| anchors | predicted+softmax overlap | predicted+affine overlap | oracle+softmax overlap | oracle+affine overlap | direct Ridge overlap |
|---:|---:|---:|---:|---:|---:|
| 128 | 0.13688 | **0.15400** | 0.49757 | **0.75700** | 0.15392 |
| 256 | 0.13879 | 0.15391 | 0.51512 | **0.81950** | **0.15392** |

At 256 anchors, the oracle-affinity affine decoder reaches cosine `0.99218`, top-1
`0.9995`, and neighbor overlap `0.81950`. The same true affinities passed through the
softmax barycentric readout reach only cosine `0.80677`, top-1 `0.0030`, and overlap
`0.51512`.

Meanwhile, once predicted affinities receive the learned affine readout, their
coordinate and neighborhood metrics converge almost exactly to the matched direct
Fourier Ridge. At 128 anchors, predicted-affine overlap is `0.15400` versus `0.15392`
for direct Ridge; at 256 anchors it is `0.15391` versus `0.15392`.

## Interpretation

The experiment sharply localizes the current scale failure.

### 1. Anchor-affinity coordinates are not the main information bottleneck

The oracle-affinity affine result is extremely strong and improves systematically
with anchor count. Therefore a sufficiently rich set of B-anchor affinities contains
ample information to recover the held-out B embedding and its neighborhoods in this
synthetic setting.

This rejects the stronger hypothesis that regional affinity coordinates are
intrinsically too lossy for reconstruction.

### 2. The current softmax barycentric readout is a severe bottleneck

Even when given the **true** held-out B affinities, the current positive-simplex
readout has near-chance exact retrieval. Cosine similarities to anchors are being
treated as if they were calibrated mixture logits, and the subsequent positivity and
sum-to-one constraint removes information needed for coordinate reconstruction.

The earlier anchor-count plateau should therefore not be interpreted as evidence that
regional coordinates themselves saturate near 32 anchors. Much of that plateau was a
property of the readout.

### 3. After fixing the readout, sparse A-to-affinity transport becomes the remaining bottleneck

Predicted affinities decoded affinely nearly reproduce the direct Fourier Ridge
frontier, while oracle affinities are vastly better. The information gap is therefore
now localized primarily to

\[
\text{sparse A-side response field}
\rightarrow
\text{B-side affinity field},
\]

not to the existence of an anchor-affinity chart.

This is a much cleaner target for the next experiment: improve or enrich the
source-to-affinity transport while holding the regional coordinate system and decoder
fixed.

### 4. The affine diagnostic is not yet a Torus win

The learned affinity decoder is intentionally permissive. A linear
source-to-affinity map followed by a linear affinity-to-B map can collapse
algebraically toward direct Ridge. Matching direct Ridge therefore proves that the
regional bottleneck can be removed; it does **not** establish a unique geometric
advantage for Pontifex.

A scientifically useful next decoder should preserve explicit regional structure
without merely becoming an unconstrained direct coordinate regressor. Candidate
controls include calibrated signed/sparse prototype reconstruction, locally linear or
hierarchical charts, and neighborhood-preserving objectives selected only on
cartography/validation data.

## Evidence boundary

This experiment establishes a decomposition of failure for the current synthetic,
pairwise MiniLM-to-BGE setup:

- true anchor affinities retain substantial B-space information;
- the current softmax-positive-simplex barycentric readout destroys a large fraction
  of that information;
- a learned affine readout removes most of the observed decoder gap;
- once that gap is removed, prediction of affinities from sparse A-side observations
  is the principal remaining limitation.

It does **not** establish:

- a scalable multi-teacher Torus Assembly;
- teacher-order invariance;
- held-out-teacher generalization;
- a sparse student entering a frozen Assembly on disjoint data;
- tokenizer-free byte-level inference;
- long-context retrieval at fixed probe budget;
- an external downstream advantage;
- or superiority of a geometric decoder over direct regression.

Those remain separate hypotheses.

## Reproducibility

Implementation:

`experiments/pontifex_torus/regional_decoder_ablation.py`

Workflow:

`.github/workflows/pontifex-regional-decoder-ablation.yml`

Completed run:

`https://github.com/franklinbaldo/papers/actions/runs/35323048953`

Artifact:

`https://github.com/franklinbaldo/papers/actions/runs/35323048953/artifacts/10538030101`
