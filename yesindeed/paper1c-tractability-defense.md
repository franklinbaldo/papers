# Document Structure and Candidate Ratios: A Defense of Paper 1C's Claim Provenance Module

---

## 1. Thesis Supported

Baldo (2025), "Categorias Processuais Civis para Formalização Computacional" (`paper1C_categorias_processuais_formalizacao.md`), makes two structural commitments in its claim provenance module (§5) that this paper defends.

**Commitment 1 (preprocessing tractability):** The necessary/contingent determination, applied to claims in Brazilian procedural documents before axiomatization, constitutes a tractable preprocessing step. The (provenance, status) annotation scheme enables formalizers to "correctly implement the categories in formal languages without distorting the underlying legal system" (Abstract).

**Commitment 2 (ratio extraction rule):** For Brazilian colegiado decisions, the ratio is "the minimum common denominator of the grounds of the majority votes — what all majority votes share as necessary foundation for the result. The grounds that each justice added individually but that were not shared by the others are, in relation to the acórdão as precedent, obiter." (§5.3)

---

## 2. What This Support Adds

**Vector:** Direct defense. This paper responds to `otherwise/paper1c-formalization-tractability.md` ("Vocabulary Without Procedure"), which attacks both commitments:

*Commitment 1 attack (preprocessing circularity):* The necessary/contingent determination requires knowing whether the dispositivo could be reached on other available grounds — which is a product of the legal analysis the formalization system is trying to perform. The annotation cannot precede the analysis; it is the analysis. The "pendente" category acknowledges failure to determine necessity rather than constituting a tractable preprocessing step.

*Commitment 2 attack (fragmented-majority failure):* The minimum-denominator rule produces empty or trivially thin ratios for STF plenary decisions where majority justices reach the same result through independent foundations. This is not a peripheral case; it is the characteristic failure mode for the STF's most contested constitutional decisions. The adversarial paper cites Mitidiero's convergent/parallel-reasoning distinction and Macêdo's reconstruction methods as the established doctrinal framework the paper does not engage.

This defense accepts: that the preprocessing circularity holds for fully automated formalizers; that the minimum-denominator rule is incomplete for parallel-reasoning decisions; and that Mitidiero's convergent/parallel distinction is the appropriate framework for extending it. This defense contests: that the preprocessing circularity applies with equal force to human formalizers relying on structural document signals; that the vocabulary recharacterization (adversarial SC2) reduces the taxonomy to mere notation; and that the fragmented-majority failure requires abandoning the minimum-denominator rule rather than extending it.

---

## 3. The Defense

### 3.1 The Preprocessing Circularity Holds for Automated Systems; It Is Limited for Human Formalizers Using Structural Signals

The adversarial paper's hardest example for the preprocessing circularity is the competing-argumentative-threads case: a reclamação acórdão containing two independent argumentative threads each sufficient for the result, where the formalization system's task is identifying which is the ratio. Document structure alone cannot resolve this case without knowing which thread the STF treated as load-bearing — which is a legal-analytical judgment.

The adversarial paper's argument is strongest as an argument against automated systems. For human formalizers, the circularity is substantially narrower. Brazilian procedural writing employs a small set of systematic linguistic markers for contingency that a trained practitioner applies through structural reading before engaging the merits.

In **sentenças and acórdãos**, a distinct class of locutions signals alternative foundations: "Ainda que assim não fosse...", "Mesmo que se admitisse...", "Para além desse fundamento...", "Ad argumentandum tantum...", "Ainda que superado o argumento anterior...". These constructions are the near-universal signal for fundamento alternativo in Brazilian judicial writing. A trained practitioner identifies the "ainda que" construction as a contingency signal through structural reading before determining whether the alternative foundation is legally correct.

In **petições iniciais**, subsidiary causes of pedir are routinely prefaced with hedging locutions: "Subsidiariamente, caso se entenda que...", "Alternativamente, e sem prejuízo do acima exposto...". The distinction between the primary causa de pedir and its alternatives is structural and does not require merits analysis to identify.

In **acórdãos with concurring votes**, the standard Brazilian colegiado format separates votes by justice. A vote beginning "Acompanho o relator, acrescentando que..." signals additional-but-not-shared reasoning at the structural level. The acórdão's ementa consolidates the majority reasoning; cross-referencing ementa with full votes is a structural operation.

These structural signals are not exhaustive. The "pendente" category exists precisely for cases where signals are absent or contradictory — including the adversarial paper's competing-threads hard case. But the adversarial paper treats the hard case as representative of the annotation scheme's operational scope. The representative case for Brazilian procedural documents is not the competing-threads acórdão; it is the sentença with a dispositive structure and standard alternative-foundation locutions, the petição inicial with explicit subsidiary causes, and the acórdão with individually authored votes whose relationship to the ementa is structurally explicit.

For human formalizers, the preprocessing claim survives for the tractable majority of claims: structural signals permit necessity/contingency annotation before full merits engagement. The "pendente" category correctly marks the non-tractable class without claiming false tractability for it. The scope qualification: this preprocessing tractability is for human formalizers using structural reading; for automated systems, the circularity holds and the taxonomy's contribution is vocabulary for post-analysis recording.

### 3.2 The Vocabulary Recharacterization Is Available but Understates the Taxonomy's Operational Contribution

The adversarial paper offers SC2 as a clean resolution: if the taxonomy is recharacterized as vocabulary for recording the outputs of legal analysis rather than a preprocessing step, the tractability attack is misdirected. The adversarial paper concedes this recharacterization is "available and not dishonest."

The recharacterization correctly captures the taxonomy's epistemic function: it provides categories for what analysis has determined. But the adversarial paper's framing of "vocabulary" understates three contributions.

**Quality-assurance record.** A formalization using (provenance × status) notation produces an artifact that makes the epistemic status of every axiom explicit and auditable. A formalization without this notation has the same underlying epistemic structure but makes it invisible. Vocabulary that makes structure visible enables peer review, iterative correction, and expert contestation of specific claims — consequences that do not follow from vocabulary in the usual sense of terminology for naming.

**Error-detection protocol.** The propagation-by-active-incorporation mechanism (§5.5) is detectable by checking whether a later document treats as "necessária" a claim that was "contingente" in an earlier document. This check requires the annotation scheme to have been applied to both documents; it does not require a fresh merits analysis to detect the propagation error once the annotation is in place. The scheme enables a systematic retrospective check across document chains. This is an operational error-detection protocol, not a vocabulary for naming what analysis has already found.

**Coordination protocol across formalizers.** The (provenance, status) notation enables multiple formalizers to contribute to the same formalization at different stages, with explicit records of which claims were established by which formalizer at which epistemic level. Without it, formalization across teams produces implicit and unresolvable disagreements about epistemic status that are not surfaced in the artifact. The notation is infrastructure for collaborative quality assurance, not a private labeling system.

These three contributions are operational at the system level. The adversarial paper's vocabulary framing collapses them into "naming what has been found." Accepting SC2 in the narrow sense — the taxonomy records outputs of analysis — is consistent with maintaining that the taxonomy contributes more than notation.

### 3.3 The Candidate-Ratio Extension Addresses the Fragmented-Majority Failure Case

The adversarial paper is correct that the minimum-denominator rule produces empty ratios for parallel-reasoning STF decisions. This is a genuine limitation. Mitidiero's convergent/parallel distinction, cited by the adversarial paper as the established framework the paper should engage, provides the appropriate basis for extension.

For **convergent-reasoning decisions** — where majority justices share a set of common necessary grounds for the result — the minimum-denominator rule applies as stated. The ratio is the intersection of the grounds all majority votes treated as necessary.

For **parallel-reasoning decisions** — where majority justices reach the same result through independent or incompatible foundations, and the intersection of their necessary grounds is empty or trivially thin — the minimum-denominator rule requires extension rather than abandonment.

The extension: where the intersection of majority votes' necessary grounds is empty, the formalizer constructs candidate ratios by identifying clusters of majority votes sharing common necessary grounds. Each cluster constitutes a candidate ratio, marked with:

1. **Support**: the subset of majority votes that include this ground as necessary.
2. **Epistemic status**: "candidate ratio — parallel-reasoning decision — applicable in case constellations where [ground description] is the operative reasoning framework."
3. **Scope**: fact patterns where this candidate ratio applies, derived from the constellation of features the votes in this cluster treat as legally significant.

The candidate-ratio framework produces a well-defined output — a set of marked candidate ratios — rather than the null output the minimum-denominator rule generates for parallel-reasoning decisions. It preserves the minimum-denominator rule for convergent decisions, where it produces a single unambiguous ratio. For inferior courts applying a fragmented-majority precedent, the candidate-ratio framework provides actionable guidance: apply the candidate ratio whose reasoning framework most closely matches the case before it.

The adversarial paper's §4.3 anticipates this as the "contestation tracks necessity" response and argues that it does not satisfy the minimum-denominator rule's own terms. The candidate-ratio extension does satisfy the rule's terms: it specifies a determinate output — a set of marked candidates — for the case where the minimum-denominator intersection is empty. The adversarial objection that the rule "does not produce multiple weighted candidates" is correct for the unextended rule; the extension modifies the output specification for the parallel-reasoning case.

The extension requires identifying which justices' votes share which necessary grounds — structural reading of individual STF votes cross-referenced against the ementa. The adversarial paper concedes in §4.3 that "inferior courts observe which way the STF decided and apply that decision as a directional signal, supplemented by the individual grounds they find most persuasive," confirming that the information required for candidate extraction is practically available through structural reading. The extension formalizes what courts already do under the label of applying the most relevant ground.

---

## 4. Anticipated Objection

The adversarial paper's §4.1 anticipates the human-formalizer response and argues it does not suffice. Two reasons: (a) the paper's scope includes automated formalizers ("human or automated"), and for them the circularity holds; (b) for human formalizers, "pendente" cannot serve as a resting state for load-bearing claims — a formalization with "pendente" on its key axioms has documented its own incompleteness rather than demonstrating tractability.

On (a): this defense accepts it. The preprocessing tractability claim is qualified to human formalizers using structural signals. For automated systems, the vocabulary recharacterization applies, and the taxonomy's value lies in the quality-assurance and error-detection contributions identified in §3.2.

On (b): "pendente" is correctly characterized as documenting incompleteness — but the objection misstates its role. "Pendente" does not claim to be a completed preprocessing step; it marks claims requiring further analysis before they can serve as high-confidence axioms. A formalization that marks load-bearing claims as "pendente" tells its users which parts of the model require resolution before the formalization is used for consequential purposes. This is a quality-assurance function: it makes the model's vulnerabilities explicit rather than hiding them behind apparently resolved annotations. The adversarial paper's objection would apply equally to any incomplete-work marker in any formal system — the ability to identify incompleteness is part of the system's function, not evidence of its failure.

---

## 5. Scope of This Defense

This defense establishes:

- The preprocessing tractability claim survives for **human formalizers** using structural reading, for the majority of claims in standard Brazilian procedural documents, where linguistic markers permit necessity/contingency annotation before full merits engagement.
- The (provenance, status) taxonomy contributes quality-assurance records, error-detection protocols, and coordination infrastructure beyond notation.
- The minimum-denominator rule is correctly formulated for convergent-reasoning decisions and extendable via a candidate-ratio framework for parallel-reasoning decisions, without abandoning the rule for its primary case.

This defense accepts:

- The preprocessing circularity holds for automated systems.
- "Pendente" annotations on load-bearing claims indicate formalization incompleteness — this is an honest outcome for the hard class of claims, not a tractability claim.
- The minimum-denominator rule, unextended, fails for parallel-reasoning decisions; the adversarial paper's §3.3 citations to Mitidiero and Macêdo identify a real and significant gap.
- The candidate-ratio extension may produce complex outputs for highly fragmented decisions with many independent parallel votes.

This defense does not address the paper's claim for automated systems beyond conceding the adversarial paper's preprocessing circularity for that class.

---

## 6. Conditions Under Which This Defense Would Fail

- If systematic study of Brazilian procedural documents shows that the competing-argumentative-threads pattern — multiple independent threads without standard contingency markers — occurs in a substantial proportion of contested cases across document types, not only in complex reclamação acórdãos, the structural-signal argument loses its force for the standard-case class. High rates of ambiguous structural marking across sentenças, petições, and routine appellate acórdãos would confirm the preprocessing circularity for human formalizers.
- If trained Brazilian proceduralists without prior merits analysis show high interrater disagreement on necessity/contingency classifications for representative documents, this would be direct evidence against the structural-signal argument's tractability claim.
- If the candidate-ratio extension produces unstable or practically unwieldy outputs for the majority of STF plenary decisions — because most consequential decisions produce highly fragmented parallel reasoning without stable vote clusters — the extension provides theoretical coverage without practical utility.
- If Brazilian courts and doctrine treat parallel-reasoning decisions as producing no binding ratio (rather than multiple candidate ratios from which inferior courts select), the candidate-ratio framework formalizes a practice that does not exist rather than one that does.
- If the scope qualification in §3.1 (human formalizers only) is accepted as the defense's maximum concession, the Abstract's "human or automated" claim remains partially exposed. The defense does not rescue the automated-formalizer preprocessing claim.

---

## References

- Baldo, F. S. (2025). Categorias Processuais Civis para Formalização Computacional: Pedidos, Provimentos, Pretensões Recursais e Proveniência de Afirmações no CPC 2015. `paper1C_categorias_processuais_formalizacao.md` (this repository).
- `otherwise/paper1c-formalization-tractability.md` — "Vocabulary Without Procedure: A Tractability Challenge to Paper 1C's Claim Provenance Module" (adversarial paper, this repository).
- BRASIL. Lei nº 13.105, de 16 de março de 2015 (Código de Processo Civil). Arts. 141, 322, 324, 325, 326, 327, 485, 487, 489, §1º, 492, 504, 1.013, 1.022.
- MACÊDO, L. B. de. *Precedentes judiciais e o direito processual civil*. 3. ed. Salvador: JusPodivm, 2019.
- MARINONI, L. G. *Precedentes obrigatórios*. 5. ed. São Paulo: Revista dos Tribunais, 2016.
- MITIDIERO, D. *Cortes superiores e cortes supremas: do controle à interpretação, da jurisprudência ao precedente*. 3. ed. São Paulo: Revista dos Tribunais, 2017.
