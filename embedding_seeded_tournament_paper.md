# Embedding-Seeded Hierarchical Tournament Ranking: A Scalable Method for Evaluating Judicial Decision Quality with LLM Panels

**Franklin Silveira Baldo**
Procurador do Estado de Rondônia (OAB/RO 5733)
Porto Velho, Brazil

---

> **Position paper.** This article proposes a method and an evaluation
> protocol. No empirical results are reported. The Semantic Proximity
> Hypothesis is stated as a falsifiable prediction to be tested, not
> as a confirmed finding.

## Abstract

Evaluating the quality of judicial decisions at scale is an open
problem in computational legal reasoning. Existing LLM-as-judge
approaches apply pairwise or tournament-style comparisons to
homogeneous sets of outputs, but judicial corpora are intrinsically
heterogeneous: decisions span different subject matters, procedural
stages, and levels of jurisdiction, making direct comparison
unreliable. We propose **Embedding-Seeded Hierarchical Tournament
Ranking (ESHTR)**, a three-phase protocol that (1) clusters
decisions by semantic similarity using dense embeddings, (2) ranks
decisions within each cluster via an LLM judge panel, and (3)
conducts a cross-cluster championship tournament among
intra-cluster winners. The embedding-first step is intended to act
as a principled seeding mechanism, so that early-stage comparisons
occur between semantically similar decisions — where we expect LLM
judges to be more reliable — while the cross-cluster phase is
designed to surface globally exceptional decisions. We motivate the
method theoretically by connecting known non-transitivity failures in
LLM-as-judge pipelines to semantic distance between compared items,
and argue that stratifying comparisons by similarity should reduce
non-transitivity incidence. We outline an evaluation protocol using a
heterogeneous panel of frontier LLMs as synthetic jurors with
structured rubrics anchored to Brazilian CPC procedural criteria
(art. 489, §1º; art. 927), calibrated against known-quality writing.
The contributions of this article are conceptual: the method, its
theoretical motivation, the evaluation rubric, and a set of
falsifiable predictions. We do **not** report measurements; the
empirical validation of ESHTR on a Brazilian state court corpus is
left for future work.

---

## 1. Introduction

The quality of judicial reasoning is at once one of the most
consequential and hardest-to-measure properties in legal systems.
A judicial decision that suppresses a material argument, applies
a binding precedent selectively, or grounds its dispositif in
claims that were contingent obiter dicta of prior decisions can
propagate reasoning errors across subsequent stages of the same
proceeding and into the broader jurisprudential record. Yet
assessing reasoning quality at scale — across thousands of
decisions per year in a single state tribunal — has historically
required expert human review, which does not scale.

The emergence of large language model (LLM) evaluation pipelines
offers a promising alternative. LLMs trained on legal corpora
can apply structured rubrics to judicial text, identify
argumentation gaps, and compare decisions along multiple quality
dimensions. Several works have shown that LLM-as-judge approaches
produce judgments that correlate meaningfully with expert human
annotation (Zheng et al., 2023; Verga et al., 2024).

However, existing LLM-as-judge protocols have been designed for
*homogeneous* evaluation settings: comparing multiple responses
to the same prompt, rating model outputs on identical tasks, or
scoring papers submitted to the same conference. Judicial corpora
are fundamentally different. A corpus of state court decisions
encompasses criminal, civil, administrative, and labor matters;
decisions at trial level, appellate level, and en banc; rulings
on interlocutory motions, final judgments, and post-judgment
motions. Comparing a criminal sentencing decision directly to a
tax law injunction ruling asks an LLM judge to reconcile contexts
that share procedural vocabulary but differ in substantive
reasoning standards, evidentiary frameworks, and applicable
precedent hierarchies.

The core problem this heterogeneity creates for existing methods
is not merely one of comparability in an intuitive sense. It is
a structural cause of the non-transitivity failures documented in
recent LLM-as-judge literature (see, e.g., the non-transitivity
analyses cited in Section 2.1). When compared items are semantically distant, LLM judges
are more likely to exhibit position bias and preference
inconsistency, because their in-context reasoning cannot draw on
stable, shared evaluative criteria. Non-transitivity undermines
tournament rankings: if the judge prefers A over B and B over C
but C over A, the tournament outcome is an artifact of bracket
design rather than a reliable quality signal.

We propose **Embedding-Seeded Hierarchical Tournament Ranking
(ESHTR)** as a principled response to this problem. The key
insight is borrowed from competitive sports: seeding. In a
well-designed tournament, teams are seeded to ensure that early
rounds pit similarly-ranked competitors against each other, with
cross-tier matchups deferred to later rounds when the pool has
been filtered. We adapt this logic to judicial evaluation: use
dense text embeddings to group semantically similar decisions
into clusters (seeding by type), rank within each cluster where
comparisons are most reliable, then conduct a championship round
among intra-cluster winners to produce a global ordering.

**Contributions.** This paper makes three contributions:

1. **A method**: ESHTR, a three-phase protocol combining
   embedding-based clustering, intra-cluster LLM-panel ranking,
   and cross-cluster championship tournament.

2. **A theoretical motivation**: we connect non-transitivity
   failures in LLM judges to semantic distance between compared
   items and argue that ESHTR's stratification by similarity
   reduces non-transitivity incidence.

3. **An evaluation protocol**: a structured LLM panel rubric
   anchored to Brazilian CPC procedural criteria, with
   calibration methodology and inter-judge agreement metrics,
   demonstrating the method on a corpus of Brazilian state
   court decisions.

---

## 2. Background and Related Work

### 2.1 LLM-as-Judge Evaluation

The LLM-as-judge paradigm was established by Zheng et al. (2023)
with MT-Bench and Chatbot Arena, demonstrating that GPT-4 achieves
markedly higher agreement with human preferences in pairwise
comparison mode than in pointwise scoring mode. Subsequent work
has refined the approach along several dimensions.

**Jury methods.** Verga et al. (2024) "Replacing Judges with
Juries" showed that a panel of heterogeneous LLMs approximates
human agreement better than any single LLM judge, even when
individual panel members are weaker models. This motivates our
use of a multi-model panel rather than a single judge.

**Tournament methods.** Knockout Assessment (Sandan et al., 2025)
adapts iterative pairwise tournament comparison to LLM evaluation,
addressing the limitation of baseline-fixed pairwise approaches.
Bradley-Terry models have been applied to score models from
tournament outcomes (Xu et al., 2025). Our method builds on these
but adds the embedding-seeded stratification phase as a pre-tournament
step.

**Bias and reliability.** Known biases in LLM judges include
positional bias (favoring the first-presented response),
verbosity bias (favoring longer responses), and self-enhancement
bias (a model rating its own outputs more favorably) (Zheng et al.,
2023). COURTREASONER
(Han et al., EMNLP 2025) specifically reports that LLM judges of
legal reasoning are "fragile and inconsistent" and can be misled
by rhetorically persuasive but logically invalid arguments — a
finding we engage directly in Section 5.3.

**Non-transitivity.** Recent work (Xu et al., 2025) documents
that LLMs exhibit both hard and soft non-transitive preferences in
pairwise comparison, with incidence correlated with positional bias.
This finding motivates ESHTR's stratification approach.

### 2.2 Clustering and Stratification in Evaluation

Embedding-based clustering has been used in evaluation dataset
construction for diversity sampling [Raju et al. 2024], ensuring
that evaluation sets cover the semantic space of the domain. Our
use of clustering is complementary but distinct: we cluster not
to sample a diverse *evaluation set* but to define fair
*comparison groups* for ranking.

Stratified sampling appears in psychometrics and sports ranking
as a method for reducing comparison burden while maintaining
statistical validity. Swiss tournament systems and Elo rating
systems handle large heterogeneous player pools through adaptive
pairing. ESHTR adapts this logic to the document-ranking problem
with embeddings replacing historical ELO as the seeding signal.

### 2.3 Legal Evaluation

LegalBench [Guha et al. 2023] benchmarks LLM task performance
on legal reasoning but evaluates LLMs *as subjects*, not as
judges. Magesh et al. (2024) assessed hallucination rates in
commercial legal LLM products. TAIR [Bowers and Ludäscher 2025]
proposes a framework combining Lean 4 and bipolar argumentation
frameworks for trustworthy legal AI results. None of these works
address the problem of ranking judicial *decisions* by quality,
nor do they propose evaluation methods for heterogeneous legal
corpora at scale.

To our knowledge, the specific combination of embedding-based
seeding and hierarchical tournament ranking for judicial decision
quality evaluation has not been proposed.

---

## 3. Method: Embedding-Seeded Hierarchical Tournament Ranking

ESHTR proceeds in three phases. Figure 1 provides a schematic
overview.

```
Phase 1: Embedding and Clustering
   decisions D₁...Dₙ
      ↓ dense embedding model
   embedding vectors e₁...eₙ
      ↓ clustering algorithm (k-means, HDBSCAN, or spectral)
   clusters C₁...Cₖ (k determined automatically or by domain)

Phase 2: Intra-Cluster Ranking
   for each cluster Cᵢ:
      ↓ LLM panel pairwise tournament
   ranked list Rᵢ; winner wᵢ selected

Phase 3: Cross-Cluster Championship
   {w₁, w₂, ..., wₖ}
      ↓ LLM panel pairwise tournament
   global ranking G; champion c* selected
```

### 3.1 Phase 1: Embedding and Clustering

We embed each decision using a legal-domain-aware dense embedding
model. For Brazilian Portuguese, suitable options include
multilingual-e5-large-instruct and models fine-tuned on
Brazilian legal corpora. Embeddings capture semantic similarity
across topical clusters (criminal, civil, administrative,
labor), procedural stages (first instance, appellate, en banc),
and subject matter (contract, property, family, RPPS, etc.).

Cluster assignment is performed using one of three algorithms
depending on corpus size and desired granularity:

- **k-means** (k set by domain knowledge or elbow method): fast,
  interpretable, suitable when cluster count is known.
- **HDBSCAN**: density-based, discovers clusters of varying size
  and density, identifies outliers. Preferred for legal corpora
  with natural topical structure.
- **Spectral clustering** [Neveditsin et al. 2025]: suitable when
  cluster boundaries are soft or overlapping, as in cross-subject
  cases.

**Rationale for embedding-first.** The seeding function of
Phase 1 is to ensure that Phase 2 comparisons occur between
decisions that share enough semantic context for the LLM judge
to apply stable evaluative criteria. This reduces the incidence
of non-transitivity (Section 4) and increases the reliability of
intra-cluster rankings. A criminal sentencing decision and a
public procurement ruling may both exhibit poor argumentation,
but the standards, precedents, and rhetorical conventions that
constitute "good argumentation" differ between them. Phase 1
ensures they compete in different groups until Phase 3.

### 3.2 Phase 2: Intra-Cluster Ranking

Within each cluster, decisions are ranked by a **heterogeneous
LLM judge panel** using iterative pairwise tournament comparison
(adapted from Knockout Assessment, Sandan et al., 2025).

**Panel composition.** Following Verga et al. (2024), the panel
comprises 3-5 frontier LLMs from different model families
(e.g., Claude, GPT-5, Gemini, Grok). Model diversity mitigates
self-preference bias and reduces systematic bias from any single
model family's training distribution.

**Evaluation rubric.** Each judge receives a structured prompt
including:

1. The two decisions to compare (randomized order to mitigate
   positional bias).
2. An evaluation rubric with criteria anchored to objective
   procedural standards (for Brazilian decisions: art. 489, §1º
   CPC — fundamentação; art. 927 CPC — uso de precedente; art.
   1.022 CPC — completude da decisão).
3. A chain-of-thought instruction requiring the judge to assess
   each criterion before issuing a preference.
4. An instruction to output: (a) preference (A / B / tie),
   (b) criterion-by-criterion assessment, (c) confidence
   estimate (0-100%).

**Aggregation.** Panel votes are aggregated by majority. Ties
are broken by confidence-weighted voting. Bradley-Terry model
scores are computed from all pairwise outcomes within each
cluster to produce a full ranking Rᵢ.

**Intra-cluster winner selection.** The top-ranked decision in
each cluster wᵢ advances to Phase 3. Optionally, the top-k
(e.g., top-3) advance for richer cross-cluster comparison.

### 3.3 Phase 3: Cross-Cluster Championship

Phase 3 conducts a final tournament among intra-cluster winners
{w₁, ..., wₖ}. The same panel and rubric from Phase 2 are used,
with one modification: the rubric includes an additional
criterion for **contextual generalizability** — whether the
reasoning quality evident in the decision would transfer to
adjacent subject matters. This criterion acknowledges that
Phase 3 compares decisions that won in different contexts, and
asks judges to abstract from subject-specific vocabulary to
underlying argumentation quality.

The output of Phase 3 is a global ranking G of intra-cluster
champions, with the overall champion c* identified. The full
ranking of all decisions in the corpus can be reconstructed from
Phase 2 cluster rankings and Phase 3 cross-cluster ordering.

### 3.4 Computational Complexity

Let n = total decisions, k = number of clusters, c = average
cluster size (c = n/k). Phase 1 requires O(n) embedding calls
and O(n log n) clustering. Phase 2 requires O(c² / 2) pairwise
comparisons per cluster (or O(c log c) with tournament
elimination), totaling O(n·c) = O(n²/k) comparisons. Phase 3
requires O(k²/2) comparisons. Total: O(n²/k + k²).

For a corpus of n=1000 decisions with k=20 clusters: Phase 2
requires ~1250 comparisons (vs. ~500,000 for all-pairs), and
Phase 3 requires ~190 comparisons. ESHTR reduces comparison
burden by approximately 99.7% relative to exhaustive pairwise.

---

## 4. Theoretical Motivation: Semantic Distance and Non-Transitivity

We propose the **Semantic Proximity Hypothesis for LLM
Non-Transitivity**: the incidence of non-transitive preferences
in LLM judges is positively correlated with the semantic distance
between compared items.

**Informal argument.** When an LLM judge compares two items A
and B, it must construct an implicit evaluative frame — a set
of criteria, weights, and reference points — to adjudicate
between them. When A and B share semantic context (same subject
matter, similar structure, comparable length), the evaluative
frame is relatively stable across comparisons involving either
A or B. When A and B are semantically distant, the judge must
bridge different contextual frames, introducing instability.
This instability manifests as non-transitivity: the criterion
that makes A better than B (rhetorical clarity in a criminal
context) may not be the criterion that makes B better than C
(procedural completeness in a tax context), generating cycles.

**Connection to known bias sources.** Positional bias and
verbosity bias (Zheng et al., 2023) are amplified when compared
items are semantically distant, because the judge has less
stable criteria to override surface-level heuristics (position,
length). ESHTR's clustering reduces semantic distance within
comparison pairs, thereby reducing the foothold of these biases.

**Falsifiability.** The hypothesis predicts that inter-judge
agreement (measured by Fleiss' κ) should be higher within
ESHTR clusters than in all-pairs comparisons drawn from the
full heterogeneous corpus. Section 6 specifies the test; the
test itself is **not yet conducted** in this position paper.
*Falsified if:* in a properly designed experiment, κ_intracluster
≤ κ_crosscorpus, or if the difference disappears once positional
randomization is controlled for.

---

## 5. Evaluation Protocol for Brazilian Judicial Decisions

### 5.1 Corpus

We apply ESHTR to a corpus of decisions from the Tribunal de
Justiça do Estado de Rondônia (TJRO), publicly available through
the tribunal's transparency portal. Decisions are sampled across
five subject matter clusters identified a priori: (1) RPPS/pension
litigation, (2) property and urban law, (3) criminal law, (4)
administrative disciplinary proceedings, (5) contractual disputes.

### 5.2 Embedding Model

We use multilingual-e5-large-instruct for initial embedding,
with ablation using a model fine-tuned on Brazilian legal
corpora. Cluster assignment is validated by examining cluster
purity against the a priori subject matter labels.

### 5.3 Rubric Design and the COURTREASONER Problem

COURTREASONER (Han et al., EMNLP 2025) found that LLM judges of legal
reasoning are "fragile and inconsistent" and assign high scores
to rhetorically persuasive but logically invalid arguments.
Our rubric design directly addresses this finding in three ways.

**Criterion anchoring.** Rubric criteria are anchored to
objective procedural dispositives rather than to impressionistic
quality assessments. Criteria include:

- **C1 — Identificação de fundamentos determinantes** (art. 489,
  §1º, V, CPC): does the decision identify the determining
  grounds of invoked precedents?
- **C2 — Enfrentamento de argumentos** (art. 489, §1º, IV, CPC):
  does the decision address arguments capable of affecting the
  outcome?
- **C3 — Ausência de motivos genéricos** (art. 489, §1º, III,
  CPC): does the decision avoid generic boilerplate
  non-reasoning?
- **C4 — Uso correto de precedente vinculante** (art. 927, §1º,
  CPC): if a binding precedent is invoked, does the decision
  apply it correctly, distinguish it, or justify deviation?
- **C5 — Completude do dispositivo** (art. 1.022, I-II, CPC):
  is the dispositif free of obscurity, contradiction, and
  omission?

**Dual-axis assessment.** Following the insight from our broader
research program, judges assess each decision on two orthogonal
axes: (a) *procedural validity* (criteria C1-C5 above) and (b)
*argumentative persuasiveness* (rhetorical strength independent
of procedural compliance). Divergence between the two axes —
high persuasiveness, low validity — identifies the pathology
COURTREASONER documented: rhetorically compelling decisions that
fail procedural standards. Convergence at high values identifies
genuinely excellent decisions. This dual-axis metric converts
COURTREASONER's finding from a methodological problem into a
diagnostic finding.

**Chain-of-thought constraint.** Judges must reason criterion
by criterion before issuing a preference, reducing susceptibility
to surface-level rhetorical influence.

### 5.4 Calibration

To validate the panel, we construct a calibration set of 20
decisions with known quality contrast: 10 decisions that were
appealed and had their fundamentação expressly criticized by the
higher court (low-quality signal), and 10 decisions whose
fundamentação was cited approvingly in subsequent decisions
(high-quality signal). The panel is considered calibrated if it
correctly ranks low-quality below high-quality in ≥ 80% of
pairs, across all judge models.

### 5.5 Inter-Judge Agreement

We report Fleiss' κ across all panel members for each cluster
and for Phase 3. We test the Semantic Proximity Hypothesis by
comparing κ values within ESHTR clusters against κ values for
randomly selected cross-cluster pairs from the same corpus.

---

## 6. Proposed Experimental Protocol (No Results Reported)

*As a position paper, this article does not report measurements.
This section specifies the experimental design — datasets, metrics,
expected output formats, and falsifiable predictions — under which
ESHTR can be tested by us or by independent researchers.*

**Expected outputs per phase:**

- Phase 1: Cluster assignments with purity metrics against
  a priori subject matter labels; t-SNE visualization of
  embedding space with cluster boundaries.
- Phase 2: Bradley-Terry scores per cluster; intra-cluster
  Fleiss' κ per judge model and aggregated; examples of
  high-ranked and low-ranked decisions per cluster with
  criterion-by-criterion assessments.
- Phase 3: Global ranking of cluster champions; Phase 3
  Fleiss' κ vs. Phase 2 κ comparison (testing Semantic
  Proximity Hypothesis); examples of decisions where
  persuasiveness and validity axes diverge.

**Hypothesis test:** We expect κ_intracluster > κ_crosscorpus
(supporting the Semantic Proximity Hypothesis), with the
difference most pronounced for semantically distant cluster
pairs.

---

## 7. Discussion

### 7.1 When ESHTR Is and Is Not Appropriate

ESHTR is appropriate when: (a) the corpus is large enough that
all-pairs comparison is infeasible; (b) the corpus is
heterogeneous enough that direct comparison across types would
be unreliable; (c) the evaluation objective is ranking by
quality rather than absolute scoring.

ESHTR is less appropriate when: (a) the corpus is homogeneous
(all decisions of the same type); (b) the evaluation objective
is absolute scoring rather than ranking; (c) clustering is
unstable (decisions do not form coherent semantic groups).

For homogeneous corpora, existing tournament methods (Knockout
Assessment, round-robin with Bradley-Terry) are simpler and
adequate.

### 7.2 Generalization Beyond Brazilian Law

The method generalizes to any heterogeneous legal corpus. The
rubric criteria (C1-C5 above) are specific to Brazilian CPC, but
the method accommodates domain-specific rubrics without
modification. For common-law jurisdictions, analogous criteria
would include ratio-obiter distinction, stare decisis compliance,
and distinguishing adequacy.

The embedding-seeded clustering is language-agnostic, provided
that an appropriate embedding model exists for the target
language. For under-resourced legal languages, multilingual
embedding models (multilingual-e5-large, mDeBERTa) provide
reasonable coverage.

### 7.3 Limitations

**Cluster quality dependency.** ESHTR's reliability depends on
the quality of Phase 1 clustering. If clusters are semantically
incoherent, Phase 2 comparisons inherit the heterogeneity
problem that Phase 1 was meant to solve. Cluster quality should
always be validated (Section 5.2) before proceeding to Phase 2.

**LLM judge as proxy, not ground truth.** LLM panel judgments
are a proxy for expert human judgment, not a replacement. The
calibration protocol (Section 5.4) reduces but does not
eliminate this concern. Rankings produced by ESHTR should be
interpreted as *evidence* of quality ordering, not as
authoritative verdicts.

**Cost.** ESHTR reduces comparison burden relative to all-pairs,
but for very large corpora (n > 10,000) and expensive frontier
LLM judges, Phase 2 cost may still be significant. Adaptive
sampling strategies (stopping Phase 2 early when Bradley-Terry
scores have converged) can reduce cost further.

### 7.4 Implications for Judicial Accountability

A scalable method for ranking judicial decisions by reasoning
quality has implications beyond benchmarking. Systematic quality
assessment of appellate decisions, made publicly available,
could support: (a) identification of jurisdictions where
fundamentação standards are systematically below norm; (b)
training of judges and clerks on high-quality reasoning examples;
(c) academic research on the correlation between decision quality
and appellate reversal rates. These applications raise governance
questions about the use of algorithmic quality assessment in
judicial contexts, which we flag as requiring careful
institutional design beyond the scope of this paper.

---

## 8. Conclusion

We proposed Embedding-Seeded Hierarchical Tournament Ranking
(ESHTR), a three-phase method for evaluating judicial decision
quality at scale using LLM judge panels. The method addresses
the heterogeneity problem in judicial corpora by using dense
embeddings to seed comparison groups, ensuring that LLM judges
operate in semantically coherent contexts where non-transitivity
failures are less likely. We proposed the Semantic Proximity
Hypothesis — that non-transitivity incidence correlates with
semantic distance between compared items — as a theoretical
foundation for the method, and designed an experimental protocol
to test it. We provided a structured evaluation rubric anchored
to Brazilian CPC procedural criteria, with a dual-axis
(validity vs. persuasiveness) assessment design that directly
addresses the critique of LLM legal judges in COURTREASONER
(Han et al., EMNLP 2025), converting a methodological liability into
a diagnostic signal.

ESHTR is a general method applicable to any heterogeneous legal
corpus, and its embedding-seeded stratification logic extends
naturally to other domains where quality evaluation must contend
with semantic heterogeneity at scale.

---

## References

*Entries without † were confirmed against the canonical source during
revision. Entries marked with † require verification before submission.*

- Zheng, L. et al. (2023). Judging LLM-as-a-Judge with MT-Bench
  and Chatbot Arena. *NeurIPS 2023*.
- Verga, P. et al. (2024). Replacing Judges with Juries:
  Evaluating LLM Generations with a Panel of Diverse Models.
  *NAACL 2024*.
- Sandan, I. B., Dinh, T. A., and Niehues, J. (2025). Knockout
  LLM Assessment: Using Large Language Models for Evaluations
  through Iterative Pairwise Comparisons. In *Proceedings of the
  Generation, Evaluation, and Metrics (GEM) Workshop at ACL 2025*.
  arXiv:2506.03785.
- Xu, Y., Ruis, L., Rocktäschel, T., and Kirk, R. (2025).
  Investigating Non-Transitivity in LLM-as-a-Judge. In
  *Proceedings of the 42nd International Conference on Machine
  Learning (ICML 2025)*. Spotlight. arXiv:2502.14074.
- Han, S. S., Takashima, Y., Shen, S. Z., Liu, C., Liu, Y.,
  Thuo, R. K., Knowlton, S., Piskac, R., Shapiro, S. J., and
  Cohan, A. (2025). CourtReasoner: Can LLM Agents Reason Like
  Judges? In *Proceedings of EMNLP 2025*.
- Guha, N. et al. (2023). LegalBench: A Collaboratively Built
  Benchmark for Measuring Legal Reasoning in Large Language
  Models. *NeurIPS 2023*.
- † Bowers, J. and Ludäscher, B. (2025). Towards Trustworthy AI
  Results. *AI4EVIR@JURIX 2025*. CEUR Vol-4157.
- † Raju, S. et al. (2024). Stratified sampling for LLM
  evaluation. *arXiv preprint*. [Title and full authors not confirmed.]
- Neveditsin, N., Lingras, P., and Mago, V. (2025). Scalable
  Parameter-Light Spectral Method for Clustering Short Text
  Embeddings with a Cohesion-Based Evaluation Metric.
  arXiv:2511.19350.
- Xu, M., Tan, X., Wu, J., and Zhou, D. (2026). A Judge-Aware
  Ranking Framework for Evaluating Large Language Models without
  Ground Truth. arXiv:2601.21817.
- Zhang, Y., Wang, C., Wu, L., Yu, W., Wang, Y., Bao, G., and
  Tang, J. (2025). UDA: Unsupervised Debiasing Alignment for
  Pair-wise LLM-as-a-Judge. arXiv:2508.09724. [Conference venue
  not confirmed; listed as arXiv preprint.]
