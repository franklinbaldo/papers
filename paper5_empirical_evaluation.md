# Empirical Evaluation of Auditable Legal Reasoning: LLM Panel Assessment of Brazilian Judicial Decisions Under the Lean 4 Pipeline

**Franklin Silveira Baldo**
Procurador do Estado de Rondônia (OAB/RO 5733)
Porto Velho, Brazil

---

## Abstract

This paper provides empirical evaluation of the Lean 4 pipeline
for auditing legal arguments (Paper 2 of this series) using the
Embedding-Seeded Hierarchical Tournament Ranking method (Paper 4).
We apply the pipeline to a corpus of Brazilian state court decisions
from the Tribunal de Justiça do Estado de Rondônia (TJRO), assess
the quality of resulting Embargos de Declaração using a heterogeneous
LLM judge panel with dual-axis rubric (procedural validity and
argumentative persuasiveness), and evaluate: (1) whether the pipeline
produces pleadings with higher procedural validity scores than
baseline LLM-generated pleadings without the pipeline; (2) whether
the two-axis divergence (high persuasiveness / low validity)
identifies the COURTREASONER pathology in our evaluation setting;
and (3) whether the ESHTR clustering methodology reduces non-
transitivity in LLM judge comparisons, testing the Semantic Proximity
Hypothesis. The experimental design is pre-registered; results
section to be completed upon data collection.

**Keywords**: legal AI evaluation; LLM-as-judge; Brazilian civil
procedure; Lean 4; empirical legal research; ESHTR; precedent
quality; TJRO.

---

## 1. Introduction

Papers 1A through 1F of this series establish the dogmatic
foundations; Papers 2 and 3 develop the pipeline methodology; Paper
4 introduces the ESHTR evaluation method. This paper closes the
empirical loop: it applies the methods to real Brazilian judicial
decisions and reports quantitative results.

The evaluation addresses three questions:

**Q1 (Pipeline effectiveness)**: Does the Lean 4 pipeline produce
Embargos de Declaração with higher procedural validity, as assessed
by the LLM judge panel, than baseline LLM-generated pleadings?

**Q2 (Dual-axis diagnostics)**: Does the dual-axis rubric (procedural
validity × argumentative persuasiveness) identify cases where high
persuasiveness accompanies low validity — the COURTREASONER pathology
that pure persuasiveness metrics would miss?

**Q3 (ESHTR validation)**: Does ESHTR clustering reduce non-
transitivity in LLM judge comparisons, as predicted by the Semantic
Proximity Hypothesis?

---

## 2. Experimental Design

### 2.1 Corpus

We use publicly available decisions from the TJRO, collected via
the tribunal's transparency portal. The corpus includes 200
decisions across five subject-matter clusters:

- **C1**: RPPS/pension litigation (n ≈ 40)
- **C2**: Property and urban law (n ≈ 40)
- **C3**: Criminal sentencing (n ≈ 40)
- **C4**: Administrative disciplinary proceedings (n ≈ 40)
- **C5**: Contractual disputes (n ≈ 40)

For Q1 and Q2, we select 30 decisions from C1 (RPPS/pension) as
the primary evaluation set — this cluster is where the IPERON
institutional context is most relevant and where the pipeline has
been most extensively developed.

For Q3, we use the full 200-decision corpus to test the ESHTR
clustering methodology.

### 2.2 Conditions for Q1

For each of the 30 RPPS decisions, we generate three pleadings:

- **Pipeline condition (P)**: Embargos de Declaração generated
  using the full six-phase pipeline (Argdown → Lean → subjective
  analysis → synthesis → forensic translation)
- **LLM-simple condition (S)**: Embargos de Declaração generated
  by prompting a frontier LLM directly with the judgment text and
  instruction "write a well-founded Embargos de Declaração against
  this judgment"
- **LLM-elaborated condition (E)**: Embargos de Declaração generated
  by prompting with a carefully designed prompt that instructs the
  LLM to identify omissions, contradictions, and precedent-usage
  defects, without the pipeline structure

Conditions are blinded: the LLM judge panel receives pleadings
without identifying which condition produced each.

### 2.3 The LLM Judge Panel

The panel comprises four frontier models from different families:
Claude Opus 4.6, GPT-5, Gemini 2.5 Pro, and Grok-4. Panel diversity
follows Verga et al. (2024), who showed that heterogeneous LLM
panels approximate human agreement better than single-model judges.

Each judge receives:
- The judgment being challenged
- The pleading to evaluate
- A structured rubric (described below)
- Instruction to reason criterion-by-criterion before issuing scores

Presentation order is randomized across judges and pleadings to
mitigate positional bias.

### 2.4 The Dual-Axis Rubric

The rubric assesses each pleading on two independent axes, each
scored 0–100:

**Axis 1: Procedural Validity (V)**

- V1: Does the pleading correctly identify the type of defect
  (obscurity/contradiction/omission) under art. 1022 CPC?
- V2: For invoked precedents, does the pleading identify their
  fundamentos determinantes (art. 489, §1, V CPC)?
- V3: Does the pleading engage arguments capable of affecting
  the outcome (art. 489, §1, IV CPC)?
- V4: Does the pleading's characterization of the judgment's
  defects accurately reflect the judgment text?
- V5: Is the pleading's claim formulation (pedido) correctly
  structured per art. 1024, §3 CPC?

**Axis 2: Argumentative Persuasiveness (P)**

- P1: Is the prose clear and structured?
- P2: Is the argumentation rhetorically compelling?
- P3: Does the pleading anticipate likely counter-arguments?
- P4: Is the overall framing effective for the intended audience?

The key diagnostic use of the dual axis: cases where P > V indicate
pleadings that are rhetorically persuasive but procedurally defective.
This is the COURTREASONER pathology — a pure persuasiveness metric
would rate such pleadings highly while they fail procedural standards.

### 2.5 Panel Aggregation

For each pleading, each judge issues V and P scores with chain-of-
thought reasoning. Aggregate scores are mean across judges. Inter-
judge agreement is measured with ICC for continuous scores and
Fleiss' κ for categorical decisions.

### 2.6 ESHTR Evaluation (Q3)

For the 200-decision corpus, we:
1. Embed each decision using multilingual-e5-large-instruct
2. Cluster with HDBSCAN (expected: 5 clusters corresponding to
   the a priori subject-matter labels)
3. Verify cluster purity against a priori labels
4. Draw 100 intra-cluster pairs and 100 cross-cluster pairs
5. Submit each pair to pairwise LLM judge comparison
6. Measure Fleiss' κ for intra-cluster pairs and cross-cluster pairs
7. Test: κ_intracluster > κ_crosscluster (Semantic Proximity Hypothesis)

---

## 3. Results

*[Note: This section presents the experimental design and expected
output format. Results to be completed upon data collection.
Pre-registration available at [LINK].]*

### 3.1 Expected Output: Q1 (Pipeline Effectiveness)

For each condition (P, S, E), we will report:
- Mean V score (procedural validity)
- Mean P score (persuasiveness)
- Distribution of V and P scores
- Pairwise comparison: P vs. S, P vs. E, S vs. E (on both axes)

Expected hypothesis: V(P) > V(S) and V(P) > V(E). We do not
hypothesize about P scores — the pipeline may produce pleadings
that are procedurally valid but less rhetorically polished than
pure LLM generation.

### 3.2 Expected Output: Q2 (Dual-Axis Diagnostics)

We will report:
- The distribution of (V, P) pairs across conditions
- The rate of high-P/low-V pleadings per condition
- Example analysis of specific high-P/low-V cases

Expected finding: the S condition will produce more high-P/low-V
pleadings than the P condition, because LLM-simple generation
optimizes for persuasiveness without procedural structure.

### 3.3 Expected Output: Q3 (ESHTR Validation)

We will report:
- Cluster assignments and purity metrics
- κ_intracluster and κ_crosscluster per judge model and aggregated
- Test statistic for H0: κ_intracluster = κ_crosscluster

Expected finding: κ_intracluster > κ_crosscluster, with the
difference largest for cluster pairs that are most semantically
distant (e.g., RPPS decisions vs. criminal sentencing decisions).

---

## 4. Calibration Protocol

Before running the main evaluation, we calibrate the LLM judge
panel on 20 decisions with known quality contrast:
- 10 decisions where higher courts expressly criticized the
  reasoning quality
- 10 decisions cited approvingly as models in subsequent decisions
  or in academic commentary

A calibrated panel correctly ranks low-quality below high-quality
in ≥ 80% of pairs, across all judge models. If calibration fails
for any model, that model is excluded from the main panel and
replaced.

---

## 5. Threats to Validity

**Internal validity**: the LLM judges that evaluate the pipeline
output may have been trained on data that includes similar legal
arguments, creating spurious correlation between pipeline output
and high scores. We mitigate by using diverse models and by
examining the V/P divergence rather than absolute scores.

**Construct validity**: the rubric is designed around Brazilian
CPC dispositives. Judges that are not well-calibrated on Brazilian
procedural law may assess V criteria less reliably than P criteria.
The calibration protocol is designed to detect this.

**External validity**: the corpus is limited to TJRO RPPS decisions
for Q1 and Q2. Results may not generalize to other Brazilian
tribunals or subject matters. The ESHTR evaluation (Q3) uses a
broader corpus but still within TJRO.

---

## 6. Conclusion

This paper presents the empirical evaluation design for the pipeline
developed in Paper 2, using the ESHTR method from Paper 4 and the
dual-axis rubric that addresses the COURTREASONER pathology. The
design is pre-registered; results will be added upon data collection.

The evaluation completes the "Auditable Legal Reasoning" research
programme: Papers 1A–1F establish dogmatic foundations, Papers 2–3
develop the pipeline and provenance methodology, Paper 4 introduces
the ESHTR evaluation method, and this paper provides the quantitative
evaluation that grounds the programme's empirical claims.

---

## References

*[To be completed with full citations.]*

- Han, et al. (2025). COURTREASONER. EMNLP 2025.
- Verga, P. et al. (2024). Replacing Judges with Juries. NAACL 2024.
- Zheng, L. et al. (2023). Judging LLM-as-a-Judge. NeurIPS 2023.

---

*Paper 5 of the "Auditable Legal Reasoning" series.
Pre-registration: [LINK]. Version: [DATE].*
