---
type: "Protocol"
title: "Preregistered forecast — MaleCNS semantic tagging (Claude, 2026-09-14)"
description: "Independent numerical forecast for four events in the MaleCNS semantic tagging experiment, registered before the matched-drive results exist and before reading the parallel forecast."
tags: [malecns, forecast, preregistration, brier, connectome, reservoir-computing]
timestamp: 2026-09-14T19:05:00+00:00
---

# Preregistered forecast — MaleCNS semantic tagging

**Author:** Claude Opus 5. **Registered:** 2026-09-14, before the matched-drive
rerun produced any number and before reading the parallel forecast in
`preregistered-forecast-chatgpt-2026-09-14.md`.

## State of information at registration

Everything below is already measured; nothing here is a prediction.

* **Corpus.** 17 hand-annotated TJRO documents, 355 chunks at 64 tokens, 9 tag
  categories, 24.8% of chunks carry at least one tag, 22 chunks carry two.
* **Encoder.** paraphrase-multilingual-MiniLM-L12-v2, 384 dims, 512-token
  context, scales 64/256/512. Qwen3-Embedding-0.6B is downloaded but unrun.
* **Sensation gate, single tag** (`resultado`, 5.1% positive), ridge probe,
  leave-one-document-out, penalty swept: absolute 0.477 AUPRC (9.4x random),
  relations 0.399 (7.9x), position alone 0.071 (1.4x).
* **Multi-tag direct probes** (24.8% positive): relations 0.687, absolute 0.600,
  absolute+relations 0.667 with semantic flavours; 0.512/0.512/0.561 with a
  random codebook. tagAcc 0.538–0.617 against a chance of 0.111.
* **Reservoir conditions so far are drive-confounded** and excluded from my
  reasoning as evidence about topology: with `w ~ N(0, s^2/d)` the 1540-dim
  relations block received half the current the 384-dim absolute block did. In
  that confounded run MaleCNS scored 0.297–0.481 and the degree-preserving null
  0.515–0.596. Drive is now calibrated to 0.050000 RMS for every representation.
* **Operator characterisation.** rho = 3776.27 (ARPACK), spectral concentration
  24.8, leading pair exactly degenerate after row normalisation and
  hemisphere-local (v1+v2 carries 94.4% of its energy on one soma side).
  Row-normalised typical gain 0.297 at gain 0.95. The echo state property breaks
  between gain 0.95 and 1.50; the *bulk* loses it while the leading subspace
  contracts. Leading-subspace saturation switches on between gain 2.5 and 3.2.
* **Reward gate is negative on MiniLM**: no tag-conditioned signal localises the
  span, and the redundancy family scores below random with negative correlation.
  This no longer matters for the design, since the annotation is the teacher.

## The four forecasts

### 1. The tag-free representation works for tagging — **88%**

**Why.** This is close to already-observed rather than predicted. A ridge probe
on tag-free features finds spans on *held-out documents* at 9.4x random in the
single-tag setting and 2.4–2.8x in the multi-tag one, with tag identity at
0.54–0.62 against 0.111 chance, and the positional control at 1.4x rules out the
obvious trivial explanation. The 12% I withhold is not doubt that the effect
exists; it is doubt that it survives the stricter reading of "useful" once the
per-tag decomposition lands.

**Resolves yes if:** on held-out documents, macro per-tag AUPRC is at least 2x
each tag's own prevalence, and tag accuracy on true spans is at least 3x chance,
on at least one of the three representations and replicated on Qwen.

**Failure modes in the number.** Macro per-tag AP resting on two or three
well-covered tags while the rest sit at prevalence — the tags run from 8 to 18
positive chunks and a single document swinging moves a column a lot. Seventeen
documents is a small enough corpus that leave-one-document-out has visible
variance. A Qwen replica that disagrees would also count against it, though I
expect a stronger encoder to help rather than hurt.

### 2. Frozen MaleCNS adds information over the direct control — **20%**

**Why.** The mechanism runs the wrong way. The direct probe reads the full
384- or 1540-dimensional representation; the fly's readout reads 1,314 descending
neurons after a *random* projection into 8,982 sensory neurons and recurrence
measured at typical gain 0.297. A reservoir earns its place when the input is
low-dimensional and the task needs temporal integration, and neither holds here:
pretrained sentence embeddings are already near-linearly-separable, and tag
localisation is largely a per-chunk judgement. The honest hope is kernel
expansion — a nonlinearity making something linearly separable that was not —
and 1,314 > 384 leaves room for that on `absolute`, but 1,314 < 1,540 makes it
compression for `relations`.

**Resolves yes if:** with matched drive and identical input, MaleCNS beats its
own direct probe on the same representation, on macro per-tag AUPRC, with the
paired per-seed difference positive in at least 8 of 10 seeds.

**Failure modes in the number.** The bottleneck dominating everything. The
operating point being wrong rather than the operator: gain 0.95 sits at typical
gain 0.297, so the topology is barely in the loop, and a gain sweep might rescue
it — I am *not* counting a rescue by re-tuning as a yes unless the tuning is
selected on validation. Four steps per chunk may be too few for recurrence to do
anything. Against all that, the 20% is mostly the chance that kernel expansion on
`absolute` is real.

### 3. A specific MaleCNS topology advantage — **6%**

**Why.** This requires event 2 *and* that the advantage is specific to this
wiring rather than to having recurrence at all. Conditional on 2 happening, I
give topology specificity about 30%. Nothing I measured about the operator
suggests special computational structure: it is spectrally concentrated 24.8x,
its two slowest modes are a hemisphere-local integrator rather than anything
task-shaped, its bulk loses the echo state property before the bulk reaches a
useful operating point, and reaching bulk-matched requires clamping 86% of the
leading subspace. A degree-preserving rewiring keeps the degree sequence and the
sign structure, which is most of what makes a sparse operator behave as it does.

**Resolves yes if:** MaleCNS beats the direct control, the degree-preserving null
and the matched random ESN, all three on held-out macro per-tag AUPRC, at >= 10
seeds, paired, with a mean margin of at least 0.03 over the best control and the
same sign in at least 8 of 10 seeds.

**Failure modes in the number.** The most likely near-miss is beating the random
ESN but not the degree-preserving null, which would show that degree structure
rather than wiring specificity is doing the work — I would report that as a no.
The second is a positive that does not replicate across encoders. I am also
pricing in that no published controlled positive exists in the community despite
several groups running this brain, which is weak evidence but not no evidence.

### 4. Run 2 conditioned learning produces a strong result — **12%**

**Why.** The paradigm itself is sound and the inference-time story is clean: the
fly sees only tag-free text, with no tag, mask or food. A learned input
projection should help considerably more than the random one in event 2, because
gradient can find directions this particular operator handles well — that is the
FLM design and the reason to expect more than 20% here on the narrow question of
"does it tag at inference". What holds the number down is the phrase *surviving
the controls*: the direct-input control is parameter-matched and reads the same
rich embeddings with no bottleneck, and beating it is the same hard problem as
event 2 with a better projection.

**Resolves yes if:** after reward-conditioned training, at inference with only
tag-free text, the adapter+MaleCNS beats the parameter-matched direct-input
control *and* both topology nulls on held-out macro per-tag AUPRC, paired over
>= 10 seeds, margin >= 0.03, same sign in >= 8 of 10.

**Failure modes in the number.** The adapter doing the task by itself — with
~300k parameters over a 384-dim pretrained embedding, the direct control is
strong, and a tie there is the single most likely outcome. Truncated BPTT over
256-byte windows limiting what the recurrence can contribute. Training
instability on 17 documents; this run needs the ~1,000-document corpus to mean
much, and if it is run at 17 the variance will swamp a 0.03 effect.

## Which layer is most likely to work

Ranked, most to least likely:

1. **Semantic interface.** Already working. The multiscale relation is the part
   still in question, and the multi-tag reversal — relations 0.687 above absolute
   0.600, where single-tag had absolute ahead — is the most interesting live
   result in the project.
2. **Conditioned learning as a paradigm.** "Reward during training, nothing at
   inference" is likely to produce a working tagger. Whether the *fly* is why it
   works is a separate question and is what the controls decide.
3. **Generic recurrence.** Some chance a reservoir helps a linear readout by
   kernel expansion, mostly on the lower-dimensional `absolute` input.
4. **MaleCNS topology specifically.** Least likely. Everything measured about
   this operator says it is a spectrally concentrated, hemisphere-dominated,
   weakly-recurrent object whose degree structure is most of its behaviour.

The uncomfortable implication, stated now rather than after the fact: the most
likely outcome of this project is a clean negative on the connectome and a
genuinely useful finding about hierarchical semantic representation. That is a
good paper and it is not the paper we set out to write.

## Scoring

Brier score per event, `(p - outcome)^2`, outcome 1 for yes and 0 for no; lower
is better. Mean over the four events is the headline. Registered probabilities:

| # | Event | p |
|---|---|---|
| 1 | Tag-free representation works for tagging | 0.88 |
| 2 | Frozen MaleCNS adds over the direct control | 0.20 |
| 3 | Specific MaleCNS topology advantage | 0.06 |
| 4 | Run 2 conditioned learning survives the controls | 0.12 |

A forecast of 0.5 everywhere scores 0.25. Anything above that is worse than
having said nothing.
