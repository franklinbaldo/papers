---
type: "Findings Record"
title: "MaleCNS Car Interface Run 22: active tie-break for common-mode OBD/GNSS false consensus"
description: "A persistent camera-vs-OBD/GNSS conflict can trigger an on-demand independent LiDAR ego-speed witness; this sharply reduces common-mode pair error when camera and LiDAR are healthy, while exposing a clear identifiability boundary when auxiliary witnesses are themselves biased."
tags: [malecns, driving, obd-ii, gnss, android, camera, lidar, active-sensing, common-mode, sensor-fusion, robustness, experiment]
timestamp: 2026-09-19T14:58:00-04:00
---

# Run 22 — detect false consensus, then buy one more independent observation

Run 21 showed that one additional witness can veto some false clock repairs, but it left a harder adversary: OBD-II and GNSS can agree with one another while sharing the same wrong speed offset. Agreement is then not evidence of correctness. Run 22 starts *after* deterministic clock repair and matched-time alignment and isolates this common-mode failure.

The new policy does not let a dissenting camera overwrite an agreeing OBD/GNSS pair by itself. It first looks for a persistent observable pattern:

- OBD and GNSS remain mutually close;
- their pair estimate persistently disagrees with phone-camera ego-speed;
- the disagreement keeps the same sign over a short window.

That pattern is treated as **conflict, not diagnosis**. A single dissenting camera cannot identify which side is wrong. Only after persistent conflict does the interface request one more declared sensor: a low-cost LiDAR ego-speed estimate. The LiDAR is used as an independent tie-break. If it clearly supports camera, the estimate becomes the mean of camera+LiDAR; if it supports the OBD/GNSS pair, the pair is retained; if it is ambiguous, the conservative action is to keep the pair.

This is an active-information baseline for a future MaleCNS coordinator. MaleCNS should have to beat this kind of ordinary policy before receiving credit for deciding when another physical observation is worth its cost.

## Reality boundary

The deployable module receives only matched-time values that can exist in an ordinary car with declared sensors:

- OBD-II speed;
- phone GNSS speed;
- Android camera ego-speed;
- optional external LiDAR ego-speed, but only when requested.

The fusion code does **not** receive true vehicle speed, injected fault mode, simulator pose, map state, hidden timestamps, future samples, or a flag saying which sensor is wrong. Synthetic truth and fault labels exist only in the generator/scoring path.

The experiment intentionally assumes the Run-15–21 timebase work has already produced matched-time observations. This run therefore tests common-mode identity rather than timing error.

## Executed validation

The exact staged implementation was executed with:

- 3 seeds;
- 30 episodes per seed per condition;
- 250 matched-time steps per episode at 10 Hz;
- 36 conditions = six OBD/GNSS pair regimes × three camera regimes × two LiDAR regimes;
- 3,240 episodes and 810,000 simulated control-time steps.

Pair regimes:

- clean;
- shared static bias;
- shared drift;
- shared jump halfway through the episode;
- OBD-only static bias;
- GNSS-only static bias.

Camera regimes:

- clean;
- persistent additive bias;
- ±6% scale error.

LiDAR regimes:

- clean;
- persistent additive bias.

Sensor noise used in the frozen harness is 0.18 m/s OBD, 0.45 m/s GNSS, 0.55 m/s camera ego-speed, and 0.35 m/s LiDAR ego-speed. The conflict policy uses an 8-sample window, requires 6 supporting samples, requires OBD/GNSS pair gap <=0.90 m/s, requires pair-vs-camera gap >=0.90 m/s, and uses a 0.15 m/s LiDAR decision margin. These thresholds were chosen heuristically before the final run and were **not** tuned on an independent calibration set.

`python -m unittest -v test_active_common_mode_tiebreak.py` -> **5/5 passed**.

`python -m py_compile active_common_mode_tiebreak.py common_mode_active_witness_ablation.py test_active_common_mode_tiebreak.py` -> **passed**.

The surrounding Python environment emitted an unrelated spreadsheet-runtime warmup traceback on interpreter startup, but both commands returned exit status 0 and the requested tests/compile completed successfully.

## Primary result: healthy camera + healthy on-demand LiDAR

| OBD/GNSS regime | pair-only MAE | naive 3-way mean MAE | active tie-break MAE | improvement vs pair | LiDAR request rate |
|---|---:|---:|---:|---:|---:|
| clean | 0.194364 | 0.195813 | **0.194364** | 0.00% | 0.00% |
| shared static bias | 1.608240 | 1.072308 | **0.572190** | **64.42%** | 78.02% |
| shared drift | 0.927247 | 0.631729 | **0.605991** | **34.65%** | 28.11% |
| shared jump | 0.988142 | 0.689776 | **0.337291** | **65.87%** | 43.65% |
| OBD-only bias | 0.812670 | **0.544205** | 0.812670 | 0.00% | 0.00% |
| GNSS-only bias | 0.783070 | **0.526793** | 0.783070 | 0.00% | 0.00% |

The active policy is deliberately specialized. It does not pretend to solve arbitrary single-sensor faults. When only OBD or only GNSS is biased, their mutual disagreement prevents the common-mode trigger from firing; the ordinary three-way average is better there. Under the intended adversary, however, the on-demand independent witness materially changes the result.

Against the naive always-three-sensor mean, active tie-break is also better in the three common-mode regimes:

- shared static bias: **46.64% lower MAE**;
- shared drift: **4.07% lower MAE**;
- shared jump: **51.10% lower MAE**.

The scoring-only side-selection accuracy on requested events was 93.40% for shared static bias, 91.15% for shared drift, and 95.56% for shared jump. These labels were used only after inference to score whether the physical side selected by the LiDAR was closer to synthetic truth.

## Detection behavior

With a healthy camera:

- clean pair: auxiliary request rate **0.00%**;
- shared static bias: **78.02%** of steps requested LiDAR;
- shared drift: **28.11%** overall; among steps where the shared bias magnitude was >=0.8 m/s, request recall was **48.99%**;
- shared jump: **43.65%** overall; among truly common-mode steps, request recall was **87.27%**;
- false-request rate before the jump was approximately **0.03%**.

So the detector is strong on persistent or abrupt large common-mode errors and weaker on slowly emerging drift. That is exactly the expected boundary of a short persistence window.

## Critical falsifier: the camera can be the liar

The third witness solves **detection of disagreement**, not identifiability. With clean OBD/GNSS but a persistently biased camera, the conflict detector requested LiDAR on **77.44%** of steps. A healthy LiDAR usually sided with the clean pair, so the active MAE was only `0.202737` versus pair-only `0.192639`, but that is still **5.24% worse** than leaving the healthy pair alone. With a ±6% camera scale error, the penalty was **2.67%**.

This is not a bug to hide. It is the central epistemic result of the run: **two agreeing sensors versus one dissenting sensor is not enough to know who is wrong**. The useful object for MaleCNS is therefore not “camera says pair is wrong”; it is “there is unresolved cross-modal conflict and another observation may have value.”

## Second falsifier: the tie-break sensor can also be wrong

With shared static OBD/GNSS bias, healthy camera, but a persistently biased LiDAR:

- pair-only MAE: `1.597399`;
- naive three-way MAE: `1.063958`;
- active tie-break MAE: `1.210898`.

The active policy still improved over the faulty pair by **24.20%**, but it became **13.81% worse** than simply averaging the three primary sensors. Side-selection accuracy fell to about **54.00%**, close to an unreliable tie-break.

Therefore low-cost LiDAR must not be promoted to privileged truth. Its own health, calibration and temporal alignment need to be observable inputs, and a future controller should be allowed to abstain when auxiliary evidence is weak.

## Research interpretation

Run 22 advances the interface from passive robust fusion to a small **value-of-information primitive**:

1. deterministic preprocessing aligns time;
2. primary modalities form a cheap estimate;
3. persistent cross-modal contradiction creates a `common_mode_conflict` signal;
4. the system may pay for one additional independent observation;
5. the new observation arbitrates only when it is sufficiently discriminative.

That is a better target for MaleCNS than basic arithmetic or fixed trust weighting. A MaleCNS coordinator can later receive the same conflict/evidence/cost channels and decide among actions such as:

- request LiDAR ego-motion;
- run a more expensive camera ego-motion model;
- activate ultrasonic/LiDAR scene probes;
- run on-device YOLO;
- query a local LLM transducer for semantic compression;
- ask another vehicle/edge agent for a Wi-Fi/RF token;
- abstain and preserve the conventional estimate.

The matched baseline should remain an ordinary hand-written value-of-information policy like this one.

## Candidate channel records

| signal/action | cost | expected rate/latency | real-car availability | simulator/mock method | privacy/safety | ablation |
|---|---|---|---|---|---|---|
| OBD/GNSS pair-internal gap | negligible | 2–10 Hz after alignment | yes | inject independent vs shared sensor faults | no location needs to leave device | remove pair-gap gate and measure false common-mode alarms |
| camera-vs-pair signed conflict | camera ego-motion already running | 5–30 Hz depending on visual odometry | Android camera | generate independent camera speed/noise/bias | raw images stay local; expose scalar only | hide signed conflict vs expose it to active controller |
| persistent common-mode conflict score | tiny rolling-window arithmetic | same as aligned fusion loop | yes | shared OBD/GNSS bias + camera witness | derived scalar | 1-step threshold vs persistent window |
| LiDAR tie-break request | hardware energy + compute only when triggered | typically 5–10 Hz device dependent | declared low-cost external LiDAR | synthetic independent speed witness with optional bias | active sensor; mounting/eye safety/device rules remain hardware-specific | always-on LiDAR vs conflict-triggered LiDAR vs no LiDAR |
| LiDAR support side / margin | negligible after a requested sample | per requested scan | yes with LiDAR ego-motion implementation | compare LiDAR distance to pair and camera hypotheses | do not treat as truth; health must remain explicit | binary side vs continuous support margin |

## Curriculum consequence

A clean staged curriculum for the active controller is now available:

1. **one signal / one actuator**;
2. deterministic timebase health and clock repair;
3. conventional robust fusion;
4. persistent single-modality fault evidence;
5. false consensus: OBD+GNSS agree while both are wrong;
6. expose camera conflict but do not permit automatic override;
7. permit one costly auxiliary request;
8. add auxiliary-sensor corruption;
9. only then let MaleCNS learn whether/when to buy information.

This makes marginal value measurable at every stage.

## Cache and dependency accounting

No CARLA package, simulator asset, dataset, model, weight, Python dependency, or external sensor artifact was downloaded. **No heavyweight cache miss occurred.** The run uses only Python standard-library code and synthetic/mock sensor backends, so there was nothing new to place in persistent dataset/model caches.

The calendar-day research obligation was already satisfied in `RESEARCH_2026-09-19.md`, which separately records explicit MaleCNS/connectome-derived embodied-control prior art and autonomous-driving dataset/benchmark/safety sources including PAVE, Waymo Safety Impact, NHTSA SGO data, and Tesla reporting. This run did not duplicate that research pass.

## Limits and next falsification

1. Camera and LiDAR ego-speed are synthetic scalar channels, not outputs of a real visual-odometry or LiDAR-odometry stack yet.
2. The common-mode biases are generated directly; no claim is made that their distribution matches a particular real vehicle fault.
3. Thresholds are heuristic and were not calibrated on a held-out set.
4. The current policy requests LiDAR only after primary conflict; latency and energy are represented as request rate, not measured hardware joules or wall-clock milliseconds.
5. A biased camera can cause many requests even when OBD/GNSS are healthy.
6. A biased LiDAR can mis-arbitrate; no auxiliary sensor is privileged truth.
7. The next implementation step should replace at least one synthetic ego-speed witness with a checksum-pinned real or public logged slice, or with a cached camera ego-motion artifact computed from such a slice.
8. A second strong next step is to expose `request_cost`, `conflict_score`, `aux_margin`, and per-channel health to the same ordinary policy and a MaleCNS controller, then compare learned information acquisition against this fixed baseline with equal budgets.
