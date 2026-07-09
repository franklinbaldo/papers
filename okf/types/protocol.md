---
type: "OKF Type Spec"
title: "Protocol"
description: "Canonical rules document for a repeatable process this repository runs (currently: the adversarial/supportive/synthesis debate apparatus)."
tags: [okf-type-spec]
timestamp: 2026-07-09T00:00:00Z
---

# Protocol

**`type` value:** `"Protocol"`
**Applies to:** `PROTOCOL.md`. Currently the only file of this type.

## Purpose

A Protocol document states the actual rules governing a repeatable
process in one canonical place, so they don't have to be
reconstructed by reading dozens of session logs. `PROTOCOL.md` exists
because a 2026-07-09 audit found the debate apparatus's real rules
(edit-cycle cadence, overdue-obligation handling, loop-cutoff
behavior) reconstructible only from prose scattered across 55
`synthesis/blog/` entries, with no canonical document anywhere.

## Required fields (beyond OKF baseline)

None beyond OKF's own required `type`.

## Recommended fields

- `description` — name the process the protocol governs.

## Conventional sections

`PROTOCOL.md`'s structure — role definitions, then one section per
rule with an explicit "previous rule / problem observed / revised
rule" structure where a rule has changed — is worth preserving for
future Protocol documents, since the "why did this rule change"
context is exactly what tends to get lost when rules only exist as
scattered session-log prose.

## Notes

If this repository's process changes (e.g. the debate apparatus's
absorption trigger is revised again), update `PROTOCOL.md` in the same
change, not as a follow-up — a stale Protocol document is worse than
none, since it's trusted as canonical.
