# Closed-loop embedding translation through a frozen MaleCNS

This front generalises the pattern the last week of MaleCNS work kept
rediscovering. Tagging, semantic flavour, Few-NERD, the visual attractor,
FlyDoom, FlyMirror, FlyTTS and the state-conditioned coupling stack all share one
shape:

```
input -> trainable adapter -> frozen MaleCNS -> trainable adapter -> output
                 ^                                                     |
                 +------------- trainable feedback adapter <-----------+
```

What differs between them is only the environment and the objective. So the
question worth asking is whether the middle is a reusable component:

> Is there a `MaleCNSClosedLoop` module that different tasks configure by
> supplying `InputAdapter`, `OutputAdapter`, `FeedbackAdapter` and an objective,
> with the same frozen connectome at the centre?

Embedding translation is the cleanest possible instance to test that on. The
target is a point in a metric space, so the "consequence" the loop consumes is a
real error vector rather than a label, and "did round `t+1` land closer than round
`t`" is a question with a number for an answer.

## What this is not

It is not a claim that a fly brain does language. It is not a claim that the
connectome computes embeddings. The claim under test is narrower and empirical: a
large fixed recurrent dynamical substrate, wrapped in small trainable interfaces,
either supplies useful dynamics to an external task or it does not, and the
controls decide which.

MaleCNS `connectome-weights` are measured synaptic connection strengths from the
v1.0 release. They are not trained neural-network weights. Leak, gain, `tanh` and
drive normalisation are modelling choices, declared in
`src/malecns_wifi/closed_loop_translation.py` and in the preregistration.

The input port reuses the annotation-selected sensory population the tagging runs
already use. The feedback port is a **synthetic interface**: uniformly sampled
non-sensory neurons, disjoint from the input port. The fly has no "your embedding
was wrong" afferent, and this file does not pretend otherwise.

## Layout

| file | role |
| --- | --- |
| `src/malecns_wifi/closed_loop_translation.py` | substrate, frozen sparse recurrence, adapters, the loop |
| `src/malecns_wifi/translation_pairs.py` | frozen two-encoder embedding cache with provenance, group-disjoint splits |
| `src/malecns_wifi/translation_metrics.py` | trajectory scoring, retrieval, centroid baseline |
| `scripts/build_translation_embedding_cache.py` | encode a corpus once with MiniLM and E5 |
| `scripts/run_closed_loop_translation.py` | all arms, audits and references in one run |
| `preregistered-closed-loop-embedding-translation-2026-09-16.md` | protocol, amendment, kill criteria |

Reused from the existing stack rather than rebuilt: `compiler.compile_connectome`,
`runtime.load_graph`, `tagger.row_normalise`, `tagger.select_populations`'s
annotation convention, and `characterize.degree_preserving_null` /
`characterize.random_esn` for the topology nulls.

## Three design decisions that carry the experiment

### 1. The gradient never touches the operator

`FrozenSpMM` is a custom autograd function: forward is `W @ x`, backward is
`W.T @ grad` against a precomputed transpose. The operator has no gradient path at
all, so no optimiser can reach it even by accident, and backward costs one sparse
product instead of a dense 165k x 165k Jacobian. On this CPU that is the
difference between 27 ms and 840 ms per step, which is the difference between
running the whole brain and giving up and shrinking it to 512 neurons.

A test checks the hand-written backward against dense autograd. A per-run audit
records the gradient norm of every parameter and the `requires_grad` flag of every
frozen tensor, into the result JSON.

### 2. Every operator runs at the same bulk operating point

MaleCNS, the degree-preserving null and the random ESN have different bulk gains.
At a fixed scalar gain they would sit in different dynamical regimes, and an arm
difference would be reporting dynamic range rather than topology. So each
substrate's gain is rescaled to a common bulk operating point measured with random
probes: `gain = bulk_target / bulk_gain(W)`.

The measured bulk gain of the row-normalised MaleCNS operator is **0.295**, so at
`bulk_target = 0.9` its effective gain is about **3.05**. At the previously used
`gain = 0.95` the recurrent contribution was around 30% of the input drive — the
topology was barely in the loop.

### 3. The feedback channel is graded, and the grade is reported

A closed-loop arm that sees `b_target` is doing supervised recurrent correction,
not inference. A wide feedback adapter could route the target around the substrate
entirely and post a good score while the connectome does nothing. So:

- `scalar` — cosine, error norm, round index. Three numbers, 768-dimensional
  target. This is the headline arm, and a test asserts the channel is invariant to
  rotating both prediction and target, i.e. that it carries magnitude and not
  identity.
- `full` / `residual` — oracle channels, run as upper bounds, never reported as
  inference.

Drive RMS is matched after every adapter, so an adapter can change the direction
and geometry of the current it injects but never its magnitude.

## The calibration that nearly invalidated the whole comparison

Worth recording because it is the kind of thing that silently ruins a result.

E5-base-v2 space is strongly anisotropic. On this corpus the mean cosine between
two *unrelated* E5 vectors is **0.674** (MiniLM: 0.049). Consequently:

| predictor | mean cosine | retrieval@1 |
| --- | --- | --- |
| target centroid, constant | **0.827** | 0.007 (chance) |
| closed-form least-squares linear map | 0.881 | **0.959** |

The constant centroid outscores real work on cosine. The first calibration run
trained on a cosine loss and did exactly what the geometry invites: cosine 0.80
with retrieval at chance. Every arm had learned to emit the centroid.

So the objective is InfoNCE with in-batch negatives, the primary metric is
retrieval@1, and mean cosine is only ever reported as a delta against the centroid
baseline. Both references are recomputed on every run and printed with the
results.

One more: splits are **group-disjoint**. STS-B contributes both sentences of each
pair and they are near-paraphrases, so an item-level shuffle would train on a
near-duplicate of half the test set. The corpus builder iterates row-major
precisely so that a truncated corpus still contains both members of each pair —
column-major iteration would have taken only `sentence1` and quietly turned the
grouping into a no-op.

## Running it

```bash
python scripts/compile_connectome.py --output artifacts/runtime-v1

python scripts/build_translation_embedding_cache.py \
    --limit 2000 --output artifacts/translation/minilm-e5.npz

python scripts/run_closed_loop_translation.py \
    --graph artifacts/runtime-v1/graph.npz \
    --cache artifacts/translation/minilm-e5.npz \
    --output artifacts/closed-loop-translation-seed0.json
```

The whole thing runs on CPU against the real 165,122-neuron, 10,228,000-edge
operator. No part of this front needs a GPU to reproduce.

## Next, if the loop turns out to do anything

- the `T = 1, 2, 4, 8, 16` recurrent-depth ladder;
- the partial-rewiring curve `p` from the Algorithmic Connectome front, which asks
  how much biological topology is actually needed;
- multi-seed replication, then reverse and third-space pairs;
- phase 2: a learned critic that predicts the feedback with no access to
  `b_target`, which is the only route from supervised correction to autonomous
  inference.
