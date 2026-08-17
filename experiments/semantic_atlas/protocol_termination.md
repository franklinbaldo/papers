---
type: "Protocol"
title: "Semantic Atlas Experiment F — Termination Geometry"
description: "Pre-registered experiment testing whether EOS behavior induces stable terminal basins, stopping surfaces, spectral bottlenecks, or genuinely singular dynamics in a semantic atlas."
tags: [semantic-atlas, preregistration, eos, dynamics, attractors, stopping-time, spectral-geometry, graph-laplacian]
timestamp: 2026-08-09T01:56:00Z
---

# Semantic Atlas Experiment F — Termination Geometry

## Question

Is an end-of-sequence token merely a lexical stopping decision, or does autoregressive termination have a stable geometry in semantic state space?

The experiment deliberately distinguishes four increasingly strong claims:

1. **absorbing state** — after `EOS`, the generation episode is over by definition;
2. **terminal basin** — causal states near some endings converge into regions where stopping becomes progressively more likely;
3. **terminal horizon** — a level set of stopping probability separates states from which termination within a short horizon is unlikely from states where it becomes sharply likely;
4. **dynamic singularity** — some effective dynamical quantity becomes non-regular, non-extendable, rank-deficient, or otherwise qualitatively degenerate near termination.

Only the fourth claim licenses the word **singularity**. The first three do not.

## Frontier correction — learned remaining-length signals are a load-bearing control

Token index, normalized sequence length, and prompt-implied target length are not strong enough controls for the 2026 frontier.

Merzouk et al. (2026), **How Much is Left? LLMs Linearly Encode Their Remaining Output Length** (arXiv:2607.05316), report that simple linear probes on frozen hidden states can decode total response length before generation and track approximate remaining length during generation. Xie et al. (2026), **Predicting LLM Output Length via Entropy-Guided Representations** (arXiv:2602.11812), use on-the-fly hidden states and token entropy for static and progressive remaining-length prediction.

These results create a direct false-green risk for this experiment: an apparent semantic tail, basin, stopping field, or spectral separation may simply recover a pre-existing internal length estimate. Therefore a geometric termination result is interesting only if SRF state/velocity/history adds reproducible information **conditional on a learned remaining-length baseline**, not merely beyond absolute token position.

The primary analysis must freeze a learned remaining-length control before inspecting the geometry result. At minimum use a linear hidden-state probe; when feasible, add a progressive hidden-state-plus-entropy predictor as a stronger secondary baseline. These probes are predictive controls, not claims that the decoded quantity causally determines `EOS`.

## Motivation

Semantic Atlas already treats generation as a trajectory through a model-relative semantic world. `EOS` then raises a natural boundary-condition question: what does the end of a trajectory look like from inside that world?

A token-level implementation gives the trivial answer: when `EOS` is emitted, decoding stops. The interesting question concerns the *approach* to `EOS`. If many apparently different endings enter reproducible regions of hidden/SRF state before the stop decision, termination may be represented by a field or family of basins rather than by a single final symbol.

This is not purely speculative. Newman, Hewitt, Liang & Manning (BlackboxNLP 2020), *The EOS Decision and Length Extrapolation*, report hidden-state **length manifolds** and **length attractors**, including clusters in which models become stuck once `EOS` is the highest-probability prediction. Their result motivates testing terminal attractors but does not imply that `EOS` is a geometric singularity.

A complementary geometric question is whether terminal states are separated from continuable states by reproducible **spectral bottlenecks** in a neighborhood or diffusion graph. Spectral graph methods can identify weakly connected regions without using endpoint labels to choose the cut. This gives the experiment an independent structural test: if a terminal basin is a genuine region of the semantic dynamics rather than merely a high `p_EOS` classifier contour, it may also appear as a stable low-conductance region of sampled state space. That implication is a hypothesis, not a definition.

## Stopping field

For causal semantic state `q_t`, incoming velocity `v_t`, optional compressed history/state `h_t`, and horizon `H`, estimate

\[
\lambda_H(q_t,v_t,h_t)
=
P(T-t\le H\mid q_t,v_t,h_t),
\]

where `T` is the first emitted `EOS` position.

A simpler lexical observable is

\[
p_{EOS}(t)=P(x_{t+1}=EOS\mid x_{\le t}),
\]

but the atlas claim concerns whether this stopping probability has stable structure after projection into the SRF and whether velocity/history explain residual ambiguity.

For the primary frontier-controlled analysis, let

\[
\hat r_t = f_{len}(h_t, e_t)
\]

be the preregistered estimate of remaining output length, where `e_t` may include registered entropy features for the stronger baseline. Compare models that predict `EOS within H` from `\hat r_t` alone against models that add `q_t`, `v_t`, and compressed history. The Semantic Atlas claim requires incremental held-out value beyond `\hat r_t`.

## Terminal basin

For a candidate region `B`, call it a terminal basin at horizon `H` only if all of the following hold on held-out generations:

- entering `B` increases `lambda_H` relative to matched states outside `B`;
- trajectories tend to remain in `B` or move toward higher `lambda_H` until termination;
- the effect survives controls for absolute token position, prompt-implied target length, **and learned remaining-length prediction**;
- the region is not explained solely by one trivial lexical marker such as a final punctuation token.

Multiple terminal basins are expected. A proof conclusion, a refusal, a short factual answer, a narrative ending, and a degenerative repetition may all terminate with the same special token while approaching it through different regions.

## Spectral terminal-basin test

A classifier can produce a smooth stopping field even when the underlying support has no special boundary. The spectral test therefore asks a separate question: **does the sampled semantic geometry itself contain a weak bridge between continuable and terminal regimes?**

On the training split only, construct a weighted state graph from SRF states or a preregistered native-space representation. Freeze the representation, neighborhood rule, kernel/bandwidth, symmetrization, and density normalization before evaluating terminal labels. Let `W` be the weighted adjacency matrix, `D` the degree matrix, and

\[
L_{norm}=I-D^{-1/2}WD^{-1/2}.
\]

Write

\[
0=\mu_1\le\mu_2\le\cdots
\]

for the normalized-Laplacian spectrum. Use the Fiedler vector associated with `mu_2` to generate sweep cuts and record the minimum-conductance candidate cut without using `EOS`, endpoint type, or future distance-to-`EOS` as cut-selection labels.

The primary spectral hypothesis is not merely `mu_2 > 0`; any connected finite graph typically has a nonzero first non-trivial eigenvalue. Instead it is:

> A low-conductance partition identified from training geometry alone will reproducibly enrich for high stopping hazard on held-out trajectories, and crossing that partition will predict termination dynamics beyond position and learned remaining-length controls.

For a candidate terminal set `S`, report conductance

\[
\phi(S)=\frac{w(S,\bar S)}{\min(\operatorname{vol}S,\operatorname{vol}\bar S)}.
\]

Cheeger-type relations between conductance and the first non-trivial Laplacian eigenvalue motivate the use of `mu_2` and Fiedler sweep cuts as bottleneck diagnostics. They do **not** imply that a terminal basin exists, that a cut is causal, or that the graph is the true manifold.

The analysis must test at least three alternatives:

1. **single terminal bottleneck:** one stable low-conductance division separates most terminal approach states from continuable states;
2. **multiple endpoint-specific bottlenecks:** different ending modes form distinct basins with no universal terminal partition;
3. **no spectral terminal structure:** stopping hazard varies over a geometrically well-connected support and is better described as a policy/readout field than a basin boundary.

Density is a critical confound. Apparent low-conductance cuts must survive density-matched controls, reasonable changes in `k`/bandwidth, and resampling. The learned remaining-length estimate is also a critical confound: spectral enrichment must be tested after stratifying or residualizing by `\hat r_t`.

A graph/Laplacian **spectral gap** in this protocol is only a representation-geometric observable. It is not a quantum-field-theoretic mass gap and carries no physical compactification claim.

## Terminal horizon

For a threshold `tau`, define a stopping surface

\[
\Sigma_{H,\tau}
=
\{s:\lambda_H(s)=\tau\}.
\]

The word **horizon** is justified operationally only if crossing such a surface predicts a sharp and reproducible change in short-horizon termination probability after conditioning on the registered length controls.

Unlike a physical event horizon, this surface need not be irreversible: a control intervention may push generation back toward lower stopping probability. Measuring the intervention cost is part of the experiment.

## Dynamic singularity

Do **not** call `EOS` a singularity merely because there is no subsequent generated state.

A dynamic-singularity claim requires evidence such as:

- a locally estimated transition operator losing rank in a reproducible way;
- a control or prediction Jacobian becoming ill-conditioned or discontinuous;
- a semantic velocity/flow field becoming non-extendable under a representation that remains regular away from termination;
- a topology change that cannot be removed by increasing atlas resolution or changing observers.

Neither a small `mu_2` nor a low-conductance Fiedler cut is evidence of a dynamic singularity. Those are weaker global-connectivity statements about the registered sampled graph.

If no singular phenomenon appears, the correct language is absorbing boundary, terminal basin, stopping surface, or spectral bottleneck as appropriate.

## Dataset

Generate a frozen corpus containing at least the following ending modes:

1. short factual answers;
2. mathematical/proof conclusions;
3. long-form explanatory conclusions;
4. narrative endings;
5. refusals/safety endings where permitted by the benchmark;
6. format-constrained endings;
7. repetitive or degenerate endings;
8. artificial truncation controls where generation is stopped externally rather than by `EOS`.

Record for the final `N` model steps before termination:

- prompt and exact token prefix;
- token index and distance-to-`EOS`;
- `p_EOS` and compressed top-k logits;
- generator hidden state at registered layers;
- SRF position `q_t`;
- semantic velocity `v_t`;
- local trajectory curvature;
- graph component / diffusion coordinates / Fiedler coordinate under the frozen spectral construction;
- endpoint type label;
- model/tokenizer revision and seed.

Also collect matched mid-generation and externally truncated states so that the support graph is not built only from the terminal window.

## Baselines

Compare stopping prediction using:

1. token index / normalized sequence length only;
2. recent lexical tokens only;
3. preregistered linear hidden-state probe for total/remaining output length;
4. progressive hidden-state + entropy remaining-length predictor when feasible;
5. native hidden state;
6. SRF position `q_t` only;
7. `q_t + v_t`;
8. `q_t + v_t + compressed history`;
9. learned remaining-length prediction + `q_t`;
10. learned remaining-length prediction + `q_t + v_t + compressed history`;
11. frozen graph spectral coordinates / Fiedler coordinate without endpoint labels;
12. learned remaining-length prediction + frozen spectral coordinates;
13. shuffled SRF coordinates matched by marginal distribution;
14. degree-preserving or density-matched randomized support graphs.

A semantic termination field is interesting only if it adds predictive or structural information beyond both trivial position cues **and a learned internal length signal**. A spectral result is interesting only if it is stable beyond one convenient graph construction and adds held-out structural information beyond density, distance, and the same length controls.

Train all learned baselines and geometric models on the same registered training families and evaluate on the same held-out families. Do not give the geometric model privileged access to post-hoc endpoint labels or future tokens unavailable to the length baselines. In particular, Fiedler/sweep-cut selection must be label-blind with respect to held-out termination outcomes.

## Primary measurements

### Stopping prediction

For horizons `H in {1, 2, 4, 8, 16, 32}` report:

- AUROC / AUPRC for `EOS within H`;
- Brier score and calibration curves;
- incremental gain of velocity/history over position alone;
- incremental gain of SRF position/velocity/history over the preregistered learned remaining-length predictor;
- incremental gain of frozen spectral coordinates over distance/density and learned remaining-length controls;
- performance split by endpoint type and prompt family.

The load-bearing frontier comparison is the **incremental** held-out value after the learned length control. A strong raw SRF or spectral score that disappears after conditioning on predicted remaining length does not support an independent semantic termination geometry.

### Convergence toward termination

Conditioned on ending type, measure as `k -> 0` for states `k` tokens before `EOS`:

- within-type SRF dispersion;
- between-type separation;
- trajectory speed and curvature;
- concentration of `p_EOS`;
- local transition entropy;
- diffusion distance / Fiedler coordinate evolution under the frozen graph;
- the same convergence summaries after stratifying or residualizing by predicted remaining length.

A universal collapse to one point is **not** expected or required.

### Basin persistence

Cluster candidate high-`lambda` states on a training split. On held-out trajectories measure:

- entry rate;
- dwell time;
- return probability after leaving;
- termination rate within the registered horizon;
- stability across seeds and reasonable atlas resolutions;
- persistence after matching states on predicted remaining length.

### Spectral separation

Without using held-out terminal labels to define the graph cut, report:

- `mu_2` and the preregistered low-frequency spectrum across train/resample splits;
- minimum Fiedler-sweep conductance and its stability;
- enrichment of `EOS within H` and high `lambda_H` on each side of the frozen cut;
- mutual information / predictive gain of the frozen spectral partition for termination after conditioning on `\hat r_t`;
- conductance of high-`lambda` candidate basins compared with density-matched random regions;
- crossing rate, dwell time, and return probability around the spectral boundary;
- sensitivity to neighborhood size, kernel bandwidth, representation choice, and diffusion scale;
- endpoint-specific analyses testing whether one universal cut is inferior to multiple basin-specific cuts.

Required negative controls:

- degree-preserving edge randomization;
- shuffled state coordinates preserving marginal density;
- random cuts matched for occupancy;
- graph construction on token position / predicted remaining length alone;
- Euclidean-distance and local-density predictors without spectral features.

The strongest useful outcome is not merely a small `mu_2`; it is **out-of-sample correspondence between a label-blind geometric bottleneck and termination dynamics that survives the length and density controls**.

### Horizon sharpness

For registered `tau` values, estimate how termination probability changes when a trajectory crosses `Sigma_(H,tau)`. Compare against randomly rotated or shuffled surfaces with the same marginal occupancy, against surfaces induced by the learned remaining-length predictor alone, and against the frozen spectral boundary.

The stopping surface and the spectral boundary are separate objects. Their alignment is a result to measure, not an assumption.

## Control experiment

Use the Semantic Servo or a simpler registered steering primitive to apply small interventions approximately aligned with `-grad lambda_H` (delay termination) or `+grad lambda_H` (encourage termination).

For states near a stable spectral bottleneck, add a second registered intervention that attempts to cross the Fiedler/spectral partition while holding predicted remaining length as constant as feasible. This tests whether the bottleneck is dynamically meaningful rather than a passive sampling feature.

Measure:

- minimum intervention norm required to change `EOS within H` probability by a registered amount;
- actual realized change in termination time;
- change in the learned remaining-length estimate;
- whether the intervention crosses the frozen spectral partition;
- semantic-route deviation;
- KL drift and language-quality degradation.

If a small intervention reliably crosses the estimated stopping surface in both directions, the object behaves more like a controllable boundary than a one-way event horizon. If crossing a spectral cut has no effect once position/remaining length are controlled, the cut should be reported as descriptive geometry rather than a causal boundary. If an intervention changes termination only by first shifting the learned remaining-length estimate, report that mediation rather than claiming an independent geometric mechanism.

## Falsification

The geometric-termination hypothesis weakens if:

- token position / simple lexical cues explain essentially all predictable stopping behavior;
- a learned hidden-state remaining-length predictor explains the apparent SRF advantage;
- candidate basins disappear on held-out prompts or under reasonable observer changes;
- `q_t`, velocity, and history add no information beyond learned length features;
- high-`lambda` regions do not exhibit persistence or reproducible flow after matching on predicted remaining length;
- spectral cuts are unstable across resampling or reasonable graph hyperparameters;
- spectral separation is explained by sampling density, token position, or predicted remaining length;
- label-blind Fiedler cuts do not predict held-out stopping dynamics better than matched random or distance-only cuts;
- crossing a stable spectral bottleneck has no reproducible relation to transition/control difficulty;
- any apparent singularity disappears under increased resolution or a better-conditioned coordinate system.

A negative result remains useful: it would say that `EOS` is principally an output-policy/length-planning decision rather than a macroscopic feature of the semantic dynamics. A mixed result is also informative: a terminal field may be predictive without forming a spectrally separated basin.

## Reporting language

Use the following hierarchy unless evidence justifies escalation:

`EOS token -> absorbing stopping event -> terminal basin / spectral bottleneck -> stopping surface/horizon -> dynamic singularity`

The terminal basin and spectral bottleneck are not ordered implications: either can occur without the other. Never move rightward because the metaphor is attractive.

The phrase **spectral gap** must always be qualified as graph/Laplacian spectral gap in this protocol. It must not be presented as a physical mass gap or as evidence about Yang--Mills theory.

## References

- Cheeger, J. (1970). **A Lower Bound for the Smallest Eigenvalue of the Laplacian.** In *Problems in Analysis (Papers Dedicated to Salomon Bochner)*, Princeton University Press, pp. 195–199.
- Chung, F. R. K. (1997). **Spectral Graph Theory.** CBMS Regional Conference Series in Mathematics 92, American Mathematical Society.
- Coifman, R. R., & Lafon, S. (2006). **Diffusion Maps.** *Applied and Computational Harmonic Analysis*, 21(1), 5–30. https://doi.org/10.1016/j.acha.2006.04.006.
- Khandait, A., & Gerken, J. E. (2026). **From Layers to Networks: Comparing Neural Representations via Diffusion Geometry.** arXiv:2605.15901.
- Newman, B., Hewitt, J., Liang, P., & Manning, C. D. (2020). **The EOS Decision and Length Extrapolation.** BlackboxNLP 2020, pp. 276–291. https://aclanthology.org/2020.blackboxnlp-1.26/
- Merzouk, M. A., Carpov, D., Bronzi, M., Fornasiere, D., & Oberman, A. (2026). **How Much is Left? LLMs Linearly Encode Their Remaining Output Length.** arXiv:2607.05316.
- Xie, H., Chen, Y., Wang, L., Hu, L., & Wang, D. (2026). **Predicting LLM Output Length via Entropy-Guided Representations.** arXiv:2602.11812.

## Issue

Implements the preregistration for #280; refs #260 #264 #266 #268 #276 #282 and the manifold-aware follow-up #307.