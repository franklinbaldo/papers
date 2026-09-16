---
type: "PreregisteredForecast"
title: "MaleCNS semantic tagging — ChatGPT forecast before matched-drive/Qwen results"
timestamp: 2026-09-14T18:30:00-04:00
status: "frozen"
forecaster: "ChatGPT"
experiment: "MaleCNS semantic tagging / PR #441"
---

# Preregistered forecast — ChatGPT

This forecast is frozen **before** reading the matched-drive MiniLM reservoir rerun, the Qwen3-Embedding-0.6B replication, or any trainable-adapter Run 2 result. Earlier pilot evidence is already known and is part of the information set: tag-free sensation is measurable, multi-tag direct probes are above chance, relations beat absolute in the preliminary direct multi-tag result, and the first reservoir numbers were confounded by unequal drive energy.

The purpose is calibration, not advocacy. Later results should be scored against these probabilities without retroactively changing the definitions.

## Forecasts

### F1 — Useful tag-free tagging representation: **75%**

Event: a text with **no tags supplied at inference** can be mapped through the frozen semantic front-end (absolute embeddings, multiscale child/parent relations, or their combination) to support useful multi-tag span placement on held-out documents.

Operational success criterion: after validation-only hyperparameter selection, at least one tag-free representation produces both:

- any-tag AUPRC >= 2x its prevalence baseline; and
- macro per-tag AUPRC >= 1.5x the corresponding macro prevalence/chance baseline,

on held-out documents, with no tag identity, food signal, or gold span entering the inference features.

This forecast concerns the semantic tagging idea broadly, not a MaleCNS advantage.

### F2 — MaleCNS adds useful information beyond the direct probe: **40%**

Event: under matched drive energy and the same tag-free input representation, the frozen MaleCNS state improves over the direct no-connectome control.

Operational success criterion: on held-out documents, MaleCNS exceeds the paired direct control by >= 0.02 absolute macro per-tag AUPRC, with the same folds, representation, flavour targets, penalty-selection protocol, and encoder. A result that appears only under unmatched drive does not count.

### F3 — MaleCNS topology-specific advantage: **25%**

Event: the advantage is specific to the real connectome topology rather than generic recurrence or degree structure.

Operational success criterion for the eventual adequately powered run: MaleCNS beats **direct control, degree-preserving null, and matched random ESN** in the same training regime, with mean paired effect >= 0.03 macro per-tag AUPRC and at least 8/10 seeds in the same direction. This is the preregistered strong topology claim; weaker pilot differences do not satisfy it.

### F4 — Strong paper-level conditioned-learning result: **20%**

Event: Run 2, with a trainable interface around frozen MaleCNS, produces a reproducible result strong enough to support a paper claim that conditioned training improves tag placement at inference when **no tag and no food signal are supplied**.

Operational success criterion: after validation-only model selection and on held-out documents, the trained MaleCNS condition satisfies the topology criterion in F3 or otherwise shows a clearly reproducible, control-surviving conditioned-learning effect that cannot be attributed to the semantic encoder, direct adapter capacity, drive-energy mismatch, position, or label leakage.

## Qualitative prediction

The most likely success ordering is:

1. semantic representation / chunk relations work;
2. generic recurrence may help;
3. MaleCNS-specific topology advantage is harder;
4. a strong conditioned-learning paper result is hardest.

In one sentence: **I am more confident that the multiscale semantic tagging interface works than that the fly connectome itself provides the decisive advantage.**

## Scoring rule

When the relevant experiments close, record each event as 1 (occurred) or 0 (did not occur) and compute the Brier component `(p - outcome)^2` for each forecast. Do not redefine an event after seeing the result; ambiguities should be resolved conservatively against the forecast claim.
