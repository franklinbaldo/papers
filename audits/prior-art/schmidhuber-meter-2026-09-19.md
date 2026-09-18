---
type: "Audit Report"
title: "Schmidhuber Meter prior-art audit — 2026-09-19"
description: "Claim-specific temporal audit of the Schmidhuber Meter / Claim-Level Citation Debt Index, separating earlier work on microattribution, missed citations, expected under-citation, attribution gaps, priority rewards, simultaneous discovery, and citation allocation from the surviving auditable conjunction."
tags: [schmidhuber-meter, citation-debt, prior-art, bibliometrics, scientific-credit, citation-recommendation]
timestamp: 2026-09-19T00:00:00Z
---

# Schmidhuber Meter prior-art audit — 2026-09-19

> **Status:** first claim-specific reproducible prior-art audit of [`schmidhuber_meter.md`](../../schmidhuber_meter.md) and the canonical [`okf/schmidhuber-meter.md`](../../okf/schmidhuber-meter.md) definition. This audit materially narrows the novelty boundary. It does **not** establish exhaustive novelty, copying, plagiarism, bad faith, or causal dependence.

## 1. Claims audited

- **C1 — claim-level citation debt:** scientific credit deficit should be audited at the level of a specific earlier claim × compared work, not only at author, paper, group, or field level;
- **C2 — observable public-evidence conjunction:** an assessment combines public temporal priority, substantive technical overlap, historical discoverability, and observed credit;
- **C3 — decomposed substantive overlap:** concept, mechanism, experiment, distinctive prediction/result, and rare conjunction are assessed separately;
- **C4 — deterministic v0.1 score:** `SM_base = 10 × P × O × D × (1 − C)` for temporally eligible pairs;
- **C5 — impact separation:** later impact measures consequence, not historical citation obligation/expectation;
- **C6 — causality separation:** temporal priority + overlap + absent citation does not establish copying or derivation; dependency evidence defaults to unknown;
- **C7 — reproducible audit record:** cutoff evidence, candidate dates, component evidence, searches, formula version, and uncertainty remain inspectable.

The informal name “Schmidhuber Meter” is not treated as the substantive contribution. The novelty question concerns the operational conjunction and record structure.

## 2. Temporal reconstruction of our claims

The first located commit containing the **canonical metric definition** is [`e1a977e56d7bac3e4bf44c5594dab5e3e42f76eb`](https://github.com/franklinbaldo/papers/commit/e1a977e56d7bac3e4bf44c5594dab5e3e42f76eb), message `okf: add Schmidhuber Meter concept`, at **2026-09-18 21:23:06 UTC**.

That public Git commit already contains C1–C7: claim-pair unit, temporal gate, five-part overlap, historical discoverability, observed credit, the multiplicative formula, impact separation, dependency-evidence separation, and minimum audit template.

An earlier commit in the same branch, `c88f6f049c33987e58106bbd26712d3f2fad7dca` at 21:22:55 UTC, introduced the `Citation Debt Assessment` type and many fields but not yet the canonical formula/concept. The later methodology paper does not move priority forward because the substantive definition was already public.

**Cutoff for C1–C7: 2026-09-18 21:23:06 UTC.**

Only material first public before that instant is eligible as prior art against these claims.

## 3. Search protocol

Sources: arXiv, ACL Anthology, Nature/Nature Genetics/Nature Physics, Wiley/Strategic Management Journal/JASIST, Journal of Political Economy, science-of-science literature, citation-recommendation literature, citation/data-attribution literature, citation-ethics literature, and targeted web discovery. Primary sources were preferred for dates and technical claims.

Representative queries included:

- `"citation debt" bibliometrics missing citations metric`
- `"citation debt index" scientific citations`
- `"citation credit" deficit bibliometrics`
- `"missing citation" metric bibliometrics prior work omitted citation`
- `"missed citations" reviewers dataset citation recommendation`
- `"citation recommendation" "prior art" scientific papers`
- `"citation credit allocation" scientific literature prior work`
- `"scientific priority" citation metric credit allocation prior discovery`
- `"under-citation" expected citations bibliometrics`
- `"bibliographic negligence" citation omission`
- `"citation amnesia" recency bias older work`
- `simultaneous discoveries science idea twins`
- `scooped priority reward citations independent teams`
- `attribution gap citations relevant sources read but uncited`
- `microattribution scientific credit scholarly contribution smaller than paper`
- `microattribution data provenance quantitative credit Nature Genetics`
- exact-title searches for CitationR, *The Attribution Crisis in LLM Search Results*, *CITECHOICE*, *Idea Twins*, and *Scooped!`;
- post-cutoff searches restricted to 18–19 September 2026 for combinations of `citation credit`, `citation gap`, `missing citation`, `prior art metric`, and `attribution gap`.

Exact-phrase searches for `"citation debt"` and `"citation debt index"` located mostly unrelated financial/technical-debt usages and no pre-cutoff scholarly metric matching the complete conjunction. That is a bounded negative result, **not** proof of absence.

## 4. Pre-cutoff findings

### 4.1 Microattribution predates the claim that scientific credit must attach below paper level

**Work/programme:** Nature Genetics editorials on **microattribution**, followed by Giardine et al., **“Systematic documentation and analysis of human genetic variation in hemoglobinopathies using the microattribution approach.”**

- Nature Genetics editorial **“Compete, collaborate, compel”**: **August 2007**, DOI `10.1038/ng0807-931`;
- **“Human Variome Microattribution Reviews”**: January 2008, DOI `10.1038/ng0108-1`;
- implemented analysis: Giardine et al., *Nature Genetics* 43, 295–301, **2011-03-20**, DOI `10.1038/ng.785`;
- primary sources: <https://doi.org/10.1038/ng0807-931>, <https://doi.org/10.1038/ng.785>.

**Compared claims:** C1, C7.

**Classification:** `partial_prior_art`.

Microattribution explicitly aims to assign quantitative citation credit to scientific contributions smaller than a conventional article, using stable accessions, contributor identity, provenance, and microcitations. The 2011 implementation attaches credit to individual genetic variants/data contributions and counts use at that granularity.

**Consequence for our novelty boundary:** the general proposition “scientific credit should attach to units below the paper” is **not new**. The narrower surviving distinction is that the Schmidhuber Meter audits a **scientific claim × later work relationship** for missing historical credit, rather than designing a positive citation system for database entries/data contributors.

### 4.2 Expected-versus-observed citation gaps substantially predate this work

**Work:** Erin G. Teich et al., **“Citation inequity and gendered citation practices in contemporary physics.”**

- arXiv v1: **2021-12-16 17:37:25 UTC**;
- journal: *Nature Physics* 18, 1161–1170 (2022), DOI `10.1038/s41567-022-01770-1`;
- sources: <https://arxiv.org/abs/2112.09047>, <https://doi.org/10.1038/s41567-022-01770-1>.

**Compared claims:** C1, C2, C4.  
**Classification:** `partial_prior_art`.

Teich et al. define a **citation gap** as under-citation relative to expected rates, using a model of expected citations. This anticipates the generic move from raw citation counts to a deficit relative to expectation.

**Difference:** the unit is demographic/group-level citation inequality, not a claim × later-work pair with claim-specific priority, technical overlap, and historical discoverability.

### 4.3 Reviewer-identified missed citations are already an expert-labelled computational task

**Work:** Kehan Long et al., **“Recommending Missed Citations Identified by Reviewers: A New Task, Dataset and Baselines.”**

- public proceedings: **May 2024**, LREC-COLING 2024;
- ACL Anthology ID `2024.lrec-main.1196`;
- source: <https://aclanthology.org/2024.lrec-main.1196/>.

**Compared claims:** C1, C2, C7.  
**Classification:** `partial_prior_art`.

Long et al. define **Recommending Missed Citations (RMC)** and build CitationR from references peer reviewers identified as missing from submitted full papers. Thus omitted citations were already an expert-labelled, computationally evaluated object before our cutoff.

**Difference:** RMC recommends missing references; it does not establish claim-specific temporal priority, historical discoverability, impact separation, or a pairwise credit-deficit score.

### 4.4 “Attribution gap” was already measured as consumed/relevant sources minus credited sources

**Work:** Ilan Strauss et al., **“The Attribution Crisis in LLM Search Results.”**

- arXiv v1: **2025-06-27 15:44:16 UTC**, `2508.00838`;
- source: <https://arxiv.org/abs/2508.00838>.

**Compared claims:** C1, C2, C4, C7.  
**Classification:** `partial_prior_art`.

Strauss et al. define an **attribution gap** as the difference between relevant URLs consumed/read by search-enabled LLM systems and URLs actually cited, and quantify uncited relevant sources and citation efficiency.

**Difference:** it concerns web-source attribution and has direct exposure traces rather than a scholarly prior-art problem. It does not compare scientific claims by temporal priority or technical overlap.

### 4.5 Simultaneous-discovery detection provides a systematic public-data basis for independent convergence

**Work:** Michaël Bikard, **“Idea twins: Simultaneous discoveries as a research tool.”**

- first published: **2020-04-09**;
- *Strategic Management Journal* 41(8), 1528–1543;
- DOI `10.1002/smj.3162`.

**Compared claims:** C1, C6, C7.  
**Classification:** `adjacent_prior_work` with `partial_prior_art` relevance to the independence/priority protocol.

Bikard proposes a systematic method to identify recent simultaneous discoveries using open scientific sources. This makes independent parallel discovery a first-class empirical phenomenon rather than an exceptional explanation.

**Difference:** it is not a missing-credit score, but it directly supports the rule that overlap plus timing must not be converted into copying/derivation.

### 4.6 The consequences of priority ordering for later credit have already been estimated

**Work:** Ryan Hill & Carolyn Stein, **“Scooped! Estimating Rewards for Priority in Science.”**

- earliest public version verified in this run: **online 2025-01-07**;
- *Journal of Political Economy* 133(3), 793–845 (2025);
- DOI `10.1086/733398`.

**Compared claims:** C1, C5, C6.  
**Classification:** `partial_prior_art`.

Hill & Stein identify priority races among independently and concurrently pursued structural-biology projects and estimate a priority premium: scooped projects receive 21% fewer citations and are less likely to publish in top journals. Their design also distinguishes situations in which trailing teams could learn from the first release.

This anticipates the treatment of **priority and downstream recognition consequences** as measurable objects and supports separating independence from post-exposure dependence.

### 4.7 Citation amnesia shows that historical visibility/age matters

**Work:** Jan Philip Wahle et al., **“Citation Amnesia: On The Recency Bias of NLP and Other Academic Fields.”**

- arXiv v1: **2024-02-19 10:59:29 UTC**;
- <https://arxiv.org/abs/2402.12046>.

**Compared claim:** C2 (historical discoverability).  
**Classification:** `adjacent_prior_work`.

Across roughly 240 million papers, Wahle et al. document declining citation age in many fields. The work does not define pairwise discoverability, but it directly warns against interpreting absent credit without considering historical visibility of older literature.

### 4.8 Author survey evidence identifies omitted citations that undermine priority claims as a real problem

**Work:** Simon Wakeling, Monica Lestari Paramita & Stephen Pinfield, **“How do authors perceive the way their work is cited? Findings from a large-scale survey on quotation accuracy.”**

- version of record online: **2025-07-08**;
- *JASIST* 76(10), 1396–1410;
- DOI `10.1002/asi.70000`.

**Compared claims:** C1, C2, C7.  
**Classification:** `adjacent_prior_work`.

Among 2,648 corresponding authors, respondents identify non-citation as a problem; the paper reports that respondents regarded priority/discovery claims omitting countervailing prior work as especially serious. This supports the problem statement but does not provide a quantitative citation-debt method.

### 4.9 CITECHOICE is a very recent pre-cutoff causal audit of citation-credit allocation

**Work:** Sriram Selvam & Anneswa Ghosh, **“CITECHOICE: A Causal Audit of How Document Presentation Redistributes Citation Credit in Agentic Search.”**

- arXiv v1: **2026-09-14 07:47:47 UTC**, `2609.15164`;
- public roughly 4.5 days before our cutoff.

**Compared claims:** C2, C5, C7.  
**Classification:** `adjacent_prior_work` / `partial_prior_art` for observable citation-credit allocation.

CITECHOICE holds an agentic-search transcript fixed while experimentally varying presentation of source documents that support the same fact, showing that presentation can causally redistribute visible citation credit.

**Difference:** its unit is source allocation by search agents rather than scholarly claim priority, but it means the general notion of auditing citation-credit allocation is pre-cutoff.

### 4.10 Bibliographic omission as lost priority/reward has explicit prior ethical literature

**Work:** Marco Cosentino, Franca Marino & Georges J. M. Maestroni, **“Disregarded Conflicting Results with Prior Research: A Case Report in a Leading Biomedical Journal.”**

- publication: **2014**;
- *Journal of Academic Ethics* 12(3), 245–249;
- DOI `10.1007/s10805-014-9213-3`.

**Compared claims:** C1 and problem framing behind C2.  
**Classification:** `adjacent_prior_work`.

The article explicitly discusses omission of relevant citations as causing unfair loss of priority and undermining science’s reward system. Its misconduct framing is stronger than, and should **not** be imported into, the Schmidhuber Meter.

## 5. What the earlier work changes

The current paper should **not** claim novelty for these components in isolation:

- assigning scientific credit below the paper level;
- citation/attribution gaps between expected or relevant sources and observed credit;
- automated recommendation of citations that should have been included;
- empirical consequences of being first versus being scooped;
- systematic identification of simultaneous/independent discoveries;
- age/recency bias in citation practice;
- the proposition that omitted prior work can distort priority credit;
- auditing how citation credit is allocated.

The strongest surviving contribution located in this run is narrower:

> **an auditable claim-pair framework combining a public claim-specific temporal gate, decomposed substantive overlap, reconstructible historical discoverability, observed credit, separately recorded dependency evidence, and a versioned deterministic score while keeping later impact outside the base historical-deficit score.**

No pre-cutoff source located in the recorded searches instantiated this full conjunction or the exact formula `10 × P × O × D × (1 − C)`.

That is a bounded search conclusion. It must not be rewritten as “no prior work exists” or “we are first.”

## 6. Schmidhuber Meter implications for this audit itself

Every material candidate above predates our cutoff. They therefore **cannot** produce citation debt in our favor. The direction of possible credit obligation runs the other way: our methodology should acknowledge antecedents that narrow its novelty claim.

Frozen subject-side record for future monitoring:

```text
subject_claim: claim-level Citation Debt Index conjunction (C1–C7)
subject_artifact: okf/schmidhuber-meter.md
subject_cutoff: 2026-09-18T21:23:06Z
priority_evidence: public Git commit e1a977e56d7bac3e4bf44c5594dab5e3e42f76eb
priority_confidence: 1.0
formula_version: 0.1
impact_role: separate from SM_base
causal_dependency_default: unknown
```

Future post-cutoff comparisons should preserve `overlap_concept`, `overlap_mechanism`, `overlap_experiment`, `overlap_prediction`, `overlap_rare_conjunction`, historical `discoverability`, `credit_received`, `dependency_evidence`, formula version, `sm_base`, and separately dated impact.

## 7. Post-cutoff scan

Targeted searches for material first made public after **2026-09-18 21:23:06 UTC** used combinations of `citation debt`, `citation gap`, `citation credit`, `missing citation`, `prior art metric`, and `attribution gap`, including recency-limited searches.

**Result:** no materially overlapping post-cutoff scholarly work was located in this run.

Accordingly, there is currently no `later_overlap`, `later_non_citing`, `later_citing`, or `later_derivative` candidate. This is a bounded negative result and should be revisited as the literature moves.

## 8. Classification summary

| Candidate | First public date used | Compared claims | Classification | Main effect on novelty boundary |
|---|---:|---|---|---|
| Nature Genetics microattribution / Giardine et al. | 2007-08 | C1/C7 | `partial_prior_art` | sub-paper granular credit/provenance is old |
| Teich et al., *Citation inequity…* | 2021-12-16 | C1/C2/C4 | `partial_prior_art` | expected-vs-observed citation gap is old |
| Long et al., CitationR/RMC | 2024-05 | C1/C2/C7 | `partial_prior_art` | missed citations are already expert-labelled/computable |
| Strauss et al., *Attribution Crisis* | 2025-06-27 | C1/C2/C4/C7 | `partial_prior_art` | relevant-consumed minus credited sources already quantified |
| Bikard, *Idea twins* | 2020-04-09 | C1/C6/C7 | `adjacent_prior_work` | systematic independent convergence is established |
| Hill & Stein, *Scooped!* | 2025-01-07 | C1/C5/C6 | `partial_prior_art` | priority has quantified downstream credit consequences |
| Wahle et al., *Citation Amnesia* | 2024-02-19 | C2 | `adjacent_prior_work` | recency/visibility bias constrains discoverability inference |
| Wakeling et al., author survey | 2025-07-08 | C1/C2/C7 | `adjacent_prior_work` | omitted citation against priority claims is an observed concern |
| Selvam & Ghosh, CITECHOICE | 2026-09-14 | C2/C5/C7 | `adjacent_prior_work` / `partial_prior_art` | citation-credit allocation was already causally auditable |
| Cosentino et al. | 2014 | C1/C2 | `adjacent_prior_work` | omission→priority/reward problem framing is old |

## 9. Epistemic conclusion

The prior-art boundary is materially narrower after this run.

The Schmidhuber Meter is **not** a new discovery that credit can attach below paper level, that citations can be missing, that under-citation can be measured, that priority affects recognition, or that independent parallel discovery exists. Those components have antecedents.

What was **not located** before the cutoff is the specific operational conjunction used here: claim-specific public provenance + decomposed technical overlap + historical discoverability + observed credit + explicit causality separation + impact separation + versioned pairwise score and reproducible audit record.

That surviving claim remains provisional pending broader domain-specific validation and empirical calibration.
