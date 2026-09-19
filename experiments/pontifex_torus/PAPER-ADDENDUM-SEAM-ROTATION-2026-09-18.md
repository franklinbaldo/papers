---
type: "Interpretability Paper"
title: "Pontifex Torus Addendum: Seam Rotation and Coordinate-Gauge Invariance"
description: "Discriminant tests separating toroidal probe coordinates from the stronger claim that raw text semantics are invariant to moving a circular seam."
tags: [pontifex, torus, occlusion, equivariance, seam, gauge, latent-space]
timestamp: 2026-09-18T01:24:00-04:00
---

# Pontifex Torus Addendum: Seam Rotation and Coordinate-Gauge Invariance

**Franklin Baldo**  
Independent Researcher

## Question

The dynamic double-occlusion experiment established the operational rule

\[
p(t+1)=(p(t)+1)\bmod N,
\]

but did not establish that the *semantic response field itself* is independent of where a circular seam is placed. This addendum separates two claims that can otherwise be conflated:

1. whether raw cyclic sequence rotation preserves intervention-response structure; and
2. whether the learned Torus chart is invariant to an arbitrary change of coordinate origin while the raw text and response field remain fixed.

The distinction is important. A torus may be useful as a periodic **coordinate substrate for probes** even when natural-language sequence semantics are not intrinsically circular. Moving the seam in raw text physically changes word order, whereas changing the phase origin of a coordinate chart need not.

## Experiment 1: raw seam rotation

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

## Results 1

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

## Interpretation 1

The result is mixed in a scientifically useful way.

First, **singleton occlusion response geography is strongly phase-aligned in both spaces**. Although cyclic raw-text rotation changes the whole-text embedding (mean cosine is below 1 in both encoders), the *shape* of the singleton response field follows the physical token positions: aligned Pearson is about `0.79` in both spaces, while the unaligned control is approximately zero. The aligned field beats the unaligned control on more than 98% of text/rotation cases in both encoders.

Second, **higher-order interaction equivariance is encoder-dependent**. BGE shows a strong pair-field result: aligned interaction Pearson `0.589` versus `-0.050` unaligned, with alignment winning on 92.9% of cases. MiniLM is much weaker: `0.386` versus `0.315`, and alignment wins on only 49.2% of cases. Therefore the current evidence does not support a universal claim that pair interactions simply rotate equivariantly with the raw-text seam.

Third, correlation should not be confused with metric invariance. The aligned NRMSE values remain large, especially for pair interactions. Cyclic rotation can preserve a substantial ordering/shape signal while changing response amplitudes materially.

The supported claim is consequently narrow:

> **Some intervention-indexed semantic geography survives cyclic seam movement, very strongly for singleton fields in both tested encoders and for BGE pair interactions, but raw text is not established as an intrinsically seam-free torus and MiniLM pair interactions fail the robust equivariance control.**

This is compatible with the current Pontifex formulation in which the torus is a computational substrate rather than a claim about the intrinsic topology of language.

## Experiment 2: coordinate-gauge invariance

Raw cyclic rotation changes linguistic order, so it conflates moving the Torus coordinate origin with changing the sequence presented to the encoder. The cleaner gauge test keeps **all response values, raw text, train/test split, and physical intervention states fixed** and changes only the phase origin used to label positions.

For phase shifts

\[
\alpha\in\{0,1/8,1/4,1/2,3/4\},
\]

the same fixed response field is fitted with three matched representations over ten held-out-text seeds:

1. **position agnostic** — invariant by construction, but cannot exploit position;
2. **Torus Fourier** — complete sine/cosine pairs with the existing local interaction terms;
3. **raw seam polynomial** — a deliberately non-periodic modulo-position basis with an arbitrary discontinuity at the chosen seam.

For every nonzero `alpha`, the model is retrained after relabeling both train and held-out coordinates by the same phase shift. Gauge invariance requires its physical predictions to remain unchanged.

## Results 2

The Torus Fourier representation is invariant to the coordinate-origin choice to floating-point precision:

| representation | mean prediction drift RMSE | mean normalized drift | max drift RMSE | held-out RMSE |
|---|---:|---:|---:|---:|
| position agnostic | 0 | 0 | 0 | 0.03862 |
| **Torus Fourier** | **1.18e-16** | **1.09e-15** | **2.35e-16** | **0.03241** |
| raw seam polynomial | 0.00798 | 0.07354 | 0.01365 | 0.03329 |

The raw-coordinate control exposes a strong arbitrary-seam effect. Its mean prediction drift is `0.000353` at an eighth-turn, `0.00913` at a quarter-turn, `0.00927` at a half-turn, and `0.01316` at three-quarters of a turn. The Torus prediction is unchanged at every tested phase apart from numerical roundoff; held-out RMSE (`0.03241`) and neighbor overlap (`0.25243`) are identical across phase origins.

Run: `https://github.com/franklinbaldo/papers/actions/runs/35314063702`  
Artifact: `pontifex-alignment-benchmark` (Actions artifact id `10534343265`).  
Implementation: `experiments/pontifex_torus/gauge_invariance.py`.

## Interpretation 2

This result closes the narrower coordinate question raised by the seam-rotation experiment. The current complete Fourier Torus basis plus isotropically regularized Ridge is **coordinate-gauge invariant** under a global phase-origin change. This is also the behavior expected mathematically: a global phase shift rotates each complete sine/cosine pair inside its span, while the Ridge penalty is isotropic in that feature subspace.

The position-agnostic control is exactly invariant too, which is why invariance alone is not evidence of useful semantic geometry. Its held-out RMSE is materially worse (`0.03862` versus `0.03241`). The useful result is the conjunction: the Torus basis exploits position while avoiding sensitivity to the arbitrary choice of phase zero.

The non-periodic raw-coordinate control is slightly worse in task RMSE (`0.03329`) and, more importantly for this discriminant, changes its physical predictions substantially when the arbitrary seam is moved. Thus the periodic representation removes a real coordinate artifact that the matched non-periodic representation retains.

This **does not** establish that language itself has circular topology. It validates a property of the chosen computational chart. It also does not establish multi-teacher Assembly, tokenizer-free inference, long-context scaling, or downstream retrieval value. Those remain separate empirical questions.

The combination of Experiments 1 and 2 sharpens the ontology:

> **Raw-text seam rotation is only partially equivariant and can materially change semantics; coordinate-gauge rotation of the Torus chart is exactly invariant. The torus is therefore presently supported as a seam-free computational coordinate system for intervention geography, not as a claim that text itself is a circle.**

## Evidence boundary

**Established in this addendum:** cyclic raw-sequence rotation experiment; strong singleton response-field alignment in both encoders; strong BGE pair-interaction alignment; weak/non-robust MiniLM pair-interaction alignment; coordinate-gauge invariance of the current complete Fourier Torus basis under global phase-origin changes; arbitrary-seam sensitivity of the matched raw polynomial coordinate control.

**Not established:** intrinsic circular topology of language; metric invariance of response amplitudes under raw sequence rotation; scalable multi-teacher Assembly; held-out-teacher generalization; tokenizer-free inference; long-context advantage; downstream retrieval advantage.

Implementations: `experiments/pontifex_torus/seam_rotation.py` and `experiments/pontifex_torus/gauge_invariance.py`.
