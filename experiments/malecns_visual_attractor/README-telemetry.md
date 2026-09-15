---
type: "Protocol"
title: "MaleCNS receptor telemetry"
description: "Telemetry contract for receptor-level snapshots in the stationary-screen calibration."
tags: [malecns, drosophila, telemetry, visual]
timestamp: 2026-09-14T21:15:00-04:00
---

# Receptor telemetry

The stationary-screen calibration emits a compact retina snapshot at registered checkpoints. Each snapshot contains:

- one ASCII character per mapped visual receptor;
- a 64-column raster using ` .:-=+*#%@` as intensity levels;
- the current leading transducer candidate;
- instantaneous/cumulative receiver-excitation reward;
- generator body latent and screen parameters;
- top activated receptor body IDs with normalized x/y and optic-column provenance.

The rectangular raster is telemetry only. It preserves all mapped receptors but does not claim a rectangular native retinal topology. Resolved optic-column receptors are ordered by eye/y/x; unresolved receptors are retained deterministically rather than dropped.
