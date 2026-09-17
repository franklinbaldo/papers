---
type: "Audit Report"
title: "Self-tokenizing generative machine teaching prior-art audit — 2026-09-17"
description: "Claim-specific prior-art audit of the self-tokenizing generative machine-teaching combination, with GitHub-derived public cutoffs and explicit separation of antecedents from later work."
tags: [generative-machine-teaching, self-tokenization, prior-art, grammar-compression, machine-teaching, predicate-invention, program-synthesis, dynamic-tokenization]
timestamp: 2026-09-17T17:00:11-04:00
---

# Self-tokenizing generative machine teaching prior-art audit — 2026-09-17

> **Status:** first reproducible prior-art audit focused on the paper's current **self-tokenizing** combination. This audit materially narrows several component-level originality claims. It does not establish exhaustive novelty, patent novelty, or causal dependence between projects.

## 1. Audited claim and claim-specific cutoffs

The current paper, [`generative_machine_teaching.md`](../../generative_machine_teaching.md), does not claim that curriculum learning, machine teaching, synthetic data, Gödel numbering, assembly theory, or tokenization were individually invented here. Its candidate contribution is compositional. The strongest current claim is approximately:

1. a teacher emits **deterministic procedural demonstrations** rather than merely selecting examples;
2. the student may observe only a continuous primitive binary stream and is externally scored at that primitive interface;
3. successful constructions can become **endogenous reusable symbols** during the same learning process;
4. the symbolic registry carries stable identities plus executable construction evidence and can recursively change the vocabulary available to later lessons;
5. concatenation is the primitive construction operation, while proof/assembly cost and reuse are explicit;
6. curriculum search and tokenizer/registry growth are evaluated jointly, with learner-relative pedagogical cost and executable algorithm acquisition as endpoints.

The GitHub history supports two different cutoffs because the broader proposal predates the self-tokenizing strengthening.

### 1.1 Broader generative-machine-teaching cutoff

Commit [`40dcb679b76488593d280c5075e394e4edc65618`](https://github.com/franklinbaldo/papers/commit/40dcb679b76488593d280c5075e394e4edc65618), timestamped **2026-07-30 19:34:18 UTC**, introduced the paper as **“Generative Machine Teaching from Deterministic Binary Curricula”**. Pull request [`#236`](https://github.com/franklinbaldo/papers/pull/236) was publicly opened at **2026-07-30 19:35:17 UTC**. The initial version already contained hidden deterministic lesson programs, optionally unsegmented binary streams, learner-relative teaching cost, and executable algorithm acquisition.

For those broader subclaims, the conservative public cutoff is **2026-07-30 19:35:17 UTC**.

### 1.2 Current self-tokenizing combination cutoff

The stronger architecture was added in commit [`db57bcedc7f54b66de893f83e7475ffbd094902c`](https://github.com/franklinbaldo/papers/commit/db57bcedc7f54b66de893f83e7475ffbd094902c), timestamped **2026-07-30 20:58:13 UTC**, with the explicit message **“paper: make the teaching language self-tokenizing.”** A public PR title-change event at **2026-07-30 21:02:42 UTC** renamed #236 to “paper: propose self-tokenizing generative machine teaching”. More importantly, a public review event submitted at **2026-07-30 21:04:34 UTC** states that the revision:

- makes concatenation the sole primitive operation;
- makes endogenous/self-tokenization a central contribution;
- distinguishes physical, virtual, latent, and native dynamic tokens;
- specifies a deterministic restricted lesson DSL;
- models lessons as procedural state transitions.

That review is a timestamped public GitHub artifact that directly states the load-bearing self-tokenizing combination. Therefore this audit uses **2026-07-30 21:04:34 UTC** as the conservative claim-specific cutoff for the current central claim. Work first made public after that instant is not prior art against that claim.

## 2. Search protocol

The search decomposed “self-tokenizing generative machine teaching” into older vocabularies rather than assuming antecedents would use the same name. Representative queries included:

- `LZ78 dictionary phrase index next symbol`
- `SEQUITUR hierarchical structure sequence grammar rule`
- `straight-line program grammar compression single string concatenation`
- `smallest grammar problem reusable nonterminal`
- `DreamCoder library learning reusable abstractions program synthesis`
- `Playgol reusable learned programs background knowledge`
- `predicate invention reusable verified knowledge pool`
- `continual learning dynamic predicate invention reusable abstractions`
- `self-tokenizing language model bytes`
- `self-tokenization language model`
- `dynamic tokenization byte language model`
- `end-to-end learned tokenization reinforcement learning`
- `machine teaching generated curriculum`
- `iterative machine teaching learner state sequential examples`
- exact-title / attribution searches for `"Programs That Teach Programs" "Franklin Baldo"` and `"generative machine teaching" "Franklin Baldo"`
- post-cutoff searches for `self-tokenizing`, `machine teaching tokenization`, `dynamic vocabulary machine teaching`, `proof-indexed tokenization`, and `procedural machine teaching`.

Sources checked included the GitHub PR timeline and commit history, arXiv, IEEE, JAIR, ACL Anthology, PMLR/ICML, PLDI, IJCAI, ICLR proceedings, Springer/MLJ, DBLP and targeted recent-result web searches. Aggregators were used for discovery; dates and substantive claims were confirmed against primary or publisher records when available.

## 3. Findings before the self-tokenizing cutoff

### 3.1 LZ78 already gives a growing addressable dictionary whose entries are recursively constructed from earlier entries

**Classification:** `prior_art` for the narrow subclaim “a raw sequential stream can induce a growing dictionary of reusable, numerically addressable phrases”; strong `partial_prior_art` for the paper's self-tokenizing registry combination.

Ziv & Lempel, **“Compression of Individual Sequences via Variable-Rate Coding”**, *IEEE Transactions on Information Theory* 24(5), **September 1978**, DOI `10.1109/TIT.1978.1055934`, is the historical source behind LZ78.

- <https://doi.org/10.1109/TIT.1978.1055934>

LZ78 incrementally parses a stream while constructing an explicit dictionary. A new dictionary phrase is represented by a reference/index to an earlier phrase plus one new symbol; later occurrences can refer to the dictionary entry by index. The resulting trie therefore gives each learned phrase an address and a recursive expansion path back to primitives.

This is materially closer to the current registry than a generic comparison to BPE. It already contains four structural ideas that should not carry originality weight by themselves: **online vocabulary growth, stable indices, recursive construction from previously known units, and later reuse by reference**.

**Difference:** LZ78 is a compression code, not a machine-teaching protocol. Its dictionary additions are dictated by parsing/compression rather than teacher-selected demonstrations; entries do not carry pedagogical proof obligations, learner-relative curriculum objectives, or an executable target-algorithm acquisition test.

### 3.2 SEQUITUR already learns a reusable hierarchical grammar incrementally from a symbol stream

**Classification:** strong `partial_prior_art`.

Nevill-Manning & Witten, **“Identifying Hierarchical Structure in Sequences: A Linear-Time Algorithm”**, *Journal of Artificial Intelligence Research*, **1997**, introduced SEQUITUR.

- <https://jair.org/index.php/jair/article/view/10122>

SEQUITUR processes a sequence incrementally, replaces repeated phrases by grammatical rules, and recursively builds a hierarchy whose rules generate the original sequence. The learned nonterminals function as reusable symbolic abstractions discovered from the stream rather than supplied as an immutable external vocabulary.

This directly weakens any broad claim that the paper is novel merely because **reusable symbols emerge while processing an unsegmented primitive sequence** or because those symbols possess an explicit expansion hierarchy.

**Difference:** SEQUITUR optimizes grammar induction/compression, not teaching. It has no teacher action space, curriculum search, student-specific pedagogical complexity, or criterion that a derived symbol becomes available specifically because a procedural lesson demonstrated and verified it.

### 3.3 Straight-line grammars already formalize a concatenative construction DAG with reusable substructures and description-length objectives

**Classification:** strong `partial_prior_art` for the concatenation/proof-DAG/assembly-reuse subclaim.

Charikar et al., **“The Smallest Grammar Problem”**, *IEEE Transactions on Information Theory* 51(7), published **2005-07-31**, asks for the smallest context-free grammar that generates exactly one given string and analyzes grammar-based compression algorithms including LZ78 and Re-Pair.

- <https://doi.org/10.1109/TIT.2005.850116>

The broader straight-line-program (SLP) literature represents one string by an acyclic grammar whose nonterminals recursively expand into terminals or earlier nonterminals. Modern descriptions explicitly characterize an SLP as a context-free grammar generating only that string; binary SLP rules are effectively reusable concatenative construction steps.

- <https://doi.org/10.4230/LIPIcs.ESA.2021.45>

The current paper adds stable protocol identity, multiple construction proofs, pedagogical semantics and assembly metadata, but **“construct complex strings from reusable concatenative subobjects and price representation by a compact construction DAG” is established territory**. The analogy is close enough that future versions should compare the registry not only with BPE/SentencePiece and assembly theory, but also with grammar-based compression / SLPs.

### 3.4 Learned libraries and invented predicates already let learning change the symbolic language available to later problems

**Classification:** `partial_prior_art`.

Several independent program-learning traditions anticipate the generic idea that learned abstractions become new primitives for future learning:

- Cropper, **“Playgol: Learning Programs Through Play”**, IJCAI **2019**, lets a learner create play tasks, solve them, save the solutions into background knowledge, and reuse those learned programs on later build tasks. <https://www.ijcai.org/proceedings/2019/841>
- Ellis et al., **“DreamCoder: Bootstrapping Inductive Program Synthesis with Wake-Sleep Library Learning”**, PLDI **2021**, automatically derives a library of common program components; the progressively deepening library then changes and accelerates later synthesis. <https://www.pldi21.org/poster_pldi.355.html>
- Muggleton, Lin & Tamaddoni-Nezhad, **“Meta-Interpretive Learning of Higher-Order Dyadic Datalog: Predicate Invention Revisited”**, *Machine Learning* **2015**, formalizes invention of new predicate symbols during inductive logic programming. <https://doi.org/10.1007/s10994-014-5471-Y>

These works prevent “the learner's language grows as learning proceeds” from serving as a standalone novelty claim.

**Difference:** their invented abstractions are programs/predicates in a structured hypothesis language, not tokens induced and evaluated through a primitive binary next-symbol channel. They do not jointly optimize a machine teacher over demonstrations that create an addressable proof registry.

### 3.5 Two 2026 predicate-invention systems are unusually close to verified, cumulative symbolic vocabulary growth

**Classification:** strong `partial_prior_art`.

Crespo-Fernandez et al., **“Continual learning and refinement of causal models through dynamic predicate invention”**, arXiv v1 **2026-02-19**, constructs symbolic causal world models online and uses predicate invention to create reusable abstractions and a hierarchy of concepts from observations.

- <https://arxiv.org/abs/2602.17217>

Yu et al., **“ADVENT: LLM-Driven Automatic Predicate Invention for ILP”**, arXiv v1 **2026-07-02 01:33:45 UTC**, combines LLM-generated auxiliary predicates with **Prolog deductive verification**. Successful invented predicates and learned rules accumulate in a knowledge pool for cross-task reuse; removing that pool measurably reduces performance.

- <https://arxiv.org/abs/2607.01585>

ADVENT is particularly relevant because it combines **new symbol invention, executable verification, cumulative reuse, and sequential knowledge growth** before our cutoff. It is not tokenization and does not operate on an unsegmented binary channel, but it materially anticipates the abstract mechanism “a learned symbolic object is verified, admitted to a registry/pool, and becomes available as a building block for later learning.”

This antecedent was absent from the earlier PR-level novelty discussion and materially narrows the defensible novelty boundary.

### 3.6 End-to-end and self-tokenizing byte models predate our claim, including use of the phrase “self-tokenizing”

**Classification:** strong `partial_prior_art` for endogenous/dynamic tokenization; `prior_art` for the generic proposition that token boundaries/granularity can be learned jointly with prediction rather than fixed externally.

Relevant pre-cutoff examples include:

- Hwang, Wang & Gu, **“Dynamic Chunking for End-to-End Hierarchical Sequence Modeling” (H-Net)**, arXiv v1 **2025-07-10 17:39:37 UTC**: dynamically learns content- and context-dependent segmentation jointly with the model directly from raw bytes. <https://arxiv.org/abs/2507.07955>
- Owodunni, Ahia & Kumar, **“FLEXITOKENS: Flexible Tokenization for Evolving Language Models”**, arXiv v1 **2025-07-17**, later Findings of ACL 2026: byte-level models learn a boundary predictor for variable-length segments. <https://arxiv.org/abs/2507.12720>
- Dauncey & Wattenhofer, **“You Can Learn Tokenization End-to-End with Reinforcement Learning”**, arXiv v1 **2026-02-15 00:31:24 UTC**: discrete token boundaries are optimized directly for language-model loss using score-function / RL estimators. <https://arxiv.org/abs/2602.13940>
- Deng et al., **“ByteFlow: Language Modeling through Adaptive Byte Compression without a Tokenizer”**, arXiv v1 **2026-03-03 23:20:31 UTC**, ICLR 2026: learns adaptive segmentation of raw byte streams using compression-driven chunking and explicitly describes earlier approaches as **“self-tokenizing methods.”** <https://arxiv.org/abs/2603.03583>

Therefore neither **learned tokenization**, **dynamic tokenization from bytes**, nor the label **self-tokenizing** can carry component-level originality here.

**Difference:** these models learn transient/content-dependent segmentations or latent chunks for efficient prediction. They generally do not create a persistent stable-ID registry with explicit executable construction witnesses that a teacher can intentionally extend through a curriculum.

### 3.7 Generated curricula and state-aware sequential teaching are established prior art

**Classification:** `partial_prior_art` for the teacher side of the combination; already acknowledged in the paper, but confirmed here as a hard boundary.

Liu et al., **“Iterative Machine Teaching”**, ICML/PMLR **2017**, studies a teacher feeding examples sequentially and intelligently based on the learner's current state/performance to accelerate convergence.

- <https://proceedings.mlr.press/v70/liu17b.html>

Such et al., **“Generative Teaching Networks”**, arXiv v1 **2019-12-17 00:57:50 UTC**, explicitly proposes learning generators that produce training data, environments and curricula so students learn rapidly.

- <https://arxiv.org/abs/1912.07768>

Thus “teacher generates experience/curricula” and “teacher acts sequentially as learner state changes” are prior art. The current paper must earn distinctiveness from the **interaction between teaching and evolving symbolic representation**, not from either half separately.

## 4. Novelty boundary after this round

The audit materially revises the earlier intuition that the main prior-art neighborhood is primarily machine teaching + BPE/SentencePiece + assembly theory. A more accurate map has at least four independent antecedent lines:

1. **LZ78 / SEQUITUR / grammar compression:** a raw stream can create recursively expandable, reusable, addressable symbolic units and compact construction grammars.
2. **Dynamic byte tokenization:** segmentation and representation granularity can be learned jointly with prediction, including work explicitly described as self-tokenizing before our cutoff.
3. **Library learning / predicate invention:** acquired abstractions can enlarge the language/hypothesis space available to later tasks.
4. **Machine teaching / GTNs:** teachers can adapt sequences or generate curricula/data to drive a learner toward a target.

The especially important new antecedent in this round is the **LZ78 → grammar induction/SLP** line. The current registry's stable references and recursive concatenative expansions are not merely analogous to modern NLP tokenizers; they are structurally close to decades-old adaptive dictionary and grammar-compression mechanisms. ADVENT is a second important correction because verified invented concepts accumulated for later reuse were public weeks before our self-tokenizing claim.

After accounting for those components, this search **did not locate** a pre-**2026-07-30 21:04:34 UTC** work that combines all of the following in one experimental machine-teaching framework:

1. teacher-selected **deterministic procedural demonstrations** rather than passive parsing alone;
2. an optionally boundary-free primitive binary channel whose **external common score remains primitive next-bit prediction**;
3. demonstrations that can admit new **stable, addressable symbolic units** for use by later lessons;
4. explicit executable construction witnesses / proof metadata for those units;
5. a **concatenation-only** construction substrate with reuse/assembly cost exposed rather than hidden inside a neural tokenizer;
6. joint search/evaluation over curriculum and the evolving registry under **learner-relative pedagogical cost**;
7. success defined partly by **executable algorithm acquisition and transfer**, not only compression or language-model likelihood.

That exact conjunction remains **unresolved by this search**, not established as first or unique. It is also plausible that different communities distribute the ingredients across compression, inductive programming, emergent communication and machine teaching without using compatible terminology.

## 5. Work after our cutoff

Post-cutoff searches used `self-tokenizing`, `adaptive tokenization`, `machine teaching tokenization`, `dynamic vocabulary machine teaching`, `procedural machine teaching`, `proof-indexed tokenization`, the exact paper title, and `generative machine teaching Franklin Baldo`.

The search did locate post-cutoff adaptive-tokenization work in other domains (for example, August 2026 work on user-representation and video tokenization), but none was materially close to the full machine-teaching + persistent proof-registry combination. No post-cutoff source found in this round met the threshold for `later_overlap`, `later_non_citing`, `later_independent`, `later_citing`, or `later_derivative` with respect to the audited combination.

The exact-title / attribution searches also did not locate a later paper that cites or reproduces the current proposal. This is a **negative search result only**; it is not evidence that no such work exists.

## 6. Classification summary

| Candidate | Earliest public date used | Compared subclaim | Classification | Why |
|---|---:|---|---|---|
| Ziv & Lempel / LZ78 | 1978-09 | growing indexed dictionary from raw stream; recursive phrase construction | `prior_art` for subclaim / strong `partial_prior_art` for combination | stable reusable phrase indices and recursive expansion predate the registry |
| SEQUITUR | 1997 | learned reusable hierarchical symbols from sequence | `partial_prior_art` | incrementally induced grammar/nonterminals from the observed stream |
| Smallest grammar / SLP literature | 2005-07-31 | concatenative reusable construction DAG and description cost | `partial_prior_art` | compact acyclic grammars already encode repeated substructure by reusable nonterminals |
| Playgol | 2019 | learned programs become future background knowledge | `partial_prior_art` | acquired abstractions change later learning |
| DreamCoder | 2021 | learned abstraction library reshapes future synthesis | `partial_prior_art` | progressively learned reusable symbolic library |
| MIL predicate invention | 2015 | invention of new symbolic predicates | `partial_prior_art` | learning can extend its own symbolic hypothesis language |
| H-Net | 2025-07-10 | dynamic segmentation learned from raw bytes | `partial_prior_art` | content/context-dependent tokenization is learned jointly end-to-end |
| FLEXITOKENS | 2025-07-17 | learnable byte-boundary tokenizer | `partial_prior_art` | adaptive variable-length tokenization precedes our cutoff |
| RL end-to-end tokenization | 2026-02-15 | token boundaries optimized directly for predictive loss | `partial_prior_art` | endogenous segmentation optimized jointly with model objective |
| Continual dynamic predicate invention | 2026-02-19 | online reusable concept hierarchy | `partial_prior_art` | continual observation grows reusable symbolic abstractions |
| ByteFlow | 2026-03-03 | self-tokenizing raw-byte language model | `partial_prior_art`; term-level anticipation | pre-cutoff paper explicitly uses “self-tokenizing methods” |
| ADVENT | 2026-07-02 | invented symbols + executable verification + cumulative reuse | strong `partial_prior_art` | verified invented predicates/rules enter a reusable knowledge pool |
| Iterative Machine Teaching | 2017 | state-aware sequential teacher | `partial_prior_art` | teacher selects experience based on current learner state |
| Generative Teaching Networks | 2019-12-17 | generated teaching data/curricula | `partial_prior_art` | generated pedagogical experience is established |
| exact full conjunction | — | all seven load-bearing commitments above | `uncertain_date_or_dependency` only in the sense of unresolved novelty | no exact pre-cutoff antecedent located; absence is not proof |

## 7. Reproducibility and next search

The strongest remaining uncertainty is not whether the individual mechanisms have antecedents—they do—but whether an older **interactive formal-language / inductive-programming teaching** paper already combines symbol invention with an intentional teacher and a primitive observation channel. The next useful search should therefore emphasize historical terms such as **language invention, predicate invention under teaching, grammar induction with queries, teaching dimension for program classes, inductive inference with membership/equivalence queries, and concept learning with representation change**, rather than repeating modern “tokenizer” searches.

A future revision of `generative_machine_teaching.md` should also consider adding LZ78, SEQUITUR/grammar compression, DreamCoder/library learning and verified predicate invention to Related Work. The audit itself is kept separate so that this epistemic correction remains dated and reviewable rather than silently rewriting the paper's history.
