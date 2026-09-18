# Handoff — Grok adversarial review of Pontifex Torus

Date: 2026-09-17 (America/Porto_Velho)

## Mission

Perform an **adversarial scientific sanity check** of the current Pontifex Torus line of work.

Do not try to be encouraging. Assume the central interpretation may be wrong and try to find the strongest reasons why the results could be artifacts, leakage, weak baselines, an over-flexible metaphor, or a trivial consequence of the experimental construction.

At the same time, do not dismiss the project merely because the framing is unusual. The relevant experiments were run this week and are not something that should be judged from model memory. Inspect the actual paper, code, workflows, and results.

The desired outcome is not a yes/no opinion. The desired outcome is a precise map of:

1. what is already empirically supported;
2. what is only a metaphor or hypothesis;
3. what may be an experimental artifact;
4. what would falsify the interesting claims;
5. which next experiments are maximally discriminating.

## Repository state

Repository:

https://github.com/franklinbaldo/papers

PR under review:

https://github.com/franklinbaldo/papers/pull/485

Branch:

`experiment/pontifex-red-1`

Current paper:

https://github.com/franklinbaldo/papers/blob/experiment/pontifex-red-1/pontifex_torus.md

Latest paper commit at handoff:

`eba03f423f1e381fe04c9562dbd7928f363f38e7`

The PR is experimental and should **not** be merged merely because individual experiment workflows pass. The branch still has an OKF-conformance failure that predates / is structurally separate from the new scientific experiments.

## Central idea, stripped of metaphor

We have two semantic encoders:

- A: `sentence-transformers/all-MiniLM-L6-v2`
- B: `BAAI/bge-small-en-v1.5`

Their raw coordinates are not assumed aligned.

For each text we apply the same token occlusion interventions at normalized positions and multiple occlusion sizes. Inside each encoder we measure the change from the original embedding to the occluded embedding, currently as cosine distance.

This creates paired intervention-response fields:

[
R_A(x,p,l), qquad R_B(x,p,l).
]

The current scientific object is therefore not initially the raw embedding mapping but a cross-space mapping between **response fields**.

The "torus" is presently a periodic computational substrate over normalized intervention position, not a demonstrated claim that embedding space literally has toroidal topology.

## Why the torus / light language appeared

The current conceptual model is:

- normalized text traversal is periodic: a finite object runs from phase 0 to phase (2pi);
- a canonical simple torus (T_0) provides a geometric prior;
- learned terrain (G=T_0+Delta G) deforms transport;
- an occlusion center emits a normalized source signal ("light");
- the learned terrain transports / backprojects that signal into regions of B;
- evidence accumulated over multiple occlusion centers reconstructs semantic geography;
- a B embedding may then be synthesized from accumulated target-region evidence;
- regional "reflectance" is learned from prior transport reliability;
- regional darkness visualizes low learned reflectance.

Treat "light", "terrain", "reflectance", and "color" as operational metaphors unless the mathematics actually justifies a stronger physical analogy.

## Key scripts to inspect

Core cached field:

https://github.com/franklinbaldo/papers/blob/experiment/pontifex-red-1/experiments/pontifex_torus/build_field_store.py

Same-task alignment:

https://github.com/franklinbaldo/papers/blob/experiment/pontifex-red-1/experiments/pontifex_torus/alignment_benchmark.py

Initial embedding reconstruction:

https://github.com/franklinbaldo/papers/blob/experiment/pontifex-red-1/experiments/pontifex_torus/embedding_reconstruction.py

Cycle / canonical torus test:

https://github.com/franklinbaldo/papers/blob/experiment/pontifex-red-1/experiments/pontifex_torus/cycle_epistemics.py

Learned regional reflectance:

https://github.com/franklinbaldo/papers/blob/experiment/pontifex-red-1/experiments/pontifex_torus/terrain_reflectance.py

Inverse backprojection:

https://github.com/franklinbaldo/papers/blob/experiment/pontifex-red-1/experiments/pontifex_torus/inverse_backprojection.py

Dated findings:

https://github.com/franklinbaldo/papers/blob/experiment/pontifex-red-1/experiments/pontifex_torus/FINDINGS-2026-09-17.md

## Experimental results that must be challenged

### 1. Response-field alignment

Successful run:

https://github.com/franklinbaldo/papers/actions/runs/35290923618

Ten seeds, same task: predict held-out B response field from A response field.

Mean results:

- Ridge profile map:
  - RMSE 0.02999
  - neighbor overlap 0.2665
  - learned state 8,448 B
- Relative-representation+kNN:
  - RMSE 0.03243
  - neighbor overlap 0.2149
  - retained state 36,352 B
- Pontifex Torus:
  - RMSE 0.03241
  - neighbor overlap 0.2524
  - learned map state 88 B
- Orthogonal Procrustes:
  - RMSE 0.04348
- CCA-8:
  - median RMSE ~0.03197
  - numerically unstable mean due to catastrophic seeds

Current restrained interpretation:

- Pontifex is **not** the best full-information aligner; Ridge wins absolute RMSE.
- Pontifex's strongest current result is compactness of the learned response-field map.
- The comparison is not yet complete: regularized CCA and a geometry-native GW-style baseline are missing.
- "State bytes" accounting must be challenged for fairness.

### 2. Direct embedding reconstruction from response fields

Successful run:

https://github.com/franklinbaldo/papers/actions/runs/35291518629

Important ten-seed means:

- raw MiniLM embedding -> BGE embedding, Ridge:
  - cosine 0.9548
  - normalized RMSE 0.01533
  - retrieval top-1 99.4%
  - neighbor overlap 0.6111

- **oracle true B response field -> B embedding, PLS**:
  - cosine 0.8374
  - normalized RMSE 0.02910
  - retrieval top-1 27.8%
  - neighbor overlap 0.2717

- direct A response field -> B embedding, Ridge:
  - cosine 0.8316
  - top-1 11.4%
  - neighbor overlap 0.2741

- Torus A->B field -> embedding:
  - cosine ~0.807–0.809 depending decoder
  - top-1 ~4.4–11.1%

Key diagnostic:

Even the **true B response field** is not sufficient for near-exact B embedding recovery under the tested decoders. Therefore the current scalar response field discards substantial information about the original B embedding.

Do not allow the paper to imply otherwise.

### 3. Repeated passes / sequential geometry

Pass-count sweep:

- 1 pass held-out RMSE ~0.04534
- best aggregate at 16 passes ~0.03947
- then gradual degradation through 500 passes

Five-seed T1 -> T2..T11 -> T1 experiment:

- T1 after first 16 passes: 0.05688 RMSE
- T1 after learning T2..T11 without revisiting T1: 0.04230
- after returning to T1: 0.03305

This looks like positive backward transfer in the toy, but increasing passes also changes total optimization budget. Challenge all causal interpretations.

### 4. Canonical torus / cycle closure

Successful run:

https://github.com/franklinbaldo/papers/actions/runs/35293515247

As training pairs increase 4 -> 84:

- mean cycle error falls ~0.0572 -> 0.0400
- mean cycle-derived darkness falls ~0.541 -> 0.400
- embedding cosine error falls ~0.255 -> 0.195

At 84 texts, shuffled A/B correspondence:

- cycle error ~0.0598
- cycle darkness ~0.515

versus true correspondence:

- cycle error ~0.0400
- cycle darkness ~0.400

However:

- per-text cycle residual is near-useless for predicting actual B-field error;
- naive local "darkness = instantaneous non-closure" is contradicted by regional results and was explicitly rejected.

Important conceptual point:

A canonical identity torus closes perfectly by definition while knowing nothing about the A<->B terrain. **Closure alone cannot equal knowledge.**

### 5. Learned regional reflectance / color

Successful run:

https://github.com/franklinbaldo/papers/actions/runs/35293632766

Regional darkness is instead learned from out-of-fold transport error on **previous traversals**.

Under true correspondence, correlation between learned regional darkness and held-out regional B error:

- 8 train texts: Pearson 0.658, Spearman 0.632
- 16: 0.679 / 0.656
- 32: 0.713 / 0.676
- 64: 0.759 / 0.727
- 84: **0.801 / 0.776**

At 84 texts:

- true-map mean darkness ~0.512
- shuffled-map darkness ~0.625
- true B-field RMSE ~0.03235
- shuffled B-field RMSE ~0.03640

This is the current strongest support for "color" as a regional epistemic visualization.

But:

- text-level darkness is a weak confidence estimate;
- it does not reliably predict final embedding error;
- the regional metric may partly reflect region-specific variance / scale structure;
- the normalization procedure itself must be inspected for leakage or tautology.

### 6. New inverse-light backprojection experiment

Successful run:

https://github.com/franklinbaldo/papers/actions/runs/35295020261

Artifact:

https://github.com/franklinbaldo/papers/actions/runs/35295020261/artifacts/10527431873

Pipeline actually implemented:

[
	ext{occlusion center}
ightarrow
	ext{cheap-space response light}
ightarrow
K_G
ightarrow
	ext{B-region affinity accumulation}
ightarrow
hat E_B.
]

Implementation details:

- 16 representative B anchors define target semantic regions.
- The cross-space object is a regularized linear probe-to-region kernel.
- Selected occlusion centers emit standardized A-response deviations.
- Unvisited centers contribute zero deviation from the canonical prior.
- Target-region evidence is accumulated.
- Softmax turns region scores into nonnegative mass.
- The B vector is reconstructed by a barycentric combination of B anchors.
- Budgets count occlusion **centers**.
- Two variants:
  - smallest lens only;
  - all four lens sizes at each center.

Ten-seed means:

Canonical regional prior, 0 probes:

- cosine 0.7931
- top-1 2.78%
- neighbor overlap 0.0889

Backprojection, smallest lens, 8 centers / 8 scalar probes:

- cosine 0.7941
- top-1 2.78%
- neighbor overlap 0.1619

Backprojection, all lenses, 1 center / 4 scalar probes:

- cosine 0.7935
- top-1 3.06%
- neighbor overlap 0.1892

Backprojection, all lenses, 4 centers / 16 scalar probes:

- cosine 0.7946
- top-1 3.33%
- neighbor overlap 0.2131

Backprojection, all lenses, 8 centers / 32 scalar probes:

- cosine **0.7974**
- normalized RMSE **0.03248**
- top-1 **4.44%**
- neighbor overlap **0.3013**

Direct A-profile -> B-embedding Ridge, same full 32 scalar responses:

- cosine **0.8316**
- normalized RMSE **0.02962**
- top-1 **11.39%**
- neighbor overlap **0.2741**

Current interpretation, deliberately cautious:

- The backprojection does **not** beat direct Ridge in absolute vector fidelity.
- It does, at full budget, have higher mean B-space neighbor overlap: 0.3013 vs 0.2741.
- This neighbor-overlap difference has **not** been tested for paired statistical significance.
- The result is therefore only suggestive that the regional architecture may preserve relative semantic geography better than absolute coordinates.
- The source kernel is still linear Ridge; the experiment tests factorization / regional constraints, not literal optical propagation.
- The barycentric target decoder uses B anchors learned from training embeddings, which may strongly constrain or bias the comparison.

## Claims / ideas that are NOT established

Challenge these especially hard:

### "Infinite context"

The proposal is that any finite sequence can be parameterized by normalized phase and traversed without fitting the entire object into a fixed context window. This could support **arbitrarily long finite streaming context** if state can be accumulated without destructive interference.

It does **not** establish literal infinite context.

Open failure modes include:

- order information loss;
- aliasing under normalized phase;
- semantic interference;
- accumulation saturation;
- inability to distinguish repeated / duplicated segments;
- probe budget growing linearly or worse with semantic complexity;
- hidden dependence on full-text embeddings used to compute the current response field.

The last point is especially important: current response fields use original full-text MiniLM/BGE embeddings as references when computing cosine distance after masking. Therefore the current toy does **not** yet demonstrate a true streaming implementation that avoids full-context encoding.

### "Light conservation"

A unit of light and canonical return of 1 are definitions of the computational model, not a discovered law of information conservation.

The reviewer should determine whether conservation language adds mathematics or merely renames normalization.

### "Torus"

The torus currently supplies periodic position coordinates / a closed traversal prior. There is no evidence yet that latent semantic topology is intrinsically toroidal.

Ask whether a circle, cylinder, periodic Fourier basis, or even ordinary normalized interval with boundary handling would explain the same results.

### "Information loss"

Low return / darkness is currently empirical transport unreliability, not Shannon information loss unless a formal information-theoretic connection is established.

## Highest-risk methodological issues to inspect

Please inspect the code for these rather than merely discussing them abstractly:

1. **Synthetic corpus simplicity.**
   The 120-text corpus is generated from a small combinatorial grammar. Determine how much of the apparent cross-encoder mapping is explained by template structure.

2. **Full-text leakage into the response field.**
   Each response is cosine distance between the encoder's original full-text embedding and a masked-text embedding. This is incompatible with strong claims of streaming / unbounded context unless replaced by a genuinely local or recursively accumulated reference.

3. **Common-grid interpolation.**
   Alignment baselines interpolate variable raw positions onto a normalized 8-point grid. Determine whether interpolation creates artificial smoothness favorable to the Torus.

4. **Train/test leakage.**
   Verify that no held-out B field or B embedding affects:
   - kernel fitting;
   - anchor selection;
   - reflectance estimation;
   - hyperparameter selection;
   - probe selection.

5. **Anchor leakage / unfair target access.**
   The inverse-backprojection method stores target B anchor embeddings from training data. Account for this memory explicitly and compare against equally memory-rich baselines.

6. **Map-state accounting.**
   The reported 88 B for Torus does not include input field stores, code, anchor memory, or all inference state. Decide which comparison is scientifically fair.

7. **Baseline tuning.**
   Ridge alpha, CCA regularization, anchor count, kNN k, PLS components, softmax temperature, grid density, and probe policy are not comprehensively tuned under a validation-only protocol.

8. **Multiple-comparisons / iterative researcher degrees of freedom.**
   Many related experiments were run in rapid succession. Identify where a fresh frozen holdout is required.

9. **Neighbor-overlap metric.**
   Verify that the apparent backprojection advantage 0.3013 vs 0.2741 is robust:
   - paired per-seed test;
   - bootstrap confidence interval;
   - multiple k values;
   - retrieval against a larger candidate set;
   - real corpus.

10. **Shuffled controls.**
    Evaluate whether the current shuffled A/B control is sufficiently hard or whether other nulls are needed:
    - within-template shuffle;
    - position shuffle;
    - lens-label shuffle;
    - phase scramble;
    - random periodic features;
    - random anchors;
    - same-capacity non-periodic linear model.

11. **The canonical prior.**
    Determine whether the high cosine of the zero-probe regional prior (~0.793) simply reflects anisotropy / common mean direction in BGE embeddings. If so, report improvement over this prior rather than absolute cosine.

12. **Direct raw embedding translation.**
    A simple MiniLM->BGE Ridge achieves ~0.955 cosine and ~99.4% held-out top-1 on the synthetic corpus. Explain what use case could justify the much weaker cartographic reconstruction, and what budget/availability constraints are required to make the comparison meaningful.

## Adversarial questions

Please answer each explicitly.

1. Is there any result here that cannot be explained by a simple low-dimensional shared semantic factor in the synthetic grammar?

2. Does periodic position add value after controlling for:
   - normalized absolute position;
   - polynomial basis;
   - random Fourier features;
   - nonperiodic splines?

3. Is "torus" scientifically doing work, or is it only a useful visualization of periodic coordinates?

4. Does learned regional darkness measure epistemic uncertainty, or merely region-specific predictive difficulty?

5. Is the 0.80 darkness-vs-error correlation partly tautological because darkness is defined from prior OOF prediction error and tested on the same fixed region identities?

6. Does inverse backprojection provide anything beyond a low-rank / anchor-constrained linear regression?

7. Is the better neighbor overlap of backprojection real and statistically meaningful?

8. Does the barycentric anchor reconstruction artificially favor neighborhood metrics while necessarily hurting coordinate fidelity?

9. Is there a proper inverse-problem formulation (e.g. adjoint operator, tomography, kernel inverse, Radon-like transform) that makes the current method principled, or is "backprojection" currently only an analogy?

10. Under what minimal conditions would a response field identify a target embedding up to an equivalence class?

11. What information is provably destroyed by scalar cosine-distance occlusion responses?

12. Can the current response-field representation distinguish two texts with the same occlusion response profile but different B embeddings?

13. Is the claimed path to arbitrarily long finite context compatible with the fact that current response computation uses the full original text embedding?

14. What experiment would most efficiently falsify the "context length independent of raw token count" idea?

15. What is the strongest prior art for:
    - representational similarity analysis;
    - model stitching / latent translation;
    - relative representations;
    - hyperalignment / Procrustes / CCA;
    - Gromov-Wasserstein alignment;
    - inverse problems / backprojection / tomography in representation space;
    - active sensing / adaptive experimental design;
    - uncertainty calibration from cycle consistency;
    - long-context streaming embeddings?

Do fresh web / literature research. Do not rely only on memory. Give exact papers, dates, and links.

## Decisive experiments requested from the reviewer

Propose a short ordered set of experiments that would most efficiently distinguish:

A. genuine intervention-indexed semantic geometry;

from

B. a small synthetic dataset plus a regularized low-rank linear mapping.

At minimum consider:

- real corpora with much larger lexical and structural diversity;
- frozen untouched final test set created before further method changes;
- length extrapolation;
- texts with repeated/reordered clauses;
- adversarial same-bag-of-semantics sequences with different order;
- substantially longer texts;
- probe-budget curves at equal expensive-B observation cost;
- active vs uniform probe selection;
- nonperiodic basis controls;
- random-coordinate / random-anchor controls;
- richer response observables versus the current scalar cosine response;
- genuinely streaming response construction with no full-text embedding available;
- paired significance tests for all claimed differences.

## Output format

Return a review with these sections:

1. **Executive scientific diagnosis**
   - What, if anything, is genuinely surprising?
   - What is likely trivial / expected?
   - What is currently unsupported?

2. **Code-level audit**
   - Leakage, unfair access, metric issues, implementation bugs, state accounting.

3. **Claim-by-claim stress test**
   - response-field alignment
   - active cartography
   - repeated passes / backward transfer
   - cycle closure
   - reflectance / color
   - inverse backprojection
   - arbitrarily long finite context

4. **Prior-art audit**
   - closest work and whether any novelty claim survives.

5. **Falsification plan**
   - smallest set of decisive next experiments, ordered by information value.

6. **Paper edits required before publication**
   - exact claims to weaken, delete, or strengthen.

7. **Bottom-line confidence**
   - Give separate confidence assessments for:
     - empirical response-field phenomenon;
     - torus/periodic geometry being causally useful;
     - learned reflectance as regional uncertainty;
     - inverse backprojection as a useful reconstruction mechanism;
     - arbitrarily long finite-context extension.

Be adversarial but evidence-driven. A negative conclusion is useful if well supported.


## Update — one lens x 32 normalized positions

New successful run:

https://github.com/franklinbaldo/papers/actions/runs/35295286403

Artifact:

https://github.com/franklinbaldo/papers/actions/runs/35295286403/artifacts/10528195900

The source field was rebuilt using all discrete token-start positions available in
the short synthetic sentences, then interpolated to a common 32-position normalized
phase grid. Only occlusion size=1 is retained. Thus this is a **one-lens,
32-normalized-position** experiment, not 32 independent raw occlusions for every
sentence.

Ten-seed full-budget result:

- inverse backprojection:
  - cosine 0.79769
  - normalized RMSE 0.03246
  - retrieval top-1 4.17%
  - neighbor overlap **0.36235**
- direct Ridge on the same 32 scalar response coordinates:
  - cosine 0.83043
  - normalized RMSE 0.02972
  - retrieval top-1 9.72%
  - neighbor overlap **0.31308**

Earlier one-lens / 8-position backprojection had neighbor overlap only ~0.1619.
The 32-position condition therefore shows a large increase in relational geometry
preservation, while exact vector fidelity remains much worse than Ridge.

Adversarial priority: determine whether this gain is real or an interpolation /
smoothness artifact. Require a follow-up on texts long enough to expose at least 32
**distinct raw token occlusion centers**, plus paired significance and nonperiodic
controls.


## Update — fixed real probes versus virtual Torus resolution

New successful runs:

- fixed-K virtual resolution:
  https://github.com/franklinbaldo/papers/actions/runs/35295761935
- terrain bandwidth sweep:
  https://github.com/franklinbaldo/papers/actions/runs/35295852947
- real-probe frontier:
  https://github.com/franklinbaldo/papers/actions/runs/35295926064

Core protocol:

- one lens only (`size=1`);
- only `K` actual held-out A-side occlusion responses are revealed;
- those `K` observations define a circular interpolated source function;
- a continuous Fourier transport kernel is learned from training texts;
- `M` virtual positions are used only to numerically integrate the inferred source
  through that terrain;
- increasing `M` therefore does **not** reveal any new held-out encoder observation.

Key result for `K=8`:

- M=8: neighbor overlap 0.29475
- M=16: 0.35292
- M=32: 0.35295
- M=128: 0.35388
- M=512: 0.35388

So virtual traversal helps strongly from 8 to ~16 steps, then saturates.

Terrain-bandwidth sweep (4, 8, 16, 32 Fourier harmonics) does not shift the plateau
much. Best observed relational score is H=32, M=16, K=8:

- neighbor overlap 0.362996
- cosine ~0.79567

The real-probe frontier at M=128 is:

- K=1: neighbor 0.1091
- K=2: 0.1640
- K=3: 0.2609
- K=4: 0.2519
- K=5: 0.2578
- K=6: 0.2733
- K=7: 0.2904
- K=8: 0.3539

Interpretation to attack:

The data support the narrow distinction

`K = observational information budget`

versus

`M = virtual integration resolution`.

They do **not** support a claim that arbitrarily increasing M creates arbitrarily
better estimates. M may be arbitrarily large computationally, but useful accuracy
saturates once the inferred continuous terrain is resolved.

Adversarial questions:

1. Is the gain M=8 -> M=16 merely numerical quadrature convergence rather than a
   distinctive scientific advantage of the torus?
2. Would an ordinary continuous spline / Gaussian-process / Fourier functional
   regressor show the same behavior without toroidal language?
3. Does circular interpolation across the start/end boundary introduce an unjustified
   prior that happens to help this synthetic grammar?
4. Is the non-monotonic K=3/4/5 behavior evidence that uniform probe placement is
   poor and active selection is the real problem?
5. What control best distinguishes "continuous semantic terrain" from ordinary
   function interpolation plus low-rank regression?
