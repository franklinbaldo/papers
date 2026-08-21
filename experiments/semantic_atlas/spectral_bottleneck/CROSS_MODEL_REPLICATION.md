# Cross-model replication: SmolLM2-360M

The frozen implicit-confidence transfer protocol that passed on `HuggingFaceTB/SmolLM2-135M` was repeated unchanged on the larger model from the same family.

## Frozen replication protocol

- model: `HuggingFaceTB/SmolLM2-360M`;
- pinned revision: `f8027fd0eaeea54caa13c31d31b9fdc459c38b49`;
- observer: middle-layer causal endpoint (`16/32` hidden-state index);
- graph neighborhood: `k = 8`, unchanged from the 135M transfer;
- training corpus: the same 96 explicit confidence examples;
- test corpus: the same 24 implicit evidence/replication examples;
- thresholds and all five gates: unchanged;
- forbidden explicit confidence-term count in test: `0`.

## Result — not replicated

- training Fiedler pole accuracy: **0.4844**;
- implicit held-out pole accuracy: **0.6875**;
- implicit bridge ratio: **1.3255**;
- token-length held-out accuracy: **0.6250**;
- supervised centroid held-out accuracy: **0.6250**;
- shuffled-label accuracy: **0.4875**;
- scrambled-representation accuracy: **0.4375**;
- conductance: **0.1190**;
- `lambda2`: **0.0956**.

Scientific gates:

- FAIL — held-out implicit alignment;
- FAIL — implicit bridges near the spectral boundary;
- FAIL — beats token length by the registered margin;
- PASS — shuffled-label control;
- PASS — scrambled-geometry control.

The replication therefore has `supported = false`.

## Interpretation

This is a substantive negative result, not merely weaker transfer. The training Fiedler alignment itself falls below chance-level usefulness (`0.4844`), so the 360M middle-layer endpoint graph does not expose explicit confidence as its first non-trivial spectral partition under the frozen construction. The failure occurs before the implicit realization shift.

The result rules out the stronger statement that the observed confidence bottleneck is automatically preserved across model scale even within the SmolLM2 family. It also makes model/checkpoint/layer dependence a load-bearing part of the hypothesis.

At the same time, this comparison does **not** yet establish that the 360M model lacks confidence-related spectral structure altogether. The replication preregistered one proportional observer location (middle layer). A mechanistic follow-up should scan all hidden layers with the same corpus and graph rule, reporting the entire depth profile rather than selecting a favorable layer and calling it a replication.

The next question is therefore:

> Does the confidence-associated low-frequency mode disappear in the 360M model, or is it displaced to a different depth?

Any layer scan is exploratory. If it identifies a stable depth window, that location must be frozen and tested on a new corpus before it can count as a new 360M confirmation.
