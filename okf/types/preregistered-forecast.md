---
type: "OKF Type Spec"
title: "Preregistered Forecast"
description: "A numerical forecast registered before the result exists, with resolution criteria and a scoring rule fixed in advance."
tags: [okf-type-spec]
timestamp: 2026-09-14T20:10:00+00:00
---

# Preregistered Forecast

**`type` values:** `"Forecast"`, `"PreregisteredForecast"`
**Applies to:** `experiments/*/preregistered-forecast-*.md`

## Purpose

A record of what someone expected *before* the experiment resolved, written so
that being wrong is visible afterwards. Without it, a result always looks like
what everyone anticipated, and the calibration information is lost.

## Required content

* One probability per event, as an exact number.
* The **resolution criterion** for each: what observation would count as the
  event occurring. Written before the data exists, so it cannot be adjusted to
  fit.
* The **failure modes priced into the number**, so a wrong forecast can be
  diagnosed rather than merely scored.
* The **information state at registration** — what was already measured and what
  was still unknown.
* A scoring rule, normally Brier `(p - outcome)^2`.

## Rules

A registered forecast is **frozen**. Probabilities are never revised after the
fact; a changed view is recorded in a new document or in an adjudication note.
Where two forecasters register independently, neither reads the other before
committing.
