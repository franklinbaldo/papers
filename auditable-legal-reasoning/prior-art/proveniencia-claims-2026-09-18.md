---
type: "Audit Report"
title: "Claim Provenance — necessary/contingent/pending procedural claims prior-art audit — 2026-09-18"
description: "Claim-specific temporal audit of necessary/contingent/pending claim status, cross-document procedural provenance, contingent-to-load-bearing propagation, pending uncertainty, and regressive inference in proveniencia_claims.md."
tags: [proveniencia, prior-art, legal-reasoning, argumentation, provenance, procedural-law, lean, auditability]
timestamp: 2026-09-18T16:57:00-04:00
---

# Claim Provenance — necessary/contingent/pending procedural claims prior-art audit — 2026-09-18

> **Status:** first claim-specific temporal prior-art audit of [`proveniencia_claims.md`](../../proveniencia_claims.md). This record narrows the paper's originality boundary. It does not establish exhaustive novelty, patent novelty, causal dependence, copying, or priority beyond the public record and searches described here.

## 1. Claims audited

The paper mixes a doctrinal observation, a provenance model, an epistemic-state convention, and an operational workflow. They are audited separately:

- **C1 — cross-document necessity status:** the ratio/obiter idea can be generalized operationally so that claims in petitions, defenses, judgments, appeals, and precedents are classified by whether they are necessary/load-bearing or contingent relative to that document's legal effect;
- **C2 — claim provenance across a procedural chain:** a claim reused downstream should retain an auditable record of where it came from and how it was used in earlier documents;
- **C3 — contingent-to-load-bearing propagation:** a claim may be harmlessly contingent in its source document yet become load-bearing when reused later, and that transition should be explicitly detected rather than silently inheriting argumentative weight;
- **C4 — `pendente` as first-class epistemic state:** inability to determine provenance or necessity from available material should be represented explicitly and allowed to propagate into downstream formal conclusions rather than being silently coerced to confirmed/false;
- **C5 — regressive inference workflow:** the audit starts from the document currently under review and traces exogenous claims backward toward prior documents and their source status;
- **C6 — full computational conjunction:** source-document necessity status + claim provenance + explicit pending state + backward procedural tracing + proof-dependency visibility in a Lean-oriented legal formalization.

The audit distinguishes novelty of the **combination** from novelty of the components.

## 2. Temporal reconstruction of our claims

### 2.1 Relevant cutoff: 2026-05-13 03:20:27 UTC

The current file timestamp and the repository creation date are not used.

The earliest public GitHub state located that already contains the substantive claims C1–C6 is commit [`3de41c63f429ab2f4f9a1844825be2e9bd78dbf4`](https://github.com/franklinbaldo/papers/commit/3de41c63f429ab2f4f9a1844825be2e9bd78dbf4), authored and committed at **2026-05-13 03:20:27 UTC**. That import added the then-named `paper3_proveniencia_claims.md`; the file already stated, in substance:

- the necessary/contingent/pending distinction for claims in procedural documents;
- the contingent-to-necessary propagation problem;
- `Proveniencia` and `StatusClaim` with a `pendente` constructor;
- uncertainty carried through proof dependencies;
- backward/regressive inference from the document under review toward prior source documents.

The later rename to `proveniencia_claims.md`, OKF conversion, and Mermaid additions did not create those claims.

### 2.2 Same-cutoff internal scope control

The same commit also added `paper1C_categorias_processuais_formalizacao.md`, which already described the necessary/contingent distinction and propagation across successive procedural documents while expressly stating that the article **did not aim at innovative dogmatic contribution**, but at descriptive precision for computational formalization.

That simultaneous public record matters epistemically: the defensible originality reading of `proveniencia_claims.md` is primarily the **operational/computational conjunction**, not a claim that procedural doctrine had never distinguished essential from non-essential allegations or grounds.

## 3. Search protocol

Searches were claim-led and date-sensitive. Sources included arXiv version records and full text, W3C provenance standards, Inference Web/PML material, argumentation and legal-AI literature, legal-procedure sources, Springer/DOI records, Oxford Academic, and targeted exact-title/exact-author searches.

Representative queries included:

- `claim provenance legal documents necessary contingent pending`
- `necessary contingent claims procedural documents legal`
- `ultimate facts evidentiary facts pleadings necessary allegations`
- `fatos essenciais fatos simples causa de pedir processo civil`
- `ratio obiter necessary grounds counterfactual legal`
- `Proof Markup Language theorem prover axioms provenance justification`
- `Inference Web sources assumptions conclusions provenance`
- `W3C PROV derivation entity source provenance`
- `Wigmore chart legal evidence propositions inference`
- `Carneades legal argument proof standards argument graph`
- `Legal Knowledge Interchange Format arguments cases rules`
- `argumentation labelling accepted rejected undecided`
- `why provenance trace output back to source`
- `legal claim auditing per-claim source provenance`
- `procedural state transitions legal knowledge graph`
- exact-title searches for `Claim Provenance in Legal Documents: Tracking Necessary versus Contingent Assertions Across Procedural Stages`;
- exact-author/title searches combining `Franklin Silveira Baldo`, `Claim Provenance`, `contingent-to-necessary`, and `regressive inference`.

Negative searches are bounded search results, not proof of non-existence.

## 4. Pre-cutoff findings

### 4.1 Pleading doctrine already distinguishes essential/load-bearing allegations from secondary/evidentiary allegations

**Work/doctrine:** longstanding pleading doctrine on **ultimate / essential / principal facts** versus evidentiary, simple, or secondary facts.

Examples located before our cutoff include:

- Philippine Supreme Court jurisprudence, including *Remitere v. Vda. de Yulo* as quoted in G.R. No. 89114 (1991), defining an essential fact by a counterfactual deletion test: a fact is essential if striking it would leave the cause of action insufficient: <https://lawphil.net/judjuris/juri1991/dec1991/gr_89114_1991.html>;
- Brazilian civil-procedure doctrine, including José Miguel Garcia Medina's *Curso de Direito Processual Civil Moderno* (2018 edition), distinguishing `fatos principais/essenciais/jurígenos` from `fatos simples/secundários`, with only the former necessary to identify the claim: <https://www.jusbrasil.com.br/doutrina/secao/capitulo-iii-processo-de-conhecimento-procedimento-comum-curso-de-direito-processual-civil-moderno-ed-2018/3467451856>.

**Compared claim:** C1.

**Classification:** `partial_prior_art`.

**Why:** the paper cannot treat the idea that pleadings contain load-bearing versus non-load-bearing factual assertions as new. That distinction is old and operationally close to the paper's necessity test. What was not located in these sources is the paper's single taxonomy applied uniformly across the entire procedural-document chain.

### 4.2 Wigmorean analysis and argument mapping predate claim-dependency graphs in law by a century

**Work:** John Henry Wigmore's chart method for legal evidence, developed in the early twentieth century; later formalized and revived in legal evidence analysis.

A recent comparative paper describes Wigmore charts, Bayesian networks, and chain event graphs as alternative graphical methods for representing propositions, evidence, testimony, and facts in a legal case: A. Philip Dawid et al., **“A comparison of graphical methods in the case of the murder of Meredith Kercher”**, arXiv:2403.16628, v1 **2024-03-25 11:17:56 UTC**, <https://arxiv.org/abs/2403.16628>.

**Compared claims:** C2, C3.

**Classification:** `adjacent_prior_work`.

**Why:** legal claim/evidence dependency structure is not new. Wigmorean analysis does not, however, appear to encode the specific source-document status transition “contingent there → load-bearing here.”

### 4.3 Database `why`/`where` provenance already formalizes backward tracing from an output to contributing inputs

**Work:** Peter Buneman, Sanjeev Khanna, Wang-Chiew Tan, **“Why and Where: A Characterization of Data Provenance.”** ICDT 2001, DOI 10.1007/3-540-44503-X_20.

- proceedings/publication: **2001**; Springer records first online **2001-10-12**;
- <https://doi.org/10.1007/3-540-44503-X_20>.

The paper distinguishes `why` provenance — source data that influenced the existence of an output — from `where` provenance — source locations from which output data was extracted.

**Compared claims:** generic component of C2 and C5.

**Classification:** `prior_art` for backward provenance/lineage as a general computational operation; `adjacent_prior_work` for the legal-procedural specialization.

**Consequence:** `regressive inference` cannot be defended as a new general idea merely because it starts at an output and traces backward. Its potentially distinctive part is the **legal procedural target and the status being traced**.

### 4.4 Proof Markup Language / Inference Web directly anticipates provenance of axioms, sources, and derivation steps

**Work:** Paulo Pinheiro da Silva, Deborah L. McGuinness, Richard Fikes, **“A Proof Markup Language for Semantic Web Services.”** *Information Systems* 31(4–5), 381–395, 2006, DOI 10.1016/j.is.2005.02.003; preceded by Inference Web work from 2003 onward.

- journal publication: **June–July 2006**;
- <https://doi.org/10.1016/j.is.2005.02.003>;
- project documentation: <https://inference-web.org/>.

PML/Inference Web represents where knowledge came from, the inference steps used to derive conclusions, sources, assumptions, and justifications. It was explicitly designed around explanations of automated theorem-prover results and later split explanation representation into provenance, justification, and trust modules.

**Compared claims:** C2, broad component of C4, C5.

**Classification:** `prior_art` for machine-readable provenance of premises/axioms and derivation paths; `partial_prior_art` for C6.

**Consequence:** claim-level source provenance and exposing dependency chains of formal conclusions are established prior art. The narrower question is what *legal status* is attached to those source claims and how that status changes across procedural reuse.

### 4.5 Carneades and LKIF already formalize legal arguments, proof standards, cases, and claim status

**Works:** Thomas F. Gordon, **“Visualizing Carneades argument graphs.”** *Law, Probability and Risk* 6(1–4), 109–117, published **2007-10-10**, DOI 10.1093/lpr/mgm026; Thomas F. Gordon, **“Constructing legal arguments with rules in the Legal Knowledge Interchange Format (LKIF).”** 2008, DOI 10.1007/978-3-540-85569-9_11.

- <https://doi.org/10.1093/lpr/mgm026>
- <https://doi.org/10.1007/978-3-540-85569-9_11>

Carneades represents legal argument graphs and evaluates whether claims meet proof standards given evidence and counterarguments. LKIF was designed to represent rules, ontologies, cases, and justificatory legal arguments and can be used with Carneades to construct/evaluate legal case arguments.

**Compared claims:** C1–C4.

**Classification:** `partial_prior_art`.

**Why:** formal legal claim graphs, legal-case arguments, varying proof standards, and computable claim evaluation clearly predate our cutoff. They do not appear to anticipate the exact source-document necessity provenance and contingent-to-load-bearing transition audited here.

### 4.6 Explicit `undecided` / assumption-dependent status is established prior art

**Works:**

- Johan de Kleer, **“An assumption-based TMS.”** *Artificial Intelligence* 28(2), 127–162, **March 1986**, DOI 10.1016/0004-3702(86)90080-9;
- Phan Minh Dung, **“On the acceptability of arguments and its fundamental role in nonmonotonic reasoning, logic programming and n-person games.”** *Artificial Intelligence* 77(2), 321–357, **September 1995**, DOI 10.1016/0004-3702(94)00041-X;
- later argument-labelling literature explicitly uses `in`, `out`, and `undec`, with `undec` meaning that one abstains from accepting or rejecting the argument.

**Compared claim:** C4.

**Classification:** `partial_prior_art`.

**Why:** first-class unresolved status and explicit dependency on assumptions are old computational ideas. The `pendente` constructor may still be a useful legal-engineering choice, but the generic epistemic pattern is not new.

### 4.7 W3C PROV standardizes derivation and provenance independently of the legal domain

**Work:** W3C Provenance Working Group, **PROV-DM / PROV family**, W3C Recommendation **2013-04-30**; Proposed Recommendation text dated 2013-03-12.

- <https://www.w3.org/TR/prov-dm/>
- <https://www.w3.org/TR/prov-overview/>.

PROV models entities, activities, agents, derivations, responsibility, and provenance bundles, with explicit extensibility for domain-specific vocabularies.

**Compared claims:** C2, C5.

**Classification:** `prior_art` for generic derivation/provenance modeling; `adjacent_prior_work` for legal necessity status.

### 4.8 Compliance-by-Construction Argument Graphs is a close pre-cutoff convergence on auditable claim/evidence provenance

**Work:** Mahyar T. Moghaddam, **“Compliance-by-Construction Argument Graphs: Using Generative AI to Produce Evidence-Linked Formal Arguments for Certification-Grade Accountability.”** arXiv:2604.04103.

- arXiv v1: **2026-04-05 12:55:16 UTC**;
- <https://arxiv.org/abs/2604.04103>.

The work treats each AI-assisted step as a claim supported by verifiable evidence, uses a typed argument graph, validates explicit reasoning constraints, and records provenance in a W3C-PROV-aligned ledger.

**Compared claims:** C2, C4, broad auditability part of C6.

**Classification:** `partial_prior_art`.

**Why:** this is only ~38 days before our cutoff and materially anticipates the broad “typed claims + evidence + validation + provenance ledger for auditable high-stakes reasoning” architecture. It does not encode the paper's specific necessary/contingent status across procedural documents.

## 5. Post-cutoff work

### 5.1 Falkor-IRAC appeared about 31 hours after our cutoff

**Work:** Joy Bose, **“Falkor-IRAC: Graph-Constrained Generation for Verified Legal Reasoning in Indian Judicial AI.”** arXiv:2605.14665.

- arXiv v1: **2026-05-14 10:19:23 UTC**;
- our cutoff: **2026-05-13 03:20:27 UTC**;
- delta: approximately **30 h 59 min** after our verified public claim;
- <https://arxiv.org/abs/2605.14665>.

Falkor-IRAC represents judgments as structured IRAC nodes enriched with **procedural state transitions, precedent relationships, and statutory references**, and accepts an LLM-generated legal answer only when a supporting path can be traced through the graph.

**Compared claims:** C2, C5, broad graph-verification portion of C6.

**Classification:** `later_overlap`.

**Why:** it is posterior and therefore cannot be prior art against our May 13 cutoff. It is a striking near-simultaneous convergence on procedural-state graphs and traceable reasoning paths, but it does not disclose the necessary/contingent source-status mechanism. Full-text citation inspection was not available through the source surface used in this run, so dependency/citation status is not classified.

### 5.2 GANDR later makes per-claim legal audit traces a first-class artifact without locating our citation

**Work:** Chen Qian, Yimeng Wang, Yu Chen, Lingfei Wu, Andreas Stathopoulos, **“GANDR: Claim Auditing for Verifiable Legal Answer Generation.”** arXiv:2609.10293.

- arXiv v1: **2026-09-09 15:08:09 UTC**;
- <https://arxiv.org/abs/2609.10293>.

GANDR decomposes legal answers into claims, audits each claim against its cited source, and emits a **per-claim audit trace** on every round. Its full arXiv HTML was searched for `Baldo` and `Claim Provenance`; neither string was located.

**Compared claims:** claim-level audit/provenance component of C2 and C6.

**Classification:** `later_non_citing`.

**Caution:** this records only three verifiable facts — later publication, material overlap at the per-claim audit level, and absence of our citation in the searchable full text. It does **not** establish copying, derivation, awareness, bad faith, or causal dependence. GANDR's architecture and evaluation are also substantially different and more developed as an empirical legal-answer-generation system.

## 6. Revised originality boundary

### 6.1 Claims that are not defensibly novel in broad form

After this search, the following broad ideas are occupied by prior work:

- differentiating essential/load-bearing from secondary allegations in pleadings;
- representing legal propositions and evidential/inferential dependencies as graphs;
- machine-readable source/axiom/derivation provenance;
- tracing a result backward to contributing source material;
- representing unresolved/undecided or assumption-dependent states explicitly;
- typed claim/evidence graphs with validation and provenance ledgers in auditable high-stakes systems.

### 6.2 Narrow combination not located before the cutoff

No pre-cutoff source located in this run implemented the following **combined mechanism**:

1. every procedural document is treated as its own argumentative context;
2. each reused claim retains provenance to the source document;
3. the source claim is classified by whether it was load-bearing for the legal effect of that source document;
4. a later use is separately classified by whether it is load-bearing in the later document;
5. the audit specifically flags the transition **contingent in source → load-bearing downstream**;
6. unresolved source/status questions remain explicit as `pending` rather than being silently resolved;
7. the workflow begins from the currently available procedural document and recursively traces claims backward;
8. formal theorem dependencies expose which conclusions remain conditional on unresolved source/status assertions.

**Classification of the full conjunction:** `partial_prior_art`.

This classification is intentionally conservative: many components have clear antecedents, but the exact legal-procedural composition was not located after the bounded searches above. The correct wording is **“no material antecedent implementing the full conjunction was located in these searches before the 2026-05-13 cutoff”**, not “we were the first.”

### 6.3 Consequence for the paper's framing

The strongest defensible contribution is therefore not “provenance for claims,” “pending status,” “backward tracing,” or even “necessary versus non-necessary statements” individually. It is the **status-sensitive cross-document procedural provenance audit**, especially the explicit detection of a claim whose argumentative role changes from non-load-bearing in its source to load-bearing downstream.

This also reconciles the standalone paper with the same-cutoff companion `paper1C_categorias_processuais_formalizacao.md`, which expressly disclaimed innovative dogmatic contribution.

## 7. Negative and unresolved searches

This run did not locate, before the cutoff:

- a paper using the exact phrase `contingent-to-necessary` for procedural-claim propagation;
- a formal legal model that attaches a source-document load-bearing/contingent status to a proposition and compares that status with the proposition's downstream role;
- a pre-cutoff system combining that transition test with a first-class unresolved provenance state and Lean-style theorem-dependency audit;
- the exact title of our paper in indexed scholarly sources outside our GitHub record.

These are search outcomes, not proofs of absence.

## 8. Classification summary

| Candidate | First verified public date | Claim(s) | Classification |
| --- | --- | --- | --- |
| Ultimate/essential vs evidentiary/simple facts doctrine | longstanding; cited sources pre-2026 | C1 | `partial_prior_art` |
| Wigmorean legal evidence mapping | early 20th c. | C2–C3 | `adjacent_prior_work` |
| Buneman–Khanna–Tan, why/where provenance | 2001 | C2, C5 | `prior_art` (generic provenance) |
| PML / Inference Web | 2003–2006 | C2, C4, C5 | `prior_art` / `partial_prior_art` |
| Carneades / LKIF | 2007–2008 | C1–C4 | `partial_prior_art` |
| ATMS / abstract-argumentation undecided status | 1986–1995+ | C4 | `partial_prior_art` |
| W3C PROV | 2013 | C2, C5 | `prior_art` (generic provenance) |
| Compliance-by-Construction Argument Graphs | 2026-04-05 | C2, C4, C6 | `partial_prior_art` |
| Falkor-IRAC | 2026-05-14 10:19:23 UTC | C2, C5, C6 | `later_overlap` |
| GANDR | 2026-09-09 15:08:09 UTC | C2, C6 | `later_non_citing` |

## 9. Epistemic conclusion

The audit materially narrows the novelty boundary. The broad ingredients are heavily anticipated by procedural doctrine, provenance systems, argumentation frameworks, and recent auditable-AI architectures. The most specific surviving research claim is the **cross-document change-of-role audit**: preserving the source document's load-bearing status for a claim and detecting when that same claim becomes load-bearing downstream, while unresolved provenance/status remains explicit and visible in formal dependencies.

No causal inference is made from the post-cutoff Falkor-IRAC or GANDR overlaps.
