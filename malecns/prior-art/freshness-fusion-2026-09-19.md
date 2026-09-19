---
type: "Audit Report"
title: "MaleCNS freshness-aware fusion — claim-level prior-art audit — 2026-09-19"
description: "Temporal audit of report-age metadata, exponential freshness weighting, age-aware learned fusion, and the RUN4 stale-specialist ablation for the MaleCNS sensor colony."
tags: [malecns, prior-art, sensor-fusion, freshness, latency, age-of-information, citation-debt]
timestamp: 2026-09-19T01:08:00Z
---

# MaleCNS freshness-aware fusion — claim-level prior-art audit — 2026-09-19

> **Status:** claim-specific audit of the freshness addition introduced after the broader sensor-colony and consensus-fusion audits. This record narrows the novelty boundary of [`FINDINGS_2026-09-18_RUN4_FRESHNESS.md`](../../experiments/malecns_car_interface/FINDINGS_2026-09-18_RUN4_FRESHNESS.md). It does not establish exhaustive novelty, patent novelty, copying, causal dependence, or priority beyond the public record and searches described here.

## 1. Claims audited

RUN4 contains several separable propositions:

- **C1 — report age as an explicit lawful coordinator input:** `SpecialistReport.age_ms` exposes acquisition/processing age to the coordinator rather than relying on confidence or consensus alone.
- **C2 — fixed freshness-weighted fusion:** multiply specialist confidence by exponential age decay, `confidence * 2 ** (-age_ms / half_life_ms)`, then compute the weighted mean.
- **C3 — timing dispersion as a compact state signal:** expose `age_spread_ms = max(age) - min(age)` and potentially stale fraction, acquisition-to-inference latency, inter-arrival jitter, and missing-sample duration.
- **C4 — confidence, consensus, and freshness are distinct reliability dimensions:** an internally confident and mutually agreeing group can still be jointly stale.
- **C5 — synthetic RUN4 result:** in the repository's fixed five-specialist simulation, at 40% stale specialists raw confidence weighting produced MAE `0.441725` and the 150 ms half-life freshness baseline `0.107660`, about 75.6% lower error.
- **C6 — learned MaleCNS benchmark hypothesis:** a learned higher-level MaleCNS coordinator should receive compact timing metadata together with value/confidence/novelty/agreement and beat fixed freshness-aware baselines under realistic asynchronous failures.

C5 is an experiment-specific result. It is not a claim that age-aware sensor fusion itself is new.

## 2. Temporal reconstruction

### 2.1 Earliest content-bearing Git commit

The first commit in PR #564 that contains the complete RUN4 findings is:

- commit [`7b205d33314b6aa8855a5bd7e8fa218797cadd86`](https://github.com/franklinbaldo/papers/commit/7b205d33314b6aa8855a5bd7e8fa218797cadd86)
- Git timestamp: **2026-09-19 00:57:27 UTC**
- message: `experiment: record freshness ablation findings`

That commit already states the age-as-input hypothesis, exponential freshness weighting, age spread, the synthetic result, and the learned-coordinator proposal.

### 2.2 Conservatively verified public exposure

GitHub records PR #564 as created at **2026-09-19 00:57:33 UTC**. A Git commit timestamp proves when the object says it was created, but the connector does not expose the exact branch-push instant. For temporal classification this audit therefore uses **2026-09-19 00:57:33 UTC** as the conservative public cutoff while retaining 00:57:27 UTC as the earliest content-bearing Git timestamp.

Every antecedent classified below predates both timestamps by months or years, so this six-second distinction does not affect the ledger.

**Priority confidence:** `1.0` for public availability by PR creation.

## 3. Search protocol

The search decomposed the claim into timing metadata, age/freshness weighting, learned temporal gating, asynchronous multimodal fusion, stale measurements, common-mode stale agreement, and Age-of-Information (AoI). Sources included arXiv, DOI/publisher pages, IEEE-oriented discovery, MDPI/Sensors, autonomous-driving literature, Age-of-Information/distributed-estimation literature, and public GitHub implementations.

Representative queries:

- `"sensor fusion" stale measurements freshness latency weighting`
- `"age-aware" sensor fusion stale measurements`
- `"Age of Information" distributed state estimation sensors stale`
- `"exponential decay" sensor fusion latency confidence`
- `"timestamp offset" sensor fusion staleness autonomous vehicle`
- `"Age-of-Sensing" asynchronous fusion gate`
- `quality freshness reliability sensor fusion GitHub`
- `common-mode stale sensors consensus fusion`
- `learned gate temporal freshness multimodal fusion`

Negative searches for the exact MaleCNS conjunction and for post-cutoff publications are bounded results, not proof of non-existence.

## 4. Pre-cutoff findings

### 4.1 Age-of-Information already makes freshness a first-class estimation variable

**Work:** Aritra Mitra, John A. Richards, Saurabh Bagchi & Shreyas Sundaram, **“Finite-Time Distributed State Estimation over Time-Varying Graphs: Exploiting the Age-of-Information.”** arXiv:1810.06151, first submitted **2018-10-15**.

- Primary source: https://arxiv.org/abs/1810.06151

The paper defines a distributed observer whose `freshness-index` tracks the age of state information diffusing through a sensor network. Nodes use those indices to reject stale information and maintain stable estimation.

**Compared claims:** C1, C3, generic C4.

**Classification:** `prior_art` for the generic proposition that information age/freshness should be represented explicitly and used to suppress stale distributed sensor information; `adjacent_prior_work` for the exact MaleCNS contract.

**Consequence:** “time/freshness belongs in the fusion state” is not a standalone novelty claim.

### 4.2 Zoox 2025 explicitly feeds timestamp offsets into autonomous-driving sensor fusion

**Work:** Meng Fan, Yifan Zuo, Patrick Blaes, Harley Montgomery & Subhasis Das, **“Robust sensor fusion against on-vehicle sensor staleness.”** arXiv:2506.05780, first submitted **2025-06-06 06:18:54 UTC**.

- Primary source: https://arxiv.org/abs/2506.05780

The work identifies varying on-vehicle sensor delays as a deployment failure mode and adds a **per-point timestamp offset feature** for LiDAR and radar relative to camera, giving the fusion network explicit fine-grained temporal awareness. It also trains with realistic staleness augmentation.

**Compared claims:** C1, C3, C6.

**Classification:** `prior_art` for the generic claim that explicit timing metadata should be a model input in autonomous-driving sensor fusion; `partial_prior_art` for C6 because the learned architecture is not a MaleCNS coordinator and does not use the repository's SpecialistReport contract.

### 4.3 AoI-FusionNet 2026 combines age-aware decay with learned modality gating

**Work:** Tehmina Bibi, Anselm Köhler, Jan-Thomas Fischer & Falko Dressler, **“AoI-FusionNet: Age-Aware Tightly Coupled Fusion of UWB-IMU under Sparse Ranging Conditions.”** arXiv:2603.12849, first submitted **2026-03-13 09:50:57 UTC**.

- Primary source: https://arxiv.org/abs/2603.12849

AoI-FusionNet directly combines raw UWB and IMU inputs, contains an **Age-of-Information-aware decay module that reduces the influence of stale UWB measurements**, and uses learned attention gating to balance modalities according to availability and temporal freshness.

**Compared claims:** C1, C2, C6.

**Classification:** `prior_art` for the generic combination `measurement age -> decay stale observations -> learned fusion informed by temporal freshness`; `partial_prior_art` for the exact fixed C2 function and MaleCNS-specific C6.

### 4.4 TA-Fusion 2026 treats Age-of-Sensing as an active learned trust gate

**Work:** **“Time-Aware Graph Neural Network for Asynchronous Multi-Station Integrated Sensing and Communications Fusion in Open RAN.”** *Sensors* 26(8):2376, published **2026-04-12**, DOI 10.3390/s26082376.

- Publisher/DOI: https://doi.org/10.3390/s26082376

The paper defines Age-of-Sensing as a dynamic reliability variable, uses asynchronous telemetry plus AoS metadata at inference time, and introduces a TA-Gate that actively rescales node trust to prioritize fresh reports and suppress stale ones. It also reports a deterministic inverse-AoS weighted fusion baseline before the learned gate.

**Compared claims:** C1, C3, C6.

**Classification:** `prior_art` for explicit sensing-age metadata as an active learned trust/fusion signal; `partial_prior_art` for C6's learned-coordinator design because the substrate and interface differ.

### 4.5 Ananta Meridian publicly implemented quality/confidence × freshness × reliability fusion before RUN4

**Work:** public repository [`saurabh-code-xr/Ananta-Arctic-Sensor-Fusion`](https://github.com/saurabh-code-xr/Ananta-Arctic-Sensor-Fusion), created **2026-04-26**.

The initial public history already describes a core fusion engine with **quality, freshness, and reliability weighting**, accepts per-sensor `latency` as “age of the reading in milliseconds,” includes a `stale_data` scenario, and documents the `confidence_weighted` method as `Quality × freshness × reliability weighting`.

The repository then added continuous freshness functions in commit [`f491e56365c8dbdab9ed1fbeb4aff52ebec3eeeb`](https://github.com/saurabh-code-xr/Ananta-Arctic-Sensor-Fusion/commit/f491e56365c8dbdab9ed1fbeb4aff52ebec3eeeb), dated **2026-04-30 01:27:26 UTC**. Its `freshness.py` implements exponential, linear, and sigmoid decay, including:

`f(t) = exp(-t / tau)`.

Its fusion engine states the effective weight as:

`quality * freshness_factor(latency) * reliability_factor * adversarial_down_weight`.

Our RUN4 baseline uses:

`confidence * 2 ** (-age / half_life)`.

The two freshness terms belong to the same exponential-decay family because `2 ** (-t/h) = exp(-(ln 2)t/h)`; a change of parameterization maps half-life to an exponential time constant.

**Compared claims:** C1, C2, C4.

**Classification:** **`prior_art` for C2's generic method class** `confidence/quality × exponential freshness(age)` in multisensor fusion; `partial_prior_art` for the larger RUN4 architecture because Ananta is not a MaleCNS sensor colony and does not contain the same specialist/coordinator experiment.

**Consequence:** RUN4 must not present exponential age-decayed confidence weighting as a new sensor-fusion algorithm.

### 4.6 Common-mode failure literature already warns that redundant sources can agree and still fail together

Redundancy does not imply independent failure. Safety/reliability literature treats common-cause/common-mode sensor failures as a distinct hazard; for example SAE paper 2014-01-2164 evaluates air-data sensor failure handling under common-mode pitot failures caused by shared environmental conditions.

- SAE: https://saemobilus.sae.org/papers/evaluation-sensor-failure-detection-identification-accommodation-sfdia-performance-following-common-mode-failures-pitot-tubes-2014-01-2164

**Compared claim:** C4.

**Classification:** `adjacent_prior_work`.

**Why:** this does not specifically describe stale shared frames, but it establishes the more general failure of naive consensus under correlated/common-cause failures. RUN4's “several specialists can share the same delayed modality and agree while all are stale” is a concrete instance of that established reliability problem.

## 5. Novelty boundary after the search

### Not defensible as standalone novelty

The following ideas have clear pre-cutoff antecedents:

- representing sensor/report age or timestamp offset explicitly;
- treating age/freshness as a reliability variable in distributed estimation;
- suppressing/downweighting stale measurements;
- learned gating that uses measurement freshness;
- deterministic age-weighted fusion baselines;
- multiplying source quality/confidence by a freshness factor;
- **exponential** decay of sensor trust with measurement age/latency;
- the general warning that redundant sources can fail together under a common cause.

### What remains specific to this repository after the search

No pre-cutoff source was located in the searches above that exactly combines all of the following:

1. redundant specialist reservoirs instantiated from the measured **MaleCNS** fly connectome;
2. the repository's reality-bounded `SpecialistReport` carrying value/confidence/novelty plus `age_ms`;
3. the exact fixed 150 ms half-life baseline within the colony benchmark suite;
4. the exact deterministic RUN4 stale-specialist ablation and numerical results;
5. the planned matched comparison against a learned higher-level MaleCNS coordinator receiving confidence, consensus, novelty, and compact timing signals.

This is a bounded negative search result, **not** a claim that no such antecedent exists.

The scientifically defensible contribution of RUN4 is therefore an **executed MaleCNS-specific architecture diagnostic and benchmark contract**, not the invention of freshness-aware or exponential age-weighted sensor fusion.

## 6. Post-cutoff search

The conservative subject cutoff is **2026-09-19 00:57:33 UTC**. The audit was run immediately afterward. Searches for newly released `freshness-aware sensor fusion`, `stale sensor fusion`, `Age-of-Sensing fusion`, `exponential latency weighting`, and close variants did not locate a materially overlapping work whose first public release was after that cutoff.

**Result:** no candidate is classified as `later_independent`, `later_overlap`, `later_non_citing`, `later_citing`, or `later_derivative` in this round.

The post-cutoff observation window is only minutes long, so this negative result is intentionally weak.

## 7. Classification ledger

| Work | First verified public date | Compared claim | Classification | Material overlap |
|---|---:|---|---|---|
| Mitra et al., AoI distributed estimation | 2018-10-15 | C1/C3/C4 | `prior_art` for generic freshness-state claim | freshness-index tracks age and rejects stale information |
| Zoox, on-vehicle sensor staleness | 2025-06-06 | C1/C3/C6 | `prior_art` generic; `partial_prior_art` MaleCNS conjunction | explicit timestamp-offset feature for AV fusion |
| AoI-FusionNet | 2026-03-13 | C1/C2/C6 | `prior_art` generic; `partial_prior_art` exact conjunction | AoI-aware decay + learned attention gating |
| TA-Fusion | 2026-04-12 | C1/C3/C6 | `prior_art` generic; `partial_prior_art` MaleCNS conjunction | Age-of-Sensing trust gate; age-weighted baseline |
| Ananta Meridian | public repo 2026-04-26; continuous decay commit 2026-04-30 | C1/C2/C4 | `prior_art` for C2 method class | quality/confidence × exponential freshness(latency) × reliability |
| common-mode sensor-failure literature | 2014 and earlier | C4 | `adjacent_prior_work` | redundant sensors can fail coherently under shared cause |

## 8. Revision consequence

RUN4's observed numerical result remains valid as a result of its own deterministic synthetic experiment. The interpretation must be narrowed: **the experiment demonstrates that freshness information is valuable in this MaleCNS colony test regime; it does not establish novelty of freshness-aware weighting itself.**

The strongest correction is C2. A public April 2026 implementation already uses latency/age to compute exponential freshness and multiplies it into source quality/reliability for fusion. AoI-FusionNet and TA-Fusion independently show that temporal freshness can also be fed to learned fusion gates. Those precedents make the planned learned MaleCNS coordinator a comparison of substrates/architectures, not a first proposal to learn from age metadata.

## 9. Schmidhuber Meter readiness

If a materially overlapping work appears later, use:

- `subject_claim`: `MaleCNS colony freshness-aware coordinator signal and benchmark`
- `subject_artifact`: `experiments/malecns_car_interface/FINDINGS_2026-09-18_RUN4_FRESHNESS.md`
- earliest content-bearing Git timestamp: `2026-09-19T00:57:27Z`
- conservative verified public cutoff: `2026-09-19T00:57:33Z`
- `priority_confidence`: `1.0` for public availability by PR creation
- `formula_version`: `0.1`
- `dependency_evidence`: `unknown` unless positive evidence exists

Use the conservative public cutoff for later-work classification unless an earlier branch-push timestamp becomes independently verifiable.
