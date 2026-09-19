---
type: "OKF Type Spec"
title: "Dogmatic Paper"
description: "Position paper establishing a doctrinal thesis about Brazilian civil procedure (CPC 2015), part of the Raciocinio Juridico Auditavel dogmatic series."
tags: [okf-type-spec]
timestamp: 2026-07-09T00:00:00Z
---

# Dogmatic Paper

**`type` value:** `"Dogmatic Paper"`
**Applies to:** `auditable-legal-reasoning/embargos-de-declaracao-e-precedentes-vinculantes.md`, `auditable-legal-reasoning/embargos-de-declaracao-cpc-2015.md` through `auditable-legal-reasoning/livre-convencimento-patrimonialismo-judicial.md` (8 files at repo root).
**Examples:** `auditable-legal-reasoning/cinco-saidas-precedentes-vinculantes.md`, `auditable-legal-reasoning/vinculacao-racional-dialogo-institucional.md`.

## Purpose

A Dogmatic Paper advances a doctrinal thesis about Brazilian civil
procedure — what the CPC 2015 requires, with legally precise
argumentation grounded in statute, doctrine, and (where available) real
case law. These papers are in Portuguese, target legal practitioners
and academics, and together form the "eixo dogmatico" of the
Raciocinio Juridico Auditavel research programme (see
`auditable-legal-reasoning/research-program.md`).

## Required fields (beyond OKF baseline)

None beyond OKF's own required `type`.

## Recommended fields

- `title` — the paper's full academic title (already present as the
  file's first `# ` heading in every existing instance).
- `description` — one sentence stating the paper's core thesis, not
  its subject matter in the abstract. Compare the existing values in
  `README.md`.
- `tags` — at minimum, the paper's own short slug (`paper1a` .. `paper1g`,
  or `paper1-dogmatico` for the umbrella), so debate documents that
  attack or defend the paper's theses can be found by the same tag.
  See `.okf/specs/adversarial-critique.md` and
  `.okf/specs/supportive-defense.md`.
- `timestamp` — last substantive edit, not last mechanical edit
  (renames, frontmatter addition). Derived from `git log` at adoption
  time; keep it current by hand when the doctrinal content changes,
  since a bulk `git log`-derived value would otherwise also bump on
  purely mechanical commits.

## Conventional sections

Every existing Dogmatic Paper follows this shape and new ones SHOULD
too:

- `## Resumo` / `## Abstract` — Portuguese and English abstracts.
- Numbered sections developing the thesis.
- `## Objeções e Respostas` (where applicable) — anticipated
  counterarguments and responses; this is where absorbed conclusions
  from the adversarial/supportive debate apparatus land (see
  `archive/adversarial-paper-development/protocol.md`).
- `## Referências` — bibliography.
- A closing italicized line: series membership and version date.

## Notes

Dogmatic Papers are the ones most frequently targeted by
`Adversarial Critique` / `Supportive Defense` documents. When absorbing
a debate conclusion into a Dogmatic Paper's body, prefer adding a
scoped qualifier or a new short paragraph over rewriting existing
prose — see the commit history of `auditable-legal-reasoning/cinco-saidas-precedentes-vinculantes.md`
for a worked example of incremental, well-cited absorption.
