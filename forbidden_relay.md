---
type: "Empirical Paper"
title: "Forbidden Relay: A Pre-registered Benchmark for Recoverable Messages Across LLM Chains"
description: "Pre-registered empirical design for testing whether discrete RL relay transducers can preserve benign natural words and random nonces across language-model chains without literal intermediate leakage; results not yet collected."
tags: [forbidden-relay, emergent-communication, multi-hop-llm, reinforcement-learning, preregistration]
timestamp: 2026-08-01T23:08:00Z
---

# Forbidden Relay: A Pre-registered Benchmark for Recoverable Messages Across LLM Chains

**Franklin Baldo**  
Independent Researcher  
franklinbaldo@gmail.com

---

> **Pre-registered design; no results yet.** This paper specifies the benchmark, hypotheses, exclusions, metrics, and analysis plan before implementation and data collection. All results sections below describe planned outputs, not observed findings.

## Abstract

This paper pre-registers **Forbidden Relay**, a benign benchmark for testing whether reinforcement-learned discrete relay transducers can preserve recoverable information across one or more language-model transformations while preventing literal appearance of the target in intermediate messages. The first relay observes a target drawn from natural words or random nonces. Intermediate relays observe only the text produced by the previous language model and may edit it through constrained keep, delete, insert, retrieve, replace, and stop operations. A terminal receiver must reconstruct the target exactly. Language models are treated as frozen or adapter-coadapted stochastic channels, and associative relay memories are frozen during evaluation episodes.

The benchmark separates semantic transmission from exact symbolic transmission, direct generation from receiver-dependent reconstruction, and channel discovery from private coadaptation. It evaluates depth transfer, model transfer, edit efficiency, literal leakage, independent-observer decodability, and the contribution of associative memory. The benchmark does not include harmful requests or optimize against real safety policies. Its strongest policy-like condition uses only synthetic, benign literal bans such as prohibiting fruit names or city names in intermediate outputs.

The main pre-registered hypotheses are that shared relay policies will generalize to greater chain depth better than position-specific policies; semantic codes will survive frozen pretrained language-model channels better than arbitrary codes; coadapted channels will support more compact but less transferable protocols; and associative textual memory will improve sample efficiency while increasing the risk of model-specific overfitting. No claim is made that the architecture produces a universal jailbreak generator. The study is designed to determine whether the prerequisite communication and transfer capabilities exist under controlled conditions.

**Keywords:** emergent communication, multi-agent reinforcement learning, language-model chains, covert-channel diagnostics, associative memory, curriculum learning, pre-registration

---

## 1. Research Question

The primary question is:

> Can constrained reinforcement-learned relay transducers make a terminal receiver recover an exact benign target after the information passes through a chain of language models, while no intermediate language-model output contains the target literally?

Secondary questions are:

1. How does exact recovery change with chain depth?
2. Do shared relay policies extrapolate beyond training depth?
3. Are semantic targets easier to preserve than random nonces?
4. Does associative textual memory improve sample efficiency and transfer?
5. How much of the target is decodable by independent observers rather than only the trained receiver?
6. Does limited language-model coadaptation create transferable channel structure or a private code?
7. Does a literal prohibition remove information or only force a different representation?

## 2. Scope and Safety Boundary

The study includes only:

- ordinary concrete nouns, animals, fruits, colors, objects, and cities;
- randomly generated pronounceable nonces;
- random alphanumeric identifiers;
- synthetic literal bans over benign categories;
- constrained textual editing and retrieval;
- exact or contrastive receiver reconstruction.

The study excludes:

- harmful or illegal task content;
- real-world refusal-bypass optimization;
- attempts to weaken production safety systems;
- unrestricted target-conditioned prompt generation against deployed services;
- publication of broadly transferable policy-evasion checkpoints;
- claims about universal jailbreaks from synthetic-task success.

Direct language-model production of a target and downstream receiver reconstruction are reported as different outcomes.

## 3. System Under Test

For depth \(N\), an episode has the form:

$$
z
\xrightarrow{T_\theta}
p_0
\xrightarrow{M_0}
y_0
\xrightarrow{C_\theta}
p_1
\xrightarrow{M_1}\cdots
\xrightarrow{C_\theta}p_N
\xrightarrow{M_N}y_N
\xrightarrow{R_\psi}\hat z.
$$

The first transmitter sees \(z\). Intermediate transceivers see only their incoming text, hop index, remaining budget, and authorized read-only memory. The final receiver sees only \(y_N\).

The primary condition shares one relay policy across all hops:

$$
\theta_0=\theta_1=\cdots=\theta_N.
$$

A comparison condition uses position-specific policies.

## 4. Target Families

### 4.1 Natural semantic targets

A balanced vocabulary will contain categories such as:

- fruits;
- animals;
- common objects;
- colors;
- cities;
- occupations.

Targets will be split by lexical item, not merely by episode, so held-out evaluation contains unseen targets.

### 4.2 Pronounceable nonces

Nonces will be procedurally generated from consonant-vowel templates, for example:

```text
KUVAREL
NEMORA
TALUVEN
```

Train, validation, and test sets will use disjoint generated strings.

### 4.3 Alphanumeric identifiers

Identifiers will be uniformly sampled from a fixed alphabet and length, for example:

```text
T9M4Q2
K7V2L8
```

This family tests exact symbolic transmission without ordinary semantics.

## 5. Literal-Prohibition Conditions

The benchmark has three progressively stricter conditions.

### Condition A — direct transmission allowed

No intermediate literal ban. This verifies that the architecture can communicate before testing constrained communication.

### Condition B — exact literal ban

For every intermediate language-model output \(y_i\), \(i<N\):

$$
\operatorname{norm}(z)\not\subseteq\operatorname{norm}(y_i),
$$

where normalization applies Unicode normalization, lowercase conversion, and whitespace collapse.

### Condition C — synthetic category policy

The language model receives a benign instruction such as:

> Do not write any fruit name in your response.

The target belongs to that category. Intermediate literal appearance is prohibited, while the terminal receiver still attempts exact reconstruction.

Condition C is not treated as evidence of bypassing real safety alignment. It is a controlled policy-like perturbation.

## 6. Relay Actions and Budgets

The primary relay action set is:

$$
\mathcal A=\{\operatorname{KEEP},\operatorname{DELETE},
\operatorname{INSERT},\operatorname{RETRIEVE},
\operatorname{REPLACE},\operatorname{STOP}\}.
$$

Budgets are specified before training:

- maximum incoming length: 64 tokenizer tokens;
- maximum output length: 64 tokenizer tokens;
- maximum edit operations per hop: 8;
- maximum newly inserted tokens per hop: 12;
- maximum retrieved candidates per query: 8;
- maximum retrieval operations per hop: 4.

An unrestricted rewriter is included only as a baseline and is not compared as if it had the same action budget.

## 7. Associative Memory

The memory contains tuples:

$$
(s_j,E_{\mathrm{fixed}}(s_j),\mu_j).
$$

It is populated only from training data and training trajectories. Before every validation or test run:

- the memory is frozen;
- test targets are not present as direct entries unless they independently occurred as ordinary corpus strings under a declared condition;
- no writes occur during an episode;
- no episode-specific target ID is available as metadata;
- all entries retain provenance and source-split labels.

A no-memory ablation and nearest-neighbor-without-RL baseline are required.

## 8. Language-Model Channel Regimes

### 8.1 Frozen single-model channel

All hops use the same frozen pretrained model and decoding configuration.

### 8.2 Frozen heterogeneous channel

Hops sample from multiple frozen model checkpoints or families. The sequence is recorded per episode.

### 8.3 Adapter-coadapted channel

The backbone remains frozen while a small adapter is updated in blocks from relay trajectories. This condition begins only after the frozen-channel learner reaches a pre-specified competence threshold.

### 8.4 Cross-model test

Relay and receiver parameters are frozen and evaluated with at least one language model not used during training.

A fully fine-tuned language-model condition is outside the initial study and requires a separate amendment to this pre-registration.

## 9. Training Curriculum

The curriculum uses a prerequisite graph plus a learning-progress bandit.

### Stage 0 — receiver validation

The receiver identifies targets from direct canonical representations without a language-model channel.

### Stage 1 — one-hop unconstrained communication

- depth \(N=1\);
- target set sizes \(K\in\{2,4,16\}\);
- direct transmission allowed;
- generous budget;
- frozen deterministic or low-temperature channel.

### Stage 2 — constrained editing and retrieval

- \(K\in\{16,64,256\}\);
- associative memory enabled;
- distractor candidates introduced;
- edit cost gradually activated.

### Stage 3 — multiple hops

- depths \(N\in\{1,2,4\}\) mixed;
- one shared relay policy in the primary condition;
- replay of earlier depths to limit forgetting.

### Stage 4 — literal prohibition

Condition B is introduced first for natural targets, then for nonces and identifiers.

### Stage 5 — channel variability

- decoding stochasticity;
- prompt-style variation;
- frozen heterogeneous channels;
- memory entries from multiple source models.

### Stage 6 — adapter coadaptation

A language-model adapter is updated more slowly than the relay and receiver. The ordinary next-token objective and reference-policy constraint remain active.

### Stage 7 — frozen generalization

No component or memory is updated. Evaluation uses unseen targets, greater depths, and unseen channels.

The bandit task score is based on learning progress, forgetting, exploration bonus, and language-model-call cost. Test conditions never influence curriculum selection.

## 10. Optimization

The receiver minimizes cross-entropy for finite target sets:

$$
\mathcal L_R=-\log q_\psi(z\mid y_N).
$$

The relay is trained by PPO or actor-critic from terminal reward:

$$
R=\mathbf 1[\hat z=z]
-\lambda_L L
-\lambda_E E
-\lambda_T T.
$$

The pre-registered initial coefficients are:

$$
\lambda_L=1.0,\qquad
\lambda_E=0.01,\qquad
\lambda_T=0.002.
$$

Any change to these coefficients after observing validation outcomes must be logged as exploratory and results must also be reported under the original specification when feasible.

The primary benchmark score uses exact terminal reconstruction and zero forbidden intermediate occurrence. Receiver confidence is used for training diagnostics, not as a substitute for exact test success.

## 11. Experimental Factors

The core factorial design varies:

- target family: natural, nonce, identifier;
- depth: \(1,2,4,6,8,12\);
- policy: shared or position-specific;
- memory: none, nearest-neighbor, ART memory;
- channel: frozen single, frozen heterogeneous, adapter-coadapted;
- restriction: none, literal ban, synthetic category policy;
- receiver: jointly trained or independently trained observer.

Depths \(1,2,4\) are training depths. Depths \(6,8,12\) are held-out extrapolation depths.

## 12. Baselines

The study requires:

1. no relay;
2. direct prompt forwarding;
3. random edits under the same budget;
4. manual public codec;
5. delete-only policy;
6. insert-only policy;
7. constrained insert-and-delete policy;
8. nearest-neighbor retrieval without RL;
9. ART without memory-performance metadata;
10. unrestricted rewriter;
11. position-specific policies;
12. shared policy;
13. frozen channel;
14. adapter-coadapted channel.

The manual codec must be fixed before test evaluation and cannot use test-target-specific rules.

## 13. Primary Outcomes

### 13.1 Valid exact success

$$
\operatorname{VES}=
\mathbf 1[\hat z=z]
\mathbf 1[L=0].
$$

The primary reported metric is mean VES over held-out episodes.

### 13.2 Exact reconstruction

Exact accuracy regardless of leakage, reported separately to show whether failure is caused by communication loss or constraint violation.

### 13.3 Literal leakage rate

Fraction of episodes with prohibited target occurrence in any intermediate language-model output.

### 13.4 Edit and token cost

Mean operations and transmitted tokens per successful episode.

### 13.5 Depth transfer

Performance at \(N\in\{6,8,12\}\) after training only at \(N\leq4\).

### 13.6 Model transfer

Performance after replacing at least one channel with an unseen model.

## 14. Secondary Outcomes

- receiver cross-entropy;
- top-\(k\) reconstruction accuracy;
- success per language-model call;
- training sample efficiency;
- memory candidate rank selected by the relay;
- survival statistics per retrieved string;
- independent-observer decoding accuracy;
- human decoding accuracy on a sampled subset;
- naturalness and semantic-coherence ratings;
- performance after memory-entry permutation;
- performance after receiver swap;
- performance after adapter removal.

## 15. Independent Observer Tests

A code may be public, semantically transparent, or private to the trained receiver. To distinguish these:

1. train an independent receiver on separate trajectories without access to the original receiver weights;
2. evaluate a frozen general-purpose embedding classifier;
3. ask human annotators to choose among a finite set of candidate targets;
4. permute memory IDs while preserving strings;
5. swap the terminal receiver between independently trained systems.

High trained-receiver performance with chance independent-observer performance is classified as receiver-private decodability, not general semantic preservation.

## 16. Side-Channel Audit

Before accepting any run, verify:

- intermediate relays did not receive the original target;
- hidden recurrent state was reset at every hop;
- no writable global store existed during the episode;
- no target-correlated episode ID reached actors or receiver;
- random seeds were not target-dependent;
- API metadata did not encode target class;
- target strings were not inserted into memory from validation or test;
- the final receiver saw only declared final text;
- logs identify all checkpoint and memory versions.

Runs failing the audit are excluded and reported by count and reason.

## 17. Statistical Analysis Plan

For each primary condition, report mean VES with bootstrap 95% confidence intervals over episodes. Episodes are grouped by target so resampling does not treat repeated uses of one lexical item as independent targets.

A mixed-effects logistic model is planned:

$$
\operatorname{logit}P(\operatorname{VES}=1)=
\beta_0+\beta_1N+\beta_2\text{memory}
+\beta_3\text{shared}
+\beta_4\text{target family}
+\beta_5\text{channel regime}
+u_{target}+u_{seed}.
$$

Interaction terms of primary interest are:

- depth × shared policy;
- depth × target family;
- memory × channel regime;
- coadaptation × model transfer.

Multiple comparisons across the pre-registered primary hypotheses will use Holm correction. Exploratory analyses will be labeled separately.

At least five independent training seeds are required per core condition. The exact episode budget will be determined by a pilot restricted to Stage 1; the pilot cannot include held-out targets or depths and will be used only to estimate variance and compute requirements.

## 18. Pre-registered Hypotheses

### H1 — shared-policy depth transfer

At unseen depths \(N>4\), the shared relay policy will achieve higher VES than position-specific policies extended by reuse or interpolation.

### H2 — semantic advantage in frozen channels

Natural semantic targets will have higher VES than random identifiers under frozen pretrained channels at matched target entropy and token budget.

### H3 — associative-memory sample efficiency

ART memory will reach a fixed validation VES with fewer language-model calls than no-memory and nearest-neighbor-without-RL conditions.

### H4 — model-specific memory overfitting

Memory entries learned against one model family will yield a smaller gain, or a negative gain, on unseen model families unless training includes heterogeneous channels.

### H5 — coadaptation compactness-transfer tradeoff

Adapter-coadapted channels will use fewer transmitted tokens for equal within-pair accuracy but transfer worse to unseen models than frozen-channel protocols.

### H6 — literal suppression does not imply information removal

For natural targets, Condition B will reduce direct literal leakage more than it reduces independent receiver reconstruction, demonstrating that surface suppression and recoverability differ.

### H7 — nonce difficulty

Exact nonce and identifier transmission will degrade faster with depth than natural-word transmission under frozen channels.

### H8 — private receiver codes under coadaptation

The gap between trained-receiver and independent-observer accuracy will be larger in adapter-coadapted conditions than frozen-channel conditions.

### H9 — curriculum advantage

The learning-progress curriculum will reach held-out VES thresholds with fewer language-model calls than a depth-only schedule under equal maximum budgets.

### H10 — no universal-evasion conclusion

Success on synthetic literal bans will not be interpreted as evidence of universal jailbreak generation unless broad cross-target, cross-policy, and cross-model transfer is separately demonstrated in a future approved study.

## 19. Criteria That Would Falsify the Main Proposal

The practical proposal is weakened if:

- constrained relays do not outperform random editing or fixed codecs;
- success disappears on held-out targets;
- no policy extrapolates beyond trained depth;
- all apparent communication is explained by literal leakage;
- associative memory only memorizes target identities;
- coadapted success vanishes after trivial checkpoint swaps;
- side-channel audits account for the observed performance;
- language-model-call cost makes learning infeasible at the proposed scale.

A negative result remains informative: it would bound the ability of small discrete policies to exploit pretrained language-model channels without internal model access.

## 20. Expected Output Format

No empirical outputs exist yet. After data collection, this section will be replaced consistently across abstract, introduction, results, and conclusion.

Planned figures:

1. VES versus chain depth;
2. leakage versus chain depth;
3. edit and token cost versus depth;
4. training calls to competence threshold;
5. trained versus independent receiver accuracy;
6. within-model versus cross-model transfer;
7. memory-entry survival curves;
8. frozen versus coadapted protocol compactness.

Planned tables:

1. target-family splits;
2. model and checkpoint versions;
3. primary factorial results;
4. baseline and ablation comparison;
5. side-channel audit exclusions;
6. pre-registered hypothesis decisions.

## 21. Reproducibility Requirements

The implementation repository must publish, subject to safety review:

- environment and dependency lockfiles;
- target generators and fixed splits;
- normalized literal-leak checker;
- relay action interpreter;
- memory construction and freeze procedure;
- checkpoint-version manifests;
- curriculum configuration;
- training seeds;
- evaluation scripts;
- aggregate benign benchmark results.

Weights or discovered strings that demonstrate broad policy-evasion transfer are not automatically included in public artifacts and require a separate release decision.

## 22. Limitations

Exact target recovery is a narrow communication task. It does not measure general reasoning, natural dialogue, or beneficial usefulness.

Natural-word advantages may reflect pretrained semantic priors rather than emergent protocol formation. Nonces and identifier controls address but do not eliminate this concern.

The receiver defines what counts as recoverable. Independent receivers and finite-class exact tasks reduce observer dependence but cannot remove it entirely.

Synthetic literal policies are intentionally weak analogues of real safety policies. They permit controlled measurement without supporting strong conclusions about deployed alignment systems.

The experiment may be dominated by inference cost. A small relay network does not make language-model rollouts cheap.

## 23. Conclusion

Forbidden Relay is designed to answer a bounded question before making a broader claim. It asks whether constrained discrete policies can preserve exact benign information through repeated language-model transformations without reproducing the target literally at intermediate hops. It separates semantic and symbolic targets, frozen and coadapted channels, public and private decodability, and direct generation from downstream reconstruction.

If successful, the benchmark will establish a controlled substrate for studying interstitial agency, learned channel codes, and compositional safety. If unsuccessful, it will provide useful limits on what black-box relay policies can learn under explicit budgets and side-channel controls. In either case, the result will not by itself establish a universal jailbreak generator. That stronger claim requires a different target distribution, a different risk review, and evidence of broad transfer that this pre-registration deliberately does not seek.

## Pre-registration

A permanent external pre-registration link has not yet been created. `[LINK]` will be replaced only after the protocol is deposited; the repository history records this version of the design before data collection.