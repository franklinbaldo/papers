# Alternative experiment: fly-assisted standalone semantic tagger

Status: **parallel exploratory protocol**. This does not replace, reinterpret, or
retroactively alter Run 1 / Run 2 in PR #441.

## Question

Can a biological recurrent substrate be useful as a **training scaffold** for
semantic span tagging even when the final tagger does not contain the substrate?

The product objective is the tagger. MaleCNS is allowed to become irrelevant or
be removed entirely after it has helped discover a useful transformation of the
semantic stream.

## Final deployed model

Held-out inference is always:

```text
untagged text
    -> semantic relation channels
    -> low-rank residual flavourizer
    -> tag head
    -> spans / tag identity
```

There is **no MaleCNS, food, tag mask, gold span, or taste head at inference**.

## Training-time scaffold

The assisted arm temporarily adds:

```text
semantic relation channels
    -> flavourizer
    -> frozen MaleCNS
    -> disposable taste head
    -> food target from gold spans/tags
```

Training loss:

```text
L = L_tag + lambda(epoch) * L_fly + beta * L_residual
```

`lambda` is annealed to exactly zero before training ends. The final phase therefore
uses exactly the deployed architecture. The recurrent operator remains frozen in
this experiment; learning happens in the semantic transformation and tag head.

The core comparison is not "does the fly still exist at inference?" It is:

> Two final taggers have the same architecture and see the same held-out input.
> Did temporary training through MaleCNS produce the better standalone tagger?

## Hierarchical relation channels

There is no single privileged text-to-fly interface. The semantic input is a set of
channels, each expressing a smaller span **relative to a containing larger span**.

A possible hierarchy is:

```text
1024
├─ 512           R(512 | 1024)
│  ├─ 256        R(256 | 512), R(256 | 1024)
│  │  ├─ 128     R(128 | 256), R(128 | 512), ...
│  │  │  ├─ 64   R(64 | 128), R(64 | 256), ...
│  │  │  │  └─ token / byte-window relations
```

The first controlled version need not instantiate every edge. It can start with a
small preregistered bundle and expand only in a later mechanism study.

### Mixed encoders are allowed

Embedding models do not share coordinates, so a MiniLM child vector must never be
divided/subtracted directly from a Qwen parent vector. Instead **each relation
channel is internally single-encoder**:

```text
Qwen:    R(256 | 1024)
MiniLM:  R(64  | 256)
Tiny/BPE/byte encoder: R(local-byte-window | 64)
```

The same scale may be encoded more than once by different models when it participates
in different channels. This is useful, not redundant: models expose different
semantic/detail biases, while each geometric relation remains well-defined.

A fine span can also have several ancestor relations simultaneously, such as
`R(256|512)` and `R(256|1024)`. These are separate channels rather than averaged
away.

### Channel mixing and energy control

Each channel is normalised independently and projected independently into the sensory
interface. Their currents are mixed simultaneously, then the **combined realised
RMS is calibrated to the same target** used by controls. Adding channels therefore
cannot win by injecting more current.

Initial controlled mixer: fixed equal channel weights. A learned channel mixer is a
separate later hypothesis because a powerful mixer could itself solve the tagging
problem.

## Flavourizer

The first model is intentionally weak:

```text
E' = E + U tanh(V E)
```

with low rank `r`. It begins at identity (`U = 0`). The fly-assisted loss may teach
this map to "season" the semantic trajectory so that tag-relevant regions acquire a
geometry the recurrent substrate reacts to. The tag loss simultaneously teaches the
same transformed representation to support the actual spans.

It is acceptable — desired, even — for the final flavourizer/tag head to internalise
the useful transformation so completely that MaleCNS can be deleted.

## Arms

Minimum paired arms, identical final architecture and seeds:

1. `tag_only`: flavourizer + tag head, no auxiliary substrate.
2. `malecns_assisted`: same model, temporary MaleCNS taste loss.
3. `degree_null_assisted`: same assistance schedule through degree-preserving null.
4. `random_esn_assisted`: same assistance schedule through matched random ESN.

Optional teacher controls:

5. `random_fixed_teacher`: matched random fixed map into taste space.
6. `direct_taste_aux`: same food auxiliary predicted directly from the transformed
   semantics, with no recurrent substrate.

These distinguish "extra supervised loss helps" from "this recurrent substrate
provides a useful training geometry".

## Primary outcome

Evaluate **after assistance is zero**, using only the standalone tagger:

- macro per-tag AUPRC (primary);
- any-tag AUPRC;
- tag accuracy on true spans;
- learning curve / sample efficiency;
- per-document paired deltas;
- residual size `||Delta|| / ||E||` needed to reach the result.

A MaleCNS training-scaffold advantage requires the final standalone
`malecns_assisted` tagger to beat `tag_only`, `degree_null_assisted`, and
`random_esn_assisted` under matched data, seeds, parameter count, drive energy,
selection protocol, and final architecture.

If `malecns_assisted` trains faster but converges to the same held-out score, report a
sample-efficiency effect rather than a final-quality effect.

## Claim boundary

A positive result says:

> temporary optimization through this substrate helped learn a better standalone
> tagger.

It does **not** say:

- the fly is required at deployment;
- a living fly understands language;
- MaleCNS is generally better for text;
- the anatomical ports are privileged unless they beat matched random ports;
- Run 1 or Run 2 succeeded retroactively.

This is a distinct cell in the interface-regime matrix.

## Instrumentation in this branch

- `malecns_wifi.fly_assisted`: low-rank flavourizer, annealed auxiliary loss,
  differentiable frozen recurrence, fixed drive RMS, standalone scoring.
- `malecns_wifi.semantic_channels`: heterogeneous hierarchical relation channels,
  mixed-encoder-safe construction, multiple ancestors, fixed-total-energy mixing.
- toy tests verify that the fly branch can backpropagate into the flavourizer, is
  skipped when assistance reaches zero, cannot win by increasing drive amplitude,
  and is absent from final inference.

## First implementation milestone

Before an expensive GPU run:

1. build a small channel bundle from existing cached MiniLM/Qwen features;
2. make `tag_only` overfit a toy subset (positive control);
3. make assisted training propagate a non-zero gradient through a toy frozen graph;
4. verify assistance reaches exactly zero and removing the fly/taste branch changes
   no inference logits;
5. run one seed of all four arms as a smoke test;
6. only then preregister seeds/budget and launch the comparison.

The byte-level end of the hierarchy is intentionally an extension point rather than
silently equating raw bytes with semantic vectors. It can be supplied by a tiny
learned byte/BPE encoder, provided every reported relation is still computed within
one coherent encoder space.
