---
type: "Protocol"
---

# Preregistered benchmark — MaleCNS on MultiEURLEX-21 Portuguese

Date: 2026-09-15

## Question

Can a MaleCNS-based classifier perform useful real-world multilabel legal topic classification on a consolidated public benchmark, under the official MultiEURLEX/MTEB Portuguese split, without spending accelerator time reproducing published competitors?

## Benchmark

- Task: `MultiEURLEXMultilabelClassification`
- Dataset: `mteb/eurlex-multilingual`
- Subset/language: `pt` (`por-Latn`)
- Labels: 21 EUROVOC concepts
- Use the dataset-provided `train`, `validation`, and `test` splits as published. Do not reshuffle or relabel them.
- Dataset source/version must be recorded in the result artifact (HF revision when available).

## Arms that may consume accelerator time

1. `malecns_independent`: MaleCNS with peer coupling disabled.
2. `malecns_state_uncertainty`: MaleCNS with the state-conditioned uncertainty coupling rule from PR #460.

No accelerator time is to be spent rerunning external competitors merely for leaderboard comparison.

## External competitors

Competitor scores come from the public Hugging Face MTEB results dataset / official benchmark sources. Every imported comparison row must record:

- model name;
- model revision if provided;
- exact task name;
- split;
- subset/language;
- metric/score field as published;
- source URL / source dataset;
- whether the row is directly comparable to the MaleCNS result.

Rows whose metric, split, language, label set, or evaluation protocol differs are retained only as context and marked `comparable=false`; they must not be used to claim a win/loss.

## Metrics

Preserve the metric(s) emitted by the official MTEB task/evaluator whenever technically possible. In addition, compute from MaleCNS multilabel probabilities on the untouched test split:

- micro-F1;
- macro-F1;
- micro average precision (multilabel AUPRC/mAP-style summary);
- macro average precision when defined.

Threshold selection, if needed for F1, must use the official validation split only. Test labels must never affect threshold selection, training, stopping, or architecture choice.

## First execution

A smoke run may use a deterministic prefix/sample of the official train/validation/test splits solely to validate I/O, shapes, checkpointing, and metric code. Smoke numbers are not benchmark evidence.

The first benchmark evidence run uses the full Portuguese official splits unless a documented resource limit forces a preregistered deterministic cap. Any cap makes the result `partial_benchmark` and not directly comparable to full MTEB leaderboard values.

## Scientific hygiene

- No tuning against test labels.
- No changes to labels or split membership.
- No post-hoc selection of favorable competitors.
- Store predictions, thresholds, metrics, timing, dataset revision, code commit, and executor provenance.
- The benchmark starts with Portuguese only. Other languages require a new extension protocol.
