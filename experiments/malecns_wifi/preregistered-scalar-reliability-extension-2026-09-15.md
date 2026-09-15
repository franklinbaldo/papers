# Preregistered extension — scalar reliability peer coupling

Date: 2026-09-15

This extends the reliability-weighted peer-coupling replication from PR #453 without changing the scientific mechanism.

## Fixed mechanism

- six semantic channels: MiniLM/E5 × scales 8/32/128;
- one independent trainable adapter/flavour per channel;
- scalar per-channel reliability estimated from training bytes only before learning;
- reliability-weighted leave-one-channel-out peer teacher;
- `peer_lambda = 0.50`;
- teacher remains `0.65 * ground_truth + 0.35 * peer`;
- no inference-time attention/router;
- MaleCNS remains the multimodal integrator;
- frozen semantic encoder outputs may be served from a provenance-checked cache, but cache use must not change channel values or downstream training logic.

## New seeds

`20260920, 20260921, 20260922, 20260923, 20260924, 20260925`

For each seed, compare only:

1. independent (`peer_lambda = 0`)
2. scalar reliability-weighted coupling (`peer_lambda = 0.50`)

Equal-weight and directed sender→receiver arms are excluded from this extension.

## Primary metric

Final `all_direct / unseen_generalization` AUPRC.

## Support rule

The scalar-reliability mechanism is supported in this extension if all of the following hold:

- scalar unseen > independent unseen on at least 4 of 6 seeds;
- mean `(scalar_unseen - independent_unseen) >= +0.05`;
- mean `(scalar_all - independent_all) >= -0.02`.

No gate changes after observing outcomes.

## Passive longitudinal logging

The run may record sender/receiver diagnostic observations (per-channel probabilities, targets, errors, epoch/seed/context identifiers, and related derived diagnostics) provided that these diagnostics do not affect training, arm assignment, stopping, seeds, or preregistered adjudication.

These logs are exploratory longitudinal data for future analysis of directional teaching relationships, not evidence for the present support rule.
