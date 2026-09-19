---
type: "Findings Record"
title: "MaleCNS Car Interface Run 11: Paid probe-then-trust specialist gating"
description: "Separating specialist activation from admission into fusion improves robustness when probed specialists can be confidently wrong, while showing little or no benefit when specialist fault rates are low."
tags: [malecns, driving, sensor-colony, probe-then-trust, value-of-information, sensor-fusion, robustness, experiment]
timestamp: 2026-09-19T03:53:00-04:00
---

# Run 11 — paid probe-then-trust specialist gating

## Question

Runs 9 and 10 kept two operations coupled: paying compute to activate a specialist and allowing the returned report to affect the fused estimate. Does explicitly separating **probe** from **trust** improve robustness under the same compute budget?

## Implementation advance

`probe_trust.py` adds a reality-bounded trust score for an already-paid-for specialist report. The score uses only:

- the candidate's declared confidence;
- candidate age / freshness;
- agreement with the current fused estimate from already-trusted reports of the candidate modality plus an independent modality.

It does **not** receive hidden truth, a synthetic fault flag, simulator geometry, perfect pose, object truth, or realized future error.

`colony_probe_trust_ablation.py` starts each episode with two trusted camera specialists and two trusted IMU specialists. It then pays for four additional camera reports and four additional IMU reports. Every policy therefore pays for the same eight extra probes and the same 12-specialist compute budget. The comparison differs only in whether every probed report is automatically admitted to fusion.

To make trust failure observable, the harness independently injects a specialist-level fault into a configurable fraction of the eight additional probes. A faulty specialist receives a signed bias of magnitude 0.6–1.4 while reporting confidence 0.95. This fault flag exists only inside the synthetic generator; the gate never receives it. The original camera/IMU burst-noise model remains present as well.

The gate score is:

`declared confidence × temporal freshness × exp(-cross-modal disagreement / 0.35)`

A single scalar admission threshold is calibrated on a disjoint uniform-age synthetic stream. Grid search over 0.00–0.50 in steps of 0.02 selected threshold **0.12** at the default 20% injected specialist-fault probability.

## Executed validation

Calibration:

- calibration episodes per threshold: 12,000;
- threshold candidates: 26;
- calibration stream seed: `2026091901`;
- selected threshold: `0.12`;
- calibration probe-then-trust MAE: `0.106743`;
- calibration acceptance fraction: `0.525240`.

Primary evaluation:

- five independent seeds per camera-age profile;
- 10,000 episodes per seed, 50,000 episodes per profile;
- default injected specialist-fault probability: 20%;
- profiles: uniform, fresh-skewed and stale-skewed camera age;
- paid probes per episode: 8 (4 camera + 4 IMU);
- initial trusted reports: 2 camera + 2 IMU;
- external dependencies in experiment logic: Python standard library plus repository-local modules.

Mean absolute error across five seeds (mean ± sample SD):

| camera-age profile | pilot only (4 specialists) | always trust all paid probes | probe then trust | admission fraction |
|---|---:|---:|---:|---:|
| uniform | 0.123118 ± 0.000509 | 0.109534 ± 0.001040 | **0.107562 ± 0.000732** | 0.5221 ± 0.0020 |
| fresh-skewed | 0.111500 ± 0.000598 | 0.098857 ± 0.000776 | **0.097163 ± 0.000652** | 0.6236 ± 0.0013 |
| stale-skewed | 0.124981 ± 0.000823 | 0.107201 ± 0.000762 | **0.104967 ± 0.000604** | 0.4427 ± 0.0008 |

Relative to automatically trusting every paid probe, probe-then-trust reduced mean MAE by approximately:

- **1.80%** on uniform camera age;
- **1.71%** on fresh-skewed camera age;
- **2.08%** on stale-skewed camera age.

The stale-skew profile admits fewer probes because the lawful freshness term makes old camera reports less likely to enter fusion; the compute was still spent, so this is a trust effect, not a cheaper acquisition policy.

## Fault-rate ablation

The same threshold was then held fixed while the injected high-confidence specialist-fault probability changed on the uniform-age profile. Each row again averages five independent 10,000-episode seeds.

| injected fault probability | always trust MAE | probe-then-trust MAE | relative change vs always trust | admission fraction |
|---:|---:|---:|---:|---:|
| 0% | 0.100749 | 0.100739 | +0.01% | 0.6302 |
| 10% | **0.103698** | 0.103793 | -0.09% | 0.5747 |
| 20% | 0.108934 | **0.106746** | +2.01% | 0.5221 |
| 30% | 0.117287 | **0.111387** | +5.03% | 0.4721 |

Here positive relative change means lower MAE for probe-then-trust. The 0–10% conditions are effectively neutral at this scale and the 10% mean is slightly worse. The benefit appears only as confidently wrong specialist reports become common enough to matter.

## Result

This run supports the architectural distinction proposed after Run 10:

**paying to hear a fly is not the same action as trusting that fly.**

Under a meaningful specialist-level failure rate, the colony can use only lawful properties of an already-observed report to prevent some confidently wrong specialists from entering the actuator-facing estimate. The gain rises with fault prevalence and remains present across camera freshness regimes.

The result is deliberately narrower than “trust gating is always better.” With no injected high-confidence faults, the gate is nearly neutral; at 10% it is slightly worse on the five-seed mean. A production coordinator should therefore learn or adapt the trust policy instead of applying a permanently aggressive filter.

The experiment also clarifies what probe-then-trust does **not** solve. It does not decide which specialist should be activated next: all eight extra probes are still paid for. It therefore isolates trust/admission from acquisition and should be combined later with a lawful acquisition policy rather than conflated with value-of-information.

## Prior-art and falsification boundary

A claim-level audit is recorded in [`audits/prior-art/malecns-probe-trust-2026-09-19.md`](../../audits/prior-art/malecns-probe-trust-2026-09-19.md).

The audit materially narrows the interpretation of this run:

- fault detection/isolation and GNSS RAIM/FDE have separated **measurement availability** from **measurement acceptance/exclusion** for decades, so the generic probe-versus-trust split is established prior art rather than a standalone novelty claim;
- cross-sensor inconsistency/conflict without ground truth is also established; disagreement is useful evidence, but it does not identify which participant is wrong;
- hard exclusion has known missed-detection and **wrong-exclusion** failure modes, so mean MAE alone is not enough for an actuator-facing integrity argument;
- fixed fault thresholds have known sensitivity to system state and noise. The present `0.12` threshold was calibrated under one synthetic generator at 20% high-confidence faults and should be treated as a condition-specific baseline, not a transportable constant;
- simultaneous/correlated faults are a separate isolation problem. Wrong modalities may agree with each other, defeating a simple cross-modal-consensus trust signal;
- abrupt legitimate state changes can also create large disagreement with a stale reference estimate and therefore need explicit recovery/change-point tests.

Accordingly, RUN11's defensible contribution is the **executed MaleCNS-specific matched-compute control result**: under this generator, separating paid acquisition from admission improves mean error once confidently wrong specialist reports are prevalent enough, while the same fixed gate is neutral or slightly harmful at low injected fault rates.

The next learned gate should therefore be compared not only with `always trust` and this fixed gate, but also with an adaptive/statistically calibrated hard gate and a soft robust/reliability-weighted fusion baseline. It should be stress-tested under fault-prevalence/magnitude shift, confidence miscalibration, correlated faults, common upstream bias, asynchronous latency, and abrupt legitimate state transitions. If those simpler robust baselines match a learned gate, the added coordinator complexity has not earned attribution.

## Reality-bound status

Decision-time trust inputs are only reports that have already been physically/digitally acquired: scalar value, declared confidence, timestamp-derived age and cross-modal agreement. In a real ordinary car these can be produced from phone/OBD/declared sensors and specialist processing latency.

Synthetic truth and the injected fault flag are used only by the experiment harness for scoring and stress generation. Neither is visible to `probe_trust_score` or `should_trust_probe`.

The same contract can later be applied to camera/YOLO, IMU, OBD wheel speed, GPS, ultrasonic, low-cost LiDAR, RF/Wi-Fi or local semantic transducers: probe output first, then decide whether it should enter the control fusion path.

## Validation and cache status

The experiment was executed with deterministic repository-local logic and five independent evaluation seeds per condition. `test_probe_trust.py` adds contract checks that stale or cross-modally disagreeing reports score lower, that a paid probe can be rejected, and that the cross-check modality must actually be independent.

No dataset, model weight, CARLA artifact, simulator asset or Python package was downloaded. There was no heavyweight cache miss. Today's repository already contains the dedicated MaleCNS prior-art/falsification audit and the 2026-09-19 driving dataset/benchmark/safety research record, so this run remained focused on the next falsifiable implementation step rather than duplicating those searches.

## Next experiment

The next clean comparison is a **learned trust gate** trained on delayed lawful outcomes, with the fixed gate above retained as a control. Candidate inputs should remain limited to report confidence/freshness, within-modality disagreement, cross-modal consistency, latency/queue health and budget state. The learned gate should be tested under distribution shift in fault rate and under modality-correlated failures before it is replaced by a MaleCNS coordinator.
