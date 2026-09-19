---
type: "Audit Report"
title: "Semantic Atlas inverse-atlas / route-conditioned memory prior-art audit — 2026-09-17"
description: "Claim-specific temporal audit of the Semantic Atlas inverse-atlas proposal: semantic-state memory, incoming-trajectory conditioning, planned outgoing-direction conditioning, lexical retrieval, and verified generation."
tags: [semantic-atlas, prior-art, retrieval, memory, trajectory, planning, rag, speculative-decoding]
timestamp: 2026-09-17T19:57:00-04:00
---

# Semantic Atlas inverse-atlas / route-conditioned memory prior-art audit — 2026-09-17

> **Status:** claim-specific revision/supplement to `audits/2026-08-09-semantic-atlas-frontier-scan.md`. That earlier scan correctly treated DReSD as prior work for dense semantic retrieval, but its bounded negative conclusion for the joint inverse-Atlas claim is now too weak: this round located two materially closer pre-cutoff mechanisms and one additional near-cutoff memory paper. This record preserves the older audit rather than silently replacing it. It does not establish patent novelty, exhaustive literature coverage, causal independence, plagiarism, or derivation.

## 1. Claim audited and public cutoff

The object audited here is **not** the whole Semantic Atlas paper and should not inherit the manuscript's earlier 2026-08-08 cutoff. It is the later **inverse-atlas / route-conditioned lexical memory** proposal developed on PR #277.

### 1.1 Earliest GitHub evidence located

The earliest implementation commit located is:

- [`9a64fddfef27ab211ead5781a1b9c396cebc8e8f`](https://github.com/franklinbaldo/papers/commit/9a64fddfef27ab211ead5781a1b9c396cebc8e8f), `feat(inverse-atlas): add inference memory and route-conditioned lexical lookup`, authored/committed **2026-08-09 00:47:56 UTC**.

That commit already implements a non-parametric `InferenceMemory` over SRF states, optional `desired_delta`, weighting by alignment between a stored observed transition and the desired outgoing displacement, a local token distribution, and generator proposals re-embedded and verified against a target SRF state.

The first unambiguous public GitHub surface located for the **full stated claim** is PR [`#277`](https://github.com/franklinbaldo/papers/pull/277), opened **2026-08-09 00:48:47 UTC**. Its opening body explicitly states:

- memory keyed by causal SRF state;
- history-conditioned retrieval using the direction from which the conversation arrived;
- route-conditioned retrieval using alignment between observed semantic displacement and the planner's desired local displacement;
- the novelty boundary as an inverse atlas for an **independently planned semantic route**;
- the conditional object `P(token/block | q_t, incoming_velocity, desired_delta, local lexical evidence)`;
- re-embedding/verification of generated candidates rather than assuming a semantic midpoint.

A later commit, [`17bbab599b823c234fa60ce93bc2b834e99f0f6f`](https://github.com/franklinbaldo/papers/commit/17bbab599b823c234fa60ce93bc2b834e99f0f6f), explicitly adds incoming-trajectory conditioning in code at 00:59:32 UTC, but the PR opening text already made the incoming-trajectory component public.

**Conservative cutoff used for temporal classification of the joint claim: `2026-08-09 00:48:47 UTC` (PR #277 creation).**

The commit timestamp 51 seconds earlier is recorded as implementation evidence, but this audit does not assume that a local Git commit timestamp alone proves public availability before the PR surface existed.

## 2. Claim decomposition

The joint proposal is decomposed before searching so that prior art for one component is not mistaken for anticipation of the entire combination.

| ID | claim component |
|---|---|
| **A** | store prior inference experiences in a non-parametric memory indexed by semantic state and retrieve nearby experiences |
| **B** | condition retrieval on the **incoming trajectory/history**, so equal current states can retrieve differently depending on how they were reached |
| **C** | condition retrieval on an **independently planned desired outgoing semantic displacement/route**, rewarding stored transitions aligned with the desired next direction |
| **D** | use retrieved experiences to construct a local lexical/token/block distribution or generation guidance |
| **E** | express current state, history and route in a calibrated cross-model Semantic Reference Frame rather than one model's raw latent coordinates |
| **F** | treat generated lexical realizations as proposals and **re-embed/verify** them against the desired semantic target rather than assuming that lexical or vector interpolation is faithful |

A source may be prior art for B or C while remaining only partial prior art for the joint A–F combination.

## 3. Search protocol

This round deliberately expanded beyond the terminology used in the August frontier scan. Representative queries included:

- `"route-conditioned retrieval" language model semantic trajectory desired direction`
- `"trajectory-aware retrieval" language model kNN semantic memory generation`
- `"direction-aware retrieval" embeddings language model semantic goal`
- `"semantic trajectory" retrieval generation planned route language model`
- `"desired displacement" retrieval semantic route language model`
- `"future direction" retrieval language model kNN`
- `"retrieval augmented" trajectory language generation planning`
- `"semantic planning" retrieval language model latent route`
- `goal-directed traversal embedding space retrieval semantic goal vector`
- `trajectory-conditioned memory retrieval future state LLM`
- `route-specific query rewrites trajectory-conditioned feedback memory LLM`

Sources consulted included arXiv, ACL Anthology, MDPI proceedings/DOI pages, author/project pages, DBLP for date cross-checking, and GitHub where relevant. Search indexes and secondary summaries were used for candidate discovery only; material classifications below rely on primary proceedings/preprint records whenever available.

## 4. Findings

### 4.1 Tracert-RAG — desired-direction semantic traversal is pre-cutoff prior art

**Siu-Him Zhang, Jhe-Wei Lin. _Tracert-Retrieval-Augmented Generation: Boosting Multi-Hop Retrieval-Augmented Generation with Direction-Aware Graph Traversal._ Engineering Proceedings 120(1):47.**

- Primary proceedings page: <https://www.mdpi.com/2673-4591/120/1/47>
- DOI: <https://doi.org/10.3390/engproc2025120047>
- Earliest public disclosure verified: **presented at ICKII 2025, 22–24 August 2025**; the primary proceedings page records the presentation and the official online publication date **2026-02-05**.
- Compared components: **C**, partly A/D.
- **Classification for component C: `prior_art`.**
- **Classification for the joint inverse-Atlas A–F claim: `partial_prior_art`.**

Tracert-RAG predicts a **semantic goal vector** from a query, constructs a local graph over document embeddings, and retrieves by greedy traversal toward that goal. Crucially, its edge cost combines local semantic distance with an angular penalty for deviation from the vector pointing from the current node toward the goal. In other words, retrieval is explicitly conditioned on a desired semantic direction/trajectory in embedding space.

That materially anticipates the broad mechanism "prefer retrieved items/transitions whose semantic motion aligns with the desired outgoing direction." The inverse-Atlas implementation cannot claim novelty merely for using an outgoing semantic vector to steer retrieval.

The remaining difference is substantive but narrower. Tracert-RAG retrieves document chunks along a query-to-goal path; it does not store model inference transitions as local lexical experiences, does not condition on incoming semantic velocity, does not use a calibrated cross-model SRF, and does not define a local next-token/block distribution from matched transitions.

### 4.2 Wu et al. — trajectory-aware memory retrieval plus future-state steering is pre-cutoff partial prior art

**Hongyan Wu, Zhiliang Tian, Zhen Huang, Tengyue Hu, Linbo Qiao, Yifu Gao, Feng Liu, Dongsheng Li. _Emotion Trajectory-aware Retrieval for Markov-driven Emotion Anticipation in LLM-based Emotional Support Conversation._ Findings of ACL 2026.**

- ACL Anthology: <https://aclanthology.org/2026.findings-acl.2127/>
- DOI: <https://doi.org/10.18653/v1/2026.findings-acl.2127>
- Earliest primary public date verified in this round: **July 2026** proceedings record. The exact day of first Anthology publication was not recovered; DBLP's record was already updated on **2026-08-04**, independently confirming public indexing before our 2026-08-09 cutoff.
- Compared components: **A, B, D**, and a close analogue of future-directed guidance.
- **Classification: `partial_prior_art`.**

This paper builds a dynamic emotion memory and retrieves by a hierarchy combining ordinary semantic similarity with **whole emotion-trajectory alignment**, rather than only the current emotional state. It then uses retrieved trajectories to estimate a future emotion state and uses that anticipated state to steer LLM strategy generation.

This is a material predecessor for the claim that memory retrieval should depend on **how the current state was reached** and that retrieved trajectories can support future-state-guided generation. It sharply narrows component B: trajectory/history-conditioned memory retrieval for LLM generation is not novel in the abstract.

It does not, on the inspected primary record, condition retrieval on an independently supplied desired semantic displacement selected by a separate route planner. Its state space is an emotion trajectory, not a calibrated cross-model SRF, and the retrieved object supports strategy planning rather than a local lexical token/block distribution.

### 4.3 CoEvo-Mem — route-specific retrieval and trajectory-conditioned memory feedback just before our cutoff

**Bowen Ye, Yongchao Xu, Zhijian Li, Xiang Yin, Junkai Ma, Wenzhao Li. _CoEvo-Mem: Co-Evolving Retrieval Policy and Memory Bank for LLM Agents._**

- Primary source: <https://arxiv.org/abs/2608.01739>
- arXiv v1: **2026-08-03 06:04:51 UTC**, six days before our cutoff.
- Compared components: A/B and adaptive route-specific retrieval.
- **Classification: `partial_prior_art`.**

CoEvo-Mem uses a frozen LLM to generate **route-specific query rewrites and a routing prior**, then learns a residual router; task outcomes assign credit to routing decisions while **trajectory-conditioned feedback** updates memory values and graph relations. The retrieval policy and memory bank therefore co-evolve through the interaction trajectory.

This is closer than the August 9 Semantic Atlas scan recognized to the broad idea that retrieval and memory should be route/trajectory-sensitive rather than a flat semantic kNN lookup. It is not the same geometric claim: its routes are retrieval/query routes and its trajectory-conditioned signal updates memory utility/relations, rather than comparing an observed semantic transition vector with an externally planned `desired_delta` in a common SRF. It nevertheless removes room for broad novelty language around "route-specific memory retrieval" or "trajectory-conditioned memory" by themselves.

### 4.4 DReSD — semantic non-parametric lexical drafting with verification is prior component work

**Milan Gritta, Huiyin Xue, Gerasimos Lampouras. _DReSD: Dense Retrieval for Speculative Decoding._ Findings of ACL 2025.**

- arXiv: <https://arxiv.org/abs/2502.15572>
- ACL Anthology: <https://aclanthology.org/2025.findings-acl.1017/>
- arXiv v1: **2025-02-21 16:32:28 UTC**.
- Compared components: **A/D/F** at a broad mechanism level.
- **Classification: `partial_prior_art`.**

DReSD uses approximate nearest-neighbor search over contextualized token embeddings to retrieve semantically relevant token sequences for speculative decoding, with the target model verifying drafts. This was already identified in the 2026-08-09 frontier scan and remains an important boundary: semantic non-parametric retrieval for lexical continuation and subsequent model verification predate the inverse-Atlas proposal.

DReSD does not add incoming trajectory or a separately planned outgoing semantic route, so it does not anticipate B/C/E together.

### 4.5 RaDA — planned trajectory plus dynamically retrieved exemplars is adjacent earlier work

**Minsoo Kim, Victor Bursztyn, Eunyee Koh, Shunan Guo, Seung-won Hwang. _RaDA: Retrieval-augmented Web Agent Planning with LLMs._ Findings of ACL 2024.**

- ACL Anthology: <https://aclanthology.org/2024.findings-acl.802/>
- DOI: <https://doi.org/10.18653/v1/2024.findings-acl.802>
- Verified publication: **August 2024**; Adobe Research gives **2024-08-11**.
- Compared components: planned trajectory + retrieval during execution.
- **Classification: `adjacent_prior_work`.**

RaDA first constructs a high-level task-decomposition trajectory, then traverses it while dynamically retrieving exemplars to synthesize actions. This establishes an earlier architecture in which a planned route/trajectory and retrieval are explicitly coupled during generation/action execution. It is not semantic-vector directional retrieval and is therefore not a direct anticipation of component C, but it is important context against overly broad "retrieval follows a plan" novelty language.

### 4.6 GRIP — retrieval decisions inside the autoregressive trajectory are adjacent earlier work

**Bo Li, Mingda Wang, Gexiang Fang, Shikun Zhang, Wei Ye. _Retrieval as Generation: A Unified Framework with Self-Triggered Information Planning._ ACL 2026.**

- arXiv: <https://arxiv.org/abs/2604.11407>
- ACL Anthology: <https://aclanthology.org/2026.acl-long.196/>
- arXiv v1: **2026-04-13 12:53:17 UTC**.
- Compared components: retrieval coupled to evolving generation trajectory.
- **Classification: `adjacent_prior_work`.**

GRIP lets a model decide when to retrieve, how to reformulate queries and when to stop within one autoregressive trajectory. It supports dynamic multi-step evidence integration but does not implement the geometric incoming/outgoing route-conditioning of the inverse Atlas. It is therefore context rather than material anticipation of the narrow claim.

## 5. Later work after our cutoff

### 5.1 VESTA — later independent convergence on route-conditioned retrieval-and-verification loops

**Can Zhang et al. _From Intent to Evidence: Policy-Steered Multi-Strategy Retrieval for Long-Video Agents._**

- Primary source: <https://arxiv.org/abs/2608.31005>
- arXiv v1: **2026-08-31 15:55:48 UTC**, after our 2026-08-09 cutoff.
- Compared idea: route-conditioned retrieval, verification, persistent structured evidence, iterative re-query.
- **Classification: `later_independent` for the broad architectural convergence; not equivalent to the inverse-Atlas A–F claim.**

VESTA describes a "route-conditioned acquire–verify–consolidate loop": an intent router chooses an evidence-acquisition policy over a shared scene index, retrieved regions remain provisional until verified, a ledger preserves structured observations, and the reasoner can re-query as evidence needs evolve.

The inspected arXiv text contained no occurrence of `Semantic Atlas` or `Baldo`. That supports only the narrow factual statement that **no citation/acknowledgment was located in the searchable paper text**; it does not prove causal independence, copying, non-copying, or awareness.

The mechanism is also materially different. VESTA's "route" is an acquisition-policy route (`focused`, `recall`, `contrastive`), not an outgoing vector in semantic state space. It is therefore recorded as a later architectural convergence rather than a later duplication of the specific claim.

No post-cutoff source located in this round was strong enough to classify as `later_derivative` or as a full `later_non_citing` reproduction of A–F.

## 6. Revision of the 2026-08-09 frontier assessment

The earlier file `audits/2026-08-09-semantic-atlas-frontier-scan.md` recorded the bounded negative result:

> no inspected source supersedes the route-conditioned inverse-Atlas claim

That statement was appropriately bounded to its inspected source set, but it should **not** be reused today as evidence that the constituent route/trajectory mechanisms were unoccupied. This round changes the epistemic picture:

1. **Outgoing semantic-direction-conditioned retrieval is occupied prior art** at least as broadly as Tracert-RAG's goal-vector / angular-alignment traversal.
2. **History/trajectory-aware memory retrieval used to estimate a future state and steer LLM generation is occupied prior art** in Wu et al.'s emotional-support domain.
3. **Route-specific retrieval coupled to trajectory-conditioned memory feedback is occupied prior art** in CoEvo-Mem, published only six days before our cutoff.
4. **Dense semantic lexical retrieval plus target-model verification** was already occupied by DReSD, as the old scan correctly recorded.

Accordingly, novelty language for the inverse Atlas must not rest on A, B, C, or F separately.

## 7. Surviving bounded combination claim

After the searches above, **no pre-cutoff source was located that combines all of the following in one mechanism**:

1. a calibrated **cross-model semantic reference frame** for the current state;
2. local memory of prior **inference transitions** plus their lexical realizations;
3. separate representation of **incoming semantic trajectory**;
4. an **independently planned desired outgoing semantic displacement**;
5. retrieval weighting that explicitly matches stored transition vectors to that desired displacement;
6. a local lexical/token/block distribution or generated realization from those matched memories; and
7. re-embedding/verification against the desired semantic target.

This is a **bounded negative search result, not a first-in-the-world claim**. The combination is also more specific than the code in the first `9a64fdd...` commit: the opening PR text supplies the full incoming-trajectory + desired-route claim, while the code added explicit incoming-trajectory weighting shortly afterwards. Future writing should therefore distinguish the conceptual combination from the exact implementation revision used in an experiment.

A defensible novelty boundary is now:

> not "trajectory-aware retrieval" or "direction-aware retrieval", but whether **calibrated cross-model state + incoming trajectory + independently planned outgoing displacement** can serve as a reusable inverse semantic atlas whose local transition memories improve lexical realization beyond strong trajectory-, direction-, and semantic-retrieval baselines.

That boundary is experimentally testable and substantially narrower than the August formulation.

## 8. Baselines implied by the audit

Any future empirical claim for the inverse Atlas should compare against at least:

- ordinary semantic kNN / retrieval memory;
- DReSD-like dense semantic lexical retrieval + verifier;
- a Tracert-RAG-like **desired-direction / goal-vector** condition without incoming history;
- a trajectory-history condition inspired by Wu et al. without an independent desired route;
- a route/routing-memory condition inspired by CoEvo-Mem;
- full inverse Atlas with `q_t + incoming_velocity + desired_delta`;
- ablations removing the calibrated SRF, incoming trajectory, desired route, and re-embedding verification one at a time.

A positive result against position-only kNN is no longer sufficient evidence for the distinctive claim.

## 9. Search ledger and negative evidence

Important negative/near-negative searches were preserved because future rounds should not simply repeat them:

- no pre-cutoff source located under the searched terms that explicitly conditions **lexical memory retrieval simultaneously on current semantic location, incoming trajectory, and an externally planned outgoing semantic vector**;
- no pre-cutoff source located that adds this exact conditioning inside a **calibrated cross-model reference frame**;
- no source inspected in this round supplied the full A–F chain;
- searches for later convergence found VESTA after the cutoff, but its route variable is a retrieval-policy category rather than a semantic displacement vector.

These results mean only "not located under this query/source set". Citation-neighbor expansion from Tracert-RAG, Wu et al., CoEvo-Mem and DReSD is the highest-value next search direction.

## 10. Classification summary

| work | earliest public date used | classification | claim effect |
|---|---:|---|---|
| Tracert-RAG | 2025-08-22 presentation; 2026-02-05 online proceedings | `prior_art` for C; `partial_prior_art` for joint A–F | removes broad novelty of desired semantic-direction-conditioned retrieval |
| Wu et al., Emotion Trajectory-aware Retrieval | July 2026 proceedings | `partial_prior_art` | removes broad novelty of trajectory/history-aware memory retrieval for future-state-guided LLM generation |
| CoEvo-Mem | 2026-08-03 06:04:51 UTC | `partial_prior_art` | occupies route-specific retrieval + trajectory-conditioned memory adaptation as broad mechanisms |
| DReSD | 2025-02-21 16:32:28 UTC | `partial_prior_art` | occupies dense semantic lexical retrieval + verifier |
| RaDA | 2024-08 | `adjacent_prior_work` | planned trajectory + dynamic exemplar retrieval already established architecturally |
| GRIP | 2026-04-13 12:53:17 UTC | `adjacent_prior_work` | retrieval control coupled to autoregressive trajectory is established |
| VESTA | 2026-08-31 15:55:48 UTC | `later_independent` | later convergence on route-conditioned retrieval/verify loop; no Semantic Atlas/Baldo citation located; route semantics differ |

## 11. Epistemic conclusion

The material change from the August frontier scan is **narrowing, not invalidation**. The inverse-Atlas proposal still has an unresolved combination claim, but several of the intuitions that made it sound distinctive are already independently represented in the pre-cutoff literature.

The strongest current formulation is therefore comparative:

> Can a calibrated common semantic frame, with both incoming-history and independently planned outgoing-direction conditioning, add measurable value over existing semantic, trajectory-aware, direction-aware, route-specific and verifier-backed retrieval methods?

That is the claim future experiments should earn. No stronger originality statement is supported by this search round.
