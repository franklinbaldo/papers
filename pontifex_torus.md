---
type: "Interpretability Paper"
title: "Pontifex Torus: Active Cartography Between Semantic Spaces by Multiscale Occlusion"
description: "Living empirical extension of Pontifex: shared occlusions induce response fields, occlusion/context scales act as lenses, and a deformable periodic substrate is learned between semantic spaces before optional connectome control."
tags: [pontifex, torus, occlusion, latent-space, active-cartography, malecns]
timestamp: 2026-09-17T17:40:00-04:00
---

# Pontifex Torus: Active Cartography Between Semantic Spaces by Multiscale Occlusion

**Franklin Baldo**  
Independent Researcher

> **Living empirical paper.** This manuscript records a new experimental direction
> that grew out of the original `pontifex.md` position paper. Early direct-head
> experiments are reported even when adverse because they explain the architectural
> pivot. Claims about the torus, active cartography, and connectome control remain
> hypotheses unless explicitly tied to a completed experiment below.

## Abstract

The original Pontifex proposal used shared occlusions to collect scalar responses
from multiple unaligned embedding spaces and trained a small convergence head over
those responses. Initial experiments showed that simple learned fusion can help on
real retrieval data, but the direct nonlinear convergence head was highly unstable
across synthetic seeds, scale, and semantic-family diversity. This paper explores a
more structured alternative. Instead of collapsing interventions immediately into a
head, we treat their responses as a **multiscale semantic terrain**. Two semantic
spaces occupy the inner and outer halves of a deformable periodic substrate, here
called a torus. Text position, occlusion size, and context horizon locate an
intervention on that substrate. The accumulated deformation of the substrate — not
the agent that explores it — is the candidate map between spaces. Occlusion size and
context size act as controllable lenses, allowing the system to predict unobserved
regions and select new interventions actively rather than exhaustively traversing a
space. A first cheap experiment, without a connectome, finds that adding occlusion
scale reduces held-out cross-space response prediction error and that a local
periodic interaction basis reduces RMSE by about 13.8% relative to a scale-agnostic
baseline on the initial smoke run. A held-out occlusion-size test also improves when
scale is represented explicitly. The next stages test active intervention selection,
local-to-global context transfer, smooth deformation fields, and finally whether
Drosophila MaleCNS descending activity is a useful operator for updating the field
under an externally imposed equidistant-flight objective.

## 1. Why Pontifex changed

The original Pontifex hypothesis was deliberately minimal: do not align embedding
coordinates; instead, apply the same perturbations to multiple encoders and learn a
convergence rule over within-space similarity signals. The first RED-1 run was
encouraging enough to continue — median held-out AUPRC delta was about `+0.030`
across three seeds — but the variance was very large.

Scaling made the weakness clearer. In the sample-scale smoke study, median delta was
`-0.472`, `-0.453`, and `-0.364` at N=100, 300, and 1000 respectively. At N=1000,
only one of five seeds was positive, although that seed was strongly positive
(`+0.292`). Semantic-family diversity showed the same pattern: occasional positive
interaction effects mixed with large negative runs. The conclusion is not that
shared interventions are useless. It is that a generic nonlinear head over a small
stack of scalar signals is too unconstrained to carry the central scientific claim.

A real-data control on SciFact gave a complementary result. Precomputed Cohere dense
embeddings plus a lexical channel produced macro AUPRC `0.7047` for the best single
channel and `0.7302` for learned linear fusion, a gain of about `+0.0254`. The simple
mean was worse (`0.6024`), while the nonlinear MLP collapsed (`0.0093`). This suggests
that cross-signal structure can matter while again warning against treating a
particular neural head as the contribution.

The architectural pivot is therefore: **preserve the intervention geometry before
learning how to combine it.**

## 2. Shared interventions define comparable geography

Let `E_A` and `E_B` be two embedding functions whose raw coordinates need not share
a basis or even a dimension. For input `x`, position `i`, occlusion size `l`, and
context horizon `r`, define an intervention `P(x; i, l, r)` and a within-space
response such as

\[
R_A(x,i,l,r)=1-\cos(E_A(x_r),E_A(P(x;i,l,r)))
\]

with an analogous `R_B`.

The raw vectors are not compared coordinate by coordinate. The intervention
coordinates `(x,i,l,r)` are shared externally, while each response is measured
inside its own space. Repeating interventions therefore induces response fields
whose points correspond because the intervention is the same, not because embedding
dimensions have been aligned.

This is related to representational-similarity analysis, manifold alignment, latent
space translation, relative representations, and diffeomorphic registration. The
claim here is not that mapping one latent space to another is new. The experimental
question is whether **intervention-indexed local geography** enables useful partial,
multiscale, and actively sampled maps that would be hidden by an immediate global
alignment or convergence head.

## 3. Why a torus

The torus is a computational substrate, not a claim about the intrinsic topology of
embedding space.

The inner half represents semantic space A and the outer half semantic space B.
Corresponding interventions occupy corresponding longitudinal regions, while the
local metric and relief on each half may differ. This captures an important
property: correspondence of samples does not imply preservation of distance.

The learned object is a deformation field `F`. Repeated local updates change the
substrate

\[
T_{n+1}=T_n+\Delta T_n,
\]

and convergence is approached when updates become small on both observed and
held-out interventions without loss of mapping quality. The final deformation,
not a fly or controller, is the candidate semantic map.

A first implementation does not construct a 3-D mesh. Normalized intervention
position is represented periodically by Fourier coordinates, and ridge regression
over local position/scale interactions is used as the cheapest smooth-deformation
surrogate. If even this representation fails, a biologically elaborate controller
would be premature.

## 4. Occlusion size as a semantic lens

Occlusion size is not treated as an incidental hyperparameter. For fixed text and
position, varying `l` creates a family of observations

\[
R_E(i,1), R_E(i,2), R_E(i,4), R_E(i,8), \ldots
\]

that helps localize the intervention's region of the response field. A map that has
learned how terrain changes under increasing or decreasing occlusion can use scale
as a **lens**: small occlusions reveal local relief; larger occlusions expose broader
semantic structure.

This yields a direct falsification test: train on sizes `1,2,8` and predict size `4`
on unseen texts. If explicit scale does not improve prediction over a size-agnostic
map, the lens hypothesis has little empirical content.

## 5. Context horizon as a second lens

A separate hypothesis is that short-context responses are easier to estimate and
carry information about longer-context responses. For context horizons

\[
r_1 < r_2 < \cdots < r_k,
\]

we ask whether observing `R_E(i,l,r_1)` reduces uncertainty about
`R_E(i,l,r_{k})`, including across different encoders.

This is stronger than ordinary pairwise alignment: it tests whether different
semantic spaces share aspects of a **local-to-global response law** because their
representations were learned from related structure in the same linguistic world.
The hypothesis is empirical; encoders may differ enough that transfer fails.

## 6. Active cartography

An exhaustive response field can be expensive. Once a partial map exists, the
system should choose where to intervene next. Candidate policies include random
sampling, uniform grids, uncertainty sampling, curvature sampling, and geometric
coverage.

The first active-cartography control uses label-free k-center selection in torus
feature space. It chooses points farthest from the observations already available
using only the inner-space response and intervention coordinates; it does not inspect
the outer-space target response before selecting a point. The relevant quantity is
mapping error as a function of the fraction of the response field actually measured.

If a useful map requires nearly 100% traversal, the proposed cartographic advantage
is weak. If performance approaches the full-map result after observing only a small
fraction, the map has practical predictive structure.

## 7. Where MaleCNS enters — and where it does not

MaleCNS is not required for Pontifex Torus to be useful. It is a candidate **update
operator** only after the geometric substrate demonstrates value with ordinary
optimizers.

The proposed embodied experiment imposes an external objective: maintain flight
approximately equidistant from the inner and outer surfaces. The fly receives a
literal sensory rendering of the current terrain. Descending activity controls
local deformation of the substrate rather than being asked directly to classify
text or emit an embedding. In the simplest form,

`terrain -> sensory channels -> frozen MaleCNS -> descending activity -> local warp`.

The comparison must hold the geometry, observation budget, and external equidistance
objective fixed while changing only the update controller: direct gradient, linear
controller, PID-like control, random recurrent reservoir, degree-preserving
connectome null, and MaleCNS.

A MaleCNS advantage would therefore mean better sample efficiency, held-out mapping,
robustness, or deformation cost — not merely that a fly can be inserted into the
pipeline.

## 8. Preliminary experiments

### 8.1 Torus v0 smoke

The first completed smoke uses MiniLM (`all-MiniLM-L6-v2`) as the inner space and
BGE-small (`bge-small-en-v1.5`) as the outer space. Eighty synthetic texts, six
positions per text, and occlusion sizes `1,2,4,8` produce 1,920 intervention rows.
Whole texts are held out 70/30.

| condition | held-out RMSE |
|---|---:|
| size-agnostic periodic map | 0.04032 |
| + occlusion-size lens | 0.03857 |
| local torus interaction basis | **0.03476** |

Relative to the size-agnostic map, explicit scale improves RMSE by roughly 4.3%, and
the local torus interaction basis by roughly 13.8%.

For the stronger unseen-scale test, training uses sizes `1,2,8` and evaluation uses
size `4` only:

| condition | unseen-size-4 RMSE |
|---|---:|
| size-agnostic | 0.04928 |
| scale lens | **0.04424** |
| torus interactions | 0.04594 |

The simpler lens generalizes best to the unobserved scale in this run. This is an
important constraint: richer local interactions should not be assumed to generalize
better merely because they fit the full response field better.

### 8.2 Early sample-efficiency signal

Using only 10% of training response-field rows, the torus condition obtains RMSE
`0.03602`; using all rows obtains `0.03476`. The size-agnostic condition at 10% is
`0.04195`. This motivates the active-selection study but is not yet evidence that an
active policy beats random sampling.

### 8.3 Infrastructure feasibility

A separate MS MARCO experiment opens the public 8.84-million-vector TCT-ColBERT
FAISS index by mmap and extracts a deterministic 1,000-PID sample into a ~2.86 MB
feature store without re-encoding. This establishes a path for testing the same
cartographic ideas over large public latent spaces while materializing only the
points needed by an experiment.

## 9. Immediate evaluation ladder

The current ladder is intentionally incremental:

1. replicate torus/lens effects with larger N and multiple splits;
2. compare random sampling with label-free active geometric coverage;
3. test short-context -> long-context transfer within and across spaces;
4. replace the Fourier ridge surrogate with an explicit smooth local deformation
   field and compare against linear alignment / relative-representation baselines;
5. move from synthetic texts to real rationale/retrieval datasets;
6. add multiple semantic spaces and test whether previously learned maps reduce the
   observations needed to characterize a new space;
7. only then compare ordinary deformation controllers with MaleCNS and connectome
   nulls.

The strongest useful result need not be a new global alignment method. A system that
reaches comparable mapping quality with substantially fewer interventions, carries
local uncertainty, or predicts unobserved scales would already justify the
cartographic formulation.

## 10. Reproducibility

Code and live findings are under:

- `experiments/pontifex_red1/`
- `experiments/pontifex_torus/`
- `.github/workflows/pontifex-torus-v0.yml`

The dated experimental narrative is in
`experiments/pontifex_torus/FINDINGS-2026-09-17.md`.
