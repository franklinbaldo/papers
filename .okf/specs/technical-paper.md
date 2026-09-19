---
type: "OKF Type Spec"
title: "Technical Paper"
description: "English-language position or methodology paper developing the formal/technical tooling that implements the dogmatic series."
tags: [okf-type-spec]
timestamp: 2026-07-09T00:00:00Z
---

# Technical Paper

**`type` value:** `"Technical Paper"`
**Applies to:** `auditable-legal-reasoning/lean-argdown-pipeline.md`, `auditable-legal-reasoning/claim-provenance.md`,
`archive/adversarial-paper-development/methods/embedding-seeded-tournament.md` (ESHTR), `semantic-tokenization/semantic-tokenization-transformers.md` (STT).
**Examples:** `auditable-legal-reasoning/lean-argdown-pipeline.md`, `archive/adversarial-paper-development/methods/embedding-seeded-tournament.md`.

## Purpose

A Technical Paper develops methodology, tooling, or evaluation
infrastructure in English. Three of the four (`auditable-legal-reasoning/lean-argdown-pipeline.md`,
`auditable-legal-reasoning/claim-provenance.md`, ESHTR) are built specifically to formalize or
evaluate the dogmatic series and are counted inside the "Raciocinio
Juridico Auditavel" programme's eleven-paper scope (`auditable-legal-reasoning/research-program.md`).
STT is a general tokenization-architecture proposal that happens to live
in this repository but is **not** part of that programme — see
`auditable-legal-reasoning/research-program.md`'s Resumo for the explicit scope boundary. Don't
infer programme membership from `type` alone; check `tags`.

## Required fields (beyond OKF baseline)

None beyond OKF's own required `type`.

## Recommended fields

- `tags` — include the paper's slug (`pipeline`, `proveniencia`, `eshtr`,
  `stt`). For ESHTR and STT specifically, also consider whether the
  paper is empirically load-bearing for the dogmatic programme (ESHTR)
  or a separate general-AI thread (STT), and reflect that distinction
  in prose if not in tags.
- `description`.

## Conventional sections

ESHTR and STT open with a `> **Position paper.**` blockquote banner
(see `.okf/specs/interpretability-paper.md` for the shared convention).
`auditable-legal-reasoning/lean-argdown-pipeline.md` and `auditable-legal-reasoning/claim-provenance.md` do not use this
banner — they describe an implemented pipeline with a demonstrated
worked example, not an unrealized design — but they DO disclose where
the implementation lives (`franklinbaldo/skills`, external to this
repository) rather than claiming in-repo verifiability. Any new
Technical Paper should pick one of these two honesty conventions
explicitly, not silently imply completed results it doesn't have (see
`.okf/specs/empirical-paper.md` for the failure mode this guards against).

## Notes

Filenames in this repository do not carry sequential paper numbers
(`paper2_`, `paper3_`, etc.) — this was a deliberate 2026-07-09 rename
(see `propostas_melhoria_2026-07-09.md`) because the numbering implied
a single linear reading order that never existed (three research axes
share the numbering; a "Paper 4" was referred to in other papers' prose
for years without ever being assigned a file — ESHTR). If a Technical
Paper is ever added, name it descriptively (as `archive/adversarial-paper-development/methods/embedding-seeded-tournament.md`
and `semantic-tokenization/semantic-tokenization-transformers.md` already are), not by number.
Cite it by name in prose too, not by an ordinal that has no
corresponding, stable file identity.
