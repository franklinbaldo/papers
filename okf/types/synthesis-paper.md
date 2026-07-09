---
type: "OKF Type Spec"
title: "Synthesis Paper"
description: "Capstone paper summarizing the coherence and status of a defined subset of the research programme."
tags: [okf-type-spec]
timestamp: 2026-07-09T00:00:00Z
---

# Synthesis Paper

**`type` value:** `"Synthesis Paper"`
**Applies to:** `sintese_programa.md`. Currently the only file of this type.

## Purpose

A Synthesis Paper explains how a set of other papers in this repository
fit together as one research programme, and states explicitly which
papers it does and does not cover. A 2026-07-09 audit found `sintese_programa.md`
making an internal arithmetic error (claiming "sete papers" while its
own breakdown summed to ten) and omitting one full paper (`paper1G`)
from a section that claimed to cover the complete dogmatic axis —
both symptoms of a synthesis whose stated scope had drifted from its
actual content.

## Required fields (beyond OKF baseline)

None beyond OKF's own required `type`.

## Recommended fields

- `description` — should name the scope (which axes/papers) rather
  than just "synthesizes the research programme," precisely because
  "the research programme" is ambiguous when more than one programme
  shares a repository (see the alignment/interpretability vs.
  dogmatic/technical/empirical split documented in `sintese_programa.md`'s own
  Resumo).

## Conventional sections

- An explicit paper count and axis breakdown early in the Resumo/Abstract,
  where the count and the breakdown MUST be arithmetically consistent
  with each other and with the `## Referencias` list's actual item count.
- An explicit scope-exclusion sentence when the synthesis does not cover
  every paper in the repository, naming what's excluded and why (see
  `sintese_programa.md`'s Resumo for the current wording).

## Notes

Any time a new paper is added to a programme a Synthesis Paper claims
to cover, update the Synthesis Paper in the same change — or, if that's
not practical immediately, open a tracked follow-up rather than letting
the count silently go stale (this is exactly how `sintese_programa.md` drifted from
paper1G before 2026-07-09).
