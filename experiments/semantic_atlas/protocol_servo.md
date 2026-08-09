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

## Frontier correction — context-dependent steering is already a required baseline

The initial preregistration compared the Servo mainly against static activation addition. That is no longer a sufficient frontier baseline.

Li, Li & Huang (2026), **Steering Vector Fields for Context-Aware Inference-Time Control in Large Language Models** (arXiv:2602.01654), explicitly replace a global steering vector with a context-dependent local field derived from the gradient of a learned concept scorer. Jin et al. (2026), **Beyond Steering Vector: Flow-based Activation Steering for Inference-Time Intervention** (arXiv:2605.05892), go further and learn a concept-conditioned, token-varying velocity field with curved multi-step activation trajectories.

Therefore this experiment does **not** treat context-dependent directions, local vector fields, or curved activation paths as Semantic Atlas novelty. The distinct claim under test is narrower: whether a controller can track an **independently planned, multistep route in a calibrated SRF**, repeatedly re-observing actual generated semantic state and correcting toward the next registered waypoint at bounded intervention cost.

The primary run must include at least one implemented state-dependent steering baseline from this family. If exact reproduction of SVF or FLAS is impractical for the frozen model/task, preregister the closest faithful local-field baseline and report the deviation rather than silently falling back to a static vector.

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
- context-dependent local steering field (SVF-like or a preregistered faithful equivalent);
- token-varying / multi-step flow steering (FLAS-like) when implementation cost is compatible with the primary run; otherwise register it as a secondary frontier baseline and state why it was deferred;
- random direction with matched norm;
- desired direction shuffled across examples.

The state-dependent baseline receives the **same behavior objective** as the Servo but not the Atlas route. This separates the value of adaptive local steering from the additional value of planning and tracking an explicit SRF path. A second diagnostic may give the baseline the same local desired direction while withholding future waypoints; this asks whether route look-ahead itself contributes beyond local feedback.

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

For the frontier baselines also report matched intervention-budget and model-forward accounting. A method that reaches the goal using materially more intervention steps or model work must not be presented as equally efficient merely because endpoint success matches.

## Claim boundary

A future head that predicts semantic displacement is evidence of a compressible local dynamic signal, not evidence of a universal semantic state.

A Jacobian intervention that changes the *head prediction* but not the actual generated trajectory is a failed controller.

Beating a static steering vector does **not** establish the Semantic Servo contribution. Current prior art already contains context-dependent vector fields and token-varying activation flows. The route-control claim requires improvement over a state-dependent steering baseline on explicit route tracking, waypoint satisfaction, or another registered observable that the baseline does not trivially optimize.

Token savings count as efficiency only at the token level. Compute efficiency requires matched end-to-end wall-clock/FLOP accounting.

## Stop conditions

Stop escalating steering magnitude if language quality collapses, activations become numerically unstable, or output distributions exhibit large uncontrolled KL drift. Record the failure rather than searching indefinitely for a successful example.

## Frontier references

- Li, J., Li, Y., & Huang, K.-H. (2026). **Steering Vector Fields for Context-Aware Inference-Time Control in Large Language Models.** arXiv:2602.01654.
- Jin, Z., Deng, R., Wang, J., Shen, X., & Zhang, C. (2026). **Beyond Steering Vector: Flow-based Activation Steering for Inference-Time Intervention.** arXiv:2605.05892.
