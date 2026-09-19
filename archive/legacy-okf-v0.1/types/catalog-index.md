---
type: "OKF Type Spec"
title: "Index"
description: "Human-facing catalog and reading guide; this repository's adaptation of OKF's index.md convention to README.md."
tags: [okf-type-spec]
timestamp: 2026-07-09T00:00:00Z
---

# Index

**`type` value:** `"Index"`
**Applies to:** `README.md`.

## Purpose

Provides orientation: what documents exist, grouped by axis/type, each
with a one-line description, plus pointers to the debate apparatus and
its rules. Serves the same role OKF's reserved `index.md` filename
serves (§6 of `okf/SPEC.md`: "progressive disclosure — letting a human
or agent see what is available before opening individual documents"),
under a different, GitHub-conventional filename.

## Why `README.md` and not `index.md`

GitHub renders `README.md` on a repository's landing page automatically;
`index.md` gets no such treatment. Since this repository's single most
important audience is a human landing on the GitHub page, `README.md`
keeps that behavior. This is a deliberate divergence from OKF's literal
reserved-filename convention, not an oversight — `README.md` is **not**
in OKF's reserved-filename list (`index.md`, `log.md` only), so under a
strict reading it required frontmatter like any other concept document,
which it now has. `okf/index.md` uses the literal reserved filename
(frontmatter-free, per spec) for the `okf/` subdirectory specifically,
where GitHub's special-casing doesn't apply and OKF's own convention is
the more natural fit.

## Required fields (beyond OKF baseline)

None beyond OKF's own required `type`.

## Recommended fields

- `okf_version` — this repository's `README.md` carries `okf_version:
  "0.1"` as a custom frontmatter key (OKF permits arbitrary producer-
  defined keys on any concept document). This isn't literally what
  §11 of `okf/SPEC.md` specifies (that section only names bundle-root
  `index.md` as the place for this field) — it's a deliberate
  adaptation given `README.md`'s functional role, documented here so
  the divergence is visible rather than silent.

## Conventional sections

One heading per axis/type grouping, each a bullet list of
`` `filename.md` — one-line description ``, matching the frontmatter
`description` field of each linked document where one exists.

## Notes

If `README.md`'s per-file descriptions and each file's own frontmatter
`description` field ever diverge, treat that as a real inconsistency
to fix, not a stylistic difference — `okf/validate.py` does not
currently check this automatically (see its module docstring for why),
so it requires human vigilance.
