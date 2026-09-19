---
type: "Audit Report"
title: "MaleCNS consensus-gated fusion — claim-level prior-art audit — 2026-09-19"
description: "Temporal audit of median/MAD consensus gating, confidence weighting after robust screening, ensemble-agreement signals, and the RUN3 synthetic result for MaleCNS sensor colonies."
tags: [malecns, prior-art, sensor-fusion, robust-statistics, consensus, confidence, citation-debt]
timestamp: 2026-09-19T00:02:43Z
---

# MaleCNS consensus-gated fusion — claim-level prior-art audit — 2026-09-19

> **Status:** claim-specific audit of the consensus-fusion addition introduced after the broader [sensor-colony audit](./malecns-sensor-colony-2026-09-19.md). This record narrows the novelty boundary of [`FINDINGS_2026-09-18_RUN3_CONSENSUS_FUSION.md`](../../experiments/malecns_car_interface/FINDINGS_2026-09-18_RUN3_CONSENSUS_FUSION.md). It does not establish exhaustive novelty, patent novelty, copying, causal dependence, or priority beyond the public record and searches described here.

## 1. Claims audited

The RUN3 change contains several separable propositions:

- **C1 — fixed consensus-gated confidence fusion:** compute a robust center by median, estimate dispersion by median absolute deviation (MAD), reject reports outside `max(min_radius, mad_scale * MAD)`, then confidence-weight only the surviving reports.
- **C2 — self-confidence is insufficient:** a robust coordinator should have access to both each specialist's self-reported reliability/confidence and cross-specialist agreement/disagreement; suggested lawful signals include robust center, MAD/disagreement, fraction inside consensus, aggregate confidence, and novelty/surprise.
- **C3 — synthetic RUN3 result:** under the repository's fixed five-specialist simulation at 20% fault probability with faulty confidence `0.95`, raw confidence-weighted fusion reached MAE `0.171619` while the consensus-gated rule reached `0.062747`, about 63.4% lower error.
- **C4 — benchmark hypothesis for a learned MaleCNS coordinator:** a learned coordinator should be compared against single-specialist, mean/median, raw confidence weighting, and consensus-gated confidence under normal noise, dropout, confidently wrong specialists, and drift.

C3 is an experiment-specific observed result, not a claim that robust consensus fusion itself is new.

## 2. Temporal reconstruction

### 2.1 Content-bearing Git commit: 2026-09-18 23:59:21 UTC

The first commit in PR #552 that already contains the consensus-gated method is:

- commit [`266a7ee85ca6097be26e034056f8e54dceecacc1`](https://github.com/franklinbaldo/papers/commit/266a7ee85ca6097be26e034056f8e54dceecacc1)
- Git author/committer timestamp: **2026-09-18 23:59:21 UTC**
- message: `Add robust consensus fusion for sensor colonies`

The later commits add tests (23:59:35), the ablation (23:59:48), and the findings record (2026-09-19 00:00:41 UTC). The merge commit is later still and is not the claim cutoff.

### 2.2 Conservatively verified public exposure: 2026-09-19 00:00:49 UTC

GitHub records PR #552 as created at **2026-09-19 00:00:49 UTC**. The connector does not expose a branch-push timestamp, so the commit's Git timestamp proves the content existed in Git at 23:59:21 but does not, by itself, prove the exact second at which that commit became publicly reachable on GitHub.

For temporal classification in this audit, the **conservative public cutoff is therefore 2026-09-19 00:00:49 UTC**, while 23:59:21 UTC is retained as the earliest content-bearing Git timestamp. Every material antecedent found below predates both timestamps, so this distinction does not change any classification.

**Priority confidence:** `1.0` that the claim was public by PR creation; no claim is made here about an earlier branch-push instant.

## 3. Search protocol

The search was decomposed around the actual algorithm, not the words “MaleCNS” or “consensus fusion” alone. Sources included publisher/DOI pages, TU Wien's institutional repository, DNV workshop proceedings, Wiley, SAGE, MDPI, IEEE/PubMed discovery, and prior sensor-fusion literature already recorded in the colony audit.

Representative queries:

- `"median absolute deviation" "confidence-weighted" sensor fusion`
- `median MAD outlier rejection weighted sensor fusion`
- `Hampel confidence indicator weighting sensor measurements`
- `cross-sensor agreement reliability weights consensus sensor fusion`
- `robust consensus outlier sensor fusion confidence`
- `exclude faulty measurements before confidence weighted averaging`
- `sensor reliability weights MAD consensus no ground truth`
- `multi sensor fusion confidently wrong sensor consensus`

Negative searches for the exact four-step conjunction and for post-cutoff publications are bounded search results, not proof of non-existence.

## 4. Pre-cutoff findings

### 4.1 Schörgendorfer 2006: confidence-weighted fusion already includes a fault-tolerant screening-before-fusion lineage

**Work:** Angela Schörgendorfer, *Extended Confidence-Weighted Averaging in Sensor Fusion*, master's thesis, Technische Universität Wien, 2006; related peer-reviewed conference paper with Wilfried Elmenreich at Junior Scientist Conference 2006, event 19–21 April 2006.

- Institutional thesis record: https://repositum.tuwien.at/handle/20.500.12708/179560
- Conference record: https://repositum.tuwien.at/handle/20.500.12708/51595
- Thesis PDF: https://mobile.aau.at/~welmenre/papers/theses/schoergendorfer_extended%20confidence%20weighted%20averaging%20in%20sensor%20fusion.pdf

The thesis reviews fault-tolerant confidence-weighted averaging and explicitly discusses identifying/excluding faulty measurements before final fusion, including distortion-based exclusion of extreme observations. Its main contribution is extended confidence-weighted averaging with sensor-error correlations.

**Compared claims:** generic substructure of C1; C2.

**Classification:** `partial_prior_art` for C1's exact rule; **direct prior art for the generic pattern** `screen unreliable measurements -> confidence-weight surviving measurements`.

**Why not full C1 prior art:** the located method does not instantiate our exact `median center -> MAD radius -> hard inlier gate -> self-confidence weighted mean` rule.

**Consequence:** RUN3 must not present “check reliability/consistency before trusting confidence” as a new sensor-fusion principle.

### 4.2 Chen et al. 2012 comes unusually close to the median/MAD + confidence-weighting conjunction

**Work:** Chien-Chu Chen et al., **“Outlier-Detection-Based Indoor Localization System for Wireless Sensor Networks.”** *International Journal of Navigation and Observation*, 2012, Article 961785, DOI 10.1155/2012/961785.

- Publisher: https://onlinelibrary.wiley.com/doi/10.1155/2012/961785

The paper uses the Hampel filter's median and MAD-scale, combines the MAD-scale score with a density estimate to assign each reading a **confidence indicator**, and then uses those confidence indicators as weights in localization. It explicitly prefers assigning reliability confidence rather than merely throwing anomalous data away.

**Compared claims:** C1, C2.

**Classification:** `partial_prior_art` with **high component overlap**.

**Why:** it anticipates the chain `robust median/MAD deviation -> reliability/confidence -> heavier weighting of trustworthy observations`. Its exact confidence function, KDE component, localization objective, and absence of the MaleCNS specialist/report architecture keep it from being the same algorithm.

### 4.3 Park & Chang 2016: robust center-relative weighting of sensor measurements

**Work:** Chee-Hyun Park & Joon-Hyuk Chang, **“Time-of-arrival source localization based on weighted least squares estimator in line-of-sight/non-line-of-sight mixture environments.”** First published online **2016-12-14**, DOI 10.1177/1550147716683827.

- Publisher: https://journals.sagepub.com/doi/10.1177/1550147716683827

The method fuses multiple measurements while assigning less weight to samples farther from an inlier center; one formulation uses distance from the median, and the paper contrasts robust center/outlyingness weights with conventional inverse-variance weighting.

**Compared claims:** C1, C2.

**Classification:** `partial_prior_art`.

**Consequence:** robust agreement with a median-like ensemble center as a basis for fusion weights is established prior art.

### 4.4 Robust distributed consensus under outliers is an established neighboring literature

**Work:** **“Robust Consensus Nonlinear Information Filter for Distributed Sensor Networks with Measurement Outliers.”** 2018, distributed sensor-fusion / information-filter literature.

- PubMed discovery record: https://pubmed.ncbi.nlm.nih.gov/?term=%22Robust+Consensus+Nonlinear+Information+Filter%22

The work addresses distributed consensus estimation when sensor measurements contain outliers.

**Compared claims:** C2, C4.

**Classification:** `adjacent_prior_work`.

**Why:** it establishes that consensus and robustness to outlier-producing agents/sensors are not a new problem formulation, but it does not reproduce C1's fixed rule or the MaleCNS experiment.

### 4.5 MFO-Fusion 2024 uses MAD-based degradation detection before a second fusion/optimization stage

**Work:** Zixuan Zou et al., **“MFO-Fusion: A Multi-Frame Residual-Based Factor Graph Optimization for GNSS/INS/LiDAR Fusion in Challenging GNSS Environments.”** *Remote Sensing* 16(17), 3114, published **2024-08-23**, DOI 10.3390/rs16173114.

- Publisher: https://www.mdpi.com/2072-4292/16/17/3114

MFO-Fusion computes multi-frame residuals, uses MAD to detect and eliminate degraded GNSS states, and then performs a second-stage factor-graph optimization with the remaining/healthy information.

**Compared claims:** C1 generic two-stage structure; C4 robustness benchmark rationale.

**Classification:** `partial_prior_art`.

**Why:** it directly anticipates `MAD-based robust screening -> downstream fusion`, though not confidence-weighting of surviving redundant specialists.

### 4.6 ARMS 2026 directly combines MAD robustness, reliability weighting, and cross-sensor agreement without ground truth

**Work:** Yi Liu, Bingjie Guo & Shuai Wang (DNV), **“ARMS — Adaptive Robust Multi-Sensor Fusion for Vessel STW Estimation.”** Presented in the DNV Nordic Maritime Universities Workshop, Tromsø, **29–30 January 2026**.

- Primary workshop programme/abstracts: https://www.dnv.com/contentassets/8e19a6da9cf444adaeaf945a7c25f632/dnv-nordic-maritime-universities-workshop-2026-programme-and-abstracts.pdf

ARMS combines three mechanisms: Huber robustness parameters learned from residual statistics via MAD; sensor reliability weights updated from precision and bias; and **consensus-based outlier detection using cross-sensor agreement without ground truth**.

**Compared claims:** C1, C2, C4.

**Classification:** `partial_prior_art` for C1's exact implementation; **prior_art for C2's generic proposition** that self/source reliability should be combined with ensemble/cross-sensor agreement rather than trusted in isolation.

**Consequence:** the sentence “a coordinator should infer both self-confidence and social/ensemble agreement” is a sensible design conclusion in the MaleCNS setting, but not a standalone novelty claim in robust sensor fusion.

## 5. Novelty boundary after the search

### Not defensible as standalone novelty

The following ideas have clear pre-cutoff antecedents:

- confidence/reliability-weighted sensor fusion;
- robust median/MAD outlier detection;
- rejecting or downweighting outliers before weighted fusion;
- deriving a confidence indicator from robust deviation and then weighting observations by it;
- using distance/agreement with a robust ensemble center to determine influence;
- combining source reliability with cross-sensor consensus/agreement;
- evaluating fusion under faulty/outlier sensors.

### What remains specific to this repository after the search

No pre-cutoff source was located in the searches above that exactly combines all of the following:

1. redundant **MaleCNS** sensor specialists from the measured fly connectome;
2. the repository's exact fixed baseline `median -> MAD radius -> hard consensus gate -> specialist self-confidence weighting`;
3. a reality-bounded `SpecialistReport` interface;
4. the exact deterministic RUN3 ablation and numerical result;
5. the planned comparison against a learned higher-level MaleCNS coordinator under matched connectome/control conditions.

This is a bounded negative search result, **not** a claim that no such antecedent exists.

The scientifically useful contribution of RUN3 is therefore better framed as **an executed baseline and failure-mode diagnostic inside the MaleCNS colony programme**, not as invention of robust consensus/confidence sensor fusion.

## 6. Post-cutoff search

The conservative subject cutoff is 2026-09-19 00:00:49 UTC and this audit was run immediately afterward. Targeted freshness searches for `consensus-gated confidence sensor fusion`, `MAD confidence weighting sensor`, `cross-sensor agreement reliability fusion`, and close variants did not locate a materially overlapping work whose first public release was after that cutoff.

**Result:** no candidate is classified as `later_independent`, `later_overlap`, `later_non_citing`, `later_citing`, or `later_derivative` in this round.

This narrow negative result says little about future convergence because the post-cutoff observation window is only minutes long.

## 7. Classification ledger

| Work | First verified public date | Compared claim | Classification | Material overlap |
|---|---:|---|---|---|
| Schörgendorfer, *Extended Confidence-Weighted Averaging* | 2006 (conference 19–21 Apr) | C1/C2 | `partial_prior_art` | screening faulty observations before confidence-weighted fusion |
| Chen et al., WSN outlier localization | 2012 | C1/C2 | `partial_prior_art` | median/MAD-scale -> confidence indicator -> weighted processing |
| Park & Chang, robust TOA WLS | 2016-12-14 | C1/C2 | `partial_prior_art` | median/inlier-center distance controls fusion weight |
| Robust Consensus Nonlinear Information Filter | 2018 | C2/C4 | `adjacent_prior_work` | consensus estimation under measurement outliers |
| MFO-Fusion | 2024-08-23 | C1/C4 | `partial_prior_art` | MAD degradation detection before second-stage fusion/optimization |
| ARMS | 2026-01-29/30 workshop | C1/C2/C4 | `partial_prior_art` overall; `prior_art` for generic C2 | MAD + reliability weights + cross-sensor agreement without truth |

## 8. Revision consequence

The broader sensor-colony audit remains valid: it had already established confidence weighting and median robust fusion as old components. This follow-up adds a stronger and more specific correction for RUN3: **the coupling of robust consensus evidence with reliability/confidence weighting also has clear pre-cutoff antecedents.**

The RUN3 findings record should therefore be read as an empirical architecture note and baseline, with its exact MaleCNS-specific conjunction separated from the prior art of its robust-fusion ingredients.

## 9. Schmidhuber Meter readiness

If a materially overlapping work appears later, use:

- `subject_claim`: `MaleCNS colony consensus-gated confidence fusion`
- `subject_artifact`: `experiments/malecns_car_interface/FINDINGS_2026-09-18_RUN3_CONSENSUS_FUSION.md`
- earliest content-bearing Git timestamp: `2026-09-18T23:59:21Z`
- conservative verified public cutoff: `2026-09-19T00:00:49Z`
- `priority_confidence`: `1.0` for public availability by PR creation
- `formula_version`: `0.1`
- `dependency_evidence`: `unknown` unless positive evidence exists

The conservative public cutoff should be used when classifying later works unless an earlier branch-push timestamp becomes independently verifiable.
