---
type: "Technical Paper"
title: "RL Relay Transducers: Discrete Control and Communication Through Frozen and Co-adapted Language-Model Channels"
description: "Formal framework for reinforcement-learned discrete editors with associative textual memory that communicate and steer through black-box language-model channels."
tags: [rl-relay-transducers, emergent-communication, multi-agent-rl, black-box-llm-control, associative-memory]
timestamp: 2026-08-01T23:04:00Z
---

# RL Relay Transducers: Discrete Control and Communication Through Frozen and Co-adapted Language-Model Channels

**Franklin Baldo**  
Independent Researcher  
franklinbaldo@gmail.com

---

> **Position paper.** This article proposes a formal architecture, training regimes, and evaluation program. It reports no implementation or empirical results. Claims about learnability, capacity, transfer, emergent codes, or safety behavior are hypotheses to be tested.

## Abstract

This paper introduces **reinforcement-learned relay transducers**, discrete sequence policies placed between language-model calls. A relay transducer receives text emitted by one language model and constructs the next prompt through auditable operations such as keep, delete, insert, retrieve, replace, and stop. It does not require access to logits, hidden states, model weights, or gradients through the language model. An **associative relay transducer** augments this editor with an embedding-indexed table of previously observed strings. The policy can compare an incoming span with the vector store and reuse the surface string associated with a retrieved embedding.

The resulting system treats language models as stochastic channels inside a cooperative partially observed Markov game. A transmitter encodes a target representation; intermediate transceivers decode and re-encode what they receive; a terminal receiver reconstructs the target. Receivers can learn by ordinary backpropagation, while discrete relay actions and sampled language-model tokens are optimized by policy gradient from terminal or shaped rewards. Frozen, adapter-coadapted, and fully co-trained language-model channels define distinct scientific regimes: discovery of channel invariants, invention of a joint protocol, and possible private collusion.

The paper formalizes communication and steering objectives, memory constraints, depth-dependent capacity, joint training at multiple time scales, curriculum optimization, distributed rollout collection, and controls against hidden side channels. It also separates benign communication capability from direct refusal bypass and downstream reconstruction of disallowed information. The proposed empirical companion, Forbidden Relay, is deliberately restricted to benign natural words, random nonces, and synthetic literal prohibitions.

**Keywords:** reinforcement learning, emergent communication, language-model channels, discrete sequence editing, associative memory, centralized training, decentralized execution, prompt steering

---

## 1. Problem Setting

Let \(Z\) be a target variable sampled from a task distribution. A chain contains language-model channels \(M_0,\ldots,M_N\), relay policies, and a terminal receiver. The simplest one-hop system is:

$$
z \xrightarrow{T_\theta} p_0
\xrightarrow{M_\phi} y_0
\xrightarrow{R_\psi} \hat z.
$$

Here:

- \(T_\theta\) is a relay transmitter;
- \(p_0\) is a discrete textual prompt;
- \(M_\phi\) is a language model treated as a stochastic channel;
- \(y_0\) is generated text;
- \(R_\psi\) is a receiver;
- \(\hat z\) is a reconstructed target.

For multiple hops, an intermediate relay transceiver \(C_\theta\) observes the current text and constructs the next prompt:

$$
y_i \xrightarrow{C_\theta} p_{i+1}
\xrightarrow{M_{i+1}} y_{i+1}.
$$

The same policy may be shared across positions or specialized by hop. Shared parameters test whether the learned transformation composes beyond the training depth.

The defining interface constraint is:

> Relay policies act only through discrete textual operations and authorized memory retrieval. They do not receive language-model logits, hidden activations, internal gradients, or privileged episode state at execution time.

## 2. Roles and Terminology

A **relay transmitter** observes the original target and produces the first prompt.

A **relay receiver** maps the final language-model output to a target prediction or embedding.

A **relay transceiver** receives text from an upstream channel, estimates what information it contains, and produces text for a downstream channel.

A **relay transducer** is the generic discrete policy implementing any of these roles.

An **associative relay transducer (ART)** adds a textual memory indexed by embeddings. The ART remains a transducer rather than a second unrestricted language model because its generated output is constrained to procedural edits and retrieved strings.

A **language-model channel** is the stochastic mapping from prompt text to generated text. A frozen channel is not updated by the relay objective. A co-adapted channel updates adapters or model weights in response to relay trajectories.

## 3. Discrete Edit Policy

Let the incoming message be tokenized as:

$$
x=(x_1,\ldots,x_L).
$$

The relay policy emits an edit program \(a_{1:T}\). The primitive action set is:

$$
\mathcal A = \{\operatorname{KEEP},\operatorname{DELETE},
\operatorname{INSERT}(v),\operatorname{RETRIEVE}(j),
\operatorname{REPLACE}(j),\operatorname{STORE}(u),
\operatorname{STOP}\}.
$$

`REPLACE` can be implemented as deletion followed by insertion, but retaining it as a macro-action may improve credit assignment. `STORE` is disabled during evaluation episodes unless the memory design explicitly permits local, non-shared storage.

An edit program is executed deterministically:

$$
p'=\operatorname{Execute}(x,a_{1:T},\mathcal M).
$$

The policy distribution is:

$$
a_t \sim \pi_\theta(\cdot\mid x,a_{<t},h,\mathcal M,B),
$$

where \(h\) contains authorized context such as hop index and remaining budget, and \(B\) is the edit or token budget.

Three implementations are distinguished:

1. **token policy:** keep/delete decisions per token plus insertions at gaps;
2. **span policy:** select a span, operation, and replacement candidate;
3. **hierarchical policy:** first choose a location and operation class, then choose content.

The hierarchical policy is expected to scale best when only a few edits are needed.

## 4. Associative Textual Memory

The memory is a set:

$$
\mathcal M=\{(s_j,e_j,\mu_j)\}_{j=1}^{K},
$$

where:

- \(s_j\) is an observed string;
- \(e_j=E_{\mathrm{fixed}}(s_j)\) is a frozen retrieval embedding;
- \(\mu_j\) stores provenance and performance metadata.

For an input span \(u\), the retriever returns candidate indices:

$$
\mathcal N_k(u)=\operatorname{TopK}_{j}
\operatorname{sim}(E_{\mathrm{fixed}}(u),e_j).
$$

The relay policy does not have to select the nearest candidate. It can score each candidate using similarity, historical survival, token cost, channel identity, and remaining depth:

$$
q_\theta(j\mid u)=f_\theta(
\operatorname{sim}(E(u),e_j),
\mu_j,
N-i,
B).
$$

Then:

$$
j\sim\pi_\theta(j\mid u,\mathcal N_k(u)).
$$

The stored string \(s_j\), not its vector, is inserted into the next prompt. The final interface remains discrete and auditable.

### 4.1 Stable and adaptive spaces

Using embeddings from a language model that is being updated would make memory geometry drift. The recommended design separates:

$$
e_j^{\mathrm{retrieval}}=E_{\mathrm{fixed}}(s_j)
$$

from a learned policy projection:

$$
e_j^{\mathrm{policy}}=P_\theta(e_j^{\mathrm{retrieval}}).
$$

The fixed space preserves identity and reproducibility; the projection adapts retrieval decisions to the current channel.

### 4.2 Reward-conditioned retrieval plasticity

Cosine search should be treated as a high-recall candidate generator, not as the final selection rule. The policy should not choose directly among all \(K\) memory entries. Instead, frozen semantic similarity produces a small candidate set, and a learned retrieval layer ranks those candidates by downstream utility:

$$
\text{semantic cosine recall}
\longrightarrow
\text{learned functional ranking}
\longrightarrow
\text{relay accept/reject/commit action}.
$$

Each memory entry may therefore retain both a frozen semantic key and a trainable functional key:

$$
m_j=(s_j,e_j,k_j,\mu_j),
\qquad
k_j^{(0)}=e_j.
$$

For a selected input span \(u_t\), local relay state \(h_t\), and remaining depth \(d_t\), a trainable query is:

$$
q_t=\operatorname{norm}
\left(
W_q[E_{\mathrm{fixed}}(u_t);E_{\mathrm{fixed}}(x);h_t;d_t]
\right).
$$

The first stage remains reproducible and uses only frozen semantic keys:

$$
\mathcal C_t=
\operatorname{TopK}_{j}
\cos(q_t,e_j).
$$

A contextual reranker then combines semantic affinity, learned functional affinity, historical utility, exploration, and cost:

$$
S_t(j)=
\alpha\cos(q_t,e_j)
+\beta\cos(q_t,k_j)
+\gamma U_\omega(h_t,j)
+\kappa\sqrt{\frac{\log T}{n_j+1}}
-\lambda C_j.
$$

Here \(U_\omega\) estimates whether chunk \(j\) has been useful in similar model, hop, role, and channel contexts; \(n_j\) is its usage count; and \(C_j\) includes token, leakage, and low-survival penalties. The exploration term prevents early successful chunks from monopolizing exposure before alternatives are tested.

Crucially, **selection alone must not increase future rank**. Promoting a chunk whenever it is chosen would create a self-reinforcing popularity loop in which early retrieval noise becomes permanent. The update should depend on downstream credit, preferably an advantage relative to the expected outcome:

$$
A_{t,j}=R_t-V_\eta(s_t).
$$

A simple functional-key update is:

$$
k_j\leftarrow
\operatorname{norm}
\left(k_j+\eta A_{t,j}q_t\right).
$$

Positive advantage moves the functional key toward similar future queries; negative advantage moves it away. A contextual utility estimate can be updated separately:

$$
U_{t+1}(h_t,j)
=
U_t(h_t,j)
+\eta_U\left(A_{t,j}-U_t(h_t,j)\right).
$$

Where credit is delayed across several retrieved chunks, the centralized critic may assign per-decision advantages, or counterfactual ablations may estimate whether replacing or removing a specific chunk changes terminal success. This is preferable to assigning the full terminal reward equally to every retrieval in a successful trajectory.

Successful trajectories also define contrastive training pairs. A chunk with positive attributed advantage is a positive key for its query, while exposed but unsuccessful alternatives are negatives:

$$
\mathcal L_{\mathrm{retrieval}}
=
-\log
\frac{
\exp(\cos(q_t,k_{j^+})/\tau)
}{
\sum_{j\in\mathcal C_t}
\exp(\cos(q_t,k_j)/\tau)
}.
$$

The architecture therefore separates four responsibilities:

1. the frozen semantic encoder preserves meaning and supports broad recall;
2. trainable query and functional keys learn task- and channel-specific accessibility;
3. the utility reranker learns contextual survival and cost;
4. the relay policy decides whether to bind, reject, or commit a candidate.

Utility should be conditioned on model family, checkpoint, hop depth, relay role, and memory version. A string may be useful as an initial transmitter code and harmful as a late relay code, or robust for one language-model family and brittle for another.

All functional keys, utility estimates, and rankings are frozen during held-out evaluation. They may be updated between training episodes, but never through a globally writable store during an evaluation trajectory. Every rollout records the retriever, key-table, and utility-model versions so that improvements in candidate delivery remain auditable and cannot become an undeclared side channel.

### 4.3 Memory provenance

Each entry should record at least:

```text
string
frozen embedding
functional retrieval key
embedding-model version
retriever and utility-model version
source model and checkpoint
source episode class
usage and exposure counts
attributed advantage and success rate
average survived hops
token cost
observer decodability
safety classification
```

Episode-specific target identities must not become direct retrieval keys in evaluation.

## 5. The Cooperative Partially Observed Game

The full chain is modeled as a cooperative partially observed Markov game. At hop \(i\):

1. the relay observes local text \(o_i=y_{i-1}\);
2. it samples an edit program \(a_i\);
3. the resulting prompt \(p_i\) is sent to \(M_i\);
4. the language model samples \(y_i\);
5. after the final hop, the receiver predicts \(\hat z\);
6. the trajectory receives a shared terminal reward.

A trajectory is:

$$
\tau=(z,o_0,a_0,p_0,y_0,\ldots,o_N,a_N,p_N,y_N,\hat z,R).
$$

Intermediate actors do not observe \(z\), prior hidden states, or the complete history unless those data are explicitly present in their incoming text. This preserves decentralized execution.

A centralized critic may receive privileged training information:

$$
V_\eta(z,\tau_{\le i},N-i,\text{versions}),
$$

while actors remain local. This is centralized training with decentralized execution.

## 6. Communication and Steering Are Different Objectives

### 6.1 Communication

The communication objective asks whether a target can be recovered after traversing the channel:

$$
J_{\mathrm{comm}}=
\mathbb E[\log q_\psi(z\mid y_N)]
-\lambda_C C(\tau).
$$

For discrete targets, terminal accuracy and cross-entropy are natural. For continuous representations, contrastive loss is preferable to raw cosine similarity because it requires discrimination among alternatives.

A contrastive receiver loss is:

$$
\mathcal L_R=-\log
\frac{\exp(\operatorname{sim}(\hat e,e_z)/\tau)}
{\sum_{z'}\exp(\operatorname{sim}(\hat e,e_{z'})/\tau)}.
$$

### 6.2 Steering

The steering objective asks whether the actual language-model output approaches a desired output distribution:

$$
J_{\mathrm{steer}}=
- d(F(y_N),F(y^*))
-\lambda_C C(\tau).
$$

Steering does not require a receiver. Communication can succeed even when the language-model output is not itself close to the target, provided the receiver reconstructs it.

Direct refusal bypass is a steering failure. Receiver-dependent reconstruction is an end-to-end communication failure. They require separate metrics.

## 7. Reward Design

For a benign exact-transmission task, a terminal reward can be:

$$
R=\mathbf 1[\hat z=z]
-\lambda_L L(\tau)
-\lambda_E E(\tau)
-\lambda_T T(\tau),
$$

where:

- \(L\) detects prohibited literal leakage;
- \(E\) counts edit operations;
- \(T\) counts inserted or transmitted tokens.

A receiver-confidence reward gives denser feedback:

$$
R_{\mathrm{conf}}=\log q_\psi(z\mid y_N).
$$

Potential-based shaping may use estimated recoverability:

$$
r_i=\gamma\Phi(s_{i+1})-\Phi(s_i),
$$

with \(\Phi\) trained to predict terminal success. The benchmark result must still be reported under terminal exact evaluation.

Penalizing insertion is necessary. Without it, a relay may ignore the incoming message and rewrite an unrestricted prompt. The paper therefore distinguishes constrained editors from unrestricted rewriters and treats the latter as a baseline.

## 8. Optimization Without Differentiating Through the Channel

The receiver is trained by ordinary backpropagation:

$$
\nabla_\psi\mathcal L_R.
$$

The relay policy is trained from sampled discrete actions:

$$
\nabla_\theta J=
\mathbb E\left[
\sum_i A_i\nabla_\theta
\log\pi_\theta(a_i\mid o_i,\mathcal M)
\right].
$$

PPO, actor-critic, REINFORCE with a learned baseline, or off-policy sequence methods are possible. PPO is a reasonable first implementation because edit programs can be collected on-policy and reused for a bounded number of epochs.

If the language model is trainable, its sampled tokens are also actions:

$$
\nabla_\phi J=
\mathbb E\left[
\sum_{i,k}A_{i,k}\nabla_\phi
\log\pi_\phi(y_{i,k}\mid p_i,y_{i,<k})
\right].
$$

The relay gradient does not pass through the language model. Both policies receive correlated reward but update from their own log probabilities.

## 9. Three Channel Regimes

### 9.1 Frozen channel

The language model is fixed:

$$
\phi=\phi_0.
$$

This tests whether relays discover representations robust to an existing language-model transformation.

### 9.2 Adapter-coadapted channel

The backbone is fixed and a small adapter is trainable:

$$
\phi=\phi_0+\Delta\phi_{\mathrm{adapter}}.
$$

This tests limited coadaptation while controlling cost and catastrophic forgetting.

### 9.3 Fully co-trained channel

All model weights may change. This tests joint invention of a communication protocol, but greatly increases the risk of private collusion and loss of ordinary language competence.

Results from these regimes are not interchangeable. Frozen-channel success supports a claim about invariants already present in the model. Co-trained success may only show that the components invented a private code.

## 10. Mixed Objective for Language-Model Training

A co-adapted language model should retain its ordinary language objective:

$$
\mathcal L_M=
\lambda_{PT}\mathcal L_{\mathrm{next-token}}
+\lambda_{SFT}\mathcal L_{\mathrm{relay-SFT}}
+\lambda_{RL}\mathcal L_{\mathrm{relay-RL}}
+\beta D_{KL}(\pi_\phi\|\pi_{\mathrm{ref}}).
$$

A constraint can require:

$$
\mathcal L_{\mathrm{next-token}}(\phi)
\leq
\mathcal L_{\mathrm{baseline}}+\epsilon.
$$

A practical first implementation alternates:

1. collect trajectories against a frozen language-model snapshot;
2. update the receiver frequently;
3. update the relay with PPO;
4. convert high- and low-reward trajectories into supervised or preference pairs;
5. update language-model adapters slowly by SFT or preference optimization;
6. freeze a new snapshot and resume relay training.

This avoids moving transmitter, channel, and receiver at the same speed.

## 11. Multiple Time Scales

Joint online updates make the environment highly non-stationary. The recommended ordering is:

$$
\text{receiver updates fastest}
>
\text{relay updates}
>
\text{language-model updates}
>
\text{curriculum updates slowest}.
$$

Versioned snapshots are part of the formal state. Every trajectory should record:

```text
relay checkpoint
language-model checkpoint
receiver checkpoint
memory version
embedding-model version
curriculum configuration
random seed
```

Old on-policy trajectories should not be treated as current after the channel changes. They may be discarded, down-weighted, replayed under the new snapshot, or reused only as offline supervised data.

## 12. Depth-Dependent Capacity

For target distribution \(Z\), depth \(N\), and budget \(B\), define an operational capacity:

$$
C_N(B)=
\sup_{\pi:\operatorname{cost}(\pi)\leq B}
I(Z;\hat Z_N).
$$

This is not the Shannon capacity of a stationary memoryless channel. Language-model channels are conditional, stateful through their prompts, and potentially heterogeneous. \(C_N(B)\) is an experiment-relative measure under fixed model versions, decoding family, and task distribution.

A per-hop retention diagnostic is:

$$
\rho_i=
\frac{I(Z;Y_i)}{I(Z;Y_{i-1})},
$$

estimated through probes or contrastive decoders. Values above one may occur when a channel expands a compressed code into a more decodable representation; they do not imply creation of information about \(Z\) beyond what entered the causal path.

## 13. Curriculum Optimization

A curriculum configuration is:

$$
c=(N,K,B,V,\eta,M,\tau,u),
$$

where:

- \(N\): relay depth;
- \(K\): target-set size;
- \(B\): edit and token budget;
- \(V\): insertion vocabulary;
- \(\eta\): channel stochasticity;
- \(M\): model family and memory difficulty;
- \(\tau\): task type;
- \(u\): trainable components unlocked at that stage.

The teacher should optimize learning progress rather than immediate task reward. For task cell \(c\):

$$
LP_t(c)=q_t(c)-q_{t-w}(c).
$$

A practical teacher combines a prerequisite graph, a bandit score, and replay against forgetting:

$$
S_t(c)=
\alpha LP_t(c)
+\beta\sqrt{\frac{\log t}{n_t(c)+1}}
+\gamma F_t(c)
-\delta\operatorname{Cost}(c).
$$

The curriculum begins with receiver identification and one-hop direct transmission, then introduces editing, associative retrieval, multiple hops, literal bans, distractor memories, heterogeneous channels, coadapted adapters, and finally frozen evaluation on unseen targets, models, and depths.

## 14. Distributed Training

Rollout generation can be distributed independently from policy learning:

```text
Target sampler
    -> rollout workers
       [relay snapshot, LLM snapshot, frozen retriever, memory snapshot]
    -> trajectory store
    -> receiver learner
    -> relay learner
    -> optional LLM-adapter learner
    -> curriculum teacher
```

Workers may use local language models or remote black-box APIs. The learner receives action log probabilities, values, version identifiers, outputs, and terminal rewards.

The global vector store must be read-only during an evaluation episode. A globally writable store would permit the sender to deposit the target and the receiver to retrieve it without information traversing the language-model chain.

## 15. Side-Channel Controls

A valid relay benchmark should prohibit or audit:

- shared recurrent state across hops;
- episode IDs correlated with targets;
- writable global memory during episodes;
- access by intermediate actors to the original target;
- hidden access to prior messages not present in current text;
- target-specific retrieval keys;
- shared random seeds that encode the target;
- uncontrolled metadata in API calls;
- receiver access to the sender's private state.

Each relay invocation should begin from a clean episodic hidden state unless the state itself is part of the declared textual channel.

## 16. Baselines and Ablations

The minimum comparison set is:

- no relay;
- manual public codec;
- random editing;
- delete-only relay;
- insert-only relay;
- insert-and-delete relay;
- associative retrieval without RL;
- cosine-only retrieval;
- cosine retrieval with a learned reranker;
- reward-conditioned functional keys;
- ART with frozen memory;
- unrestricted textual rewriter;
- position-specific relay policies;
- one shared relay policy;
- frozen language model;
- adapter-coadapted language model;
- fully co-trained language model;
- receiver trained jointly versus receiver frozen;
- semantic targets versus random nonces.

Critical ablations remove:

- associative memory;
- memory performance metadata;
- functional retrieval keys;
- contextual utility ranking;
- retrieval exploration bonus;
- attributed advantage, replacing it with selection-only promotion;
- edit-cost penalty;
- centralized critic;
- curriculum adaptation;
- replay against forgetting;
- cross-model training;
- language-model ordinary-text objective.

## 17. Safety Scope

The architecture is a general black-box prompt and communication optimizer. A target-conditioned steering reward can be repurposed to optimize refusal bypass. A receiver-conditioned communication reward can create a covert end-to-end channel even when the language model never emits the target directly.

The proposed first benchmark therefore excludes real harmful requests and uses:

- benign natural words;
- random identifiers;
- synthetic literal prohibitions;
- constrained edit actions;
- frozen evaluation memory;
- no release of broadly transferable policy-evasion weights.

Safety evaluation should report direct generation and receiver reconstruction separately.

## 18. Falsifiable Hypotheses

### H1: Channel-adapted coding

ARTs will select strings based on survival through the language-model channel, not merely nearest embedding similarity.

### H2: Shared-policy depth transfer

A relay policy shared across hops will extrapolate to greater depths better than position-specific policies, though it may learn more slowly.

### H3: Semantic advantage under frozen channels

Semantically structured codes will survive frozen pretrained language-model channels better than arbitrary codes at matched token cost.

### H4: Arbitrary-code advantage under coadaptation

Co-trained channels will support more compact arbitrary protocols than frozen channels, but those protocols will transfer less well to unseen models.

### H5: Associative memory improves sample efficiency

A frozen, provenance-aware textual memory will reduce the number of rollouts required to rediscover robust strings.

### H6: Reward-conditioned retrieval improves candidate quality

At matched cosine candidate-pool size, a retriever with functional keys and contextual utility trained from attributed downstream advantage will increase useful-chunk recall and reduce relay sample complexity relative to cosine-only retrieval. Selection-only promotion is expected to collapse toward early popular chunks and transfer worse.

### H7: Memory can harm transfer

Memory entries optimized for one model family may reduce performance on another unless model identity or uncertainty is represented.

### H8: Private-code opacity

A jointly trained receiver may recover targets from texts that independent receivers and humans cannot decode.

### H9: Ordinary-language regularization limits collusion

Next-token and reference-policy constraints will improve transfer and observer decodability at the cost of lower within-pair channel capacity.

### H10: Curriculum by learning progress outperforms depth-only curricula

A curriculum that adapts across target entropy, memory ambiguity, depth, and channel variability will reach fixed held-out performance with fewer language-model calls.

### H11: Capability duality is conditional, not automatic

Broad benign steering performance will correlate with synthetic policy-evasion performance, but narrow communication policies will not necessarily generalize to arbitrary refused targets.

## 19. Limitations

The operational capacity depends on the receiver family and cannot establish an observer-independent amount of meaning. Mutual-information estimates in high-dimensional text are difficult and should be supported by exact finite-class tasks.

A relay may exploit tokenizer artifacts or API formatting rather than meaningful language-model transformations. Tokenizer and serialization permutations are needed.

Joint training may produce degenerate collusion. Cross-model swaps, independent receivers, adapter removal, and frozen-channel replications are necessary before claiming a general communication phenomenon.

Reward-conditioned retrieval adds another source of path dependence. Early noisy advantages can distort functional keys, and correlated chunk sequences make individual credit difficult. Exposure logging, exploration, counterfactual replacement tests, held-out query families, and comparison with frozen semantic retrieval are required before claiming that the learned ranker discovered generally useful chunks.

The language-model call is expensive even when the relay network is small. Training is likely to be inference-bound and sample-inefficient rather than GPU-memory-bound.

Finally, the formalism describes capability, not authorization. Whether a recoverable signal is a legitimate code or a policy violation depends on the deployment's declared users, receivers, and end-to-end policy.

## 20. Conclusion

RL relay transducers make the space between language-model calls trainable without requiring differentiable access to the models themselves. Their actions remain discrete and inspectable. Associative memory lets them reuse strings associated with useful embedding regions. A frozen cosine layer preserves semantic recall, while reward-conditioned functional keys and contextual utility learn which retrieved strings actually survive and help in particular channel contexts. Receivers learn what survived; relay policies learn how to preserve or steer it; language models can remain frozen or slowly coadapt.

This architecture provides a controlled setting for studying communication through LLMs, black-box textual control, multi-hop credit assignment, learned codebooks, private protocols, and compositional safety. The central empirical question is not simply whether a prompt can cause a desired output. It is whether a learned discrete policy can construct representations that remain recoverable across repeated stochastic transformations, and whether those representations describe general properties of language-model channels or only private agreements among co-trained components.