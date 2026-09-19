---
type: "Audit Report"
title: "MaleCNS common-mode sensor stall and cross-modal rescue — claim-level prior-art audit — 2026-09-19"
description: "Temporal audit of same-sensor specialist redundancy, physical modality diversity, modality-level summaries, and robust cross-modal coordination in MaleCNS RUN5."
tags: [malecns, prior-art, sensor-fusion, common-mode-failure, redundancy, multimodal, driving, citation-debt]
timestamp: 2026-09-19T02:00:52Z
---

# MaleCNS common-mode sensor stall and cross-modal rescue — claim-level prior-art audit — 2026-09-19

> **Status:** claim-specific audit of RUN5, introduced after the broader sensor-colony, consensus-fusion, and freshness audits. This record narrows the novelty boundary of [`FINDINGS_2026-09-18_RUN5_COMMON_MODE_STALL.md`](../../experiments/malecns_car_interface/FINDINGS_2026-09-18_RUN5_COMMON_MODE_STALL.md). It does not establish exhaustive novelty, patent novelty, copying, causal dependence, or priority beyond the public record and searches described here.

## 1. Claims audited

RUN5 contains several separable propositions:

- **C1 — same-sensor cognitive redundancy does not defeat sensor-level common-mode failure:** several specialists reading the same stalled physical stream can agree and remain wrong because no additional processor can recreate information the sensor did not acquire.
- **C2 — physical/modality diversity is required for resilience to some common-mode sensor failures:** independent sensing principles can preserve useful information when one modality is stale or impaired.
- **C3 — modality-level hierarchical fusion:** redundant specialists from one declared modality are collapsed into a robust modality summary before higher-level cross-modality coordination.
- **C4 — RUN5 synthetic result:** in the repository's deterministic camera-stall experiment, same-camera redundancy barely changes error under common-mode staleness, whereas a fresh independent IMU modality plus hierarchical freshness fusion sharply lowers error.
- **C5 — reality-bounded coordinator contract:** modality, modality-summary age, confidence, novelty, and cross-modality disagreement are available as low-bandwidth coordinator signals without exposing simulator truth.
- **C6 — learned MaleCNS coordinator benchmark hypothesis:** a learned higher-level MaleCNS coordinator should eventually outperform fixed hierarchical freshness fusion under matched compute and realistic correlated failures.

C4 is an experiment-specific result. It is not a claim that common-mode failure, sensor diversity, multimodal fusion, or hierarchical decision fusion is new.

## 2. Temporal reconstruction

### 2.1 Earliest content-bearing Git commits

The RUN5 branch contains four content-bearing commits on top of the then-current `main`:

- [`6143806fbabb6a70d07078fd7ad6a01b843a928e`](https://github.com/franklinbaldo/papers/commit/6143806fbabb6a70d07078fd7ad6a01b843a928e), Git timestamp **2026-09-19 01:55:55 UTC**, `model modality-level specialist summaries` — first occurrence of the explicit per-modality summary layer relevant to C3/C5.
- [`1a8fb402a163f6f221001844b273ad7eeb0c50b1`](https://github.com/franklinbaldo/papers/commit/1a8fb402a163f6f221001844b273ad7eeb0c50b1), **01:56:09 UTC**, tests for the modality-summary contract.
- [`c504911e1e9355fb595ac548a7bb596cbf8004b8`](https://github.com/franklinbaldo/papers/commit/c504911e1e9355fb595ac548a7bb596cbf8004b8), **01:56:29 UTC**, `add common-mode sensor stall ablation` — first executable occurrence of C1/C2/C4's experimental design.
- [`a627298b87aad91431aae9b8e9138bb1031c4719`](https://github.com/franklinbaldo/papers/commit/a627298b87aad91431aae9b8e9138bb1031c4719), **01:57:19 UTC**, `record common-mode stall findings` — first occurrence of the complete numerical result and explicit interpretation.

### 2.2 Conservatively verified public exposure

GitHub records PR [#573](https://github.com/franklinbaldo/papers/pull/573) as created at **2026-09-19 01:57:30 UTC**. The connector exposes the branch commit timestamps but not the exact push instant, so this audit uses **2026-09-19 01:57:30 UTC** as the conservative public cutoff for C1–C6 while retaining the earlier content-bearing Git timestamps above.

All antecedents classified below predate even the earliest branch commit, so the distinction does not affect any pre/post-cutoff classification.

**Priority confidence:** `1.0` for public availability by PR creation.

## 3. Search protocol

The search decomposed the RUN5 claim into common-cause/common-mode failure, identical versus diverse redundancy, heterogeneous physical sensing, modality-specific processing, decision-level fusion, adaptive modality reliability, graceful degradation, sensor dropout, and hierarchical multimodal fusion.

Sources consulted included NIST and NASA reliability literature, arXiv, publisher/DOI pages, autonomous-driving sensor-fusion literature, safety-oriented multimodal architecture papers, and multisensor condition-monitoring literature.

Representative queries included:

- `common mode failure redundant sensors same sensor processors`
- `common cause failure redundancy diverse sensors independent evidence`
- `autonomous vehicle sensor redundancy modality diversity common cause failure`
- `heterogeneous sensors sensor failure decision level fusion`
- `modality-specific experts sensor failure fusion`
- `camera lidar expert router sensor failure`
- `graceful degradation multimodal sensor fusion missing modality`
- `sensor diversity redundancy fail-operational autonomous driving`
- `hierarchical modality summary fusion sensor failures`
- `common-mode stale sensor multimodal fusion`

Negative searches for the exact MaleCNS conjunction and for post-cutoff releases are bounded results, not proof of non-existence.

## 4. Pre-cutoff findings

### 4.1 NIST 1993 already states the common-sensor limitation of redundant processors

**Work:** *Proceedings of the Digital Systems Reliability and Nuclear Safety Workshop*, NIST Special Publication 500-216, workshop held **1993-09-13/14**.

- Primary source: https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication500-216.pdf

The hardware common-mode-failure section explicitly notes that if redundant processors all receive signals from a **common sensor**, a fault in the input/output system or shared sensing path is a common-mode failure that can defeat the intended fault tolerance.

**Compared claims:** C1, generic C2.

**Classification:** `prior_art` for the generic proposition that computational redundancy downstream of a shared sensor cannot protect against failures common to that sensor/path; `adjacent_prior_work` for the exact MaleCNS/sensor-fusion architecture.

**Consequence:** RUN5 must not present “more processors on one sensor do not defeat sensor-level common-mode failure” as a new reliability principle.

### 4.2 NASA/IEEE 2024–2025: common causes defeat redundancy; diversity is a standard mitigation

**Work:** Harry W. Jones, **“Common Cause Failures Dominate and Defeat Redundancy.”** NASA NTRS document 20240013667, publicly acquired **2024-10-28**; presented at RAMS, January 2025; later indexed by IEEE.

- Primary source: https://ntrs.nasa.gov/citations/20240013667
- DOI/IEEE record: https://doi.org/10.1109/RAMS48127.2025.10935209

Jones states that redundancy improves reliability only when failures are sufficiently independent, that no amount of identical redundancy can reduce failure probability below the common-cause component, and that common-cause risk can be reduced using diverse technologies/components and independent resources.

**Compared claims:** C1, C2.

**Classification:** `prior_art` for the generic reliability claims in C1/C2.

**Consequence:** the scientific interest of RUN5 lies in instantiating and measuring this established principle inside the MaleCNS colony, not in discovering the principle.

### 4.3 Kannan et al. 2022: sensor-specific processing followed by reliability-aware decision fusion

**Work:** Vigneshwar Kannan, Dzung Viet Dao & Huaizhong Li, **“An information fusion approach for increased reliability of condition monitoring With homogeneous and heterogeneous sensor systems.”** *Structural Health Monitoring*, first published online **2022-07-08**, DOI 10.1177/14759217221112451.

- Primary publisher: https://journals.sagepub.com/doi/full/10.1177/14759217221112451

The method detects sensor distortion/failure, trains **different classifiers for different sensor types**, and then performs **decision-level fusion** using signal-integrity scores and the separate classifications. It explicitly addresses heterogeneous sensor systems and reliability under sensor failure/distortion.

**Compared claims:** C2, C3, C5.

**Classification:** `partial_prior_art` for the architecture pattern “sensor/modality-specific processing -> compact outputs/health evidence -> higher-level fusion.”

**Why partial:** it does not use multiple MaleCNS specialists per modality, robust median modality summaries, the `SpecialistReport` contract, or freshness-aware MaleCNS coordination.

### 4.4 Kirchner et al. 2026: independent modality-specific encoders plus shared fusion for fail-operational driving

**Work:** Sven Kirchner, Nils Purschke, Chengdong Wu & Alois Knoll, **“Towards Safety-Compliant Transformer Architectures for Automotive Systems.”** arXiv:2601.18850, first submitted **2026-01-26 14:12:27 UTC**.

- Primary source: https://arxiv.org/abs/2601.18850

The paper proposes multimodal automotive perception with **multiple independent modality-specific encoders** fused into a shared latent representation, explicitly motivating sensor diversity/redundancy as a route to fault tolerance and fail-operational behavior when one modality degrades.

**Compared claims:** C2, C3, C6.

**Classification:** `partial_prior_art`.

**Why partial:** the hierarchy and substrate differ, but the generic design move of preserving independent modality paths before higher-level fusion is plainly pre-cutoff.

### 4.5 MoME 2025: modality experts plus a reliability/quality-aware router under severe sensor failures

**Work:** Konyul Park, Yecheol Kim, Daehun Kim & Jun Won Choi, **“Resilient Sensor Fusion under Adverse Sensor Failures via Multi-Modal Expert Fusion.”** arXiv:2503.19776, first submitted **2025-03-25 15:46:18 UTC**.

- Primary source: https://arxiv.org/abs/2503.19776

MoME decouples LiDAR/camera dependencies into three parallel expert decoders — camera-only, LiDAR-only, and fused — and uses an Adaptive Query Router to select an expert based on feature quality across severe sensor-failure scenarios.

**Compared claims:** C2, C3, C6.

**Classification:** `partial_prior_art`.

**Why partial:** modality-specific experts and high-level reliability-aware routing precede RUN5, but MoME does not instantiate multiple measured-connectome reservoirs per modality or collapse same-modality specialist populations into the repository's summary contract.

### 4.6 Grace-BEV 2026: active modality reliability assessment and graceful degradation

**Work:** Haifa Zhang et al., **“Can BEV Perception Gracefully Degrade under Sensor Failures?”** arXiv:2605.30983, first submitted **2026-05-29 08:18:44 UTC**.

- Primary source: https://arxiv.org/abs/2605.30983

Grace-BEV explicitly assesses modality trustworthiness with a TrustGate Router, dynamically recalibrates feature integration, and trains with modality dropout to remain functional under missing/corrupted modalities.

**Compared claims:** C2, C5, C6.

**Classification:** `partial_prior_art` for active reliability-aware cross-modal coordination under sensor failure.

### 4.7 Viktor 2026 states the RUN5 generic conclusion almost verbatim in the autonomous-vehicle domain

**Work:** Patrik Viktor, **“From Modality Performance to Graceful Degradation: A PRISMA 2020 Systematic Review of Sensor Architectures for Autonomous Vehicles.”** *Sensors* 26(16):5316, published **2026-08-21**, DOI 10.3390/s26165316.

- Primary publisher: https://www.mdpi.com/1424-8220/26/16/5316

The review's section on redundancy diversity and common-cause failure states that redundancy should be evaluated by **independence of evidence, not sensor count**; multiple cameras can share glare, contamination, power, compute, or timing failure, while camera/LiDAR/radar diversity reduces some common causes because the modalities rely on different physical principles. It also warns that majority voting can fail under correlated modality degradation and recommends reliability-aware reasoning using sensor-health evidence and context.

**Compared claims:** C1, C2, generic C5/C6.

**Classification:** `prior_art` for C1/C2 in the same autonomous-vehicle sensor-architecture context; `adjacent_prior_work` for the exact MaleCNS implementation and coordinator contract.

**Consequence:** after this source, the strongest prose claim in RUN5 — “population redundancy is not enough; physical/modality diversity is needed against common-mode sensor failure” — must be treated as an established design principle being experimentally instantiated, not a new principle.

## 5. Novelty boundary after the search

### Not defensible as standalone novelty

The following ideas have clear pre-cutoff antecedents:

- identical computational redundancy cannot defeat a common failure upstream of all replicas;
- the number of redundant processors/sensors is less important than independence of failure modes;
- diverse sensing principles can reduce common-cause vulnerability;
- multiple modality-specific processing paths can feed a higher-level fusion layer;
- reliability/quality/health signals can guide cross-modal routing or weighting;
- multimodal perception can be trained/designed for graceful degradation under missing or corrupted modalities;
- freshness-aware weighting itself, already narrowed in the RUN4 audit, is not new.

### What remains specific to this repository after the search

No pre-cutoff source was located in the searches above that exactly combines all of the following:

1. redundant specialist reservoirs instantiated from the measured **MaleCNS** fly connectome;
2. several specialists per declared physical modality estimating the same reality-bounded semantic scalar;
3. a `SpecialistReport` carrying value, confidence, novelty, `age_ms`, and modality without exposing simulator truth;
4. a robust same-modality summary using medians before cross-modal coordination;
5. the exact deterministic RUN5 comparison of one camera, five-camera median/freshness, camera+IMU hierarchy, and hierarchical freshness under a shared camera-stall process;
6. the observed RUN5 numerical curve, including the near-zero gain from same-camera replication under common-mode staleness and the large gain from the independent fresh modality;
7. the planned matched-compute comparison against a learned higher-level MaleCNS coordinator.

This is a bounded negative search result, **not** a claim that no such antecedent exists.

The scientifically defensible contribution of RUN5 is therefore an **executed MaleCNS-specific architecture diagnostic and benchmark** showing how an established common-cause reliability principle manifests in this colony design, plus a concrete contract for testing learned MaleCNS coordination against fixed fusion baselines.

## 6. Post-cutoff search

The conservative subject cutoff is **2026-09-19 01:57:30 UTC**. Searches performed immediately afterward for `common-mode sensor fusion`, `modality diversity common cause failure`, `multimodal sensor failure experts`, `graceful degradation sensor fusion`, and close variants did not locate a materially overlapping work whose first public release was after that cutoff.

**Result:** no candidate is classified as `later_independent`, `later_overlap`, `later_non_citing`, `later_citing`, or `later_derivative` in this round.

The post-cutoff observation window is only minutes long, so this negative result is intentionally weak.

## 7. Classification ledger

| Work | First verified public date | Compared claim | Classification | Material overlap |
|---|---:|---|---|---|
| NIST SP 500-216, digital-system common-mode failure | 1993-09 | C1/C2 | `prior_art` generic; `adjacent_prior_work` exact architecture | redundant processors sharing one sensor retain a common failure point |
| Jones, *Common Cause Failures Dominate and Defeat Redundancy* | 2024-10-28 public NASA record | C1/C2 | `prior_art` | identical redundancy cannot beat common-cause floor; diversity mitigates |
| Kannan et al., heterogeneous sensor information fusion | 2022-07-08 | C2/C3/C5 | `partial_prior_art` | sensor-specific classifiers + signal-integrity-aware decision fusion |
| Kirchner et al., safety-compliant automotive Transformers | 2026-01-26 | C2/C3/C6 | `partial_prior_art` | independent modality encoders + shared fusion for fail-operational behavior |
| MoME | 2025-03-25 | C2/C3/C6 | `partial_prior_art` | modality experts + adaptive quality router under sensor failure |
| Grace-BEV | 2026-05-29 | C2/C5/C6 | `partial_prior_art` | active modality trust assessment + failure-aware fusion |
| Viktor, AV sensor-architecture systematic review | 2026-08-21 | C1/C2/C5/C6 | `prior_art` C1/C2; `adjacent_prior_work` exact implementation | independence of evidence over sensor count; physical modality diversity for common-cause resilience |

## 8. Revision consequence

RUN5's numerical result remains valid as the result of its deterministic synthetic experiment. The interpretation must be narrower:

- **established principle:** common-cause/common-mode faults defeat identical redundancy, and physically diverse sensing can reduce shared failure vulnerability;
- **established architecture family:** modality-specific processing/expert paths followed by higher-level reliability-aware fusion already exists;
- **RUN5 contribution:** instantiate these principles inside the MaleCNS sensor-colony contract, preserve lawful age/modality metadata, quantify the failure of same-camera specialist replication under shared staleness, quantify cross-modal rescue in the repository's synthetic regime, and define a matched future benchmark for a learned MaleCNS coordinator.

Accordingly, prose should describe RUN5 as a MaleCNS-specific **diagnostic/benchmark and architecture refinement**, not as the invention of modality diversity or common-mode-resilient sensor fusion.

## 9. Schmidhuber Meter readiness

If a materially overlapping work appears later, use:

- `subject_claim`: `MaleCNS modality hierarchy and common-mode sensor-stall benchmark`
- `subject_artifact`: `experiments/malecns_car_interface/FINDINGS_2026-09-18_RUN5_COMMON_MODE_STALL.md`
- earliest modality-summary Git timestamp: `2026-09-19T01:55:55Z`
- earliest common-mode ablation Git timestamp: `2026-09-19T01:56:29Z`
- earliest complete findings Git timestamp: `2026-09-19T01:57:19Z`
- conservative verified public cutoff: `2026-09-19T01:57:30Z`
- `priority_confidence`: `1.0` for public availability by PR creation
- `formula_version`: `0.1`
- `dependency_evidence`: `unknown` unless positive evidence exists

Use the conservative public cutoff for later-work classification unless an earlier branch-push timestamp becomes independently verifiable.
