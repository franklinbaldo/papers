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

It does **not** infer plagiarism, copying, intent, bad faith, negligence, independent reinvention, or causal derivation. Those require independent evidence and are outside the base score.

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

`P` is confidence in **public ordering**, not probability that the earlier author privately conceived the idea first.

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

The equal-weight mean is **provisional**. The five components are not assumed to be statistically independent or equally predictive of citation expectation. Audits should preserve the component vector so that future calibrations can reweight or replace the aggregate without destroying the evidence record.

## D — Historical discoverability

`D ∈ [0,1]` uses only reconstructible public proxies available before or around publication of B:

- indexed before B;
- public full text before B;
- natural keyword retrievability;
- bibliographic proximity, including whether B cites work that cites A;
- venue/repository visibility.

It does not estimate what B's authors actually knew or read. High discoverability is therefore evidence about the historical information environment, not evidence of exposure.

## C — Credit received

`C ∈ [0,1]` records publicly visible acknowledgment of A by B.

A direct, substantively appropriate citation can approach 1. Partial or indirect acknowledgment may receive an intermediate value. No located acknowledgment is 0.

Citation context must be inspected where possible. The audit should distinguish at least whether the citation is used as background, support, method/reuse, comparison, critique, or explicit priority acknowledgment. Merely citing A for an unrelated fact is not automatically full claim-level credit, and citation presence by itself is not proof that the cited work was read or causally influential.

# Base score

Version 0.1 deliberately uses a simple deterministic model that can be recomputed from a pair of papers plus public provenance:

```
B = P × O × D × (1 - C)

SM_base = 10 × B
```

This is a **provisional, uncalibrated composite indicator**, not a probability, causal estimate, or validated measurement scale. It is preferred over an uncalibrated learned probability of "citation expected" until a sufficiently large expert-annotated calibration set exists.

The multiplicative form and equal component weights are modeling choices. Because weighting, normalization, and aggregation can change composite-indicator rankings, any consequential comparison should preserve the raw component vector and report a sensitivity analysis under plausible alternative weights/aggregations. If a pair's qualitative interpretation changes materially under reasonable alternatives, that instability is part of the result.

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

Temporal priority + overlap + no citation is never sufficient by itself. A low or intermediate score likewise cannot establish independent reinvention. Causal labels belong only in `dependency_evidence` when positively supported.

# Interpretation

Version 0.1 is not empirically calibrated, so its numeric cut points have **no validated mapping** to expert judgments of citation obligation or missing credit. Until calibration, the preferred report is the raw component vector plus continuous `SM_base` and uncertainty/sensitivity information.

If bins are useful only for visualization, use neutral versioned labels:

- **0–2** — v0.1 bin A;
- **2–4** — v0.1 bin B;
- **4–6** — v0.1 bin C;
- **6–8** — v0.1 bin D;
- **8–9.5** — v0.1 bin E;
- **9.5–10** — v0.1 bin F.

Do not label bins as "reinvention", "convergence", misconduct, copying, or any other causal state. The earlier mnemonic labels are retired for scored interpretation because the base score was explicitly designed not to identify dependency.

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
citation_function:

formula_version:
sm_base:
component_uncertainty:
sensitivity_analysis:

impact_as_of:
sm_impact:

dependency_evidence:
evidence_as_of:
```

The body should provide the evidence for each non-null value, the important queries used, relevant negative searches, and uncertainty. A scored assessment should not hide disagreement between annotators behind a single decimal value.

# Calibration and falsification contract

Version 0.1 should be treated as a testable measurement proposal. Calibration should use blinded expert judgments on claim pairs and include hard negative controls such as common-knowledge claims, reversed chronology, low discoverability, canonical/obliterated-by-incorporation cases, generic overlap, simultaneous discoveries, and cases where a citation is present but serves a different function.

At minimum, test:

- inter-annotator reliability for `P`, all overlap components, `D`, and `C`;
- correlation/ranking agreement between `SM_base` and blinded expert judgments of whether a citation is expected;
- robustness of rankings to plausible weights, normalization choices, and additive/geometric/multiplicative alternatives;
- out-of-domain stability across fields with different citation norms;
- calibration of any interpretation thresholds before attaching semantic labels to score ranges.

If plausible model choices produce frequent rank reversals, the aggregate should be downgraded to a dashboard/vector rather than presented as a stable scalar index. If expert judgments do not show useful out-of-sample agreement with the score, the v0.1 formula should be replaced rather than defended by construction.

# Relationship to prior-art audits

Prior-art classification and citation-debt scoring answer different questions.

A candidate published **before** the subject cutoff can be `prior_art`, `partial_prior_art`, or `adjacent_prior_work`, but it cannot owe citation debt to the later claim.

A candidate published **after** the subject cutoff may be `later_independent`, `later_overlap`, `later_non_citing`, `later_citing`, or, only with positive evidence, `later_derivative`.

`later_non_citing` is a bibliographic observation. It is not evidence of misconduct by itself.

# Versioning

The raw components are canonical; the aggregate formula is versioned.

This allows later empirical calibration without destroying earlier audit evidence. A future statistically calibrated model may replace the version 0.1 product, but historical assessments must retain the formula version used and remain reproducible.

# Falsification revision — 2026-09-19

A claim-level adversarial audit after the initial prior-art pass found two material problems in the uncalibrated v0.1 presentation: composite-indicator rankings can be sensitive to weighting/aggregation choices, and the earlier interpretation labels `ordinary convergence` / `plausible reinvention` silently suggested causal states that `SM_base` is not designed to identify. Formula v0.1 is preserved for reproducibility, but sensitivity analysis is now required for consequential comparisons and causal interpretation labels are retired. See `audits/prior-art/schmidhuber-meter-falsification-2026-09-19.md`.