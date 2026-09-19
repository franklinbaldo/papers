---
type: "Protocol"
---

# Peer reliability replication stack

This branch is stacked on `experiment/malecns-peer-reliability-grid` and implements the preregistered two-new-seed replication of the selected `peer_lambda=0.50` candidate.

Per seed, it compares identical-initialization arms:

- independent;
- unweighted peer coupling at λ=0.50;
- reliability-weighted peer coupling at λ=0.50.

Seeds: 20260916 and 20260917.

The batch emits the preregistered checks directly in JSON; no threshold is chosen after seeing replication results.
