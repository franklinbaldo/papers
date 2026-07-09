---
type: "OKF Type Spec"
title: "Companion Note"
description: "Short supporting document for a paper, explicitly scoped as auxiliary and not a first-class contribution in its own right."
tags: [okf-type-spec]
timestamp: 2026-07-09T00:00:00Z
---

# Companion Note

**`type` value:** `"Companion Note"`
**Applies to:** `o3-originality-assessment.md`. Currently the only file
of this type.

## Purpose

A Companion Note supports a paper (background research, a prior-art
scan, supplementary analysis) without itself being a citable
contribution. This type exists specifically to make that
subordination structurally visible: a Companion Note's `type` value
alone signals "read the paper it supports for the actual claim; this
is supporting material, weigh it accordingly."

## Required fields (beyond OKF baseline)

- **An editorial note at the top of the body**, before any content,
  disclosing what the note actually is if its provenance could be
  mistaken for something more authoritative than it is. This is not
  an OKF frontmatter field — OKF has no field for "epistemic status of
  this document's own content" — so it must be prose in the body.
  `o3-originality-assessment.md`'s editorial note (added 2026-07-09) is
  the reference example: it discloses that the file is an unedited AI
  browsing-session transcript, not an independent originality
  assessment, and lists the specific textual evidence (tracking
  parameters on URLs, references to files that don't exist in this
  repository, an undefined citation to a "novelty scoring framework")
  that gives this away on close reading.

## Recommended fields

- `tags` — the paper this note supports.

## Conventional sections

None prescribed beyond the required editorial-note convention above.

## Notes

Before adding a new Companion Note, ask whether it should exist at
all in its current form — an AI-generated scan pasted in without
independent verification is a liability if it isn't clearly labeled
as such, and a genuine editorial improvement over silence is usually
either (a) the disclosed-and-hedged version this type spec requires,
or (b) doing the actual verification and writing a real note instead.
