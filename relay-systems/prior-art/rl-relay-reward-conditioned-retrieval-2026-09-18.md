---
type: "Audit Report"
title: "RL Relay reward-conditioned retrieval prior-art audit — 2026-09-18"
description: "Claim-specific temporal audit of the reward-conditioned retrieval mechanism in RL Relay Transducers, including two-stage semantic/utility retrieval, functional keys, downstream credit, and later CoEvo-Mem overlap."
tags: [rl-relay-transducers, prior-art, retrieval, reinforcement-learning, episodic-memory, credit-assignment, llm-agents]
timestamp: 2026-09-18T14:18:00-04:00
---

# RL Relay reward-conditioned retrieval prior-art audit — 2026-09-18

> **Status:** first claim-specific temporal prior-art audit of §4.2, “Reward-conditioned retrieval plasticity,” in [`rl_relay_transducers.md`](../../rl_relay_transducers.md). This audit reconstructs the public GitHub cutoff of the specific retrieval claim rather than using the paper's file timestamp or the repository creation date. It separates component novelty from novelty of the complete relay-specific mechanism. It does **not** establish patent novelty, exhaustive literature coverage, independent invention, copying, plagiarism, or causal dependence.

## 1. Claims audited

The section is best decomposed into six claims rather than treated as one broad idea:

- **C1 — semantic recall followed by learned utility selection:** frozen semantic/cosine retrieval provides a high-recall top-k candidate set, after which a learned layer ranks candidates according to downstream utility rather than semantic proximity alone;
- **C2 — dual semantic/functional keys:** each memory item retains a frozen semantic key `e_j` plus a separate trainable functional key `k_j`, initialized from the semantic key, so semantic identity remains stable while accessibility can adapt;
- **C3 — signed advantage update of the functional key:** selection alone does not promote a memory. A downstream advantage `A = R - V` moves `k_j` toward a similar query after positive credit and away after negative credit, e.g. `k_j <- norm(k_j + eta A q_t)`;
- **C4 — contextual composite reranking:** the learned ranker can combine semantic affinity, functional affinity, contextual utility, an exploration bonus, and cost, with utility conditioned on model/checkpoint, hop, relay role, and memory version;
- **C5 — attributed delayed credit and evaluation discipline:** when several memories are used, credit should be assigned per retrieval via critic/counterfactual methods rather than blindly copying terminal reward to every selected item; successful/exposed alternatives can form contrastive pairs; learned retrieval state is versioned and frozen during held-out evaluation;
- **C6 — full relay-specific conjunction:** C1-C5 are embedded inside an auditable discrete relay that still makes the final bind/reject/commit decision while the language-model channel can remain frozen and black-box.

The audit is about those mechanism claims. The paper's H6 prediction that the scheme will improve useful-chunk recall/sample efficiency is a falsifiable empirical hypothesis, not an already-demonstrated result.

## 2. Temporal reconstruction of our claim

The reward-conditioned retrieval section was not part of the original RL Relay paper. It was introduced later in a dedicated branch and pull request.

The earliest claim-bearing Git commit located is:

- [`875af6311915236f25c5264e44626f4b88a15f2f`](https://github.com/franklinbaldo/papers/commit/875af6311915236f25c5264e44626f4b88a15f2f) — **2026-08-02 01:40:19 UTC**, `paper: add reward-conditioned retrieval plasticity`.

The commit already contains the material C1-C6 mechanism: frozen cosine recall, trainable functional keys, a contextual utility reranker, UCB-like exploration, advantage-based positive/negative key movement, delayed/counterfactual credit, contrastive training, and the freeze/versioning rule for evaluation.

The branch became unambiguously public through [PR #246](https://github.com/franklinbaldo/papers/pull/246), opened at **2026-08-02 01:40:37 UTC**, eighteen seconds after the commit timestamp. Its public description independently records the same architecture and credit rule.

### Cutoff used

This audit therefore uses the conservative, externally checkable cutoff:

**2026-08-02 01:40:37 UTC** — public PR #246 containing the claim-bearing commit.

Only material publicly available before that instant can be classified as `prior_art`, `partial_prior_art`, or `adjacent_prior_work`. Later material is classified separately even when it is unusually close in time or more developed experimentally.

## 3. Search protocol

The search deliberately did not rely on the phrase “reward-conditioned retrieval,” because older work uses different vocabulary. Sources included arXiv primary records/full text, ACL Anthology, PMLR/ICML, AAAI/IBM publication records, and later-paper full-text citation inspection.

Representative mechanism-level queries included:

- `semantic similarity utility Q-value episodic memory retrieval reinforcement learning`
- `"two-stage retrieval" semantic reward utility memory agent`
- `"reward-conditioned" retrieval memory language model`
- `episodic memory Q value semantic retrieval reinforcement learning agent`
- `trainable retriever frozen black-box language model reward`
- `retrieval ranker downstream reward reinforcement learning candidate passages`
- `stable key rapidly updated value episodic memory reinforcement learning`
- `credit assignment retrieved memories terminal reward provenance`
- `trainable memory key advantage update associative memory`
- `positive negative reward move memory embedding key toward query`
- exact-title / `Franklin Baldo` / `RL Relay Transducers` searches inside later highly overlapping work.

“Not located” below means only that the stated searches and accessible sources did not locate a material antecedent. It is not evidence of nonexistence.

## 4. Pre-cutoff findings

### 4.1 Neural Episodic Control already separates relatively stable representations from rapidly updated reward values

**Work:** Alexander Pritzel et al., **“Neural Episodic Control.”** ICML 2017, PMLR 70.

- public proceedings: <https://proceedings.mlr.press/v70/pritzel17a.html>
- status/date: ICML 2017;
- mechanism: a memory stores keys derived from state representations together with rapidly updated value estimates, allowing value information to change much faster than the representation learner.

**Compared claims:** C2 and C4.

**Classification:** `adjacent_prior_work` for C2 and `partial_prior_art` for the broader stable-representation/plastic-utility separation.

It does **not** anticipate the exact dual-key arrangement in which one frozen semantic vector and one independently trainable functional vector are stored for the same textual memory item.

### 4.2 Reinforced Ranker-Reader predates the two-stage “retrieve broadly, learn to rank for downstream success” structure

**Work:** Shuohang Wang et al., **“R³: Reinforced Ranker-Reader for Open-Domain Question Answering.”** AAAI 2018.

- publication record: <https://research.ibm.com/publications/r3-reinforced-ranker-reader-for-open-domain-question-answering>
- mechanism: a large-scale IR stage produces candidate passages; a ranker learns, jointly with the reader through reinforcement learning, which retrieved passages are useful for downstream answer extraction.

**Compared claims:** C1 and C4.

**Classification:** `partial_prior_art`.

The architecture already establishes that first-stage retrieval can be treated as candidate generation and a learned RL ranker can optimize downstream usefulness. It is not an episodic-memory system, has no frozen semantic/functional dual keys, and does not implement the relay-specific update rule.

### 4.3 REPLUG and PRCA establish trainable retrieval/context adaptation around frozen or black-box language models

**Work:** Weijia Shi et al., **“REPLUG: Retrieval-Augmented Black-Box Language Models.”**

- arXiv v1: **2023-01-30**;
- <https://arxiv.org/abs/2301.12652>.

REPLUG keeps the language model black-box/frozen and trains the retriever using language-model feedback so retrieved documents become more useful to the downstream model.

**Classification:** `partial_prior_art` for C1/C6.

**Work:** Haoyan Yang et al., **“Fitting Black-Box Large Language Models for Retrieval Question Answering via Pluggable Reward-Driven Contextual Adapter.”**

- arXiv v1: **2023-10-23**;
- <https://arxiv.org/abs/2310.18347>.

PRCA inserts a trainable reward-driven contextual adapter between retrieval and a black-box LLM and optimizes it with reinforcement learning.

**Classification:** `partial_prior_art` for C1/C4/C6.

Together these works remove novelty from the generic proposition that a frozen/black-box LLM may be surrounded by a learned retrieval-side component optimized for downstream utility. They do not supply the exact per-memory functional-key rule.

### 4.4 Memento and Memory-R1 make environmental outcome feedback part of memory selection before our cutoff

**Work:** Huichi Zhou et al., **“Memento: Fine-tuning LLM Agents without Fine-tuning LLMs.”**

- arXiv v1: **2025-08-22 07:25:30 UTC**;
- <https://arxiv.org/abs/2508.16153>.

Memento formulates memory/case selection as online reinforcement learning while keeping the underlying LLM unchanged. Episodic memories and environmental feedback update the policy governing which experiences should be reused.

**Compared claims:** C1, C4, C6.

**Classification:** `partial_prior_art`.

**Work:** Sikuan Yan et al., **“Memory-R1: Enhancing Large Language Model Agents to Manage and Utilize Memories via Reinforcement Learning.”**

- arXiv v1: **2025-08-27 12:26:55 UTC**;
- <https://arxiv.org/abs/2508.19828>.

Memory-R1 learns memory-management/retrieval behavior with outcome-driven reinforcement learning over an external memory bank.

**Compared claims:** C1, C4, C6.

**Classification:** `partial_prior_art`.

Neither one alone reproduces the exact semantic-top-k → functional-key rerank pipeline, but both make “memory access should adapt from task reward rather than remain pure semantic similarity” clearly pre-cutoff territory.

### 4.5 MemRL directly anticipates the central two-phase semantic-plus-utility retrieval claim

**Work:** Shengtao Zhang et al., **“MemRL: Self-Evolving Agents via Runtime Reinforcement Learning on Episodic Memory.”**

- arXiv v1: **2026-01-06 17:14:50 UTC**;
- <https://arxiv.org/abs/2601.03192>.

This is the closest pre-cutoff antecedent located for C1. MemRL explicitly criticizes passive semantic matching, keeps the backbone reasoning model stable, and makes the external memory-use policy plastic through reinforcement learning. Its **Two-Phase Retrieval** first uses semantic relevance to filter candidate experiences and then uses learned Q-value utility to identify high-utility memories. The paper explicitly contrasts pure semantic retrieval with semantic-plus-Q utility selection.

**Compared claims:** C1, C4, and the broad stable-core/plastic-memory aspect of C6.

**Classification:** `prior_art` for the broad C1 proposition **“semantic relevance should generate/filter candidates, while task-reward-derived utility should control final memory selection.”** It is `partial_prior_art` for C4/C6.

**Material revision:** the general two-stage semantic-to-utility retrieval idea cannot carry novelty for RL Relay as of our August cutoff. The novelty question must be narrowed below that level.

### 4.6 MemQ predates the broad delayed-credit-to-memory-utility claim

**Work:** Junwei Liao et al., **“MemQ: Integrating Q-Learning into Self-Evolving Memory Agents over Provenance DAGs.”**

- arXiv v1: **2026-05-08 18:30:24 UTC**;
- <https://arxiv.org/abs/2605.08374>.

MemQ propagates downstream credit through a provenance DAG recording which memories were retrieved when new memories were produced, using TD-style/Q-learning machinery and eligibility traces. This directly addresses the fact that useful memory is often visible only after later outcomes.

**Compared claims:** C5 and C4.

**Classification:** `prior_art` for the broad claim **“downstream outcome credit should be propagated back to memories/retrieval decisions rather than assigning utility only from immediate selection.”** `partial_prior_art` for the specific critic/counterfactual/contrastive package in RL Relay.

MemQ does not supply the exact signed update of a separate functional vector key.

## 5. What remains narrower than the located prior art

The strongest residual mechanism is **not** “reward-aware retrieval” in general. That territory is substantially occupied before our cutoff by MemRL, MemQ, Memento/Memory-R1, and older retrieval-ranking work.

The narrower residual is the conjunction:

1. retain a frozen semantic key for reproducible broad recall;
2. store a second per-memory **functional vector key**, initialized from the semantic key;
3. update that functional vector itself with signed downstream advantage so positive outcomes pull it toward similar queries and negative outcomes push it away;
4. combine that vector affinity with contextual utility, exploration, and cost;
5. leave the final bind/reject/commit decision to an auditable relay policy;
6. freeze/version all learned retrieval state during held-out evaluation.

Searches for `trainable memory key advantage update`, `positive negative reward memory embedding toward query`, `functional key semantic key reinforcement learning retrieval`, metric-learning variants, and the closest episodic-memory systems did **not** locate a pre-cutoff source implementing that exact signed per-memory vector-key mechanism.

**Classification:** C2-C3 and the complete C6 conjunction remain `partial_prior_art`, not `prior_art`, on the evidence located in this run. This is a bounded negative result, not a “first” claim.

## 6. Post-cutoff finding: CoEvo-Mem appears about 28 hours later

**Work:** Bowen Ye et al., **“CoEvo-Mem: Co-Evolving Retrieval Policy and Memory Bank for LLM Agents.”**

- arXiv v1: **2026-08-03 06:04:51 UTC**;
- <https://arxiv.org/abs/2608.01739>.

This date is **2026-08-03**, while our conservative public cutoff is **2026-08-02 01:40:37 UTC**. CoEvo-Mem is therefore about **28 hours 24 minutes** later and cannot be classified as prior art against our claim.

The overlap is nevertheless material. CoEvo-Mem keeps the LLM frozen, uses dense/cosine semantic retrieval, learns routing/retrieval behavior from terminal task reward and an advantage-style baseline, assigns outcome-conditioned credit to memories, stores learned memory utility, and lets updated utilities affect later ranking and selection. It therefore converges strongly on the C1/C4/C5 direction.

Full-text searches in this audit did **not** locate `Baldo` or `RL Relay Transducers` in CoEvo-Mem. Conversely, CoEvo-Mem explicitly discusses and cites **MemRL** and **MemQ** as predecessors for utility learning from task feedback and memory selection.

**Classification:** `later_non_citing` for the materially overlapping reward/utility-driven retrieval subsystem.

That classification records only three facts: its public date is later than our cutoff; the mechanism materially overlaps; and no citation to our work was located in the inspected full text. It does **not** imply copying, derivation, plagiarism, or bad faith. The paper's explicit MemRL/MemQ lineage is positive evidence of an already-existing independent technical route to this design space, so no causal dependence on RL Relay is established.

The near-simultaneous timing is scientifically interesting because it shows the design pressure was active: reward-aware retrieval utility was already an emerging research direction, and our defensible distinction should be stated at the narrower mechanism level rather than at the level of “reward-conditioned memory retrieval.”

## 7. Claim-by-claim classification after this audit

| Claim | Classification | Reason |
|---|---|---|
| C1 semantic recall → learned utility selection | `prior_art` | MemRL publicly implements two-phase semantic relevance plus learned Q-value utility before our cutoff; R³ and later retrieval work supply older structural antecedents. |
| C2 frozen semantic key + separate trainable functional vector key | `partial_prior_art` | Stable representation/plastic value and trainable-retriever components predate us, but the exact dual per-memory vector-key mechanism was not located. |
| C3 signed advantage directly moves functional key toward/away from query | `partial_prior_art` | Reward/value learning and metric-learning ingredients predate us; no pre-cutoff source implementing this exact signed vector-key update was located in the searched literature. |
| C4 contextual semantic + functional + utility + exploration + cost reranker | `partial_prior_art` | Semantic+utility ranking is prior art via MemRL; exploration/value/cost components are established individually; the full composite conjunction was not located. |
| C5 delayed attributed credit to retrieval decisions | `prior_art` broadly; `partial_prior_art` for our package | MemQ predates downstream credit propagation through retrieved-memory provenance; critic/counterfactual plus contrastive pairing as specified here was not located as one package. |
| C6 complete relay-specific conjunction | `partial_prior_art` | No single pre-cutoff work located combines C1-C5 with the discrete relay's bind/reject/commit interface and the exact functional-key update. |
| CoEvo-Mem overlapping subsystem | `later_non_citing` | arXiv v1 is ~28h24m after our public PR; material overlap, no citation to our paper located, and no causal inference warranted. |

## 8. Epistemic revision

Before this audit, §4.2 could be read as though the major conceptual step were simply making retrieval plastic from downstream reward while retaining semantic recall. That reading is too broad.

After the audit, the defensible novelty boundary is narrower:

- **not novel in the broad sense:** learned downstream-utility reranking of retrieved candidates; reward-driven memory selection around a frozen LLM; semantic relevance plus Q/value utility; delayed credit to retrieved memories;
- **still unresolved and more specific:** the **dual-key representation** with a frozen semantic vector plus a trainable functional vector, the **signed advantage update of the functional vector itself**, and its integration with contextual utility/exploration/cost inside the discrete relay architecture under explicit held-out freezing/versioning.

No pre-cutoff material antecedent to that exact conjunction was located after the searches recorded above. The proper statement is therefore “no material antecedent to the exact signed dual-key relay mechanism was located in this audit,” not “we were the first.”

## 9. Audit trail and negative searches

Important negative checks preserved from this run:

- no previous claim-specific prior-art audit for reward-conditioned retrieval was located under `audits/prior-art/`;
- no pre-cutoff paper located in the searched corpus implements the exact `frozen semantic key + separate trainable functional vector key + signed advantage moves vector toward/away from query` rule;
- no `Baldo` or `RL Relay Transducers` occurrence was located in the inspected full text of CoEvo-Mem;
- no positive evidence of derivation from our work was located for CoEvo-Mem;
- the later paper's own references explicitly expose a MemRL/MemQ lineage, which must be considered before any dependency inference.

This audit should be revised if an earlier public implementation of the signed functional-key mechanism is found, or if a version/citation history changes the presently verified dates.