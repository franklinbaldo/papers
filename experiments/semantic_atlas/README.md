---
type: "Companion Note"
title: "Semantic Atlas Toy Experiments"
description: "Map of the falsifiable toy harnesses supporting semantic_atlas.md, and of the boundary between the cheap synthetic test layer and anything run against a real model."
tags: [semantic-atlas, experiment, preregistration, toy-harness]
timestamp: 2026-08-09T00:20:00Z
---

# Semantic Atlas toy experiments

This directory contains the falsifiable toy harnesses for `semantic_atlas.md`.

## Cheap test layer

The default unit suite intentionally requires no model download:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
pytest -q
```

It covers the deterministic geometry/control primitives. In particular, Experiment A tests **held-out canonical coordinate agreement** under paired calibration and must fail under shuffled correspondences; preserving pairwise distances alone is not considered an SRF success.

## Model-backed layer

Install the optional model dependencies only for registered runs:

```bash
pip install -e '.[dev,models]'
```

Model-backed runs must pin model/tokenizer revisions and persist a result manifest before aggregate outcomes are inspected. GPU-backed experiments are not part of the cheap CI gate and must not be reported as executed until their artifacts exist.
