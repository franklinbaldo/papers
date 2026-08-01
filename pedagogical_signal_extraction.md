---
type: "Technical Paper"
title: "Structured Irregularity: Learning as Signal Extraction in Noisy Pedagogical Channels"
description: "Position paper on optimal learners, progressive decodability, retrospective interpretation, and the distinction between noise and temporarily opaque structure."
tags: [machine-teaching, noisy-channels, progressive-decodability, predictive-information, learner-modeling]
timestamp: 2026-07-31T14:15:00Z
---

# Structured Irregularity: Learning as Signal Extraction in Noisy Pedagogical Channels

**Franklin Baldo**  
Independent Researcher  
franklinbaldo@gmail.com

---

> **Position paper.** This article develops a conceptual and experimental framework. It reports no empirical results. Its claims about optimal pedagogy, optimal learners, progressive decodability, and structured irregularity are hypotheses to be formalized and tested.

## Abstract

A teacher may know a deterministic function while communicating through a channel that is noisy, partially opaque, historically layered, or poorly matched to the learner. The learner's problem is therefore not merely to recover a clean message. It is to determine which apparent irregularities are exogenous noise, which are structured signals not yet decodable, and which inferred patterns will continue to predict future demonstrations and task behavior.

This paper distinguishes two regimes. In the **ideal pedagogical regime**, an optimal teacher communicates with an optimal learner and the research problem is to identify the shortest or most efficient message that induces a target competence. In the **ecological regime**, teachers and learners are imperfect, the channel is noisy, conventions may initially be unknown, and earlier observations may become interpretable only after later structure has been acquired.

The central hypothesis is that optimal teaching does not reduce to maximal compression or maximal raw entropy. An optimal pedagogical message may use highly diverse, locally irregular demonstrations while preserving a stable higher-order grammar that makes those demonstrations progressively decodable. The complementary learner hypothesis is that a good learner is not the system that finds the greatest number of patterns in a finite transcript, but the system that extracts compact invariants that survive new data, perturbation, and intervention while improving prediction of primitive future observations and execution of the target function. In the binary benchmark, the externally scored predictive task is next-bit prediction. Tokens, segments, and higher-order symbols are endogenous, context-dependent instruments that the learner may construct because they make prediction, transfer, or action more efficient; they are not privileged targets supplied by the benchmark.

The paper proposes operational distinctions among noise, opacity, concealment, and signal; defines progressive decodability and retrospective interpretation; sketches a learner-relative objective; and presents experiments for separating genuine structure discovery from compression-based overfitting.

**Keywords:** machine teaching, noisy channels, progressive decodability, structured irregularity, predictive information, retrospective interpretation, invariance, pedagogical communication

---

## 1. The Problem

Learning from a teacher is often modeled as if the teacher selected examples from a known space and the learner interpreted them through an already shared representation. Real communication is less orderly. The teacher may use a convention the learner has not yet inferred. The channel may corrupt or omit evidence. The learner may initially treat a meaningful symbol as noise. A later demonstration may reveal a grammar that retrospectively changes the interpretation of the entire prior transcript.

This creates a basic ambiguity. At time $t$, an unexplained regularity may be:

1. exogenous channel noise;
2. a lawful feature of the teacher's policy;
3. an encoded layer whose decoding rule has not yet been learned;
4. an accidental finite-sample coincidence;
5. deliberate concealment with no pedagogical path to recovery.

These categories cannot generally be distinguished from one observation. They separate only through continued interaction, out-of-sample prediction, interventions, or explicit assumptions about the teacher.

The resulting research question is broader than denoising:

> What makes a learner capable of extracting the pedagogically relevant invariants of a noisy or initially opaque interaction, and what form does an optimal teaching message take for such a learner?

This question complements self-tokenizing generative machine teaching. That framework asks how demonstrations can construct both a competence and the symbolic vocabulary used to express it. The present paper asks what the learner is doing when parts of that emerging vocabulary are not yet readable, and why an optimized curriculum might nevertheless become progressively clear.

---

## 2. Scope: Deterministic Target, Uncertain Interaction

Let the target be a deterministic function:

$$
f:X\rightarrow Y.
$$

A teacher knows $f$ and follows a policy $\pi_T$ that selects a transmitted message $x_t$ from the target, the interaction history, and possibly a model of the learner:

$$
x_t=\pi_T(f,H_{t-1},\widehat A_t).
$$

The learner need not observe $x_t$ directly. A channel $Q$ produces:

$$
y_t\sim Q(\cdot\mid x_t,H_{t-1}).
$$

The learner updates an internal model:

$$
M_t=U_A(M_{t-1},y_t).
$$

In the strict binary track, $y_t\in\{0,1\}$ and the primitive predictive objective is:

$$
-\log p_A(y_{t+1}\mid y_{1:t}).
$$

The learner may internally encode a context-dependent substring as one token, a sequence of learned tokens as a higher-order token, or no token at all. These representations are justified by their contribution to prediction and competence, not by literal agreement with a canonical segmentation. Two learners may therefore construct different registries while being functionally equivalent at the observable bit interface.

The target is deterministic in this paper so that uncertainty about the interaction can be separated from uncertainty in the target itself. This restriction is methodological, not a claim that stochastic processes contain no learnable information. A stochastic target can communicate a stable distribution or conditional law, but it raises a different identification problem.

Even with deterministic $f$, three sources of uncertainty remain:

- **teacher uncertainty:** the learner does not initially know $\pi_T$;
- **channel uncertainty:** the learner does not know which observed variation comes from $Q$;
- **representation uncertainty:** the learner does not initially know how $x_t$ or $y_t$ should be segmented and interpreted.

The learner therefore learns not only $f$, but also enough of the teacher, channel, and representational protocol to identify which aspects of the transcript are relevant to $f$. The hierarchy is: primitive observations are evidence, prediction and task competence are the externally evaluated objectives, and tokens are revisable internal instruments for reaching those objectives.

---

## 3. Two Regimes of Pedagogy

### 3.1 Ideal pedagogical regime

In the ideal regime:

- the teacher is optimized for a specified learner;
- the learner is optimized for the task family;
- the channel is noiseless or its noise law is known;
- the communication budget is explicit;
- competence is measured on held-out inputs.

The objective is to find an efficient teaching sequence:

$$
C^*_{A,f}
=
\arg\min_C J(C;A,f)
$$

subject to:

$$
\Pr[\operatorname{Score}(A(C),f)\geq q]\geq r.
$$

This regime supports the theoretical question: **what is the optimal message for teaching a target function to an optimal learner?**

### 3.2 Ecological regime

In the ecological regime:

- the teacher may be inconsistent, incomplete, or only approximately pedagogical;
- the learner may be misspecified;
- the channel introduces corruption, omission, timing variation, or irrelevant context;
- conventions are acquired gradually;
- some observations become meaningful only after later observations.

Here the problem is not to recover one predetermined clean string. It is to construct a model that separates predictive structure from variation that does not support future inference.

The ecological regime should not be treated merely as a degraded ideal regime. It includes a phenomenon absent from ordinary denoising: **retrospective interpretation**. A later-acquired rule can turn an earlier opaque event into evidence.

---

## 4. Noise Is Learner-Relative

A bit or symbol is not intrinsically noise. It is noise relative to a model, task, and stage of learning.

Let $H_t=y_{1:t}$ be the observed history. A component $z$ of $H_t$ may be uninformative under the current model $M_t$ but useful under a later model $M_{t+k}$. We call this **temporary opacity** rather than noise when there exists a finite extension of the interaction under which $z$ contributes to improved prediction or task performance.

### 4.1 Exogenous noise

Exogenous noise is variation introduced by the channel that does not encode the teacher's target or policy. Under a correctly specified model, learning it does not improve prediction of the target beyond modeling the channel itself.

### 4.2 Endogenous opacity

Endogenous opacity is structured information emitted by the teacher whose decoding rule is not yet available to the learner. Identifiers, delimiters, or higher-order token references may initially appear arbitrary and become interpretable later.

### 4.3 Accidental pattern

An accidental pattern compresses or fits the observed history but fails under new samples, longer sequences, mark permutations, or controlled interventions.

### 4.4 Concealment

Concealment occurs when information is transformed so that no recovery path is supplied within the interaction or shared prior assumptions. Concealment may be communication for another recipient, but it is not pedagogy for the specified learner. It is outside the central teaching problem.

This taxonomy prevents a premature rule that all arbitrary identifiers or opaque codes are invalid. A free identifier can be part of a legitimate pedagogical language if its role becomes inferable through interaction. The relevant question is not whether the code looks arbitrary locally, but whether its structure is recoverable and useful for the learner within the teaching horizon.

---

## 5. Progressive Decodability

The paper's central conjecture is that optimized pedagogy tends toward **progressive decodability**.

Informally, a curriculum is progressively decodable when successive portions of the interaction expose reusable structure that makes later messages easier to interpret and may also reinterpret earlier messages. The curriculum need not be locally simple. It must have a stable route from local evidence to increasingly predictive representations.

Let $M_t$ be the learner's model after prefix $H_t$. Let $L_{\mathrm{future}}(M_t)$ be predictive loss on future teacher actions or held-out executions of $f$. Define the predictive gain of stage $t$ by:

$$
G_t
=
L_{\mathrm{future}}(M_{t-1})
-
L_{\mathrm{future}}(M_t).
$$

A staged curriculum is $\delta$-progressively decodable for learner $A$ when, at designated stage boundaries,

$$
\mathbb E[G_t]\geq \delta_t\geq 0,
$$

and every charged message component either contributes to predictive or task gain within a finite horizon or is classified as channel overhead.

This is stronger than the trivial statement that an ideal Bayesian observer cannot lose expected information by receiving additional data. It requires an operational path by which the specified learner extracts structure from the actual representation and demonstrates that structure out of sample.

### 5.1 Retrospective gain

Let $z_i$ be an earlier observation. Its retrospective gain at time $t>i$ is:

$$
R_{i,t}
=
L_{\mathrm{future}}(M_t^{-z_i})
-
L_{\mathrm{future}}(M_t),
$$

where $M_t^{-z_i}$ is trained or inferred from the same history with $z_i$ removed or masked. A positive $R_{i,t}$ after negligible gain at time $i$ measures the extent to which later structure made earlier evidence usable.

This captures layered knowledge formation: first the learner acquires the protocol, then the protocol unlocks the code, and the decoded layer supports acquisition of the target function.

---

## 6. Structured Irregularity

A pedagogically optimal message need not be repetitive or low entropy. Repetition can establish a code, but excessive regularity carries little new information. Conversely, maximally irregular data without a stable protocol may be incomprehensible.

The proposed resolution is **structured irregularity**:

> high diversity or local surprise in the demonstrations, governed by a low-complexity and consistently reusable higher-order grammar.

A teacher may choose examples that are maximally discriminative among competing hypotheses. Such examples can look irregular at the object level while being highly regular at the pedagogical level: each is selected by the same policy of eliminating the learner's most important remaining ambiguity.

Let $H(Y_t\mid H_{t-1})$ measure local uncertainty in the next observation and let $K(\pi_T)$ denote the description cost of the teacher policy. An efficient pedagogical process may combine:

- high local information yield;
- low or moderate policy complexity;
- high predictive gain after the policy is inferred;
- low redundancy after the learner has stabilized the relevant representation.

The ideal is therefore not minimum entropy. Nor is it maximum entropy. It is a message whose irregularities are maximally informative under a stable inferential structure.

### Conjecture 1 — Pedagogical structured-irregularity principle

For a fixed learner, target family, reliability threshold, and communication budget, optimal curricula tend to maximize discrimination among live hypotheses while minimizing the complexity of the meta-structure required to interpret that discrimination.

This conjecture turns clarity into a property of the complete teacher-learner system, not a property of individual messages viewed in isolation.

---

## 7. What Is an Optimal Learner?

A learner cannot be defined as a system that merely finds patterns. Every finite sequence admits many exact descriptions, including descriptions that have no predictive value.

A better learner extracts **predictive invariants**: representations that compress relevant aspects of the past, improve prediction of the future, remain stable under appropriate perturbations, and support execution or transfer. In a bit-level channel, next-bit prediction remains the common external interface throughout this process. Tokenization is one possible internal realization of an invariant, not a separate primitive task.

For learner $A$, define a provisional quality functional:

$$
Q(A)
=
\alpha\,\Delta_{\mathrm{pred}}
+\beta\,\Delta_{\mathrm{task}}
+\gamma\,\Delta_{\mathrm{transfer}}
-\lambda L(M_A)
-\mu\,\operatorname{Instability}(M_A).
$$

Here:

- $\Delta_{\mathrm{pred}}$ is held-out predictive improvement;
- $\Delta_{\mathrm{task}}$ is competence on unseen inputs of $f$;
- $\Delta_{\mathrm{transfer}}$ measures reuse under longer sequences, new compositions, or symbol permutations;
- $L(M_A)$ penalizes gratuitous model complexity;
- instability penalizes patterns that disappear under resampling or intervention.

### Conjecture 2 — Learner as invariant extractor

Among learners with comparable resources, the better learner is the one that identifies the smallest stable representation sufficient for predicting future interaction and executing the target, rather than the one that achieves the greatest retrospective fit. Literal token identity is not part of this criterion: distinct registries should be treated as equivalent when they induce comparable primitive predictions, task behavior, transfer, and total representational cost.

This connects compression to prediction without equating them. Minimum description length supplies a useful bias, but out-of-sample persistence determines whether the compressed regularity is pedagogically real.

---

## 8. Teacher and Learner Are Co-Defined

An optimal message is learner-relative. A code that is perfectly efficient for one learner may be opaque to another. Likewise, a learner's competence is teacher-relative when the teacher determines which distinctions are exposed.

The coupled optimization is:

$$
(A^*,\pi_T^*)
=
\arg\max_{A,\pi_T}
\left[
\operatorname{Competence}(A,\pi_T,f)
-
\lambda C(\pi_T)
-
\mu C(A)
\right].
$$

This does not imply that arbitrary private codes are automatically good teaching. A private code is valuable only when the total cost of inducing and using it is lower than the alternatives and when the learner can recover it with the available evidence.

Canonical identifiers are therefore an important controlled benchmark, not a universal requirement. Experiments should compare:

1. canonical IDs with no semantic degrees of freedom;
2. freely selected but pedagogically learnable IDs;
3. random IDs stable across the interaction;
4. IDs that change unpredictably;
5. encrypted IDs whose key is never pedagogically supplied.

The first isolates structural learning. The second studies emergent coding. The third measures tolerance to arbitrary but stable conventions. The fourth introduces channel-like noise. The fifth is concealment and should not be counted as successful teaching for the specified learner. Exact recovery of any one identifier system is a diagnostic only; the primary comparison is whether the induced representation improves prediction and target competence at the primitive observation interface.

---

## 9. Distinguishing Real Patterns from Overfitting

A pattern discovered in noise should count as learned structure only if it survives tests not used to discover it.

### 9.1 Future prediction

Models inferred from $H_t$ must predict later teacher actions or target outputs. Retrospective compression alone is insufficient.

### 9.2 Counterfactual teacher probes

Change the learner state or target ambiguity while holding superficial statistics constant. A learner that modeled the teacher's pedagogical policy should predict the changed example choice.

### 9.3 Mark and ID permutations

Permute primitive marks or stable identifiers. Structural knowledge should transfer after relabeling; memorized surface associations should fail.

### 9.4 Noise interventions

Inject controlled bit flips, omissions, irrelevant fields, and timing variation. Measure whether the learner preserves task-relevant invariants and whether uncertainty is calibrated.

### 9.5 Delayed-key experiments

Emit a structured but initially opaque code, later teach its decoding rule, and test whether the learner retrospectively recovers information from the earlier transcript. Compare against a condition in which no decoding rule is ever supplied.

### 9.6 Adversarial coincidence

Construct training prefixes with simple but false regularities that reverse out of sample. The learner should prefer models whose structure remains predictive rather than those with the strongest in-sample compression.

---

## 10. Experimental Program

### Experiment 1 — Ideal teaching frontier

For small deterministic function classes, exhaustively search teacher messages under fixed learners. Use the same primitive next-observation or next-bit scoring interface for all learner representations. Measure message length, policy complexity, competence threshold, and decodability profile. Test whether optimal messages exhibit staged structure rather than opaque one-shot encodings, and whether different internal token systems can achieve equivalent observable competence.

### Experiment 2 — Entropy versus grammar

Independently vary:

- local diversity of examples;
- regularity of the higher-order lesson protocol;
- amount of redundant repetition;
- learner capacity.

Test the prediction that the best curricula use high discriminative diversity under a stable protocol, rather than globally minimizing or maximizing entropy.

### Experiment 3 — Opacity, noise, and concealment

Compare stable unknown codes, recoverable delayed codes, random corruption, unstable conventions, and unrecoverable encryption. Estimate when the learner correctly reclassifies apparent noise as signal.

### Experiment 4 — Retrospective interpretation

Give learners prefixes containing information that is useless under their current grammar. Later teach the missing segmentation or reference rule. Measure $R_{i,t}$ and test whether earlier observations acquire predictive value.

### Experiment 5 — Pattern overfitting

Reward either transcript compression or held-out teacher prediction. Determine whether compression-only learners invent brittle structure and whether predictive objectives recover the target-generating invariants more reliably.

### Experiment 6 — Co-adaptive teacher and learner

Jointly optimize teacher and learner policies. Observe whether their emergent codes become progressively decodable, collapse into private shortcuts, or remain robust when transferred to new partners.

---

## 11. Falsifiable Hypotheses

**H1 — Progressive decodability.** Under ideal teacher-learner optimization with explicit total cost, successful curricula will exhibit increasing recoverable structure across stages more often than equally short arbitrary codes.

**H2 — Structured irregularity.** The best curricula will combine high information gain at the example level with a comparatively simple and stable lesson-selection policy.

**H3 — Retrospective learning.** Learners with persistent memory and representation revision will extract measurable later value from observations that were initially opaque.

**H4 — Predictive and representational invariance.** Held-out primitive prediction, transfer, and intervention stability will distinguish genuine learned structure from in-sample compression better than description length alone. Distinct token registries that preserve these quantities should be functionally equivalent even when their boundaries and identifiers disagree.

**H5 — Stable arbitrary codes.** Free but stable identifiers will be learnable when their role is demonstrated, though usually at a greater teaching cost than canonical identifiers.

**H6 — Unrecoverable concealment.** Codes whose decoding information is absent from the interaction and prior assumptions will not support target acquisition beyond chance or incidental leakage.

**H7 — Learner relativity.** The curriculum that is optimal for one learner architecture will not generally be optimal for another.

**H8 — Ecological robustness.** Learners optimized only on noiseless ideal curricula will underperform learners trained to separate opacity from exogenous noise.

---

## 12. Relation to Prior Work

Shannon's communication theory separates source, channel, noise, and decoder, but ordinarily presumes a specified coding problem rather than a learner that must infer the code and the teacher's intention [1]. Identification in the limit studies whether a learner can converge to a correct language or generator from an indefinitely growing sequence [2]. Algorithmic induction and minimum description length motivate preferences for compact explanations [3, 4], while predictive information emphasizes the portion of past structure that supports prediction of the future [5]. The information bottleneck formalizes compression that preserves task-relevant information [6].

Machine teaching asks which examples an informed teacher should choose for a learner, and rational pedagogical models couple teacher selection with learner inference [7, 8]. The present proposal adds four emphases:

1. the distinction between exogenous noise and temporarily undecodable structure;
2. retrospective reinterpretation of earlier evidence;
3. structured irregularity as a candidate property of optimal curricula;
4. predictive invariance, rather than retrospective pattern discovery alone, as the criterion for learner quality.

The framework is also compatible with self-tokenizing teaching: learning a registry or code is one form of reducing opacity, and later token reuse is a concrete mechanism by which previously transmitted structure can become increasingly accessible. The primitive prediction substrate need not change when the symbolic scale changes; a learner may continue predicting the next bit while using whatever context-adapted hierarchy of tokens best supports that prediction and the target task.

---

## 13. Limitations

The proposed definitions remain incomplete. Progressive decodability depends on stage boundaries, learner class, evaluation horizon, and baseline. Predictive success may still arise from a model that does not recover the teacher's internal process. Conversely, two different generative explanations may be observationally equivalent within any finite experiment.

The distinction between opacity and noise is also horizon-relative. A symbol may remain undecoded not because it is noise, but because the curriculum ended too early. Experiments must therefore state what information is available, what priors are shared, and how long recovery is permitted.

Finally, the idealization of a deterministic target excludes learnable stochastic laws. Extending the framework to stochastic targets will require separating irreducible target entropy from channel noise, teacher randomness, and learner uncertainty.

---

## 14. Conclusion

Learning in a pedagogical channel is not merely the removal of noise from a message. The learner must decide which variations are irrelevant, which are clues to a hidden protocol, and which inferred structures will survive future evidence.

The ideal teacher may use locally surprising and highly discriminative demonstrations, but the message becomes teachable only through a stable higher-order structure. The ideal learner is correspondingly not the most enthusiastic finder of patterns. It is the system that turns apparent irregularity into compact predictive invariants, revises earlier interpretations when new structure arrives, and refuses patterns that collapse outside the transcript in which they were discovered.

The resulting hypothesis can be stated compactly:

> Optimal pedagogy is structured irregularity made progressively decodable; optimal learning is the extraction of predictive invariants from the mixture of signal, opacity, and noise. Primitive observations supply the evidence, while tokens are adaptive instruments whose value is earned by future prediction and competence.

---

## References

1. C. E. Shannon, “A Mathematical Theory of Communication,” *Bell System Technical Journal*, 27, 379–423 and 623–656, 1948.
2. E. M. Gold, “Language Identification in the Limit,” *Information and Control*, 10(5), 447–474, 1967.
3. R. J. Solomonoff, “A Formal Theory of Inductive Inference, Parts I and II,” *Information and Control*, 7, 1–22 and 224–254, 1964.
4. J. Rissanen, “Modeling by Shortest Data Description,” *Automatica*, 14(5), 465–471, 1978.
5. W. Bialek, I. Nemenman, and N. Tishby, “Predictability, Complexity, and Learning,” *Neural Computation*, 13(11), 2409–2463, 2001.
6. N. Tishby, F. C. Pereira, and W. Bialek, “The Information Bottleneck Method,” in *Proceedings of the 37th Annual Allerton Conference on Communication, Control, and Computing*, 1999.
7. X. Zhu, “Machine Teaching: An Inverse Problem to Machine Learning and an Approach Toward Optimal Education,” *Proceedings of the AAAI Conference on Artificial Intelligence*, 29(1), 2015.
8. P. Shafto, N. D. Goodman, and T. L. Griffiths, “A Rational Account of Pedagogical Reasoning: Teaching by, and Learning from, Examples,” *Cognitive Psychology*, 71, 55–89, 2014.
