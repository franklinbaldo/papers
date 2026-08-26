---
type: "Technical Paper"
title: "Geometric Parallax for Held-Out Dense Retrievers: Does Cross-Model Geometry Predict Query-Specific Failure?"
description: "Short paper proposing a leave-one-retriever-out test of whether cross-model aligned geometry predicts query-specific retrieval effectiveness for a completely held-out dense retriever beyond target-free QPP, with label-equivalent crossover and fine-tuning intervention as secondary tests."
tags: [dense-retrieval, query-performance-prediction, representation-alignment, semantic-parallax, model-interaction, zero-shot-evaluation]
timestamp: 2026-08-26T02:40:00Z
---

# Geometric Parallax for Held-Out Dense Retrievers: Does Cross-Model Geometry Predict Query-Specific Failure?

**Franklin Baldo**  
Independent Researcher  
franklinbaldo@gmail.com

---

> **Short position/measurement paper.** This paper deliberately narrows an earlier “semantic observers” programme after adversarial review. It does not propose a new decomposition of retrieval difficulty, a new query-performance-prediction (QPP) task, or a new information order over embedding models. Its sole positive claim is empirical and falsifiable: cross-model geometry may contain query-specific information about a completely held-out dense retriever that is not already captured by target-free QPP computed from that retriever itself.

## Abstract

Query-specific retrieval effectiveness varies substantially across systems, topics, corpora, and query formulations. Information-retrieval research has long modeled these effects through topic difficulty, system-topic interactions, ANOVA, average average precision, and query-performance prediction. Modern dense-retrieval QPP goes further by exploiting the geometry, perturbation robustness, projection, and displacement of a retriever's own embeddings. In parallel, model-routing and psychometric work predicts model-item outcomes from behavioral profiles, while representation-similarity studies caution that geometric similarity need not track behavior.

This leaves a narrower question. Suppose a dense retriever has never contributed relevance judgments or query-level effectiveness labels to training. Can its **position relative to a population of other retrievers**, after cross-model representation alignment, predict which queries it will handle well or poorly better than the strongest target-free QPP methods that are allowed to inspect the held-out retriever's own embeddings and ranked lists?

We call the candidate signal **geometric parallax**: the query-specific, retriever-specific residual of a held-out retriever relative to a cross-retriever consensus representation. The primary experiment is leave-one-retriever-out. All aligners and residual-to-performance mappings are fitted on source retrievers only. At test time, the target retriever contributes embeddings and rankings but **zero relevance judgments and zero query-level performance labels**. The main statistic is incremental predictive value over target-free QPP. If this increment is not positive and reproducible across retrievers and collections, the parallax claim is rejected.

A secondary operational statistic, the label-equivalent crossover \(k^*\), asks how many labeled queries from the held-out retriever a behavior-supervised predictor needs before it matches the zero-label geometric method. A final intervention compares a base retriever with a fine-tuned descendant and tests whether geometry predicts the query-specific performance change caused by fine-tuning. Together these experiments distinguish a genuinely cross-model signal from a re-description of ordinary query difficulty.

**Keywords:** dense retrieval, query performance prediction, representation alignment, retriever shift, zero-shot model evaluation, system-query interaction, semantic parallax

---

## 1. The claim after cutting the framework down

The original observer intuition was that different embedding models might be viewed as partially different measurements of shared semantic structure. That framing generated useful negative results but too much machinery for the surviving empirical question.

This paper therefore asks only:

\[
\boxed{
\text{Does cross-model geometry predict held-out retriever failure beyond target-free QPP?}
}
\]

The domain is dense retrieval because an embedding model by itself does not produce an obvious item-level correctness variable, while a retriever produces a standard per-query effectiveness outcome such as AP, RR, or nDCG.

Let

\[
y_{mi}
\]

be the measured effectiveness of retriever \(m\) on query \(i\). The matrix \(Y=[y_{mi}]\) is known during evaluation but withheld according to the protocol below.

The paper does **not** claim novelty for decomposing \(Y\). Topic effects, system effects, system-topic interactions, query formulations, corpora, and their interactions are established IR objects. Nor does it claim novelty for predicting query difficulty from one retriever's embedding geometry. The claim concerns information that appears only when the target retriever is compared with a population of other retrievers.

---

## 2. Prior art that defines the boundary

### 2.1 Topic difficulty and system-topic interaction already exist

Average Average Precision (AAP) has long summarized topic difficulty as average effectiveness across a population of systems. More recent IR work explicitly models topic, system, corpus, query formulation, and interaction effects using ANOVA.

Culpepper, Faggioli, Ferro, and Kurland's *Topic Difficulty: Collection and Query Formulation Effects* shows that topic and query-formulation effects can be larger than system effects and reports substantial topic-system and topic-corpus interactions. Their analysis also emphasizes that difficulty is not an intrinsic scalar property of an information need independent of system, corpus, and formulation.

Accordingly, a decomposition such as

\[
y_{mi}=\mu+\alpha_m+\beta_i+\gamma_{mi}
\]

is not a contribution. The only scientifically interesting part here is whether the interaction \(\gamma_{mi}\) has **out-of-sample geometric predictability for an unseen retriever**.

### 2.2 Trial-by-trial error structure already exists

Geirhos, Meding, and Wichmann introduced error consistency precisely because marginal accuracy is insufficient to characterize whether systems fail on the same items. Therefore this paper does not claim novelty for item-level agreement or disagreement itself.

### 2.3 Behavioral model-item prediction is mature

Model routing and psychometrics already predict whether a particular model will succeed on a particular item. EmbedLLM learns compact model vectors from correctness matrices and evaluates correctness forecasting and routing. ICL-Router similarly uses model-performance profiles to predict whether a candidate model will answer a query correctly. Item-response and nominal-response models factor model ability, item difficulty, discrimination, and residual interaction structure.

These methods establish a strong behavioral baseline but generally learn the target model's profile from observed performance data.

### 2.4 Representation similarity does not automatically imply behavioral similarity

Friedman et al. show that representational similarity in small Transformers is not consistently correlated with behavioral similarity and depends on the representation being compared. This is a direct prior against the present hypothesis. A geometric residual is not presumed to have behavioral meaning; it must demonstrate it out of sample.

### 2.5 Dense-retrieval QPP already exploits embedding geometry

Modern QPP methods predict per-query retrieval effectiveness without relevance judgments at inference time. Dense-QPP based on noisy perturbations estimates query difficulty by perturbing query embeddings and measuring retrieval robustness. Projection-displacement QPP (PDQPP) explicitly uses the geometry of the dense retriever's own embedded space. Other methods use rank-score distributions, retrieved-document coherence, pseudo-feedback, or learned query-document features.

Therefore the claim is **not**:

> embedding geometry predicts query difficulty.

That is established prior art.

### 2.6 QPP under retriever shift and zero-label retriever selection already exist

QPP-MLC explicitly addresses generalization under retriever and concept shift. LARMOR ranks dense retrievers using target-corpus pseudo-relevance signals without test labels. These works mean that “no qrels for the target retriever” is also not by itself a novelty claim.

The remaining gap is whether **relative cross-retriever geometry** supplies per-query information beyond what target-free methods already extract from the held-out retriever in isolation.

---

## 3. Setup

Let

\[
\mathcal M=\{1,\ldots,M\}
\]

be a set of dense retrievers evaluated on a common query set \(\mathcal Q\) and corpus \(\mathcal C\).

For query \(i\) and retriever \(m\), let

\[
q_{mi}\in\mathbb R^{d_m}
\]

be its query embedding. Depending on the model, document embeddings or top-ranked document embeddings may also be used.

Let

\[
y_{mi}\in\mathbb R
\]

be query-level effectiveness, for example AP, RR@10, or nDCG@10.

### 3.1 Leave-one-retriever-out split

For each target retriever \(t\), define

\[
\mathcal M_{train}=\mathcal M\setminus\{t\}.
\]

All supervised fitting that uses effectiveness labels is restricted to \(\mathcal M_{train}\).

For the held-out retriever \(t\):

- no \(y_{ti}\) may be used to fit the alignment;
- no \(y_{ti}\) may be used to fit the residual-to-performance predictor;
- no aggregate target accuracy/MAP may be used as a capability feature in the zero-shot condition;
- its embeddings and ranked lists may be used because target-free QPP baselines are also allowed to inspect them.

This is the central anti-leakage rule.

### 3.2 Common comparison frame

Let

\[
T_m:\mathbb R^{d_m}\to\mathbb R^p
\]

be an alignment learned without target effectiveness labels. Candidate aligners include paired orthogonal Procrustes, linear maps, GPA/GCPA, relative representations, and stronger nonlinear maps, provided their capacity is registered before the final test.

For each query \(i\), define the source-observer consensus

\[
c_{-t,i}=\operatorname{Agg}_{m\ne t} T_m(q_{mi}).
\]

For held-out retriever \(t\), define its geometric residual

\[
r_{ti}=T_t(q_{ti})-c_{-t,i}.
\]

The term **parallax** refers only to predictive structure in \(r_{ti}\), not to the residual being nonzero.

---

## 4. Primary hypothesis: incremental zero-label prediction

Let

\[
B_{ti}
\]

be the strongest registered target-free QPP feature set for retriever \(t\). It should include modern dense-retrieval baselines such as perturbation robustness and projection/displacement geometry whenever reproducible implementations are available.

Let

\[
G_{ti}=\phi(r_{ti},c_{-t,i},\text{cross-retriever geometric summaries})
\]

be geometric-parallax features.

Train on source retrievers only:

\[
\hat y^{B}_{mi}=f_B(B_{mi}),
\]

and

\[
\hat y^{B+G}_{mi}=f_{BG}(B_{mi},G_{mi}).
\]

Freeze both predictors and evaluate on held-out retriever \(t\).

Define

\[
\Delta_P
=
L(\hat y^B_t,y_t)
-
L(\hat y^{B+G}_t,y_t),
\]

where \(L\) is a preregistered query-level prediction loss or rank-prediction loss.

### H1 — Cross-retriever geometric increment

\[
\boxed{\Delta_P>0}
\]

on held-out retrievers, with uncertainty excluding zero after aggregation over retrievers, collections, and random seeds.

### Kill condition

If the cross-model geometric features do not improve over the strongest target-free QPP baseline on independent held-out retrievers/collections, then **semantic parallax is retired as an IR prediction claim**.

There is no fallback claim that the decomposition itself is novel.

---

## 5. Operational value: label-equivalent crossover \(k^*\)

Even a statistically positive \(\Delta_P\) can be operationally trivial. Behavioral calibration labels may be cheap.

For the held-out retriever \(t\), allow a supervised behavioral baseline to observe \(k\) labeled query outcomes

\[
\{(i,y_{ti})\}_{i\in S_k}.
\]

Fit a registered family of predictors using those labels. Baselines should include at least:

- a hierarchical model with retriever ability, query difficulty, and interaction terms;
- matrix-factorization / EmbedLLM-style latent interaction models adapted to retrieval effectiveness;
- simple ridge/logistic/ranking regressors on standard QPP features;
- where appropriate, IRT-like models for discretized success outcomes.

Define

\[
k^*
=
\min\{k:L(\hat y^{behavior}_{t,k},y_t)
\le
L(\hat y^{B+G}_{t,0},y_t)\}.
\]

The zero subscript emphasizes that the geometric method has received no target effectiveness labels.

The interpretation is straightforward:

> \(k^*\) is the number of target-retriever labels that the cross-model geometric signal is worth under the registered protocol.

A small \(k^*\) does not falsify H1, but it limits practical importance.

---

## 6. Interventional test: fine-tuning-induced interaction shift

The observational experiment can still confuse architecture family, training corpus, and latent model ancestry. A fine-tuning intervention gives a cleaner test.

Let \(m_0\) be a base dense retriever and \(m_1\) a fine-tuned descendant trained on a declared objective/domain intervention.

For each query \(i\), define the performance change

\[
\Delta y_i=y_{m_1 i}-y_{m_0 i}
\]

and geometric change relative to a fixed external retriever population

\[
\Delta r_i=r_{m_1 i}-r_{m_0 i}.
\]

### H2 — Geometric prediction of intervention response

A model trained only on other base/fine-tune pairs should predict query-specific \(\Delta y_i\) from \(\Delta r_i\) above target-free single-retriever QPP changes.

This asks a stronger question than whether a hard query remains hard:

> does the representation change induced by an intervention identify **which queries gain or lose effectiveness because of that intervention**?

### Kill condition for the intervention claim

If \(\Delta r\) does not improve prediction of \(\Delta y\) beyond the best target-free QPP delta baseline across independent fine-tuning interventions, no causal interpretation of parallax is supported.

---

## 7. Required baselines

A credible experiment should include four baseline families.

### 7.1 Query-performance prediction

At minimum:

- classical post-retrieval score-distribution QPP;
- dense-retrieval perturbation QPP;
- PDQPP or an equivalent projection/displacement method;
- a shift-aware learned QPP baseline such as QPP-MLC where protocol compatibility permits.

### 7.2 Population-level topic difficulty

Include AAP-like cross-system query difficulty computed **only from source retrievers**. This tests whether the geometric model merely reconstructs the source-pool mean difficulty.

### 7.3 Behavioral interaction models

For \(k^*\):

- matrix factorization / EmbedLLM-style interaction prediction;
- hierarchical system-query effects;
- ability+difficulty models where the outcome supports them.

### 7.4 Geometry controls

Compare parallax with:

- target retriever's own query embedding alone;
- target retriever's own QPP geometry alone;
- distance to source centroid without alignment residual features;
- random/shuffled cross-retriever correspondence;
- same-architecture seed variation where available.

---

## 8. Statistics and evaluation

### 8.1 Unit of generalization

Queries are not the only independent unit. The positive claim is about **new retrievers**, so leave-one-retriever-out performance is primary.

Report both:

- per-target-retriever prediction quality;
- hierarchical or bootstrap uncertainty across target retrievers and collections.

### 8.2 Metrics

Use at least one absolute metric and one rank metric, for example:

- MAE/MSE for effectiveness prediction;
- Pearson correlation;
- Spearman or Kendall correlation;
- pairwise ordering accuracy for query difficulty.

The primary metric must be preregistered.

### 8.3 Significance of incremental value

Evaluate \(\Delta_P\) by paired resampling at the query level nested within held-out retriever, then aggregate across retrievers. A positive mean with one favorable retriever is insufficient.

### 8.4 Multiple alignment capacities

Because residual magnitude depends on the aligner, report a small registered capacity ladder such as

\[
\text{orthogonal}\rightarrow\text{linear}\rightarrow\text{shallow nonlinear}.
\]

The claim concerns predictive value that is not an obvious artifact of one arbitrarily weak alignment.

---

## 9. Secondary stress test: query reformulations

Query reformulation is established prior art and is not the novelty claim. It is useful as a stress test because IR work shows that formulation can strongly change effectiveness.

For a subset of information needs with multiple independently validated query formulations, ask whether a parallax predictor trained on one formulation family transfers to another.

The null expectation should be conservative: robustness often fails to transfer across perturbation families. Failure here does not rescue or kill H1; it only bounds the generality of the signal.

---

## 10. What would count as a meaningful positive result?

The strongest result would have four properties:

1. \(\Delta_P>0\) against modern target-free dense-QPP baselines for most held-out retrievers;
2. the gain replicates on an independent collection and model family;
3. \(k^*\) is large enough that geometry substitutes for a nontrivial amount of target labeling;
4. fine-tuning-induced geometric changes predict query-specific effectiveness changes out of sample.

That result would justify a modest conclusion:

> **Cross-model representation geometry contains retriever-specific information about query effectiveness that is not recoverable from the held-out retriever's standard target-free QPP signals alone.**

It would not establish a universal semantic space, a hierarchy of observers, or a new theory of query difficulty.

---

## 11. What would count as a negative result?

The negative result is equally clean.

If modern QPP computed on the target retriever already captures everything predictive, then

\[
\Delta_P\le0.
\]

In that case the multi-retriever alignment machinery is an unnecessary epicycle for this task and **semantic parallax should be abandoned as a retrieval-prediction construct**.

If \(\Delta_P>0\) but \(k^*\) is very small, the signal may be scientifically real but operationally minor.

If observational gains exist but the fine-tuning intervention fails, the result supports predictive association without a causal reading.

These outcomes are specified before the first experiment and are not fallback hypotheses.

---

## 12. Scope and relation to the discarded observer framework

An earlier version of this project explored Blackwell ordering, Le Cam deficiency, realization protocols, multiscale observer resolution, and order stability. Those ideas are no longer needed to state or test the present claim.

They are retained in a separate companion note and Lean ledger because the negative results explain why several natural definitions of “model A sees more than model B” are vacuous or benchmark-relative. They should not burden this short paper.

The present paper needs only three objects:

\[
\boxed{
\text{system-query interaction},\quad
\text{cross-model geometric residual},\quad
\text{held-out-retriever prediction}.
}
\]

---

## 13. Conclusion

IR already knows that query difficulty is system-dependent, that system-query interactions matter, that formulations change difficulty, and that dense embedding geometry can predict retrieval performance. The open question is narrower.

Given a new dense retriever with no query-level effectiveness labels, does its geometric relationship to a population of other retrievers tell us anything useful about its failures that cannot already be inferred from the retriever itself?

The primary statistic is

\[
\Delta_P.
\]

The operational statistic is

\[
k^*.
\]

The intervention statistic is the out-of-sample predictability of

\[
\Delta y_i
\]

from cross-model geometric change after fine-tuning.

If all three fail, the geometric-observer idea has no remaining empirical claim in dense retrieval. If they survive, the result is small but well-defined: **model-query interaction has a cross-model geometric signature that transfers to unseen retrievers.**

---

## References

Arabzadeh, N., Hamidi Rad, R., Khodabakhsh, M., & Bagheri, E. (2023). **Noisy Perturbations for Estimating Query Difficulty in Dense Retrievers.** CIKM 2023. https://doi.org/10.1145/3583780.3615270

Culpepper, J. S., Faggioli, G., Ferro, N., & Kurland, O. (2022). **Topic Difficulty: Collection and Query Formulation Effects.** *ACM Transactions on Information Systems*, 40(1), Article 19. https://doi.org/10.1145/3470563

Datta, S., Faggioli, G., Ferro, N., Ganguly, D., Muntean, C. I., Perego, R., & Tonellotto, N. (2026). **Projection-displacement based query performance prediction for embedded space of dense retrievers.** *ACM Transactions on Information Systems*, 44(1), Article 7. https://doi.org/10.1145/3765617

Friedman, D., Lampinen, A. K., Dixon, L., Chen, D., & Ghandeharioun, A. (2023). **Comparing Representational and Functional Similarity in Small Transformer Language Models.** NeurIPS 2023 workshop / OpenReview preprint.

Geirhos, R., Meding, K., & Wichmann, F. A. (2020). **Beyond accuracy: quantifying trial-by-trial behaviour of CNNs and humans by measuring error consistency.** NeurIPS 2020.

Jung, J., & Jeon, J. J. (2025). **Generalizing Query Performance Prediction under Retriever and Concept Shifts via Data-driven Correction.** CIKM 2025. https://doi.org/10.1145/3746252.3761404

Khramtsova, E., Zhuang, S., Baktashmotlagh, M., & Zuccon, G. (2024). **Leveraging LLMs for Unsupervised Dense Retriever Ranking.** SIGIR 2024. https://doi.org/10.1145/3626772.3657798

Wang, C., et al. (2026). **ICL-Router: In-Context Learned Model Representations for LLM Routing.** AAAI 2026. https://doi.org/10.1609/aaai.v40i39.40628

Zhuang, R., Wu, T., Wen, Z., Li, A., Jiao, J., & Ramchandran, K. (2025). **EmbedLLM: Learning Compact Representations of Large Language Models.** ICLR 2025. arXiv:2410.02223.
