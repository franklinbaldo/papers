---
type: "Technical Paper"
title: "The Schmidhuber Meter: A Claim-Level Citation Debt Index"
description: "A practical, auditable framework for measuring public temporal priority, substantive overlap, discoverability, missing bibliographic credit, and the consequence of that deficit at the level of scientific claims."
tags: [schmidhuber-meter, citation-debt, bibliometrics, prior-art, scientific-credit]
timestamp: 2026-09-19T00:00:00Z
authors:
  - ref: /about/authors/franklin-silveira-baldo.md
    byline: "Franklin Silveira Baldo"
    affiliations:
      - "Independent Researcher"
    corresponding: true
publication:
  status: ready
  targets: [zenodo]
  zenodo:
    publication_type: preprint
    access_right: open
    license: cc-by-nc-4.0
    version: "0.1"
---

# The Schmidhuber Meter: A Claim-Level Citation Debt Index

**Franklin Silveira Baldo**  
Independent Researcher

> **Methodology paper — frozen v0.1.** This paper proposes a claim-level bibliometric index for citation credit deficit. Version 0.1 is a deliberately **uncalibrated composite indicator**, not a probability, causal estimator, misconduct detector, or validated measurement scale. It does not infer plagiarism, copying, intent, negligence, independent reinvention, or causal derivation from temporal priority and overlap alone. The operational definition is restricted to public, auditable evidence. The claim-specific prior-art audit is maintained at [`audits/prior-art/schmidhuber-meter-2026-09-19.md`](audits/prior-art/schmidhuber-meter-2026-09-19.md), and the later adversarial validity audit at [`audits/prior-art/schmidhuber-meter-falsification-2026-09-19.md`](audits/prior-art/schmidhuber-meter-falsification-2026-09-19.md).

## Abstract

Citation counts measure recognition received, not recognition plausibly missing. This paper proposes the **Schmidhuber Meter (SM)**, a claim-level Citation Debt Index for a narrower question: when a later work materially overlaps an earlier public claim, how strong is the observable combination of public priority, substantive overlap, historical discoverability, and missing bibliographic credit?

Prior work already establishes several components of this problem. Citation gaps have been defined as under-citation relative to expected rates; reviewer-identified missing citations have been formalized as a recommendation task; attribution gaps have been quantified as relevant sources consumed but not credited; simultaneous discoveries can be identified systematically from public data; and the downstream rewards of scientific priority have been estimated empirically [4–10]. Accordingly, this paper does **not** claim novelty for missing citations, under-citation, priority effects, citation-credit allocation, or independent rediscovery in isolation.

The proposed contribution is the operational conjunction. First, priority is reconstructed at the level of the **specific claim**, using its earliest verifiable public appearance. Second, overlap is decomposed into concept, mechanism, experiment, distinctive prediction/result, and rare conjunction rather than reduced to abstract-level semantic similarity. Third, discoverability is reconstructed from historical public proxies. Fourth, received credit is inspected in citation context. Fifth, scientific impact is kept outside the base score because later success cannot retroactively change the historical citation situation; impact instead measures the later consequence of a deficit. Finally, dependency evidence is represented separately so that timing plus overlap plus non-citation is never silently converted into a copying claim.

For an earlier claim \(A\) and later work \(B\), version 0.1 defines:

$$
SM_{base}(A,B)=10\,P\,O\,D\,(1-C),
$$

where \(P\) is priority confidence, \(O\) substantive overlap, \(D\) historical discoverability, and \(C\) received credit, each normalized to \([0,1]\). The product is kept because it is deterministic and recomputable, not because it has been empirically validated as an optimal scale. Consequential comparisons must therefore preserve the raw component vector, make missingness explicit, and report sensitivity to plausible weighting, normalization, and aggregation choices. A future calibrated model may replace this product without destroying the evidence recorded by v0.1 audits.

## 1. Motivation

Scientific credit is distributed through many mechanisms, but citation remains one of its most visible traces. Existing scientometrics measures citation accumulation, delayed recognition, inequality in citation allocation, priority rewards, and numerous biases in citation practice. Yet these literatures do not directly collapse into a practical answer to a pairwise historical question:

> Given a specific earlier claim and a specific later work, how strong is the publicly auditable evidence that bibliographic credit is missing?

That question is intentionally weaker than “who copied whom?” and stronger than “are these papers semantically similar?”

It also differs from several neighboring phenomena. A **sleeping beauty** asks when a work begins receiving recognition [1]. The **Matthew effect** concerns cumulative advantage in recognition [2]. **Obliteration by incorporation** concerns cases in which a contribution becomes sufficiently canonical that explicit citation of its source disappears [3]. A citation-debt audit instead asks whether a particular later work, under a particular historical information environment, exhibits an observable deficit of credit to a particular earlier claim.

## 2. Prior art and the narrowed novelty claim

A reproducible audit conducted on 2026-09-19 materially narrowed the contribution claimed here [12]. A subsequent falsification-oriented audit tested the validity assumptions of the proposed score rather than its priority [14]. The following ideas predate this work and must not be represented as inventions of the Schmidhuber Meter.

### 2.1 Expected-versus-observed citation gaps are established

Teich et al. define a citation gap as under-citation relative to expected rates, coupled with over-citation elsewhere, and estimate expected citation rates with a model that excludes the demographic variable under study [5]. This is clear prior art for the generic move from raw citation counts to a **deficit relative to an expectation**.

The distinction is one of unit and evidence. Their analysis concerns group-level citation inequality. The present framework concerns an earlier-claim × later-work pair and conditions the score on public temporal priority, technical overlap, and historical discoverability.

### 2.2 Missed citations are already a computational task

Long et al. define **Recommending Missed Citations (RMC)** and construct CitationR from citations that peer reviewers explicitly identified as missing from submitted papers [4]. This is material prior art for the idea that omitted citations can be operationalized, expert-labelled, and predicted rather than treated only as anecdote.

CitationR is therefore not merely a convenient future calibration dataset. It also constrains the novelty claim of this paper.

### 2.3 Attribution gaps have already been quantified from observable traces

Strauss et al. define an **attribution gap** for search-enabled LLMs as the difference between relevant web sources consumed and sources actually cited [6]. Their setting differs from scientific priority, but the structure is important: relevant input sources can be observed, credited sources can be observed, and the gap can be quantified.

Observed source visitation is stronger evidence of exposure than the discoverability proxies available in ordinary scholarly-history reconstruction. The present framework therefore does not claim the generic concept of a measurable attribution deficit.

### 2.4 Independent simultaneous discovery is an empirical phenomenon, not a residual excuse

Bikard systematizes identification of **simultaneous discoveries** from openly available scientific sources and produces a large collection of “idea twins” [7]. That literature is central to the epistemic posture of the present index: material overlap and temporal proximity do not establish derivation.

A citation-debt score can be high while causal dependency remains unknown. Conversely, a low score cannot prove independent reinvention.

### 2.5 Priority has measurable downstream rewards

Hill and Stein construct priority races among independently and concurrently pursued structural-biology projects and estimate a sizeable priority premium: scooped projects are less likely to publish in top journals and receive fewer citations [8]. Their design also distinguishes races where trailing teams could versus could not have learned from the first release.

This is prior art for treating **priority and its downstream recognition consequences** as measurable objects. It also motivates separating the historical deficit from later consequence.

### 2.6 Visibility and citation-age biases matter

Wahle et al. document a broad decline in the citation of older work across a very large corpus and call the phenomenon “citation age recession” [9]. Any citation-debt system that ignores the historical visibility of an antecedent risks treating ordinary retrieval failure as intentional omission.

### 2.7 Citation-credit allocation itself is already auditable

CITECHOICE, released four days before the public cutoff of the Schmidhuber Meter concept, experimentally shows that document presentation can redistribute visible citation credit within frozen agentic-search transcripts [10]. This is adjacent but important prior art: citation allocation is partly a property of retrieval and presentation systems, not a transparent readout of intellectual contribution.

### 2.8 Omitted prior work is recognized as a priority problem

Wakeling et al.’s survey of 2,648 corresponding authors reports that respondents identify non-citation as a problem, with a particularly serious case being priority or discovery claims that omit work capable of countering those claims [11]. Earlier ethics literature likewise discusses omission of relevant work as a source of unfair loss of priority [13].

### 2.9 Composite-indicator methodology constrains the score

The Schmidhuber Meter is not exempt from the ordinary weaknesses of composite indicators. Methodological work on composite indices emphasizes that weighting, normalization, aggregation, and missing-data choices can materially change rankings and interpretation [15–17]. Version 0.1 therefore treats the product formula as one transparent aggregation rule, not as a discovered measurement law.

The practical consequence is mandatory for consequential use: keep the raw components, expose missingness, and test whether reasonable alternative modeling choices materially change the ordering or conclusion. If they do, that instability is part of the finding rather than something to average away.

### 2.10 Surviving contribution after the audits

No pre-cutoff source located in the documented searches was found to instantiate the complete conjunction used here:

1. claim-specific public temporal provenance;
2. decomposed substantive technical overlap;
3. reconstructible historical discoverability;
4. observed claim-level credit with citation-function inspection;
5. explicit separation of dependency evidence;
6. explicit separation of later impact from the base historical-deficit score;
7. a versioned, recomputable claim-pair audit record with missingness and uncertainty exposed.

The bounded search also did not locate the exact v0.1 product \(10POD(1-C)\). These are **search results, not proofs of uniqueness or firstness**. The paper therefore claims a proposed operational synthesis, not discovery of the underlying citation phenomena or proof that the v0.1 scalar is already a valid universal scale.

## 3. Why the unit of analysis is the claim

Papers are poor atomic units for priority. Modern scientific work evolves through preprints, Git commits, pull requests, proceedings, notebooks, datasets, blog posts, and revised manuscripts. A paper first made public in January may acquire the audited technical claim in August.

Let \(A\) denote a concrete claim. Its provenance record is:

$$
\Pi(A)=(t_A,a_A,v_A,e_A),
$$

where \(t_A\) is the earliest verified public timestamp, \(a_A\) the public artifact, \(v_A\) the exact version, and \(e_A\) the evidence establishing that provenance.

Repository creation dates, current file timestamps, and the first version of a paper are insufficient whenever the claim entered later.

## 4. Temporal eligibility

For candidate work \(B\), let \(t_B\) be its earliest verified public date. Define:

$$
\Delta t=t_B-t_A.
$$

If \(\Delta t\le 0\), no citation debt from \(B\) to \(A\) is scored in \(A\)'s favor. The relationship may instead be `prior_art`, `partial_prior_art`, `adjacent_prior_work`, contemporaneous work, or an uncertain chronology.

This temporal gate prevents a category error: a paper cannot owe historical credit to a claim that was not yet public.

## 5. Priority confidence

Define:

$$
P\in[0,1]
$$

as **priority confidence**, reflecting the strength of public evidence for the ordering.

Strong evidence includes arXiv v1 timestamps, DOI online-first records, proceedings, public releases, inspectable public Git commits, and public pull requests containing the relevant claim. Retrospective recollection or an undated private manuscript receives little or no weight because the metric is about **public priority**, not private conception.

## 6. Substantive overlap

Semantic similarity between abstracts is insufficient. Similar words can hide different mechanisms, while different terminology can describe materially equivalent machinery.

We therefore decompose substantive overlap:

$$
O_c,O_m,O_e,O_p,O_r\in[0,1].
$$

- **Conceptual overlap \(O_c\):** materially the same central idea or relation.
- **Mechanistic overlap \(O_m\):** the same or materially equivalent mechanism.
- **Experimental overlap \(O_e\):** unusually similar design, controls, interventions, datasets, or evaluation procedure.
- **Prediction/result overlap \(O_p\):** the same distinctive prediction or empirical consequence.
- **Rare-conjunction overlap \(O_r\):** the same uncommon combination of otherwise known components.

For formula version 0.1, every overlap dimension is explicitly marked as `scored`, `not_applicable`, or `unknown`. The aggregate is:

$$
O=\operatorname{mean}(O_c,O_m,O_e,O_p,O_r),
$$

but only over dimensions that are genuinely applicable **and scored**. A `not_applicable` dimension may be excluded from the denominator only with substantive justification. An applicable but `unknown` dimension may **not** be silently dropped, because doing so can make a poorly observed pair look more similar than a well-observed pair. When applicable dimensions remain unknown, the preferred options are to leave scalar \(O\) and \(SM_{base}\) unset or to report an explicit interval such as \(O_{min}\)–\(O_{max}\) under a declared missing-data rule.

The equal-weight mean is provisional. The five components are not assumed to be statistically independent or equally predictive of citation expectation. Audits therefore preserve the component vector and coverage state even when an aggregate is reported.

The rare-conjunction term prevents generic overlap from dominating. “Reinforcement learning plus memory” is weak evidence. A highly specific conjunction of unusual architectural choices can be much more informative.

## 7. Historical discoverability

Temporal priority does not imply practical findability. A public but effectively invisible repository commit is not equivalent to an indexed article returned by ordinary literature search.

Define:

$$
D\in[0,1]
$$

as **historical discoverability**, reconstructed from public proxies available before or around publication of \(B\).

Useful evidence includes:

- indexing before \(B\);
- public full-text availability;
- natural keyword retrievability;
- bibliographic proximity, including whether \(B\) cites works that cite \(A\);
- venue/repository visibility;
- terminology correspondence available at that historical time.

This does not estimate what the authors of \(B\) actually knew or read. Private reading history is excluded from the base score. Discoverability is evidence about the historical information environment, not evidence of exposure.

## 8. Credit received

Let:

$$
C\in[0,1]
$$

represent publicly visible claim-level acknowledgment of \(A\) by \(B\).

A direct and substantively appropriate citation can approach 1. Partial or indirect acknowledgment may receive an intermediate value. No located acknowledgment is 0.

Citation context is part of the audit, not optional commentary. The assessment should record the citation's function where possible—for example `background`, `support`, `method_or_reuse`, `comparison`, `critique`, or `explicit_priority_acknowledgment`. Citing \(A\) for an unrelated fact is not automatically full credit for the overlapping claim. Conversely, a legitimate citation to a canonical predecessor or an earlier version may provide substantial credit even without exact title matching.

The scalar \(C\) is itself provisional. Citation-motivation research shows that citation presence and purpose are heterogeneous [18]. If annotators cannot reliably reduce relevant citation contexts to one scalar, the framework should retain a richer vector rather than force agreement into a decimal.

## 9. The base Schmidhuber Meter

For a temporally eligible pair with sufficiently observed components, version 0.1 defines:

$$
B=P\,O\,D\,(1-C),
$$

and:

$$
\boxed{SM_{base}=10\,P\,O\,D\,(1-C)}.
$$

The multiplicative form suppresses the score when temporal evidence, overlap, discoverability, or the missing-credit term is weak. It is chosen for transparency and recomputability.

It is **not** empirically established as the optimal functional form. Version 0.1 is an uncalibrated composite indicator. Any consequential pairwise comparison or ranking must therefore preserve the raw component vector and report a sensitivity analysis under plausible alternative weights, normalizations, missing-data treatments, and aggregation rules. If reasonable alternatives produce rank reversals or qualitatively different conclusions, the aggregate is unstable for that use case and the vector/dashboard should take precedence over the scalar.

## 10. Why impact is separate

A later paper does not become more obligated to cite an antecedent because it later becomes famous. Impact mostly occurs after the original citation decision.

Therefore later influence is not part of \(SM_{base}\).

A separate \(SM_{impact}\) may summarize the **consequence** of the same deficit using dated public measures such as field- and age-normalized citation impact, downstream reuse, benchmark adoption, or software adoption.

The distinction is:

$$
\text{citation deficit}\ne\text{consequence of citation deficit}.
$$

Hill and Stein’s priority-premium results [8] strengthen the case for this separation: priority order can affect the later distribution of recognition, but those downstream consequences are analytically distinct from the evidence available when a bibliography was assembled.

## 11. Dependency evidence is separate

A high Schmidhuber Meter does not prove copying.

Dependency evidence is represented separately as a categorical state, for example:

- `unknown`;
- `evidence_of_independence`;
- `positive_exposure_evidence`;
- `positive_derivation_evidence`.

The default is `unknown`.

Temporal priority plus high overlap does not establish derivation. Temporal priority plus no citation does not establish derivation. Even a score near 10 does not establish plagiarism. Likewise, a low or intermediate score cannot establish independent reinvention.

Positive causal claims require independent evidence such as explicit public discussion, documented reuse, acknowledged access, copied distinctive errors, or another verifiable connection. The simultaneous-discovery literature [7] is a direct reason to keep this field outside the score.

## 12. Interpretation without causal labels

Version 0.1 has no empirically validated mapping from score ranges to expert judgments of citation obligation, dependency, or independent discovery. The preferred report is therefore the raw component vector, continuous \(SM_{base}\) when defined, missingness coverage, uncertainty interval where needed, and sensitivity analysis.

If bins are useful for visualization, v0.1 uses neutral labels only:

- **0–2 — v0.1 bin A**;
- **2–4 — v0.1 bin B**;
- **4–6 — v0.1 bin C**;
- **6–8 — v0.1 bin D**;
- **8–9.5 — v0.1 bin E**;
- **9.5–10 — v0.1 bin F**.

Earlier mnemonic labels such as `ordinary convergence`, `plausible reinvention`, `Schmidhuber territory`, and `full Schmidhuber` are retired for scored interpretation. They suggested causal or normative states that the base score was explicitly designed not to identify. Semantic labels should not be restored until blinded calibration shows that stable thresholds correspond to reproducible expert judgments.

## 13. Practical audit protocol

A useful index must be independently reproducible. A minimal assessment for \(A\times B\) records:

1. exact text or normalized statement of claim \(A\);
2. first public artifact containing \(A\);
3. exact cutoff \(t_A\) and evidence;
4. earliest public version of \(B\);
5. temporal classification;
6. each overlap component with textual or technical evidence;
7. for every overlap component, whether it is `scored`, `not_applicable`, or `unknown`;
8. overlap coverage and the missing-data rule;
9. discoverability proxies reconstructed at the historical cutoff;
10. direct and indirect credit in \(B\);
11. citation function/context where a citation exists;
12. important search queries and databases consulted;
13. negative searches that materially constrain the conclusion;
14. raw component values and formula version;
15. scalar score or interval, where justified;
16. component uncertainty and sensitivity analysis;
17. impact data and observation date, if used;
18. dependency evidence, normally `unknown`;
19. uncertainty and revision history.

The accompanying OKF concept and `Citation Debt Assessment` type implement this structure for machine- and human-readable audits. A scored assessment should not hide annotator disagreement behind a single decimal value.

## 14. Calibration and falsification strategy

A probabilistic quantity such as

$$
P(\text{citation expected}\mid X)
$$

is theoretically attractive, but an uncalibrated probability can conceal subjective judgment behind false precision.

Version 0.1 therefore uses a deterministic index whose inputs can be inspected directly. A future version should be calibrated from data rather than intuition.

Promising calibration sources include:

- reviewer-identified missing citations such as CitationR [4];
- controlled blinded expert annotation of claim pairs;
- known corrections or post-publication citation disputes;
- negative controls involving generic overlap, reversed chronology, canonical/common-knowledge claims, low discoverability, and obliteration-by-incorporation cases;
- simultaneous-discovery datasets [7], which are valuable controls against converting overlap into derivation.

At minimum, calibration should test:

- inter-annotator reliability for \(P\), every overlap component, \(D\), and \(C\);
- ranking agreement between \(SM_{base}\) and blinded judgments of whether a citation is expected;
- robustness to plausible weights, normalizations, missing-data treatments, and additive/geometric/multiplicative alternatives;
- out-of-domain stability across fields with different citation norms;
- whether citation function needs to remain multidimensional rather than be collapsed into \(C\);
- whether any proposed interpretation thresholds are calibrated before semantic labels are attached.

If plausible model choices produce frequent rank reversals, the aggregate should be downgraded to a dashboard/vector. If expert judgments do not show useful out-of-sample agreement with the score, formula v0.1 should be replaced rather than defended by construction.

The raw components should remain stable enough that future formulas can be applied retrospectively without destroying the original evidence record.

## 15. Relationship to neighboring scientometrics

### 15.1 Sleeping beauties

Sleeping-beauty metrics measure delayed recognition over citation trajectories [1]. The earlier work in a citation-debt case need never awaken; a later overlapping work may accumulate the recognition instead.

### 15.2 Matthew effect

The Matthew effect concerns cumulative advantage and path-dependent recognition [2]. Citation debt can coexist with it, but a pairwise score does not identify the social cause of unequal recognition.

### 15.3 Obliteration by incorporation

A contribution may become so canonical that later authors legitimately use it without repeatedly citing its original source [3]. This is a crucial negative control: a well-known textbook fact should not acquire a large citation-debt score merely because its historical origin is absent from every modern bibliography.

### 15.4 Citation inequity and expected citation gaps

Expected-versus-observed citation analysis already has a mature literature [5]. The Schmidhuber Meter is not a replacement for demographic or field-level citation-gap analysis; it adopts a different unit of analysis and additional temporal/technical evidence requirements.

### 15.5 Missed-citation recommendation

RMC/CitationR [4] directly formalizes omitted scholarly references as an expert-labelled recommendation problem. It is the closest computational antecedent located for the “should this reference be here?” subproblem.

### 15.6 Attribution and citation allocation in search systems

Attribution-gap work [6] and CITECHOICE [10] show that source credit can be quantified and causally affected by retrieval/presentation systems. These results caution against interpreting citation presence as a pure function of intellectual relevance.

### 15.7 Priority races and simultaneous discovery

Idea-twin and scooping research [7,8] shows both that independent convergence is common enough to study systematically and that priority order changes later rewards. Those findings motivate the explicit separation between temporal priority, causal dependency, and downstream impact.

### 15.8 Composite indicators

Composite-index methodology [15–17] is not prior art for citation debt as such, but it supplies a direct validity constraint on how a multi-component score should be used. Weighting and aggregation are modeling choices, so robustness is an empirical question rather than an aesthetic property of the formula.

## 16. Paper-level summaries

The natural unit is a claim pair, not an author. For a paper with many audited claims, reporting distributions is preferable to naive summation:

- maximum \(SM_{base}\), with coverage and uncertainty;
- median score among sufficiently observed eligible later works;
- number of high-confidence priority cases;
- number of `later_non_citing` pairs;
- number of pairs above any **preregistered, explicitly uncalibrated** visualization threshold;
- sensitivity of these summaries to alternative plausible aggregation rules;
- impact-weighted consequence statistics reported separately.

Author-level rankings require particular caution because an evidence audit can otherwise turn into a reputational leaderboard detached from the uncertainty of individual claim pairs. Version 0.1 should not be used as an author misconduct ranking.

## 17. Limitations

The framework has significant limitations.

First, scholarly citation norms vary by field. Second, historical search behavior is difficult to reconstruct. Third, oral communication and private circulation leave incomplete public records. Fourth, independent rediscovery is common. Fifth, technical-overlap assessment can be disputed. Sixth, citation purpose is heterogeneous and may not reduce reliably to a scalar credit variable. Seventh, the v0.1 product and its equal-weight overlap mean are not empirically calibrated. Eighth, weighting, normalization, aggregation, and missing-data choices can change composite-indicator rankings. Ninth, missing evidence can bias overlap upward if `unknown` is confused with `not_applicable`; v0.1 therefore requires an explicit missingness contract. Tenth, a memorable eponym can encourage people to read the score as accusation rather than audit.

For these reasons the method is conservative about causality, requires provenance for every important judgment, preserves raw components, treats negative searches as bounded evidence rather than proof of nonexistence, and requires uncertainty/sensitivity reporting for consequential use.

## 18. Why “Schmidhuber”?

The name refers to a recognizable cultural pattern in artificial-intelligence history: Jürgen Schmidhuber has repeatedly published arguments that celebrated later developments have antecedents in earlier work by himself or others. Those historical claims are themselves empirical propositions and should be evaluated case by case under the same rules as any other priority claim.

The eponym is rhetorical, not evidentiary.

The method aims to replace:

> “We did this first.”

with:

> “Here is the claim, its earliest public version, the compared work, the technical overlap, what was unknown, the historical discoverability evidence, the observed credit and citation function, the uncertainty, the sensitivity analysis, and the exact score calculation.”

## 19. Conclusion

Citation counts measure recognition that occurred. The Schmidhuber Meter proposes a different object: **observable citation credit deficit at the claim level**.

Its design principles are:

1. reconstruct priority from the first public appearance of the specific claim;
2. distinguish technical overlap from superficial semantic similarity;
3. distinguish `unknown` from `not_applicable` evidence;
4. reconstruct historical discoverability rather than assume it;
5. inspect received credit and citation function in context;
6. keep impact as a later consequence rather than a retroactive obligation multiplier;
7. keep causal dependency separate from bibliometric overlap;
8. preserve raw evidence, uncertainty, and sensitivity so every aggregate score can be recomputed or challenged.

The 2026-09-19 prior-art audit narrows the proposal: missing citations, expected citation gaps, attribution gaps, priority rewards, simultaneous discovery, citation amnesia, and citation-credit allocation all have antecedents. The later falsification audit narrows the measurement claim further: the v0.1 product is one uncalibrated composite aggregation; missingness must be explicit; citation function matters; and causal score-band labels are not justified. The proposed contribution is therefore the **integration of these concerns into a public, claim-pair, versioned audit protocol and testable score**, not invention of the component phenomena or a claim that the current scalar is already universally validated.

A useful scientometric instrument should make priority disputes narrower, more reproducible, and easier to revise when better evidence appears. If calibration shows the scalar does not do that, the correct outcome is to replace the scalar while preserving the audit record.

---

## References

[1] Qing Ke, Emilio Ferrara, Filippo Radicchi & Alessandro Flammini. “Defining and identifying Sleeping Beauties in science.” *Proceedings of the National Academy of Sciences* 112(24), 7426–7431 (2015). DOI: `10.1073/pnas.1424329112`.

[2] Robert K. Merton. “The Matthew Effect in Science.” *Science* 159, 56–63 (1968).

[3] Eugene Garfield. “The ‘Obliteration Phenomenon’ in Science—and the Advantage of Being Obliterated.” *Essays of an Information Scientist*, Vol. 1 (1977).

[4] Kehan Long, Shasha Li, Pancheng Wang, Chenlong Bao, Jintao Tang & Ting Wang. “Recommending Missed Citations Identified by Reviewers: A New Task, Dataset and Baselines.” *LREC-COLING 2024*, 13699–13711. <https://aclanthology.org/2024.lrec-main.1196/>.

[5] Erin G. Teich et al. “Citation inequity and gendered citation practices in contemporary physics.” *Nature Physics* 18, 1161–1170 (2022). DOI: `10.1038/s41567-022-01770-1`; arXiv: `2112.09047`.

[6] Ilan Strauss, Jangho Yang, Tim O’Reilly, Sruly Rosenblat & Isobel Moure. “The Attribution Crisis in LLM Search Results.” arXiv: `2508.00838` (v1, 2025-06-27).

[7] Michaël Bikard. “Idea twins: Simultaneous discoveries as a research tool.” *Strategic Management Journal* 41(8), 1528–1543 (2020). DOI: `10.1002/smj.3162`.

[8] Ryan Hill & Carolyn Stein. “Scooped! Estimating Rewards for Priority in Science.” *Journal of Political Economy* 133(3), 793–845 (2025). DOI: `10.1086/733398`.

[9] Jan Philip Wahle, Terry Ruas, Mohamed Abdalla, Bela Gipp & Saif M. Mohammad. “Citation Amnesia: On The Recency Bias of NLP and Other Academic Fields.” arXiv: `2402.12046` (2024).

[10] Sriram Selvam & Anneswa Ghosh. “CITECHOICE: A Causal Audit of How Document Presentation Redistributes Citation Credit in Agentic Search.” arXiv: `2609.15164` (v1, 2026-09-14).

[11] Simon Wakeling, Monica Lestari Paramita & Stephen Pinfield. “How do authors perceive the way their work is cited? Findings from a large-scale survey on quotation accuracy.” *Journal of the Association for Information Science and Technology* 76(10), 1396–1410 (2025). DOI: `10.1002/asi.70000`.

[12] Franklin Silveira Baldo. “Schmidhuber Meter prior-art audit — 2026-09-19.” [`audits/prior-art/schmidhuber-meter-2026-09-19.md`](audits/prior-art/schmidhuber-meter-2026-09-19.md).

[13] Marco Cosentino, Franca Marino & Georges J. M. Maestroni. “Disregarded Conflicting Results with Prior Research: A Case Report in a Leading Biomedical Journal.” *Journal of Academic Ethics* 12(3), 245–249 (2014). DOI: `10.1007/s10805-014-9213-3`.

[14] Franklin Silveira Baldo. “Schmidhuber Meter falsification audit — 2026-09-19.” [`audits/prior-art/schmidhuber-meter-falsification-2026-09-19.md`](audits/prior-art/schmidhuber-meter-falsification-2026-09-19.md).

[15] OECD / European Union / EC-JRC. *Handbook on Constructing Composite Indicators: Methodology and User Guide* (2008). DOI: `10.1787/9789264043466-en`.

[16] Melissa J. Dobbie & David Dail. “Robustness and sensitivity of weighting and aggregation in constructing composite indices.” *Ecological Indicators* 29 (2013). DOI: `10.1016/j.ecolind.2012.12.025`.

[17] William E. Becker, Michaela Saisana, Paolo Paruolo & Ine Vandecasteele. “Weights and importance in composite indicators: Closing the gap.” *Ecological Indicators* 80 (2017). DOI: `10.1016/j.ecolind.2017.03.056`.

[18] Lutz Bornmann & Hans-Dieter Daniel. “What do citation counts measure? A review of studies on citing behavior.” *Journal of Documentation* 64(1), 45–80 (2008). DOI: `10.1108/00220410810844150`.

## Repository specification

The machine-readable operational definition for this paper is maintained in:

- [Schmidhuber Meter OKF concept](okf/schmidhuber-meter.md)
- [Citation Debt Assessment OKF type](.okf/specs/citation-debt-assessment.md)

The OKF definition is the source of truth for automated audits; this paper provides the scientific rationale and methodology. Formula version 0.1 is frozen for reproducibility, while interpretation and future calibration remain explicitly revisable.