---
type: "Interpretability Paper"
title: "Pontifex Torus — Addendum: Quadratic Gain Is Almost Entirely Cross-Interaction Structure"
description: "A term-level ablation separates self-squared response curvature from cross-frequency interactions and finds that the full quadratic transport advantage is almost entirely reproduced by cross terms, while a matched small set of cross terms is no better than self-squares."
tags: [pontifex, torus, transport, quadratic, interactions, ablation, cartography]
timestamp: 2026-09-18T08:18:00-04:00
---

# Pontifex Torus — Addendum: Quadratic Gain Is Almost Entirely Cross-Interaction Structure

## Question

The capacity-matched transport experiment established that degree-2 polynomial
transport predicts B-anchor affinities better than equal-state RBF random Fourier
features and a small tanh MLP on the current synthetic cartography field. That result
still left a structural ambiguity: does the gain come from independent curvature of
each response coefficient, `x_i^2`, or from interactions between different response
coefficients, `x_i x_j`?

This experiment decomposes the quadratic basis directly.

## Protocol

The data and outer evaluation protocol are unchanged from the preceding transport
ablations: a 2,000-text synthetic one-lens field, whole-text 70/30 outer split over
three seeds, 256 B-side anchors, and the same affine affinity-to-B decoder fit only on
outer-training texts. The sparse condition exposes `K=8` actual A-side probes; the
full-response control removes sparse acquisition loss.

The standardized A response has 17 Fourier coefficients. We compare:

1. **linear** — the 17 original coefficients;
2. **squares** — linear + all 17 self-squared terms;
3. **matched random cross** — linear + 17 randomly selected pair products `x_i x_j`;
4. **matched screened cross** — linear + 17 pair products selected using only
   outer-training covariance with the B-affinity targets;
5. **all cross** — linear + all 136 distinct pair products, but no squares;
6. **full quadratic** — linear + 17 squares + all 136 pair products.

The `squares`, `matched random cross`, and `matched screened cross` models all have 34
features and exactly 8,960 Ridge scalars including intercepts. Therefore their direct
comparison controls feature count. Ridge alpha is selected using training texts only;
the outer held-out texts are untouched until final scoring.

The screened-cross selector is intentionally simple. Its failure would not show that
cross terms are unselectable, only that marginal training covariance does not isolate
a tiny sufficient subset under this protocol.

## Result

### Eight real probes

| basis | features | affinity RMSE ↓ | B top-1 ↑ | neighbor overlap ↑ |
|---|---:|---:|---:|---:|
| linear | 17 | 0.05865 | 0.1289 | 0.1658 |
| squares | 34 | 0.05607 | 0.1700 | 0.1699 |
| matched random cross | 34 | 0.05611 | 0.1706 | 0.1717 |
| matched screened cross | 34 | 0.05607 | 0.1672 | 0.1707 |
| **all cross** | 153 | **0.05045** | **0.3256** | **0.1818** |
| full quadratic | 170 | 0.05040 | 0.3211 | 0.1814 |

Self-squares reduce affinity RMSE by about **4.39%** relative to linear transport. A
capacity-matched set of 17 cross terms does essentially the same: **4.32%** for the
random subset and **4.40%** for the covariance-screened subset. There is no evidence
here that a tiny selected set of pair interactions is intrinsically better than
self-curvature.

The decisive comparison is the nested large basis. Using **all cross terms but no
squares** reduces RMSE by **13.97%**, versus **14.06%** for the full quadratic model.
In absolute RMSE reduction, the all-cross basis accounts for **99.37%** of the full
quadratic improvement. Adding all 17 self-squared terms on top of all-cross changes
RMSE by only `0.000052`, about `0.10%` of the all-cross RMSE.

Downstream behavior says the same thing. All-cross is slightly *better* than the full
quadratic model in mean top-1 (`0.3256` vs `0.3211`) and neighbor overlap (`0.1818`
vs `0.1814`), differences too small and seed-limited to treat as a confirmed win but
inconsistent with self-squares being necessary for the quadratic advantage.

### Full A response

| basis | features | affinity RMSE ↓ | B top-1 ↑ | neighbor overlap ↑ |
|---|---:|---:|---:|---:|
| linear | 17 | 0.05793 | 0.1600 | 0.1881 |
| squares | 34 | 0.05503 | 0.2050 | 0.1924 |
| matched random cross | 34 | 0.05524 | 0.2094 | 0.1885 |
| matched screened cross | 34 | 0.05500 | 0.2111 | 0.1890 |
| **all cross** | 153 | 0.04695 | 0.4722 | **0.2156** |
| full quadratic | 170 | **0.04667** | **0.4778** | 0.2150 |

The same structure survives when sparse acquisition is removed. Squares alone improve
RMSE by **5.01%**, while all-cross improves it by **18.96%** and full quadratic by
**19.44%**. All-cross therefore explains **97.55%** of the full model's absolute RMSE
reduction. Adding squares to all-cross yields only a further `0.000276` RMSE decrease.

The full-response control matters because it shows that this interaction structure is
not merely an artifact of reconstructing a response field from eight probes.

## Interpretation

The strongest supported statement is now narrower and more structural than
"quadratic features help":

> On the current synthetic response-field transport task, nearly all of the full
> degree-2 gain is carried by **cross-coefficient interactions** rather than by
> independent self-squared curvature.

At the same time, the matched 17-term comparison prevents an overly strong reading.
A tiny set of cross terms is not superior to 17 self-squared terms, and simple
training-covariance screening does not concentrate the gain. The evidence is instead
consistent with a **distributed interaction field**: many pairwise relations together
matter, while no small marginally selected subset captured most of the effect.

This is scientifically useful for Pontifex because the 17 source coefficients are a
Fourier description of the intervention response field. Products between different
coefficients represent coupling between distinct response modes. That is compatible
with the broader cartographic hypothesis that semantic transport depends on relations
between regions/modes rather than independent per-coordinate warping.

It is **not**, however, evidence that those interactions are caused by toroidal
topology. The Fourier coordinates themselves and the polynomial readout are generic.
A non-periodic or differently parameterized response basis could exhibit the same
pairwise structure.

## Evidence boundary

**Supported here:** on the 2,000-text synthetic pairwise-cartography field, the
quadratic transport advantage over linear Ridge is almost completely retained when
self-squared terms are removed and all cross terms are kept. This holds both with
`K=8` actual probes and with the complete available A response. Equal-size 17-term
cross subsets do not outperform self-squares, suggesting that the useful interaction
signal is not trivially concentrated in a few marginally strong pairs.

**Not established:** that a torus uniquely induces these interactions; that the same
interaction field appears on real corpora, long documents, other encoder pairs, or
multi-teacher Assembly; that covariance screening is the optimal sparse interaction
selector; tokenizer-free byte inference; teacher-order invariance; held-out-teacher
transfer; or any long-context retrieval advantage.

The experiment uses only the synthetic pairwise cartography field. It does not
instantiate, tune on, or contaminate the reserved future benchmark partitions

\[
D_{assembly}\perp D_{student}\perp D_{val}\perp D_{test}.
\]

## Next discriminant

Two follow-ups now have higher information value than another generic nonlinear
baseline:

1. **interaction topology:** identify whether the useful `x_i x_j` terms cluster by
   Fourier frequency distance, phase relation, or harmonic family. A structured
   sparse interaction graph can then be compared with random graphs at the same edge
   budget;
2. **long-input replication:** repeat the decomposition on genuinely longer texts
   where `K=8` is a small fraction of available raw positions, freezing the chosen
   interaction family before final evaluation.

The first test asks whether the distributed pairwise signal has a compact geometric
organization. The second asks whether the effect survives the present short synthetic
grammar.

## Reproducibility

Implementation:

- `experiments/pontifex_torus/quadratic_term_ablation.py`
- `.github/workflows/pontifex-quadratic-term-ablation.yml`

Successful run:

- `https://github.com/franklinbaldo/papers/actions/runs/35343736843`
- artifact `pontifex-quadratic-term-ablation` (`10546142563`)
- artifact URL: `https://github.com/franklinbaldo/papers/actions/runs/35343736843/artifacts/10546142563`

The PR remains experimental; this addendum does not authorize merging it.
