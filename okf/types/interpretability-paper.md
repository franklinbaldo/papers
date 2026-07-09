---
type: "OKF Type Spec"
title: "Interpretability Paper"
description: "General mechanistic/post-hoc interpretability position paper, not part of the Raciocinio Juridico Auditavel programme."
tags: [okf-type-spec]
timestamp: 2026-07-09T00:00:00Z
---

# Interpretability Paper

**`type` value:** `"Interpretability Paper"`
**Applies to:** `pontifex_position_paper.md`. Currently the only file
of this type.

## Purpose

An Interpretability Paper proposes an architecture or method for
understanding model internals or behavior, independent of the
Brazilian-legal-reasoning research programme (see
`paper6_sintese.md`'s explicit scope exclusion).

## Required fields (beyond OKF baseline)

None beyond OKF's own required `type`.

## Recommended fields

- `tags` — `pontifex` at minimum.

## Conventional sections

- A `> **Position paper.**` banner immediately after the author block,
  stating explicitly that no empirical results are reported and that
  specific figures (speed, accuracy, agreement rates) are design
  targets, not measurements. This is the same convention ESHTR and
  STT use; keep the wording consistent across all three if edited.
- A `## Companion documents` section, if a companion note (see
  `okf/types/companion-note.md`) exists — and the companion note MUST
  be characterized accurately there. A 2026-07-09 audit found
  `pontifex_position_paper.md` citing its companion originality
  assessment as independent validation when it was in fact an
  unedited AI browsing-session transcript; both citations were
  corrected to describe it as a preliminary, non-independent scan.

## Notes

If this repository ever adds a second Interpretability Paper, split
`tags` so `pontifex` remains specific to the first one rather than
becoming a de facto synonym for the whole type.
