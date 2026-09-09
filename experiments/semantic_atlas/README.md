---
type: "Companion Note"
title: "Semantic Atlas Toy Experiments"
description: "Map of the falsifiable toy harnesses supporting semantic_atlas.md, and of the boundary between the cheap synthetic test layer and anything run against a real model."
tags: [semantic-atlas, experiment, preregistration, toy-harness]
timestamp: 2026-09-08T21:35:00-04:00
---

# Semantic Atlas toy experiments

This directory contains the falsifiable toy harnesses for `semantic_atlas.md` and its follow-up papers.

## Cheap test layer

The default unit suite intentionally requires no model download:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
pytest -q
```

It covers the deterministic geometry/control primitives. In particular, Experiment A tests **held-out canonical coordinate agreement** under paired calibration and must fail under shuffled correspondences; preserving pairwise distances alone is not considered an SRF success.

The DQRF/DGCT tests cover frozen field fingerprints, bounded vortical and control fields, the decomposition

\[
F_M(q)=a_M(q)\mathcal V_Q(q)+r_M(q),
\]

residual energy/effective-rank measurements, and paired cross-model concordance. Synthetic tests verify that a correctly specified frozen gauge exposes a deliberately planted low-complexity residual better than a mismatched field.

## Model-backed layer

Install the optional model dependencies only for registered runs:

```bash
pip install -e '.[dev,models]'
```

Model-backed runs must pin model/tokenizer revisions and persist a result manifest before aggregate outcomes are inspected. GPU-backed experiments are not part of the cheap CI gate and must not be reported as executed until their artifacts exist.

### Dynamic Gauge Compression Test v1

DGCT-v1 is preregistered in:

- `protocol_dynamic_gauge_compression_v1.md` — scientific contract;
- `dynamic_gauge_compression_v1.json` — frozen executable parameters.

Run it with:

```bash
python scripts/run_dynamic_gauge_compression.py
```

It generates the continuation corpus once, embeds the same cumulative text states with both pinned observers, aligns them through the existing SRF calibration contract, splits by whole trajectory, and compares raw dynamics with residual dynamics under frozen zero, radial-gradient, smooth-vortex, and random divergence-free gauges.

The output is:

```text
artifacts/dynamic_gauge_compression_v1.json
```

A successful exit is only evidence that the registered measurement ran. The v1 experiment does **not** test a Navier–Stokes-inspired field and cannot by itself establish a vortex-specific result.
