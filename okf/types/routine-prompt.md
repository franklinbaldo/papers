---
type: "OKF Type Spec"
title: "Routine Prompt"
description: "Verbatim operating instructions loaded by an external scheduled routine at the start of each run."
tags: [okf-type-spec]
timestamp: 2026-08-14T00:00:00+00:00
---

# Routine Prompt

**`type` value:** `"Routine Prompt"`
**Applies to:** `prompts/*.md`.

## Purpose

A Routine Prompt is the operating instruction set for one automated
role in the debate apparatus (`synthesis`, `adversarial`,
`supportive`). It exists so the scheduled routine's instructions live
under version control instead of inside an external scheduler's
configuration, where they cannot be read, reviewed, or diffed.

The scheduler holds only a pointer — a few lines naming the file to
read. Everything the routine actually does is specified here.

## Distinct from Protocol

`PROTOCOL.md` (type `Protocol`) is *descriptive and shared*: it states
the rules governing the apparatus as a whole — roles, debate-state
definitions, absorption trigger, loop cutoff, document format. All
three routines are bound by it.

A Routine Prompt is *imperative and role-specific*: it tells one role
what to do this run, in order. Where the two overlap, the Routine
Prompt defers to `PROTOCOL.md` rather than restating it — restating is
what allowed the two to silently diverge for 29 sessions before the
2026-08-14 reconciliation.

## Required fields (beyond OKF baseline)

None beyond OKF's own required `type`.

## Recommended fields

- `description` — name the role and its cadence.
- `supersedes` — the external prompt text this file replaced, if the
  routine previously carried its instructions in the scheduler.

## Conventional sections

Role statement; what the routine may exclusively do; per-run steps in
execution order; stop condition. Rules shared with the other two roles
belong in `PROTOCOL.md` and are referenced, not copied.

## Notes

A Routine Prompt is loaded verbatim by a process that cannot ask
clarifying questions. It must be self-sufficient: every step stated in
executable terms, every derived quantity given a derivation rule, and
every "reject / defer / escalate" branch given a concrete action. A
step that requires judgment should say what the judgment is between,
not leave the routine to invent the options.
