---
type: "Technical Paper"
title: "Programs That Teach Programs: Generative Machine Teaching from Deterministic Binary Curricula"
description: "Position paper proposing deterministic lesson generators and curriculum search for teaching algorithms from unsegmented binary streams."
tags: [generative-machine-teaching, curriculum-learning, machine-teaching, program-induction]
timestamp: 2026-07-30T19:26:00Z
---

# Programs That Teach Programs: Generative Machine Teaching from Deterministic Binary Curricula

**Franklin Baldo**  
Independent Researcher  
franklinbaldo@gmail.com

---

> **Position paper.** This article proposes a formal framework and an experimental
> benchmark. It reports no training results. Claims about learnability, curriculum
> efficiency, transfer, or threshold sequence lengths are hypotheses to be tested,
> not empirical findings.

## Abstract

This paper proposes **generative machine teaching**, a paradigm in which a lesson is not a stored set of labeled examples but a deterministic program that generates a finite training string according to a rule. A student model does not observe the lesson program, its parameters, labels, semantic descriptions, or necessarily even the boundaries between lessons. It receives only the generated symbols. A curriculum is an ordered sequence of such lesson generators. The teaching problem is to find the curriculum that causes a specified learning algorithm to acquire a target algorithm at minimum pedagogical cost, measured by transmitted bits, number of lessons, generator description length, computation, and generalization error.

As an initial benchmark, we introduce a minimal binary construction system rooted in an empty token. Two primitive marks act as opening and closing boundaries. The empty token contains no internal marks. Every later token must be defined by an explicit finite sequence of construction steps starting from that empty token; its representation therefore records its own genealogy. The basic encoding is intentionally not self-delimiting. When tokens and lessons are concatenated, the student receives a continuous binary stream whose segmentation is underdetermined. The student must infer useful boundaries, recover the construction operations, generalize to unseen depths, execute learned transformations, and, for language-capable models, explain the inferred system.

The proposal unifies questions from curriculum learning, machine teaching, teaching dimension, program synthesis, in-context learning, and algorithmic information theory while making a distinct experimental commitment: the teacher chooses deterministic **generators of experience**, and the learner observes only their outputs. We define pedagogical complexity relative to a learner, propose benchmark tracks for segmented and unsegmented streams, specify behavioral metrics and controls against teacher-student collusion, and state falsifiable hypotheses. The central empirical question is: **what is the shortest deterministic experience from which a given learner can acquire a given algorithm?**

**Keywords:** generative machine teaching, curriculum learning, program induction, teaching dimension, in-context learning, deterministic data generation, binary language, algorithmic pedagogy

---

## 1. Introduction

Machine learning systems usually receive data whose ontology has already been chosen for them. A dataset specifies where one example ends and another begins. Inputs and outputs occupy known fields. Labels identify relevant distinctions. Tokenizers impose symbol boundaries. Loss functions announce what should count as success. Even self-supervised learning ordinarily assumes documents, sequences, patches, frames, or other externally supplied units.

This paper studies a more austere teaching problem. A learner receives a sequence composed only of two physical symbols. It may receive no spaces, labels, comments, natural-language instructions, token boundaries, lesson boundaries, or declaration of the generating task. All learnable organization must be recoverable from regularities in the sequence and from the learner's inductive biases.

The motivating intuition is that a language might teach its own construction. Begin with a bounded region containing nothing: an empty token. Then define every new token by the operations required to construct it from that token. No token may be introduced merely by assigning a name to an arbitrary bit pattern. A token exists in the language only if it has a finite genealogy from the empty root.

This idea immediately raises an empirical question. Suppose a large language model, a transformer trained from scratch, a recurrent model, or a symbolic synthesizer receives only a continuous binary string generated from those rules. How long must the string be before the learner can correctly infer and explain what is being constructed? More importantly, what sequence of demonstrations minimizes that length?

That question generalizes beyond the initial language. A lesson can be treated as a deterministic program that produces training data. The student sees only the output of the program. Different lessons can expose base cases, recurrences, contrasts, compositions, or boundary conventions. A curriculum is an ordering of those lesson programs. Searching for a curriculum then means searching for a sequence of generated experiences that efficiently induces a target algorithm in a particular learner.

The proposal is related to several established lines of work. Curriculum learning studies how the ordering and pacing of training data affect learning [1]. Automated curriculum learning chooses tasks or samples according to learning progress [2], and recent benchmarks compare curriculum methods across domains [3]. Machine teaching studies the inverse problem of selecting training data for a known learner and target [4]. Teaching dimension formalizes the number of examples required to identify a concept within a hypothesis class [5]. Sequential machine teaching optimizes a sequence that drives a learner toward a target state [6]. Program synthesis from examples studies how observations constrain candidate programs and how representative examples improve synthesis [7]. Work on in-context learning shows that transformers can be trained to infer members of function classes from examples presented at inference time [8]. Minimum Description Length and algorithmic induction connect learning with concise explanations of data [9, 10].

The proposal differs in the conjunction of the following commitments:

1. A lesson is a **deterministic generator**, not merely a selected example or minibatch.
2. The learner observes only the generator's output, not its code or semantic description.
3. The output alphabet may be only binary.
4. Token and lesson boundaries may be withheld.
5. The target is acquisition of an executable algorithm, not only prediction on the training distribution.
6. Curriculum search optimizes the choice, parameters, output lengths, and order of lesson generators.
7. Teaching cost is measured relative to the learner that receives the curriculum.

The initial binary language is not presented as the only possible substrate. It is proposed as a deliberately minimal test environment in which the provenance of every token is explicit and the costs of segmentation, induction, execution, extrapolation, and explanation can be measured separately.

The paper makes five contributions:

1. It defines **generative machine teaching** as teaching through outputs of hidden deterministic lesson programs.
2. It formalizes learner-relative **pedagogical complexity** for algorithm acquisition.
3. It specifies a minimal genealogical binary language rooted in an empty token.
4. It proposes a benchmark spanning segmented lessons, unsegmented binary streams, program recovery, behavioral generalization, and explanation.
5. It identifies failure modes, including underdetermination, tokenizer artifacts, memorization, and teacher-student collusion, and proposes controls for each.

No claim is made that current models will solve the strongest version of the benchmark, or that the proposed encoding is optimal. The aim is to make those questions experimentally precise.

---

## 2. Related Work and the Proposed Boundary

### 2.1 Curriculum learning

Bengio et al. introduced curriculum learning as training under a meaningful ordering of examples, often moving from simpler to more difficult cases [1]. The central observation is that data order can affect optimization speed and, for nonconvex systems, the solution reached. Later work automated syllabus selection using learning-progress signals [2], analyzed curriculum effects on optimization and generalization, and developed broader benchmark infrastructure [3].

Most curriculum-learning systems choose or reweight items from a previously defined dataset or task family. Their samples already possess an externally supplied representation and supervision protocol. The present proposal instead places a program generator inside each lesson. The teacher chooses not only which existing observation to show, but which deterministic process should produce the learner's experience.

### 2.2 Machine teaching and teaching dimension

Machine teaching reverses the usual learning problem. Given a learner and a target, the teacher seeks training data that causes the learner to acquire that target [4]. Teaching dimension asks how many examples are sufficient to uniquely identify concepts within a specified hypothesis class [5]. Sequential machine teaching extends the problem to ordered sequences and can be formulated as optimal control over learner dynamics [6].

Generative machine teaching belongs to this family, but changes the teacher's action space. A teacher action is a lesson generator plus its parameters and output budget. The learner may not observe labels, examples as separate entities, or even the fact that multiple lessons exist. The teacher must therefore teach representational conventions and algorithmic structure, not merely select informative labeled instances.

### 2.3 Program synthesis and representative examples

Programming by example and inductive program synthesis recover programs consistent with observed input-output behavior. Representative examples can sharply reduce the synthesis search space and improve stability [7]. This supports the intuition that a carefully chosen observation can teach more than a much larger undifferentiated sample.

The strongest benchmark proposed here begins one level earlier. Before a learner can infer a transformation from input-output pairs, it may need to discover what counts as an input, an output, a pair, a token, a sequence, and an application. Those concepts can themselves be introduced by earlier deterministic lessons.

### 2.4 In-context learning

Transformers can be trained to infer functions from examples placed in their context, without parameter updates at inference time. Garg et al. demonstrated this for several function classes under controlled conditions [8]. This provides one candidate student regime for the proposed benchmark: a frozen model receives a binary curriculum as context and is evaluated on new queries.

The present proposal does not assume that a general-purpose pretrained LLM is the only or best learner. It explicitly compares frozen in-context learners, models trained from scratch, recurrent architectures, meta-learned students, symbolic synthesizers, and neuro-symbolic systems.

### 2.5 Description length and induction

Minimum Description Length treats learning as the search for a compact account of observations [9]. Solomonoff induction assigns greater prior weight to shorter programs capable of generating a sequence [10]. These traditions motivate two parts of the proposal: penalizing the hidden complexity of lesson generators, and treating the learner's recovery of a compact generative rule as stronger evidence than local continuation accuracy.

However, compressibility and teachability are not identical. A short target program may be difficult for a particular learner to infer from outputs. A longer target may admit a curriculum containing highly diagnostic demonstrations. Pedagogical complexity must therefore be indexed to the learner.

### 2.6 Scope of the novelty claim

The individual ingredients of this proposal have precedents: ordered training, optimized teaching sequences, generated tasks, program induction, binary coding, and description-length objectives. The claimed research contribution is narrower and compositional: an explicit framework in which **deterministic hidden lesson programs generate symbol streams; curriculum search operates over those programs; and success is algorithm acquisition from their outputs, optionally without segmentation or semantic scaffolding**.

The novelty of that exact framing and benchmark must be tested against further literature review and implementation. This position paper does not claim priority over every possible formulation of program-generated curricula.

---

## 3. A Minimal Genealogical Binary Language

### 3.1 Nothing, emptiness, and representation

Metaphysical nothingness cannot be named, delimited, or measured without ceasing to be nothing in the relevant sense. A computational system can instead begin with the first representable absence: a bounded token with no internal content.

The initial object is therefore called the **empty token**, not because an already existing container happens to be unfilled, but because delimitation is the first representational act. The system does not encode absolute nothingness; it encodes the transition from no object to an object whose content length is zero.

### 3.2 Primitive marks

Let the physical alphabet be:

$$
\Sigma = \{0,1\}.
$$

The marks may be read mnemonically as:

$$
0 \equiv |\mathrm{begin}|,
\qquad
1 \equiv |\mathrm{end}|.
$$

At the foundational level, these are not yet semantic tokens available as ordinary data. They are primitive marks used by the construction mechanism.

The first token is:

$$
E := 01.
$$

In mnemonic form:

```text
|begin||end|
```

The outer marks bound an interior of length zero.

### 3.3 Construction operations

For any finite path $p \in \Sigma^*$, define:

$$
\tau(p) := 0p1.
$$

The empty token corresponds to the empty path $\varepsilon$:

$$
\tau(\varepsilon)=01=E.
$$

Define two elementary append-inside operations:

$$
A_b(0p1) := 0pb1,
\qquad b\in\{0,1\}.
$$

Each operation inserts one primitive mark immediately before the external closing mark.

Applying $A_0$ to the empty token produces the token **begin**:

$$
B := A_0(E)=001.
$$

Mnemonic form:

```text
|begin||begin||end|
```

Applying $A_1$ to the empty token produces the token **end**:

$$
D := A_1(E)=011.
$$

Mnemonic form:

```text
|begin||end||end|
```

The first three definitions are therefore:

$$
E=01,
\qquad
B=001,
\qquad
D=011.
$$

The primitive marks and the constructed tokens must not be conflated. The mark `0` is available to the construction mechanism before the token $B$ is defined. The token $B$ is the constructed representation whose sole interior mark is `0`. The same distinction applies to `1` and $D$.

### 3.4 Mandatory genealogy

The language adopts the following constitutive restriction:

> Every new token must be defined by the finite sequence of construction steps required to obtain it from the empty token.

For a path:

$$
p=b_1b_2\ldots b_n,
$$

its token is constructed by:

$$
\tau(p)
=
A_{b_n}\left(
A_{b_{n-1}}\left(
\cdots A_{b_1}(E)\cdots
\right)
\right).
$$

The path $p$ is simultaneously:

- the recipe for constructing the token;
- its address in the derivation tree;
- a finite witness that the token is reachable from the empty root;
- the interior of its physical representation.

A semantic name may later abbreviate a token, but the name cannot replace its derivation. A token that lacks a construction path from $E$ is not admitted into the language.

### 3.5 Derivation tree

At depth $n$, the system contains $2^n$ possible paths and therefore $2^n$ tokens. The first levels are:

```text
Depth 0
  01

Depth 1
  001
  011

Depth 2
  0001
  0011
  0101
  0111
```

The construction system therefore defines an infinite rooted binary tree. This derivation tree should be distinguished from later data structures represented inside the language. At this stage, each token contains a linear path of marks. Lists, trees, application, equality, and recursion must be introduced by later constructions and lessons rather than silently assumed.

### 3.6 Intentional non-self-delimitation

The encoding $\tau(p)=0p1$ is not prefix-free and is not uniquely decodable under concatenation.

For paths $p$ and $q$:

$$
\tau(p)\tau(q)=0p10q1.
$$

But the same complete string can be read as one token:

$$
0rq1
$$

with:

$$
r=p10q.
$$

For example:

```text
001011
```

can be segmented as:

```text
001 011
```

representing $B$ followed by $D$. It can also be read as the single token:

```text
0 0101 1
```

whose path is `0101`.

This is not treated as a defect to be concealed. It creates an experimental distinction between:

1. detecting non-random structure;
2. inferring useful segmentation;
3. recovering construction rules;
4. assigning operational roles to recovered structures.

A later curriculum may teach a self-delimiting protocol, but that protocol must itself be constructed from the empty token. The benchmark can therefore measure the cost of being given boundaries, discovering boundaries, and learning a boundary convention.

### 3.7 An illustrative stream

Enumerating the empty token, both depth-one tokens, and all depth-two tokens yields:

```text
01 001 011 0001 0011 0101 0111
```

Without spaces, the student receives only:

```text
010010110001001101010111
```

This 24-bit stream is not proposed as a sufficient curriculum. It merely demonstrates the observational condition: the intended sequence of genealogical objects is not recoverable from syntax alone. The curriculum must provide enough regularity for a learner to prefer a productive interpretation over many alternatives.

---

## 4. Lessons as Hidden Deterministic Programs

### 4.1 Target algorithms

Let $\mathcal P$ be a class of target algorithms. A target may be a sequence generator:

$$
P:\mathbb N\rightarrow\Sigma^*,
$$

or a general transformation:

$$
P:X\rightarrow Y.
$$

For the latter case, a previously learned representation must encode elements of $X$, elements of $Y$, and the relationship between them.

### 4.2 Lesson generators

A lesson is a pair:

$$
\ell_i=(G_i,z_i),
$$

where $G_i$ is a deterministic generator and $z_i$ contains its finite parameters. Given target $P$:

$$
y_i=G_i(P,z_i),
\qquad y_i\in\Sigma^*.
$$

The determinism requirement is:

$$
G_i(P,z_i)=G_i(P,z_i)
$$

for every execution under the same formal specification.

The student receives $y_i$. It does not receive $G_i$, $z_i$, a source-code representation of $P$, or a natural-language explanation of the lesson.

Deterministic generation should not be confused with deterministic training. Student initialization, optimization, hardware, sampling, dropout, or decoding may remain stochastic. Determinism is a property of the pedagogical evidence.

### 4.3 What a lesson can do

A generator may produce sequences that expose:

- a base case;
- increasing construction depth;
- repeated applications of one operation;
- sibling relations in the derivation tree;
- alternation between operations;
- composition of previously acquired operations;
- minimal pairs that differ in one bit;
- cases chosen to distinguish rival hypotheses;
- a construction trace containing intermediate states;
- a self-delimiting convention;
- encoded input-output behavior of a target program.

At the earliest stage, the stream has no native truth-value or error token. Consequently, a generator cannot simply label an item “negative” unless such a label has already been taught. Early contrastive teaching must be expressed through recurrence, position, symmetry, continuation, or another relation visible in the output. Once the language has constructed truth, falsity, equality, or validity tokens, later lessons can encode explicit counterexamples internally.

### 4.4 Lessons are not datasets

A stored dataset can be treated extensionally as a finite collection of observations. A lesson generator has an intensional description: it specifies how observations are produced. Two generators can emit the same finite string while embodying different rules. Since the student observes only the string, those generators are observationally equivalent for that lesson. They may become distinguishable only through further outputs or tests.

This underdetermination is intentional. Learning is evaluated not by access to the hidden generator but by the ability to infer a program that generalizes under a defined test oracle.

---

## 5. Curricula as Programs for Teaching Programs

### 5.1 Open-loop curricula

An open-loop curriculum is an ordered sequence:

$$
C=(\ell_1,\ell_2,\ldots,\ell_k).
$$

Its segmented observational form is:

$$
Y_C=(y_1,y_2,\ldots,y_k).
$$

Its unsegmented form is the concatenation:

$$
S_C=y_1y_2\cdots y_k.
$$

In the strongest condition, the student receives only $S_C$. It is not told the value of $k$ or any boundary positions.

### 5.2 Student dynamics

Let $A$ be a learning algorithm with initial state $h_0$. Under segmented presentation:

$$
h_i=A(h_{i-1},y_i).
$$

After the curriculum:

$$
h_C=A(C).
$$

The final state induces a hypothesis or executable behavior:

$$
\widehat P_{A,C}.
$$

For a frozen in-context learner, $h_C$ is a functional state induced by the prompt rather than a persistent parameter update. For a gradient-trained learner, it includes learned parameters. For a symbolic synthesizer, it may be a surviving version space or a recovered program.

### 5.3 Closed-loop curricula

An adaptive teacher observes probes of the student's current competence and chooses the next lesson:

$$
\ell_{i+1}=\pi_T(P,h_i),
$$

where $\pi_T$ is a teaching policy.

The teacher need not have direct access to hidden activations. It may condition on observable answers to diagnostic queries. This produces personalized curricula: different students can receive different experiences while targeting the same algorithm.

### 5.4 The curriculum-search problem

For a fixed learner $A$ and target $P$, curriculum search seeks:

$$
C^*_{A,P}
=
\arg\min_C J(C;A,P),
$$

subject to a competence threshold:

$$
\operatorname{Score}(\widehat P_{A,C},P)\geq q.
$$

The criterion $J$ may include transmitted bits, number of lessons, generator complexity, teacher computation, student computation, and generalization error.

This definition captures the central proposal:

> Searching for the best curriculum means searching for the sequence of deterministic lessons that most efficiently teaches a target algorithm to a specified learning algorithm.

### 5.5 No universally best curriculum

The optimum is indexed to the learner. In general:

$$
C^*_{A_1,P}\neq C^*_{A_2,P}.
$$

A transformer may exploit long-range repetition. A recurrent model may benefit from local incremental traces. A symbolic synthesizer may learn from a few highly discriminative cases. A pretrained LLM may import strong priors that help or mislead it.

A curriculum optimized for a population $\mathcal A$ is:

$$
C^*_{\mathcal A,P}
=
\arg\min_C
\mathbb E_{A\sim\mathcal A}
[J(C;A,P)].
$$

Population optimization provides one route to curricula that transfer across architectures instead of exploiting one student's idiosyncrasies.

---

## 6. Pedagogical Complexity

### 6.1 Bit cost

The most direct cost is the number of transmitted bits:

$$
B(C)=\sum_{i=1}^{k}|y_i|.
$$

Under an unsegmented curriculum this is simply:

$$
B(C)=|S_C|.
$$

A bit-minimal curriculum answers:

> What is the shortest deterministic experience from which learner $A$ can acquire target $P$ at the required level?

### 6.2 Lesson count

The number of distinct presentations may matter independently of total bits:

$$
N(C)=k.
$$

A curriculum containing one long stream and a curriculum containing many short lessons may have equal bit cost but different effects on optimization or in-context inference.

### 6.3 Generator description length

Bit cost alone permits pathological teachers. A generator with enormous hidden complexity could emit a short adversarial code that exploits a specific learner. Define:

$$
D(C)=\sum_{i=1}^{k}L(G_i,z_i),
$$

where $L$ is description length in a fixed lesson-generator language.

The generator language and its encoding must be fixed before curriculum optimization. Otherwise description length can be manipulated by changing the metalanguage.

### 6.4 Computational cost

Let:

- $T_T(C)$ be teacher-side search and generation cost;
- $T_A(C)$ be learner-side training or inference cost.

Both may be included when practical efficiency matters.

### 6.5 Error and generalization

Let $E(\widehat P_{A,C},P)$ measure disagreement on held-out tests, including extrapolation beyond the observed sizes and depths.

A composite objective is:

$$
J(C;A,P)
=
\lambda_B B(C)
+
\lambda_N N(C)
+
\lambda_D D(C)
+
\lambda_T T_T(C)
+
\lambda_A T_A(C)
+
\lambda_E E(\widehat P_{A,C},P).
$$

Alternatively, one may minimize transmission and description costs subject to strict behavioral constraints.

### 6.6 Learner-relative pedagogical complexity

Define:

$$
K_A^{\mathrm{teach}}(P;q)
=
\min_C
\left[
\lambda_B B(C)
+
\lambda_N N(C)
+
\lambda_D D(C)
\right]
$$

subject to:

$$
\Pr\left[
\operatorname{Score}(\widehat P_{A,C},P)\geq q
\right]
\geq r,
$$

where the probability is taken over relevant student stochasticity and $r$ is a reliability threshold.

This quantity is not Kolmogorov complexity and not ordinary sample complexity. It is a learner-relative cost of constructing an experience that causes algorithm acquisition.

### 6.7 Teachability versus compressibility

A target with a short description may still be hard to infer for a given learner because many competing hypotheses fit the observed prefix. Conversely, a larger program may possess a small set of highly diagnostic behaviors.

The benchmark should therefore compare:

- target program description length;
- shortest curriculum length;
- generator description length;
- learner success.

Their relationship is an empirical question rather than an assumed identity.

---

## 7. Benchmark Design

### 7.1 Central measurement

For model $M$, target $P$, and curriculum family $\mathcal C$, define the acquisition curve:

$$
S_{M,P,\mathcal C}(n),
$$

where $n$ is the number of curriculum bits presented and the score aggregates behavioral tests.

Define the acquisition threshold:

$$
N_{q,r}(M,P,\mathcal C)
=
\min\left\{
 n:
 \Pr[S_{M,P,\mathcal C}(n)\geq q]\geq r
\right\}.
$$

The initial motivating question—how long a binary string must be before a model can infer the system—becomes an estimate of $N_{q,r}$ under a specified model, curriculum family, evaluation rubric, and presentation condition.

There is no reason to assume in advance that the relevant scale is hundreds, thousands, or millions of bits.

### 7.2 Presentation tracks

#### Track A: Explicit token and lesson boundaries

The student receives the same binary content with all token and lesson boundaries supplied externally. This isolates rule induction from segmentation.

#### Track B: Lesson boundaries only

The student knows where each lesson begins and ends but must infer tokenization and internal structure.

#### Track C: Token boundaries only

Tokens are separated, but lesson boundaries and pedagogical grouping are hidden.

#### Track D: Fully continuous binary stream

All outputs are concatenated. The student receives only a sequence in $\{0,1\}^*$.

#### Track E: Self-delimitation taught internally

The curriculum begins in the ambiguous system and later teaches an internally constructed framing or length protocol. No external delimiter is added.

Comparing the tracks estimates the separate costs of token segmentation, lesson segmentation, and protocol acquisition.

### 7.3 Student regimes

The benchmark should distinguish at least four regimes.

#### Frozen in-context learners

A pretrained model receives the curriculum in its context and answers diagnostic queries without parameter updates.

#### Students trained from scratch

Byte-level or bit-level transformers and recurrent models are optimized directly on lesson outputs.

#### Meta-learned students

A student is trained across many target programs and curricula, then evaluated on acquisition of unseen programs from new deterministic lessons.

#### Symbolic and neuro-symbolic learners

Program synthesizers, version-space learners, and hybrid systems provide interpretable baselines and help separate architecture limitations from information insufficiency.

### 7.4 Target families

#### Foundation tasks

- recover the empty token;
- identify the two construction operations;
- recover the begin and end tokens;
- infer parent-child relations;
- reconstruct paths to unseen tokens;
- enumerate valid tokens at unseen depths.

#### Linear sequence rules

- repetition;
- alternation;
- block growth;
- unary counting;
- binary counting;
- parity;
- deterministic substitutions;
- finite recurrences.

#### Composition tasks

- concatenate constructed objects;
- apply one learned transformation after another;
- represent and evaluate pairs;
- construct lists and trees after their conventions have been taught.

#### Functional algorithms

- complement;
- reversal;
- increment;
- addition on bounded integers;
- filtering;
- sorting short lists;
- tree traversal.

#### Stateful algorithms

- finite-state machines;
- counters;
- stack operations;
- cellular automata;
- small interpreters.

#### Transfer tasks

- unseen targets from a known program family;
- new compositions of known primitives;
- greater construction depth;
- longer inputs;
- permuted physical alphabets;
- curricula generated by unseen teachers.

### 7.5 Curriculum families

A benchmark implementation should include human-designed and automatically searched curricula built from a restricted DSL. Candidate lesson generators may include:

- `emit_empty`;
- `enumerate_depth(d)`;
- `emit_parent_children(p)`;
- `emit_construction_trace(p)`;
- `repeat_operation(b, n)`;
- `alternate_operations(n)`;
- `emit_sibling_pairs(d)`;
- `emit_minimal_variants(p)`;
- `enumerate_function_examples(P, domain_slice)`;
- `compose_lessons(g_1, g_2)`;
- `repeat_lesson(g, n)`;
- `permute_alphabet(g, permutation)`.

The exact DSL is a major design decision. It must be expressive enough to discover nontrivial curricula while constrained enough to prevent arbitrary hidden communication.

### 7.6 Bit budgets

The first benchmark can evaluate curricula at geometrically increasing budgets:

$$
32,64,128,256,512,1024,2048,4096,8192,16384,\ldots
$$

Adaptive refinement around observed transition regions can estimate acquisition thresholds more efficiently.

---

## 8. Evaluation: What Counts as Learning?

### 8.1 Why explanation is insufficient

A language model can produce a persuasive but false account of a binary pattern. Natural-language explanation is therefore evidence only when paired with executable success.

### 8.2 Structural recovery

The student must identify or operationally use:

- the empty root;
- construction operations;
- derivation depth;
- parent-child relations;
- candidate segmentation;
- dependencies between definitions.

### 8.3 Genealogy reconstruction

Given an unseen token, the student must return the sequence of operations that constructs it from $E$. Conversely, given a path, it must produce the correct token.

### 8.4 Validity discrimination

The student must distinguish well-formed constructions from malformed or rule-inconsistent strings under the conventions taught by the curriculum.

For the foundational language alone, every string of the form $0p1$ is a token. Later extensions may define stricter objects whose validity depends on previously taught composition rules.

### 8.5 Behavioral execution

For an unseen input $x$:

$$
\widehat P(x)
$$

is compared with:

$$
P(x).
$$

Exact match should be used when outputs are discrete and deterministic.

### 8.6 Extrapolation

Tests must include:

- paths deeper than any observed path;
- inputs longer than training examples;
- compositions not shown in the curriculum;
- new combinations of familiar operations;
- alphabet permutations.

Interpolation alone does not demonstrate algorithm acquisition.

### 8.7 Program recovery

Where possible, the student should emit a program in a canonical evaluation DSL. The recovered program can be checked by:

- formal equivalence;
- exhaustive testing on finite domains;
- property-based testing;
- randomized differential testing;
- model checking for small state spaces.

### 8.8 Description and explanation

Language-capable students may be asked to explain the system. A structured rubric should score whether the explanation:

1. identifies deterministic structure;
2. identifies the empty token;
3. distinguishes primitive marks from constructed tokens;
4. recovers both append-inside operations;
5. states the genealogical restriction;
6. recognizes segmentation ambiguity;
7. predicts unseen constructions correctly;
8. avoids claiming uniqueness where the data are underdetermined.

Explanation should be reported separately from behavioral competence.

### 8.9 Composite score

A possible benchmark score is:

$$
\operatorname{Score}
=
w_s S_{\mathrm{structure}}
+w_g S_{\mathrm{genealogy}}
+w_e S_{\mathrm{execution}}
+w_x S_{\mathrm{extrapolation}}
+w_p S_{\mathrm{program}}
+w_l S_{\mathrm{language}}.
$$

Behavioral terms should dominate the language-explanation term.

---

## 9. Curriculum Search

### 9.1 Exhaustive search in small spaces

For shallow targets and small generator DSLs, curricula can be enumerated. Exhaustive search establishes true optima under restricted assumptions and provides ground truth for evaluating approximate search methods.

### 9.2 Greedy information gain

Maintain a hypothesis set $\mathcal H_i$ compatible with observations. Choose the next lesson to maximize expected reduction:

$$
\ell_{i+1}
=
\arg\max_{\ell}
\mathbb E\left[
\Delta(\mathcal H_i,\mathcal H_{i+1})
\right].
$$

For neural learners, $\mathcal H_i$ may be approximated by ensembles, posterior samples, or observed error profiles.

### 9.3 Evolutionary and program search

Curricula represented as programs can be mutated by:

- inserting or deleting lessons;
- changing parameters;
- changing output budgets;
- swapping lesson order;
- composing generators;
- introducing repetition;
- replacing a generator with a semantically related one.

Fitness combines acquisition and cost.

### 9.4 Reinforcement-learning teachers

An adaptive teacher can be modeled as an agent. Its state summarizes student performance, its actions select lessons, and its reward reflects learning progress minus pedagogical cost.

### 9.5 Bayesian optimization

For parameterized but expensive curricula, Bayesian optimization can search over lesson lengths, pacing, repetition schedules, and generator mixtures while minimizing the number of full student-training runs.

### 9.6 Coevolution

Teacher and student populations may be optimized together:

$$
(A^*,C^*)
=
\arg\min_{A,C}
J(C;A,P).
$$

This may discover students that are unusually teachable and teachers that exploit their representational capacities. It also creates the strongest risk of private codes and collusion, requiring the controls discussed below.

---

## 10. Baselines, Ablations, and Controls

### 10.1 Baseline curricula

Each target should include:

1. random ordering of the same lessons;
2. reverse ordering;
3. increasing derivation depth;
4. decreasing derivation depth;
5. random deterministic outputs matched for length;
6. human-designed curriculum;
7. greedy discriminative curriculum;
8. automatically optimized curriculum;
9. direct program description, when allowed, as a reference bound.

### 10.2 Matched-content order ablation

To isolate curriculum order, compare curricula containing the same multiset of lesson outputs under different permutations. Total bits and content remain fixed.

### 10.3 Boundary ablation

Present identical underlying outputs with:

- all boundaries;
- lesson boundaries only;
- token boundaries only;
- no boundaries.

### 10.4 Redundancy ablation

Hold target and generator family constant while varying repetition. This tests whether redundancy supplies useful evidence or merely increases memorization.

### 10.5 Contrast ablation

Remove lessons selected specifically to eliminate rival hypotheses. Compare with curricula using only positive regularity and repetition.

### 10.6 Genealogy ablation

Compare the proposed genealogical representation with arbitrary token identifiers of matched length. This tests whether representation of construction history improves extrapolation.

### 10.7 Alphabet permutation

Randomly exchange `0` and `1`, or map them to unrelated byte values. A learner that acquired the abstract rule should transfer after corresponding remapping rather than depend on familiar binary semantics.

### 10.8 Fresh procedural targets

Generate target programs after the evaluated model's training cutoff or from randomized compositional grammars. This reduces contamination from memorized sequences or standard textbook tasks.

### 10.9 Cross-student evaluation

A curriculum optimized for one student is tested on held-out architectures and initializations. Severe performance collapse indicates specialization or exploitative teaching rather than general pedagogical structure.

---

## 11. Failure Modes

### 11.1 Fundamental underdetermination

Any finite binary string is compatible with infinitely many generating programs. The benchmark cannot establish that the learner discovered the unique true meaning of a sequence, because no such uniqueness generally exists.

Success means that the learner acquired a hypothesis that:

- accounts for the curriculum compactly or reliably;
- passes hidden behavioral tests generated from the target;
- extrapolates under specified transformations;
- remains stable under representation controls.

The benchmark measures useful induction, not metaphysical certainty.

### 11.2 Teacher-student collusion

An unrestricted teacher can encode a target identifier in a short string that a particular student has learned to decode. This would minimize bit cost without teaching the target's operational structure.

Controls include:

- a restricted and published lesson DSL;
- generator description-length penalties;
- hidden target and alphabet permutations;
- held-out students;
- held-out teacher generators;
- behavioral extrapolation tests;
- audits of curriculum dependence on irrelevant student features.

### 11.3 Tokenizer artifacts

A binary character stream may not be a binary token stream inside an LLM. Tokenizers can merge runs or patterns of digits. Benchmark reports must include:

- raw bit length;
- model-token length;
- exact tokenizer output;
- byte- or character-level controls.

Claims about bit efficiency must not silently substitute proprietary tokenizer units for bits.

### 11.4 Pretraining contamination

Pretrained models may recognize binary counting, bracket languages, or familiar mathematical narratives. Controls include randomized operations, generated targets, symbol permutations, and students trained from scratch.

### 11.5 Memorization and local prediction

High next-bit accuracy can be achieved without recovering the generating algorithm. Evaluation must emphasize unseen depths, lengths, compositions, and explicit execution.

### 11.6 Explanation without competence

LLMs may verbalize the intended theory after weak pattern matching. Behavioral tests must be primary.

### 11.7 Competence without explanation

The opposite dissociation is also possible. A student may execute a rule but fail to describe it. The benchmark should not classify this as total failure; explanation and execution are separate outcomes.

### 11.8 Determinism without informativeness

A deterministic generator may produce a sequence that leaves many hypotheses indistinguishable. Determinism is necessary for reproducibility, not sufficient for teaching quality.

### 11.9 Search cost

Optimizing curricula by repeatedly training students may be computationally prohibitive. Initial experiments should use small models, shallow targets, caching, surrogate models, and exhaustive ground truth only where feasible.

---

## 12. Falsifiable Hypotheses

### H1: Order matters under matched content

For a fixed learner and target, an optimized ordering of the same lesson outputs will reach a competence threshold with fewer training steps or higher reliability than random order.

### H2: Generator selection matters beyond ordering

Curricula optimized over lesson generators will outperform curricula that merely reorder a fixed dataset under matched bit budgets.

### H3: Diagnostic contrasts reduce teaching cost

Curricula containing outputs selected to distinguish high-probability rival hypotheses will reach acquisition thresholds using fewer bits than repetition-only curricula.

### H4: Segmentation has a separable cost

Providing token or lesson boundaries will reduce acquisition thresholds. A curriculum that teaches self-delimitation internally will recover part of that gap without external markers.

### H5: Optimal curricula are learner-relative

Curriculum rankings will differ across transformers, recurrent models, symbolic synthesizers, and pretrained LLMs.

### H6: Population optimization improves transfer

Curricula optimized against heterogeneous student populations will sacrifice some performance on a single training student but outperform specialized curricula on held-out students.

### H7: Genealogical representations improve depth extrapolation

Students trained on tokens whose representations encode construction paths will generalize to unseen depths more reliably than students trained on arbitrary identifiers of matched length.

### H8: Teachability and description length are related but non-identical

Target program length will correlate with pedagogical complexity, but substantial learner-dependent deviations will remain.

### H9: Execution and explanation have distinct thresholds

Some learners will execute correctly before they can explain the rule; pretrained language models may sometimes explain before achieving reliable extrapolative execution.

### H10: Meta-learned students can acquire unseen algorithms from generator outputs alone

A student trained across diverse deterministic lesson programs will learn unseen target algorithms from output-only curricula more efficiently than a student trained solely for next-symbol prediction on undifferentiated streams.

Each hypothesis can fail. For example, order may cease to matter for sufficiently powerful students; unsegmented induction may remain intractable at practical budgets; genealogical encoding may add length without useful bias; or optimized teachers may consistently exploit model artifacts rather than discover transferable pedagogy.

---

## 13. Experimental Roadmap

### 13.1 Experiment 1: Recovering the foundational language

**Target.** Recover $E$, $A_0$, $A_1$, the depth-one tokens, and the general form $\tau(p)=0p1$.

**Students.** Small bit-level transformers, LSTMs, symbolic grammar learners, and selected pretrained LLMs.

**Curricula.** Human-designed enumerations, construction traces, sibling groupings, and automatically searched sequences.

**Conditions.** All five boundary tracks.

**Tests.** Generate unseen tokens, recover paths, infer parent-child relationships, and explain the mark-token distinction.

**Primary output.** Acquisition curves and bit thresholds, not a single anecdotal model response.

### 13.2 Experiment 2: Constructing a self-delimiting extension

**Target.** Teach a protocol that lets the student uniquely segment later token sequences.

**Constraint.** The protocol must be introduced through already constructible tokens and operations; no new external delimiter is permitted.

**Comparison.** External boundaries versus internally taught boundaries versus no boundary protocol.

**Primary output.** Segmentation accuracy, overhead in bits, and downstream algorithm acquisition.

### 13.3 Experiment 3: Teaching simple sequence algorithms

**Targets.** Alternation, counting, parity, substitutions, and recurrences.

**Question.** Does prior acquisition of the genealogical language reduce the later cost of teaching algorithms, or does it merely add overhead?

**Controls.** Direct binary examples without the language; arbitrary token identifiers; natural-language instructions as an upper reference condition.

### 13.4 Experiment 4: Learning the curriculum

**Teacher.** Search over a restricted lesson DSL using exhaustive search for tiny targets and evolutionary or reinforcement-learning methods for larger ones.

**Student.** Fixed bit-level transformer.

**Objective.** Minimize bits and generator complexity while meeting extrapolation thresholds.

**Analysis.** Compare discovered curricula with simple-to-complex, random, reverse, and human curricula.

### 13.5 Experiment 5: Cross-model pedagogy

Optimize curricula separately for several students, then cross-evaluate every curriculum-student pair. The resulting matrix reveals whether curricula teach general structure or exploit architecture-specific biases.

### 13.6 Experiment 6: Meta-learning to be taught

Train students across many target programs and teacher-generated curricula. Evaluate whether they acquire unseen programs from shorter streams, whether they infer lesson boundaries, and whether their learned inductive biases transfer to unseen teacher policies.

### 13.7 Experiment 7: Coevolving teachers and students

Coevolve teacher and student populations under strong anti-collusion controls. Test whether the resulting protocols remain interpretable and transferable to independently trained students.

---

## 14. Open Design Questions

### 14.1 What should the lesson-generator DSL contain?

A weak DSL may make the benchmark trivial or incapable of expressing useful pedagogy. An unrestricted DSL enables hidden communication. Defining this metalanguage is the most important implementation decision.

### 14.2 Should the empty token be called “empty,” “void,” or “nothing”?

“Nothing” captures the motivating intuition but risks conflating metaphysical absence with a represented object. “Empty token” is operationally precise. The benchmark can preserve the philosophical motivation while using the computational term in formal definitions.

### 14.3 Is append-inside the only primitive operation?

The initial system uses $A_0$ and $A_1$. Later research may ask whether a single universal construction operation can generate both, whether one mark can be derived from the other, or whether richer structural operations reduce total pedagogical cost.

### 14.4 When does a physical mark become a token?

The system deliberately distinguishes primitive construction marks from their later internal representations. A full semantics must state which operations may manipulate marks directly and when constructed tokens become first-class data.

### 14.5 How should semantics enter?

Names such as “begin,” “end,” “pair,” or “apply” are external descriptions used by researchers. The learner should not receive them in the binary-only condition. Operational meaning must be established through use and successful prediction.

### 14.6 Can the system teach its own interpreter?

A long-term target is a curriculum whose binary stream teaches not only tokens and algorithms but an interpreter capable of executing subsequent definitions. This would provide a concrete sense in which the language “constructs itself.”

### 14.7 Can a curriculum teach the learner how to learn later lessons?

Early lessons may install representational conventions or inference strategies that reduce the cost of all subsequent algorithms. Measuring this amortization is central to distinguishing a language curriculum from a collection of unrelated demonstrations.

---

## 15. Broader Implications

### 15.1 Models can be compared by teachability

Current benchmarks mainly ask what a model knows or can learn from a fixed training procedure. Generative machine teaching asks how much structured experience a model needs to acquire a capability. Two models with similar final accuracy may differ sharply in pedagogical complexity.

### 15.2 Curricula become executable research objects

A curriculum is no longer an informal list of topics. It is a program whose outputs induce another program in a learner. It can be versioned, tested, minimized, mutated, compared, and audited.

### 15.3 Teacher models can be evaluated independently

A teacher is judged not by eloquence or resemblance to human pedagogy, but by the competence its generated experiences induce under explicit costs and controls.

### 15.4 Emergent communication can be studied under stronger constraints

Many multi-agent communication systems allow agents to coadapt arbitrary symbols. The proposed benchmark begins with a fixed binary channel, explicit derivational restrictions, and held-out students. This may help distinguish transferable compositional protocols from private codes.

### 15.5 The benchmark resembles communication with an unknown interpreter

An unsegmented binary curriculum resembles a message sent to a receiver whose language is unknown. Unlike a purely communicative puzzle, however, the receiver is evaluated through executable tasks and the sender can be optimized against a specified learner.

### 15.6 A science of machine pedagogy

The broader research program is the study of:

> programs that generate experiences capable of installing other programs in learners.

Such a program would connect curriculum design, machine teaching, meta-learning, representation learning, and program synthesis under a common experimental object: the deterministic lesson generator.

---

## 16. Conclusion

This paper proposed generative machine teaching: a framework in which deterministic hidden lesson programs generate the only evidence available to a student. A curriculum is an ordered sequence of those programs, and curriculum search seeks the experience that most efficiently induces a target algorithm in a specified learner.

The initial benchmark begins with a minimal binary construction system. The first representable object is the empty token:

$$
E=01.
$$

The begin and end tokens are constructed by inserting the corresponding primitive marks into the empty token:

$$
B=001,
\qquad
D=011.
$$

Every later token must carry a finite construction path from $E$. The representation therefore contains its own genealogy. Because the encoding is intentionally not self-delimiting, a continuous stream does not reveal token or lesson boundaries. The learner must infer a useful structure and demonstrate that inference through unseen construction, execution, extrapolation, and program recovery.

The proposal converts an informal question—how many binary tokens an LLM needs before it understands what a string means—into a family of measurable quantities indexed by learner, target, curriculum, reliability, and presentation condition.

The strongest version of the research question is:

> What is the shortest deterministic experience from which a given learning algorithm can acquire a given target algorithm?

Answering it requires not only better students, but algorithms that learn how to teach.

---

## References

[1] Yoshua Bengio, Jérôme Louradour, Ronan Collobert, and Jason Weston. “Curriculum Learning.” *Proceedings of the 26th International Conference on Machine Learning*, 2009, pp. 41–48. DOI: [10.1145/1553374.1553380](https://doi.org/10.1145/1553374.1553380).

[2] Alex Graves, Marc G. Bellemare, Jacob Menick, Rémi Munos, and Koray Kavukcuoglu. “Automated Curriculum Learning for Neural Networks.” *Proceedings of the 34th International Conference on Machine Learning*, PMLR 70, 2017, pp. 1311–1320. [https://proceedings.mlr.press/v70/graves17a.html](https://proceedings.mlr.press/v70/graves17a.html).

[3] Yuwei Zhou et al. “CurBench: Curriculum Learning Benchmark.” *Proceedings of the 41st International Conference on Machine Learning*, PMLR 235, 2024, pp. 62088–62107. [https://proceedings.mlr.press/v235/zhou24o.html](https://proceedings.mlr.press/v235/zhou24o.html).

[4] Xiaojin Zhu, Adish Singla, Sandra Zilles, and Anna N. Rafferty. “An Overview of Machine Teaching.” 2018. [arXiv:1801.05927](https://arxiv.org/abs/1801.05927).

[5] Sally A. Goldman and Michael J. Kearns. “On the Complexity of Teaching.” *Journal of Computer and System Sciences*, vol. 50, no. 1, 1995, pp. 20–31. DOI: [10.1006/jcss.1995.1003](https://doi.org/10.1006/jcss.1995.1003).

[6] Laurent Lessard, Xuezhou Zhang, and Xiaojin Zhu. “An Optimal Control Approach to Sequential Machine Teaching.” 2018. [arXiv:1810.06175](https://arxiv.org/abs/1810.06175).

[7] Yewen Pu, Zachery Miranda, Armando Solar-Lezama, and Leslie Pack Kaelbling. “Selecting Representative Examples for Program Synthesis.” 2017. [arXiv:1711.03243](https://arxiv.org/abs/1711.03243).

[8] Shivam Garg, Dimitris Tsipras, Percy Liang, and Gregory Valiant. “What Can Transformers Learn In-Context? A Case Study of Simple Function Classes.” *Advances in Neural Information Processing Systems 35*, 2022. [https://proceedings.neurips.cc/paper_files/paper/2022/hash/c529dba08a146ea8d6cf715ae8930cbe-Abstract-Conference.html](https://proceedings.neurips.cc/paper_files/paper/2022/hash/c529dba08a146ea8d6cf715ae8930cbe-Abstract-Conference.html).

[9] Peter Grünwald. “A Tutorial Introduction to the Minimum Description Length Principle.” 2004. [arXiv:math/0406077](https://arxiv.org/abs/math/0406077).

[10] Ray J. Solomonoff. “A Formal Theory of Inductive Inference, Part I.” *Information and Control*, vol. 7, no. 1, 1964, pp. 1–22. DOI: [10.1016/S0019-9958(64)90223-2](https://doi.org/10.1016/S0019-9958(64)90223-2).
