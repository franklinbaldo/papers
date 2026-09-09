---
type: "OKF Type Spec"
title: "Scientific Position Paper"
description: "Research-grounded natural-science position papers that derive a falsifiable hypothesis or research agenda from the literature without claiming unperformed experiments as results."
tags: [okf-type-spec]
timestamp: 2026-09-08T20:15:00-04:00
---

# Scientific Position Paper

**`type` value:** `"Scientific Position Paper"`

## Purpose

A Scientific Position Paper develops a natural-science hypothesis, synthesis, or research agenda from primary and peer-reviewed literature. It may contain original derivations from published equations or scaling laws, but it must distinguish those derivations from empirical results and must not imply that proposed simulations or experiments have been performed.

This type is intentionally separate from `Technical Paper`, whose historical use in this repository is methodology/tooling for the legal-formal and machine-learning programmes.

## Required fields (beyond OKF baseline)

None beyond OKF's required `type`.

## Recommended fields

- `title`
- `description`
- `tags`
- `timestamp`

## Honesty convention

A paper of this type should open with a visible status statement when its central thesis is prospective. Claims should be labeled as one of: literature result, algebraic consequence/derivation, hypothesis, proposed test, or open uncertainty when the distinction would otherwise be ambiguous.

If a motivating result is newly announced, preprint-only, disputed, or not yet independently validated, that status must be stated explicitly. Negative derivations and falsifiers are first-class results: a paper should preserve them even when they narrow the original intuition that motivated the investigation.
