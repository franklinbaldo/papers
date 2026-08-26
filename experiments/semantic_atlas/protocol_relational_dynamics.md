# Semantic Atlas — Relational Dynamics Experiment v1

## Question

With both encoders frozen, document vectors are static. The candidate dynamical object is the **relational structure induced by a growing corpus**: k-nearest-neighbor identity and rank, density/hub structure, and region-level neighborhood churn.

The experiment asks a deliberately narrow question:

> Given two frozen embedding observers over the same final corpus, does the neighborhood-churn process induced by the *actual corpus-growth order* diverge between observers more than expected under exchangeable (stationary) insertion, and does any excess divergence survive appropriate hubness correction?

No generator, policy, labels, retraining, or trajectory model is used.

## Frozen substrate

The experiment inherits the exact model identities and source corpus from `model_backed_a_v1.json`:

- reference observer: `Qwen/Qwen3-Embedding-0.6B@97b0c61`;
- transfer observer: `sentence-transformers/all-MiniLM-L6-v2@1110a24`;
- source commit: the existing Experiment A `source_commit`;
- corpus selection: the same path-hash rule used by Experiment A.

All 116 selected Markdown documents are embedded: 80 calibration, 24 held out, and 12 trajectory-source documents. The latter are treated only as documents; **no continuations are generated**.

Raw and L2-normalized matrices for both observers are persisted through the content-addressed embedding-cache format introduced in PR #371, including corpus/model provenance and SHA-256 integrity.

## Chronology and stationary null

### Observed order

For each selected document, define its arrival time as the earliest Git commit timestamp touching that path at or before the frozen source commit. Sort by this timestamp; ties are broken by `sha256(path)`.

This is a repository-growth chronology, not a claim about publication date or semantic causality. It is used because it is deterministic, externally recorded, and available without labels.

### Null

The stationary null is **exchangeable insertion**: 128 shared random permutations of the same final 116-document corpus, seed `20260825`.

The final vectors and pairwise geometry are held fixed. Only insertion order changes. Therefore this null automatically preserves each observer's anisotropy, static neighborhood mismatch, and final hub structure.

If the observed chronology does not depart from this null on the preregistered semantic-drift statistic, neighborhood churn is treated as finite-sample estimation transient rather than corpus-flow dynamics.

## Churn law

Primary `k = 5`; sensitivity checks use `k in {3, 10}`.

Start with `n_0 = 24` documents and add batches of 4 until the final corpus is present.

For an anchor document `i` present before batch `t`, let `N_k^t(i)` be its k-nearest-neighbor set after the batch. Define

`churn_t(i) = 1 - |N_k^{t-1}(i) ∩ N_k^t(i)| / k`.

If `b` documents are added to a previous prefix of size `n`, exchangeability implies that the expected fraction of the new top-k set occupied by the arriving batch is

`b / (n - 1 + b)`.

Define the **mass-normalized churn hazard**

`H_m(t) = mean_i churn_t^m(i) / [b / (n - 1 + b)]`.

Under ideal exchangeable insertion, the expectation is approximately 1. This removes the trivial decline in raw churn as the corpus grows.

The primary cross-observer statistic is

`D = mean_t |H_reference(t) - H_transfer(t)|`.

The empirical p-value is the upper-tail rank of chronological `D` among the 128 exchangeable permutations, with the usual +1 correction.

## Regions and resolution

The baseline SRF/Quasar alignment is used only to define a shared descriptive partition, not to choose outcomes. Fit the existing baseline alignment on the frozen 80-document calibration split; map all documents into canonical vectors; L2-normalize the midpoint of the paired canonical vectors; then run deterministic spherical k-means with 6 regions.

Region labels are frozen on the final corpus and reused throughout insertion replay.

For each region and step, report mass-normalized churn. The secondary regional divergence statistic is the mean absolute observer difference over all region-by-step cells.

For anchors present at `n_0`, define **resolution mass** as the number (and final-corpus fraction) of added documents until the anchor's kNN set changes for the first time. Anchors that never change are right-censored. Report global and region-level medians plus censoring fractions.

## Gap mechanism

Before each insertion batch, record for every existing anchor:

- the top-1 gap `s_(1) - s_(2)`;
- the k-boundary gap `s_(k) - s_(k+1)`.

The k-boundary gap is the mechanically relevant margin for kNN-set stability. Compare churn probability in the lowest versus highest quartile of this pre-insertion boundary gap. The expected signature is higher churn in the low-gap quartile.

This is a mechanism check, not the primary significance test.

## Nonstationarity gate

For each insertion step and each observer, compute cosine distance between the arriving-batch centroid and the previous-prefix centroid; average over the two observers and over steps.

Compare the chronological score to the same statistic under the 128 exchangeable permutations.

If `p >= 0.05`, the experiment **fails the nonstationarity gate**. Any observed kNN evolution is interpreted as finite-corpus transient only.

## Hubness controls

Hubness is measured on the final kNN graph through k-occurrence skewness, Robin Hood index, maximum k-occurrence, and anti-hub fraction.

Two correction families are preregistered:

1. **Symmetric CSLS**, neighborhood 10.
2. **Exact empirical Mutual Proximity** on the final cosine-distance matrix.

Both corrections are fit **once on the final frozen corpus and then held fixed during insertion replay**. This prevents the correction's own population statistics from becoming a second moving process.

A control is called effective only if it reduces absolute k-occurrence skewness relative to raw cosine in **both** observers.

DBNorm is deliberately not a primary control in v1. Its published construction assumes distinct query and gallery banks in cross-modal retrieval. Treating one symmetric corpus as both banks would create an unvalidated method adaptation precisely where the experiment is supposed to remove discretionary choices.

## Decision rule

At alpha = 0.05:

1. **Stationary null not rejected:** nonstationarity p >= 0.05. Stop. No corpus-flow interpretation.
2. **Dynamic transfer not rejected:** nonstationarity detected, but raw `D` p >= 0.05.
3. **Model-specific relational dynamics survive hubness controls:** nonstationarity detected, raw `D` p < 0.05, and `D` remains significant under every hubness control that actually reduces hubness in both observers.
4. **Raw divergence is hubness-sensitive:** nonstationarity detected and raw `D` p < 0.05, but at least one effective hubness correction makes `D` non-significant.
5. **Hubness controls ineffective:** raw divergence is significant but neither preregistered correction reduces hubness in both observers; no mechanism claim is allowed.

Sensitivity at `k = 3` and `k = 10` is reported but does not replace the primary `k = 5` decision.

## Static-alignment boundary

The experiment does not choose a new aligner from these outcomes. Existing baseline-alignment diagnostics are reported for context: paired canonical cosine, cross-model self-retrieval, pairwise-cosine correlation, and final native kNN overlap.

A dynamic result cannot repair weak static alignment. Conversely, the exchangeable null preserves whatever static mismatch exists, so a chronological excess in dynamic divergence is not reducible merely to the fact that the two final kNN graphs differ.

## Falsification value

All three substantive outcomes are useful:

- transfer survives: model-specific relational dynamics is not detected at this scale/order;
- divergence survives hubness correction: a genuine candidate mechanism enters the Semantic Atlas program;
- divergence disappears after effective correction: the apparent observer-specific dynamics was largely hubness emergence.

The encoders remain frozen throughout. **Positions do not move; induced relations do.**
