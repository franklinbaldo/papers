---
type: "Interpretability Paper"
title: "Pontifex Torus — Addendum: Fourier-Local Interactions Are a Weak Full-Response Signal, Not a Sparse-Transport Law"
description: "A capacity-matched graph ablation tests whether the cross-frequency interactions behind quadratic transport follow local Fourier frequency topology. Local edges show a small advantage with the full A response, but the advantage disappears under the actual K=8 sparse acquisition regime."
tags: [pontifex, torus, transport, quadratic, interactions, topology, fourier, ablation, cartography]
timestamp: 2026-09-18T09:24:00-04:00
---

# Pontifex Torus — Addendum: Fourier-Local Interactions Are a Weak Full-Response Signal, Not a Sparse-Transport Law

## Question

The preceding term-level ablation showed that nearly all of the degree-2 transport gain is carried by cross-coefficient products `x_i x_j`, but that a tiny 17-edge subset does not capture the effect. The next question is whether the useful distributed interaction field nevertheless has a compact topology.

Because the A-side response is represented by a Fourier basis, the simplest structural hypothesis is **frequency locality**: interactions between the same or adjacent harmonics should be more useful than equally numerous arbitrary or distant harmonic interactions.

This experiment tests that hypothesis without selecting edges from held-out labels.

## Protocol

The field and outer evaluation protocol are unchanged: 2,000 synthetic texts, whole-text 70/30 train/test splits over seeds 0, 1, and 2, 256 B-side anchors, Ridge transport with alpha chosen using training texts only, and the same affine affinity-to-B diagnostic decoder.

With eight Fourier harmonics, the standardized A response has 17 coefficients: one DC term plus sine/cosine pairs for harmonics 1 through 8. The 16 harmonic coefficients define 120 harmonic-harmonic pair products. We compare:

1. **linear** — 17 source coefficients and no cross terms;
2. **local-frequency** — linear plus exactly 36 harmonic-harmonic edges satisfying `|h_i-h_j| <= 1`;
3. **nonlocal-frequency** — linear plus 36 harmonic-harmonic edges with the largest frequency gaps;
4. **random-harmonic** — linear plus 36 uniformly sampled harmonic-harmonic edges, repeated 12 times per outer seed;
5. **all-cross** — linear plus all 136 distinct cross terms, including DC couplings, as the high-capacity ceiling from the previous ablation.

The local, nonlocal, and every random graph have the same 36-edge budget, 53 input features total, and 13,824 Ridge state scalars including intercepts. Graph definitions are label-free. Random graphs are fixed from outer seed and replicate id.

Two acquisition conditions are evaluated independently:

- **matched sparse:** `K=8` actual A probes followed by the existing virtual-resolution reconstruction;
- **full response:** the complete available A response, which removes sparse acquisition loss before the Fourier representation.

## Result

### Eight real probes

| interaction graph | cross edges | affinity RMSE ↓ | B top-1 ↑ | neighbor overlap ↑ |
|---|---:|---:|---:|---:|
| linear | 0 | 0.05865 | 0.1289 | 0.1658 |
| **local frequency** | 36 | 0.05395 | **0.2206** | 0.1707 |
| nonlocal frequency | 36 | 0.05396 | 0.2089 | **0.1747** |
| random harmonic, mean of 36 runs | 36 | **0.05391** | **0.2209** | 0.1741 |
| all cross | 136 | 0.05045 | 0.3256 | 0.1818 |

The 36-edge local graph improves affinity RMSE by about **8.0%** over linear transport, so a small interaction graph is genuinely useful. But the edge identity is not specifically validated by frequency locality. The random-harmonic mean is slightly better in affinity RMSE (`0.05391` vs `0.05395`) and downstream neighbor overlap (`0.1741` vs `0.1707`). The deliberately nonlocal graph is essentially tied on affinity RMSE and has the best neighbor overlap of the 36-edge deterministic graphs (`0.1747`).

The per-seed random comparison makes the lack of robust sparse-topology evidence clearer. Local frequency beats only 8/12, 4/12, and 4/12 random graphs in affinity RMSE across seeds 0, 1, and 2. In neighbor overlap it beats 0/12, 5/12, and 5/12. Thus the actual `K=8` acquisition regime does **not** support the claim that Fourier-local edges are privileged.

### Full A response

| interaction graph | cross edges | affinity RMSE ↓ | B top-1 ↑ | neighbor overlap ↑ |
|---|---:|---:|---:|---:|
| linear | 0 | 0.05793 | 0.1600 | 0.1881 |
| **local frequency** | 36 | **0.05235** | 0.2722 | **0.1993** |
| nonlocal frequency | 36 | 0.05283 | **0.2772** | 0.1978 |
| random harmonic, mean of 36 runs | 36 | 0.05251 | 0.2691 | 0.1948 |
| all cross | 136 | 0.04695 | 0.4722 | 0.2156 |

When sparse acquisition is removed, a **small but consistent frequency-local signal appears**. Local frequency has lower mean affinity RMSE than the random graph ensemble (`0.05235` vs `0.05251`) and higher neighbor overlap (`0.1993` vs `0.1948`). Across the three outer seeds, local beats 8/12, 10/12, and 9/12 random graphs in affinity RMSE, and 10/12, 11/12, and 10/12 in neighbor overlap.

The effect is modest. Relative to the random mean, the local graph improves affinity RMSE by only about **0.31%** and neighbor overlap by about **2.3%**. It also does not dominate every metric: the nonlocal graph has slightly higher B top-1 (`0.2772` vs `0.2722`). The 36 local edges recover about half of the absolute affinity-RMSE improvement achieved by all 136 cross terms over the linear baseline, but random 36-edge graphs recover nearly as much.

## Interpretation

The discriminant produces a useful negative/conditional result rather than a clean topology win:

> Cross interactions are important, but **locality in Fourier frequency is not a robust law of the operational sparse transport**. A weak local-frequency enrichment is visible when the complete A response is available, and that enrichment disappears after the current `K=8` acquisition/reconstruction stage.

This narrows the architecture in two ways.

First, the previous conclusion that useful interaction signal is distributed survives: even a generic 36-edge graph materially improves over linear transport, while all 136 cross terms still provide a substantially stronger ceiling.

Second, the new result separates **latent field structure** from **observable sparse structure**. If the small full-response advantage is real, then the present acquisition/reconstruction pipeline may scramble exactly the phase/frequency relations needed to expose it. An equally plausible alternative is that the full-response effect is simply a small sample-specific fluctuation. The current experiment cannot distinguish those explanations.

The result therefore argues against hard-coding a nearest-frequency interaction graph into Pontifex now. The scientifically cleaner move is to test whether topological enrichment replicates across acquisition budgets, longer inputs, and independently chosen edge budgets before turning it into an architectural prior.

## Evidence boundary

**Supported here:** on the current 2,000-text synthetic pairwise-cartography field, 36 cross interactions materially improve transport over a linear model. With the complete A response, same/adjacent-harmonic interactions show a small, seed-consistent advantage over capacity-matched random harmonic graphs in affinity RMSE and neighbor overlap. Under `K=8` sparse acquisition, that advantage is absent and random/nonlocal controls match or exceed the local graph on the main metrics.

**Not established:** that Fourier frequency locality is a true semantic topology; that the weak full-response enrichment generalizes beyond this synthetic field; that sparse acquisition destroys a real topology rather than exposing a statistical fluctuation; that a torus uniquely explains any interaction pattern; or that a 36-edge graph is the correct architectural budget.

This diagnostic uses only the synthetic pairwise-cartography field. It does not instantiate, tune on, or contaminate the reserved future benchmark partitions

\[
D_{assembly}\perp D_{student}\perp D_{val}\perp D_{test}.
\]

Nothing in this result is evidence yet for multi-teacher Assembly, held-out-teacher transfer, tokenizer-free long-context inference, or teacher-order invariance.

## Next discriminant

The highest-information follow-up is now an **acquisition-budget × topology curve** rather than another single graph. Freeze the graph rules and measure local-vs-random enrichment at `K = 4, 6, 8, 10, full` on genuinely longer texts, where each K remains meaningfully sparse. If local enrichment increases monotonically as acquisition error falls, that would support the hypothesis that sparse reconstruction masks a latent Fourier-local relation. If no such curve appears, the weak full-response result should be treated as non-structural.

A second follow-up can test topology without an arbitrary `|Δh|<=1` threshold: estimate training-only per-edge utility, then ask whether high-utility edges are enriched by frequency gap, phase family, or harmonic ratio on held-out outer splits. Any learned sparse graph must be selected strictly inside the training partition and evaluated unchanged on the outer test texts.

## Reproducibility

Implementation:

- `experiments/pontifex_torus/interaction_topology_ablation.py`
- `.github/workflows/pontifex-interaction-topology.yml`

Successful run:

- `https://github.com/franklinbaldo/papers/actions/runs/35349218820`
- artifact `pontifex-interaction-topology-ablation` (`10549315772`)
- artifact URL: `https://github.com/franklinbaldo/papers/actions/runs/35349218820/artifacts/10549315772`

The PR remains experimental; this addendum does not authorize merging it.