---
type: "Empirical Paper"
title: "When Semantic Geometry Is Not a Bottleneck: Falsification-Driven Spectral Probes of Small Language Models"
description: "Empirical companion to the manifold-aware Semantic Atlas testing whether semantic variables and future model uncertainty appear as reproducible low-conductance or low-frequency structure in small language-model representations."
tags: [semantic-atlas, spectral-geometry, graph-laplacian, falsification, representation-geometry, language-models, uncertainty, reproducibility]
timestamp: 2026-08-17T03:36:00Z
---

# When Semantic Geometry Is Not a Bottleneck: Falsification-Driven Spectral Probes of Small Language Models

**Franklin Baldo**  
Independent Researcher  
franklinbaldo@gmail.com

---

> **Empirical companion and negative-result paper.** This manuscript reports a sequence of small, reproducible experiments motivated by the spectral extension of *From Semantic Points to Concept Manifolds*. It does not treat a graph-Laplacian spectral gap as a physical mass gap, and it does not claim that the tested models establish universal semantic manifolds. Its main result is methodological: semantic decodability, graph smoothness, and first-bottleneck topology are empirically distinct properties, and apparently strong spectral-semantic results can disappear under fresh-corpus and cross-model confirmation.

## Abstract

A natural extension of geometric accounts of language-model representations is to ask whether semantically meaningful regions are separated by measurable spectral bottlenecks. Given a neighborhood graph over hidden states, the normalized graph Laplacian provides label-free observables such as the first non-trivial eigenvalue, Fiedler vector, conductance, and diffusion modes. If a semantic distinction coincides with a robust low-conductance division, those observables could in principle identify weak bridges in a semantic atlas without fitting the downstream label itself.

We subjected that hypothesis to a staged falsification programme on two pinned SmolLM2 checkpoints. A planted synthetic benchmark first established that the implementation can recover a genuine bottleneck: the constructed bottleneck graph had a median conductance about 7.4% of its continuous control, a first non-trivial eigenvalue about 21.7% of the control, 99.8% recovery of the planted partition, and approximately 6.8-fold longer cross-region hitting time. The same machinery was then applied to language-model states.

The strongest generic hypothesis failed. In a first real-model test, mean-pooled states yielded only 56.25% held-out pole accuracy under the Fiedler partition even though a supervised centroid baseline reached 75%. A post-hoc switch to the causal endpoint state produced striking results for approval and epistemic confidence, motivating a fresh confirmation. On entirely new contexts and paraphrases, confidence alone replicated: 100% training alignment, 93.75% held-out alignment, low bridge score, and successful shuffle, scramble, and token-length controls. Stance and permission, however, remained at chance under Fiedler despite 100% supervised centroid accuracy. Confidence subsequently transferred at 87.5% accuracy from explicit certainty language to new evidence/replication descriptions containing none of the registered explicit certainty terms.

Those positive findings did not survive the strongest confirmations. The same transfer protocol failed at the exact middle layer of a larger 360M checkpoint. An exploratory all-layer scan found transient passing windows near the middle of both models and suggested a relative-depth rule near 56%. We preregistered that rule and tested it once on a completely fresh corpus. It failed in both models: training Fiedler alignment fell to 51.56% in the 135M model and 48.44% in the 360M model, while supervised centroid accuracy remained 93.75% and 87.5%, respectively.

Finally, to remove hand-labelled semantic poles altogether, we tested whether the final causal representation graph on 160 natural repository texts predicts the model's own future next-token entropy. Current entropy was strongly spectrally smooth in both models (permutation p approximately 0.002), validating the instrument's positive control. Entropy eight teacher-forced tokens later was not smooth (p approximately 0.38 and 0.65), showed no low-frequency enrichment, was not improved by the representation kNN geometry over a scalar current-entropy baseline, and was not better than scrambled representation geometry.

These experiments reject the strong proposal that semantically meaningful or dynamically relevant variables should generically appear as the first graph-Laplacian bottleneck. They also show why a negative spectral result is not evidence that semantic information is absent: several failed Fiedler contrasts remained nearly perfectly linearly decodable. The surviving research direction is therefore narrower: spectral operators may still be useful multiscale diagnostics, but low-frequency semantic structure must be distinguished from the much stronger claim that a semantic variable is the graph's first Cheeger/Fiedler bottleneck, and any such claim requires independent corpus, observer, layer, graph, and model replication.

**Keywords:** semantic geometry, spectral graph theory, graph Laplacian, Fiedler vector, conductance, representation geometry, language models, falsification, uncertainty, semantic atlas

---

## 1. Why test spectral bottlenecks?

The manifold-aware Semantic Atlas proposes that local language-model representations may have structured geometry rather than behaving merely as isolated points in a globally reduced space. Once a local support graph is available, spectral graph theory supplies a tempting family of observables. For weighted adjacency matrix \(W\) and degree matrix \(D\), define

\[
L_{\mathrm{norm}}=I-D^{-1/2}WD^{-1/2}.
\]

For a connected graph with eigenvalues

\[
0=\mu_1\le \mu_2\le \cdots,
\]

\(\mu_2\) and its associated Fiedler vector characterize the weakest large-scale connectivity mode. Fiedler sweep cuts provide candidate low-conductance partitions, while diffusion operators provide related multiscale geometry.

There is an obvious semantic hypothesis:

> If a representation contains a meaningful conceptual division, perhaps that division will appear as a weak bridge in the support graph and therefore as a low-frequency or even first non-trivial spectral mode.

The hypothesis is attractive because the graph can be constructed without using the semantic label. It is also dangerously easy to over-interpret. A low-conductance cut may reflect topic, syntax, template, density, document source, sequence length, observer choice, or an arbitrary graph scale. Even when a semantic variable is strongly encoded, there is no theorem requiring it to be the graph's weakest global connection.

This paper therefore treats the strong Fiedler hypothesis as something to try to **kill**, not something to illustrate.

## 2. Experimental discipline

The experiments were developed in stages. Each stage was allowed to motivate a later experiment, but a post-hoc success was never allowed to retroactively convert an earlier failure into confirmation.

The discipline was:

1. validate the implementation on a planted synthetic bottleneck;
2. freeze an initial observer and controlled language corpus;
3. distinguish execution success from scientific gate success;
4. use held-out contexts and paraphrase families;
5. preserve negative controls such as shuffled labels and representation scrambling;
6. when a post-hoc observer looked promising, test it on an entirely fresh corpus;
7. when a model/layer pattern looked promising, preregister the pattern and test it once on another fresh corpus;
8. after repeated hand-crafted semantic tests, stop adding new semantic labels and move to a natural-text, model-derived continuous observable.

Scientific negatives return successful workflow exit codes. The CI result answers whether the experiment executed correctly; the artifact records whether the hypothesis passed its registered gates.

All core experiments are implemented under `experiments/semantic_atlas/spectral_bottleneck/` and executed by GitHub Actions on pinned model revisions.

## 3. Synthetic validation: the instrument can see a real bottleneck

Before applying spectral machinery to model states, we constructed a synthetic positive control with two broad regions connected by a moderately narrow bridge and compared it with a continuous control cloud. The cut itself was recovered from the Fiedler vector without using the planted labels to construct the graph.

Across five seeds and three neighborhood sizes:

- median bottleneck/control conductance ratio: **0.0737**;
- median bottleneck/control \(\mu_2\) ratio: **0.2170**;
- planted Fiedler partition recovery: **99.76%**;
- cross-region hitting-time ratio: **6.81x**;
- robust seed × neighborhood pass fraction: **13/15 = 86.7%**;
- all registered synthetic gates passed.

This result is deliberately modest. It demonstrates that the implementation distinguishes a known weak bridge from a matched continuous control. It does not say that language-model representations contain analogous bridges.

## 4. First real-model test: the strong hypothesis fails immediately

The first real-model smoke test used `HuggingFaceTB/SmolLM2-135M`, pinned at revision `93efa2f097d58c2a74874c7e644dbc9b0cee75a2`. The registered observer was attention-masked mean pooling at the middle hidden layer. Three semantic axes were constructed with independent context and paraphrase holdouts:

- approval versus rejection;
- certainty versus uncertainty;
- increase versus decrease.

The graph was built without semantic labels. The Fiedler coordinate was oriented on the training poles only after extraction, then extended to held-out examples through local graph geometry.

The aggregate result was negative:

- median held-out Fiedler pole accuracy: **0.5625**;
- held-out bridge absolute-score / pole absolute-score ratio: **1.1034**;
- supervised centroid held-out accuracy: **0.7500**;
- shuffled-label accuracy: **0.5050**;
- scrambled-representation accuracy: **0.5000**;
- robust axis × graph-scale fraction: **0.0000**.

Only the negative controls passed.

This establishes the first important distinction of the paper:

\[
\text{semantic information present}
\not\Rightarrow
\text{semantic variable is the first spectral bottleneck}.
\]

The centroid baseline can decode the variable while the Fiedler mode is doing something else.

## 5. Observer sensitivity: causal endpoint states look very different

A post-hoc sensitivity analysis replaced mean pooling with the hidden state at the final non-padding token at the same middle layer. Everything else remained fixed.

The aggregate held-out Fiedler accuracy rose to **0.9375** and the median bridge ratio fell to **0.7446**. But the result was uneven:

- approval/rejection: **0.9375**;
- certainty/uncertainty: **1.0000**;
- increase/decrease: **0.5000**.

The all-axis hypothesis still failed.

This was not confirmation. It was a diagnostic showing that the observer is load-bearing. For an autoregressive model, the causal endpoint is a natural candidate state because it summarizes the prefix at the position from which the next-token distribution is computed. But choosing it after seeing the failure requires an independent test.

## 6. Fresh endpoint confirmation: confidence alone survives

A second corpus was frozen before inspection. It used new contexts, new paraphrase families, the same pinned 135M model, the causal endpoint observer, label-blind graph-scale selection by connectedness, token-length control, shuffled labels, and feature-marginal-preserving representation scrambling.

Three contrasts were preregistered:

1. stance/support versus opposition;
2. epistemic confidence versus uncertainty;
3. permission versus prohibition.

The generic hypothesis required all three to pass. It failed.

### 6.1 Stance

- selected `k`: **8**;
- train Fiedler pole accuracy: **0.6250**;
- held-out accuracy: **0.5000**;
- bridge ratio: **0.8460**;
- token-length accuracy: **0.5000**;
- supervised centroid accuracy: **1.0000**.

### 6.2 Epistemic confidence

- selected `k`: **8**;
- train Fiedler pole accuracy: **1.0000**;
- held-out accuracy: **0.9375**;
- bridge ratio: **0.7917**;
- token-length accuracy: **0.3125**;
- supervised centroid accuracy: **0.9375**;
- shuffled-label accuracy: **0.5038**;
- scrambled-representation accuracy: **0.3750**;
- conductance: **0.0191**;
- \(\mu_2\): **0.0244**.

All six confidence gates passed.

### 6.3 Permission

- selected `k`: **6**;
- train Fiedler pole accuracy: **0.5156**;
- held-out accuracy: **0.5000**;
- bridge ratio: **2.3201**;
- token-length accuracy: **0.5000**;
- supervised centroid accuracy: **1.0000**.

The contrast is especially informative because both stance and permission were perfectly decodable by a supervised centroid while remaining effectively absent from the first spectral mode. Linear decodability and graph bottleneck topology are therefore not interchangeable observables even on the same states.

## 7. Confidence transfers beyond explicit certainty vocabulary

The prospective confidence result motivated a harder realization-shift test. The training graph used exactly the 96 explicit-confidence training examples from the previous confirmation. The test set consisted of 24 new evidence descriptions in which confidence was implied through replication behavior and measurement agreement rather than directly named.

The test protocol rejected execution if any registered explicit certainty term appeared in a held-out sentence. The observed forbidden-term count was zero.

With the already registered causal endpoint observer and `k = 8`:

- train Fiedler pole accuracy: **1.0000**;
- implicit held-out accuracy: **0.8750**;
- implicit bridge ratio: **0.8638**;
- token-length accuracy: **0.6250**;
- supervised centroid accuracy: **0.8125**;
- shuffled-label accuracy: **0.5013**;
- scrambled-representation accuracy: **0.5625**;
- conductance: **0.0191**;
- \(\mu_2\): **0.0244**.

All five registered transfer gates passed. In this controlled realization shift, the label-blind spectral coordinate even slightly exceeded the supervised centroid baseline (`0.8750` versus `0.8125`).

At this stage it would have been tempting to promote epistemic confidence to a privileged spectral variable. The next experiments show why that would have been premature.

## 8. Larger-model replication and the layer-selection trap

The identical confidence-transfer protocol was run on `HuggingFaceTB/SmolLM2-360M` at pinned revision `f8027fd0eaeea54caa13c31d31b9fdc459c38b49`, using the exact middle layer.

It did not replicate:

- train Fiedler alignment: **0.4844**;
- implicit held-out accuracy: **0.6875**;
- bridge ratio: **1.3255**;
- token-length accuracy: **0.6250**;
- supervised centroid accuracy: **0.6250**;
- shuffled-label accuracy: **0.4875**;
- scrambled-representation accuracy: **0.4375**.

Because training alignment itself failed, this was not merely a weaker transfer result. Confidence was not the first spectral mode at that observer location.

An exploratory all-layer scan was then run on both models, reporting every layer rather than selecting only favorable ones. It found transient passing windows:

- 135M: layers **15–18 / 30**;
- 360M: layers **18, 20–21 / 32**.

The 135M layer `17/30 = 0.5667` and 360M layer `18/32 = 0.5625` looked strikingly aligned. That suggested a mechanistic hypothesis: perhaps confidence becomes the first low-frequency mode near 56% of model depth.

This pattern was exploratory. It required a fresh test before it could count as evidence.

## 9. Fresh relative-depth confirmation falsifies the 56% rule

The rule

\[
\ell^*=\operatorname{round}(0.56N)
\]

was frozen before a new corpus was inspected. No layer scan or layer selection was allowed. A third, completely fresh explicit-confidence training set and implicit evidence test set were generated, with the same `k = 8`, token-length baseline, shuffle control, representation-scramble control, and an additional requirement that the Fiedler coordinate align with the semantic pole on the fresh training graph.

### 9.1 SmolLM2-135M, layer 17/30

- train Fiedler pole accuracy: **0.5156**;
- implicit held-out accuracy: **0.7500**;
- bridge ratio: **0.7685**;
- token-length accuracy: **0.5000**;
- supervised centroid accuracy: **0.9375**;
- shuffled-label accuracy: **0.4900**;
- scrambled-representation accuracy: **0.5000**.

`Supported = false` because fresh training alignment failed.

### 9.2 SmolLM2-360M, layer 18/32

- train Fiedler pole accuracy: **0.4844**;
- implicit held-out accuracy: **0.5000**;
- bridge ratio: **1.0565**;
- token-length accuracy: **0.5000**;
- supervised centroid accuracy: **0.8750**;
- shuffled-label accuracy: **0.4963**;
- scrambled-representation accuracy: **0.3750**.

`Supported = false`.

The relative-depth hypothesis is therefore falsified by the fresh corpus. The earlier matching depth windows were properties of the exploratory realization, not a corpus-independent law.

Again, the supervised baselines matter. The 135M and 360M states still contained enough information for 93.75% and 87.5% centroid accuracy. What disappeared was specifically the claim that confidence was the graph's first large-scale connectivity mode.

## 10. Removing semantic labels: natural-text future uncertainty

After several controlled semantic corpora, continuing to invent new polarity sets would create increasing researcher degrees of freedom. The final experiment therefore removes human semantic labels entirely.

The repository itself supplied natural prose. The protocol deterministically selected at most one excerpt per eligible Markdown file, excluding experiment machinery and other registered infrastructure. Both models evaluated the same 160 source files. Each example was truncated to a fixed 64-token model window. The observed state was the final-layer causal hidden state at token position 31.

For each example we measured next-token predictive entropy at horizons

\[
H\in\{0,4,8,16\}
\]

under teacher forcing. The representation graph was built only from states at \(t\). The primary question was whether entropy at \(t+8\) was spectrally smoother than permutation controls and whether a cross-validated kNN predictor using state geometry beat a scalar ridge predictor that knew only entropy at \(t\).

The design includes an important positive control: entropy at \(H=0\) is directly downstream of the current final hidden state and should therefore exhibit local smoothness if the graph/statistic pipeline is functioning.

### 10.1 SmolLM2-135M

Current entropy behaved as expected:

- Rayleigh energy: **0.7186**;
- permutation lower-tail p: **0.0020**;
- low-frequency 10% power: **0.4100**;
- low-frequency enrichment p: **0.0020**.

At the preregistered primary horizon \(H=8\):

- Rayleigh energy: **0.9975**;
- spectral-smoothness permutation p: **0.3772**;
- low-frequency power: **0.0879**;
- low-frequency enrichment p: **0.6208**;
- kNN / current-entropy-baseline MSE ratio: **1.1064**;
- observed / scrambled-geometry energy ratio: **0.9854**.

Only the current-entropy positive-control gate passed.

### 10.2 SmolLM2-360M

Current entropy again supplied a strong positive control:

- Rayleigh energy: **0.6764**;
- permutation lower-tail p: **0.0020**;
- low-frequency 10% power: **0.4268**;
- low-frequency enrichment p: **0.0020**.

At \(H=8\):

- Rayleigh energy: **1.0175**;
- spectral-smoothness permutation p: **0.6487**;
- low-frequency power: **0.0806**;
- low-frequency enrichment p: **0.7106**;
- kNN / current-entropy-baseline MSE ratio: **1.1589**;
- observed / scrambled-geometry energy ratio: **1.0829**.

Again, only the current-entropy positive control passed.

The secondary horizons \(H=4\) and \(H=16\) also failed to show robust spectral organization in either model.

Thus, on these natural teacher-forced trajectories, the final causal representation graph at \(t\) does **not** organize the model's own predictive entropy several tokens into the future in the simple way proposed here.

## 11. What the negative results establish

The experimental sequence supports several conclusions more strongly than it supports the original spectral-bottleneck idea.

### 11.1 Decodability is not topology

A variable can be almost perfectly linearly recoverable while having chance-level alignment with the Fiedler vector. The stance, permission, and fresh-confidence confirmations provide direct examples.

A probe asks approximately:

\[
\text{Can a supervised decision surface recover } y \text{ from } h?
\]

A first-bottleneck claim asks something much stronger:

\[
\text{Is } y \text{ aligned with the weakest global connectivity mode of a graph built from } h?
\]

These questions should not be conflated.

### 11.2 Spectral smoothness is not the same as a first bottleneck

Failure of the Fiedler hypothesis does not rule out all spectral structure. A semantic variable may occupy several low-frequency modes, a local diffusion coordinate, or a spectrally smooth subspace without being \(\mu_2\)'s eigenvector. The present experiments mainly falsify the strong first-mode formulation.

Future spectral work should therefore report label-signal Dirichlet energy, cumulative low-frequency power, and multiscale diffusion stability before escalating to claims about a unique bottleneck.

### 11.3 Observer and corpus are part of the hypothesis

Mean pooling and causal endpoint observation produced radically different outcomes. The same causal endpoint and graph rule then produced a strong confidence result on one corpus and chance-level training alignment on another.

It is therefore incomplete to say that a model "has" a spectral semantic variable without specifying at least:

- checkpoint;
- layer/observer;
- token position or pooling rule;
- corpus and split;
- graph construction;
- neighborhood scale;
- kernel/normalization;
- spectral statistic;
- independent replication rule.

### 11.4 A positive control is essential

The natural-text entropy experiment is especially useful because the same graph/statistic that failed at future horizons strongly detected current entropy in both models. That pattern is harder to dismiss as a broken implementation: the instrument sees the relation when it should be easiest to see and loses it when the predictive claim becomes non-trivial.

### 11.5 Falsification changed the theory

The initial question was whether weak semantic bridges might be recoverable through Cheeger/Fiedler structure. After the full experiment sequence, the defensible claim is narrower:

> Spectral operators are useful diagnostics for representation geometry, but semantic meaning must not be identified with the first graph-Laplacian mode. Any semantic spectral claim must earn stability across corpus, observer, graph scale, checkpoint, and held-out behavior.

That is a stronger research programme precisely because it says what would count as failure.

## 12. Implications for the Semantic Atlas

These results do not falsify the Semantic Atlas or the manifold-aware extension as a whole. They falsify one proposed shortcut: treating low conductance or the first Fiedler cut as a generic semantic primitive.

The Atlas programme should therefore keep the following quantities separate:

1. **representation coordinates** — where states lie;
2. **local manifold/chart structure** — whether neighborhoods have reproducible low-dimensional geometry;
3. **linear/nonlinear decodability** — what variables can be recovered with fitted probes;
4. **spectral smoothness** — whether a variable varies slowly over the representation graph;
5. **first-bottleneck topology** — whether a variable aligns with the weakest global graph cut;
6. **transition dynamics** — what future states actually follow;
7. **control cost / semantic gravity** — how difficult it is to alter those trajectories.

The empirical error would be to infer item 7 from item 5, or item 5 from item 3, without direct measurement.

For the manifold-aware paper's Experiment M4, the recommended order is now:

1. validate graph construction on planted and resampled controls;
2. establish held-out spectral smoothness or diffusion stability before asking for a Fiedler cut;
3. report multiple low-frequency modes rather than only \(\mu_2\);
4. require independent corpus replication before naming a semantic bottleneck;
5. only then ask whether the spectral object predicts transition or intervention cost.

The natural future-entropy result also cautions against assuming that local geometry is automatically predictive at non-trivial horizons. If a semantic atlas is to approximate dynamics, velocity/history/action information may be load-bearing rather than optional augmentation of a position-only state.

## 13. Limitations

The experiments are intentionally small.

- Both checkpoints come from one model family.
- The controlled semantic corpora are constructed rather than naturally annotated.
- The natural-text experiment uses prose from one research repository and is not an external corpus replication.
- The main spectral graph uses one registered kNN/Gaussian construction at a time; other graph estimators may expose different structure.
- The natural future-entropy experiment uses teacher-forced continuation. Autonomous model generation may produce different dynamical regularities.
- We do not perform activation interventions in this paper.
- We do not test whether higher spectral modes or learned diffusion coordinates predict control cost.
- We do not claim that a negative Fiedler result proves the absence of a manifold.

These limitations point to specific follow-ups, but they should not be used to erase the negative results already obtained.

## 14. Reproducibility

The repository contains the full protocol sequence rather than only the final favored result.

Key files include:

- `experiments/semantic_atlas/spectral_bottleneck/experiment.py` — planted synthetic bottleneck;
- `real_model_experiment.py` — first registered real-model smoke;
- `observer_comparison.py` — explicitly post-hoc observer sensitivity;
- `confirmatory_endpoint.py` — fresh endpoint confirmation;
- `confidence_transfer.py` — explicit-to-implicit confidence transfer;
- `confidence_depth_scan.py` — exploratory all-layer scan;
- `relative_depth_confirmation.py` — fresh falsification of the 56% rule;
- `natural_future_entropy.py` — natural-text, label-free future-uncertainty test;
- `REAL_MODEL_FINDINGS.md`, `CROSS_MODEL_REPLICATION.md`, and `RELATIVE_DEPTH_CONFIRMATION.md` — chronological finding records;
- `.github/workflows/semantic-spectral-*.yml` and `.github/workflows/semantic-natural-future-entropy.yml` — executable CI protocols.

Model revisions and corpus manifests are recorded in result artifacts. Scientific gate failure is represented in `summary.json`; it does not masquerade as CI failure.

## 15. Conclusion

The experiment began with a plausible geometric intuition: perhaps a semantic atlas contains weak bridges that can be discovered through Cheeger-type graph structure. The synthetic benchmark showed that our machinery can recover such a bridge when one actually exists. The real models then supplied the more valuable lesson.

Some semantic distinctions were strongly decodable but not spectral bottlenecks. A particularly striking confidence result survived one prospective confirmation and an explicit-to-implicit realization shift, then failed a new corpus and cross-model relative-depth confirmation. A label-free natural-text experiment showed strong spectral organization of current predictive entropy but no corresponding organization of entropy four, eight, or sixteen tokens into the teacher-forced future.

The correct conclusion is therefore neither "semantic spectral geometry works" nor "representation geometry is useless." It is sharper:

> **Spectral geometry is a diagnostic, not a semantic oracle.**

The graph Laplacian can reveal genuine structure, but semantic meaning, dynamical relevance, and control cost must each be independently earned. In this setting, the first Fiedler bottleneck is too strong and too fragile to serve as a generic semantic primitive.

That negative result improves the Semantic Atlas programme. It replaces an attractive metaphor with a hierarchy of distinct, falsifiable claims and leaves a cleaner target for future work: reproducible local charts and spectral smoothness that predict held-out dynamics or intervention cost without relying on a privileged graph mode.

---

## Claim boundary

This paper reports small-model controlled experiments and one natural-text repository experiment. It does **not** establish that larger language models lack spectral semantic structure, that manifolds are absent, that graph Laplacians cannot be useful, or that all future-horizon geometry is unpredictable. It establishes that the specific strong hypotheses tested here—generic first-Fiedler semantic bottlenecks, a corpus-independent 56%-depth confidence bottleneck, and position-only spectral prediction of future entropy under the registered natural-text protocol—did not survive their strongest preregistered tests.
