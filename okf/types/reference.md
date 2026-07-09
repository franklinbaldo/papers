---
type: "OKF Type Spec"
title: "Reference"
description: "Vendored external material, mirrored into this repository so this repository's OKF adoption does not depend on that material staying reachable."
tags: [okf-type-spec]
timestamp: 2026-07-09T00:00:00Z
---

# Reference

**`type` value:** `"Reference"`
**Applies to:** `okf/SPEC.md`. Currently the only file of this type;
would also apply to any future vendored external document (e.g. a
copy of a cited standard) that this repository chooses to mirror
rather than only link to.

## Purpose

`Reference` is one of OKF's own example `type` values (§4.1 of
`okf/SPEC.md`: "Example values: BigQuery Table, BigQuery Dataset, API
Endpoint, Metric, Playbook, Reference"). This repository uses it for
external material vendored in verbatim, distinct from every other type
here, which describes original content produced by this repository's
authors or its debate apparatus.

## Required fields (beyond OKF baseline)

- `resource` — the canonical external URL the content was vendored
  from. Required (not just recommended) for this type specifically,
  since a Reference document's entire purpose is to mirror something
  external, and without `resource` a reader can't tell what it's a
  copy of or check it against updates.

## Recommended fields

- `description`, `timestamp` (of the vendoring, not of the upstream
  document's own last change, which this repository doesn't track).

## Conventional sections

A vendoring note near the top of the body — before the mirrored
content itself — stating what was vendored, from where, when, and why
(typically: so this repository's own conformance doesn't depend on an
external repository staying reachable or unchanged). See `okf/SPEC.md`'s
own vendoring note for the pattern.

## Notes

If the upstream source publishes a new version, update the vendored
copy and its `timestamp` together, and check whether anything in
`okf/types/` or `okf/validate.py` needs to change to match.
