---
type: "Findings Record"
title: "MaleCNS car interface run 1: modular buses and lawful fusion scalars"
description: "Executed validation of the expanded reality-bounded interface and first cross-sensor scalar channels; this is not yet a driving or CARLA result."
tags: [malecns, findings, sim-to-real, sensors, sensor-fusion, validation]
timestamp: 2026-09-18T17:55:00-04:00
---

# MaleCNS car interface run 1: modular buses and lawful fusion scalars

## Frozen protocol / code under test

This run validates the executable contract in:

- `experiments/malecns_car_interface/interface.py`
- `experiments/malecns_car_interface/signals.py`
- `experiments/malecns_car_interface/test_interface.py`

The governing design note is `experiments/malecns_car_interface/README.md`.

The change closes an implementation gap: the README already described ultrasound/LiDAR, on-device perception, RF/peer communication and semantic transducers, but the executable interface previously exposed only phone, OBD, navigation and bodily-feedback buses.

## What changed

The reality boundary now has explicit optional buses for:

- physical ranging (`range`): ultrasound and declared LiDAR measurements;
- on-device perception (`perception`): YOLO/tiny-model outputs such as counts, confidence, drivable-area fraction, optical flow and visual TTC;
- radio (`radio`): passive RF context and peer-vehicle communication quality;
- semantics (`semantic`): optional local semantic transducers such as hazard score / LLM confidence;
- lawful derived scalars (`derived`).

Phone/OBD fields were extended with signals that a real retrofit can obtain when the device/vehicle exposes them, including GNSS speed, ambient light, steering angle and wheel speeds.

`signals.py` adds four first derived channels, computed only from public real-car-observable inputs:

1. GNSS speed vs OBD speed disagreement;
2. wheel-speed spread;
3. steering-command vs measured-yaw residual using a bicycle-model expectation;
4. GNSS confidence from reported horizontal accuracy.

Missing sensor inputs remain `None`; the implementation does not fill them from simulator truth.

## Execution

Environment: Python 3.13.5.

Command:

```bash
python -m unittest -v test_interface.py
```

The test files were executed from an isolated temporary directory using the exact code committed to the branch in this run.

## Result

**6 tests passed; 0 failures; exit status 0.**

Registered gates:

- PASS — declared modular buses are accepted;
- PASS — exact simulator object distance is rejected as privileged state;
- PASS — simulator lane-center truth is rejected as privileged state;
- PASS — public schema exposes ranging, perception, radio, semantic and derived buses;
- PASS — cross-sensor scalars are computed from lawful phone + OBD inputs;
- PASS — missing sensor values remain missing rather than being silently imputed.

The execution environment emitted an unrelated `artifact_tool` spreadsheet-runtime warmup traceback before the unittest report; the unittest process itself completed successfully with exit status 0 and all six registered tests passing.

## Cache / external assets

This validation required no datasets, model weights, CARLA assets or package downloads beyond the existing Python standard library. Therefore this run had **zero experiment cache misses** and performed no redundant external downloads.

## Interpretation and limits

This is an interface/fusion-contract validation only.

It does **not** establish:

- that MaleCNS can drive a car;
- that any derived scalar improves driving;
- that CARLA integration works;
- that YOLO, ultrasound, LiDAR, RF or a local LLM improves performance;
- any safety claim.

The next useful experiment is an ablation in which a simple closed-loop or recorded-data task receives raw phone/OBD channels with and without these derived disagreement scalars. A positive result would justify exposing the scalars to MaleCNS; a negative result should remove or deprioritize them.
