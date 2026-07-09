---
type: "OKF Type Spec"
title: "Technical Paper"
description: "English-language position or methodology paper developing the formal/technical tooling that implements the dogmatic series."
tags: [okf-type-spec]
timestamp: 2026-07-09T00:00:00Z
---

# Technical Paper

**`type` value:** `"Technical Paper"`
**Applies to:** `paper2_pipeline_lean_argdown.md`, `paper3_proveniencia_claims.md`,
`embedding_seeded_tournament_paper.md` (ESHTR), `semantic_tokenization_transformers.md` (STT).
**Examples:** `paper2_pipeline_lean_argdown.md`, `embedding_seeded_tournament_paper.md`.

## Purpose

A Technical Paper develops methodology, tooling, or evaluation
infrastructure in English. Three of the four (`paper2`, `paper3`,
ESHTR) are built specifically to formalize or evaluate the dogmatic
series and are counted inside the "Raciocinio Juridico Auditavel"
programme's eleven-paper scope (`paper6_sintese.md`). STT is a
general tokenization-architecture proposal that happens to live in
this repository but is **not** part of that programme — see
`paper6_sintese.md`'s Resumo for the explicit scope boundary. Don't
infer programme membership from `type` alone; check `tags`.

## Required fields (beyond OKF baseline)

None beyond OKF's own required `type`.

## Recommended fields

- `tags` — include the paper's slug (`paper2`, `paper3`, `eshtr`,
  `stt`). For ESHTR and STT specifically, also consider whether the
  paper is empirically load-bearing for the dogmatic programme (ESHTR)
  or a separate general-AI thread (STT), and reflect that distinction
  in prose if not in tags.
- `description`.

## Conventional sections

ESHTR and STT open with a `> **Position paper.**` blockquote banner
(see `okf/types/interpretability-paper.md` for the shared convention).
`paper2` and `paper3` do not use this banner — they describe an
implemented pipeline with a demonstrated worked example, not an
unrealized design — but they DO disclose where the implementation
lives (`franklinbaldo/skills`, external to this repository) rather
than claiming in-repo verifiability. Any new Technical Paper should
pick one of these two honesty conventions explicitly, not silently
imply completed results it doesn't have (see `okf/types/empirical-paper.md`
for the failure mode this guards against).

## Notes

If a Technical Paper is ever added as `paper4_*`, retire the "ESHTR
is informally called Paper 4 by other papers' prose" pattern that
existed before 2026-07-09 — it referred to a paper number that was
never actually assigned a file. Cite ESHTR by name, not by number,
unless a real `paper4_*.md` exists.
