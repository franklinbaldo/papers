# Auditing Legal Reasoning with Lean 4: A Six-Phase Pipeline for Brazilian Civil Procedure Using Argdown and Formal Verification

**Franklin Silveira Baldo**
Procurador do Estado de Rondônia (OAB/RO 5733)
Porto Velho, Brazil

---

## Abstract

We present a six-phase methodology for auditing procedural legal
arguments in Brazilian civil procedure using Lean 4 as a formal
verification nucleus, with Argdown as the upstream argument
representation language. The pipeline — Argdown decomposition,
Lean formalization, iterative subjective legal analysis, resolutive
synthesis, and forensic translation — addresses a gap in the
AI&Law literature: existing frameworks either use argumentation
frameworks with acyclicity-based verification (TAIR, Bowers and
Ludäscher 2025) or treat legal reasoning as purely defeasible and
outside the scope of formal proof assistants. We argue that
deductive verification via compilation is more appropriate than
structural acyclicity verification for legal argumentation,
because legal systems have inherent Kelsenian circular structure
— the Grundnorm, precedent chains, constitutional self-reference —
that acyclicity requirements cannot accommodate. Lean 4's `#print
axioms` command provides the key audit mechanism: every theorem
exposes the complete set of postulated hypotheses, making the
dependency structure of legal arguments transparent and reproducible.
We demonstrate the pipeline on a real Brazilian state court case
(Apelação 7003561-54.2024.8.22.0010, TJRO), producing five verified
theorems that formalize procedural defects in the court's treatment
of binding STF precedent. We also introduce two dogmatic
contributions on Embargos de Declaração under the CPC 2015 that
the pipeline canonicalizes: infringement effects as automatic
consequence of granting the motion, and five legitimate responses
to binding precedent. The pipeline is implemented in the open-source
skill `franklinbaldo/skills`.

**Keywords**: legal reasoning; formal verification; Lean 4; Argdown;
Brazilian civil procedure; binding precedent; argumentation;
AI&Law; CPC 2015.

---

## 1. Introduction

Formal verification of legal reasoning has been a goal of AI&Law
research since the field's inception [CITE Bench-Capon, Prakken].
Two broad approaches have developed: argumentation frameworks, which
model legal reasoning as defeasible inference over structured attack
and support relations [CITE Dung 1995, Prakken ASPIC+, Carneades];
and formal proof assistants, which verify deductive inferences in
type-checked logical systems [CITE Coq, Isabelle, Lean].

The dominant view in recent AI&Law literature is that legal reasoning
is inherently defeasible and therefore belongs to argumentation
frameworks, with proof assistants reserved for mathematical
subproblems [CITE TAIR 2025]. This article challenges that view
with a concrete argument: deductive verification via compilation
is *more* appropriate than structural acyclicity-based verification
for legal argumentation, because legal systems have inherent
circular structure that acyclicity cannot accommodate.

The argument draws on Kelsen's theory of the Grundnorm: any legal
system has a foundational hypothesis — the constitutional order,
the validity of the constitution — that is itself not derivable
from a higher norm. This circularity is a feature, not a bug: it
is what makes a legal system a system, capable of self-reference
and self-amendment. Argumentation frameworks that require acyclicity
as a structural integrity condition must cut this chain at some
arbitrary point. Lean 4's axiom-based approach does not: it
explicitly postulates foundational assumptions and makes them
auditable via `#print axioms`. The circularity is acknowledged
and exposed, not eliminated.

**Contributions.** This paper makes four contributions:

1. **A six-phase pipeline** combining Argdown argument decomposition,
   Lean 4 formalization, iterative qualitative legal analysis,
   and forensic translation.

2. **A theoretical argument** for compilation-based verification
   over acyclicity-based verification in legal argumentation,
   grounded in Kelsenian legal theory.

3. **A modular Lean 4 library** for Brazilian civil procedure,
   implementing canonical modules for procedural claims, judgments,
   appellate claims, precedent regimes (art. 926 and 927 CPC), and
   argument provenance.

4. **Two dogmatic contributions** on Embargos de Declaração and
   the five legitimate responses to binding precedent, formalized
   as verified theorems in the library.

---

## 2. Background

### 2.1 Argumentation Frameworks

Dung's abstract argumentation frameworks (1995) model argumentation
as a directed graph where nodes are arguments and edges are attacks.
Semantics compute acceptable sets — extensions — that survive
mutual attack. Extensions under preferred, grounded, complete, and
stable semantics capture different intuitions about which arguments
win contested debates.

Bipolar Argumentation Frameworks (BAFs) [CITE Cayrol and
Lagasquie-Schiex 2005] extend Dung with support relations, allowing
arguments to reinforce as well as attack each other. ASPIC+
[CITE Prakken] provides a structured instantiation of argumentation
frameworks with explicit rules (strict and defeasible), preferences,
and argument construction. These frameworks have been extensively
applied to legal reasoning [CITE Bench-Capon, Sartor, Atkinson].

TAIR [CITE Bowers and Ludäscher, AI4EVIR@JURIX 2025] is the most
recent work combining formal verification with legal argumentation.
TAIR bifurcates: Lean 4 for mathematical subproblems requiring
absolute proof; BAFs with acyclicity verification for legal
defeasible reasoning. The "Scholar" component parses arguments
into BAF structure; the "Judge" component verifies structural
integrity including acyclicity and temporal consistency.

### 2.2 Proof Assistants in Legal Reasoning

Applications of proof assistants to legal reasoning are sparse.
Coq has been used for formalization of specific legal domains
[CITE Bourcier]. Isabelle/HOL has been applied to property rights
[CITE Lehmann]. These applications focus on deductive subproblems
within legal domains — contract validity, property transfer rules
— not on argumentation structure.

The dominant objection to proof assistants for legal reasoning is
that law is defeasible: rules have exceptions, precedents can be
overridden, competing principles must be balanced. Proof assistants
handle monotonic logic; legal reasoning is non-monotonic. Therefore,
proof assistants are inappropriate for legal reasoning.

This article challenges the objection at its root.

### 2.3 Argdown

Argdown [CITE Voigt et al. 2018+] is a Markdown-inspired markup
language for structured argumentation. Claims are marked `[Claim]`,
arguments are marked `<Argument>`, and support (`+`) and attack
(`-`) relations are expressed through indentation. The official
TypeScript parser produces JSON, Mermaid diagrams, Graphviz
visualizations, and ASPARTIX-format argumentation framework
representations. A VS Code plugin provides live preview.

Argdown is the operational successor to Toulmin-style argument
decomposition in the computational setting. Toulmin (1958)
established the vocabulary — claim, data, warrant, rebuttal — but
produced no parser and no computational tools. Argdown implements
the same intuitions with a maintained parser, active community,
and export pipeline to existing AF solvers.

---

## 3. Why Compilation Beats Acyclicity for Legal Reasoning

### 3.1 The Acyclicity Problem

TAIR's structural verification includes acyclicity as an integrity
condition: argument graphs should not contain cycles. This is
appropriate for domains where circularity represents error —
circular references in contracts, contradictory causal chains in
evidence. It is inappropriate for legal argumentation as such.

Legal systems are inherently circular at their foundations. The
Brazilian Constitution establishes procedures for constitutional
amendment; the validity of those procedures derives from the
Constitution. This is structural circularity: the system refers
to itself to ground its own validity. Kelsen's Grundnorm is the
explicit acknowledgment that every legal system has an ultimate
hypothesis — the postulate that the founding constitution is valid
— that is itself not derivable from a prior norm.

Beyond the constitutional level, precedent chains exhibit circular
structure. A binding precedent from the STF binds lower courts
because the CPC says so; the CPC is valid because it was enacted
constitutionally; the constitutional amendment process was followed
because the prior constitution established it; and so on. Every
such chain terminates in the Grundnorm — a hypothesis, not a
derivation.

An argumentation framework that requires acyclicity must cut this
chain at some point. But any cut is arbitrary: why is the STF
precedent not treated as a node in the cycle, while the
constitutional foundation is? The cut reflects the modeler's
decision, not a structural feature of the legal system.

### 3.2 Compilation as the Right Criterion

Lean 4's type-checker takes a different approach. It does not
require that the graph of dependencies be acyclic; it requires
that the type assignments be consistent. Circular dependencies are
permitted in principle (mutual inductive types, for instance);
what is prohibited is *inconsistency* — postulating both `A` and
`¬A` as axioms.

This is precisely the right criterion for legal reasoning. Legal
systems prohibit logical contradiction: a court cannot simultaneously
hold that a statute is valid and that it is void in the same case
and on the same question. Legal systems do not prohibit self-
reference or circular grounding: constitutional self-amendment is
valid; precedent chains that reach the Grundnorm are valid.

When we formalize a legal argument in Lean 4, we postulate:
- Systemic presuppositions (the constitutional order is valid, the
  CPC is in force) as axioms in the highest layer
- Norms as axiom-constructors, with citations
- Facts of the case as axioms, with citations to the record

`#print axioms` then reveals the complete dependency structure:
every theorem exposes what it presupposes. This is not proof that
the axioms are correct — it is proof that *given the axioms, the
theorem follows*. The audit value is in the transparency: any
reviewer can inspect the axiom list and judge whether the
presuppositions are warranted.

TAIR's acyclicity check tells you that the argument graph has no
cycles. `#print axioms` tells you what the argument *assumes*.
The latter is more informative for legal verification.

---

## 4. The Six-Phase Pipeline

### 4.1 Overview

```
Phase 0: Source documents (judgment, appeal, precedents)
    ↓
Phase 1: Argdown (argument decomposition and topology)
    ↓
Phase 2: Lean (formalization — LLM-formalizer)
    ↓
Phase 3: Subjective legal analysis ⇄ Phase 2 (iterative)
    ↓
Phase 4: Resolutive synthesis (defeat table with cross-references)
    ↓
Phase 5: Forensic translation (the actual legal pleading)
```

The pipeline separates identification (Phases 1–2) from resolution
(Phase 4) by interposing the subjective legal analysis (Phase 3).
This separation is the key methodological contribution: marking
defeats before Lean compiles turns verification into ritual
confirmation. The analysis gate ensures that compilation is a
necessary but not sufficient condition for marking defeat.

### 4.2 Phase 1: Argdown Decomposition

The LLM-formalizer reads the source documents and produces an
Argdown file. Each claim in the judgment is represented as a
`[Claim]` node; each argument in the judgment or in the opposing
pleading is represented as an `<Argument>` node; attack (`-`) and
support (`+`) relations reflect the argumentative structure.

Argdown annotations capture provenance and status:

```argdown
[Marilene exercises teaching functions]: 
  The TJRO's central claim.
  #necessary #judgment
  - <P1 — Omission of express exclusion>: The ADI 3.772 ratio
    expressly excludes "especialistas em educação". The voto
    transcribed this exclusion and did not engage with it.
  - <P2 — Internal contradiction>: The transcribed ratio implies
    the negation of the claim for the specific cargo.
```

Tags `#necessary`/`#contingent`/`#pending` mark the status of
each claim in its source document; tags `#judgment`/`#appeal`/
`#precedent` mark provenance.

### 4.3 Phase 2: Lean Formalization

The LLM-formalizer receives the Argdown file and source documents
and produces a Lean 4 file. The file follows the six-layer
architecture:

1. **Basic types** — `Decisao`, `Precedente`, `Caso`, `Tribunal`,
   imported from `Tipos.lean`
2. **Opaque predicates** — non-deductive legal qualifications
3. **Systemic presuppositions** — operate as `[Field K]`; not
   theses of the exercise
4. **Norms and precedents** — axiom-constructors with citations
5. **Facts of the case** — from the record, with citations
6. **Theorems** — one per attack in the Argdown

The pipeline imports the modular library (described in Section 5).
Each theorem in Layer 6 corresponds to an attack in the Argdown
file, enabling full traceability between the Argdown topology and
the Lean proof.

**Hard rule**: if a theorem does not compile, return to Phase 1
or the Argdown file for revision. Never adjust axioms to force
compilation. Failed compilation is a diagnostic, not an obstacle.

### 4.4 Phase 3: Subjective Legal Analysis (Iterative Gate)

Phase 3 is the gate between verification and resolution. The
LLM-analyst (ideally in a separate context from the LLM-formalizer,
to prevent justification of what was formalized) receives the
compiled Lean file, the Argdown, and the source documents and
produces a legal analysis in *forensic prose* — the register of
an institutional memo, not workspace jargon.

For each compiled theorem, the analysis assesses:

- **Documentary anchoring**: is the central axiom grounded in
  authoritative source in the record, or is it inference?
- **Counter-argument engagement**: does the analysis identify
  counter-arguments of equivalent force that the pleading does not
  address?
- **Reasonable formulation**: is the axiom a fair representation
  of the position the court could sustain — not a caricature the
  court would easily repudiate?

If any criterion fails: return to Phase 2 with refinement
instructions. The analysis has authority to block passage to
Phase 4. Only when all central axioms are assessed as acceptable
does the analysis issue a passage recommendation.

The analysis uses qualified hedging: "has solid grounding in...",
"it must be noted, however, that...", "requires explicit engagement
with...". This register is the right one: it reflects the actual
epistemic state, not false confidence.

### 4.5 Phase 4: Resolutive Synthesis

Phase 4 marks defeats with cross-references. Every defeat in the
synthesis table must reference: (a) the Lean theorem that formally
sustains it; and (b) the section of the Phase 3 analysis that
assessed the axiom quality. Marking without (a) is speculation;
marking without (b) treats Lean as oracle.

### 4.6 Phase 5: Forensic Translation

The forensic pleading describes the *case*, not the analytic
path. Every workspace term is eliminated: no "legitimate exits",
no "partition", no "outside the legitimate space". The pleading
uses recognized Brazilian procedural vocabulary — "aplicação
seletiva de precedente vinculante", "uso impróprio de precedente",
"omissão quanto a argumento capaz de infirmar a conclusão" — anchored
in the dispositives of the CPC.

---

## 5. The Lean 4 Library for Brazilian Civil Procedure

The pipeline is supported by a modular library implementing
canonical categories of Brazilian civil procedure. The library
is organized in topological compilation order:

```
Tipos.lean                     (Decisao, Precedente, Caso, Tribunal, ...)
    ↓
Saidas/Aplicar.lean            (AplicaCorretamente, art. 489 §1º V)
Saidas/Distinguir.lean         (DistingueCorretamente, art. 489 §1º VI)
Saidas/Superar.lean            (SuperaPlenamente, ReconheceSuperacaoExterna,
                                SuperaRacionalmente)
    ↓
Pretensoes/Pedido.lean         (Pedido, RelacaoEntrePedidos)
Pretensoes/Provimento.lean     (Provimento, MotivoExtincao, ModoHomologacao)
Pretensoes/Dispositivo.lean    (Dispositivo, resultado_agregado)
Pretensoes/Recursal.lean       (PretensaoRecursal, ViciosArt1022,
                                implicaModificacao)
Proveniencia.lean              (Proveniencia, StatusClaim — both include
                                | pendente constructor)
    ↓
art_489_cpc.lean               (CPC.Art489)
art_926_cpc.lean               (CPC.Art926 — derives 3-exit partition)
art_927_cpc.lean               (CPC.Art927 — derives 5-exit partition)
art_1022_cpc.lean              (CPC.Art1022)
art_10_cpc.lean                (CPC.Art10)
art_5_e_6_cpc.lean             (CPC.Art5E6)
```

### 5.1 The Five-Exit Partition Theorem

The central theoretical theorem of the library formalizes what
we call the five legitimate responses to binding precedent under
art. 927 CPC:

```lean
theorem saidas_legitimas_precedente_vinculante :
    ∀ (d : Decisao) (p : Precedente),
      Vinculante p →
      Fundamentada d →
      FundamentaSeEm d p ∨ DeixaDeSeguir d p →
      AplicaCorretamente d p ∨
      DistingueCorretamente d p ∨
      SuperaPlenamente d p ∨
      ReconheceSuperacaoExterna d p ∨
      SuperaRacionalmente d p
```

This theorem is *derived*, not postulated. It follows from the
axioms of `art_927_cpc.lean` that combine the trait modules. The
partition has five exits because Brazilian precedent binding is
*rational*, not *hierarchical*: a lower court can confront a
binding STF precedent by identifying error in the ratio — but must
do so expressly, with qualified argumentative burden. This is
`SuperaRacionalmente`, the fourth exit, which requires `ApontaErroExpresso`
and `DemonstraIrracionalidadeOuSuperacaoNormativa`.

The `apenas_tribunal_fonte_supera_plenamente` axiom captures the
one asymmetry: *full* overruling (robust overruling with effect
modulation) is reserved for the source court. The rational
supersession exit (`SuperaRacionalmente`) remains available to
bound courts, but with higher burden.

### 5.2 Infringement as Consequence, Not Claim

The `Pretensoes/Recursal.lean` module canonicalizes the dogmatic
rule that infringement effects in Embargos de Declaração are not
an autonomous claim. There is no constructor for "embargos
infringentes" in `PretensaoRecursal`. Instead:

```lean
def implicaModificacao (vicios : List ViciosArt1022)
    (acordao : Decisao) : Prop :=
    ∃ v ∈ vicios, sanacao_de_v_modifica acordao
```

Modification is a derived predicate — a consequence of granting
the motion when the curing implies modification. This reflects
art. 1024, §3 CPC exactly.

### 5.3 The Provenance Module

The `Proveniencia.lean` module introduces `pendente` as a first-class
constructor in both `Proveniencia` and `StatusClaim`:

```lean
inductive Proveniencia
  | endogena
  | fonte_declarada : String → Proveniencia
  | fonte_inferida
  | confirmada_pelo_formalizador
  | pendente

inductive StatusClaim
  | necessaria
  | contingente
  | pendente
```

`pendente` is not a failure state; it is honest registration of
the formalizador's epistemic limit. Theorems that depend on `pendente`
axioms carry that status through `#print axioms`, making the
uncertainty explicit and auditable.

---

## 6. Case Study: Apelação 7003561-54.2024.8.22.0010

### 6.1 The Case

IPERON (Instituto de Previdência dos Servidores do Estado de
Rondônia) appealed a first-instance judgment that had recognized
the lawfulness of a public servant's cargo accumulation. The
servant, Marilene Betiol, was originally appointed as "Especialista
em Supervisão Escolar" and subsequently reclassified as "Professora
Classe C" under state law (LC 680/2012).

The TJRO 2ª Câmara Especial, in its judgment of 29 April 2026,
maintained the first-instance ruling, invoking the STF's ADI 3.772
as the binding precedent supporting its conclusion.

### 6.2 The ADI 3.772 Ratio and the Selective Application

The ADI 3.772 (STF, Rel. Min. Carlos Britto, j. 09.10.2009) ratio,
as transcribed verbatim in the TJRO judgment, reads:

> "As funções de direção, coordenação e assessoramento pedagógico
> integram a carreira do magistério, desde que exercidos, em
> estabelecimentos de ensino básico, por professores de carreira,
> **excluídos os especialistas em educação** [...]"

The TJRO transcribed the full ratio including the express exclusion
("excluídos os especialistas em educação") and then concluded that
Marilene — originally appointed as Especialista em Supervisão
Escolar — falls within the magistério category. The judgment did
not engage with the exclusion clause, did not distinguish the case
from the paradigm, did not identify any subsequent STF precedent
superseding the exclusion, and did not identify any error in the
ratio's reasoning.

This is what we term "silent partial application of binding
precedent": invoking the precedent to benefit from the favorable
portion while ignoring the express qualification in the same ratio,
without adopting any of the five legitimate responses.

### 6.3 The Five Theorems

The Lean formalization produces five theorems corresponding to the
five attacks identified in the Argdown file:

**Theorem 1** (`ataque_1_ressalva_da_ADI`): applying the ADI 3.772
ratio with the express exclusion to the fact of original appointment
as Especialista derives `¬ ProfessorDeCarreira Marilene
cargo_supervisao_escolar`. Compiles. `#print axioms` shows 8
axioms, all grounded in facts of the record or in the verbatim
ratio.

**Theorem 2** (`ataque_2_contradicao_interna`): the transcribed
premise + the sustained conclusion + the fact of original appointment
→ False. Direct modus tollens. Compiles.

**Theorem 3** (`ataque_3_aplicacao_seletiva`): uses
`fora_do_espaco_legitimo_nao_fundamentada` from `art_927_cpc.lean`.
The TJRO invoked the binding precedent and did not adopt any of
the five legitimate responses. The TJRO cannot perform full
overruling (not the source court); rational supersession requires
express error identification (not done); recognition of supersession
requires a subsequent STF precedent (none identified); distinction
requires identification of substantive difference (not done).
Therefore `¬ Fundamentada acordao_TJRO`. Compiles.

**Theorem 4** (`ataque_4_aderencia_substantiva_ausente`): the ADI
3.772 ratio was fixed in the context of special retirement
(art. 40 §5º CF); the Marilene case concerns cargo accumulation
(art. 37 XVI CF). The regimes are constitutionally distinct; the
precedent lacks substantive adherence to the case. Compiles.

**Theorem 5** (`ataque_5_omissao_TCE`): the TCE-RO Parecer Prévio
PPL-TC 00027/19, an autonomous ground invoked in the appeal, was
not engaged by the judgment. Omission under art. 489, §1, IV CPC.
Compiles.

### 6.4 The Subjective Analysis Finding

The Phase 3 analysis issued a passage recommendation after the
first iteration. The only refinement-triggering observation:
axiom `regimes_constitucionais_distintos` (Theorem 4) is a
systemic presupposition that the court could challenge by arguing
that the notion of "função de magistério" has common scope across
both regimes. The pleading was revised to address this counter-
argument explicitly in Section 6 (addressing the regime autonomy
omission). No axioms required reformulation.

---

## 7. Related Work

### 7.1 Positioning Relative to TAIR

TAIR [CITE Bowers and Ludäscher 2025] is a vision paper proposing
a framework that bifurcates: Lean for mathematical subproblems,
BAFs for legal defeasible reasoning. Our methodology is a
methodological counter-proposal on the legal side: we argue that
Lean is appropriate for legal argumentation precisely because its
compilation criterion (consistency under postulated axioms)
accommodates the Kelsenian circular structure of legal systems
that acyclicity cannot. We are not an extension of TAIR; we are
an alternative architecture for the legal-reasoning component,
with empirical demonstration on a real Brazilian case.

The key divergence: TAIR's acyclicity checks verify structural
properties of the argument graph. Our `#print axioms` audit verifies
the presupposition structure of the argument. The latter is more
informative for legal accountability: lawyers, judges, and parties
care about what an argument assumes, not about whether its
dependency graph is acyclic.

### 7.2 Positioning Relative to COURTREASONER

COURTREASONER [CITE Han et al. EMNLP 2025] found that LLM judges
of legal reasoning are "fragile and inconsistent" and misled by
rhetorically persuasive but logically invalid arguments. Our
pipeline addresses this finding structurally: the Phase 3 subjective
analysis includes a dual-axis assessment (procedural validity via
CPC criteria and argumentative persuasiveness independently), with
divergence between the two axes identifying the COURTREASONER
pathology as a diagnostic signal rather than a methodological
problem.

### 7.3 Argdown vs. Toulmin

We position Argdown as the operational successor to Toulmin (1958)
for computational argumentation. Toulmin established the vocabulary
(claim, data, warrant, rebuttal) but produced no parser and no
toolchain. Argdown implements the same intuitions with maintained
parser, active community, VS Code plugin, and export pipeline to
AF solvers. For LLM-assisted formalization, Argdown is superior:
its Markdown-like syntax is in the training distribution of all
current LLMs, its parser validates output, and its export to ASPARTIX
enables integration with PyArg and AF-XRAY when structural
visualization is useful.

---

## 8. Conclusion

We presented a six-phase pipeline for auditing legal arguments in
Brazilian civil procedure using Lean 4 as the formal verification
nucleus. The pipeline is grounded in a theoretical argument —
compilation beats acyclicity for legal reasoning because legal
systems have Kelsenian circular structure that acyclicity
requirements cannot accommodate — and demonstrated on a real case
with five verified theorems.

The modular library for Brazilian civil procedure implements
canonical categories (pedidos, provimentos, pretensões recursais,
regime de precedentes vinculantes) with provenance and status
tracking for all claims. The library canonicalizes two dogmatic
contributions: infringement effects as automatic consequence of
motion granting (not autonomous claim), and five legitimate
responses to binding precedent (reflecting the rational, not
hierarchical, character of Brazilian precedent binding).

The pipeline is open-source at `franklinbaldo/skills`. Future work
includes: extension to Recurso Especial and Recurso Extraordinário;
empirical evaluation using the Embedding-Seeded Hierarchical
Tournament Ranking method (Paper 4 of this series); and integration
with Brazilian court transparency portals for corpus-scale analysis.

---

## References

*[Full references to be completed with DOIs. Key citations:]*

- Bowers, J. and Ludäscher, B. (2025). Towards Trustworthy AI
  Results. AI4EVIR@JURIX 2025. CEUR Vol-4157.
- Cayrol, C. and Lagasquie-Schiex, M.-C. (2005). On the acceptability
  of arguments in bipolar argumentation frameworks. ECSQARU 2005.
- Dung, P. M. (1995). On the acceptability of arguments and its
  fundamental role in nonmonotonic reasoning, logic programming
  and n-person games. Artificial Intelligence 77(2), 321–357.
- Han, et al. (2025). COURTREASONER. EMNLP 2025.
- Kelsen, H. (1967). Pure Theory of Law. University of California
  Press.
- Marinoni, L. G. (2016). Precedentes obrigatórios. 5. ed. RT.
- Mitidiero, D. (2021). Precedentes: da persuasão à vinculação.
  4. ed. RT.
- Prakken, H. (2010). An abstract framework for argumentation
  with structured arguments. Argument & Computation 1(2), 93–124.
- Toulmin, S. (1958). The Uses of Argument. Cambridge UP.
- Voigt, C. et al. (2018+). Argdown. https://argdown.org

---

*Paper 2 of the "Auditable Legal Reasoning" series.
Implementation: franklinbaldo/skills. Version: [DATE].*
