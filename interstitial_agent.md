---
type: "Alignment Paper"
title: "The Interstitial Agent: Meaning, Control, and Safety Between Language Models"
description: "Position paper arguing that agency, message persistence, and safety failures can arise in the learned transformations between individually compliant language models."
tags: [interstitial-agency, composed-ai-systems, llm-safety, emergent-communication, end-to-end-alignment]
timestamp: 2026-08-01T22:59:00Z
---

# The Interstitial Agent: Meaning, Control, and Safety Between Language Models

**Franklin Baldo**  
Independent Researcher  
franklinbaldo@gmail.com

*Draft status: position paper. No relay-transducer implementation or empirical result is claimed here. Propositions marked as hypotheses require the formal and empirical companion papers.*

---

## Abstract

Language-model safety is usually evaluated at the boundary of one model call: a prompt enters, an answer leaves, and the answer is classified as compliant or noncompliant. This paper studies a different object. Consider a chain in which the output of one language model is passed through a learned discrete transducer before becoming the prompt of another. The transducer may delete tokens, insert tokens, retrieve previously observed strings from an embedding-indexed memory, or select among procedural transformations. It cannot inspect or modify model logits, yet it can be optimized by reinforcement learning from an end-to-end reward.

Such a system introduces **interstitial agency**: goal-directed control exercised in the transformations between model calls rather than wholly inside any one model. A message may persist through the chain even when no intermediate output reproduces its original surface form. Conversely, every model in the chain may satisfy its local policy while the composed system violates the intended end-to-end policy. The same architecture can act as a robust communication code, a prompt controller, a covert channel, or an automated policy-evasion mechanism; the distinction often lies in the target distribution and reward, not in the mechanism itself.

The paper develops a vocabulary for reasoning about these systems: relay transducers, associative relay memory, message persistence, local and end-to-end compliance, compositional safety gaps, and capability duality. It argues that alignment claims for composed AI systems must be stated over the full causal path, including learned editors, retrieval memories, topology, and reward functions. It does not claim that every relay system is a jailbreak generator, nor that all indirect communication is adversarial. Its narrower claim is that sufficiently general black-box steering and communication capabilities create a latent dual-use capacity that cannot be assessed by inspecting individual model outputs alone.

**Keywords:** interstitial agency, composed AI systems, language-model safety, emergent communication, relay transducers, end-to-end alignment, covert channels

---

## 1. The Missing Object of Analysis

A conventional language-model interaction has a visible boundary:

```text
prompt -> model -> output
```

Safety evaluation is naturally attached to that boundary. Did the model refuse? Did it disclose disallowed content? Did the answer satisfy the system instruction? This framing becomes incomplete when model calls are composed:

```text
LLM_0 -> learned transducer -> LLM_1 -> learned transducer -> ... -> LLM_N
```

The intermediate transducer is external to every language model. It may operate only on discrete text. Nevertheless, it observes a state, selects an action, changes the next prompt, and receives delayed reward from a terminal outcome. It is therefore not merely plumbing. It is a policy-bearing component.

The central claim of this paper is:

> In composed language-model systems, effective agency and safety-relevant capability may reside in the learned transformations between model calls, in the topology that connects them, and in the end-to-end reward, even when no individual model has access to the complete task.

This is not a metaphorical claim that every software adapter is an agent. The relevant transducer is adaptive and goal-directed: it selects among possible edits or memory retrievals because those actions alter the probability of a future rewarded state.

## 2. Relay Transducers and Interstitial Agency

A **relay transducer** is a learned discrete sequence transformer placed between language-model calls. Given an observed message, it may select actions such as:

- preserve a token or span;
- delete a token or span;
- insert a token or previously stored string;
- retrieve a candidate from an embedding-indexed table;
- replace a span by a retrieved string;
- stop editing and release the next prompt.

An **associative relay transducer** adds a memory whose entries pair previously observed strings with frozen embeddings and provenance metadata. The transducer may compare an input span with this vector store, retrieve a nearby entry, and reuse the entry's original string as a discrete action.

The transducer has no privileged access to language-model internals. It need not see logits, hidden states, gradients, or model weights. Its power comes from repeated black-box interaction and reward.

**Interstitial agency** is the goal-directed contribution made by such policies at the boundaries between model calls. It is interstitial because it is neither reducible to the language model that produced the incoming text nor to the language model that consumes the edited text.

Agency in the complete system may therefore be distributed across:

1. the generative policies of the language models;
2. the edit and retrieval policy of the relay transducers;
3. the topology that determines which outputs reach which nodes;
4. the memory architecture;
5. the curriculum that selects tasks;
6. the reward that defines success.

The reward is particularly important. The same physical architecture can be optimized to preserve benign identifiers, to steer outputs toward a desired semantic region, or to defeat a refusal. Architecture alone does not determine use.

## 3. Message Persistence Without Surface Persistence

Suppose an initial sender possesses a message \(m\). After several transformations, a terminal receiver reconstructs \(\hat m\). None of the intermediate texts need contain \(m\) literally.

This creates a distinction between **surface persistence** and **functional persistence**.

- Surface persistence occurs when the same string or an obvious spelling variant survives.
- Functional persistence occurs when sufficient information survives for an authorized receiver to recover the original message or its task-relevant identity.

A city name may become a description, a description may become a metaphor, and a trained receiver may map the metaphor back to the city. A random identifier may instead be represented by a distributed textual pattern that has no ordinary semantics. In both cases, persistence is a property of the causal relation between sender, channel, and receiver, not only of lexical overlap.

This matters philosophically because messages are often treated as objects located in strings. In a learned relay, the message is better modeled as an invariant or recoverable distinction across transformations. No one representation is metaphysically privileged. The relevant question is whether changing the initial message changes the distribution of terminal reconstructions in a reliable, discriminable way.

This also creates an observer-relative aspect. A representation may be opaque to a human or independent classifier while remaining decodable by the trained receiver. Opacity does not imply absence of information.

## 4. Local Compliance and End-to-End Compliance

Let each language model be governed by a local policy. A local evaluator sees only the prompt received by that model and the output it generated. It may correctly conclude that every model call complied.

The composed system can nevertheless produce an end-to-end effect that violates the intended system policy. For example:

1. no intermediate model outputs a forbidden literal;
2. each output is individually benign or ambiguous;
3. the terminal receiver reconstructs the forbidden information;
4. the system's objective is satisfied despite local compliance.

This yields the **compositional safety gap**:

> Local compliance of every component is not sufficient for end-to-end compliance of the composed system.

The gap can arise without any component being deceptive in isolation. It may be an ordinary consequence of coding. A safety filter that checks only surface forms is analogous to a network monitor that checks each packet independently while ignoring the application-layer protocol reconstructed from the packet sequence.

End-to-end assessment must therefore include:

- the information available to the initial sender;
- all relay transformations;
- shared and local memories;
- the identity and capabilities of the terminal receiver;
- the reward optimized during training;
- the possibility of decoding across multiple messages or branches.

This does not entail that every recoverable latent signal should be prohibited. It entails that policy scope must be explicit. If a policy governs only direct model output, local evaluation may be adequate. If it governs what the complete service enables a user or downstream agent to obtain, local evaluation is insufficient.

## 5. Capability Duality

A relay system optimized to preserve information through a difficult language-model channel may discover:

- paraphrases that survive summarization;
- redundant semantic encodings;
- syntactic patterns preserved by generation;
- strings associated with stable embedding regions;
- model-specific prompt transformations;
- representations recoverable by a trained decoder but not obvious to an observer.

These are useful for benign communication and robustness. The same competencies can support policy evasion when the target distribution changes.

This paper calls that relation **capability duality**:

> A sufficiently general ability to steer or preserve arbitrary target representations through frozen language-model channels creates a latent ability to optimize policy-evasive transformations whenever prohibited targets are admitted into the objective.

Capability duality is not an identity. A system trained only on a narrow benign codebook may fail to generalize to refused tasks. A transducer that preserves semantic concepts may not transmit arbitrary strings. A receiver-dependent covert code may not cause the language model itself to emit prohibited content. Universal evasion is therefore an empirical claim with demanding transfer requirements.

The weaker point remains: the architectural boundary between robust communication and automated jailbreak search is thin. Changing the reward from “recover this benign nonce” to “produce or reconstruct this refused target” can convert the same optimization machinery from communication research into offensive prompt optimization.

## 6. Two Different Safety Failures

The phrase “jailbreak” can obscure two distinct mechanisms.

### 6.1 Direct generation failure

The relay transducer changes a prompt so that a language model directly emits content it would otherwise refuse. The language model's local output policy is defeated.

### 6.2 End-to-end reconstruction failure

The language model never emits the prohibited content directly. It emits a representation from which a downstream receiver reconstructs that content. The local model may remain compliant under a literal policy, while the complete system violates an end-to-end information policy.

The second mechanism resembles a covert channel more than a conventional jailbreak. It is potentially harder to detect because the representation can be distributed, semantically indirect, or receiver-specific.

A responsible research program must measure these mechanisms separately. Demonstrating end-to-end reconstruction does not by itself demonstrate that a language model's own safety policy was bypassed. Conversely, demonstrating direct refusal bypass does not establish a robust communication protocol across multiple hops.

## 7. Memory Changes the Ontology of the Channel

An embedding-indexed memory gives the relay transducer access to strings observed in earlier training episodes. This memory is not merely an implementation optimization. It changes what the channel can do.

The system can accumulate a lexicon of strings that:

- occupy useful semantic neighborhoods;
- survive particular language models;
- retain decodability over many hops;
- transfer across model versions;
- induce stable responses;
- act as canonical representatives of broader embedding regions.

Such a lexicon can become a learned protocol. It can also become a library of steering strategies.

Memory design therefore determines whether the experiment measures communication through language models or communication around them. A globally writable memory shared during an episode creates a trivial side channel: the sender writes the target and the receiver reads it. To preserve the intended causal test, evaluation memory should be frozen, locally scoped, or otherwise prevented from carrying episode-specific secrets outside the textual relay.

The relevant safety principle is broader:

> Every persistent store accessible across nodes is part of the communication channel and must be included in the threat model.

## 8. Distributed Systems and Distributed Responsibility

Relay architectures naturally support distributed execution. Different language models and transducers can run on different machines, organizations, or trust domains. This improves scale but complicates responsibility.

A failure may be attributable to no single node considered independently. One service generates a harmless paraphrase, another retrieves a code phrase, and a final receiver reconstructs the target. The causal contribution is distributed.

This weakens governance models based solely on component certification. Certification remains useful, but a composed deployment requires system-level evaluation under the actual topology and interfaces. Replacing one node, changing a memory snapshot, or adding one extra hop can alter the effective protocol.

The distributed case also makes provenance essential. An auditable rollout should identify:

- model and checkpoint at every hop;
- transducer policy version;
- memory and embedding-model version;
- curriculum configuration;
- actions taken by every transducer;
- terminal reward and evaluator;
- information visible to each component.

Without this record, system-level claims cannot be reproduced or assigned.

## 9. What This Is Not

This proposal is not the claim that:

- every text editor is an autonomous agent;
- every indirect description is a covert channel;
- every communication protocol is a jailbreak;
- a vector store necessarily contains hidden malicious knowledge;
- local model safety is useless;
- semantic similarity proves exact information transmission;
- a receiver's successful guess proves that the message traversed the intended path;
- a shared reward automatically produces universal transfer;
- current language models already support the strongest hypothesized behavior.

The paper also does not argue that messages have one observer-independent identity. Different tasks justify different equivalence relations: exact string recovery, class identity, semantic equivalence, executable behavior, or embedding proximity.

## 10. Research Program

The conceptual claims motivate two companion papers.

The formal companion should define relay transmitters, receivers, and transceivers; discrete edit and retrieval actions; black-box language-model channels; terminal and shaped rewards; joint training with frozen or adapter-modified language models; channel capacity by depth; and controls against memory side channels.

The empirical companion should test a deliberately benign **Forbidden Relay** benchmark. An initial node receives a natural word or random nonce. Intermediate language-model outputs may not contain the target literally. A terminal receiver must recover it after a specified number of hops. Synthetic prohibitions, rather than real harmful requests, can test whether literal suppression removes information or merely changes its representation.

The empirical work should distinguish:

- natural semantic targets from random identifiers;
- frozen channels from co-adapted channels;
- shared relay policies from position-specific policies;
- public codes from receiver-private codes;
- direct generation from downstream reconstruction;
- within-model performance from transfer to unseen models;
- training-depth success from extrapolation to longer chains.

## 11. Limitations and Failure Modes

The framework risks over-attributing agency to coordination machinery. A relay policy may merely exploit stable correlations without representing a message in any rich sense. The empirical work should therefore use interventions: change the target while holding other variables fixed, permute codebooks, replace receivers, and insert unseen language models.

Embedding similarity may reward vague semantic proximity rather than information preservation. Exact identification among contrastive alternatives is a stronger diagnostic.

Jointly trained language models and transducers may collude in a private code that does not reveal a general property of language-model channels. Frozen-model and cross-model transfer conditions are necessary controls.

A safety framing can itself create offensive knowledge. Publishing broadly transferable transducer weights, discovered refusal-bypass strings, or an unrestricted target-conditioned optimizer could materially lower barriers to abuse. Synthetic benchmarks and staged disclosure are therefore part of the research design, not an afterthought.

Finally, system-level safety is difficult to define without specifying the authorized receiver and policy scope. A medical code understood only by authorized clinicians is not equivalent to a covert channel intended to evade oversight, even if both rely on receiver-relative decoding. Normative judgment cannot be read directly from mutual information.

## 12. Conclusion

When language models are chained through learned discrete transformations, the meaningful unit of analysis is no longer one model call. A relay transducer can exert goal-directed control without touching logits. An associative memory can stabilize a vocabulary across episodes. A message can persist without retaining its words. Every component can appear locally compliant while the composed system enables an outcome that the deployment policy intended to prevent.

These observations support a shift from component-only alignment toward causal, end-to-end evaluation of composed AI systems. The shift does not erase local responsibility or make all indirect communication suspicious. It requires us to identify where control actually resides: in models, in memories, in topology, in learned transformations, and above all in the objective that makes one terminal state preferable to another.

The interstitial agent is not a hidden creature between models. It is the organized policy of the space between them.