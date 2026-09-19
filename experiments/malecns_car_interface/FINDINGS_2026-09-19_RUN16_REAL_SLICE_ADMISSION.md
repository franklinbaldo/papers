---
type: "Findings Record"
title: "MaleCNS Car Interface Run 16: real-slice timebase admission gate"
description: "Before treating a public OBD-II/GNSS dataset as a real matched-time experiment, a lightweight admission gate now verifies that paired channels and timestamp resolution survive preprocessing; a public LEVIN derivative fails because timestamps were quantized to minutes, while a three-row second-resolution fixture passes the interface gate but is far too small for benchmark evidence."
tags: [malecns, driving, obd-ii, gnss, android, sensor-fusion, real-data, dataset-admission, temporal-alignment, caching, experiment]
timestamp: 2026-09-19T08:56:00-04:00
---

# Run 16 — admit the timebase before admitting the dataset

## Question

Run 15 established that matched-time cross-modal calibration is materially safer than comparing a delayed GNSS observation with the current OBD-II sample. The immediate temptation is to take any public file containing both `gps_speed` and `speed` and call the next run a real-data validation.

That is not sufficient. A downstream CSV can preserve both scalar columns while silently destroying the physical timebase that makes the Run-15 identification possible. This run therefore adds an **offline source-admission gate** before any external slice is allowed into a matched-time experiment.

The gate is reality-bounded by construction. It inspects only recorded timestamps and recorded channel values. It does not use simulator truth, future trajectory, fault labels, perfect pose, map/object truth, CARLA state, or any quantity unavailable in the declared physical interface.

## Concrete implementation

Added:

- `sensor_slice_admission.py` — standard-library admission primitive for paired scalar streams;
- `real_slice_admission_probe.py` — a pinned two-source compatibility probe over public LEVIN-schema material;
- `test_sensor_slice_admission.py` — four deterministic unit tests.

For a candidate pair the gate records:

- row count and number of unique timestamps;
- inferred timestamp quantum from the GCD of positive unique timestamp deltas;
- duplicate-timestamp fraction;
- finite paired-channel coverage;
- median absolute cross-channel delta as a descriptive quantity only;
- separate `interface_compatible` and `benchmark_ready` decisions.

The Run-16 contract for the OBD/GNSS pair requires timestamp quantum `<= 1 s`, at least three unique timestamps, at least 95% finite paired observations, and at least 100 rows before a slice may be called benchmark-ready. These are interface/admission requirements, not parameters tuned against hidden truth.

The module also supplies `sha256_file()` and a revision/content keyed `cache_key()`. The intended persistent layout for future heavyweight source material is conceptually:

`~/.cache/malecns-car/<source>/<revision-or-content-key>/...`

so the same bytes are reused across experiments rather than reacquired each round.

## Source audit

### Original LEVIN source

The upstream `YunSolutions/levin-openData` repository describes roughly four months of data from about 30 four-wheelers, with OBD sampled at 1 Hz and accelerometer data at 25 Hz. Its documented schema contains both GPS speed (`gps_speed`) and OBD speed (`speed`), and its `DataDescription` says the timestamp represents the second in which data was collected. The README states that the dataset is licensed CC BY-NC-SA; the repository metadata's MIT license should therefore not be assumed to override the README's data-license statement.

Pinned source pages used in this run:

- `https://github.com/YunSolutions/levin-openData/blob/master/README.md`
- `https://github.com/YunSolutions/levin-openData/blob/master/DataDescription`

The full upstream data are linked through external Mega/Google Drive locations. They were **not downloaded in this run**.

### Public derivative with both speed channels

A public derivative at:

`mukul-bhele/vehicletelematics@508333cf545f531e9a0dbdcf561f50114bd8ef16`

contains `Dataset/Complete Dataset (After Analysis).csv`, blob:

`104c5cfb239875bd04fcc8031bdae72bfc2d755b`

with both `gps_speed` and `speed`. The file is only about 35.8 kB and was inspectable through the repository interface. A ten-row head probe revealed a crucial loss: timestamps are rendered only to the minute (`07-12-2017 16:48`, `16:49`, ...), even though the original LEVIN schema documents second-level timestamps.

The same derived representation appears in another public mirror (`sohnakrish/DriveSmart-UBI@13fb8cbedbb13a18c2e4eb81149db00081137906`), so the problem is not merely a display quirk in one GitHub page.

### Tiny second-resolution fixture

A public LEVIN-schema test fixture at:

`AreHumphrey/InsureML@94b204b2dd63e20dec0d9801c4676c59d03ef363`

file `src/data/tests/v2_no_dtc.csv`, blob:

`effa9c8135c53002cb20ea97ce551f38c250ecd5`

preserves three consecutive second-resolution timestamps and both speed channels. It is useful for testing the interface contract but is only three rows, so it is not scientific evidence about road performance and is not admitted as a benchmark.

## Executed validation

The exact staged standard-library implementation was executed locally.

Unit validation:

`python -m unittest -v test_sensor_slice_admission.py`

Result: **4 tests passed** in approximately 0.002 s.

The source compatibility probe produced:

| source probe | rows | unique timestamps | inferred quantum | duplicate fraction | paired fraction | median abs(GPS-OBD) | interface-compatible | benchmark-ready |
|---|---:|---:|---:|---:|---:|---:|---|---|
| three-row second-resolution fixture | 3 | 3 | **1 s** | 0.0% | 100% | 1.7052 km/h | **yes** | **no** — only 3 rows |
| ten-row minute-quantized derivative head | 10 | 2 | **60 s** | 80.0% | 100% | 1.0962 km/h | **no** | **no** |

The second row is the important falsification. Its speed values look superficially usable and the cross-channel deltas are not absurd, but the temporal representation is unusable for a matched-time OBD/GNSS experiment. If it had been admitted based only on column names, any calibration result would have mixed lawful vehicle dynamics with unknown within-minute ordering.

## Interpretation

This is a source-quality result, **not a real-road control-performance result**.

The available small public derivative cannot validate Run 15 because minute quantization has removed the temporal information required to decide which OBD observation corresponds to a GPS measurement. The three-row fixture establishes only that second-resolution LEVIN-schema rows exist publicly and that the gate accepts their timebase; it is far too small to estimate error distributions, drift, calibration recovery, or safety outcomes.

The immediate scientific advance is therefore negative but useful: **do not run the real OBD/GNSS ablation on the convenient derivative**. Acquire a full second-resolution source, pin its revision/bytes, cache it once, and only then execute the Run-15 estimator comparison.

This protects the MaleCNS programme from a particularly dangerous failure mode: giving a coordinator an apparently meaningful disagreement channel whose semantics were already corrupted by dataset preprocessing.

## New candidate channel: timebase health

A deployable car can expose the same class of information online as a cheap coordinator channel.

- **Signal:** rolling timestamp quantum, duplicate/quantization rate, measurement-to-arrival age, jitter, and optional drift between a sensor clock and the phone monotonic clock.
- **Cost:** negligible scalar bookkeeping once timestamps are already carried by the interface.
- **Expected rate/latency:** update at each observation; summarize over a rolling window of seconds to minutes.
- **Real-car availability:** yes for Android camera/IMU/GNSS, OBD adapters that preserve receive timestamps, network/RF messages, LiDAR and ultrasonic controllers with host timestamps.
- **Simulator emulation:** quantize, jitter, delay, duplicate or drift only the sensor timestamps before the same interface code sees them; never expose the unperturbed simulator clock to the agent.
- **Privacy/safety:** timestamp-health summaries contain no route geometry; raw GNSS position is unnecessary for speed/timebase health.
- **Required ablation:** with vs without timebase-health inputs under timestamp quantization, clock drift, packet bursts and asynchronous modality delays, measuring false cross-modal fault inference and control degradation.

This is a candidate input to a later resource/active-sensing coordinator. It is not evidence that MaleCNS itself adds value.

## Cache and dependency status

No CARLA build, model weights, simulator assets, Python package, 77.5 MB derivative archive, or full LEVIN dataset was downloaded. In particular, the `Vehicle Telematics (Cleaned using Excel).rar` object exposed by the public derivative is roughly 77.5 MB and was intentionally **not fetched**, because its already-visible derivative timestamp contract was enough to reject that path for Run-15 matched-time validation.

There was therefore no heavyweight cache miss. The only external material inspected was small text/CSV content through the GitHub connection. The local shell still does not need network access for this validation.

## Daily research status

The dedicated 2026-09-19 prior-art pass for explicit MaleCNS/connectome-derived embodied control and the driving-dataset/safety pass are already recorded in `RESEARCH_2026-09-19.md`. This run did not duplicate them. Its source audit is an additional dataset-quality step focused narrowly on the OBD/GNSS transition to real observations.

## Next discriminating experiment

Acquire a full source with both OBD and GNSS speed and **preserved second-or-better measurement timestamps** into a persistent checksum/version-keyed cache. Before any estimator result is reported, run this admission gate and freeze the exact admitted slice.

Then compare on that identical real slice:

1. OBD-only;
2. age-aware robust fusion;
3. matched-time bias calibration;
4. matched-time calibration under replayed dropout/latency stress;
5. a resource controller allowed to request another lawful observation;
6. finally a frozen MaleCNS coordinator against matched random/rewired and conventional controllers.

Until such a slice is admitted, the state of the programme is explicit: the temporal interface is implemented and source compatibility is now testable, but **real-road performance validation remains pending**.
