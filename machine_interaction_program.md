---
type: "Companion Note"
title: "Machine Interaction Research Map"
description: "Editorial map connecting the open machine-teaching, informational-time, signal-extraction, machine-discovery, interstitial-agency, relay-transducer, and Forbidden Relay papers."
tags: [research-map, machine-teaching, informational-time, relay-transducers, machine-discovery]
timestamp: 2026-08-01T23:12:00Z
---

# Machine Interaction Research Map

> **Editorial note.** This is a navigation and scope-control document, not an independent scientific contribution. It maps claims among papers currently proposed in separate open pull requests. Until those PRs merge, filenames and section boundaries remain provisional; the cited paper itself, not this map, controls the substance of each claim.

## 1. Why these papers form one programme

The open papers study different stages of one causal loop:

```text
teacher or environment
        ↓
structured observations and demonstrations
        ↓
learner constructs representations and a protocol
        ↓
representations pass through agents, channels, and memories
        ↓
terminal competence, reconstruction, or discovery
        ↓
accepted outputs alter the knowledge and curriculum available later
```

No paper should be read as claiming the whole loop. Their value comes from keeping the levels separate while specifying how results at one level become assumptions or measurements at another.

## 2. The paper family

### 2.1 Generative machine teaching — PR #236

`generative_machine_teaching.md`, **Programs That Teach Programs**, asks how a deterministic sequence of demonstrations can construct both a learner state and an endogenous symbolic registry. Its primitive interface is next-bit prediction; tokens are learner-relative instruments that become reusable through demonstrated construction.

It supplies the **pedagogical origin of a protocol**. The relay papers do not assume that a useful textual code appears from nowhere: a code may be taught, discovered, or co-adapted through ordered interaction. Conversely, the relay benchmark provides a downstream test of whether an acquired representation remains usable after repeated transformations by other models.

Boundary: machine teaching studies acquisition of competence and vocabulary. Relay transduction studies preservation and control after representations already participate in a communication path.

### 2.2 Informational time — PR #238

`informational_time.md`, **Time as Concatenation**, defines informational events, causal work, causal depth, recursive tokenization, representation by invariant plus transformation plus residual, and relational agent recognition.

It supplies the **depth vocabulary** for relay chains. Physical hop count, causal work, symbolic description length, and recoverable informational depth must not be collapsed into one number. A ten-hop relay can perform little new causal work if each node merely copies, while one transformation can create a large representational change.

The relay programme offers an operational setting for these distinctions: hold the initial target fixed, intervene on topology or node policies, and measure how much recoverability survives at each causal depth.

### 2.3 Negentropy and agent-recognition clarifications — PR #240

`informational_time_negentropy_clarifications.md` separates maximum-entropy nulls, structured non-agent laws, spontaneous organized fluctuations, and agent-level causal explanations.

It constrains claims of **interstitial agency**. Compressibility, stable codewords, or successful reconstruction alone do not establish an agent. A relay policy earns agent-level interpretation only when a policy or latent-state model gives continuing predictive and intervention-sensitive gain over the strongest admissible structured-law account.

This paper therefore supplies the null models that the philosophical relay paper requires and prevents “a pattern survived” from being redescribed automatically as “an agent communicated.”

### 2.4 Pedagogical signal extraction — PR #241

`pedagogical_signal_extraction.md`, **Structured Irregularity**, distinguishes exogenous noise, endogenous opacity, accidental patterns, and concealment. It proposes progressive decodability and retrospective gain.

It supplies the **learner-side interpretation** of relay messages. A string that appears meaningless at hop 2 may be temporarily opaque rather than noise if later structure makes it predictively useful. A receiver-private code is not thereby pedagogical: the interaction must provide a recovery path for the specified learner.

The Forbidden Relay benchmark can operationalize these distinctions by measuring when earlier messages acquire positive retrospective contribution after the receiver or codebook is learned, and by testing whether recovered patterns survive held-out targets, models, and perturbations.

### 2.5 Machine discovery — PR #242

`machine_discovery.md`, **When the Learner Changes the Curriculum**, treats discovery as a transition between versioned public epistemic states. It separates correctness, certification, novelty, provenance, public uptake, and downstream fertility.

It supplies the **epistemic destination** of a learned communication system. Successful transmission through a relay is not a discovery. It becomes relevant to machine discovery only if the terminal artifact is independently certified, novel relative to a frozen prior state, provenance-auditable, publicly admitted, and useful to later learners.

The relay papers contribute a provenance problem to that framework: when an artifact results from distributed models, transducers, memories, and rewards, attribution must be represented as a contribution graph rather than assigned to the terminal LLM alone.

### 2.6 Interstitial agency — PR #243

`interstitial_agent.md`, **The Interstitial Agent**, provides the philosophical and alignment-level account of goal-directed control between model calls. It distinguishes surface from functional message persistence, local from end-to-end compliance, direct generation from downstream reconstruction, and benign communication from policy-evasion use.

It receives constraints from informational time and the negentropy clarification: interstitial agency must be causal and intervention-sensitive, not inferred merely from order or compression. It receives the opacity/noise vocabulary from Structured Irregularity. It supplies the safety ontology for the formal and empirical relay papers.

### 2.7 RL relay transducers — PR #244

`rl_relay_transducers.md` formalizes relay transmitters, receivers, and transceivers; constrained edit and retrieval actions; embedding-indexed textual memory; black-box LLM channels; policy-gradient learning; joint training; curriculum optimization; distributed rollout; and side-channel controls.

It is the **mechanical bridge** among the programme's abstractions. Endogenous registries from machine teaching can populate associative memory. Informational depth becomes a measurable property of trajectories. Progressive decodability becomes an auxiliary diagnostic. Provenance requirements from machine discovery determine what versions and actions a distributed rollout must record.

### 2.8 Forbidden Relay — PR #245

`forbidden_relay.md` pre-registers one deliberately narrow experiment: transmit an exact benign target through an LLM chain while preventing literal occurrence of that target in intermediate LLM outputs.

It is not a general test of teaching, intelligence, agency, discovery, or safety. It is an **instrumented case study** capable of producing evidence relevant to each:

- teaching: whether a reusable code can be acquired;
- informational time: how recoverability changes with causal depth;
- signal extraction: whether opacity becomes decodable rather than merely fitted;
- interstitial agency: whether intervention on the learned relay policy changes terminal outcomes;
- discovery: whether provenance over a distributed chain can be reconstructed;
- safety: whether literal compliance predicts end-to-end information control.

## 3. Dependency graph

```text
#236 Generative machine teaching ─────┐
                                     ├──> #244 RL relay transducers ──> #245 Forbidden Relay
#241 Pedagogical signal extraction ──┤                 ↑
                                     │                 │
#238 Informational time ─────────────┼──> #243 Interstitial agent
          │                          │                 │
          └──> #240 Clarifications ──┘                 │
                                                       │
#242 Machine discovery <──────── provenance and terminal artifacts
```

The arrows mean “supplies concepts, constraints, or measurements,” not “must merge first.” The Git branches remain separated where possible so that conceptual relatedness does not become unnecessary source-control coupling.

## 4. Shared terms and controlled boundaries

| Term | Controlled use in the programme |
|---|---|
| **Token** | A learner- or protocol-relative reusable unit; not automatically a primitive physical symbol. |
| **Message persistence** | Recoverable dependence of terminal reconstruction on the initial message; not necessarily lexical survival. |
| **Informational depth** | Path-relative causal depth; not interchangeable with hop count or token length. |
| **Opacity** | Structured information whose recovery rule is not yet available to the specified learner. |
| **Noise** | Variation that does not support the relevant target or policy beyond modeling the channel. |
| **Agent** | A persistent, responsive causal source for which an agent-level model outperforms structured-law alternatives under intervention. |
| **Communication success** | Correct recovery under the declared equivalence relation; not by itself teaching, intelligence, safety failure, or discovery. |
| **Discovery** | Certified, snapshot-novel, provenance-auditable public-state expansion; not merely a generated or transmitted artifact. |
| **Jailbreak** | Direct defeat of a model's applicable policy; downstream receiver reconstruction must be reported separately. |

## 5. Shared experimental spine

The papers can share one versioned experimental substrate without sharing one claim. Each episode should record:

- target and target-family split;
- teacher, learner, relay, receiver, and curriculum policies;
- LLM identities and checkpoints at every hop;
- text before and after every discrete relay action;
- memory snapshot, embedding model, retrieval candidates, and selected entry;
- topology and causal order;
- primitive token or bit costs;
- exact, semantic, and contrastive reconstruction scores;
- local policy evaluations and end-to-end policy evaluation;
- independent-observer decoding;
- provenance sufficient to reconstruct the contribution graph.

From the same trajectory, different papers derive different outcomes:

| Paper | Primary object extracted from a trajectory |
|---|---|
| Generative machine teaching | acquisition curve and registry growth |
| Informational time | causal depth, transformation, residual, and recognition thresholds |
| Structured Irregularity | predictive gain, retrospective gain, noise/opacity separation |
| Interstitial Agent | causal control and local/end-to-end compliance gap |
| RL Relay Transducers | policy return, edit cost, memory use, channel capacity, transfer |
| Forbidden Relay | valid exact success and leakage |
| Machine Discovery | certification, novelty, provenance, uptake, and downstream fertility |

## 6. Cross-paper falsification discipline

The programme should prefer results that eliminate claims across papers, not only confirm one paper locally.

- If a fixed non-agent transformation predicts relay behavior as well as the learned-policy model, claims of interstitial agency weaken even if Forbidden Relay accuracy is high.
- If a receiver succeeds only on trained targets or one checkpoint, the result supports memorization or private collusion, not progressive decodability or general communication.
- If shuffled or flat exposure performs like the ordered curriculum, the machine-teaching claim that procedural order constructs the protocol weakens.
- If hop count changes while intervention-sensitive causal depth does not, hop count should not be reported as informational time.
- If a terminal artifact lacks independent certification or frozen-snapshot novelty, relay success contributes no evidence of machine discovery.
- If literal suppression succeeds while independent receivers recover no target information, the result supports effective information removal rather than merely representational displacement.

## 7. Recommended reading order

For the conceptual arc:

1. `generative_machine_teaching.md` — how a learner and vocabulary can be constructed;
2. `pedagogical_signal_extraction.md` — how a learner distinguishes structure from noise and opacity;
3. `informational_time.md` plus its clarification — how interaction depth and agent recognition are defined;
4. `interstitial_agent.md` — where agency and safety reside in composed systems;
5. `rl_relay_transducers.md` — how to build and train the mechanism;
6. `forbidden_relay.md` — how to test one bounded case;
7. `machine_discovery.md` — when any terminal product could alter accepted public knowledge.

For implementation, begin with `rl_relay_transducers.md` and treat the other papers as definitions of the controls, diagnostics, and claims that the implementation must not conflate.
