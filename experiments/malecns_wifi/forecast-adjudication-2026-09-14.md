---
type: "Adjudication"
title: "Joint adjudication rules for the two preregistered MaleCNS forecasts"
description: "Event definitions fixed before any matched-drive or Qwen result exists, so that both frozen forecasts are scored against the same disambiguated events."
tags: [malecns, forecast, preregistration, brier, adjudication]
timestamp: 2026-09-14T19:40:00+00:00
---

# Joint adjudication rules

Agreed between both forecasters **before** the matched-drive Run 1 rerun, the
Qwen replication, or any Run 2 result exists. Neither frozen forecast is edited
and no probability changes. This note fixes only what each event *means*, so that
two documents written independently are scored against the same targets.

* `preregistered-forecast-claude-2026-09-14.md` — 88 / 20 / 6 / 12
* `preregistered-forecast-chatgpt-2026-09-14.md` — 75 / 40 / 25 / 20

## Why this note exists

One defect and one looseness, both found by comparing the documents rather than
by either author reviewing their own.

**The defect is in the Claude forecast.** Its F4 requires the trainable-adapter
condition to beat the direct control *and* both topology nulls at a margin of
0.03 with 8 of 10 seeds in the same direction. That is a topological advantage.
Its F3 was not restricted to the frozen regime, so F3 covers any adequately
powered run including Run 2. Under those definitions `F4 => F3`, which forces
`P(F4) <= P(F3)`, and the registered numbers are 12% and 6%. The registration is
incoherent as written. The underlying intuition — a learned input projection
should help the operator more than a random one, so the adapter regime is the
better bet — is intelligible, but it only makes sense if F3 and F4 name
*different regimes*, which the document did not say.

**The looseness is in the ChatGPT forecast.** Its F4 can be satisfied either by
meeting the F3 topology criterion *or* by "otherwise showing a clearly
reproducible, control-surviving conditioned-learning effect". That disjunction
avoids the ordering problem but leaves the second branch open enough to be
argued after the fact.

## The four events, as they will be scored

**F1 — Useful tag-free tagging representation.** A tag-free front-end supports
multi-tag span placement on held-out documents, with no tag identity, food signal
or gold span entering the inference features. Each forecaster's own stated
threshold applies, because they differ deliberately and both were registered:
Claude requires macro per-tag AUPRC >= 2x prevalence, tag accuracy >= 3x chance,
*and* replication on Qwen; ChatGPT requires any-tag AUPRC >= 2x prevalence *and*
macro per-tag AUPRC >= 1.5x its baseline, without a replication requirement. The
stricter threshold is not adjusted downward for having been the bolder call.

**F2 — Frozen MaleCNS beats the direct control.** In the **frozen** regime, with
matched drive energy and the same tag-free input: MaleCNS exceeds its own paired
direct probe on held-out macro per-tag AUPRC. ChatGPT's 0.02 absolute margin and
Claude's 8-of-10 paired-seed consistency both apply to their own forecasts. A
result that appears only under unmatched drive does not count for either.

**F3 — Topology-specific advantage, frozen regime.** Restricted to the frozen
regime, to make the contrast with F2 well defined. MaleCNS beats the direct
control, the degree-preserving null **and** the matched random ESN, on held-out
macro per-tag AUPRC, mean paired effect >= 0.03, same sign in >= 8 of 10 seeds.
Beating the random ESN but not the degree-preserving null resolves **no**: that
outcome shows degree structure rather than wiring specificity is doing the work.

**F4 — Run 2 conditioned learning.** Restricted to the **trainable-adapter**
regime. After reward-conditioned training, at inference with only tag-free text
and no tag, mask or food, the adapter+MaleCNS condition beats the
parameter-matched direct-input control and both topology nulls, mean paired
effect >= 0.03, same sign in >= 8 of 10 seeds. The ChatGPT "or otherwise"
branch is closed: an effect that does not beat the direct-input control does not
resolve F4 yes, whatever else it shows.

With F3 and F4 naming disjoint regimes, `P(F4) > P(F3)` is coherent and both
registrations stand as written.

## What the disagreement actually is

Not an information asymmetry. Both forecasters had the operator characterisation
— spectral concentration 24.8x, the hemisphere-local degenerate leading pair, the
bulk losing the echo state property before reaching a useful operating point, the
86% leading-subspace clamping at bulk-matched — before registering. The 20-point
gaps on F2 and F3 are judgement about the same evidence.

The crux, stated by both sides:

* **Claude, lower.** The readout is a bottleneck (1,314 of 165,122 neurons, and
  compression rather than expansion for the 1,540-dimensional relations block);
  pretrained sentence embeddings are already close to linearly separable; the
  task is largely a per-chunk judgement rather than one needing temporal
  integration; and a degree-preserving rewiring keeps in-degree, out-degree and
  sign structure, which is most of what determines how a sparse operator behaves.
* **ChatGPT, higher.** Recurrent dynamics can add temporal information even over
  rich embeddings; and the real wiring carries structure beyond degrees and signs
  — sensory-to-internal-to-descending pathways, modularity, motifs, asymmetry and
  anatomical localisation — all of which the degree-preserving null destroys, so
  degrees and signs are not necessarily "most of" the relevant computation.

Implied conditionals: given F2, ChatGPT puts P(topology-specific) at about 62%
and Claude at about 30%. That single number is the disagreement.

## Scoring

Brier component `(p - outcome)^2` per event, outcome 1 or 0, mean over the four
events reported per forecaster. Events are resolved by the definitions above.
Neither document is edited, no probability is revised, and an ambiguity that
survives this note is resolved conservatively against the forecast claim.
