---
type: "Protocol"
title: "Pontifex AG News single-item cross-model transport"
description: "Prospective external classification benchmark for low-budget A→B semantic transport with disjoint unlabeled correspondence and labeled-head pools, frozen before official test scoring."
tags: [pontifex, ag-news, classification, cross-model-transfer, sample-efficiency, leakage-audit]
---

# Question

Can a small unlabeled correspondence budget recover downstream utility already present in a stronger semantic space B when a single A→B map is applied to every item, without the query/document gauge ambiguity found in two-tower retrieval?

This benchmark is a new task after negative MS MARCO transport evidence because single-item classification removes a concrete architectural confound rather than changing the success criterion. Every baseline receives the same restriction.

# External task

- dataset: Hugging Face `fancyzhx/ag_news`, revision pinned at run time from dataset metadata before loading;
- official splits: canonical train and test;
- primary metric: accuracy on the full canonical test split;
- secondary metric: macro-F1;
- four canonical AG News classes; no relabeling or custom target;
- classification head: multinomial logistic regression.

# Spaces

A: `sentence-transformers/all-MiniLM-L6-v2`.

B: `BAAI/bge-small-en-v1.5`.

Both model revisions are resolved and pinned before encoding. A↔B pretraining overlap is `pretraining_overlap_possible`; overlap of either pretraining corpus with AG News is `unknown`. Neither is classified as evaluation leakage.

# Frozen information partition

Only the canonical AG News train split is partitioned. Rows are ordered by SHA-256 of `pontifex-agnews-v1\0<train-index>` and assigned without consulting labels:

- first 4,096 rows: `D_transport`; first 80% become `D_student`, remainder `D_transport_val`;
- next 12,000 rows: `D_head_train`;
- next 3,000 rows: `D_head_val`;
- all remaining train rows are unused.

`D_student`/`D_transport_val` labels are never read by the transport code. `D_head_train`/`D_head_val` labels may train/select downstream heads but never transport maps. The full canonical test split is used only after every map, hyperparameter, and classifier is frozen.

No test text, label, prediction, metric, statistic, or test-derived choice enters map/head fitting or selection. Test embeddings are inference-time inputs only.

# Transport budget

K ∈ {16, 32, 64, 128, 256, 512, 1024} shared unlabeled A↔B observations, always the first K items in the frozen `D_student` order.

For every K record:

- shared text bytes;
- paired float32 representation bytes;
- fitted/stored float count;
- fit+validation-selection time;
- test mapping and prediction time;
- approximate mapping FLOPs/item;
- utility recovered per probe, fitted float, supervision byte, and fit second.

# Downstream heads

Two fixed-label-budget references are selected using only `D_head_train` and `D_head_val`:

- `A-only`: logistic classifier trained on A coordinates;
- `B-oracle`: logistic classifier trained on B coordinates.

The B head is frozen once and reused unchanged for every A→B transport. Therefore transport methods cannot compensate for a poor map by retraining the downstream classifier.

# Budget-matched transports

All transport methods see the exact same K A↔B pairs and the same `D_transport_val` coordinate targets for unsupervised hyperparameter selection:

- Orthogonal Procrustes;
- Ridge linear map;
- CCA;
- PLS;
- RFF + Ridge;
- capacity-matched one-hidden-layer MLP regression;
- Pontifex = Procrustes coarse map + local residual interpolation;
- shuffled-correspondence Pontifex with a deterministic derangement and the same validation procedure.

No task label is used to fit or select any transport.

Mean/convex fusion of true A and B test embeddings is not budget-matched because it requires B at inference; it is therefore excluded from the primary frontier rather than given extra information. `B-oracle` already supplies the allowed ceiling reference.

# Hyperparameter boundary

All choices freeze on train-derived validation data:

- logistic C on `D_head_val` accuracy, tie-broken deterministically;
- Ridge alpha on `D_transport_val` B-coordinate cosine loss;
- CCA/PLS component count on the same coordinate loss;
- RFF gamma/width/Ridge alpha on the same coordinate loss;
- MLP width/alpha on the same coordinate loss;
- Pontifex tau/lambda on the same coordinate loss;
- shuffled Pontifex receives the identical grid and selection rule.

Test accuracy/F1 are computed only after the complete prediction bank is frozen.

# Metrics and decision rules

Primary downstream metric remains accuracy. Geometry recovery is diagnostic only.

When `B-oracle > A-only`:

`fraction_of_B_utility_recovered = (accuracy(transport) - accuracy(A-only)) / (accuracy(B-oracle) - accuracy(A-only))`.

Also freeze targets at 50% and 90% of the A→B accuracy gap and report the minimum K reaching each target. If B does not beat A, fraction recovery and those targets are marked not applicable rather than redefined.

Geometry diagnostics on held-out `D_transport_val`:

- mean cosine to true B coordinate;
- 10-neighbor overlap between transported and true-B held-out geometry.

# Leakage audit PASS

PASS requires all of the following:

- dataset/model revisions, seed, ordered IDs, pool hashes and every K-prefix hash recorded;
- `D_transport`, `D_head_train`, `D_head_val`, and test are disjoint by official row ID;
- zero task labels used by transport fit/selection;
- no test-derived information used before predictions are frozen;
- true B test embeddings used only for the B oracle, post-freeze diagnostics where declared, and never to select a transport;
- shuffled correspondence evaluated at identical K and selection budget;
- pretraining overlap recorded separately from evaluation leakage.

Any violation changes the record to WARN/FAIL and prevents a confirmatory claim.

# Success boundary

Strong support requires a real low-budget regime in which Pontifex either beats information-matched transports at the same K while materially recovering the B gap, or reaches a frozen quality target with fewer pairs/parameters/compute. Beating a generic map only on geometry is insufficient. A result below A-only, a result matched by shuffled correspondence, or a result erased by a simpler capacity-matched baseline is evidence against practical Pontifex advantage for this encoder/task pair.
