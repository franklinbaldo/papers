---
type: "Protocol"
title: "Semantic Atlas Experiment C — Manifold Geometry versus Flat Geometry"
description: "Pre-registration testing whether local/manifold geometry earns predictive advantage over flat Euclidean geometry on held-out transitions, and control advantage over straight-line steering at matched budget."
tags: [semantic-atlas, preregistration, manifolds, geodesics, steering, euclidean-baseline]
timestamp: 2026-08-24T12:00:00Z
---

# Semantic Atlas Experiment C — Manifold Geometry versus Flat Geometry

## Status

Pre-registration. Nothing below may be tuned after inspecting aggregate
outcomes. A scientific negative exits normally and is recorded as such.

## Motivation and dependency

The spectral-bottleneck programme (`experiments/semantic_atlas/spectral_bottleneck/`)
closed one shortcut: semantic variables are not generically the first Fiedler
bottleneck, and the confidence property that did pass registered gates proved
strongly conditional on checkpoint, layer, and corpus realization. This
experiment does not attempt to rescue the bottleneck formulation. It tests the
central arrow of the manifold-aware Atlas directly:

> representation → local manifold structure → **advantage** in predicting real
> dynamics or in controlling them,

with flat Euclidean geometry as the pre-registered adversary. The comparison is
Section 5.2 of `semantic_atlas_manifolds.md` ("the key comparison ... is
whether [curved paths] produce better measured behavior") turned into a
falsifiable gate.

Depends on no spectral result. Requires only pinned models and frozen corpora.

## Models and observer

- `HuggingFaceTB/SmolLM2-135M` @ `93efa2f097d58c2a74874c7e644dbc9b0cee75a2`;
- `HuggingFaceTB/SmolLM2-360M` @ `f8027fd0eaeea54caa13c31d31b9fdc459c38b49`.

Observer: **final-layer causal hidden state at the last input token**, frozen a
priori. No layer scan is permitted anywhere in this experiment; the
relative-depth falsification showed that scan-derived coordinates do not
survive fresh corpora, and this protocol refuses that degree of freedom.

Each model must pass its gates **independently**. No cross-model pooling.

## Corpora

Three disjoint frozen manifests, created before any run:

1. **support set** — natural prose excerpts (same eligibility rules as
   `natural_future_entropy.py`: one deterministic excerpt per eligible file,
   machinery excluded), used exclusively to build representation graphs;
2. **transition set** — frozen prompt families; for each prompt, the model's
   own teacher-forced continuations supply realized transitions
   \((z_t, z_{t+\delta})\) for \(\delta \in \{1, 8\}\);
3. **steering set** — frozen origin/target description pairs spanning at least:
   sentiment polarity flip; register shift (informal→formal); topic move inside
   one domain; topic move across domains; one deliberately hard pair expected
   to expose a barrier.

Manifest hashes are frozen at registration; corrections require a new manifest
version and an explanation in the findings record.

## Graph construction (frozen)

Symmetric Gaussian-weighted kNN over support-set states, reusing the graph
machinery of `spectral_bottleneck`, with `k ∈ {8, 16, 32}` all reported (no
post-hoc selection). Geodesic distance = graph shortest-path distance;
diffusion distance at registered times \(t \in \{1, 4\}\) as secondary family.
All conclusions must hold in at least 2 of 3 neighborhood scales; single-scale
survival does not count.

## Part 1 — Predictive advantage (geodesic versus Euclidean)

### Hypothesis P

Geodesic (and diffusion) distances on the support graph predict properties of
**realized** transitions strictly better than Euclidean distance.

Primary outcome: rank correlation between distance and the model's own
log-probability of the realized continuation, computed **on discordant
triples**: triples \((z_t, b_1, b_2)\) of an actual next state and two
counterfactual continuations where Euclidean and geodesic rankings disagree.
Concordant cases are reported but carry no evidential weight — agreement there
is guaranteed by construction and would make any positive result trivial.

Secondary outcomes: transition plausibility (realized versus density-matched
distractors), and sign of entropy change \(\Delta H_{t\rightarrow t+8}\).


### Gates (per model, per horizon)

1. PASS — geodesic beats Euclidean on discordant triples: median
   \(\Delta\)Spearman \(\ge 0.05\), permutation \(p < 0.01\) (10,000
   permutations, seed frozen);
2. PASS — advantage survives in \(\ge 2/3\) neighborhood scales and exceeds
   the degree-preserving edge-randomization contrast (advantage on the real
   graph minus advantage on randomized graphs \(> 0\));
3. PASS — density-matched control: bucketing states by local kNN radius, the
   geodesic advantage within buckets remains positive (rules out "geodesic is
   just a density proxy");
4. PASS — direction consistency: geodesic-closer pairs must show higher
   realized log-probability, not merely different ranks;
5. PASS — holds independently in both pinned models.

Support requires all five gates for Part 1.

### Falsifier (Part 1)

Euclidean matches or beats geodesic on discordant triples under every
registered graph family in either model, or the apparent advantage vanishes
under edge randomization or density bucketing. **This negative is not
trivial**: discordant-triple evaluation isolates exactly the cases where the
two geometries make different predictions, so failure means the manifold's
extra structure buys nothing about the model's actual behavior — the core of
the manifold hypothesis, not a side consequence of spectral clustering theory.

## Part 2 — Control advantage (geometry-aware versus straight-line steering)

### Hypothesis C

Candidate selection constrained by measured support geometry reaches frozen
semantic targets at lower measured cost than straight-line (Euclidean
interpolation) steering at identical intervention budget.

Conditions (all sharing candidates, budget, seeds, and scoring):

1. `straight-line`: hidden-state nudges along the Euclidean origin→target
   chord;
2. `support-projected`: same nudges after projection onto the span of
   support-set neighbors (tangent approximation);
3. `shuffled-support`: condition 2 whose "projection" uses a
   degree-preserving randomized support set (negative control);
4. `random-direction`: matched-norm random nudges (floor control).


### Gates

1. PASS — success@budget: `support-projected` beats `straight-line` by
   \(\ge 10\) percentage points aggregated over the steering manifest;
2. PASS — efficiency: median intervention norm per unit of target progress at
   least 10% below `straight-line`;
3. PASS — degradation guard: no worsening \(\ge 0.1\) nats of mean
   log-probability and no blinded-fluency drop;
4. PASS — specificity: `shuffled-support` and `random-direction` fail gates
   1–2 (if they pass, the advantage was generic perturbation, not geometry);
5. PASS — replicates in both pinned models.

Support requires all five gates for Part 2.

### Falsifier (Part 2)

Straight-line steering matches geometry-aware steering at matched budget in
either model, or the advantage survives support randomization. As in Part 1,
this negative has content: it rejects the operative reason the Atlas prefers
manifold charts — better behavior per unit cost — on the registered models,
rather than rejecting some auxiliary spectral assumption nobody needs.

## Analysis discipline

- Every threshold above is frozen at registration; no re-fitting after
  inspection.
- All neighborhood scales, horizons, and diffusion times are reported,
  including failures; no selective reporting.
- Execution failures fail CI; scientific gate failures exit normally and are
  recorded in a dated Findings Record alongside `summary.json` artifacts.
- Any exploratory analysis discovered mid-run must be labelled exploratory
  and, if promotable, preregistered on a fresh corpus before counting — the
  rule that killed the 56% depth rule applies to this experiment's own
  surprises too.

## Claim boundary

A positive result establishes predictive/control advantage of graph-local
geometry over Euclidean distance **on these two pinned small checkpoints,
these corpora, and this frozen observer**, and nothing more. It does not
establish cross-model chart portability (M5), that bottlenecks are causal
barriers, or that a rendered atlas faithfully represents the full geometry. A
negative result does not show manifolds are absent from larger models; it shows
that on the tested realizations their extra structure earned no measurable
predictive or control advantage over flat geometry — which is precisely what
the programme must stop assuming and start measuring.

