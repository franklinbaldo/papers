---
type: "Protocol"
title: "Pontifex Banking77 fine-grained classification transport"
description: "Prospective external fine-grained classification replication of MiniLM→BGE-small transport after the negative AG News result, with frozen unlabeled correspondence budgets, fixed B head, strong information-matched baselines, and canonical test accuracy."
timestamp: 2026-09-19T15:38:00-04:00
tags: [pontifex, banking77, classification, cross-model-transfer, sample-efficiency, leakage-audit, replication]
---

# Question

Does low-budget unlabeled A→B transport recover useful downstream structure on a recognized **fine-grained** semantic classification task when the encoder pair is held fixed from the already-run AG News experiment?

This is a prospective cross-task replication, not a rescue of AG News. AG News remains a negative result under its frozen criterion. Banking77 is added because its 77 intent classes impose a finer semantic partition than four-class news topic classification while preserving the same single-item architecture and avoiding the two-tower query/document gauge confound. The encoder pair is not changed after looking at Banking77 test results.

# External task

- dataset: Hugging Face `PolyAI/banking77`, revision resolved and recorded before loading;
- official splits: canonical train and test;
- primary metric: **accuracy** on the full canonical test split;
- secondary metric: macro-F1;
- original 77 intent labels; no relabeling and no custom target;
- downstream head: multinomial logistic regression selected only on train-derived head validation.

# Spaces

A: `sentence-transformers/all-MiniLM-L6-v2`.

B: `BAAI/bge-small-en-v1.5`.

These are deliberately identical to the AG News pair. A↔B pretraining overlap is `pretraining_overlap_possible`; overlap of either pretraining corpus with Banking77 is `unknown`. Neither is automatically evaluation leakage.

# Frozen information partition

Only Banking77 **train** rows are partitioned. Before labels are inspected for partitioning, train row IDs are ordered by SHA-256 of `pontifex-banking77-v1\0<train-index>` and assigned:

- first 2,048 rows: `D_transport`; first 80% (`1,638`) are `D_student`, remaining `410` are `D_transport_val`;
- next 6,500 rows: `D_head_train`;
- next 1,000 rows: `D_head_val`;
- any remaining train rows are unused.

`D_student` and `D_transport_val` labels are never read by the transport code. Head labels may train/select classifiers but never transport maps. Canonical test labels are not materialized until every transport, hyperparameter, classifier, and test prediction is frozen.

# Transport budgets

K ∈ {16, 32, 64, 128, 256, 512, 1024}, always prefixes of the frozen `D_student` order.

Every K records shared text bytes, paired float32 representation bytes, fitted/stored floats, fit/selection time, full-test map+predict time, approximate mapping FLOPs/item, and utility delta per probe/parameter/supervision byte/fit second.

# Fixed downstream heads

Using only `D_head_train`/`D_head_val`:

- A-only head is trained/selected on A coordinates;
- B-oracle head is trained/selected on B coordinates.

The B head is then frozen and reused unchanged for **every** A→B transport. No transport receives a task-specific downstream retraining advantage.

# Budget-matched methods

Every method sees exactly the same K A↔B pairs and the same `D_transport_val` B coordinates for label-free hyperparameter selection:

- Orthogonal Procrustes;
- identified-subspace RankProcrustes;
- Ridge linear map;
- CCA;
- PLS;
- RFF + Ridge;
- one-hidden-layer MLP regression, capacity constrained;
- Pontifex = Procrustes coarse map + local residual interpolation;
- RankPontifex = RankProcrustes coarse map + the same local residual interpolation;
- shuffled-correspondence Pontifex with a deterministic derangement and identical validation grid.

The rank controls remain prospectively included because K<d leaves full Procrustes directions underidentified; this lesson was established before Banking77 test evaluation.

Mean/convex fusion with true B at inference is not information-matched and is excluded from the primary frontier. B-oracle is the explicit ceiling.

# Hyperparameter boundary

Everything freezes from train-derived data:

- logistic C on `D_head_val` accuracy;
- Ridge alpha on `D_transport_val` B-coordinate cosine loss;
- CCA/PLS component count on the same coordinate loss;
- RFF gamma/width/Ridge alpha on the same coordinate loss;
- MLP width/alpha on the same coordinate loss;
- Pontifex and RankPontifex tau/lambda on the same coordinate loss;
- shuffled Pontifex uses the same grid and rule.

No canonical test metric can influence these choices.

# Metrics and decision rules

Primary downstream metric: accuracy. Geometry recovery is diagnostic only.

If `B-oracle > A-only`:

`fraction_of_B_utility_recovered = (accuracy(transport)-accuracy(A-only)) / (accuracy(B-oracle)-accuracy(A-only))`.

Freeze 50% and 90% A→B quality targets and report the minimum K each method needs to reach each. If B does not beat A, these quantities are marked not applicable rather than redefined.

Secondary geometry diagnostics on `D_transport_val`:

- mean cosine to true B coordinate;
- neighbor-overlap@10 between transported and true-B validation geometry.

# Leakage audit PASS

PASS requires:

- dataset/model revisions, seeds, ordered pool hashes, text hashes, and every K-prefix hash recorded;
- train transport/head pools mutually disjoint by canonical row ID and separate from canonical test;
- zero task labels used for transport fit/selection;
- no test label, prediction, score, statistic, or target-derived information used before prediction freeze;
- true B test coordinates used only by B-oracle inference and never transport selection;
- shuffled correspondence information-matched;
- pretraining overlap recorded separately from evaluation leakage.

Any violation changes the findings audit to WARN/FAIL and blocks a confirmatory claim.

# Success / failure boundary

Strong support requires a real low-budget regime where Pontifex materially recovers the B-over-A gap while beating information-matched simple/capacity-matched transports at the same K, or reaches the same frozen quality target with less supervision/parameters/compute.

Evidence against practical advantage includes: remaining below A-only; failing frozen targets; being matched or beaten by shuffled correspondence; or losing to a simpler baseline such as Ridge/Procrustes under equal information.

This benchmark cannot change the interpretation of the already-observed AG News result. It is an independent cross-task replication for the same encoder pair.
