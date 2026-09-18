---
type: "Interpretability Paper"
title: "Pontifex Torus Addendum: Seam-Rotation Equivariance of Occlusion Response Fields"
description: "A discriminant test separating toroidal probe coordinates from the stronger claim that raw text semantics are invariant to moving a circular seam."
tags: [pontifex, torus, occlusion, equivariance, seam, latent-space]
timestamp: 2026-09-18T01:24:00-04:00
---

# Pontifex Torus Addendum: Seam-Rotation Equivariance of Occlusion Response Fields

**Franklin Baldo**  
Independent Researcher

## Question

The dynamic double-occlusion experiment established the operational rule

\[
p(t+1)=(p(t)+1)\bmod N,
\]

but did not establish that the *semantic response field itself* is independent of where a circular seam is placed. This addendum tests a stronger claim directly.

The distinction is important. A torus may be useful as a periodic **coordinate substrate for probes** even when natural-language sequence semantics are not intrinsically circular. Moving the seam in raw text physically changes word order, whereas changing the phase origin of a coordinate chart need not.

## Experiment

The test uses the same 120-text synthetic cartography corpus as the current Pontifex Torus experiments. No downstream benchmark test set, Assembly test partition, or future student/test split is consumed.

For each text, the raw token sequence is cyclically left-rotated by approximately one quarter and one half of its length. MiniLM (`all-MiniLM-L6-v2`, space A) and BGE-small (`bge-small-en-v1.5`, space B) are evaluated on:

1. the original and cyclically rotated full text;
2. every size-1 singleton occlusion response;
3. a complete fixed-separation simultaneous-pair orbit;
4. the pair interaction residual

\[
I_E(i,j)=R_E(i,j)-R_E(i)-R_E(j).
\]

After rotating the raw sequence by `s`, the response field is re-aligned to the same physical tokens using the inverse circular coordinate shift. A seam-equivariant field should correlate more strongly after this alignment than under the intentionally unaligned control.

## Results

Across 240 rotation instances per encoder (two rotations for each of 120 texts):

| metric | MiniLM / A | BGE / B |
|---|---:|---:|
| full-text cosine, original vs cyclic rotation | 0.9519 | 0.9782 |
| singleton field, aligned Pearson | **0.7906** | **0.7895** |
| singleton field, unaligned Pearson | -0.0329 | -0.0266 |
| singleton alignment gain | **+0.8234** | **+0.8161** |
| singleton aligned beats unaligned | **98.3%** | **99.6%** |
| pair-interaction field, aligned Pearson | 0.3863 | **0.5889** |
| pair-interaction field, unaligned Pearson | 0.3150 | -0.0502 |
| interaction alignment gain | +0.0712 | **+0.6391** |
| interaction aligned beats unaligned | 49.2% | **92.9%** |
| singleton aligned NRMSE | 0.8387 | 0.7180 |
| interaction aligned NRMSE | 1.7044 | 1.0427 |

Run: `https://github.com/franklinbaldo/papers/actions/runs/35309939303`  
Artifact: `pontifex-seam-rotation` (Actions artifact id `10532768489`).

## Interpretation

The result is mixed in a scientifically useful way.

First, **singleton occlusion response geography is strongly phase-aligned in both spaces**. Although cyclic raw-text rotation changes the whole-text embedding (mean cosine is below 1 in both encoders), the *shape* of the singleton response field follows the physical token positions: aligned Pearson is about `0.79` in both spaces, while the unaligned control is approximately zero. The aligned field beats the unaligned control on more than 98% of text/rotation cases in both encoders.

Second, **higher-order interaction equivariance is encoder-dependent**. BGE shows a strong pair-field result: aligned interaction Pearson `0.589` versus `-0.050` unaligned, with alignment winning on 92.9% of cases. MiniLM is much weaker: `0.386` versus `0.315`, and alignment wins on only 49.2% of cases. Therefore the current evidence does not support a universal claim that pair interactions simply rotate equivariantly with the raw-text seam.

Third, correlation should not be confused with metric invariance. The aligned NRMSE values remain large, especially for pair interactions. Cyclic rotation can preserve a substantial ordering/shape signal while changing response amplitudes materially.

The supported claim is consequently narrow:

> **Some intervention-indexed semantic geography survives cyclic seam movement, very strongly for singleton fields in both tested encoders and for BGE pair interactions, but raw text is not established as an intrinsically seam-free torus and MiniLM pair interactions fail the robust equivariance control.**

This is compatible with the current Pontifex formulation in which the torus is a computational substrate rather than a claim about the intrinsic topology of language.

## Stronger next discriminant: coordinate-gauge invariance

Raw cyclic rotation changes linguistic order, so it conflates two operations:

1. moving the torus coordinate origin;
2. changing the text sequence presented to the encoder.

The cleaner next experiment must hold the raw text and all physical occlusion states fixed, change only the phase origin used by the learned Torus chart, and test whether predictions transform equivariantly. For an arbitrary chart shift `alpha`, the same physical state should satisfy

\[
\hat I_B(p,q;\alpha)
\approx
\hat I_B(p,q;0)
\]

after inverse coordinate alignment.

This should be evaluated on held-out whole texts and compared directly with a non-periodic raw-coordinate basis. A periodic Fourier/Torus representation earns its role only if it is less sensitive to this arbitrary chart origin than the matched non-periodic control.

## Evidence boundary

**Established in this addendum:** cyclic raw-sequence rotation experiment; strong singleton response-field alignment in both encoders; strong BGE pair-interaction alignment; weak/non-robust MiniLM pair-interaction alignment.

**Not established:** intrinsic circular topology of language; metric invariance of response amplitudes; coordinate-gauge invariance of the learned Torus map; multi-teacher Assembly; tokenizer-free inference; long-context advantage; downstream retrieval advantage.

Implementation: `experiments/pontifex_torus/seam_rotation.py`.
