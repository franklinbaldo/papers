---
type: "Protocol"
title: "Closed-loop embedding translation through a frozen MaleCNS — preregistration"
description: "Preregistered exploratory test of whether a frozen MaleCNS operator, wrapped in small trainable interfaces and run as a persistent state in a closed loop, can translate MiniLM embeddings into E5 space, against open-loop, degree-preserving-null, random-ESN, direct and centroid controls."
tags: [malecns, drosophila, connectome, closed-loop, embedding-translation, reservoir-computing, preregistration]
timestamp: 2026-09-16T20:00:00+00:00
---

# Preregistered exploratory test — closed-loop embedding translation through a frozen MaleCNS

Date: 2026-09-16

## The question

Every MaleCNS front so far has used the connectome as a feature extractor with a
consequence bolted on. This one asks the loop question directly, on a task with a
dense, continuous, unambiguous target:

> Can a frozen MaleCNS operator, wrapped in small trainable interfaces and run as
> a persistent state in a closed loop, translate between two independent
> representation spaces — and does the loop supply improvement that the same
> substrate open-loop, a degree-preserving null, and a random ESN do not?

Translation is the right task for this because the target is a point in a metric
space. Error is a vector, error magnitude is a scalar, and "did round `t+1` land
closer than round `t`" is a question with a number for an answer. Tagging and NER
give a loop a label; this gives it a gradient of consequence.

## Architecture

```
embedding A (MiniLM, 384-d, frozen)
      -> adapter_in            trainable, rank 16
      -> fixed random port projection onto annotated sensory neurons
      -> frozen MaleCNS operator, persistent state h_t
      -> fixed sparse readout, width 512
      -> adapter_out           trainable LoRA residual on a frozen random base
      -> embedding B_hat_t     (E5-base-v2 space, 768-d)
      -> error / consequence
      -> adapter_feedback      trainable, rank 16
      -> fixed random port projection onto a disjoint neuron population
      -> same persistent h_t
```

`h` is reset once per example and never between the rounds of one example. The
recurrent depth of a run is `rounds x inner_steps`.

## What is frozen

The operator, both port projections, the readout projection, the LoRA base, and
both sentence encoders. The operator is a buffer, never a parameter; gradient
passes through it via a precomputed transpose, so no optimiser can reach it even
by accident. Only `adapter_in`, the `adapter_out` residual, and `adapter_feedback`
train.

MaleCNS `connectome-weights` are measured synaptic connection strengths from the
v1.0 release. They are not trained network weights. Leak, gain, `tanh` and drive
RMS normalisation are modelling choices declared here.

## The feedback channel is the experiment

Any closed-loop arm that can see `b_target` is doing **supervised recurrent
correction**, not autonomous inference. A wide enough feedback adapter could route
the target around the substrate and score well while the connectome does nothing.
So the channel is graded, and the grade is reported with every number:

| mode | features | can it carry the target? |
| --- | --- | --- |
| `none` | — | open loop |
| `scalar` | cosine, error norm, round index | no, 3 numbers for a 768-d target |
| `residual` | error vector + scalars | yes, `b_target = b_hat + e` |
| `full` | prediction, target, error, scalars | yes, directly |

**`scalar` is the headline arm.** Improvement there is improvement the loop had to
compute. `full` is run as an upper bound and must never be reported as inference.

The drive RMS is matched after each adapter, so no adapter can win by increasing
current — only by changing the direction and geometry of what it injects.

## Arms

Identical embeddings, split, ports, readout, optimiser, learning rate, epochs and
interface budget. The only thing that varies is the operator and the feedback mode.

1. `direct_lowrank` — A -> rank-16 adapter -> B. No substrate.
2. `mlp` — A -> small MLP -> B.
2b. `centroid` and `least_squares_linear` — computed, not trained; the two
   reference points every other number is read against.
3. `malecns_open` — substrate, `feedback_mode = none`.
4. `malecns_closed[scalar]` — headline arm.
5. `malecns_closed[full]` — oracle-channel upper bound.
6. `degree_null_closed` — directed configuration model: in-degree, out-degree,
   weight multiset and presynaptic sign preserved, motifs destroyed.
7. `random_esn_closed` — random operator, matched density and weight multiset.

## Amendment, same day, before any arm was interpreted

Two calibration facts, measured on the *training* embeddings alone, changed the
objective and the primary metric. Both are recorded here rather than quietly
applied downstream.

1. **The target space is anisotropic.** Mean pairwise cosine between two unrelated
   E5-base-v2 vectors in this corpus is **0.674**. (MiniLM, for contrast: 0.049.)
2. **The centroid beats everything on cosine.** Emitting the pool centroid for
   every input scores **mean cosine 0.829** with **retrieval@1 = 0.003**, i.e.
   chance. A least-squares linear map scores a *lower* cosine, 0.738, at
   **retrieval@1 = 0.42**.

Mean cosine is therefore anti-correlated with translation quality in this target
space, and a plain cosine objective trains straight into the collapse. The first
calibration run did exactly that: cosine 0.80 with retrieval at chance.

Consequently:

- the training objective is **InfoNCE with in-batch negatives** (temperature
  0.05), not cosine. `objective="cosine"` is retained for ablation only;
- the **primary metric is retrieval@1**, with CSLS retrieval alongside it;
- mean cosine is reported only as a **delta against the centroid baseline**, and
  never on its own;
- two reference points are computed on every run and printed with the results:
  the **centroid baseline** and a **closed-form least-squares linear map** fitted
  on the training split. An arm that cannot beat the linear map has not
  demonstrated that the substrate contributes anything.

A third calibration decision, made on the operators alone with random inputs and
no task data: each substrate's gain is rescaled so all operators run at the same
**bulk operating point** (0.9), because MaleCNS, the degree-preserving null and
the random ESN have different bulk gains. At a fixed scalar gain an arm difference
would report dynamic range rather than topology. Measured bulk gain of the
row-normalised MaleCNS operator is 0.295, so its effective gain is about 3.05.

## Primary outcomes

The trajectory, not the endpoint:

- `quality(t)`: mean cosine and retrieval@1 at every round;
- `error_contraction_t = ||e_{t+1}|| / ||e_t||`, per transition, mean and median,
  plus the fraction of items that improved.

measured on retrieval@1 as well as on cosine.

Secondary: MSE, retrieval@{1,5,10} with chance printed beside it, MRR, CSLS
retrieval, kNN preservation@10, Spearman correlation of pairwise distances.

## Engineering smoke (must pass before any arm is interpreted)

Asserted in-run, in the result JSON, not in prose:

- gradient reaches all three adapters with finite norms;
- no frozen tensor has `requires_grad`;
- the hand-written sparse backward matches dense autograd;
- state RMS changes between rounds (the state is not being reset);
- round 0 is identical with and without feedback, later rounds are not
  (the feedback genuinely perturbs the trajectory);
- loss decreases, no NaN or blow-up;
- the embedding cache fingerprint verifies against the stored texts.

## Kill criteria

The MaleCNS-specific hypothesis is weakened, and the result recorded as negative,
if under comparable conditions any of the following holds:

- `malecns_closed[scalar]` ≈ `malecns_open` (no loop effect: the loop is idle);
- `degree_null_closed` >= `malecns_closed`;
- `random_esn_closed` >= `malecns_closed`;
- `mlp` or `direct_lowrank` >= any substrate arm;
- no substrate arm beats the closed-form `least_squares_linear` reference;
- `error_contraction` >= 1 across the trajectory in the scalar arm.

A negative here is still a finding. If a closed loop helps but the nulls match it,
the result is about *generic recurrent closed-loop translation*, not about
biological topology — and that is worth reporting as such.

## Scope of this run

Single seed, CPU, ~2000 sentences from the STS-B pool, MiniLM -> E5-base-v2,
rank 16, T = 4, inner_steps = 2. This is an engineering smoke plus a first
controlled comparison. It is not a confirmatory result, no number here licenses a
claim about the connectome, and nothing is tuned on the test split.

## Follow-ups this run does not attempt

- the `T = 1, 2, 4, 8, 16` ladder;
- the partial-rewiring curve `p in {0, 0.1, 0.25, 0.5, 0.75, 1.0}` from the
  Algorithmic Connectome front, which asks how much biological topology is needed
  if the loop does work;
- multi-seed replication;
- reverse and third-space pairs (E5 -> MiniLM, MiniLM -> Qwen, E5 -> Qwen);
- phase 2: a learned critic predicting the feedback with no access to `b_target`,
  which is the only path from supervised correction to autonomous inference.
