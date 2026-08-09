---
type: "Protocol"
title: "Semantic Atlas Experiment C — Future Semantic Head and Closed-Loop Servo"
description: "Pre-registered experiment testing whether hidden states predict future semantic displacement and whether Jacobian feedback can follow routes with less search than semantic MPC."
tags: [semantic-atlas, preregistration, jacobian, activation-steering, control]
timestamp: 2026-08-09T00:19:00Z
---

# Semantic Atlas Experiment C — Future Semantic Head and Closed-Loop Servo

## Dependency

Compare directly with Experiment B. The purpose of this layer is to replace rollout-heavy search with a learned local model of semantic dynamics.

## H1 — future semantic state is predictable

For a selected layer `l` and horizon `H`, fit

`F_H(h_l,t) -> q_(t+H) - q_t`.

Use train/test splits by prompt family. The primary baseline predicts the mean displacement; secondary baselines use the current SRF velocity without hidden state.

Report R²/cosine/distance error for horizons fixed before the primary run.

## H2 — local Jacobian control moves the predicted future

For the linear baseline head, the Jacobian is the learned weight matrix. Given desired displacement `d*`, solve the regularized minimum-energy correction

`dh = J^T (J J^T + λI)^-1 (d* - F(h))`.

First validate this equation entirely offline on held-out hidden-state/displacement pairs. Only then inject corrections into model activations.

## Closed-loop intervention

1. observe current hidden state and SRF position;
2. select next route waypoint;
3. compute desired horizon displacement;
4. calculate bounded correction;
5. intervene at one frozen layer;
6. generate a short block;
7. re-observe and repeat.

Sweep intervention norm on a predeclared grid. Do not tune per example.

## Baselines

- no steering;
- natural-language goal prompt;
- semantic MPC from Experiment B;
- static activation addition learned from positive/negative examples;
- random direction with matched norm;
- desired direction shuffled across examples.

## Metrics

- future-head held-out error;
- route tracking error;
- success@budget;
- visible tokens;
- all model-forward tokens;
- wall-clock;
- base-vs-steered KL;
- correction norm;
- fluency/coherence;
- failure/off-manifold rate.

## Claim boundary

A future head that predicts semantic displacement is evidence of a compressible local dynamic signal, not evidence of a universal semantic state.

A Jacobian intervention that changes the *head prediction* but not the actual generated trajectory is a failed controller.

Token savings count as efficiency only at the token level. Compute efficiency requires matched end-to-end wall-clock/FLOP accounting.

## Stop conditions

Stop escalating steering magnitude if language quality collapses, activations become numerically unstable, or output distributions exhibit large uncontrolled KL drift. Record the failure rather than searching indefinitely for a successful example.
