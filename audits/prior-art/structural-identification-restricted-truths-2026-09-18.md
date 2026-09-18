---
type: "Audit Report"
title: "Structural Identification from Restricted Truths prior-art audit — 2026-09-18"
description: "Claim-specific temporal audit of structural identification by restricted invariant truths, version spaces, teaching/specification complexity, query cost, and finite hitting/set-cover characterization."
tags: [structural-identification, prior-art, teaching-dimension, version-spaces, model-theory, set-cover, query-cost, identifiability]
timestamp: 2026-09-18T03:22:00-04:00
---

# Structural Identification from Restricted Truths prior-art audit — 2026-09-18

> **Status:** first claim-specific reproducible temporal audit of the novelty boundary in [`structural_identification_from_restricted_truths.md`](../../structural_identification_from_restricted_truths.md). The paper is already unusually conservative about prior art. This audit nevertheless finds a close pre-cutoff 2026 antecedent and sharpens which parts are established teaching/model-theory machinery versus the narrower surviving synthesis. It does **not** establish exhaustive novelty, patent novelty, independent invention, copying, plagiarism, or causal dependence.

## 1. Claims audited

The paper's mathematical contribution decomposes into claims that must be dated and assessed separately:

- **C1 — structural version-space identification:** relative to a hypothesis class `H`, equivalence relation `~`, and admissible truth-valued queries `Q`, evidence identifies target `A` when every surviving candidate is equivalent to `A`;
- **C2 — invariant-query / structural-quotient requirement:** if the goal is identification up to structure, admissible queries should be invariant under the declared structural equivalence, so a version space is a union of equivalence classes rather than a selector of presentations;
- **C3 — observational-equivalence barrier:** if a non-equivalent competitor agrees with the target on every admissible query, no evidence drawn from that query family can identify the target;
- **C4 — finite hitting/set-cover characterization:** for a fixed target, each sound query excludes a set of non-equivalent competitors; identifying sets are exactly covers of all competitors, and minimum-cost identification is weighted set cover;
- **C5 — conjunction collapse:** if finite conjunction is itself an admissible unit-cost query, every finite identifying family can be compressed into one conjunction, so raw query count degenerates and a meaningful complexity requires a restricted grammar and/or query cost;
- **C6 — joint parameterization:** identification complexity is treated explicitly as relative to `(M, ~, H, Q, c)`, separating truth, discrimination, identifiability, structural equivalence, and cost;
- **C7 — Lean formalization:** the generic core laws and the finite example are machine-checked in Lean 4.

C7 is an implementation/formalization contribution rather than a broad mathematical priority claim. This audit therefore concentrates on C1–C6.

## 2. Temporal reconstruction of our claims

### 2.1 Public GitHub event

The earliest unambiguous public GitHub event located for this paper is pull request [`#344`](https://github.com/franklinbaldo/papers/pull/344), **“paper: structural identification theory with Lean proofs.”** It was opened at:

**2026-08-24 03:38:56 UTC.**

The PR body already exposes the substantive C1–C7 architecture rather than merely naming the paper. In particular it states:

- the correction that “minimum number of truths” degenerates under free finite conjunction;
- the parameterization `(candidate universe, structural equivalence, hypothesis class, admissible query family, query cost)`;
- observational-equivalence impossibility;
- invariance under structural equivalence;
- the exact hitting-set characterization;
- finite-conjunction collapse; and
- minimum-cost identification as weighted set cover / Set Cover special case.

The merged commit `8b56c53b129d57e855bc2b17a0a515069c72be6b` is later, at 2026-08-24 03:55:00 UTC, and therefore is **not** used as the priority cutoff.

### 2.2 Cutoff used

Because the PR is a dated public GitHub record and contains the claims explicitly, this audit uses the conservative cutoff:

**Cutoff for C1–C7: 2026-08-24 03:38:56 UTC.**

Only work publicly available before that time is eligible for `prior_art` / `partial_prior_art` / `adjacent_prior_work`. Work after that time is classified separately.

## 3. Search protocol

The search decomposed the framework instead of searching only the title. Sources included arXiv, ACM/COLT records, JCSS/Elsevier, NeurIPS proceedings, DBLP, model-theory literature, and targeted discovery searches. Primary records were preferred for dates and technical claims.

Representative queries included:

- `teaching dimension uniquely identify target concept version space`
- `exact specification by examples hypothesis space`
- `minimum teaching set minimum set cover`
- `teaching set hitting set competitor hypotheses`
- `cost sensitive active learning version space query cost`
- `outcome dependent query costs version space singleton`
- `distinguishing structures first order sentence minimal quantifier rank`
- `logical complexity graph define up to isomorphism quantifier depth`
- `structural identification restricted queries isomorphism`
- `version space structural identifiability teaching cost`
- `identifiability order dimension partial orders teaching number hitting set`
- `conjunction collapse identification query language`
- post-cutoff searches for `structural identifiability version space teaching September 2026`, `identification query cost structures 2026`, and exact-title / distinctive-phrase searches.

Negative searches are bounded search results only. “Not located” does not imply nonexistence.

## 4. Pre-cutoff findings

### 4.1 Exact specification and teaching dimension already formalize target isolation in a hypothesis space

**Work:** Martin Anthony, Graham Brightwell, David Cohen, and John Shawe-Taylor, **“On Exact Specification by Examples.”** COLT 1992.

- public proceedings date: **1992-07-01**;
- DOI: <https://doi.org/10.1145/130385.130420>.

**Work:** Sally A. Goldman and Michael J. Kearns, **“On the Complexity of Teaching.”** Preliminary COLT 1991; institutional technical report WUCS-92-28 dated **1992-08-11**; JCSS 1995.

- institutional record: <https://openscholarship.wustl.edu/cse_research/591/>;
- journal DOI: <https://doi.org/10.1006/jcss.1995.1003>.

**Compared claims:** C1, C3, and the unweighted form of C4/C6.

**Classification:** `prior_art` for the generic identification problem “choose observations/examples so that exactly one target remains in a hypothesis/concept class”; `partial_prior_art` for the full structural-quotient formulation.

Anthony et al. define a target function as *specified* by a set when it is the only hypothesis agreeing with the target on that set, and minimize the cardinality of such specifying sets. Goldman–Kearns formalize teaching dimension as the minimum number of instances a helpful teacher must reveal to uniquely identify the target concept. This is already the core version-space isolation problem.

Consequently, neither “evidence identifies when it removes all competing hypotheses” nor “minimum specifying evidence” is a new mathematical object here. The current paper correctly acknowledges this in prose; the audit makes the priority classification explicit.

**Difference:** these works operate on concepts/hypotheses with labeled examples. They do not foreground a separately declared structural equivalence on presentations and an invariance requirement on admissible tests. That quotient layer is where the present abstraction departs from the ordinary teaching formulation.

### 4.2 Set-cover geometry of a teaching set is classical, not merely an analogy

The classical teaching problem can be written exactly in the competitor-exclusion geometry used by C4: every example/query eliminates a subset of incorrect concepts; a teaching set must eliminate all of them. Later teaching literature explicitly describes optimal teaching-sequence construction for a general finite concept class as a minimum-set-cover problem and cites Goldman–Kearns for the hardness result.

A useful accessible statement is in the AI teaching literature: optimal teaching for arbitrary concepts is NP-hard by reduction to **MINIMUM SET COVER**, with teaching examples selected to eliminate the remaining concepts.

**Compared claim:** C4.

**Classification:** `prior_art` for the generic finite “target competitors + tests that eliminate subsets + minimum cover” characterization; `partial_prior_art` for its quotient-by-structural-equivalence specialization.

This changes the most important priority boundary in the paper. The theorem `identifies_iff_hits_competitors` is a correct and useful structural restatement, and the Lean proof is valuable as verification, but the underlying finite combinatorial equivalence is not a new optimization insight. The paper already calls the NP-hardness consequence unsurprising; this audit recommends treating the entire finite set-cover layer as imported teaching/specification machinery once the structural quotient has been formed.

### 4.3 Logical definability already measures the cost of identifying a structure up to isomorphism

**Work:** Oleg Pikhurko and Oleg Verbitsky, **“Logical complexity of graphs: a survey.”** arXiv v1 **2010-03-25**.

- URL: <https://arxiv.org/abs/1003.4865>.

The paper defines graph logical depth `D(G)` as the minimum quantifier depth of a first-order sentence defining `G` **up to isomorphism**, and also studies logical width and shortest defining-sentence length.

**Work:** Thiago Alves Rocha, Ana Teresa C. Martins, Francicleber Martins Ferreira, **“On Distinguishing Sets of Structures by First-Order Sentences of Minimal Quantifier Rank.”** LSFA 2018 / ENTCS 2019.

- public conference version: **2018**;
- DOI: <https://doi.org/10.1016/j.entcs.2019.07.012>.

**Compared claims:** C2, C5, C6.

**Classification:** `prior_art` for the general idea that structural identification up to isomorphism must be relative to a logical resource/cost measure rather than raw truth count; `partial_prior_art` for the present generic query-family abstraction.

Pikhurko–Verbitsky directly optimize logical resources of a sentence defining a structure up to isomorphism. Rocha et al. optimize quantifier rank of a sentence distinguishing sets of relational structures. Thus the paper's insistence that the *internal complexity* of a query matters is firmly established model-theoretic territory.

**Difference:** these works fix logical languages/fragments and optimize logical complexity; the present framework abstracts away from a specific logic and can attach arbitrary domain-specific cost to an invariant test.

### 4.4 Query cost plus version-space elimination is established active-learning machinery

**Work:** Sivan Sabato, Anand D. Sarwate, Nathan/Nati Srebro, **“Auditing: Active Learning with Outcome-Dependent Query Costs.”** arXiv v1 **2013-06-10 20:18:48 UTC**, NeurIPS 2013.

- arXiv: <https://arxiv.org/abs/1306.2347>;
- proceedings: <https://proceedings.neurips.cc/paper_files/paper/2013/hash/40008b9a5380fcacce3976bf7c08af5b-Abstract.html>.

**Compared claims:** cost component of C6 and adaptive extension of C4.

**Classification:** `prior_art` for the generic idea of identifying a hypothesis by shrinking a finite version space while queries have nonuniform/outcome-dependent costs; `adjacent_prior_work` for the nonadaptive structural certificate in this paper.

Sabato et al.'s general finite-hypothesis section explicitly defines a query cost, a current version space, chooses queries by hypotheses eliminated per unit cost, and terminates when the version space is a singleton. This predates the present paper by thirteen years and confirms that adding query cost to hypothesis identification is not independently novel.

**Difference:** C6 uses a static evidence certificate over invariant structural predicates, not an adaptive label-query policy with unknown outcome-dependent costs.

### 4.5 A very close August 2026 antecedent combines version spaces, structural objects, teaching cost, and hitting sets

**Work:** Faizanuddin Ansari, Debanjan Dutta, and Swagatam Das, **“Identifiability and Order-Dimension Limits of In-Context Learning on Partial Orders.”**

- arXiv v1: **2026-08-14 06:47:40 UTC**;
- URL: <https://arxiv.org/abs/2608.14004>.

**Compared claims:** C1, C3, C4, and C6.

**Classification:** `partial_prior_art` for the full present framework; `prior_art` within the specific domain of finite partial orders for a combination of version-space identifiability, teaching cost, structural complexity, and hitting-set characterization.

This is the closest newly located antecedent in this run and predates our public cutoff by about ten days. Ansari et al. explicitly:

- define a **version-space semantics** over partial orders consistent with demonstrations and background theory;
- separate **logical identifiability**, **prompt teaching cost**, and **structural complexity**;
- characterize whether a query is forced true, forced false, or genuinely unidentifiable across the version space;
- characterize the open-world teaching number as the number of covers plus a **blocker-set hitting number**; and
- distinguish structural representation complexity (order dimension) from teaching/certificate complexity.

This materially narrows any claim that the combination “structural object + version space + explicit teaching/identification cost + hitting set” first appears in the present note.

**Difference:** the Ansari–Dutta–Das framework is specialized to finite partial orders on a known universe and mixed positive/negative comparison prompts. It does not state the general `(M, ~, H, Q, c)` abstraction, does not make quotienting arbitrary presentations by an independently declared equivalence the central construction, and does not impose a generic invariance condition on arbitrary query families. The present note therefore still has a plausible contribution as a **domain-independent interface/quotient abstraction and formalization**, not as the first appearance of the constituent machinery.

### 4.6 The observational-equivalence barrier is a generic identifiability fact

C3 states that if two non-equivalent candidates give the same answer to every admissible query, no evidence selected from those queries can distinguish them.

**Classification:** `prior_art` at the level of principle; the Lean theorem is a verified restatement in the paper's abstraction.

This follows immediately from both classical version-space semantics and the model-theoretic notion of equivalence relative to a logical fragment. Ansari et al.'s trichotomy makes the same epistemic point in a concrete structural class: when multiple consistent posets disagree on a query, the query is not logically identifiable from the prompt/background theory.

The current theorem is still useful because it pins the limitation to the declared query family and structural equivalence in a minimal Lean interface. Its novelty should not be described as discovery of a new identifiability impossibility principle.

### 4.7 Conjunction collapse is a correct load-bearing warning, but not a safe standalone novelty claim

C5 observes that if the admissible language is closed under finite conjunction and every formula costs one unit, a finite identifying family can be replaced by its conjunction.

The run did **not** locate a pre-cutoff paper using the exact name “conjunction collapse” for this particular teaching/structural-identification observation. That negative search does not imply novelty. The mathematical step is an immediate consequence of conjunction semantics, while Scott-sentence and logical-complexity traditions already make clear that **one formula is not one unit of information** unless formula complexity is ignored.

**Classification:** `adjacent_prior_work` for the mature logical-complexity boundary; `uncertain_date_or_dependency` would be appropriate only if someone attempted to claim priority for this exact named lemma. The paper itself wisely says it does not claim novelty for the fact that conjunction combines formulas.

## 5. Post-cutoff search

Targeted searches over work publicly visible between **2026-08-24 03:38:56 UTC** and this audit did not locate a work that materially duplicates the full domain-independent structural-quotient abstraction after our cutoff.

The searches included combinations of:

- `structural identifiability version space teaching September 2026`;
- `identification query cost structures arxiv September 2026`;
- `teaching number hitting set September 2026`;
- `restricted queries structural identification`;
- the exact paper title and distinctive tuple/phrase combinations.

No candidate met the threshold for `later_overlap`, `later_non_citing`, `later_citing`, or `later_derivative` in this run. This is a bounded negative result, not evidence that no such work exists.

## 6. Claim-by-claim classification after the audit

| Claim | Classification | Reason |
|---|---|---|
| C1 structural version-space isolation | `prior_art` generically; surviving specialization only | teaching/specification already defines unique target isolation in a hypothesis class |
| C2 quotient by declared structural equivalence + invariant queries | `partial_prior_art` | model theory defines up-to-isomorphism identification; teaching supplies version spaces; exact generic interface remains a synthesis |
| C3 observational-equivalence barrier | `prior_art` as principle | immediate version-space/logical-equivalence identifiability limit |
| C4 finite hitting/set-cover characterization | `prior_art` generically; `partial_prior_art` structurally | teaching-set construction already has competitor-elimination / set-cover geometry; Ansari et al. give a structural hitting-set case before cutoff |
| C5 conjunction collapse | `adjacent_prior_work`; exact naming not established | immediate logical fact; broader formula-complexity problem is classical |
| C6 `(M, ~, H, Q, c)` joint abstraction | `partial_prior_art` | all components and several close combinations predate cutoff; exact domain-independent quotient interface was not located in searched sources |
| C7 Lean formalization | implementation contribution; not priority-audited as theorem novelty | value is machine checking of this interface, not novelty of the underlying classical facts |

## 7. Revised novelty boundary

After this audit, the paper should **not** be summarized as introducing:

- version-space structural identification as a new problem;
- minimum specifying evidence;
- the general competitor-elimination/set-cover view;
- query cost in hypothesis identification;
- structural definability up to isomorphism under logical-resource constraints; or
- the observational-indistinguishability principle.

A defensible narrower contribution is:

> a compact, domain-independent interface that takes structural equivalence itself as an explicit parameter, requires admissible tests to respect that equivalence, combines the resulting quotient version space with arbitrary query cost, exposes the free-conjunction degeneracy in that interface, and machine-checks the generic laws in Lean 4.

Even this should be phrased as a synthesis/formalization claim unless a broader search establishes that the exact interface has not appeared elsewhere. The strongest newly found pressure on originality is Ansari–Dutta–Das (2026-08-14), which already combines a structural class, version-space identifiability, teaching cost, and a hitting-set term before our 2026-08-24 cutoff.

## 8. Recommended revision to the paper

The current paper is already largely aligned with this conclusion. A future editorial patch should add Ansari, Dutta & Das (2026) to the teaching/identifiability related-work section and explicitly state that a structurally specialized combination of version spaces, teaching cost, and hitting sets was public ten days before PR #344.

The set-cover paragraph should also be read as a **re-expression after quotienting**, not as a novel generic combinatorial theorem. This does not weaken the Lean artifact; it clarifies what the artifact certifies.

## 9. Search ledger and unresolved questions

### Sources/bases consulted

- GitHub history / PR #344 / commit history;
- arXiv;
- ACM Digital Library / COLT;
- Washington University Open Scholarship;
- JCSS / Elsevier metadata;
- NeurIPS proceedings;
- DBLP;
- model-theory / finite-model-theory literature discovered through primary records and cited-work tracing.

### Important unresolved questions

1. Has the exact five-parameter quotient interface `(M, ~, H, Q, c)` appeared in diagnosis, experiment design, exact learning, or algebraic specification under different terminology?
2. Is there an older explicit theorem stating the positive-evidence version of weighted teaching/specification as weighted set cover in exactly the target-specific form used here?
3. Has the “free conjunction makes finite certificate cardinality collapse to one” observation been published as an explicit warning in teaching dimension, definability, or description-complexity literature?
4. Are there proof-assistant formalizations (Lean/Coq/Isabelle) of teaching dimension/specifying sets that would narrow C7 as an implementation contribution?

These are appropriate targets for a later incremental audit rather than grounds for overstating the current negative search.
