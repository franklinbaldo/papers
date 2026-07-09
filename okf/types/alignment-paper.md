---
type: "OKF Type Spec"
title: "Alignment Paper"
description: "General AI alignment position paper, not part of the Raciocinio Juridico Auditavel programme."
tags: [okf-type-spec]
timestamp: 2026-07-09T00:00:00Z
---

# Alignment Paper

**`type` value:** `"Alignment Paper"`
**Applies to:** `paper_affordance_restriction.md`. Currently the only
file of this type.

## Purpose

An Alignment Paper develops a general AI-safety/alignment pattern,
distinct from the Brazilian-civil-procedure-specific research
programme. It may use a legal system as a worked example (PINK, in
`paper_affordance_restriction.md`) without being a Dogmatic Paper
itself — the distinction is whether the paper's *contribution* is a
legal thesis or a general alignment technique instantiated in a legal
domain.

## Required fields (beyond OKF baseline)

None beyond OKF's own required `type`.

## Recommended fields

- `tags` — `affordance-restriction` at minimum; add others if more
  Alignment Papers are added and need cross-referencing.

## Conventional sections

`paper_affordance_restriction.md` sets a high bar for this type and
is the reference example:

- A `*Draft status: ...*` disclosure line naming the citation
  convention used (`[CITATION NEEDED]` markers vs. verified inline
  citations), immediately after the author block.
- A `## X. What This Is Not` section anticipating over-readings.
- A `## X. Limitations and Failure Modes` section naming failure modes
  the pattern does *not* eliminate, not just ones it solves.
- A validation/deployment-status section that distinguishes completed
  work from planned work explicitly (phase numbers, dates), the same
  discipline `okf/types/empirical-paper.md` requires but applied to
  engineering milestones rather than experimental results.

## Notes

None currently — this type's sole instance was the best-behaved
document found in the 2026-07-09 audit. Preserve its conventions in
any future Alignment Paper rather than relaxing them.
