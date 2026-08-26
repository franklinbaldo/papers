---
type: "Technical Paper"
title: "Beyond Query Performance Prediction: Does Cross-Model Embedding Geometry Transfer to Unseen Retrievers?"
description: "Falsification-driven position paper asking whether cross-model aligned residual geometry adds target-behavior-free predictive value for query-level retrieval failure on a completely held-out dense retriever, beyond modern QPP baselines."
tags: [dense-retrieval, query-performance-prediction, embeddings, representation-alignment, semantic-parallax, cold-start, formal-verification]
timestamp: 2026-08-26T02:55:00Z
---

# Beyond Query Performance Prediction: Does Cross-Model Embedding Geometry Transfer to Unseen Retrievers?

**Franklin Baldo**  
Independent Researcher  
franklinbaldo@gmail.com

---

> **Position paper and preregisterable experimental proposal after four adversarial revisions.** The original manuscript proposed that embedding models might be ordered as progressively clearer observers of a shared semantic structure. That claim did not survive scrutiny. A Lean companion records why several natural formalizations of “sees more” are vacuous or protocol-relative. Subsequent literature review also showed that paraphrase robustness, query-level error prediction, unsupervised dense-retriever selection, geometric query-performance prediction, cold-start model routing, and model–item interaction modeling are all established research areas. The surviving question is narrower: **does explicitly cross-model, post-alignment residual geometry provide incremental query-level predictive information for a completely held-out dense retriever, beyond the strongest target-behavior-free Query Performance Prediction (QPP) signals?** The proposed unit of practical value is the number of labeled target queries required for a behavior-trained predictor to match that zero-target-behavior advantage.

## Abstract

Dense retrieval provides a clean setting for testing whether cross-model representation geometry contains transferable information about model-specific failure. Query Performance Prediction (QPP) already estimates retrieval effectiveness without relevance judgments at prediction time. Recent dense-QPP methods perturb query embeddings or exploit the geometry of query and pseudo-relevant document embeddings; unsupervised retriever-selection methods choose among dense retrievers on unlabeled target corpora; mixture-of-retriever systems estimate per-query retriever trustworthiness; and supervised QPP methods explicitly study generalization under retriever shift. Therefore neither “geometry predicts retrieval difficulty,” “a new retriever can be evaluated without labels,” nor “per-query model selection” is a defensible novelty claim.

We isolate a stricter experiment. Given retrievers \(M_1,\ldots,M_n\), hold out one retriever \(M_*\) from all performance-supervised training. Using only an unlabeled shared calibration corpus, align its query/document representation space to a common cross-model frame. For each query, compute features describing how \(M_*\)'s aligned representation, local neighborhood, and ranking geometry depart from the consensus of source retrievers. A predictor relating those **cross-model residuals** to retrieval failure is trained only on source retrievers and then applied to \(M_*\), without observing any relevance judgment or task outcome from \(M_*\). The primary estimand is the incremental predictive value of these residuals over the best target-free QPP baseline under leave-one-retriever-out evaluation.

The experiment is deliberately easy to falsify. If modern within-retriever QPP, cross-retriever supervised QPP, or zero-shot retriever-selection signals explain all predictable variation, the proposed “semantic parallax” construct adds no scientific value and should be retired in this domain. If cross-model residuals provide reproducible incremental value, we quantify that value by a **label-equivalent crossover** \(k^*\): the smallest number of labeled queries from the held-out retriever required for a behavior-trained adaptation method to match the zero-target-behavior predictor. Cross-realization robustness is treated as a secondary stress test, not a novelty claim.

The paper's contribution is therefore not a new information order, a new QPP task, or a claim of universal semantic geometry. It is a sharp test of whether **cross-model aligned geometry contains behaviorally useful information about an unseen retriever that is not already available from target-local QPP signals**.

**Keywords:** dense retrieval, query performance prediction, embedding geometry, representation alignment, cold-start model evaluation, semantic parallax, label efficiency, model selection

---

## 1. The claim that survived

The motivating observer intuition was:

> Different embedding models may be different observations of partially shared semantic structure.

The first manuscript tried to turn this into an order: perhaps a stronger model “sees more” or resolves finer semantic structure. Four rounds of adversarial review removed progressively stronger versions of that claim.

The present paper does **not** ask which observer is globally better. It asks a narrower transfer question:

\[
\boxed{
\text{Does cross-model geometric disagreement predict the failures of an unseen retriever?}
}
\]

More specifically, let \(M_*\) be a dense retriever whose relevance judgments and per-query outcomes are unavailable during fitting. We permit access to:

- the frozen retriever itself or its embedding API;
- an unlabeled target corpus;
- target queries without relevance judgments;
- a shared unlabeled alignment/calibration corpus;
- a population of source retrievers for which training-time retrieval outcomes are available.

We forbid, in the strict condition:

- relevance judgments from \(M_*\)'s evaluation queries;
- aggregate target-benchmark scores for \(M_*\);
- anchor-query correctness/performance labels from \(M_*\);
- any fitting of the residual-to-performance map using outcomes from \(M_*\).

This is **zero target-behavior supervision**, not merely “zero-shot” in the looser routing sense.

The candidate signal is cross-model geometry after alignment. Its value is measured only after all strong target-free QPP baselines have been given the same unlabeled target data.

---

## 2. Why the original observer order failed

A machine-checked Lean 4 companion lives at:

`formalizations/semantic_observers/SemanticObservers.lean`.

Its purpose is a negative-result ledger, not a badge of formal sophistication.

### 2.1 Point-indexed deterministic Blackwell comparison generically collapses

For deterministic observers

\[
A:\Theta\to Z_A,
\qquad
B:\Theta\to Z_B,
\]

an exact deterministic garbling \(A\to B\) exists iff every fiber of \(A\) refines a fiber of \(B\):

\[
\exists g,\;g\circ A=B
\quad\Longleftrightarrow\quad
A(x)=A(y)\Rightarrow B(x)=B(y).
\]

The Lean theorem is `deterministicGarbling_iff_fiberRefines`.

Therefore, if \(A\) is injective on a finite benchmark, an unrestricted simulator can reproduce any \(B\) by memorizing the correspondence. If both observers are injective, exact garblings exist in both directions.

For high-dimensional floating-point embeddings on a finite benchmark, exact collisions are atypical. Thus choosing

\[
\Theta=\{\text{individual input items}\}
\]

makes unrestricted point-indexed comparison generically uninformative.

### 2.2 Restricted observer orders are task-relative

The Lean companion also gives a finite counterexample where

\[
A\succeq_{\mathcal D_1} B
\]

but

\[
B\succeq_{\mathcal D_2} A.
\]

Dominance on one decision family does not imply an intrinsic observer order.

### 2.3 Extractability depends on the rule class

Invertible coordinate changes preserve unrestricted information but need not preserve performance for a fixed restricted probe class. The formal companion proves invariance only when admissible rule classes correspond under pushforward/pullback and gives a finite counterexample otherwise.

These three results eliminate “semantic resolution order” as the primary thesis. They motivate an empirical question where the predictor is judged only by held-out behavior and where the target model is genuinely unseen behaviorally.

---

## 3. The prior-art boundary is much tighter than it first appears

The surviving experiment sits at the intersection of several mature literatures. A useful paper must state explicitly what is already occupied.

### 3.1 Query Performance Prediction already predicts per-query retrieval failure

QPP asks whether retrieval effectiveness for a query can be predicted without access to its relevance judgments at prediction time. This is a mature IR problem, not a new task introduced here.

For dense retrievers specifically, Arabzadeh et al. (2023) propose **Noisy Perturbations for Estimating Query Difficulty in Dense Retrievers**. They perturb a contextualized query representation and use ranking instability as an unsupervised performance signal.

Datta et al. (2025/2026) propose **Projection-Displacement-Based Query Performance Prediction for Embedded Space of Dense Retrievers (PDQPP)**. PDQPP explicitly exploits dense embedding geometry, projecting queries and pseudo-relevant documents into local subspaces and using projection displacement as a proxy for coherence and retrieval quality.

Thus:

> **Not novel:** using embedding geometry to predict per-query dense-retrieval performance without query relevance labels.

### 3.2 Zero-label dense-retriever selection is established

Khramtsova et al. (2023) formulate the problem of selecting which dense retriever to use on an unlabeled target collection. Their candidate signals include representation- and distribution-based measures; they also show that many intuitive unsupervised selection criteria perform poorly.

Khramtsova et al. (2024) introduce **LARMOR**, using an LLM to generate pseudo-queries, pseudo-relevance judgments, and reference rankings from the target corpus to rank dense retrievers without human target labels.

Thus:

> **Not novel:** deciding which dense retriever is likely to work on a target corpus without human relevance labels.

### 3.3 Per-query retriever mixing is established

Kalra et al. (2025) introduce **Mixture of Retrievers (MoR)**. It computes per-query, per-retriever trustworthiness signals before and after retrieval and uses them to weight heterogeneous retrievers in a zero-shot mixture.

Thus:

> **Not novel:** estimating per-query retriever suitability and using it to route or fuse retrieval systems.

### 3.4 Retriever-shift QPP is already a direct neighbor

Jung and Jeon (2025) explicitly study **QPP under retriever and concept shifts**. Their QPP-MLC predicts top-\(k\) document relevance and aggregates those predictions to query-level effectiveness.

This is particularly important prior art because it attacks the same generalization problem from the QPP side.

Thus:

> **Not novel:** training a performance predictor in one retrieval regime and asking it to generalize under a change of retriever.

### 3.5 Routing and psychometrics already model model–item interactions

EmbedLLM (Zhuang et al., 2025) learns compact model representations from a model-by-question correctness matrix and uses them for correctness forecasting and routing. Modern routers likewise estimate query–model compatibility and onboard new models using behavioral profiles, anchors, public model metadata, or interaction histories.

ZeroRouter (Yan et al., 2026) reduces model lock-in using a model-agnostic query space but still charts a newly introduced model with a small set of anchor queries. RouteProfile (Xu et al., 2026) studies cold-start routing from structured public model profiles, including descriptions, family information, and reported benchmark signals.

Psychometric approaches such as IRT and recent option-level LLM response models explicitly decompose ability, item difficulty, discrimination, and model–item interaction structure.

Thus:

> **Not novel:** predicting which model will fail on which item, nor learning compact behavioral profiles of models.

### 3.6 Representation similarity does not guarantee behavioral similarity

Friedman et al. (2023) show directly that common representation-similarity measures are not reliably aligned with functional/behavioral similarity in small Transformer models, and that conclusions depend on which representation is examined.

This is not merely background. It supplies a strong null expectation for the present proposal:

> cross-model geometry may simply fail to carry transferable behavior information.

### 3.7 Candidate novelty after these concessions

The literature review above leaves one deliberately narrow candidate contribution:

> **Cross-model aligned residual geometry as an incremental, target-behavior-free feature for per-query QPP on a completely held-out dense retriever, evaluated against modern target-local and cross-retriever QPP baselines.**

We have not identified prior work that makes this exact leave-one-retriever-out residual-transfer test the primary object. That absence is a literature-search result, not proof of novelty; the empirical programme is designed so that close prior methods are strong baselines rather than rhetorical foils.

---

## 4. Experimental object: behavior-free held-out retriever

Let

\[
\mathcal M=\{M_1,\ldots,M_n\}
\]

be a population of dense retrievers. Each retriever maps query text and document text to vectors in its own representation space.

Choose one target retriever

\[
M_*\in\mathcal M
\]

and remove **all target-retriever performance labels** from model fitting.

The remaining source set is

\[
\mathcal M_{- *}=\mathcal M\setminus\{M_*\}.
\]

### 4.1 Allowed unlabeled data

Let \(C_{align}\) be a corpus of texts shared across retrievers and containing no relevance judgments used in the evaluation target. Each retriever embeds the same texts:

\[
z_m(x)=E_m(x).
\]

An alignment

\[
T_m:Z_m\to Z_c
\]

is fit using only representation correspondence or geometry objectives.

For the held-out retriever \(M_*\), fitting \(T_*\) may use its embeddings on \(C_{align}\), but may not use any query-level retrieval effectiveness label.

This distinction is critical: **the retriever is held out behaviorally, not observationally**. We need its unlabeled representations in order to test whether those representations reveal useful information before behavior is observed.

### 4.2 Consensus and residual

For query \(q_i\), define a source-model consensus representation

\[
c_i
=
\operatorname{Agg}_{m\ne *} T_m(z_m(q_i)).
\]

The held-out model's aligned query residual is

\[
r_{*i}^{(q)}
=
T_*(z_*(q_i))-c_i.
\]

A richer cross-model residual feature family may include, subject to preregistration:

1. residual norm and low-dimensional residual coordinates learned only from source models;
2. disagreement of local query neighborhoods after alignment;
3. disagreement between the held-out retriever's query-to-document similarity profile and the source consensus;
4. rank-overlap and rank-displacement relative to source retrievers;
5. residual statistics over the top-\(k\) documents retrieved by \(M_*\);
6. query/document subspace-angle differences in the aligned frame.

Call the resulting feature vector

\[
p_{*i}=P(M_*,q_i,C_{align},C_{target}).
\]

We use “parallax” only as shorthand for this **cross-model residual feature family**. It is not assumed to be a new primitive of representation theory.

---

## 5. Outcome: what counts as an item-level error for an embedding retriever?

An embedding model does not itself answer a multiple-choice question. The natural behavioral unit is therefore retrieval performance per query.

For query \(q_i\), let

\[
y_{mi}
\]

be a held-out effectiveness measure for retriever \(M_m\), computed from relevance judgments that are unavailable to all predictors during target fitting.

Candidate continuous outcomes include:

- Reciprocal Rank at cutoff;
- nDCG@10;
- Recall@\(k\);
- Average Precision where judgments support it.

The primary analysis should select **one continuous metric in advance**, preferably nDCG@10 for graded relevance collections or RR@10 when first-hit success is operationally central.

A secondary binary endpoint may define

\[
Y_{mi}^{(\tau)}
=
\mathbf 1[y_{mi}\ge\tau]
\]

for a preregistered usefulness threshold \(\tau\). This permits calibrated probabilities and proper scoring rules, but it must not replace the continuous primary result merely because it gives a cleaner effect.

The target qrels are used **only for final evaluation and for the controlled \(k\)-label adaptation curve**.

---

## 6. The primary estimand: incremental value beyond QPP

Let

\[
Q_{*i}
\]

contain the strongest target-free QPP features available to the held-out retriever. Depending on the benchmark, these should include conventional score-distribution signals and modern dense-QPP methods.

Let \(f_Q\) be a predictor trained without target-retriever outcomes using \(Q\), and let \(f_{Q+P}\) additionally use cross-model residual features \(P\).

For a preregistered loss \(L\), define

\[
\boxed{
\Delta_P
=
L(f_Q)-L(f_{Q+P}).
}
\]

The primary hypothesis is

\[
H_1:\Delta_P>0
\]

under leave-one-retriever-out evaluation and independent test queries.

The null is

\[
H_0:\Delta_P\le0.
\]

This is the central scientific test. If \(H_0\) cannot be rejected with practically meaningful effect size, semantic parallax adds no useful information beyond QPP in this domain.

### 6.1 Do not compare against a weak QPP baseline

At minimum, the QPP baseline family must include:

- score-distribution QPP such as NQC or comparable classical baselines;
- Arabzadeh et al.'s noisy-perturbation dense-QPP signal;
- PDQPP or a faithful geometric dense-QPP implementation;
- a supervised source-trained QPP predictor;
- QPP-MLC or the closest reproducible retriever-shift QPP baseline;
- a MoR-style per-query retriever-trustworthiness signal when applicable.

The relevant baseline is the **best preregistered target-free system selected without target test labels**, not an arbitrary historical method.

### 6.2 Why this differs from ordinary within-model QPP

Within-model QPP asks whether properties of \(M_*\)'s query, scores, embeddings, and retrieved documents predict \(M_*\)'s effectiveness.

The present signal asks whether

\[
\text{how }M_*\text{ differs from other models on the same query}
\]

contains incremental predictive information after those target-local signals are already present.

If not, the observer metaphor has no empirical payoff here.

---

## 7. Leave-one-retriever-out protocol

For each target retriever \(M_*\):

1. **Remove target behavior.** Hide all relevance-derived outcomes for \(M_*\) from fitting, feature selection, hyperparameter choice, and alignment selection.
2. **Fit the common frame.** Fit \(T_m\) using only an unlabeled shared calibration corpus.
3. **Construct source residuals.** For each source model, define its residual relative to a consensus that excludes that model, preventing trivial self-inclusion.
4. **Train source predictor.** Fit the residual-to-performance relationship using source retrievers only.
5. **Freeze everything.** Alignment family, residual featurization, QPP baseline choice, and prediction model are frozen before target qrels are exposed.
6. **Apply to \(M_*\).** Produce per-query performance predictions using only target unlabeled embeddings, rankings, and corpus statistics.
7. **Evaluate once.** Reveal held-out qrels and compute predictive loss, ranking correlation, calibration, and downstream selection utility.
8. **Repeat for every retriever.** Each retriever becomes the behaviorally unseen target in turn.

Hyperparameter tuning must be nested inside the source-model folds. Otherwise the leave-one-model-out claim is illusory.

### 7.1 Architecture-family holdout

A stronger test leaves out an entire retriever family rather than one checkpoint:

\[
\mathcal F_*\cap\mathcal F_{train}=\varnothing.
\]

This distinguishes transfer to a genuinely new observer family from interpolation among nearly identical encoders.

### 7.2 Corpus/task holdout

A second orthogonal axis holds out the target retrieval collection. The strongest generalization cell is therefore:

\[
\text{new retriever family}
\times
\text{new target collection}.
\]

This cell is expected to be difficult. A negative result there should not be rescued by reporting only easier in-family cells.

---

## 8. The label-equivalent crossover \(k^*\)

Even a statistically significant \(\Delta_P\) may be operationally trivial. A few labeled target queries may allow an ordinary behavioral method to outperform it.

Let \(B_k\) be the best preregistered behavior-trained adaptation baseline given exactly \(k\) labeled queries from \(M_*\). Candidate methods include:

- a simple calibrated target-specific regression update;
- matrix-factorization/model-embedding methods in the spirit of EmbedLLM;
- IRT/Rasch-style model–item adaptation;
- anchor-query profiling analogous to cold-start routing;
- hierarchical shrinkage combining source population structure with \(k\) target labels.

Let

\[
L_0=L(f_{Q+P})
\]

be the zero-target-behavior loss of the best QPP-plus-parallax system.

For equivalence margin \(\epsilon\), define

\[
\boxed{
k^*
=
\min\left\{
k:
\mathbb E[L(B_k)]
\le
L_0+\epsilon
\right\}.}
\]

Expectation is taken over repeated stratified draws of the \(k\) labeled queries.

This number has a direct interpretation:

> \(k^*\) is the approximate number of target behavior labels that the target-free system is worth against a strong behavioral adaptation method.

It is an **operational value metric**, not the novelty claim.

### 8.1 Crossover must be reported as a curve

Report

\[
k\mapsto L(B_k)
\]

for a logarithmic or otherwise preregistered grid such as

\[
k\in\{0,5,10,20,50,100,200,500,1000\}.
\]

A single interpolated \(k^*\) hides variance and can be unstable near crossing points.

### 8.2 Practical interpretation

If a behavioral baseline with \(k=20\) labels already dominates the geometry-based predictor, the scientific finding may still be interesting, but the deployment case is weak.

If hundreds of target labels are needed before a behavior-trained method catches up, cross-model geometry has demonstrated a meaningful cold-start value.

---

## 9. Mandatory baselines and controls

### 9.1 Target-local QPP

These are the most important baselines because they have access to the same unlabeled target queries and rankings without needing any cross-model theory.

### 9.2 Cross-retriever QPP

QPP-MLC and comparable transfer-capable QPP systems test whether performance relationships learned elsewhere already generalize to the held-out retriever.

### 9.3 Unsupervised retriever selection

Khramtsova et al. (2023) and LARMOR provide aggregate model-selection baselines. Although they are not per-query predictors, they test whether the same operational decision can be solved without parallax.

### 9.4 Mixture/routing signals

MoR-style per-query retriever weights test whether standard pre/post-retrieval trust signals already capture the useful heterogeneity.

### 9.5 Behavioral model profiles

EmbedLLM-style factorization and IRT-style adaptation are required on the \(k\)-label curve because they convert observed model behavior into compact capability profiles.

### 9.6 Model identity and global capability

For source-model training, include model identity or hierarchical random effects, global source performance, model family, dimension, parameter count where meaningful, and public metadata as nuisance covariates.

However, the strict held-out condition may **not** use target-benchmark aggregate accuracy/effectiveness for \(M_*\), because that is target behavior supervision in compressed form.

### 9.7 Same-recipe seed null

When multiple training seeds/checkpoints are available for the same retriever recipe, estimate the variability of residual and QPP effects among nominally equivalent observers. Cross-model effects smaller than this floor are not interpreted as meaningful observer specificity.

---

## 10. What exactly is “parallax” here?

The term should carry no metaphysical weight.

For this paper, **cross-model retrieval parallax** means only:

> a feature of a held-out retriever's representation or ranking that is defined relative to a common frame or source-model consensus, and whose predictive value is evaluated incrementally beyond target-local QPP signals.

A residual is not parallax merely because it is nonzero.

A valid feature must satisfy all of the following:

1. alignment uses no target relevance labels;
2. feature construction uses no target behavior labels;
3. residual-to-performance mapping is trained only on source retrievers;
4. predictive value is tested on untouched target queries;
5. incremental gain is measured over strong target-local QPP baselines;
6. the effect survives reasonable changes in alignment capacity;
7. the effect replicates across several held-out retrievers.

If condition 5 fails, the special name is unnecessary: the residual is simply another geometric quantity already subsumed by QPP.

---

## 11. Alignment is a nuisance axis, not a hidden tuning knob

Cross-model residuals depend on how spaces are aligned. Therefore the paper must report an alignment-capacity curve rather than choose one favorable map.

Candidate ladder:

\[
\text{orthogonal Procrustes}
\rightarrow
\text{linear map}
\rightarrow
\text{multi-way shared frame}
\rightarrow
\text{small nonlinear map}
\rightarrow
\text{unpaired/shared-latent method where justified}.
\]

For each class \(a\), report

\[
\Delta_P(a).
\]

Three outcomes have different meanings:

- **stable positive \(\Delta_P(a)\):** residual behavior is not an artifact of one alignment capacity;
- **vanishing \(\Delta_P(a)\) with stronger alignment:** the apparent parallax was mostly alignment error;
- **increasing gain only with highly flexible aligners:** likely overfitting unless correspondence evaluation independently supports the aligner.

All alignment choices are made without target qrels.

---

## 12. Cross-realization robustness is secondary

Earlier versions of this paper centered realization protocols

\[
X\sim\nu(\cdot\mid\theta)
\]

such as lexical paraphrase, context change, and register shift.

That remains useful, but robustness transfer across perturbation families has extensive prior art and often fails. It is therefore a **stress test**, not a novelty claim.

If two independently generated semantic-preserving realization families \(\nu_j\) and \(\nu_k\) are available, evaluate:

\[
\Delta_P^{\nu_j\to\nu_k}.
\]

A positive cross-realization effect would strengthen the interpretation that residuals capture more than generator-specific artifacts. A negative result is expected enough that it should not invalidate an otherwise positive within-distribution leave-one-retriever-out result.

Realization generators must remain independent of tested retrievers, and semantic preservation must be audited independently.

---

## 13. Evaluation metrics

QPP has traditionally used correlation with true query effectiveness. Correlation alone is insufficient for this paper because \(k^*\) requires a loss with operational meaning.

Report at least:

1. **MAE or RMSE** for continuous per-query effectiveness prediction;
2. **Spearman correlation** with true per-query effectiveness, for comparability with QPP literature;
3. **calibration/proper scoring loss** for any binary success endpoint;
4. **routing/selection regret** if predictions are used to choose among retrievers;
5. **paired bootstrap confidence intervals** for \(\Delta_P\);
6. **effect heterogeneity** across target retrievers and collections.

No result is considered confirmatory if the gain is driven by one target retriever or one dataset after model selection.

---

## 14. Suggested benchmark design

A practical first study can use public dense retrievers and BEIR/MTEB retrieval collections because they provide a diverse retriever population, shared text inputs, and query-level relevance judgments for final evaluation.

### 14.1 Retriever population

Include retrievers spanning:

- different training objectives;
- different architecture families;
- general versus domain-specialized models;
- multiple embedding dimensions;
- at least one family with several related checkpoints or seeds when possible.

Avoid a population dominated by near-duplicates, which would make leave-one-model-out artificially easy.

### 14.2 Alignment corpus

Use a frozen corpus disjoint from target qrels and, preferably, disjoint from final target collections. The same text identities may be embedded by every retriever to support paired alignment; an unpaired alignment baseline can be added but is not necessary for the first test.

### 14.3 Retrieval collections

Use several collections with materially different domains and query styles. Report both:

- retriever-held-out / collection-seen-among-sources;
- retriever-held-out / collection-held-out.

### 14.4 Pre-registration

Freeze before revealing target outcomes:

- retriever population;
- target folds;
- alignment corpus;
- residual feature family;
- QPP baseline family;
- primary outcome;
- predictive loss;
- alignment-capacity ladder;
- \(k\) grid;
- equivalence margin \(\epsilon\).

---

## 15. Hypotheses and falsifiers

### H1 — Incremental cross-model geometric value

**Hypothesis.** Cross-model aligned residual features improve prediction of per-query effectiveness for a behaviorally held-out retriever beyond the strongest preregistered target-free QPP baseline:

\[
\Delta_P>0.
\]

**Falsified if.** The gain is non-positive, inside the same-seed/null floor, or fails across held-out retrievers.

This is the paper's primary hypothesis.

### H2 — Family-level generalization

**Hypothesis.** The incremental value survives when an entire retriever architecture/training family is held out.

**Falsified if.** Gains exist only when the target is a near-neighbor of source retrievers.

### H3 — Operational label value

**Hypothesis.** The target-free predictor has nontrivial label-equivalent value \(k^*\) against strong behavioral adaptation baselines.

**Falsified as a deployment claim if.** Very small \(k\) values consistently dominate the target-free system.

A small \(k^*\) does not falsify H1; it says the geometric signal is cheap to replace.

### H4 — Alignment robustness

**Hypothesis.** \(\Delta_P\) remains positive across a preregistered range of non-destructive alignment classes.

**Falsified if.** Predictive value disappears once alignment quality improves or exists only under one tuned alignment.

### H5 — Cross-realization robustness

**Hypothesis.** Some predictive value transfers across structurally distinct semantic-preserving realization protocols.

**Status.** Secondary replication/stress test, with a strong prior that transfer may be weak.

---

## 16. What would count as a positive paper?

A convincing positive result would look like this:

1. PDQPP, noisy-perturbation QPP, QPP-MLC, and other preregistered target-free baselines establish a strong floor.
2. Adding cross-model aligned residual features reduces held-out prediction loss by a reproducible amount across multiple target retrievers.
3. The gain survives architecture-family holdout and at least one collection shift.
4. The effect is not explained by retriever identity, model family, dimension, global source capability, or alignment error.
5. The \(k\)-curve shows that the gain is not immediately replaced by a trivial handful of target qrels.

Only then is it reasonable to say:

> cross-model representation geometry contains transferable information about retriever-specific failure that is not captured by ordinary target-local QPP.

Even this result would **not** establish a universal semantic geometry or a hierarchy of semantic observers.

---

## 17. A negative result is arguably the cleaner result

Several negative outcomes are scientifically useful.

### 17.1 QPP subsumes parallax

If

\[
\Delta_P\approx0,
\]

then target-local geometric/ranking signals already contain everything useful that cross-model residuals reveal. The special parallax construct should be retired for retrieval.

### 17.2 Residuals interpolate but do not transfer

If gains vanish on architecture-family holdout, the predictor has learned family identity rather than a transferable relation between geometry and failure.

### 17.3 Geometry is behaviorally weak

This would align with Friedman et al.'s broader warning that representational similarity need not track functional similarity.

### 17.4 Geometry has signal but little economic value

If \(\Delta_P>0\) but \(k^*\) is tiny, the scientific effect is real but operationally cheap to replace with direct behavior measurement.

### 17.5 Cross-realization transfer fails

This would reproduce a common robustness pattern: robustness or predictability under one perturbation family need not transfer to another.

A negative paper can therefore make a precise statement about the boundary between representational analysis and performance prediction.

---

## 18. Relation to the original Semantic Observer programme

The original observer metaphor can survive only in a weak, operational sense.

The Lean ledger rules out easy claims that one injective embedding “contains more” than another on a finite item-indexed benchmark. QPP prior art rules out the claim that local geometry predicting failure is itself novel. Routing and psychometrics rule out the claim that item-specific model failure prediction is novel.

What remains testable is whether **relations among observers** contribute information unavailable from each observer considered locally.

In this paper, that question becomes:

\[
\boxed{
I(\text{cross-model residual};\text{target retrieval failure}\mid\text{best target-local QPP})>0?
}
\]

The notation is conceptual rather than an instruction to estimate conditional mutual information directly. The empirical estimand is the held-out predictive improvement \(\Delta_P\).

If the answer is no, the observer programme should not invoke semantic parallax to explain retrieval behavior. If the answer is yes, the result motivates a later investigation of *why* cross-model residuals carry the extra signal.

---

## 19. Relation to Semantic Atlas, Pontifex, and Perquire

This narrower paper should not borrow novelty from adjacent projects.

For the **Semantic Atlas**, a positive result would suggest that uncertainty about a region can depend on disagreement among multiple embedding observers rather than one geometry alone. It would not establish navigational dynamics.

For **Pontifex**, cross-observer residuals remain a candidate interpretability signal, but the retrieval experiment supplies a much harder prerequisite: residual information must first predict behavior beyond strong local baselines.

For **Perquire**, the most direct implication is retriever selection or confidence estimation. Again, this is downstream engineering value, not part of the present novelty claim.

---

## 20. Conclusion

Four adversarial revisions progressively removed the attractive but weak claims from the Semantic Observer idea.

- deterministic point-indexed information orders collapse under injectivity;
- restricted task orders are benchmark-relative;
- extractability depends on the probe class;
- paraphrase robustness is established prior art;
- per-item model failure prediction is established in routing and psychometrics;
- dense-retriever failure prediction without qrels is the mature QPP problem;
- embedding geometry is already used by dense-QPP methods;
- unsupervised dense-retriever selection and per-query retriever weighting already exist;
- retriever-shift QPP is already an explicit research topic.

The surviving question is therefore intentionally small:

\[
\boxed{
\text{Does cross-model aligned geometry add anything beyond the best target-free QPP for an unseen retriever?}
}
\]

The primary number is \(\Delta_P\), the incremental held-out predictive value. The operational number is \(k^*\), the number of target behavior labels required to replace that zero-target-behavior advantage.

If \(\Delta_P\le0\), semantic parallax adds nothing in this domain and should be retired. If \(\Delta_P>0\) but \(k^*\) is tiny, it is scientifically interesting but practically weak. Only a reproducible positive \(\Delta_P\) with nontrivial \(k^*\), surviving retriever-family and dataset holdout, would justify a stronger positive claim.

That is a much smaller paper than the original “semantic observers” proposal. It is also the first version whose central experiment is not obviously already contained in the surrounding literature.

---

## References

Achara, N., et al. (2026). **Multi-Way Representation Alignment.** arXiv:2602.06205.

Arabzadeh, N., Hamidi Rad, R., Khodabakhsh, M., & Bagheri, E. (2023). **Noisy Perturbations for Estimating Query Difficulty in Dense Retrievers.** CIKM 2023. https://doi.org/10.1145/3583780.3615270

Blackwell, D. (1951). **Comparison of Experiments.** Proceedings of the Second Berkeley Symposium on Mathematical Statistics and Probability, 93–102.

Blackwell, D. (1953). **Equivalent Comparisons of Experiments.** Annals of Mathematical Statistics, 24(2), 265–272.

Datta, S., Faggioli, G., Ferro, N., Ganguly, D., Muntean, C. I., Perego, R., & Tonellotto, N. (2025/2026). **Projection-Displacement-Based Query Performance Prediction for Embedded Space of Dense Retrievers.** ACM Transactions on Information Systems, 44(1). https://doi.org/10.1145/3765617

Friedman, D., Lampinen, A. K., Dixon, L., Chen, D., & Ghandeharioun, A. (2023). **Comparing Representational and Functional Similarity in Small Transformer Language Models.** UniReps, NeurIPS Workshop 2023.

Geirhos, R., Meding, K., & Wichmann, F. A. (2020). **Beyond Accuracy: Quantifying Trial-by-Trial Behaviour of CNNs and Humans by Measuring Error Consistency.** NeurIPS 2020.

Gröger, F., Wen, S., & Brbić, M. (2026). **Revisiting the Platonic Representation Hypothesis: An Aristotelian View.** ICML 2026. arXiv:2602.14486.

Huh, M., Cheung, B., Wang, T., & Isola, P. (2024). **Position: The Platonic Representation Hypothesis.** ICML 2024, PMLR 235.

Jha, R., Zhang, C., Shmatikov, V., & Morris, J. X. (2025). **Harnessing the Universal Geometry of Embeddings.** NeurIPS 2025. arXiv:2505.12540.

Jung, J., & Jeon, J. J. (2025). **Generalizing Query Performance Prediction under Retriever and Concept Shifts via Data-driven Correction.** CIKM 2025, 1261–1271. https://doi.org/10.1145/3746252.3761404

Kalra, J. S., Zhao, X., Kim, T. E., Cai, F., Diaz, F., & Wu, T. (2025). **MoR: Better Handling Diverse Queries with a Mixture of Sparse, Dense, and Human Retrievers.** EMNLP 2025, 11971–11990. arXiv:2506.15862.

Khramtsova, E., Zhuang, S., Baktashmotlagh, M., Wang, X., & Zuccon, G. (2023). **Selecting which Dense Retriever to use for Zero-Shot Search.** SIGIR-AP 2023. arXiv:2309.09403.

Khramtsova, E., Zhuang, S., Baktashmotlagh, M., & Zuccon, G. (2024). **Leveraging LLMs for Unsupervised Dense Retriever Ranking.** SIGIR 2024. arXiv:2402.04853.

Le Cam, L. (1964). **Sufficiency and Approximate Sufficiency.** Annals of Mathematical Statistics, 35(4), 1419–1455.

Torgersen, E. (1991). **Comparison of Statistical Experiments.** Cambridge University Press.

Xu, J., Pu, H., Feng, T., Zhang, H., You, J., & Liu, G. (2026). **RouteProfile: Elucidating the Design Space of LLM Profiles for Routing.** arXiv:2605.00180.

Yan, C., Zhang, W., Ning, Z., Xu, F., Tao, Z., Zhang, L., et al. (2026). **Breaking Model Lock-in: Cost-Efficient Zero-Shot LLM Routing via a Universal Latent Space.** AAAI 2026, 40(43), 36483–36490.

Zhuang, R., Wu, T., Wen, Z., Li, A., Jiao, J., & Ramchandran, K. (2025). **EmbedLLM: Learning Compact Representations of Large Language Models.** ICLR 2025.
