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
2. **topk_barycenter** — weighted average of the top-k values with weights `softmax(s_i / temperature)`;
3. **confidence_gated** — use retrieval only above a confidence threshold `tau`; otherwise pay for the real channel.

`temperature` and the confidence threshold `tau` are distinct. `temperature` controls how top-k values are blended. `tau` decides whether retrieval is trusted at all.

No learned attention over memory is allowed in this experiment. A learned retriever is a later hypothesis because it can become the task model itself.

## Nested selection of retrieval hyperparameters

`tau` is a selected hyperparameter and is subject to the same leakage discipline as gain or ridge. It is never chosen on the outer held-out document.

For each outer held-out document `D`:

```text
remove D first
    -> build memory only from the remaining documents
    -> split those documents into inner-train / inner-validation
    -> select (k, tau, temperature where applicable) only on inner-validation
    -> rebuild/refit the chosen rule using all outer-training documents
    -> predict D once
```

The primary confidence-gated arm uses a frozen finite candidate grid for `k`, `tau`, and any top-k temperature before outer scoring begins.

Selection is **lexicographic rather than a post-hoc weighted utility**:

1. retain only candidates that, on inner validation, preserve at least 90% of `full_pyramid_real` macroAP and remain within 0.03 absolute macroAP of it;
2. among qualifying candidates, choose the one avoiding the largest fraction of expensive-channel encoder calls;
3. ties are broken by higher inner-validation macroAP, then by the more conservative policy (more real fallbacks);
4. if no candidate meets the quality floor, choose the candidate with highest inner-validation macroAP, breaking ties by lower cost, and record that the economic regime was not reached.

The outer document contributes neither labels nor retrieval-quality outcomes to this choice. Output records `selected_by_fold`, not a single globally selected `tau`.

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

## Formulaicity is a target-domain property, not an apology

Associative completion is expected to work best where a corpus repeatedly revisits similar semantic states inside similar larger structures. That includes precisely the high-volume domains for which expensive repeated embedding work matters: judicial decisions, contracts, medical records, insurance claims, filings and procurement documents.

The registered mechanism prediction is therefore:

> **The more structurally repetitive a corpus is, the greater the fraction of expensive observations that associative completion can safely avoid at a fixed quality floor.**

The experiment reports formulaicity before interpreting savings. It is measured in two complementary ways.

### F_sem — label-free semantic neighbourability

Using only the cheap key representation and cross-document neighbours, compute for every query its nearest admissible cosine similarity after excluding its own document. Let `m_i` be that maximum similarity. Report:

```text
F_sem_mean   = mean(m_i)
F_sem_median = median(m_i)
F_sem_q10    = 10th percentile(m_i)
coverage(c)  = fraction(m_i >= c) over a frozen confidence grid
```

`F_sem` is label-free and requires no expensive target channel. It measures whether the cheap semantic states themselves recur across documents.

Because nearest-neighbour confidence can be inflated by a few generic memory hubs, also report the distribution of which memory records win top-1 retrieval: top-1 winner concentration, unique-winner fraction, and the share of queries served by the most-used 1% of memory items. High `F_sem` with extreme hub concentration is not interpreted as healthy formulaicity.

### F_struct — annotated structural regularity

Where span/section annotations exist, report a secondary structural statistic from the relative-position distributions of recurring tags. For tag `j`, bin its normalized start position into a frozen number of bins, compute normalized entropy `H_j / log(B)`, and define:

```text
F_struct = mean_j [1 - H_j / log(B)]
```

Only tags present in the preregistered minimum number of documents enter the mean. `F_struct = 1` means highly position-regular structure; values near 0 mean diffuse placement. This is diagnostic and corpus-descriptive; it is never fed to the tagger or retrieval rule.

### Cross-domain prediction

For every corpus/genre tested later, report `(F_sem, F_struct where available, avoided-call fraction, quality retention)`. The stronger claim is not "TJRO is cheap to retrieve" but that **formulaicity predicts the economic frontier**.

A future multi-genre test should evaluate whether avoided-call fraction at the frozen quality floor increases with `F_sem`/`F_struct`. If it does not, the proposed mechanism explanation is wrong even if this corpus yields a systems win.

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

Applicability diagnostics:

- `F_sem_mean`, `F_sem_median`, `F_sem_q10` and frozen-threshold semantic coverage curve;
- top-1 hub concentration / unique-winner fraction;
- `F_struct` when structural annotations exist;
- retrieval hit/fallback rate by target scale;
- savings and quality-retention frontier conditioned on the formulaicity statistics.

The systems ledger is part of the result. "Short embeddings are cheap", "retrieval saves work", and "this corpus is repetitive" are not accepted as assumptions.

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

### A5 — formulaicity explains where the system pays

The primary corpus result reports the formulaicity statistics next to the savings result. A single corpus cannot establish the cross-domain relationship, so no correlation claim is made from TJRO alone. The registered follow-up prediction is that, across independent corpora/genres, higher `F_sem` and (where available) `F_struct` predict a higher avoided-call fraction at the same frozen quality floor.

Failure of that relationship does not erase a local systems win, but it falsifies the proposed general applicability mechanism.

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
- **retrieval helps reconstruction but not tagging:** the recovered geometry is accurate in cosine space yet task-irrelevant;
- **formulaicity proxy fails:** `F_sem`/`F_struct` do not predict the observed savings frontier across corpora.

These are not post-hoc excuses. They are measured failure modes.

## No rescue by bigger memory or stronger retriever

The confirmatory run freezes the training-memory corpus, key schema, target channel set, `k` candidates, `tau` grid, temperature grid, threshold-selection rule and retrieval method before held-out scoring.

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
