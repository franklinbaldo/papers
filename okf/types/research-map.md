---
type: "OKF Type Spec"
title: "Research Map"
description: "Canonical map of a multi-paper research programme: initiatives, relationships, evidence state, dependencies, and source-of-truth boundaries."
tags: [okf-type-spec, research-program]
timestamp: 2026-09-19T15:00:00-04:00
---

# Research Map

**`type` value:** `"Research Map"`

**Applies to:** canonical programme maps that organize several papers, experiments, repositories, and adjacent initiatives without duplicating their substantive claims.

## Purpose

A Research Map is the source of truth for **relationships and current programme state** across multiple research artifacts. It is not itself evidence for a scientific claim and must not silently promote hypotheses into findings.

Use it to record:

- initiative identity and scope;
- parent/sibling/adjacent relationships;
- current evidence status;
- canonical papers and repositories;
- dependencies and interfaces between initiatives;
- explicit boundaries between evidence, hypothesis, protocol, and infrastructure;
- the next discriminating question when one is already frozen elsewhere.

## Anti-duplication rule

Dynamic programme status belongs in the Research Map. Individual papers should contain only a short, stable **Research programme position** section that states their own scope and points to the canonical map. They should not copy a large status table that will drift.

## Evidence discipline

Statuses such as `evidence-positive`, `evidence-negative`, `mixed`, `protocol`, and `hypothesis` describe the programme's current public evidence record. They do not replace the underlying paper, protocol, findings record, run artifact, or prior-art audit.

## Required fields in the body

- scope and non-scope;
- initiative graph/tree;
- status vocabulary;
- canonical artifact for each initiative;
- evidence/hypothesis boundary;
- maintenance rule.
