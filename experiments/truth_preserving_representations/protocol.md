---
type: "Protocol"
title: "Sparse Truth Structural Identification — Experimental Protocol"
description: "Pre-registered finite-structure benchmark separating held-out operation prediction from structural identification up to isomorphism under arbitrary labels."
tags: [preregistration, structural-identifiability, finite-groups, in-context-algebra]
timestamp: 2026-08-24T01:36:00Z
---

# Sparse Truth Structural Identification — Experimental Protocol

## Status

Pre-registration for the **next model-backed experiment** accompanying `truth_preserving_representations.md`.

The exact toy enumeration in this directory was completed before this protocol and is therefore an apparatus check, not confirmatory evidence for the hypotheses below. No model-backed result should be entered into this document after inspection without an explicit dated amendment.

## 1. Primary question

When algebraic elements are assigned fresh arbitrary token identities in every episode, does held-out operation prediction track the amount of information available to identify the generating algebraic structure, or can predictive competence become high while multiple non-isomorphic structures remain exactly compatible with the revealed truths?

## 2. Primary estimand

For a frozen hypothesis class $\mathcal H$ and revealed evidence $E_k$, compute

$$
N_k=|V_{\mathcal H}(E_k)/\cong|.
$$

The primary learned-model analysis asks how model confidence and structural-class accuracy vary with $N_k$ after controlling for evidence count $k$ and held-out operation accuracy.

The central dissociation of interest is:

$$
\text{high held-out product accuracy}
\quad\text{with}\quad
N_k>1.
$$

## 3. Gate 0 — exact apparatus

Already completed before preregistration of the model-backed gate.

Required invariants:

- arbitrary bijective relabeling preserves the complete transported operation;
- local order-four evidence leaves more than one non-isomorphic group in the toy class;
- stronger background constraints can collapse that version space;
- a non-injective decoder admits multiple non-isomorphic latent operation tables with identical decoded multiplication.

Repository unit tests encode these invariants. Gate 0 passing is necessary but not evidence for a learned-model claim.

## 4. Gate 1 — finite exact version-space corpus

### 4.1 Hypothesis class

Before generation, freeze a catalog of finite groups with explicit isomorphism-class identifiers. The primary track should include at least two group orders for which multiple non-isomorphic groups exist. Candidate orders include 4, 6, 8, 9, 10, 12, and 16, subject to exact enumeration/tooling feasibility.

Do **not** allow carrier cardinality alone to identify most classes.

Record:

- group/order catalog;
- canonical operation tables;
- source or generator used for each table;
- isomorphism-canonicalization method;
- corpus seed;
- split seed.

### 4.2 Episode generation

For every episode:

1. sample a target isomorphism class according to the frozen class prior;
2. sample a fresh random permutation of its carrier into opaque token IDs;
3. construct the complete relabeled Cayley table;
4. sample or select a sequence of revealed product facts;
5. after each prefix $E_k$, compute the exact surviving isomorphism classes;
6. sample held-out product queries only from facts not yet revealed.

No token identity may carry a stable group-element meaning across episodes.

### 4.3 Split policy

Freeze three conceptually different splits:

- **IID relabeling split:** known group classes, unseen carrier permutations;
- **combination split:** known group classes but held-out patterns of revealed facts;
- **class-OOD split:** at least one group class or order held out from model training when feasible.

The class-OOD split is exploratory unless the exact training/test class families are frozen before the first model-backed run.

## 5. Evidence conditions

At minimum compare:

### R — random truths

Uniformly sample unrevealed multiplication facts.

### G — exact information-greedy truths

At each step choose a fact that maximally reduces the exact number of surviving isomorphism classes or, under a declared prior, the posterior entropy over classes. Ties are resolved by a frozen deterministic rule or seeded randomization.

### T — minimum/near-minimum teaching truths

For small structures, search exactly for a minimum identifying set when computationally feasible. For larger structures use a frozen approximation. Exact and approximate cases must be reported separately.

### D — structurally redundant control

Select facts with substantial local predictive utility but low discrimination among the currently surviving structural classes. This condition is intended to separate ordinary operation interpolation from structural elimination.

## 6. Learner conditions

### B0 — exact constraint solver

Tracks the true version space. This is the epistemic ceiling/floor: if $N_k>1$, no learner should be scored as wrong merely for not identifying a unique target from the supplied evidence.

### B1 — non-neural relational baseline

A constraint/graph-based predictor using only revealed relations, with hyperparameters frozen before evaluation.

### B2 — prediction-only transformer

An *In-Context Algebra*-style sequence model trained to answer held-out product queries under episode-specific random token mappings.

### B3 — prediction + structural objective

Matched architecture and compute to B2, with an auxiliary objective over the target isomorphism class or a permutation-invariant structural representation.

The B2/B3 comparison is invalid if model size, data volume, or training compute is not matched within the preregistered tolerance.

## 7. Endpoints

### Primary endpoints

1. **Structural-class log loss** conditional on the exact version space.
2. **Structural exact recovery rate** on episodes with $N_k=1$.
3. **Premature certainty rate:** probability mass assigned to a single class when $N_k>1$.
4. **Prediction-identification dissociation:** held-out operation accuracy stratified by $N_k$.

### Secondary endpoints

- held-out product accuracy;
- complete-table reconstruction up to isomorphism;
- evidence budget required to reach $N_k=1$;
- area under the structural-ambiguity collapse curve;
- invariance across fresh relabelings of the same underlying target;
- representation-probe accuracy for isomorphism class at matched product accuracy.

## 8. Confirmatory hypotheses

### H1 — arbitrary relabeling robustness

On known structural classes, a relational learner should retain performance across unseen carrier permutations substantially better than a stable-token memorization control.

### H2 — prediction does not imply structural identification

There exists a preregistered evidence range in which the prediction-only learner is substantially above chance on held-out products while a nontrivial fraction of episodes have $N_k>1$.

The claim fails if the dissociation disappears after conditioning on evidence count and query type.

### H3 — discriminative teaching beats random revelation

The G or T evidence policy reaches $N_k=1$ with fewer revealed facts than R on the exact finite benchmark.

This hypothesis is primarily about the benchmark geometry; learned-model gains under the same policy are a separate result.

### H4 — structural supervision improves epistemic calibration

At matched product accuracy, B3 should reduce premature structural certainty and improve structural recovery on $N_k=1$ episodes relative to B2.

## 9. Negative controls

Required controls:

- **shuffled-truth control:** permute result tokens so revealed triples are inconsistent with the target operation;
- **stable-label leakage control:** train/evaluate a deliberately stable token mapping to establish how much easier the leaked task is;
- **carrier-size-only baseline:** predict class from group order alone;
- **fact-count-only baseline:** predict ambiguity from $k$ without reading fact content;
- **random class-prior baseline:** ignores evidence;
- **fresh-relabel duplicate episodes:** identical underlying facts under independent token permutations, used to test output invariance.

## 10. Non-injective extension

This is a separate secondary track and must not be mixed into the bijective primary result.

Introduce an observation/decoder map

$$
f:X\twoheadrightarrow A
$$

with controlled fiber sizes. Generate latent operations compatible with the same decoded algebra. Measure whether a learner can or should distinguish latent implementations under different intervention sets.

Key distinction:

- observational equivalence under the decoder;
- latent structural equivalence up to isomorphism;
- interventional distinguishability when operations on representatives are directly queried.

The toy 3-to-2 decoder in `core.py` is the Gate 0 sanity check for this track.

## 11. Statistical reporting

Because the exact structural state is known, report confidence intervals over episodes rather than inferential significance alone.

For every main curve report:

- number of target classes;
- number of episodes;
- evidence-budget distribution;
- exact distribution of $N_k$;
- per-class and macro-averaged endpoints;
- at least 95% bootstrap intervals over episodes using a frozen resampling seed.

Do not average away $N_k$: the primary scientific object is performance conditional on exact ambiguity.

## 12. Falsification and downgrade rules

The position paper's experimental contribution is substantially weakened if:

1. $N_k$ adds no explanatory or calibration information after ordinary product accuracy and evidence count are known;
2. structurally discriminative evidence does not outperform random evidence even under exact finite optimization;
3. learned results depend on token identities and fail fresh relabelings;
4. class recovery is driven primarily by carrier size or other trivial metadata;
5. an implementation-level literature scan finds a prior benchmark already performing the same version-space quotient evaluation;
6. B3 appears better only because of extra compute or supervision volume rather than the structural objective.

## 13. Literature comparator requirement

Before the first model-backed confirmatory run, re-check at least:

- *In-Context Algebra* and released code/data if available;
- finite-group learning benchmarks;
- teaching-dimension / preference-based teaching variants;
- finite model identification / active query learning;
- invariant/orbit recovery benchmarks;
- recent representation-identifiability work.

If a semantically equivalent benchmark is found, amend the protocol before execution rather than silently narrowing the novelty claim afterward.
