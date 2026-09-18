---
type: "Interpretability Paper"
title: "Pontifex Torus: Active Cartography Between Semantic Spaces by Multiscale Directed Occlusion"
description: "Living empirical extension of Pontifex: shared directed occlusions induce response fields, occlusion/context scales act as lenses, repeated bidirectional traversals refine a deformable periodic map between semantic spaces, and active cartography seeks useful inference before exhaustive traversal."
tags: [pontifex, torus, occlusion, latent-space, active-cartography, semantic-tomography, malecns]
timestamp: 2026-09-17T17:40:00-04:00
---

# Pontifex Torus: Active Cartography Between Semantic Spaces by Multiscale Directed Occlusion

**Franklin Baldo**  
Independent Researcher

> **Living empirical paper.** This manuscript records the empirical evolution of Pontifex. Early adverse results are preserved because they motivated the architectural pivot. Claims about directed tomography, repeated traversal, spectral rendering, and MaleCNS control remain hypotheses unless explicitly tied to completed experiments below.

## Abstract

The original Pontifex proposal used shared occlusions to collect scalar responses from multiple unaligned embedding spaces and trained a small convergence head over those responses. Initial experiments showed that simple learned fusion can help on real retrieval data, but the direct nonlinear convergence head was highly unstable across synthetic seeds, scale, and semantic-family diversity. This paper develops a more structured alternative. Instead of collapsing interventions immediately into a head, we treat their responses as a **multiscale, directed semantic terrain**. Two semantic spaces occupy the inner and outer halves of a deformable periodic substrate, called a torus. Position, occlusion size, context horizon, traversal direction, and eventually sensory rendering locate and characterize an intervention. The accumulated deformation of the substrate — not the exploring agent — is the candidate map between spaces.

Occlusion size and context size act as controllable lenses. Direction turns static saliency into a trajectory field. Forward and reverse traversals expose asymmetry, anisotropy, and possible hysteresis. Repeated traversals continue until marginal information gain saturates, giving an operational notion of how well a local route has been learned. In domains beyond text, directed occlusions generalize naturally to multiple spatial directions, yielding a form of **semantic tomography**. The learned map can then be used at inference time to localize a cheap-space trajectory on the torus and project it into a richer, more expensive semantic space without evaluating that richer encoder on every example.

Completed experiments now support three early components of this program. On 120 held-out synthetic texts, explicit occlusion scale reduces cross-space response prediction error, while a local periodic interaction basis reduces RMSE from `0.04031` to `0.03508`. Label-free k-center active cartography beats random sampling at every tested budget from 5% to 40%. A context-lens experiment shows that combining local responses from both spaces predicts the expensive space's full-context response much more accurately than using the cheap full-context response alone (`0.01461` versus `0.04599` RMSE). These are still toy results, but they justify moving from generic convergence heads toward intervention-indexed cartography.

## 1. Why Pontifex changed

The original Pontifex hypothesis was deliberately minimal: do not align embedding coordinates; instead, apply the same perturbations to multiple encoders and learn a convergence rule over within-space similarity signals. The first RED-1 run was encouraging enough to continue — median held-out AUPRC delta was about `+0.030` across three seeds — but the variance was very large.

Scaling made the weakness clearer. In the sample-scale smoke study, median delta was `-0.472`, `-0.453`, and `-0.364` at N=100, 300, and 1000 respectively. At N=1000, only one of five seeds was positive, although that seed was strongly positive (`+0.292`). Semantic-family diversity showed the same pattern: occasional positive interaction effects mixed with large negative runs.

A real-data control on SciFact gave a complementary result. Precomputed Cohere dense embeddings plus a lexical channel produced macro AUPRC `0.7047` for the best single channel and `0.7302` for learned linear fusion, a gain of about `+0.0254`. The simple mean was worse (`0.6024`), while the nonlinear MLP collapsed (`0.0093`). Cross-signal structure can matter, but a generic nonlinear head is not a stable scientific centerpiece.

The architectural pivot is therefore:

> **Preserve and interrogate the intervention geometry before learning how to combine it.**

## 2. Shared interventions define comparable geography

Let `E_A` and `E_B` be two embedding functions whose raw coordinates need not share a basis or even a dimension. For input `x`, intervention position `p`, occlusion size `l`, context horizon `r`, and traversal direction `d`, define

\[
P(x;p,l,r,d)
\]

and a within-space response such as

\[
R_A(x,p,l,r,d)=1-\cos(E_A(x_r),E_A(P(x;p,l,r,d))).
\]

The raw vectors are never compared coordinate by coordinate. The externally shared intervention coordinates provide correspondence, while each response is measured inside its own latent space.

The natural object is therefore not a saliency score but a response field:

\[
\mathcal R_E(p,l,r,d).
\]

For text, `d` is naturally left-to-right or right-to-left. For images, it may range over directions in the image plane; for 3-D structure, over directions on the sphere; for video, over spatial directions plus time; for audio, over paths through time-frequency space; for graphs, over topologically defined traversal directions.

This is related to representational-similarity analysis, manifold alignment, latent-space translation, relative representations, and diffeomorphic registration. The claim is not that latent-space mapping itself is new. The experimental question is whether **intervention-indexed, directed, multiscale geography** enables partial and actively sampled maps that would be hidden by immediate global alignment.

## 3. Why a torus

The torus is a computational substrate, not a claim about the intrinsic topology of embedding space.

The inner half represents semantic space A and the outer half semantic space B. Corresponding interventions occupy corresponding regions, while local metric, relief, and deformation may differ. The learned object is a deformation field `F` accumulated through repeated local updates:

\[
T_{n+1}=T_n+\Delta T_n.
\]

Convergence is not merely `||ΔT|| -> 0`; updates must become small while held-out mapping quality remains good. The final deformation, not the fly or controller, is the candidate semantic map.

A first implementation uses periodic Fourier coordinates and ridge regression rather than a literal 3-D mesh. This is intentionally cheap: geometry should earn its keep before adding a biologically elaborate controller.

## 4. Occlusion size as a semantic lens

For fixed position, varying occlusion size produces a family

\[
R_E(p,1),R_E(p,2),R_E(p,4),R_E(p,8),\ldots
\]

that helps localize an intervention's region. Small occlusions expose local relief; larger occlusions reveal broader structure. The map can learn how response changes with scale and use that relation as a lens.

A direct falsification test trains on sizes `1,2,8` and predicts size `4` on unseen texts. In the latest 120-text run, scale-aware prediction improves over a size-agnostic baseline (`0.04177` versus `0.04638` RMSE). The richer torus interaction model also improves over the agnostic baseline (`0.04269`) but does not beat the simpler lens on this interpolation test.

## 5. Context horizon as a second lens

Short contexts can provide local information about longer contexts. For horizons

\[
r_1<r_2<\cdots<r_k,
\]

we ask whether local responses reduce uncertainty about the full-context response.

The completed context-lens v0 experiment uses context widths 8, 12, and full. Predicting the expensive space B's full-context response gives:

| predictor | RMSE |
|---|---:|
| A full-context only | 0.04599 |
| A local-to-global | 0.04551 |
| B local-to-global | 0.01762 |
| A+B local cross-space signals | **0.01461** |

The cross-space local gain relative to A-full-only is `0.03138` RMSE. This is a large toy effect and directly supports the idea that local response trajectories can carry information about richer global states.

## 6. Direction, orientation, and semantic tomography

Static occlusion discards an important variable: the **sense of traversal**. Let

\[
\gamma_d(t)=E(P(x;t,d)).
\]

A route and its reverse visit related intervention coordinates but need not induce equivalent response trajectories. We therefore distinguish

\[
\gamma_{\rightarrow}
\quad\text{and}\quad
\gamma_{\leftarrow}.
\]

For text, these are the two natural directions. For image or 3-D data, a family `d in D` creates a bundle of trajectories

\[
\Gamma(x)=\{\gamma_d\}_{d\in D}.
\]

This motivates **directed occlusion tomography**: characterize a semantic region by probing it from multiple directions and scales, analogously to reconstructing structure from multiple projections.

A useful local signature becomes

\[
Q(r)=\big(\gamma_d,\gamma_{-d},D(\gamma_d,\gamma_{-d}^{-1})\big).
\]

The last term measures directional asymmetry. Two regions that appear similar in one direction may become distinguishable on the return path.

## 7. Bidirectional traversal, hysteresis, and repeated passes

A single traversal measures a route. A forward-and-back traversal also measures whether the region is reversible at the chosen scale.

If

\[
\gamma_{-d}=\gamma_d^{-1},
\]

the route is approximately reversible under the probe. If not, the difference may reflect anisotropy, history dependence, or hysteresis.

The protocol should therefore support repeated cycles:

\[
K_0\to\gamma_{\rightarrow}^{(1)}\to K_1
\to\gamma_{\leftarrow}^{(1)}\to K_2
\to\gamma_{\rightarrow}^{(2)}\to\cdots
\]

where `K_n` is the current knowledge state of the map. A second outward pass is not redundant: after the first return, uncertainty has changed, so the next traversal can change occlusion size, context horizon, direction, or sensory encoding specifically where ambiguity remains.

We define local saturation operationally by marginal information gain:

\[
\Delta I_n\to 0.
\]

A route is sufficiently characterized when another adaptively chosen traversal no longer reduces uncertainty materially. The number of passes to saturation,

\[
N_{sat}(r),
\]

becomes a property of the semantic geography itself.

## 8. Active cartography

An exhaustive response field is expensive. Once a partial map exists, the system should choose where to intervene next.

The completed active-cartography v0 control uses label-free k-center selection in torus feature space. Selection sees only the inner-space response and intervention coordinates; it never observes the outer-space target before choosing a point.

| observed training rows | active k-center RMSE | random RMSE mean | gain vs random |
|---:|---:|---:|---:|
| 5% | **0.03794** | 0.03839 | +0.00045 |
| 10% | **0.03618** | 0.03671 | +0.00053 |
| 20% | **0.03540** | 0.03590 | +0.00050 |
| 40% | **0.03524** | 0.03534 | +0.00010 |

The full-map torus RMSE is `0.03508`. Active sampling beats the mean of eight random draws at every tested budget. At 20% coverage it is already close to the full-map result.

This is the first direct evidence for the practical cartographic claim: useful cross-space geography can be recovered before exhaustive traversal.

The next policy should be stronger than k-center: choose among **forward, reverse, new direction, new scale, or new context** according to expected information gain.

## 9. From map construction to inverse reconstruction

Once the torus has been learned between a cheap space `E_c` and a richer space
`E_r`, inference need not collapse the entire learned field into a generic decoder.
The map itself can be traversed in the reverse observational direction.

For a new object `x`, choose an occlusion centered at position `p` with lens size
`l`. The local response observed in the cheap space provides a source signal

\[
L(x,p,l).
\]

Instead of asking a regressor to emit the rich embedding directly, inject that signal
at the center of the occlusion and propagate it through the learned geometry toward
candidate regions on the rich side of the torus. Let

\[
K_G(r\mid p,l)
\]

denote the propagation kernel induced by the saved geometry `G`: the contribution
that a source at intervention coordinate `(p,l)` makes to rich-side region `r`.
After one probe,

\[
\Delta A_r(p,l)
=
L(x,p,l)K_G(r\mid p,l).
\]

Walking the occlusion through the text accumulates evidence:

\[
A_r^{(k)}
=
\sum_{i=1}^{k}
L(x,p_i,l_i)K_G(r\mid p_i,l_i).
\]

The vector `A^{(k)}` is a progressively refined territorial estimate of where the
new text belongs in the rich semantic geography. In the simplest reconstruction,
rich-region anchors `c_r` can be combined barycentrically:

\[
\hat E_r^{(k)}
=
\frac{\sum_r A_r^{(k)}c_r}
     {\sum_r A_r^{(k)}}.
\]

More generally, `A^{(k)}` can drive retrieval, downstream prediction, or an inverse
optimization over the empirical rich-space manifold.

This formulation is intentionally close to an adjoint or backprojection operator.
Map construction measures how semantic regions project into intervention responses;
reconstruction reverses that direction by using observed intervention responses to
project evidence back onto semantic regions. The first implementation need not use
literal optics, radiometry, or a physical cavity: the required object is the
learned propagation operator induced by the geometry.

### 9.1 Reconstruction quality is a probe-budget curve

Exhaustively traversing every possible occlusion is unnecessary when only a coarse
estimate is needed. Let

\[
B = |P_B|
\]

be the maximum probe budget, where `P_B` is the subset of intervention positions
actually evaluated. Reconstruction becomes a progressive approximation:

\[
\hat E_r^{(1)},
\hat E_r^{(2)},
\ldots,
\hat E_r^{(B)}.
\]

The user or downstream system can therefore request a target quality/cost point
rather than a fixed exhaustive traversal.

Three probe policies are natural controls:

1. **uniform** — choose approximately equally spaced positions;
2. **coarse-to-fine** — begin with sparse coverage, then refine regions whose
   projected evidence remains ambiguous;
3. **active** — choose the next position/lens that maximizes expected reduction in
   reconstruction uncertainty.

For adaptive probing,

\[
(p^*,l^*)
=
\arg\max_{p,l}
\mathbb E[\Delta U(p,l)],
\]

where `U` is uncertainty over the current rich-side localization or reconstruction.

The central efficiency curves are therefore:

\[
k
\mapsto
\cos(\hat E_r^{(k)},E_r),
\]

\[
k
\mapsto
\mathrm{Retrieval}(\hat E_r^{(k)},E_r),
\]

and

\[
k
\mapsto
U_k.
\]

Useful thresholds such as

\[
N_{0.90}
=
\min\{k:\cos(\hat E_r^{(k)},E_r)\ge0.90\}
\]

or the number of probes required to recover the correct nearest neighbor become
more informative than a single full-budget score.

This provides the practical interpretation of "fast", "balanced", or "accurate"
reconstruction: these are simply different probe budgets or stopping criteria, not
different models.

### 9.2 Two reconstruction goals

The paper distinguishes two targets:

1. **absolute reconstruction** — approximate the original rich embedding coordinates;
2. **functional reconstruction** — preserve the rich space's neighbors, ranking,
   intervention responses, or downstream behavior even if the synthetic vector is
   not coordinate-identical to the original.

A synthetic rich embedding can therefore be useful even when its cosine similarity
to the original vector is imperfect, provided the functions that matter are
preserved.

### 9.3 Canonical torus, unit light, and learned reflectance

The reconstruction geometry needs a prior even before any terrain has been observed.
We define a **canonical simple torus** `T_0` whose transport law closes a complete
cycle by definition. A unit probe injected into `T_0` therefore has nominal return

\[
Q_{in}=1,
\qquad
Q_{return}^{(0)}=1.
\]

This is a geometric prior, not evidence that the cross-space terrain is already
known. Terrain is represented as learned deformation away from that prior:

\[
G_n=T_0+\Delta G_n.
\]

A first traversal supplies the first empirical constraint on `\Delta G`; later
traversals refine it. The important distinction is between **cycle closure** and
**knowledge of regional transport**. A trivial identity cycle can close perfectly
while carrying no useful information about the other semantic space.

For a region `r`, the operational quantity that can be learned from previous
traversals is its transport reliability. Let `e_n(r)` be out-of-sample transport
error estimated from earlier observations. Define

\[
\rho_n(r)=\exp(-e_n(r))
\]

as a normalized **reflectance**, and

\[
D_n(r)=1-\rho_n(r)
\]

as **darkness**. Brightness/darkness is therefore not a metaphysical statement that
information literally disappears. It is a learned property of how reliably the
current terrain transports information through that region.

This gives color a direct operational meaning:

- bright regions: previous traversals predict reliable transport;
- dark regions: previous traversals indicate high transport uncertainty/error;
- changing color after new traversals visualizes terrain becoming better known.

A separate cycle-residual quantity,

\[
C_n(x)=d(x,G_n^{-1}(G_n(x))),
\]

measures global non-closure. Experiments below show that `C_n` and `D_n(r)` are
related but should not be identified: cycle closure is useful as a global maturity
signal, whereas learned regional reflectance is the better local color variable.

## 10. Spectral rendering and color as a sensory channel

For an embodied MaleCNS version, geometry need not carry every variable. Different aspects of the response field can be rendered into distinct sensory channels.

A particularly natural visual channel is spectral composition. The fly should not be fed human RGB arbitrarily; a biologically aligned implementation can project semantic variables into Drosophila photoreceptor channels such as UV, blue, and green-sensitive pathways while controlling total intensity.

A possible decomposition is:

- terrain relief -> response magnitude;
- occlusion-scale derivative -> spectral composition;
- direction -> optic-flow orientation;
- local uncertainty -> contrast or modulation depth;
- recent trajectory/history -> spectral state or temporal modulation.

This allows the same location to look different depending on how the agent arrived there, making history available without storing it only in controller state. This is a hypothesis for future ablation, not a completed result.

## 11. Where MaleCNS enters — and where it does not

MaleCNS is optional. It is a candidate **local update and active-sensing operator** only after the geometry demonstrates value with conventional methods.

The embodied experiment imposes an external objective: maintain flight approximately equidistant from inner and outer surfaces. The fly receives a sensory rendering of the terrain. Descending activity controls local deformation of the substrate and potentially probe choice, rather than being asked to classify text directly.

The comparison must hold geometry, observation budget, and external objective fixed while changing the controller: direct gradient, linear/PID-like control, random recurrent reservoir, degree-preserving connectome null, and MaleCNS.

A MaleCNS advantage means better sample efficiency, held-out mapping, robustness, information gain per probe, or deformation cost.

## 12. Preliminary empirical status

### 12.1 Torus v0, 120-text replication

MiniLM (`all-MiniLM-L6-v2`) is the inner space and BGE-small (`bge-small-en-v1.5`) the outer space. 120 synthetic texts, eight positions per text, and sizes `1,2,4,8` produce 3,840 intervention rows with whole-text 70/30 holdout.

| condition | held-out RMSE |
|---|---:|
| size-agnostic periodic map | 0.04031 |
| + occlusion-size lens | 0.03841 |
| local torus interaction basis | **0.03508** |

The torus gain over the agnostic baseline is `0.00522` RMSE, about 13% relative.

### 12.2 Unseen occlusion scale

Training on sizes `1,2,8` and evaluating only size `4`:

| condition | RMSE |
|---|---:|
| size-agnostic | 0.04638 |
| scale lens | **0.04177** |
| torus interactions | 0.04269 |

### 12.3 Sample efficiency

With random training-row subsampling, torus RMSE is `0.03724` at 10% coverage and `0.03508` at full coverage. Active k-center improves this 10% result to `0.03618`.

### 12.4 Active cartography

Active k-center beats random mean at every tested budget from 5% to 40%, with the largest absolute gain near 10–20% coverage. This supports the hypothesis that the terrain contains recoverable structure and that probe choice matters.

### 12.5 Context lens

The strongest completed toy result is the local-to-global cross-space experiment: A+B local responses predict B full-context response at `0.01461` RMSE, versus `0.04599` from A full-context alone. This is not yet a real downstream task, but it directly motivates cheap-space localization followed by rich-space projection.

### 12.6 Infrastructure feasibility

A separate MS MARCO experiment opens the public 8.84-million-vector TCT-ColBERT FAISS index by mmap and extracts a deterministic 1,000-PID sample into a ~2.86 MB feature store without re-encoding. This establishes a route to large-scale tests while materializing only selected points.


### 12.7 Repeated exposure, accumulation, and return to an earlier text

A pass-count sweep over `1,2,4,8,16,32,64,128,256,500` repeated updates per
current text found a non-monotonic optimum. Across ten paired seeds, mean held-out
RMSE improved from `0.04534` at one pass to `0.03947` at 16 passes, a reduction
of about 13%. Performance then gradually degraded as the pass count increased,
although most checkpoints remained better than one pass. This shows that repeated
exposure is useful only up to a finite consolidation regime in the current online
learner.

A separate five-seed sequence applied 16 passes to T1, then to ten different texts
T2..T11 without resetting the shared geometry, and finally returned to T1 for another
16 passes. T1's mean RMSE improved from `0.05688` after its first exposure to
`0.04230` after learning T2..T11, despite T1 not being shown again. Returning to T1
reduced it further to `0.03305`. The ten intervening texts therefore produced
positive backward transfer in all five seeds; the final return specialized T1 further
but caused mild average interference with T2..T11.

These results motivate preserving geometry checkpoints and treating learning as a
search over reusable states rather than one irreversible trajectory.

### 12.8 Same-task semantic response-field alignment benchmark

A ten-seed benchmark compares Pontifex with alignment baselines on the same task:
predict the held-out BGE response field from the corresponding MiniLM response field.
Because text lengths induce slightly different raw occlusion coordinates, all methods
operate on response functions interpolated onto the same normalized position/lens
grid.

| method | mean held-out RMSE | text-neighbor overlap | learned/map state |
|---|---:|---:|---:|
| mean B | 0.03681 | 0.0995 | 256 B |
| Ridge profile map | **0.02999** | **0.2665** | 8,448 B |
| Orthogonal Procrustes | 0.04348 | 0.2463 | 8,704 B |
| CCA-8 | median 0.03197; numerically unstable mean | 0.2346 | 12,288 B |
| Relative representations + kNN | 0.03243 | 0.2149 | 36,352 B |
| **Pontifex Torus** | **0.03241** | **0.2524** | **88 B** |

Pontifex is not the best full-information aligner in this toy: Ridge has lower error
and slightly better neighborhood preservation. The current Torus result is instead a
compression result. Its response-field map is about 96x smaller than the Ridge map
while keeping RMSE within roughly 8%, and is essentially tied in RMSE with the
relative-representation baseline while using roughly 413x less map state.

This suggests that the more relevant comparison is the **B-observation budget
frontier**, not only the full-information endpoint.

### 12.9 Synthetic rich-embedding reconstruction

The next experiment asks whether a reconstructed response field can be inverted into
a usable original BGE embedding. It separates the two error sources:

\[
A\text{-field}
\rightarrow
\widehat{B\text{-field}}
\rightarrow
\hat E_B
\]

and also evaluates the oracle route

\[
B\text{-field true}
\rightarrow
\hat E_B.
\]

Four field-to-vector decoders were tested across ten seeds: Ridge, PLS, kNN
barycentric reconstruction, and anchor-similarity inversion. Important means are:

| route | cosine to true B | normalized RMSE | retrieval top-1 | neighbor overlap |
|---|---:|---:|---:|---:|
| raw MiniLM embedding -> BGE, Ridge | **0.9548** | **0.01533** | **99.4%** | **0.6111** |
| oracle B field -> BGE, PLS | 0.8374 | 0.02910 | 27.8% | 0.2717 |
| direct A field -> BGE, Ridge | 0.8316 | 0.02962 | 11.4% | 0.2741 |
| Ridge A->B field -> BGE, PLS | 0.8237 | 0.03030 | 6.7% | 0.2772 |
| Torus A->B field -> BGE, Ridge | 0.8088 | 0.03155 | 4.4% | 0.1913 |
| Torus A->B field -> BGE, PLS | 0.8067 | 0.03172 | 11.1% | 0.2781 |

The oracle control is decisive: even the **true** scalar B response field cannot yet
recover the original B embedding with high fidelity. Therefore decoder choice alone
cannot close the gap. The current field preserves useful functional geography but
discards information required for near-exact coordinate reconstruction.

This negative result motivates the inverse-propagation formulation in Section 9:
rather than flattening the field into a generic regression problem, reconstruct by
walking intervention probes and backprojecting their evidence through the learned
geometry. It also motivates richer observables — direction, context, anchor-relative
responses, additional lens scales, and actively selected probes — whose contribution
can be measured incrementally.



### 12.10 Canonical-torus cycle residual

A five-seed experiment tests whether A->B->A cycle non-closure can act as an
epistemic signal. The learned geometry is fit with increasing numbers of paired
texts (`4,8,16,32,64,84`). A shuffled A/B correspondence is used as a negative
control.

Under true correspondence, increasing terrain knowledge produces a clear aggregate
trend:

| paired training texts | mean cycle error | mean cycle darkness | B-field RMSE | embedding cosine error |
|---:|---:|---:|---:|---:|
| 4 | 0.0572 | 0.541 | 0.03433 | 0.255 |
| 8 | 0.0498 | 0.471 | 0.03362 | 0.278 |
| 16 | 0.0482 | 0.456 | 0.03358 | 0.247 |
| 32 | 0.0459 | 0.438 | 0.03300 | 0.208 |
| 64 | 0.0416 | 0.412 | 0.03239 | 0.199 |
| 84 | **0.0400** | **0.400** | **0.03235** | **0.195** |

At 84 training texts, shuffled correspondence produces substantially worse cycle
error (`0.0598`) and darkness (`0.515`) than true correspondence
(`0.0400`, `0.400`). Thus cycle closure does distinguish a learned geometry from
a deliberately wrong correspondence at the aggregate level.

However, instantaneous cycle residual is **not** a good local color map. Within a
fixed learned state, per-text cycle error has near-zero correlation with B-field
error, and local cycle-derived darkness can even be negatively correlated with local
B error. Therefore the naive rule "dark = local cycle did not close" is rejected.

The correct interpretation from this experiment is narrower: cycle non-closure is a
useful measure of overall geometric maturity, but not by itself a calibrated local
measure of terrain knowledge.

### 12.11 Learned regional reflectance from previous laps

A second experiment implements the stronger terrain interpretation: once a region
has been traversed, its color should summarize the transport reliability learned
from **previous laps**. Regional darkness is estimated from out-of-fold A->B
transport error on already observed texts, then evaluated against held-out regional
error.

This succeeds strongly. Under true correspondence:

| paired training texts | mean regional darkness | Pearson(darkness, held-out regional B error) | Spearman |
|---:|---:|---:|---:|
| 8 | 0.551 | 0.658 | 0.632 |
| 16 | 0.541 | 0.679 | 0.656 |
| 32 | 0.536 | 0.713 | 0.676 |
| 64 | 0.520 | 0.759 | 0.727 |
| 84 | **0.512** | **0.801** | **0.776** |

The regional color becomes **more predictive** as more terrain is learned. At 84
texts, the deliberately shuffled map remains substantially darker on average
(`0.625`) and has worse B-field error (`0.03640`) than the true map
(`0.512`, `0.03235`).

This is the first result supporting the proposed semantic use of color: a region's
darkness, when learned from prior transport experience, predicts where the map will
be less reliable on held-out data.

The same color does **not yet** provide a strong per-text confidence score. Weighting
regional darkness by a new text's A-side response yields only a weak correlation
with that text's B-field error (Pearson about `0.13` at 84 training texts), and is
not reliably correlated with embedding reconstruction error. Thus the present result
supports **regional epistemic color**, not yet a scalar confidence estimate for a
whole reconstructed text.

These two experiments establish an important separation:

\[
\text{cycle closure}
\neq
\text{regional reflectance}.
\]

Cycle closure tracks global map maturity. Learned reflectance from previous laps
provides the better local terrain-color variable.

### 12.12 Inverse light backprojection to a synthetic B embedding

The next experiment implements the proposed reconstruction path literally as a
regional inverse-propagation operator rather than a generic vector decoder:

\[
\text{occlusion center}
\rightarrow
\text{cheap-space light}
\rightarrow
K_G
\rightarrow
\text{B-side regional accumulation}
\rightarrow
\hat E_B.
\]

Sixteen representative B-embedding anchors define target semantic regions. The
learned cross-space object is a probe-to-region kernel `K_G`: selected occlusion
centers emit standardized cheap-space response light, the kernel transports those
deviations into B-region affinity space, regional evidence is accumulated, and the
synthetic B vector is produced only at the end by a barycentric combination of the
B anchors. No coefficient maps source probes directly to B embedding coordinates.

The experiment evaluates uniform walks with `1,2,4,8` occlusion centers. Two source
modes are tested: the smallest lens only, and all four available lens sizes at each
visited center. Ten paired seeds use the same 70/30 held-out split protocol.

| method | centers | scalar probes | cosine to B | normalized RMSE | retrieval top-1 | neighbor overlap |
|---|---:|---:|---:|---:|---:|---:|
| canonical regional prior | 0 | 0 | 0.7931 | 0.03283 | 2.78% | 0.0889 |
| backprojection, smallest lens | 8 | 8 | 0.7941 | 0.03274 | 2.78% | 0.1619 |
| backprojection, all lenses | 1 | 4 | 0.7935 | 0.03279 | 3.06% | 0.1892 |
| backprojection, all lenses | 4 | 16 | 0.7946 | 0.03271 | 3.33% | 0.2131 |
| backprojection, all lenses | 8 | 32 | **0.7974** | **0.03248** | **4.44%** | **0.3013** |
| direct A-profile -> B-embedding Ridge | 8 | 32 | **0.8316** | **0.02962** | **11.39%** | 0.2741 |

The result is mixed and therefore informative. The first inverse-backprojection
implementation does **not** beat unconstrained direct Ridge in absolute reconstruction:
its cosine similarity and exact held-out retrieval remain substantially worse.
However, the full-budget regional reconstruction preserves held-out B-space
neighborhood structure better than direct Ridge (`0.3013` versus `0.2741` mean
neighbor overlap). This difference has not yet been subjected to a paired
significance test and should not be treated as a confirmed win.

The probe-budget curve is weak in coordinate fidelity but clearer in relational
structure. Multiple lenses matter: the eight-center smallest-lens condition reaches
only `0.1619` neighbor overlap, while eight centers with all lenses reach
`0.3013`. Thus the current evidence is more compatible with the interpretation
that inverse propagation reconstructs **semantic geography** before it reconstructs
the original absolute vector coordinates.

Important limitations remain. The transport kernel is still a regularized linear
operator learned from paired data, the target regions are empirical B anchors, the
barycentric decoder restricts outputs to their span, and only eight normalized text
positions are available in the current cached field. The result therefore tests the
backprojection *architecture*, not a fully physical optical model.

### 12.13 One lens at 32 normalized positions

A targeted resolution ablation holds the occlusion lens fixed at `size=1` and
increases the positional representation from 8 to 32 normalized positions. The
dense source field first evaluates every discrete token-start position available in
each synthetic sentence, then interpolates that observed response function onto a
common 32-point phase grid. Therefore these are 32 normalized reconstruction
positions, not 32 independent encoder calls for short sentences.

At full budget:

| method | lens count | normalized positions | cosine to B | top-1 | neighbor overlap |
|---|---:|---:|---:|---:|---:|
| backprojection, previous 8-position field | 1 | 8 | 0.7941 | 2.78% | 0.1619 |
| backprojection, dense 32-position grid | 1 | 32 | **0.7977** | **4.17%** | **0.3623** |
| direct Ridge on same 32 scalar responses | 1 | 32 | **0.8304** | **9.72%** | 0.3131 |

The absolute-vector metrics improve only modestly, but relational reconstruction
changes substantially: neighbor overlap more than doubles relative to the earlier
one-lens/8-position condition and exceeds the direct Ridge control at the same
32-scalar representation (`0.3623` versus `0.3131`). This reinforces, but does
not yet prove, the hypothesis that positional traversal density is especially useful
for reconstructing semantic neighborhood geometry rather than exact coordinates.

The comparison is not a clean statement that "32 real probes beat 8 real probes":
the 32-point field is an interpolation of all available discrete token-start
responses in these short synthetic texts. A decisive follow-up requires genuinely
longer texts with at least 32 distinct raw occlusion centers and no interpolation.

### 12.14 Fixed real probes versus arbitrary virtual torus resolution

A stricter experiment separates **real observations** from **virtual traversal
resolution**. One lens (`size=1`) is used throughout. For held-out texts, only
`K` real A-side occlusion responses are revealed at actual token-start positions.
Those observations define a circular piecewise-linear source function. A continuous
Fourier transport kernel `K_G(theta,r)` is learned only from training texts.
Inference then integrates the same inferred source function through the learned
terrain using `M` virtual quadrature points.

Increasing `M` therefore reveals **no additional held-out encoder observations**.

With eight real probes fixed:

| virtual steps M | cosine to B | neighbor overlap |
|---:|---:|---:|
| 8 | 0.79531 | 0.29475 |
| 16 | 0.79568 | **0.35292** |
| 32 | 0.79569 | 0.35295 |
| 64 | 0.79569 | 0.35349 |
| 128 | 0.79569 | **0.35388** |
| 256 | 0.79569 | 0.35388 |
| 512 | 0.79569 | 0.35388 |

Thus virtual traversal density improves relational reconstruction substantially from
`M=8` to approximately `M=16`, while exact-vector cosine changes only slightly.
Beyond that point the integral converges and additional virtual steps do not create
new information.

The same qualitative pattern appears with fewer real probes. For `K=4`, neighbor
overlap rises from `0.1851` at `M=8` to `0.2582` at `M=16`, then remains
approximately flat. For `K=2`, it rises from `0.1374` to `0.1700`, then
plateaus/slightly declines.

This supports a more precise claim:

> The Torus permits arbitrarily fine **virtual traversal**, but reconstruction quality
> improves only until the learned continuous terrain is numerically resolved. Virtual
> steps refine integration; they do not manufacture new semantic observations.

### 12.15 Terrain bandwidth and the virtual-resolution plateau

A follow-up varies the Fourier bandwidth of the continuous terrain while keeping the
same held-out real probes. Harmonic counts `4,8,16,32` produce very similar
saturation behavior.

For `K=8` real probes, the best mean neighbor-overlap values are:

| harmonics | M=8 | M=16 | M=32 | M>=128 |
|---:|---:|---:|---:|---:|
| 4 | 0.3404 | 0.3467 | 0.3434 | 0.3447 |
| 8 | 0.2948 | 0.3529 | 0.3530 | 0.3539 |
| 16 | 0.2910 | 0.3567 | 0.3542 | 0.3555 |
| 32 | 0.2907 | **0.3630** | 0.3543 | 0.3556 |

Higher terrain bandwidth does not move the useful virtual-resolution frontier much
beyond `M≈16` in this toy. The strongest relational result is the 32-harmonic,
16-step condition (`0.3630` mean neighbor overlap). This argues against the naive
idea that simply increasing virtual resolution without bound should continually
increase reconstruction quality.

### 12.16 Real-probe frontier at saturated virtual resolution

Holding virtual resolution at a numerically saturated regime shows the complementary
effect: **real probes add information**.

At `M=128`, one-lens regional backprojection gives:

| real probes K | cosine to B | neighbor overlap |
|---:|---:|---:|
| 1 | 0.79305 | 0.1091 |
| 2 | 0.79309 | 0.1640 |
| 3 | 0.79395 | 0.2609 |
| 4 | 0.79392 | 0.2519 |
| 5 | 0.79397 | 0.2578 |
| 6 | 0.79466 | 0.2733 |
| 7 | 0.79455 | 0.2904 |
| 8 | **0.79569** | **0.3539** |

The curve is not perfectly monotonic because the current policy chooses approximately
uniform raw positions and different `K` values select different locations. The
overall trend is nevertheless clear: additional real observations change the
reconstruction frontier much more than adding virtual steps after quadrature
convergence.

The practical decomposition is therefore:

\[
\boxed{K = \text{observation / information budget}}
\]

\[
\boxed{M = \text{virtual integration resolution}}
\]

with `M` arbitrarily refinable in principle, but `K` controlling how much new
information enters the reconstruction.

## 13. Efficiency and continual-learning comparison protocol

The sequential shared-geometry experiments now create a direct comparison point with
online continual learning. The comparison must not use raw accuracy or RMSE numbers
across unrelated datasets. Instead, methods should be compared under a common stream
and normalized resource budget.

The closest established families are:

- **episodic-memory / replay methods**, including GEM and experience replay, which
  preserve or revisit earlier examples and explicitly measure backward transfer;
- **efficient rehearsal policies**, which optimize what to replay and how many update
  iterations to spend;
- **regularization methods** such as EWC, which protect prior knowledge without
  retaining a full replay buffer;
- **parameter-isolation / progressive methods**, which avoid forgetting by preserving
  old parameters and adding capacity;
- **test-time / online adaptation**, where repeated updates trade additional compute
  for adaptation quality.

These are not yet empirical competitors to Pontifex Torus because the published
benchmarks use different tasks and models. The immediate requirement is therefore to
run their simplest representative mechanisms on the **same Pontifex response-field
stream**.

### 13.1 Common-budget baselines

For a fixed stream of texts and a fixed validation/test split, compare:

1. **single-pass online SGD** — one update per text, no replay;
2. **fixed repeated SGD** — the current Pontifex protocol at 2/4/8/16/32/... passes;
3. **uniform replay** — retain previous text response rows and mix a fixed replay
   budget with the current text;
4. **best-checkpoint rollback** — save each geometry and restore the best
   validation geometry when a later update degrades it;
5. **adaptive-pass policy** — stop revisiting the current text when validation
   improvement or geometry change falls below a frozen threshold;
6. **EWC-like regularization** — penalize changes to parameters estimated as important
   to earlier texts;
7. **frozen-history / progressive control** — preserve previous geometry components
   and allocate new parameters to later texts;
8. **offline upper bound** — fit the same low-capacity model jointly on all available
   training response rows.

The first comparison should deliberately keep the same low-capacity torus feature
basis. This isolates the learning rule rather than confounding continual-learning
strategy with model size.

### 13.2 Efficiency ledger

Every run should report the following quantities:

| axis | metric |
|---|---|
| predictive quality | held-out RMSE and downstream task metric when available |
| retention | mean change on previously seen texts after learning a new text |
| backward transfer | performance change on an old text after learning later texts |
| forward transfer | performance on a new text before versus after prior texts |
| update cost | number of optimizer steps / partial-fit calls |
| sample exposure | total response rows consumed by updates |
| encoder cost | number of expensive encoder evaluations, reported separately from cached-field learning |
| wall time | cold-start and warm-cache runtime |
| trainable state | number of trainable parameters and bytes |
| replay memory | stored examples/response rows and bytes |
| geometry memory | number and total bytes of saved geometry checkpoints |
| efficiency | improvement per 1k row-exposures and per second |
| stability | variance across seeds and worst-seed regression |

The current torus learner has a particularly small trainable geometry: the v0
interaction basis has ten coefficients plus an intercept. For the sequential
T1..T11 protocol with 8 positions and four occlusion sizes, each text contributes
32 response rows. At 16 passes per text, eleven texts therefore produce 176
`partial_fit` calls and 5,632 row-exposures before the optional return to T1.
This accounting should be used instead of calling the method "cheap" qualitatively.

Encoder work must be amortized separately. Once the MiniLM/BGE response field is
materialized, pass-count, replay, rollback, and return experiments operate on the
same cached field and should not be charged repeated encoder inference. A cold run
and a warm-cache run must both be reported.

### 13.3 Backward-transfer result to compare

The first five-seed T1..T11 experiment already exposes a continual-learning metric.
After T1 received 16 passes, its mean RMSE was `0.05688`. After ten different texts
were learned, without showing T1 again, its mean RMSE was `0.04230`.
Expressed as an error-based backward-transfer score,

\[
BWT_{RMSE}=RMSE(T_1\text{ after first exposure})-
RMSE(T_1\text{ after later texts}),
\]

the mean is approximately `+0.01458`: positive backward transfer in all five seeds.
This is a toy result and must not be numerically compared with classification BWT
reported on MNIST, CIFAR, ImageNet, or language-model benchmarks. What is comparable
is the **sign, robustness, update budget, memory budget, and mechanism**.

Returning to T1 for another 16 passes yields additional specialization but also mild
average interference with T2..T11. That makes the stability-plasticity trade-off
directly measurable and creates a useful comparison against replay and
regularization methods.

### 13.4 External reference points

The benchmark should explicitly include these reference families:

- Lopez-Paz & Ranzato, **Gradient Episodic Memory for Continual Learning** (NeurIPS
  2017): finite episodic memory, forgetting metrics, and positive backward transfer.
- Davalas et al., **A rehearsal framework for computational efficiency in online
  continual learning** (Applied Intelligence, 2024): compares rehearsal schedules
  and emphasizes training-iteration count as computational cost; its ER-50 control
  illustrates that more repeated updates can improve accuracy while increasing cost
  and overfitting risk.
- Harun et al., **GRASP: A Rehearsal Policy for Efficient Online Continual Learning**
  (CoLLAs/PMLR, 2025): reports matching uniform-replay performance with fewer updates,
  making update efficiency a natural comparator.
- Online continual-learning empirical surveys and replay baselines such as MIR/GDumb
  should be used to avoid comparing only against elaborate methods.
- Test-time training/adaptation work should be treated as an adjacent comparison for
  repeated per-example updates, not as the same continual-learning problem.

The scientific target is not to show that Pontifex Torus beats methods trained on
unrelated benchmark tasks. It is to determine whether **saved shared geometry plus
selective revisitation** reaches an equivalent retention/generalization frontier
with fewer updates, less replay memory, or more positive backward transfer under the
same response-field stream.


## 14. Immediate evaluation ladder

1. implement inverse backprojection through the saved torus geometry rather than a generic field-to-vector decoder;
2. benchmark reconstruction as a function of probe budget `1,2,4,8,16,32,all`;
3. compare uniform, coarse-to-fine, and active probe selection at equal budgets;
4. cross occlusion-lens size with pass count and probe budget;
5. add explicit left-to-right/right-to-left traversal and test whether bidirectional evidence improves inversion;
6. add richer observable channels one at a time: context horizon, anchor-relative responses, additional lens scales, and inter-text probes;
7. compare absolute embedding reconstruction with functional reconstruction (retrieval, neighbors, downstream behavior);
8. run the same B-observation-budget frontier for Ridge, regularized CCA, Procrustes, relative representations, and Pontifex;
9. replicate the strongest effects on real corpora and larger encoder pairs;
10. only after the geometry/inversion mechanism earns its keep, add spectral rendering and compare ordinary controllers with MaleCNS/connectome nulls.

The strongest useful result need not be a globally superior alignment algorithm. A system that reaches useful rich-space predictive quality with substantially fewer expensive observations, carries local uncertainty, or predicts unobserved scales/directions would already justify the cartographic formulation.

## 15. Reproducibility

Code and live findings are under:

- `experiments/pontifex_red1/`
- `experiments/pontifex_torus/`
- `.github/workflows/pontifex-torus-v0.yml`
- `.github/workflows/pontifex-alignment-benchmark.yml`
- `.github/workflows/pontifex-embedding-reconstruction.yml`
- `experiments/pontifex_torus/alignment_benchmark.py`
- `experiments/pontifex_torus/embedding_reconstruction.py`
- `experiments/pontifex_torus/cycle_epistemics.py`
- `experiments/pontifex_torus/terrain_reflectance.py`
- `experiments/pontifex_torus/inverse_backprojection.py`
- `experiments/pontifex_torus/virtual_resolution.py`
- `.github/workflows/pontifex-virtual-resolution.yml`
- `.github/workflows/pontifex-virtual-bandwidth.yml`
- `.github/workflows/pontifex-real-probe-frontier.yml`
- `.github/workflows/pontifex-inverse-backprojection.yml`
- `.github/workflows/pontifex-cycle-epistemics.yml`
- `.github/workflows/pontifex-terrain-reflectance.yml`

The dated experimental narrative is in `experiments/pontifex_torus/FINDINGS-2026-09-17.md`.
