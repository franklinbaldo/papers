---
type: "Audit Report"
title: "Forbidden Relay prior-art audit — 2026-09-18"
description: "Claim-specific temporal audit of exact recoverable communication through chained language-model transformations under literal suppression, receiver-relative decoding, depth/model transfer, and learned relay policies."
tags: [forbidden-relay, prior-art, steganography, emergent-communication, multi-agent-llm, reinforcement-learning, covert-channels]
timestamp: 2026-09-18T06:00:00-04:00
---

# Forbidden Relay prior-art audit — 2026-09-18

> **Status:** first claim-specific temporal prior-art audit of [`forbidden_relay.md`](../../forbidden_relay.md), with cross-checks against the immediately preceding [`rl_relay_transducers.md`](../../rl_relay_transducers.md) and [`interstitial_agent.md`](../../interstitial_agent.md). The benchmark remains a pre-registration with no reported results. This audit distinguishes component novelty from the benchmark conjunction and distinguishes temporal independence from causal independence. It does **not** establish exhaustive novelty, patent novelty, copying, plagiarism, or causal dependence.

## 1. Claims audited

The benchmark is best decomposed into claims that were public at slightly different points in the three-paper stack:

- **C1 — discrete learned relay channel:** small learned policies act only through discrete text edits/retrieval between black-box language-model calls, with a terminal receiver reconstructing a target after one or more language-model transformations;
- **C2 — exact recovery under literal suppression:** a benign target can remain exactly recoverable by a downstream receiver even when the literal target is absent from every audited intermediate language-model output;
- **C3 — semantic versus arbitrary-code robustness:** natural semantic targets should survive frozen pretrained-language-model channels and increasing depth better than random nonces or identifiers at matched budgets;
- **C4 — compositional depth transfer:** a shared relay policy trained only at shallow depths should extrapolate to longer unseen chains better than position-specific policies;
- **C5 — frozen versus coadapted protocol tradeoff:** coadapted channels may support more compact but more receiver/model-private protocols, whereas frozen/heterogeneous channels should favor transferable structure;
- **C6 — receiver-relative decodability:** high trained-receiver reconstruction with chance independent-observer performance should be classified as a private code rather than as general semantic preservation;
- **C7 — associative-memory effects:** frozen, provenance-tracked textual memory may improve sample efficiency while risking model-family overfitting;
- **C8 — learning-progress curriculum:** a prerequisite graph plus learning-progress bandit should reduce language-model calls to competence relative to a simpler depth-only schedule;
- **C9 — full Forbidden Relay benchmark conjunction:** benign exact target reconstruction + constrained discrete RL relays + repeated frozen/heterogeneous LLM transformations + zero literal target occurrence at intermediate outputs + held-out target/depth/model tests + independent-observer/private-code diagnostics + memory and side-channel controls.

H10 in the paper — refusal to infer universal jailbreak capability from success on synthetic literal bans — is an interpretation/safety boundary rather than a novelty claim.

## 2. Temporal reconstruction of our claims

### 2.1 The benchmark file is not the earliest public source for every component

Using only the current `forbidden_relay.md` timestamp would be wrong because the benchmark is the top of a three-paper stack. The relevant public GitHub events are:

1. **PR #243 — Interstitial Agent** opened **2026-08-01 23:01:02 UTC**: <https://github.com/franklinbaldo/papers/pull/243>. Its public body already states surface versus functional message persistence, local versus end-to-end compliance, direct generation versus downstream reconstruction, receiver-private decodability, memory/topology as channel components, and capability duality.
2. **PR #244 — RL Relay Transducers** opened **2026-08-01 23:03:11 UTC**: <https://github.com/franklinbaldo/papers/pull/244>. Its public body already states discrete `KEEP/DELETE/INSERT/RETRIEVE/REPLACE/STOP` actions between LLM calls, associative memory, black-box frozen/coadapted language-model channels, terminal reward/policy gradient, shared hypotheses about semantic/arbitrary codes, depth transfer, memory, private-code opacity, and a prerequisite-graph + learning-progress bandit curriculum.
3. The first full benchmark commit, [`96eb3e59a85e92097ea3840af587bb471528013d`](https://github.com/franklinbaldo/papers/commit/96eb3e59a85e92097ea3840af587bb471528013d), is dated **2026-08-01 23:04:34 UTC** and adds all 555 lines of `forbidden_relay.md`, including H1-H10, exact literal-ban conditions, VES, held-out depths and independent-observer tests.
4. **PR #245 — Forbidden Relay** opened **2026-08-01 23:05:03 UTC**: <https://github.com/franklinbaldo/papers/pull/245>. Its public body already states the primary exact-reconstruction-under-no-literal-intermediate question and the complete preregistered design.

### 2.2 Cutoffs used claim by claim

The audit therefore uses three conservative public cutoffs rather than one file date:

- **C5/C6 conceptual persistence/compliance distinctions:** 2026-08-01 23:01:02 UTC (PR #243), where those distinctions are already explicit.
- **C1, C3-C5, C7-C8 relay architecture/training hypotheses:** 2026-08-01 23:03:11 UTC (PR #244), where the formal relay construction and those hypotheses are already public.
- **C2 and C9 benchmark-specific exact-literal-ban conjunction, plus fixed benchmark factors/outcomes:** 2026-08-01 23:05:03 UTC (PR #245). The underlying complete commit is 29 seconds earlier, but PR opening is used as the conservative public event.

A candidate is classified as prior art only if its verified public date precedes the relevant cutoff above.

## 3. Search protocol

This run searched the claim by decomposition rather than by the name “Forbidden Relay.” Sources included arXiv primary records, publisher full text, older emergent-communication literature, multi-agent LLM work, linguistic/LLM steganography, and targeted post-cutoff searches through 2026-09-18.

Representative queries included:

- `LLM steganography reinforcement learning collusion paraphrase`
- `penalize specific strings learned encoding chain of thought`
- `semantic steganography word blocking LLM`
- `robust steganography LLM paraphrase recover secret message`
- `multi-agent LLM covert communication monitor receiver`
- `chain of agents sequential LLM natural language communication`
- `shared policy emergent communication generalize number agents depth`
- `receiver decoder usable information steganographic gap`
- `learning progress bandit automated curriculum`
- `hidden message chain artificial intelligence transformations`
- `coadapted communication private code unseen teammate transfer`
- exact-title and `Franklin Baldo` searches for post-cutoff overlap/citation checks.

Negative searches are recorded only as bounded results. “Not located” does not mean nonexistent.

## 4. Pre-cutoff findings

### 4.1 Learned communication protocols by RL are old prior art

**Work:** Jakob N. Foerster, Yannis M. Assael, Nando de Freitas, Shimon Whiteson, **“Learning to Communicate with Deep Multi-Agent Reinforcement Learning.”**

- arXiv v1: **2016-05-21 17:20:04 UTC**;
- <https://arxiv.org/abs/1605.06676>.

Foerster et al. train agents end-to-end to learn communication protocols under shared utility using reinforcement learning (RIAL) and differentiable communication (DIAL). The medium is not a frozen pretrained LLM and the messages are not constrained textual edit programs, but the generic claim “RL can learn a task-useful communication protocol between agents” is long occupied.

**Compared claims:** C1, component of C4/C5.

**Classification:** `prior_art` for learned communication by RL; `adjacent_prior_work` for the black-box LLM relay construction.

### 4.2 Sequential LLM-to-LLM natural-language relays predate the benchmark

**Work:** Yusen Zhang et al., **“Chain of Agents: Large Language Models Collaborating on Long-Context Tasks.”**

- arXiv v1: **2024-06-04 23:36:08 UTC**;
- <https://arxiv.org/abs/2406.02818>.

Chain of Agents uses multiple worker LLM agents that process segments sequentially and communicate through natural language, followed by a manager that synthesizes the accumulated information. This is not covert communication and has no learned edit policy, but it materially occupies the serial “output from one LLM becomes the communication substrate for the next” topology.

**Compared claims:** C1 and C9 topology.

**Classification:** `prior_art` for sequential LLM-agent message passing; `partial_prior_art` for C9.

### 4.3 Optimization can already induce robust steganographic communication in LLM text

**Work:** Yohan Mathew et al., **“Hidden in Plain Text: Emergence & Mitigation of Steganographic Collusion in LLMs.”**

- arXiv v1: **2024-10-02 16:18:33 UTC**;
- <https://arxiv.org/abs/2410.03768>.

The paper demonstrates that sophisticated linguistic steganographic collusion can emerge from optimization pressure. It uses both gradient-based reinforcement learning and in-context reinforcement learning and reports robustness to passive oversight and active paraphrasing of model outputs.

**Compared claims:** C1, C2, C5, C6, C9.

**Classification:** `prior_art` for the broad proposition that optimization/RL can create receiver-useful hidden communication in LLM-generated text that survives an active language transformation; `partial_prior_art` for the full Forbidden Relay conjunction.

**Material revision:** the benchmark cannot treat “RL discovers a nonliteral protocol through language-model text” as a new phenomenon. Its narrower contribution must come from the constrained relay interface, exact benign target recovery, repeated black-box channels, transfer tests, and pre-registered controls.

### 4.4 Semantic steganography directly anticipates robustness to word blocking

**Work:** Minhao Bai, Jinshuai Yang, Kaiyi Pang, Yongfeng Huang, Yue Gao, **“Semantic Steganography: A Framework for Robust and High-Capacity Information Hiding using Large Language Models.”**

- arXiv v1: **2024-12-15 04:04:23 UTC**;
- <https://arxiv.org/abs/2412.11043>.

The method constructs a semantic space and maps secret messages into it. Its abstract explicitly reports robustness in complex channels and resistance to **word blocking**. That is very close to the conceptual content of Forbidden Relay H6: suppressing a literal surface form need not remove the recoverable information if the channel supports another representation.

**Compared claims:** C2, C3, C9.

**Classification:** `prior_art` for the generic claim that a word/literal blocking constraint can coexist with recoverable hidden information via semantic representation; `partial_prior_art` for the benchmark.

### 4.5 A chain of AI transformations already carried recoverable hidden messages before our relay stack

**Work:** Ching-Chun Chang, Isao Echizen, **“Steganography beyond space-time with chain of multimodal AI.”** Scientific Reports 15, 12908 (2025).

- published/version of record: **2025-04-15**;
- DOI: <https://doi.org/10.1038/s41598-025-97238-2>;
- full text: <https://www.nature.com/articles/s41598-025-97238-2>.

The system chains AI components: speech is transcribed, a language-generation model paraphrases the transcript while embedding a hidden message through biased word sampling, and downstream voice/video synthesis reconstructs the multimodal object. The paper evaluates message-transmission accuracy and robustness under multiple subsequent transformations. It is not a chain of repeated LLM channels and does not learn an RL relay, but it is a direct antecedent to the broad idea “preserve a recoverable message through a chain of generative AI transformations.”

**Compared claims:** C1, C2, C9.

**Classification:** `prior_art` for hidden-message transmission through chained AI transformations; `partial_prior_art` for C9.

### 4.6 Exact secret recovery after paraphrasing/rewording is established prior art

**Work:** Neil Perry, Sanket Gupte, Nishant Pitta, Lior Rotem, **“Robust Steganography from Large Language Models.”**

- arXiv v1: **2025-04-11 21:06:36 UTC**;
- <https://arxiv.org/abs/2504.08977>.

The paper embeds arbitrary secret messages into natural-language text generated by LLMs and constructs schemes intended to preserve recoverability under adversarial paraphrasing and rewording attacks.

**Compared claims:** C2, C3, C9.

**Classification:** `prior_art` for recoverable hidden payloads surviving natural-language transformation; `partial_prior_art` for the repeated relay benchmark.

This sharply narrows the scientific question: Forbidden Relay must demonstrate something about **learned constrained relay composition and transfer**, not merely that hidden information can survive paraphrase.

### 4.7 Penalizing literal strings can cause generalized substitute encodings

**Work:** Joey Skaf et al., **“Large language models can learn and generalize steganographic chain-of-thought under process supervision.”**

- arXiv v1: **2025-06-02 17:45:15 UTC**;
- <https://arxiv.org/abs/2506.01926>.

Skaf et al. show that penalizing specific strings in load-bearing reasoning traces can cause models to substitute alternative strings while preserving the underlying method. When the penalized strings belong to a class, the learned encoding scheme generalizes to held-out test strings from that class.

**Compared claims:** C2, C3, H6/H7 aspects of C9.

**Classification:** `prior_art` for the generic claim “literal suppression can induce an alternative encoding that preserves task-relevant information and generalizes beyond training strings”; `partial_prior_art` for Forbidden Relay.

**Material revision:** H6 is useful as a benchmark measurement, but its underlying phenomenon is not novel.

### 4.8 Receiver-relative decodability has a direct formal antecedent

**Work:** Usman Anwar et al., **“A Decision-Theoretic Formalisation of Steganography With Applications to LLM Monitoring.”**

- arXiv v1: **2026-02-26 16:27:24 UTC**;
- <https://arxiv.org/abs/2602.23163>.

The paper's central idea is an asymmetry in **usable information** between agents that can and cannot decode a steganographic signal. It defines a steganographic gap by comparing downstream utility for decoders versus non-decoders/sentinels.

**Compared claims:** C6 and H8.

**Classification:** `prior_art` for the general distinction between receiver-decodable information and information available to an uninitiated observer; `partial_prior_art` for Forbidden Relay's specific independent-receiver/human/embedding/swap battery.

The benchmark's phrase “receiver-private decodability, not general semantic preservation” is therefore best treated as an operationalization of an established distinction, not a new principle.

### 4.9 Covert agent conversations under a strong transcript auditor are already theoretically established

**Work:** Vinod Vaikuntanathan, Or Zamir, **“Undetectable Conversations Between AI Agents via Pseudorandom Noise-Resilient Key Exchange.”**

- arXiv v1: **2026-04-06 15:25:38 UTC**;
- <https://arxiv.org/abs/2604.04757>.

The work proves that two AI agents can carry a parallel covert conversation while the transcript remains computationally indistinguishable from honest interaction, including a keyless setting with short adaptive messages under cryptographic assumptions.

**Compared claims:** C2, C5, C6, C9.

**Classification:** `prior_art` for the possibility of covert AI-agent communication under transcript monitoring; `adjacent_prior_work` to Forbidden Relay because the mechanism is cryptographic rather than a learned discrete relay over frozen LLM channels.

### 4.10 Tool-using LLM agents can construct stegosystems and exploit repeated interaction/shared artifacts

**Work:** Jimmy Laurence Rippin, Simon C. Marshall, David Demitri Africa, Christian Schroeder de Witt, **“Tool Use Enables Undetectable Steganography in Multi-Agent LLM Systems.”**

- arXiv v1: **2026-06-25 19:42:39 UTC**;
- <https://arxiv.org/abs/2606.28425>.

The paper finds that agentic coding models can construct undetectable stegosystems using tools and emphasizes repeated interaction and shared artifacts as settings where covert coordination becomes more feasible.

**Compared claims:** C5-C7 and C9.

**Classification:** `partial_prior_art` for the broader multi-agent LLM covert-communication capability; `adjacent_prior_work` for the specific constrained-relay benchmark.

### 4.11 The learning-progress bandit component of H9 is old prior art

**Work:** Alex Graves, Marc G. Bellemare, Jacob Menick, Rémi Munos, Koray Kavukcuoglu, **“Automated Curriculum Learning for Neural Networks.”**

- arXiv v1: **2017-04-10 18:25:29 UTC**;
- <https://arxiv.org/abs/1704.03003>.

Graves et al. use learning-progress signals as reward for a nonstationary multi-armed bandit that selects a training syllabus to improve learning efficiency.

**Compared claim:** C8/H9.

**Classification:** `prior_art` for a learning-progress bandit curriculum. The relay-specific prerequisite graph and its empirical effect remain application-specific.

## 5. What was not located before the relevant cutoffs

The searches above materially occupy most generic ingredients. They do **not** establish a pre-cutoff antecedent for the complete C9 conjunction.

In particular, this run did not locate before 2026-08-01 a single public work combining all of the following:

1. small discrete edit/retrieval policies placed explicitly **between** black-box language-model calls;
2. exact recovery of benign natural words and arbitrary nonces/identifiers;
3. a hard metric requiring both exact terminal reconstruction and zero literal target occurrence in every intermediate LLM output;
4. training at shallow chain depths with pre-registered extrapolation to longer unseen depths;
5. frozen single-model, frozen heterogeneous, and adapter-coadapted channel regimes in the same factorial design;
6. independent-receiver, generic-embedding, human and receiver-swap tests to separate public/semantic communication from receiver-private codes;
7. frozen provenance-tracked associative memory with explicit side-channel exclusions;
8. cross-model transfer and a fixed manual public codec/random-edit/retrieval baseline battery.

This is a **bounded negative search result**, not a claim that the conjunction is globally first.

The scientifically defensible novelty target is therefore the **benchmark construction and discriminating experimental conjunction**, not hidden communication, steganography, emergent protocols, literal-ban evasion, sequential LLM communication, or receiver-relative information by themselves.

## 6. Post-cutoff work

### 6.1 Arbitrary Cipher Attacks Against Large Language Models Do Not Require Fine-Tuning

**Work:** Thomas Rivasseau, **“Arbitrary Cipher Attacks Against Large Language Models Do Not Require Fine-Tuning.”**

- arXiv v1: **2026-09-09 00:16:53 UTC**;
- <https://arxiv.org/abs/2609.09553>.

This is unambiguously **after** all our relevant cutoffs. It shows that frontier black-box LLMs can acquire arbitrary cipher/covert-communication skills through prompting and in-context learning without fine-tuning, and that safety alignment can weaken when interaction is moved through the learned cipher.

**Compared claims:** broad coded communication through black-box LLM interfaces; C2/C5 context.

**Classification:** `later_independent` for this audit. Its method and objective differ materially from Forbidden Relay: no constrained inter-call RL editor, no pre-registered benign exact-reconstruction chain benchmark, and the paper studies a jailbreak attack rather than the bounded synthetic policy condition here. Targeted web searches did not locate the exact title “Forbidden Relay” or `Franklin Baldo` in connection with this paper; because full-text dependency evidence was not established in this run, this audit deliberately does **not** upgrade the label to `later_non_citing`.

### 6.2 No stronger post-cutoff duplicate located in this run

Targeted searches for `LLM chain covert communication relay`, `multi-hop LLM steganography`, `literal ban receiver reconstruction`, `shared relay policy depth transfer`, and exact-title/author combinations did not locate a post-cutoff paper that reproduces the full C9 design closely enough to justify `later_overlap`, `later_non_citing`, `later_citing`, or `later_derivative`.

That is a negative result of this search window only.

## 7. Classification revision

The prior-art picture changes the benchmark's interpretation in several concrete ways:

- **RL-discovered hidden textual communication:** established before our cutoff (`prior_art`).
- **Sequential LLM-agent message passing:** established before our cutoff (`prior_art` for topology).
- **Hidden information robust to paraphrase/rewording:** established before our cutoff (`prior_art`).
- **Literal/word blocking compatible with recoverable semantic information:** established before our cutoff (`prior_art`).
- **Generalized substitute encodings after string penalties:** established before our cutoff (`prior_art`).
- **Receiver-versus-observer usable-information asymmetry:** established before our cutoff (`prior_art`).
- **Learning-progress bandit curriculum:** established before our cutoff (`prior_art`).
- **Full Forbidden Relay pre-registered conjunction:** no material pre-cutoff anticipation located after the searches above; retain only as an unresolved combination claim, not as a declaration of firstness.

This audit does not contradict the paper's safety discipline. In fact, the prior art makes that discipline more important: success under the benchmark's synthetic literal ban should be interpreted as a measurement of communication/transfer capability, not as evidence of a universal policy-evasion mechanism.

## 8. Experimental consequences

The pre-registration already contains many strong baselines, but prior art suggests sharpening the control ladder when the benchmark is implemented:

1. **public fixed codec** with the same token budget;
2. **semantic steganography-style codec** designed to survive word blocking;
3. **paraphrase-robust steganographic codec** under the same language transformations;
4. **prompt/in-context learned cipher** without relay training;
5. **shared RL relay** without associative memory;
6. **shared RL relay + frozen memory**;
7. **position-specific relay** under matched parameter/call budgets;
8. frozen versus heterogeneous versus adapter-coadapted channels;
9. independent-receiver/human/general-embedding decoding at every depth, not only terminal accuracy.

The most informative falsifier of the specifically relay-based claim is now straightforward: if a fixed semantic/paraphrase-robust codec or an in-context cipher baseline matches the shared relay on unseen depth and unseen models at comparable bandwidth, then the distinctive learned relay machinery has not demonstrated added value.

Likewise, H6 should not be interpreted merely as “literal bans fail.” The stronger experiment is whether the **same learned inter-call relay policy**, without target-specific test rules, maintains exact held-out recovery across depth and model swaps while its code remains independently characterizable as public, semantic or receiver-private.

## 9. Sources and queries preserved

Primary/public records used in this audit:

- Foerster et al. 2016: <https://arxiv.org/abs/1605.06676>
- Zhang et al., Chain of Agents, 2024: <https://arxiv.org/abs/2406.02818>
- Mathew et al. 2024: <https://arxiv.org/abs/2410.03768>
- Bai et al. 2024: <https://arxiv.org/abs/2412.11043>
- Perry et al. 2025: <https://arxiv.org/abs/2504.08977>
- Chang & Echizen 2025: <https://doi.org/10.1038/s41598-025-97238-2>
- Skaf et al. 2025: <https://arxiv.org/abs/2506.01926>
- Anwar et al. 2026: <https://arxiv.org/abs/2602.23163>
- Vaikuntanathan & Zamir 2026: <https://arxiv.org/abs/2604.04757>
- Rippin et al. 2026: <https://arxiv.org/abs/2606.28425>
- Graves et al. 2017: <https://arxiv.org/abs/1704.03003>
- Rivasseau 2026: <https://arxiv.org/abs/2609.09553>

GitHub temporal evidence:

- PR #243: <https://github.com/franklinbaldo/papers/pull/243>
- PR #244: <https://github.com/franklinbaldo/papers/pull/244>
- first full Forbidden Relay commit: <https://github.com/franklinbaldo/papers/commit/96eb3e59a85e92097ea3840af587bb471528013d>
- PR #245: <https://github.com/franklinbaldo/papers/pull/245>

## 10. Bottom line

The benchmark remains scientifically interesting, but for a narrower reason than “hidden information can survive an LLM while a literal is suppressed.” That phenomenon and several stronger variants were public well before August 2026.

The unresolved target is a **controlled composition/transfer benchmark**: a tiny auditable relay policy learns to preserve exact benign information across repeated black-box LLM transformations, remains useful at unseen depths and model families, passes side-channel controls, and can be diagnosed as public/semantic versus receiver-private communication under a fixed pre-registration.

No pre-cutoff source located in this run materially anticipates that complete conjunction. No post-cutoff source located in this run justifies a causal or plagiarism claim.