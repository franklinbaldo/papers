---
type: "Audit Report"
title: "Schmidhuber Meter falsification audit — 2026-09-19"
description: "Adversarial claim-level audit of the Schmidhuber Meter v0.1, separating novelty from truth-status and testing aggregation, missingness, citation-function, discoverability, and interpretation assumptions."
tags: [schmidhuber-meter, citation-debt, falsification, bibliometrics, composite-indicators, prior-art]
timestamp: 2026-09-19T13:20:00Z
---

# Schmidhuber Meter falsification audit — 2026-09-19

> **Status:** adversarial truth-status audit following the initial prior-art audit. This report does not infer misconduct, copying, negligence, or causal derivation. It preserves priority and validity as separate axes.

## 1. Subject and temporal cutoff

The canonical subject is [`okf/schmidhuber-meter.md`](../../okf/schmidhuber-meter.md), not the later prose paper.

The earliest located public commit containing the full v0.1 conjunction is:

- commit: [`e1a977e56d7bac3e4bf44c5594dab5e3e42f76eb`](https://github.com/franklinbaldo/papers/commit/e1a977e56d7bac3e4bf44c5594dab5e3e42f76eb)
- message: `okf: add Schmidhuber Meter concept`
- public Git timestamp: **2026-09-18 21:23:06 UTC**

It already contains the claim-pair unit, temporal gate, five overlap components, discoverability, credit, product formula, impact separation, dependency-evidence separation, interpretation bands, and audit template.

**Cutoff for C1–C8: 2026-09-18T21:23:06Z.**

The current methodology paper and the Zenodo-freeze work do not move this cutoff forward.

## 2. Claims and explicit falsifiers

### C1 — Observable claim-pair citation deficit is a coherent construct

**Claim.** Public priority, substantive overlap, historical discoverability, and received credit jointly capture a useful observable notion of claim-level citation deficit.

**Would falsify or materially weaken it:** blinded domain experts fail to distinguish high- from low-`SM_base` pairs as cases where a citation would normally be expected; judgments are dominated by omitted variables such as field norms, common-knowledge status, review genre, bibliography limits, or citation function.

### C2 — The multiplicative v0.1 aggregate is a useful scalar ordering

**Claim.** `SM_base = 10 × P × O × D × (1-C)` is a useful transparent baseline.

**Would falsify or materially weaken it:** plausible alternative weights/normalizations/aggregation rules cause frequent rank reversals or materially different classifications, or expert-labelled citation-expectation judgments are not monotone in the score out of sample.

### C3 — Equal-mean overlap is a defensible v0.1 reduction

**Claim.** Concept, mechanism, experiment, prediction/result, and rare conjunction can initially be reduced by an equal arithmetic mean.

**Would falsify or materially weaken it:** dimensions have materially unequal predictive value; strong dependence makes double-counting important; or a vector/dashboard predicts expert judgments substantially better than the scalar mean.

### C4 — Missing overlap dimensions can be handled without distorting the score

**Claim as originally written.** Use only overlap components that can be assessed; missing components are not imputed.

**Direct counterexample.** A pair with `O_concept=1` and four applicable-but-unknown dimensions obtains `O=1` if unknown dimensions are simply dropped, while a better-observed pair with `[1,0,0,0,0]` obtains `O=0.2`. Less evidence can therefore produce a larger score.

This is a structural defect, not a literature disagreement.

### C5 — Historical discoverability is a defensible expectation proxy

**Claim.** Indexing, full text, keyword retrievability, bibliographic proximity, and venue visibility can proxy the historical opportunity to discover the antecedent.

**Would falsify or materially weaken it:** discoverability contributes little after controlling for field/venue/time, or it mostly tracks popularity/cumulative advantage rather than citation expectation; reconstructed discoverability disagrees strongly with historically available search systems or expert search attempts.

### C6 — Received credit can be represented by a claim-level scalar

**Claim.** `C ∈ [0,1]` usefully summarizes acknowledgment after inspecting citation context.

**Would falsify or materially weaken it:** annotators cannot reliably agree on partial versus full credit; citation purpose/polarity changes the normative interpretation in ways not recoverable from a scalar; or citation presence/absence is systematically decoupled from intellectual acknowledgment.

### C7 — Interpretation bands are meaningful enough for communication

**Claim as originally written.** Score intervals were labelled `ordinary convergence`, `plausible reinvention`, `citation eyebrow raised`, `Schmidhuber territory`, and `full Schmidhuber`.

**Would falsify or materially weaken it:** thresholds lack empirical calibration; labels imply causal states that the score explicitly excludes; experts do not associate the bins with stable levels of citation expectation.

### C8 — Impact and dependency should remain outside the base score

**Claim.** Later impact measures consequence, not retroactive citation obligation; causal dependency requires separate positive evidence.

**Would falsify or materially weaken it:** a defensible causal model shows that the relevant decision-time expectation necessarily depends on information only observable after publication, or a validated dependency estimator can be derived from the base components alone. No such evidence was located.

## 3. Adversarial search protocol

Sources consulted included OECD/JRC composite-indicator methodology, Ecological Indicators, Social Indicators Research, Journal of Documentation, ACL/NAACL citation-worthiness work, arXiv, PubMed/PMC, and targeted web discovery.

Representative searches:

- `composite indicator multiplicative aggregation weighting uncertainty sensitivity analysis`
- `composite index rank reversal weighting aggregation`
- `weights importance composite indicators`
- `citation behavior citation motives field norms review`
- `citation function polarity context classification`
- `citation worthiness context benchmark`
- `citation copying misprints references`
- `missing citation reviewer dataset limitations`
- `citation debt index claim level`
- `Schmidhuber Meter`
- post-cutoff recency searches for `claim-level citation debt`, `citation debt index`, `missing bibliographic credit`, and the exact title.

The post-cutoff exact/conjunction searches found no materially overlapping scholarly work first made public after the cutoff. That is a bounded negative result.

## 4. Pre-cutoff findings relevant to validity

### 4.1 Composite-indicator methodology makes sensitivity analysis a requirement, not a nicety

**Source:** OECD / European Union / EC-JRC, *Handbook on Constructing Composite Indicators: Methodology and User Guide* (2008), DOI [`10.1787/9789264043466-en`](https://doi.org/10.1787/9789264043466-en).

The handbook treats weighting, normalization, aggregation, and missing-data choices as subjective modeling decisions and explicitly recommends uncertainty/sensitivity analysis to determine how those choices affect composite outputs/rankings.

**Compared claims:** C2, C3, C4, C7.  
**Priority classification:** `partial_prior_art` for the validation methodology, not for the citation-debt construct.  
**Truth-status:** `boundary_condition`.  
**Strength:** **strong**.  
**Target:** aggregation stability / interpretation.  
**Required action:** `add_control` + `downgrade_confidence`.

The v0.1 product may remain as a reproducible baseline, but a scalar rank should not be treated as robust until reasonable alternative weighting/aggregation choices are shown not to reorder the cases materially.

### 4.2 Empirical composite-index work shows weights and aggregation can materially change rankings

**Sources:**

- Melissa J. Dobbie & David Dail, *Robustness and sensitivity of weighting and aggregation in constructing composite indices*, *Ecological Indicators* 29 (2013), DOI [`10.1016/j.ecolind.2012.12.025`](https://doi.org/10.1016/j.ecolind.2012.12.025).
- William E. Becker, Michaela Saisana, Paolo Paruolo & Ine Vandecasteele, *Weights and importance in composite indicators: Closing the gap*, *Ecological Indicators* 80 (2017), DOI [`10.1016/j.ecolind.2017.03.056`](https://doi.org/10.1016/j.ecolind.2017.03.056).
- Athanasios Greco et al., *On the Methodological Framework of Composite Indices: A Review of the Issues of Weighting, Aggregation, and Robustness* (2019), DOI [`10.1007/s11205-017-1832-9`](https://doi.org/10.1007/s11205-017-1832-9).

**Compared claims:** C2/C3/C7.  
**Classification:** `boundary_condition`.  
**Strength:** **strong**.  
**Target:** magnitude and ordering, not the existence of the construct.  
**Required action:** `add_control`.

This literature directly supports keeping the raw vector canonical and treating formula v0.1 as one aggregation choice rather than a validated measurement law.

### 4.3 The original missing-dimension rule can reward ignorance

No external paper is needed for this counterexample. If the mean is taken over only observed/applicable components without distinguishing `unknown` from `not_applicable`, a sparse pair can score higher simply because low-overlap dimensions were never measured.

**Compared claim:** C4.  
**Classification:** `contrary_evidence`.  
**Strength:** **strong**.  
**Target:** mechanism / score computation.  
**Required action:** `revise_mechanism`.

The canonical OKF definition is corrected in this run: every overlap component must be `scored`, `not_applicable`, or `unknown`; unknown applicable dimensions cannot be silently omitted, and unresolved missingness should produce a null scalar or an interval/sensitivity result.

### 4.4 Citation presence/absence is not a pure trace of intellectual credit

**Sources:**

- Lutz Bornmann & Hans-Dieter Daniel, *What do citation counts measure? A review of studies on citing behavior*, *Journal of Documentation* 64(1), 45–80 (2008), DOI [`10.1108/00220410810844150`](https://doi.org/10.1108/00220410810844150).
- Iman Tahamtan & Lutz Bornmann, *What Do Citation Counts Measure? An Updated Review...* (arXiv v1 2019-06-10), [`arXiv:1906.04588`](https://arxiv.org/abs/1906.04588).

Both reviews conclude that citations serve multiple scientific and non-scientific functions and that context, location, semantics, and polarity matter for interpretation.

**Compared claims:** C1/C6.  
**Classification:** `boundary_condition`.  
**Strength:** **moderate-to-strong**.  
**Target:** credit scalar / construct validity.  
**Required action:** `add_boundary_condition` + `add_control`.

The current framework already inspects citation context, so this does not falsify `C`. It does require recording citation function instead of treating reference-list presence as a sufficient measure of claim-level credit.

### 4.5 Citation copying weakens naive exposure/credit interpretations

**Source:** M. V. Simkin & V. P. Roychowdhury, *Theory of Citing*, arXiv v1 **2011-09-11**, [`arXiv:1109.2272`](https://arxiv.org/abs/1109.2272), later in *Handbook of Optimization in Complex Networks*.

The authors use propagated citation misprints to argue that many citations are copied from prior reference lists rather than produced by direct reading of the cited source.

**Compared claims:** C5/C6.  
**Classification:** `boundary_condition`.  
**Strength:** **moderate** for this framework.  
**Target:** inference from citation presence to exposure/credit.  
**Required action:** `no_change` to dependency separation; `add_boundary_condition` to credit interpretation.

This actually strengthens the decision to keep causal exposure outside `SM_base`.

### 4.6 Citation-worthiness is learnable but context-dependent and dataset-sensitive

**Sources:**

- Rakesh Gosangi et al., *On the Use of Context for Predicting Citation Worthiness of Sentences in Scholarly Articles*, NAACL 2021, DOI [`10.18653/v1/2021.naacl-main.359`](https://doi.org/10.18653/v1/2021.naacl-main.359).
- Tong Zeng & Daniel E. Acuna, *Modeling citation worthiness...*, arXiv v1 **2024-05-20**, [`arXiv:2405.12206`](https://arxiv.org/abs/2405.12206).

Gosangi et al. show that document context improves citation-worthiness prediction. Zeng & Acuna report markedly different F1 across benchmarks (about 0.507 on ACL-ARC versus 0.856 on their PMOA-CITE setting) and emphasize section/surrounding context.

**Compared claims:** C1/C5/C7.  
**Priority classification:** `partial_prior_art` for automated citation-expectation modeling.  
**Truth-status:** `boundary_condition`.  
**Strength:** **moderate**.  
**Target:** generalization / calibration.  
**Required action:** `add_control` + `downgrade_confidence` for universal thresholds.

The implication is not that SM cannot work; it is that calibration from one corpus or field cannot be assumed to transfer unchanged across domains.

## 5. Strongest internal contradiction: causal labels on a non-causal score

The original v0.1 bands included `ordinary convergence` and `plausible reinvention`. But the same metric definition explicitly says that temporal priority + overlap + non-citation cannot establish dependency and that dependency defaults to `unknown`.

`reinvention` and, in context, `convergence` are explanations of causal/independence history. `SM_base` does not contain evidence sufficient to choose them.

**Classification:** `contrary_evidence` (internal logical inconsistency).  
**Strength:** **strong**.  
**Target:** interpretation, not formula arithmetic.  
**Required action:** `revise_mechanism`.

The canonical OKF definition now retires causal band names. Before calibration, bins are only neutral versioned visualization bins; the preferred output is the raw component vector, continuous score, and uncertainty/sensitivity information.

## 6. What survives

No finding in this audit requires abandoning the underlying project.

The strongest surviving proposal remains:

> maintain an auditable claim-pair evidence record separating public temporal provenance, technical overlap, historical discoverability, received credit, impact, and dependency evidence, while keeping all raw components versioned and recomputable.

What is **not yet validated** is the stronger measurement claim that the particular v0.1 scalar product and its cut points constitute a stable, field-general scale of citation deficit.

Current truth-status:

- claim-pair evidence record: **plausible / methodologically useful**;
- public-priority gate: **plausible within its deliberately public definition**;
- decomposed overlap vector: **plausible, weights uncalibrated**;
- discoverability proxy: **plausible but not exposure evidence**;
- credit scalar: **usable only with citation-function/context annotation**;
- product formula: **transparent baseline, not validated scale**;
- old semantic interpretation bands: **retracted from canonical scored interpretation**;
- impact/dependency separation: **supported; no contrary evidence located**.

## 7. Required empirical discrimination

A calibration study should freeze, before looking at outcomes:

1. a stratified sample of claim pairs across several fields;
2. blinded expert judgments of whether a citation to A is expected in B and why;
3. independent annotation of `P`, each overlap component, `D`, `C`, citation function, and uncertainty;
4. hard negatives: common knowledge, obliteration-by-incorporation, reversed chronology, generic overlap, low discoverability, simultaneous discovery, and citation-present-but-wrong-function cases;
5. comparison of the current product against additive/geometric models, reweighted models, and a raw-vector/dashboard baseline;
6. rank-reversal/sensitivity analysis under plausible weights and missing-data treatments;
7. held-out field evaluation.

**Decision rule:** if the scalar is unstable under reasonable modeling choices or does not agree usefully with blinded experts out of sample, preserve the evidence vector and replace/demote the scalar rather than tuning labels post hoc.

## 8. Changes made by this audit

The canonical [`okf/schmidhuber-meter.md`](../../okf/schmidhuber-meter.md) is revised to:

- state explicitly that v0.1 is an uncalibrated composite indicator;
- require sensitivity analysis for consequential scalar comparisons;
- distinguish `unknown` from `not_applicable` overlap dimensions and prevent missing-evidence inflation;
- record citation function alongside credit;
- add uncertainty/sensitivity fields;
- retire causal band labels such as `plausible reinvention`;
- add an explicit falsification contract.

The prose methodology paper is not silently rewritten in this commit because a concurrent Zenodo-freeze PR is editing that file. Its formula remains historically reproducible, but the canonical OKF definition is the source of truth for scored use. Synchronizing the prose interpretation with this audit is a mechanical follow-up once that concurrent edit is reconciled.

## 9. Post-cutoff scan

Recency-limited searches after **2026-09-18 21:23:06 UTC** for the exact title, `Schmidhuber Meter`, `claim-level citation debt`, `citation debt index`, and combinations of `missing bibliographic credit` + claim-level priority found no materially overlapping scholarly work.

No `later_independent`, `later_overlap`, `later_non_citing`, `later_citing`, or `later_derivative` candidate is assigned in this run.

This is a bounded negative search, not evidence of uniqueness.