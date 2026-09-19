---
type: "Interpretability Paper"
title: "Pontifex Torus — Addendum: Low-Order Interactions Beat Equal-State Generic Nonlinear Controls"
description: "A capacity-matched ablation shows that quadratic cross-space transport retains an advantage over RBF random Fourier features and a small tanh MLP at nearly identical stored state, narrowing the explanation from raw parameter count to inductive bias on the current synthetic cartography field."
tags: [pontifex, torus, transport, nonlinear, capacity, ablation, rff, mlp]
timestamp: 2026-09-18T07:16:00-04:00
---

# Pontifex Torus — Addendum: Low-Order Interactions Beat Equal-State Generic Nonlinear Controls

## Question

The preceding model-class ablation showed that degree-2 interactions improve
A-response -> B-anchor-affinity transport relative to tuned linear Ridge. That result
left an obvious alternative explanation: perhaps the nonlinear model won simply
because it had roughly an order of magnitude more coefficients.

This addendum tests that explanation directly. We compare the quadratic map with two
generic nonlinear alternatives that store essentially the same number of scalar
model values:

1. degree-2 polynomial features + Ridge;
2. RBF random Fourier features (RFF) + Ridge;
3. one-hidden-layer tanh MLP.

A standardized linear Ridge remains as the deliberately smaller-capacity baseline.

## Protocol

The experiment uses the existing 2,000-text synthetic one-lens cartography field.
Whole texts are split 70/30 into outer train/test partitions for each of three seeds.
The target is the same vector of cosine affinities to 256 B-side anchors used in the
previous bottleneck experiments. Every transport model is evaluated through the same
affine affinity-to-B embedding decoder, fit only on outer-training texts.

For each outer split:

- feature standardization is fit only on outer-training texts;
- Ridge alpha, RFF gamma, and MLP regularization are selected only on an inner split
  of the outer-training texts;
- the outer held-out texts are scored only after model selection;
- the sparse condition exposes exactly `K=8` actual A-side probes per held-out text;
- the full-response control removes sparse acquisition loss while keeping the same
  transport target and decoder.

The common Fourier response representation has 17 input coefficients. Degree-2
expansion produces 170 features. With 256 affinity outputs, the stored scalar state
is:

| model | stored scalars | float64 bytes |
|---|---:|---:|
| linear Ridge | 4,608 | 36,864 |
| quadratic + Ridge | 43,776 | 350,208 |
| RFF + Ridge | 43,822 | 350,576 |
| tanh MLP | 43,822 | 350,576 |

Thus the three nonlinear controls differ by only 46 stored scalars, about 0.1%, while
the linear baseline is intentionally much smaller. RFF projection weights and
phases are counted in its state budget. Polynomial feature generation itself is a
deterministic basis expansion and contributes no learned state.

## Result

### Eight real probes

| transport | affinity RMSE ↓ | B top-1 ↑ | B neighbor overlap ↑ |
|---|---:|---:|---:|
| linear Ridge | 0.05866 | 0.1261 | 0.1661 |
| **quadratic + Ridge** | **0.05046** | **0.3161** | **0.1808** |
| RFF + Ridge | 0.05247 | 0.2344 | 0.1760 |
| tanh MLP | 0.05979 | 0.1222 | 0.1655 |

At matched nonlinear state, the quadratic model remains strongest. Relative to the
small linear baseline, its affinity RMSE falls by about **14.0%**. The equal-state RFF
control also improves substantially, by about **10.6%**, but does not close the gap:
its RMSE is about 4.0% higher than the quadratic model. The equal-state MLP does not
improve on linear Ridge under this training protocol.

The downstream effect is larger than the RMSE difference alone suggests. Exact B
retrieval top-1 rises from `0.1261` for linear transport to `0.3161` for quadratic,
versus `0.2344` for RFF. Mean neighbor overlap is `0.1808` for quadratic, `0.1760`
for RFF, and `0.1661` for linear.

### Full A response

| transport | affinity RMSE ↓ | B top-1 ↑ | B neighbor overlap ↑ |
|---|---:|---:|---:|
| linear Ridge | 0.05795 | 0.1589 | 0.1873 |
| **quadratic + Ridge** | **0.04665** | **0.4744** | **0.2147** |
| RFF + Ridge | 0.05006 | 0.3044 | 0.2012 |
| tanh MLP | 0.05916 | 0.1572 | 0.1867 |

Removing sparse acquisition strengthens rather than removes the ordering. Quadratic
transport reduces affinity RMSE by about **19.5%** relative to linear Ridge; RFF
reduces it by about **13.6%**. Quadratic again wins the matched-state comparison,
including retrieval top-1 (`0.4744` versus `0.3044` for RFF) and neighbor overlap
(`0.2147` versus `0.2012`).

The result is consistent across all three outer seeds in the reported means; this run
is still too small to support fine-grained significance claims.

## What changed scientifically

The simplest "quadratic wins because it has more parameters" explanation is no
longer sufficient. RFF and the MLP have essentially identical stored scalar state to
the quadratic map, yet neither matches it on this field. At the same time, RFF does
beat the much smaller linear baseline, so the experiment does **not** support a claim
that degree-2 structure is uniquely necessary.

The narrower interpretation is:

> the current cross-space affinity transport contains useful nonlinear structure,
> and a low-order interaction basis is a particularly effective inductive bias for
> that structure at this model-state budget.

This is more specific than the previous "nonlinearity helps" result, but it is still
not evidence that a torus is the unique or correct topology. The quadratic basis used
here is generic. The result is about compact transport structure in the current
response coordinates.

The failed MLP is also informative but should not be overinterpreted. Matching stored
state does not match optimization difficulty. The MLP's final fits took roughly an
order of magnitude longer than the closed-form/linear solves on this runner, and a
single hidden layer with Adam may be poorly conditioned for the available sample
size. Its loss therefore argues against a naive generic neural replacement under this
protocol, not against neural transport models in general.

## Efficiency boundary

State matching is close; compute matching is not exact. On the GitHub runner, mean
final-fit time in the sparse condition was approximately:

- linear Ridge: `0.020 s`;
- quadratic Ridge: `0.051 s`;
- RFF Ridge: `0.039 s`;
- MLP: `0.591 s`.

Hyperparameter-selection time also differs by method. These wall times are diagnostic
runner measurements, not stable hardware-independent benchmarks. The present result
therefore supports an **equal-state** comparison, not a strict equal-FLOP claim.

## Evidence boundary

**Supported here:** on the current 2,000-text synthetic pairwise-cartography field,
nonlinear A-response -> B-anchor-affinity transport survives a near-exact stored-state
control. Degree-2 interactions outperform equal-state RFF and tanh-MLP alternatives
under the tested protocol, both with eight real probes and with the complete available
A response. RFF also improves over linear Ridge, showing that some of the gain is
shared by generic nonlinear structure.

**Not established:** that the toroidal topology causes this advantage; that quadratic
transport will remain best on real corpora or longer documents; scalable multi-teacher
Assembly; teacher-order invariance; held-out-teacher transfer; tokenizer-free byte
inference; or a long-context retrieval advantage.

This experiment uses only the synthetic pairwise cartography field. It does not
instantiate, tune on, or contaminate the future benchmark partitions

\[
D_{assembly}\perp D_{student}\perp D_{val}\perp D_{test}.
\]

Those partitions remain reserved for the multi-teacher/student evaluation protocol.

## Next discriminant

The strongest next test is no longer another generic nonlinear model on this same
short grammar. Two orthogonal checks are more informative:

1. **basis ablation:** separate the quadratic features into self-squared terms versus
   cross-frequency interactions. If cross-frequency terms carry most of the gain,
   that would identify a concrete interaction structure rather than merely "degree
   two" capacity;
2. **longer-input replication:** generate or use texts with far more than eight raw
   positions so that `K=8` remains genuinely sparse, then repeat the matched-state
   frontier. This directly tests whether the interaction advantage survives outside
   the current short-text regime.

A later real-corpus replication should freeze all model-family choices on validation
before touching the final test split.

## Reproducibility

Implementation:

- `experiments/pontifex_torus/transport_capacity_matched_ablation.py`
- `.github/workflows/pontifex-transport-capacity-matched.yml`

Successful run:

- `https://github.com/franklinbaldo/papers/actions/runs/35338457578`
- artifact `pontifex-transport-capacity-matched` (`10543757768`)
- artifact URL: `https://github.com/franklinbaldo/papers/actions/runs/35338457578/artifacts/10543757768`

The PR remains experimental; this addendum does not authorize merging it.
