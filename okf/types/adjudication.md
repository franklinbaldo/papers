---
type: "OKF Type Spec"
title: "Adjudication"
description: "Rules fixing what preregistered events mean, agreed before the results exist, so independent forecasts are scored against the same targets."
tags: [okf-type-spec]
timestamp: 2026-09-14T20:10:00+00:00
---

# Adjudication

**`type` value:** `"Adjudication"`
**Applies to:** `experiments/*/forecast-adjudication-*.md`

## Purpose

Two forecasts written independently will define their events slightly
differently, and one of them may define them incoherently. An Adjudication fixes
what each event *means* so both are scored against the same targets, and it must
be dated before any relevant result exists.

## Rules

* It **disambiguates events; it never changes a probability**. The registered
  documents are not edited.
* It may close a loose disjunction or restrict an event's scope, and it records
  why.
* Any ambiguity surviving the note is resolved conservatively **against** the
  forecast claim, so that vagueness never helps a forecaster.
