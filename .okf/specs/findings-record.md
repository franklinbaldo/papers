---
type: "OKF Type Spec"
title: "Findings Record"
description: "Record of what a pre-registered experiment actually produced when executed, including the gates it failed, kept structurally distinct from the protocol that specified it and from any paper that cites it."
tags: [okf-type-spec]
timestamp: 2026-08-23T00:00:00Z
---

# Findings Record

**`type` value:** `"Findings Record"`
**Applies to:** the three execution records under
`experiments/semantic_atlas/spectral_bottleneck/`
(`REAL_MODEL_FINDINGS.md`, `CROSS_MODEL_REPLICATION.md`,
`RELATIVE_DEPTH_CONFIRMATION.md`). Future executed experiments should
get their own record of this type rather than extending these.

## Purpose

A Findings Record states what an experiment **produced when it was
actually run**, against a pinned model or corpus, under a protocol
frozen beforehand.

This type exists because the repository already distinguishes the two
neighbours and had nowhere to put the middle:

- a **Protocol** states the rules *before* execution, and stays valid
  whether or not anyone ever runs it;
- an **Empirical Paper** makes a citable claim, and its own spec exists
  because a 2026-07-09 audit caught an introduction claiming completed
  results that its conclusion admitted did not exist.

A Findings Record is neither. It is the evidence layer in between, and
labelling it as either neighbour loses exactly the information the
repository works hardest to keep visible. Calling an execution record a
Protocol hides that it ran; calling it a Paper inflates a note into a
contribution.

The type carries no presumption about outcome. A record whose every
registered gate failed is as complete an instance of this type as one
that passed — arguably more useful, since the negative case is the one
a later reader is most likely to rediscover by accident.

## Required fields (beyond OKF baseline)

- **The identity of what was run against**, in the body: model or corpus
  name *and* pinned revision/commit. A record without a pin cannot be
  replicated and is not an instance of this type.
- **The registered gates and their outcomes**, stated as such. Not prose
  that implies a verdict — an explicit list where each gate is marked
  passed or failed.
- **Claim boundary** whenever the record contains post-hoc analysis: an
  explicit statement of what the post-hoc result may *not* be used to
  conclude. Post-hoc sensitivity cannot retroactively convert a negative
  frozen result into confirmation, and the record must say so where it
  applies.

## Recommended fields

- The protocol document this record executes, named by path.
- The date or revision of execution, when it differs materially from the
  document's `timestamp`.

## Conventional sections

Frozen protocol · Result · Gates · Interpretation and limits. Records
that cover several rounds (a first smoke, a post-hoc probe, a fresh
confirmation, a cross-model replication) should keep those rounds
separated under their own headings rather than merged into one verdict.

## Notes

This type was added when the Semantic Atlas execution records were
consolidated into `main`. The three files had existed for a week without
frontmatter, which failed `okf/validate.py` and, through it, blocked
every open Semantic Atlas pull request — eight of them — from merging.
The blocking was working as designed: the records were a kind of
document the repository had not yet declared.
