# Fresh relative-depth confirmation — falsified

An exploratory all-layer scan on the original explicit-to-implicit confidence-transfer corpus found passing confidence windows at layers `15–18/30` in SmolLM2-135M and at layers `18`, `20–21/32` in SmolLM2-360M. The especially close alignment of `17/30 = 0.5667` and `18/32 = 0.5625` motivated a preregistered mechanistic prediction:

> On a fresh confidence corpus, choosing `round(0.56 * num_hidden_layers)` without any layer scan should recover the same low-frequency confidence geometry in both models.

This prediction was tested once on a completely new controlled corpus with all choices frozen in advance.

## Frozen protocol

- models/checkpoints:
  - `HuggingFaceTB/SmolLM2-135M@93efa2f097d58c2a74874c7e644dbc9b0cee75a2`;
  - `HuggingFaceTB/SmolLM2-360M@f8027fd0eaeea54caa13c31d31b9fdc459c38b49`;
- observer: causal endpoint;
- relative depth rule: `round(0.56 * N)`;
- selected layers:
  - 135M: `17/30 = 0.5667`;
  - 360M: `18/32 = 0.5625`;
- graph: Gaussian-weighted symmetric kNN, `k = 8`;
- training set: 96 completely new explicit-confidence sentences;
- held-out set: 24 completely new implicit evidence/replication sentences, 8 per class;
- forbidden explicit confidence terms in held-out set: zero;
- nuisance control: token-count predictor;
- negative controls: shuffled labels and feature-marginal-preserving representation scramble;
- model-level support required all six gates, including fresh training Fiedler alignment >= `0.80`;
- cross-model confirmation required both pinned models to pass independently.

## SmolLM2-135M — failed

- train Fiedler pole accuracy: **0.5156**;
- implicit held-out pole accuracy: **0.7500**;
- bridge ratio: **0.7685**;
- token-length accuracy: **0.5000**;
- supervised centroid held-out accuracy: **0.9375**;
- shuffled-label accuracy: **0.4900**;
- scrambled-representation accuracy: **0.5000**;
- conductance: **0.2024**;
- `lambda2`: **0.1722**.

Gates:

- FAIL — fresh training alignment;
- PASS — implicit held-out alignment;
- PASS — bridge boundary;
- PASS — beats token length by margin;
- PASS — shuffled-label control;
- PASS — scrambled-geometry control.

`Supported = false`.

The apparently respectable held-out score cannot rescue the hypothesis because the Fiedler orientation fails to align with the semantic pole even on the fresh training graph. The supervised centroid baseline shows that confidence remains strongly decodable in these states while not defining the first graph partition.

## SmolLM2-360M — failed

- train Fiedler pole accuracy: **0.4844**;
- implicit held-out pole accuracy: **0.5000**;
- bridge ratio: **1.0565**;
- token-length accuracy: **0.5000**;
- supervised centroid held-out accuracy: **0.8750**;
- shuffled-label accuracy: **0.4963**;
- scrambled-representation accuracy: **0.3750**;
- conductance: **0.1480**;
- `lambda2`: **0.1406**.

Gates:

- FAIL — fresh training alignment;
- FAIL — implicit held-out alignment;
- FAIL — bridge boundary;
- FAIL — beats token length by margin;
- PASS — shuffled-label control;
- PASS — scrambled-geometry control.

`Supported = false`.

## Conclusion

The preregistered cross-model relative-depth prediction is **falsified** by the fresh corpus. The earlier depth alignment was an exploratory property of the original controlled realization and does not generalize as a corpus-independent rule.

This result materially narrows the spectral programme:

1. semantic information can be highly linearly decodable while having little or no alignment with the first non-trivial graph-Laplacian eigenvector;
2. a strong Fiedler result on one controlled corpus must not be interpreted as a stable semantic bottleneck without independent corpus replication;
3. observer, layer, corpus realization, graph construction, and model checkpoint are all potentially load-bearing;
4. the first-eigenmode/Cheeger formulation is too strong as a generic semantic primitive;
5. future work should distinguish **semantic spectral smoothness or low-frequency subspaces** from the much stronger claim that a semantic variable is the graph's first bottleneck.

## Methodological pivot

Further hand-crafted polarity corpora would create too much researcher freedom after several observed outcomes. The next experiment should therefore remove hand-labelled semantic poles entirely. A cleaner target is a model-derived continuous observable on natural text—for example next-token predictive entropy—and ask whether that scalar is smoother on the representation graph than permutation controls and whether its variation concentrates in low-frequency Laplacian modes.

That question keeps the useful spectral machinery while dropping the unsupported assumption that semantic content must coincide with the Fiedler partition.
