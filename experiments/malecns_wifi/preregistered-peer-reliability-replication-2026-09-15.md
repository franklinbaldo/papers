---
type: "Protocol"
---

# Preregistered replication — reliability-weighted peer coupling

Date: 2026-09-15.

This replication is defined after the exploratory grid selected `peer_lambda=0.50`, but before any replication run is observed.

## Fixed scientific question

Does the strong unseen-generalization improvement observed at `peer_lambda=0.50` replicate on new seeds, and is the improvement specifically attributable to reliability-weighted peer evidence rather than peer coupling alone?

## Frozen architecture

Keep the successful v3 architecture unchanged:

- one independent trainable adapter per `(embedding model, chunk scale)`;
- one local flavour per `(embedding model, chunk scale)`;
- MiniLM and multilingual E5 encoders;
- scales 8, 32, 128;
- frozen MaleCNS reservoir;
- same synthetic train/validation examples and held-out expressions;
- same translator construction and channel-dropout arms;
- same optimizer, epochs, adapter rank/residual scale, taste loss, anchor loss, gain/leak and projections conditional on seed.

## Replication seeds

Use two new seeds only:

- 20260916
- 20260917

The exploratory seed 20260915 is not counted as replication evidence.

## Three arms per seed

All three arms must start from identical initialization within a seed.

1. `independent`: peer_lambda = 0.
2. `unweighted_0.50`: peer_lambda = 0.50 with equal leave-one-channel-out peer weights.
3. `reliability_0.50`: peer_lambda = 0.50 with reliability weights fixed from training bytes only before learning, using the same `exp(-balanced_BCE)` rule as the exploratory grid.

Validation bytes must not affect peer weights.

## Primary metric

Final epoch `all_direct / unseen_generalization` AUPRC.

The replication supports the reliability hypothesis if BOTH new seeds satisfy:

`reliability_0.50 unseen_generalization > independent unseen_generalization`

and the mean improvement across the two new seeds is at least +0.10 AUPRC.

## Global-performance guard

Across the two new seeds, mean final `all_direct / all` AUPRC for `reliability_0.50` must be no more than 0.02 below the mean independent value.

This keeps the original exploratory guard unchanged.

## Mechanism comparison

`reliability_0.50` should also outperform `unweighted_0.50` in mean final `all_direct / unseen_generalization` AUPRC. This comparison tests whether channel reliability, rather than coupling alone, is responsible for the effect.

## Secondary descriptive metrics

Report, but do not use to redefine success after the run:

- `minilm_short_only`, `no_128`, `no_encoder_0`, `no_encoder_1` unseen-generalization AUPRC;
- adapter movement norms;
- flavour cosine to initialization;
- preclip gradient norms;
- fixed reliability weights per seed;
- GPU memory.

Exploratory/replication curriculum evidence only; not Stage A/B confirmatory evidence.
