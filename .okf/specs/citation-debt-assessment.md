---
type: "OKF Type Spec"
title: "Citation Debt Assessment"
description: "Claim-level, evidence-backed assessment of temporal priority, substantive overlap, discoverability, received credit, and impact for the Schmidhuber Meter / Citation Debt Index."
tags: [okf-type-spec, prior-art, bibliometrics, citation-debt]
timestamp: 2026-09-18T21:12:00Z
---

# Citation Debt Assessment

**`type` value:** `"Citation Debt Assessment"`

**Applies to:** the canonical metric concept at `okf/schmidhuber-meter.md` and future claim-by-claim assessment records produced by prior-art audits.

## Purpose

A Citation Debt Assessment records only publicly auditable evidence relevant to the Schmidhuber Meter (SM): whether one claim was publicly available before a compared work, how strongly the two overlap, how discoverable the earlier claim was at the relevant time, what credit the later work gives it, and how consequential any missing credit became.

The type is deliberately narrower than an accusation of plagiarism, copying, derivation, bad faith, or negligence. High overlap plus temporal priority does not establish causal dependence. Evidence of actual exposure or derivation is recorded separately and is never inferred from the score.

## Required fields (beyond OKF baseline)

Concrete scored assessments SHOULD expose the following producer-defined fields in frontmatter when they are known:

- `subject_claim` — stable identifier or concise normalized text for the earlier claim.
- `subject_artifact` — repository path, DOI, arXiv identifier, URL, or other public artifact containing that claim.
- `subject_cutoff` — earliest verified public timestamp of that specific claim.
- `candidate_work` — title or stable identifier of the compared work.
- `candidate_cutoff` — earliest verified public timestamp of the compared work.
- `temporal_classification` — one of the repository prior-art classes: `prior_art`, `partial_prior_art`, `adjacent_prior_work`, `later_independent`, `later_overlap`, `later_non_citing`, `later_citing`, `later_derivative`, or `uncertain_date_or_dependency`.

A document that defines the metric itself rather than scoring a pair MAY set `assessment_status: metric_definition` instead of the pair-specific fields above.

## Recommended fields

- `assessment_status` — `metric_definition`, `draft`, or `audited`.
- `evidence_as_of` — when public evidence and impact data were last checked.
- `priority_confidence` — 0..1, reflecting quality of the public temporal evidence.
- `overlap_concept` — 0..1.
- `overlap_mechanism` — 0..1.
- `overlap_experiment` — 0..1.
- `overlap_prediction` — 0..1.
- `overlap_rare_conjunction` — 0..1.
- `discoverability` — 0..1, derived only from public historical proxies.
- `credit_received` — 0..1, with citation context explained in the body.
- `sm_base` — 0..10, when a versioned formula has been applied.
- `sm_impact` — optional 0..10 consequence score incorporating later impact.
- `formula_version` — exact metric version used.
- `dependency_evidence` — categorical, normally `unknown`; positive exposure/derivation requires independent evidence.

Do not place private beliefs about what authors read, intended, knew, or should morally have done into the score.

## Conventional sections

1. **Claim and cutoff evidence** — exact claim, first public version, timestamp, and provenance.
2. **Compared work and cutoff** — exact candidate version and public date.
3. **Temporal classification** — one repository taxonomy value with justification.
4. **Overlap** — concept, mechanism, experiment, distinctive predictions/results, and rare conjunction.
5. **Discoverability** — historical public proxies: indexing, full-text availability, keyword retrievability, bibliographic proximity, and venue/repository visibility.
6. **Credit** — direct citation, indirect citation, acknowledgement, and citation context.
7. **Impact** — dated public measures, kept separate from citation expectation.
8. **Scores** — raw components, formula version, `SM-base`, and optional `SM-impact`.
9. **Dependency evidence** — normally unknown; list only positive, independently verifiable evidence.
10. **Queries and negative searches** — enough to reproduce important searches.
11. **Uncertainty and revision history** — preserve meaningful epistemic revisions rather than silently overwriting them.

## Notes

- Temporal priority is a gate: a later claim cannot create citation debt against an earlier work.
- The relevant date is the first public date of the **specific claim**, not the repository creation date, current file date, or first version of a paper if the claim was added later.
- `later_non_citing` means only that no citation was located in the checked public material. It does not imply copying or derivation.
- Impact does not make a citation more obligatory after the fact; it measures the consequence of a deficit and therefore belongs in `SM-impact`, not the historical expectation component.
- Every numerical score must remain reconstructible from raw public evidence. If a component cannot be supported publicly, leave it unknown rather than estimating private states.
