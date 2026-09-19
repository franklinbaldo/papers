---
type: "Interpretability Paper"
title: "Pontifex Torus — Addendum: Degree-2 Transport Flips at Added Composition, Not Length Alone"
description: "A paired c1→c4 clause ladder with fixed acquisition budget reproduces the degree-2 transport reversal as soon as a second independent clause is added. A length-matched repeat4 control remains weakly positive, showing that input length alone is insufficient to explain the sign flip while leaving redundancy/composition as an unresolved causal factor."
tags: [pontifex, torus, transport, quadratic, interactions, composition, length, paired-control, ablation, cartography]
timestamp: 2026-09-18T11:34:00-04:00
---

# Pontifex Torus — Addendum: Degree-2 Transport Flips at Added Composition, Not Length Alone

## Question

The previous matched-n contrast established a real regime reversal: distributed degree-2 interactions improved A→B affinity transport on one-clause synthetic texts and hurt on four-clause texts, even after matching both corpora at 800 examples. But that comparison still moved several variables together: text families were independently generated, token count increased, the number of independent clauses increased, and the effective positional observation density changed.

This experiment asks a sharper question:

> If text identity is paired, the acquisition budget is fixed, and clauses are added incrementally to the same underlying family, where does the sign of the quadratic advantage change? And if a four-segment text is made long by repeating one clause instead of adding independent content, does the reversal remain?

## Protocol

A new paired generator samples 800 four-clause families once. For each family, `c1`, `c2`, `c3`, and `c4` are nested prefixes of the same sampled clauses. Therefore family index `i` denotes the same growing text across the entire ladder. The outer train/test split uses the same family indices for every regime and seed.

A fifth corpus, `repeat4`, repeats the first clause four times while preserving the same connector sequence. It is a deliberately low-diversity long-input control. Its mean token count (`48.125`) is nearly identical to independent `c4` (`48.215`), versus `11.164`, `23.450`, and `35.868` for `c1`, `c2`, and `c3`.

Every text in every regime receives exactly **8** size-1 probes at the same deterministic relative-position quantiles. Thus the acquisition budget is fixed rather than becoming denser or sparser merely because a text is longer. The response is converted to the same eight-harmonic Fourier representation used in the preceding transport experiments.

For outer seeds `0, 1, 2`, each regime uses a whole-family 70/30 train/test split. All learned quantities remain training-only: source-field statistics, feature scaling, B-side anchors, the diagnostic affinity decoder, and Ridge alpha selection. The compared transport classes are:

1. **linear** — 17 Fourier coefficients;
2. **all-cross** — linear plus all 136 distinct `x_i x_j` terms;
3. **full-degree-2** — linear plus 17 squares and all 136 cross terms.

The discriminant is the held-out affinity-RMSE gain relative to the linear baseline within each regime. Positive means the degree-2 basis helps; negative means it hurts.

## Result

The sign flip appears immediately when one independent clause becomes two, and it stays negative through four clauses.

| regime | mean tokens | linear RMSE ↓ | all-cross RMSE ↓ | all-cross gain vs linear | full degree-2 RMSE ↓ | full degree-2 gain |
|---|---:|---:|---:|---:|---:|---:|
| `c1` | 11.164 | 0.058135 | **0.051778** | **+0.006357 (+10.93%)** | **0.051766** | **+0.006369 (+10.96%)** |
| `c2` | 23.450 | **0.061251** | 0.064082 | **−0.002830 (−4.62%)** | 0.064656 | **−0.003405 (−5.56%)** |
| `c3` | 35.868 | **0.049951** | 0.052438 | **−0.002487 (−4.98%)** | 0.052707 | **−0.002755 (−5.52%)** |
| `c4` | 48.215 | **0.037807** | 0.039447 | **−0.001640 (−4.34%)** | 0.039608 | **−0.001801 (−4.76%)** |
| `repeat4` | 48.125 | 0.040967 | **0.040259** | **+0.000708 (+1.73%)** | **0.040253** | **+0.000713 (+1.74%)** |

The `c1` advantage is positive in **3/3 outer seeds**. The all-cross gain is then negative in **3/3 seeds at c2, c3, and c4**. Full degree-2 has the same sign pattern. The ladder is not monotonically decreasing after the transition — the harm is largest around `c2/c3` and attenuates at `c4` — so the evidence is for a **sharp regime transition**, not a simple linear dose-response with clause count.

The long repeat control is the most discriminating result. `repeat4` and independent `c4` have essentially the same mean token length, yet all-cross changes from `−0.001640` RMSE gain on `c4` to `+0.000708` on `repeat4`. The repeat-minus-independent difference is positive in every outer seed (`+0.001845`, `+0.002151`, `+0.003048`). Full degree-2 shows the same pattern (`+0.001963`, `+0.002396`, `+0.003183`).

The downstream metrics are less uniform and should not be collapsed into the RMSE claim. At `c2` and `c3`, degree-2 transport worsens affinity RMSE while still giving small average gains in top-1 and neighbor overlap. At `c4`, those downstream gains nearly vanish or reverse. `repeat4` gains strongly in top-1 (`0.1097 → 0.1764` for all-cross) but not in neighbor overlap (`0.1216 → 0.1201`). The cleanest replicated signal is therefore the sign of **held-out affinity RMSE**, not a universal downstream improvement.

## Interpretation

The experiment rules out two simple explanations for the earlier short-vs-long reversal:

1. **sample count** — already controlled in the preceding n=800 experiment;
2. **input length by itself** — `repeat4` is as long as `c4` on average but does not reproduce the negative degree-2 RMSE effect.

The strongest current description is therefore:

> the usefulness of distributed degree-2 transport is sensitive to **independent compositional content**, or to some correlated property introduced by independent clauses, rather than to token length alone.

The c1→c2 transition is particularly informative because it occurs with the same paired text families, the same eight acquisition coordinates, the same split indices, and the same fitting protocol. The earlier language of merely “short-vs-long regime dependence” can now be narrowed: the sign reversal survives a paired incremental design and is absent in a nearly length-matched repeated-content control.

But this still does **not** establish a causal law of “composition kills quadratic transport.” `repeat4` changes more than abstract compositional diversity: it also increases lexical repetition, redundancy, self-similarity, and potentially the conditioning of both encoder response fields. Those properties may make a low-order transport map easier even at long length. Likewise, the synthetic clause generator is highly constrained and does not approximate the distribution of natural long-form text.

## Evidence boundary

**Supported here:** on this synthetic paired generator, with 800 paired families, fixed eight-probe acquisition, identical family-level outer splits, train-only preprocessing/model selection, and the same encoders, degree-2 A→B affinity transport helps reliably for one independent clause, hurts reliably for two through four independent clauses, and returns to a small positive RMSE gain when a single clause is repeated to approximately the same token length as the four-independent-clause condition.

**Not established:** that clause count itself is the causal variable; that semantic composition rather than redundancy or encoder conditioning explains the difference; that natural text has the same transition; that a different nonlinear basis or regularizer would behave similarly; that the Torus is the correct semantic topology; or that this result predicts multi-teacher Assembly/student transfer.

The experiment never instantiates, tunes on, or reads the reserved future benchmark partitions

\[
D_{assembly}\perp D_{student}\perp D_{val}\perp D_{test}.
\]

Those partitions remain untouched. This is synthetic pairwise-cartography evidence only.

## Next discriminant

The next high-information control should break the remaining **composition ↔ redundancy** coupling at fixed length. A useful design is a four-segment family with three matched regimes:

- four independently sampled clauses;
- four paraphrases of one latent proposition, preserving semantic redundancy without literal repetition;
- four lexically different but semantically unrelated clauses whose token-length histogram is matched exactly.

If the degree-2 sign follows semantic independence rather than lexical repetition, that would strengthen a compositional-complexity account. If it follows lexical/response redundancy instead, the next model should target field conditioning rather than linguistic composition.

A second useful diagnostic is to compare training-vs-held-out affinity error for linear and all-cross at each rung. If the c2–c4 reversal is primarily variance/overfitting, the quadratic model should keep improving training error while its held-out advantage flips. If both training and held-out errors stop improving, the basis itself is structurally misspecified in the multi-clause regime.

## Reproducibility

- paired-field builder: `experiments/pontifex_torus/build_paired_clause_ladder.py`
- discriminant: `experiments/pontifex_torus/clause_complexity_ladder.py`
- workflow: `.github/workflows/pontifex-clause-complexity-ladder.yml`
- run: `https://github.com/franklinbaldo/papers/actions/runs/35361668730`
- artifact: `https://github.com/franklinbaldo/papers/actions/runs/35361668730/artifacts/10555587883`

The PR remains experimental. This addendum does not authorize merging it.
