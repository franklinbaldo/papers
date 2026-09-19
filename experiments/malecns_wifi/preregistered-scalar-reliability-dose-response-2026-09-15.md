---
type: "Protocol"
---

# Preregistered experiment — scalar reliability dose response

Date: 2026-09-15

## Question

Does the instability seen at `peer_lambda = 0.50` come from over-coupling rather than from scalar reliability weighting itself?

## Fixed mechanism

- six semantic channels: MiniLM/E5 × scales 8/32/128;
- one independent adapter/flavour per channel;
- scalar reliability estimated from training bytes only before learning;
- reliability-weighted leave-one-channel-out peer teacher;
- teacher: `0.65 * target + 0.35 * peer`;
- no inference-time router/attention;
- frozen semantic fields may be served from the existing provenance-checked cache.

## Seeds

`20260926, 20260927, 20260928, 20260929`

## Arms

For each seed, identical initialization is compared across:

1. independent (`peer_lambda = 0`)
2. scalar reliability `peer_lambda = 0.05`
3. scalar reliability `peer_lambda = 0.10`
4. scalar reliability `peer_lambda = 0.25`
5. scalar reliability `peer_lambda = 0.50`

No directed sender→receiver matrix and no equal-weight arm.

## Primary outputs

For final `all_direct` validation:

- unseen-generalization AUPRC per seed/arm;
- all-example AUPRC per seed/arm;
- per-arm mean delta versus independent;
- per-arm count of seeds with unseen improvement versus independent.

## Selection rule for a follow-up confirmatory arm

An arm is eligible for a future confirmatory replication only if, on these four seeds:

- unseen improves over independent on at least 3/4 seeds;
- mean unseen delta versus independent is at least `+0.05`;
- mean all-example delta versus independent is at least `-0.02`.

If multiple arms qualify, select the one with the largest mean unseen delta; ties are broken by smaller `peer_lambda`.

This experiment maps coupling strength and selects a candidate for a subsequent fresh-seed confirmation. The four-seed mapping itself is not Stage A/B confirmatory evidence.
