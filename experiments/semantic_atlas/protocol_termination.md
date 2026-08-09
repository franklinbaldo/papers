---
type: "Protocol"
title: "Semantic Atlas Experiment F — Termination Geometry"
description: "Pre-registered experiment testing whether EOS behavior induces stable terminal basins, stopping surfaces, or genuinely singular dynamics in a semantic atlas."
tags: [semantic-atlas, preregistration, eos, dynamics, attractors, stopping-time]
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

## Motivation

Semantic Atlas already treats generation as a trajectory through a model-relative semantic world. `EOS` then raises a natural boundary-condition question: what does the end of a trajectory look like from inside that world?

A token-level implementation gives the trivial answer: when `EOS` is emitted, decoding stops. The interesting question concerns the *approach* to `EOS`. If many apparently different endings enter reproducible regions of hidden/SRF state before the stop decision, termination may be represented by a field or family of basins rather than by a single final symbol.

This is not purely speculative. Newman, Hewitt, Liang & Manning (BlackboxNLP 2020), *The EOS Decision and Length Extrapolation*, report hidden-state **length manifolds** and **length attractors**, including clusters in which models become stuck once `EOS` is the highest-probability prediction. Their result motivates testing terminal attractors but does not imply that `EOS` is a geometric singularity.

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

## Terminal basin

For a candidate region `B`, call it a terminal basin at horizon `H` only if all of the following hold on held-out generations:

- entering `B` increases `lambda_H` relative to matched states outside `B`;
- trajectories tend to remain in `B` or move toward higher `lambda_H` until termination;
- the effect survives controls for absolute token position and prompt-implied target length;
- the region is not explained solely by one trivial lexical marker such as a final punctuation token.

Multiple terminal basins are expected. A proof conclusion, a refusal, a short factual answer, a narrative ending, and a degenerative repetition may all terminate with the same special token while approaching it through different regions.

## Terminal horizon

For a threshold `tau`, define a stopping surface

\[
\Sigma_{H,\tau}
=
\{s:\lambda_H(s)=\tau\}.
\]

The word **horizon** is justified operationally only if crossing such a surface predicts a sharp and reproducible change in short-horizon termination probability.

Unlike a physical event horizon, this surface need not be irreversible: a control intervention may push generation back toward lower stopping probability. Measuring the intervention cost is part of the experiment.

## Dynamic singularity

Do **not** call `EOS` a singularity merely because there is no subsequent generated state.

A dynamic-singularity claim requires evidence such as:

- a locally estimated transition operator losing rank in a reproducible way;
- a control or prediction Jacobian becoming ill-conditioned or discontinuous;
- a semantic velocity/flow field becoming non-extendable under a representation that remains regular away from termination;
- a topology change that cannot be removed by increasing atlas resolution or changing observers.

If no such phenomenon appears, the correct language is absorbing boundary, terminal basin, or stopping surface.

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
- endpoint type label;
- model/tokenizer revision and seed.

## Baselines

Compare stopping prediction using:

1. token index / normalized sequence length only;
2. recent lexical tokens only;
3. native hidden state;
4. SRF position `q_t` only;
5. `q_t + v_t`;
6. `q_t + v_t + compressed history`;
7. shuffled SRF coordinates matched by marginal distribution.

A semantic termination field is interesting only if it adds predictive or structural information beyond trivial length cues.

## Primary measurements

### Stopping prediction

For horizons `H in {1, 2, 4, 8, 16, 32}` report:

- AUROC / AUPRC for `EOS within H`;
- Brier score and calibration curves;
- incremental gain of velocity/history over position alone.

### Convergence toward termination

Conditioned on ending type, measure as `k -> 0` for states `k` tokens before `EOS`:

- within-type SRF dispersion;
- between-type separation;
- trajectory speed and curvature;
- concentration of `p_EOS`;
- local transition entropy.

A universal collapse to one point is **not** expected or required.

### Basin persistence

Cluster candidate high-`lambda` states on a training split. On held-out trajectories measure:

- entry rate;
- dwell time;
- return probability after leaving;
- termination rate within the registered horizon;
- stability across seeds and reasonable atlas resolutions.

### Horizon sharpness

For registered `tau` values, estimate how termination probability changes when a trajectory crosses `Sigma_(H,tau)`. Compare against randomly rotated or shuffled surfaces with the same marginal occupancy.

## Control experiment

Use the Semantic Servo or a simpler registered steering primitive to apply small interventions approximately aligned with `-grad lambda_H` (delay termination) or `+grad lambda_H` (encourage termination).

Measure:

- minimum intervention norm required to change `EOS within H` probability by a registered amount;
- actual realized change in termination time;
- semantic-route deviation;
- KL drift and language-quality degradation.

If a small intervention reliably crosses the estimated stopping surface in both directions, the object behaves more like a controllable boundary than a one-way event horizon.

## Falsification

The geometric-termination hypothesis weakens if:

- token position / simple lexical cues explain essentially all predictable stopping behavior;
- candidate basins disappear on held-out prompts or under reasonable observer changes;
- `q_t`, velocity, and history add no information beyond native length features;
- high-`lambda` regions do not exhibit persistence or reproducible flow;
- any apparent singularity disappears under increased resolution or a better-conditioned coordinate system.

A negative result remains useful: it would say that `EOS` is principally an output-policy decision rather than a macroscopic feature of the semantic dynamics.

## Reporting language

Use the following hierarchy unless evidence justifies escalation:

`EOS token -> absorbing stopping event -> terminal basin -> stopping surface/horizon -> dynamic singularity`

Never move rightward because the metaphor is attractive.

## References

- Newman, B., Hewitt, J., Liang, P., & Manning, C. D. (2020). **The EOS Decision and Length Extrapolation.** BlackboxNLP 2020, pp. 276–291. https://aclanthology.org/2020.blackboxnlp-1.26/

## Issue

Implements the preregistration for #280; refs #260 #264 #266 #268 #276.