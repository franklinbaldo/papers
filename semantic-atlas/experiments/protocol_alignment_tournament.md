---
type: "Protocol"
title: "Semantic Atlas Experiment A.1 — Cross-Observer Alignment Tournament"
description: "Preregistered comparison of linear, correlation-aware, local-manifold, and transport-based cross-observer alignment methods on the frozen Experiment A corpus."
tags: [semantic-atlas, preregistration, alignment, cca, manifold-alignment, optimal-transport]
timestamp: 2026-08-25T06:25:00Z
---

# Semantic Atlas Experiment A.1 — Cross-Observer Alignment Tournament

## Question

Experiment A found replicated anchoring above a shuffled-correspondence control,
but only moderate absolute held-out agreement. Is that limitation intrinsic to the
observer pairings, or is it partly caused by the rigid assumption that whitening
followed by one global orthogonal Procrustes map is the correct cross-observer
alignment family?

This experiment tests that question before changing Experiment B/MPC.

## Frozen data boundary

A.1 reuses the exact Experiment A corpus derivation:

- source commit `ff68b0653063e11e9cc3da887003bc0d46b14d26`;
- deterministic `sha256(path)` ordering;
- first 80 Markdown documents: calibration;
- next 24: held-out;
- next 12: trajectory corpus;
- excerpt length and text extraction identical to Experiment A.

No held-out document may be replaced, added, removed, or reclassified after any
A.1 result is observed.

The primary local observer pair is the already frozen Experiment A v1 pair:

- `Qwen/Qwen3-Embedding-0.6B@97b0c61`;
- `sentence-transformers/all-MiniLM-L6-v2@1110a24`.

The API replication pair is secondary:

- `gemini-embedding-001`;
- `jina-embeddings-v3`, 1024 dimensions, task `retrieval.passage`.

## Data preservation rule

Experiment A artifacts preserved corpus identity, model identity, aggregate
metrics, atlas state, generated continuations, and SRF trajectories. They did not
preserve the raw calibration/held-out embedding matrices or the complete learned
alignment transform. That is sufficient to reproduce the published A outcome for
pinned local models, but insufficient for zero-recollection methodological
reanalyis, especially for hosted APIs whose outputs are not revision-addressed.

Therefore A.1 introduces an immutable observer-cache artifact. For every observer
and split used in the tournament it records or durably references:

1. observer/provider identity and all non-secret request configuration;
2. source commit, ordered corpus paths, and text-content hashes;
3. embedding dimensionality and dtype;
4. raw observed embedding matrix, or a durable content-addressed object plus
   SHA-256 when repository size makes direct versioning unreasonable;
5. cache SHA-256;
6. collection timestamp for non-revisioned hosted APIs.

Credentials, authorization headers, provider tokens, and environment values must
never be persisted.

For immutable local checkpoints, recomputation from the frozen corpus and revision
is allowed. For hosted APIs, no new A.1 call may be used for model selection unless
the returned raw embeddings are persisted under this rule before alignment results
are inspected. GitHub Actions artifact retention alone is not longitudinal storage.

## Alignment methods

All methods receive the same calibration rows and are evaluated on the same frozen
held-out rows.

### M0 — current baseline

Whitening in each native space followed by orthogonal Procrustes onto the frozen
reference canonical targets.

### M1 — regularized affine alignment

Fit a linear map plus intercept from transfer-observer calibration embeddings to
the reference canonical targets using ridge regularization. Regularization strength
is selected only inside calibration folds.

### M2 — regularized CCA

Fit regularized canonical-correlation projections for the two observers on paired
calibration examples and map the resulting shared coordinates into a frozen common
orientation. Number of canonical components and regularization are selected only
inside calibration folds.

### M3 — graph-regularized manifold alignment

Construct frozen k-nearest-neighbor graphs independently in each observer space
using calibration rows only. Optimize paired alignment loss plus within-observer
Laplacian smoothness. Neighborhood size and graph regularization are selected only
inside calibration folds.

The graph Laplacian is a local-geometry regularizer, not a semantic oracle. Negative
spectral results in Experiment A/#307 do not license Fiedler-based label selection
here.

### M4 — local Procrustes

Use a frozen calibration-only neighborhood rule to choose local paired anchors for
each query, then fit a regularized local orthogonal/affine map. Held-out labels or
held-out cross-observer distances may not choose the neighborhood or model family.

### M5 — Gromov-Wasserstein / fused GW diagnostic

Estimate whether relational geometry can be aligned when pointwise global maps are
insufficient. This is a secondary structural diagnostic. It may not replace the
primary paired methods merely because its post-hoc visualization looks cleaner.

Kernel CCA, neural alignment, normalizing flows, or other nonlinear rescue methods
are outside A.1. They require a separately preregistered follow-up if A.1 is
negative.

## Hyperparameter selection

All tunable choices are selected using only the 80 calibration documents through
fixed inner cross-validation folds derived deterministically from path hashes.
Every method uses the same folds.

The 24 held-out documents are opened exactly once for confirmatory comparison after
all method configurations are frozen.

No metric computed on held-out may alter:

- regularization strength;
- dimension/components;
- neighborhood size;
- graph kernel/bandwidth;
- local/global method selection;
- transport regularization;
- method inclusion or exclusion.

## Negative controls

Each primary method M0–M4 must be rerun under the same deterministic shuffled-row
correspondence used as a semantic-anchor negative control. Additional calibration-
only permutations may estimate uncertainty, but they may not replace the registered
held-out control after results are observed.

A method that improves paired alignment while improving shuffled alignment by the
same amount has not demonstrated a better semantic alignment.

## Confirmatory metrics

Report on the same 24 held-out documents:

1. canonical-coordinate RMSE;
2. row-wise canonical cosine;
3. nearest-quasar agreement under the frozen SRF simplex;
4. kNN overlap / neighborhood recall for registered `k` values;
5. local pairwise-distance correlation;
6. paired-minus-shuffled separation for all applicable metrics.

Trajectory/path agreement on the frozen 12 trajectory sources is secondary and is
computed only after the held-out alignment comparison has been frozen. MPC route
completion is not part of method selection in A.1.

## Decision rule

The current Procrustes method remains the default unless another primary method:

1. improves held-out canonical cosine and coordinate RMSE in the same direction;
2. does not materially reduce nearest-quasar agreement;
3. improves at least one local-geometry metric without degrading the other below
   the baseline uncertainty band; and
4. preserves or strengthens the paired-vs-shuffled separation.

A method that wins only one metric does not replace M0. If methods trade off with no
clear Pareto improvement, retain M0 and report the ambiguity.

The API observer pair is a replication check, not a tuning set. A method selected
from the local pair must be applied unchanged to the API pair if cached API
embeddings are available. Failure to replicate is evidence against generality.

## Relation to Experiment B (#267)

A.1 is a measurement-quality experiment, not steering. It must not tune MPC using
B outcomes.

If A.1 identifies a clearly superior alignment before the first confirmatory B run,
B may use that transform only through an explicitly versioned new A-derived
substrate and with #267 recording the change before outcomes are inspected.

If B has already produced confirmatory outcomes on the original A substrate before
A.1 finishes, A.1 becomes a separate replication/robustness analysis; it must not
retroactively redefine the original B result.

## Falsification

The hypothesis that alignment family is the main bottleneck weakens if M1–M4 do not
produce a clear held-out Pareto improvement over M0, if gains disappear under the
shuffled control, or if a local-pair winner fails on the frozen API replication.

A negative result supports the simpler reading that moderate observer agreement is
an empirical property of the representations/corpus rather than merely a bad
choice of global orthogonal alignment.

## Reporting

Version the complete method table, hyperparameters selected from calibration,
negative controls, held-out metrics, cache hashes, and any failures. Do not report
only the winning method.

Refs #266 #267 #307 #368 #369.
