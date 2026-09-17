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

## 9. From map construction to inference

Once the torus has been learned between a cheap space `E_c` and a richer space `E_r`, inference need not execute `E_r` immediately.

For a new object `x`, generate a small cheap-space probe trajectory

\[
Q_c(x)=\{E_c(P_1(x)),\ldots,E_c(P_k(x))\}.
\]

Use it to localize the most probable torus region:

\[
p(r\mid Q_c(x)).
\]

If uncertainty remains high, choose another probe adaptively. Once localized, use the learned local deformation to project toward the richer side.

Two levels of recovery are possible:

1. **Rich observables:** predict target-space distances, neighbors, response fields, relevance, or other downstream quantities without reconstructing the raw vector.
2. **Synthetic rich embedding:** estimate `\hat E_r(x)` sufficiently well to reuse models trained on the expensive representation.

The central downstream test is therefore not merely vector reconstruction. It is:

> Does cheap-space probing plus torus localization recover enough of the rich representation to improve prediction over the cheap representation alone?

Evaluation should compare `cheap`, `cheap + atlas`, `synthetic rich`, and `real rich`, while measuring performance as a function of the number of cheap probes required.

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

## 13. Immediate evaluation ladder

1. replicate torus/lens, active selection, and context-lens effects across seeds and real corpora;
2. add explicit left-to-right/right-to-left text traversal and quantify directional asymmetry;
3. implement repeated forward/reverse cycles and measure information gain to saturation;
4. extend directed occlusion to 2-D and 3-D domains and test semantic tomography;
5. replace Fourier ridge with an explicit smooth local deformation field and compare with linear alignment, relative representations, and registration baselines;
6. implement torus localization at inference time from a small cheap-space trajectory;
7. test synthetic-rich observables and synthetic-rich embeddings on downstream prediction;
8. test whether maps learned between earlier spaces reduce probes needed to characterize a new space;
9. add spectral rendering and multimodal sensory channels;
10. only then compare ordinary controllers with MaleCNS and connectome nulls.

The strongest useful result need not be a globally superior alignment algorithm. A system that reaches useful rich-space predictive quality with substantially fewer expensive observations, carries local uncertainty, or predicts unobserved scales/directions would already justify the cartographic formulation.

## 14. Reproducibility

Code and live findings are under:

- `experiments/pontifex_red1/`
- `experiments/pontifex_torus/`
- `.github/workflows/pontifex-torus-v0.yml`

The dated experimental narrative is in `experiments/pontifex_torus/FINDINGS-2026-09-17.md`.
