---
type: "Interpretability Paper"
title: "Pontifex Torus — Addendum: Nonlinear Transport Survives the Sparse-Probe Bottleneck"
description: "A held-out-text ablation shows that degree-2 transport from A-side response functions to B-anchor affinities improves over tuned linear Ridge, isolating recoverable nonlinear transport structure while leaving Assembly claims untested."
tags: [pontifex, torus, transport, nonlinear, ablation, affinities, retrieval]
timestamp: 2026-09-18T06:20:00-04:00
---

# Pontifex Torus — Addendum: Nonlinear Transport Survives the Sparse-Probe Bottleneck

## Relation to the living manuscript

The preceding decoder ablation localized a major failure mode in the regional
reconstruction pipeline: true B-anchor affinities contain enough information for
high-fidelity reconstruction, whereas the original positive softmax/barycentric
readout throws much of that information away. Replacing the readout with an affine
control largely exposes the remaining problem as

\[
\text{A-side response observations}
\longrightarrow
\widehat{\text{B-anchor affinities}}.
\]

This addendum asks a narrower discriminant question: **is the remaining transport
error mostly an observation-budget problem, or does the linear transport model class
itself leave recoverable structure on the table?**

## Experiment

The experiment uses the 2,000-text synthetic one-lens response field and holds out
whole texts with a 70/30 split across five seeds. The target is a vector of cosine
affinities to 256 B-side anchors. Every transport condition is followed by the same
affine affinity-to-B-embedding decoder, so changes downstream are attributable to
the transport stage rather than a decoder change.

Three transport controls are compared:

1. `linear_fixed`: Ridge with `alpha=1`, matching the preceding diagnostic;
2. `linear_tuned`: the same linear model, with `alpha` selected only inside the
   training partition from `{0.1, 1, 10}`;
3. `quadratic_tuned`: degree-2 polynomial interactions among the Fourier response
   coefficients followed by Ridge, with `alpha` selected by the same training-only
   inner split.

For the sparse conditions, the same K-probe observation/reconstruction mechanism is
used for both train and held-out inference. A `full_response` control removes sparse
acquisition loss while keeping the transport target and downstream decoder fixed.
The virtual integration resolution is `M=128`, the response basis uses 8 harmonics,
and the dense reference grid uses 512 phase points.

No held-out test text is used for hyperparameter selection.

## Result

The nonlinear control improves over **tuned** linear Ridge, so the comparison is not
merely an effect of fixing a poor regularization constant.

| A-side source | transport | affinity RMSE ↓ | B retrieval top-1 ↑ | B neighbor overlap ↑ |
|---|---|---:|---:|---:|
| matched sparse, K=4 | tuned linear | 0.06460 | 0.0367 | 0.0962 |
| matched sparse, K=4 | **quadratic** | **0.06073** | **0.0720** | **0.1000** |
| matched sparse, K=8 | tuned linear | 0.05935 | 0.1083 | 0.1590 |
| matched sparse, K=8 | **quadratic** | **0.05335** | **0.2123** | **0.1718** |
| matched sparse, nominal K=16 | tuned linear | 0.05814 | 0.1473 | 0.1789 |
| matched sparse, nominal K=16 | **quadratic** | **0.05054** | **0.2947** | **0.1990** |
| full A response | tuned linear | 0.05815 | 0.1470 | 0.1789 |
| full A response | **quadratic** | **0.05054** | **0.2943** | **0.1989** |

At the practically sparse `K=8` point, degree-2 transport reduces B-affinity RMSE
from `0.05935` to `0.05335`, approximately a **10.1% relative error reduction**.
Exact held-out B retrieval top-1 rises from `0.1083` to `0.2123`, and neighbor
overlap rises from `0.1590` to `0.1718`.

With the complete A response function available, the same comparison reduces affinity
RMSE from `0.05815` to `0.05054`, about **13.1%**, while B retrieval top-1 rises from
`0.1470` to `0.2943` and neighbor overlap from `0.1789` to `0.1989`.

The nominal `K=16` condition should not be interpreted as a sixteen-probe sparse
regime in this corpus. The synthetic texts expose only about `10.17` distinct raw
probe positions on average, so nominal `K=16` is effectively the full-observation
frontier and correctly converges to the `full_response` result.

## What this result means

The result falsifies a useful simpler explanation: **the remaining error is not only
caused by sparse observation.** Even after the available A response function is
fully observed, a low-order nonlinear transport recovers B-affinity structure that a
tuned linear map misses. The current bottleneck therefore contains a genuine
model-class component.

It also refines the earlier sparse-probe interpretation. Increasing real probes still
matters, but at a fixed useful budget such as `K=8`, improving the transport function
itself produces a substantial gain without revealing additional held-out encoder
observations.

This does **not** establish that the toroidal geometry is uniquely responsible for
the nonlinearity. Polynomial expansion is a generic nonlinear control, and it uses a
larger feature space than linear Ridge. The finding is therefore evidence for
**recoverable nonlinear cross-space transport structure**, not a victory of one
particular Torus parameterization. Parameter count, trainable-state bytes, inference
cost, and real-corpus generalization must be matched before claiming an efficiency
advantage.

## Evidence boundary

**Supported by this experiment:** on the current 2,000-text synthetic cartography
field, degree-2 response interactions improve held-out A-response -> B-anchor-affinity
transport beyond training-tuned linear Ridge. The effect survives whole-text holdout
and is visible both under an eight-real-probe budget and with the complete A response
function.

**Not established:** a scalable multi-teacher Assembly; teacher-order invariance;
held-out-teacher generalization; tokenizer-free byte inference; long-context
inference; real-corpus retrieval superiority; or an efficiency advantage after
matching nonlinear models for parameter count and compute.

This experiment uses only the synthetic pairwise-cartography field. It does not
instantiate, tune on, or contaminate the future benchmark partitions

\[
D_{assembly}\perp D_{student}\perp D_{val}\perp D_{test}.
\]

Those partitions remain reserved for the multi-teacher/student evaluation protocol.

## Next discriminant

The next clean test is an **equal-capacity nonlinear transport frontier**: compare
quadratic features against parameter-matched alternatives such as random Fourier/RBF
features and a very small MLP while holding the real-probe budget, B-anchor target,
downstream affine decoder, train/test texts, trainable-state bytes, and update compute
as close as possible. If the gain disappears under matched capacity, the present
result is primarily a capacity effect. If a compact nonlinear map preserves it, the
transport stage has a stronger case for structured nonlinear geometry.

A second required follow-up is to repeat the sparse `K=8` comparison on genuinely
longer texts where `K` remains far below the number of available raw positions; the
current short synthetic grammar cannot test that regime.

## Reproducibility

Implementation:

- `experiments/pontifex_torus/transport_model_class_ablation.py`
- `.github/workflows/pontifex-transport-model-class.yml`

Successful run:

- `https://github.com/franklinbaldo/papers/actions/runs/35333736906`
- artifact `pontifex-transport-model-class` (`10542193271`)

The PR remains experimental; this addendum does not authorize merging it.
