---
type: "Audit Report"
title: "Informational Time and Critical Recognition prior-art audit — 2026-09-18"
description: "Claim-specific temporal audit of informational causal depth and critical agent-recognition time, separating pre-cutoff causal-depth, goal-recognition, intentional-stance, sequential-testing, and MDL antecedents from the surviving combination."
tags: [informational-time, causal-depth, agent-recognition, prior-art, goal-recognition, intentional-stance, mdl, sequential-testing]
timestamp: 2026-09-18T01:02:23-04:00
---

# Informational Time and Critical Recognition prior-art audit — 2026-09-18

> **Status:** first claim-specific reproducible prior-art audit of the causal-time and critical-recognition claims in [`informational_time.md`](../../informational_time.md), with the later four-family agent-recognition refinement in [`informational_time_negentropy_clarifications.md`](../../informational_time_negentropy_clarifications.md) audited under its own later cutoff. This audit materially narrows the novelty boundary. It does **not** establish exhaustive novelty, patent novelty, independent invention, copying, plagiarism, or causal dependence.

## 1. Claims audited

The paper family contains several separable propositions that must not borrow novelty from one another:

- **C1 — path-relative informational time:** a realized causal path is assigned a time-like quantity by accumulating positive-cost, recoverable causal distinctions along the path;
- **C2 — path versus endpoint/distance distinction:** the causal history actually traversed is distinct from a minimal or endpoint-relative description/path quantity; later symbolic compression of the history does not retroactively shorten the causal sequence that occurred;
- **C3 — causal work versus causal depth:** total event work and maximum sequential dependency depth are different quantities, especially under parallelism;
- **C4 — critical recognition time:** `C_{A←B}` is the minimum accumulated informational time at which an observer obtains both complexity-charged retrospective evidence for an agent model and sustained out-of-sample predictive advantage over admissible non-agent alternatives;
- **C5 — relational/directional recognition:** recognition is observer-, channel-, model-class-, and direction-dependent rather than a context-free scalar property of the observed system;
- **C6 — active recognition:** informative interventions selected by the observer may reduce the recognition time relative to matched passive observation;
- **C7 — four-family recognition refinement:** a stronger later criterion requires the agent model to defeat not only randomness or self-generation but also the strongest admissible structured non-agent law, with prospective prediction/intervention and full model/registry/search/parameter cost charged.

Recursive endogenous tokenization itself is not re-audited here because it has a separate repository audit in `audits/prior-art/generative-machine-teaching-2026-09-17.md`. The present audit focuses on causal time/depth and agent recognition.

## 2. Temporal reconstruction of our claims

### 2.1 C1–C6: original Informational Time proposal

The public pull request [`#238`](https://github.com/franklinbaldo/papers/pull/238), **“paper: define informational time from recursive tokenization,”** was created at **2026-07-30 21:51:06 UTC**. Its opening public description already enumerated:

- informational events as non-empty recoverable causal distinctions;
- path-relative informational time and informational distance;
- causal work versus causal depth;
- critical recognition time `C_{A←B}` based on both net description-length evidence and held-out predictive gain;
- relational agent recognition;
- an experimental program including interaction and cross-observer transfer.

The earliest located file commit is [`58959bfe8edc0dcbf54930358adfc93cf6e62e49`](https://github.com/franklinbaldo/papers/commit/58959bfe8edc0dcbf54930358adfc93cf6e62e49), timestamped **2026-07-30 22:01:50 UTC**, and its first version already contains the critical-recognition definition and the causal-time thesis. Because the PR description itself publicly states the claim family ten minutes earlier, this audit uses the earlier verifiable public event rather than the later commit timestamp.

**Cutoff for C1–C6: 2026-07-30 21:51:06 UTC.**

### 2.2 C7: stronger maximum-entropy / self / law / agent comparison

The public pull request [`#240`](https://github.com/franklinbaldo/papers/pull/240), **“paper: clarify negentropy and relational agent recognition,”** was created at **2026-07-31 03:28:13 UTC**. Its opening description already makes the stronger refinement explicit:

- maximum entropy is an observer-relative epistemic null;
- local negentropy alone does not establish agency;
- persistent structured external laws must be separated from agent-level models;
- recognition depends on comparative predictive gain and intervention-sensitive response;
- the revised criterion compares `M_agent` against maximum entropy, self-generation, **and the strongest admissible structured non-agent law**.

**Cutoff for C7: 2026-07-31 03:28:13 UTC.**

Using one paper-wide date for all seven claims would therefore be incorrect.

## 3. Search protocol

Sources searched included primary proceedings and journal pages, arXiv/Preprints records, PubMed/MIT institutional records, publisher metadata, and targeted web discovery. Searches deliberately decomposed the claims rather than relying on the paper title.

Representative queries:

- `causal depth physical time logical depth longest chain`
- `causal depth process state minimum over histories`
- `path dependent informational time causal history event cost`
- `goal recognition time prefix length before goal recognized`
- `worst case distinctiveness goal recognition`
- `active goal recognition intervention expedite recognition`
- `agent recognition predictive model non-agent intentional stance`
- `agency detection Bayesian prediction randomness agent`
- `intentional stance compression prediction real patterns`
- `minimum description length sequential prediction model selection`
- `prequential MDL cumulative prediction`
- `sequential probability ratio test first threshold crossing`
- `agent model versus structured law prediction compression`
- `critical recognition time agent`
- post-cutoff searches over August–September 2026 for `agent recognition`, `agenticness`, `goal-directedness`, `causal depth`, and `informational time`.

Negative searches are logged as bounded search results only. “Not found” does not mean “does not exist.”

## 4. Pre-cutoff findings

### 4.1 A causal-depth/physical-time preprint was public three days before our paper

**Work:** Babu George, **“Causal Depth as an Invariant of Irreducible Computation: Reassessing Logical Depth, Causal Order, and Physical Time.”**

- submitted: **2026-07-25**;
- posted publicly on Preprints.org: **2026-07-27**;
- URL: <https://www.preprints.org/manuscript/202607.1938>.

**Compared claims:** C1–C3.

**Classification:** `prior_art` for the generic process/state causal-depth distinction and causal-depth-as-time-like dependency structure; `partial_prior_art` for the Informational Time formulation as a whole.

This is the most important finding of the run. George explicitly distinguishes:

1. the **causal depth of a process** as the height/longest chain of its causal dependency graph;
2. the **causal depth of a state** as the minimum process depth over admissible processes producing that endpoint;
3. an actual trajectory quantity from an endpoint-relative minimum;
4. causal/circuit depth from Bennett logical depth, arguing that the former has the extremal structure needed for comparison with physical time.

The public date is about three days before our C1–C6 cutoff. It therefore cannot be treated as later convergence.

**Difference:** `informational_time.md` does not identify its primary path quantity with circuit depth. It defines `τ_I(π)` as the **sum of coded, recoverable causal distinctions along a realized path**, then separately defines total work, longest-path causal depth, informational distance, recursive proof-preserving symbolic compression, and agent-recognition stopping time. George's causal-depth object is graph-height based and its physical-time target is relativistic/proper time; our framework is observer/registry-relative and explicitly stops short of identifying informational time with physical time. The overlap is nevertheless material enough that any novelty claim around simply separating causal trajectory depth from logical/description depth must be abandoned.

### 4.2 Work/span and causal-set longest-chain ideas independently occupy much of C3's mathematical substrate

**Works/families:** parallel-computation work/span; causal-set longest-chain accounts of proper time; Bennett logical depth and information distance.

**Compared claims:** C2–C3.

**Classification:** `prior_art` for the underlying mathematical distinctions; `adjacent_prior_work` for the specific registry-relative informational accounting.

The present paper already acknowledges Bennett, information distance, and related foundations. The audit adds the stronger priority conclusion: distinguishing total work from sequential depth and distinguishing a path/history cost from a compact description are not independently novel components. Their scientific value here lies in how they are assembled into the interaction/recognition framework.

### 4.3 Goal Recognition Design already defined a path-length-to-recognition quantity in 2014

**Work:** Sarah Keren, Avigdor Gal & Erez Karpas, **“Goal Recognition Design.”** ICAPS 2014.

- published: **2014-05-10** on the ICAPS proceedings site;
- DOI: <https://doi.org/10.1609/icaps.v24i1.13617>;
- primary proceedings: <https://ojs.aaai.org/index.php/ICAPS/article/view/13617>.

**Compared claims:** C4 and C6.

**Classification:** `prior_art` for the generic idea of measuring recognition by the length of an observed prefix before the hidden intentional variable becomes identifiable; `partial_prior_art` for `C_{A←B}`.

Keren et al. introduce **worst-case distinctiveness (`wcd`)**, the maximal length of a prefix of an optimal agent path before the observer can tell which goal the agent is pursuing. This is a direct temporal/path-length recognition measure more than a decade before `C_{A←B}`.

**Difference:** `wcd` assumes an agent and asks **which goal** it has. `C_{A←B}` asks a stronger model-selection question: when is an **agent-level account itself** warranted over non-agent alternatives, after complexity cost and prospective predictive testing? `C` is also measured in accumulated informational path cost rather than merely number of observed actions.

### 4.4 Active Goal Recognition already established that observer interventions can expedite recognition

**Work:** Maayan Shvo & Sheila A. McIlraith, **“Active Goal Recognition.”** AAAI 2020.

- published: **2020-04-03**;
- DOI: <https://doi.org/10.1609/aaai.v34i06.6551>;
- primary proceedings: <https://ojs.aaai.org/index.php/AAAI/article/view/6551>.

**Related work:** Kevin C. Gall, Wheeler Ruml & Sarah Keren, **“Active Goal Recognition Design.”** IJCAI 2021, <https://www.ijcai.org/proceedings/2021/559>.

**Compared claim:** C6.

**Classification:** `prior_art` for the generic claim that granting the observer agency to sense/act/intervene can expedite recognition; `partial_prior_art` for reducing `C_{A←B}` specifically.

Shvo & McIlraith explicitly give the observer agency to gather evidence and intervene in order to enhance or expedite goal recognition. Gall et al. make observer and subject actions interleave online. Consequently H12 in `informational_time.md` should be read as a new application/test of an established active-recognition principle, not as a new principle by itself.

### 4.5 Dennett's intentional stance and real-patterns program strongly anticipate predictive/compressive justification of agent-level models

**Works:** Daniel C. Dennett, **The Intentional Stance** (1987) and **“Real Patterns”** (1991).

- “Real Patterns” public bibliographic record: *The Journal of Philosophy* 88(1), January 1991, DOI `10.2307/2027085`;
- Tufts archive: <https://dl.tufts.edu/concern/pdfs/wp988x11s>;
- intentional-stance précis: <https://www.cambridge.org/core/journals/behavioral-and-brain-sciences/article/abs/precis-of-the-intentional-stance/7F329FF3E07BFEC4A62154B4E94C01A4>.

**Compared claims:** C4, C5, C7.

**Classification:** `prior_art` for the generic proposition that an intentional/agent-level description earns use by supplying predictive explanatory leverage; `partial_prior_art` for the paper's complexity-charged stopping criterion.

Dennett's intentional stance treats intentional predicates as a predictive/explanatory strategy. The real-patterns line connects higher-level ontology to compressibility and predictive usefulness. This substantially anticipates the paper's broad intuition that “agency” should not be read directly from surface complexity but justified by the usefulness of an agent-level predictive description.

**Difference:** Dennett does not define a directional accumulated-time stopping quantity with preregistered non-agent model classes, registry/search cost, and prospective held-out threshold.

### 4.6 Bayesian inverse planning already formalized intentional-agent inference from observed actions

**Work:** Chris L. Baker, Rebecca Saxe & Joshua B. Tenenbaum, **“Action understanding as inverse planning.”** *Cognition* 113(3), 2009.

- author manuscript issued July 2009: <https://dspace.mit.edu/entities/publication/2e23673d-f720-4720-98bc-6db894ba27e1>;
- DOI: <https://doi.org/10.1016/j.cognition.2009.07.005>.

**Compared claims:** C4, C5.

**Classification:** `prior_art` for probabilistic inference of latent beliefs/goals from behavior under an intentional-agent generative model; `partial_prior_art` for the full recognition criterion.

Baker et al. formalize the intentional stance using Bayesian inverse planning: observed actions update beliefs over hidden mental states under a rational-planning model. This occupies a large part of the “model another source as an action-generating agent” substrate.

**Difference:** the task starts inside an intentional-agent model family rather than testing whether an intentional model defeats maximum-entropy, self-generated, and structured non-agent explanations under a complexity charge.

### 4.7 Agency-versus-randomness detection was empirically tied to nonrandom structure before our proposal

**Work:** Yuan Meng, Thomas L. Griffiths & Fei Xu, **“Inferring Intentional Agents From Violation of Randomness.”** 2017.

- record: <https://collaborate.princeton.edu/en/publications/inferring-intentional-agents-from-violation-of-randomness/>.

**Compared claims:** C4 and the later C7 refinement.

**Classification:** `partial_prior_art`.

The experiments directly compare judgments that binary sequences were generated by agents/non-agents with judgments that the same sequences were nonrandom/random and find strong correspondence. This is relevant because the companion clarification begins from maximum entropy/randomness as a weak null.

**Difference:** the work studies human attribution and subjective randomness, not a normative model-selection criterion, and it does not include the crucial structured-law null that C7 requires.

### 4.8 Predictive coding already models agency detection as Bayesian inference over hidden causes

**Work:** Marc Andersen, **“Predictive coding in agency detection.”** *Religion, Brain & Behavior*.

- first published online: **2017-11-21**;
- DOI: <https://doi.org/10.1080/2153599X.2017.1387170>.

**Compared claims:** C4, C5, C7.

**Classification:** `adjacent_prior_work` / `partial_prior_art`.

Andersen explicitly recasts agency detection as Bayesian predictive inference over hidden causes rather than as a dedicated detector. This strengthens the conclusion that observer-relative priors and prediction are established ingredients of agency detection.

**Difference:** it does not provide the paper's MDL-like complexity charge, structured-law comparator, or recognition-time stopping rule.

### 4.9 Sequential hypothesis testing already supplies the generic first-threshold-crossing recognition-time form

**Work:** Abraham Wald, **“Sequential Tests of Statistical Hypotheses.”** *Annals of Mathematical Statistics* 16(2), 1945.

- publication: **June 1945**;
- DOI: <https://doi.org/10.1214/aoms/1177731118>.

**Compared claim:** C4.

**Classification:** `prior_art` for the generic mathematical idea of accumulating evidence sequentially and stopping when a model/hypothesis threshold is crossed; `partial_prior_art` for `C_{A←B}`.

The formal skeleton of “minimum observation time at which accumulated evidence crosses a prescribed threshold” is classical sequential analysis. Therefore novelty cannot rest on the stopping-time structure itself.

### 4.10 Prequential prediction and MDL already couple model complexity/compression to sequential predictive performance

**Works:** 

- A. P. Dawid, **“Present Position and Potential Developments: Some Personal Views: Statistical Theory — The Prequential Approach.”** 1984, DOI <https://doi.org/10.2307/2981683>;
- Jörg Bornschein, Yazhe Li & Marcus Hutter, **“Sequential Learning Of Neural Networks for Prequential MDL.”** arXiv v1 **2022-10-14**, <https://arxiv.org/abs/2210.07931>;
- Qian Li, Xinyu Mao, Shang-Hua Teng & Guangxu Yang, **“Prediction Under Imperfect Compression: A Theory of Approximate MDL.”** arXiv v1 **2026-06-03 13:03:56 UTC**, <https://arxiv.org/abs/2606.04834>.

**Compared claims:** C4 and C7.

**Classification:** `prior_art` for sequential out-of-sample predictive evaluation and description-length model selection as separate/generic ingredients; `partial_prior_art` for their conjunction inside agent recognition.

Dawid's prequential program makes sequential future prediction the object of statistical assessment. Prequential MDL explicitly evaluates models by cumulative next-step predictive loss. Li et al., less than two months before our cutoff, state the MDL objective as `L(model)+L(data|model)` and prove conditions linking approximate compression/model selection to reliable sequential prediction.

This substantially narrows the broad claim that combining retrospective compression with prospective predictive performance is itself new. The remaining question is whether applying both to the **agent-versus-structured-non-agent recognition boundary and measuring the first crossing in informational causal cost** is a distinct and useful construction.

### 4.11 Contemporary AI-agent work already tests goal-directedness with behavioral and internal evidence

**Work:** Raghu Arghal et al., **“A Behavioural and Representational Evaluation of Goal-Directedness in Language Model Agents.”**

- arXiv v1: **2026-02-09 18:00:28 UTC**;
- <https://arxiv.org/abs/2602.08964>.

**Compared claims:** C4/C7.

**Classification:** `adjacent_prior_work`.

The paper directly addresses when goal-directedness can be attributed to LLM agents and argues that behavioral evidence should be complemented by representational evidence. It is not a model-selection stopping-time framework and requires internal activations, so it does not anticipate the black-box/observer-relative criterion, but it is an important pre-cutoff comparator for any empirical claim of “detecting agency.”

## 5. Post-cutoff works

### 5.1 No material post-cutoff duplicate of `C_{A←B}` was located in this run

Targeted August–September 2026 searches did not locate a paper that defines the same combination of:

1. accumulated observer-relative causal/informational path cost;
2. a complexity-charged agent-versus-non-agent model comparison;
3. prospective held-out or intervention-sensitive advantage;
4. the first threshold crossing as directional recognition time.

Accordingly, this run creates **no `later_non_citing`, `later_overlap`, or `later_derivative` classification for the full `C_{A←B}` claim**.

A September 2026 survey, Mia Lassiter & Brinnae Bent, **“Defining AI Agents: A Compendium of Criteria, Metrics, and Benchmarks”** (arXiv v1 **2026-09-10**, <https://arxiv.org/abs/2609.11018>), is relevant as `later_independent` background on operational agent evaluation, but it is a survey taxonomy rather than a recognition-time construction and is not materially duplicative.

Absence of a located later duplicate is weak search evidence only.

## 6. Classification summary

| Claim | Classification after this audit | Main reason |
|---|---|---|
| C1 path-relative informational time | `partial_prior_art` | causal/process depth and time-like causal order were public earlier; coded recoverable-distinction sum remains a more specific construction |
| C2 actual path vs endpoint/minimum description/distance | `prior_art` at generic level; combination unresolved | George 2026 explicitly separates process trajectory depth from minimum state depth; Bennett/information-distance lineage is older |
| C3 work vs causal depth | `prior_art` | work/span/circuit-depth distinction and George's graph height predate cutoff |
| C4 critical recognition time | `partial_prior_art` | WCD, Wald stopping, intentional stance/inverse planning, and prequential MDL occupy major components; full combination not located |
| C5 observer/directional recognition | `partial_prior_art` | intentional stance, Bayesian inverse planning, predictive agency-detection work make model/observer dependence old; exact directional cost quantity not located |
| C6 active recognition lowers time | `prior_art` at principle level | Active Goal Recognition explicitly gives observer agency to expedite recognition |
| C7 agent must beat strongest structured non-agent law under full cost and prospective test | `partial_prior_art` | ingredients are established, but the exact four-family, complexity-charged criterion was not located |

## 7. What survives as the defensible frontier

After this audit, the paper should **not** imply novelty for any of the following in isolation:

- causal depth as a time-like dependency quantity;
- separating an actual causal process from a minimal endpoint-generating process;
- work versus span/depth;
- length of observed behavior before a goal becomes identifiable;
- intervention to accelerate recognition;
- intentional/agent models justified by predictive usefulness;
- Bayesian inference of latent goals/beliefs from behavior;
- first threshold crossing in sequential evidence;
- description-length model selection plus prospective sequential prediction.

The unresolved combination is narrower:

> **No pre-cutoff antecedent was located in the searched sources that defines a directional agent-recognition stopping quantity as the minimum accumulated cost of recoverable causal distinctions at which a complexity-charged agent model both out-compresses the strongest admissible non-agent alternatives — including structured laws — and preserves a preregistered prospective predictive/intervention advantage.**

This is a negative search result, not a priority claim. The combination itself may still be obvious, independently invented, or present under terminology not found in this run.

The especially close George preprint means the causal-time half of the paper needs stronger citation discipline. Its distinct contribution, if any, is more plausibly the **registry/observer-relative causal accounting plus the critical-recognition construction**, not the generic move from logical/description depth to causal dependency depth.

## 8. Experimental consequences

The audit suggests a sharper benchmark for Experiment 8/9. The paper should compare `C_{A←B}` against component baselines rather than only random/stationary generators:

1. **WCD-like prefix baseline:** number/cost of observations until candidate goals become distinguishable, assuming agency;
2. **Bayesian inverse-planning baseline:** posterior threshold for an intentional model without explicit description-length penalty;
3. **SPRT baseline:** likelihood-ratio stopping time between predeclared agent/non-agent hypotheses;
4. **prequential-MDL baseline:** sequential model selection by cumulative predictive codelength;
5. **structured-law control:** a complexity-matched adaptive but non-agent dynamics model;
6. **full criterion:** retrospective full-cost description length + prospective held-out/intervention test measured in `τ_I` rather than raw observation count;
7. **passive versus active recognition:** equalized communication/observation budgets, to test whether the proposed informational cost changes the established active-recognition result rather than merely reproducing it.

A decisive result is not that the full criterion eventually labels obvious agents correctly. It should show that its additional accounting changes decisions, calibration, false-positive rate, or sample/informational efficiency relative to these established baselines.

## 9. Searches that did not produce a material antecedent

No pre-cutoff source located in this run combined all of the following in one operational definition:

- an event ontology requiring positive-cost recoverable causal distinctions;
- accumulated realized-path cost as the recognition clock;
- agent-versus-maximum-entropy/self/structured-law comparison;
- registry/model/search cost in retrospective evidence;
- held-out or intervention-sensitive prospective advantage;
- a directional observer-dependent first-crossing quantity.

Exact-phrase searches for `critical recognition time` in the agent-modeling sense did not locate an earlier use. This lexical negative has low evidential weight because the relevant ideas occur under `goal recognition`, `intent recognition`, `sequential testing`, `intentional stance`, `agency detection`, `MDL`, and `prequential prediction`.

## 10. Epistemic revision relative to the paper's current framing

This run changes the defensible reading in three material ways:

1. **Causal depth is not an open component.** George's July 27 preprint is temporally prior and unusually close, including the process-versus-state distinction and explicit physical-time framing.
2. **Recognition time is not open at the generic level.** Goal Recognition Design has measured path-prefix length to recognition since 2014, and active recognition has deliberately minimized that latency through intervention since at least 2020.
3. **Compression + prediction is not an open combination in general model selection.** The intentional-stance/real-patterns lineage, sequential testing, prequential prediction, and MDL already connect predictive usefulness, model complexity, and sequential evidence.

The candidate contribution is therefore the **specific cross-domain synthesis and operationalization** described in §7, if it survives direct baseline testing.

## 11. Source/date ledger

| Candidate | Earliest public date used | Status versus our cutoff | Classification | URL |
|---|---:|---|---|---|
| George, *Causal Depth as an Invariant…* | 2026-07-27 | before C1–C7 | `prior_art` / `partial_prior_art` | <https://www.preprints.org/manuscript/202607.1938> |
| Keren et al., *Goal Recognition Design* | 2014-05-10 | before | `prior_art` / `partial_prior_art` | <https://ojs.aaai.org/index.php/ICAPS/article/view/13617> |
| Shvo & McIlraith, *Active Goal Recognition* | 2020-04-03 | before | `prior_art` / `partial_prior_art` | <https://ojs.aaai.org/index.php/AAAI/article/view/6551> |
| Gall et al., *Active Goal Recognition Design* | 2021 | before | `partial_prior_art` | <https://www.ijcai.org/proceedings/2021/559> |
| Dennett, *Real Patterns* | 1991-01 | before | `prior_art` / `partial_prior_art` | <https://dl.tufts.edu/concern/pdfs/wp988x11s> |
| Baker, Saxe & Tenenbaum, *Action understanding as inverse planning* | 2009-07 author manuscript | before | `prior_art` / `partial_prior_art` | <https://dspace.mit.edu/entities/publication/2e23673d-f720-4720-98bc-6db894ba27e1> |
| Meng, Griffiths & Xu, *Inferring Intentional Agents From Violation of Randomness* | 2017 | before | `partial_prior_art` | <https://collaborate.princeton.edu/en/publications/inferring-intentional-agents-from-violation-of-randomness/> |
| Andersen, *Predictive coding in agency detection* | 2017-11-21 | before | `adjacent_prior_work` / `partial_prior_art` | <https://doi.org/10.1080/2153599X.2017.1387170> |
| Wald, *Sequential Tests of Statistical Hypotheses* | 1945-06 | before | `prior_art` / `partial_prior_art` | <https://doi.org/10.1214/aoms/1177731118> |
| Dawid, *The Prequential Approach* | 1984-03 | before | `prior_art` component | <https://doi.org/10.2307/2981683> |
| Bornschein, Li & Hutter, *Prequential MDL* | 2022-10-14 | before | `prior_art` component | <https://arxiv.org/abs/2210.07931> |
| Li et al., *Prediction Under Imperfect Compression* | 2026-06-03 | before | `partial_prior_art` | <https://arxiv.org/abs/2606.04834> |
| Arghal et al., *Behavioural and Representational Evaluation of Goal-Directedness* | 2026-02-09 | before | `adjacent_prior_work` | <https://arxiv.org/abs/2602.08964> |
| Lassiter & Bent, *Defining AI Agents: A Compendium…* | 2026-09-10 | after | `later_independent` background | <https://arxiv.org/abs/2609.11018> |

## 12. Bottom line

The audit rejects a broad originality reading of both halves of `informational_time.md`. A near-contemporaneous paper posted **three days earlier** already makes causal depth, actual process versus minimal state depth, and physical-time comparison its central subject. Separately, decades of goal recognition, intentional-stance modeling, sequential testing, predictive inference, and MDL occupy the components from which critical recognition time is built.

What remains scientifically interesting is narrower and testable: whether **measuring agent-recognition threshold crossing in accumulated recoverable causal cost, while charging full representation/model cost and requiring prospective advantage over a strong structured-law null, yields a useful boundary that established goal-recognition, Bayesian, SPRT, and prequential-MDL baselines do not already provide**.
