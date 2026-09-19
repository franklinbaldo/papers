---
type: "Protocol"
title: "Semantic Atlas — Dynamic Gauge Compression Test v1.1"
description: "Observation-only amendment to DGCT v1 after the transfer observer was shown to truncate away the changing continuation."
tags: [semantic-atlas, dqrf, dynamic-gauge, compression, cross-model, preregistration]
timestamp: 2026-09-09T00:05:00-04:00
---

# Semantic Atlas — Dynamic Gauge Compression Test v1.1

DGCT v1 completed successfully as software but is invalid for cross-model inference: the transfer observer (`all-MiniLM-L6-v2`) produced exactly zero transition energy. The generated cumulative states placed a long invariant prompt before the changing continuation, so the short-context observer truncated away the part that changed.

This amendment changes **only observation**. It does not change the generated continuations, field families, field dimensions, field seeds, scales, strengths, trajectory split, amplitude model, ridge values, complexity metrics, sample fractions, or interpretation ladder frozen in `protocol_dynamic_gauge_compression_v1.md` and `dynamic_gauge_compression_v1.json`.

## Frozen observation rule

Before either semantic observer embeds calibration or trajectory states, both receive the exact same deterministic suffix window:

```text
observation(text) = text[-512:]
```

The generator continues to receive the original unmodified prompt. Thus v1.1 changes what the measuring instruments can see, not what trajectory is generated.

The same suffix operation is applied to calibration texts and generated trajectory states so calibration and measurement use the same observation contract.

## Observability validity gate

Before any gauge comparison is interpreted, both observers must exhibit non-degenerate raw dynamics on train and held-out trajectories:

\[
E(F_M)=\mathbb E\|F_M\|_2^2 > 10^{-12}.
\]

If either observer fails this gate, the process must fail rather than emit a green scientific result. This gate is a measurement-validity condition, not a success criterion for DQRF.

## Confirmatory boundary

The v1 result remains archived as **invalid/inconclusive**, not negative and not positive. v1.1 is the first run eligible to test the original cross-model DGCT claim after restoring observability.

No v1 result was used to alter the frozen candidate fields. In particular, the weak v1 reference-observer numbers do not authorize retuning `vortex_smooth` or any control before v1.1.

Expected command:

```bash
python scripts/run_dynamic_gauge_compression_v1_1.py
```

Expected artifact:

```text
artifacts/dynamic_gauge_compression_v1_1.json
```
