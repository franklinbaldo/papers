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

The emerging architecture is broader than pairwise translation. A **Torus Assembly** can be constructed from several teacher embedding spaces on a dedicated cartography corpus, frozen, and then used as a common latent target for a cheap sparse-probe student trained on a disjoint corpus. Final downstream evaluation must use a third, untouched test corpus. Inference may operate directly on raw bytes or characters rather than learned subword tokens, and may accumulate evidence from arbitrarily long finite inputs through a fixed number of local observations followed by dense virtual traversal of the learned continuous terrain. These assembly, tokenizer-free, and long-context extensions are proposals unless explicitly tied to completed experiments below.

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

### 7.1 Narrative phase symmetry and a Noether-style conservation hypothesis

The directed-occlusion construction admits a sharper interpretation when the traversal coordinate is treated as **narrative phase** rather than merely token position. Let

\[
\theta\in S^1
\]

parameterize the complete beginning-to-end traversal, with the seam identifying the end of one cycle with the beginning of the next. For a bilateral occlusion, let

\[
\Phi(\theta)=\big(\phi_L(\theta),\phi_R(\theta)\big)
\]

denote the latent responses associated with the material on the two sides of the moving lens.

The candidate continuous symmetry is a change of the arbitrary phase origin,

\[
\theta\mapsto\theta+\varepsilon.
\]

The scientific hypothesis is **not** that embeddings themselves remain constant under this translation. Local responses are expected to change. The stronger and testable claim is that there may exist an action

\[
S[\Phi]
=
\oint
\mathcal L\!\left(
\Phi,
\partial_\theta\Phi
\right)
\,d\theta
\]

whose value is invariant to the arbitrary choice of the traversal origin:

\[
S[\Phi(\theta+\varepsilon)]
=
S[\Phi(\theta)].
\]

Only under such an explicitly specified variational model would Noether's theorem apply in its classical sense. If the phase-translation symmetry holds, the corresponding Noether current is a candidate **semantic current** along the narrative trajectory. In a generic first-order formulation,

\[
J_\theta
=
\sum_a
\frac{\partial\mathcal L}
     {\partial(\partial_\theta\phi_a)}
\partial_\theta\phi_a
-
\mathcal L,
\qquad
a\in\{L,R\},
\]

and the idealized conservation statement is

\[
\partial_\theta J_\theta=0.
\]

The bilateral structure suggests an even more concrete empirical quantity. As the occlusion moves, a small interval of the story leaves one side of the lens and enters the other. If some semantic charge is transported rather than created or destroyed by this boundary motion, then the local bilateral fluxes should be approximately antisymmetric:

\[
j_L(\theta)+j_R(\theta)\approx0.
\]

This motivates a **semantic flux conservation** test. The candidate invariant need not be the norm of an embedding; it can be any learned or predefined scalar functional

\[
Q(\phi_L,\phi_R)
\]

whose variance across phase is anomalously small relative to matched controls. The empirical problem is therefore to search for a simple \(Q\), or a restricted Lagrangian family, such that conservation generalizes across unseen texts, encoders, lens sizes, and seam rotations.

The torus adds a global closure condition. Because

\[
\theta=0\equiv2\pi,
\]

a conserved local current can also be integrated around a complete narrative cycle:

\[
\mathcal C
=
\oint J_\theta\,d\theta.
\]

A non-trivial, reproducible circulation would be a topological summary of the whole traversal, but it must not be interpreted as a conserved Noether charge merely because the path is closed. Local phase symmetry, conservation, and global circulation are separate hypotheses and require separate controls.

This formulation yields direct falsification tests:

1. **seam rotation:** change the arbitrary start/end cut while preserving the cyclic ordering;
2. **phase translation:** shift every occlusion coordinate by the same amount;
3. **bilateral swap:** exchange the two sides together with traversal reversal;
4. **semantic shuffle:** preserve the phase schedule but destroy correspondence between content and response;
5. **cross-text generalization:** fit the candidate invariant on one set of narratives and evaluate conservation error on untouched narratives.

The null is that any apparent conservation is explained by normalization, periodic Fourier features, smoothness, or the mechanics of the occlusion schedule. A Noether-style interpretation earns scientific weight only if an invariant survives these controls and if an explicit action with the claimed continuous symmetry predicts the observed conserved quantity.

A dependency-free Lean skeleton is maintained in
`formalizations/pontifex_torus/PontifexTorusNoether.lean`. It formalizes the exact structural claims that are already safe to prove — periodic closure, invariance to phase-origin translation when assumed, bilateral swap involution, and zero net current from antisymmetric bilateral flux. It deliberately does **not** formalize the classical analytic Noether theorem or assert that real embedding trajectories satisfy the symmetry; those remain mathematical and empirical obligations.

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

### 12.17 Simultaneous double occlusion: a semantic "double slit"

A first pairwise-intervention experiment applies two distinct size-1 occlusions
simultaneously. To avoid importing quantum-mechanical claims into a semantic model,
"interference" is defined operationally as the failure of scalar response
superposition:

\[
I_E(p,q)
=
R_E(p,q)-R_E(p)-R_E(q).
\]

Across 3,840 paired interventions from 120 texts, the interaction term is clearly
nonzero in both spaces, although it has different marginal structure:

- A mean interference: `-0.0597`, mean absolute `0.0618`;
- B mean interference: `+0.00692`, mean absolute `0.01985`;
- cross-space `I_A` vs `I_B`: Pearson `0.229`, Spearman `0.232`;
- raw B additive prediction `R_B(p)+R_B(q)` has RMSE `0.02682` against the true
  simultaneous B response.

The central held-out-text test asks whether observing the simultaneous perturbation in
A adds transferable information about B beyond the two individual A perturbations.

| A-side information used | mean B-joint RMSE | mean Pearson |
|---|---:|---:|
| two single responses | 0.03698 | 0.614 |
| singles + toroidal pair geometry | 0.03028 | 0.764 |
| singles + simultaneous A response | 0.03355 | 0.697 |
| **singles + simultaneous A response + toroidal pair geometry** | **0.02786** | **0.805** |

Thus the simultaneous A measurement improves on the matched singles+geometry control
by about 8% RMSE, and the full pair representation is the strongest tested
cross-space predictor. It approaches the error of the unfair target-space additive
reference (`0.02682`), which has direct access to the two true B singleton responses.

A separate test predicts B's non-additive residual itself. Using A's interference
plus pair geometry gives RMSE `0.02327` and Pearson `0.453`, versus RMSE
`0.02698` for the zero-interference null, about a 14% reduction in error. This
supports the existence of a transferable pair-interaction signal in this toy.

The result should **not** be described as quantum interference. Cosine-distance
responses are nonlinear quantities, so non-additivity is not surprising by itself.
The scientifically relevant result is narrower: the non-additive effect observed
under a simultaneous intervention in A contains held-out information about the
non-additive response in B that is not fully recoverable from the two singleton
responses alone.

Absolute pair separation does not explain the effect simply: correlation between
separation and `|I_A|` is only `0.040`, and with `|I_B|` is `-0.132`.
Future tests should map interaction as a two-dimensional function of midpoint and
separation and compare against non-periodic pair-coordinate controls.

### 12.17.1 Dynamic toroidal wraparound orbit

The static pair experiment was extended into the explicitly periodic motion required
by the Torus hypothesis. For each text and each available circular separation
`Delta`, two size-1 occlusions advance together by one raw intervention position:

\[
i(t+1)=(i(t)+1)\bmod N,
\qquad
j(t+1)=(j(t)+1)\bmod N.
\]

Thus the leading occlusion does not stop at the last position: on its next movement
it wraps immediately to position zero while the other occlusion continues modulo
`N`. Across 120 texts this generated 6,278 oriented orbit states.

A seam-continuity diagnostic compares the absolute step-to-step change in the
non-additive interaction residual at wrap transitions with ordinary non-wrap
transitions. The result is mixed:

| space | mean abs step at wrap | mean abs step away from wrap | pooled wrap/non-wrap ratio |
|---|---:|---:|---:|
| A / MiniLM | 0.04478 | 0.02789 | 1.606 |
| B / BGE | 0.02066 | 0.02471 | 0.836 |

In A, wrap transitions are substantially larger on average than ordinary steps; in B
they are slightly smaller. Looking only at the transition where the **leading**
occlusion wraps gives mean absolute changes of `0.02950` in A and `0.01731` in B.
The current evidence therefore does **not** support the strong claim that the learned
response itself is seam-free merely because the intervention coordinate is periodic.

A second held-out whole-text test predicts `I_B` using the same A-side scalar
interaction information while changing only the coordinate representation:

| features for predicting B interaction | overall RMSE | RMSE after leading occlusion wrapped | Pearson |
|---|---:|---:|---:|
| A-side scalar interaction only | 0.02436 | 0.02421 | 0.292 |
| + non-periodic raw/polynomial pair coordinates | **0.02311** | **0.02142** | **0.420** |
| + periodic toroidal pair coordinates | 0.02370 | 0.02262 | 0.365 |

The periodic representation loses `0.00059` RMSE overall to the matched raw-coordinate
control and `0.00120` on states after the leading occlusion has wrapped. This is useful
negative evidence: **correct toroidal motion is a structural rule of the intervention
process, but the current circular feature basis has not yet earned a predictive
advantage for pair interactions.**

A cleaner next test is seam-rotation equivariance: move phase zero to several arbitrary
positions while keeping the same physical pair states, and require predictions not to
depend on that arbitrary coordinate choice.

Completed run:
`https://github.com/franklinbaldo/papers/actions/runs/35306211464`.

### 12.18 First scale ladder: fixed regional capacity does not scale automatically

A one-lens scale ladder increased the same synthetic grammar from 120 texts to
500, 1,000, and 2,000 texts while keeping the current regional reconstruction
capacity fixed at 16 B-side anchors. The experiment intentionally held the
representation and hyperparameters constant so that corpus scale, rather than a
capacity retune, changed.

For eight real probes and saturated virtual integration:

| corpus texts | Torus neighbor overlap (K=8, M=128) | direct Fourier Ridge neighbor overlap | Torus cosine | direct Ridge cosine |
|---:|---:|---:|---:|---:|
| 120 | **0.3539** | 0.3624 | 0.7957 | 0.8388 |
| 500 | 0.1855 | **0.2025** | 0.7904 | 0.8444 |
| 1,000 | 0.1558 | **0.1764** | 0.7900 | 0.8469 |
| 2,000 | 0.1315 | **0.1539** | 0.7911 | 0.8474 |

The absolute numbers are not directly comparable as retrieval accuracy because the
candidate set also grows, but the trend is adverse for the fixed 16-anchor regional
decoder: its relational advantage on the 120-text toy does not survive naive scale.
The direct coordinate baseline improves in cosine while the regional representation
becomes increasingly capacity constrained.

This is useful negative evidence. It argues against treating a fixed small set of
anchors as the final latent space. A scalable system must allow the semantic terrain
itself to grow in representational capacity — for example through more anchors,
hierarchical regions, learned prototypes, multiresolution charts, or the multi-teacher
Assembly proposed below. A required follow-up is therefore a capacity frontier
`anchors in {16,32,64,128,...}` at fixed corpus size and a corpus-size frontier at
matched capacity.

The scale run is
`https://github.com/franklinbaldo/papers/actions/runs/35297174362`, with separate
artifacts for 500, 1,000, and 2,000 texts.

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


## 14. Torus Assembly: a latent space assembled from multiple teachers

The pairwise experiments above should not be interpreted as requiring one designated
target encoder. A stronger architecture is to construct a new latent space
`Z_assembly` from several independently trained embedding spaces:

\[
E_1,E_2,\ldots,E_n
\quad\longrightarrow\quad
Z_{assembly}.
\]

The teachers need not share coordinates, dimensionality, tokenizer, context length,
or training objective. They are related through shared interventions and the
transport geometry learned from their response fields.

For a cartography text `x`, every teacher receives the same intervention family:

\[
\mathcal R_i(x,p,l,r,d).
\]

The Assembly is then updated sequentially:

\[
Z_1 \leftarrow E_1,
\]

\[
Z_{i+1}
\leftarrow
\operatorname{Fuse}(Z_i,E_{i+1}).
\]

The update should preserve useful geometry already acquired from previous teachers.
A generic objective is

\[
\mathcal L_i
=
\mathcal L_{new\ teacher}
+
\lambda\mathcal L_{preserve}
+
\mu\mathcal L_{geometry}.
\]

This is not intended to produce an arithmetic average of teacher embeddings. Each
teacher may be locally reliable in different semantic regions. Let
`rho_i(r)` denote the learned regional transport reliability of teacher `i`.
A conceptual local assembly rule is

\[
Z(r)
=
\frac{
\sum_i \rho_i(r)\,T_i(E_i,r)
}{
\sum_i \rho_i(r)
},
\]

where `T_i` transports teacher-local evidence into the common Assembly chart.

This makes the Assembly a **mixture of semantic geometries conditioned on terrain**.
One teacher may contribute more to retrieval-like neighborhoods, another to
multilingual structure, another to code, long documents, or another semantic
relation. The scientific question is whether the assembled terrain preserves
complementary structure that no one teacher preserves alone.

### 14.1 Sequential coupling and repeated cycles

The Assembly should not depend strongly on teacher order. A first implementation may
train sequentially

\[
E_1\to E_2\to E_3\to\cdots\to E_n,
\]

but the resulting space must be challenged by alternative permutations and repeated
cycles:

\[
E_1\to E_2\to\cdots\to E_n\to E_1\to\cdots.
\]

If different teacher orders converge to functionally similar Assembly geometries,
that is evidence that the method is discovering shared structure rather than merely
remembering an arbitrary sequence of transformations.

Required order controls include multiple random teacher permutations, forward versus
reverse order, and a jointly trained multi-teacher upper bound.

### 14.2 Held-out teacher test

A particularly strong sanity check is to leave one teacher entirely outside Assembly
construction:

\[
Z_{assembly}=Z(E_1,E_2,E_3)
\]

and ask, on previously unseen texts, whether `Z_assembly` predicts response geometry
or downstream neighborhoods of an unseen teacher `E_4`.

Success would not prove the existence of a universal latent space, but it would be
stronger evidence that the Assembly captures geometry shared across representation
systems rather than only memorizing pairwise translations.

## 15. Strict corpus separation: cartography, distillation, validation, test

For the central hypothesis to be meaningful, texts used to **create the latent
space** must be disjoint from texts used to train a cheap generator and from texts
used for final evaluation. The protocol therefore uses four partitions:

\[
D_{assembly}
\;\perp\;
D_{student}
\;\perp\;
D_{val}
\;\perp\;
D_{test}.
\]

### 15.1 Assembly corpus

Only `D_assembly` is used to construct and repeatedly refine the multi-teacher
terrain. The same texts are deliberately passed through all teachers because the
shared interventions provide cross-space correspondence:

\[
x\in D_{assembly}
\Rightarrow
\{E_i(x),\mathcal R_i(x)\}_{i=1}^n.
\]

After cartography and teacher-order training are complete, `Z_assembly` is frozen.

### 15.2 Student/distillation corpus

Texts in `D_student` never participated in Assembly construction. The frozen
Assembly and, when necessary, the expensive teachers produce target Assembly states

\[
z^*(x)\in Z_{assembly}.
\]

A cheap student then learns

\[
g_\theta(\text{sparse local observations of }x)
\to
\hat z(x).
\]

This separates two kinds of generalization:

1. can the Assembly represent texts it never saw while being constructed?;
2. can a cheap sparse-observation student learn to enter that frozen space?

### 15.3 Validation and final benchmark

`D_val` selects the probe budget, number of anchors/prototypes, harmonic bandwidth,
active-probe policy, pair-intervention policy, stopping threshold, and other
hyperparameters.

`D_test` is untouched until the final benchmark. It must not be used to choose
teachers, teacher order, latent capacity, probe locations, or architectural variants.

The final pipeline is therefore:

\[
D_{assembly}
\to
Z_{assembly}\;\text{(freeze)}
\]

\[
D_{student}
\to
g_\theta\;\text{(distill)}
\]

\[
D_{val}
\to
\text{choose protocol}
\]

\[
D_{test}
\to
\text{one-shot external task evaluation}.
\]

A benchmark result is scientifically useful only if the final test text has never
appeared in either Assembly construction or student training.

## 16. Multi-occlusion dynamics live on a torus, not on a bounded line

For simultaneous occlusions, periodicity is part of the operational definition.
With a text represented by `N` intervention positions, each occlusion advances by

\[
p_j(t+1)
=
(p_j(t)+v_j)\bmod N.
\]

Therefore an occlusion at the final position does not stop, reflect, or disappear.
On the next movement it reappears at the first position:

\[
N-1\to0\to1\to2\to\cdots.
\]

For two occlusions,

\[
(p_1,p_2)\in S^1\times S^1=T^2.
\]

For `k` simultaneous occlusions, the joint intervention state lies on

\[
T^k=(S^1)^k.
\]

### 16.1 Double-occlusion orbit

When two occlusions move at the same velocity with fixed circular separation
`Delta`,

\[
p_2(t)
=
p_1(t)+\Delta
\pmod N.
\]

The pair traces a closed diagonal orbit in `T^2`. A convenient coordinate system is
the circular midpoint `m` and separation `Delta`.

The previously measured pair-interaction residual

\[
I_E(p,q)
=
R_E(p,q)-R_E(p)-R_E(q)
\]

can therefore be promoted from a static set of sampled pairs to a periodic field

\[
I_E(\theta\mid\Delta)
\]

and, after varying separation,

\[
I_E(\theta,\Delta).
\]

A completed follow-up now moves both occlusions through complete orbits including the
wraparound transition at the end of the text. The intervention dynamics therefore
satisfy the toroidal rule operationally. However, the first held-out control does not
show a predictive advantage for the current periodic feature basis over matched raw
coordinates, and MiniLM interaction residuals remain more discontinuous at the natural
wrap seam. Section 12.17.1 reports this negative result. Periodicity is part of the
intervention contract; seamless semantic geometry remains an empirical question.

### 16.2 Higher-order interaction fields

The same construction extends beyond two interventions. A sparse hierarchy is

\[
Z(x)
=
Z_0
+
\sum_i\phi(p_i)
+
\sum_{i<j}\psi(p_i,p_j)
+
\sum_{i<j<k}\omega(p_i,p_j,p_k)
+\cdots.
\]

Exhaustive higher-order probing is combinatorially infeasible, so the practical
hypothesis is that learned reflectance/uncertainty and active cartography can identify
which pair or higher-order interactions are worth observing.

The phrase "double slit" remains only a mnemonic. Pair non-additivity in nonlinear
embedding responses is not evidence of quantum mechanics.

## 17. Tokenizer-free Torus embeddings

The Assembly architecture permits a stronger inference interface than conventional
subword embeddings: the cheap student need not share any teacher tokenizer.

"Tokenizer-free" here means **no learned lexical/subword tokenization such as BPE or
SentencePiece at inference**. The input still has a physical representation, such as
UTF-8 bytes or Unicode characters.

Represent a finite raw byte sequence as

\[
x=(b_1,\ldots,b_N)
\]

and normalize its position to phase

\[
\theta_i=2\pi i/N.
\]

An intervention becomes a window in raw sequence coordinates:

\[
O(x,\theta,w),
\]

where `w` may be defined in bytes, characters, or a relative fraction of the
object. The local cheap sensor

\[
s_i
=
f_{byte}(x[\theta_i-w:\theta_i+w])
\]

produces a probe signal without first converting the text into teacher subwords.

The full inference path is then

\[
\text{raw bytes}
\to
K\text{ local probes}
\to
G_x(\theta)
\to
M\text{ virtual traversal points}
\to
z(x)\in Z_{assembly}.
\]

The teachers may remain tokenized during Assembly construction. Their expensive
representations are distilled into the frozen geometry; the deployed student can be
byte- or character-level.

### 17.1 Arbitrarily long finite inputs

This creates a direct long-context hypothesis. Let `N` be raw input length,
`K` the number of actual local probes, and `w` local window width. If useful
quality can be maintained while `K\ll N`, expensive semantic observation cost is
closer to

\[
O(Kw)
\]

than to processing the entire object through a global transformer. Virtual traversal

\[
M\gg K
\]

can be arbitrarily fine computationally but, as the completed fixed-`K` experiments
show, cannot manufacture information after the inferred field is numerically
resolved.

The strong claim to test is therefore **not** that context is literally infinite.
It is:

> a fixed-dimensional Assembly embedding may be estimated for arbitrarily long
> finite raw inputs from a sparse number of local observations, with quality governed
> more by semantic/cartographic complexity than by raw sequence length.

The current response-field experiments do not yet establish this because they use a
full-text embedding as the reference from which occlusion distance is measured. A
genuinely tokenizer-free long-context implementation must replace that dependency
with local, recursive, or accumulated reference states that never require a teacher
to embed the full long document.

### 17.2 Domain-general consequence

If the student consumes raw bytes or another primitive sequence representation, text
becomes only one possible substrate. The same Assembly interface could in principle
receive code, DNA, serialized structured data, quantized audio, or other sequences
without defining a domain-specific learned tokenizer. This is a future extension,
not an empirical result.

## 18. Downstream target: specific long-document retrieval tasks

Reconstructing BGE coordinates is a diagnostic, not the intended endpoint. The
external benchmark should ask whether an Assembly embedding solves a concrete task.

The primary target should be a **long-document retrieval** task in which a query must
retrieve the correct long document or passage from a candidate corpus. Candidate
benchmarks include LongEmbed-style long-document retrieval tasks, with a synthetic
needle-retrieval task as a controlled length stress test and a real long-document
retrieval task as the primary downstream measure.

The central comparison is not merely "does Pontifex beat the strongest full encoder?"
but the Pareto frontier

\[
(\text{expensive observed bytes/tokens},\;
 \text{latency},\;
 \text{memory},\;
 \text{retrieval quality}).
\]

Required systems include:

1. the original teachers independently;
2. an expensive teacher ensemble;
3. a conventional direct teacher-to-teacher/student distillation baseline;
4. chunk-and-pool long-document embeddings;
5. a long-context embedding baseline;
6. the frozen Torus Assembly student at `K=1,2,4,8,16,32,64`;
7. the Assembly with active probing;
8. the Assembly with selected pair/double-occlusion probes.

For a fixed task metric such as nDCG@10 or Recall@k, report both quality and actual
observation cost. A result can be relevant even if the sparse Assembly is less
accurate than a full long-context teacher, provided it lies on a substantially
better cost/quality frontier.

Two scaling curves are especially important:

\[
K
\mapsto
\mathrm{RetrievalQuality},
\]

and

\[
N
\mapsto
\mathrm{RetrievalQuality}
\quad\text{at fixed }K.
\]

The second curve directly tests the long-context hypothesis. If quality remains
useful as raw document length grows while the number of actual probes is held fixed,
that is evidence that the Assembly is exploiting learned terrain rather than simply
re-encoding the entire document.

## 19. Immediate evaluation ladder

1. **capacity scaling:** repeat the 500/1k/2k corpus ladder with 16/32/64/128+ regional anchors or hierarchical prototypes to determine whether the current scale failure is a fixed-capacity bottleneck;
2. **seam-rotation control:** repeat complete double-occlusion orbits under multiple arbitrary phase-zero rotations and test whether pair-interaction prediction is equivariant to seam placement before attributing value to toroidal coordinates;
3. **pair-probe efficiency:** compare one simultaneous pair observation against two singleton observations at matched expensive-encoder cost;
4. **Assembly v0:** choose at least three heterogeneous teacher embedding spaces and build a frozen multi-teacher Assembly only on `D_assembly`;
5. **teacher-order control:** train several teacher permutations and quantify whether the resulting Assembly geometry/downstream behavior converges;
6. **held-out teacher:** exclude one teacher from Assembly construction and test prediction of its response geometry on unseen texts;
7. **student distillation:** train a sparse-probe student on a disjoint `D_student` to enter the frozen Assembly;
8. **raw-byte student:** replace teacher-token interventions at inference with byte/character windows and remove any requirement for a full-text reference embedding;
9. **long-input stress:** at fixed `K`, sweep raw input length over progressively longer documents and report quality versus actually observed bytes;
10. **specific downstream retrieval:** run a long-document retrieval benchmark with untouched `D_test`, comparing teachers, ensemble, direct distillation, chunk pooling, long-context encoders, and Torus Assembly;
11. **active sensing:** replace uniform probes with reflectance/uncertainty-guided singleton and pair interventions;
12. **functional reconstruction first:** prioritize retrieval, neighbor preservation, and downstream behavior over coordinate-identical reconstruction;
13. **only after these controls**, connect the continuous Assembly field to a dense sensory rendering/MaleCNS interface.

The central scientific target is now:

\[
\boxed{
\text{Can complementary knowledge from multiple latent spaces be distilled into a}
\atop
\text{frozen intervention-indexed geometry that new, arbitrarily long finite inputs}
\atop
\text{can enter using sparse tokenizer-free observations at a favorable cost/quality frontier?}
}
\]

A negative result at any stage is useful. In particular, failure under strict corpus
separation, teacher-order sensitivity, inability to generalize to a held-out teacher,
or degradation with input length at fixed probe budget would directly constrain the
theory.

## 19.1 Current evidence boundary

As of this revision:

**Completed evidence:** pairwise response-field alignment; scale/context lenses;
active k-center sampling; repeated-pass/backward-transfer toy results; inverse
regional reconstruction; learned regional reflectance; fixed-real-probe versus
virtual-resolution separation; static simultaneous-double-occlusion interaction;
complete dynamic double-occlusion orbits with explicit modulo wraparound (including
an adverse periodic-vs-raw coordinate control); and the 500/1k/2k fixed-capacity
scale ladder.

**Not yet established:** scalable multi-teacher Assembly; teacher-order invariance;
held-out-teacher generalization; a sparse student entering a frozen Assembly on
disjoint text; tokenizer-free byte-level inference; true long-context inference
without a full-text teacher reference; seam-rotation equivariance of the dynamic
multi-occlusion field; and any external long-document retrieval advantage.

## 20. Reproducibility

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
- `experiments/pontifex_torus/double_slit.py`
- `.github/workflows/pontifex-double-slit.yml`
- `.github/workflows/pontifex-scale-ladder.yml`
- `.github/workflows/pontifex-virtual-resolution.yml`
- `.github/workflows/pontifex-virtual-bandwidth.yml`
- `.github/workflows/pontifex-real-probe-frontier.yml`
- `.github/workflows/pontifex-inverse-backprojection.yml`
- `.github/workflows/pontifex-cycle-epistemics.yml`
- `.github/workflows/pontifex-terrain-reflectance.yml`

The dated experimental narrative is in `experiments/pontifex_torus/FINDINGS-2026-09-17.md`.


## Research programme position

- **Initiative:** Pontifex / Torus
- **Scope:** Periodic multiscale intervention cartography, transport, active acquisition, reconstruction, Assembly, tomography, and Torus-specific structural hypotheses.
- **Not claimed here:** Pontifex does not require Torus; Semantic Atlas static geometry, Semantic Observers, Perquire inversion, and the Interventional Latent Graph remain independent or upstream initiatives. Evidence for useful periodic coordinates is not evidence that semantic spaces are intrinsically topological tori.
- **Canonical map:** [Semantic Systems Research Map](research/semantic-systems-map.md)

Programme-wide relationships and current cross-project status are maintained in the canonical map rather than duplicated here. This living paper remains authoritative for Torus-specific hypotheses, experiments, positive results, adverse results, and limitations.
