---
type: "Protocol"
title: "Semantic Atlas Experiment E — Empirical Inverse Atlas"
description: "Pre-registered experiment testing whether inference memory in the SRF can recover lexical realizations and route-conditioned draft tokens without a full model call at every step."
tags: [semantic-atlas, preregistration, knn, retrieval, decoding]
timestamp: 2026-08-09T00:48:00Z
---

# Semantic Atlas Experiment E — Empirical Inverse Atlas

## Question

Can previously observed causal inference states form a non-parametric inverse map from Semantic Reference Frame coordinates back to locally realizable language?

This experiment does **not** assume that a token has a unique semantic coordinate. It treats lexical realization as a conditional distribution over an observed local neighborhood.

## Prior-art boundary

Nearest-neighbor language models already store a representation of a context together with the token that followed it and use nearest-neighbor retrieval to improve next-token prediction. Inference-time memories and retrieval-based speculative decoding extend related ideas.

Gritta, Xue & Lampouras (2025), **DReSD: Dense Retrieval for Speculative Decoding** (arXiv:2502.15572), is a particularly close baseline: it uses approximate nearest-neighbor search over contextualized token embeddings to retrieve semantically relevant token sequences for target-model speculative decoding. Therefore neither dense semantic retrieval nor retrieval-backed drafting is a Semantic Atlas novelty claim.

The additional hypothesis here is specific to Semantic Atlas:

1. store the memory in the calibrated SRF rather than only in one model's native hidden coordinates;
2. condition retrieval on semantic **direction/route**, not only current-point similarity;
3. expose lexical uncertainty as a function of atlas resolution / zoom;
4. use the memory as an inverse layer for an independently planned semantic route.

## Datastore

For every registered inference step, store an `InferenceRecord` with:

- causal SRF state `q_t`;
- optional incoming velocity and observed `q_(t+1)`;
- exact context reference/text according to the frozen privacy/data policy;
- sampled next token and a short lexical block when collected;
- model and tokenizer revisions;
- when affordable, the target model's top-k token probabilities/logits.

Storing top-k distributions is preferred to storing only one sampled token because one draw throws away information that was already computed during inference.

Training/calibration trajectories and held-out query trajectories must be separated by prompt family.

## Decoder A — positional kNN

Given a query state `q`, retrieve the nearest `k` inference records in SRF distance and estimate a token distribution with a registered kernel bandwidth.

This is the direct analogue of a non-parametric lexical lookup and is the simplest baseline inside the atlas.

## Decoder B — route-conditioned kNN

For desired local displacement `d*`, reweight neighbors by both state proximity and agreement between their observed displacement

`q_(t+1) - q_t`

and `d*`.

This tests whether knowing **where the planner wants to go** provides useful lexical information beyond knowing only where the conversation currently is.

## Decoder C — verified LLM interpolation

When the local datastore does not have sufficiently low entropy, retrieve neighboring contexts/realizations around the desired target and use the full generator as an inverse solver.

The generator is asked to synthesize a candidate using the retrieved examples as constraints/hints. Every candidate is then re-embedded and evaluated in the SRF. No assumption is made that mixing two texts produces the Euclidean midpoint of their embeddings.

The registered policy keeps the candidate with the smallest measured route/target error and counts every failed attempt toward compute cost.

## Multiresolution test

For each held-out state, vary neighborhood size / radius to emulate semantic zoom. Measure

`H(next_token | local atlas neighborhood)`.

The central multiresolution prediction is that sufficiently dense, fine local regions should have lower lexical entropy than coarse regions. The atlas can decode directly only where the registered entropy/confidence threshold is satisfied; otherwise it must fall back to the target model.

## Conditions

1. full target LLM;
2. native-space kNN-LM-style retrieval;
3. DReSD-style dense contextual retrieval/speculative drafting, using the closest faithful reproduction compatible with the frozen model and datastore;
4. SRF positional kNN;
5. SRF position + incoming velocity;
6. SRF route-conditioned inverse atlas;
7. inverse atlas with stored top-k logits;
8. inverse atlas + verified LLM interpolation;
9. random-neighbor and shuffled-route controls.

If an exact DReSD reproduction is not technically compatible with the frozen model, record the deviation and preserve the essential comparison: dense context-conditioned ANN retrieval of candidate token sequences with target-model verification, **without** Atlas route information.

## Metrics

- next-token top-1/top-k recall against target-model distribution;
- KL/Jensen-Shannon divergence when comparable stored logits exist;
- short-block exact/accepted-token rate under target-model verification;
- SRF endpoint error of retrieved/generated blocks;
- local route progress and curvature;
- lexical entropy versus radius / k;
- lookup latency and serialized datastore size;
- fraction of steps confidently decoded without a target-model forward;
- target-model calls per output token;
- total FLOPs/latency including failed interpolation attempts.

For speculative-drafting conditions, report accepted tokens per target-model verification and end-to-end speed/latency separately from semantic route quality. Retrieval speedup is not evidence of route conditioning, and route improvement is not automatically a speedup.

## Key ablations

- state only vs state + desired route;
- emitted token only vs stored top-k distribution;
- native dense retrieval vs calibrated SRF retrieval;
- correct vs shuffled route directions;
- exact same-model memory vs cross-model calibrated memory;
- fixed radius vs adaptive zoom by lexical entropy.

## Falsification

The inverse-atlas claim is weakened if SRF retrieval does not beat native-space/dimensionality-matched baselines on held-out lexical prediction or route realization.

The **route-conditioned** claim fails if desired direction provides no held-out advantage over position-only retrieval **and over a strong dense contextual retrieval baseline such as DReSD-style drafting**.

The multiresolution claim fails if lexical uncertainty does not decrease predictably with local atlas support or if sufficiently useful resolution requires essentially memorizing every exact context.

The efficiency claim fails if target-model verification/interpolation calls erase any savings from lookup-based draft generation, or if a non-Atlas dense-retrieval baseline already achieves equal or better acceptance/latency at comparable datastore cost.

## Claim boundary

A successful result demonstrates statistical recoverability of local lexical realizations from an empirical inference memory. It does not imply a unique inverse function `SRF point -> token`, and it does not make a stored corpus equivalent to a model's unobserved knowledge.

Dense semantic retrieval and retrieval-based speculative decoding are prior art. The narrower frontier claim is that **calibrated SRF position plus incoming trajectory plus an independently planned desired displacement** provides useful held-out lexical guidance beyond strong context-only retrieval.

## Frontier reference

- Gritta, M., Xue, H., & Lampouras, G. (2025). **DReSD: Dense Retrieval for Speculative Decoding.** arXiv:2502.15572.

Refs #260 #276 #282.
