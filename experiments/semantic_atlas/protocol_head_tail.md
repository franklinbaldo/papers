---
type: "Protocol"
title: "Semantic Atlas Experiment F.1 — Semantic Head and Tail"
description: "Operationalizes semantic head and semantic tail as multiresolution boundary regimes rather than fixed token positions."
tags: [semantic-atlas, preregistration, boundary-conditions, head, tail, multiscale]
timestamp: 2026-08-09T01:58:30Z
---

# Semantic Atlas Experiment F.1 — Semantic Head and Tail

## Working hypothesis

Every finite work has at least trivial temporal boundaries, but its **semantic head** and **semantic tail** need not coincide with a fixed number of first or last tokens.

The proposed objects are dynamical regimes:

- **semantic head** — a region in which the work is still localizing its macrostate and many semantically distinct futures remain reachable;
- **semantic tail** — a region in which admissible futures contract, unresolved obligations are discharged, and the probability of termination rises.

These are hypotheses about effective dynamics, not literary universals asserted by definition. Their width, strength, and internal structure must be measured.

## Head as localization

Let `Z_work` denote a frozen semantic representation of the completed work at a chosen coarse resolution. For prefix state `s_t`, define a head-localization signal through the information gained about `Z_work` as new material arrives. Operational proxies include:

- decrease in uncertainty of a predictor of `Z_work` from prefixes;
- decrease in uncertainty over genre/topic/task/voice labels fixed before analysis;
- change in the reachable semantic volume over a fixed horizon;
- sensitivity of long-horizon continuation to small perturbations of the early prefix.

A semantic head is expected to combine broad branching with rapid localization: many futures are initially possible, but early choices strongly determine which semantic world the work will inhabit.

## Tail as contraction

For state `s_t`, let `R_H(s_t)` be the estimated set of natural semantic states reachable within horizon `H` under a fixed budget. Define a coarse future-volume proxy `V_H(t)` from this reachable set.

A candidate semantic tail is a sustained interval in which, relative to matched mid-work states:

\[
\frac{d}{dt}\log V_H(t) < 0
\]

and the short-horizon stopping field

\[
\lambda_H(s_t)=P(EOS\text{ within }H\mid s_t)
\]

rises or remains high.

The tail therefore begins before `EOS`. `EOS` is a point event; the tail is an approach regime.

## Nested heads and tails

The hypothesis is explicitly multiresolution. A novel, proof, legal argument, conversation, chapter, paragraph, and subargument may each contain local heads and tails.

A late semantic reset can create a new local head even near the physical end of a document. Likewise an epilogue may be a long, low-branching tail after the main narrative has already reached its semantic climax.

Consequently, normalized token position is a baseline, not the definition.

## Measurements

For a frozen corpus of complete works and generated responses, estimate along each trajectory:

1. `V_H(t)` or a registered entropy proxy for reachable futures;
2. `lambda_H(t)` for termination within multiple horizons;
3. prediction uncertainty for `Z_work` from the current prefix;
4. semantic velocity, curvature, and local transition entropy;
5. sensitivity of future trajectory to controlled local perturbations.

Compare automatic head/tail segmentation against:

- normalized-position heuristics;
- fixed first/last `k%` baselines;
- lexical discourse markers only;
- shuffled trajectories preserving token counts.

## Duality test

A strong form of the hypothesis predicts an asymmetric boundary structure:

- the head is characterized by **selection/localization** among many possible futures;
- the tail is characterized by **contraction/closure** toward a smaller family of futures.

This is not assumed to be time-reversal symmetry. Causal generation gives the two boundaries different information-theoretic roles.

## Falsification

The head/tail hypothesis weakens if all useful signals collapse to normalized token position, if future-volume estimates show no reproducible contraction before stopping, or if head localization adds no predictive structure beyond simple prefix length and lexical markers.

## Relation to Experiment F

Experiment F asks whether `EOS` has a stable termination geometry. F.1 generalizes the question from the final special token to semantic boundary regimes of finite works. A positive tail result does not imply a singularity; it may be only a smooth contraction toward an absorbing event.

Refs #280 #260 #264 #266.