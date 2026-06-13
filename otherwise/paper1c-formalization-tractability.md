# Vocabulary Without Procedure: A Tractability Challenge to Paper 1C's Claim Provenance Module

---

## 1. Thesis Attacked

"Categorias Processuais Civis para Formalização Computacional" (Baldo, 2025; `paper1C_categorias_processuais_formalizacao.md`) proposes to provide "sufficient descriptive precision for formalizers — human or automated — to correctly implement the categories in formal languages without distorting the underlying legal system" (Abstract). The paper covers four modules: claims (pedidos, §2), dispositions (provimentos, §3), appellate claims (pretensões recursais, §4), and claim provenance (proveniência de afirmações, §5).

This attack targets two structural commitments in the claim provenance module:

**Commitment 1 — The preprocessing claim (§5.1–5.4):** The necessary/contingent distinction, applied to each claim in each document before axiomatization, constitutes a tractable preprocessing step. Claims annotated with (provenance, status) attributes prior to formalization produce axiom sets that do not inadvertently propagate contingent claims as necessary ones. The paper presents this annotation as enabling formalizers to "correctly implement the categories ... without distorting the underlying legal system."

**Commitment 2 — The ratio extraction rule (§5.3):** For Brazilian colegiado decisions, the ratio decidendi is "the minimum denominator of the grounds of the majority votes — what all majority votes share as necessary foundation for the result. The grounds that each justice added individually but that were not shared by the others are, in relation to the acórdão as precedent, obiter."

Both commitments fail to deliver what the paper promises. Commitment 1 generates a circularity: the necessary/contingent determination requires the legal analysis the formalization system is trying to perform, not a preprocessing step that precedes it. Commitment 2 produces empty or indeterminate ratios for the class of Brazilian decisions most important for the formalization system's core use case.

A supportive defense (`yesindeed/paper1c-tractability-defense.md`) accepts the preprocessing circularity for automated systems, restricts the tractability claim to human formalizers relying on structural document signals, and proposes a candidate-ratio extension for parallel-reasoning decisions. This paper argues that each response fails to rescue the paper's operational claims as stated.

---

## 2. Faithful Reconstruction

The strongest form of the paper's claim provenance argument, integrating the original case and the defense, runs as follows.

Computational formalization of legal arguments requires selecting claims from prior documents for use as axioms. A claim drawn from a precedent and elevated to axiomatic status carries its full logical weight in the formalization. If that claim was actually *contingent* in the precedent — present in the reasoning but not load-bearing for the legal effect — then its subsequent treatment as an axiom builds on an unstable foundation. The formalization produces valid-looking theorems that do not correspond to what the precedent actually established. The paper's response is the (provenance, status) annotation scheme. Before formalizing any claim as an axiom, the formalizer determines where the claim comes from (provenance) and whether it was necessary or contingent in its origin document (status). Claims annotated as (declarada, necessária) carry high epistemic weight; claims annotated as (inferida, pendente) require verification before load-bearing use. The annotation scheme makes the epistemic hierarchy of the formalization explicit and auditable.

The ratio extraction rule is offered as a determinate, algorithmically-formulated alternative to contested theoretical debates about ratio in civilian systems: identify the grounds each majority justice treats as necessary for the result; take their intersection; that intersection is the ratio. The procedure has a clear output in principle and reduces formalizer discretion.

The supportive defense strengthens this case in three directions. For preprocessing tractability: Brazilian procedural writing employs a systematic set of locutions for contingency — "Ainda que assim não fosse...", "Mesmo que se admitisse...", "Ad argumentandum tantum..." in sentenças and acórdãos; "Subsidiariamente, caso se entenda que..." in petições iniciais; vote-to-ementa structural relationships in colegiado decisions. A trained practitioner identifies these signals through structural reading before engaging the merits. For the majority of Brazilian procedural documents, necessity/contingency can be annotated through structural reading, making preprocessing tractable for human formalizers. The "pendente" category correctly handles the non-tractable class without overclaiming tractability for it.

For the vocabulary characterization: quality-assurance records (making the epistemic status of every axiom auditable), error-detection protocols (cross-document propagation checks once annotation is in place), and coordination infrastructure across formalizers are operational contributions the taxonomy enables at the system level, beyond the naming function "vocabulary" suggests.

For the ratio extraction failure: following Mitidiero's convergent/parallel distinction, fragmented-majority decisions can receive candidate ratios — clusters of majority votes sharing necessary grounds, each marked with support, epistemic status, and scope — rather than null output from the unextended rule.

---

## 3. The Attack

### 3.1 The Necessary/Contingent Determination Requires the Output It Purports to Enable

The paper's criterion for necessity is functional: "a claim is necessary in a document if, without it, the legal effect of the act would not occur or would be substantially different" (§5.2). For sentença foundations: "the foundation without which the dispositivo would not stand is necessary. Alternative foundations — 'even if this were not so, it would also follow that...' — are contingent."

This criterion correctly identifies what necessity means. The problem is that determining whether a specific foundation is necessary for a specific dispositivo requires knowing whether the dispositivo could have been reached on other available grounds. That determination is a product of legal analysis — the analysis that identifies which of the decision's argumentative threads the issuing court treated as load-bearing. It is not a preprocessing step that can be completed before the analysis runs; it is a central output of the analysis itself.

A concrete illustration from reclamação proceedings. The STF grants a reclamação against an inferior-court acórdão that departed from a súmula. The STF's reclamação acórdão contains two independent argumentative threads: (a) the inferior court failed to demonstrate that its cited factual differences track any feature of the súmula's ratio, so the departure demonstration was structurally inadequate; and (b) even if the demonstration were formally adequate, the identified distinctions would not change the outcome because the súmula's underlying rationale applies equally to the inferior court's case. The reclamação is granted under either argument standing alone.

Is thread (a) necessary or contingent in the STF's acórdão? Under the paper's criterion: necessary if the dispositivo would not occur or would be substantially different without it; contingent if thread (b) alone would have produced the same dispositivo.

Determining the answer requires resolving which thread the STF actually treated as the ratio — as opposed to which thread was offered as reinforcement. This is the formalization system's core analytical task for this decision: identifying the ratio of the STF's reclamação judgment. The claim provenance annotation ("is thread (a) necessary?") cannot be completed before the formalization determines the ratio; it is completed only by determining the ratio. The preprocessing claim inverts the operational dependency.

The paper's annotation scheme has a release valve: the "pendente" status, for cases where provenance or necessity cannot be determined. For the reclamação example above, "pendente" may be the honest answer. But "pendente" is an acknowledgment that the determination was not made — not a tractable preprocessing step. For load-bearing claims in contested proceedings — the claims that matter most for a formalization system's downstream accuracy — "pendente" may be the honest but operationally useless answer precisely because the determination requires the analysis the system is supposed to perform.

**The structural-signal response does not resolve the hard case.** The supportive defense argues that Brazilian procedural writing employs systematic locutions for contingency — "Ainda que assim não fosse...", "Subsidiariamente..." — that allow practitioners to identify alternative foundations structurally, without merits engagement. This argument is accurate for the class of cases it describes: when a court explicitly marks a thread with an alternative-foundation locution, a practitioner can identify that thread as contingent through surface reading.

The adversarial hard case is not this class. The hard case is precisely the document in which neither thread is marked as subordinate — where both argumentative threads are stated in the declarative mode, each presented as a primary ground for the result. The reclamação acórdão in the example above says (paraphrased): "[Ground A: the departure demonstration was structurally inadequate.] [Ground B: the cited distinctions would not change the outcome regardless.]" Neither ground is prefaced with "ainda que" or any alternative-foundation signal. The reader who wishes to annotate these claims cannot determine which is necessary from document structure; she must determine which the STF treated as the load-bearing ground of the decision.

The defense concedes this directly in §3.1: "These signals are not exhaustive — the 'pendente' category handles cases where they are absent." The concession confirms the adversarial claim: for cases without explicit markers, the preprocessing scheme cannot be completed before the legal analysis. The structural-signal argument limits the scope of the circularity to the unmarked-parallel-threads class; it does not eliminate it.

A further difficulty: the easy-case tractability the defense establishes does not demonstrate preprocessing value where value is needed. Practitioners who read Brazilian procedural documents well enough to correctly identify "ainda que" constructions as alternative-foundation markers are practitioners who already manage the annotation task without a formal taxonomy. The scheme's value was supposed to lie in systematizing the process for cases that are genuinely difficult — complex constitutional adjudications, reclamação acórdãos with multiple grounds, STF plenary decisions. These are precisely the cases for which the structural-signal argument fails by the defense's own admission.

### 3.2 The Propagation Mechanism Is Identified Before It Can Be Identified

The paper's propagation analysis (§5.5) identifies two failure modes: propagation-by-omission (a party fails to contest a contingent claim in a subsequent document) and propagation-by-active-incorporation (a subsequent decision treats a prior contingent claim as "as established by the court below"). Both are correctly identified as sources of downstream formalization error.

The practical consequence the paper draws is that a recorrente who demonstrates that an acórdão rests on a claim that was contingent in the first-instance sentença can raise an argument about infra petita reasoning or violation of the devolutive effect. The recorrente identifies and challenges the propagation error.

But this practical consequence reveals the sequencing problem. The recorrente can raise the argument only after having done the legal analysis that determines (a) the claim was contingent in the prior document and (b) the subsequent document improperly elevated it to necessary status. That analysis is the substance of the appellate argument; the taxonomy provides a vocabulary for articulating it, not a procedure for performing it.

For a computational formalization system to implement the propagation check, it would need to:
1. Determine which claims were necessary vs. contingent in each prior document in the chain.
2. Identify when a subsequent document treats a prior contingent claim as established.

Step 1 requires the legal analysis that the annotation scheme was supposed to organize. The scheme provides a notation for step 1's outputs; it is not an algorithm for producing those outputs. A system that cannot independently perform step 1 cannot detect propagation errors; it can only record, after a human has determined necessity, which claims were contingent.

The paper conflates having a vocabulary for describing propagation errors with having a procedure for detecting them. These are different contributions with different computational implications.

### 3.3 The Ratio Extraction Rule Fails for Fragmented Majority Decisions; the Candidate-Ratio Extension Does Not Escape the Same Problem

The minimum-denominator rule is precise and implementable in principle. Its structural weakness is the class of decisions where the intersection of majority votes' necessary grounds is empty or trivially thin.

Brazilian superior courts — particularly the STF in plenary sessions on constitutional questions — regularly produce acórdãos where justices file individual votes that reach the same operative result through substantially different foundations. Consider a stylized but representative pattern: the STF reviews the constitutionality of a legislative measure by an eight-to-three vote. Among the eight votes in the majority: three ground their votes on the constitutional principle of legal certainty; two on the democratic legitimacy of the legislative choice; two on the proportionality of the measure under the administrative-regulatory interpretation of the constitution; one on an interpretive presumption of legislative constitutionality that the other seven do not invoke. There is no single ground that all eight majority votes treat as necessary for the result.

Under the minimum-denominator rule, this decision has no substantive ratio decidendi. The intersection of eight distinct sets of necessary grounds — where no single ground appears in all eight — is empty. The rule's output is a binding precedent without any binding legal ground: the measure was upheld, by whom, with no identified ratio. Future inferior courts applying the precedent have nothing to apply; they know the result but not the reasoning that justifies or limits it.

This is not a peripheral failure case. The STF's most contested and consequential decisions on constitutional questions — tax constitutionality, fundamental rights interpretation, federalism — are precisely those where justices bring distinct constitutional frameworks to the same question, producing fragmented majority reasoning. The minimum-denominator rule systematically fails for the class of STF decisions that generates most of the binding precedent the formalization system would need to process.

The Brazilian literature engages this problem directly. Mitidiero distinguishes "convergent reasoning" decisions (where majority justices share substantial foundational grounds) from "parallel reasoning" decisions (where majority justices reach the same result through incompatible or independent foundations), and argues that the two require different ratio-extraction approaches. Macêdo identifies the minimum-denominator approach as producing unusable results for parallel-reasoning decisions and proposes reconstruction methods that identify the best candidate ratio from fragmented votes. The paper's rule, applied mechanically, produces the pathological output Mitidiero and Macêdo describe — the empty-ratio result — without acknowledging that this is the characteristic output for a substantial portion of the STF's constitutional jurisprudence.

**The candidate-ratio extension requires the same vote-level necessity determination and is not in the paper.** The supportive defense proposes extending the minimum-denominator rule for parallel-reasoning decisions: where the intersection of majority grounds is empty, construct candidate ratios by clustering majority votes sharing common necessary grounds, marking each with support, epistemic status, and scope.

The extension is a genuine advance over the unextended rule. Mitidiero's framework is engaged; the null-output pathology is addressed; and the defense correctly observes that inferior courts already apply something like this informal reconstruction. The adversarial paper accepts the extension as technically coherent.

Two difficulties remain.

The first is structural. The candidate-ratio framework presupposes a vote-level necessity determination: the formalizer must identify, within each individual justice's vote, which grounds that justice treated as necessary for the result. The clustering step follows from this determination. But the preprocessing circularity from §3.1 applies at the vote level: a justice's individual vote in a contested constitutional case may itself contain multiple argumentative threads, presented without explicit subordination signals, each independently contributing to that justice's conclusion. Determining which thread was load-bearing for that justice's vote requires reading the vote as a legal argument and asking which ground was doing the work — which is the same legal-analytical judgment the document-level preprocessing circularity describes. The candidate-ratio framework decomposes the document-level problem into vote-level subproblems, but the subproblems inherit the same structure.

The defense responds that cross-referencing individual votes against the ementa is a structural operation that permits this determination. This misidentifies what the cross-referencing accomplishes. Ementa cross-referencing checks whether a justice's stated grounds are structurally consistent with the ementa's consolidated position — it is a consistency check. It does not identify, within a justice's vote that is consistent with the ementa, which of that justice's multiple argumentative threads were necessary for that consistency. A justice may have written three independent lines of argument each supporting the consolidated result; cross-referencing against the ementa confirms all three are consistent with it and does not discriminate among them. The vote-level necessity determination requires the same analytical judgment the document-level determination requires.

The second difficulty is about the paper's current claim. The adversarial attack targets Paper 1C's §5.3 as written: the minimum-denominator rule without qualification, without acknowledgment of fragmented-majority decisions as a challenge class, without specification of what the formalizer should do when the denominator is empty. The extension is a proposal from the defense paper. A defense paper can establish that an extension is available and technically coherent; it cannot retroactively correct the supported paper's text. SC3 requires the paper to incorporate a specified extension that produces non-empty, practically useful ratios for fragmented-majority decisions — not merely that such an extension has been proposed in a separate filing. The extension remains to be incorporated into Paper 1C's §5.3.

### 3.4 The Paper's Disclaimer Does Not Immunize the Tractability Problem

The paper explicitly disclaims dogmatic innovation: "This is not a paper of innovative dogmatic contribution ... it is a paper of systematic mapping" (§1). This disclaimer addresses one class of objection — that the paper's categories diverge from settled doctrine — but not the class raised here.

The tractability problem is not about whether the paper's categories are correct. The claim provenance categories are correctly described: necessary and contingent claims are real distinctions, provenance attributes are a genuine taxonomy, propagation is a real pathological mechanism. The problem is that having correct categories does not make those categories computationally tractable as a preprocessing step. Describing what to determine ("which claims are necessary?") is different from providing a procedure for determining it. The paper provides the former and presents it as the latter.

The disclaimer that the paper targets "sufficient descriptive precision" reinforces this point rather than answering it. Descriptive precision at the conceptual level does not imply tractability at the operational level. The paper's explicit goal — enabling formalizers to "correctly implement the categories in formal languages without distorting the underlying legal system" — is an operational claim. Meeting it requires not only that the categories be correctly described but that applying them to actual Brazilian court documents be tractable. The tractability argument challenges this operational claim, not the descriptive precision of the categories themselves.

---

## 4. Anticipated Reply and Why It Does Not Suffice

### 4.1 The Human-Formalizer Response

The paper targets both "human" and "automated" formalizers. The defense accepts the circularity for automated systems and restricts the tractability claim to human formalizers relying on structural signals. For automated systems, the defense redirects: the taxonomy's three operational contributions — quality-assurance records, error-detection protocols, and coordination infrastructure — establish a system-level value that exceeds mere vocabulary.

The structural-signal argument does not suffice for the reasons in §3.1: the signals cover explicitly marked alternative foundations, not the competing-unmarked-threads class that constitutes the preprocessing scheme's hard case. The defense's own concession that "pendente" handles the signal-absent class confirms that the hard case is unresolved. The easy-case tractability the defense establishes — cases where practitioners read "ainda que" constructions structurally — is tractability for cases that practitioners can already handle without formal annotation infrastructure.

The operational-contributions argument does not suffice for two reasons.

First, the three contributions are conditional on annotation accuracy. A quality-assurance record that marks a contingent claim as (declarada, necessária) provides false confidence rather than genuine assurance. The QA function requires that annotations correctly reflect the necessity status they claim to record. For the hard cases — where necessity cannot be determined from structural reading — annotations are either "pendente" (error-detection cannot run on incomplete annotations) or wrong (QA produces a misleading certainty signal). The defense's three contributions presuppose a correctly annotated artifact; but the preprocessing circularity challenges whether correct annotation can precede the analysis for the cases that drive the system's value.

Second, the three contributions are properties of structured annotation generally, not of the (provenance × status) taxonomy's specific categories. Any standardized annotation scheme — one marking claims as contested or uncontested, as backed by cited authority or not, as relied upon by the court or mentioned in passing — produces auditable quality-assurance records, enables cross-document propagation checks, and supports multi-formalizer coordination. The defense establishes that structured annotation has these operational properties; it does not establish that the (provenance × status) taxonomy's specific categories (necessary/contingent × declarada/inferida/pendente) provide them distinctively. If any well-structured annotation vocabulary achieves these functions equally well, then what the defense has established is that structured annotation generally has these benefits — which is true but does not rescue the paper's specific taxonomy against SC2. SC2's path remains open: acknowledge that the taxonomy provides a standardized vocabulary for recording analysis outputs, with operational benefits achievable through structured annotation generally, and revise the Abstract's "human or automated" preprocessing claim accordingly.

### 4.2 The Incremental-Progress Response

The paper might respond that requiring complete, tractable determination of claim provenance for all claims sets an impossibly high bar. Legal formalization proceeds incrementally: high-confidence (declarada, necessária) claims anchor the model; uncertain (inferida, pendente) regions are progressively resolved. The taxonomy supports this incremental process by making explicit what is known and what is not.

This response correctly captures how formalization work actually proceeds in practice. The practical value of marking epistemic status explicitly — knowing which parts of the model are solid and which are uncertain — is real and non-trivial.

The response does not rescue Commitment 1. The paper presents the (provenance, status) annotation as a preprocessing step that *enables* correct implementation. If the hardest cases — which include the most legally significant claims in complex decisions — cannot be determined without performing the legal analysis that is the formalization's main work, the annotation scheme is not a preprocessing step. It is a notation system for the outputs of the analysis once completed. This is a smaller but still useful contribution; the problem is that the paper presents it as a larger one. An honest statement of the contribution would say: the taxonomy provides vocabulary for recording the provenance and necessity status of claims after the relevant legal analysis has been performed, and this recording serves quality-assurance and auditability functions. That formulation does not claim preprocessing tractability; it correctly characterizes the taxonomy as vocabulary.

### 4.3 The "Contestation Tracks Necessity" Response and the Candidate-Ratio Extension

On the ratio extraction failure for fragmented decisions (§3.3), the defense proposes the candidate-ratio extension: for parallel-reasoning decisions where the intersection of majority grounds is empty, construct candidate ratios from clusters of votes sharing necessary grounds. The defense acknowledges the adversarial paper's §3.3 directly and accepts that the minimum-denominator rule requires extension for parallel-reasoning decisions.

The adversarial reply is in §3.3. The vote-level necessity determination faces the same circularity structure as the document-level determination. Cross-referencing individual votes against the ementa is a consistency check, not a necessity-identification procedure within each vote. The extension decomposes the problem without resolving it. And the extension is a proposal in the defense paper, not a claim in Paper 1C's §5.3: the paper's current text presents the minimum-denominator rule without qualification, without acknowledgment of the fragmented-majority failure class.

The defense's correct observations — that inferior courts already informally reconstruct from individual grounds, that the extension follows directly from Mitidiero's framework — confirm that the extension is available and its normative basis is established. These confirm SC3's path: incorporate the extension into §5.3 with the Mitidiero framework engaged. They do not establish that the paper's current claim is sound.

---

## 5. Scope of the Attack

This attack targets:

- **The claim provenance module's tractability claim** (§5): The necessary/contingent distinction and the (provenance, status) annotation scheme cannot function as a general preprocessing step independent of the legal analysis the formalization system is trying to perform. The defense has narrowed the scope of this attack — for the class of documents with explicit alternative-foundation locutions, structural signals do permit human-formalizer annotation before full merits engagement. The remaining scope: (a) the competing-unmarked-threads class, which is the most operationally significant failure class and for which the defense concedes "pendente" is the honest answer; (b) automated formalizers, for which the defense accepts the circularity in full; (c) the claim that the taxonomy's operational contributions (QA, error-detection, coordination) are specific to the (provenance × status) categories rather than properties of structured annotation generally.

- **The ratio extraction rule for colegiado decisions** (§5.3): The minimum-denominator rule produces empty or indeterminate ratios for STF plenary decisions with fragmented majority reasoning. The candidate-ratio extension proposed in the supportive defense requires the same vote-level necessity determination that the minimum-denominator rule requires, and is not incorporated into Paper 1C's §5.3 as written.

This attack does not contest:

- The value of the pedidos and provimentos taxonomies (§§2–3) as reference material for formalizers. The categorization of cumulated, alternative, subsidiary, successive, and prejudicial claims against the CPC 2015 structure is correct and useful. The composition rules for multi-claim dispositivos are accurately stated.

- The appellate claims module (§4): the extensão/profundidade distinction in the devolutive effect is correctly mapped.

- The paper's identification of contingent-claim propagation as a genuine pathological mechanism in Brazilian litigation (§5.5). This observation is correct and non-trivial. Practitioners who can identify propagation-by-omission and propagation-by-active-incorporation in actual cases gain a sharper attack vector. The taxonomy is useful as vocabulary for naming what they have already identified through legal analysis.

- The paper's goal of providing systematic vocabulary for formalization work. The attack is that the taxonomy is presented as computationally more powerful than it is: as a general tractable preprocessing step rather than as a vocabulary for expert-analyzed output in the easy case and post-analysis recording in the hard case.

- The defense's structural-signal argument for the explicitly-marked class: for documents with "ainda que" and "subsidiariamente" constructions, human formalizers can annotate necessity/contingency structurally before full merits engagement. This limited tractability claim survives.

- The candidate-ratio extension as technically coherent and normatively grounded in Mitidiero's framework. The adversarial attack on this point is that (a) the extension does not escape the vote-level necessity circularity, and (b) it is not in the paper. The attack does not contest the extension's logical coherence or desirability.

---

## 6. Surrender Conditions

The attack would not hold, or would hold only partially, under the following conditions.

1. **A procedure for the competing-unmarked-threads case.** The defense has established structural-signal tractability for the explicitly-marked class. SC1's operative scope is now the class the defense concedes to "pendente": documents with two or more argumentative threads presented without explicit subordination signals. If there exists an operational procedure — independent of the formalization system's main legal analysis — that determines necessity for this class, the circularity is resolved for the cases where it bites. The "pendente" status category does not meet this condition; it marks cases where the determination failed.

2. **Restricted scope: vocabulary, not preprocessing, with honest Abstract revision.** If the paper is recharacterized as providing a vocabulary for recording the outputs of legal analysis — with preprocessing tractability qualified to the explicitly-marked class for human formalizers, and post-analysis recording for the hard class and for automated systems — SC2 is satisfied at the cost of revising the Abstract's scope. The defense has taken a step in this direction by accepting the circularity for automated systems; the full SC2 path requires the Abstract's "human or automated" specification to be revised to reflect the conditional scope. The three operational contributions (QA, error-detection, coordination) are then attributed accurately as benefits of structured annotation generally, achievable by this taxonomy among others.

3. **The candidate-ratio extension incorporated into §5.3, with the vote-level circularity addressed.** SC3 now requires two things: (a) incorporation of the extension into Paper 1C's §5.3 as a specified rule for the parallel-reasoning case, with Mitidiero's convergent/parallel distinction engaged; and (b) specification of how the vote-level necessity determination — identifying which grounds in each justice's individual vote were load-bearing — can be performed structurally or procedurally without the legal analysis the §3.1 circularity identifies at the document level. The defense has established the extension's technical coherence; it has not specified how the vote-level circularity is resolved.

4. **Empirical evidence of reliable interrater agreement on necessary/contingent classification.** The defense has restricted the tractability claim to the explicitly-marked class. Interrater agreement data is now most valuable at two points: (a) for documents with structural markers — do trained practitioners reliably agree on necessity/contingency annotation from surface reading, without prior joint legal analysis of the underlying question? High agreement here would confirm the defense's scope-qualified claim. (b) For documents without markers (the "pendente" class) — what rate of agreement do trained practitioners achieve? High disagreement would confirm that necessity determination in this class depends on the practitioner's substantive legal analysis rather than on structural reading, supporting the adversarial characterization of "pendente" as honest incompleteness rather than tractable preprocessing. The interrater evidence, when produced, would allow the adversarial claim's scope to be calibrated against the structural-signal defense's scope claim rather than remaining at a structural impasse.

---

## References

Baldo, F. S. (2025). Categorias Processuais Civis para Formalização Computacional: Pedidos, Provimentos, Pretensões Recursais e Proveniência de Afirmações no CPC 2015. `paper1C_categorias_processuais_formalizacao.md` (this repository).

`yesindeed/paper1c-tractability-defense.md` — "Document Structure and Candidate Ratios: A Defense of Paper 1C's Claim Provenance Module" (supportive paper, this repository).

BRASIL. Lei nº 13.105, de 16 de março de 2015 (Código de Processo Civil). Arts. 141, 322, 324, 325, 326, 327, 485, 487, 489, §1º, 492, 504, 1.013, 1.022.

DIDIER JR., F.; CUNHA, L. C. da. *Curso de direito processual civil*. Vol. 3. 16. ed. Salvador: JusPodivm, 2019.

MACÊDO, L. B. de. *Precedentes judiciais e o direito processual civil*. 3. ed. Salvador: JusPodivm, 2019.

MARINONI, L. G. *Precedentes obrigatórios*. 5. ed. São Paulo: Revista dos Tribunais, 2016.

MITIDIERO, D. *Cortes superiores e cortes supremas: do controle à interpretação, da jurisprudência ao precedente*. 3. ed. São Paulo: Revista dos Tribunais, 2017.
