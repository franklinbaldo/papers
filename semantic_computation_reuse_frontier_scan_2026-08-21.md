---
type: "Companion Note"
title: "Semantic Computation Reuse — Frontier Scan, 21 August 2026"
description: "External prior-art scan used to narrow the novelty boundary of semantic computation reuse as of 2026-08-21."
tags: [semantic-computation-reuse, prior-art, literature-review, reasoning-memory, trajectory-stitching]
timestamp: 2026-08-21T19:53:00-04:00
---

# Semantic Computation Reuse — Frontier Scan, 21 August 2026

> **Editorial note.** This is a time-stamped frontier scan supporting `semantic_computation_reuse.md`, not an independent scientific contribution and not a systematic review. It records the closest prior art found in an adversarial literature search conducted on 2026-08-21. The search deliberately tried to falsify novelty by looking for work on reasoning memory, experience graphs, trajectory stitching/recombination, reasoning caches, compiled reasoning, state reuse, successor representations, bisimulation, and composable KV caches. Absence of a paper from this note is not evidence that it does not exist.

## 1. Bottom line

The broad idea that external memory can replace some inference is no longer novel. By 2026 the literature contains strong examples of:

- retrieval-augmented and nearest-neighbor language modeling;
- persistent agent experience and procedural memory;
- downstream-utility-aware memory selection;
- graph-structured experience retrieval;
- trajectory stitching and cross-trajectory recombination;
- reasoning compilation into reusable deterministic programs;
- exact or approximate reuse of internal KV computation;
- successor/bisimulation-style definitions of states by their future behavior.

The working novelty boundary for Semantic Computation Reuse should therefore be narrow:

> **Can concrete textual checkpoints from heterogeneous prior LLM computations be composed into a previously unseen ordered path whose causal effect is to reduce fresh LLM inference on a novel held-out task, beyond what is explained by relevant content, procedural guidance, or unordered hints?**

No work found in this scan demonstrated that complete conjunction directly.

## 2. Closest lines of work

### 2.1 Reasoning Memory: procedural knowledge at scale

Wu, Sachan, Yih & Chen (2026), *Procedural Knowledge at Scale Improves Reasoning*, is the closest large-scale reasoning-memory precedent found.

The system decomposes existing reasoning trajectories into roughly 32 million subquestion-subroutine pairs. At inference time the model verbalizes a subquestion, retrieves procedural subroutines, and reasons under them as procedural priors. It beats document, trajectory, template, and compute-matched test-time-scaling baselines across math, science, and coding benchmarks.

**Collision:** strong evidence that reasoning trajectories contain reusable procedural knowledge and that large retrieval memories can outperform extra fresh reasoning.

**Remaining distinction:** the retrieved material guides new reasoning. The proposal under SCR is to preserve and compose concrete textual states so that a path itself displaces part of the new reasoning budget.

Source: https://arxiv.org/abs/2604.01348

### 2.2 ReasoningBank, ProcMEM, and Agent Workflow Memory

ReasoningBank treats experience memory as a dimension of test-time scaling and distills successful and failed trajectories into reusable strategies. ProcMEM learns reusable procedural skills without updating model weights. Agent Workflow Memory induces reusable workflows from trajectories and can reduce later agent steps.

**Collision:** experience, strategy, workflow, and procedural reuse are established targets.

**Boundary:** SCR cannot claim novelty for "learning from prior reasoning" or "reducing repeated steps through memory." Its stronger claim must turn on raw/concrete state composition and causal compute displacement.

Sources:

- https://arxiv.org/abs/2509.25140
- https://arxiv.org/abs/2602.01869
- https://proceedings.mlr.press/v267/wang25bx.html

### 2.3 MemRL and ExpGraph: semantic recall is not functional utility

MemRL uses a two-stage retrieval mechanism in which semantic memory retrieval is filtered/ranked through runtime reinforcement learning and environmental feedback. ExpGraph summarizes trajectories into skills and failure lessons, organizes them in a self-evolving graph, and trains a retrieval copilot from the measured difference in executor performance with versus without retrieved experiences.

**Collision:** the distinction `semantic similarity != downstream usefulness` is clearly occupied. Graph structure plus utility-aware retrieval is also occupied.

**Internal consequence:** `rl_relay_transducers.md` and the ASP cross-paper notes should be aligned with this literature rather than presenting reward-conditioned semantic retrieval as an isolated novelty.

Sources:

- https://arxiv.org/abs/2601.03192
- https://arxiv.org/abs/2605.30712

### 2.4 SE-Agent and offline-RL trajectory stitching

SE-Agent explicitly performs revision, recombination, and refinement across LLM-agent trajectories. It uses cross-trajectory information to expand the reasoning search space and escape local optima.

Trajectory stitching is older in offline RL. In partially observed settings, Hong, Dragan & Levine (ICLR 2024) show that naive stitching can fail and that representations satisfying bisimulation-like conditions can recover useful action-relevant abstractions.

**Collision:** recombining pieces of different trajectories into a new trajectory is not itself novel.

**Boundary:** SCR must show that textual checkpoints act as reusable computation under restricted fresh inference, not merely that cross-trajectory inspiration improves search.

Sources:

- https://papers.nips.cc/paper_files/paper/2025/hash/a911e543a95493ae5004fdc01909043e-Abstract-Conference.html
- https://proceedings.iclr.cc/paper_files/paper/2024/file/1c3d419b754cb4de0a67a453cb28d959-Abstract-Conference.html

### 2.5 CACHE-ED2 and ReaComp: reasoning can be compiled

CACHE-ED2 repositions an LLM as a system-level developer: on a new document format it reasons once, synthesizes a reusable DSL extraction program, and routes later matching documents to deterministic LLM-free execution. The authors report about 2.6x lower cumulative token use over 1,000 documents in their evaluated setting.

ReaComp compiles small sets of reasoning traces into symbolic program synthesizers. The induced solvers can run with zero test-time LLM calls on supported problems and can also complement LLM search while reducing token use.

**Collision:** "pay reasoning once, reuse it later" is directly established.

**Boundary:** SCR asks whether reuse is possible for a novel problem by open composition of previously computed textual states, without first compiling a complete reusable solver or known per-class procedure.

Sources:

- https://www.amazon.science/publications/cache-ed2-compiling-llm-reasoning-into-reusable-extraction-programs-for-document-extraction-at-scale
- https://arxiv.org/abs/2605.05485

### 2.6 C²KV: computation representations can be composed

C²KV learns compressed, position-agnostic KV representations that can be independently generated, stored, and concatenated for non-prefix reuse. The frozen base model can then consume the composed KV memory, with reported large inference speedups in long-context settings.

**Collision:** composable reuse of internal LLM computation is no longer speculative.

**Boundary:** SCR asks whether ordinary text can provide a weaker, portable, black-box equivalent: not exact KV-state reuse, but behaviorally useful textual state interventions that can be composed across historical computations.

Source: https://arxiv.org/abs/2607.17715

### 2.7 Successor representations and bisimulation

Dayan's successor representation defines state features in terms of expected future state occupancy. Bisimulation-based RL abstractions identify states by reward/transition behavior rather than surface identity.

**Collision:** the "mountain" intuition — value a state by what futures it opens — has mature conceptual ancestors. Likewise, `continuation equivalence` resembles predictive/bisimulation-style equivalence and should not be sold as a wholly new state abstraction.

**Boundary:** SCR can use these tools to define behavioral substitutability without claiming their invention.

Sources:

- https://doi.org/10.1162/neco.1993.5.4.613
- https://proceedings.iclr.cc/paper_files/paper/2024/file/1c3d419b754cb4de0a67a453cb28d959-Abstract-Conference.html

## 3. Negative evidence: composition is hard

RECON (2026) evaluates memory systems on compositional long-context tasks including multi-hop chains, cascading invalidations, source conflicts, counterfactual reasoning, temporal constraints, and temporal retrieval. Its strongest reported non-oracle system reaches only 22.4% accuracy.

This does not test SCR directly, but it is useful negative evidence against assuming that useful memory fragments compose reliably. Retrieval and reasoning can each fail even when relevant historical information exists.

Source: https://arxiv.org/abs/2607.16716

## 4. Frontier matrix

| Line | Persistent memory | Cross-trajectory composition | Future-utility ranking | Directly avoids fresh LLM inference | Uses concrete textual checkpoints as reusable states | Novel problem without stored complete procedure |
|---|---:|---:|---:|---:|---:|---:|
| Reasoning Memory | yes | indirectly | retrieval relevance | partially | no, procedural subroutines | yes |
| ReasoningBank / ProcMEM | yes | abstraction-level | yes/implicit | partially | no | partly |
| MemRL | yes | no central claim | yes | partially | episodic experience | yes |
| ExpGraph | yes | graph traversal | yes | reduces steps | no, summarized skills/lessons | yes |
| SE-Agent | per task/search | yes | trajectory quality | no clear substitution claim | trajectory segments | same current task |
| Offline-RL stitching | dataset | yes | value/policy | can avoid exploration | state/history representation | yes |
| CACHE-ED2 | yes | no | routing to compiled program | yes, LLM-free reuse | no | recurring format/class |
| ReaComp | yes | solver induction | solver performance | yes, often zero-token | no | task family covered by induced solver |
| C²KV | yes | yes | trained composition objective | yes | no, internal KV | new context composition |
| SCR proposed | yes | **yes** | later stage | **claim to test** | **yes** | **yes** |

The last row is a proposal, not a result.

## 5. The novelty boundary that survives this scan

The paper should not claim novelty for any one of these ingredients:

- semantic memory;
- nearest-neighbor retrieval;
- downstream-utility-aware retrieval;
- reasoning memories or skills;
- experience graphs;
- trajectory recombination;
- successor/value-based state selection;
- reasoning compilation;
- amortized inference;
- composable internal caches.

The conjunction still worth testing is:

```text
heterogeneous prior LLM computations
        ↓
retain concrete textual checkpoints
        ↓
compose a path never previously observed
        ↓
feed path to black-box LLM
        ↓
strictly limit remaining generation
        ↓
measure whether ordered path preserves success
beyond same-information / procedural controls
```

If the effect disappears under same-fragment shuffle or a concise procedural summary, the stronger "textual computation state" interpretation is unsupported.

## 6. Implications for the repository's existing papers

This scan also sharpens the internal programme.

- `semantic_atlas.md`: navigation/reachability should be positioned relative to RL planning, successor representations, and state-abstraction literature; SCR should not duplicate its map claim.
- `rl_relay_transducers.md`: semantic recall plus reward-conditioned functional ranking now has close public neighbors in MemRL and ExpGraph.
- `agent_successor_policy_*`: successor-style future occupancy has a direct classical lineage and should be used as foundation rather than novelty.
- `informational_time.md`: its distinction between historical causal work and later compact representation is strengthened by concrete 2026 examples of reasoning compilation and cache reuse.
- `semantic_computation_reuse.md`: the defensible contribution is the bridge from those pieces to causal substitution by open textual state composition.

## 7. Search terms and update trigger

Search families used in this frontier pass included variants of:

- reasoning memory / procedural memory / episodic memory;
- reasoning state reuse / intermediate state reuse;
- trajectory stitching / trajectory recombination / trajectory evolution;
- experience graph / graph memory / successor representation / reachability;
- reasoning cache / compiled reasoning / amortized reasoning;
- composable memory / composable KV cache;
- black-box LLM memory / state intervention;
- bisimulation / predictive state equivalence.

This note should be revisited before any novelty claim is submitted. A newly discovered paper satisfying all of the following would materially threaten SCR's current boundary:

1. concrete textual checkpoints from prior LLM reasoning are the reusable unit;
2. checkpoints from heterogeneous trajectories are composed into a previously unseen ordered path;
3. the target task lacks a stored complete solution/procedure;
4. the composed path is evaluated against same-information order/topology controls;
5. fresh inference is causally reduced at matched task performance.
