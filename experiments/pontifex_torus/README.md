---
type: "Findings Record"
title: "Pontifex Torus v0"
description: "Cheap falsification study for occlusion-size lenses, periodic latent-space maps, and sample-efficient semantic cartography."
tags: [pontifex, torus, occlusion, latent-space, experiment]
timestamp: 2026-09-17T16:45:00-04:00
---

# Pontifex Torus v0

This experiment is the first cheap test of the newer Pontifex direction.
It deliberately excludes MaleCNS so the geometry can fail independently of the
connectome hypothesis.

## Core picture

Two embedding spaces are treated as the inner and outer halves of a toroidal
substrate. Shared occlusions provide corresponding interventions. A learned local
periodic deformation field approximates the map from the response surface in the
inner space to the response surface in the outer space.

The experiment does **not** claim that the torus representation itself is novel
latent-space alignment. The questions are narrower:

1. Does occlusion size contain predictive information about where a response lands
   in the other semantic space?
2. Does a periodic local map over text position + occlusion scale beat a
   size-agnostic map on unseen texts?
3. Can the map interpolate an occlusion size never observed during training?
4. How quickly does the map become useful as only a fraction of the response field
   is sampled?

## Encoders

- inner: `sentence-transformers/all-MiniLM-L6-v2`
- outer: `BAAI/bge-small-en-v1.5`

For each text, position and occlusion size `1, 2, 4, 8`, each space contributes a
within-space cosine displacement between the original text and its masked version.
No coordinate-level alignment between the two encoders is used.

## Conditions

- `agnostic`: source response + periodic text position only;
- `lens`: adds log occlusion size;
- `torus`: adds source-response × position/scale interactions and a second Fourier
  harmonic, acting as a cheap smooth local deformation field.

## Falsification tests

### Held-out texts

Train the map on 70% of texts and predict the outer response surface on wholly new
texts.

### Held-out scale

Train using occlusion sizes `1, 2, 8` and predict size `4` on held-out texts. A
positive result here is stronger than interpolation over already-observed scales.

### Sample efficiency

Train with 10%, 20%, 40%, 80% and 100% of available response-field samples while
keeping the same held-out texts. This is the first proxy for the active-cartography
claim: a useful map should emerge before exhaustive traversal.

## Next layers if v0 shows signal

1. context-window scale as a second lens variable;
2. active selection of the next occlusion by uncertainty/curvature;
3. explicit smooth torus mesh / deformation field rather than Fourier ridge;
4. multiple semantic spaces and map composition;
5. trivial/PID/random-recurrent controllers;
6. MaleCNS descending activity controlling local deformation while an external
   controller enforces equidistant flight.

The learned deformation, not the fly, is the map. MaleCNS is an optional candidate
operator for updating that map.
