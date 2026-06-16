# Document Structure and Candidate Ratios: A Defense of Paper 1C's Claim Provenance Module

---

## 1. Thesis Supported

Baldo (2025), "Categorias Processuais Civis para Formalização Computacional" (`paper1C_categorias_processuais_formalizacao.md`), makes two structural commitments in its claim provenance module (§5) that this paper defends.

**Commitment 1 (preprocessing tractability):** The necessary/contingent determination, applied to claims in Brazilian procedural documents before axiomatization, constitutes a tractable preprocessing step. The (provenance, status) annotation scheme enables formalizers to "correctly implement the categories in formal languages without distorting the underlying legal system" (Abstract).

**Commitment 2 (ratio extraction rule):** For Brazilian colegiado decisions, the ratio is "the minimum common denominator of the grounds of the majority votes — what all majority votes share as necessary foundation for the result. The grounds that each justice added individually but that were not shared by the others are, in relation to the acórdão as precedent, obiter." (§5.3)

---

## 2. What This Support Adds

**Vector:** Direct defense. This paper responds to `otherwise/paper1c-formalization-tractability.md` ("Vocabulary Without Procedure"), which attacks both commitments.

*Commitment 1 attack (preprocessing circularity):* The necessary/contingent determination requires knowing whether the dispositivo could be reached on other available grounds — which is a product of the legal analysis the formalization system is trying to perform. The annotation cannot precede the analysis; it is the analysis. The "pendente" category acknowledges failure to determine necessity rather than constituting a tractable preprocessing step. The adversarial paper further argues that easy-case tractability for explicitly-marked documents does not demonstrate preprocessing value: practitioners who can identify "ainda que" constructions already handle those cases without formal annotation infrastructure, and the scheme was supposed to add value for hard cases, which it concedes to "pendente." The adversarial paper also argues that the three operational contributions (quality-assurance records, error-detection protocols, coordination infrastructure) are properties of structured annotation generally, not of the (provenance × status) taxonomy's specific categories.

*Commitment 2 attack (fragmented-majority failure):* The minimum-denominator rule produces empty or trivially thin ratios for STF plenary decisions where majority justices reach the same result through independent foundations. The adversarial paper cites Mitidiero's convergent/parallel-reasoning distinction and Macêdo's reconstruction methods as the established doctrinal framework the paper does not engage. On the candidate-ratio extension proposed in response, the adversarial paper argues the extension requires a vote-level necessity determination that faces the same competing-unmarked-threads problem as the document-level determination, and that ementa cross-referencing is a consistency check rather than a necessity-identification procedure within individual votes.

This defense accepts: that the preprocessing circularity holds for fully automated formalizers; that the minimum-denominator rule is incomplete for parallel-reasoning decisions; and that Mitidiero's convergent/parallel distinction is the appropriate framework for extending it. This defense contests: that the preprocessing circularity applies with equal force to human formalizers relying on structural document signals; that easy-case tractability fails to demonstrate preprocessing value because the taxonomy's contribution is formal recording, not enabling initial identification; that the operational contributions are interchangeable with any structured annotation scheme; and that the vote-level circularity has the same incidence and severity as the document-level circularity.

---

## 3. The Defense

### 3.1 The Preprocessing Circularity Holds for Automated Systems; It Is Limited for Human Formalizers Using Structural Signals; and Tractability in the Easy Class Is Not Vacuous

The adversarial paper's hardest example for the preprocessing circularity is the competing-argumentative-threads case: a reclamação acórdão containing two independent argumentative threads each sufficient for the result, where the formalization system's task is identifying which is the ratio. Document structure alone cannot resolve this case without knowing which thread the STF treated as load-bearing — which is a legal-analytical judgment.

The adversarial paper's argument is strongest as an argument against automated systems. For human formalizers, the circularity is substantially narrower. Brazilian procedural writing employs a small set of systematic linguistic markers for contingency that a trained practitioner applies through structural reading before engaging the merits.

In **sentenças and acórdãos**, a distinct class of locutions signals alternative foundations: "Ainda que assim não fosse...", "Mesmo que se admitisse...", "Para além desse fundamento...", "Ad argumentandum tantum...", "Ainda que superado o argumento anterior...". These constructions are the near-universal signal for fundamento alternativo in Brazilian judicial writing. A trained practitioner identifies the "ainda que" construction as a contingency signal through structural reading before determining whether the alternative foundation is legally correct.

In **petições iniciais**, subsidiary causes of pedir are routinely prefaced with hedging locutions: "Subsidiariamente, caso se entenda que...", "Alternativamente, e sem prejuízo do acima exposto...". The distinction between the primary causa de pedir and its alternatives is structural and does not require merits analysis to identify.

In **acórdãos with concurring votes**, the standard Brazilian colegiado format separates votes by justice. A vote beginning "Acompanho o relator, acrescentando que..." signals additional-but-not-shared reasoning at the structural level. The acórdão's ementa consolidates the majority reasoning; cross-referencing ementa with full votes is a structural operation.

These structural signals are not exhaustive. The "pendente" category exists precisely for cases where signals are absent or contradictory — including the adversarial paper's competing-threads hard case. But the adversarial paper treats the hard case as representative of the annotation scheme's operational scope. The representative case for Brazilian procedural documents is not the competing-threads reclamação acórdão; it is the sentença with a dispositive structure and standard alternative-foundation locutions, the petição inicial with explicit subsidiary causes, and the acórdão with individually authored votes whose relationship to the ementa is structurally explicit.

For human formalizers, the preprocessing claim survives for the tractable majority of claims: structural signals permit necessity/contingency annotation before full merits engagement. The "pendente" category correctly marks the non-tractable class without claiming false tractability for it.

The adversarial round 2 argument presses that easy-case tractability does not demonstrate preprocessing value: practitioners who can identify "ainda que" constructions can already handle those cases without formal annotation infrastructure, so the scheme adds nothing for the easy class while failing for the hard class where it would have been useful.

This argument conflates two distinct functions: *enabling identification* and *enabling systematic recording*. The structural-signal tractability claim is not that the taxonomy enables practitioners to recognize what they could not otherwise recognize. It is that the taxonomy provides a formal framework for converting recognized determinations into standardized, cross-document-checkable records. A practitioner who reads "ainda que" and recognizes the construction as marking a contingent foundation does not thereby produce an annotated artifact. The annotation scheme converts an implicit recognition into an explicit, standardized record that downstream processes can operate on.

Without standardized annotation, even for the easy class: (a) different formalizers working across different documents in the same chain may record the same structural determination inconsistently — one annotating the "ainda que" thread as (inferida, contingente), another as (declarada, contingente) — creating coordination failures invisible to downstream processes; (b) propagation-error checks across document chains cannot run without a formal record of the original claim's contingent status to compare against the subsequent document's treatment; (c) quality-assurance audits cannot verify which claims in source documents were treated as necessary and which as contingent without a shared annotation artifact.

The preprocessing contribution for the easy class is not that the scheme enables novel identification. It is that the scheme produces formal records on which the quality-assurance, error-detection, and coordination functions (§3.2) depend. The annotation step converts an implicit competence into an explicit, verifiable artifact — and this conversion is tractable for the easy class before full merits engagement. The adversarial argument would succeed if the taxonomy's claimed value were entirely in enabling identification that practitioners could not otherwise perform. The taxonomy's value for the easy class lies in the formal record, not in enabling the initial recognition.

The scope qualification: this preprocessing tractability is for human formalizers using structural reading; for automated systems, the circularity holds and the taxonomy's contribution is vocabulary for post-analysis recording.

### 3.2 The Vocabulary Recharacterization Is Available but Understates the Taxonomy's Operational Contribution; and the Operational Contributions Are Not General to Any Structured Annotation Scheme

The adversarial paper offers SC2 as a clean resolution: if the taxonomy is recharacterized as vocabulary for recording the outputs of legal analysis rather than a preprocessing step, the tractability attack is misdirected. The adversarial paper concedes this recharacterization is "available and not dishonest."

The recharacterization correctly captures the taxonomy's epistemic function: it provides categories for what analysis has determined. But the adversarial paper's framing of "vocabulary" understates three contributions.

**Quality-assurance record.** A formalization using (provenance × status) notation produces an artifact that makes the epistemic status of every axiom explicit and auditable. A formalization without this notation has the same underlying epistemic structure but makes it invisible. Vocabulary that makes structure visible enables peer review, iterative correction, and expert contestation of specific claims — consequences that do not follow from vocabulary in the usual sense of terminology for naming.

**Error-detection protocol.** The propagation-by-active-incorporation mechanism (§5.5) is detectable by checking whether a later document treats as "necessária" a claim that was "contingente" in an earlier document. This check requires the annotation scheme to have been applied to both documents; it does not require a fresh merits analysis to detect the propagation error once the annotation is in place. The scheme enables a systematic retrospective check across document chains. This is an operational error-detection protocol, not a vocabulary for naming what analysis has already found.

**Coordination protocol across formalizers.** The (provenance, status) notation enables multiple formalizers to contribute to the same formalization at different stages, with explicit records of which claims were established by which formalizer at which epistemic level. Without it, formalization across teams produces implicit and unresolvable disagreements about epistemic status that are not surfaced in the artifact. The notation is infrastructure for collaborative quality assurance, not a private labeling system.

The adversarial round 2 argument presses that these three contributions are properties of structured annotation generally, not of the (provenance × status) taxonomy's specific categories. Any standardized annotation scheme — one marking claims as contested or uncontested, as backed by cited authority or not — would equally produce auditable records, enable cross-document checks, and support multi-formalizer coordination.

At sufficient abstraction, any annotation scheme provides some structure. The adversarial argument proves too much if taken to the conclusion that annotation schemes are interchangeable at the operational level. The question is whether the scheme's specific categories track the distinctions that are legally and computationally significant for the target use case.

The (provenance × status) taxonomy's categories — necessary/contingent × declared/inferred/pending — track the distinction that determines formalization accuracy: whether a claim was load-bearing for the legal effect of the originating document. This determines whether a claim can be safely elevated to axiomatic status in a downstream formalization. Alternative annotation schemes tracking different distinctions would not enable the taxonomy's specific error-detection use case.

A scheme marking claims as "cited by the court/not cited" would fail to detect propagation-by-active-incorporation when a subsequent decision treats as established a claim that was present but contingent in the prior decision, even if both decisions cited the claim. Citation status does not determine load-bearing status. A scheme marking claims as "contested/uncontested" would fail similarly: a claim can be uncontested in context and contingent in the originating decision. Detecting the specific propagation error — a contingent claim elevated to necessary axiomatic status — requires specifically tracking the necessary/contingent distinction, not a proxy for it.

The adversarial argument correctly observes that the three operational contributions follow from structured annotation generally. It does not establish that alternative annotation schemes would provide these contributions for the specific propagation error the taxonomy targets. The adversarial SC2 path — revise the Abstract to acknowledge the taxonomy as providing a standardized vocabulary with benefits achievable through structured annotation generally — does not engage the specific claim that the taxonomy's categories are necessary for detecting the particular error class. An annotation scheme tracking proxy distinctions achieves QA, error-detection, and coordination for different error types, not for this one. Whether the taxonomy's categories are *sufficient* for propagation-error detection (they are) and whether any structured scheme would be equally sufficient (they would not, for this error type) are separate questions.

These three contributions are operational at the system level. Accepting SC2 in the narrow sense — the taxonomy records outputs of analysis — is consistent with maintaining that the taxonomy contributes more than notation, and that its specific categories are necessary for its specific use case.

### 3.3 The Candidate-Ratio Extension Addresses the Fragmented-Majority Failure Case; the Vote-Level Circularity Has Lower Incidence Than the Document-Level Circularity

The adversarial paper is correct that the minimum-denominator rule produces empty ratios for parallel-reasoning STF decisions. This is a genuine limitation. Mitidiero's convergent/parallel distinction, cited by the adversarial paper as the established framework the paper should engage, provides the appropriate basis for extension.

For **convergent-reasoning decisions** — where majority justices share a set of common necessary grounds for the result — the minimum-denominator rule applies as stated. The ratio is the intersection of the grounds all majority votes treated as necessary.

For **parallel-reasoning decisions** — where majority justices reach the same result through independent or incompatible foundations, and the intersection of their necessary grounds is empty or trivially thin — the minimum-denominator rule requires extension rather than abandonment.

The extension: where the intersection of majority votes' necessary grounds is empty, the formalizer constructs candidate ratios by identifying clusters of majority votes sharing common necessary grounds. Each cluster constitutes a candidate ratio, marked with:

1. **Support**: the subset of majority votes that include this ground as necessary.
2. **Epistemic status**: "candidate ratio — parallel-reasoning decision — applicable in case constellations where [ground description] is the operative reasoning framework."
3. **Scope**: fact patterns where this candidate ratio applies, derived from the constellation of features the votes in this cluster treat as legally significant.

The candidate-ratio framework produces a well-defined output — a set of marked candidate ratios — rather than the null output the minimum-denominator rule generates for parallel-reasoning decisions. It preserves the minimum-denominator rule for convergent decisions, where it produces a single unambiguous ratio. For inferior courts applying a fragmented-majority precedent, the candidate-ratio framework provides actionable guidance: apply the candidate ratio whose reasoning framework most closely matches the case before it.

The adversarial paper's §4.3 anticipates this as the "contestation tracks necessity" response and argues that it does not satisfy the minimum-denominator rule's own terms. The candidate-ratio extension does satisfy the rule's terms: it specifies a determinate output — a set of marked candidates — for the case where the minimum-denominator intersection is empty. The adversarial objection that the rule "does not produce multiple weighted candidates" is correct for the unextended rule; the extension modifies the output specification for the parallel-reasoning case.

The adversarial round 2 argument presses a further difficulty: the candidate-ratio extension requires a vote-level necessity determination — identifying which grounds each individual justice treated as necessary in their individual vote before the clustering step runs. The extension decomposes the document-level problem into vote-level subproblems; those subproblems inherit the competing-unmarked-threads structure from §3.1. Ementa cross-referencing checks consistency between an individual vote and the consolidated majority position; it does not resolve, within a vote consistent with the ementa, which of that vote's multiple argumentative threads were necessary for that justice's conclusion.

The structural claim is correct: vote-level necessity determination is required, and ementa cross-referencing does not substitute for it. The question is whether the vote-level competing-unmarked-threads problem has the same incidence and severity as the document-level problem.

The document-level competing-unmarked-threads problem arises partly from the multi-authored structure of colegiado decisions. The collective acórdão merges reasoning streams from multiple justices, each arriving at the same dispositivo through different argumentative paths, without explicit subordination signals across those paths. The problem is structurally generated by the act of merging multiple independent argumentative contributions into one document. Individual justice votes are single-authored. A justice arguing their position typically advances a coherent argumentative line; the parallel-tracks-without-subordination pattern that produces the hard case at the document level has lower incidence within a single justice's reasoning, because a justice is arguing from a single perspective rather than producing a resolution among multiple independently arrived-at conclusions.

This does not eliminate the vote-level problem. A justice's individual vote can contain multiple supporting arguments for the same conclusion, sometimes without explicit subordination signals. But the incidence is substantially lower than at the document level, and the structure of the relevant question differs. For the clustering step, the question at the vote level is not "which thread did the court as a whole treat as the ratio?" — a question requiring determination of the court's collective interpretive stance — but "is this ground necessary for this justice's stated conclusion?" The latter question has a narrower scope, answerable in part from the vote's internal argumentative structure: when a ground would eliminate the justice's conclusion if removed, it is necessary; when the justice's reasoning would survive its removal, it is contingent. For the case where two grounds are both present without explicit subordination, both may be genuinely necessary for the justice's conclusion — in which case both are included in the vote's necessary-ground set, and the clustering step correctly receives a larger ground set for that justice's vote.

When determination is genuinely unavailable — a justice's vote contains competing unmarked threads that the formalizer cannot resolve from the vote's internal structure — the "pendente" marker applies at the vote level, and the clustering step proceeds on the grounds that can be determined. The candidate-ratio output for that justice's vote is correspondingly uncertain, flagged as such.

The adversarial paper's own §4.3 concession — that "inferior courts observe which way the STF decided and apply that decision as a directional signal, supplemented by the individual grounds they find most persuasive" — confirms that vote-level ground identification is practically available through structural reading. Courts performing this reconstruction operate without performing a fresh constitutional analysis from first principles. The candidate-ratio extension formalizes what courts already do. The adversarial argument that the formalization requires an intractable judgment sits in tension with the adversarial paper's acknowledgment that courts routinely perform the underlying reconstruction. Whether the formalization is *more tractable* or *less tractable* than courts' informal reconstruction depends on whether the formalization provides systematic resources that informal reconstruction lacks — which is precisely what the annotation scheme is designed to supply.

The extension requires identifying which justices' votes share which necessary grounds — structural reading of individual STF votes cross-referenced against the ementa as a consistency check, supplemented by the vote's own argumentative structure for necessity determination within each vote. The adversarial paper correctly identifies that ementa cross-referencing alone does not resolve vote-level necessity; it does not follow that vote-level necessity determination is as intractable as document-level necessity determination for parallel-reasoning decisions.

---

## 4. Anticipated Objection

The adversarial paper's §4.1 anticipates the human-formalizer response and argues it does not suffice. Two reasons: (a) the paper's scope includes automated formalizers ("human or automated"), and for them the circularity holds; (b) for human formalizers, "pendente" cannot serve as a resting state for load-bearing claims — a formalization with "pendente" on its key axioms has documented its own incompleteness rather than demonstrating tractability.

On (a): this defense accepts it. The preprocessing tractability claim is qualified to human formalizers using structural signals. For automated systems, the vocabulary recharacterization applies, and the taxonomy's value lies in the quality-assurance and error-detection contributions identified in §3.2 — specifically, those contributions depend on the taxonomy's categories tracking the necessary/contingent distinction, not on any structured annotation scheme generally.

On (b): "pendente" is correctly characterized as documenting incompleteness — but the objection misstates its role. "Pendente" does not claim to be a completed preprocessing step; it marks claims requiring further analysis before they can serve as high-confidence axioms. A formalization that marks load-bearing claims as "pendente" tells its users which parts of the model require resolution before the formalization is used for consequential purposes. This is a quality-assurance function: it makes the model's vulnerabilities explicit rather than hiding them behind apparently resolved annotations.

The adversarial paper's further objection — that the easy class's tractability does not demonstrate value because practitioners can handle those cases without formal infrastructure — is addressed in §3.1. The taxonomy's preprocessing contribution for the easy class is not enabling identification but enabling formal recording; the formal record is what the error-detection and coordination functions require, and it is not produced by practitioners' implicit recognition without annotation.

---

## 5. Scope of This Defense

This defense establishes:

- The preprocessing tractability claim survives for **human formalizers** using structural reading, for the majority of claims in standard Brazilian procedural documents, where linguistic markers permit necessity/contingency annotation before full merits engagement.
- The taxonomy's preprocessing value for the easy class lies in producing formal records — not in enabling initial identification that practitioners could not perform without it. Systematic recording is the preprocessing contribution.
- The (provenance, status) taxonomy contributes quality-assurance records, error-detection protocols, and coordination infrastructure beyond notation — and these contributions are specific to the taxonomy's necessary/contingent categories, not properties of structured annotation generally, because the propagation error the taxonomy detects requires specifically tracking load-bearing status.
- The minimum-denominator rule is correctly formulated for convergent-reasoning decisions and extendable via a candidate-ratio framework for parallel-reasoning decisions, without abandoning the rule for its primary case.
- The vote-level necessity determination required by the candidate-ratio extension faces a structurally parallel but lower-incidence version of the competing-unmarked-threads problem: individual justice votes are single-authored and have lower parallel-tracks incidence; the vote-level question ("is this ground necessary for this justice's conclusion?") is narrower in scope than the document-level question.

This defense accepts:

- The preprocessing circularity holds for automated systems.
- "Pendente" annotations on load-bearing claims indicate formalization incompleteness — this is an honest outcome for the hard class of claims, not a tractability claim.
- The minimum-denominator rule, unextended, fails for parallel-reasoning decisions; the adversarial paper's §3.3 citations to Mitidiero and Macêdo identify a real and significant gap.
- The candidate-ratio extension may produce complex outputs for highly fragmented decisions with many independent parallel votes.
- Vote-level necessity determination is required for the candidate-ratio clustering step, and ementa cross-referencing alone does not resolve it.

This defense does not address the paper's claim for automated systems beyond conceding the adversarial paper's preprocessing circularity for that class.

---

## 6. Conditions Under Which This Defense Would Fail

- If systematic study of Brazilian procedural documents shows that the competing-argumentative-threads pattern — multiple independent threads without standard contingency markers — occurs in a substantial proportion of contested cases across document types, not only in complex reclamação acórdãos, the structural-signal argument loses its force for the standard-case class. High rates of ambiguous structural marking across sentenças, petições, and routine appellate acórdãos would confirm the preprocessing circularity for human formalizers.
- If trained Brazilian proceduralists without prior merits analysis show high interrater disagreement on necessity/contingency classifications for representative documents, this would be direct evidence against the structural-signal argument's tractability claim.
- If the claim that easy-class formal recording constitutes a preprocessing contribution is contested on the ground that the formal record adds nothing beyond what informal annotations already capture in practice — i.e., that formalizers already produce consistent annotation records without the specific taxonomy's categories — the recording-not-identification argument would require empirical support regarding actual formalizer practice.
- If the candidate-ratio extension produces unstable or practically unwieldy outputs for the majority of STF plenary decisions — because most consequential decisions produce highly fragmented parallel reasoning without stable vote clusters — the extension provides theoretical coverage without practical utility.
- If Brazilian courts and doctrine treat parallel-reasoning decisions as producing no binding ratio (rather than multiple candidate ratios from which inferior courts select), the candidate-ratio framework formalizes a practice that does not exist rather than one that does.
- If the adversarial paper's SC2 path is developed with a specific alternative annotation scheme that successfully enables propagation-error detection at equivalent or higher accuracy than the (provenance × status) taxonomy — by tracking a different axis that happens to coincide with necessary/contingent status in practice — the distinctiveness claim in §3.2 would be weakened.
- If the scope qualification in §3.1 (human formalizers only) is accepted as the defense's maximum concession, the Abstract's "human or automated" claim remains partially exposed. The defense does not rescue the automated-formalizer preprocessing claim.

---

## References

- Baldo, F. S. (2025). Categorias Processuais Civis para Formalização Computacional: Pedidos, Provimentos, Pretensões Recursais e Proveniência de Afirmações no CPC 2015. `paper1C_categorias_processuais_formalizacao.md` (this repository).
- `otherwise/paper1c-formalization-tractability.md` — "Vocabulary Without Procedure: A Tractability Challenge to Paper 1C's Claim Provenance Module" (adversarial paper, this repository).
- BRASIL. Lei nº 13.105, de 16 de março de 2015 (Código de Processo Civil). Arts. 141, 322, 324, 325, 326, 327, 485, 487, 489, §1º, 492, 504, 1.013, 1.022.
- MACÊDO, L. B. de. *Precedentes judiciais e o direito processual civil*. 3. ed. Salvador: JusPodivm, 2019.
- MARINONI, L. G. *Precedentes obrigatórios*. 5. ed. São Paulo: Revista dos Tribunais, 2016.
- MITIDIERO, D. *Cortes superiores e cortes supremas: do controle à interpretação, da jurisprudência ao precedente*. 3. ed. São Paulo: Revista dos Tribunais, 2017.
