---
type: "Experiment Protocol"
title: "Cached Semantic Tile Pyramid with Low-Level Flavourizers"
description: "Pre-registered variation testing whether dense low-level semantic channels and reusable cached embeddings improve tag localisation, with and without MaleCNS-assisted training."
tags: [malecns, semantic-tagging, flavourizer, multiscale, cache, preregistration]
timestamp: 2026-09-14T20:30:00-04:00
status: "pre-registered; no confirmatory results yet"
---

# Cached Semantic Tile Pyramid with Low-Level Flavourizers

> **Pre-registered variation; no confirmatory results yet.** This is a new cell in the interface matrix. It does not rescue or reinterpret Run 1, Run 2, or the fly-assisted experiment in #443.

## Question

Can precise semantic span tagging be improved by representing a document as a dense pyramid of reusable short-span embeddings and applying trainable flavourizers directly to the lowest-cost, highest-resolution channels?

A secondary question is whether temporary MaleCNS assistance improves those flavourizers even when the final tagger runs without a connectome.

The central engineering hypothesis is that short spans are cheap to embed in batches, easy to cache by content, and cheap to re-use across training runs. The central modelling hypothesis is that low-level channels provide the spatial precision needed for tag boundaries while higher channels provide context.

## Representation

A document is tiled at predeclared scales:

`1024, 512, 256, 128, 64, 32, 16, 8, 4` tokens.

Tiles overlap at stride `scale / 2` except the document/root tile. Smaller scales may later be extended to token/byte channels, but token/byte results are **exploratory unless added in a new preregistration before execution**.

For every child tile, relation channels are computed only inside one encoder space. Examples:

- `R(256|512)` and `R(256|1024)` under Jina;
- `R(64|128)` and `R(64|256)` under MiniLM;
- a future tiny encoder may provide `R(8|32)` or lower channels.

Different encoders may coexist as separate channels. Cross-encoder subtraction/division is forbidden.

## Content-addressed semantic tiles

Each raw tile has a stable cache identity:

`sha256(encoder_id || encoder_revision || normalisation_version || text_bytes)`.

The embedding is computed once and reused whenever the exact same tile appears again. Relation channels are derived from cached child/parent embeddings and do not call the encoder again.

The cache report must include:

- total tile occurrences;
- unique cache keys;
- reuse ratio;
- embedding calls avoided by reuse;
- wall-clock encode time by scale;
- encoded tokens/bytes by scale;
- cache bytes by scale.

No claim that short chunks are cheaper is accepted without this measured ledger. Encoder launch/batching overhead counts.

## Flavourizers

Each scale/channel may have its own low-rank residual transformation:

`C'_s = C_s + U_s tanh(V_s C_s)`.

The transformation acts on cached features; changing or retraining a flavourizer must not trigger re-embedding.

The primary comparison freezes four arms before results:

1. `none` — no flavourizer;
2. `high_only` — flavourizers only on channels whose child scale is >=128;
3. `low_only` — flavourizers only on channels whose child scale is <=32;
4. `all_scales` — flavourizers on all eligible channels.

Parameter budget is matched between `high_only` and `low_only` by adjusting rank if necessary. `all_scales` is reported with its larger parameter count and is not used to claim that scale rather than capacity caused an improvement unless a matched-budget control agrees.

## Final inference path

The confirmatory deployed path contains no gold labels, food, or tag text:

`untagged text -> cached tile embeddings -> relation channels -> flavourizers -> tag head`.

For the fly-assisted arm, MaleCNS exists only during training and is absent from held-out inference.

## Primary outcomes

The primary scientific metric is **macro per-tag AUPRC** on held-out documents.

Secondary metrics:

- any-tag AUPRC;
- tag identity accuracy on true spans;
- boundary AUPRC at the finest available tile resolution;
- sample efficiency (examples required to reach fixed macroAP thresholds);
- per-document paired deltas;
- residual magnitude `||Delta|| / ||C||` by scale;
- compute/cache ledger.

## Confirmatory gates

### G1 — low-level flavour is useful

`low_only` must beat `none` by >=0.03 absolute macro per-tag AUPRC and have a positive paired document delta in at least 12/17 documents.

### G2 — localisation is genuinely low-level

`low_only` must beat matched-budget `high_only` by >=0.02 macro per-tag AUPRC **or** >=0.04 boundary AUPRC, with the same held-out folds.

### G3 — dense pyramid beats the sparse relation design

The best confirmatory dense-pyramid arm must beat the existing sparse-relations representation by >=0.03 macro per-tag AUPRC under the same encoder and tag split.

### G4 — caching has practical value

At least 50% of flavourizer-training epochs after cache construction must require zero encoder calls. This is a systems gate, not a semantic-quality claim.

## MaleCNS-assisted variant

After the standalone pyramid is evaluated, the same final architecture may be trained with the #443 training-only scaffold:

`flavourized channels -> frozen MaleCNS -> disposable taste head -> food target`.

The final tagger is evaluated after the fly branch is removed.

Arms are:

- tag-only;
- MaleCNS-assisted;
- degree-null-assisted;
- random-ESN-assisted.

A topology-specific teaching claim requires MaleCNS assistance to beat **all three** alternatives under matched data, seeds, final parameters, selection, and inference path.

## Kill rule

This variation is not an infinite escape hatch. If the predeclared dense pyramid plus `none/high_only/low_only/all_scales` fails G1-G3, lower channels are not recursively added as a rescue. Token/byte channels require a separately frozen follow-up before results are inspected.

Likewise, a positive found only after changing scales, ports, encoder family, or flavourizer capacity outside this protocol is reported as a new axis effect, not as this experiment succeeding.

## Interpretation boundaries

A win for low-level flavourizers means fine channels are useful for tagging under this representation. It does not mean MaleCNS caused the win.

A win for MaleCNS-assisted training means the connectome was useful as a temporary training scaffold. It does not mean the connectome is necessary at inference.

A cache/reuse win is an engineering result and must not be presented as a biological or semantic result.
