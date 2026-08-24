---
type: "OKF Type Spec"
title: "Supportive Blog"
description: "Dated supportive-session record that preserves a complete round-specific defense and its assessment."
tags: [okf-type-spec, supportive, blog]
timestamp: 2026-08-22T00:00:00Z
---

# Supportive Blog

**`type` value:** `"Supportive Blog"`

**Applies to:** dated files under `yesindeed/blog/` that record a complete
supportive round, including its trigger, argument selection, discarded
alternatives, assessment, open questions, and resulting paper changes.

## Purpose

A Supportive Blog is the role-specific, long-form specialization of a
[`Session Log Entry`](session-log-entry.md). It records not only that a
supportive session occurred, but also preserves the session's complete
round-specific reasoning so that later adversarial and synthesis roles can
cite, contest, and absorb it without reconstructing the argument from a terse
log.

Use this type only when the document itself carries the substantive
supportive argument. A short dated activity record remains a
`Session Log Entry`; the living cross-round defense thread at
`yesindeed/<slug>.md` remains a `Supportive Defense`.

## Required fields beyond the OKF baseline

None.

## Recommended fields

- `title` — identifies the target thread and round.
- `description` — summarizes the new supportive move rather than merely
  repeating the filename.
- `tags` — includes `supportive`, `blog`, and the target paper/thread slug.
- `timestamp` — matches the dated session represented by the file.

## Conventional sections

Long-form entries normally identify the triggering material, state entering
the round, selected argument, discarded alternatives, assessment, remaining
open questions, and changes made to the living paper or defense. Section
names may vary when the argument requires a different structure.

## Relationship to adjacent types

- `Supportive Defense`: living document edited across multiple rounds.
- `Supportive Blog`: immutable-in-spirit record of one substantive supportive
  round.
- `Session Log Entry`: generic dated record for any apparatus role, including
  shorter supportive entries that do not need a specialized long-form type.
