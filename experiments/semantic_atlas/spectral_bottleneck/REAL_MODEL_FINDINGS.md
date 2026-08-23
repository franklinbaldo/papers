---
type: "Findings Record"
title: "Real-Model Spectral Bottleneck Findings"
description: "Execution record for the spectral-bottleneck probes on SmolLM2-135M: the frozen mean-pooling smoke that failed its registered gates, a post-hoc observer-sensitivity probe explicitly barred from confirming it, and a fresh endpoint run that rejected the generic all-axis hypothesis while the confidence axis passed all six gates."
tags: [semantic-atlas, spectral-geometry, findings, falsification, smollm2, negative-result]
timestamp: 2026-08-17T03:00:00Z
---

# Real-model spectral bottleneck findings

This note records the real-model checks added after the synthetic spectral-bottleneck smoke. It separates frozen results, post-hoc sensitivity analyses, fresh confirmation, and cross-realization transfer.

## Frozen first real-model smoke — negative

Model: `HuggingFaceTB/SmolLM2-135M`  
Resolved revision: `93efa2f097d58c2a74874c7e644dbc9b0cee75a2`  
Registered observer: middle-layer (`15/30`) attention-masked mean pooling  
Graph: symmetric Gaussian-weighted kNN, normalized graph Laplacian, balanced Fiedler sweep  
Split: both contexts and paraphrase families held out  
Axes: approval/rejection, certainty/uncertainty, increase/decrease

Observed aggregate:

- median held-out pole accuracy: **0.5625**;
- median bridge absolute-score / pole absolute-score ratio: **1.1034**;
- supervised centroid held-out accuracy: **0.7500**;
- shuffled-label accuracy: **0.5050**;
- feature-marginal-preserving scrambled-representation accuracy: **0.5000**;
- robust axis × k fraction: **0.0000**.

Registered gates:

- FAIL — held-out semantic partition;
- FAIL — bridges near spectral boundary;
- PASS — shuffled labels near chance;
- PASS — scrambled geometry near chance;
- FAIL — not driven by one axis;
- FAIL — robust across axis and k.

**Conclusion:** the strong claim that the target semantic polarity is the first low-conductance/Fiedler partition of the raw mean-pooled state is not supported by this smoke test. The supervised centroid result shows that failure is not equivalent to absence of semantic information in the representation.

The GitHub Actions push run and the automatically duplicated pull-request run produced identical aggregate metrics and gate outcomes. A tiny numerical difference occurred only in one near-degenerate final-layer descriptive record and did not affect the registered middle-layer result.

## Post-hoc observer sensitivity — promising but not confirmatory

The same frozen corpus, split, model revision, graph construction, k values, metrics, and thresholds were then rerun using the middle-layer hidden state at the **final non-padding input token**, a natural causal endpoint observer for an autoregressive model.

Observed aggregate:

- median held-out pole accuracy: **0.9375**;
- median bridge absolute-score / pole absolute-score ratio: **0.7446**;
- supervised centroid held-out accuracy: **0.9375**;
- shuffled-label accuracy: **0.5000**;
- scrambled-representation accuracy: **0.5000**;
- robust axis × k fraction: **0.4444**.

Per-axis median held-out accuracy:

- approval/rejection: **0.9375**;
- certainty/uncertainty: **1.0000**;
- increase/decrease: **0.5000**.

The endpoint observer therefore changes the result dramatically, but the same all-axis gates still fail because the third axis remains at chance and robustness is insufficient.

**Claim boundary:** this is a post-hoc observer-sensitivity result. It cannot retroactively convert the negative mean-pooling experiment into confirmation.

## Fresh endpoint confirmation — generic hypothesis rejected, confidence replicated

A second experiment was frozen before inspection. It used the exact checkpoint above, the middle-layer causal-endpoint observer, entirely new contexts and paraphrases, an explicit token-length nuisance baseline, shuffled-label and representation-scramble controls, and a label-blind neighborhood rule: choose the smallest registered `k` for which the training graph is connected.

The three preregistered contrasts were:

1. stance/support vs opposition;
2. epistemic confidence vs uncertainty;
3. permission vs prohibition, a contrast not used in the exploratory run.

The experiment was defined to confirm the **generic** spectral-semantic claim only if all three contrasts passed six registered gates. That all-axis hypothesis **did not confirm**.

### Stance

- selected `k`: **8**;
- training Fiedler pole accuracy: **0.6250**;
- held-out pole accuracy: **0.5000**;
- bridge ratio: **0.8460**;
- token-length accuracy: **0.5000**;
- supervised centroid accuracy: **1.0000**;
- shuffled-label accuracy: **0.5000**;
- scrambled-representation accuracy: **0.6250**.

### Epistemic confidence

- selected `k`: **8**;
- training Fiedler pole accuracy: **1.0000**;
- held-out pole accuracy: **0.9375**;
- bridge ratio: **0.7917**;
- token-length accuracy: **0.3125**;
- supervised centroid accuracy: **0.9375**;
- shuffled-label accuracy: **0.5038**;
- scrambled-representation accuracy: **0.3750**;
- conductance: **0.0191**;
- `lambda2`: **0.0244**.

**All six confidence gates passed.**

### Permission

- selected `k`: **6**;
- training Fiedler pole accuracy: **0.5156**;
- held-out pole accuracy: **0.5000**;
- bridge ratio: **2.3201**;
- token-length accuracy: **0.5000**;
- supervised centroid accuracy: **1.0000**;
- shuffled-label accuracy: **0.5000**;
- scrambled-representation accuracy: **0.6250**.

This comparison is load-bearing. Stance and permission were perfectly linearly decodable by the supervised centroid baseline while remaining at chance under the Fiedler partition. Therefore **linear semantic decodability and low-conductance topology are empirically distinct properties** in this setup.

The correct update is not “semantic concepts generally form spectral bottlenecks.” It is the narrower hypothesis that **epistemic confidence may be a privileged low-frequency/topological variable in causal language-model state**.

## Cross-realization transfer — confidence survives without explicit certainty vocabulary

The confidence result was then subjected to a stricter frozen transfer test. The training set was exactly the explicit `confidence_confirm` training set from the fresh confirmation. The held-out set consisted of 24 entirely new descriptions in which epistemic confidence was implied by evidence patterns rather than directly named:

- repeated independent replications and convergent measurements for the positive pole;
- failed replications, unstable measurements, outlier dependence, or contradictory instruments for the negative pole;
- mixed replications or conflicting evidence for bridge states.

The protocol rejected the run if any registered explicit certainty terms appeared in the implicit test set. The observed forbidden-term count was **zero**.

With the already-registered endpoint observer and `k = 8`:

- training pole accuracy: **1.0000**;
- implicit held-out pole accuracy: **0.8750**;
- implicit bridge ratio: **0.8638**;
- token-length held-out accuracy: **0.6250**;
- supervised centroid held-out accuracy: **0.8125**;
- shuffled-label accuracy: **0.5013**;
- scrambled-representation accuracy: **0.5625**;
- conductance: **0.0191**;
- `lambda2`: **0.0244**.

All five registered transfer gates passed. Notably, the label-blind spectral coordinate slightly exceeded the supervised centroid baseline on the implicit realization shift (`0.8750` vs `0.8125`).

This makes a pure direct-vocabulary explanation substantially less plausible. It does **not** eliminate all lexical/style confounds: replication language itself has regularities, the corpus remains controlled, and only one small model/checkpoint has been tested.

## Current interpretation

The evidence now supports a substantially narrower but more interesting claim than the original broad proposal:

1. **The generic claim fails.** Arbitrary linearly decodable semantic contrasts are not automatically first spectral bottlenecks.
2. **Observer choice is load-bearing.** Mean pooling destroyed the signal that appears at the causal endpoint.
3. **Epistemic confidence replicated prospectively.** On a fresh corpus with a frozen endpoint observer and label-blind graph scale selection, confidence passed every registered gate.
4. **The result transfers across linguistic realization.** A Fiedler coordinate learned/oriented from explicit confidence language generalized to descriptions of replication evidence containing none of the registered explicit confidence terms.
5. **Topology and decodability differ.** Other contrasts can be decoded perfectly without forming the first low-conductance partition.
6. **The result is not yet an Atlas-level law.** Natural corpora, additional checkpoints/model families, causal interventions, and navigation/control cost remain untested.

A useful working hypothesis is therefore:

> In some causal LLM representations, epistemic confidence/uncertainty behaves as a low-frequency global variable whose poles are separated by a low-conductance region, while many other semantic distinctions remain ordinary decodable directions without comparable topological separation.

## Next gates

The highest-value next tests are, in order:

1. **checkpoint/model replication:** repeat the frozen confidence-transfer protocol on another checkpoint/model without tuning thresholds;
2. **natural-language transfer:** replace controlled templates with naturally occurring passages labelled only after corpus freezing;
3. **causal test:** intervene approximately along the confidence spectral coordinate and ask whether measured confidence/calibration changes more cheaply than matched Euclidean or random controls;
4. **dynamics:** test whether crossing the confidence bottleneck predicts trajectory persistence, correction difficulty, or semantic steering cost;
5. **cross-model geometry:** ask whether the confidence partition aligns only in sign/classification or preserves richer diffusion/geodesic structure.

Only after those gates should the manuscript promote the confidence result from a controlled pilot finding to a broader claim about semantic spectral geometry.
