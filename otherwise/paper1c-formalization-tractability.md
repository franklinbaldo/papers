# Vocabulary Without Procedure: A Tractability Challenge to Paper 1C's Claim Provenance Module

---

## 1. Thesis Attacked

"Categorias Processuais Civis para Formalização Computacional" (Baldo, 2025; `paper1C_categorias_processuais_formalizacao.md`) proposes to provide "sufficient descriptive precision for formalizers — human or automated — to correctly implement the categories in formal languages without distorting the underlying legal system" (Abstract). The paper covers four modules: claims (pedidos, §2), dispositions (provimentos, §3), appellate claims (pretensões recursais, §4), and claim provenance (proveniência de afirmações, §5).

This attack targets two structural commitments in the claim provenance module:

**Commitment 1 — The preprocessing claim (§5.1–5.4):** The necessary/contingent distinction, applied to each claim in each document before axiomatization, constitutes a tractable preprocessing step. Claims annotated with (provenance, status) attributes prior to formalization produce axiom sets that do not inadvertently propagate contingent claims as necessary ones. The paper presents this annotation as enabling formalizers to "correctly implement the categories ... without distorting the underlying legal system."

**Commitment 2 — The ratio extraction rule (§5.3):** For Brazilian colegiado decisions, the ratio decidendi is "the minimum denominator of the grounds of the majority votes — what all majority votes share as necessary foundation for the result. The grounds that each justice added individually but that were not shared by the others are, in relation to the acórdão as precedent, obiter."

Both commitments fail to deliver what the paper promises. Commitment 1 generates a circularity: the necessary/contingent determination requires the legal analysis the formalization system is trying to perform, not a preprocessing step that precedes it. Commitment 2 produces empty or indeterminate ratios for the class of Brazilian decisions most important for the formalization system's core use case.

---

## 2. Faithful Reconstruction

The strongest form of the paper's claim provenance argument runs as follows.

Computational formalization of legal arguments requires selecting claims from prior documents for use as axioms. A claim drawn from a precedent and elevated to axiomatic status carries its full logical weight in the formalization. If that claim was actually *contingent* in the precedent — present in the reasoning but not load-bearing for the legal effect — then its subsequent treatment as an axiom builds on an unstable foundation. The formalization produces valid-looking theorems that do not correspond to what the precedent actually established. The practitioner or the system then fails to identify the right attack vector: challenging the axiomatic claim as unnecessary, which would collapse the downstream conclusions.

The paper's response is the (provenance, status) annotation scheme. Before formalizing any claim as an axiom, the formalizer determines where the claim comes from (provenance) and whether it was necessary or contingent in its origin document (status). Claims annotated as (declarada, necessária) carry high epistemic weight; claims annotated as (inferida, pendente) require verification before load-bearing use. The annotation scheme makes the epistemic hierarchy of the formalization explicit and auditable.

This scheme is coherent and identifies a genuine problem. Contingent claims do propagate through procedural document chains. The propagation-by-omission mechanism — a party fails to contest a contingent claim in a subsequent document, allowing it to acquire uncontested status — is a real pathological pattern in Brazilian litigation. The propagation-by-active-incorporation mechanism — a subsequent decision treats a prior contingent claim as "as established by the court below" — is a genuine source of downstream formalization error that Brazilian appellate practitioners encounter.

The ratio extraction rule is offered as a determinate, algorithmically-formulated alternative to the contested theoretical debates about ratio in civilian systems. Rather than requiring formalizers to adjudicate academic disputes, the rule specifies a procedure: identify the grounds each majority justice treats as necessary for the result; take their intersection; that intersection is the ratio. The procedure has a clear output in principle and reduces formalizer discretion.

---

## 3. The Attack

### 3.1 The Necessary/Contingent Determination Requires the Output It Purports to Enable

The paper's criterion for necessity is functional: "a claim is necessary in a document if, without it, the legal effect of the act would not occur or would be substantially different" (§5.2). For sentença foundations: "the foundation without which the dispositivo would not stand is necessary. Alternative foundations — 'even if this were not so, it would also follow that...' — are contingent."

This criterion correctly identifies what necessity means. The problem is that determining whether a specific foundation is necessary for a specific dispositivo requires knowing whether the dispositivo could have been reached on other available grounds. That determination is a product of legal analysis — the analysis that identifies which of the decision's argumentative threads the issuing court treated as load-bearing. It is not a preprocessing step that can be completed before the analysis runs; it is a central output of the analysis itself.

A concrete illustration from reclamação proceedings. The STF grants a reclamação against an inferior-court acórdão that departed from a súmula. The STF's reclamação acórdão contains two independent argumentative threads: (a) the inferior court failed to demonstrate that its cited factual differences track any feature of the súmula's ratio, so the departure demonstration was structurally inadequate; and (b) even if the demonstration were formally adequate, the identified distinctions would not change the outcome because the súmula's underlying rationale applies equally to the inferior court's case. The reclamação is granted under either argument standing alone.

Is thread (a) necessary or contingent in the STF's acórdão? Under the paper's criterion: necessary if the dispositivo would not occur or would be substantially different without it; contingent if thread (b) alone would have produced the same dispositivo.

Determining the answer requires resolving which thread the STF actually treated as the ratio — as opposed to which thread was offered as reinforcement. This is the formalization system's core analytical task for this decision: identifying the ratio of the STF's reclamação judgment. The claim provenance annotation ("is thread (a) necessary?") cannot be completed before the formalization determines the ratio; it is completed only by determining the ratio. The preprocessing claim inverts the operational dependency.

The paper's annotation scheme has a release valve: the "pendente" status, for cases where provenance or necessity cannot be determined. For the reclamação example above, "pendente" may be the honest answer. But "pendente" is an acknowledgment that the determination was not made — not a tractable preprocessing step. For load-bearing claims in contested proceedings — the claims that matter most for a formalization system's downstream accuracy — "pendente" may be the honest but operationally useless answer precisely because the determination requires the analysis the system is supposed to perform.

The paper does not acknowledge this dependency. It presents the (provenance, status) annotation as preceding formalization, enabling formalizers to "build with transparent epistemic marking." In practice, the marking can only be applied after the legal analysis has identified which claims are load-bearing — which is the formalization's output, not its input.

### 3.2 The Propagation Mechanism Is Identified Before It Can Be Identified

The paper's propagation analysis (§5.5) identifies two failure modes: propagation-by-omission (a party fails to contest a contingent claim in a subsequent document) and propagation-by-active-incorporation (a subsequent decision treats a prior contingent claim as "as established by the court below"). Both are correctly identified as sources of downstream formalization error.

The practical consequence the paper draws is that a recorrente who demonstrates that an acórdão rests on a claim that was contingent in the first-instance sentença can raise an argument about infra petita reasoning or violation of the devolutive effect. The recorrente identifies and challenges the propagation error.

But this practical consequence reveals the sequencing problem. The recorrente can raise the argument only after having done the legal analysis that determines (a) the claim was contingent in the prior document and (b) the subsequent document improperly elevated it to necessary status. That analysis is the substance of the appellate argument; the taxonomy provides a vocabulary for articulating it, not a procedure for performing it.

For a computational formalization system to implement the propagation check, it would need to:
1. Determine which claims were necessary vs. contingent in each prior document in the chain.
2. Identify when a subsequent document treats a prior contingent claim as established.

Step 1 requires the legal analysis that the annotation scheme was supposed to organize. The scheme provides a notation for step 1's outputs; it is not an algorithm for producing those outputs. A system that cannot independently perform step 1 cannot detect propagation errors; it can only record, after a human has determined necessity, which claims were contingent.

The paper conflates having a vocabulary for describing propagation errors with having a procedure for detecting them. These are different contributions with different computational implications.

### 3.3 The Ratio Extraction Rule Fails for Fragmented Majority Decisions

The minimum-denominator rule is precise and implementable in principle. Its structural weakness is the class of decisions where the intersection of majority votes' necessary grounds is empty or trivially thin.

Brazilian superior courts — particularly the STF in plenary sessions on constitutional questions — regularly produce acórdãos where justices file individual votes that reach the same operative result through substantially different foundations. Consider a stylized but representative pattern: the STF reviews the constitutionality of a legislative measure by an eight-to-three vote. Among the eight votes in the majority: three ground their votes on the constitutional principle of legal certainty; two on the democratic legitimacy of the legislative choice; two on the proportionality of the measure under the administrative-regulatory interpretation of the constitution; one on an interpretive presumption of legislative constitutionality that the other seven do not invoke. There is no single ground that all eight majority votes treat as necessary for the result.

Under the minimum-denominator rule, this decision has no substantive ratio decidendi. The intersection of eight distinct sets of necessary grounds — where no single ground appears in all eight — is empty. The rule's output is a binding precedent without any binding legal ground: the measure was upheld, by whom, with no identified ratio. Future inferior courts applying the precedent have nothing to apply; they know the result but not the reasoning that justifies or limits it.

This is not a peripheral failure case. The STF's most contested and consequential decisions on constitutional questions — tax constitutionality, fundamental rights interpretation, federalism — are precisely those where justices bring distinct constitutional frameworks to the same question, producing fragmented majority reasoning. The minimum-denominator rule systematically fails for the class of STF decisions that generates most of the binding precedent the formalization system would need to process.

The Brazilian literature engages this problem directly. Mitidiero distinguishes "convergent reasoning" decisions (where majority justices share substantial foundational grounds) from "parallel reasoning" decisions (where majority justices reach the same result through incompatible or independent foundations), and argues that the two require different ratio-extraction approaches. Macêdo identifies the minimum-denominator approach as producing unusable results for parallel-reasoning decisions and proposes reconstruction methods that identify the best candidate ratio from fragmented votes. The paper's rule, applied mechanically, produces the pathological output Mitidiero and Macêdo describe — the empty-ratio result — without acknowledging that this is the characteristic output for a substantial portion of the STF's constitutional jurisprudence.

The paper's §5.3 presents the minimum-denominator rule as uncontroversially correct: "the ratio is the minimum common denominator." This formulation does not acknowledge the contested Brazilian doctrine on parallel-reasoning decisions, does not identify fragmented-majority cases as a challenge class, and does not specify what the formalizer should do when the denominator is empty. For a paper that aims at "sufficient descriptive precision for formalizers," the omission of the most practically significant failure class for the rule it specifies is a material gap.

### 3.4 The Paper's Disclaimer Does Not Immunize the Tractability Problem

The paper explicitly disclaims dogmatic innovation: "This is not a paper of innovative dogmatic contribution ... it is a paper of systematic mapping" (§1). This disclaimer addresses one class of objection — that the paper's categories diverge from settled doctrine — but not the class raised here.

The tractability problem is not about whether the paper's categories are correct. The claim provenance categories are correctly described: necessary and contingent claims are real distinctions, provenance attributes are a genuine taxonomy, propagation is a real pathological mechanism. The problem is that having correct categories does not make those categories computationally tractable as a preprocessing step. Describing what to determine ("which claims are necessary?") is different from providing a procedure for determining it. The paper provides the former and presents it as the latter.

The disclaimer that the paper targets "sufficient descriptive precision" reinforces this point rather than answering it. Descriptive precision at the conceptual level does not imply tractability at the operational level. The paper's explicit goal — enabling formalizers to "correctly implement the categories in formal languages without distorting the underlying legal system" — is an operational claim. Meeting it requires not only that the categories be correctly described but that applying them to actual Brazilian court documents be tractable. The tractability argument challenges this operational claim, not the descriptive precision of the categories themselves.

---

## 4. Anticipated Reply and Why It Does Not Suffice

### 4.1 The Human-Formalizer Response

The paper targets both "human" and "automated" formalizers. For human formalizers, the circularity in §3.1 is not a circularity in the usual sense: a skilled Brazilian proceduralist who reads the STF reclamação acórdão and identifies which argumentative thread is the load-bearing ratio can then annotate the claims accordingly. The taxonomy provides vocabulary for making the analysis explicit and auditable; it does not pretend to replace the legal analysis.

This response identifies the taxonomy's strongest use case. Human formalizers who have completed the legal analysis do benefit from a structured annotation scheme. The paper's categories provide a shared vocabulary that makes the epistemic structure of formalization work legible to others.

The response does not suffice for two reasons. First, the paper's explicit scope includes automated formalizers: "human or automated." For automated systems, the legal analysis that human formalizers perform before annotation is not available. An automated system applying the annotation scheme faces the circularity in §3.1 directly: it cannot determine claim necessity without the legal analysis that is the formalization's main task. Second, for human formalizers, the "pendente" category cannot serve as a resting state for load-bearing claims. A formalization with many "pendente" status assignments on its key axioms has not benefited from the preprocessing scheme; it has documented its own incompleteness. The practical value of a preprocessing scheme that produces "pendente" for the hardest and most consequential cases is limited to its use as an incomplete-work marker, not as a quality assurance mechanism.

### 4.2 The Incremental-Progress Response

The paper might respond that requiring complete, tractable determination of claim provenance for all claims sets an impossibly high bar. Legal formalization proceeds incrementally: high-confidence (declarada, necessária) claims anchor the model; uncertain (inferida, pendente) regions are progressively resolved. The taxonomy supports this incremental process by making explicit what is known and what is not.

This response correctly captures how formalization work actually proceeds in practice. The practical value of marking epistemic status explicitly — knowing which parts of the model are solid and which are uncertain — is real and non-trivial.

The response does not rescue Commitment 1. The paper presents the (provenance, status) annotation as a preprocessing step that *enables* correct implementation. If the hardest cases — which include the most legally significant claims in complex decisions — cannot be determined without performing the legal analysis that is the formalization's main work, the annotation scheme is not a preprocessing step. It is a notation system for the outputs of the analysis once completed. This is a smaller but still useful contribution; the problem is that the paper presents it as a larger one. An honest statement of the contribution would say: the taxonomy provides vocabulary for recording the provenance and necessity status of claims after the relevant legal analysis has been performed, and this recording serves quality-assurance and auditability functions. That formulation does not claim preprocessing tractability; it correctly characterizes the taxonomy as vocabulary.

### 4.3 The "Contestation Tracks Necessity" Response

On the ratio extraction failure for fragmented decisions (§3.3), the paper might respond that inferior courts applying an STF decision with an empty minimum-denominator ratio do not face a formalizable void. They observe which way the STF decided and apply that decision as a directional signal, supplemented by the individual grounds they find most persuasive. The formalization system should represent this as multiple candidate ratios with different probative weights, not as a single ratio.

This response correctly diagnoses what inferior courts actually do in practice. It does not satisfy the rule's own terms. The minimum-denominator rule specifies a single output: the intersection of majority grounds. When that intersection is empty, the rule does not produce multiple weighted candidates; it produces a null output. A rule that outputs null for the most contested class of STF decisions is not "sufficient descriptive precision for formalizers"; it is a rule that requires supplementation by a different method — precisely the Mitidiero/Macêdo reconstruction methods the paper does not engage — when it encounters its characteristic failure case.

---

## 5. Scope of the Attack

This attack targets:

- **The claim provenance module's tractability claim** (§5): The necessary/contingent distinction and the (provenance, status) annotation scheme cannot function as a preprocessing step independent of the legal analysis the formalization system is trying to perform. The taxonomy is correctly described but mischaracterized as operational preprocessing rather than post-analysis vocabulary.

- **The ratio extraction rule for colegiado decisions** (§5.3): The minimum-denominator rule produces empty or indeterminate ratios for STF plenary decisions with fragmented majority reasoning — the class of decisions most central to the formalization system's core use case.

This attack does not contest:

- The value of the pedidos and provimentos taxonomies (§§2–3) as reference material for formalizers. The categorization of cumulated, alternative, subsidiary, successive, and prejudicial claims against the CPC 2015 structure is correct and useful. The composition rules for multi-claim dispositivos are accurately stated.

- The appellate claims module (§4): the extensão/profundidade distinction in the devolutive effect is correctly mapped; the connection between pretensão recursal and the five legitimate exits from Paper 1B is structurally accurate.

- The paper's identification of contingent-claim propagation as a genuine pathological mechanism in Brazilian litigation (§5.5). This observation is correct and non-trivial. Practitioners who can identify propagation-by-omission and propagation-by-active-incorporation in actual cases gain a sharper attack vector. The taxonomy is useful as vocabulary for naming what they have already identified through legal analysis.

- The paper's goal of providing systematic vocabulary for formalization work. The attack is that the taxonomy is presented as computationally more powerful than it is: as a tractable preprocessing step rather than as a vocabulary for expert-analyzed output.

---

## 6. Surrender Conditions

The attack would not hold, or would hold only partially, under the following conditions.

1. **A document-structure algorithm for necessary/contingent determination.** If there exists an operational procedure that determines claim necessity from document structure alone — without requiring the legal analysis that is the formalization's main work — the circularity in §3.1 is resolved. The algorithm would need to be specified precisely enough to apply to cases like the competing-argumentative-threads example in §3.1 (two independent threads each sufficient for the result). The "pendente" status category does not meet this condition; it marks cases where the determination failed, not cases where the procedure succeeded.

2. **Restricted scope: vocabulary, not preprocessing.** If the paper is recharacterized as providing a vocabulary for recording the outputs of legal analysis rather than a preprocessing step that precedes the analysis, the tractability attack is misdirected. The paper would then claim: "here are the categories human formalizers should use to annotate claims after they have determined which are load-bearing through legal analysis." This recharacterization is available but substantially weakens the paper's operational claim. The Abstract's specification that formalizers — "human or automated" — can "correctly implement the categories" reads as a specification claim, not a vocabulary claim.

3. **A working ratio extraction procedure for fragmented colegiado decisions.** If the paper specifies an extension to the minimum-denominator rule that produces non-empty, practically useful ratios for STF plenary decisions with fragmented majorities — engaging Mitidiero's convergent/parallel-reasoning distinction or Macêdo's reconstruction methods — the §3.3 attack's reach is limited to whatever residual failure cases remain. The paper's current formulation does not acknowledge fragmented-majority decisions as a challenge class.

4. **Empirical evidence of reliable interrater agreement on necessary/contingent classification.** If practitioners and researchers applying the taxonomy to representative Brazilian court decisions demonstrate high interrater agreement on which claims are necessary vs. contingent — without requiring joint prior legal analysis — this would provide evidence that the determination is less analytically demanding than §3.1 claims. High interrater disagreement would confirm the observer-dependence problem. This evidence would be especially valuable for the class of decisions with competing argumentative threads, where the preprocessing circularity is sharpest.

---

## References

Baldo, F. S. (2025). Categorias Processuais Civis para Formalização Computacional: Pedidos, Provimentos, Pretensões Recursais e Proveniência de Afirmações no CPC 2015. `paper1C_categorias_processuais_formalizacao.md` (this repository).

BRASIL. Lei nº 13.105, de 16 de março de 2015 (Código de Processo Civil). Arts. 141, 322, 324, 325, 326, 327, 485, 487, 489, §1º, 492, 504, 1.013, 1.022.

DIDIER JR., F.; CUNHA, L. C. da. *Curso de direito processual civil*. Vol. 3. 16. ed. Salvador: JusPodivm, 2019.

MACÊDO, L. B. de. *Precedentes judiciais e o direito processual civil*. 3. ed. Salvador: JusPodivm, 2019.

MARINONI, L. G. *Precedentes obrigatórios*. 5. ed. São Paulo: Revista dos Tribunais, 2016.

MITIDIERO, D. *Cortes superiores e cortes supremas: do controle à interpretação, da jurisprudência ao precedente*. 3. ed. São Paulo: Revista dos Tribunais, 2017.
