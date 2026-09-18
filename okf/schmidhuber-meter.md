---
type: "Citation Debt Assessment"
title: "Schmidhuber Meter"
description: "Canonical, auditable claim-level metric for public temporal priority, substantive overlap, discoverability, missing bibliographic credit, and the later consequence of that deficit."
tags: [schmidhuber-meter, citation-debt, prior-art, bibliometrics]
timestamp: 2026-09-18T21:12:00Z
assessment_status: metric_definition
formula_version: "0.1"
---

# Schmidhuber Meter

The **Schmidhuber Meter (SM)** is the informal name for a claim-level **Citation Debt Index**.

It is designed to answer a limited, auditable question:

> Given only public evidence, how strong is the combination of earlier public priority, substantive technical overlap, historical discoverability, and missing bibliographic credit between one claim and one later work?

It does **not** infer plagiarism, copying, intent, bad faith, negligence, or causal derivation. Those require independent evidence and are outside the base score.

# Unit of analysis

The unit is a pair:

```
earlier claim A × compared work B
```

The earlier side is a **specific claim**, not an entire paper. If a claim entered a paper later, its cutoff is the earliest public version containing that claim.

# Temporal gate

Let `t_A` be the earliest verified public timestamp of the claim and `t_B` the earliest verified public timestamp of the compared work.

If `t_A >= t_B`, no citation debt from B to A is scored. The relationship may instead be prior art, contemporaneous work, or temporally uncertain.

# Observable components

All components must be supported by public evidence.

## P — Priority confidence

`P ∈ [0,1]` measures confidence in the claim-level temporal ordering.

Strong evidence includes arXiv v1 timestamps, DOI online-first records, proceedings, releases, public PRs, and public repository commits whose relevant content can be inspected.

## O — Substantive overlap

Overlap is decomposed rather than inferred from abstract-level semantic similarity:

- `O_concept` — same core idea or relation.
- `O_mechanism` — same or materially equivalent mechanism.
- `O_experiment` — unusually similar experimental design, controls, interventions, or datasets.
- `O_prediction` — same distinctive prediction or result.
- `O_rare_conjunction` — overlap in an uncommon combination of otherwise known components.

For formula version 0.1, the aggregate overlap is the arithmetic mean of the five available components unless an audit explicitly records a different pre-registered weighting:

```
O = mean(
  O_concept,
  O_mechanism,
  O_experiment,
  O_prediction,
  O_rare_conjunction
)
```

Missing components are not silently imputed.

## D — Historical discoverability

`D ∈ [0,1]` uses only reconstructible public proxies available before or around publication of B:

- indexed before B;
- public full text before B;
- natural keyword retrievability;
- bibliographic proximity, including whether B cites work that cites A;
- venue/repository visibility.

It does not estimate what B's authors actually knew or read.

## C — Credit received

`C ∈ [0,1]` records publicly visible acknowledgment of A by B.

A direct, substantively appropriate citation can approach 1. Partial or indirect acknowledgment may receive an intermediate value. No located acknowledgment is 0.

Citation context should be inspected where possible: merely citing A for an unrelated fact is not automatically full claim-level credit.

# Base score

Version 0.1 deliberately uses a simple deterministic model that can be recomputed from a pair of papers plus public provenance:

```
B = P × O × D × (1 - C)

SM_base = 10 × B
```

This is a provisional, transparent baseline. It is preferred over a learned probability of "citation expected" until a sufficiently large expert-annotated calibration set exists.

# Impact is separate

Later influence does not retroactively make a citation more obligatory. Therefore impact is **not** part of `SM_base`.

A separate `SM_impact` may summarize the consequence of the same deficit using dated public measures such as field- and age-normalized citation impact, downstream reuse, or software adoption.

Any impact transform must state its formula version and observation date.

# Dependency evidence

`dependency_evidence` is separate from the score.

Default:

```
dependency_evidence: unknown
```

Possible stronger states require positive independent evidence, such as a public discussion, correspondence made public by an authorized source, explicit reuse, documented access, or another verifiable connection.

Temporal priority + overlap + no citation is never sufficient by itself.

# Interpretation

Suggested descriptive bands for `SM_base`:

- **0–2** — ordinary convergence or weak citation expectation.
- **2–4** — plausible reinvention; antecedent exists but specificity or discoverability is limited.
- **4–6** — citation eyebrow raised: meaningful public antecedence and overlap.
- **6–8** — Schmidhuber territory: strong, discoverable, distinctive antecedent with little or no located credit.
- **8–9.5** — full Schmidhuber: unusually strong observable citation deficit.
- **9.5–10** — reserve for exceptionally strong public evidence; the number still does not itself establish plagiarism or derivation.

These labels are communicative, not adjudications of misconduct.

# Minimum audit template

A future scored concept of type `Citation Debt Assessment` should make the following inspectable:

```
subject_claim:
subject_artifact:
subject_cutoff:
candidate_work:
candidate_cutoff:
temporal_classification:

priority_confidence:

overlap_concept:
overlap_mechanism:
overlap_experiment:
overlap_prediction:
overlap_rare_conjunction:

discoverability:
credit_received:

formula_version:
sm_base:

impact_as_of:
sm_impact:

dependency_evidence:
evidence_as_of:
```

The body should provide the evidence for each non-null value, the important queries used, relevant negative searches, and uncertainty.

# Relationship to prior-art audits

Prior-art classification and citation-debt scoring answer different questions.

A candidate published **before** the subject cutoff can be `prior_art`, `partial_prior_art`, or `adjacent_prior_work`, but it cannot owe citation debt to the later claim.

A candidate published **after** the subject cutoff may be `later_independent`, `later_overlap`, `later_non_citing`, `later_citing`, or, only with positive evidence, `later_derivative`.

`later_non_citing` is a bibliographic observation. It is not evidence of misconduct by itself.

# Versioning

The raw components are canonical; the aggregate formula is versioned.

This allows later empirical calibration without destroying earlier audit evidence. A future statistically calibrated model may replace the version 0.1 product, but historical assessments must retain the formula version used and remain reproducible.
