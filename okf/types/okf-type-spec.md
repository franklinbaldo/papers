---
type: "OKF Type Spec"
title: "OKF Type Spec"
description: "A document that specifies how one repository-defined type should be used. This file describes itself."
tags: [okf-type-spec]
timestamp: 2026-07-09T00:00:00Z
---

# OKF Type Spec

**`type` value:** `"OKF Type Spec"`
**Applies to:** every file under `okf/types/`, including this one.

## Purpose

OKF (`okf/SPEC.md`) deliberately does not register a fixed taxonomy of
`type` values — it leaves that to producers. This repository is a
producer that wants its types documented rather than implicit, so
each type gets one spec file here, and `okf/validate.py` enforces that
every concept document's `type` field matches one of them.

## Required fields (beyond OKF baseline)

None beyond OKF's own required `type`.

## Recommended fields

- `description` — one sentence.

## Conventional sections

Every type spec in `okf/types/` follows this shape:

1. `# <Type Name>` heading, restating the exact `type` string, the
   file globs it applies to, and 1-2 example filenames.
2. `## Purpose` — what the type is for, in prose, with enough context
   that someone unfamiliar with this repository's history understands
   why the type exists (not just what it contains).
3. `## Required fields (beyond OKF baseline)` — fields this repository
   requires for this type that OKF itself doesn't mandate. Usually
   "none" — OKF's baseline (`type` alone) is deliberately minimal, and
   this repository mostly relies on the "Recommended fields" and
   "Conventional sections" of each type rather than adding hard
   requirements `okf/validate.py` enforces.
4. `## Recommended fields` — which of OKF's recommended fields
   (`title`, `description`, `resource`, `tags`, `timestamp`) matter
   most for this type, and any repository-specific convention for
   them (e.g. what a `tags` value should look like).
5. `## Conventional sections` — expected body structure.
6. `## Notes` — anything else: known failure modes this type spec
   guards against, cross-references to related types, or open
   questions.

## Notes

Adding a new `type` to this repository means adding a new file here
in the same change — `okf/validate.py` treats an undocumented `type`
value as a lint failure, by design, so the type taxonomy can't
silently drift the way `sintese_programa.md`'s paper count did before
the 2026-07-09 audit.
