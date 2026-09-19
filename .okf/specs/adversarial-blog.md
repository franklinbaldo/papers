---
type: "OKF Type Spec"
title: "Adversarial Blog"
description: "Dated adversarial-session record that preserves a complete round-specific argument and its assessment."
tags: [okf-type-spec, adversarial, blog]
timestamp: 2026-08-13T00:00:00Z
---

# Adversarial Blog

**`type` value:** `"Adversarial Blog"`

**Applies to:** dated files under `otherwise/blog/` that record a complete
adversarial round, including its trigger, argument selection, discarded
alternatives, assessment, open questions, and resulting paper changes.

## Purpose

An Adversarial Blog is the role-specific, long-form specialization of a
[`Session Log Entry`](session-log-entry.md). It records not only that an
adversarial session occurred, but also preserves the session's complete
round-specific reasoning so that later supportive and synthesis roles can cite,
contest, and absorb it without reconstructing the argument from a terse log.

Use this type only when the document itself carries the substantive adversarial
argument. A short dated activity record remains a `Session Log Entry`; the
living cross-round attack thread at `otherwise/<slug>.md` remains an
`Adversarial Critique`.

## Required fields beyond the OKF baseline

None.

## Recommended fields

- `title` — identifies the target thread and round.
- `description` — summarizes the new adversarial move rather than merely
  repeating the filename.
- `tags` — includes `adversarial`, `blog`, and the target paper/thread slug.
- `timestamp` — matches the dated session represented by the file.

## Conventional sections

Long-form entries normally identify the triggering material, state entering the
round, selected argument, discarded alternatives, assessment, remaining open
questions, and changes made to the living paper or critique. Section names may
vary when the argument requires a different structure.

## Relationship to adjacent types

- `Adversarial Critique`: living document edited across multiple rounds.
- `Adversarial Blog`: immutable-in-spirit record of one substantive adversarial
  round.
- `Session Log Entry`: generic dated record for any apparatus role, including
  shorter adversarial entries that do not need a specialized long-form type.

