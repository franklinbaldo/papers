---
type: "OKF Type Spec"
title: "Supportive Defense"
description: "Living document defending a specific paper's thesis, maintained across rounds by the supportive role of the debate apparatus."
tags: [okf-type-spec]
timestamp: 2026-07-09T00:00:00Z
---

# Supportive Defense

**`type` value:** `"Supportive Defense"`
**Applies to:** the 10 non-blog files directly under `archive/adversarial-paper-development/yesindeed/`
(e.g. `archive/adversarial-paper-development/yesindeed/paper1b-exit4-defense.md`). Does **not** apply to
`archive/adversarial-paper-development/yesindeed/blog/*.md` — see `.okf/specs/session-log-entry.md` for those.

## Purpose

The mirror image of `.okf/specs/adversarial-critique.md`: the current,
cumulative state of one defense thread for one target paper's thesis,
maintained round over round by the supportive role described in
`archive/adversarial-paper-development/protocol.md`.

## Required fields (beyond OKF baseline)

None beyond OKF's own required `type`.

## Recommended fields

- `tags` — role tag `supportive` plus the target paper's slug.
- `description` — one sentence naming the specific claim being
  defended.

## Conventional sections

Every existing Supportive Defense opens with:

- `## 1. Thesis Supported` — quotes or precisely paraphrases the
  specific claim(s) from the target paper being defended.

A recurring closing convention worth preserving: a `## X. Scope` (or
similarly named) section stating what the defense does **not**
establish, alongside what it does — see `archive/adversarial-paper-development/yesindeed/paper1f-recalibration-defense.md`
for the pattern that made the 2026-07-09 absorption into `paper1F`
tractable, since the scope section named the boundaries precisely
enough to lift straight into the target paper's prose.

## Notes

A defense that concedes a point should say so explicitly ("This
defense accepts...") rather than silently narrowing scope — several
absorbable conclusions found in the 2026-07-09 audit were located
specifically by grepping for that phrase across `archive/adversarial-paper-development/yesindeed/`.
