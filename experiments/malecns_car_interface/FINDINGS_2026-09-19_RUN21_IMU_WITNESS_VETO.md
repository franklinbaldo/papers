---
type: "Findings Record"
title: "MaleCNS Car Interface Run 21: independent OBD witness veto for clock repair"
description: "An OBD speed-delta contradiction score can veto some false GNSS clock repairs caused by a corrupted phone-IMU witness, reducing clean-clock harm at the cost of slightly weaker correction recall when a real offset is present."
tags: [malecns, driving, obd-ii, gnss, android, imu, sensor-fusion, timebase, clock-offset, robustness, experiment]
timestamp: 2026-09-19T13:57:00-04:00
---

# Run 21 — do not let one bad witness repair the clock alone

Run 20 showed that phone-IMU kinematics can estimate a persistent GNSS timestamp offset, but it also left a sharp falsifier: the IMU itself can be wrong because of mounting projection, gravity leakage, thermal/constant bias, clipping, or sensor-pipeline artifacts. Run 21 keeps the Run-20 IMU estimator as the proposer and adds an independent, nearly-free OBD-II speed-delta witness as a **veto**, not as a second mandatory proof.

For each candidate offset proposed by the IMU path, the new guard compares GNSS delta-speed with the OBD speed delta over that same shifted interval. If applying the proposed shift makes GNSS/OBD consistency more than 8% worse than leaving the reported clock untouched, the repair is vetoed. Static OBD speed bias largely cancels in a delta, so this witness can remain informative even when absolute OBD speed is biased.

## Reality boundary

The deployable estimator sees only already-observed GNSS speed values and reported timestamps, phone longitudinal IMU samples, OBD-II speed history, and the current arrival boundary. It never receives the actual GNSS measurement time, injected fault mode, true vehicle speed, simulator pose, map state, or future sample. Candidate intervals ending after the current arrival are structurally ineligible.

The synthetic harness retains actual measurement time and true speed **only for scoring** timestamp error and matched-reference error. Those fields are not passed to either estimator.

## Executed validation

The exact staged code was executed with:

- 3 seeds;
- 12 episodes per seed;
- 250 steps per episode at 10 Hz;
- 45 conditions = OBD `clean/static/drift` × GNSS clock `clean/+0.3 s offset/+0.3 s offset with ±0.2 s jitter` × IMU `clean/bias/axis-scale/gravity-leak/clipping`;
- 1,620 episodes and 405,000 simulated control-time steps in total;
- GNSS at 2 Hz, 15% dropout, and 0.4–1.2 s arrival delay.

The IMU stressors were fixed before the final run: ±0.60 m/s² additional constant bias, scale factor 0.65 or 1.35, sinusoidal gravity leakage amplitude 0.80 m/s², and clipping at ±0.80 m/s².

`python -m unittest -v test_clock_offset_witness_veto.py` → **3/3 passed**.

`python -m py_compile clock_offset_witness_veto.py obd_gnss_clock_witness_corruption_ablation.py test_clock_offset_witness_veto.py` → **passed**.

### Clean OBD, clean GNSS clock: safety against false repair

| IMU mode | IMU-only matched-reference MAE | + OBD witness veto | delta |
|---|---:|---:|---:|
| clean | 0.157606 | **0.152243** | **3.40% better** |
| constant bias | 0.177009 | **0.169663** | **4.15% better** |
| axis scale | 0.158402 | **0.156672** | **1.09% better** |
| gravity leakage | 0.174699 | **0.162076** | **7.23% better** |
| clipping | 0.170520 | **0.150588** | **11.69% better** |

Across the five IMU regimes, clean-clock matched-reference MAE fell from `0.167647` to **`0.158248`** (**5.61% better**). The fraction of GNSS updates on which a clock repair was active fell from about **12.29% to 8.62%**. Average absolute timestamp error fell from **0.361 to 0.239 steps**.

This is the behavior the guard was intended to produce: when there is no clock offset, an independent witness suppresses some false repairs, especially when the IMU is clipped or contaminated by gravity leakage.

### Clean OBD, real +0.3 s clock offset: the price of caution

The guard is not free. Averaged over the same five IMU regimes, matched-reference MAE with a real fixed offset rose from `0.269960` to `0.274925` (**1.84% worse**) and repair activity fell from **58.90% to 55.29%**. Under offset+jitter the corresponding penalty was **1.13%** (`0.307471 → 0.310932`).

The penalty was modest for constant IMU bias (+0.80%) and essentially neutral under clipping (-0.20%), but larger for clean IMU (+3.93%) and axis-scale stress (+2.82%). The independent OBD witness sometimes vetoes a true repair because finite noisy speed deltas can temporarily prefer the unshifted alignment.

### Drifting OBD

The same trade-off survived when OBD had slow bias drift. Averaged across IMU regimes:

- clean GNSS clock: `0.298882 → 0.290977` (**2.64% better**);
- fixed +0.3 s offset: `0.369815 → 0.374369` (**1.23% worse**);
- offset+jitter: `0.412165 → 0.415226` (**0.74% worse**).

With static OBD bias the guard was nearly neutral in aggregate because absolute reference error was dominated by the injected OBD bias; this is consistent with using OBD **delta** only as a timing witness rather than treating it as ground truth speed.

## Interpretation

This run falsifies the tempting rule “if the IMU clock estimator has enough internal evidence, repair the timestamp.” A physically available second witness can catch some wrong repairs. It also shows why requiring full multi-sensor consensus would be too conservative: the veto improves the no-offset safety case but slightly reduces recall on genuine offsets.

That creates a much cleaner decision problem for MaleCNS. The deterministic interface can expose **witness conflict** rather than hiding it. When the IMU proposes a repair and OBD strongly contradicts it, an active controller can decide whether the expected value of more information justifies the cost of another observation: request another GNSS fix, run camera ego-motion, inspect Android rotation/gravity quality, or activate another physically declared witness. MaleCNS should compete here against ordinary active-sensing policies, not get credit for basic timestamp arithmetic.

## Candidate channel record

| signal | cost | expected rate/latency | real-car availability | simulator/mock method | privacy/safety | ablation |
|---|---|---|---|---|---|---|
| OBD support for proposed clock repair | ~13 candidate offsets × <=40 recent pairs; no new sensor | GNSS-fix rate after warm-up | yes, standard OBD speed + phone GNSS | inject clock fault while independently perturbing OBD/IMU | derived scalar; no raw location needs to leave device | IMU-only repair vs OBD-veto guard with identical observations |
| clock-witness conflict / veto flag | one bit after the same calculation | GNSS-fix rate | yes | independently corrupt IMU, OBD, or both | should trigger conservative information gathering, not direct steering | expose flag to active controller vs hide it |
| reference candidate offset | negligible after scoring | GNSS-fix rate | yes | same | diagnostic only; do not treat OBD as privileged truth | compare value of scalar vs binary conflict flag |

A third independent witness is the natural next curriculum stage. Camera ego-motion is particularly attractive because it is already available from the Android camera and can be computed locally; active ultrasonic/LiDAR signals are more useful for scene geometry than speed-clock alignment but can become independent timing witnesses when pulse/scan times and ego-motion are jointly observed.

## Cache/dependency accounting

No CARLA bundle, dataset, model, Python package, simulator asset, or external weight was downloaded. **No heavyweight cache miss occurred.** The run used only the Python standard library plus already committed experiment logic.

The repository already contains the dedicated 2026-09-19 MaleCNS embodied-control prior-art pass and the autonomous-driving dataset/benchmark/safety review in `RESEARCH_2026-09-19.md`, including the explicit distinction between genuine MaleCNS/connectome-derived control and generic insect-inspired robotics. This run therefore did not duplicate the calendar-day research pass.

## Limits and next falsification

1. The OBD witness is not independent under every fault. Common-mode timing errors or software pipelines that shift OBD and GNSS together can defeat the veto.
2. The guard uses a fixed 8% contradiction threshold chosen as a conservative analogue of the existing Run-20 activation margin; it has not been optimized on an independent calibration set.
3. The experiment remains discrete-step synthetic. Continuous monotonic timestamps, interpolation, and joint offset+drift estimation remain required.
4. The largest immediate adversary is **common-mode failure**: make OBD and GNSS agree while both are wrong, then measure how much a truly independent third witness (camera ego-motion or another declared sensor) is worth.
5. The first checksum-pinned synchronized real OBD/GNSS or camera/IMU slice remains required before any road-data performance claim.
