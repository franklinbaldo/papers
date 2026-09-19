---
type: "OKF Type Spec"
title: "Adversarial Critique"
description: "Living document attacking a specific paper's thesis, maintained across rounds by the adversarial role of the debate apparatus."
tags: [okf-type-spec]
timestamp: 2026-07-09T00:00:00Z
---

# Adversarial Critique

**`type` value:** `"Adversarial Critique"`
**Applies to:** the 8 non-blog files directly under `otherwise/`
(e.g. `otherwise/paper1b-rational-supersession.md`). Does **not**
apply to `otherwise/blog/*.md` — see `okf/types/session-log-entry.md`
for those.

## Purpose

An Adversarial Critique is the *current, cumulative* state of one
attack thread against one target paper's thesis — not a single
session's output. It is edited in place, round over round, by the
adversarial role described in `PROTOCOL.md`. The corresponding
`otherwise/blog/` entries are the append-only session-by-session
changelog of edits to this file; the critique document itself is the
living synthesis.

## Required fields (beyond OKF baseline)

None beyond OKF's own required `type`.

## Recommended fields

- `tags` — role tag `adversarial` plus the target paper's slug (e.g.
  `paper1b`, `eshtr`). This lets a consumer find every critique
  against a given paper by tag rather than by directory-scanning
  filenames.
- `description` — one sentence naming the specific claim under attack,
  not just the target paper's title.

## Conventional sections

Every existing Adversarial Critique opens with:

- `## 1. Thesis Attacked` — quotes or precisely paraphrases the
  specific claim(s) from the target paper.

Beyond that, structure is round-numbered and cumulative (`### Round N`
or equivalent) rather than fixed; see any existing file for the
pattern in practice, since PROTOCOL.md does not mandate one and the
apparatus has converged on a workable structure organically.

## Notes

Per `PROTOCOL.md`'s revised absorption trigger, when a round contains
an explicit bilateral concession, that conclusion should be queued
for absorption into the target Dogmatic/Technical Paper rather than
waiting for the next fixed edit cycle. This type spec doesn't enforce
that (OKF frontmatter has no field for "pending absorption"); it's a
process note, tracked in `synthesis/blog/` and `PROTOCOL.md` instead.
