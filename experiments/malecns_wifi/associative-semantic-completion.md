---
type: "Protocol"
title: "Associative Completion of Sparse Semantic Pyramids"
description: "Pre-registered variation testing whether cheap local or seen-prefix embeddings can retrieve missing expensive coarse semantic channels from leakage-safe memory, preserving tagging quality while reducing embedding cost."
tags: [semantic-pyramid, retrieval, associative-memory, embeddings, cache, tagging, preregistration]
timestamp: 2026-09-14T21:15:00-04:00
status: "pre-registered variation; no confirmatory results yet"
---

# Associative Completion of Sparse Semantic Pyramids

> **Separate stacked variation on the semantic-flavour pyramid.** This experiment does not reinterpret the dense-pyramid result, the fly-assisted result, or Run 1 / Run 2. It asks a systems-and-representation question that exists even if MaleCNS is never used.

## Question

Can a semantic pyramid be **sparse in computation but approximately dense in representation**?

At position `t`, the system may have only cheap, fine channels computed from the text already observed. Some larger or more expensive channels are missing. Instead of paying immediately to embed the larger context, query an associative memory with the cheap representation, retrieve previously observed large-channel values attached to semantically similar keys, and use the retrieved value as a provisional completion.

The proposed path is:

```text
text observed up to t
    -> cheap local / seen-prefix embedding q_t
    -> cosine search in prior semantic memory
    -> retrieved estimate of missing coarse channel(s)
    -> flavourizer / tagger / optional MaleCNS
```

When retrieval confidence is low, compute the real expensive channel and optionally add it to memory. A successful system therefore becomes cheaper as its memory becomes more useful.

## Cache is not memory

Two mechanisms must remain separate in code and reporting.

**Exact cache** reuses an embedding only when `(encoder, revision, normalization, exact text)` is identical. It is lossless and content-addressed.

**Associative memory** answers a different question: *given a cheap representation similar to something seen before, what expensive channel was associated with that kind of state?* It is approximate and can be wrong.

A cache hit never counts as associative retrieval, and a retrieval hit never counts as exact reuse.

## Memory record

A memory item is a key-value association plus provenance:

```text
key      = cheap representation available at query time
value    = an observed expensive channel from the same historical example
metadata = document id, position, scale, sensor type, encoder/revision, time/order
```

The key and value **do not need to share a coordinate system or dimensionality**. For example:

```text
key   = tiny-encoder embedding of 16 observed tokens      in R^64
value = Jina absolute channel for its 256-token context   in R^1024
```

This is legitimate because no cross-encoder subtraction is performed. The memory stores an empirical association `key -> value`. Any later relational arithmetic remains restricted to vectors in a coherent encoder space.

The memory may also store a derived value such as `R(16|256)` directly. That is a separate target type and is reported separately from reconstructing the parent absolute embedding.

## Query: only what has been seen

The confirmatory online query at position `t` may use only information available from the current document at or before `t`.

Allowed key schemas include:

- `local`: a cheap embedding of the current fine tile;
- `seen_prefix`: a cheap representation of text observed up to `t`;
- `local_plus_prefix`: a fixed combination of the two.

The first registered implementation may choose one schema before results. It may not inspect future text in the current document.

The phrase "retrieve the larger context" therefore means **retrieve a historically associated coarse semantic state**, not peek at the unseen future context of the current document.

## Retrieval

For a normalized query `q` and normalized memory keys `k_i`:

```text
s_i = cosine(q, k_i)
N_k(q) = top-k memories by s_i
```

Three completion rules are frozen as the initial comparison:

1. **top1** — use the value attached to the nearest key;
2. **topk_barycenter** — weighted average of the top-k values with weights `softmax(s_i / tau)`;
3. **confidence_gated** — use retrieval only above a confidence threshold selected inside training folds; otherwise pay for the real channel.

No learned attention over memory is allowed in this experiment. A learned retriever is a later hypothesis because it can become the task model itself.

## Missing-channel completion

Suppose the live sparse field contains real channels at fine scales but omits expensive coarse channels:

```text
16    real
32    real
64    retrieved
128   retrieved
256   retrieved or real fallback
512   absent
```

The completed field carries provenance for every channel:

```text
source = real | exact_cache | retrieved
confidence = 1.0 for real/cache, retrieval confidence otherwise
```

The tagger/flavourizer may receive `confidence` and `is_retrieved` as explicit scalar metadata, but those metadata are fixed facts, not learned labels.

## Leakage rules

Retrieval is a powerful leakage mechanism, so the memory boundary is part of the experiment rather than an implementation detail.

### Confirmatory LODO rule

For held-out document `D`, the associative memory is built **only from the other documents**. No key or value derived from `D` may exist in the memory used to score `D`.

```text
M_D = memory(training documents only)
```

This applies even to unlabeled channels. The held-out document is not allowed to teach the memory what its own future or coarse context looks like.

### Online causality rule

The query for position `t` uses only current/past text. Future text from the held-out document is forbidden.

A separate exploratory `same_document_prefix_memory` arm may later reuse values genuinely computed earlier in the same document, but only if their source position is `< t` and the value itself did not encode future text relative to its creation point. That arm is never mixed into the confirmatory LODO result.

## Baselines

Every retrieval result is compared against:

1. **full_pyramid_real** — all registered channels computed normally; expensive quality ceiling;
2. **sparse_only** — only the channels we actually paid to compute;
3. **centroid_imputation** — replace each missing channel by the training-memory mean at that scale/type;
4. **shuffled_memory** — cosine search uses the real keys but values are permuted among memory records;
5. **parametric_imputation** — a small ridge map from cheap key to expensive value, trained only on training documents;
6. **top1 retrieval**;
7. **top-k barycenter retrieval**;
8. **confidence-gated retrieval + real fallback**.

The centroid and shuffled controls test whether "having something in the slot" is enough. The ridge control tests whether nearest-neighbour memory is adding anything over a simple learned cross-scale map.

## Primary outcomes

Scientific quality:

- held-out macro per-tag AUPRC;
- boundary AUPRC;
- any-tag AUPRC;
- per-document paired deltas against `sparse_only` and `full_pyramid_real`;
- per-scale/channel completion error against the real missing value, reported as cosine and normalized L2 diagnostics.

Systems value:

- number of expensive encoder calls actually executed;
- expensive tokens/bytes actually encoded;
- retrieval calls and search time;
- exact-cache hits, associative retrieval hits, and real fallbacks separately;
- fraction of missing channels filled without an encoder call;
- end-to-end wall-clock and cache/memory bytes.

The systems ledger is part of the result. "Short embeddings are cheap" and "retrieval saves work" are not accepted as assumptions.

## Registered gates

### A1 — associative completion adds information

The primary `confidence_gated` arm must beat `sparse_only` by at least **0.02 absolute macro per-tag AUPRC** or **0.03 boundary AUPRC**, with positive paired document delta in at least 12/17 documents.

### A2 — the gain is semantic retrieval, not slot filling

`confidence_gated` must beat both `centroid_imputation` and `shuffled_memory` on held-out macro per-tag AUPRC.

### A3 — it is economically meaningful

Relative to `full_pyramid_real`, the primary arm must avoid at least **50% of expensive-channel encoder calls** while retaining at least **90% of full-pyramid macroAP** and remaining within **0.03 absolute macroAP** of the full pyramid.

Both quality conditions are reported; passing one but not the other is not rounded into success.

### A4 — confidence means something

Completion error must be lower in higher-confidence retrieval bins. A confidence gate whose confidence is uncalibrated cannot justify skipping expensive embeddings; if the monotonic trend fails, the adaptive fallback claim fails even if average retrieval is useful.

## Per-scale curve

The result is reported separately for every target scale and sensor type. We expect some channels to be much more retrievable than others.

A plausible outcome is:

```text
64    cheap enough to compute; retrieval unnecessary
128   highly retrievable
256   useful retrieval with occasional fallback
512   weak retrieval
1024  mostly fallback
```

The experiment does **not** require that every missing embedding be reconstructible. The architectural claim is precisely that a confidence gate can exploit the easy cases and pay for the hard ones.

## Failure modes that count as results

- **semantic collision:** locally similar keys belong to incompatible coarse contexts;
- **novel state:** no close neighbour exists, so fallback dominates;
- **hub memory:** a few generic keys retrieve for everything;
- **averaging blur:** top-k barycenters wash out information that top1 preserves;
- **encoder floor:** a tiny key encoder cannot distinguish states needed to predict the coarse channel;
- **retrieval helps reconstruction but not tagging:** the recovered geometry is accurate in cosine space yet task-irrelevant.

These are not post-hoc excuses. They are measured failure modes.

## No rescue by bigger memory or stronger retriever

The confirmatory run freezes the training-memory corpus, key schema, target channel set, `k` candidates, threshold-selection rule and retrieval method before held-out scoring.

If the registered memory fails, adding external corpora, a learned retriever, larger keys, future-aware queries or a different encoder family is a new experiment. The associative-completion claim is not rescued after the result by making the memory arbitrarily powerful.

## Relationship to the semantic retina

The dense semantic pyramid asks whether different scales/sensor types form a useful field. This variation asks whether all of those senses need to be physically measured at every timestep.

If successful, the architecture becomes:

```text
cheap real sensation
    + exact cached sensation
    + associative remembered sensation
    + expensive real fallback when memory is uncertain
        -> flavourizers
        -> tagger / optional recurrent substrate
```

The intended interpretation is not that retrieved channels are "true". They are **remembered hypotheses about missing senses**, explicitly marked by confidence and replaced by observation when the memory is uncertain.
