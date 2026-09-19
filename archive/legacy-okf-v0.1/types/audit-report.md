---
type: "OKF Type Spec"
title: "Audit Report"
description: "Point-in-time external review of some part of this repository, with findings and an execution-status log."
tags: [okf-type-spec]
timestamp: 2026-07-09T00:00:00Z
---

# Audit Report

**`type` value:** `"Audit Report"`
**Applies to:** `propostas_melhoria_2026-07-09.md`. Future audits
should get their own dated file of this type rather than extending
this one indefinitely — see Notes.

## Purpose

An Audit Report is a dated, external (i.e. not produced by the routine
debate apparatus itself) review that finds and proposes fixes for
problems, then records what was actually decided and executed,
distinct from the proposal. It complements, but is not a replacement
for, `synthesis/blog/`'s ongoing per-session record.

## Required fields (beyond OKF baseline)

None beyond OKF's own required `type`.

## Recommended fields

- `description` — one line naming the scope of the audit.
- `timestamp` — the audit's own date, not the date of the most recent
  status update appended to it (see Notes on why this file keeps
  growing rather than being re-dated).

## Conventional sections

`propostas_melhoria_2026-07-09.md`'s structure is the reference
pattern:

1. A status-update blockquote at the very top, appended to (not
   rewritten) each time a decision is made or work is executed —
   this preserves the sequence of "what was proposed" vs. "what was
   decided" vs. "what was actually done," which matters when they
   don't fully coincide.
2. Findings grouped into priority tiers, each with concrete file/line
   citations and a proposed fix — not vague direction.
3. A closing "how I can help from here" section offering a menu of
   next actions at different scopes, rather than assuming the whole
   report will be actioned at once.

## Notes

This file is intentionally allowed to keep accumulating status-update
blockquotes rather than being re-organized after each execution round
— the sequence of proposal-then-decision-then-execution is itself
part of the record. A genuinely new audit (different scope, different
date, independent of this one) should be a new file, not a new
top-level section appended here.
