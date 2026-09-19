---
type: "Findings Record"
title: "MaleCNS Car Interface Run 15: Matched-time OBD/GNSS calibration"
description: "A reality-bounded asynchronous OBD-II/GNSS subexperiment shows that matching measurements by physical timestamp before learning persistent cross-modal bias is materially safer than comparing a stale GNSS fix with current OBD speed."
tags: [malecns, driving, obd-ii, gnss, android, sensor-fusion, temporal-alignment, calibration, experiment]
timestamp: 2026-09-19T07:56:00-04:00
---

# Run 15 — matched-time OBD/GNSS calibration

## Question

Run 14 made residual scale freshness-aware, but it still left a general temporal-identification problem: **two honest sensors can disagree simply because they refer to different physical times**. A robust kernel can downweight that disagreement, but it cannot recover the information lost by comparing a stale measurement with a current one.

This run therefore advances the OBD-II ↔ Android GNSS channel pair with a small deployable primitive: learn persistent reference-sensor bias only from **matched-time cross-modal residuals**. A later-arriving GNSS fix is paired with the historical OBD sample from the GNSS measurement timestamp, never with the current OBD sample.

The new `PersistentBiasCalibrator` is modality-generic and receives only sensor values plus externally maintained timestamp alignment. It does not accept simulator truth, injected-fault flags, privileged pose, future state, CARLA state, or object truth.

## Concrete implementation

Added:

- `temporal_bias_calibration.py` — clipped EWMA persistent-bias estimator with a persistence gate;
- `obd_gnss_time_alignment_ablation.py` — deterministic standard-library harness;
- `test_temporal_bias_calibration.py` — four invariants for persistence, zero-mean noise, correction direction, and opposite-sign evidence.

Default calibration contract:

- EWMA `alpha = 0.15`;
- innovation clip radius `1.0 m/s`;
- correction deadband `0.35 m/s`;
- evidence residual threshold `0.60 m/s`;
- four persistent same-sign observations before correction is allowed.

These are frozen engineering defaults in this run rather than parameters selected against hidden truth.

## Harness and reality boundary

This is a **synthetic interface validation**, not a real-road result.

Each 25 s episode contains a smoothly changing latent vehicle speed used only to generate observations and calculate final MAE. The deployable algorithms see only:

- OBD speed samples at 10 Hz;
- GNSS speed fixes at 2 Hz;
- each GNSS fix's measurement timestamp;
- arrival time / age;
- historical OBD samples already observed.

GNSS fixes have 0.4–1.2 s effective delay, 15% packet/fix loss, `σ = 0.45 m/s` noise; OBD has `σ = 0.18 m/s` noise. The evaluation compares four bias regimes: clean, static offset, slow drift, and a persistent step change.

The key ablation is not hidden-truth access. It is whether the exact same calibrator updates from:

1. **aligned residual:** `OBD(t_measure) - GNSS(t_measure)`; or
2. **unaligned residual:** `OBD(t_arrival) - GNSS(t_measure)`.

The second arm intentionally reproduces the physically wrong but tempting comparison that conflates sensor disagreement with ordinary vehicle acceleration/deceleration.

## Executed validation

Execution: five independent seeds × 300 episodes per condition × 250 steps per episode. The same generated episode is reused across arms within a comparison.

| condition | OBD only MAE | stale Huber MAE | delta-transport MAE | **matched-time bias calibration MAE** | unaligned calibration MAE |
|---|---:|---:|---:|---:|---:|
| clean | **0.143463** | 0.203328 | 0.185083 | 0.143489 | 0.187025 |
| static OBD offset | 1.496514 | 1.257023 | 1.220802 | **0.427450** | 0.572579 |
| slow OBD drift | 0.383305 | 0.344795 | 0.321005 | **0.318175** | 0.347018 |
| OBD step bias | 1.096244 | 0.966666 | 0.957665 | **0.579356** | 0.589111 |

Seed-to-seed SD for the matched-time calibrator was `0.000382 / 0.004567 / 0.004778 / 0.010533` in clean/static/drift/jump order.

### What changed

Against OBD-only, matched-time calibration was:

- effectively neutral in the clean condition (`+0.018%` MAE, i.e. a tiny degradation);
- **71.44% lower MAE** under a persistent static OBD offset;
- **16.99% lower MAE** under slow drift;
- **47.15% lower MAE** after a persistent OBD bias jump.

Against the identical but temporally wrong unaligned calibrator, matched-time calibration reduced MAE by about **25.35%** under static offset and **8.31%** under drift. In the clean regime the difference is especially diagnostic: the aligned calibrator activated on only about **0.011%** of time steps, while the unaligned version activated on about **7.99%**, creating a large false-correction penalty (`0.187025` vs `0.143489`).

Under abrupt bias jumps the aligned advantage over the unaligned calibrator shrank to about **1.66%**. That is an honest limitation: a persistence-gated estimator necessarily lags a newly appearing offset.

## Interpretation

The useful result is not that this particular five-parameter calibrator is optimal. It is that **timestamp alignment is a first-class sensor-interface primitive**. Robust fusion cannot be asked to solve a temporal mismatch that the interface could have removed deterministically.

For the MaleCNS colony this changes the contract. Before a coordinator sees cross-modal disagreement, the interface should expose both:

- a raw current disagreement signal, when that is behaviorally meaningful; and
- a matched-time disagreement signal, when the modalities estimate the same physical scalar at different latencies.

That distinction helps prevent the colony from learning the false rule “acceleration means one sensor is lying.”

The next MaleCNS-specific use is not to replace this calibrator. It is to consume its lawful outputs as low-cost channels when deciding whether to spend compute or request another observation.

## New derived candidate channels

### Persistent cross-modal bias estimate

- **Signal:** signed `bias_hat` between two sensors after matched-time alignment.
- **Cost:** effectively free once both streams are present; a few scalar operations per corroborating sample.
- **Expected rate/latency:** updates at the slower corroborating modality rate; latency is that modality's arrival delay.
- **Real-car availability:** yes for comparable pairs such as OBD wheel/vehicle speed ↔ phone GNSS speed, camera ego-yaw ↔ IMU yaw, or ultrasonic ↔ LiDAR range trend.
- **Simulator emulation:** inject only sensor-space offset/drift/delay and expose the same timestamps and observed values the physical interface would expose.
- **Privacy/safety:** the scalar bias itself contains no route geometry; raw GNSS location should not be retained when only speed is required.
- **Required ablation:** raw streams vs raw + bias estimate under clean, offset, drift, jump, dropout, and latency shifts.

### Bias-persistence evidence

- **Signal:** small integer/normalized confidence that same-sign matched-time disagreement has persisted long enough to justify correction or re-query.
- **Cost:** free scalar state.
- **Rate:** corroborator arrival rate.
- **Real-car availability:** direct from the same stream pair.
- **Simulator emulation:** identical state machine over simulated sensor outputs only.
- **Privacy/safety:** no additional personal data beyond the underlying sensor pair.
- **Required ablation:** correction with vs without persistence gating; measure clean-regime false activation and fault-regime recovery time.

These are candidates for a future coordinator input, not evidence that MaleCNS itself adds value.

## Validation and cache status

The numerical run and four unit tests were executed locally from the exact standard-library source staged for this change. `pytest` reported `4 passed`. The experiment used no dataset, model weights, CARLA build, simulator assets, Python package download, or other heavyweight dependency, so there was **no heavyweight cache miss**.

The shell cannot resolve `github.com`, so repository writes were made through the GitHub connection rather than a local clone. The committed experiment source is the same source executed locally; the branch itself was not cloned back into the shell after commit.

Today's dedicated prior-art and driving-dataset/safety pass is already recorded in `RESEARCH_2026-09-19.md`. It distinguishes explicit MaleCNS/connectome-derived driving/robotics from generic insect inspiration and classifies PAVE, Waymo, NHTSA, Tesla/public safety evidence, and closed-loop benchmark implications. This run therefore did not duplicate that daily search.

## Next discriminating experiment

Use a small persistent, checksum-pinned **real** synchronized slice and replace synthetic speed with actual observations. The first target remains OBD-II vehicle/wheel speed ↔ Android GNSS speed because this run now supplies the timestamp/bias-calibration interface required to make that comparison meaningful.

On the real slice, freeze:

1. raw OBD-only;
2. Run-14-style age-aware robust fusion;
3. matched-time bias calibration;
4. matched-time calibration + dropout/latency stress;
5. a resource controller that may request/recruit another channel;
6. only then, a frozen MaleCNS coordinator against matched random/rewired/conventional controls.

The agent must never receive dataset future trajectory, simulator pose, map truth, object labels, or any other value unavailable to the declared physical sensor stack.