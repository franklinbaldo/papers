---
type: "OKF Type Spec"
title: "Experiment Report"
description: "Executed-experiment report that records method, observed results, diagnostics, and bounded interpretation for one experiment or experiment ladder."
tags: [okf-type-spec]
timestamp: 2026-09-18T00:00:00-04:00
---

# Experiment Report

**`type` value:** `"Experiment Report"`

**Applies to:** dated reports and paper addenda under `experiments/` that document an experiment or experiment ladder that has actually been executed.

## Purpose

An Experiment Report records an executed experiment with enough methodological and interpretive context to stand as a readable research artifact. It is appropriate when a document does more than preserve raw gate outcomes: it explains the question, discriminating design, measurements, observed behavior, and bounded interpretation.

It differs from a **Protocol**, which freezes rules before execution, and from a **Findings Record**, which is the narrower evidence layer tied directly to a registered protocol and its gates. It also differs from an **Empirical Paper**, which makes a larger citable contribution rather than reporting one experimental slice.

## Required fields (beyond OKF baseline)

None beyond the OKF baseline. The body must make clear what was executed and must not present unrun work as an observed result.

## Recommended fields

- `title` and `description`;
- `timestamp` or execution date;
- links or paths to the executable experiment and produced artifacts;
- an explicit claim boundary where post-hoc interpretation is present.

## Conventional sections

Question · design/method · result · diagnostics/controls · interpretation · claim boundary.

## Notes

A negative or null result remains a valid Experiment Report. The type carries no presumption that the experiment supported its motivating hypothesis.
