---
type: "OKF Type Spec"
title: "Empirical Paper"
description: "Pre-registered empirical evaluation design; reports results only once data collection has actually happened."
tags: [okf-type-spec]
timestamp: 2026-07-09T00:00:00Z
---

# Empirical Paper

**`type` value:** `"Empirical Paper"`
**Applies to:** `paper5_empirical_evaluation.md`. Currently the only file
of this type; a second would be created if the RPPS corpus evaluation
in `paper5` is extended or a new empirical study is designed.

## Purpose

An Empirical Paper specifies (and, once run, reports) a quantitative
evaluation against a real corpus. As of 2026-07-09, `paper5` is a
**pre-registered design with no data collected yet** — this is the
single most important fact about this type, enforced structurally
below because a 2026-07-09 audit (`propostas_melhoria_2026-07-09.md`,
finding 0.1) found this exact paper's introduction claiming completed
results its own conclusion admitted did not exist.

## Required fields (beyond OKF baseline)

None beyond OKF's own required `type`.

## Recommended fields

- `description` — MUST NOT claim results exist if they don't. Compare
  the current value: "desenho pre-registrado de avaliacao empirica...
  (resultados ainda nao coletados)" — the parenthetical is load-bearing,
  not decorative.

## Conventional sections

- A `> **Pre-registered design; no results yet.**` banner immediately
  after the author block, mirroring ESHTR/STT/Pontifex's
  `> **Position paper.**` convention but worded for the empirical case
  specifically.
- Every section that will eventually hold results (e.g. `## 3. Results`)
  MUST be honest about its current status — either fully absent, or
  explicitly labeled as a design/expected-output template ("Expected
  Output", not "Output"), consistent throughout the whole document
  (introduction, method, results, and conclusion sections must all
  agree on whether data has been collected — the 2026-07-09 audit's
  finding was specifically an *inconsistency* between sections, not a
  single wrong sentence).
- `## Pre-registration` note with a link, once one exists (currently
  `[LINK]`, deliberately left unresolved — see `paper5`'s footer and
  `propostas_melhoria_2026-07-09.md`'s Nivel 4 notes on why this
  wasn't guessed at).

## Notes

When `paper5` (or a future Empirical Paper) actually collects data,
the update needs to touch every section consistently in the same
commit: abstract, introduction, results, conclusion, and this file's
banner. A partial update that leaves even one section in the old
"no data yet" state reintroduces the exact inconsistency this type
spec exists to prevent.
