---
type: "Technical Paper"
title: "The Schmidhuber Meter: A Claim-Level Citation Debt Index"
description: "A practical, auditable framework for measuring public temporal priority, substantive overlap, discoverability, missing bibliographic credit, and the consequence of that deficit at the level of scientific claims."
tags: [schmidhuber-meter, citation-debt, bibliometrics, prior-art, scientific-credit]
timestamp: 2026-09-18T21:30:00Z
---

# The Schmidhuber Meter: A Claim-Level Citation Debt Index

**Franklin Silveira Baldo**  
Independent Researcher

> **Methodology paper.** This paper proposes a claim-level bibliometric index for citation credit deficit. It does not infer plagiarism, copying, intent, negligence, or causal derivation from temporal priority and overlap alone. The operational definition is intentionally restricted to public, auditable evidence.

## Abstract

Citation counts measure recognition received, not recognition plausibly missing. This paper proposes the **Schmidhuber Meter (SM)**, a claim-level Citation Debt Index designed to quantify a narrower phenomenon: a later work materially overlaps an earlier public claim, the earlier claim was discoverable through public scholarly infrastructure, yet the later work gives little or no bibliographic credit to it.

The method is built around five requirements. First, priority is reconstructed at the level of the **specific claim**, using the earliest verifiable public appearance rather than the date of the current paper or repository. Second, overlap is decomposed into concept, mechanism, experiment, distinctive prediction/result, and rare conjunction rather than approximated by abstract-level semantic similarity. Third, discoverability is estimated only from historical public proxies such as indexing, public full text, keyword retrievability, bibliographic proximity, and venue visibility. Fourth, received credit is measured from citation and acknowledgment context. Fifth, scientific impact is kept separate from the base score because later success cannot retroactively make a citation more obligatory; impact instead measures the consequence of a credit deficit.

For an earlier claim (A) and later work (B), version 0.1 defines

[
SM_{base}(A,B)=10,P,O,D,(1-C),
]

where (P) is priority confidence, (O) substantive overlap, (D) historical discoverability, and (C) received credit, all normalized to ([0,1]). The model is deliberately deterministic and inspectable. A future calibrated model may replace the product after sufficient expert-labelled data exist, but the raw components are intended to remain stable and versioned.

The method is designed for practical application by reading the compared works and verifying publicly available bibliographic and repository evidence. It therefore excludes private mental states, unverifiable reading histories, and inferred motives from the main score.

## 1. Motivation

Scientific credit is distributed through many mechanisms, but citations remain one of its most visible traces. Existing bibliometrics measures how often papers are cited, how recognition evolves over time, and how prestige or visibility can compound. Yet these measures do not directly answer a different question:

> Given a specific earlier claim and a specific later work, how strong is the observable evidence that bibliographic credit is missing?

This problem appears in several familiar forms. Some papers remain obscure for years and later become highly recognized, the phenomenon studied as **sleeping beauties**. Ke et al. introduced the beauty coefficient as a parameter-free measure of delayed recognition over citation trajectories [1]. The **Matthew effect** describes cumulative advantage in scientific recognition [2]. **Obliteration by incorporation** describes the opposite-looking case in which an idea becomes so canonical that the original source ceases to be explicitly cited [3].

These are related to citation debt, but they are not the same problem.

A sleeping beauty asks when recognition arrives. Citation debt asks whether a later overlapping work plausibly omitted credit to an earlier claim.

The distinction matters because an earlier work can remain obscure forever while a later, overlapping work becomes canonical. The original work never "awakens"; the scientific credit accrues elsewhere.

## 2. Why priority must be claim-level

Papers are poor atomic units for priority.

Modern scientific work often evolves through arXiv revisions, public Git commits, pull requests, repositories, conference drafts, notebooks, blog posts, datasets, and later manuscript revisions. A paper first made public in January may acquire its central technical claim in August.

Let (A) denote a concrete claim. Its provenance record is:

[
Pi(A)=(t_A, a_A, v_A, e_A),
]

where:

- (t_A) is the earliest verified public timestamp;
- (a_A) is the public artifact containing the claim;
- (v_A) is the exact version;
- (e_A) is the evidence that establishes that provenance.

The relevant cutoff is therefore the first public version containing the specific audited claim.

Repository creation dates, current file timestamps, and the first version of a paper are insufficient whenever the claim entered later.

This rule is central because a work published before (t_A) cannot owe historical citation debt to (A).

## 3. Temporal eligibility

For a candidate work (B), let (t_B) be its earliest verified public date.

Define:

[
Delta t=t_B-t_A.
]

If (Delta tleq 0), no citation debt from (B) to (A) is scored.

The relationship may instead be:

- prior art;
- partial prior art;
- adjacent prior work;
- contemporaneous or uncertain chronology.

This temporal gate prevents a common category error: treating later similarity as evidence that an earlier paper should have cited work that did not yet exist.

## 4. Priority confidence

Not all timestamps deserve equal confidence.

We define:

[
Pin[0,1]
]

as **priority confidence**, reflecting the quality of the public evidence for the ordering.

Strong evidence includes:

- arXiv v1 timestamps;
- DOI online-first records;
- proceedings;
- public releases;
- inspectable public Git commits;
- public pull requests containing the relevant text.

Weak evidence includes retrospective recollection, undated PDFs, or claims that a private manuscript existed.

The score is intentionally about **public priority**, not private conception.

## 5. Substantive overlap

A practical citation-debt index cannot rely on semantic similarity alone. Similar language may conceal different mechanisms, while different terminology may describe the same technical idea.

We therefore decompose overlap into five observable dimensions:

[
O_c, O_m, O_e, O_p, O_r in [0,1].
]

### 5.1 Conceptual overlap (O_c)

Do the two works make materially the same central claim or propose the same scientific relation?

### 5.2 Mechanistic overlap (O_m)

Do they instantiate the claim through the same or materially equivalent mechanism?

Mechanistic overlap is often more diagnostic than topic similarity.

### 5.3 Experimental overlap (O_e)

Do they make unusually similar choices of experimental design, controls, interventions, datasets, or evaluation procedure?

### 5.4 Prediction/result overlap (O_p)

Do they derive or report the same distinctive prediction or empirical consequence?

### 5.5 Rare-conjunction overlap (O_r)

Do several individually known but uncommon components appear together in the same configuration?

This term matters because combinations differ dramatically in specificity. "Reinforcement learning plus memory" is common. A frozen semantic key plus a separately trainable functional key updated toward or away from a query according to downstream advantage is far more distinctive.

For version 0.1:

[
O=operatorname{mean}(O_c,O_m,O_e,O_p,O_r),
]

using only components that can actually be assessed. Missing components are not silently imputed.

## 6. Historical discoverability

Temporal priority alone does not imply that later authors could reasonably have encountered an earlier claim.

A public but effectively invisible Git commit is different from an indexed paper returned by ordinary literature search.

We therefore define:

[
Din[0,1]
]

as **historical discoverability**, reconstructed only from public proxies available before or around publication of (B).

Suitable evidence includes:

- whether (A) was indexed before (B);
- whether full text was publicly accessible;
- whether natural keywords for the claim retrieved (A);
- whether (A) was bibliographically near sources cited by (B);
- whether sources cited by (B) themselves cited (A);
- whether (A) appeared in a visible venue, repository, or preprint server.

This is deliberately not an estimate of what the authors of (B) actually read.

Private reading history is excluded from the base score.

## 7. Credit received

Let:

[
Cin[0,1]
]

represent the credit actually visible in (B).

Examples include:

- direct and substantively appropriate citation;
- partial recognition;
- indirect acknowledgment;
- citation to an earlier version;
- acknowledgment without formal reference;
- no located acknowledgment.

Citation context matters. A paper can cite an earlier work for an unrelated fact while failing to credit the overlapping claim.

The problem of reviewer-identified missing citations is already computationally tractable enough to have produced a dedicated benchmark. Long et al. define the task of **Recommending Missed Citations Identified by Reviewers** and release CitationR, built from papers that reviewers explicitly recommended adding [4]. Their dataset provides a promising future calibration source for citation-expectation models.

## 8. The base Schmidhuber Meter

The first operational version favors transparency over statistical sophistication.

For a temporally eligible pair:

[
B=P,O,D,(1-C),
]

and:

[
oxed{
SM_{base}=10,P,O,D,(1-C)
}
]

The score lies in ([0,10]).

The multiplicative form encodes four gates:

1. weak temporal evidence suppresses the score;
2. weak substantive overlap suppresses the score;
3. poor discoverability suppresses the score;
4. received credit suppresses the score.

This is not claimed to be the uniquely correct functional form. It is the **version 0.1 auditable baseline**.

Its value is practical: every term can be inspected and recomputed from public evidence.

## 9. Why impact is not in the base score

A tempting formula is:

[
	ext{similarity}	imes	ext{citations of later paper}.
]

That is conceptually wrong.

A paper does not become more obligated to cite an antecedent because it later becomes famous.

Impact occurs after the original citation decision and therefore measures a different quantity: the **consequence** of any missing credit.

Accordingly, later influence is kept outside (SM_{base}).

A separate:

[
SM_{impact}
]

may combine the base deficit with dated public impact measures such as:

- field- and age-normalized citation percentile;
- downstream reuse;
- benchmark adoption;
- software reuse;
- repository adoption where scientifically relevant.

The impact transform must be versioned and reported with an observation date.

Thus:

[
	ext{citation deficit}

eq
	ext{consequence of citation deficit}.
]

## 10. Dependency evidence is separate

A high Schmidhuber Meter does not prove copying.

Let dependency evidence be represented separately as a categorical variable:

[
Gin
{
	ext{unknown},
	ext{evidence of independence},
	ext{positive exposure evidence},
	ext{positive derivation evidence}
}.
]

The default is **unknown**.

Temporal priority plus high overlap does not establish derivation.

Temporal priority plus no citation does not establish derivation.

Even a score near 10 does not establish plagiarism.

Positive causal claims require independent evidence such as explicit public discussion, documented reuse, acknowledged access, copied distinctive errors, or another verifiable link.

## 11. Interpretation bands

For communication, version 0.1 proposes the following descriptive bands:

- **0–2 — ordinary convergence:** weak citation expectation or low overlap.
- **2–4 — plausible reinvention:** an antecedent exists, but specificity or discoverability is limited.
- **4–6 — citation eyebrow raised:** clear public antecedence and meaningful overlap.
- **6–8 — Schmidhuber territory:** distinctive, discoverable antecedent with little or no located credit.
- **8–9.5 — full Schmidhuber:** unusually strong observable citation deficit.
- **9.5–10 — exceptional public-evidence case:** reserved for extremely strong observable conditions; the score still does not itself establish misconduct.

The labels are intentionally memorable, but they are not misconduct categories.

## 12. Practical audit protocol

The index is useful only if an independent reader can reproduce it.

A minimal assessment for (A	imes B) records:

1. exact text or normalized statement of claim (A);
2. first public artifact containing (A);
3. exact cutoff (t_A) and evidence;
4. earliest public version of (B);
5. temporal classification;
6. each overlap component with textual or technical evidence;
7. discoverability proxies reconstructible at the historical cutoff;
8. direct and indirect credit in (B);
9. important search queries and databases consulted;
10. negative searches that materially constrain the conclusion;
11. score components and formula version;
12. impact data and observation date, if used;
13. dependency evidence, normally unknown;
14. uncertainty and revision history.

This record should be stored independently from raw search output.

The accompanying OKF concept and `Citation Debt Assessment` type in this repository implement this structure for machine- and human-readable audits.

## 13. Why a deterministic v0.1 is preferable

A probabilistic quantity such as:

[
P(	ext{citation expected}mid X)
]

is theoretically attractive.

But an uncalibrated probability is worse than a transparent index: it presents subjective weights as probabilistic knowledge.

Version 0.1 therefore uses a deterministic score whose inputs are directly inspectable.

A future version can be learned from data once a sufficient calibration corpus exists.

Possible sources include:

- reviewer-identified missing citations such as CitationR [4];
- controlled expert annotation of claim pairs;
- known corrections or post-publication citation disputes;
- negative controls involving generic overlap, reversed chronology, or low discoverability.

The raw components should survive such calibration even if the aggregation formula changes.

## 14. Relation to neighboring bibliometric phenomena

### 14.1 Sleeping beauties

Ke et al. quantify delayed recognition with a beauty coefficient derived from citation trajectories [1].

The Schmidhuber Meter asks a different question. The earlier work need never awaken. The later overlapping paper can accumulate the recognition instead.

### 14.2 Matthew effect

Merton's Matthew effect concerns cumulative advantage in scientific recognition [2].

Citation debt may coexist with such dynamics, but a high score does not identify their social cause.

### 14.3 Obliteration by incorporation

A foundational contribution can become so embedded in common knowledge that explicit citation becomes unnecessary or is replaced by eponymic reference. This phenomenon, described in the bibliometric tradition as obliteration by incorporation, is a crucial negative control [3].

A canonical elementary fact should not receive a large citation-debt score merely because its original source is absent from every modern bibliography.

Historical discoverability is therefore not enough; the audit must also interpret the actual technical specificity of the claim and citation context.

## 15. Paper-level summaries

The natural unit of the index is a claim pair, not an author.

A paper may nevertheless have many audited claims.

We recommend reporting distributions rather than naively summing scores:

- maximum (SM_{base});
- median score among eligible later works;
- number of high-confidence priority cases;
- number of `later_non_citing` pairs;
- number of pairs above a preregistered threshold;
- impact-weighted consequence statistics separately.

An author-level ranking should be treated with particular caution because it can easily turn an evidence audit into a reputational leaderboard.

## 16. Limitations

The framework has several limitations.

First, scholarly citation norms vary by field.

Second, historical search-engine behavior is imperfectly reconstructible.

Third, oral communication and private drafts leave incomplete records.

Fourth, independent rediscovery is common.

Fifth, expert assessment of technical overlap can disagree.

Sixth, citation counts and venue prestige are imperfect measures of scientific consequence.

Seventh, the memorable name can invite misuse as an accusation score.

For those reasons, the index is deliberately conservative about causality and aggressively explicit about provenance.

## 17. Why "Schmidhuber"?

The name refers to a familiar cultural pattern in artificial intelligence: after a celebrated result appears, Jürgen Schmidhuber has often publicly argued that substantially related ideas appeared earlier in his own or adjacent work.

The eponym is rhetorical, not evidentiary.

Individual historical priority claims involving Schmidhuber remain separate empirical questions and should be audited under the same rules as anyone else's.

The metric is intended to replace:

> "We did this first."

with:

> "Here is the claim, here is its first public version, here is the later work, here is the overlap, here is how discoverable the antecedent was, here is the observed credit, and here is the exact score calculation."

## 18. Conclusion

Citation counts measure recognition that occurred.

The Schmidhuber Meter measures a different object: **observable citation credit deficit at the claim level**.

Its design principles are:

1. priority belongs to specific claims, not automatically to whole papers;
2. only public, verifiable provenance enters the score;
3. technical overlap must be decomposed beyond semantic similarity;
4. historical discoverability must be reconstructed rather than assumed;
5. received credit must be checked in context;
6. impact measures consequence, not retrospective obligation;
7. dependency and misconduct remain separate questions;
8. every aggregate score must remain reconstructible from raw evidence.

The resulting metric is deliberately less dramatic than its name.

That is a feature.

A useful scientometric instrument should make disputes narrower, not louder.

---

## References

[1] Qing Ke, Emilio Ferrara, Filippo Radicchi, and Alessandro Flammini. "Defining and identifying Sleeping Beauties in science." *Proceedings of the National Academy of Sciences* 112(24), 7426–7431, 2015. DOI: 10.1073/pnas.1424329112. https://pubmed.ncbi.nlm.nih.gov/26015563/

[2] Robert K. Merton. "The Matthew Effect in Science." *Science* 159, 56–63, 1968.

[3] Eugene Garfield. "The 'Obliteration Phenomenon' in Science—and the Advantage of Being Obliterated." Reprinted in *Essays of an Information Scientist*, Vol. 1, 1977. The concept is discussed in the bibliometric literature as obliteration by incorporation.

[4] Kehan Long, Shasha Li, Pancheng Wang, Chenlong Bao, Jintao Tang, and Ting Wang. "Recommending Missed Citations Identified by Reviewers: A New Task, Dataset and Baselines." *LREC-COLING 2024*, pp. 13699–13711. https://aclanthology.org/2024.lrec-main.1196/

## Repository specification

The machine-readable operational definition for this paper is maintained in:

- [Schmidhuber Meter OKF concept](okf/schmidhuber-meter.md)
- [Citation Debt Assessment OKF type](okf/types/citation-debt-assessment.md)

The OKF definition is the source of truth for automated audits; this paper provides the scientific rationale and methodology.
