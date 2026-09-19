---
type: "Audit Report"
title: "Lean–Argdown legal reasoning pipeline prior-art audit — 2026-09-18"
description: "Claim-specific temporal audit of the legal-reasoning audit pipeline, reconstructing separate public cutoffs for the Lean axiom-audit method, the staged workflow, the Argdown migration, and the later compilation-vs-acyclicity thesis."
tags: [prior-art, legal-ai, lean4, argdown, formal-verification, computational-law, legal-reasoning, brazilian-civil-procedure]
timestamp: 2026-09-18T08:59:25-04:00
---

# Lean–Argdown legal reasoning pipeline prior-art audit — 2026-09-18

> **Status:** first claim-specific temporal prior-art audit of [`pipeline_lean_argdown.md`](../../pipeline_lean_argdown.md), _Auditing Legal Reasoning with Lean 4: A Six-Phase Pipeline for Brazilian Civil Procedure Using Argdown and Formal Verification_. This audit reconstructs claim-specific public dates from both `franklinbaldo/papers` and the earlier public implementation in `franklinbaldo/skills`. It does **not** establish exhaustive novelty, patent novelty, copying, plagiarism, or causal dependence.

## 1. Claims audited

The current paper bundles several historically distinct claims. They should not share one cutoff.

- **C1 — Lean legal dependency audit:** represent a legal argument as named axioms/facts/theorems in Lean 4, compile it, and use `#print axioms` to expose the transitive legal/factual assumptions supporting each theorem, including which authorities are load-bearing.
- **C2 — staged legal-audit workflow:** separate argument decomposition, formal verification, substantive legal assessment, defeat/resolution synthesis, and forensic translation instead of treating formal compilation as the final legal judgment.
- **C3 — exact six-phase Argdown pipeline:** source material → Argdown topology → Lean formalization → subjective legal analysis with loop-back → resolutive defeat synthesis → forensic translation.
- **C4 — compilation-over-acyclicity thesis:** theorem-prover compilation is more appropriate than purported acyclicity-based argumentation verification because legal systems contain circular/self-referential structures that acyclic argument graphs cannot accommodate.
- **C5 — dual-gate / role-separation thesis:** successful formal compilation is necessary but not sufficient; a separate legal-analysis gate must assess whether axioms fairly and adequately represent law/record, ideally with role/context separation from the formalizer.
- **C6 — Brazilian CPC implementation:** a modular Lean 4 library and worked Brazilian civil-procedure case connect Argdown attacks to compiled theorems and later forensic drafting.
- **C7 — full conjunction:** Argdown as the upstream argument notation + Lean as an assumption/dependency auditor + explicit post-compilation legal fairness gate + defeat synthesis + forensic translation, implemented for Brazilian civil procedure.

The main novelty question is C7. C4 is different: the present audit found a correctness problem in the paper's stated comparator, not merely an older work occupying the same idea.

## 2. Temporal reconstruction of our claims

### 2.1 C1 — Lean legal dependency audit: 8 May 2026

The paper is **not** the first public artifact carrying C1. The linked public repository `franklinbaldo/skills` contains an earlier implementation.

Commit [`3aa3288196a0078c7d3ba86117df3aca5c5d16db`](https://github.com/franklinbaldo/skills/commit/3aa3288196a0078c7d3ba86117df3aca5c5d16db), **2026-05-08 23:36:26 UTC**, introduced `legal-argument-lean`. Its initial `SKILL.md` already says that the payoff is the `#print axioms` audit, requires `#print axioms` for every theorem, maps legal authorities and case facts to named axioms, and proposes comparing axiom sets to identify load-bearing precedents and hidden argumentative hierarchy.

**C1 cutoff:** **2026-05-08 23:36:26 UTC**.

### 2.2 C2/C5/C6 — staged workflow and separate legal gate: 9 May 2026

`franklinbaldo/skills` PR [`#2`](https://github.com/franklinbaldo/skills/pull/2), **opened 2026-05-09 17:43:42 UTC**, publicly described the predecessor seven-phase pipeline: Toulmin decomposition → structural Dung mapping → Lean → subjective legal analysis → resolutive Dung → forensic translation. Its design principles already state that Lean compilation is necessary but insufficient for defeat, that substantive analysis must assess legal quality, and that formalizer/analyst roles should be separated.

The PR also carried the worked Brazilian case and compiled Lean theorems.

**C2/C5/C6 cutoff:** **2026-05-09 17:43:42 UTC**.

### 2.3 C3 — exact Argdown six-phase pipeline: 10 May 2026

`franklinbaldo/skills` PR [`#3`](https://github.com/franklinbaldo/skills/pull/3), **opened 2026-05-10 10:52:29 UTC**, replaced Toulmin + structural Dung with Argdown and publicly enumerated the resulting six phases:

`material → Argdown → Lean → subjective legal analysis → defeat synthesis → forensic translation`.

That PR is earlier than the paper and therefore supplies the cutoff for the exact Argdown wiring.

**C3 cutoff:** **2026-05-10 10:52:29 UTC**.

### 2.4 C4 — compilation-over-acyclicity thesis: 13 May 2026

The earliest public paper version located is commit [`3de41c63f429ab2f4f9a1844825be2e9bd78dbf4`](https://github.com/franklinbaldo/papers/commit/3de41c63f429ab2f4f9a1844825be2e9bd78dbf4), 2026-05-13 03:20:27 UTC, under the old filename `paper2_pipeline_lean_argdown.md`. It already contains the paper's stronger theoretical claim that compilation is superior to structural acyclicity because of Kelsenian circularity.

The corresponding public PR [`#9`](https://github.com/franklinbaldo/papers/pull/9) opened at **2026-05-13 03:20:45 UTC**. This audit conservatively uses the PR opening as the public cutoff.

**C4 cutoff:** **2026-05-13 03:20:45 UTC**.

### 2.5 Cutoff table

| Claim | Earliest public GitHub evidence located | Cutoff used |
|---|---|---|
| C1 | `franklinbaldo/skills` commit `3aa3288…` | 2026-05-08 23:36:26 UTC |
| C2/C5/C6 | `franklinbaldo/skills` PR #2 | 2026-05-09 17:43:42 UTC |
| C3 | `franklinbaldo/skills` PR #3 | 2026-05-10 10:52:29 UTC |
| C4 | `franklinbaldo/papers` PR #9 | 2026-05-13 03:20:45 UTC |
| C7 | requires C1–C6; exact Argdown conjunction publicly present by PR #3, with C4 added in PR #9 | claim-specific; do not collapse to one paper date |

No current-file timestamp is used as priority evidence.

## 3. Search protocol

Sources searched included arXiv primary records, CEUR proceedings, ACM/ITP/publisher records, Lean reference documentation, Argdown primary documentation, journal articles on Dung-style argumentation cycles, and GitHub history. Searches decomposed the paper into theorem-prover legal reasoning, neuro-symbolic legal pipelines, intermediate verification, natural-language-to-logic translation, proof-assistant assumption auditing, argument-map/proof-assistant bridges, and cyclic argumentation.

Representative queries:

- `legal reasoning theorem prover proof assistant Isabelle Lean formal verification`
- `legal argumentation proof assistant Isabelle HOL`
- `LLM legal formal verification SMT multi-agent`
- `legal reasoning intermediate verification procedural compliance agent`
- `natural language legal case logical formula symbolic reasoner`
- `Argdown Lean 4`
- `Argdown theorem prover legal`
- `Argdown formal verification legal reasoning`
- `#print axioms legal reasoning Lean`
- `legal argumentation acyclicity Dung cycles`
- `cycles argumentation frameworks legal cases`
- `TAIR Bowers Ludäscher acyclicity`
- exact-title searches for `Auditing Legal Reasoning with Lean 4`
- exact-combination searches for `six-phase pipeline Argdown Lean legal`

The exact-title and exact Argdown+Lean searches did not locate a pre-cutoff scholarly duplicate. “Not located” below remains a bounded search result, not proof of nonexistence.

## 4. Candidate-by-candidate findings

### 4.1 Benzmüller, Fuenmayor & Lomfeld — LogiKEy / value-oriented legal reasoning in Isabelle/HOL — 23 Jun 2020

- **First public date used:** arXiv v1, 2020-06-23 06:57:15 UTC.
- **Venue/status:** preprint lineage later published; related peer-reviewed Isabelle/HOL work appeared at ITP 2021.
- **Compared claims:** C1, C4, C6.
- **Classification:** `prior_art` for the broad proposition that substantive/value-oriented legal reasoning can be formalized, automatically evaluated, and reconstructed inside a proof assistant; `partial_prior_art` for C1/C6.
- **Overlap:** LogiKEy encodes cases/laws plus context-dependent value preferences and uses Isabelle/HOL theorem-proving technology as a testbed for formal verification of legal theories/DSLs. That materially contradicts any broad framing in which proof assistants had been confined to mathematical subproblems or could not accommodate substantive legal reasoning.
- **Difference:** no Argdown upstream layer, no Lean `#print axioms` legal burden audit, no six-phase workflow, and no Brazilian CPC library.
- **URL:** https://arxiv.org/abs/2006.12789 ; https://doi.org/10.4230/LIPIcs.ITP.2021.7

### 4.2 Merigoux et al. — _Catala: a programming language for the law_ — 4 Mar 2021

- **First public date used:** arXiv v1, 2021-03-04.
- **Venue/status:** PACMPL 2021.
- **Compared claims:** C2, C5, C6.
- **Classification:** `partial_prior_art`.
- **Overlap:** Catala systematically translates statutory law into executable formal artifacts, implements a compiler, proves core compilation steps in F*, and explicitly designs the workflow as a shared medium for lawyers and programmers. It occupies the broad territory “formalization/compilation as a legal-audit and collaboration instrument rather than autonomous substantive adjudication.”
- **Difference:** statutory executable specification rather than adversarial legal argument auditing; no Argdown/Lean dependency audit or defeat synthesis.
- **URL:** https://arxiv.org/abs/2103.03198 ; https://doi.org/10.1145/3473582

### 4.3 Bench-Capon — _Dilemmas and paradoxes: cycles in argumentation frameworks_ — 13 Feb 2014

- **First public date used:** online publication 2014-02-13.
- **Venue/status:** _Journal of Logic and Computation_.
- **Compared claim:** C4.
- **Classification:** `prior_art` for the proposition that Dung-style argumentation frameworks can contain and semantically analyze cycles; **direct corrective evidence** against C4 as presently framed.
- **Reason:** the article is specifically about even and odd cycles in Dung-style argumentation frameworks. Thus acyclicity is not a general integrity requirement of Dung AFs.
- **URL:** https://doi.org/10.1093/logcom/exu011

### 4.4 Bench-Capon — _Before and after Dung: Argumentation in AI and Law_ — 2020

- **First public date:** 2020 publication.
- **Venue/status:** _Argument & Computation_ 11(1–2).
- **Compared claim:** C4.
- **Classification:** `prior_art` / corrective evidence.
- **Reason:** the legal examples explicitly contain cycles; the paper explains that opposing legal arguments naturally form cycles and that even-length cycles are close to inescapable in argumentation-framework representations of live legal disputes. This is stronger than merely observing that abstract AFs permit cycles: legal AF practice uses them as representations of contested issues.
- **URL:** https://doi.org/10.3233/AAC-190477

### 4.5 Bowers & Ludäscher — TAIR, _Towards Trustworthy AI Results using Evidence Structures_ — workshop 9 Dec 2025; proceedings 5 Feb 2026

- **First public date used for conservative documentary classification:** CEUR proceedings publication 2026-02-05. The paper was presented at AI4EVIR/JURIX on 2025-12-09.
- **Compared claims:** C2, C4, C5.
- **Classification:** `partial_prior_art` for C2/C5; corrective evidence for C4.
- **Overlap:** TAIR already defines a staged generation → verification → gap-detection loop, independent verification, and domain-dependent evidence standards. In law it builds a BAF from source briefs and later performs structural and argumentation-semantic checks.
- **Critical correction:** no `acycl` or `cycle` requirement was located in the primary TAIR paper. Its legal verification code checks edge resolution, citations/metadata and temporal consistency; the next stage performs argumentation-theoretic semantic analysis. The paper's table explicitly contrasts mathematical proof checking with legal `coherence, defense`, not “acyclicity.” Accordingly, `pipeline_lean_argdown.md` currently attributes to TAIR an acyclicity criterion that the cited primary source does not establish.
- **URL:** https://ceur-ws.org/Vol-4157/paper6.pdf

### 4.6 Chen, Cai, Hou & Dong — L4M, _Towards Trustworthy Legal AI through LLM Agents and Formal Reasoning_ — 26 Nov 2025

- **First public date used:** arXiv v1, 2025-11-26 04:05:06 UTC.
- **Compared claims:** C2, C5, C7.
- **Classification:** `partial_prior_art`, and `prior_art` for the generic multi-stage/role-separated neuro-symbolic legal pipeline claim.
- **Overlap:** L4M already combines role-differentiated LLM agents with solver-backed formal verification: statute formalization; independent prosecutor/defense extraction; autoformalization into constraints; solver adjudication; unsat-core-driven iterative self-critique; final Judge-LLM verbalization. This materially narrows any claim that a staged legal pipeline combining role separation, formal verification, iterative repair, and human-readable legal output was new in May 2026.
- **Difference:** SMT/Z3 rather than Lean; no Argdown; no `#print axioms`; the solver is closer to adjudicator than audit-only diagnostic; no explicit later independent legal-fairness gate over the axioms after successful solving.
- **URL:** https://arxiv.org/abs/2511.21033

### 4.7 Bowers & Ludäscher / TAIR versus our dual-gate principle

TAIR is especially important to distinguish from the current paper rather than caricature. TAIR explicitly says formal mathematical reasoning admits a definitive proof-checking endpoint while legal reasoning culminates in structured assessments of coherence and contestability. That is conceptually close to C5's separation of machine-checkable derivability from later legal assessment, even though TAIR does not put a Lean proof in the legal branch.

- **Classification:** `partial_prior_art` for C5.
- **Residual distinction:** our workflow runs Lean over legal theorems themselves and then subjects the declared legal/factual axioms to a separate substantive gate. That exact composition was not located in TAIR.

### 4.8 LawThinker — 12 Feb 2026

- **First public date used:** arXiv v1, 2026-02-12 15:19:11 UTC.
- **Compared claims:** C2, C5.
- **Classification:** `partial_prior_art`.
- **Overlap:** LawThinker makes verification an atomic step after each exploration operation and checks knowledge accuracy, fact-law relevance, and procedural compliance. It is prior art for the generic principle that trustworthy legal reasoning must verify intermediate process steps, not merely final answers.
- **Difference:** retrieval/research agent rather than theorem-prover formalization; no Argdown, Lean or axiom dependency audit.
- **URL:** https://arxiv.org/abs/2602.12056

### 4.9 Nguyen & Satoh — PYTHEN — 16 Mar 2026

- **First public date used:** arXiv v1, 2026-03-16 14:10:37 UTC.
- **Compared claims:** C4, C6.
- **Classification:** `adjacent_prior_work` / `partial_prior_art`.
- **Overlap:** formal defeasible legal reasoning with explicit rules, conditions and exceptions, positioned as an LLM-autoformalization target. It further weakens the broad binary “proof assistants are deductive, legal reasoning is defeasible, therefore formal systems cannot handle the latter”; the field already had multiple formal routes for defeasibility.
- **Difference:** Python rule engine rather than proof assistant and no audit workflow.
- **URL:** https://arxiv.org/abs/2603.15317

### 4.10 Xue et al. — Legal2LogicICL — 13 Apr 2026

- **First public date used:** arXiv v1, 2026-04-13 16:36:48 UTC.
- **Compared claims:** C2/C6.
- **Classification:** `partial_prior_art`.
- **Overlap:** natural-language legal cases are transformed into PROLEG logical formulae before being sent to a symbolic reasoner; the work explicitly situates itself within existing logic-based legal reasoning pipelines.
- **Difference:** its contribution is the ICL/RAG semantic parser and generalization, not a verification/audit workflow, Argdown topology or Lean assumption audit.
- **URL:** https://arxiv.org/abs/2604.11699

### 4.11 Argdown itself — public before our cutoffs

- **First public evidence used:** Argdown documentation contains dated examples from 2018 and the project predates our work by years.
- **Compared claim:** C3.
- **Classification:** `prior_art` for all Argdown syntax/argument-mapping functionality; `adjacent_prior_work` for C3.
- **Reason:** argument titles/statements, premise-conclusion structures, attack/support relations, metadata and argument-map export are Argdown capabilities, not contributions of our paper.
- **Bounded negative:** searches for `Argdown + Lean`, `Argdown + theorem prover`, and `Argdown + formal verification + legal reasoning` did not locate a pre-cutoff scholarly workflow using Argdown as the upstream representation for Lean legal auditing.
- **URL:** https://argdown.org/ ; https://argdown.org/syntax/

### 4.12 Lean `#print axioms` — existing platform capability

- **First public status:** standard Lean functionality predating our work.
- **Compared claim:** C1.
- **Classification:** `prior_art` for the command/capability; no novelty should be attributed to the existence of transitive axiom-dependency inspection.
- **Reason:** Lean's reference manual states that `#print axioms` displays all axioms a declaration depends on directly or indirectly and explicitly describes this as usable to audit proof assumptions.
- **Residual distinction:** searches did not locate a pre-cutoff legal-method paper operationalizing that output as a per-theorem ledger of statutes, precedents and case facts to compare argumentative burden/load-bearing authorities.
- **URL:** https://lean-lang.org/doc/reference/latest/Axioms/#displaying-axiom-dependencies

## 5. Material correction: C4 does not survive as written

This is the strongest result of the audit.

The current paper says that TAIR uses BAFs with “acyclicity verification,” that argumentation frameworks requiring acyclicity cannot accommodate legal circularity, and that Lean is superior because its dependency graph need not be acyclic.

Three independent problems appear:

1. **The cited TAIR primary source does not establish an acyclicity gate.** Targeted full-text search found no `acycl` or `cycle` occurrence. TAIR checks structural integrity such as edge resolution/metadata and then computes argumentation semantics.
2. **Dung-style argumentation frameworks are not generally acyclic.** Cycles have a dedicated formal literature, and Bench-Capon explicitly uses them to represent dilemmas and legal disputes.
3. **Lean mutual recursion is not evidence that arbitrary circular logical justification is permitted.** Lean's kernel accepts recursive definitions only through controlled mechanisms such as structural/well-founded recursion, termination proofs, inductive/fixpoint constructions, or unsafe/partial modes with different logical status. Mutual recursion is therefore not a license for theorem A to justify theorem B while theorem B justifies theorem A without a well-founded construction. The present analogy between legal circular grounding and arbitrary cyclic theorem dependencies is technically unsafe.

**Classification for C4:** the broad proposition is **not defensible as an originality claim in its current form**. Prior work already establishes cyclic AF semantics, including legal examples, and the TAIR comparator is misdescribed. This is recorded as an epistemic correction, not as a priority dispute.

A narrower thesis could survive: `#print axioms` exposes the **assumption boundary** of a formalized legal argument in a way that an argumentation topology alone does not. That is a comparison between two different audit questions — premise dependency versus dialectical acceptability — and does not require claiming that argumentation frameworks forbid cycles.

## 6. Post-cutoff convergence

### 6.1 Wang & Gilpin — _Bridging Legal Interpretation and Formal Logic_ — 13 May 2026 19:11:09 UTC

- **Temporal relation:** later than C1–C6 cutoffs; notably only ~16 hours after the paper-specific C4 PR cutoff.
- **Compared claims:** C1, C2, C5.
- **Classification:** `later_independent`.
- **Overlap:** proposes combining LLM legal interpretation with formal verification to reduce unsupported, assumption-laden legal conclusions.
- **Dependency assessment:** no positive evidence of dependence on our work was located. Given the same-day timing, causal inference would be especially unwarranted.
- **URL:** https://arxiv.org/abs/2605.14049

### 6.2 Chen et al. — LexGuard / _Which Changes Matter?_ — 26 May 2026

- **First public date:** arXiv v1, 2026-05-26 04:20:06 UTC.
- **Compared claims:** C2/C5.
- **Classification:** `later_independent` relative to our work.
- **Reason:** later formal-reasoning legal pipeline with adversarial agents and SMT verification. Its visible intellectual lineage includes the authors' own pre-cutoff L4M paper, which strongly supports an independent continuation path.
- **URL:** https://arxiv.org/abs/2605.26530

### 6.3 Wang et al. — _Know Your Limits_ — 15 Jun 2026

- **First public date:** arXiv v1, 2026-06-15 02:14:49 UTC.
- **Compared claim:** C5.
- **Classification:** `later_independent`.
- **Overlap:** empirically documents a gap between legally reasonable interpretation and strict formal entailment and shows that formal structure does not by itself guarantee faithful reasoning. This converges strongly with our principle that compilation/formal verification is not sufficient for legal validity.
- **Difference:** benchmark study of solver/autoformalization faithfulness, not the Argdown→Lean→legal-analysis pipeline.
- **URL:** https://arxiv.org/abs/2606.16118

No later work examined in this round crossed the evidentiary threshold for `later_non_citing`, `later_citing`, or `later_derivative` with respect to the **full** C7 conjunction. Absence of a citation search hit is not enough by itself to upgrade a merely adjacent later paper to `later_non_citing`.

## 7. Claim classification matrix

| Claim | Classification after audit | Main evidence |
|---|---|---|
| C1 — Lean legal dependency audit | `partial_prior_art` | LogiKEy/Isabelle legal theorem proving is old; `#print axioms` is standard Lean; no earlier legal use of its transitive output as burden/load-bearing-authority ledger was located |
| C2 — staged legal-audit workflow | `partial_prior_art` | TAIR, L4M, LawThinker and logic-based legal pipelines predate our cutoff |
| C3 — exact Argdown six-phase pipeline | components are `prior_art`; exact conjunction not located | Argdown is old; formal legal pipelines are old; no pre-cutoff Argdown→Lean legal workflow located |
| C4 — compilation > acyclicity because law is circular | **requires correction; not defensible as written** | cycles are native to Dung-style AF literature and legal examples; TAIR does not state an acyclicity gate; Lean recursion analogy is too broad |
| C5 — compilation necessary but insufficient + separate legal gate | `partial_prior_art` | TAIR/L4M/LawThinker already separate formal/process verification dimensions; exact “Lean legal theorem → independent axiom fairness gate” remains narrower |
| C6 — Brazilian CPC Lean implementation | `adjacent_prior_work` / implementation-specific residual | formal legal libraries existed; no earlier Brazilian CPC Lean library located in searched sources |
| C7 — full conjunction | no material pre-cutoff antecedent located after bounded searches | novelty, if claimed, must live in the integration and audit contract, not its ingredients |

## 8. What should change in the paper

This audit does not silently rewrite the paper; it records the epistemic revision first.

The next substantive revision should:

1. **Delete or replace the claim that TAIR verifies legal BAFs by acyclicity.** Cite what TAIR actually verifies.
2. **Drop the claim that argumentation frameworks generally require acyclicity.** Cycles are a long-studied feature, including in legal AFs.
3. **Remove the argument that Lean permits circular proof dependencies simply because it supports mutual inductive/recursive definitions.** If self-reference matters, state exactly which Lean construction models it and what soundness/termination conditions apply.
4. Reframe the comparison as **different audit surfaces**:
   - Argdown/AF: dialectical topology, attacks/supports, extensions/coherence;
   - Lean: consequence under explicit assumptions plus transitive axiom dependency;
   - legal-analysis gate: whether those assumptions fairly encode the governing sources and record.
5. Position the contribution against **LogiKEy, Catala, TAIR, L4M, LawThinker, PROLEG/PYTHEN and Legal2LogicICL**, rather than a binary “argumentation frameworks versus proof assistants.”
6. Make the strongest residual claim integration-specific: the paper's distinctive object is the **traceability contract across Argdown attack → Lean theorem → `#print axioms` assumption ledger → independent legal assessment → defeat synthesis → forensic translation**, particularly in Brazilian civil procedure.

## 9. Bounded negative frontier

After the searches above, no pre-cutoff work was located that combines all of the following in one legal workflow:

1. Argdown as the source-level attack/support representation;
2. a Lean theorem corresponding to each material attack;
3. `#print axioms` used as an explicit per-theorem ledger of legal/factual dependencies;
4. successful compilation treated only as a **necessary** condition;
5. a separate legal analyst reviewing the adequacy/fairness/provenance of those axioms;
6. defeat synthesis cross-referenced to both formal theorem and substantive review; and
7. translation of the accepted structure back into a Brazilian forensic pleading.

That bounded negative result is the defensible novelty frontier found in this run. It is not evidence that no such work exists.

## 10. Search-result discipline

- The audit distinguishes component novelty from novelty of the combination.
- Work after each claim-specific cutoff is not called prior art.
- No later paper is treated as evidence of copying or derivation without positive evidence.
- Exact-title and exact-combination searches that returned no candidate are preserved as negative search results only.
- The C4 correction is based on primary/field-standard sources and should be treated as a correction of our own framing, not as an adversarial priority claim.
