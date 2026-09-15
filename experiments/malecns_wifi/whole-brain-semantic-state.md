---
type: "Protocol"
title: "Whole-Brain Semantic State with Flavourized Recurrent Feedback"
description: "Pre-registered follow-up separating semantic state decoding from descending/action readout, then testing flavourized feedback through the frozen MaleCNS state."
tags: [malecns, semantic-tagging, whole-brain, flavourizer, recurrence, preregistration]
timestamp: 2026-09-14T21:24:00-04:00
status: "pre-registered; no confirmatory results yet"
---

# Whole-Brain Semantic State with Flavourized Recurrent Feedback

> **New follow-up cell.** This protocol does not alter, rescue, or reinterpret the registered F3 decision rule. F3 remains the experiment that reads the descending population and requires MaleCNS to beat its registered direct and topology controls. This follow-up asks a different question that F3 was not designed to answer.

## Motivation

The current F3 recurrent dynamics update the complete MaleCNS state (~165k neurons), but the semantic decoder observes only the descending population (~1.3k neurons). That is biologically sensible if the question is *what action leaves the brain?* It is not the natural primary observation if the question is *what semantic information is represented inside the brain?*

The distinction is explicit:

```text
semantic input
   -> sensory interface
   -> complete recurrent MaleCNS state H_t
      |-> semantic state probe: what is represented?
      `-> descending/action port: what should the body/text controller do?
```

Descending neurons are retained as an action-oriented diagnostic and as a future control port. They are not privileged as the semantic readout in this follow-up.

A second motivation comes from the flavourization hypothesis. A frozen connectome need not be a good zero-shot transform of an arbitrary embedding geometry. A trainable low-rank flavourizer may instead learn, over many training epochs, to present semantic distinctions in directions that the recurrent substrate can preserve or amplify. The recurrent operator remains frozen; only the interface/taste/tag heads learn.

## Questions

### Q1 — wrong door / readout capacity

How much semantic information is present in the complete recurrent state, and how much is lost specifically by reading only descending neurons?

### Q2 — matched-budget whole-brain decoding

When the whole state is projected through a fixed random map to the same dimensional budget as a comparator, does the apparent semantic deficit shrink?

### Q3 — flavourized recurrent feedback

Can a trainable semantic flavourizer improve the final standalone tagger when its auxiliary feedback is computed from the whole recurrent state rather than only the descending action port?

### Q4 — topology specificity

If assistance helps, is the effect specific to MaleCNS wiring rather than generic recurrence or an extra auxiliary loss?

### Q5 — recurrent depth

Does giving the frozen recurrent dynamics more internal steps per semantic chunk improve the learned interface or state decodability?

## Stage A — frozen-state readout ladder

The representation, corpus, outer held-out-document split, tags, operator construction, drive calibration, seed policy, nested ridge selection, and gain-selection discipline remain matched to the audited F3 machinery. The only new axis is what portion of the recurrent state is exposed to the semantic probe.

Readouts are frozen before execution:

1. `descending_1314` — anatomical descending population; existing F3 semantic port.
2. `random_1314` — 1,314 random neurons, matched width.
3. `wholebrain_projected_1314` — fixed random projection of all neurons to width 1,314.
4. `wholebrain_projected_inputdim` — fixed random projection of all neurons to the semantic block width used by the comparator.
5. `wholebrain_projected_sensorydim` — fixed random projection of all neurons to the sensory-interface width.
6. `wholebrain_full` — all recurrent neurons, diagnostic ceiling only.

The fixed whole-brain projections are seeded, non-trainable, and identical across MaleCNS/degree-null/random-ESN comparisons for a seed and width. They may not see labels.

`wholebrain_full` is **not** a claim condition because p >> n is extreme. It is an information ceiling: if the full state scores well while matched-budget projections do not, the result is reported as readout/compression sensitivity rather than a clean semantic win.

### Stage-A primary contrast

`wholebrain_projected_1314 - descending_1314`

A wrong-door effect is supported only if mean held-out macro per-tag AUPRC improves by at least `+0.03` and the paired sign is positive in at least 8/10 seeds.

### Stage-A secondary contrasts

Report, without substituting them for the primary contrast after seeing results:

- `random_1314 - descending_1314`;
- `wholebrain_projected_inputdim - direct_raw`;
- `wholebrain_projected_sensorydim - projected_direct`;
- `wholebrain_full` as the diagnostic ceiling;
- every readout's gain-0 delta;
- MaleCNS vs degree-null vs random-ESN at each matched readout width.

Dimensional equality is not claimed to make two architectures identical; it removes one obvious capacity asymmetry and is reported as such.

## Stage B — whole-brain flavourized assistance

Stage B is stacked on the trainable flavourizer design from #443/#444. The deployable tagger remains:

```text
untagged text
  -> cached semantic channels
  -> low-rank residual flavourizer
  -> tag head
  -> tags/spans
```

No connectome, food target, taste head, gold mask, or tag text exists at held-out inference.

During the assisted portion of training only:

```text
semantic channels
  -> trainable flavourizer
  -> fixed sensory projection
  -> frozen recurrent operator
  -> fixed whole-brain state projection
  -> disposable taste head
  -> flavour/food auxiliary loss
  -> gradient back through recurrence into flavourizer
  -> next training epoch
  -> repeat
```

The whole-brain state projection is fixed and unlabelled. It is not an additional learned semantic model.

### Stage-B arms

1. `tag_only` — identical deployable model, no recurrent auxiliary branch.
2. `malecns_assisted` — frozen MaleCNS recurrent auxiliary branch.
3. `degree_null_assisted` — independently redrawn degree-preserving null per registered seed.
4. `random_esn_assisted` — matched random recurrent control.

All arms share data, outer folds, final deployable parameter count, optimizer budget, seed policy, flavourizer rank, tag head, stopping rule and evaluation.

### Primary Stage-B outcome

Held-out macro per-tag AUPRC of the **standalone final tagger after the recurrent branch is absent**.

Secondary outcomes:

- any-tag AUPRC;
- boundary AUPRC;
- tag identity accuracy on true spans;
- per-document paired deltas;
- sample efficiency;
- residual magnitude `||Delta|| / ||C||`;
- taste loss trajectory;
- whole-brain state decodability during training;
- drive RMS;
- gradient norm reaching the flavourizer from the auxiliary branch.

### Stage-B gates

A generic assistance claim requires `malecns_assisted - tag_only >= +0.03` macro per-tag AUPRC and positive held-out document deltas in at least 12/17 documents.

A topology-specific claim additionally requires MaleCNS to beat **both** `degree_null_assisted` and `random_esn_assisted` by at least `+0.02` macro per-tag AUPRC, with positive paired document deltas in at least 12/17 documents for each contrast.

No topology claim is allowed from taste loss alone.

## Recurrent depth

The current short rollout is not assumed to be the correct semantic timescale. This follow-up freezes a recurrent-depth ladder before execution:

`4 / 16 / 64 steps per chunk`

Depth is selected only inside the training data of each outer held-out-document fold. The held-out document never selects depth, gain, ridge, epoch, or stopping point.

The same depth-selection procedure is applied independently to MaleCNS, degree-null and random-ESN. No operator receives a preferred depth merely because it is cheaper or because another operator selected it.

A claim that *deeper recurrence itself* matters requires the best predeclared deep setting (`16` or `64`) to beat `4` by at least `+0.02` held-out macro per-tag AUPRC and have a positive paired document delta in at least 12/17 documents. Otherwise recurrent depth is reported as a selected operating point, not a mechanism claim.

If `64` is the selected boundary, that is recorded as right-censoring. Extending to 128/256 after seeing that result is a separate preregistered follow-up, not a rescue of this cell.

## Gain

F3 showed strong selection pressure toward the high end of its registered gain grid. This follow-up is allowed to use that result as prior evidence because it is a new experiment, but it must not rewrite F3.

For comparability, the initial confirmatory gain grid remains:

`0.0 / 0.25 / 0.5 / 0.95 / 1.5 / 2.5 / 4.0`

`0.0` remains a reported recurrence-off condition. If `4.0` again behaves as a right boundary, a wider grid requires a separately frozen follow-up.

## Readout budgets and overfitting

There are far more brain neurons than chunks. Therefore:

- `wholebrain_full` is a ceiling, never the primary confirmatory condition;
- matched-budget projections are fixed before labels and before fitting the decoder;
- ridge/regularisation is selected within training folds only;
- all projection seeds are logged;
- the number of exposed features is reported for every arm;
- no learned dimensionality reducer may be added post-result as a rescue.

## Perception versus action

This protocol deliberately reserves descending neurons for a later action layer. A future text-control experiment may map recurrent state/descending activity to operations such as advancing a cursor, opening/closing a span, emitting a tag, selecting a region, or editing text.

That future action problem is not part of this semantic-state claim. Success here means semantic identity is represented or becomes useful for learning; it does not mean the fly has learned an action policy over text.

## Kill rules

- F3 is never relabelled positive based on this follow-up.
- A high `wholebrain_full` score alone is insufficient for a semantic-state claim.
- If fixed matched-budget whole-brain projections do not beat the descending readout, the wrong-door hypothesis is negative under this design.
- If MaleCNS assistance does not beat tag-only, no topology-specific teaching claim is made even if MaleCNS beats a null.
- If MaleCNS does not beat both recurrent controls under matched budgets, assistance is reported as generic recurrence/auxiliary training rather than a biological-wiring advantage.
- No new readout width, recurrence depth, gain, encoder family, tag set, flavourizer capacity or learned compressor is introduced after results and counted as this experiment succeeding.

## Interpretation boundary

The intended decomposition is:

```text
input information
  -> sensory interface loss
  -> recurrent computation / preservation
  -> location of information in the whole brain
  -> readout compression
  -> semantic decoder
```

The experiment is designed to identify which term is responsible for an observed loss rather than charging all losses to the recurrent topology.
