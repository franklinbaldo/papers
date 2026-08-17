# Real-model spectral bottleneck findings

This note records the first real-model checks added after the synthetic spectral-bottleneck smoke. It separates frozen results from post-hoc sensitivity analyses.

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

**Claim boundary:** this is a post-hoc observer-sensitivity result. It cannot retroactively convert the negative mean-pooling experiment into confirmation. It motivates a fresh, separately frozen confirmatory experiment.

## Interpretation

The evidence currently supports a narrower statement than the initial spectral-bottleneck hypothesis:

1. semantic polarity can be linearly decodable without being the first graph-Laplacian mode;
2. observer choice is load-bearing — mean pooling and causal endpoint states expose very different graph geometry;
3. for at least two controlled semantic contrasts, a causal endpoint observer produced a Fiedler partition that generalized to unseen contexts and paraphrases;
4. this behavior did not generalize to every tested semantic contrast;
5. therefore `small lambda2` or a visually clean Fiedler cut must not be treated as a generic marker of semantic structure.

## Next confirmatory gate

The next run must be frozen before inspection and must not reuse the first corpus. It should:

- pin the exact model revision above;
- preregister the middle-layer causal-endpoint observer;
- use entirely new contexts and paraphrases;
- use multiple semantic contrasts, including a new contrast not present in the exploratory run;
- choose graph neighborhood size using a label-blind connectivity rule rather than by downstream accuracy;
- report token-length prediction as an explicit nuisance baseline;
- preserve shuffled-label and representation-scramble controls;
- keep a negative result as a scientific result rather than a CI execution failure.

Only after such a confirmation should the paper escalate from “observer-sensitive exploratory signal” to evidence that selected semantic contrasts form reproducible low-conductance geometry in this model.
