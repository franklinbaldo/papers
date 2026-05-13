# Claim Provenance in Legal Documents: Tracking Necessary versus Contingent Assertions Across Procedural Stages

**Franklin Silveira Baldo**
Procurador do Estado de Rondônia (OAB/RO 5733)
Porto Velho, Brazil

---

## Abstract

Legal proceedings produce chains of documents — petition, reply,
judgment, appeal, appellate judgment — in which assertions from
earlier documents propagate to later ones. When a contingent
assertion (one not necessary to produce the legal effect of its
source document) is invoked in a later document as if it were a
necessary one, a reasoning error propagates silently through the
proceeding. This article introduces the necessary/contingent/pending
distinction for claims in any procedural document, not only
precedents, and demonstrates that tracking this distinction is
essential for auditable legal argument formalization. We formalize
the distinction in Lean 4 through the `Proveniencia` and `StatusClaim`
types — both including a `pendente` constructor as honest
registration of epistemic limits. The `pendente` status is not a
failure: it records that the formalizer cannot determine the status
from available material, with the consequence that theorems
depending on pending axioms carry that uncertainty transparently
through `#print axioms`. We demonstrate the distinction in the
context of the Brazilian Marilene case, identifying a claim in the
appellate judgment that derives from a contingent assertion in the
first-instance judgment regarding the servant's functional
classification, and tracing the procedural consequences of that
propagation. The framework extends the ratio/obiter distinction
beyond precedents to all procedural documents, and introduces
regressive inference as the operational workflow: starting from
the available document and inferring backward toward prior
documents.

**Keywords**: claim provenance; necessary claims; contingent claims;
legal document chains; procedural propagation; Lean 4; ratio
decidendi; obiter dictum; Brazilian civil procedure.

---

## 1. Introduction

The ratio/obiter distinction is one of the most discussed topics
in common law jurisprudence. Ratio decidendi — the holding, the
grounds necessary for the decision — binds; obiter dictum — things
said by the way — does not. The distinction is foundational to
precedent doctrine.

What the literature has not systematically developed is that the
same distinction applies to every document in a proceeding, not
only to judicial opinions treated as precedents. A petition has
assertions necessary to its claim (the cause of action, the
facts that ground it) and contingent ones (rhetorical elaborations,
examples, background that is not part of the cause of action). A
judgment has assertions necessary to its dispositif and assertions
the judge included but could have omitted. An appellate judgment
builds on the first-instance judgment — and can build on its
contingent assertions as if they were necessary, propagating an
error that was harmless in the original document but becomes
load-bearing in the later one.

This paper formalizes the distinction and demonstrates its
consequences. Section 2 defines necessary, contingent, and pending
claims in the context of Brazilian civil procedure. Section 3
presents the Lean 4 formalization in the `Proveniencia` module.
Section 4 presents the regressive inference workflow — the
operational procedure for applying the distinction starting from
the available document. Section 5 demonstrates on the Marilene
case. Section 6 discusses implications and limits. Section 7
concludes.

---

## 2. Necessary, Contingent, and Pending Claims

### 2.1 The Definitions

**A necessary claim** in a document is one without which the legal
effect of that document would not have occurred — or would have
occurred differently. In a judgment, necessary claims are those
that sustain the dispositif: the reasoning without which the court
could not have reached the decision it reached. In a petition,
necessary claims are those that constitute the cause of action —
the legal facts from which the claim is derived.

**A contingent claim** in a document is one that is present but
was not necessary to produce the legal effect. In a judgment: the
"moreover", the "it should be noted", the observation the judge
added that the judgment could have done without. In a petition:
the rhetorical reinforcement, the historical context, the citation
that illustrates but does not ground the claim.

**A pending claim** has status that the formalizer cannot determine
from available material. The pending status is a first-class
epistemic state, not a temporary placeholder: it may remain pending
indefinitely without invalidating the formalization. The consequence
is that theorems depending on pending axioms carry that uncertainty
through `#print axioms`.

### 2.2 The Distinction Applied Document by Document

**In the initial petition**: necessary claims are the facts
constituting the cause of action (proximate cause: the legal fact;
remote cause: the underlying facts). Contingent claims are
rhetorical elaborations, illustrative examples, and argumentative
reinforcements that go beyond what the cause of action strictly
requires.

**In the reply**: necessary claims are specific denials of the
plaintiff's facts (art. 341 CPC — specific denial is required
under penalty of presumed truth), and the presentation of procedural
and substantive defenses. Contingent claims are argumentative
elaborations beyond the necessary denial and defense structure.

**In the judgment**: necessary claims are those without which the
dispositif could not be what it is. The judgment that finds for
the plaintiff necessarily holds that (a) procedural requirements
are satisfied, (b) the cause of action is established, and (c)
the legal consequence follows. Everything else — historical
elaborations, alternative reasoning, comments on matters not
strictly required by the case — is contingent.

**In the appellate judgment**: same structure as the first-instance
judgment, with the additional complication of concurring opinions.
Where multiple judges join the result but through different
reasoning, the ratio is the reasoning that commanded a majority
both on the outcome and on the grounds. Reasoning that commanded
a majority only on outcome is contingent relative to the binding
ratio.

**In a binding precedent**: the standard ratio/obiter distinction
applies. The ratio decidendi is the reasoning necessary for the
decision in the precedent. The obiter dictum is what was said by
the way. For Brazilian binding precedents under art. 927 CPC,
the "fundamentos determinantes" (art. 489, §1, V) is the
operationalization of the ratio.

### 2.3 The Propagation Problem

When a later document invokes a contingent claim from an earlier
document as if it were a necessary one, a reasoning error propagates.
The error was harmless in the original document — the contingent
claim could have been omitted without changing the outcome. But
when treated as load-bearing in the later document, its contingent
status is hidden.

This propagation has procedural consequences:

**Violation of the devolutive effect**: an appellate court that
builds on a contingent assertion of the first-instance judgment
as an autonomous ground may be deciding on matter that was not
part of the appeal's object. The devolutive effect (art. 1013
CPC) transfers to the appellate court what was impugned; what was
not impugned becomes res judicata. A contingent assertion that
was not impugned is not part of the appeal's object.

**Violation of the limits of res judicata**: art. 504 CPC establishes
that motives do not become res judicata. Treating a contingent
assertion as if it has the force of res judicata violates this
provision.

**Reasoning defect**: when the appellate court founds its decision
on a claim it treats as a necessary presupposition from the
first-instance judgment, but that claim was contingent, the
appellate court's reasoning has a foundational gap. The reasoning
defect may be curable by Embargos de Declaração if it manifests
as omission, contradiction, or obscurity.

---

## 3. Lean 4 Formalization

### 3.1 The Proveniencia and StatusClaim Types

```lean
/- Module: Proveniencia.lean -/

inductive Proveniencia
  | endogena
      -- the claim is the document's own reasoning
  | fonte_declarada : String → Proveniencia
      -- the document explicitly cites the source
  | fonte_inferida
      -- the formalizer infers a prior source document
  | confirmada_pelo_formalizador
      -- the formalizer verified against the source document
  | pendente
      -- the formalizer cannot determine provenance
      -- from available material; may remain pending indefinitely

inductive StatusClaim
  | necessaria
      -- without this claim, the legal effect would differ
  | contingente
      -- present but not necessary for the legal effect
  | pendente
      -- formalizer cannot determine from available material
```

### 3.2 Annotating Axioms with Provenance and Status

In Layer 5 (facts of the case), axioms can be annotated:

```lean
/-- Marilene was originally appointed as Especialista em Supervisão
    Escolar (Decreto 7.999/1997, posse 23.03.1998).
    Provenance: fonte_declarada (acórdão TJRO, p. 3).
    Status: necessaria (load-bearing for the court's conclusion). -/
axiom marilene_origem :
    CargoOriginariamente Marilene cargo_supervisao_escolar
```

```lean
/-- The reclassification to Professora Classe C occurred via
    LC 680/2012.
    Provenance: fonte_declarada (sentença de primeiro grau, p. 7).
    Status: pendente — the formalizer has not verified whether
    this claim was necessary to the first-instance dispositif
    or was included as contextual background. -/
axiom marilene_reenquadramento :
    Reenquadrada Marilene cargo_professora_classe_c
```

### 3.3 The Audit Effect

`#print axioms` for any theorem that depends on a pending axiom
reveals the pending status in the axiom list. This is the key
audit property: uncertainty propagates transparently.

A theorem with ten axioms, nine of which have solid documentary
grounding and one of which is pending, is a theorem whose conclusion
is conditional on the pending axiom being resolved favorably.
The Phase 3 subjective analysis receives this information and
assesses whether the pending axiom is a central load-bearing
presupposition or a peripheral one whose uncertainty does not
affect the theorem's legal force.

---

## 4. Regressive Inference Workflow

### 4.1 The Starting Point

The formalizer typically starts with the document most immediately
at issue — in Embargos de Declaração, the appellate judgment being
challenged; in Recurso Especial, the appellate judgment being
appealed.

From this document, the formalizer:

1. Classifies each claim as endogenous (the court's own reasoning)
   or exogenous (derived from prior documents).
2. For exogenous claims with declared source: records the source
   and marks as `fonte_declarada`.
3. For exogenous claims with implied source: infers the likely
   prior document and marks as `fonte_inferida`.
4. For claims where source cannot be determined: marks as `pendente`.

### 4.2 Backward Inference

For each `fonte_inferida` claim, the formalizer generates a query
to the human operator: "The judgment appears to presuppose X from
a prior document. Do you have that document? If so, what was the
status of X there — was it necessary to the dispositif or
contingent?"

The operator can:
- **Confirm with citation**: status upgrades to `confirmada_pelo_formalizador`
- **Confirm without citation**: status upgrades to `fonte_inferida`
  with operator confirmation
- **Not have the document**: status remains `pendente`
- **Report that X was contingent in the source**: status becomes
  `contingente` with source marked

### 4.3 The Pending Status as Feature

The key insight is that `pendente` is not an error state to be
resolved before proceeding. The formalization can proceed with
pending axioms; the uncertainty propagates through `#print axioms`;
the Phase 3 analysis assesses whether pending axioms are central
or peripheral; and the forensic translation can, if appropriate,
note the pending status as a point requiring verification before
the pleading is filed.

This honest registration of epistemic limits is superior to the
alternative — treating all axioms as confirmed — because it makes
the boundary of what is known explicit, both for the formalizer
and for any reviewer of the formalization.

---

## 5. Demonstration: Marilene Case

### 5.1 The Propagation in the Judgment

The TJRO appellate judgment invokes the ADI 3.772 ratio and
concludes that Marilene's functions constitute magistério for
purposes of cargo accumulation.

A claim-status analysis reveals a contingent-to-necessary
propagation:

**In the first-instance judgment**: the court noted, in passing,
that Marilene "exercises functions analogous to teaching" based
on her functional responsibilities after reclassification. This
observation was *contingent* in the first-instance judgment: the
dispositif finding in Marilene's favor could have been grounded
purely on the reclassification by LC 680/2012, without the
functional observation.

**In the appellate judgment**: the TJRO treats the first-instance
court's contingent observation about "functions analogous to
teaching" as a *necessary presupposition* — a fact established
in the lower court that the appellate court builds upon to apply
the ADI 3.772 ratio. But the observation was never load-bearing
in the lower court; it was never impugned in the appeal (because
IPERON focused on the legal qualification, not the functional
description); and it therefore should not be treated as
authoritatively established in the appellate record.

### 5.2 The Lean Annotation

```lean
/-- Claim: Marilene exercises functions analogous to teaching.
    Provenance: fonte_inferida — this appears to derive from
    a contingent observation in the first-instance judgment.
    Status: pendente — the formalizer has not verified (a) that
    the claim appears in the first-instance judgment with this
    formulation, or (b) whether it was necessary or contingent
    there.
    Note for Phase 3: this axiom is load-bearing for the ADI
    3.772 application. If it is confirmed as contingent in the
    first-instance judgment, the appellate court is treating a
    contingent prior assertion as established fact — a reasoning
    defect.  -/
axiom marilene_exerce_funcoes_pedagogicas :
    ExerceFuncoesPedagogicas Marilene
```

### 5.3 The Phase 3 Finding

The Phase 3 analysis flags this axiom as requiring verification:

> "O axioma `marilene_exerce_funcoes_pedagogicas` aparece como
> pressuposto central do raciocínio que aplica a ratio da ADI 3.772
> ao caso concreto. Sua proveniência é inferida — parece derivar
> de observação da sentença de primeiro grau —, e seu status no
> documento de origem é pendente de verificação. Antes de protocolar
> a peça, recomenda-se verificar: (a) se a sentença de primeiro
> grau efetivamente contém essa afirmação; e (b) se era fundamento
> necessário do dispositivo ou observação contingente. Se contingente,
> o v. acórdão embargado está construindo sobre premissa que não
> tinha o peso que lhe atribui — vício passível de ser suscitado
> como omissão na medida em que o acórdão não explicitou o fundamento
> da assertiva."

---

## 6. Discussion

### 6.1 Extension of the Ratio/Obiter Distinction

The literature on ratio/obiter focuses on judicial opinions treated
as precedents. The contribution of this paper is the extension:
every procedural document has necessary and contingent claims, and
tracking this distinction across the document chain is necessary
for auditable legal argument formalization.

This extension is motivated by the same theoretical consideration
that grounds the ratio/obiter distinction in precedent doctrine:
what binds (or, more generally, what carries argumentative weight)
is the reasoning that was actually load-bearing for the legal
effect, not everything that was said in the document.

### 6.2 Limits

The necessary/contingent distinction requires judgment about
counterfactuals: would the legal effect have been the same without
this claim? This counterfactual is not always determinable from
the text alone. The `pendente` constructor is the honest response
to cases where it is not.

The distinction also presupposes a theory of legal effect. For
judgments, the legal effect is the dispositif. For petitions, the
legal effect is the filing of the claim with the specified cause
of action. These are clear. For intermediate documents (manifestations,
expert reports, amicus briefs), the "legal effect" is less clear,
and the necessary/contingent distinction may be harder to apply.

---

## 7. Conclusion

We introduced the necessary/contingent/pending distinction for
claims in any procedural document, formalized it in Lean 4 through
the `Proveniencia` and `StatusClaim` types, and demonstrated its
application in the Marilene case where a contingent assertion in
the first-instance judgment was invoked as a load-bearing
presupposition in the appellate judgment.

The `pendente` constructor is the key design choice: it registers
epistemic limits honestly, propagates uncertainty through `#print
axioms`, and allows the formalization to proceed without false
confidence. The Phase 3 subjective analysis gates the transition
from pending to confirmed or refuted.

The framework extends AI&Law's treatment of claim provenance beyond
precedent doctrine to the full document chain of a proceeding.

---

## References

*[To be completed. Key citations:]*

- Cross, R. and Harris, J. W. (1991). Precedent in English Law.
  4th ed. Oxford: Clarendon Press.
- Dworkin, R. (1986). Law's Empire. Harvard UP.
- Marinoni, L. G. (2016). Precedentes Obrigatórios. 5. ed. RT.
- MacCormick, N. (1978). Legal Reasoning and Legal Theory. Oxford UP.
- Mitidiero, D. (2021). Precedentes. 4. ed. RT.

---

*Paper 3 of the "Auditable Legal Reasoning" series.*
*Implementation: franklinbaldo/skills. Version: [DATE].*
