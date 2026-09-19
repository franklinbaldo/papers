---
type: "Audit Report"
title: "MaleCNS terminal-value specialist recruitment — prior-art and falsification audit — 2026-09-19"
description: "Claim-level temporal and adversarial audit of RUN10 delayed terminal-value recruitment, continuation-policy dependence, the final-allocation oracle gap, and the proposed probe-then-trust follow-on."
tags: [malecns, prior-art, falsification, sensor-colony, dynamic-recruitment, terminal-value, rollout, value-of-information, active-feature-acquisition]
timestamp: 2026-09-19T07:03:00Z
---

# MaleCNS terminal-value specialist recruitment — prior-art and falsification audit — 2026-09-19

> **Status:** claim-specific audit of [`FINDINGS_2026-09-19_RUN10_TERMINAL_VALUE.md`](../../experiments/malecns_car_interface/FINDINGS_2026-09-19_RUN10_TERMINAL_VALUE.md). This record separates temporal priority from present plausibility. It does not establish patent novelty, exhaustive novelty, copying, causal dependence, or misconduct. Negative searches are bounded observations, not proof of absence.

## 1. Claims and hypotheses audited

RUN10 contains several separable claims. For each one this audit states an explicit falsifier or materially narrowing observation.

### C1 — delayed terminal supervision improves on the one-step marginal objective in the RUN10 harness

Observed RUN10 result: terminal-value training lowers MAE relative to RUN9's one-step marginal learner by approximately 0.65%, 1.18%, and 1.04% for uniform, fresh-skewed, and stale-skewed camera-age profiles, respectively.

**Would be wrong or materially weakened if:** independent seeds or paired resampling show the advantage is indistinguishable from zero or reverses; a capacity/training-matched one-step estimator closes the gap; or a policy-invariant shaped/dense reward dominates terminal-only supervision under the same information contract.

### C2 — reward horizon alone is insufficient to explain RUN9's failure

RUN10's terminal learner improves on RUN9 but still loses to the best simple matched-budget baseline by roughly 0.22%, 0.22%, and 0.43% across the three profiles.

**Would be wrong if:** a properly estimated terminal objective, without changing state, policy class, continuation policy, or available information, reliably beats the matched simple baselines. The present experiment falsifies only the stronger claim that *this* terminalization, by itself, is sufficient.

### C3 — random-continuation terminal labels are a meaningful long-horizon action-value target

Training scores a candidate action by final loss after the remaining budget is spent under a fixed randomized continuation policy.

**Would be too broad or misleading if:** action rankings or learned allocations change materially when the continuation/base policy is replaced by a stronger lawful policy; a nongreedy acquisition method dominates; or the random continuation injects enough target variance to explain most of the residual deficit.

### C4 — the large clairvoyant final-allocation gap indicates a value-of-information problem

RUN10 compares deployable policies against an evaluation-only oracle that can inspect realized outputs of specialists that were not yet recruited.

**Would be wrong as stated if:** the oracle advantage disappears when information must be purchased before it is observed, or a lawful no-probe policy/function class closes most of the gap. A free clairvoyant oracle estimates an upper bound associated with perfect information; it does not itself estimate the attainable value of a costly probe.

### C5 — separating `probe / activate` from `trust / use` is the next discriminating architecture

The proposed follow-on pays to reveal a specialist report, then separately decides whether that report may influence fusion.

**Would lack advantage if:** under matched compute and latency, probe-then-trust does not beat always-trust plus a robust fixed gate; information gained by probes does not predict downstream value; or acquisition cost wipes out the gain.

### C6 — delayed real-world signals can replace synthetic truth while preserving the reality-bounded contract

Candidate deployment signals include later IMU/OBD/GNSS consistency, route progress, interventions, collisions, or other delayed task outcomes.

**Would be materially limited if:** these signals are too delayed, confounded, sparse, or misaligned with the control target to provide stable credit assignment, or if policies exploit proxy structure that does not improve the intended driving objective.

## 2. Temporal reconstruction

### 2.1 Content-bearing commits

PR [#611](https://github.com/franklinbaldo/papers/pull/611) contains the following content-bearing commits:

- [`49ba8d009454e1c1696f9067400d56a72d1494af`](https://github.com/franklinbaldo/papers/commit/49ba8d009454e1c1696f9067400d56a72d1494af), Git timestamp **2026-09-19 06:57:11 UTC**, `Add terminal-value recruitment ablation` — first implementation of C1-C3 and the terminal-value training rule.
- [`4e3f86799de90fc9307d4dd5d116ac7e024821d1`](https://github.com/franklinbaldo/papers/commit/4e3f86799de90fc9307d4dd5d116ac7e024821d1), **06:57:29 UTC**, `Test terminal-value recruitment budget invariants`.
- [`a4c9c8f961925ff937f1dde505d3a3e99028376b`](https://github.com/franklinbaldo/papers/commit/a4c9c8f961925ff937f1dde505d3a3e99028376b), **06:57:53 UTC**, `Record terminal-value recruitment findings` — first occurrence of the complete numerical C1/C2 result, C4 interpretation, and C5 follow-on.

### 2.2 Conservatively verified public exposure

GitHub records PR [#611](https://github.com/franklinbaldo/papers/pull/611) as created at **2026-09-19 06:58:05 UTC**. A Git commit timestamp alone does not prove the exact instant of public push. Therefore this audit uses **2026-09-19 06:58:05 UTC** as the conservative public cutoff for C1-C6.

All antecedents classified below were public long before this cutoff, so the conservative choice does not affect their temporal class.

**Priority confidence:** `1.0` for public availability by PR creation.

## 3. Search protocol

The search decomposed RUN10 into long-horizon action evaluation, rollout with a continuation/base policy, sequential information acquisition, active feature acquisition, sensor scheduling, value of information, sparse terminal rewards, reward shaping, acquisition/trust separation, and conditions under which greedy acquisition is already near-optimal.

Sources consulted included arXiv, PMLR/ICML, JAIR, Springer/EURASIP, decision-theoretic value-of-information literature, and bibliographic records for foundational reward-shaping work.

Representative overlap queries:

- `rollout action continuation policy terminal cost sensor scheduling`
- `terminal value resource allocation active sensing continuation policy`
- `active feature acquisition sequential query cost prediction`
- `nongreedy active feature acquisition sparse reward`
- `sensor scheduling value of information MDP`
- `resource scheduling measurement validation radar`
- `probe then trust sensor fusion active sensing`
- `MaleCNS terminal value recruitment`

Representative adversarial queries:

- `terminal reward sparse reward active feature acquisition failure`
- `greedy active sensing near optimal adaptive submodularity sensor placement`
- `reward shaping terminal reward policy invariance`
- `rollout base policy dependence continuation policy`
- `value of perfect information versus sample information acquisition cost`
- `active feature acquisition greedy failure joint information`
- `sensor selection stronger baseline no benefit`

Immediate post-cutoff searches were also run for terminal-value sensor selection, probe/trust sensor fusion, value-of-information recruitment, and MaleCNS recruitment. No materially overlapping first-public-after-cutoff work was located; the observation window is only minutes long and therefore weak.

## 4. Pre-cutoff novelty / overlap findings

### 4.1 Rollout already evaluates current actions through a continuation/base policy

**Work:** Dimitri Bertsekas, **“Multiagent Rollout Algorithms and Reinforcement Learning.”** arXiv:1910.00120, first submitted **2019-09-30**.

- Primary preprint: https://arxiv.org/abs/1910.00120

Rollout methods evaluate present decisions using a base policy for downstream decisions and exploit the resulting cost-to-go. Bertsekas also emphasizes a cost-improvement property relative to the chosen base policy.

**Compared claims:** C1, C3.

**Classification:** `partial_prior_art` for the generic mechanism “candidate action + specified continuation/base policy + downstream outcome”; `adjacent_prior_work` for the exact MaleCNS allocation setting.

**Consequence:** RUN10's use of terminal outcome under a continuation policy is not novel as a general decision-theoretic pattern. Its contribution is the executed MaleCNS-specific ablation and negative benchmark.

### 4.2 Active feature acquisition already formalizes paying to reveal information under a prediction objective

**Work:** Yang Li & Junier Oliva, **“Active Feature Acquisition with Generative Surrogate Models.”** ICML 2021, PMLR 139:6450-6459.

- Primary proceedings: https://proceedings.mlr.press/v139/li21p.html

AFA treats unobserved features as information that can be queried at evaluation time to improve prediction. The paper formulates the problem as an MDP and models potential information gain from acquisitions.

**Compared claims:** C4, C5.

**Classification:** `prior_art` for the generic paid-information-acquisition problem; `partial_prior_art` for the proposed specialist probe mechanism.

### 4.3 Nongreedy AFA explicitly targets joint value and sparse-reward training difficulty

**Work:** Michael Valancius, Maxwell Lennon & Junier Oliva, **“Acquisition Conditioned Oracle for Nongreedy Active Feature Acquisition.”** arXiv:2302.13960, first submitted **2023-02-27**; ICML 2024, PMLR 235.

- Primary preprint: https://arxiv.org/abs/2302.13960
- Proceedings: https://proceedings.mlr.press/v235/valancius24a.html

The work emphasizes that sequential feature acquisitions can be jointly informative, that greedy approaches can miss such effects, and that RL approaches can be difficult to train in AFA because of complicated state/action spaces and sparse rewards.

**Compared claims:** C1, C3, C4, C5.

**Classification:** `partial_prior_art` for long-horizon information acquisition; `boundary_condition` for interpreting the RUN10 failure as evidence about the value of terminal objectives generally.

### 4.4 Adaptive submodularity gives an important regime where simple greedy acquisition is already competitive

**Work:** Daniel Golovin & Andreas Krause, **“Adaptive Submodularity: Theory and Applications in Active Learning and Stochastic Optimization.”** arXiv:1003.3967, first submitted **2010-03-21**; JAIR 42 (2011), 427-486.

- Primary preprint: https://arxiv.org/abs/1003.3967
- JAIR record: https://mlanthology.org/jair/2011/golovin2011jair-adaptive/

For objectives satisfying adaptive submodularity, a simple adaptive greedy policy is provably competitive with the optimal policy; the paper includes sensor-placement and active-learning examples.

**Compared claims:** C3, C4.

**Classification:** `boundary_condition` rather than direct prior art for the RUN10 algorithm.

**Consequence:** a more complex long-horizon allocator is not guaranteed to be useful. If this harness exhibits approximate diminishing returns, a well-estimated greedy policy may be the appropriate strong baseline.

### 4.5 Reward shaping predates terminal-only versus immediate-credit framing

**Work:** Andrew Y. Ng, Daishi Harada & Stuart Russell, **“Policy Invariance Under Reward Transformations: Theory and Application to Reward Shaping.”** ICML 1999, pp. 278-287.

- Bibliographic record: https://dblp.org/rec/conf/icml/NgHR99

Potential-based reward shaping establishes conditions under which denser auxiliary rewards can improve learning without changing the optimal policy.

**Compared claims:** C1, C2, C3.

**Classification:** `adjacent_prior_work`; `boundary_condition` for any inference that the only meaningful alternatives are myopic reward versus sparse terminal reward.

### 4.6 Sensor/resource scheduling under an MDP is established

**Work:** Zhenkai Zhang & Yubo Tian, **“A novel resource scheduling method of netted radars based on Markov decision process during target tracking in clutter.”** *EURASIP Journal on Advances in Signal Processing* 2016:16, published **2016-02-05**, DOI 10.1186/s13634-016-0309-3.

- Open-access article: https://link.springer.com/article/10.1186/s13634-016-0309-3

The work selects radar resources and radiation parameters dynamically under an MDP/tracking objective, within a larger tracking pipeline that also performs measurement association/validation before fusion.

**Compared claims:** generic C4/C5.

**Classification:** `prior_art` for adaptive sensor-resource scheduling; `partial_prior_art` for the conceptual separation between deciding what to acquire and deciding how measurements are accepted into estimation.

**Consequence:** the abstract `activate/probe` versus `accept/trust` split is not itself a new architecture. The MaleCNS-specific instantiation, contract, and matched-budget experiment remain separate questions.

## 5. Falsification and contrary-evidence ledger

### 5.1 RUN10 itself falsifies “reward horizon alone is sufficient” in this implementation

The terminal learner consistently improves over RUN9's one-step marginal learner but still loses to the best simple matched-budget baseline in all three profiles.

**Classification:** `failed_replication_or_null` with respect to the stronger sufficiency hypothesis behind C2.

**Strength:** `strong` *within this exact harness, policy class, continuation policy, and seed*.

**Target attacked:** mechanism/sufficiency claim, not the numerical C1 improvement.

**Required change:** `no_change` to the current RUN10 conclusion because the Findings Record already states this negative result explicitly.

### 5.2 The C1 improvement is small and currently single-seed

The reported terminal-over-one-step gain is only ~0.65-1.18%, while terminal remains ~0.22-0.43% worse than the best simple baseline. The run fixes one seed (`20260919`).

**Classification:** `boundary_condition`.

**Strength:** `moderate`.

**Target attacked:** magnitude/generalization of C1, not the deterministic numbers already reported.

**Required change:** `add_control` and `downgrade_confidence` in any generalized claim until independent seeds or paired uncertainty estimates are available.

### 5.3 Continuation-policy dependence limits the interpretation of the terminal objective

Rollout theory evaluates present actions relative to a downstream/base policy. RUN10 instead labels an action after a *randomized* lawful continuation. The target is therefore the value of an action **under that continuation distribution**, not a continuation-independent intrinsic value of recruiting that modality.

**Classification:** `boundary_condition`.

**Strength:** `strong`.

**Target attacked:** C3 mechanism/generalization.

**Required change:** `narrow_claim` plus `add_control` using at least one stronger lawful continuation policy. This also matches RUN10's own proposed follow-on.

### 5.4 Sparse terminal rewards are not the only principled way to handle long-horizon credit

AFA literature reports training difficulty from sparse rewards, and potential-based reward shaping supplies a classical route to denser credit while preserving the optimal policy under its assumptions.

**Classification:** `boundary_condition`.

**Strength:** `moderate`.

**Target attacked:** the implied reward-design search space around C1-C3.

**Required change:** `add_control`; include at least one dense/shaped or expected-information baseline before concluding that more complex recurrent coordination is needed.

### 5.5 The clairvoyant oracle gap is not a direct estimate of actionable value of information

Decision-theoretic VoI distinguishes perfect information from sample/acquirable information. Perfect-information value is an upper bound; the value of a concrete data acquisition design must account for what can actually be learned and for collection cost.

A concise modern treatment is:

- Christopher Jackson et al., **“Value of Information: Sensitivity Analysis and Research Design in Bayesian Evidence Synthesis.”** *Journal of the American Statistical Association*; open version: https://pmc.ncbi.nlm.nih.gov/articles/PMC7034331/

RUN10's oracle sees the realized outputs of specialists that the deployable agent has not paid to activate. Its gap is therefore best read as a **value-of-clairvoyance / perfect-information upper bound**, not as evidence that a lawful paid probe will recover a similar gain.

**Classification:** `contrary_evidence` against the strong wording of C4; `boundary_condition` for the weaker hypothesis that probing may still be useful.

**Strength:** `strong` for the interpretation, not for whether probe-then-trust will empirically work.

**Target attacked:** mechanism/interpretation of the oracle gap.

**Required change:** `revise_mechanism` / `narrow_claim`: the oracle gap motivates a probe experiment but does not demonstrate actionable VoI.

### 5.6 Greedy may be hard to beat in diminishing-return regimes

Adaptive-submodularity theory proves strong greedy guarantees under explicit conditions. RUN10 has not established whether its specialist-acquisition objective violates or approximately satisfies such diminishing-return structure.

**Classification:** `boundary_condition`.

**Strength:** `weak-to-moderate`, because the assumptions have not been verified for the harness.

**Target attacked:** general expectation that long-horizon planning should materially outperform a correctly estimated marginal policy.

**Required change:** `add_control`: test marginal gains/diminishing returns or compare against a stronger expected-information greedy baseline before escalating policy complexity.

## 6. Priority boundary after the search

### Not defensible as standalone novelty

The following ideas clearly predate RUN10:

- evaluating a current action through a downstream/base continuation policy;
- sequential acquisition of costly information to improve prediction or decisions;
- nongreedy acquisition because multiple future observations may be jointly valuable;
- adaptive sensor/resource scheduling under an MDP;
- generic separation between acquisition/resource scheduling and subsequent measurement acceptance/validation;
- reward shaping as an alternative to sparse terminal credit;
- value-of-information analysis distinguishing perfect-information upper bounds from attainable sample information.

### What remains specific to RUN10 after this search

No pre-cutoff source was located that exactly combines all of the following:

1. the repository's MaleCNS specialist-colony setup and `SpecialistReport`-derived lawful state;
2. the fixed 12-specialist camera/IMU budget and per-modality cap;
3. the exact RUN9 one-step marginal learner and RUN10 random-continuation terminal target;
4. the fixed 4/8 and disagreement×freshness matched-budget controls;
5. the three camera-age profiles and reported numerical result;
6. the explicit no-hidden-truth-at-action-time contract;
7. the planned MaleCNS-coordinator hurdle under the same information and compute budget.

This is a bounded negative search result, **not** a claim that no antecedent exists.

The scientifically defensible contribution of RUN10 is therefore an **executed negative/control result inside the MaleCNS sensor-colony program**: extending the reward horizon recovers part of RUN9's deficit but does not beat simple matched-budget policies, and the experiment exposes continuation-policy and information-acquisition questions that must be separated in the next test.

## 7. Post-cutoff search

The conservative cutoff is **2026-09-19 06:58:05 UTC**. Searches run immediately afterward for terminal-value sensor selection, probe/trust active sensing, value-of-information sensor recruitment, and MaleCNS recruitment did not locate a materially overlapping work first released after the cutoff.

**Result:** no `later_independent`, `later_overlap`, `later_non_citing`, `later_citing`, or `later_derivative` candidate is assigned in this round.

Because the post-cutoff window is only minutes long, this negative result is intentionally weak.

## 8. Classification ledger

| Work / result | First verified public date | Compared claim | Priority classification | Truth-status relation | Strength / consequence |
|---|---:|---|---|---|---|
| Ng, Harada & Russell, reward shaping | 1999 | C1-C3 | `adjacent_prior_work` | `boundary_condition` | moderate; terminal-only is not the only principled credit design |
| Golovin & Krause, adaptive submodularity | 2010-03-21 | C3/C4 | `adjacent_prior_work` | `boundary_condition` | weak-moderate; greedy can be near-optimal under explicit diminishing-return assumptions |
| Zhang & Tian, radar resource scheduling | 2016-02-05 | C4/C5 | `prior_art` generic / `partial_prior_art` | boundary on novelty | acquisition scheduling plus downstream measurement handling predates RUN10 |
| Bertsekas, rollout | 2019-09-30 | C1/C3 | `partial_prior_art` | `boundary_condition` | strong; continuation/base policy is load-bearing in rollout value |
| Li & Oliva, AFA | 2021 | C4/C5 | `prior_art` generic / `partial_prior_art` | alternative mechanism | paid information acquisition under prediction objective is established |
| Valancius et al., ACO | 2023-02-27 | C1/C3/C4/C5 | `partial_prior_art` | `boundary_condition` | moderate; nongreedy joint acquisition and sparse-reward difficulty are established |
| RUN10 own result | 2026-09-19 06:58:05 cutoff | C2 | n/a | `failed_replication_or_null` | strong in-harness: reward horizon alone did not produce a winning allocator |
| Perfect-information vs sample-information VoI distinction | classical; modern synthesis pre-cutoff | C4 | `adjacent_prior_work` | `contrary_evidence` to strong interpretation | strong; free clairvoyance is an upper bound, not measured actionable VoI |

## 9. Required next tests

The most discriminating next pass should preserve the negative result and add controls rather than increasing model complexity reflexively.

1. **Replicate C1 across seeds / paired uncertainty.** Report paired deltas and confidence intervals or bootstrap intervals, not only one deterministic seed.
2. **Continuation-policy ablation.** Train/evaluate the same terminal-value learner with random continuation and at least one stronger lawful continuation. If action values reorder, report the continuation dependence explicitly.
3. **Probe value under cost.** Compare no-probe, fixed probing, and learned probing where every activated report consumes the same declared compute/latency budget. The attainable gain is the relevant sample-information analogue; the free oracle remains only an upper bound.
4. **Separate activation from trust.** Under matched acquisition, compare always-use, robust fixed gate, and learned trust gate before a MaleCNS coordinator.
5. **Stronger greedy control.** Estimate expected marginal information/value rather than realized hidden-truth marginal value, and test whether gains exhibit diminishing returns.
6. **Reward-design control.** Add a dense or potential-based/shaped credit baseline if a valid potential can be defined without leaking hidden state.

## 10. Epistemic update

- **Priority:** narrowed. The generic long-horizon, rollout, active-acquisition, sensor-scheduling, and probe/trust abstractions are established prior art.
- **C1 validity:** `downgrade_confidence` for generalization; keep the executed deterministic result.
- **C2 validity:** `no_change`; RUN10 already records the relevant negative result.
- **C3 mechanism:** `narrow_claim` + `add_control` because terminal action value is continuation-policy dependent.
- **C4 mechanism:** `revise_mechanism`; treat the oracle gap as a perfect-information/clairsentience upper bound, not a measured actionable VoI effect.
- **C5 hypothesis:** retain as a testable follow-on, but not as a generic novelty claim; `add_boundary_condition` and matched-cost controls.
- **C6 hypothesis:** remains uncertain; `add_control` when a real delayed-supervision signal is selected.

The current evidence does **not** support abandoning the MaleCNS coordinator program. It does support a stricter hurdle: before adding recurrent complexity, the next experiment should demonstrate that lawful, paid information acquisition plus separate trust gating creates value beyond strong simple policies under matched compute.
