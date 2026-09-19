---
type: "Audit Report"
title: "MaleCNS contextual specialist recruitment — claim-level prior-art audit — 2026-09-19"
description: "Temporal audit of RUN7's contextual bandit policy selection, sensor-health context, delayed supervision, and matched-compute recruitment benchmark."
tags: [malecns, prior-art, sensor-colony, contextual-bandit, resource-allocation, dynamic-recruitment, citation-debt]
timestamp: 2026-09-19T04:01:00Z
---

# MaleCNS contextual specialist recruitment — claim-level prior-art audit — 2026-09-19

> **Status:** claim-specific audit of [`FINDINGS_2026-09-18_RUN7_CONTEXTUAL_RECRUITMENT.md`](../../experiments/malecns_car_interface/FINDINGS_2026-09-18_RUN7_CONTEXTUAL_RECRUITMENT.md). This record distinguishes established contextual-bandit/resource-allocation ideas from the repository-specific MaleCNS benchmark. It does not establish exhaustive novelty, patent novelty, copying, causal dependence, or priority beyond the public record and searches described here.

## 1. Claims audited

RUN7 contains several separable propositions:

- **C1 — contextual policy selection:** a higher-level learner can choose among already-defined specialist-allocation policies according to observed context rather than committing to one allocator globally.
- **C2 — sensor-health context for resource allocation:** lawful observable sensor-health information, here camera-specialist freshness, can be used as decision-time context for allocating compute/recruitment.
- **C3 — delayed supervision without hidden decision-time truth:** the policy can choose from observable context and receive a delayed post-action training/evaluation signal; latent simulator truth is not supplied at decision time.
- **C4 — RUN7 empirical result:** under the repository's deterministic camera/IMU harness, the learned mapping `fresh -> fixed_imu_heavy` and `stale -> stateless_dynamic` modestly but consistently beats the better global baseline at 20%, 50%, and 80% camera-stall prevalence.
- **C5 — reality-bounded coordinator contract:** a coordinator can be trained/evaluated using signals available from real acquisition/inference telemetry rather than hidden simulator fault labels.
- **C6 — MaleCNS benchmark hypothesis:** a future MaleCNS coordinator should beat the conventional contextual-bandit baseline under the same inputs, delayed-feedback contract, compute budget, and prevalence shifts.

C4 is an experiment-specific result. C1-C3 are much broader methodological claims and must be evaluated against the contextual-bandit and adaptive sensor/resource-management literature.

## 2. Temporal reconstruction

### 2.1 Earliest content-bearing Git commits

PR [#590](https://github.com/franklinbaldo/papers/pull/590) contains four content-bearing commits on top of the then-current `main`:

- [`c10059a2ce59e61291d9a02eefdab63bed01ede2`](https://github.com/franklinbaldo/papers/commit/c10059a2ce59e61291d9a02eefdab63bed01ede2), Git timestamp **2026-09-19 03:56:46 UTC**, `experiment: add contextual recruitment bandit baseline` — first executable occurrence of C1-C3/C5.
- [`5dcde606f22b5bc768b1203da8d3e23125bf845f`](https://github.com/franklinbaldo/papers/commit/5dcde606f22b5bc768b1203da8d3e23125bf845f), **03:56:54 UTC**, tests for the bandit contract.
- [`f682e60a917a0915af3321f706746ad59fc89bf4`](https://github.com/franklinbaldo/papers/commit/f682e60a917a0915af3321f706746ad59fc89bf4), **03:57:09 UTC**, `experiment: add learned recruitment policy ablation` — first executable occurrence of C4's experimental design.
- [`482a01d7a3c2126814ad9ad047078390e1379c77`](https://github.com/franklinbaldo/papers/commit/482a01d7a3c2126814ad9ad047078390e1379c77), **03:57:42 UTC**, `experiment: record contextual recruitment findings` — first occurrence of C4's complete numerical result and explicit interpretation.

### 2.2 Conservatively verified public exposure

GitHub records PR [#590](https://github.com/franklinbaldo/papers/pull/590) as created at **2026-09-19 03:57:51 UTC**. The commit timestamps establish when the content was committed, but this audit does not assume that a commit timestamp alone proves the exact public push instant. Therefore **2026-09-19 03:57:51 UTC** is used as the conservative public cutoff for C1-C6, while retaining the earlier content-bearing Git timestamps above.

All pre-cutoff candidates below predate even the earliest content-bearing commit, so the conservative choice does not alter their classification.

**Priority confidence:** `1.0` for public availability by PR creation.

## 3. Search protocol

The search decomposed RUN7 into contextual action selection, meta-policy selection, adaptive sensor management, context-aware model routing, resource allocation under changing sensor quality, delayed bandit feedback, and causal/reality-bounded decision-time context.

Sources consulted included arXiv, PMLR/AISTATS, NeurIPS proceedings, Oxford Academic, ACM RecSys records, IEEE/ICDCS metadata, and recent sensor/resource-allocation literature.

Representative queries included:

- `contextual bandit sensor management covariates`
- `contextual bandit choose policy among existing policies meta bandit`
- `contextual meta-bandit system selection`
- `contextual bandit sensor quality resource allocation`
- `contextual bandit adaptive sensor allocation freshness`
- `contextual bandit model selection edge computing sensor`
- `contextual bandit delayed feedback resource allocation`
- `sensor health contextual bandit fixed heuristic policies`
- `learned recruitment sensor specialists bandit`
- `MaleCNS contextual recruitment bandit`

Post-cutoff searches were repeated with a one-day recency bound. Negative searches for the exact MaleCNS conjunction and for releases after the cutoff are bounded observations, not proof of non-existence.

## 4. Pre-cutoff findings

### 4.1 Contextual multi-armed bandits already formalize context -> action -> payoff

**Work:** Tyler Lu, David Pal & Martin Pal, **“Contextual Multi-Armed Bandits.”** AISTATS 2010, PMLR 9:485-492, published **2010-03-31**.

- Primary proceedings: https://proceedings.mlr.press/v9/lu10a.html

The paper formalizes online selection of an action from a set of possible actions based on observed context/side information, with payoff depending jointly on context and chosen action.

**Compared claims:** generic C1.

**Classification:** `prior_art` for the generic contextual-bandit primitive; `adjacent_prior_work` for RUN7's sensor-colony application.

**Consequence:** RUN7 cannot claim novelty merely for learning a context-conditioned action choice.

### 4.2 Pavlidis et al. 2010 apply dynamic bandits with covariates directly to sensor management

**Work:** Nicos G. Pavlidis et al., **“Prospects for Bandit Solutions in Sensor Management.”** *The Computer Journal* 53(9):1370-1383, published **2010-01-12**, DOI 10.1093/comjnl/bxp122.

- Publisher: https://academic.oup.com/comjnl/article/53/9/1370/425557

The work poses sensor management in dynamic environments as sequential action selection with side information, using a multi-armed bandit with covariates. The manager learns which action is best for observed covariates while seeing the consequences of selected actions rather than a complete model of the environment.

**Compared claims:** C1, C2, generic C5.

**Classification:** `prior_art` for context-conditioned sensor-management decisions; `partial_prior_art` for RUN7's exact freshness-driven specialist allocation.

### 4.3 Krause & Ong 2011 explicitly evaluate contextual bandits on sensor management

**Work:** Andreas Krause & Cheng S. Ong, **“Contextual Gaussian Process Bandit Optimization.”** NeurIPS 2011.

- Primary proceedings: https://papers.nips.cc/paper/2011/hash/f3f1b7fc5a8779a9e618e1f23a7b7860-Abstract.html

The framework receives context, chooses an action, learns from payoff, and is evaluated in part on sensor management; context-sensitive optimization is reported to outperform no or naive use of context.

**Compared claims:** C1, generic C2.

**Classification:** `prior_art` for context-sensitive bandit optimization in sensor management.

### 4.4 Ngo et al. 2020 select among pre-existing compute/model choices from input context

**Work:** Mao V. Ngo, Tie Luo, Hakima Chaouchi & Tony Q. S. Quek, **“Contextual-Bandit Anomaly Detection for IoT Data in Distributed Hierarchical Edge Computing.”** arXiv:2004.06896, first submitted **2020-04-15 06:13:33 UTC**; later ICDCS 2020, DOI 10.1109/ICDCS47774.2020.00191.

- Primary preprint: https://arxiv.org/abs/2004.06896

The authors construct multiple anomaly-detection DNNs of different complexity at different edge layers and choose one **on the fly** from contextual information extracted from the input. The selection itself is formulated as a contextual bandit.

**Compared claims:** C1, C2.

**Classification:** `partial_prior_art` with strong mechanistic overlap.

**Why partial:** it selects models/compute locations rather than same-budget MaleCNS specialist-allocation rules, but the pattern “existing alternatives + observed context -> learned online selector” clearly predates RUN7.

### 4.5 Santana et al. 2020 are especially close to the higher-level policy-selector interpretation

**Work:** Marlesson R. O. Santana et al., **“Contextual Meta-Bandit for Recommender Systems Selection.”** RecSys 2020, pp. 444-449, DOI 10.1145/3383313.3412209, conference **2020-09-22/26**.

- Official conference listing: https://recsys.acm.org/recsys20/accepted-contributions/
- DOI: https://doi.org/10.1145/3383313.3412209

Their meta-bandit acts as a policy over options, where each option maps to a pre-trained independent recommender system; the meta-bandit learns online and chooses a recommender according to context. Reported experiments show the contextual meta-selector outperforming the component recommenders and an ensemble.

**Compared claims:** C1, generic C4.

**Classification:** `prior_art` for the generic proposition “a higher-level contextual bandit learns when to invoke one of several already-defined systems/policies”; `partial_prior_art` for RUN7's exact specialist-allocation setting.

**Consequence:** the architectural lesson “do not discard a heuristic; learn when to invoke it” is not new in the abstract. RUN7's value must be stated at the MaleCNS/sensor-colony level and in its particular controlled result.

### 4.6 Delayed post-action feedback is established bandit machinery

**Work:** Claire Vernade et al., **“Linear Bandits with Stochastic Delayed Feedback.”** arXiv:1807.02089, first submitted **2018-07-05 17:09:33 UTC**.

- Primary preprint: https://arxiv.org/abs/1807.02089

The paper formalizes linear bandits in which feedback is delayed and only partially observable, with algorithms that integrate information as it becomes available.

**Compared claims:** generic C3.

**Classification:** `prior_art` for delayed bandit feedback as a general learning setup; `adjacent_prior_work` for RUN7's specific insistence that hidden simulator truth is allowed only as post-action harness supervision and must be replaced by a reproducible physical target in deployment.

### 4.7 PIR 2026 is a close sensor/resource-allocation antecedent only weeks before RUN7

**Work:** Navaneeth Krishnan Kamalakannan, Janakiraman Kamalakannan & Harinisri Velmurugan, **“Physiological Information Reliability: Cross-Layer Adaptive Resource Allocation for Cardiovascular Sensing.”** arXiv:2609.00435, first submitted **2026-08-31 22:17:14 UTC**; ML4H 2026 Findings submission.

- Primary preprint: https://arxiv.org/abs/2609.00435

PIR combines multimodal signal-quality information with wireless, energy, and compute state and uses a contextual bandit to adapt sensing/communication decisions. It compares its learned controller with fixed and heuristic policies and explicitly studies a changing signal/resource environment.

**Compared claims:** C2, C4, C5, generic C6.

**Classification:** `partial_prior_art` with high conceptual overlap.

**Why partial:** PIR allocates sensing/network resources rather than MaleCNS specialist instances and does not implement RUN7's two policy arms, binary camera-age context, or measured-connectome coordinator hypothesis. But “lawful sensor/system-health context -> contextual-bandit resource decision -> comparison against fixed/heuristic policies” is plainly pre-cutoff.

## 5. Novelty boundary after the search

### Not defensible as standalone novelty

The following ideas have clear pre-cutoff antecedents:

- contextual bandits choosing actions from observed side information;
- contextual-bandit sensor management;
- context-conditioned selection among several pre-existing models/systems/policies;
- a meta-level learner deciding when to invoke one of several existing alternatives;
- adaptive resource allocation from observed sensor/signal/system health;
- delayed post-action feedback in bandit learning;
- comparison of learned contextual decisions against fixed or heuristic baselines.

### What remains specific to this repository after the search

No pre-cutoff source was located in the searches above that exactly combines all of the following:

1. redundant specialists instantiated from the measured **MaleCNS** connectome;
2. the repository's reality-bounded `SpecialistReport` contract;
3. a fixed total budget of 12 specialist instances;
4. the exact competing arms `fixed_imu_heavy` (4 camera / 8 IMU) and the prior `stateless_dynamic` disagreement × freshness allocator;
5. decision-time context restricted to median camera-specialist `age_ms`, bucketed at 150 ms, with no fault label or simulator truth;
6. delayed latent truth used only after the action as synthetic harness supervision, with an explicit deployment requirement for reproducible delayed physical/task feedback;
7. the RUN7 result that the learned `fresh -> fixed`, `stale -> dynamic` mapping modestly beats the better global baseline at 20%, 50%, and 80% stall prevalence under matched compute;
8. the intended follow-on comparison in which a learned adapter and a MaleCNS coordinator must beat this conventional contextual-bandit baseline under the same information and resource contract.

This is a bounded negative search result, **not** a claim that no such antecedent exists.

The scientifically defensible contribution of RUN7 is therefore an **executed MaleCNS-specific benchmark and control**: it demonstrates that a lawful contextual selector can extract a small but repeatable gain from choosing between two already-defined recruitment rules under prevalence shift, and establishes a cheap conventional baseline that a future MaleCNS coordinator must exceed.

## 6. Post-cutoff search

The conservative subject cutoff is **2026-09-19 03:57:51 UTC**. Immediate post-cutoff searches for `contextual bandit sensor freshness allocation`, `contextual meta-bandit sensor allocation`, `learned recruitment sensor specialists bandit`, and `MaleCNS contextual recruitment bandit` did not locate a materially overlapping work whose first public release was after that cutoff.

One recent search result, **RoboAtlas: Contextual Active SLAM**, was first public in June 2026 and is therefore pre-cutoff; it is merely adjacent evidence that contextual bandits are actively used as high-level switching/routing mechanisms in robotics. It is not a later work relative to RUN7.

**Result:** no candidate is classified as `later_independent`, `later_overlap`, `later_non_citing`, `later_citing`, or `later_derivative` in this round.

The post-cutoff observation window is only minutes long, so this negative result is intentionally weak.

## 7. Classification ledger

| Work | First verified public date | Compared claim | Classification | Material overlap |
|---|---:|---|---|---|
| Lu, Pal & Pal, *Contextual Multi-Armed Bandits* | 2010-03-31 | C1 | `prior_art` generic | observed context -> action -> payoff |
| Pavlidis et al., *Prospects for Bandit Solutions in Sensor Management* | 2010-01-12 | C1/C2/C5 | `prior_art` generic; `partial_prior_art` exact setting | sensor management as dynamic bandit with covariates |
| Krause & Ong, *Contextual Gaussian Process Bandit Optimization* | 2011 | C1/C2 | `prior_art` generic | context-sensitive bandit optimization including sensor management |
| Vernade et al., *Linear Bandits with Stochastic Delayed Feedback* | 2018-07-05 | C3 | `prior_art` generic | learning from delayed post-action feedback |
| Ngo et al., contextual-bandit IoT anomaly detection | 2020-04-15 | C1/C2 | `partial_prior_art` | online context-driven choice among pre-built models/compute layers |
| Santana et al., *Contextual Meta-Bandit for Recommender Systems Selection* | 2020-09 | C1/C4 | `prior_art` generic; `partial_prior_art` exact setting | higher-level contextual policy chooses among pre-trained independent systems |
| Kamalakannan et al., PIR | 2026-08-31 | C2/C4/C5/C6 | `partial_prior_art` | sensor-quality/system-state contextual bandit for adaptive resource decisions vs fixed/heuristic baselines |

## 8. Citation-debt / Schmidhuber-Meter seed

This audit freezes enough evidence for later comparison if materially similar work appears after the cutoff:

- `subject_claim`: RUN7 contextual learned recruitment policy, claims C1-C6 above;
- `subject_artifact`: `experiments/malecns_car_interface/FINDINGS_2026-09-18_RUN7_CONTEXTUAL_RECRUITMENT.md` and the executable RUN7 branch history;
- `subject_cutoff`: `2026-09-19T03:57:51Z` (conservative public PR cutoff);
- `priority_confidence`: `1.0` for public availability by PR creation;
- `formula_version`: `0.1` when/if a later candidate is scored;
- `dependency_evidence`: `unknown` unless positive evidence appears.

No later candidate is scored in this audit.

## 9. Revision rule and limits

If a stronger antecedent is found later, append or supersede this assessment with an explicit revision rather than silently rewriting the epistemic history. In particular, a source that predates the cutoff and combines contextual policy selection with redundant same-modality specialists, freshness/disagreement coordinator inputs, matched compute, and delayed physical feedback could materially narrow the remaining boundary.

Conversely, a future paper published after the cutoff must never be relabeled as prior art against RUN7. It belongs in one of the repository's `later_*` classes according to the evidence then available.
